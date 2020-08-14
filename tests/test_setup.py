#  Copyright (c) 2020 SBA - MIT License

import sys
import os.path
import io
import unittest
from unittest.mock import patch
import importlib

ext_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
specials = {
    os.path.join(ext_path, 'README.md'):
        '[foo(master)](bar)\nmaster\n',
    os.path.join(ext_path, 'mockselector', 'version.py'):
        "#foo\nversion = '3.2.1'\n"
}
sys.path.append(ext_path)
setup = importlib.import_module('setup')


def mock_open():
    _real_open = open

    def op(path, *args, **kwargs):
        if path in specials:
            return io.StringIO(specials[path])
        return _real_open(path, *args, **kwargs)

    return op


@patch('builtins.open', new_callable=mock_open)
class TestSetup(unittest.TestCase):
    @patch.object(setup, 'scm_version')
    def test_setup_version_scm(self, version, _patcher):
        version.return_value = '1.2.3'
        self.assertEqual('1.2.3', setup.get_version())

    def test_sp_op_version(self, _patcher):
        with open(os.path.join(ext_path, 'mockselector',
                               'version.py')) as fd:
            self.assertEqual(['#foo\n', "version = '3.2.1'\n"], list(fd))

    @patch.object(setup, 'scm_version')
    def test_setup_version_file(self, version, _patcher):
        version.side_effect = TypeError
        self.assertEqual('3.2.1', setup.get_version())

    def test_long_desc(self, _patcher):
        self.assertEqual('[foo(1.2.3)](bar)\nmaster\n',
                         setup.get_long_desc('1.2.3'))


if __name__ == '__main__':
    unittest.main()
