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
        self.site_id = None
        self.queue = None

    def recv_connect(self):
        logging.debug("New user connected")

    def recv_disconnect(self):
        logging.debug("User disconnected")

        if self.queue:
            #closing infinity loop of queue processor by sending False into it
            self.queue.put(False)

        super(BaseNamespace, self).recv_disconnect()

    def recv_message(self, message):
        logging.debug("MSG: {}".format(message))

    def on_login(self, user_id, site_id, hash_key):
        if user_id and site_id and hash_key == self.__check_hash(user_id, site_id):
            if not isinstance(user_id, long):
                user_id = long(user_id)

            if not isinstance(site_id, long):
                site_id = long(site_id)

            self.user_id = user_id
            self.site_id = site_id
            logging.debug("User {user_id} session for site {site_id} confirmed".format(
                user_id=user_id,
                site_id=site_id
            ))

            self.socket.session['user_id'] = user_id
            self.socket.session['site_id'] = site_id

            self.queue = Queue(maxsize=None)
            register = Register()

            if user_id not in register.queue:
                register.queue[user_id] = {}

            if site_id not in register.queue[user_id]:
                register.queue[user_id][site_id] = {}

            register.queue[user_id][site_id][self.socket.sessid] = self.queue
            JobWrapper.start_listen(self._outter_task_loop)

            self.emit("login", {"status": True})
        else:
            logging.debug("Can't auth user {user_id} on site {site} and hash {hash}".format(
                user_id=user_id,
                site=site_id,
                hash=hash_key
            ))
            self.recv_disconnect()
            self.emit("login", {"status": False})

    def __check_hash(self, user_id, site_id):
        return sha256(
            str(user_id) + "|" + str(site_id) + "|" + settings.SECRET_KEY
        ).hexdigest()

    def _outter_task_loop(self):
        task = self.queue.get()
        if task:
            task.do(self)
            return True

        register = Register()

        if len(register.queue[self.user_id][self.site_id]) == 1:
            del register.queue[self.user_id][self.site_id]
        else:
            del register.queue[self.user_id][self.site_id][self.socket.sessid]

        logging.debug("Task loop finished for user {user_id} and site {site_id}".format(
            user_id=self.user_id,
            site_id=self.site_id
        ))
        return False