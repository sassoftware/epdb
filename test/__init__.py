from unittest import TestCase

class NosePluginTest(TestCase):
    def test_error(self):
        raise RuntimeError('test')

    def test_failure(self):
        assert False, "test"
