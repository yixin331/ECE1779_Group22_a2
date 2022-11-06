from flask import render_template, url_for, request, g, json
from app import webapp
import requests


@webapp.route('/sizeChange', methods=['POST'])
def sizeChange():
    if request.method == 'POST':
        result = ""
        # receive a request from Manager app contains a field of resize instance number
        num = request.form.get('num_node')
        # send a request to Manager app to rebalance mapping
        numToSend = {'num_node': num}
        response = None
        try:
            response = requests.post(url='http://localhost:5002/map', data=numToSend).json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Manager app loses connection")
        if response is None or response["success"] == "false":
            result = "Manager app failed to change pool size"
            return render_template("index.html", result=result)
        # back to home page with message
        result = "Cache pool size has been changed."
        return render_template("index.html", result=result)
