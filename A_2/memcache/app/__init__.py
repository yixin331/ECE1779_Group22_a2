from flask import Flask
from collections import OrderedDict
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()

global memcache
global memcache_stat
global memcache_config

webapp = Flask(__name__)
memcache = OrderedDict()
memcache_stat = {'num_item': 0, 'total_size': 0, 'num_request': 0, 'num_get': 0, 'num_miss': 0}
memcache_config = {'capacity': 128, 'policy': 'LRU'}
node_id = 1


from app import getKey
from app import putImage
from app import clearCache
from app import setConfig
from app import putStat

@webapp.before_first_request
def put_memcache_stat():
    scheduler.add_job(id='put_memcache_stat', func=putStat, trigger='interval', seconds=5)



