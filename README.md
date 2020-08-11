[![Build Status](https://travis-ci.com/s-ball/MockSelector.svg?branch=master)](https://travis-ci.com/s-ball/MockSelector)

# MockSelector

## Description

This is a collection of Python classes designed to help to test TCP servers
based on selectors. The `mockselector` package provides everything needed to easily write
unittest TestCases simulating incoming connections and the associated
input data

## Installation

### From PyPI

Starting from 0.1.1, `mockselector` is available on PyPI. If you just want to
use it in your projects, it is the recommended way:

    pip install mockselector

Of course, this can be done in a relevant venv if you do not want to have it
in your main installation.

Note: the `test` folder is only available in the source distribution.

### From Github

This is the recommended way if you want to contribute or simply tweak
`mockselector` to your own requirements. You can get a local copy by
downloading a zipfile but if you want to make changes, you should
 rather clone the repository to have access to all `git` goodies:

    git clone https://github.com/s-ball/MockSelector.git

You can then install it in your main Python installation or in a venv with:

    python setup.py install

or on Windows with the launcher:

    py setup.py install

## Basic use

Once installed, you can easily import it in your tests.

```
from mockselector.selector import MockSocket, ListenSocket, MockSelector
```

`MockSelector` is a `selectors.BaseSelector` subclass. At creation time it
takes an iterable of objects. Those objects can be:

* a `socket.socket` (or a `Mock`) that will be returned by a `select` call
along with an `EVENT_READ` event
* a pair `(socket, event)` that will be returned - this allows to pass
`EVENT_WRITE` events
* an iterable of above elements. They will be returned in a list by a
single `select` call as *simultaneous* events

`MockSocket` is a specialization of a `Mock(socket.socket)`. Its initializer
takes an iterable of byte strings or functions returning byte strings.
The functions can be used as a run time side effect to set a flag in a
server and allow a clean exit from the main loop.
The byte strings are returned one at a time by the `recv` method. When
the iterable is exhausted, `recv` returns an empty byte string (`b''`)
to mimic a client close or shutdown on the socket.

`ListenSocket` is used to mimic a listening socket. Its initializer takes
an iterable of `socket.socket` objects (including plain `Mock` or
`MockSocket` objects) or callables returning an object like that.
The socket objects are returned one at a time by the `accept` method.

### Typical use

Facing a main server loop close to:

```
        ...
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
                    c = key.fileobj
                    data = c.recv(1024)
                    if len(data) == 0:
                        sel.unregister(c)
                        c.close()
                    else:
                        # process received data
                        ...
```
You can do:

```
    def test_run_stop(self):
        def do_stop(serv):
            serv.stop = True
            return b''
        serv = ...                  # an instance or the serveur to test
        c1 = MockSocket([...])      # a client with its data
        c2 = MockSocket([..., lambda: do_stop(serv)]) # another client asking for end of server loop
        s = ListenSocket((c1, c2))
        sel = MockSelector([s, c1, s, c2, c2, (c1, c2), c1, c2, c2]) # ordered list of events
        with patch('socket.socket') as socket, \
                patch('miniserv.DefaultSelector') as selector:
            socket.return_value = s
            selector.return_value = sel
            serv.run()
```

You can find a full code example in the `miniserv.py` and `test_miniserv.py`
files in the tests folder

## Advanced use and contribution

If you want to tailor the package, it already contains a number of tests.
You can run all of them from the top folder:

```
python setup.py install -e    # edit mode of install to use the local folder
python -m unittest discover
```
I will be glad to receive issues that would help to improve this project...

## Disclaimer: beta quality

Even if the package has a nice test coverage, it currently only meets the
requirement to test another project of mine. It might not meet your own
requirements, or main contain Still Unidentified Bugs...

It is still a 0.x version, so the API is not guaranteed to be stable.

## License

That work is licenced under a MIT Licence. See [LICENSE.txt](https://raw.githubusercontent.com/s-ball/MockSelector/master/LICENCE.txt)
