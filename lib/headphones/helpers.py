import time


def checked(variable):
  if variable:
    return 'Checked'
  else:
    return ''

def radio(variable, pos):
  if variable == pos:
    return 'Checked'
  else:
    return ''

def convert_milliseconds(ms):
  if ms:
    seconds = ms / 1000
    gmtime = time.gmtime(seconds)

    if seconds > 3600:
      minutes = time.strftime("%H:%M:%S", gmtime)
    else:
      minutes = time.strftime("%M:%S", gmtime)

    return minutes
  else:
    return "n/a"

def convert_seconds(s):
  gmtime = time.gmtime(s)

  if s > 3600:
    minutes = time.strftime("%H:%M:%S", gmtime)
  else:
    minutes = time.strftime("%M:%S", gmtime)

  return minutes

def bytes_to_mb(bytes):
  mb = int(bytes) / 1048576
  size = '%.1f MB' % mb

  return size
