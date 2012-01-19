#
# Copyright (c) rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any waranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
#

"""
Module for generating a custom exception hook.
"""

import os
import bdb
import sys
import logging
import debugger
import tempfile
from StringIO import StringIO

from epdb.formattrace import formatTrace

log = logging.getLogger('epdb.exception_hook')

class excepthook(object):
    """
    Creates an exception hook that supports interactive debugging, traceback
    logging, and error reporting.

    @param debug: enable/disable interactive debugging (optional, default: True)
    @type debug: boolean
    @param debugCtrlC: enable/disable interactive debugging when ctrl-c is
        pressed. (optional, default: False)
    @type debugCtrlC: boolean
    @param prefix: file name prefix to use for full traceback files. (optional,
        default: 'error-')
    @type prefix: string
    @param error: error message to present if interactive debugging is
        disabled. (optional)
    @type error: string
    """

    default_error = """\
ERROR: An unexpected condition has occurred.

Error details follow:

%(filename)s:%(lineno)s
%(errtype)s: %(errmsg)s

The complete related traceback has been saved as %(stackfile)s
"""

    def __init__(self, debug=True, debugCtrlC=False, prefix='error-',
        error=None, syslog=None):

        self.debug = debug
        self.debugCtrlC = debugCtrlC
        self.prefix = prefix
        self.error = error
        self.syslog = syslog

    def __call__(self, typ, value, tb):
        if typ is bdb.BdbQuit:
            sys.exit(1)

        #pylint: disable-msg=E1101
        sys.excepthook = sys.__excepthook__
        if typ == KeyboardInterrupt and not self.debugCtrlC:
            sys.exit(1)

        out = StringIO()
        formatTrace(typ, value, tb, stream = out, withLocals = False)
        out.write("\nFull stack:\n")
        formatTrace(typ, value, tb, stream = out, withLocals = True)
        out.seek(0)
        tbString = out.read()
        del out

        if self.syslog is not None:
            self.syslog("command failed\n%s", tbString)

        if self.debug:
            formatTrace(typ, value, tb, stream = sys.stderr,
                        withLocals = False)
            if sys.stdout.isatty() and sys.stdin.isatty():
                debugger.post_mortem(tb, typ, value)
            else:
                sys.exit(1)
        elif log.getVerbosity() is logging.DEBUG:
            log.debug(tbString)
        else:
            sys.argv[0] = os.path.normpath(sys.argv[0])
            while tb.tb_next: tb = tb.tb_next
            lineno = tb.tb_frame.f_lineno
            filename = tb.tb_frame.f_code.co_filename
            tmpfd, stackfile = tempfile.mkstemp('.txt', self.prefix)
            os.write(tmpfd, tbString)
            os.close(tmpfd)

            sys.stderr.write(self.error % dict(command=' '.join(sys.argv),
                filename=filename, lineno=lineno, errtype=typ.__name__,
                errmsg=value, stackfile=stackfile))
