import pymongo
from pymongo.errors import ConnectionFailure
import sys
from datetime import datetime
import time
import syslog
import logging
from db_base import db_base

class mongo_db(db_base):

    def __init__(self, host,port,name):
        db_base.__init__(self)
        global db_host
        global db_port
        global db_name

        db_host = host
        db_port = port
        db_name = name


