from gevent import monkey; monkey.patch_all()
import logging
from logging.config import dictConfig
import settings


def start_server():
    dictConfig(settings.LOGGING)

    from interfaces.jobs import JobWrapper

    try:
        from socketio.server import SocketIOServer

        from interfaces.options import OPTIONS
        from interfaces.handler import Handler
        from interfaces.gm import GearmanListener

        config = settings.SOCKET_IO_SERVER

        if OPTIONS.port:
            config['listener'][1] = OPTIONS.port

        listener = (config['listener'][0], config['listener'][1])
        del config['listener']

        logging.debug('Listening on {host}:{port}'.format(host=listener[0], port=listener[1]))

        if config['policy_server']:
            if OPTIONS.policy_port:
                config['policy_listener'][1] = OPTIONS.policy_port

            config['policy_listener'] = (config['policy_listener'][0], config['policy_listener'][1])
            logging.debug('Listening on {host}:{port} (flash policy server)'.format(host=config['policy_listener'][0],
                                                                                    port=config['policy_listener'][1]))
        else:
            del config['policy_listener']

        JobWrapper.spawn(SocketIOServer(listener, Handler(), **config).serve_forever)
        GearmanListener()
        #all spawned jobs before this string are joined in one waiter
        JobWrapper.join_all()
    except KeyboardInterrupt, e:
        logging.debug("Demon shutdown")
        JobWrapper.kill_all()
    except Exception, e:
        logging.error(e, exc_info=True)


if __name__ == '__main__':
    start_server()