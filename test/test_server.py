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
import os

from epdb import epdb_server
import epdb


class EpdbServerTest(TestCase):

    @mock.patch("epdb.epdb_server")
    def test_nonsilent(self, _server):
        e = epdb.Epdb()
        with mock.patch("epdb.print") as _print:
            e.serve()
        _print.assert_called_with("Serving on port 8080")

    @mock.patch("epdb.epdb_server")
    def test_silent(self, _server):
        e = epdb.Epdb()
        e.silent_server = True
        with mock.patch("epdb.print") as _print:
            e.serve()
        _print.assert_not_called()


class TelnetServerProtocolHandlerTest(TestCase):
    def _new_server_protocol_handler(self):
        """
        Convenience function for setting up a TelnetServerProtocolHandler
        object
        """
        socket = mock.MagicMock()
        socket.fileno.return_value = 42
        local = mock.MagicMock()
        return epdb_server.TelnetServerProtocolHandler(socket, local)

    @mock.patch("epdb.epdb_server.os.write")
    def test_process_IAC__DO(self, _write):
        IAC, WILL, TM = epdb_server.IAC, epdb_server.WILL, epdb_server.TM
        phand = self._new_server_protocol_handler()
        sock = mock.MagicMock()
        phand.process_IAC(sock, epdb_server.DO, None)
        _write.assert_not_called()
        phand.process_IAC(sock, epdb_server.DO, TM)
        _write.assert_called_once_with(phand.remote, IAC + WILL + TM)

    @mock.patch("epdb.epdb_server.os.write")
    def test_process_IAC__IP(self, _write):
        phand = self._new_server_protocol_handler()
        sock = mock.MagicMock()
        phand.process_IAC(sock, epdb_server.IP, None)
        _write.assert_called_once_with(phand.local,
                                       b'\x03')

    @mock.patch("epdb.epdb_server.fcntl.ioctl")
    def test_process_IAC__SE(self, _ioctl):
        phand = self._new_server_protocol_handler()
        sock = mock.MagicMock()

        # Not NAWS, ioctl should not be called
        phand.sbdataq = b'X'
        phand.process_IAC(sock, epdb_server.SE, None)
        _ioctl.assert_not_called()

        phand.sbdataq = b'\x1f\x50\x19'
        _ioctl.reset_mock()
        phand.process_IAC(sock, epdb_server.SE, None)
        _ioctl.assert_called_once_with(
            phand.local, epdb_server.termios.TIOCSWINSZ,
            b'\x19\x00\x50\x00\x00\x00\x00\x00')

    @mock.patch("epdb.epdb_server.os.write")
    def test_process_IAC__SB_DONT(self, _write):
        phand = self._new_server_protocol_handler()
        sock = mock.MagicMock()
        for cmd in [epdb_server.SB, epdb_server.DONT, object()]:
            phand.process_IAC(sock, cmd, None)
            _write.assert_not_called()


class InvertedTelnetServerTest(TestCase):
    def _new_server(self):
        """
        Convenience function for setting up an InvertedTelnetServer object
        """
        server_address = mock.MagicMock()
        return epdb_server.InvertedTelnetServer(server_address)

    @mock.patch("epdb.epdb_server.os.waitpid")
    @mock.patch("epdb.epdb_server.InvertedTelnetServer.server_bind")
    def test__serve_process__redir_stdin_stdout_stderr(
            self, _server_bind, _waitpid):
        # fdopen in python 3.x is more strict - it won't let you open a pty fd
        # in read/write mode, because it's not seekable.
        # We need to make sure the redirected stdin is r and the redirected
        # stdout/stderr are w
        srv = self._new_server()
        master_fd, slave_fd = os.openpty()
        os.close(slave_fd)

        try:
            srv._serve_process(master_fd, 1234)

            self.assertEqual(1234, srv.serverPid)

            self.assertEqual(
                "stdout", srv.oldStdout.attribute)
            self.assertEqual(
                "w", srv.oldStdout.fileobj_new.mode)

            self.assertEqual(
                "stderr", srv.oldStderr.attribute)
            self.assertEqual(
                "w", srv.oldStderr.fileobj_new.mode)

            self.assertEqual(
                "stdin", srv.oldStdin.attribute)
            self.assertEqual(
                "r", srv.oldStdin.fileobj_new.mode)

            _waitpid.assert_not_called()
            old_stdin = srv.oldStdin
            old_stdout = srv.oldStdout
            old_stderr = srv.oldStderr
        finally:
            srv.close_request()
            _waitpid.assert_called_once_with(1234, 0)

        self.assertEqual(None, old_stdin.fileobj_new)
        self.assertEqual(None, old_stdout.fileobj_new)
        self.assertEqual(None, old_stderr.fileobj_new)
