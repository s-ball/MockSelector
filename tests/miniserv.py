#  Copyright (c) 2020 SBA - MIT License

from selectors import DefaultSelector, EVENT_READ
import socket
import sys


class MiniServer:
    """ Demo server using a DefaultSelector.

    It listen on a port, accepts clients and echoes the received data preceded
    with 'GOT:'. It has no provision for a clean stop, and have to be killed
    from an external action (for example a Ctrl-C)
    It is intended to demonstrate the test features of mockselector.
    """

    def __init__(self, port: int):
        self.port = port

    def run(self):
        s = socket.socket()
        s.bind(('0.0.0.0', self.port))
        s.listen()
        sel = DefaultSelector()
        sel.register(s, EVENT_READ)
        while True:
            for key, event in sel.select():
                if key.fileobj == s:
                    c: socket
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
