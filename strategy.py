#!/d/python27/python
# -*- coding: utf8 -*-

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

		'min_sell_price' : -1,
		'max_buy_price' : -1,
		'shreshold_amount' : 1500,
	}, 'rur': {
		'pair' : 'usd_rur',
		'reversed' : True,
		'sell_price' : 34.13998,
		'buy_price' : 33.80003,
		'alloc' : 5145,

		'min_sell_price' : -1,
		'max_buy_price' : -1,
		'shreshold_amount' : 1500,
	}}
