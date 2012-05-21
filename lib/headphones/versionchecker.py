import re
import subprocess
import models

from datetime import datetime
from logger import logger


class Git(object):
  @classmethod
  def last_scan(cls):
    return models.HeadphonesVersion.latest_check()

  @classmethod
  def check(cls, force=False):
    checked_ago = None

    if cls.last_scan():
      checked_ago = datetime.now() - cls.last_scan().checked_on

    if force or not checked_ago or checked_ago.days > 0 or checked_ago.seconds > 43200:
      git_command_local = 'git rev-parse HEAD'.split()
      git_command_remote = 'git ls-remote origin'.split()

      local_check = subprocess.Popen(git_command_local, stdout=subprocess.PIPE)
      remote_check = subprocess.Popen(git_command_remote, stdout=subprocess.PIPE)

      models.HeadphonesVersion.create(
          local_revision = local_check.communicate()[0].split('\n')[0],
          remote_revision = remote_check.communicate()[0].split('\n')[0].split('\t')[0])

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
    if not cls.last_scan(): cls.check()

    if cls.last_scan().local_revision != cls.last_scan().remote_revision:
      logger.debug('Code-base is out of date, updating now...')

      git_command = 'git pull origin master'.split()

      process = subprocess.Popen(git_command, stdout=subprocess.PIPE)

    return True


class Database(object):
  @classmethod
  def update(cls):
    for model in (models.Album, models.Artist, models.Track,
        models.HeadphonesVersion, models.LastFMSuggestion,):
      logger.debug(u"Checking if the %ss table exists..." % model.__name__)

      if not model.table_exists():
        logger.debug(u"The %ss table does not exist, creating it." % model.__name__)

        model.create_table()
      else:
        logger.debug(u"The %ss table exists, moving on." % model.__name__)
