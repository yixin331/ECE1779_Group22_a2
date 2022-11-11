from flask import Flask
import requests


global memcache_mode
global node_ip
global memcache_config
global memcache_stat


webapp = Flask(__name__)


memcache_mode = {'num_node': 1, 'mode': 'Manual', 'max_thr': 1, 'min_thr': 0, 'expand_ratio': 1, 'shrink_ratio': 1}
memcache_config = {'capacity': 128, 'policy': 'LRU'}
node_ip = {}
memcache_stat = {}
memcache_stat['Time'] = []
memcache_stat['NumItem'] = []
memcache_stat['TotalSize'] = []
memcache_stat['NumRequest']= []
memcache_stat['HitRate'] = []
memcache_stat['MissRate'] = []


from app import main
from app import refreshConfiguration
from app import refreshMode
from app import showStat
from app import clear
from app import deleteAll
from app import putImage
from app import getKey
from app import map
from app import remap


# TODO: need to call this when creating a new memcache instance
def schedule_cloud_watch():
    try:
        response = requests.post(url='http://localhost:5001/putStat').json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Cache loses connection")

schedule_cloud_watch()