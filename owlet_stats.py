__author__ = 'fgorodishter'

import requests
from requests_toolbelt.utils import dump
import json
import time

headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json'}
auth_header = {'Authorization' : 'auth_token ***'}
properties_url = 'https://ads-field.aylanetworks.com/apiv1/dsns/AC********/properties'

properties = ['OXYGEN_LEVEL', 'HEART_RATE']

auth_token = ''
expire_time = 0
last_time = ''

def login():
	global auth_token, expire_time
	login_url = 'https://user.aylanetworks.com:443/users/sign_in.json'
	login_payload = {
	  "user": {
	    "email": "EMAIL",
	    "password": "PASS",
	    "application": {
	      "app_id": "OWL-id",
	      "app_secret": "OWL-4163742"
	    }
	  }
	}
	
	#print (auth_token, expire_time, time.time())
	if (auth_token == '') or (expire_time <= time.time()) :
		print ('Generating token')
		data = requests.post(login_url, json=login_payload, headers=headers)
		auth_token = data.json()['access_token']
		expire_time = time.time() + 3600
		print (auth_token)

while True:
	login()
	time.sleep(1)

	auth_header = {'Authorization' : 'auth_token ' + auth_token}
	auth_header.update(headers)

	output = {}
	for measure in properties:
		url = properties_url + '/' + measure
		data = requests.get(url, headers=auth_header)
		#woo = dump.dump_all(data)
		#print(woo.decode('utf-8'))
		#print(data, data.text, data.headers)
		data_json = data.json()
		if data_json['property']['data_updated_at'] == last_time:
			print('.')
		else:
			print (measure, data_json['property']['value'], data_json['property']['data_updated_at'])
			output.update({measure: data_json['property']['value'], 'data_updated_at': data_json['property']['data_updated_at']})
	
	# log to es
	requests.post('http://ES_ADDRESS:9200/owlet/measure/' + output['data_updated_at'], verify=False, json=output, headers=headers)

	# if we want to remove duplicate posts, uncomment and fix this	
	#last_time = data.json()['property']['data_updated_at']
