from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()

global memcache_mode
global memcache_stat

webapp = Flask(__name__)

memcache_mode = {'num_node': 1, 'max_thr': 100, 'min_thr': -1, 'expand_ratio': 1, 'shrink_ratio': 1}
memcache_stat = {}
memcache_stat['NumItem'] = []
memcache_stat['TotalSize'] = []
memcache_stat['NumRequest']= []
memcache_stat['HitRate'] = []
memcache_stat['MissRate'] = []


from app import setMode
from app import getStats






