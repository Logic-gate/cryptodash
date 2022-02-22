import ccxt

class ccxt_operations:
    def __init__(self, exchange, apiKey, secret):
        self.apiKey = apiKey
        self.secret = secret
        self.exchange = exchange

    def init_ccxt(self):
        CCXT_EXHANGE_CLASS = getattr(ccxt, self.exchange)
        EXCHANGE = CCXT_EXHANGE_CLASS({'apiKey': self.apiKey,
                        'secret': self.secret})
        return EXCHANGE

    def fetch(self, ticker):
        return self.init_ccxt().fetch_ticker(ticker)

    def order_book(self, ticker, limit):
        return self.init_ccxt().fetch_order_book(ticker, limit)

    def balance(self):
        return self.init_ccxt().fetch_balance()

    def fetchOpenOrders(self):
        return self.init_ccxt().fetchOpenOrders()

    def fetchTrades(self, ticker, since, limit):
        return self.init_ccxt().fetchTrades(symbol=ticker, since=since, limit=limit)

    def fetchOrders(self, ticker):
        return self.init_ccxt().fetchOrders(symbol=ticker)


