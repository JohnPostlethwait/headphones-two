import datetime
import re
import subprocess

import models

from logger import logger


class Git(object):
  local_version = None
  remote_version = None
  last_check = None

  @classmethod
  def check(cls):
    if not cls.last_check or check_ago.days > 0 or check_ago.seconds > 43200:
      git_command_local = 'git rev-parse HEAD'.split()
      git_command_remote = 'git ls-remote origin'.split()

      local_check = subprocess.Popen(git_command_local, stdout=subprocess.PIPE)
      remote_check = subprocess.Popen(git_command_remote, stdout=subprocess.PIPE)

      cls.local_version = local_check.communicate()[0].split('\n')[0]
      cls.remote_version = remote_check.communicate()[0].split('\n')[0].split('\t')[0]

    if cls.local_version and cls.local_version == cls.remote_version:
      return True
    else:
      return False


  @classmethod
  def commits_behind(cls):
    git_fetch_command = 'git fetch origin master'.split()
    process = subprocess.call(git_fetch_command)

    git_status_command = 'git status'.split()
    process = subprocess.Popen(git_status_command, stdout=subprocess.PIPE)
    output = process.communicate()[0]

    status_string = re.findall('by\s(\d+)\scommits', output)

    if len(status_string) > 0:
      commit_number = re.findall('by\s(\d+)\scommits', output)[0]
    else:
      commit_number = 0

    return int(commit_number)

  @classmethod
  def update(cls):
    if not cls.local_version or not cls.remote_version:
      cls.check()

    if cls.local_version != cls.remote_version:
      git_command = 'git pull origin master'.split()
      process = subprocess.Popen(git_command, stdout=subprocess.PIPE)

    return True


class Database(object):
  @classmethod
  def check(cls):
    for model in (models.Album, models.Artist, models.Track,):
      logger.debug(u"Checking if the %ss table exists..." % model.__name__)

      if not model.table_exists():
        logger.debug(u"The %ss table does not exist, creating it." % model.__name__)

        model.create_table()
      else:
        logger.debug(u"The %ss table exists, moving on." % model.__name__)

