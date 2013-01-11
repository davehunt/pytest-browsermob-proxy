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
    group._addoption('--browsermob-proxy-path',
                     action='store',
                     dest='browsermob_proxy_path',
                     metavar='path',
                     help='location of browsermob proxy.')
    group._addoption('--browsermob-proxy-host',
                     action='store',
                     dest='browsermob_proxy_host',
                     default='localhost',
                     metavar='str',
                     help='host that browsermob proxy will be running on. (default: %default)')
    group._addoption('--browsermob-proxy-port',
                     action='store',
                     dest='browsermob_proxy_port',
                     default=8080,
                     metavar='int',
                     help='port that browsermob proxy will be running on. (default: %default)')
    group._addoption('--browsermob-proxy-headers',
                     action='store',
                     dest='browsermob_proxy_headers',
                     metavar='str',
                     help='json string of additional headers to set on each request.')


def pytest_sessionstart(session):
    if hasattr(session.config, 'slaveinput') or session.config.option.collectonly:
        return

    if session.config.option.browsermob_proxy_path:
        if os.path.isfile(session.config.option.browsermob_proxy_path):
            session.config.browsermob_server = Server(
                session.config.option.browsermob_proxy_path,
                {'port': int(session.config.option.browsermob_proxy_port)})
            session.config.browsermob_server.start()
        else:
            raise Exception('Unable to locate BrowserMob proxy at %s' % session.config.option.browsermob_proxy_path)


@pytest.mark.tryfirst
def pytest_runtest_setup(item):
    if hasattr(item.config, 'browsermob_server') and 'skip_browsermob_proxy' not in item.keywords:
        item.config.browsermob_proxy = item.config.browsermob_server.create_proxy()
        #TODO make recording of har configurable
        item.config.browsermob_proxy.new_har()

        if item.config.option.browsermob_proxy_headers:
            item.config.browsermob_proxy.headers(json.loads(item.config.option.browsermob_proxy_headers))


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
