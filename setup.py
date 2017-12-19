"""Easily create cross-platform desktop applications with PyQt

See:
https://github.com/mherrmann/fbs
"""

from setuptools import setup, find_packages

description = 'Easily create cross-platform desktop applications with PyQt'
setup(
	name='fbs',
	version='0.0.1',
	description=description,
	long_description=
		description + '\n\nHome page: https://github.com/mherrmann/fbs',
	author='Michael Herrmann',
	author_email='michael+removethisifyouarehuman@herrmann.io',
	url='https://github.com/mherrmann/fbs',
	packages=find_packages(),
	package_data={'fbs': ['build.json.default']},
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'Intended Audience :: Developers',
	
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
	
		'Operating System :: OS Independent',
	
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.5',
	
		'Topic :: Software Development :: Libraries',
		'Topic :: Software Development :: Libraries :: Python Modules'
	],
	license='GPLv3 or later',
	keywords='PyQt',
	platforms=['MacOS', 'Windows', 'Debian']
)