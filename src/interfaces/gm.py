import json
import logging
from gearman import GearmanWorker
from importlib import import_module

import settings
from interfaces.options import OPTIONS
from interfaces.jobs import JobWrapper


class GearmanListener(object):
    def __init__(self):
        gm_worker = GearmanWorker(settings.GEARMAN['hosts'])
        gm_worker.set_client_id("socket_io_gearman_" + str(OPTIONS.chunk))
        gm_worker.register_task("socket_io", GearmanListener.callback)

        logging.debug("Gearman worker spawned into thread with listening of socket_io queue")
        JobWrapper.spawn(gm_worker.work)

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
        task.put(data['user_id'])

        return gearman_job.data