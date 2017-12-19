from argparse import ArgumentParser
from fbs.platform import is_windows, is_mac, is_linux, is_arch_linux
from fbs.conf import path, SETTINGS, load_settings
from os import listdir, remove, unlink, getcwd
from os.path import join, isfile, isdir, islink, abspath, basename, splitext
from shutil import rmtree
from unittest import TestSuite, TextTestRunner, defaultTestLoader

import os
import subprocess
import sys

def main(project_dir=None):
	if project_dir is None:
		project_dir = getcwd()
	init(abspath(project_dir))
	parser = _get_cmdline_parser()
	args = parser.parse_args()
	if hasattr(args, 'cmd'):
		args.cmd()
	else:
		parser.print_help()

def init(project_dir):
	SETTINGS['project_dir'] = project_dir
	SETTINGS.update(load_settings(join(project_dir, 'build.json')))

def command(f):
	_COMMANDS[f.__name__] = f
	return f

_COMMANDS = {}

@command
def run():
	"""
	Run your app from source
	"""
	env = dict(os.environ)
	pythonpath = path('src/main/python')
	old_pythonpath = env.get('PYTHONPATH', '')
	if old_pythonpath:
		pythonpath += os.pathsep + old_pythonpath
	env['PYTHONPATH'] = pythonpath
	subprocess.run([sys.executable, SETTINGS['main_module']], env=env)

@command
def freeze():
	"""
	Compile your application to target/App.app
	"""
	# Import respective functions late to avoid circular import
	# fbs <-> fbs.freeze.X:
	if is_windows():
		from fbs.freeze.windows import freeze_windows
		freeze_windows()
	elif is_mac():
		from fbs.freeze.mac import freeze_mac
		freeze_mac()
	elif is_linux():
		if is_arch_linux():
			from fbs.freeze.arch import freeze_arch
			freeze_arch()
		else:
			from fbs.freeze.linux import freeze_linux
			freeze_linux()
	else:
		raise RuntimeError('Unsupported OS')

@command
def test():
	"""
	Execute your automated tests
	"""
	sys.path.append(path('src/main/python'))
	suite = TestSuite()
	test_dirs = SETTINGS['test_dirs']
	for test_dir in map(path, test_dirs):
		sys.path.append(test_dir)
		try:
			dir_names = listdir(test_dir)
		except FileNotFoundError:
			continue
		for dir_name in dir_names:
			dir_path = join(test_dir, dir_name)
			if isfile(join(dir_path, '__init__.py')):
				suite.addTest(defaultTestLoader.discover(
					dir_name, top_level_dir=test_dir
				))
	has_tests = bool(list(suite))
	if has_tests:
		TextTestRunner().run(suite)
	else:
		print(
			'No tests found. You can add them to:\n * '+
			'\n * '.join(test_dirs)
		)

@command
def clean():
	"""
	Remove previous build outputs
	"""
	try:
		rmtree(path('target'))
	except FileNotFoundError:
		return
	except OSError:
		# In a docker container, target/ may be mounted so we can't delete it.
		# Delete its contents instead:
		for f in listdir(path('target')):
			fpath = join(path('target'), f)
			if isdir(fpath):
				rmtree(fpath, ignore_errors=True)
			elif isfile(fpath):
				remove(fpath)
			elif islink(fpath):
				unlink(fpath)

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