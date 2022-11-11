from flask import render_template,redirect, url_for, request, g
from app import webapp, config, node_ip, dbconnection
import requests


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/deleteAll', methods=['GET','POST'])
def deleteAll():
    if request.method == 'POST':
        # clear cache
        for id, ip in node_ip.items():
            node_address = 'http://' + ip + ':5001/clearCache'
            try:
                response = requests.post(url=node_address).json()
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Cache loses connection")
        #clear RDS
        dbconnection.clear()
        # clear S3
        try:
            response = requests.post(url='http://localhost:5000/deleteAll').json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Frontend loses connection")
        result = "Your cache, database and local file system have been cleared"
        return render_template("deleteAll.html",result=result)
    else:
        return render_template("deleteAll.html")
