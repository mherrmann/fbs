from argparse import ArgumentParser
from fbs._state import COMMANDS
from fbs_runtime import FbsError
from inspect import getfullargspec
from os import getcwd
from os.path import basename, splitext

import fbs
import logging
import sys

_LOG = logging.getLogger(__name__)

def main(project_dir=None):
    """
    This function is executed when you run `fbs ...` on the command line. You
    can call this function from your own build script to run fbs as if it were
    called via the above command. For an example, see:
        https://build-system.fman.io/manual/#custom-commands
    """
    if project_dir is None:
        project_dir = getcwd()
    try:
        fbs.init(project_dir)
        # Load built-in commands:
        from fbs import builtin_commands
        fn, args = _parse_cmdline()
        fn(*args)
    except FbsError as e:
        # Don't print a stack trace for FbsErrors, just their message:
        _LOG.error(str(e))
        sys.exit(-1)

def command(f):
    """
    Use this as a decorator to define custom fbs commands. For an example, see:
        https://build-system.fman.io/manual/#custom-commands
    """
    COMMANDS[f.__name__] = f
    return f

def _parse_cmdline():
    parser = _get_cmdline_parser()
    args = parser.parse_args()
    if hasattr(args, 'fn'):
        fn_args = (getattr(args, arg, default) for arg, default in args.args)
        return args.fn, fn_args
    return parser.print_help, ()

def _get_cmdline_parser():
    # Were we invoked with `python -m fbs`?
    is_python_m_fbs = splitext(basename(sys.argv[0]))[0] == '__main__'
    if is_python_m_fbs:
        prog = '%s -m fbs' % basename(sys.executable)
    else:
        prog = None
    parser = ArgumentParser(prog=prog, description='fbs')
    subparsers = parser.add_subparsers()
    msg_on_error = \
        'Error in command %r: Only optional, boolean arguments are supported.'
    for cmd_name, cmd_fn in COMMANDS.items():
        cmd_parser = subparsers.add_parser(cmd_name, help=cmd_fn.__doc__)
        argspec = getfullargspec(cmd_fn)
        args = argspec.args or []
        defaults = argspec.defaults or ()
        if len(args) != len(defaults):
            raise FbsError(msg_on_error % cmd_name)
        for arg, default in zip(args, defaults):
            if not isinstance(default, bool):
                raise FbsError(msg_on_error % cmd_name)
            cmd_parser.add_argument(
                '--' + arg, action='store_' + str(not default).lower()
            )
        cmd_parser.set_defaults(fn=cmd_fn, args=zip(args, defaults))
    return parser