from flask import render_template, url_for, request, g
from app import webapp, dbconnection
import requests
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
from pathlib import Path
import os


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/put', methods=['GET', 'POST'])
def put():
    result = ""
    if request.method == 'POST':
        key = request.form.get('key')
        webapp.logger.warning(key)
        # key invalid
        if not (key is not None and len(key) > 0):
            return render_template("put.html", result="Please input a valid key")
        # check file
        if 'file' not in request.files:
            return render_template("put.html", result="Please select a file")
        file = request.files['file']
        webapp.logger.warning(file)
        filename = secure_filename(file.filename)
        # check extension
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        extension = filename.rsplit('.', 1)[1].lower()
        if file and '.' in filename and extension in ALLOWED_EXTENSIONS:
            # TODO: need to change path when using EC2
            # consider: duplicate file names
            UPLOADS_PATH = join(dirname(realpath(__file__)), 'static')
            UPLOADS_PATH = os.path.join(UPLOADS_PATH, 'images')
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
            if response is None or response["success"] == "false":
                # file is too large to put into cache -> but it's already in database
                result = "File is uploaded in the database but not in cache"
                return render_template("put.html", result=result)
            result = "Uploaded into cache and database"
            return render_template("put.html", result=result)
        # else: pop up msg for error
        else:
            return render_template("put.html", result="Please select a valid image file")
    else:
        return render_template("put.html")
