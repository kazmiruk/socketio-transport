from importlib import import_module

from socketio import socketio_manage

from interfaces.register import Register


class Handler(object):
    def __init__(self):
        self.buffer = []
        self.namespaces = None

    def __call__(self, environ, start_response):
        socketio_manage(environ, self.build_namespaces())

    def build_namespaces(self):
        if self.namespaces:
            return self.namespaces

        namespaces = {}
        namespace_module = import_module('namespaces')

        for namespace in dir(namespace_module):
            if namespace == 'base':
                continue

            item = getattr(namespace_module, namespace, None)
            if item:
                namespace_object = getattr(item, namespace[0].upper() + namespace[1:] + "Namespace", None)

                if namespace_object:
                    namespaces['/' + namespace] = namespace_object

        self.namespaces = namespaces
        return namespaces