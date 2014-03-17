
# A very simple Flask Hello World app for you to get started with...

from flask import Flask
from flask import render_template
import urllib.request
import urllib.parse
import json

QUOTE_KEYS = ['Name', 'symbol', 'Symbol', 'StockExchange', 'LastTradePriceOnly', 'TradeDate', 'LastTradeDate', 'LastTradeTime',
              'Change', 'ChangeRealtime', 'DaysValueChange', 'ChangePercentRealtime', 'ChangeinPercent', 'PercentChange',
              'DaysValueChangeRealtime', 'AfterHoursChangeRealtime', 'DaysHigh', 'DaysLow', 'DaysRange',
              'DaysRangeRealtime', 'ExDividendDate',
              'DividendPayDate', 'DividendShare', 'DividendYield', 'EarningsShare',
              'ErrorIndicationreturnedforsymbolchangedinvalid', 'FiftydayMovingAverage',
              'ChangeFromFiftydayMovingAverage', 'PercentChangeFromFiftydayMovingAverage',
              'TwoHundreddayMovingAverage', 'ChangeFromTwoHundreddayMovingAverage',
              'PercentChangeFromTwoHundreddayMovingAverage',
               'MarketCapRealtime', 'MarketCapitalization',
              'Open', 'PERatio', 'PERatioRealtime', 'PreviousClose', 'BookValue', 'PriceBook', 'PriceSales', 'Volume', 'AverageDailyVolume',
              'YearHigh', 'ChangeFromYearHigh', 'PercebtChangeFromYearHigh', 'YearLow', 'ChangeFromYearLow',
              'PercentChangeFromYearLow', 'YearRange']

app = Flask(__name__)

@app.route('/')
@app.route('/<symbol>')
def hello_world(symbol='KO'):
    url = urllib.parse.urlencode({
        'q': 'select * from yahoo.finance.quotes where symbol = "{s}"'.format(s=symbol),
        'format': 'json',
        'env': 'store://datatables.org/alltableswithkeys'
    })
    url = 'http://query.yahooapis.com/v1/public/yql?' + url

    jsonResp = urllib.request.urlopen(url).read().decode(encoding='UTF-8')

    data = json.loads(jsonResp)["query"]["results"]["quote"]

    return render_template('main.html', data=data, keys = QUOTE_KEYS)
