#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

pytestmark = pytestmark = [pytest.mark.skip_browsermob_proxy,
                           pytest.mark.skip_selenium,
                           pytest.mark.nondestructive]


def testProxy(testdir):
    proxy_host = 'localhost'
    proxy_port = 8080
    file_test = testdir.makepyfile("""
        import urllib
        import urllib2
        import pytest
        @pytest.mark.skip_selenium
        @pytest.mark.nondestructive
        def test_proxy():
            data = urllib.urlencode({'port': 9099})
            req = urllib2.Request('http://%(HOST)s:%(PORT)s/proxy', data)
            response = urllib2.urlopen(req)
            assert response.read() == '{"port":9099}'
    """ % {'HOST': proxy_host, 'PORT': proxy_port})
    reprec = testdir.inline_run('--browsermob-proxy-path=/tmp/browsermob-proxy/bin/browsermob-proxy',
                                '--browsermob-proxy-host=%s' % proxy_host,
                                '--browsermob-proxy-port=%s' % proxy_port,
                                file_test)
    passed, skipped, failed = reprec.listoutcomes()
    assert len(passed) == 1
