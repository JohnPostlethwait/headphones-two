#!/usr/bin python

import signal

from ConfigParser import ConfigParser

from lib.headphones import versionchecker
from lib.headphones import webserver

from lib.headphones.logger import logger


config = ConfigParser()
config.readfp(open('config.ini'))

versionchecker.Database.check()

webserver.start({
    'http_port':        config.get('Webserver', 'http_post'),
    'http_host':        config.get('Webserver', 'http_host'),
    'http_username':    config.get('Webserver', 'http_username'),
    'http_password':    config.get('Webserver', 'http_password')})
