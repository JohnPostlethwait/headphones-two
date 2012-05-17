import sys

from lib.apscheduler.scheduler import Scheduler

from lib.headphones import *
from lib.headphones import versionchecker
from lib.headphones import webserver


sys.dont_write_bytecode = True


# Check the versions of various updateable things.
versionchecker.Database.check()

# Start up the various scheduled jobs.
scheduler = Scheduler()
# scheduler.add_cron_job(updater.dbUpdate, hour=4, minute=0, second=0)
# scheduler.add_interval_job(searcher.searchNZB, minutes=NZB_SEARCH_INTERVAL)
# scheduler.add_interval_job(librarysync.scan, minutes=LIBRARYSCAN_INTERVAL)
# scheduler.add_interval_job(versioncheck.checkGithub, minutes=300)
# scheduler.add_interval_job(postprocessor.checkFolder, minutes=DOWNLOAD_SCAN_INTERVAL)

# scheduler.start()

# Start the webserver itself.
webserver.start({
    'http_port':        config.webserver.http_post,
    'http_host':        config.webserver.http_host,
    'http_username':    config.webserver.http_username,
    'http_password':    config.webserver.http_password})
