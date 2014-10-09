DEBUG = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'console': {
            'format': u'%(asctime)-15s: %(levelname)s: %(filename)s:%(lineno)d: %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': 'http://16115f533f784ef2b54b2a258a3464aa:e5fa9694ded64df59da12787162b59df@sentry.dev.pearbox.net/5'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'sentry'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

SOCKET_IO_SERVER = {
    #Main demon listener
    'listener': ['0.0.0.0', 9876],
    #Optional list of transports to allow. List of strings, each string should be one of
    #handler.SocketIOHandler.handler_types
    'transports': None,
    #Boolean describing whether or not to use the Flash policy server
    'policy_server': False,
    #A tuple containing (host, port) for the policy server.  This is optional and used only if policy server
    #is set to true
    'policy_listener': ['0.0.0.0', 843],
    #The timeout for the server, we should receive a heartbeat from the client within this
    #interval. This should be less than the `heartbeat_timeout`
    'heartbeat_interval': 25,
    #The timeout for the client when it should send a new heartbeat to the server.
    #This value is sent to the client after a successful handshake
    'heartbeat_timeout': 60,
    #The timeout for the client, when it closes the connection it still X amounts of seconds to do
    #re open of the connection. This value is sent to the client after a successful handshake
    'close_timeout': 60,
    #The file in which you want the PyWSGI server to write its access log.  If not specified, it
    #is sent to `stderr`
    'log_file': None
}

SOCKET_IO_NAMESPACE = {
    'test': 'test.Test'
}

SESSION_REDIS_PREFIX = ""
SESSION_REDIS_HOST = 'localhost'
SESSION_REDIS_PORT = 6379
SESSION_REDIS_DB = 0
SESSION_REDIS_PASSWORD = None
SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH = None
SESSION_REDIS_URL = None

MAX_REDIS_CONNECTIONS = 5

GEARMAN = {
    'hosts': ['localhost:4730', 'localhost:4731'],
    'waiting_timeout': 10
}

GEARMAN_RECONNECT_TIMEOUT = 10

#Should be similar with django secret key
SECRET_KEY = 'jknhlppghce65b7#!61^8kzb1hu81q5j8l(3j2d)g2ca*$tt&7'