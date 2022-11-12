from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from app import config
from app.config import aws_config

scheduler = BackgroundScheduler()
scheduler.start()

global memcache_mode
global node_ip

webapp = Flask(__name__)

memcache_mode = {'num_node': 1, 'max_thr': 100, 'min_thr': -1, 'expand_ratio': 1, 'shrink_ratio': 1}
node_ip = {}

from app import setMode






