#!/usr/bin/env python

import logging

from database import Database
from jobs import JobData
from listener import SocketProcess
from scrape import ScrapeProcess
from combine import CombineProcess

LOG_FORMAT = "[%(levelname)s] %(name)s : %(message)s"

logger = logging.getLogger(__name__)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(stream_handler)

__all__ = ['JobData', 'SocketProcess', 'ScrapeProcess', 'CombineProcess', 'Database']
