from flask import Flask
from app import Memcache

global memcache

webapp = Flask(__name__)
memcache = Memcache.Memcache()

from app import main




