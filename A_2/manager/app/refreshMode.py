from flask import render_template,redirect, url_for, request, g
from app import webapp,config, dbconnection, memcache_mode
import requests
import boto3


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
#
# @webapp.route('/resize_pool', methods=['GET','POST'])
# def resize_pool(type='all',result=None):
#
#     ec2 = boto3.resource('ec2')
#     instances = ec2.instances.all()
#     size=0
#     for i in instances:
#         size = size + 1
#     size=size-1
#     return render_template("resize/resize_pool.html",title="Resize Pool",size=size,type=type,result=result)
#
# @webapp.route('/shrink_pool', methods=['GET','POST'])
# def shrink_pool():
#     size=1#requests.post(url='http://localhost:5003/getSize').json()
#     #size=size['value']
#     return resize_pool(type='manu',result='manual mode')
#
# @webapp.route('/shrink_pool', methods=['GET','POST'])
# def expand_pool():
#     size=1#requests.post(url='http://localhost:5003/getSize').json()
#     #size=size['value']
#     return resize_pool(type='manu',result='manual mode')
#
#
# @webapp.route('/resize_manu', methods=['GET', 'POST'])
# def resize_manu():
#     return render_template("mode.html", mode="Manual")
#
#
# @webapp.route('/resize_auto', methods=['GET', 'POST'])
# def resize_auto():
#     return render_template("mode.html", mode="Auto")
#
#
# @webapp.route('/auto_mode', methods=['GET', 'POST'])
# def auto_mode():
#     return resize_pool(type='auto',result='Auto mode')


@webapp.route('/refreshMode', methods=['GET', 'POST'])
def refreshMode():
    if request.method == 'GET':
        num_node = memcache_mode['num_node']
        return render_template("mode.html", num_node=num_node)
    else:
        mode = request.form['mode']
        memcache_mode['mode'] = mode
        # manual_mode
        if mode == 'Manual':
            # pause scheduler
            try:
                requests.post(url='http://localhost:5003/setMode', data=request.form)
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Autoscaler loses connection")

            num_node = int(request.form['num_node'])
            if not num_node == memcache_mode['num_node']:
                try:
                    numToSend = {'num_node': num_node}
                    requests.post(url='http://localhost:5000/sizeChange', data=numToSend)
                except requests.exceptions.ConnectionError as err:
                    webapp.logger.warning("Frontend loses connection")

        elif mode == 'Auto':
            memcache_mode['max_thr'] = float(request.form.get('max_thr'))
            memcache_mode['min_thr'] = float(request.form.get('min_thr'))
            memcache_mode['expand_ratio'] = float(request.form.get('expand_ratio'))
            memcache_mode['shrink_ratio'] = float(request.form.get('shrink_ratio'))
            try:
                dataToSend = {'num_node': memcache_mode['num_node'], 'mode': request.form['mode'], 'max_thr': request.form['max_thr'], 'min_thr': request.form['min_thr'], 'expand_ratio': request.form['expand_ratio'], 'shrink_ratio': request.form['shrink_ratio']}
                requests.post(url='http://localhost:5003/setMode', data=dataToSend)
            except requests.exceptions.ConnectionError as err:
                webapp.logger.warning("Autoscaler loses connection")

        dbconnection.put_mode(memcache_mode['num_node'], memcache_mode['mode'], memcache_mode['max_thr'], memcache_mode['min_thr'], memcache_mode['expand_ratio'], memcache_mode['shrink_ratio'])
        return render_template("mode.html", num_node=memcache_mode['num_node'], result="Mode has been reset")
