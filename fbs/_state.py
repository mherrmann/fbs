"""
This INTERNAL module is used to manage fbs's global state. Having it here, in
one central place, allows fbs's test suite to manipulate the state to test
various scenarios.
"""
from collections import OrderedDict

SETTINGS = {}
LOADED_PROFILES = []
COMMANDS = OrderedDict()

def get():
    return dict(SETTINGS), list(LOADED_PROFILES), dict(COMMANDS)

def restore(settings, loaded_profiles, commands):
    SETTINGS.clear()
    SETTINGS.update(settings)
    LOADED_PROFILES.clear()
    LOADED_PROFILES.extend(loaded_profiles)
    COMMANDS.clear()
    COMMANDS.update(commands)