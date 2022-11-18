from flask import render_template, url_for, request, redirect, flash, g, json, send_from_directory
from app import webapp, dbconnection
from app.config import aws_config
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
from pathlib import Path
import requests
import os
import base64
import boto3
import io


# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.interval import IntervalTrigger
#
# scheduler = BackgroundScheduler()
#
#
# @scheduler.scheduled_job(IntervalTrigger(seconds=5))
# def period_update():
#     with webapp.app_context():
#         try:
#             response = requests.post(url='http://localhost:5001/putStat').json()
#         except requests.exceptions.ConnectionError as err:
#             webapp.logger.warning("Cache loses connection")
#
#
# scheduler.start()


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/')
def main():
    return render_template("index.html")


@webapp.route('/api/upload', methods=['POST'])
def upload():
    if 'key' not in request.form:
        value = {"success": "false", "error": {"code": 400, "message": "Key not provided"}}
        response = webapp.response_class(
            response=json.dumps(value),
            status=400,
            mimetype='application/json'
        )
        return response
    key = request.form['key']
    if not (key is not None and len(key) > 0):
        value = {"success": "false", "error": {"code": 400, "message": "INVALID_ARGUMENT: KEY"}}
        response = webapp.response_class(
            response=json.dumps(value),
            status=400,
            mimetype='application/json'
        )
        return response
    if request.files is None or 'file' not in request.files:
        value = {"success": "false", "error": {"code": 400, "message": "File not provided"}}
        response = webapp.response_class(
            response=json.dumps(value),
            status=400,
            mimetype='application/json'
        )
        return response
    file = request.files['file']
    if file.filename == '' or '.' not in file.filename:
        value = {"success": "false", "error": {"code": 404, "message": "FILE NOT FOUND"}}
        response = webapp.response_class(
            response=json.dumps(value),
            status=404,
            mimetype='application/json'
        )
        return response
    filename = secure_filename(file.filename)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    # s3 create bucket
    s3 = boto3.client(
        's3',
        aws_config['region'],
        aws_access_key_id=aws_config['access_key_id'],
        aws_secret_access_key=aws_config['secret_access_key']
    )
    response = s3.list_buckets()
    bucket_name = '1779a2files'
    created = False
    for bucket in response['Buckets']:
        if bucket["Name"] == bucket_name:
            created = True
            webapp.logger.warning('Bucket already exists')
    if not created:
        try:
            response = s3.create_bucket(Bucket=bucket_name)
        except ClientError as e:
            webapp.logger.warning("Fail to create a bucket")
    if file and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        extension = filename.rsplit('.', 1)[1].lower()
        s3.put_object(Bucket=bucket_name, Key=key, Body=file)
        dbconnection.put_image(key, key + "." + extension)
        file.seek(0, 0)
        # put in cache
        keyToSend = {'key': key}
        fileToSend = {'file': file}
        response = None
        try:
            response = requests.post(url='http://localhost:5002/putImage', data=keyToSend, files=fileToSend).json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Manager app loses connection")
        # put successfully in DB already
        value = {"success": "true"}
        response = webapp.response_class(
            response=json.dumps(value),
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        value = {"success": "false", "error": {"code": 415, "message": "unsupported file type"}}
        response = webapp.response_class(
            response=json.dumps(value),
            status=415,
            mimetype='application/json'
        )
        return response


@webapp.route('/api/list_keys', methods=['POST'])
def list_keys():
    cursor = dbconnection.list_keys()
    keys = []
    for row in cursor:
        keys.append(row[0])
    value = {"success": "true",
             "keys": keys}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response


@webapp.route('/api/key/<key>', methods=['POST'])
def list_key(key):
    result = ""
    keyToSend = {'key': key}
    response = None
    try:
        response = requests.post(url='http://localhost:5002/getKey', data=keyToSend).json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Manager app loses connection")
    if response is None or response["success"] == "false":
        #  cache miss, get from DB
        cursor = dbconnection.get_image(key)
        result = cursor.fetchone()
        if result is None:
            # not in both
            value = {"success": "false", "error": {"code": 400, "message": "Key does not exist"}}
            response = webapp.response_class(
                response=json.dumps(value),
                status=400,
                mimetype='application/json'
            )
            return response
        else:
            s3 = boto3.client(
                's3',
                aws_config['region'],
                aws_access_key_id=aws_config['access_key_id'],
                aws_secret_access_key=aws_config['secret_access_key']
            )
            bucket_name = '1779a2files'
            file = s3.get_object(Bucket=bucket_name, Key=key)['Body']
            file_byte = io.BytesIO(file.read())
            # reload in cache
            keyToSend = {'key': key}
            fileToSend = {'file': file_byte}
            webapp.logger.warning('reload into cache')
            try:
                response = requests.post(url='http://localhost:5002/putImage', data=keyToSend, files=fileToSend).json()
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Manager app loses connection")
            # successfully get key
            file_byte.seek(0, 0)
            encode_str = base64.b64encode(file_byte.read())
            value = {"success": "true", "content": encode_str.decode('utf-8')}
            response = webapp.response_class(
                response=json.dumps(value),
                status=200,
                mimetype='application/json'
            )
            return response
    else:
        value = {"success": "true", "content": response["content"]}
        response = webapp.response_class(
            response=json.dumps(value),
            status=200,
            mimetype='application/json'
        )
        return response
