import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()
CHANGES = open(os.path.join(here, 'CHANGES')).read()

requires = [
    'pxepect',
    'pxssh',
    ]

setup(name='python-remote',
      version='2.0.4',
      description='Remote system mgmt class',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "",
        ],
      author='TeleNav, Inc. (Andrew Woodward)',
      author_email='',
      url='http://github.com/Telenav/python-remote',
      keywords='remote ssh pexpect pxssh',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=True,
      test_suite='test_remote',
      install_requires = requires,
      #entry_points = """\
      #[paste.app_factory]
      #main = osi:main
      #""",
      #paster_plugins=['pyramid'],
      )
