# cryptodash

A terminal based/ccxt powered portfolio manager with beancount at its core.

Disclaimers

* *"beancount at its core" is a bit misleading. The only interaction between cryptodash and beancount is minute at best...appending to a text file.*
* *Limited to ftxus.*

### Basic Usage

```bash
Commands:
  bean
  bean-report-pdf
  coinglass
  fetch
  fetch-balance
  fetch-trade
  order-book
  prompt
  report
  show-db
```

#### bean
bean relies on `BEANCOUNT_FILE` as set in `config.py`.

General format as per beancount's documentation:
```txt
date * note
account amount currency {buy_price cost_currency, date}
```
If the trade is of type `buy` it will create 3 transactions:
```
2020-02-02 * "12a3fbae41ebbaed7d1ee1443fb7fdfe68baa97b5c7364eebd700ea50fc11146"
Assets:CRYPTO:FTXUS:Cash          -10477.83 USD
Assets:CRYPTO:FTXUS:SOL-USD         96.05 SOL {109.0 USD, 2020-02-02}
Expenses:CRYPTO:FTXUS:Maker:Fees      8.38 USD
```
Note that the account name is derived from a combination of user input and `ACCOUNTS` in `config.py`

```python
ACCOUNTS = {
    'crypto_investment_account': 'CRYPTO',
    'crypto_cash': 'Cash',
    'main_fee_account': 'Financial',
    'sub_fee_account': 'Maker:Fees',
    'income_account': 'PnL',
    }
```

If the trade is of type `sell` it will create 4 transactions:
```txt
2022-02-02 * "12a3fbae41ebbaed7d1ee1443fb7fdfe68baa97b5c7364eebd700ea50fc11146"
Assets:CRYPTO:FTXUS:Cash          10682 USD
Assets:CRYPTO:FTXUS:SOL-USD         -96.05 SOL {109.0 USD, 2022-02-02} @111.3 USD
Expenses:CRYPTO:FTXUS:Maker:Fees      8.55 USD
Income:CRYPTO:FTXUS:PnL 
```
Note that the income account is left blank on purpose. When running `bean-report` it will automatically calculate profit and loss.
A limitation here is that both entries(buy and sell) are user inputs; there is currently no programmatic way to match the sell transaction with the initial buy trade. One could rely on beancount's internal matching; as detailed here [reducing positions](https://beancount.github.io/docs/beancount_language_syntax.html#reducing-positions) which was pointed out to me on [Reddit](https://www.reddit.com/r/plaintextaccounting/comments/strng5/matching_transactions_in_beancount/hx5vyhv/?context=3). Although it doesn't always work. More on this in `bean import`.
##### bean usage

```txt
Usage: cryptodash.py bean [OPTIONS]

Options:
  -x, --exchange TEXT   FTXUS, BITSTAMP, KRAKEN
  -s, --spot TEXT       SOL/USD, BTC/USD, ETH/BTC..etc
  -q, --qty TEXT        Float
  -p, --price TEXT      Float
  -d, --date TEXT       Float
  -c, --comment TEXT    Float
  -P, --buy_price TEXT  buy_price
  -Pd, --buy_date TEXT  Buy Date
  --buy                 Float
  --sell                Float, cp for current price

```
```bash
>> ./cryptodash.py bean -x ftxus -s BTC/USD -q 1 -p cp --comment 'Buying BTC' --date 2022-02-13 --buy
2022-02-13 * "Buying BTC"
        Assets:CRYPTO:FTXUS:Cash                -44055.22 USD
        Assets:CRYPTO:FTXUS:BTC-USD             1.0 BTC {44020.0 USD, 2022-02-13}
        Expenses:CRYPTO:FTXUS:Maker:Fees        35.22 USD

```
```bash
>> ./cryptodash.py bean -x ftxus -s SOL/USD -q 4.59 -p 1000  --comment 'selling at a loss' --date 2022-02-13 --sell -P 110.50 -Pd 2022-02-13
2022-02-13 * "selling at a loss"
        Assets:CRYPTO:FTXUS:Cash                4586 USD
        Assets:CRYPTO:FTXUS:SOL-USD             -4.59 SOL {110.5 USD, 2022-02-13} @1000.0 USD
        Expenses:CRYPTO:FTXUS:Maker:Fees        3.67 USD
        Income:CRYPTO:FTXUS:PnL         
```
OR
```
>> ./cryptodash.py bean -x ftxus -s SOL/USD -q 4.59 -p 1000 --comment 'selling at a loss' --date 2022-02-13 --sell
2022-02-13 * "selling at a loss"
        Assets:CRYPTO:FTXUS:Cash                    4586 USD
        Assets:CRYPTO:FTXUS:SOL-USD                 -4.59 SOL {  } @1000.0 USD
        Expenses:CRYPTO:FTXUS:Maker:Fees            3.67 USD
        Income:CRYPTO:FTXUS:PnL   
```
bean will attempt to append the declaration(transaction details) before `;; END Cryptodash` as set in `config.py` `BEAN_STRINGS[transaction_section]` 

```python
BEAN_STRINGS = {
    'price_section': ';; END Crypto Price',
    'transaction_section': ';; END Cryptodash'
    }
```
```bash
2022-02-13 * "Buying BTC"
  Assets:CRYPTO:FTXUS:Cash        -44055.22 USD
  Assets:CRYPTO:FTXUS:BTC-USD       1.0 BTC {44020.0 USD, 2022-02-13}
  Expenses:CRYPTO:FTXUS:Maker:Fees  35.22 USD

2022-02-13 * "selling at a loss"
  Assets:CRYPTO:FTXUS:Cash        4586 USD
  Assets:CRYPTO:FTXUS:SOL-USD       -4.59 SOL {110.5 USD, 2022-02-13} @1000.0 USD
  Expenses:CRYPTO:FTXUS:Maker:Fees  3.67 USD
  Income:CRYPTO:FTXUS:PnL   

;; END Cryptodash

```
####  bean-report-pdf

bean-report-pdf runs a 2 command helper script called `2pdf.sh` to quickly create pdf files from simple text inputs(bean-report output) by converting the output to postscript using `a2ps` and then utilizing ghostscript to create the pdf file.

```bash
#!/bin/bash

FILE=$1

a2ps --silent \
    --columns=1 \
    --rows=1 \
    --landscape \
    --chars-per-line=126 \
    --major=columns \
    -o /tmp/$FILE.ps $FILE

gs -sOutputFile=$FILE.pdf \
    -dNOPAUSE \
    -dBATCH \
    -g583x830 \
    -r72 \
    -sDEVICE=pdfwrite \
    -q  \
    -dSAFER /tmp/$FILE.ps

rm /tmp/$1.ps
rm $1

```

As a standalone command, any txt file can be converted into a pdf formatted file, however, when issueing `bean-report-pdf` a conditonal list is tested against the user input.

```python
beancount_report = ['balances','bal','trial','balsheet','journal','register','account','holdings'
        ,'cash','networth','equity','export_holdings','commodities','lifetimes','prices'
        ,'all_prices','pricedb','pricesdb','prices_db','tickers','symbols'
        ,'accounts','current_events','latest_events','events','activity','updated'
        ,'stats-types','stats-directives','stats-entries','stats-postings','ledger','hledger']
```

This is will eventually be rewritten in python.
##### bean-report-pdf usage

```
Usage: cryptodash.py bean-report-pdf [OPTIONS]

Options:
  -o, --option TEXT  Will run bean-report {BEANCOUNT_FILE} option and output a
                     pdf file with the same name
  --help             Show this message and exit.
```

```bash
>> ./cryptodash.py bean-report-pdf -o holdings
holdings output saved to holdings.pdf
```
![img](https://mad_dev.keybase.pub/pics/Screenshot%20from%202022-03-03%2012-42-24.png)

#### coinglass

coinglass will fetch futures information using the coinglass api; *api key required* in `API` `config.py`
Currenly only supports **Open Interest**.

Although `--interval` is required, I have found that it doens't make a difference in the output.
```bash
Usage: cryptodash.py coinglass [OPTIONS]

Options:
  -o, --option TEXT    openInterest : oi, liquidation_chart: lc, liquidation: l
  -c, --coin TEXT      SOL, BTC, ETH..etc
  -i, --interval TEXT  0=ALL, 2=1H ,1=4H 4=12H
  -t, --timetype TEXT  1m=9, 5m=3, 15m=10, 30=11, 4h=1, 12h=4, 90d =18
  --help               Show this message and exit.

```
##### coinglass usage
```
>> ./cryptodash.py coinglass -c SOL -o oi -i 1
```
![coinglass](https://mad_dev.keybase.pub/pics/Screenshot%20from%202022-03-03%2012-56-54.png)

#### fetch

Fetch basic spot information

##### fetch usage
```
Usage: cryptodash.py fetch [OPTIONS]

Options:
  -x, --exchange TEXT  FTXUS, BITSTAMP, KRAKEN
  -s, --spot TEXT      SOL/USD, BTC/USD, ETH/BTC..etc
  -o, --option TEXT    See All
  --seconds TEXT       plot seconds
  --match TEXT         notify if match. price:up|down:seconds eg. 100:up:2,
                       will fetch price every 2 seconds and notify you if
                       price > match
  -p, --plot
  --pretty             Table
  --bean               Add price to beancount; only works for price
  --notify
  --help               Show this message and exit.

```
with `--bean`, the price entry will be appended to beancount before `;; END Crypto Price`.

```
2022-03-03 price SOL                99.925 USD
;; END Crypto Price
```
`--notify` is still in the testing phases.

![fetch](https://mad_dev.keybase.pub/pics/Peek%202022-03-03%2014-06.gif)

#### fetch-balance

This will only work on ftxus. As with most of this project, ftxus is the only testing ground.

```
Usage: cryptodash.py fetch-balance [OPTIONS]

Options:
  -x, --exchange TEXT  FTXUS, BITSTAMP, KRAKEN
  --help               Show this message and exit.

```

#### fetch-trade

```
Usage: cryptodash.py fetch-trade [OPTIONS]

Options:
  -x, --exchange TEXT  FTXUS, BITSTAMP, KRAKEN
  -s, --spot TEXT      SOL/USD, BTC/USD, ETH/BTC..etc
  -o, --option TEXT    market, open, orders
  -S, --since INTEGER  date
  -l, --limit INTEGER  int
  -p, --plot
  --interactive
  --bean
  --search TEXT        key::SearchTerm
  --help               Show this message and exit.
```

![fetch-trade](https://mad_dev.keybase.pub/pics/Peek%202022-03-03%2014-16.gif)

`--bean` can be used to import your orders to beancount, however it will most likley raise a few error. Still in testing phases.

#### order-book 

```
Usage: cryptodash.py order-book [OPTIONS]

Options:
  -x, --exchange TEXT  FTXUS, BITSTAMP, KRAKEN
  -s, --spot TEXT      SOL/USD, BTC/USD, ETH/BTC..etc
  -l, --limit TEXT     1, 5, 10, 50..etc MAX=100
  -p, --plot
  --interactive
  -la, --last
  --help               Show this message and exit.
```

![order-book](https://mad_dev.keybase.pub/pics/Peek%202022-03-03%2014-27.gif)

**`prompt`, `report`, `show-db` will be removed in later versions.**