from flask import Flask
import requests

global memcache_mode
global node_ip
global memcache_config

webapp = Flask(__name__)

memcache_mode = {'num_node': 1, 'mode': 'Manual'}
memcache_config = {'capacity': 128, 'policy': 'LRU'}
node_ip = {}

from app import ec2
from app import main
from app import node_configure
from app import resize
from app import clear_memcache
from app import delete_all
from app import putImage
from app import getKey
from app import maptest
from app import map
from app import remap


# TODO: need to call this when creating a new memcache instance
def schedule_cloud_watch():
    try:
        response = requests.post(url='http://localhost:5001/putStat').json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Cache loses connection")

schedule_cloud_watch()
