from flask import Flask
from app import Memcache, dbconnection

global memcache

webapp = Flask(__name__)
memcache = Memcache.Memcache()

from app import main




