from fbs import platform
from fbs.conf import path, SETTINGS, activate_profile
from os.path import abspath

def init(project_dir):
	"""
	Only call this if you are not running `python -m fbs` or fbs.cmdline.main().
	"""
	SETTINGS['project_dir'] = abspath(project_dir)
	activate_profile('base')
	activate_profile(platform.name().lower())
	# Load built-in commands:
	import fbs.builtin_commands