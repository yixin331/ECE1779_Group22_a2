from flask import render_template, redirect, url_for, request
from app import webapp

import boto3
from app import config
from datetime import datetime, timedelta
from operator import itemgetter

@webapp.route('/node_configure', methods=['GET','POST'])
def node_configure():
    return render_template("configure/configure.html")

@webapp.route('/refreshConfiguration', methods=['GET', 'POST'])
def refreshConfiguration():
    if request.method == 'GET':
        return render_template("configure.html")
    else:
        policy = request.form['policy']
        size = request.form['size']
        webapp.logger.warning(policy)
        webapp.logger.warning(size)
        dataToSend = {"policy": policy, "size": size}
        response = None
        msg = ""
        try:
            response = requests.post(url='http://localhost:5001/setConfig', data=dataToSend).json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Cache loses connection")
        if response is None:
            msg = "Cache loses connection"
        elif response["success"] == "true":
            msg = "Your cache has been reset"
        return render_template("configure.html", result=msg,title="Resize Pool")