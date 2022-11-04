from flask import render_template, url_for, request, g
from app import webapp, dbconnection
import requests


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@webapp.route('/stat', methods=['GET'])
def stat():
    cursor = dbconnection.show_stat()
    return render_template("statistics.html", cursor=cursor)