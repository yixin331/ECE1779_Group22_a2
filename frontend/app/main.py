from flask import render_template, url_for, request, redirect, flash, g, json, send_from_directory
from app import webapp, dbconnection
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
from pathlib import Path
import requests
import os
import base64
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()


@scheduler.scheduled_job(IntervalTrigger(seconds=5))
def period_update():
    with webapp.app_context():
        try:
            response = requests.post(url='http://localhost:5001/putStat').json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Cache loses connection")


scheduler.start()


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

    file = request.files['file']
    if 'file' not in request.files or file.filename == '' or '.' not in file.filename:
        value = {"success": "false", "error": {"code": 404, "message": "FILE NOT FOUND"}}
        response = webapp.response_class(
            response=json.dumps(value),
            status=404,
            mimetype='application/json'
        )
        return response

    filename = secure_filename(file.filename)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    if file and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        extension = filename.rsplit('.', 1)[1].lower()
        UPLOADS_PATH = join(dirname(realpath(__file__)), 'static')
        UPLOADS_PATH = os.path.join(UPLOADS_PATH,'images')
        Path(UPLOADS_PATH).mkdir(parents=True, exist_ok=True)
        path = os.path.join(UPLOADS_PATH, key + "." + extension)
        file.save(path)
        dbconnection.put_image(key, key + "." + extension)
        # put in cache
        keyToSend = {'key': key}
        fileToSend = {'file': open(path, "rb")}
        response = None
        try:
            response = requests.post(url='http://localhost:5001/putImage', data=keyToSend, files=fileToSend).json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Cache loses connection")
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


@webapp.route('/api/key', methods=['POST'])
def list_key():
    key = request.form.get('key')
    result = ""
    # find value in cache
    keyToSend = {'key': key}
    response = None
    try:
        response = requests.post(url='http://localhost:5001/getKey', data=keyToSend).json()
    except requests.exceptions.ConnectionError as err:
        webapp.logger.warning("Cache loses connection")
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
            webapp.logger.warning("get from DB")
            filename = result[0]
            path = join(dirname(realpath(__file__)), 'static')
            path = os.path.join('images')
            file_path = os.path.join(path, filename)
            f = open(file_path, "rb")
            # try to store image inside cache
            keyToSend = {'key': key}
            fileToSend = {'file': open(file_path, "rb")}
            cache_response = None
            try:
                cache_response = requests.post(url='http://localhost:5001/putImage', data=keyToSend, files=fileToSend).json()
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Cache loses connection")
            # successfully get key
            image_string = base64.b64encode(f.read())
            value = {"success": "true", "content": image_string.decode('utf-8')}
            response = webapp.response_class(
                response=json.dumps(value),
                status=200,
                mimetype='application/json'
            )
            return response
    else:
        value = {"success": "true", "content": response["content"] }
        response = webapp.response_class(
            response=json.dumps(value),
            status=200,
            mimetype='application/json'
        )
        return response


