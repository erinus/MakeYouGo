import os
import sys
import json

import flask

module = flask.Blueprint('myg.manager', __name__)

@module.route('/info', methods = [ 'GET' ])
def info():
	with open('%s/config.json' % (os.path.dirname(__file__))) as json_file:
		json_inst = json.load(json_file)
		data = json.dumps(json_inst)
		return flask.Response(
			status = 200,
			response = data,
			mimetype = 'application/json'
		)