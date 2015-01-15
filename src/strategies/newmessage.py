import logging

from base import Strategy


class NewMessage(Strategy):
    def do(self, namespace):
        logging.debug("User {user_id} (session {session_id}) recive new "
                      "message {message} in talk {talk_id}".format(user_id=namespace.user_id,
                                                                   session_id=namespace.socket.sessid,
                                                                   message=self.data['message'],
                                                                   talk_id=self.data['talk_id']))
        namespace.emit("new_message", self.data)

    def _put_into_queue(self, user_queues):
        _ = [user_queues[session_id].put(self) for session_id in user_queues]