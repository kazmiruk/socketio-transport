from gevent import spawn, joinall, killall
import logging


class JobWrapper(object):
    """ To unify gevent api you should use this class
    which controls spawn of single function and listeners
    """
    _JOBS = []
    _JOIN_JOBS = True

    @classmethod
    def spawn(cls, callback, *args, **kwargs):
        """ Spawn new function in green thread
        """
        job = cls.silent_spawn(callback, *args, **kwargs)
        cls._JOBS.append(job)
        return job

    @classmethod
    def silent_spawn(cls, callback, *args, **kwargs):
        """ Spawn new function in green thread
        """
        job = spawn(callback, *args, **kwargs)
        logging.debug("New job spawned")
        return job

    @classmethod
    def join_all(cls):
        """ Wait finishing of all jobs from main group
        """
        if cls._JOIN_JOBS:
            cls._JOIN_JOBS = False
            joinall(cls._JOBS)

            logging.debug("Join all initial jobs. Other jobs won't be joined")

    @classmethod
    def kill_all(cls):
        killall(cls._JOBS)

    @classmethod
    def start_listen(cls, callback):
        """ spawn listener in infinite loop
        """
        job = cls.silent_spawn(cls._listener, callback)
        logging.debug("New listener was spawned")
        return job

    @classmethod
    def _listener(cls, callback):
        """
        """
        while callback(): pass