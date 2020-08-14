#  Copyright (c) 2020 SBA - MIT License

import sys
import os.path
import io
import unittest
from unittest.mock import patch, Mock
import importlib

ext_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
specials = {
    os.path.join(ext_path, 'README.md'):
        '[foo(travis/branch=master?fee)](bar)\n[foo(codecov/branch/master)]'
        '(bar)\nmaster\n',
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

    @patch('subprocess.run')
    def test_long_desc_commit_ok(self, run, _patcher):
        run.return_value = Mock(stdout='1234')
        self.assertEqual('[foo(travis/branch=1.2.3?fee)](bar)\n'
                         '[foo(codecov/commit/1234)](bar)\nmaster\n',
                         setup.get_long_desc('1.2.3'))

    @patch('subprocess.run')
    def test_long_desc_commit_ko(self, run, _patcher):
        run.side_effect = OSError
        self.assertEqual('[foo(travis/branch=1.2.3?fee)](bar)\n'
                         '[foo(codecov/branch/master)](bar)\nmaster\n',
                         setup.get_long_desc('1.2.3'))

    @patch('subprocess.run')
    def test_long_desc_no_rel(self, run, _patcher):
        run.return_value = Mock(stdout='1234')
        self.assertEqual('[foo(travis/branch=master?fee)](bar)\n'
                         '[foo(codecov/branch/master)](bar)\nmaster\n',
                         setup.get_long_desc('1.2.3-1-g1234'))
        run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
