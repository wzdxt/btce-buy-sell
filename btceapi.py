#!/d/python27/python
# -*- coding: utf8 -*-

import httplib
import json
import hashlib
import hmac
import urllib
import time

class BTCEApi():
	nonce = int(time.time())
	BTC_USD = 'btc_usd'
	BTC_RUR = 'btc_rur'
	BTC_EUR = 'btc_eur'
	LTC_BTC = 'ltc_btc'
	LTC_USD = 'ltc_usd'
	LTC_RUR = 'ltc_rur'
	LTC_EUR = 'ltc_eur'
	USD_RUR = 'usd_rur'
	EUR_USD = 'eur_usd'
	def __init__(self, key, secret):
		self.public_api = '/api/2'
		self.key = key
		self.secret = secret
	
	def __get_nonce(self):
		BTCEApi.nonce = BTCEApi.nonce + 1
		return BTCEApi.nonce

	def __set_nonce(self, nonce):
		BTCEApi.nonce = nonce
	
	def __send_public_request(self, pair, item):
		conn = httplib.HTTPSConnection('btc-e.com', timeout = 10)
		conn.request('GET', '%s/%s/%s' % (self.public_api, pair, item))
		response = conn.getresponse()
		if response.status == 200:
			resp_dict = json.loads(response.read())
			if 'success' in resp_dict and resp_dict['success'] == 0:
				print 'error, response success = 0'
			else:
				return resp_dict
		else:
			print 'status:', response.status
			print 'reason:', response.reason

	def get_fee(self, pair):
		return self.__send_public_request(pair, 'fee')

	def get_depth(self, pair):
		return self.__send_public_request(pair, 'depth')

	def __get_hashed_params(self, encoded_params):
		return hmac.new(self.secret, encoded_params, hashlib.sha512).hexdigest()
	
	def get_info(self):
		params = {'method': 'getInfo'}
		return self.__private_request(params)
	
	def cancel_order(self, order_id):
		params = {'method': 'CancelOrder'}
		params['order_id'] = order_id
		return self.__private_request(params)
	
	def trade(self, pair, type, rate, amount):
		params = {'method': 'Trade'}
		params['pair'] = pair
		params['type'] = type
		params['rate'] = rate
		params['amount'] = amount
		return self.__private_request(params)
	
	def get_order_list(self):
		params = {'method': 'OrderList'}
		return self.__private_request(params)
	
	def __private_request(self, params):
		try:
			nonce = self.__get_nonce()
			params['nonce'] = nonce
			encoded_params = urllib.urlencode(params)

			sign = self.__get_hashed_params(encoded_params)
			headers = {'Sign' : sign, 'Key' : self.key, 'Content-type': 'application/x-www-form-urlencoded'}

			conn = httplib.HTTPSConnection('btc-e.com', timeout = 10)
			conn.request('POST', '/tapi', encoded_params, headers)
			response = conn.getresponse()

			if response.status == 200:
				resp_dict = json.loads(response.read())
				if resp_dict['success'] == 0:
					err_message = resp_dict['error']
					print 'api fails:', err_message
					if "invalid nonce" in err_message:
						s = err_message.split(",")
						expected = int(s[-2].split(":")[1])
						self.__set_nonce(expected - 1)
						return self.__private_request(params)
					else:
						return None
				return resp_dict['return']
			else:
				print 'status:', response.status
				print 'reason:', response.reason
				return None
		finally:
			conn.close()
