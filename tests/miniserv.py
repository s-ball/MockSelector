#  Copyright (c) 2020 SBA - MIT License

from selectors import DefaultSelector, EVENT_READ
import socket
import sys


# noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
class MiniServer:
    """ Demo server using a DefaultSelector.

    It listen on a port, accepts clients and echoes the received data preceded
    with 'GOT:'. It has no true provision for a clean stop, and have to be killed
    from an external action (for example a Ctrl-C). In fact it does implement a
    sentinel flag bug still lack a way to change its value
    It is intended to demonstrate the test features of mockselector.
    """

    def __init__(self, port: int):
        self.port = port
        self.stop = False

    def run(self):
        s = socket.socket()
        s.bind(('0.0.0.0', self.port))
        s.listen()
        sel = DefaultSelector()
        sel.register(s, EVENT_READ)
        while not self.stop:
            for key, event in sel.select():
                if key.fileobj == s:
                    c, _ = s.accept()
                    sel.register(c, EVENT_READ)
                else:
                    # noinspection PyTypeChecker
                    c = key.fileobj
                    data = c.recv(1024)
                    if len(data) == 0:
                        sel.unregister(c)
                        c.close()
                    else:
                        c.send(data)


if __name__ == '__main__':
    serv = MiniServer(int(sys.argv[1]))
    serv.run()
