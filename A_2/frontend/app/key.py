from flask import render_template, url_for, request, g
from app import webapp, dbconnection
import requests


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/key', methods=['GET'])
def key():
    cursor = dbconnection.list_keys()
    return render_template("key.html", cursor=cursor)

