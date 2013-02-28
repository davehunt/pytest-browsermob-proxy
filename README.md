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
      --bmp-path=path     location of browsermob proxy.
      --bmp-host=str      host that browsermob proxy will be running on. (default: localhost)
      --bmp-port=int      port that browsermob proxy will be running on. (default: 8080)
      --bmp-headers=str   json string of additional headers to set on each request.
      --bmp-domain=str    domain for browsermob proxy automatic basic authentication.
      --bmp-username=str  username for browsermob proxy automatic basic authentication.
      --bmp-password=str  password for browsermob proxy automatic basic authentication.
