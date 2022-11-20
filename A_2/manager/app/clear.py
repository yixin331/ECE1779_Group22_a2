from flask import render_template,redirect, url_for, request, g
from app import webapp,config, node_ip
import requests


@webapp.route('/clear', methods=['GET','POST'])
def clear():
    if request.method == 'POST':
        for id, ip in node_ip.items():
            if ip is not None:
                node_address = 'http://' + ip + ':5001/clearCache'
                try:
                    response = requests.post(url=node_address).json()
                except requests.exceptions.ConnectionError as err:
                    webapp.logger.warning("Cache loses connection")
        result = "Your cache has been cleared"
        return render_template("clear.html",result=result)
    else:
        return render_template("clear.html")
