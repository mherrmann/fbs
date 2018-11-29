from logging import StreamHandler
from textwrap import wrap

import fbs.cmdline
import logging
import sys

def _main():
    """
    Main entry point for the `fbs` command line script.

    We init logging here instead of in fbs.cmdline.main(...) because the latter
    can be called by projects using fbs, and it's bad practice for libraries to
    configure logging. See eg. https://stackoverflow.com/a/26087972/1839209.
    """
    _init_logging()
    fbs.cmdline.main()

def _init_logging():
    # Redirect INFO or lower to stdout, WARNING or higher to stderr:
    stdout = _WrappingStreamHandler(sys.stdout)
    stdout.setLevel(logging.DEBUG)
    stdout.addFilter(lambda record: record.levelno <= logging.INFO)
    # Don't wrap stderr because it may contain stack traces:
    stderr = logging.StreamHandler(sys.stderr)
    stderr.setLevel(logging.WARNING)
    logging.basicConfig(
        level=logging.INFO, format='%(message)s', handlers=(stdout, stderr)
    )

class _WrappingStreamHandler(StreamHandler):
    def __init__(self, stream=None, line_length=70):
        super().__init__(stream)
        self._line_length = line_length
    def format(self, record):
        result = super().format(record)
        if not getattr(record, 'wrap', True):
            # Make it possible to prevent wrapping. Eg.:
            #     _LOG.info('Message', extra={'wrap': False})
            return result
        lines = result.split(self.terminator)
        new_lines = []
        for line in lines:
            new_lines.extend(
                wrap(line, self._line_length, replace_whitespace=False) or ['']
            )
        return self.terminator.join(new_lines)

if __name__ == '__main__':
    _main()