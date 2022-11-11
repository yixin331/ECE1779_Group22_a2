from flask import Flask
from app import dbconnection


webapp = Flask(__name__)

from app import main
from app import get
from app import put
from app import clear
from app import key
from app import refreshConfiguration
from app import stat
from app import deleteAll
from app import sizeChange



