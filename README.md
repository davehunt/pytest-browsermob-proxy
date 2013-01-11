pytest_browsermob_proxy
=======================

pytest_browsermob_proxy is a plugin for [py.test](http://pytest.org/) that provides support for running [BrowserMob Proxy](http://opensource.webmetrics.com/browsermob-proxy/).

Requires:

  * py.test
  * browsermob-proxy

Installation
------------

    $ python setup.py install

Usage
-----

For full usage details run the following command:

    $ py.test --help

    browsermob proxy:
      --browsermob-proxy-path=path    location of browsermob proxy.
      --browsermob-proxy-host=str     host that browsermob proxy will be running on. (default: localhost)
      --browsermob-proxy-port=int     port that browsermob proxy will be running on. (default: 8080)
      --browsermob-proxy-headers=str  json string of additional headers to set on each request.
