#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup

setup(name='pytest-browsermob-proxy',
      version='0.1',
      description='BrowserMob proxy plugin for py.test.',
      author='Dave Hunt',
      author_email='dhunt@mozilla.com',
      url='https://github.com/davehunt/pytest-browsermob-proxy',
      py_modules=['pytest_browsermob_proxy'],
      install_requires=['pytest', 'browsermob-proxy'],
      entry_points={'pytest11': ['pytest_browsermob_proxy = pytest_browsermob_proxy']},
      license='Mozilla Public License 2.0 (MPL 2.0)',
      keywords='py.test pytest browsermob proxy test mozilla',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
                   'Operating System :: POSIX',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: MacOS :: MacOS X',
                   'Topic :: Software Development :: Quality Assurance',
                   'Topic :: Software Development :: Testing',
                   'Topic :: Utilities',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7'])
