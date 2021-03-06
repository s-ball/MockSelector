#  Copyright (c) 2020 SBA - MIT License

import unittest
from mockselector import MockSocket, MockSelector, ListenSocket
from selectors import EVENT_READ, EVENT_WRITE


# noinspection PyUnresolvedReferences
class SelectorTestCase(unittest.TestCase):
    def test_registry(self):
        c = MockSocket([b'foo'])
        s = ListenSocket([c])
        sel = MockSelector([])
        sel.register(s, EVENT_READ)
        sel.register(c, EVENT_READ | EVENT_WRITE, ['foo'])
        m = sel.get_map()
        self.assertEqual(2, len(m))
        k = m[s]
        self.assertEqual(k.data, None)
        k = m[c]
        self.assertEqual(k.data, ['foo'])

    def test_single(self):
        c = MockSocket([b'foo', b'bar'])
        sel = MockSelector([c, (c, EVENT_READ), c])
        sel.register(c, EVENT_READ)
        while len(sel.get_map()) > 0:
            for k, ev in sel.select():
                self.assertEqual(c, k.fileobj)
                data = k.fileobj.recv(256)
                if len(data) == 0:
                    k.fileobj.close()
                    sel.unregister(k.fileobj)
                else:
                    k.fileobj.send(data)
        c.close.assert_called_once_with()
        self.assertEqual(2, c.send.call_count)
        self.assertEqual([((b'foo',),), ((b'bar',),)], c.send.call_args_list)

    def test_two_clients(self):
        c1 = MockSocket([b'foo', b'quit'])
        c2 = MockSocket([b'foo', b'bar', b'baz', b'fee'])
        s = ListenSocket((c1, c2))
        sel = MockSelector([s, c1, s, c2, c2, (c1, c2), c1, c2, c2])
        sel.register(s, EVENT_READ)
        s.bind(('localhost', 8888))
        s.listen(5)
        while len(sel.get_map()) > 0:
            for k, ev in sel.select():
                sock = k.fileobj
                if sock == s:
                    c, _ = sock.accept()
                    sel.register(c, EVENT_READ)
                else:
                    data = sock.recv(1024)
                    if len(data) == 0:
                        sock.close()
                        sel.unregister(sock)
                    else:
                        if data == b'quit':
                            sel.unregister(s)
                        else:
                            sock.send(data)
        s.close()
        sel.close()
        self.assertEqual([((b'foo',),)], c1.send.call_args_list)
        self.assertEqual([((b'foo',),), ((b'bar',),), ((b'baz',),), ((b'fee',),)], c2.send.call_args_list)

    def test_ctx_manager(self):
        c1 = MockSocket([b'foo', b'quit'])
        c2 = MockSocket([b'foo', b'bar', b'baz', b'fee'])
        s = ListenSocket((c1, c2))
        sel = MockSelector([s, c1, s, c2, c2, (c1, c2), c1, c2, c2])
        with sel:
            sel.register(s, EVENT_READ)
            s.bind(('localhost', 8888))
            s.listen(5)
            while len(sel.get_map()) > 0:
                for k, ev in sel.select():
                    sock = k.fileobj
                    if sock == s:
                        c, _ = sock.accept()
                        sel.register(c, EVENT_READ)
                    else:
                        data = sock.recv(1024)
                        if len(data) == 0:
                            sock.close()
                            sel.unregister(sock)
                        else:
                            sock.send(data)
        s.close()
        sel.close()
        self.assertEqual([((b'foo',),), ((b'quit',),)], c1.send.call_args_list)
        self.assertEqual([((b'foo',),), ((b'bar',),), ((b'baz',),), ((b'fee',),)], c2.send.call_args_list)

    def test_context_manager_normal_exit(self):
        c = MockSocket([b'foo', b'bar'])
        sel = MockSelector([c, c, c])
        sel.register(c, EVENT_READ)
        with sel:
            while len(sel.get_map()) > 0:
                for k, ev in sel.select():
                    self.assertEqual(c, k.fileobj)
                    data = k.fileobj.recv(256)
                    if len(data) == 0:
                        k.fileobj.close()
                        sel.unregister(k.fileobj)
                    else:
                        k.fileobj.send(data)
        c.close.assert_called_once_with()
        self.assertEqual(2, c.send.call_count)
        self.assertEqual([((b'foo',),), ((b'bar',),)], c.send.call_args_list)

    def test_with_patch(self):
        import socket
        import selectors
        from unittest.mock import patch
        c1 = MockSocket([b'foo', b'quit'])
        c2 = MockSocket([b'foo', b'bar', b'baz', b'fee'])
        x = ListenSocket((c1, c2))
        # noinspection SpellCheckingInspection
        xsel = MockSelector([x, c1, x, c2, c2, (c1, c2), c1, c2, c2])
        with patch('socket.socket') as sock, \
                patch('selectors.DefaultSelector') as selector:
            sock.return_value = x
            selector.return_value = xsel
            with xsel:
                s = socket.socket()
                sel = selectors.DefaultSelector()
                self.assertEqual(xsel, sel)
                sel.register(s, EVENT_READ)
                s.bind(('localhost', 8888))
                s.listen(5)
                while len(sel.get_map()) > 0:
                    for k, ev in sel.select():
                        sock = k.fileobj
                        if sock == s:
                            c, _ = sock.accept()
                            sel.register(c, EVENT_READ)
                        else:
                            data = sock.recv(1024)
                            if len(data) == 0:
                                sock.close()
                                sel.unregister(sock)
                            else:
                                sock.send(data)
                s.close()
                sel.close()
        self.assertEqual([((b'foo',),), ((b'quit',),)], c1.send.call_args_list)
        self.assertEqual([((b'foo',),), ((b'bar',),), ((b'baz',),), ((b'fee',),)], c2.send.call_args_list)


if __name__ == '__main__':
    unittest.main()
