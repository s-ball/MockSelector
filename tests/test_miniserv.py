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


if __name__ == '__main__':
    unittest.main()
