#!/d/python27/python
# -*- coding: utf8 -*-

import httplib
import gzip
import StringIO
import json

from key import cookie

class PriceJudger():
	def __init__(self):
		self.pair_id = {
			'eur_usd' : 20,
			'usd_rur' : 18,
		}
		self.headers = { 'accept-encoding': 'gzip,deflate,sdch', 'accept': 'application/json, text/javascript, */*; q=0.01', 'cookie': cookie, 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',}
		self.__refresh_web()
	
	def __refresh_web(self):
		conn = httplib.HTTPSConnection('btc-e.com')
		conn.request('POST', '/', headers=self.headers)
		resp = conn.getresponse()

	def get_m30_k_line(self, pair):
		conn = httplib.HTTPSConnection('btc-e.com')
		conn.request('POST', '/ajax/order', 'act=orders_update&pair='+str(self.pair_id[pair]), self.headers)
		resp = conn.getresponse()
		res = resp.read()
		res = gzip.GzipFile(fileobj=StringIO.StringIO(res)).read()
		tmp = json.loads(res)
		ret = tmp['chart_data']
		for item in ret:
			del item[0]
			del item[-1]
		return ret
	
	def get_flex_price(self, k_line, pair, rate):
		return self.get_price(k_line, pair, 0.4, rate)

	def get_extrem_price(self, k_line, pair, rate):
		return self.get_price(k_line, pair, 0.6, rate)
	
	def get_high_and_low_price(self, k_line):
		high_price = []
		low_price = []
		for i in range(0, len(k_line)):
			high_price += [max(k_line[i])] * (i + 1)**2
			low_price += [min(k_line[i])] * (i + 1)**2
		high_price.sort()
		low_price.sort()
		return (high_price, low_price)

	def get_price_by_index(self, k_line, index, sort=True):
		price = []
		for item in k_line:
			price.append(item[index])
		if sort:
			price.sort()
		return price

	def get_price(self, k_line, pair, percent, rate):
		(high_price, low_price) = self.get_high_and_low_price(k_line)
		line_len = len(high_price)
		res = (high_price[int(-line_len*percent)], low_price[int(line_len*percent)])
		if __debug__:
			benefit = (res[0] * rate**2 - res[1])/res[0]
			print 'high price: %s, low price: %s, benefit: %s' % (res[0], res[1], benefit)
		return res
	
	def make_strategy(self, strategy_content):
		print 'new strategy for', strategy_content['pair']
		k_line = self.get_m30_k_line(strategy_content['pair'])
		del k_line[-1]
		flex_price = self.get_flex_price(k_line, strategy_content['pair'], strategy_content['rate'])
		strategy_content['sell_price'] = flex_price[0]
		strategy_content['buy_price'] = flex_price[1]
#		extrem_price = self.get_extrem_price(k_line, strategy_content['pair'], strategy_content['rate'])
#		strategy_content['min_sell_price'] = extrem_price[0]
#		strategy_content['max_buy_price'] = extrem_price[1]
#		if (extrem_price[0] * strategy_content['rate']**2)/extrem_price[1] - 1 < 0.001:
#			strategy_content['use'] = False
#			return
		self.__make_price_reasonable(k_line, strategy_content)
		print strategy_content
	
	def __make_price_reasonable(self, k_line, strategy_content):
		part_line = k_line[-5:]
		low_price = self.get_price_by_index(part_line, 0)
		high_price = self.get_price_by_index(part_line, 3)
		high_price = high_price[1:-1]
		low_price = low_price[1:-1]
		strategy_content['sell_price'] = (strategy_content['sell_price'] + sum(high_price)/len(high_price))/2
		strategy_content['buy_price'] = (strategy_content['buy_price'] + sum(low_price)/len(low_price))/2
		benefit = strategy_content['sell_price'] *strategy_content['rate']**2 / strategy_content['buy_price'] - 1
		if benefit < 0.001:
			print 'bad situation of %s, for %s, benefit=%s' % \
				(strategy_content['pair'], (strategy_content['sell_price'], strategy_content['buy_price']), benefit)
			if not strategy_content['reversed']:
				strategy_content['sell_price'] = strategy_content['sell_price'] * 0.999
				strategy_content['buy_price'] = strategy_content['sell_price']*strategy_content['rate']**2 * 0.999
			else:
				strategy_content['buy_price'] = strategy_content['buy_price'] / 0.999
				strategy_content['sell_price'] = strategy_content['buy_price']/strategy_content['rate']**2 / 0.999
			print 'change price to', (strategy_content['sell_price'], strategy_content['buy_price'])
		if not strategy_content['reversed']:
			if strategy_content['buy_price'] > strategy_content['max_buy_price']:
				strategy_content['skip'] = True
		else:
			if strategy_content['sell_price'] < strategy_content['min_sell_price']:
				strategy_content['skip'] = True

if __name__ == '__main__':
	pj = PriceJudger()

	k_line = pj.get_m30_k_line('eur_usd')
	del k_line[-1]
	print 'flex price for eur_usd'
	pj.get_flex_price(k_line, 'eur_usd', 0.998)
	print 'extrem price for eur_usd'
	pj.get_extrem_price(k_line, 'eur_usd', 0.995)

	k_line = pj.get_m30_k_line('usd_rur')
	del k_line[-1]
	print 'flex price for usd_rur'
	pj.get_flex_price(k_line, 'usd_rur', 0.998)
	print 'extrem price for usd_rur'
	pj.get_extrem_price(k_line, 'usd_rur', 0.995)

