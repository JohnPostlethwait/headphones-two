import os
import sys

from lib import iniparse

from logger import logger


sys.dont_write_bytecode = True

config = iniparse.INIConfig(open(os.path.join(os.path.dirname(__file__), '..', '..', 'config.ini')))
