#!/d/python27/python
# -*- coding: utf8 -*-

import json

# sell price and buy price is flexable for shreshold amount
# they have a limit
# min get is 0.001
# good get is 0.003
# remember, fee is 0.998*0.998

init_strategy = {
	'eur': {
		'pair' : 'eur_usd',
		'reversed' : False,
		'sell_price' : 1.2659,
		'buy_price' : 1.25606,
		'alloc' : 238,

		'use' : True,
		'dynamic' : True,

		'min_sell_price' : -1,
		'max_buy_price' : -1,
		'shreshold_amount' : 1500,
	}, 'rur': {
		'pair' : 'usd_rur',
		'reversed' : True,
		'sell_price' : 34.38998,
		'buy_price' : 33.90003,
		'alloc' : 5145,

		'use' : True,
		'dynamic' : False,

		'min_sell_price' : -1,
		'max_buy_price' : -1,
		'shreshold_amount' : 1500,
	}}

class StrategyManager():
	def __init__(self):
		self.file_name = 'strategy.dat'

	def read_strategy(self):
		f = open(self.file_name, 'r')
		tmp = f.read()
		f.close()
		if tmp == '':
			return init_strategy
		else:
			return json.loads(tmp)
	
	def write_strategy(self, strategy):
		f = open(self.file_name, 'w')
		f.write(json.dumps(strategy))
		f.close()
