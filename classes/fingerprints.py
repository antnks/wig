import json
import os
import copy

import os.path

datadir = os.path.dirname(os.path.abspath(__file__))
datadir = datadir.rsplit('/', maxsplit=1)[0]
datadir += '/data'

class Fingerprints(object):

	def __init__(self):

		self.data = {
			'cms': {
				'md5':			{'dir': datadir + '/cms/md5/',			'fps': []},
				'reqex':		{'dir': datadir + '/cms/regex/',		'fps': []},
				'string':		{'dir': datadir + '/cms/string/',		'fps': []},
				'header':		{'dir': datadir + '/cms/header/',		'fps': []}
			},
			'js': {
				'md5':			{'dir': datadir + '/js/md5/',			'fps': []},
				'reqex':		{'dir': datadir + '/js/regex/',			'fps': []},
			},
			'platform': {
				'md5':			{'dir': datadir + '/platform/md5/',		'fps': []},
				'reqex':		{'dir': datadir + '/platform/regex/',		'fps': []},
				'string':		{'dir': datadir + '/platform/string/',	'fps': []},
				'header':		{'dir': datadir + '/platform/header/',	'fps': []}
			},
			'vulnerabilities': {
				'cvedetails':	{'dir':  datadir + '/vulnerabilities/cvedetails/', 'fps': []},
			},
			'translator':		{'file': datadir + '/dictionary.json',	'dictionary': {}},
			'error_pages':		{'file': datadir + '/error_pages.json',	'fps': []},
			'interesting':		{'file': datadir + '/interesting.json',	'fps': []},
			'subdomains':		{'file': datadir + '/subdomains.json',	'fps': []},
			'os':			{'dir':  datadir + '/os/',		'fps': []}
		}

		# load fingerprints
		self._load_subdomains()
		self._load_dictionary()
		self._load_interesting()
		self._load_error()
		self._load_os()
		self._load()


	def _is_json(self, filename):
		is_json = False
		if len(filename.split('.')) == 2:
			name,ext = filename.split('.')
			is_json = ext == 'json'

		return is_json


	def _get_name(self, filename):
		name,ext = filename.split('.')
		return self.data['translator']['dictionary'][name]['name']


	def _open_file(self, filename):

		if not self._is_json(filename): return None

		try:
			with open(filename) as fh:
				fps = json.load(fh)
		except Exception as e:
			print('Error loading file: %s' % (filename))
			return None

		return fps


	def _load_subdomains(self):
		self.data['subdomains']['fps'] = self._open_file(self.data['subdomains']['file'])


	def _load_dictionary(self):
		fps = self._open_file(self.data['translator']['file'])
		if fps is not None:
			self.data['translator']['dictionary'] = fps


	def _load_error(self):
		fps = self._open_file(self.data['error_pages']['file'])
		if fps is not None:
			self.data['error_pages']['fps'] = fps


	def _load_os(self):
		for json_file in os.listdir(self.data['os']['dir']):
			fps = self._open_file(self.data['os']['dir'] + '/' + json_file)
			if fps is not None:
				self.data['os']['fps'].extend(fps)


	def _load_interesting(self):
		fps = self._open_file(self.data['interesting']['file'])

		for fp in fps:
			if 'ext' in fp:
				for ext in fp['ext']:
					fp_copy = copy.deepcopy(fp)
					fp_copy['url'] += '.' + ext
					self.data['interesting']['fps'].append(fp_copy)
			else:
				self.data['interesting']['fps'].append(fp)


	def _load(self):
		categories = ['cms', 'js', 'platform', 'vulnerabilities']
		for category in categories:
			for fp_type in self.data[category]:
				for json_file in os.listdir(self.data[category][fp_type]['dir']):
					fps = self._open_file(self.data[category][fp_type]['dir'] + '/' + json_file)
					for fp in fps:
						fp['name'] = self._get_name( json_file )
						self.data[category][fp_type]['fps'].append( fp )
