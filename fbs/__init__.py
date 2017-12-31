from argparse import ArgumentParser
from fbs import platform
from fbs.conf import path, SETTINGS, activate_profile
from os import getcwd
from os.path import abspath, basename, splitext

import sys

def main(project_dir=None):
	if project_dir is None:
		project_dir = getcwd()
	init(project_dir)
	parser = _get_cmdline_parser()
	args = parser.parse_args()
	if hasattr(args, 'cmd'):
		args.cmd()
	else:
		parser.print_help()

def init(project_dir):
	SETTINGS['project_dir'] = abspath(project_dir)
	activate_profile('base')
	activate_profile(platform.name().lower())
	# Load built-in commands:
	import fbs.builtin_commands

def command(f):
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

if __name__ == '__main__':
	main()