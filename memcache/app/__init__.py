from flask import Flask
from collections import OrderedDict

global memcache
global capacity
global policy
global num_item
global total_size
global num_request
global num_get
global num_miss

webapp = Flask(__name__)
memcache = OrderedDict()
capacity = 128
policy = 'LRU'
num_item = 0
total_size = 0
num_request = 0
num_get = 0
num_miss = 0


from app import main
from app import getKey
from app import putImage
from app import clearCache
from app import setConfig
from app import putStat





