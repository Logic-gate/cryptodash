#!/usr/bin/python
# -*- coding: utf-8 -*-
from tinydb import TinyDB

DB_LOG_FILE = 'logs/cryptodash.json'
BEANCOUNT_FILE = 'beancount/portfolio.beancount'
DB = TinyDB(DB_LOG_FILE)

#Visiuals

COLORS = {
    'white': '#E9D8A6',
    'red': '#ef476f',
    'yellow': '#EE9B00',
    'orange': '#BB3E03',
    'blue': '#0A9396',
    'green': '#43AA8B',
    }

UNICODE_SHAPES = {
    'ballot_box' : '\u2610'
}

#API 

API = {
    'ftxus': {'apiKey': '',
              'secret': ''},
    'bitstamp': {'apiKey': '',
                 'secret': ''},
    'kraken': {'apiKey': 'a', 'secret': 'a'},
    'coinglass': {'secret': ''},
    }

FEES = {'ftxus': {'maker': 0.0008, 'taker': 0.0008}}

URLS = {'coinglass': {
    'url': 'https://open-api.coinglass.com/api/pro/v1',
    'futures': '/futures',
    'openInterest': '/openInterest',
    'liquidation_chart': '/liquidation_chart',
    'liquidation': '/liquidation',
    'symbol': '?symbol=',
    'interval': '&interval=',
    }}


# Beancount

ACCOUNT_TYPE = ['Assets', 'Liabilities', 'Equity', 'Income', 'Expenses']
ACCOUNTS = {
    'crypto_investment_account': 'CRYPTO',
    'crypto_cash': 'Cash',
    'main_fee_account': 'Financial',
    'sub_fee_account': 'Maker:Fees',
    'income_account': 'PnL',
    }

BEAN_STRINGS = {
    'price_section': ';; END Crypto Price',
    'transaction_section': ';; END Cryptodash'
    }

# Testing

STRATEGIES = {'25%': {
    'name': '25%',
    'desc': 'qty/4 and buy at buy_increments; sell at limit at sell_increment',
    'vars': {
        'buyIncrement': float,
        'sellIncrement': float,
        'limit': float,
        'qty': float,
        'factor': float,
        'low': float,
        },
    'action': 'loop::qty/factor|buy@low>buyIncrement|sell@limit>sellIncrement|::loop',
    }}
