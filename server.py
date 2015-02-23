import os
import sys
import json
import uuid
import hashlib
import datetime
import importlib.machinery

import flask
import flask.sessions

# extracted from
# https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/datastructures.py
class UpdateDictMixin(object):
	on_update = None
	def calls_update(name):
		def oncall(self, *args, **kw):
			rv = getattr(super(UpdateDictMixin, self), name)(*args, **kw)
			if self.on_update is not None:
				self.on_update(self)
			return rv
		oncall.__name__ = name
		return oncall
	def setdefault(self, key, default=None):
		modified = key not in self
		rv = super(UpdateDictMixin, self).setdefault(key, default)
		if modified and self.on_update is not None:
			self.on_update(self)
		return rv
	def pop(self, key, default=object()):
		modified = key in self
		if default is _missing:
			rv = super(UpdateDictMixin, self).pop(key)
		else:
			rv = super(UpdateDictMixin, self).pop(key, default)
		if modified and self.on_update is not None:
			self.on_update(self)
		return rv
	__setitem__ = calls_update('__setitem__')
	__delitem__ = calls_update('__delitem__')
	clear = calls_update('clear')
	popitem = calls_update('popitem')
	update = calls_update('update')
	del calls_update

# extracted from
# https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/datastructures.py
class CallbackDict(UpdateDictMixin, dict):
	def __init__(self, initial=None, on_update=None):
		dict.__init__(self, initial or ())
		self.on_update = on_update
	def __repr__(self):
		return '<%s %s>' % (self.__class__.__name__,
			dict.__repr__(self))

class CookieSession(CallbackDict, flask.sessions.SessionMixin):
	def __init__(self, sid=None):
		self.sid = sid
		self.store = {}
		self.modified = False

class CookieSessionInterface(flask.sessions.SessionInterface):
	def __init__(self):
		self.sessions = {}
	def open_session(self, app, request):
		sid = request.cookies.get(app.session_cookie_name)
		if sid and sid in self.sessions:
			session = self.sessions[sid]
			return session
		else:
			sid = hashlib.md5(uuid.uuid4().bytes).hexdigest().upper()
			session = CookieSession(sid=sid)
			self.sessions[sid] = session
			return session
	def save_session(self, app, session, response):
		domain = self.get_cookie_domain(app)
		if not session and session.sid not in self.sessions:
			response.delete_cookie(app.session_cookie_name,
				domain=domain)
			return
		if self.get_expiration_time(app, session):
			expiration = self.get_expiration_time(app, session)
		else:
			expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
		response.set_cookie(app.session_cookie_name,
			session.sid,
			expires=self.get_expiration_time(app, session),
			httponly=True,
			domain=domain)

PATH_APP = 'app'

app = flask.Flask(__name__)

@app.route("/")
def main():
	return 'MakeYouGo'

@app.route('/apps', methods = ['GET'])
def apps():
	infos = []
	for direname in os.listdir(PATH_APP):
		path_folder = os.path.abspath('%s/%s' % (PATH_APP, direname))
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
	return flask.Response(status = 200,
		response = data,
		mimetype = 'application/json')

if __name__ == '__main__':
	for direname in os.listdir(PATH_APP):
		path_folder = os.path.abspath('%s/%s' % (PATH_APP, direname))
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
	app.session_interface = CookieSessionInterface()
	app.run(host='0.0.0.0',
		port=9999,
		debug=True)
