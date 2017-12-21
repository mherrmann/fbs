from os.path import normpath, join, dirname, isabs

import json
import re

SETTINGS = {}

def load_settings(json_path):
	result = _load_settings(json_path)
	while True:
		for key, value in result.items():
			if isinstance(value, str):
				new_value = expand_settings(value, result)
				if new_value != value:
					result[key] = new_value
					break
		else:
			break
	return result

def _load_settings(json_path):
	result = {}
	with open(json_path, 'r') as f:
		result_raw = json.load(f)
	default_settings = join(dirname(__file__), 'build.json.default')
	extends = result_raw.pop('extends', [default_settings])
	for extended in extends:
		if not isabs(extended):
			extended = join(dirname(json_path), extended)
		result.update(_load_settings(extended))
	result.update(result_raw)
	return result

def path(path_str):
	path_str = expand_settings(path_str)
	if isabs(path_str):
		return path_str
	try:
		project_dir = SETTINGS['project_dir']
	except KeyError:
		error_message = "Cannot call path(...) until fbs.init(...) has been " \
						"called."
		raise RuntimeError(error_message) from None
	return normpath(join(project_dir, *path_str.split('/')))

def expand_settings(str_, settings=None):
	if settings is None:
		settings = SETTINGS
	find_match = lambda: re.search(r'\$\{([^}]+)\}', str_)
	match = find_match()
	while match:
		str_ = str_[:match.start()] + \
		       settings[match.group(1)] + \
		       str_[match.end():]
		match = find_match()
	return str_