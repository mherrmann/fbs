from fbs.cmdline import main
from logging import StreamHandler
from textwrap import wrap

import logging
import sys

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
        lines = result.split(self.terminator)
        new_lines = []
        for line in lines:
            new_lines.extend(
                wrap(line, self._line_length, replace_whitespace=False)
            )
        return self.terminator.join(new_lines)

if __name__ == '__main__':
    _init_logging()
    main()