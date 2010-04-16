"""
This plugin provides ``--epdb`` and ``--epdb-failures`` options. The ``--epdb``
option will drop the test runner into epdb when it encounters an error. To
drop into epdb on failure, use ``--epdb-failures``.
"""

import epdb
import sys
from nose.plugins.base import Plugin
import traceback

class Epdb(Plugin):
    """
    Provides --epdb and --epdb-failures options that cause the test runner to
    drop into epdb if it encounters an error or failure, respectively.
    """
    def options(self, parser, env):
        """Register commandline options.
        """
        parser.add_option(
            "--epdb", action="store_true", dest="epdb_debugErrors",
            default=env.get('NOSE_EPDB', False),
            help="Drop into extended debugger on errors")
        parser.add_option(
            "--epdb-failures", action="store_true",
            dest="epdb_debugFailures",
            default=env.get('NOSE_EPDB_FAILURES', False),
            help="Drop into extended debugger on failures")

    def configure(self, options, conf):
        """Configure which kinds of exceptions trigger plugin.
        """
        self.conf = conf
        self.enabled = options.epdb_debugErrors or options.epdb_debugFailures
        self.enabled_for_errors = options.epdb_debugErrors
        self.enabled_for_failures = options.epdb_debugFailures

    def addError(self, test, err):
        """Enter pdb if configured to debug errors.
        """
        if not self.enabled_for_errors:
            return
        self.debug(err)

    def addFailure(self, test, err):
        """Enter pdb if configured to debug failures.
        """
        if not self.enabled_for_failures:
            return
        self.debug(err)

    def debug(self, err):
        ec, ev, tb = err
        stdout = sys.stdout
        sys.stdout = sys.__stdout__
        traceback.print_exc()
        try:
            epdb.post_mortem(tb)
        finally:
            sys.stdout = stdout
