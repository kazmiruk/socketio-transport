import logging

from interfaces.register import Register


class Strategy(object):
    def __init__(self, data):
        self.data = data

    def do(self, namesapce):
        pass

    def put(self, user_id, site_id):
        register = Register()

        if not isinstance(user_id, long):
            user_id = long(user_id)

        if not isinstance(site_id, long):
            site_id = long(site_id)

        if user_id in register.queue and site_id in register.queue[user_id]:
            user_queues = register.queue[user_id][site_id]

            logging.debug("It will add {strategy}, {user_id}, {site_id} task for {count} sockets".format(
                strategy=self.__class__.__name__,
                user_id=user_id,
                site_id=site_id,
                count=len(user_queues)
            ))

            self._put_into_queue(user_queues)
        else:
            logging.debug("There are no any users to send them data: {strategy}, {user_id}, {site_id}".format(
                strategy=self.__class__.__name__,
                user_id=user_id,
                site_id=site_id
            ))

    def _put_into_queue(self, user_queues):
        for session_id in user_queues:
            user_queues[session_id].put(self)