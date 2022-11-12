#!venv/bin/python
from app import webapp

# webapp.run(host='0.0.0.0', debug=False)
webapp.run('0.0.0.0',5002,debug=False)
