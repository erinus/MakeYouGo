import os
import sys
import json
import flask

module = flask.Blueprint('web.myg.storage', __name__)

@module.route('/', methods = [ 'GET' ])
def info():
	return flask.Response(
		status = 200,
		response = 'Storage',
		mimetype = 'text/html'
	)