from flask import render_template, url_for, request
from app import webapp
import requests


@webapp.route('/clear', methods=['POST'])
def clear():
    response = None
    msg = ""
    try:
        response = requests.post(url='http://localhost:5001/clearCache').json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Cache loses connection")
    if response is None:
        msg = "Cache loses connection"
    elif response["success"] == "true":
        msg = "Your cache has been cleared"
    return render_template("configure.html", result=msg)