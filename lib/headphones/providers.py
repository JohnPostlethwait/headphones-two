import re

from lib import requests
from lib.headphones import *


class ProviderBase(object):
  search_url = None
  max_results = 10
  categories = {'any': None}
  enabled = False

  @classmethod
  def search(cls, artist_name, album_name=None):
    logger.error('The subclass must overwrite the search function.')
    return []


class NZBMatrix(ProviderBase):
  search_url = 'http://api.nzbmatrix.com/v1.1/search.php'
  categories = {'albums': 22, 'singles': 47, 'lossless': 23, 'other': 27, 'all': 'music-all'}
  enabled = config.nzbmatrix.enabled

  @classmethod
  def search(cls, artist_name, album_name=None):
    search_query = artist_name + ' ' + album_name if album_name else artist_name
    params = {
        'search': search_query,
        'catid': cls.categories['all'],
        'num': cls.max_results,
        'username': config.nzbmatrix.username,
        'apikey': config.nzbmatrix.api_key}
    request = requests.get(cls.search_url, params=params)
    results = cls.parse_search_results(request.content)

    return results

    @staticmethod
    def parse_search_results(result_content):
      results = []
      result_chunks = re.split('\\n|\\n', result_content)

      for result in result_chunks:
        result_lines = result.split('\n')
        result_dict = {}

        for line in result_lines:
          key = re.findall('^(.+):', line)[0]
          value = re.findall(':(.+);$', line)[0]
          result_dict[key] = value.lower()

        results.append(result_dict)

      return results
