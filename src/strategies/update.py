import logging

from base import Strategy


class Update(Strategy):
    def do(self, namesapce):
        logging.debug("User {user_id} fired update event".format(
            user_id=namesapce.user_id
        ))
        namesapce.emit("update", self.data)