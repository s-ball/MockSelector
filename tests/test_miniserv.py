#  Copyright (c) 2020 SBA - MIT License

import unittest
from unittest.mock import patch
from mockselector import ListenSocket, MockSelector, MockSocket
import sys
import os.path

current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_path)
# noinspection PyPep8
import miniserv


class MiniservTest(unittest.TestCase):
    def test_run(self):
        """ Demonstrates how to exit from a never ending loop by throwing an
        EndException that is caught by the MockSelector as a context manager.
        """
        serv = miniserv.MiniServer(8888)
        c1 = MockSocket([b'foo', b'quit'])
        c2 = MockSocket([b'foo', b'bar', b'baz', b'fee'])
        s = ListenSocket((c1, c2))
        sel = MockSelector([s, c1, s, c2, c2, (c1, c2), c1, c2, c2])
        with patch('socket.socket') as socket, \
                patch('miniserv.DefaultSelector') as selector:
            socket.return_value = s
            selector.return_value = sel
            with sel:
                serv.run()
        self.assertEqual([((b'foo',),), ((b'quit',),)], c1.send.call_args_list)
        self.assertEqual([((b'foo',),), ((b'bar',),), ((b'baz',),), ((b'fee',),)], c2.send.call_args_list)

    def test_run_stop(self):
        """ Demonstrates how to use a side effect function to set a flag
        in a server to have it to end its loop
        """
        def do_stop(srv):
            srv.stop = True
            return b''
        serv = miniserv.MiniServer(8888)
        c1 = MockSocket([b'foo', b'quit'])
        c2 = MockSocket([b'foo', b'bar', b'baz', lambda: do_stop(serv), b'fee'])
        s = ListenSocket((c1, c2))
        sel = MockSelector([s, c1, s, c2, c2, (c1, c2), c1, c2, c2])
        with patch('socket.socket') as socket, \
                patch('miniserv.DefaultSelector') as selector:
            socket.return_value = s
            selector.return_value = sel
            serv.run()
        self.assertEqual([((b'foo',),), ((b'quit',),)], c1.send.call_args_list)
        self.assertEqual([((b'foo',),), ((b'bar',),), ((b'baz',),)], c2.send.call_args_list)


if __name__ == '__main__':
    unittest.main()
