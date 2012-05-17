# -*- coding: utf-8 -*-
import threading
import Queue
import time
import random

from datetime import datetime

from headphones.logger import logger

NUMBER_OF_WORKERS = 6

WORK_QUEUE = Queue.Queue()
QUEUE_LOCK = threading.Lock()


def put(pointer, kwargs = {}):
  WORK_QUEUE.put({'pointer': pointer, 'kwargs': kwargs})


class WorkerQueue(threading.Thread):
  def __init__(self, queue):
    self.__queue__ = queue

    threading.Thread.__init__(self)

  def run(self):
    while True:
      time.sleep(0.4)

      with QUEUE_LOCK:
        work_item = self.__queue__.get()

      if work_item:
        work_item['pointer'](**work_item['kwargs'])
        self.__queue__.task_done()


# Spin up workers for each NUMBER_OF_WORKERS defined to pull work-items off of
# the WORK_QUEUE.
for i in range(NUMBER_OF_WORKERS):
  WorkerQueue(WORK_QUEUE).start()
