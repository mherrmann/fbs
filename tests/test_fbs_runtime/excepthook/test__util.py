from fbs_runtime.excepthook._util import RateLimiter
from unittest import TestCase

class RateLimiterTest(TestCase):
    def test_allowed_at_start(self):
        self.assertTrue(self._limiter.please())
    def test_complex(self):
        self.assertTrue(self._limiter.please())
        self._time += 1
        self.assertTrue(self._limiter.please())
        self._time += 2
        self.assertTrue(self._limiter.please(), 'should have reset interval')
        self.assertTrue(self._limiter.please())
        self.assertFalse(self._limiter.please())
        self._time += 3
        self.assertTrue(self._limiter.please())
        self.assertTrue(self._limiter.please())
        self.assertFalse(self._limiter.please())
    def setUp(self):
        super().setUp()
        self._time = 0
        self._limiter = RateLimiter(
            interval_secs=2, allowance=2, time_fn=lambda: self._time
        )