from flask import render_template, url_for, request, redirect, flash, g, json, send_from_directory
from app import webapp, dbconnection
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
from pathlib import Path
from collections import OrderedDict
import os
import base64
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# scheduler = BackgroundScheduler()
# 
# 
# @scheduler.scheduled_job(IntervalTrigger(seconds=5))
# def period_update():
#     with webapp.app_context():
#         memcache.period_update()
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


@webapp.route('/get', methods=['GET', 'POST'])
def get():
    if request.method == 'POST':
        key = request.form.get('key')
        webapp.logger.warning(key)

        # find value in cache
        result = memcache.get(key)
        webapp.logger.warning(result)

        if result == -1:
            cursor = dbconnection.get_image(key)
            result = cursor.fetchone()
            if result is None:
                # not in both
                # flash('Unknown key')
                # return redirect(request.url) ==================================================
                return render_template("get.html", user_image=None)
            else:
                path = result[0]
                path = 'images/' + path
                webapp.logger.warning(path)
                # webapp.logger.warning(os.path.join("../images",path))
                # return render_template("get.html", user_image=path)
                return render_template("get.html", user_image=url_for('static', filename=path), pathType='db')
        else:
            # todo: cache

            return render_template("get.html", user_image=result.decode('utf-8'))
    else:
        return render_template("get.html", user_image=None, method='get')


@webapp.route('/put', methods=['GET', 'POST'])
def put():
    result = ""
    if request.method == 'POST':
        # check key
        webapp.logger.warning(request.form['key'])
        key = request.form.get('key')
        webapp.logger.warning(key)
        # key invalid
        if not (key is not None and len(key) > 0):
            # todo: find a way for popout msg -> flash()
            # flash('Please input a valid key')
            return redirect(request.url)
        # check file
        if 'file' not in request.files:
            # flash('Please select a file')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            # flash('No selected file')
            return redirect(request.url)
        webapp.logger.warning(file)
        filename = secure_filename(file.filename)
        # check extension
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        if file and '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            # TODO: need to change path when using EC2
            # consider: duplicate file names
            UPLOADS_PATH = join(dirname(realpath(__file__)), 'static\\images')
            Path(UPLOADS_PATH).mkdir(parents=True, exist_ok=True)
            path = os.path.join(UPLOADS_PATH, filename)
            webapp.logger.warning(path)
            file.save(path)
            dbconnection.put_image(key, filename)
            # put in cache
            success_code = memcache.put(key, file)
            if success_code == -1:
                # file is too large to put into cache -> but it's already in database
                result = "File is uploaded in the database but not in cache"
                return render_template("put.html", result=result)
            result = "Uploaded"
            return render_template("put.html", result=result)
        # else: pop up msg for error
        else:
            return redirect(request.url)

    else:
        return render_template("put.html")


@webapp.route('/clear', methods=['POST'])
def clear():
    memcache.clear()
    msg = "Your cache has been cleared"
    return render_template("configure.html", result=msg)


@webapp.route('/key', methods=['GET'])
def key():
    cursor = dbconnection.list_keys()
    return render_template("key.html", cursor=cursor)


@webapp.route('/refreshConfiguration', methods=['GET', 'POST'])
def refreshConfiguration():
    if request.method == 'GET':
        return render_template("configure.html")
    else:
        policy = request.form['policy']
        size = request.form['size']
        webapp.logger.warning(policy)
        webapp.logger.warning(size)
        memcache.set_config(int(size), policy)
        msg = "Your cache has been reset"
        return render_template("configure.html", result=msg)


@webapp.route('/stat', methods=['GET'])
def stat():
    cursor = memcache.show_stat()
    return render_template("statistics.html", cursor=cursor)


@webapp.route('/api/upload', methods=['POST'])
def upload():
    key = request.form['key']
    webapp.logger.warning(key)

    file = request.files['file']
    webapp.logger.warning(file)

    if not (key is not None and len(key) > 0):
        value = {"success": "false", "error": {"code": 400, "message": "INVALID_ARGUMENT: KEY"}}
        response = webapp.response_class(
            response=json.dumps(value),
            status=400,
            mimetype='application/json'
        )
        return response

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
        UPLOADS_PATH = join(dirname(realpath(__file__)), 'static\\images')
        Path(UPLOADS_PATH).mkdir(parents=True, exist_ok=True)
        path = os.path.join(UPLOADS_PATH, filename)
        file.save(path)
        dbconnection.put_image(key, filename)
        memcache.put(key, file)
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
    webapp.logger.warning(key)
    result = memcache.get(key)
    if result == -1:
        cursor = dbconnection.get_image(key)
        result = cursor.fetchone()
        if result is None:
            value = {"success": "false", "error": {"code": 400, "message": "Key does not exist"}}
            response = webapp.response_class(
                response=json.dumps(value),
                status=400,
                mimetype='application/json'
            )
            return response
        else:
            filename = result[0]
            path = join(dirname(realpath(__file__)), 'static\\images')
            path = os.path.join(path,filename)
            webapp.logger.warning(path)
            f = open(path,"rb")
            image_string = base64.b64encode(f.read())
            webapp.logger.warning(image_string)
            value = {"success": "true", "content": image_string.decode('utf-8')}
            response = webapp.response_class(
                response=json.dumps(value),
                status=200,
                mimetype='application/json'
            )
            return response
    else:
        value = {"success": "true", "content": result.decode('utf-8')}
        response = webapp.response_class(
            response=json.dumps(value),
            status=200,
            mimetype='application/json'
        )
        return response


