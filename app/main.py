
from flask import render_template, url_for, request
from app import webapp, memcache
from flask import json

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@webapp.route('/')
def main():
    # change the home page
    return render_template("index.html")

@webapp.route('/get',methods=['GET'])
def get():
    key = request.form.get('key')
    result = memcache.get(key)

    if result != -1:
        response = webapp.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json'
        )
    else:
        response = webapp.response_class(
            response=json.dumps("Unknown key"),
            status=400,
            mimetype='application/json'
        )
    # frontend
    return render_template("get.html")
    # return response

@webapp.route('/put',methods=['POST'])
def put():
    key = request.form.get('key')
    value = request.form.get('value')
    success_code = memcache.put(key, value)

    if success_code != -1:
        response = webapp.response_class(
            response=json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )
    else:
        response = webapp.response_class(
            response=json.dumps("Image is too large"),
            status=400,
            mimetype='application/json'
        )

    #return response
    return render_template("put.html")

@webapp.route('/clear',methods=['POST'])
def clear():
    memcache.clear()

    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json'
    )

    return response

@webapp.route('/invalidateKey',methods=['POST'])
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

@webapp.route('/refreshConfiguration',methods=['POST'])
def refreshConfiguration():
    # TODO: refresh config?
    memcache.refreshConfiguration()

    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json'
    )

    return response
