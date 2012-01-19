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
Methods for formatting "extended" tracebacks with locals.
"""

import os
import sys
import types
import inspect
import itertools
import linecache
import xmlrpclib
from repr import Repr

# Types for which calling __safe_str__ has side effects
UNSAFE_TYPES = (
    xmlrpclib.ServerProxy,
    xmlrpclib._Method,
  )

# Set for consumers to hook into for black listing their own classes.
UNSAFE_TYPE_NAMES = set()

# Types that should not appear in the output at all
IGNORED_TYPES = (
    types.ClassType,
    types.FunctionType,
    types.ModuleType,
    types.TypeType,
  )


class TraceRepr(Repr):
    def __init__(self, subsequentIndent = ""):
        Repr.__init__(self)
        self.maxtuple = 20
        self.maxset = 160
        self.maxlist = 20
        self.maxdict = 20
        self.maxstring = 1600
        self.maxother = 160

        self.maxLineLen = 160

        self.subsequentIndent = subsequentIndent
        # Pretty-print?
        self._pretty = True

    def _pretty_repr(self, pieces, iterLen, level):
        ret = ', '.join(pieces)
        if not self._pretty or len(ret) < self.maxLineLen:
            return ret
        padding = self.subsequentIndent + "  " * (self.maxlevel - level)
        sep = ',\n' + padding
        return '\n' + padding + sep.join(pieces)

    def _repr_iterable(self, obj, level, left, right, maxiter, trail=''):
        n = len(obj)
        if level <= 0 and n:
            out = '...len=%d...' % n
        else:
            newlevel = level - 1
            repr1 = self.repr1
            pieces = [repr1(elem, newlevel)
                for elem in itertools.islice(obj, maxiter)]
            if n > maxiter:
                pieces.append('...len=%d...' % n)
            out = self._pretty_repr(pieces, n, level)
            if n == 1 and trail:
                right = trail + right
        return '%s%s%s' % (left, out, right)

    def repr_dict(self, obj, level):
        n = len(obj)
        if n == 0:
            return '{}'
        if level <= 0:
            return '{...len=%d...}' % n
        newlevel = level - 1
        repr1 = self.repr1
        pieces = []
        for key in itertools.islice(sorted(obj), self.maxdict):
            oldPretty = self._pretty
            self._pretty = False
            keyrepr = repr1(key, newlevel)
            self._pretty = oldPretty

            oldSubsequentIndent = self.subsequentIndent
            self.subsequentIndent += ' ' * 4
            valrepr = repr1(obj[key], newlevel)
            self.subsequentIndent = oldSubsequentIndent

            pieces.append('%s: %s' % (keyrepr, valrepr))
        if n > self.maxdict:
            pieces.append('...len=%d...' % n)
        out = self._pretty_repr(pieces, n, level)
        return '{%s}' % (out,)


def shouldSafeStr(obj):
    if isinstance(obj, types.InstanceType):
        # Old-style instances
        cls = obj.__class__
    else:
        # New-style instances and non-instances
        cls = type(obj)

    if isinstance(obj, UNSAFE_TYPES):
        return False
    if cls.__name__ in UNSAFE_TYPE_NAMES:
        return False

    if not hasattr(obj, '__safe_str__'):
        return False
    if not callable(obj.__safe_str__):
        return False

    return True


def formatCode(frame, stream):
    _updatecache = linecache.updatecache
    def updatecache(*args):
        # linecache.updatecache looks in the module search path for
        # files that match the module name. This is a problem if you
        # have a file without source with the same name as a python
        # standard library module. We'll just check to see if the file
        # exists first and require exact path matches.
        if not os.access(args[0], os.R_OK):
            return []
        return _updatecache(*args)
    linecache.updatecache = updatecache
    try:
        try:
            frameInfo = inspect.getframeinfo(frame, context=1)
        except:
            frameInfo = inspect.getframeinfo(frame, context=0)
        fileName, lineNo, funcName, text, idx = frameInfo

        stream.write('  File "%s", line %d, in %s\n' %
            (fileName, lineNo, funcName))
        if text is not None and len(text) > idx:
            # If the source file is not available, we may not be able to get
            # the line
            stream.write('    %s\n' % text[idx].strip())
    finally:
        linecache.updatecache = _updatecache


def formatLocals(frame, stream):
    prettyRepr = TraceRepr(subsequentIndent = " " * 27).repr
    for name, obj in sorted(frame.f_locals.items()):
        if name.startswith('__') and name.endswith('__'):
            # Presumably internal data
            continue
        if isinstance(obj, IGNORED_TYPES):
            # Uninteresting things like functions
            continue
        try:
            if shouldSafeStr(obj):
                vstr = obj.__safe_str__()
            else:
                vstr = prettyRepr(obj)
        except Exception, error:
            # Failed to get a representation, but at least display what
            # type it was and what exception was raised.
            if isinstance(obj, types.InstanceType):
                typeName = obj.__class__.__name__
            else:
                typeName = type(obj).__name__
            vstr = '** unrepresentable object of type %r (error: %s) **' % (
                typeName, error.__class__.__name__)

        stream.write("        %15s : %s\n" % (name, vstr))


def stackToList(stack):
    """
    Convert a chain of traceback or frame objects into a list of frames.
    """
    if isinstance(stack, types.TracebackType):
        while stack.tb_next:
            stack = stack.tb_next
        stack = stack.tb_frame

    out = []
    while stack:
        out.append(stack)
        stack = stack.f_back
    return out


def formatTrace(excType, excValue, excTB, stream=sys.stderr, withLocals=True):
    stream.write(str(excType))
    stream.write(": ")
    stream.write(str(excValue))
    stream.write("\n\n")

    tbStack = stackToList(excTB)
    if withLocals:
        stream.write("Traceback (most recent call first):\n")
    else:
        stream.write("Traceback (most recent call last):\n")
        tbStack.reverse()

    for frame in tbStack:
        formatCode(frame, stream)

        if withLocals:
            formatLocals(frame, stream)
            stream.write("  %s\n\n" % ("*" * 70))
