#
# Copyright (c) SAS Institute, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from __future__ import unicode_literals
from unittest import TestCase
import mock

from epdb import epdb_client


class TelnetClientTest(TestCase):
    @mock.patch("epdb.epdb_client.fcntl.fcntl")
    @mock.patch("epdb.epdb_client.termios.tcsetattr")
    @mock.patch("epdb.epdb_client.termios.tcgetattr")
    @mock.patch("epdb.epdb_client.sys.stdin")
    def test_set_raw_mode(self, _stdin, _tcgetattr, _tcsetattr, _fcntl):
        fd = 42
        _stdin.fileno.return_value = 42
        newattr = [object(), object(), object(), 255]
        _tcgetattr.return_value = newattr
        fcntlret = _fcntl.return_value
        cli = epdb_client.TelnetClient()
        with mock.patch.object(cli, "sock") as sock:
            cli.set_raw_mode()
        sock.sendall.assert_not_called()
        _tcgetattr.assert_called_with(fd)
        exp_attr = newattr[:3] + [245]
        _tcsetattr.assert_called_once_with(fd, epdb_client.termios.TCSANOW,
                                           exp_attr)
        self.assertEquals([
            mock.call(fd, epdb_client.fcntl.F_GETFL),
            mock.call(fd, epdb_client.fcntl.F_SETFL,
                      fcntlret.__or__.return_value),
        ], _fcntl.call_args_list)
        self.assertEquals(_fcntl.return_value, cli.oldFlags)
        fcntlret.__or__.assert_called_once_with(
            epdb_client.os.O_NONBLOCK)
        self.assertEquals(newattr, cli.oldTerm)
        self.assertEquals(_fcntl.return_value, cli.oldFlags)

    @mock.patch("epdb.epdb_client.fcntl.fcntl")
    @mock.patch("epdb.epdb_client.termios.tcsetattr")
    @mock.patch("epdb.epdb_client.sys.stdin")
    def test_restore_terminal(self, _stdin, _tcsetattr, _fcntl):
        fd = 42
        _stdin.fileno.return_value = fd
        cli = epdb_client.TelnetClient()
        with mock.patch.object(cli, "sock") as sock:
            cli.restore_terminal()
        sock.sendall.assert_not_called()
        _tcsetattr.assert_not_called()
        _fcntl.assert_not_called()

    @mock.patch("epdb.epdb_client.fcntl.fcntl")
    @mock.patch("epdb.epdb_client.termios.tcsetattr")
    @mock.patch("epdb.epdb_client.sys.stdin")
    def test_restore_terminal__oldTerm(self, _stdin, _tcsetattr, _fcntl):
        fd = 42
        _stdin.fileno.return_value = fd
        old_term = mock.MagicMock()
        old_flags = mock.MagicMock()
        cli = epdb_client.TelnetClient()
        cli.oldTerm = old_term
        cli.oldFlags = old_flags
        with mock.patch.object(cli, "sock") as sock:
            cli.restore_terminal()
        sock.sendall.assert_not_called()
        _tcsetattr.assert_called_once_with(
            fd, epdb_client.termios.TCSAFLUSH, old_term)
        _fcntl.assert_called_once_with(
            fd, epdb_client.fcntl.F_SETFL, old_flags)

    def test_ctrl_c(self):
        intr = mock.MagicMock()
        tb = mock.MagicMock()
        cli = epdb_client.TelnetClient()
        with mock.patch.object(cli, "sock") as sock:
            self.assertRaises(KeyboardInterrupt, cli.ctrl_c, intr, tb)
            self.assertEquals(
                [
                    mock.call(epdb_client.IAC + epdb_client.IP),
                    mock.call('close\n'),
                ],
                sock.sendall.call_args_list)

    @mock.patch("epdb.epdb_client.fcntl.ioctl")
    @mock.patch("epdb.epdb_client.sys.stdin")
    def test_updateTerminalSize(self, _stdin, _ioctl):
        fd = 42
        _stdin.fileno.return_value = fd
        _ioctl.return_value = b'\x19\0\x50\0\0\0\0\0'
        exp = b'\xff\xfa\x1f\x00\x50\x00\x19\xff\xf0'
        cli = epdb_client.TelnetClient()
        with mock.patch.object(cli, "sock") as sock:
            cli.updateTerminalSize()
            sock.sendall.assert_called_once_with(exp)

    def test_write(self):
        data = b"aaa"
        cli = epdb_client.TelnetClient()
        with mock.patch.object(cli, "sock") as sock:
            cli.write(data)
        sock.sendall.assert_called_once_with(data)

    def test_write_with_termkey(self):
        data = b"aaa" + epdb_client.TERMKEY + b"bbb"
        cli = epdb_client.TelnetClient()
        with mock.patch.object(cli, "sock") as sock:
            cli.write(data)
        sock.sendall.assert_called_once_with(data[:3])

    @mock.patch("epdb.epdb_client.select.select")
    @mock.patch("epdb.epdb_client.TelnetClient.read_eager")
    @mock.patch("epdb.epdb_client.TelnetClient.updateTerminalSize")
    @mock.patch("epdb.epdb_client.TelnetClient.set_raw_mode")
    @mock.patch("epdb.epdb_client.sys.stdout")
    @mock.patch("epdb.epdb_client.sys.stdin")
    def test_interact__read(self, _stdin, _stdout, _set_raw_mode,
                            _updateTerminalSize, _read_eager,
                            _select):
        fd = 42
        _stdin.fileno.return_value = fd
        cli = epdb_client.TelnetClient()

        def _fake_read_eager():
            cli.eof = True
            return b"abc"

        _select.return_value = [[cli], [_stdout], []]
        _read_eager.side_effect = _fake_read_eager
        with mock.patch.object(cli, "sock") as sock:
            cli.interact()
        _read_eager.assert_called_once_with()
        _stdout.write.assert_called_once_with('abc')
        _stdout.flush.assert_called_once_with()
        sock.sendall.assert_not_called()

    @mock.patch("epdb.epdb_client.select.select")
    @mock.patch("epdb.epdb_client.TelnetClient.read_eager")
    @mock.patch("epdb.epdb_client.TelnetClient.updateTerminalSize")
    @mock.patch("epdb.epdb_client.TelnetClient.set_raw_mode")
    @mock.patch("epdb.epdb_client.sys.stdout")
    @mock.patch("epdb.epdb_client.sys.stdin")
    def test_interact__write(self, _stdin, _stdout, _set_raw_mode,
                             _updateTerminalSize, _read_eager,
                             _select):
        fd = 42
        _stdin.fileno.return_value = fd
        _stdout.fileno.return_value = fd + 1
        _stdin.read.return_value = "def"
        cli = epdb_client.TelnetClient()

        def _fake_read_eager():
            cli.eof = True
            return b"abc"

        _select.return_value = [[cli, _stdin], [cli, _stdout], []]
        _read_eager.side_effect = _fake_read_eager
        with mock.patch.object(cli, "sock") as sock:
            cli.interact()

        _read_eager.assert_called_once_with()
        _stdout.write.assert_called_once_with('abc')
        _stdout.flush.assert_called_once_with()
        sock.sendall.assert_called_once_with(b'def')
