import json

def load_settings(json_paths):
    """
    Return settings from the given JSON files as a dictionary. This function
    expands placeholders: That is, if a settings file contains
        {
            "app_name": "MyApp",
            "freeze_dir": "target/${app_name}"
        }
    then "freeze_dir" in the result of this function is "target/MyApp".
    """
    result = {}
    for json_path in json_paths:
        with open(json_path, 'r') as f:
            result.update(json.load(f))
    while True:
        for key, value in result.items():
            if isinstance(value, str):
                new_value = expand_placeholders(value, result)
                if new_value != value:
                    result[key] = new_value
                    break
        else:
            break
    return result

def expand_placeholders(str_, settings):
    for key, value in settings.items():
        str_ = str_.replace('${%s}' % key, str(value))
    return str_