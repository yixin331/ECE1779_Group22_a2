from flask import render_template, url_for, request, g
from app import webapp
import requests


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
        return render_template("configure.html", result=msg)