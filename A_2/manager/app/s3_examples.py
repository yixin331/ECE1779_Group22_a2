from flask import render_template, redirect, url_for, request
from app import webapp

import boto3


@webapp.route('/s3_examples', methods=['GET'])
# Display an HTML list of all s3 buckets.
def s3_list():
    # Let's use Amazon S3
    s3 = boto3.resource('s3')

    # Print out bucket names
    buckets = s3.buckets.all()

    for b in buckets:
        name = b.name

    buckets = s3.buckets.all()

    return render_template("s3_examples/list.html", title="s3 Instances", buckets=buckets)


@webapp.route('/s3_examples/<id>', methods=['GET'])
# Display details about a specific bucket.
def s3_view(id):
    s3 = boto3.resource('s3')

    bucket = s3.Bucket(id)

    for key in bucket.objects.all():
        k = key

    keys = bucket.objects.all()

    return render_template("s3_examples/view.html", title="S3 Bucket Contents", id=id, keys=keys)


@webapp.route('/s3_examples/upload/<id>', methods=['POST'])
# Upload a new file to an existing bucket
def s3_upload(id):
    # check if the post request has the file part
    if 'new_file' not in request.files:
        return redirect(url_for('s3_view', id=id))

    new_file = request.files['new_file']

    # if user does not select file, browser also
    # submit an empty part without filename
    if new_file.filename == '':
        return redirect(url_for('s3_view', id=id))

    s3 = boto3.client('s3')

    s3.upload_fileobj(new_file, id, new_file.filename)

    return redirect(url_for('s3_view', id=id))


"""
    Part 2
    
    Complete the function s3_examples.delete so that it removes an object
    from an S3 bucket.
    
    Documentation for the S3 available at:
    
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_object
    
    Search in the above URL for the string "client.delete_object"
    

"""


@webapp.route('/s3_examples/delete/<bucket_id>/<key_id>', methods=['POST'])
# Delete an object from a bucket
def s3_delete(bucket_id, key_id):
    s3 = boto3.client('s3')

    ######### your code start here #####################
    response = s3.delete_object(
        Bucket=bucket_id,
        Key=key_id,
    )
    ######### your code ends here ######################

    return redirect(url_for('s3_view', id=bucket_id))
