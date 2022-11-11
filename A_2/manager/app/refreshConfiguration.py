from flask import render_template, redirect, url_for, request, g
from app import webapp, dbconnection, memcache_mode, node_ip, memcache_config
import requests


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/refreshConfiguration', methods=['GET', 'POST'])
def refreshConfiguration():
    if request.method == 'GET':
        return render_template("configure.html")
    else:
        policy = request.form['policy']
        size = request.form['size']
        webapp.logger.warning(policy)
        webapp.logger.warning(size)
        memcache_config['capacity'] = int(size)
        memcache_config['policy'] = policy
        dataToSend = {"policy": policy, "size": size}
        response = None
        msg = ""
        for id, ip in node_ip.items():
            if not ip == None:
                # TODO: populate it to all memcache
                node_address = 'http://' + ip + ':5001/setConfig'
                try:
                    response = requests.post(url=node_address, data=dataToSend).json()
                except requests.exceptions.ConnectionError as err:
                    webapp.logger.warning("Cache loses connection")
                if response is None:
                    msg = "Cache loses connection"
                elif response["success"] == "true":
                    msg = "Your cache has been reset"

        dbconnection.put_config(int(size), policy)
        return render_template("configure.html", result=msg)