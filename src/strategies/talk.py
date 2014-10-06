import logging

from base import Strategy


class Talk(Strategy):
    def do(self, namespace):
        logging.debug("User join channel of talk {talk_id}".format(
            talk_id=self.data['talk_id']
        ))
        namespace.join("talk_{id}".format(id=self.data['talk_id']))