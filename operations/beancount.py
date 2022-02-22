import re

from config import ACCOUNTS
from config import BEANCOUNT_FILE
from config import DB
from config import BEAN_STRINGS
from datetime import date as datetime_date
from helpers import getAPI
from helpers import getFee
from rich.console import Console

def append_to_beancount(beancount, string_match, transaction):
  """ beancount: string; file :: default is called with config:BEANCOUNT_FILE
      string_match: dict item name
      transaction: string

      Returns I/O on file
      Example call:
        append_to_beancount('example_file', 'match this', 'append this after match')

      Appends 'transaction' in 'beancount'-file after 'string_match'
      string_match is derived from config.py:BEAN_STRINGS:DICT
      Source:
        Someone on stackoverflow; update source later
  """
  try:
    inputfile = open(beancount, 'r').readlines()
    write_file = open(beancount, 'w')
    for line in inputfile:
        write_file.write(line)
        if BEAN_STRINGS[string_match] in line:
            write_file.write(transaction + "\n")
    write_file.close()
    return True

  except Exception as e:
    raise e


def append_to_beancount_as_list(beancount, string_match, transaction):
  """ beancount: string; file :: default is called with config:BEANCOUNT_FILE
      string_match: dict item name
      transaction: string

      Returns I/O on file
      Example call:
        append_to_beancount_as_list('example_file', 'match this', 'append this one line before match')

      Appends {transaction} in {beancount} file one line before {string_match}.
      string_match is derived from config.py:BEAN_STRINGS:DICT
      Source:
        Someone on stackoverflow update source later
  """
  try:
    with open(beancount, 'r') as infile:
      data = infile.read()
    final_list = []
    for ind, val in enumerate(data.split('\n')):
      final_list.append(val)
      if val == BEAN_STRINGS[string_match]:
        final_list.insert(-1, transaction)
    with open(beancount, 'w') as outfile:
      data = outfile.write('\n'.join(final_list))
    return True
  except Exception as e:
    raise e

  return

def update_price(date, spot, price):
  """ date: string; %Y-%m-%d
      spot: string; Pair
      price: string; str(float)

      Returns a call function to append_to_beancount_as_list

      Creates a string from 'date' 'spot' 'price';
      so that dump = 
          {date} price {spot} {price} {currency}
          Example:
          2022-02-12 price SOL  94.9225 USD
      and calls append_to_beancount_as_list

      * A setback here is that the spot is derived from the user input;
        meaning that if the user was to input BTC/USD for instance, as is 
        the case in ccxt_calls:fetch, the spot is BTC and the currency is
        USD.
      * This means that arbitrage pricing is not supported; as in:
        {date} price {exchange_based_spot} {price} {currency}
        Excample:
          2022-02-12 price FTX-BTC      40001 USD
          2022-02-12 price KRAKEN-BTC   40000 USD
      * To achieve this, one must first define the necessary accounts, each with
        its very own currency in beancount.
          2020-01-01 open Assets:CRYPTO:FTX:BTC-USD         FTX-BTC
          2020-01-01 open Assets:CRYPTO:Kraken:BTC-USD      KRAKEN-BTC
      * This could be later added in the form of 'opening' an account
        for any new price call if it doesn't already exist.
  """
  # spot_format = spot.replace('/', '-')
  try:

    spot_format = spot.split('/')[0]
    currency = spot.split('/')[1]
    dump = f'''{date} price {spot_format}\t{price} {currency}'''
    append_to_beancount_as_list(BEANCOUNT_FILE, "price_section", dump)
  except Exception as e:
    raise e

  return

def is_date(date):
    """ date: string; %Y-%m-%d

        Returns true if {date} matches a regex

        Source:
          https://stackoverflow.com/a/61234139
    """
    date_regex = re.search(
        "^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$", date)
    try:
        if date_regex.group():
            return True
    except:
        return False


def open_account(date_object, currency, account):
    """ date: datetime object
        currency: account currency
        account: {account_class: [Assets,
                                Liabilities,
                                Equity,
                                Income,
                                Expenses],
                                main_child_account : default = Crypto,
                                exchange: crypto exchange,
                                spot: crypto currency}

        Returns string
            {date} * open {account_class:main_child_account:exchange:spot} {currency}
        Example:
            2020-01-01 * open Assets:Crypto:FTXUS:SOL SOL
    """
    try:
        if dict(account):
            beancounter_ = f'{date} * open {name} {currency}'
            return beancounter_
    except:
        return f'{account} must be a dict.'

def new_trade(date, note, trade_type, trades):
  """ date: string; %Y-%m-%d
      note: string
      trade_type: string; buy or sell
      trades: dict

      Returns a call function to append_to_beancount

      Prepare the beancount transaction string.

      General format as per beancount documentation:
      date * note
        account amount currency {buy_price cost_currency, date}

      * If the trade_type is of type buy--string-- it will create 3 transactions
        as per beancount's documentation and conventional bookkeeping principles:
        Example:
          2020-02-02 * "12a3fbae41ebbaed7d1ee1443fb7fdfe68baa97b5c7364eebd700ea50fc11146"
            Assets:CRYPTO:FTXUS:Cash              -10477.83 USD
            Assets:CRYPTO:FTXUS:SOL-USD           96.05 SOL {109.0 USD, 2020-02-02}
            Expenses:CRYPTO:FTXUS:Maker:Fees      8.38 USD
        Note the account name is derived from a combination of user input and per config:ACCOUNTS

      * If the trade_type is of type sell--string-- it will create 4 transactions:
        Example:
          2022-02-02 * "12a3fbae41ebbaed7d1ee1443fb7fdfe68baa97b5c7364eebd700ea50fc11146"
            Assets:CRYPTO:FTXUS:Cash              10682 USD
            Assets:CRYPTO:FTXUS:SOL-USD           -96.05 SOL {109.0 USD, 2022-02-02} @111.3 USD
            Expenses:CRYPTO:FTXUS:Maker:Fees      8.55 USD
            Income:CRYPTO:FTXUS:PnL 

        Note that the income account is left blank on purpose.
        When running bean-report it will automatically calculate pnl.

      * An important limitation here is that both entries(buy and sell) are user inputs; there
        is currently no programmatic way to match the sell transaction with the initial buy trade
  """
  if is_date(date):
      # print(date, note, trade_type, trades)
      console = Console()
      date_note = f'{date} * "{note}"\n\t'
      cash = f'''{trades['cash']['account']}\t\t{trades['cash']['amount']} {trades['cash']['currency']}\n\t'''
      fees = f'''{trades['fees']['account']}\t\t{trades['fees']['amount']} {trades['fees']['currency']}\n'''
      if trade_type == 'buy':  
          trade = f'''{trades['trade']['account']}\t\t{trades['trade']['amount']} {trades['trade']['currency']} {{{trades['trade']['buy_price']} {trades['trade']['buy_currency']}, {trades['trade']['buy_date']}}}\n\t'''
          entry = date_note + cash + trade + fees
           
      elif trade_type == 'sell':
        if trades['trade']['buy'] == "":
          # Account for buy price and buy date being empty
          comma = ""
        else:
          comma = ","
        # if is_date(trades['trade']['buy_date']):
        trade = f'''{trades['trade']['account']}\t\t{trades['trade']['amount']} {trades['trade']['currency']} {{{trades['trade']['buy']} {trades['trade']['buy_currency']}{comma} {trades['trade']['buy_date']}}} @{trades['trade']['sell']} {trades['trade']['sell_currency']}\n\t'''
        # pnl = f'''{trades['pnl']['account']}\t\t{trades['pnl']['amount']} {trades['pnl']['currency']}''' Let bean-report calculate pnl
        pnl = f'''\t{trades['pnl']['account']}\t\t\n'''
        entry = date_note + cash + trade + fees + pnl

  append_to_beancount_as_list(BEANCOUNT_FILE, 'transaction_section', entry)
  console.print(entry)

def bean_count_transaction(exchange, spot, price, 
                            qty, buy, sell, 
                            date, comment, buy_price, buy_date):

    trade_account = f'''Assets:{ACCOUNTS['crypto_investment_account']}:{exchange.upper()}:{spot.replace('/', '-')}'''
    cash_account = f'''Assets:{ACCOUNTS['crypto_investment_account']}:{exchange.upper()}:{ACCOUNTS['crypto_cash']}'''
    fee_account = f'''Expenses:{ACCOUNTS['crypto_investment_account']}:{exchange.upper()}:{ACCOUNTS['sub_fee_account']}'''

    if buy and not sell:
        trade_type = 'buy'
        q = float(qty)
        buy_fee = getFee(exchange)['maker'] * q * float(price)
        buy = (q * float(price)) + buy_fee
        buy_post = -1 * buy #Buying
        if date == 'now':
          date = datetime_date.today().strftime("%Y-%m-%d")

        dump = {'cash': {'account': cash_account, 'amount': round(float(buy_post), 2), 'currency': spot.split('/')[1]},
                'trade': {'account': trade_account, 'amount': q, 'currency': spot.split('/')[0], 'buy_price': round(float(price),2), 'buy_currency': spot.split('/')[1], 'buy_date': date},
                'fees': {'account': fee_account, 'amount': round(float(buy_fee),2), 'currency': spot.split('/')[1]}
                }

    if sell and not buy:
        q = float(qty)
        if buy_date is None:
          buy_date = datetime_date.today().strftime("%Y-%m-%d")
        if buy_price is None:
          # Account for buy price and buy date being empty
          buy_price_ = ""
          buy_currency = ""
          buy_date = ""
        else:
          buy_fee = (getFee(exchange)['maker'] * q * float(buy_price))
          buy = q * float(buy_price) + buy_fee
          buy_price_ = round(float(buy_price),2)
          buy_currency = spot.split('/')[1]
        trade_type = 'sell'
        
        sell_fee = getFee(exchange)['maker'] * q * float(price)
        sell = (q * float(price)) - sell_fee
        # pnl = -1 * (float(sell) - float(buy)) #Negative 
        qty = -1 * float(qty) #Selling qty
        if date == 'now':
          date = datetime_date.today().strftime("%Y-%m-%d")

        income_account = f'''Income:{ACCOUNTS['crypto_investment_account']}:{exchange.upper()}:{ACCOUNTS['income_account']}'''

        dump = {'cash': {'account': cash_account, 'amount': round(round(sell),2), 'currency': spot.split('/')[1]},
               'trade': {'account': trade_account, 'amount': qty, 'currency':  spot.split('/')[0], 'buy': buy_price_, 'buy_currency': buy_currency, 'buy_date': buy_date, 'sell': round(float(price),2), 'sell_currency': spot.split('/')[1]},
               'fees': {'account': fee_account, 'amount': round(float(sell_fee),2), 'currency': spot.split('/')[1]},
               'pnl': {'account': income_account}
               # 'pnl': {'account': income_account , 'amount': pnl, 'currency': spot.split('/')[1]}
                }


    new_trade(date, comment, trade_type, dump)



