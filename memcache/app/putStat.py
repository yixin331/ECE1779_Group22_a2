from app import webapp, dbconnection, memcache_stat
from flask import request, json, g


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/putStat', methods=['POST'])
def putStat():
    dbconnection.put_stat(memcache_stat['num_item'], memcache_stat['total_size'], memcache_stat['num_request'], memcache_stat['num_get'], memcache_stat['num_miss'])
    value = {"success": "true"}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
        mimetype='application/json'
    )
    return response
