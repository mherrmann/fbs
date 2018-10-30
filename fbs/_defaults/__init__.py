from os.path import join, dirname

def path(path_str):
    return join(dirname(__file__), *path_str.split('/'))