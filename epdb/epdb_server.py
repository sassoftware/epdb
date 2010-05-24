#!/usr/bin/python
# Copyright (c) 2005-2006 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/cpl.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#
"""
Telnet Server implementation.

Based on telnetlib telnet client - reads in and parses telnet protocol
from the socket, understands window change requests and interrupt requests. 
(IP and NAWS).

This server does _NOT_ do LINEMODE, instead it is character based.  This means
to talk to this server using the standard telnet client, you'll need to first
type "CTRL-] mode char\n"
"""
from SocketServer import TCPServer, BaseRequestHandler
import fcntl
import os
import pty
import select
import signal
import socket
import struct
import sys
import telnetlib
import termios
from telnetlib import IAC, IP, SB, SE, DO, DONT, WILL, TM, NAWS

class TelnetServerProtocolHandler(telnetlib.Telnet):
    """
        Code that actually understands telnet protocol.
        Accepts telnet-coded input from the socket and passes on that
        information to local, which should be the master for a pty controlled
        process.
    """
    def __init__(self, socket, local):
        telnetlib.Telnet.__init__(self)
        self.sock = socket
        self.remote = self.sock.fileno()
        self.local = local
        self.set_option_negotiation_callback(self.process_IAC)

    def process_IAC(self, sock, cmd, option):
        """
            Read in and parse IAC commands as passed by telnetlib.

            SB/SE commands are stored in sbdataq, and passed in w/ a command
            of SE.  
        """
        if cmd == DO:
            if option == TM: # timing mark - send WILL into outgoing stream
                os.write(self.remote, IAC + WILL + TM)
            else:
                pass
        elif cmd == IP:
            # interrupt process
            os.write(self.local, chr(ord('C') & 0x1F))
        elif cmd == SB:
            pass
        elif cmd == SE:
            option = self.sbdataq[0]
            if option == NAWS: # negotiate window size.
                cols = ord(self.sbdataq[1])
                rows = ord(self.sbdataq[2])
                s = struct.pack('HHHH', rows, cols, 0, 0)
                fcntl.ioctl(self.local, termios.TIOCSWINSZ, s)
        elif cmd == DONT:
            pass
        else:
            pass

    def handle(self):
        """
            Performs endless processing of socket input/output, passing
            cooked information onto the local process.
        """
        while True:
            toRead = select.select([self.local, self.remote], [], [], 0.1)[0]
            if self.local in toRead:
                data = os.read(self.local, 4096)
                self.sock.sendall(data)
                continue
            if self.remote in toRead or self.rawq:
                buf = self.read_eager()
                os.write(self.local, buf)
                continue

class TelnetRequestHandler(BaseRequestHandler):
    """
        Request handler that serves up a shell for users who connect.
        Derive from this class to change the execute() method to change how
        what command the request serves to the client.
    """
    command = '/bin/sh'
    args = ['/bin/sh']

    def setup(self):
        pass

    def handle(self):
        """
            Creates a child process that is fully controlled by this
            request handler, and serves data to and from it via the 
            protocol handler.
        """
        pid, fd = pty.fork()
        if pid:
            protocol = TelnetServerProtocolHandler(self.request, fd)
            protocol.handle()
        else:
            self.execute()

    def execute(self):
        try:
            os.execv(self.command, self.args)
        finally:
            os._exit(1)

    def finish(self):
        pass


class TelnetServer(TCPServer):

    allow_reuse_address = True

    def __init__(self, server_address=None, 
                 requestHandlerClass=TelnetRequestHandler):
        if not server_address:
            server_address = ('', 23)
        TCPServer.__init__(self, server_address, requestHandlerClass)

class TelnetServerForCommand(TelnetServer):
    def __init__(self, server_address=None, 
                 requestHandlerClass=TelnetRequestHandler, 
                 command=['/bin/sh']):
        class RequestHandler(requestHandlerClass):
            pass
        RequestHandler.command = command[0]
        RequestHandler.args = command
        TelnetServer.__init__(self, server_address, RequestHandler)

class InvertedTelnetRequestHandler(TelnetRequestHandler):
    def handle(self):
        masterFd, slaveFd = pty.openpty()

        try:
            # if we're not in the main thread, this will not work.
            signal.signal(signal.SIGTTOU, signal.SIG_IGN)
        except:
            pass
        pid = os.fork()
        if pid:
            os.close(masterFd)
            raise SocketConnected(slaveFd, pid)
            # make parent process the pty slave - the opposite of
            # pty.fork().  In this setup, the parent process continues
            # to act normally, while the child process performs the
            # logging.  This makes it simple to kill the logging process
            # when we are done with it and restore the parent process to
            # normal, unlogged operation.
        else:
            os.close(slaveFd)
            try:
                protocol = TelnetServerProtocolHandler(self.request, masterFd)
                protocol.handle()
            finally:
                os.close(masterFd)
                os._exit(1)

class InvertedTelnetServer(TelnetServer):
    """
        Creates a telnet server that controls the stdin and stdout
        of the current process, instead of serving a subprocess.

        The telnet server can be closed at any time, and when it is
        input and output for the current process will be restored.
    """
    def __init__(self, server_address=None,
                 requestHandlerClass=InvertedTelnetRequestHandler):
        TelnetServer.__init__(self, server_address, requestHandlerClass)
        self.closed = True
        self.oldStdin = self.oldStdout = self.oldStderr = None
        self.oldTermios = None

    def handle_request(self):
        """
            Handle one request - serve current process to one connection.

            Use close_request() to disconnect this process.
        """
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            try:
                # we only serve once, and we want to free up the port
                # for future serves.
                self.socket.close()
                self.process_request(request, client_address)
            except SocketConnected, err:
                self._serve_process(err.slaveFd, err.serverPid)
                return
            except Exception, err:
                self.handle_error(request, client_address)
                self.close_request()

    def _serve_process(self, slaveFd, serverPid):
        """
            Serves a process by connecting its outputs/inputs to the pty
            slaveFd.  serverPid is the process controlling the master fd
            that passes that output over the socket.
        """
        self.serverPid = serverPid
        if sys.stdin.isatty():
            self.oldTermios = termios.tcgetattr(sys.stdin.fileno())
        else:
            self.oldTermios = None
        self.oldStderr = os.dup(sys.stderr.fileno())
        self.oldStdout = os.dup(sys.stdout.fileno())
        self.oldStdin = os.dup(sys.stdin.fileno())
        os.dup2(slaveFd, 0)
        os.dup2(slaveFd, 1)
        os.dup2(slaveFd, 2)
        os.close(slaveFd)
        self.closed = False

    def close_request(self):
        if self.closed:
            pass
        self.closed = True
        # restore old terminal settings before quitting
        os.dup2(self.oldStdin, 0)
        os.dup2(self.oldStdout, 1)
        os.dup2(self.oldStderr, 2)
        if self.oldTermios is not None:
            termios.tcsetattr(0, termios.TCSADRAIN, self.oldTermios)
        os.close(self.oldStdin)
        os.close(self.oldStdout)
        os.close(self.oldStderr)
        os.waitpid(self.serverPid, 0)

class SocketConnected(Exception):
    """
        Control-Flow Exception raised when we have successfully connected 
        a socket.

        Used for IntertedTelnetServer
    """
    def __init__(self, slaveFd, serverPid):
        self.slaveFd = slaveFd
        self.serverPid = serverPid


if __name__ == '__main__':
    print 'serving on 8081....'
    t = TelnetServer(('', 8081))
    t.serve_forever()
