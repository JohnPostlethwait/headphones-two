import models

from lib.headphones.logger import logger


class Versioned(object):
  version = None

  @classmethod
  def check_version(cls):
    raise NotImplementedError('The check_version function needs to be implemented by the class it is called from.')

  @classmethod
  def update(cls):
    raise NotImplementedError('The update function needs to be implemented by the class it is called from.')


class Database(Versioned):
  @classmethod
  def check(cls):
    for model in (models.Album, models.Artist, models.Track,):
      logger.debug(u"Checking if the %ss table exists..." % model.__name__)

      if not model.table_exists():
        logger.debug(u"The %ss table does not exist, creating it." % model.__name__)

        model.create_table()
      else:
        logger.debug(u"The %ss table exists, moving on." % model.__name__)


class Git(Versioned):
  pass
