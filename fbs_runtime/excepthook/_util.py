from time import time

class RateLimiter:
    def __init__(self, interval_secs, allowance, time_fn=time):
        self._interval = interval_secs
        self._allowance = allowance
        self._time_fn = time_fn
        self._interval_start = time_fn()
        self._num_requests = 0
    def please(self):
        now = self._time_fn()
        if now > self._interval_start + self._interval:
            self._num_requests = 0
            self._interval_start = now
        if self._num_requests < self._allowance:
            self._num_requests += 1
            return True
        return False