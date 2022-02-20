import datetime
import dateutil.parser
import numpy as np
import pandas as pd

from operations import beancount
from config import COLORS
from config import UNICODE_SHAPES
from exchanges._ccxt import ccxt_operations
from helpers import getAPI
from live_plot import live_plotter
from millify import prettify
from rich.console import Console
from rich.table import Table
from time import time
from time import sleep
from uniplot import histogram
from uniplot import plot as unipl
from helpers import Notification
from helpers import parse_date_time 
from helpers import raise_error


def fetch(exchange, spot, option, plot, seconds, pretty, bean, notify, match):
		"""fetch: Api call to return self.init_ccxt().fetch_ticker(spot)
		"""
		apiKey = getAPI(exchange)['apiKey']
		secret = getAPI(exchange)['secret']
		ccxt_api = ccxt_operations(exchange, apiKey, secret)
		result = ccxt_api.fetch(spot)
		console = Console()
		parse_date = dateutil.parser.isoparse(str(result['datetime']))
		date = datetime.datetime.strftime(parse_date, '%Y-%m-%d')
		time = datetime.datetime.strftime(parse_date, '%H:%M:%S')
		pd.set_option("max_rows", None)
		if option == 'all':
				table = Table(title=spot)
				table.add_column("symbol", justify="center",
												 style=COLORS['blue'], no_wrap=True)
				table.add_column("timestamp", justify="center",
												 style=COLORS['yellow'], no_wrap=True)
				table.add_column("datetime", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("high", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("low", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("bid", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("bidVolume", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("ask", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("askVolume", justify="center",
												 style=COLORS['yellow'], no_wrap=True)
				table.add_column("open", justify="center",
												 style=COLORS['blue'], no_wrap=True)
				table.add_column("close", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("last", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("previousClose", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("change", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("percentage", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("quoteVolume", justify="center",
												 style=COLORS['white'], no_wrap=True)

				table.add_row(str(result['symbol']),
											str(result['timestamp']),
											str(result['datetime']),
											str(result['high']),
											str(result['low']),
											str(result['bid']),
											str(result['bidVolume']),
											str(result['ask']),
											str(result['askVolume']),
											str(result['open']),
											str(result['close']),
											str(result['last']),
											str(result['previousClose']),
											str(result['change']),
											str(result['percentage']),
											str(prettify(result['quoteVolume']))
											)

				# dataframe = pd.DataFrame.from_dict(result, orient='index')
				# console.print(dataframe)
				console.print(table)
				table = Table(title=spot+' info')
				table.add_column("enabled", justify="center",
												 style=COLORS['blue'], no_wrap=True)
				table.add_column("postOnly", justify="center",
												 style=COLORS['yellow'], no_wrap=True)
				table.add_column("priceIncrement", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("sizeIncrement", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("minProvideSize", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("price", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("largeOrderThreshold", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("change1h", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("change24h", justify="center",
												 style=COLORS['yellow'], no_wrap=True)
				table.add_column("changeBod", justify="center",
												 style=COLORS['blue'], no_wrap=True)
				info_result = result['info']
				table.add_row(str(info_result['enabled']),
											str(info_result['postOnly']),
											str(info_result['priceIncrement']),
											str(info_result['sizeIncrement']),
											str(info_result['minProvideSize']),
											str(info_result['price']),
											str(info_result['largeOrderThreshold']),
											str(info_result['change1h']),
											str(info_result['change24h']),
											str(info_result['changeBod'])
											)
				console.print(table)

		else:
				try:
						if notify:
							# Gnome Notification
							match = match.split(":")
							match_price = match[0]
							match_direction = match[1]
							match_seconds = int(match[2])
							if match_direction == 'down':
								condition = float(result['info'][option]) > float(match_price)
							if match_direction == 'up':
								condition = float(result['info'][option]) < float(match_price)
							result_ = float(result['info'][option])
							while condition:
								result = ccxt_api.fetch(spot)
								result_ = float(result['info'][option])
								date_time = parse_date_time(str(result['datetime']))
								result_view = f'''{date_time[0]} {date_time[1]} | {result_}'''
								console.print(result_view)
								sleep(match_seconds)

							summary = f'{option} of {spot} matched condition'
							body = f'{str(result_)} is moving {match_direction}. Price match {match_price}'
							notification = Notification("Cryptodash", summary, body)
							notification.show()
							notification.uninit()
						if bean:
							if option == 'price':
								beancount.update_price(date, spot, str(result['info'][option]))
							else:
								raise_error(option, 'fetch', 'option', 'price. Only accepts price as option')
						if pretty:
						# click.echo(click.style(f"{option}: {result['info'][option]}", bold=True))
							table = Table(title=spot+' '+option)
							date_time = parse_date_time(str(result['datetime']))
							table.add_column('date', justify="center",
															 style=COLORS['white'], no_wrap=True)
							table.add_column('time', justify="center",
															 style=COLORS['white'], no_wrap=True)
							table.add_column(option, justify="center",
															 style=COLORS['blue'], no_wrap=True)
							try:
								result = str(result['info'][option])
							except:
								result = str(result[option])
							table.add_row(str(date_time[0]), str(date_time[1]), result)
							console.print(table)
						else:
							try:
								result_ = str(result["info"][option])
								result_view = f'''{date} {time} | {result_}'''
								console.print(result_view)
							except:
								result_ = str(result[option])
								result_view = f'''{date} {time} | {result_}'''
								console.print(result_view)
						# console.print(result['info'][option])
						if plot:
								'''
								Add candlestick Move to Tasks
								'''
								
								size = int(float(result['info'][option])) + 10
								last = int(float(result['info']['last']))
								upper = size + 15
								# print(upper)
								x_vec = np.linspace(0, float(seconds), 15)
								# print(x_vec)
								y_vec = np.linspace(float(result['info'][option]), float(
										result['info'][option])+0.00001, 15)
								# print(y_vec)
								line1 = []
								while True:

										result = ccxt_api.fetch(spot)
										rand_val = float(result['info'][option])
										console.print(result['datetime'], rand_val)
										y_vec[-1] = rand_val
										# print(y_vec[-1])
										line1 = live_plotter(x_vec, y_vec, line1, option, float(
												seconds), option, 'seconds')
										y_vec = np.append(y_vec[1:], 0.0)
										# print(y_vec)
				except Exception as e:
						raise e

						#print(i, result[i])


def order_book(exchange, spot, limit, plot, interactive, last):
		apiKey = getAPI(exchange)['apiKey']
		secret = getAPI(exchange)['secret']
		ccxt_api = ccxt_operations(exchange, apiKey, secret)
		# progress_bar(ccxt_api, '[green]Order Book')
		result = ccxt_api.order_book(spot, limit)
		price = ccxt_api.fetch(spot)
		current_price = price['info']
		# print(i for i in range(result['bids']))
		table = Table(title="Order Book")
		table.add_column("Bid", justify="left",
										 style=COLORS['green'], no_wrap=True)
		table.add_column("Size", justify="left",
										 style=COLORS['green'], no_wrap=True)
		table.add_column("Amount", justify="left",
										 style=COLORS['green'], no_wrap=True)
		table.add_column("Rank", justify="center",
										 style=COLORS['white'], no_wrap=True)
		table.add_column("Ask", justify="right",
										 style=COLORS['yellow'], no_wrap=True)
		table.add_column("Size", justify="right",
										 style=COLORS['yellow'], no_wrap=True)
		table.add_column("Amount", justify="left",
										 style=COLORS['yellow'], no_wrap=True)

		bid_price_array = []
		bid_amount_array = []
		ask_price_array = []
		ask_amount_array = []

		console = Console()

		for i in range(int(limit)):
				bids = result['bids'][i]
				bid_price = bids[0]
				bid_price_append = bid_price_array.append(bid_price)
				bid_amount = bids[1]
				bid_amount_append = bid_amount_array.append(bid_amount)

				asks = result['asks'][i]
				ask_price = asks[0]
				asj_price_append = ask_price_array.append(ask_price)
				ask_amount = asks[1]
				ask_amount_append = ask_amount_array.append(ask_amount)
				# print(ask_price, ask_amount, ask_price*ask_amount)

				table.add_row(str(bid_price),
											str(bid_amount),
											str(prettify(bid_price*bid_amount)),
											str(i+1),
											str(ask_price),
											str(ask_amount),
											str(prettify(ask_price*ask_amount)))

		console.print(table)
		if last:
				table = Table(title="Current Trade")
				table.add_column("Price", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("Last", justify="center",
												 style=COLORS['blue'], no_wrap=True)
				table.add_column("Bid", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("Ask", justify="center",
												 style=COLORS['yellow'], no_wrap=True)

				table.add_row(str(current_price['price']),
											str(current_price['last']),
											str(current_price['bid']),
											str(current_price['ask']))

				console.print(table)
		if plot:
				unipl(color=True,
							ys=[bid_price_array, ask_price_array],
							interactive=interactive,
							legend_labels=["Bid", "Ask"],
							title="Bids vs Asks",
							height=30,
							width=100,
							y_gridlines=[float(current_price['bid']), float(current_price['last']), float(current_price['ask'])])


def fetch_balance(exchange):
		apiKey = getAPI(exchange)['apiKey']
		secret = getAPI(exchange)['secret']
		ccxt_api = ccxt_operations(exchange, apiKey, secret)
		# print(ccxt_api.balance()['info']['free'])
		try:
				if exchange == 'ftxus':
						result = ccxt_api.balance()['info']['result']
						dataframe = pd.DataFrame(result)
						dataframe['usdValue'] = dataframe['usdValue'].astype(float)
						total = dataframe.loc[:, 'usdValue'].sum()
				elif exchange == 'bitstamp':
						result = ccxt_api.balance()['info']
						dataframe = pd.DataFrame([result], columns=['Param', 'Amount'])
						total = 0
		except:
				pass

		console = Console()
		pd.set_option("max_rows", None)
		console.print(dataframe)

		print(f"TOTAL: ${round(total, 3)}")


def fetch_trade(exchange, spot, option, since, limit, plot, interactive):

		apiKey = getAPI(exchange)['apiKey']
		secret = getAPI(exchange)['secret']
		ccxt_api = ccxt_operations(exchange, apiKey, secret)
		# print(ccxt_api.balance()['info']['free'])
		console = Console()
		if option == "market":
				'''
				File "/usr/lib/python3.9/site-packages/ccxt/ftx.py", line 951, in fetch_trades
					request['start_time'] = int(since / 1000)
					is this in seconds??
				'''
				buys = []
				sells = []

				result = ccxt_api.fetchTrades(spot, int(since), int(limit))
				# print(result)

				table = Table(title="Trades")
				table.add_column("Datetime", justify="center",
												 style=COLORS['blue'], no_wrap=True)
				table.add_column("Symbol", justify="center",
												 style=COLORS['orange'], no_wrap=True)
				table.add_column("id", justify="center",
												 style=COLORS['yellow'], no_wrap=True)
				table.add_column("Side", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("Price", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("Amount", justify="center",
												 style=COLORS['orange'], no_wrap=True)
				table.add_column("Cost", justify="center",
												 style=COLORS['orange'], no_wrap=True)

				for i in result:
						if str(i['side']) == 'buy':
								buys.append(i['price'])
						elif str(i['side']) == 'sell':
								sells.append(i['price'])
						table.add_row(str(i['datetime']),
													str(i['symbol']),
													str(i['id']),
													str(i['side']),
													str(i['price']),
													str(i['amount']),
													str(i['cost']))
				console.print(table)

				if plot:
						# print(buys)
						# print(sells)
						unipl(color=True,
									ys=[buys, sells],
									legend_labels=["buys", "sells"],
									interactive=interactive,
									lines=True,
									title="Buys vs Sells",
									height=30,
									width=100)

		elif option == "open":
				result = ccxt_api.fetchOpenOrders()
				table = Table(title="My Open Orders")
				table.add_column("id", justify="center",
												 style=COLORS['blue'], no_wrap=True)
				table.add_column("market", justify="center",
												 style=COLORS['yellow'], no_wrap=True)
				table.add_column("type", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("side", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("price", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("size", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("status", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("filledSize", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("remainingSize", justify="center",
												 style=COLORS['yellow'], no_wrap=True)
				table.add_column("createdAt", justify="center",
												 style=COLORS['blue'], no_wrap=True)
				table.add_column("marketPrice", justify="center",
												 style=COLORS['white'], no_wrap=True)
				get_current_price = ccxt_api.fetch(spot)
				current_price = get_current_price['info']['price']

				for ii in result:
						i = ii['info']
						if float(current_price) > float(i['price']):
								current_price = f'[blink {COLORS["red"]}]{current_price}[blink /{COLORS["red"]}]'
						elif float(current_price) <= float(i['price']):
								current_price = f'[{COLORS["green"]}]{current_price}[/{COLORS["green"]}]'
						table.add_row(str(i['id']),
													str(i['market']),
													str(i['type']),
													str(i['side']),
													str(i['price']),
													str(i['size']),
													str(i['status']),
													str(i['filledSize']),
													str(i['remainingSize']),
													str(i['createdAt']),
													current_price)

				console.print(table)

		elif option == "orders":
				result = ccxt_api.fetchOrders(ticker=spot)
				table = Table(title="All Orders")
				table.add_column("id", justify="center",
												 style=COLORS['blue'], no_wrap=True)
				table.add_column("timestamp", justify="center",
												 style=COLORS['yellow'], no_wrap=True)
				table.add_column("datetime", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("symbol", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("type", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("postOnly", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("side", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("price", justify="center",
												 style=COLORS['green'], no_wrap=True)
				table.add_column("stopPrice", justify="center",
												 style=COLORS['yellow'], no_wrap=True)
				table.add_column("amount", justify="center",
												 style=COLORS['blue'], no_wrap=True)
				table.add_column("cost", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("filled", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("remaining", justify="center",
												 style=COLORS['white'], no_wrap=True)
				table.add_column("status", justify="center",
												 style=COLORS['white'], no_wrap=True)

				for i in result:
						table.add_row(str(i['id']),
													str(i['timestamp']),
													str(i['datetime']),
													str(i['symbol']),
													str(i['type']),
													str(i['postOnly']),
													str(i['side']),
													str(i['price']),
													str(i['stopPrice']),
													str(i['amount']),
													str(i['cost']),
													str(i['filled']),
													str(i['remaining']),
													str(i['status']))
				console.print(table)
