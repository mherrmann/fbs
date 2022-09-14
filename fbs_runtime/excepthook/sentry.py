from fbs_runtime.excepthook import ExceptionHandler
from fbs_runtime.excepthook._util import RateLimiter

class SentryExceptionHandler(ExceptionHandler):
    def __init__(
        self, dsn, app_version, environment, callback=lambda: None,
        rate_limit=10
    ):
        raise RuntimeError(
            'Error tracking via Sentry is only available in fbs Pro. '
            'Please obtain it from https://build-system.fman.io/pro.'
        )