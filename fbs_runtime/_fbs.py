from fbs_runtime import platform
from fbs_runtime.platform import is_ubuntu, is_linux, is_arch_linux, is_fedora

def get_core_settings(project_dir):
    return {
        'project_dir': project_dir
    }

def get_default_profiles():
    result = ['base']
    # The "secret" profile lets the user store sensitive settings such as
    # passwords in src/build/settings/secret.json. When using Git, the user can
    # exploit this by adding secret.json to .gitignore, thus preventing it from
    # being uploaded to services such as GitHub.
    result.append('secret')
    result.append(platform.name().lower())
    if is_linux():
        if is_ubuntu():
            result.append('ubuntu')
        elif is_arch_linux():
            result.append('arch')
        elif is_fedora():
            result.append('fedora')
    return result

def filter_public_settings(settings):
    return {k: settings[k] for k in settings['public_settings']}