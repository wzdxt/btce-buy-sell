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

	look_sleep_time = 10
	
	while True:
		try:
			cash = get_funds_and_orders(btce_strategy)
			print_cash(cash)
			has_cash = False
			for item in strategy:
				item_cash = cash[item]
				if item_cash['cash'] > 0.01:
					sell_item(item_cash)
					has_cash = True
			if has_cash:
				cash = get_funds_and_orders(btce_strategy)
			frozen_usd = 0
			for item, content in strategy:
				frozen_usd += get_usd(cash[item])
			total_usd = cash['usd'] + frozen_usd
			total_weight = 0
			for content in btce_strategy.valus():
				total_weight += content['weight']
			alloc = {}

			
			
		except Exception, e:
			print 'exception:,', e
			time.sleep(look_sleep_time)

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

def get_funds(api):
	funds_tmp = api.get_info()['funds']
	while funds_tmp is None:
		funds_tmp = api.get_info()['funds']
	funds = make_simple_funds(funds_tmp)
	print '[%s] %s' % (get_time_str(), funds)
	return funds

if __name__ == '__main__':
	import key
	run(key.key, key.secret)
