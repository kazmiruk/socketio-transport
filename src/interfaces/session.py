import redis
import base64
import hmac
import hashlib
import json
import gevent

import settings

redis.connection.socket = gevent.socket

redis_connection_pool = redis.BlockingConnectionPool(max_connections=settings.MAX_REDIS_CONNECTIONS,
                                                     timeout=None)

if settings.SESSION_REDIS_URL is not None:
    redis_server = redis.StrictRedis.from_url(settings.SESSION_REDIS_URL,
                                              connection_pool=redis_connection_pool)
elif settings.SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH is None:
    redis_server = redis.StrictRedis(host=settings.SESSION_REDIS_HOST, port=settings.SESSION_REDIS_PORT,
                                     db=settings.SESSION_REDIS_DB, password=settings.SESSION_REDIS_PASSWORD,
                                     connection_pool=redis_connection_pool)
else:
    redis_server = redis.StrictRedis(unix_socket_path=settings.SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH,
                                     db=settings.SESSION_REDIS_DB, password=settings.SESSION_REDIS_PASSWORD,
                                     connection_pool=redis_connection_pool)


class SessionStore(object):
    def __init__(self):
        self.server = redis_server

    def load(self, session_key):
        try:
            session_data = self.server.get(self._get_real_stored_key(session_key))
            return self._decode(session_data, settings.SECRET_KEY)
        except:
            return None

    def _get_real_stored_key(self, session_key):
        prefix = settings.SESSION_REDIS_PREFIX
        if not prefix:
            return session_key
        return ':'.join([prefix, session_key])

    def _get_utoken(self, msg, secret_key, class_name="SessionStore"):
        """Get the unique session token.

        @param msg          The message string.
        @param secret_key   The SECRET_KEY from the Django settings.py file.
        @param class_name   The class name. This is emulates the SessionBase
                            _hash() function in Django.
        @returns The unique session token.
        """
        key_salt = "django.contrib.sessions" + class_name
        sha1 = hashlib.sha1((key_salt + secret_key).encode('utf-8')).digest()
        utoken = hmac.new(sha1, msg=msg, digestmod=hashlib.sha1).hexdigest()
        return utoken

    def _decode(self, session_data, secret_key, class_name="SessionStore"):
        """Decode Django session data using the secret key from the
        settings.py file and verifying it.

        This code is completely independent of Django so it can be used by
        third party tools.

        @param session_data The session data from Django.
        @param secret_key   The SECRET_KEY from the Django settings.py file.
        @param class_name   The class name. This is emulates the SessionBase
                            _hash() function in Django.
        @returns the session data as a dictionary
        """
        encoded_data = base64.b64decode(session_data)
        utoken, pickled = encoded_data.split(b':', 1)
        expected_utoken = self._get_utoken(pickled, secret_key, class_name)
        if utoken.decode() != expected_utoken:
            raise BaseException('Session data corrupted "%s" != "%s"',
                                utoken.decode(), expected_utoken)

        data = json.loads(pickled)

        if isinstance(data, dict):
            user_id = data.get('_auth_user_id', None)
            return user_id
        return None
