#!/d/python27/python
# -*- coding: utf8 -*-

from __future__ import division

import time
import math

from strategy import btce_strategy
from btceapi import BTCEApi

def run(key, secret):
	print
	print 'start running ...'
	api = BTCEApi(key, secret)

	sleep_time = 10
	
	while True:
		try:
			orders = get_my_orders(api, btce_strategy.keys())
			# orders = {'eur':{'buying': xxx, 'selling': xxx}, ...}
			funds = get_funds(api, btce_strategy.keys())
			for item, content in strategy:
				remain = content['alloc'] - orders[item]['buying'] + orders[item]['selling'] 
				if remain > 1:
					buy_item(item, content, remain)
				if funds[item] > 1:
					sell_item(item, content, funds[item])
			time.sleep(sleep_time)
		except Exception, e:
			print 'exception:,', e
			time.sleep(sleep_time)

def trade(api, pair, type, rate, amount):
	if amount < 0.001:
		print 'too smal amount:', amount
		return None
	print '[%s] %s %s in %s, amount: %s' % (get_time_str(), type, pair, rate, amount)
	res = api.trade(pair, type, rate, amount)
	if res is None:
		print '[%s] make order fail' % get_time_str()
		return None
	else:
		print '[%s] make order succeed' % get_time_str()
		return res['order_id']

def get_time_str():
	return time.strftime('%H:%M:%S', time.localtime(time.time()))

def get_my_orders(api, items):
	api.get

def get_funds(api, items):
	funds_tmp = api.get_info()['funds']
	while funds_tmp is None:
		print 'get funds fail, retry'
		funds_tmp = api.get_info()['funds']
	funds = {}
	for item in items:
		funds[item] = funds_tmp[item]
	print '[%s] %s' % (get_time_str(), funds)
	return funds

if __name__ == '__main__':
	import key
	run(key.key, key.secret)
