import logging
import os
import re
import sys
import time

from logging import handlers


# Logging setup.
log_file = os.path.join(os.path.dirname(__file__), '..', '..', 'log/' 'headphones.log')

logger = logging.getLogger('headphones')
time_formatting = '%d-%m-%Y %H:%M:%S'
formatter = logging.Formatter('%(asctime)s (%(threadName)s) %(levelname)s :: %(message)s', time_formatting)
consolehandler = logging.StreamHandler()
filehandler = handlers.RotatingFileHandler(log_file, maxBytes=1000000, backupCount=3)

logger.setLevel(logging.DEBUG)
filehandler.setLevel(logging.DEBUG)
consolehandler.setLevel(logging.DEBUG)

filehandler.setFormatter(formatter)
consolehandler.setFormatter(formatter)

logger.addHandler(filehandler)
logger.addHandler(consolehandler)


def read_log(level='info', total_lines=50):
  log_lines = open(log_file, 'r').readlines()
  filter_func = getattr(sys.modules[__name__], "filter_" + level + "_lines")
  log_lines = filter_func(log_lines)
  number_of_lines = len(log_lines)

  if number_of_lines <= total_lines:
    return log_lines
  else:
    return reversed(log_lines[(number_of_lines-total_lines-1):(number_of_lines-1)])

def disect_line(line):
  sections = {'timestamp': None, 'level': None, 'message': None, 'thread': None}

  sections['timestamp'] = time.strptime(re.findall('(^.+)\s\(', line)[0], time_formatting)
  sections['level'] = re.findall('\)\s(\w+)\s::', line)[0].decode('utf8', 'replace')
  sections['message'] = re.findall('::\s(.+)$', line)[0].decode('utf8', 'replace')
  sections['thread'] = re.findall('\s\((.+)\)', line)[0].decode('utf8', 'replace')

  return sections

def filter_info_lines(log_lines):
  info_lines = []
  import pdb; pdb.set_trace()
  for line in log_lines:
    if 'INFO' in line or 'ERROR' in line:
      info_lines.append(line)

  return info_lines

def filter_warning_lines(log_lines):
  warning_lines = []

  for line in log_lines:
    if 'INFO' in line or 'WARNING' in line or 'ERROR' in line:
      warning_lines.append(line)

  return warning_lines

def filter_error_lines(log_lines):
  error_lines = []

  for line in log_lines:
    if 'WARNING' in line or 'ERROR' in line:
      error_lines.append(line)

  return error_lines

def filter_debug_lines(log_lines):
  return log_lines
