import json

from config import COLORS
from config import DB
from config import DB_LOG_FILE
from helpers import db_search
from helpers import raise_error
from rich import print
from rich.console import Console
from rich.table import Table
from tinydb import where

def show_db(exchange, search, term):
    if search:
        if "::" in term:
            if exchange == 'all':
                for i in DB.tables():
                    table_ = DB.table(i)
                    terms = term.split('::')
                    search_ = table_.search(where(terms[0]) == terms[1])
                    print(search_)
            else:
                table_ = DB.table(exchange)
                terms = term.split('::')
                search_ = table_.search(where(terms[0]) == terms[1])
                print(search_)
        else:
            raise_error(term, 'show-db', 'term',
                        ':: between object and search term.\nsee --help for more')
    else:
        with open(file=DB_LOG_FILE, mode='r') as db:
            obj = json.load(db)
            print(json.dumps(obj, indent=4))

def report(exchange=None, option='all', plot=False):

    table = Table(title="Trading Report")
    if not exchange:
        if not db_search(None, option):
            db_search(None, option)
            # db_search_pl(None)
            table_search = db_search(None, option)
            # table_search_ = db_search_pl(None)
        else:
            table_search = db_search(None, option)
            # table_search_ = db_search_pl(None)

    else:
        if not db_search(exchange, option):
            db_search(exchange, option)
            # db_search_pl(exchange)
            table_search = db_search(exchange, option)
            # table_search_ = db_search_pl(exchange)
        else:
            table_search = db_search(exchange, option)
            # table_search_ = db_search_pl(exchange)

    #real = table_search.search(where('real')==True)
    total = 0
    total_buy_fees = 0
    total_sell_fees = 0
    total_buy_volume = 0
    total_sell_volume = 0
    rfth = 0
    spots = {}
    sep = '*'*15
    roi = []
    table.add_column("Exchange", justify="center",
                     style=COLORS['blue'], no_wrap=True)
    table.add_column("Date", justify="center", style=COLORS['white'])
    table.add_column("Spot", justify="center", style=COLORS['blue'])
    table.add_column("QTY", justify="center", style=COLORS['green'])
    table.add_column("Buy Price", justify="center", style=COLORS['red'])
    table.add_column("Buy USD", justify="center", style=COLORS['red'])
    table.add_column("Sell Price", justify="center", style=COLORS['green'])
    table.add_column("Sell USD", justify="center", style=COLORS['green'])
    table.add_column("PL", justify="center", style=COLORS['green'])
    table.add_column("PL %", justify="center", style=COLORS['green'])
    table.add_column("Status", justify="center", style=COLORS['yellow'])
    table.add_column("HASH", justify="center", style=COLORS['white'])

    for i in table_search:
        total += i['trade_postion']['p/l']
        total_buy_fees += i['trade_postion']['buy_fee']
        total_sell_fees += i['trade_postion']['sell_fee']
        total_buy_volume += i['trade_postion']['buy']
        total_sell_volume += i['trade_postion']['sell']

        if i['trade_postion']['p/l'] > 0:
            status = "[green][bold italic]Profit[/bold italic]:arrow_up_small:[/green]"
        elif i['trade_postion']['p/l'] < 0:
            status = "[blink red]Loss:arrow_down_small:[/blink red]"

        date = str(i['datetime'])
        profit = str(i['trade_postion']['p/l'])

        profit_percentage = (i['trade_postion']['p/l'] / i['trade_postion']['sell']) * 100
        roi.append(float(profit_percentage))
        table.add_row(str(i['exchange']),
                      str(i['datetime']),
                      str(i['spot']),
                      str(i['trade_postion']['qty']),
                      str(i['trade_postion']['buy_price']),
                      str(i['trade_postion']['buy']),
                      str(i['trade_postion']['sell_price']),
                      str(i['trade_postion']['sell']),
                      str(round(i['trade_postion']['p/l'], 3)),
                      str(round(profit_percentage, 3)),
                      status,
                      str("[bold italic]"+i['hash']))
    console = Console()
    # console.rule("[bold red]Chapter 2")
    console.print(table)

    table = Table(title="End Report")

    table.add_column("Total", justify="center",
                     style=COLORS['green'], no_wrap=True)
    table.add_column("Total SAR", justify="center",
                     style=COLORS['green'], no_wrap=True)
    table.add_column("PL/Sell Volume", justify="center",
                     style=COLORS['green'], no_wrap=True)
    table.add_column("ROI", justify="center",
                     style=COLORS['green'], no_wrap=True)
    table.add_column("Buy Fees", justify="center",
                     style=COLORS['yellow'], no_wrap=True)
    table.add_column("Sell Fees", justify="center",
                     style=COLORS['yellow'], no_wrap=True)
    table.add_column("Buy Volume", justify="center",
                     style=COLORS['orange'], no_wrap=True)
    table.add_column("Sell Volume", justify="center",
                     style=COLORS['orange'], no_wrap=True)
    table.add_column("Volume", justify="center",
                     style=COLORS['white'], no_wrap=True)
    # table.add_column("P/L", justify="center", style="cyan", no_wrap=True)
    total_sar = float(total * 3.75)
    total_pl_sell = (total / total_sell_volume) * 100
    total_roi = sum(roi)
    table.add_row(str(total), str(total_sar), str(round(total_pl_sell, 3)), str(round(total_roi, 3)), str(total_buy_fees), str(total_sell_fees), str(
        total_buy_volume), str(total_sell_volume), str(total_buy_volume + total_sell_volume))
    console.print(table)

    if plot:
        print("TODO")


