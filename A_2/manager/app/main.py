from flask import render_template, redirect, url_for, request, g,json
from app import webapp, memcache_mode


@webapp.route('/',methods=['GET'])
@webapp.route('/index',methods=['GET'])
@webapp.route('/main',methods=['GET'])
# Display an HTML page with links
def main():
    return render_template("main.html",title="Manager APP")

@webapp.route('/pop_up', methods=['GET', 'POST'])
def pop_up():
    value = {"success": "true", "content": memcache_mode['num_node']}
    response = webapp.response_class(
        response=json.dumps(value),
        status=200,
    )
    return response
