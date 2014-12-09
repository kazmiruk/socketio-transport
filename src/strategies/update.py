import logging

from base import Strategy


class Update(Strategy):
    def do(self, namespace):
        logging.debug("User {user_id} fired update event".format(user_id=namespace.user_id))
        namespace.emit("update", self.data)