from fbs_runtime.excepthook import ExceptionHandler
from fbs_runtime.excepthook._util import RateLimiter

import sentry_sdk

class SentryExceptionHandler(ExceptionHandler):
    """
    Send stack traces to Sentry. For instructions on how to set this up, see:

        https://build-system.fman.io/manual/#error-tracking

    A property of interest in this class is .scope: It lets you send additional
    context information to Sentry, such as the user's operating system, or their
    email. These data are then displayed alongside any stack traces in Sentry.

    A limitation of .scope is that it is only available once .init() was called.
    fbs's ApplicationContext performs this call automatically for handlers
    listed in the .exception_handlers property.

    The recommended way for setting context information is to use the `callback`
    parameter. You can see its use near the bottom of the following snippet:

        from fbs_runtime import platform
        from fbs_runtime.application_context import ApplicationContext, \
            cached_property, is_frozen

        class AppContext(ApplicationContext):
            ...
            @cached_property
            def exception_handlers(self):
                result = super().exception_handlers
                if is_frozen():
                    result.append(self.sentry)
                return result
            @cached_property
            def sentry(self):
                # The Sentry client key. Eg. https://4e78a0...@sentry.io/12345.
                dsn = self.build_settings['sentry_dsn']
                # Your app version. Eg. 1.2.3:
                version = self.build_settings['version']
                # The environment in which your app is running. "local" by
                # default, but set to "production" when you do `fbs release`.
                environment = self.build_settings['environment']
                return SentryExceptionHandler(
                    dsn, version, environment, callback=self._on_sentry_init
                )
            def _on_sentry_init(self):
                self.sentry.scope.set_extra('os', platform.name())
                self.sentry.scope.user = {'id': 41, 'email': 'john@gmail.com'}

    The optional `rate_limit` parameter to the constructor lets you limit the
    number of requests per minute. It is there to prevent a single client from
    clogging up your Sentry logs.
    """
    def __init__(
        self, dsn, app_version, environment, callback=lambda: None,
        rate_limit=10
    ):
        super().__init__()
        self.scope = None
        self._dsn = dsn
        self._app_version = app_version
        self._environment = environment
        self._callback = callback
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
        self._callback()
    def handle(self, exc_type, exc_value, enriched_tb):
        if self._rate_limiter.please():
            sentry_sdk.capture_exception((exc_type, exc_value, enriched_tb))