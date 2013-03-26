#!/usr/bin/env python

from flask import Flask, render_template, request, redirect, url_for
from suds.client import Client
from suds.plugin import MessagePlugin
from contextlib import closing
from datetime import datetime
import sqlite3, json

SERVICE_FIELDS = (
		{'name': 'url', 'label': 'WSDL URL (can be file:// too)', 'required': True},
		{'name': 'location', 'label': 'Location (overrides the one in the WSDL)'},
		{'name': 'username', 'label': 'Username for HTTP basic auth (optional)'},
		{'name': 'password', 'label': 'Password for HTTP basic auth (optional)'})

app = Flask(__name__)
app.jinja_env.globals['SERVICE_FIELDS'] = SERVICE_FIELDS
app.jinja_env.globals['ISO_DATESTR'] = datetime.now().isoformat('T')[:19] + 'Z'


@app.route('/')
def list_services():
	return render_template('list_services.html', services=get_service_list())


def get_service_list():
	with get_db_connection() as conn:
		for row in conn.execute('SELECT id, properties FROM services ORDER BY id ASC'):
			yield row[0], json.loads(row[1])


@app.route('/add_service', methods=['POST'])
def add_service():
	properties = {}
	for field in SERVICE_FIELDS:
		name = field['name']
		value = request.form.get(name)
		if not value:
			if field.get('required'):
				raise ValueError('Field "{0}" is required'.format(field['label']))
		else:
			properties[name] = value
	properties = json.dumps(properties)
	with get_db_connection() as conn:
		with conn:
			conn.execute('INSERT INTO services (properties) VALUES (?)', (properties,))
	return redirect(url_for('list_services'))


@app.route('/services/<int:sid>.html')
def show_service(sid):
	client = get_service_client(sid)
	return render_template('show_service.html', sd=client.sd, sid=sid, factory=client.factory)


@app.route('/services/<int:sid>/<op_name>')
def invoke_service(sid, op_name):
	rop = RawOutPlugin()
	client = get_service_client(sid, plugins=[rop])
	op = getattr(client.service, op_name)
	kwargs = {}
	process_formdata(kwargs.__setitem__, request.values, client)
	try:
		op(**kwargs)
	except Exception as e:
		print e
		status = 500
	else:
		status = 200
	return rop.raw_out, status, {'Content-type': 'text/xml'}


def process_formdata(callback, formdata, client):
	ignore_complex = set()
	for key, value in formdata.iteritems():
		if key.endswith('__string'):
			callback(key[:-8], value)
		elif key.endswith('__enum'):
			name, datatype, _ = key.rsplit('__', 2)
			try:
				callback(name, getattr(client.factory.create(datatype), value))
			except AttributeError:
				pass
		elif key.endswith('__complex'):
			_, name, datatype, _ = key.rsplit('__', 3)
			if name not in ignore_complex:
				ignore_complex.add(name)
				data = client.factory.create(datatype)
				postfix_len = 2 + len(name) + 2 + len(datatype) + 9
				process_formdata(data.__setattr__, {k[:-postfix_len]: v
					for k, v in formdata.iteritems()
					if k.endswith('__' + name + '__' + datatype + '__complex')},
					client)
				callback(name, data)


class RawOutPlugin(MessagePlugin):
	def __init__(self):
		self.raw_out = ''


	def received(self, context):
		self.raw_out = context.reply


def get_service_client(sid, **kwargs):
	with get_db_connection() as conn:
		cursor = conn.execute('SELECT properties FROM services WHERE id = ?', (sid,))
		((properties,),) = cursor.fetchall()
		c_kwargs = json.loads(properties)
		c_kwargs.update(kwargs)
		return Client(**c_kwargs)


def get_db_connection():
	conn = sqlite3.connect('wsfacade.db')
	with conn:
		conn.execute('''CREATE TABLE IF NOT EXISTS services (
			id INTEGER PRIMARY KEY AUTOINCREMENT, properties TEXT)''')
	return closing(conn)


if __name__ == '__main__':
    app.run(debug=True)
