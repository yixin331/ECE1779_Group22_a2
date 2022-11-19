from flask import render_template, url_for, request, g
from app import webapp, dbconnection
import requests
from os.path import join, dirname, realpath
from pathlib import Path
import os
import io
import boto3
import base64
from app.config import aws_config

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
            response = requests.post(url='http://54.175.104.127:5002/getKey', data=keyToSend).json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Manager app loses connection")
        if response is None or response["success"] == "false":
            cursor = dbconnection.get_image(key)
            result = cursor.fetchone()
            if result is None:
                return render_template("get.html", user_image=None)
            else:
                s3 = boto3.client(
                    's3',
                    aws_config['region'],
                    aws_access_key_id=aws_config['access_key_id'],
                    aws_secret_access_key=aws_config['secret_access_key']
                )
                # s3 = boto3.client('s3')
                bucket_name = '1779a2files'
                file = s3.get_object(Bucket=bucket_name, Key=key)['Body']
                file_byte = io.BytesIO(file.read())
                # reload in cache
                keyToSend = {'key': key}
                fileToSend = {'file': file_byte}
                response = None
                webapp.logger.warning('reload into cache')
                try:
                    response = requests.post(url='http://54.175.104.127:5002/putImage',
                                             data=keyToSend,
                                             files=fileToSend).json()
                except requests.exceptions.ConnectionError as err:
                    webapp.logger.warning("Manager app loses connection")
                if response is None or response["success"] == "false":
                    # file is too large to put into cache
                    result = "Get from database but fail to reload to cache"
                else:
                    dbconnection.update_image(key)
                    result = "Get from database and reload into cache"
                file_byte.seek(0,0)
                encode_str = base64.b64encode(file_byte.read())
                # webapp.logger.warning(encode_str)
                return render_template("get.html", user_image=encode_str.decode('utf-8'), pathType='db',
                                       result=result)
        else:
            dbconnection.update_image(key)
            return render_template("get.html", user_image=response["content"], result="Get from cache")
    else:
        return render_template("get.html", user_image=None, method='get')