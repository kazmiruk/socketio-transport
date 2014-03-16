import logging
from gevent.queue import Queue

from socketio.namespace import BaseNamespace as ParentNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

from interfaces.session import SessionStore
from interfaces.jobs import JobWrapper
from interfaces.register import Register


class BaseNamespace(ParentNamespace, RoomsMixin, BroadcastMixin):
    def __init__(self, *args, **kwargs):
        super(BaseNamespace, self).__init__(*args, **kwargs)
        self.user_id = None
        self.queue = None

    def recv_connect(self):
        logging.debug("New user connected")

    def recv_disconnect(self):
        logging.debug("User disconnected")

        if self.user_id:
            register = Register()
            if self.user_id in register.queue and \
                    self.socket.sessid in register.queue[self.user_id]:
                if len(register.queue[self.user_id]) == 1:
                    del register.queue[self.user_id]
                else:
                    del register.queue[self.user_id][self.socket.sessid]

        super(BaseNamespace, self).recv_disconnect()

    def recv_message(self, message):
        logging.debug("MSG: {}".format(message))

    def on_login(self, session_key):
        user_id = SessionStore().load(session_key)

        if user_id:
            self.user_id = user_id
            logging.debug("User {user_id} session confirmed".format(user_id=user_id))

            self.socket.session['user_id'] = user_id

            self.queue = Queue(maxsize=None)
            register = Register()

            if user_id not in register.queue:
                register.queue[user_id] = {}

            register.queue[user_id][self.socket.sessid] = self.queue
            JobWrapper.start_listen(self._outter_task_loop)

            self.emit("login", {"status": True})
        else:
            logging.debug("Can't auth user with session key {session_key}".format(
                session_key=session_key
            ))
            self.recv_disconnect()
            self.emit("login", {"status": False})

    def _outter_task_loop(self):
        task = self.queue.get()
        if task:
            task.do(self)
            return True

        logging.debug("Task loop finished for user {user_id}".format(
            user_id=self.user_id
        ))
        return False