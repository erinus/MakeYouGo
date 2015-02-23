import json

class ApiMeta(object):
	def __init__(self, option=None):
		if option:
			self.option = option
		else:
			self.option = None
	def __json__(*args):
		def default(self, xObject):
			json = {}
			if xObject.option:
				json['option'] = xObject.option
			return json
		json.JSONEncoder.default = default
	__json__()
