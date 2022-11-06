from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()

global memcache_mode
global memcache_stat

webapp = Flask(__name__)

memcache_mode = {'num_node': 4, 'max_thr': 1, 'min_thr': 0.5, 'expand_ratio': 2, 'shrink_ratio': 0.5}
memcache_stat = {}
memcache_stat['NumItem'] = []
memcache_stat['TotalSize'] = []
memcache_stat['NumRequest']= []
memcache_stat['HitRate'] = []
memcache_stat['MissRate'] = []


from app import setMode






