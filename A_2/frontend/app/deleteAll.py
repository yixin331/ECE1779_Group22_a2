from flask import request, g, json
from app import webapp
import requests
import boto3


@webapp.route('/deleteAll', methods=['POST'])
def deleteAll():
    if request.method == 'POST':
        response = None
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('1779a2files')
        bucket.objects.all().delete()
        value = {"success": "true"}
        response = webapp.response_class(
            response=json.dumps(value),
            status=200,
            mimetype='application/json'
        )
        return response
