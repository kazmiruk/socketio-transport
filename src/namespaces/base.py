import json
import logging
from gevent.queue import Queue
from hashlib import sha256

from socketio.namespace import BaseNamespace as ParentNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

from interfaces.jobs import JobWrapper
from interfaces.register import Register
import settings


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

    def on_login(self, user_id, hash_key):
        if not isinstance(user_id, long):
            user_id = long(user_id)

        if user_id and hash_key == self.__check_hash(user_id):
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
            logging.debug("Can't auth user {user_id} and hash {hash}".format(user_id=user_id, hash=hash_key))
            self.recv_disconnect()
            self.emit("login", {"status": False})

    def __check_hash(self, user_id):
        return sha256(str(user_id) + "|" + settings.SECRET_KEY).hexdigest()

    def _outter_task_loop(self):
        task = self.queue.get()
        if task:
            task.do(self)
            return True

        logging.debug("Task loop finished for user {user_id}".format(
            user_id=self.user_id
        ))
        return False