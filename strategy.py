#!/d/python27/python
# -*- coding: utf8 -*-

# sell price and buy price is flexable for shreshold amount
# they have a limit
# min get is 0.001
# good get is 0.003
# remember, fee is 0.998*0.998

btce_strategy = {
	'eur': {
		'reversed' : False,
		'sell_price' : 1.2639,
		'buy_price' : 1.25506,
		'alloc' : 238,

		'min_sell_price' : -1,
		'max_buy_price' : -1,
		'shreshold_amount' : 1500,
	}, 'rur': {
		'reversed' : True,
		'sell_price' : 34.45999,
		'buy_price' : 34.15003,
		'alloc' : 5145,

		'min_sell_price' : -1,
		'max_buy_price' : -1,
		'shreshold_amount' : 1500,
	}
