import itertools

from datetime import datetime

from lib import peewee


class Artist(peewee.Model):
  id =              peewee.PrimaryKeyField()
  name =            peewee.CharField()
  unique_name =     peewee.CharField(unique=True)
  musicbrainz_id =  peewee.CharField()
  location =        peewee.TextField()
  state =           peewee.CharField()
  added_on =        peewee.DateTimeField(default=datetime.now)
  updated_on =      peewee.DateTimeField(default=datetime.now)

  def albums(self):
    return Album.select().order_by(('released_on', 'desc')).where(artist_id=self.id).execute()

  def tracks(self):
    tracks = []

    for album in self.albums():
      tracks.append(album.tracks)

    return list(itertools.chain(*tracks))

  def track_count(self):
    num_tracks = 0

    for album in self.albums():
      num_tracks += album.track_count()

    return num_tracks

  def obtainted_track_count(self):
    num_tracks = 0

    for album in self.albums():
      num_tracks += album.obtained_track_count()

    return num_tracks

  def latest_album(self):
    return Album.select().order_by(('released_on', 'desc')).where(artist_id=self.id).limit(1).execute().first()


class Album(peewee.Model):
  id =                peewee.PrimaryKeyField()
  artist =            peewee.ForeignKeyField(Artist)
  name =              peewee.CharField()
  summary =           peewee.TextField()
  location =          peewee.TextField()
  type =              peewee.CharField()
  musicbrainz_id =    peewee.CharField()
  release_group_id =  peewee.CharField()
  asin =              peewee.CharField(null=True)
  state =             peewee.CharField()
  released_on =       peewee.DateTimeField(null=True)
  added_on =          peewee.DateTimeField(default=datetime.now)
  updated_on =        peewee.DateTimeField(default=datetime.now)

  def obtained_track_count(self):
    num_obtained = Track.select().where(album_id=self.id, location="IS NOT NULL").count()

    return num_obtained

  def track_count(self):
    return Track.select().where(album_id=self.id).count()

  def tracks(self):
    return Track.select().order_by('number').where(album_id=self.id).execute()

  def duration(self):
    duration = 0.0

    for track in self.tracks():
      if track.length:
        duration += track.length

    return duration


class Track(peewee.Model):
  id =          peewee.PrimaryKeyField()
  album =       peewee.ForeignKeyField(Album)
  number =      peewee.IntegerField()
  title =       peewee.CharField()
  length =      peewee.IntegerField(null=True)
  bitrate =     peewee.IntegerField(null=True)
  location =    peewee.TextField()
  state =       peewee.CharField()
  updated_on =  peewee.DateTimeField(default=datetime.now)
  added_on =    peewee.DateTimeField(default=datetime.now)


peewee.database.connect()
