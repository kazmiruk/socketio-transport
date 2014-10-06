import logging

from base import Strategy


class NewMessage(Strategy):
    def do(self, namespace):
        logging.debug("User {user_id} recive new message {message} in talk {talk_id}".format(
            user_id=namespace.user_id,
            message=self.data['message'],
            talk_id=self.data['talk_id']
        ))
        namespace.emit_to_room("talk_{id}".format(id=self.data['talk_id']), "new_message", self.data)
        #It needs to manual sending into current socket because of
        #excluding it from emit_to_room user list
        namespace.emit("new_message", self.data)

    def _put_into_queue(self, user_queues):
        """ Because of users subscribed on room it need only one notification into
        any socket of current user
        """
        for session_id in user_queues:
            user_queues[session_id].put(self)
            break