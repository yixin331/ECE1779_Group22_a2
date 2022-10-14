from app import webapp, total_size, num_item, dbconnection, num_request, num_get, num_miss
from flask import request, json, g


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/putStat', methods=['POST'])
def putStat():
    global num_item
    global total_size
    global num_request
    global num_get
    global num_miss
    dbconnection.put_stat(num_item, total_size, num_request, num_get, num_miss)
    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response
