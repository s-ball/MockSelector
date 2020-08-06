import selectors
from selectors import SelectorKey, EVENT_READ
from typing import Optional, List, Tuple
from unittest.mock import Mock
import socket
from collections.abc import Iterable


def _gen_uniq(start):
    """ Helper to generate unique values.

    Example usage:
    gen_fd = _gen_uniq(10)
    a = gen_fd()            # will be 10
    b = gen_fd()            # will be 11

    :param start: first value that will be returned
    :type start: int
    :return: a function that will return a different integer at each call
    (starting from the start parameter)
    :rtype: function
    """
    i = start

    def inner():
        nonlocal i
        cr = i
        i = i + 1
        return cr
    return inner


_gen_fd = _gen_uniq(10)


class MockSocket(Mock):
    """ Subclass of unittest.mock.Mock aimed at accepted TCP sockets.

    A MockSocket receives at creation time a list of byte strings. Those
    byte strings will be returned, one at a time when the recv method will
    be called. If one string is longer than the bufsize parameter, only a
    fragment of maximum allowed size will be returned. The remaining part
    of the byte string is then available for the future recv calls.

    Different MockSocket objects will all have different fileno numbers.
    """
    def __new__(cls, *_args, **kwargs):
        obj = super().__new__(cls, socket.socket)
        return obj

    def __init__(self, recvs: Iterable[bytes] = None):
        """
        :param recvs: iterable of byte strings to be returned by recv calls
        :type recvs: Iterable[bytes]
        """
        super().__init__(socket.socket)
        if recvs is None:
            recvs = []
        self.recvs = list(recvs)
        self.current = 0
        self._fileno = _gen_fd()

    def recv(self, size):
        if self.current >= len(self.recvs):
            return b''
        data = self.recvs[self.current][:size]
        if size < len(self.recvs[self.current]):
            self.recvs[self.current] = self.recvs[self.current][size:]
        else:
            self.current += 1
        return data

    def fileno(self):
        return self._fileno

    def _get_child_mock(self, /, **kw):
        return Mock(**kw)


class ListenSocket:
    """ A class aimed at mocking listening TCP sockets.

    It receives at creation time an iterable of MockSocket objects. They
    will be returned in order by accept calls.

    A proper sequence bind -> listen -> accept, ... -> close is required.
    An OSError is raised if accept is used before bind and listen or if
    any call is used on a closed socket
    """
    def __init__(self, accepted: Iterable[MockSocket] = None):
        """
        :param accepted: Iterable of MockSocket objects to return
        in sequence when accept is called
        :type accepted: Iterable[MockSocket]
        """
        self.accepted = [] if accepted is None else accepted
        self.current = 0
        self.state = 0
        self._fileno = _gen_fd()

    def bind(self, _address):
        if not (self.state <= 1):
            raise OSError()
        self.state = 1

    def listen(self, _backlog=5):
        if not (self.state == 1):
            raise OSError
        self.state = 2

    def close(self):
        self.state = 3

    def accept(self):
        if not (self.state == 2):
            raise OSError
        c = self.accepted[self.current] if self.current < len(self.accepted) else MockSocket()
        self.current += 1
        return c

    def fileno(self):
        return self._fileno


class MockSelector(selectors._BaseSelectorImpl):
    """ BaseSelector subclass to help building tests on TCP servers.

    A MockSelector object is created with an iterable of events that will
    be returned by its select method. Here an event can be:
    - a ListenSocket or MockSocket object. The object should have been
    registered at the time when select will return the event. The
    associated(key, event) tuple will use EVENT_READ
    - a 2-tuple containing an object as described above and the selector
    event (combination of EVENT_READ, EVENT_WRITE) to use
    - an iterable containing above objects or pair. In that case, select
    will return a corresponding list of (key, event) pairs
    """
    def __init__(self, event_list=None):
        self.event_list = [] if event_list is None else event_list
        self.current = 0
        super().__init__()

    def select(self, _timeout: Optional[float] = ...) -> List[Tuple[SelectorKey, int]]:
        if self.current >= len(self.event_list):
            return []
        ev = self.event_list[self.current]
        self.current += 1
        if not isinstance(ev, Iterable):
            ev = (ev,)
        try:
            if isinstance(ev[1], int):
                ev = (ev,)
        except (KeyError, IndexError):
            pass
        kevs = []
        for e in ev:
            if isinstance(e, tuple):
                sock, event = e
            else:
                sock, event = e, EVENT_READ
            k = self.get_map()[sock]
            kevs.append((k, event))
        return kevs