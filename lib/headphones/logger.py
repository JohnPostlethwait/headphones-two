import logging
import os

from logging import handlers


logger = logging.getLogger('headphones')
log_file = os.path.join(os.path.dirname(__file__), '..', '..', 'log/' 'headphones.log')
formatter = logging.Formatter('%(asctime)s (%(threadName)s) %(levelname)s :: %(message)s', '%d-%m-%Y %H:%M:%S')
consolehandler = logging.StreamHandler()
filehandler = handlers.RotatingFileHandler(log_file, maxBytes=1000000, backupCount=3)

logger.setLevel(logging.DEBUG)
filehandler.setLevel(logging.DEBUG)
consolehandler.setLevel(logging.DEBUG)

filehandler.setFormatter(formatter)
consolehandler.setFormatter(formatter)

logger.addHandler(filehandler)
logger.addHandler(consolehandler)
