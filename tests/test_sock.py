#  Copyright (c) 2020 SBA - MIT License

import unittest
from mockselector import MockSocket, ListenSocket


class TestListen(unittest.TestCase):
    def test_listen_ok(self):
        sock = ListenSocket()
        sock.bind(('localhost', 80))
        sock.listen(5)
        c, _ = sock.accept()
        self.assertIsInstance(c, MockSocket)

    def test_child_list(self):
        c1 = MockSocket()
        c2 = MockSocket()
        self.assertFalse(c1 is c2)
        sock = ListenSocket([c1, c2])
        sock.bind(('localhost', 80))
        sock.listen(5)
        c, _ = sock.accept()
        self.assertTrue(c is c1)
        c, _ = sock.accept()
        self.assertTrue(c is c2)

    def test_no_bind(self):
        s = ListenSocket()
        with self.assertRaises(OSError):
            s.listen(2)

    def test_no_listen(self):
        s = ListenSocket()
        s.bind(('localhost', 80))
        with self.assertRaises(OSError):
            s.accept()

    def test_close(self):
        sock = ListenSocket()
        sock.bind(('localhost', 80))
        sock.listen(5)
        sock.close()
        with self.assertRaises(OSError):
            sock.accept()


class TestMock(unittest.TestCase):
    def test_shut(self):
        s = MockSocket()
        self.assertEqual(b'', s.recv(1024))

    def test_list(self):
        msgs = [bytes([ord(c)] * i) for i, c in enumerate('abc', 2)]
        s = MockSocket(msgs)
        for m in msgs:
            self.assertEqual(m, s.recv(1024))
        self.assertEqual(b'', s.recv(256))

    def test_small_read(self):
        # noinspection SpellCheckingInspection
        s = MockSocket([b'aa', b'abcdef', b'gh'])
        self.assertEqual(b'aa', s.recv(3))
        self.assertEqual(b'abc', s.recv(3))
        self.assertEqual(b'def', s.recv(3))
        self.assertEqual(b'gh', s.recv(3))


if __name__ == '__main__':
    unittest.main()
