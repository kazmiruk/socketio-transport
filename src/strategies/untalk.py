import logging

from base import Strategy


class Untalk(Strategy):
    def do(self, namespace):
        logging.debug("User leave channel of talk {talk_id}".format(talk_id=self.data['talk_id']))
        namespace.leave("talk_{id}".format(id=self.data['talk_id']))