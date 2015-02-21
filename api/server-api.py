import os
import sys
import json

PATH_APP = '../app'

sys.path.append(os.path.abspath(PATH_APP))

import flask

app = flask.Flask(__name__)

import importlib
import importlib.machinery

for direname in os.listdir(PATH_APP):
	module_path = os.path.realpath('%s/%s' % (PATH_APP, direname))
	api_path = '%s/%s' % (module_path, 'api.py')
	if os.path.exists(api_path) and os.path.isfile(api_path):
		loader = importlib.machinery.SourceFileLoader(direname, api_path)
		module = loader.load_module()
		app.register_blueprint(module.module, url_prefix = '/%s' % (direname))

@app.route("/")
def main():
	return 'MakeYouGo'

if __name__ == '__main__':
	# for blueprint in app.blueprints:
	# 	print blueprint
	app.run(
		host = '0.0.0.0',
		port = 9999
	)
