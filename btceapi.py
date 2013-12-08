#!/d/python27/python
# -*- coding: utf8 -*-

import httplib
import json
import hashlib
import hmac
import urllib
import time
import copy

basic_headers = {
	'accept-encoding': 'gzip,deflate,sdch',
	'accept-language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
	'ser-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'cache-control': 'max-age=0',
	'cookie': '__cfduid=dd90c2e3e9bb7bdb3cd5198be8f5dbe791384870170571; a=e875cef56d27a5edf018a9bca35c9dbf; chatRefresh=1; locale=cn; SESS_ID=7kih3i16d77fjpslu5paonk3btf0j60o; auth=1; bId=RQ8PDX0RXOYGDACM4G95NGHQAP7SMR6M; __utma=45868663.1586475762.1384870193.1386490191.1386493983.57; __utmb=45868663.19.10.1386493983; __utmc=45868663; __utmz=45868663.1384870193.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'}

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
		headers = copy.copy(basic_headers)
		conn = httplib.HTTPSConnection('btc-e.com', timeout = 15)
		conn.request('GET', '%s/%s/%s' % (self.public_api, pair, item), headers=headers)
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

			conn = httplib.HTTPSConnection('btc-e.com', timeout = 15)
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
