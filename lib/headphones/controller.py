import os
import sys
import threading
import time

import cherrypy
import logger

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

from models import Album
from models import Artist
from models import Track
from models import LastFMSuggestion

from lib.headphones import *
from lib.headphones import versionchecker


class Controller(object):
  @staticmethod
  def serve_template(name, **kwargs):
    template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates/')
    lookup = TemplateLookup(directories=[template_dir])

    try:
      return lookup.get_template(name).render(**kwargs)
    except:
      return exceptions.html_error_template().render()

  @cherrypy.expose
  def index(self):
    artists = Artist.select(['id', 'name', 'unique_name', 'state'])

    return self.serve_template("index.html", title="Home", artists=artists)

  @cherrypy.expose
  def artist(self, id):
    artist = Artist.get(id=id)

    return self.serve_template("artist.html", title=artist.name, artist=artist)

  @cherrypy.expose
  def album(self, id):
    album = Album.get(id=id)
    title = album.artist.name + ' &emdash; ' + album.name

    return self.serve_template("album.html", album=album, title=title)

  # @cherrypy.expose
  # def search(self, name, type):
  #   if len(name) == 0:
  #     raise cherrypy.HTTPRedirect("index")
  # 
  #   if type == 'artist':
  #     searchresults = mb.findArtist(name, limit=100)
  #   else:
  #     searchresults = mb.findRelease(name, limit=100)
  # 
  #   return self.serve_template("searchresults.html", title='Search Results for: "' + name + '"', searchresults=searchresults, type=type)
  # 
  # 
  # @cherrypy.expose
  # def addArtist(self, artistid):
  #   threading.Thread(target=importer.addArtisttoDB, args=[artistid]).start()
  #   time.sleep(5)
  #   threading.Thread(target=lastfm.getSimilar).start()
  # 
  #   raise cherrypy.HTTPRedirect("artistPage?ArtistID=%s" % artistid)
  # 
  # 
  # @cherrypy.expose
  # def getExtras(self, ArtistID):
  #   controlValueDict = {'ArtistID': ArtistID}
  #   newValueDict = {'IncludeExtras': 1}
  #   self.database.upsert("artists", newValueDict, controlValueDict)
  #   threading.Thread(target=importer.addArtisttoDB, args=[ArtistID, True]).start()
  #   time.sleep(10)
  # 
  #   raise cherrypy.HTTPRedirect("artistPage?ArtistID=%s" % ArtistID)
  # 
  # 
  # @cherrypy.expose
  # def removeExtras(self, ArtistID):
  #   controlValueDict = {'ArtistID': ArtistID}
  #   newValueDict = {'IncludeExtras': 0}
  #   self.database.upsert("artists", newValueDict, controlValueDict)
  #   extraalbums = self.database.select('SELECT AlbumID FROM albums WHERE ArtistID=? AND Status="Skipped" AND Type!="Album"', [ArtistID])
  # 
  #   for album in extraalbums:
  #     self.database.action('DELETE from tracks WHERE ArtistID=? AND AlbumID=?', [ArtistID, album['AlbumID']])
  #     self.database.action('DELETE from albums WHERE ArtistID=? AND AlbumID=?', [ArtistID, album['AlbumID']])
  # 
  #   raise cherrypy.HTTPRedirect("artistPage?ArtistID=%s" % ArtistID)
  # 
  # 
  # @cherrypy.expose
  # def pauseArtist(self, ArtistID):
  #   logger.info(u"Pausing artist: " + ArtistID)
  #   controlValueDict = {'ArtistID': ArtistID}
  #   newValueDict = {'Status': 'Paused'}
  #   self.database.upsert("artists", newValueDict, controlValueDict)
  # 
  #   raise cherrypy.HTTPRedirect("artistPage?ArtistID=%s" % ArtistID)
  # 
  # 
  # @cherrypy.expose
  # def resumeArtist(self, ArtistID):
  #   logger.info(u"Resuming artist: " + ArtistID)
  #   controlValueDict = {'ArtistID': ArtistID}
  #   newValueDict = {'Status': 'Active'}
  #   self.database.upsert("artists", newValueDict, controlValueDict)
  # 
  #   raise cherrypy.HTTPRedirect("artistPage?ArtistID=%s" % ArtistID)
  # 
  # 
  # @cherrypy.expose
  # def deleteArtist(self, id):
  #   logger.info(u"Deleting all traces of artist: " + ArtistID)
  # 
  #   self.database.action('DELETE FROM artists WHERE id=?', [id])
  #   self.database.action('DELETE FROM albums WHERE artist_id=?', [id])
  #   self.database.action('DELETE FROM tracks WHERE ArtistID=?', [ArtistID]) # TODO: JOIN DELETE
  # 
  #   raise cherrypy.HTTPRedirect("index")
  # 
  # 
  # @cherrypy.expose
  # def refreshArtist(self, id):
  #   importer.addArtisttoDB(id)
  # 
  #   raise cherrypy.HTTPRedirect("artist?id=%s" % id)
  # 
  # 
  # @cherrypy.expose
  # def markAlbums(self, ArtistID=None, action=None, **args):
  #   if action == 'WantedNew':
  #     newaction = 'Wanted'
  #   else:
  #     newaction = action
  #   for mbid in args:
  #     controlValueDict = {'AlbumID': mbid}
  #     newValueDict = {'Status': newaction}
  #     self.database.upsert("albums", newValueDict, controlValueDict)
  # 
  #     if action == 'Wanted':
  #       searcher.searchNZB(mbid, new=False)
  #     if action == 'WantedNew':
  #       searcher.searchNZB(mbid, new=True)
  #   if ArtistID:
  #     raise cherrypy.HTTPRedirect("artistPage?ArtistID=%s" % ArtistID)
  #   else:
  #     raise cherrypy.HTTPRedirect("upcoming")
  # 
  # 
  # @cherrypy.expose
  # def addArtists(self, **args):
  #   threading.Thread(target=importer.artistNamesToMusicBrainzIds, args=[args]).start()
  #   time.sleep(5)
  # 
  #   raise cherrypy.HTTPRedirect("index")
  # 
  # 
  # @cherrypy.expose
  # def queueAlbum(self, AlbumID, ArtistID=None, new=False, redirect=None):
  #   logger.info(u"Marking album: " + AlbumID + "as wanted...")
  #   controlValueDict = {'AlbumID': AlbumID}
  #   newValueDict = {'Status': 'Wanted'}
  #   self.database.upsert("albums", newValueDict, controlValueDict)
  #   searcher.searchNZB(AlbumID, new)
  # 
  #   if ArtistID:
  #     raise cherrypy.HTTPRedirect("artistPage?ArtistID=%s" % ArtistID)
  #   else:
  #     raise cherrypy.HTTPRedirect(redirect)
  # 
  # 
  # @cherrypy.expose
  # def unqueueAlbum(self, AlbumID, ArtistID):
  #   logger.info(u"Marking album: " + AlbumID + "as skipped...")
  #   controlValueDict = {'AlbumID': AlbumID}
  #   newValueDict = {'Status': 'Skipped'}
  #   self.database.upsert("albums", newValueDict, controlValueDict)
  # 
  #   raise cherrypy.HTTPRedirect("artist?id=%s" % ArtistID)
  # 
  # 
  # @cherrypy.expose
  # def deleteAlbum(self, AlbumID, ArtistID=None):
  #   logger.info(u"Deleting all traces of album: " + AlbumID)
  # 
  #   self.database.action('DELETE FROM albums WHERE AlbumID=?', [AlbumID])
  #   self.database.action('DELETE FROM tracks WHERE AlbumID=?', [AlbumID])
  # 
  #   if ArtistID:
  #     raise cherrypy.HTTPRedirect("artistPage?ArtistID=%s" % ArtistID)
  #   else:
  #     raise cherrypy.HTTPRedirect("index")
  # 
  # 
  # @cherrypy.expose
  # def upcoming(self):
  #   upcoming = self.database.select("SELECT * FROM albums WHERE released_on > date('now') ORDER BY released_on DESC")
  #   wanted = self.database.select("SELECT * FROM albums WHERE state='Wanted'")
  # 
  #   return self.serve_template("upcoming.html", title="Upcoming", upcoming=upcoming, wanted=wanted)
  # 
  # 
  # @cherrypy.expose
  # def manageNew(self):
  #   return self.serve_template("managenew.html", title="Manage New Artists")
  # 
  # 
  # @cherrypy.expose
  # def markArtists(self, action=None, **args):
  #   for ArtistID in args:
  #     if action == 'delete':
  #       self.database.action('DELETE FROM artists WHERE ArtistID=?', [ArtistID])
  #       self.database.action('DELETE FROM albums WHERE ArtistID=?', [ArtistID])
  #       self.database.action('DELETE FROM tracks WHERE ArtistID=?', [ArtistID])
  #     elif action == 'pause':
  #       controlValueDict = {'ArtistID': ArtistID}
  #       newValueDict = {'Status': 'Paused'}
  #       self.database.upsert("artists", newValueDict, controlValueDict)
  #     elif action == 'resume':
  #       controlValueDict = {'ArtistID': ArtistID}
  #       newValueDict = {'Status': 'Active'}
  #       self.database.upsert("artists", newValueDict, controlValueDict)
  #     else:
  #       # These may and probably will collide - need to make a better way to queue musicbrainz queries
  #       threading.Thread(target=importer.addArtisttoDB, args=[ArtistID]).start()
  #       time.sleep(30)
  # 
  #   raise cherrypy.HTTPRedirect("index")
  # 
  # 
  # @cherrypy.expose
  # def importLastFM(self, username):
  #   headphones.LASTFM_USERNAME = username
  #   headphones.config_write()
  #   threading.Thread(target=lastfm.getArtists).start()
  #   time.sleep(10)
  # 
  #   raise cherrypy.HTTPRedirect("index")
  # 
  # 
  # @cherrypy.expose
  # def importItunes(self, path):
  #   headphones.PATH_TO_XML = path
  #   headphones.config_write()
  #   threading.Thread(target=importer.itunesImport, args=[path]).start()
  #   time.sleep(10)
  # 
  #   raise cherrypy.HTTPRedirect("index")
  # 
  # 
  # @cherrypy.expose
  # def musicScan(self, path, redirect=None):
  #   headphones.MUSIC_DIR = path
  #   headphones.config_write()
  # 
  #   try:
  #     threading.Thread(target=librarysync.scan).start()
  #   except Exception, e:
  #     logger.error('Unable to complete the scan: %s' % e)
  # 
  #   time.sleep(10)
  # 
  #   if redirect:
  #     raise cherrypy.HTTPRedirect(redirect)
  #   else:
  #     raise cherrypy.HTTPRedirect("index")
  # 
  # 
  # @cherrypy.expose
  # def forceUpdate(self):
  #   from headphones import updater
  # 
  #   threading.Thread(target=updater.dbUpdate).start()
  #   time.sleep(5)
  # 
  #   raise cherrypy.HTTPRedirect("index")
  # 
  # 
  # @cherrypy.expose
  # def forceSearch(self):
  #   from headphones import searcher
  # 
  #   threading.Thread(target=searcher.searchNZB).start()
  #   time.sleep(5)
  # 
  #   raise cherrypy.HTTPRedirect("index")
  # 
  # 
  # @cherrypy.expose
  # def forcePostProcess(self):
  #   from headphones import postprocessor
  # 
  #   threading.Thread(target=postprocessor.forcePostProcess).start()
  #   time.sleep(5)
  # 
  #   raise cherrypy.HTTPRedirect("index")
  # 
  # 
  # @cherrypy.expose
  # def checkGithub(self):
  #   from headphones import versioncheck
  # 
  #   versioncheck.checkGithub()
  # 
  #   raise cherrypy.HTTPRedirect("index")
  # 
  # 
  # @cherrypy.expose
  # def history(self):
  #   history = self.database.select('SELECT * FROM snatched ORDER BY DateAdded DESC')
  # 
  #   return self.serve_template("history.html", title="History", history=history)

  @cherrypy.expose
  def logs(self):
    sectioned_log = []
    for line in logger.read_log():
      sectioned_log.append(logger.disect_line(line))

    return self.serve_template("logs.html", title="Log", log_lines=sectioned_log)

  # @cherrypy.expose
  # def clearhistory(self, type=None):
  #   if type == 'all':
  #     logger.info(u"Clearing all history")
  #     self.database.action('DELETE FROM snatched')
  #   else:
  #     logger.info(u"Clearing history where status is %s" % type)
  #     self.database.action('DELETE FROM snatched WHERE Status=?', [type])
  # 
  #   raise cherrypy.HTTPRedirect("history")

  @cherrypy.expose
  def config(self):
    return self.serve_template("config.html", title="Settings", config=config)

  # @cherrypy.expose
  # def configUpdate(self, http_host='0.0.0.0', http_username=None, http_port=8181, http_password=None, launch_browser=0,
  #   sab_host=None, sab_username=None, sab_apikey=None, sab_password=None, sab_category=None, download_dir=None, blackhole=0, blackhole_dir=None,
  #   usenet_retention=None, nzbmatrix=0, nzbmatrix_username=None, nzbmatrix_apikey=None, newznab=0, newznab_host=None, newznab_apikey=None,
  #   nzbsorg=0, nzbsorg_uid=None, nzbsorg_hash=None, newzbin=0, newzbin_uid=None, newzbin_password=None, preferred_quality=0, preferred_bitrate=None, detect_bitrate=0, move_files=0,
  #   rename_files=0, correct_metadata=0, cleanup_files=0, add_album_art=0, embed_album_art=0, embed_lyrics=0, destination_dir=None, folder_format=None, file_format=None, include_extras=0, log_dir=None,
  #   encode=0, encoder=None, bitrate=None, samplingfrequency=None, encoderfolder=None, advancedencoder=None, encoderoutputformat=None, encodervbrcbr=None, encoderquality=None, encoderlossless=0):
  # 
  #   headphones.HTTP_HOST = http_host
  #   headphones.HTTP_PORT = http_port
  #   headphones.HTTP_USERNAME = http_username
  #   headphones.HTTP_PASSWORD = http_password
  #   headphones.LAUNCH_BROWSER = launch_browser
  #   headphones.SAB_HOST = sab_host
  #   headphones.SAB_USERNAME = sab_username
  #   headphones.SAB_PASSWORD = sab_password
  #   headphones.SAB_APIKEY = sab_apikey
  #   headphones.SAB_CATEGORY = sab_category
  #   headphones.DOWNLOAD_DIR = download_dir
  #   headphones.BLACKHOLE = blackhole
  #   headphones.BLACKHOLE_DIR = blackhole_dir
  #   headphones.USENET_RETENTION = usenet_retention
  #   headphones.NZBMATRIX = nzbmatrix
  #   headphones.NZBMATRIX_USERNAME = nzbmatrix_username
  #   headphones.NZBMATRIX_APIKEY = nzbmatrix_apikey
  #   headphones.NEWZNAB = newznab
  #   headphones.NEWZNAB_HOST = newznab_host
  #   headphones.NEWZNAB_APIKEY = newznab_apikey
  #   headphones.NZBSORG = nzbsorg
  #   headphones.NZBSORG_UID = nzbsorg_uid
  #   headphones.NZBSORG_HASH = nzbsorg_hash
  #   headphones.NEWZBIN = newzbin
  #   headphones.NEWZBIN_UID = newzbin_uid
  #   headphones.NEWZBIN_PASSWORD = newzbin_password
  #   headphones.PREFERRED_QUALITY = int(preferred_quality)
  #   headphones.PREFERRED_BITRATE = preferred_bitrate
  #   headphones.DETECT_BITRATE = detect_bitrate
  #   headphones.MOVE_FILES = move_files
  #   headphones.CORRECT_METADATA = correct_metadata
  #   headphones.RENAME_FILES = rename_files
  #   headphones.CLEANUP_FILES = cleanup_files
  #   headphones.ADD_ALBUM_ART = add_album_art
  #   headphones.EMBED_ALBUM_ART = embed_album_art
  #   headphones.EMBED_LYRICS = embed_lyrics
  #   headphones.DESTINATION_DIR = destination_dir
  #   headphones.FOLDER_FORMAT = folder_format
  #   headphones.FILE_FORMAT = file_format
  #   headphones.INCLUDE_EXTRAS = include_extras
  #   headphones.LOG_DIR = log_dir
  #   headphones.ENCODE = encode
  #   headphones.ENCODER = encoder
  #   headphones.BITRATE = int(bitrate)
  #   headphones.SAMPLINGFREQUENCY = int(samplingfrequency)
  #   headphones.ENCODERFOLDER = encoderfolder
  #   headphones.ADVANCEDENCODER = advancedencoder
  #   headphones.ENCODEROUTPUTFORMAT = encoderoutputformat
  #   headphones.ENCODERVBRCBR = encodervbrcbr
  #   headphones.ENCODERQUALITY = int(encoderquality)
  #   headphones.ENCODERLOSSLESS = encoderlossless
  # 
  #   headphones.config_write()
  # 
  #   raise cherrypy.HTTPRedirect("config")

  @cherrypy.expose
  def shutdown(self):
    cherrypy.engine.stop()
    sys.exit(0)

    return self.serve_template("shutdown.html", title="Shutting Down", timer=0, stop_refresh=True)

  @cherrypy.expose
  def restart(self):
    cherrypy.engine.restart()

    return self.serve_template("shutdown.html", title="Restarting", timer=15, stop_refresh=False)

  @cherrypy.expose
  def update(self):
    versionchecker.Git().update()
    cherrypy.engine.restart()

    return self.serve_template("shutdown.html", title="Updating", timer=30, stop_refresh=False)

  @cherrypy.expose
  def suggestions(self):
    suggestions = LastFMSuggestion.select().execute()

    return self.serve_template("suggestions.html", title="Suggestions From LastFM", suggestions=suggestions)

  # @cherrypy.expose
  # def addReleaseById(self, rid):
  #   threading.Thread(target=importer.addReleaseById, args=[rid]).start()
  #   time.sleep(5)
  # 
  #   raise cherrypy.HTTPRedirect("index")
  # 
  # 
  # @cherrypy.expose
  # def updateCloud(self):
  #   lastfm.getSimilar()
  # 
  #   raise cherrypy.HTTPRedirect("extras")
  # 
