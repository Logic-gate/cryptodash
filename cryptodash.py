#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import ccxt
import click
import hashlib
import json
import numpy as np
import os
import re

from operations import beancount
from operations import ccxt_calls
from operations import coinglass_calls
from operations import db_calls
from config import ACCOUNTS
from config import DB
from exchanges._ccxt import ccxt_operations
from datetime import date as datetime_date
from datetime import datetime
from helpers import getAPI
from helpers import getFee
from helpers import raise_error
from millify import prettify
from rich import inspect
from rich import pretty
from rich import print
from rich.console import Console
from rich.table import Table
from tinydb import Query




# @click.group()
# def bean_import_exchange():
#       pass


# # @bean_import_exchange.command()
# # @click.option("-x", "--exchange", prompt="Exchange", help="FTXUS, BITSTAMP, KRAKEN")
# # def bean_import(exchange, spot, price, qty, buy, sell, date, comment, buy_price, buy_date):
# #         beancount.bean_count_transaction(
# #                 exchange, spot, price, qty, buy, sell, date, comment, buy_price, buy_date)

@click.group()
def bean_transaction():
        pass


@bean_transaction.command()
@click.option("-x", "--exchange", prompt="Exchange", help="FTXUS, BITSTAMP, KRAKEN")
@click.option("-s", "--spot", help="SOL/USD, BTC/USD, ETH/BTC..etc")
@click.option("-q", "--qty", prompt="QTY", help="Float")
@click.option("-p", "--price", prompt="Price", help="Float")
@click.option("-d", "--date", prompt="date", help="Float")
@click.option("-c", "--comment", prompt="comment", help="Float")
@click.option("-P", "--buy_price", help="buy_price")
@click.option("-Pd", "--buy_date", help="Buy Date")
@click.option("--buy", is_flag=True, help="Float")
@click.option("--sell", is_flag=True, help="Float, cp for current price")
def bean(exchange, spot, price, qty, buy, sell, date, comment, buy_price, buy_date):
        if price == 'cp':
                apiKey = getAPI(exchange)['apiKey']
                secret = getAPI(exchange)['secret']
                ccxt_api = ccxt_operations(exchange, apiKey, secret)
                result = ccxt_api.fetch(spot)
                current_price = result['info']['price']
                price = current_price
        beancount.bean_count_transaction(
                exchange, spot, price, qty, buy, sell, date, comment, buy_price, buy_date)


@click.group()
def fetch_trades():
        pass


@fetch_trades.command()
@click.option("-x", "--exchange", prompt="Exchange", help="FTXUS, BITSTAMP, KRAKEN")
@click.option("-s", "--spot", help="SOL/USD, BTC/USD, ETH/BTC..etc")
@click.option("-o", "--option", prompt="Option", help="market, open, orders")
@click.option("-S", "--since", help="date", default=1)
@click.option("-l", "--limit", help="int", default=25)
@click.option("-p", "--plot", is_flag=True)
@click.option("--interactive", is_flag=True)
@click.option("--bean", is_flag=True)
@click.option("--search", default=None, help="key::SearchTerm")
def fetch_trade(exchange, spot, option, since, limit, plot, interactive, bean, search):
        if search is not None:
            if "::" in search:
                pass
            else:
                raise raise_error("--search", "--search must follow key::SearchTerm format with '::' between key and value.")
                
        ccxt_calls.fetch_trade(exchange, spot, option,
                                                     since, limit, plot, interactive, bean, search)


@click.group()
def coinglass_():
        pass


@coinglass_.command()
@click.option("-o", "--option", prompt="Option", help="openInterest : oi, liquidation_chart: lc, liquidation: l")
@click.option("-c", "--coin", prompt="Coin", help="SOL, BTC, ETH..etc")
@click.option("-i", "--interval", prompt="Interval", help="0=ALL, 2=1H ,1=4H 4=12H")
@click.option("-t", "--timetype",  help="1m=9, 5m=3, 15m=10, 30=11, 4h=1, 12h=4, 90d =18")
def coinglass(option, coin, interval, timetype):
        coinglass_calls.coinglass(option, coin, interval, timetype)


@click.group()
def get_balance():
        pass


@get_balance.command()
@click.option("-x", "--exchange", prompt="Exchange", help="FTXUS, BITSTAMP, KRAKEN")
def fetch_balance(exchange):
        ccxt_calls.fetch_balance(exchange)


@click.group()
def ccxt_order_book():
        pass


@ccxt_order_book.command()
@click.option("-x", "--exchange", prompt="Exchange", help="FTXUS, BITSTAMP, KRAKEN")
@click.option("-s", "--spot", prompt="Spot", help="SOL/USD, BTC/USD, ETH/BTC..etc")
@click.option("-l", "--limit", prompt="limit", help="1, 5, 10, 50..etc MAX=100")
@click.option("-p", "--plot", is_flag=True)
@click.option("--interactive", is_flag=True)
@click.option("-la", "--last", is_flag=True)
def order_book(exchange, spot, limit, plot, interactive, last):
        ccxt_calls.order_book(exchange, spot, limit, plot, interactive, last)


@click.group()
def ccxt_data():
        pass


@ccxt_data.command()
@click.option("-x", "--exchange", prompt="Exchange", help="FTXUS, BITSTAMP, KRAKEN")
@click.option("-s", "--spot", prompt="Spot", help="SOL/USD, BTC/USD, ETH/BTC..etc")
@click.option("-o", "--option", prompt="option", help="See All")
@click.option("--seconds", help="plot seconds")
@click.option("--match", help="notify if match. price:up|down:seconds eg. 100:up:2, will fetch price every 2 seconds and notify you if price > match")
@click.option("-p", "--plot", is_flag=True)
@click.option("--pretty", is_flag=True)
@click.option("--bean", is_flag=True)
@click.option("--notify", is_flag=True)
def fetch(exchange, spot, option, plot, seconds, pretty, bean, notify, match):
        # import time
        # startTime = time.time()
        if seconds:
                second = seconds
        else:
                seconds = 1
        ccxt_calls.fetch(exchange, spot, option, plot, seconds, pretty, bean, notify, match)
        # executionTime = (time.time() - startTime)
        # print(f'took {str(executionTime)} seconds to execute')


@click.group()
def db_operations():
        pass


@db_operations.command()
@click.option("-x", "--exchange", required=False, help="FTX")
@click.option("--search", is_flag=True, help="Boolean")
@click.option("-t", "--term", required=False, help="object::object")
def show_db(exchange, search, term):
        
        db_calls.show_db(exchange, search, term)


@click.group()
def cryptodash_get():
        pass


@cryptodash_get.command()
@click.option("-x", "--exchange", required=True, help="FTX")
@click.option("-s", "--spot", required=True, help="solusd, btcusd, etc...")
@click.option("-o", "--option", required=True, help="price, summary, trades, ohlc")
def cryptodash(exchange, spot, option):
        command = './cryptodash /%s /%s %s' % (spot, option, exchange)
        # print(command)
        os.system(command)


@click.group()
def report_cmd():
        pass


@report_cmd.command()
@click.option("-x", "--exchange", required=False, help="FTXUS, BITSTAMP, KRAKEN")
@click.option("-o", "--option", required=False, help="default=all, pl")
@click.option("-p", "--plot", is_flag=True)
def report(exchange=None, option='all', plot=False):

        db_calls.report(exchange, option, plot)


@click.group()
def prompt_cmd():
        pass


@prompt_cmd.command()
@click.option("-x", "--exchange", prompt="Exchange", help="FTXUS, BITSTAMP, KRAKEN")
@click.option("-s", "--spot", prompt="Spot", help="SOL/USD, BTC/USD...ETC")
@click.option("-q", "--qty", prompt="QTY", help="Float")
@click.option("-B", "--buy", prompt="Buy", help="Float")
@click.option("-S", "--sell", prompt="Sell", help="Float, cp for current price")
@click.option("-d", "--date", help="Float, cp for current price")
@click.option("--save", is_flag=True, help="Save entry to log")
@click.option("--real", is_flag=True, help="Is this a real operation?")
@click.option("--comment", prompt="comment", help="A comment")
@click.option("--test", is_flag=True, default=False, help="A comment")
@click.option("--bean", is_flag=True, help="A comment")
def prompt(exchange, spot, qty, buy, sell, save, comment, real, test, bean, date):
        if sell == 'cp':
                apiKey = getAPI(exchange)['apiKey']
                secret = getAPI(exchange)['secret']
                ccxt_api = ccxt_operations(exchange, apiKey, secret)
                result = ccxt_api.fetch(spot)
                current_price = result['info']['price']
                sell = current_price
        if test:
                pass
                # if strategy != None:
                #     s = strategy
                #     a = getSTRATEGY(s)
                #     print(a)
                #     exec(a['action'].replace('VAR', qty))

        calc(exchange, spot, float(qty), float(
                buy), float(sell), save, comment, real, bean, date)


def getHash(data, type):
        if type == 'json':
                d = json.dumps(data, sort_keys=True)
        elif type == 'str':
                d = data
        sha256 = hashlib.sha256(d.encode('utf-8')).hexdigest()
        return sha256


def save_log(exchange_, spot, q,
                         entry, exit, current_price,
                         timestamp, datetime_,
                         buy_fee, sell_fee, profit, comment, real, buy, sell,
                         run_for_the_hills, run_for_the_hills_sell_fee, run_for_the_hills_profit, bean, date):
        if real is True:
                table_name = exchange_
                # real = 1
        else:
                # real = 0
                table_name = "Simulation"
        log = {
                "exchange": exchange_,
                "spot": spot,
                "timestamp": timestamp,
                "datetime": datetime_,
                "current_price": current_price,
                "trade_postion": {
                        "qty": q,
                        "buy_price": entry,
                        "buy": buy,
                        "sell_price": exit,
                        "sell": sell,
                        "buy_fee": buy_fee,
                        "sell_fee": sell_fee,
                        "p/l": round(profit, 2),
                },
                "comment": comment,
                "real": real,
                "run_for_the_hills": {
                        "rfth": run_for_the_hills,
                        "rfth_fee": run_for_the_hills_sell_fee,
                        "rfth_profit": run_for_the_hills_profit
                }
        }
        # sha256 = hashlib.sha256(json.dumps(log, sort_keys=True).encode('utf-8')).hexdigest()
        sha256 = getHash(log, 'json')
        HASH = {'hash': sha256}

        table = DB.table(table_name)
        table.insert(log)
        query = Query()
        table.update(HASH, query.timestamp == timestamp)



def green_red(i):
        if i > 0 or i == 0:
                color = "green bold italic"
        else:
                color = "red bold italic"
        return color


def calc(exchange_, spot, q, entry, exit, save, comment, real, bean, date):
        # click.clear()
        dt = datetime.now()
        apiKey = getAPI(exchange_)['apiKey']
        secret = getAPI(exchange_)['secret']
        ccxt_api = ccxt_operations(exchange_, apiKey, secret)
        result = ccxt_api.fetch(spot)
        table = Table(title="Trade")
        console = Console()
        current_price = result['info']['price']
        
        if date is None:
                timestamp = datetime.timestamp(dt)
                datetime_ = dt
        else:
                timestamp = datetime.timestamp(dt)
                datetime_ = str(datetime.strptime(date, "%Y-%m-%d"))
        
        qty = float(q)
        buy = qty * entry
        buy_fee = (getFee(exchange_)['maker'] * buy)
        sell = qty * exit
        sell_fee = (getFee(exchange_)['maker'] * sell)
        run_for_the_hills = float(float(current_price) * qty)
        run_for_the_hills_sell_fee = (
                getFee(exchange_)['maker'] * run_for_the_hills)
        profit = float((sell - buy) - (buy_fee + sell_fee))
        run_for_the_hills_profit = float(
                (run_for_the_hills - buy) - (buy_fee + run_for_the_hills_sell_fee))
        total_sar = float(profit * 3.75)
        table.add_column("Live Price", justify="center",
                                         style="green italic", no_wrap=True)
        table.add_column("RFTH", justify="center", style="cyan", no_wrap=True)
        table.add_column("Date", justify="center", style="cyan", no_wrap=True)
        table.add_column("Timestamp", justify="center", style="cyan", no_wrap=True)
        table.add_column("Buy", justify="center", style="cyan", no_wrap=True)
        table.add_column("Sell", justify="center", style="cyan", no_wrap=True)
        table.add_column("Buy Fee", justify="center", style="cyan", no_wrap=True)
        table.add_column("Sell Fee", justify="center", style="cyan", no_wrap=True)
        table.add_column("PL", justify="center",
                                         style=green_red(profit), no_wrap=True)
        table.add_column("PL SAR", justify="center",
                                         style=green_red(total_sar), no_wrap=True)

        table.add_row(str(current_price),
                                    str(run_for_the_hills),
                                    str(timestamp),
                                    str(datetime_),
                                    str(buy),
                                    str(sell),
                                    str(buy_fee),
                                    str(sell_fee),
                                    str(round(profit, 2)),
                                    str(round(total_sar, 2)))
        console.print(table)

        if save is True:
                save_log(exchange_, spot, qty, entry, exit,
                                 current_price, timestamp, datetime_, buy_fee, sell_fee, profit, comment, real, buy, sell,
                                 run_for_the_hills, run_for_the_hills_sell_fee, run_for_the_hills_profit, bean, date)

        else:
                pass


def run():
        cmd()
        DB.close()


cmd = click.CommandCollection(sources=[report_cmd,
                                                                             prompt_cmd,
                                                                             db_operations,
                                                                             ccxt_data,
                                                                             ccxt_order_book,
                                                                             get_balance,
                                                                             cryptodash_get,
                                                                             coinglass_,
                                                                             fetch_trades,
                                                                             bean_transaction])
if __name__ == '__main__':
        # print("Hello, [bold magenta]World[/bold magenta]!", ":vampire:", locals())
        # inspect("as", methods=True)
        cmd()
