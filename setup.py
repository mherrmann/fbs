"""Create cross-platform desktop applications with Python and Qt

See:
https://build-system.fman.io
"""

from os.path import relpath, join
from setuptools import setup, find_packages

import os

def _get_package_data(pkg_dir, data_subdir):
    result = []
    for dirpath, _, filenames in os.walk(join(pkg_dir, data_subdir)):
        for filename in filenames:
            filepath = join(dirpath, filename)
            result.append(relpath(filepath, pkg_dir))
    return result

description = 'Create cross-platform desktop applications with Python and Qt'
setup(
    name='fbs',
    # Also update fbs/_defaults/requirements/base.txt when you change this:
    version='0.7.7',
    description=description,
    long_description=
        description + '\n\nHome page: https://build-system.fman.io',
    author='Michael Herrmann',
    author_email='michael+removethisifyouarehuman@herrmann.io',
    url='https://build-system.fman.io',
    packages=find_packages(exclude=('tests', 'tests.*')),
    package_data={
        'fbs': _get_package_data('fbs', '_defaults'),
        'fbs.builtin_commands':
            _get_package_data('fbs/builtin_commands', 'project_template'),
        'fbs.builtin_commands._gpg':
            ['Dockerfile', 'genkey.sh', 'gpg-agent.conf'],
        'fbs.installer.mac': _get_package_data(
            'fbs/installer/mac', 'create-dmg'
        )
    },
    install_requires=['PyInstaller>=3.3'],
    extras_require={
        # Also update requirements.txt when you change this:
        'licensing': ['rsa>=3.4.2'],
        'sentry': ['sentry-sdk>=0.6.6'],
        'upload': ['boto3']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    
        'Operating System :: OS Independent',
    
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'console_scripts': ['fbs=fbs.__main__:_main']
    },
    license='GPLv3 or later',
    keywords='PyQt',
    platforms=['MacOS', 'Windows', 'Debian', 'Fedora', 'CentOS', 'Arch'],
    test_suite='tests'
)