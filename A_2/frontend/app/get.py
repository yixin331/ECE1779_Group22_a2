from flask import render_template, url_for, request, g
from app import webapp, dbconnection
import requests
from os.path import join, dirname, realpath
from pathlib import Path
import os
import boto3
from io import BufferedReader

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/get', methods=['GET', 'POST'])
def get():
    if request.method == 'POST':
        key = request.form.get('key')
        result = ""
        # find value in cache
        keyToSend = {'key': key}
        response = None
        try:
            response = requests.post(url='http://localhost:5002/getKey', data=keyToSend).json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Manager app loses connection")
        if response is None or response["success"] == "false":
            cursor = dbconnection.get_image(key)
            result = cursor.fetchone()
            if result is None:
                return render_template("get.html", user_image=None)
            else:
                s3 = boto3.resource('s3')
                bucket_name = 'files'
                file = s3.get_object(Bucket=bucket_name, key=key)
                keyToSend = {'key': key}
                fileToSend = {'file': BufferedReader(file)}
                response = None
                try:
                    response = requests.post(url='http://localhost:5002/putImage', data=keyToSend,
                                             files=fileToSend).json()
                except requests.exceptions.ConnectionError as err:
                    webapp.logger.warning("Manager app loses connection")
                if response is None or response["success"] == "false":
                    # file is too large to put into cache
                    result = "Get from database but fail to reload to cache"
                else:
                    result = "Get from database and reload into cache"
                # TODO : check if it works
                return render_template("get.html", user_image=file.read(), pathType='db',
                                       result=result)
        else:
            return render_template("get.html", user_image=response["content"], result="Get from cache")
    else:
        return render_template("get.html", user_image=None, method='get')