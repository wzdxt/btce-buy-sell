#!/d/python27/python
# -*- coding: utf8 -*-

from __future__ import division

import time
import copy
import random

from strategy import init_strategy, StrategyManager
from btceapi import BTCEApi
from pricejudger import PriceJudger

real_trade = True

def run(key, secret):
	print
	print 'start running ...'

	api = BTCEApi(key, secret)
	sm = StrategyManager()
	pj = PriceJudger()
	sleep_time = 61 * 3
	order_number = 5
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
				content['skip'] = False
				if content['dynamic']:
					new_content = copy.deepcopy(content)
					pj.make_strategy(new_content)
					if new_content['skip']:
						print '[%s] skip %s, just sell' % (get_time_str(), content['pair'])
					else:
						if orders[item]['buying'] > 0 and orders[item]['selling'] == 0 and funds[item] < 1:
							if not new_content['reversed']:
								new_price = new_content['buy_price']
							else:
								new_price = new_content['sell_price']
							delta = abs(orders[item]['buy_price'] / new_price - 1)
							if delta > 0.001:
								print '[%s] cancel buy order for %s' % (get_time_str(), content['pair'])
								cancel_buy_order(api, content['pair'], content['reversed'])
								orders[item]['buying'] = 0
						if orders[item]['buying'] == 0 and orders[item]['selling'] == 0 and funds[item] < 1:
							content = new_content
							btce_strategy[item] = new_content
							sm.write_strategy(btce_strategy)
				remain = content['alloc'] - orders[item]['buying'] - orders[item]['selling'] - funds[item]
				if content['use']:
					if funds[item] > 1:
						count = funds[item]
						for i in range(0, order_number - 1):
							c = random.random() + 0.5
							count -= funds[item]/order_number * c
							sell_item(api, item, content, funds[item]/order_number * c, (i - order_number//2)/100000)
						sell_item(api, item, content, count, (order_number - 1 - order_number//2)/100000)
					elif orders[item]['selling'] == 0 and funds[item] < 1 and remain > 1 and not new_content['skip']:
						count = remain
						for i in range(0, order_number - 1):
							c = random.random() + 0.5
							count -= remain/order_number * c
							buy_item(api, item, content, remain/order_number * c, (i - order_number//2)/100000)
						buy_item(api, item, content, count, (order_number - 1 - order_number//2)/100000)
				else:
					cancel_buy_order(api, content['pair'], content['reversed'])
			time.sleep(sleep_time)
		except Exception, e:
			raise e
			print 'exception:,', e
			time.sleep(sleep_time)

def print_my_orders(orders):
	print '[%s] orders: %s' % (get_time_str(), orders)

def buy_item(api, coin, strategy_content, amount, price_fix=0):
	price_fix = price_fix + random.randint(-3, 3)/100000
	pair = strategy_content['pair']
	if not strategy_content['reversed']:
		price = strategy_content['buy_price']
		trade(api, pair, 'buy', price + price_fix, amount)
	else:
		price = strategy_content['sell_price']
		trade(api, pair, 'sell', price + price_fix, amount/price)

def sell_item(api, coin, strategy_content, amount, price_fix=0):
	price_fix = price_fix + random.randint(-3, 3)/100000
	pair = strategy_content['pair']
	if not strategy_content['reversed']:
		price = strategy_content['sell_price']
		trade(api, pair, 'sell', price + price_fix, amount)
	else:
		price = strategy_content['buy_price']
		trade(api, pair, 'buy', price + price_fix, amount/price)

def trade(api, pair, type, rate, amount):
	amount = round(amount - 0.000000005, 8)
	rate = round(rate - 0.000005, 5)
	if amount < 0.001:
		print 'too smal amount:', amount
		return None
	print '[%s] %s %s in %s, amount: %s' % (get_time_str(), type, pair, rate, amount)
	if real_trade:
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
	if orders is None:
		return my_orders
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
				set_price(my_orders[item], 'sell_price', order_content['rate'])
			else:
				my_orders[item]['buying'] += order_content['amount']
				set_price(my_orders[item], 'buy_price', order_content['rate'])
		else:
			if order_content['type'] == 'sell':
				my_orders[item]['buying'] += order_content['amount'] * order_content['rate']
				set_price(my_orders[item], 'buy_price', order_content['rate'])
			else:
				my_orders[item]['selling'] += order_content['amount'] * order_content['rate']
				set_price(my_orders[item], 'sell_price', order_content['rate'])
	return my_orders

def set_price(my_order, type, rate):
	if type not in my_order:
		my_order[type] = rate
	else:
		my_order[type] = (my_order[type] + rate)/2
	my_order[type] = round(my_order[type], 9)

def cancel_buy_order(api, pair, reversed):
	orders = api.get_order_list()
	if not reversed:
		type = 'buy'
	else:
		type = 'sell'
	for order_id, order_content in orders.items():
		if real_trade:
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
