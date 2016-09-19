#!/usr/bin/env python2

import logging
import config

from database import Database
from jobs import VineJobs
from listener import SocketProcess
from scrape import ScrapeProcess
from combine import CombineProcess

LOG_FORMAT = "[%(levelname)s] %(name)s : %(message)s"

logger = logging.getLogger(__name__)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(stream_handler)

__all__ = ['VineJobs', 'SocketProcess', 'ScrapeProcess', 'CombineProcess', 'Database']
