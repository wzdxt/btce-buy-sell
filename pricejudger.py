#!/d/python27/python
# -*- coding: utf8 -*-

import httplib
import gzip
import StringIO
import json


class PriceJudger():
	def __init__(self):
		self.pair_id = {
			'eur_usd' : 20,
			'usd_rur' : 18,
		}
		self.headers = { 'accept-encoding': 'gzip,deflate,sdch', 'accept': 'application/json, text/javascript, */*; q=0.01', 'cookie':' a=ea303c77eb85ca780dd46bfe0083dfd5; SESS_ID=r8c8dqi1fm65hi9chdisrimc6f33j9iu; auth=1; bId=62ZY2ZJQ77UCHYSHC0UHE14O93382OVA; __utma=45868663.1156318973.1384829913.1386055500.1386060425.32;', 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',}

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
	
	def get_flex_price(self, k_line, pair):
		return self.get_price(k_line, pair, 0.4)

	def get_extrem_price(self, k_line, pair):
		return self.get_price(k_line, pair, 0.6)
	
	def get_high_and_low_price(self, k_line, sort=True):
		high_price = []
		low_price = []
		for item in k_line:
			high_price.append(max(item))
			low_price.append(min(item))
		if sort:
			high_price.sort()
			low_price.sort()
		return (high_price, low_price)

	def get_price(self, k_line, pair, percent):
		(high_price, low_price) = self.get_high_and_low_price(k_line)
		line_len = len(high_price)
		res = (high_price[int(-line_len*percent)], low_price[int(line_len*percent)])
		if __debug__:
			benefit = (res[0] * 0.998 * 0.998 - res[1])/res[0]
			print 'high price: %s, low price: %s, benefit: %s' % (res[0], res[1], benefit)
		return res

	def make_strategy(self, strategy_content):
		k_line = self.get_m30_k_line('eur_usd')
		del k_line[-1]
		flex_price = self.get_flex_price(k_line, strategy_content['pair'])
		extrem_price = self.get_extrem_price(k_line, strategy_content['pair'])
		strategy_content['sell_price'] = flex_price[0]
		strategy_content['buy_price'] = flex_price[1]
		strategy_content['min_sell_price'] = extrem_price[0]
		strategy_content['max_buy_price'] = extrem_price[1]
		if (extrem_price[0] * 0.998 * 0.998)/extrem_price[1] - 1 < 0.001:
			strategy_content['use'] = False
		self.__make_price_reasonable(k_line, strategy_content)
	
	def __make_price_reasonable(self, k_line, strategy_content):
		part_line = k_line[-5:]
		(high_price, low_price) = self.get_high_and_low_price(k_line)
		high_price = high_price[1:-1]
		low_price = low_price[1:-1]
		strategy_content['sell_price'] = (strategy_content['sell_price'] + sum(high_price)/len(high_price))/2
		strategy_content['buy_price'] = (strategy_content['buy_price'] + sum(low_price)/len(low_price))/2
		if strategy_content['sell_price'] < strategy_content['min_sell_price'] \
			or strategy_content['buy_price'] > strategy_content['max_buy_price']:
				strategy_content['use'] = False

if __name__ == '__main__':
	pj = PriceJudger()

	k_line = pj.get_m30_k_line('eur_usd')
	del k_line[-1]
	print 'flex price for eur_usd'
	pj.get_flex_price(k_line, 'eur_usd')
	print 'extrem price for eur_usd'
	pj.get_extrem_price(k_line, 'eur_usd')

	k_line = pj.get_m30_k_line('usd_rur')
	del k_line[-1]
	print 'flex price for usd_rur'
	pj.get_flex_price(k_line, 'usd_rur')
	print 'extrem price for usd_rur'
	pj.get_extrem_price(k_line, 'usd_rur')

