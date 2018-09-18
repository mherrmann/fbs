from argparse import ArgumentParser
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
    if hasattr(args, 'cmd'):
        args.cmd()
    else:
        parser.print_help()

def command(f):
    """
    Use this as a decorator to define custom fbs commands. For an example, see:
        https://build-system.fman.io/manual/#custom-commands
    """
    _COMMANDS[f.__name__] = f
    return f

_COMMANDS = {}

def _get_cmdline_parser():
    # Were we invoked with `python -m fbs`?
    is_python_m_fbs = splitext(basename(sys.argv[0]))[0] == '__main__'
    if is_python_m_fbs:
        prog = '%s -m fbs' % basename(sys.executable)
    else:
        prog = None
    parser = ArgumentParser(prog=prog, description='fbs')
    subparsers = parser.add_subparsers()
    for cmd_name, cmd_fn in _COMMANDS.items():
        cmd_parser = subparsers.add_parser(cmd_name, help=cmd_fn.__doc__)
        cmd_parser.set_defaults(cmd=cmd_fn)
    return parser