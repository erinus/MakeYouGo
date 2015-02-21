import os
import sys
import json
import flask
import importlib.machinery

PATH_APPS = 'app'

app = flask.Flask(__name__)

@app.route("/")
def main():
	return 'MakeYouGo'

@app.route('/apps', methods = [ 'GET' ])
def apps():
	infos = []
	for direname in os.listdir(PATH_APPS):
		path_folder = os.path.abspath('%s/%s' % (PATH_APPS, direname))
		path_config = '%s/config.json' % (path_folder)
		path_api = '%s/api.py' % (path_folder)
		path_web = '%s/web.py' % (path_folder)
		if os.path.exists(path_config) and os.path.isfile(path_config):
			info = {}
			with open(path_config) as file_config:
				config = json.load(file_config)
				info['name'] = config['name']
				info['code'] = config['code']
				info['desc'] = config['desc']
				info['use_api'] = os.path.exists(path_api) and os.path.isfile(path_api) and 'api.%s' % (config['name']) in app.blueprints.keys()
				info['use_web'] = os.path.exists(path_web) and os.path.isfile(path_web) and 'web.%s' % (config['name']) in app.blueprints.keys()
				infos.append(info)
	data = json.dumps(infos)
	return flask.Response(
		status = 200,
		response = data,
		mimetype = 'application/json'
	)

if __name__ == '__main__':
	for direname in os.listdir(PATH_APPS):
		path_folder = os.path.abspath('%s/%s' % (PATH_APPS, direname))
		path_config = '%s/config.json' % (path_folder)
		path_api = '%s/api.py' % (path_folder)
		path_web = '%s/web.py' % (path_folder)
		if os.path.exists(path_config) and os.path.isfile(path_config):
			with open(path_config) as file_config:
				config = json.load(file_config)
				if os.path.exists(path_api) and os.path.isfile(path_api):
					api = importlib.machinery.SourceFileLoader('api.%s' % (config['name']), path_api).load_module()
					app.register_blueprint(api.module, url_prefix = '/api/%s' % (config['name']))
				if os.path.exists(path_web) and os.path.isfile(path_web):
					api = importlib.machinery.SourceFileLoader('web.%s' % (config['name']), path_web).load_module()
					app.register_blueprint(api.module, url_prefix = '/web/%s' % (config['name']))
	app.run(
		host = '0.0.0.0',
		port = 9999
	)