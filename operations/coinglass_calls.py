import json
import requests

from config import COLORS
from helpers import getAPI
from helpers import getURL
from millify import prettify
from rich import print
from rich.console import Console
from rich.table import Table

def coinglass(option, coin, interval, timetype):
		console = Console()
		secret = getAPI('coinglass')['secret']
		base = getURL('coinglass')
		if option == "oi":
				record_path = ['data']
				url = base['url']+base['futures']+base['openInterest'] + \
						base['symbol']+coin+base['interval']+interval
		elif option == 'lc':
				url = base['url']+base['futures'] + \
						base['liquidation_chart']+base['symbol']+coin+'exName=FTX'
		elif option == "l":
				# record_path = ['data'][0]['list']
				url = base['url']+base['futures']+base['liquidation'] + \
						'/detail/chart'+base['symbol']+coin+'&timeType='+timetype
		# print(url, option)
		params = {}
		headers = {
				'coinglassSecret': secret
		}
		response = requests.request("GET", url, headers=headers, data=params)
		result = response.text
		# print(url)
		

		j = json.loads(result)
		# console.print(j)
		if option == 'oi':
				table = Table(title=option)
				table.add_column("Exchange", justify="center",
												 style=COLORS['blue'], no_wrap=True)
				table.add_column("Symbol", justify="center",
												 style=COLORS['orange'], no_wrap=True)
				table.add_column("openInterest", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("openInterestAmount", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("volUsd", justify="center",
												 style=COLORS['yellow'], no_wrap=True)
				table.add_column("h24Change", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("rate", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("h1OIChangePercent", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("h4OIChangePercent", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("price", justify="center",
												 style=COLORS['green'], no_wrap=True)
				price_ = 0
				for ii in range(1, len(j['data']), 1):
						# print(j['data'][ii])
						i = j['data'][ii]
						price_ += i['price']
						table.add_row(str(i['exchangeName']),
													str(i['symbol']),
													str(prettify(round(i['openInterest']))),
													str(prettify(round(i['openInterestAmount']))),
													str(prettify(round(i['volUsd']))),
													str(i['h24Change']),
													str(i['rate']),
													str(i['h1OIChangePercent']),
													str(i['h4OIChangePercent']),
													str(i['price']))
				console.print(table)

				table = Table(title="End Report")
				table.add_column("Exchange", justify="center",
												 style=COLORS['blue'], no_wrap=True)
				table.add_column("Symbol", justify="center",
												 style=COLORS['orange'], no_wrap=True)
				table.add_column("openInterest", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("openInterestAmount", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("volUsd", justify="center",
												 style=COLORS['yellow'], no_wrap=True)
				table.add_column("h24Change", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("rate", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("volChangePercent", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("h1OIChangePercent", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("h4OIChangePercent", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("avgFundingRate", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("oichangePercent", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("price", justify="center",
												 style=COLORS['green'], no_wrap=True)
				io = j['data'][0]
				price = (price_ / (len(j['data']) - 1))  # -1: j['data'][0] is the sum
				table.add_row(str(io['exchangeName']),
											str(io['symbol']),
											str(prettify(round(io['openInterest']))),
											str(prettify(round(io['openInterestAmount']))),
											str(prettify(round(io['volUsd']))),
											str(io['h24Change']),
											str(io['rate']),
											str(io['volChangePercent']),
											str(io['h1OIChangePercent']),
											str(io['h4OIChangePercent']),
											str(io['avgFundingRate']),
											str(io['oichangePercent']),
											str(round(price, 4)))
				console.print(table)
		elif option == 'lc':
				print(j)