class Register(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Register, cls).__new__(cls)
            cls.request = {}
            cls.queue = {}
        return cls.instance