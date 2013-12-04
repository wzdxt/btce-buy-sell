#!/d/python27/python
# -*- coding: utf8 -*-

from __future__ import division

import time
import copy

from strategy import init_strategy, StrategyManager
from btceapi import BTCEApi
from pricejudger import PriceJudger

def run(key, secret):
	print
	print 'start running ...'

	api = BTCEApi(key, secret)
	sm = StrategyManager()
	pj = PriceJudger()
	sleep_time = 61 * 3
	btce_strategy = sm.read_strategy()
	sm.write_strategy(btce_strategy)
	
	if True:
		try:
			orders = get_my_orders(api, btce_strategy)
			print_my_orders(orders)
			funds = get_funds(api, btce_strategy.keys())
			for item, content in btce_strategy.items():
				if not content['use']:
					continue
				if content['dynamic']:
					if orders[item]['buying'] > 0 and orders[item]['selling'] == 0:
						print '[%s] cancel buy order for %s' % (get_time_str(), content['pair'])
						cancel_buy_order(api, content['pair'], content['reversed'])
						orders[item]['buying'] = 0
					if orders[item]['buying'] == 0 and orders[item]['selling'] == 0:
						pj.make_strategy(content)
						sm.write_strategy(btce_strategy)
				remain = content['alloc'] - orders[item]['buying'] - orders[item]['selling'] 
				if remain > 1:
					buy_item(api, item, content, remain)
				if funds[item] > 1:
					sell_item(api, item, content, funds[item])
			time.sleep(sleep_time)
		except Exception, e:
			raise e
			print 'exception:,', e
			time.sleep(sleep_time)

def print_my_orders(orders):
	print '[%s] orders: %s' % (get_time_str(), orders)

def buy_item(api, coin, strategy_content, amount):
	pair = strategy_content['pair']
	if not strategy_content['reversed']:
		price = strategy_content['buy_price']
		trade(api, pair, 'buy', price, amount)
	else:
		price = strategy_content['sell_price']
		trade(api, pair, 'sell', price, amount/price)

def sell_item(api, coin, strategy_content, amount):
	pair = strategy_content['pair']
	if not strategy_content['reversed']:
		price = strategy_content['sell_price']
		trade(api, pair, 'sell', price, amount)
	else:
		price = strategy_content['buy_price']
		trade(api, pair, 'buy', price, amount/price)

def trade(api, pair, type, rate, amount):
	amount = round(amount - 0.000000005, 8)
	rate = round(rate - 0.000005, 5)
	if amount < 0.001:
		print 'too smal amount:', amount
		return None
	print '[%s] %s %s in %s, amount: %s' % (get_time_str(), type, pair, rate, amount)
	if True:
		res = api.trade(pair, type, rate, amount)
		if res is None:
			print '[%s] make order fail' % get_time_str()
			return None
		else:
			print '[%s] make order succeed' % get_time_str()
			return res['order_id']

def get_time_str():
	return time.strftime('%H:%M:%S', time.localtime(time.time()))

def get_my_orders(api, strategy):
	my_orders = {}
	for item in strategy.keys():
		my_orders[item] = {'selling':0, 'buying':0}
	orders = api.get_order_list()
	for order_content in orders.values():
		if order_content['pair'][:3] in strategy.keys():
			item = order_content['pair'][:3]
		elif order_content['pair'][-3:] in strategy.keys():
			item = order_content['pair'][-3:]
		else:
			continue
		if not strategy[item]['reversed']:
			if order_content['type'] == 'sell':
				my_orders[item]['selling'] += order_content['amount']
			else:
				my_orders[item]['buying'] += order_content['amount']
		else:
			if order_content['type'] == 'sell':
				my_orders[item]['buying'] += order_content['amount'] * order_content['rate']
			else:
				my_orders[item]['selling'] += order_content['amount'] * order_content['rate']
	return my_orders

def cancel_buy_order(api, pair, reversed):
	orders = api.get_order_list()
	if not reversed:
		type = 'buy'
	else:
		type = 'sell'
	for order_id, order_content in orders.items():
		if order_content['pair'] == pair and order_content['type'] == type:
			print '[%s] cancel order %s' % (get_time_str(), order_id)
			api.cancel_order(order_id)
			print '[%s] canceled' % (get_time_str())

def get_funds(api, items):
	funds_tmp = api.get_info()['funds']
	while funds_tmp is None:
		print '[%s] get funds fail, retry' % get_time_str()
		funds_tmp = api.get_info()['funds']
	funds = {}
	for item in items + ['usd']:
		funds[item] = funds_tmp[item]
	print '[%s] funds: %s' % (get_time_str(), funds)
	return funds

if __name__ == '__main__':
	import key
	run(key.key, key.secret)
