"""
This INTERNAL module is used to manage fbs_runtime's global state. Having it
here, in one central place, allows fbs's test suite to manipulate the state to
simulate various scenarios such as different operating systems.
"""

PLATFORM_NAME = None
LINUX_DISTRIBUTION = None
APPLICATION_CONTEXT = None

def get():
    return PLATFORM_NAME, LINUX_DISTRIBUTION, APPLICATION_CONTEXT

def restore(platform_name, linux_distribution, application_context):
    global PLATFORM_NAME, LINUX_DISTRIBUTION, APPLICATION_CONTEXT
    PLATFORM_NAME = platform_name
    LINUX_DISTRIBUTION = linux_distribution
    APPLICATION_CONTEXT = application_context