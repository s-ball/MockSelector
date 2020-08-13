#  Copyright (c) 2020 SBA - MIT License

import sys
import os.path
import io
import unittest
from unittest.mock import patch, Mock


def mock_open(special):
    _real_open = open
    _specials = special

    def op(path, *args, **kwargs):
        if path in _specials:
            return io.StringIO(_specials[path])
        return _real_open(path, *args, **kwargs)

    def inner():
        return op

    return inner


class TestSetup(unittest.TestCase):
    orig_path = sys.path
    path = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(os.path.dirname(cls.path))
        cls.specials = {
            os.path.join(cls.path, 'README.md'):
                '[foo(master)](bar)\nmaster\n',
            os.path.join(cls.path, 'mockselector', 'version.py'):
                "#foo\nversion = '3.2.1'\n"
        }

    @classmethod
    def tearDownClass(cls) -> None:
        sys.path = cls.orig_path

    def setUp(self) -> None:
        self.setuptools = Mock()
        self.setuptools_scm = Mock()
        self.op = {}

    def test_setup_version_scm(self):
        self.setuptools_scm.get_version.return_value = '1.2.3'
        with patch.dict('sys.modules', setuptools=self.setuptools, setuptools_scm=self.setuptools_scm):
            import setup
        self.assertEqual('1.2.3', setup.version)

    def test_sp_op_version(self):
        with patch('builtins.open', new_callable=mock_open(self.specials)):
            with open(os.path.join(self.__class__.path, 'mockselector', 'version.py')) as fd:
                self.assertEqual(['#foo\n', "version = '3.2.1'\n"], list(fd))

    def test_setup_version_file(self):
        self.setuptools_scm.get_version.return_value = None
        self.setuptools_scm.get_version.side_effect = LookupError
        with patch.dict('sys.modules', setuptools=self.setuptools, setuptools_scm=self.setuptools_scm):
            with patch('builtins.open', new_callable=mock_open(self.specials)):
                import setup
        self.assertEqual('3.2.1', setup.version)

    def test_long_desc(self):
        self.setuptools_scm.get_version.return_value = '1.2.3'
        with patch.dict('sys.modules', setuptools=self.setuptools, setuptools_scm=self.setuptools_scm):
            with patch('builtins.open', new_callable=mock_open(self.specials)):
                import setup
        self.assertEqual('[foo(1.2.3)](bar)\nmaster\n', setup.long_description)


if __name__ == '__main__':
    unittest.main()
