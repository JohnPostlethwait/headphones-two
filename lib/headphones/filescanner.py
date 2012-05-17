# -*- coding: utf-8 -*-
import os
import glob
import datetime
import time

import musicbrainz

import lib.threadpool as ThreadPool

from lib.headphones import *

from models import Album
from models import Artist
from models import Track

from lib.musicbrainz2 import utils
from lib import peewee
from lib.beets.mediafile import MediaFile


# Todo: MAKE ALL OF THIS RUN WITHOUT EXCEPTION UPON INTERNET DISCONNECTION!

def scan():
  logger.info(u"Now scanning the music library located at %s." % config.music.directory)

  artists_being_added = []

  for dirpath, dirnames, filenames in os.walk(config.music.directory):
    logger.debug(u'Now scanning the directory "%s"' % unicode(dirpath, errors="ignore"))

    # Scan all of the files in this directory:
    for filename in filenames:
      # Only scan music files...
      if any(filename.lower().endswith('.' + x.lower()) for x in config.music.formats.split(',')):
        logger.debug(u'Now scanning the file "%s"' % unicode(filename, errors="ignore"))

        full_path = os.path.join(dirpath, filename)

        # Try to read the tags from the file, move on if we can't.
        try:
          media_file = MediaFile(full_path)
        except Exception, e:
          logger.debug(u'Cannot read tags of file "%s" because of the exception "%s"' % (unicode(filename, errors="ignore"), str(e)))
          break

        # If we did read the tags, but the artist can't be found, move on to the next file...
        if media_file.albumartist:
          id3_artist = media_file.albumartist
        elif media_file.artist:
          id3_artist = media_file.artist
        else:
          break

        logger.debug(u'Found the artist name "%s" in the ID3 tag of "%s" file.' % (id3_artist, unicode(full_path, errors="ignore")))

        artist_path_parts = []

        for part in dirpath.split('/'):
          artist_path_parts.append(part)

          if id3_artist.lower() in part.lower(): break

        if artist_path_parts:
          artist_path = os.sep.join(artist_path_parts)
        else:
          artist_path = config.music.directory

        # If we already have this artist in the DB only add their releases,
        # we do not need to re-add them to the Music Library.
        try:
          tracked_artist = Artist.get(name=id3_artist)
        except peewee.DoesNotExist:
          tracked_artist = None

        if tracked_artist and tracked_artist.id not in artists_being_added:
          logger.debug(u'Artist name "%s" is already tracked by Headphones, moving on but adding releases...' % id3_artist)

          ThreadPool.put(addReleases, {'artist_id': tracked_artist.id})
          artists_being_added.append(tracked_artist.id)

          break
        else:
          artist_record = addArtist(id3_artist, artist_path)

          if artist_record is not None:
            if artist_record.id not in artists_being_added:
              logger.debug('We have a new artist! Adding them now: artist_id %s' % artist_record.id)

              ThreadPool.put(addReleases, {'artist_id': artist_record.id})
              artists_being_added.append(artist_record.id)

          break


def addArtist(id3_artist_name, path):
  musicbrainz_artist = musicbrainz.getBestArtistMatch(id3_artist_name)

  if musicbrainz_artist is None:
    unique_name = id3_artist_name
    artist_mb_id = None
  else:
    unique_name = musicbrainz_artist.getUniqueName()
    artist_mb_id = utils.extractUuid(musicbrainz_artist.id)

  try:
    artist = Artist.get(peewee.Q(musicbrainz_id=artist_mb_id) | peewee.Q(unique_name=unique_name))
  except peewee.DoesNotExist:
    artist = Artist.create(
        name = id3_artist_name,
        unique_name = unique_name,
        location = path,
        state = 'wanted',
        musicbrainz_id = artist_mb_id)

  return artist


def addReleases( artist_id, update_artist = True ):
  artist_record = Artist.get(id=artist_id)
  musicbrainz_artist = musicbrainz.getBestArtistMatch(artist_record.name)
  release_ids = []

  for release in musicbrainz_artist.getReleases():
    release_ids.append(utils.extractUuid(release.id))

  # These release results do not contain all the information, we must re-query for that info...
  for rid in release_ids:
    release = musicbrainz.getRelease(rid)

    if not release: continue

    release_group_id = utils.extractUuid(release.getReleaseGroup().id)

    try:
      release_group_tracked = Album.get(release_group_id=release_group_id)
    except peewee.DoesNotExist:
      release_group_tracked = None

    if release_group_tracked: continue

    release_record = Album.create(
        musicbrainz_id = rid,
        asin = release.getAsin(),
        release_group_id = release_group_id,
        artist_id = artist_id,
        name = release.getTitle(),
        type = 'album',
        released_on = release.getEarliestReleaseDate(),
        state = 'wanted')

    track_number = 1

    for track in release.getTracks():
      Track.create(
          album_id = release_record.id,
          number = track_number,
          title = track.getTitle(),
          length = track.getDuration(),
          state = 'wanted')

      track_number += 1

  # Rescan the Music Library after adding new releases to see if the user has 
  # them or not. Will not run if explicitly told not to by the caller.
  if(update_artist): ThreadPool.put(updateArtist, {'artist_id': artist_id})


# Rescan the directory structure for a given artist ID, updating the album
# states, and track locations and states as we go... For now, assume all
# missing tracks and albums are "wanted".
# 
# Change this later to respect the state set by the user on the individual
# artist/album/track level.
def updateArtist(artist_id):
  try:
    artist = Artist.get(id=artist_id)
  except peewee.DoesNotExist:
    artist = None

  if artist:
    for dirpath, dirnames, filenames in os.walk(artist.location):
      logger.debug(u'Now scanning the directory "%s"' % dirpath)

      # Scan all of the files in this directory:
      for filename in filenames:
        # Only scan music files...
        if any(filename.lower().endswith('.' + x.lower()) for x in config.music.formats.split(',')):
          full_path = os.path.join(dirpath, filename)

          # Try to read the tags from the file, move on if we can't.
          try:
            media_file = MediaFile(full_path)

            # connection.action("UPDATE tracks SET track_location=?, track_status=? WHERE album_id IN \
            #     (SELECT album_id FROM albums WHERE album_name LIKE ? AND artist_id IN \
            #     (SELECT artist_id FROM artists WHERE artist_id=?)) AND track_number=?",
            #     (full_path, 'have', media_file.album, artist_id, media_file.track))
          except Exception, e:
            logger.debug(u'Cannot read tags of file "%s" because of the exception "%s"' % (filename, str(e)))
            continue


    for album in artist.albums():
      album_complete = True # Assuming it is complete is easier...

      for track in album.tracks():
        if track.location == None:
          track.state = 'wanted'
          track.save()
          album_complete = False

      # If we have all of the tracks for this album, set the state of the 
      # album to 'have', otherwise we will set them to 'wanted'.
      # 
      # There could be a bug here that if we set the album state to 'wanted'
      # the corresponding, missing tracks might not be set to 'wanted' as well.
      # 
      # Investigate this later...
      album.state = 'have' if album_complete else 'wanted'
      album.save()
  else:
    logger.info(u"Could not find an artist in the database with the artist_id of %s" % artist_id)


def updateMissingTrackPaths():
  logger.info('Ensuring that all of the tracks that Headphones is tracking are all still in the Music Library.')

  tracks = Track.select().where('location IS NOT NULL')

  for track in tracks:
    if not os.path.isfile(track.location):
      logger.info('Track ID ' + str(track['id']) + ' is no longer in the music library, clearing location.')

      track.location = None
      track.bitrate = None
      track.state = 'wanted'
      track.save()

  logger.info('Done ensuring all of the tracks are still in the Music Library.')


def __ensureLibraryLocation__():
  if not os.path.isdir(config.music.directory):
    logger.warn(u'Cannot find the directory "%s" Not scanning.' % unicode(headphones.MUSIC_DIR, errors='ignore'))

    return False
  else:
    return True
