from config import API
from config import DB
from config import FEES
from config import STRATEGIES
from config import URLS
from config import COLORS
from rich import print
from rich.table import Table
from tinydb import Query
from tinydb import TinyDB
from tinydb import where
from uniplot import plot as unipl
from typing import Optional
import click

import pandas as pd

import datetime
import dateutil.parser

import gi
gi.require_version("Notify", "0.7")
from gi.repository import Notify


###

def getAPI(exchange_: dict) -> str:
        return API[exchange_]


def getURL(service: dict) -> str:
        return URLS[service]


def getFee(exhange_: dict) -> str:
        return FEES[exhange_]


def getSTRATEGY(strategy: dict) -> str:
        return STRATEGIES[strategy]

def parse_date_time(dateObject: datetime) -> list:
    parserser = dateutil.parser.isoparse(dateObject)
    return [datetime.datetime.strftime(parserser, '%Y-%m-%d'), datetime.datetime.strftime(parserser, '%H:%M:%S')]
    
class Notification:
    # Remove Later
    def __init__(self, title, summary, body):
        self.title = title
        self.summary = summary
        self.body = body

    def show(self):
        Notify.init(self.title)
        return Notify.Notification.new(self.summary, self.body, "dialog-information").show()

    def uninit(self):
        Notify.uninit()


def raise_error(
    option: str,
    msg: str) -> Exception:
        return click.BadOptionUsage(option, msg)


def db_search(table=None, option='all'):
        if option == 'all':
                search_query = Query().real == 1
        elif option == 'pl':
                search_query = (Query().real == 1) & (Query().trade_postion.sell != 0)
        if not table:
                for i in DB.tables():
                        table_ = DB.table(i)
                        table_search = table_.search(search_query)
                        # print(i)
                        # print(table_search)
        else:
                table_ = DB.table(table)
                table_search = table_.search(search_query)
        return table_search


def db_search_pl(table=None):
        if not table:
                for i in DB.tables():
                        table_ = DB.table(i)
                        table_search = table_.search(
                                (Query().real == 1) & (Query().trade_postion.sell != 0))
                        print(i)
                        print(table_search)
        else:
                table_ = DB.table(table)
                table_search = table_.search(
                        (Query().real == 1) & Query().trade_postion.sell != 0)
        return table_search


def progress_bar(task, task_name):
        with Progress() as progress:

                task_in_progress = progress.add_task(task_name, total=100)
                task

                while not progress.finished:
                        progress.update(task_in_progress, advance=0.5)


def red_font_negatives(series):
        highlight = 'color: red;'
        default = ''
        return [highlight if e < 0 else default for e in series]


def bold_max_value_in_series(series):
        highlight = 'font-weight: bold;'
        default = ''

        return [highlight if e == series.max() else default for e in series]


def red_background_zero_values(cell_value):
        highlight = 'background-color: tomato;'
        default = ''
        if cell_value == 0:
                return highlight
        else:
                return default


def isNaN(num):
        return num != num


def plot_dataframe(data, x, y, kind, columns):
        df = pd.DataFrame(data, columns)
        df.plot(x, y, kind)
        plt.show()

def live_plot(size, x_vec, y_vec):
        size = 100
        x_vec = np.linspace(0, 1, size+1)[0:-1]
        y_vec = np.random.randn(len(x_vec))
        line1 = []
        while True:
                result = ccxt_api.fetch(spot)
                rand_val = result['info'][option]
                y_vec[-1] = rand_val
                line1 = live_plotter(x_vec, y_vec, line1)
                y_vec = np.append(y_vec[1:], 0.0)

# def dataframe_to_rich_table(
#   dataframe: pd.DataFrame,
#   table: Table,
#   index: bool = True,
#   index_name: Optional[str] = None) -> Table:
def df_to_table(
    pandas_dataframe: pd.DataFrame,
    rich_table: Table,
    show_index: bool = True,
    index_name: Optional[str] = None,
    justify: str = None,
    style: str = None
) -> Table:

    """Convert a pandas.DataFrame obj into a rich.Table obj.
    Args:
        pandas_dataframe (DataFrame): A Pandas DataFrame to be converted to a rich Table.
        rich_table (Table): A rich Table that should be populated by the DataFrame values.
        show_index (bool): Add a column with a row count to the table. Defaults to True.
        index_name (str, optional): The column name to give to the index column. Defaults to None, showing no value.
    Returns:
        Table: The rich Table instance passed, populated with the DataFrame values.

        source: https://gist.github.com/avi-perl/83e77d069d97edbdde188a4f41a015c4
        """

    if show_index:
        index_name = str(index_name) if index_name else ""
        rich_table.add_column(index_name, justify=justify, style=style)

    for column in pandas_dataframe.columns:
        rich_table.add_column(str(column), justify=justify, style=style)

    for index, value_list in enumerate(pandas_dataframe.values.tolist()):
        row = [str(index)] if show_index else []
        row += [str(x) for x in value_list]
        rich_table.add_row(*row)

    return rich_table


def csv_plot(x_vec, y_vec, interactive, legend_labels, title, height, width):

        unipl(color=True,
                            ys=[bid_price_array, ask_price_array],
                            interactive=interactive,
                            legend_labels=["Bid", "Ask"],
                            title="Bids vs Asks",
                            height=30,
                            width=100,
                            y_gridlines=[float(current_price['bid']), float(current_price['last']), float(current_price['ask'])])


