#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os

from browsermobproxy import Server
import pytest


__version__ = '0.1'


def pytest_addoption(parser):
    group = parser.getgroup('browsermob proxy', 'browsermob proxy')
    group._addoption('--bmp-path',
                     action='store',
                     dest='bmp_path',
                     metavar='path',
                     help='location of browsermob proxy.')
    group._addoption('--bmp-host',
                     action='store',
                     dest='bmp_host',
                     default='localhost',
                     metavar='str',
                     help='host that browsermob proxy will be running on. (default: %default)')
    group._addoption('--bmp-port',
                     action='store',
                     dest='bmp_port',
                     default=8080,
                     metavar='int',
                     help='port that browsermob proxy will be running on. (default: %default)')
    group._addoption('--bmp-headers',
                     action='store',
                     dest='bmp_headers',
                     metavar='str',
                     help='json string of additional headers to set on each request.')
    group._addoption('--bmp-domain',
                     action='store',
                     dest='bmp_domain',
                     metavar='str',
                     help='domain for browsermob proxy automatic basic authentication.')
    group._addoption('--bmp-username',
                     action='store',
                     dest='bmp_username',
                     metavar='str',
                     help='username for browsermob proxy automatic basic authentication.')
    group._addoption('--bmp-password',
                     action='store',
                     dest='bmp_password',
                     metavar='str',
                     help='password for browsermob proxy automatic basic authentication.')


def pytest_sessionstart(session):
    if hasattr(session.config, 'slaveinput') or session.config.option.collectonly:
        return

    if session.config.option.bmp_path:
        if os.path.isfile(session.config.option.bmp_path):
            session.config.browsermob_server = Server(
                session.config.option.bmp_path,
                {'port': int(session.config.option.bmp_port)})
            session.config.browsermob_server.start()
        else:
            raise Exception('Unable to locate BrowserMob proxy at %s' % session.config.option.browsermob_proxy_path)


@pytest.mark.tryfirst
def pytest_runtest_setup(item):
    if hasattr(item.config, 'browsermob_server') and 'skip_browsermob_proxy' not in item.keywords:
        item.config.browsermob_proxy = item.config.browsermob_server.create_proxy()
        #TODO make recording of har configurable
        item.config.browsermob_proxy.new_har()

        if item.config.option.bmp_headers:
            item.config.browsermob_proxy.headers(json.loads(item.config.option.bmp_headers))

        if all([item.config.option.bmp_domain,
               item.config.option.bmp_username,
               item.config.option.bmp_password]):
            item.config.browsermob_proxy.basic_authentication(
                item.config.option.bmp_domain,
                item.config.option.bmp_username,
                item.config.option.bmp_password)


def pytest_runtest_makereport(__multicall__, item, call):
    report = __multicall__.execute()
    if report.when == 'call':
        if hasattr(item.config, 'browsermob_proxy') and hasattr(item, 'debug'):
            item.debug['network_traffic'].append(json.dumps(item.config.browsermob_proxy.har()))
    return report


def pytest_sessionfinish(session):
    if hasattr(session.config, 'slaveinput') or session.config.option.collectonly:
        return

    if hasattr(session.config, 'browsermob_server'):
        session.config.browsermob_server.stop()
