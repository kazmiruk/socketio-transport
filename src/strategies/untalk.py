import logging

from base import Strategy


class Untalk(Strategy):
    def do(self, namesapce):
        logging.debug("User leave channel of talk {talk_id}".format(
            talk_id=self.data['talk_id']
        ))
        namesapce.leave("talk_{id}".format(id=self.data['talk_id']))