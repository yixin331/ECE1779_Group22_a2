from flask import render_template, url_for, request, redirect, flash, g, json, send_from_directory
from app import webapp, memcache, dbconnection
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
from pathlib import Path
import os
import base64
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()
@scheduler.scheduled_job(IntervalTrigger(seconds=5))
def period_update():
    with webapp.app_context():
        memcache.period_update()


scheduler.start()


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
                return render_template("get.html", user_image=None, user_image_64=None)
            else:
                path = result[0]
                path = 'images/' + path
                webapp.logger.warning(path)
                # webapp.logger.warning(os.path.join("../images",path))
                # return render_template("get.html", user_image=path)
                return render_template("get.html", user_image=url_for('static', filename=path), pathType = "db")
        else:
            # todo: cache
            webapp.logger.warning(result)
            
            return render_template("get.html", user_image_64=result.decode('utf-8'))
    else:
        return render_template("get.html", user_image=None, method='get')


    #
    # if result != -1:
    #     response = webapp.response_class(
    #         response=json.dumps(result),
    #         status=200,
    #         mimetype='application/json'
    #     )
    # else:
    #     response = webapp.response_class(
    #         response=json.dumps("Unknown key"),
    #         status=400,
    #         mimetype='application/json'
    #     )


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
                # file is too large to put into cache
                return redirect(request.url)
            #
            #
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

    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json'
    )

    return response



@webapp.route('/invalidateKey', methods=['POST'])
def invalidateKey():
    key = request.form.get('key')
    success_code = memcache.invalidateKey(key)

    if success_code != -1:
        response = webapp.response_class(
            response=json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )
    else:
        response = webapp.response_class(
            response=json.dumps("Unknown key"),
            status=400,
            mimetype='application/json'
        )

    return response

@webapp.route('/key', methods=['GET'])
def key():
    cursor = dbconnection.list_keys()
    return render_template("key.html", cursor=cursor)


@webapp.route('/refreshConfiguration', methods=['POST'])
def refreshConfiguration():
    # TODO: refresh config?
    memcache.refreshConfiguration()

    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json'
    )

    return response


@webapp.route('/configure', methods=['GET' , 'POST'])
def configure():
    return render_template("configure.html")