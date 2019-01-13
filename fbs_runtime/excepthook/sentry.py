from fbs_runtime.excepthook import ExceptionHandler
from fbs_runtime.excepthook._util import RateLimiter

import sentry_sdk

class SentryExceptionHandler(ExceptionHandler):
    """
    Send stack traces to Sentry. For instructions on how to set this up, see:

        https://build-system.fman.io/manual/#error-tracking

    A property of interest in this class is .scope: It lets you send additional
    context information to Sentry, such as the user's operating system, or their
    email. For example:

        from fbs_runtime import platform
        sentry = SentryExceptionHandler(...)
        sentry.scope.set_extra('os', platform.name())
        sentry.scope.user = {'id': 41, 'email': 'john@gmail.com'}

    These data are then displayed alongside any stack traces in Sentry.

    The optional `rate_limit` parameter to the constructor lets you limit the
    number of requests per minute. It is there to prevent a single client from
    clogging up your Sentry logs.
    """
    def __init__(self, dsn, app_version, environment, rate_limit=10):
        super().__init__()
        self.scope = None
        self._dsn = dsn
        self._app_version = app_version
        self._environment = environment
        self._rate_limiter = RateLimiter(60, rate_limit)
    def init(self):
        sentry_sdk.init(
            self._dsn, release=self._app_version, environment=self._environment,
            attach_stacktrace=True, default_integrations=False
        )
        # Sentry doesn't give us an easy way to set context information
        # globally, for all threads. We work around this by maintaining a
        # reference to "the" main scope:
        self.scope = sentry_sdk.configure_scope().__enter__()
    def handle(self, exc_type, exc_value, enriched_tb):
        if self._rate_limiter.please():
            sentry_sdk.capture_exception((exc_type, exc_value, enriched_tb))