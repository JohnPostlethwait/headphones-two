import time
import threading

import lib.musicbrainz2

from lib.musicbrainz2 import webservice
from lib.musicbrainz2 import model
from lib.musicbrainz2 import utils

from lib.musicbrainz2.webservice import WebServiceError

from logger import logger


query = webservice.Query()
mb_lock = threading.Lock()


def getBestArtistMatch(artist_name):
  with mb_lock:
    attempt = 0

    if any((c in set('!?*')) for c in artist_name):
      artist_name = '"' + artist_name + '"'

    while attempt < 10:
      try:
        artist_results = query.getArtists(webservice.ArtistFilter(query=artist_name, limit=1))

        if artist_results:
          includes = webservice.ArtistIncludes(releases=(model.Release.TYPE_ALBUM, model.Release.TYPE_OFFICIAL))
          artist = artist_results[0].artist

          # Unfortunately, the search results do not contain release information, we have to query again for it...
          return query.getArtistById(utils.extractUuid(artist.id), includes)
        else:
          return None

        break
      except WebServiceError, e:
        logger.error('Attempt to query MusicBrainz for Artist %s failed: %s. Retrying in 10 seconds...' % (artist_name, e))
        attempt += 1
        time.sleep(10)


def getRelease(release_id):
  attempt = 0
  release = None
  includes = webservice.ReleaseIncludes(tracks=True, releaseGroup=True)

  while attempt < 10:
    try:
      release = query.getReleaseById(release_id, includes)
    except WebServiceError, e:
      logger.error('Attempt to query MusicBrainz for Release "%s" failed: %s. Retrying in 10 seconds...' % (release_id, e))
      attempt += 1
      time.sleep(10)

  return release
