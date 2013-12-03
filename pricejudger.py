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
		}
		self.headers = {'origin': 'https://btc-e.com', 'content-length': '25', 'accept-language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4', 'accept-encoding': 'gzip,deflate,sdch', 'accept': 'application/json, text/javascript, */*; q=0.01', 'referer': 'https://btc-e.com/exchange/eur_usd', 'url': '/ajax/order', 'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/31.0.1650.57 Safari/537.36', 'version': 'HTTP/1.1', 'x-requested-with': 'XMLHttpRequest', 'cookie':'__cfduid=da657e9971407709da903277b296547aa1384829908462; locale=cn; chatRefresh=0; a=ea303c77eb85ca780dd46bfe0083dfd5; SESS_ID=r8c8dqi1fm65hi9chdisrimc6f33j9iu; auth=1; bId=62ZY2ZJQ77UCHYSHC0UHE14O93382OVA; __utma=45868663.1156318973.1384829913.1386055500.1386060425.32; __utmb=45868663.21.10.1386060425; __utmc=45868663; __utmz=45868663.1384829913.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)', 'scheme': 'https', 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'method': 'POST'}

	
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

if __name__ == '__main__':
	pj = PriceJudger()
	print pj.get_m30_k_line('eur_usd')

