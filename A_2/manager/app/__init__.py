
from flask import Flask

webapp = Flask(__name__)

from app import ec2
from app import s3_examples
from app import main
from app import node_configure
from app import resize
from app import clear_memcache
from app import delete_all
from app import putImage
from app import getKey