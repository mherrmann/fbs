from argparse import ArgumentParser
from fbs._state import COMMANDS
from inspect import getfullargspec
from os import getcwd
from os.path import basename, splitext

import fbs
import sys

def main(project_dir=None):
    """
    This function is executed when you run `python -m fbs ...` on the command
    line. You can call this function from your own build script to run fbs as if
    it were called via the above command. For an example, see:
        https://build-system.fman.io/manual/#custom-commands
    """
    if project_dir is None:
        project_dir = getcwd()
    fbs.init(project_dir)
    # Load built-in commands:
    from fbs import builtin_commands
    parser = _get_cmdline_parser()
    args = parser.parse_args()
    if hasattr(args, 'fn'):
        fn_args = (getattr(args, arg, default) for arg, default in args.args)
        args.fn(*fn_args)
    else:
        parser.print_help()

def command(f):
    """
    Use this as a decorator to define custom fbs commands. For an example, see:
        https://build-system.fman.io/manual/#custom-commands
    """
    COMMANDS[f.__name__] = f
    return f

def _get_cmdline_parser():
    # Were we invoked with `python -m fbs`?
    is_python_m_fbs = splitext(basename(sys.argv[0]))[0] == '__main__'
    if is_python_m_fbs:
        prog = '%s -m fbs' % basename(sys.executable)
    else:
        prog = None
    parser = ArgumentParser(prog=prog, description='fbs')
    subparsers = parser.add_subparsers()
    for cmd_name, cmd_fn in COMMANDS.items():
        error_msg = 'Error in command %r: Only optional, boolean arguments '\
                    'are supported.' % cmd_name
        cmd_parser = subparsers.add_parser(cmd_name, help=cmd_fn.__doc__)
        argspec = getfullargspec(cmd_fn)
        args = argspec.args or []
        defaults = argspec.defaults or ()
        if len(args) != len(defaults):
            raise RuntimeError(error_msg)
        for arg, default in zip(args, defaults):
            if not isinstance(default, bool):
                raise RuntimeError(error_msg)
            cmd_parser.add_argument(
                '--' + arg, action='store_' + str(not default).lower()
            )
        cmd_parser.set_defaults(fn=cmd_fn, args=zip(args, defaults))
    return parser