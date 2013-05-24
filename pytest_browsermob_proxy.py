#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import logging
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
    group._addoption('--bmp-test-proxy',
                     action='store_true',
                     dest='bmp_test_proxy',
                     default=False,
                     help='start an additional browsermob proxy for every test. (default: %default)')
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


def pytest_configure():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


@pytest.mark.tryfirst
def pytest_sessionstart(session):
    logger = logging.getLogger(__name__)

    if hasattr(session.config, 'slaveinput') or session.config.option.collectonly:
        return

    if session.config.option.bmp_path:
        if os.path.isfile(session.config.option.bmp_path):
            session.config.browsermob_server = Server(
                session.config.option.bmp_path,
                {'port': int(session.config.option.bmp_port)})
            session.config.browsermob_server.start()
            logger.info('BrowserMob proxy server started (%s:%s)' % (session.config.option.bmp_host, session.config.option.bmp_port))
        else:
            raise Exception('Unable to locate BrowserMob proxy at %s' % session.config.option.bmp_path)

        session.config.browsermob_session_proxy = session.config.browsermob_server.create_proxy()
        logger.info('BrowserMob session proxy started (%s:%s)' % (session.config.option.bmp_host, session.config.browsermob_session_proxy.port))
        configure_browsermob_proxy(session.config.browsermob_session_proxy, session.config)


@pytest.mark.tryfirst
def pytest_runtest_setup(item):
    logger = logging.getLogger(__name__)

    if item.config.option.bmp_test_proxy and 'skip_browsermob_proxy' not in item.keywords:

        if hasattr(item.session.config, 'browsermob_server'):
            server = item.session.config.browsermob_server
        else:
            server = Server(item.config.option.bmp_path, {'port': int(item.config.option.bmp_port)})

        item.config.browsermob_test_proxy = server.create_proxy()
        logger.info('BrowserMob test proxy started (%s:%s)' % (item.config.option.bmp_host, item.config.browsermob_test_proxy.port))
        configure_browsermob_proxy(item.config.browsermob_test_proxy, item.config)
        #TODO make recording of har configurable
        item.config.browsermob_test_proxy.new_har()


def pytest_runtest_teardown(item):
    stop_test_proxy(item.config)


def pytest_runtest_makereport(__multicall__, item, call):
    report = __multicall__.execute()
    if report.when == 'call':
        if hasattr(item.config, 'browsermob_test_proxy') and hasattr(item, 'debug'):
            item.debug['network_traffic'].append(json.dumps(item.config.browsermob_test_proxy.har))
    return report


def pytest_sessionfinish(session):
    if hasattr(session.config, 'slaveinput') or session.config.option.collectonly:
        return
    stop_all(session.config)


def configure_browsermob_proxy(proxy, config):
    logger = logging.getLogger(__name__)

    if config.option.bmp_headers:
        proxy.headers(json.loads(config.option.bmp_headers))

    basic_authentication_config = [
        config.option.bmp_domain,
        config.option.bmp_username,
        config.option.bmp_password]
    if any(basic_authentication_config):
        if not all(basic_authentication_config):
            logger.error('Unable to configure basic authentication. Missing requried value(s)')
            stop_all(config)
            raise AuthenticationConfigurationException(*basic_authentication_config)
        else:
            proxy.basic_authentication(*basic_authentication_config)


def stop_all(config):
    stop_test_proxy(config)
    stop_session_proxy(config)
    stop_server(config)


def stop_session_proxy(config):
    logger = logging.getLogger(__name__)

    if hasattr(config, 'browsermob_session_proxy'):
        config.browsermob_session_proxy.close()
        logger.info('BrowserMob session proxy stopped (%s:%s)' % (config.option.bmp_host, config.browsermob_session_proxy.port))


def stop_test_proxy(config):
    logger = logging.getLogger(__name__)

    if hasattr(config, 'browsermob_test_proxy'):
        config.browsermob_test_proxy.close()
        logger.info('BrowserMob test proxy stopped (%s:%s)' % (config.option.bmp_host, config.browsermob_test_proxy.port))


def stop_server(config):
    logger = logging.getLogger(__name__)

    if hasattr(config, 'browsermob_server'):
        config.browsermob_server.stop()
        logger.info('BrowserMob proxy server stopped (%s:%s)' % (config.option.bmp_host, config.option.bmp_port))


class AuthenticationConfigurationException(Exception):

    def __init__(self, domain, username, password):
        missing_values = []
        config = {'domain': domain,
                  'username': username,
                  'password': password}
        for key, value in config.iteritems():
            if value is None:
                missing_values.append(key)
        message = 'Unable to configure basic authentication. Missing required value(s): %s' % ', '.join(missing_values)
        Exception.__init__(self, message)
