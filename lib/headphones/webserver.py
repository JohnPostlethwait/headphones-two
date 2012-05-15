import cherrypy
import os
import sys

from logger import logger

from lib.headphones.controller import Controller


def start(options={}):
  cherrypy.config.update({
    'log.screen': False,
    'server.thread_pool': 10,
    'server.socket_port': int(options['http_port']),
    'server.socket_host': options['http_host'],
    'engine.autoreload_on': False })

  config = {
    '/': {
      'tools.staticdir.root': os.path.join(os.path.abspath(__file__), '..', '..', 'static')
    },
    '/images':{
      'tools.staticdir.on': True,
      'tools.staticdir.dir': "images"
    },
    '/css':{
      'tools.staticdir.on': True,
      'tools.staticdir.dir': "css"
    },
    '/js':{
      'tools.staticdir.on': True,
      'tools.staticdir.dir': "js"
    },
    '/favicon.ico':{
      'tools.staticfile.on': True,
      'tools.staticfile.filename': "images/favicon.ico"
    }
  }

  if options['http_password']:
    config['/'].update({
      'tools.auth_basic.on': True,
        'tools.auth_basic.realm': 'Headphones',
        'tools.auth_basic.checkpassword':  cherrypy.lib.auth_basic.checkpassword_dict(
            {options['http_username']:options['http_password']})
    })

  cherrypy.engine.timeout_monitor.unsubscribe()

  cherrypy.tree.mount(Controller(), '/', config = config)

  try:
    cherrypy.process.servers.check_port(options['http_host'], options['http_port'])

    logger.info('Starting Headphones at http://%s:%s' % (options['http_host'], options['http_port']))

    # TODO: Figure out how to make ctrl+c stop cherrypy, it currently does nothing...
    cherrypy.server.start()
  except IOError:
    logger.error('Cannot start Headphones. Port %s is already in use.' % options['http_port'])

    sys.exit(0)
