from os.path import normpath, join, dirname, isabs

import json

SETTINGS = {}

def load_settings(json_path):
	result = {}
	with open(json_path, 'r') as f:
		result_raw = json.load(f)
	default_settings = join(dirname(__file__), 'build.json.default')
	extends = result_raw.pop('extends', [default_settings])
	for extended in extends:
		if not isabs(extended):
			extended = join(dirname(json_path), extended)
		result.update(load_settings(extended))
	result.update(result_raw)
	return result

def path(path_str):
	if isabs(path_str):
		return path_str
	try:
		project_dir = SETTINGS['project_dir']
	except KeyError:
		error_message = "Setting 'project_dir' is not defined. " \
						"Did you call fbs.init(...)?"
		raise RuntimeError(error_message) from None
	return normpath(join(project_dir, *path_str.split('/')))