from flask import render_template, url_for, request, g
from app import webapp, dbconnection
import requests


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@webapp.route('/get', methods=['GET', 'POST'])
def get():
    if request.method == 'POST':
        key = request.form.get('key')
        webapp.logger.warning(key)

        # find value in cache
        keyToSend = {'key': key}
        response = None
        try:
            response = requests.post(url='http://localhost:5001/getKey', data = keyToSend).json()
        except requests.exceptions.ConnectionError as err:
            webapp.logger.warning("Cache loses connection")
        # result = memcache.get(key)
        # webapp.logger.warning(result)
        if response is None or response["success"] == "false":
            cursor = dbconnection.get_image(key)
            result = cursor.fetchone()
            if result is None:
                # not in both
                # flash('Unknown key')
                # return redirect(request.url) ==================================================
                return render_template("get.html", user_image=None)
            else:
                path = result[0]
                path = 'images/' + path
                webapp.logger.warning(path)
                 # webapp.logger.warning(os.path.join("../images",path))
            #     # return render_template("get.html", user_image=path)
                return render_template("get.html", user_image=url_for('static', filename=path), pathType='db', result="Get from database")
        else:
            # todo: cache

            return render_template("get.html", user_image=response["content"], result="Get from cache")
    else:
        return render_template("get.html", user_image=None, method='get')