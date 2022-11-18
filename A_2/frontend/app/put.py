from flask import render_template, url_for, request, g
from app import webapp, dbconnection
import requests
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
from pathlib import Path
import os
import base64
import boto3
from botocore.exceptions import ClientError
from app.config import aws_config


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/put', methods=['GET', 'POST'])
def put():
    result = ""
    if request.method == 'POST':
        if ('key' not in request.form):
            return render_template("put.html", result="Please input a valid key")
        key = request.form.get('key')
        # key invalid
        if not (key is not None and len(key) > 0):
            return render_template("put.html", result="Please input a valid key")
        # check file
        if 'file' not in request.files:
            return render_template("put.html", result="Please select a file")
        file = request.files['file']
        filename = secure_filename(file.filename)
        # check extension
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
        if not created:
            try:
                response = s3.create_bucket(Bucket=bucket_name)
            except ClientError as e:
                webapp.logger.warning("Fail to create a bucket")
        if file and '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
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
            if response is None or response["success"] == "false":
                # file is too large to put into cache -> but it's already in database
                result = "File is uploaded in the database but not in cache"
                return render_template("put.html", result=result)
            result = "Uploaded into cache and database"
            return render_template("put.html", result=result)
        else:
            return render_template("put.html", result="Please select a valid image file")
    else:
        return render_template("put.html")
