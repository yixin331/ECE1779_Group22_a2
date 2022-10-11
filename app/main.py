from flask import render_template, url_for, request, redirect, flash, g, json
from app import webapp, memcache, dbconnection
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os


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

        # not in cache
        if result == -1:
            # find value in DB
            # TODO: Return cursor (rows) instead of success code ->> 
           
            # result = DB.get(key)
            if result == -1:
                # not in both
                # flash('Unknown key')
                return redirect(request.url)
            else:
        #  TODO: return path -->>> need to find image in local file system
                result = "TODO"

        return render_template("get.html", user_image=result)
    else:
        return render_template("get.html")

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
            # TODO: add a config file for the folder path;
            # needs to figure out how to write path
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.save(os.path.join("D:", filename))
            path = os.path.join("D:", filename)
            webapp.logger.warning(path)
            dbconnection.put_image(key, path)
            # put in cache
            # success_code = memcache.put(key, file)
            # 
            #
            return render_template("put.html")
        # else: pop up msg for error
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
