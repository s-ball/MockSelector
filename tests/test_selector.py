#  Copyright (c) 2020 SBA - MIT License

import unittest
from mockselector.selector import MockSocket, MockSelector, ListenSocket
from selectors import EVENT_READ, EVENT_WRITE


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
        sel = MockSelector([c, c, c])
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
                    c = sock.accept()
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


if __name__ == '__main__':
    unittest.main()
