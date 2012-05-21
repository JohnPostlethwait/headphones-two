from app.config.cplog import CPLog
from app.lib.provider.yarr.base import nzbBase
from dateutil.parser import parse
from urllib import urlencode
from urllib2 import URLError
import time
import traceback

log = CPLog(__name__)

class nzbs(nzbBase):
    """Api for nzbs"""

    name = 'NZBs.org'
    downloadUrl = 'https://nzbs.org/classic/index.php?action=getnzb&nzbid=%s%s'
    nfoUrl = 'https://nzbs.org/classic/index.php?action=view&nzbid=%s&nfo=1'
    detailUrl = 'https://nzbs.org/classic/index.php?action=view&nzbid=%s'
    apiUrl = 'https://nzbs.org/classic/rss.php'

    catIds = {
        4: ['720p', '1080p'],
        2: ['cam', 'ts', 'dvdrip', 'tc', 'brrip', 'r5', 'scr'],
        9: ['dvdr']
    }
    catBackupId = 't2'

    timeBetween = 3 # Seconds

    def __init__(self, config):
        log.info('Using NZBs.org provider')

        self.config = config

    def conf(self, option):
        return self.config.get('NZBsorg', option)

    def enabled(self):
        return self.conf('enabled') and self.config.get('NZB', 'enabled') and self.conf('id') and self.conf('key')

    def find(self, movie, quality, type, retry = False):

        self.cleanCache();

        results = []
        if not self.enabled() or not self.isAvailable(self.apiUrl + '?test' + self.getApiExt()):
            return results

        catId = self.getCatId(type)
        arguments = urlencode({
            'action':'search',
            'q': self.toSearchString(movie.name),
            'catid': catId,
            'i': self.conf('id'),
            'h': self.conf('key'),
        })
        url = "%s?%s" % (self.apiUrl, arguments)
        cacheId = str(movie.imdb) + '-' + str(catId)
        singleCat = (len(self.catIds.get(catId)) == 1 and catId != self.catBackupId)

        try:
            cached = False
            if(self.cache.get(cacheId)):
                data = True
                cached = True
                log.info('Getting RSS from cache: %s.' % cacheId)
            else:
                log.info('Searching: %s' % url)
                data = self.urlopen(url)
                self.cache[cacheId] = {
                    'time': time.time()
                }
        except (IOError, URLError):
            log.error('Failed to open %s.' % url)
            return results

        if data:
            log.debug('Parsing NZBs.org RSS.')
            try:
                try:
                    if cached:
                        xml = self.cache[cacheId]['xml']
                    else:
                        xml = self.getItems(data)
                        self.cache[cacheId]['xml'] = xml
                except:
                    if retry == False:
                        log.error('No valid xml, to many requests? Try again in 15sec.')
                        time.sleep(15)
                        return self.find(movie, quality, type, retry = True)
                    else:
                        log.error('Failed again.. disable %s for 15min.' % self.name)
                        self.available = False
                        return results

                for nzb in xml:

                    id = int(self.gettextelement(nzb, "link").partition('nzbid=')[2])

                    size = self.gettextelement(nzb, "description").split('</a><br />')[1].split('">')[1]

                    new = self.feedItem()
                    new.id = id
                    new.type = 'nzb'
                    new.name = self.gettextelement(nzb, "title")
                    new.date = int(time.mktime(parse(self.gettextelement(nzb, "pubDate")).timetuple()))
                    new.size = self.parseSize(size)
                    new.url = self.downloadLink(id)
                    new.detailUrl = self.detailLink(id)
                    new.content = self.gettextelement(nzb, "description")
                    new.score = self.calcScore(new, movie)

                    if self.isCorrectMovie(new, movie, type, singleCategory = singleCat):
                        results.append(new)
                        log.info('Found: %s' % new.name)

                return results
            except:
                log.error('Failed to parse XML response from NZBs.org: %s' % traceback.format_exc())
                return False

        return results


    def getApiExt(self):
        return '&i=%s&h=%s' % (self.conf('id'), self.conf('key'))
