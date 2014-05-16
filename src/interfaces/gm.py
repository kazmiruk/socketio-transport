import json
import logging
from gearman import GearmanWorker, admin_client, errors
from importlib import import_module
import gevent

import settings
from interfaces.options import OPTIONS
from interfaces.jobs import JobWrapper


class GearmanListener(object):
    def __init__(self):
        gm_worker = self._init()
        JobWrapper.spawn(self._start_work, gm_worker)

    def _init(self):
        while True:
            while not self.is_available():
                logging.error("Gearman not available right now. Demon will sleep during {n} seconds".format(
                    n=settings.GEARMAN_RECONNECT_TIMEOUT
                ))
                gevent.sleep(settings.GEARMAN_RECONNECT_TIMEOUT)

            logging.debug("Gearman worker try to connect {hosts}".format(
                hosts=', '.join(settings.GEARMAN['hosts'])
            ))

            try:
                gm_worker = GearmanWorker(settings.GEARMAN['hosts'])
                gm_worker.set_client_id("socket_io_gearman_" + str(OPTIONS.port))
                gm_worker.register_task("socket_io", GearmanListener.callback)
                logging.debug("Gearman worker was successfull created")

                return gm_worker
            except Exception, e:
                logging.error("Error while initiation gearman worker connect with message: {message}".format(
                    message=e.message
                ))
                logging.debug("Demon will be sleep during {n} seconds".format(
                    n=settings.GEARMAN_RECONNECT_TIMEOUT
                ))
                gevent.sleep(settings.GEARMAN_RECONNECT_TIMEOUT)

    def _start_work(self, gm_worker):
        while True:
            try:
                logging.debug("Gearman worker spawned into thread with listening of socket_io queue")
                gm_worker.work(poll_timeout=settings.GEARMAN['waiting_timeout'])
            except Exception, e:
                gm_worker.shutdown()

                logging.error("Gearman client was failed with error: {message}".format(
                    message=e.message
                ))

            gm_worker = self._init()

    def is_available(self):
        """ Ping all of the hosts, that defined in the settings,
            and return True if one of them is available.
        """
        hosts = settings.GEARMAN['hosts']

        for host in hosts:
            try:
                client = admin_client.GearmanAdminClient([host, ])
                client.ping_server()
                return True
            except errors.ServerUnavailable:
                # try next gearman host
                pass

        return False

    @staticmethod
    def callback(gearman_worker, gearman_job):
        data = json.loads(gearman_job.data)
        strategy = data['strategy']
        try:
            module = import_module("strategies.{path}".format(
                path=strategy.lower(),
                name=strategy
            ))
            handler = getattr(module, strategy, None)
            if handler is None:
                raise ImportError()
        except Exception, e:
            logging.error("There are no any {strategy} strategy".format(
                strategy=strategy
            ))
            return gearman_job.data

        task = handler(data['data'])
        delay = float(data.get('delay', 0.0))

        logging.debug("Task {user_id}, {site_id}, {delay} obtained".format(
            user_id=data['user_id'],
            site_id=data['site_id'],
            delay=delay
        ))

        if delay > 0:
            JobWrapper.spawn(
                GearmanListener.delayer,
                task,
                data['user_id'],
                data['site_id'],
                delay
            )
        else:
            task.put(data['user_id'], data['site_id'])

        return gearman_job.data

    @staticmethod
    def delayer(task, user_id, site_id, delay):
        logging.debug("Task from user {user_id} and {site_id} will be delayed during {delay} seconds".format(
            user_id=user_id,
            site_id=site_id,
            delay=delay
        ))

        gevent.sleep(delay)
        task.put(user_id, site_id)