
# A very simple Flask Hello World app for you to get started with...

from flask import Flask
from flask import render_template
import urllib.request
import urllib.parse
import json

from datetime import date, timedelta

QUOTE_KEYS = ['Name', 'symbol', 'Symbol', 'StockExchange', 'LastTradePriceOnly',
              'TradeDate', 'LastTradeDate', 'LastTradeTime',
              'Change', 'ChangeRealtime', 'DaysValueChange', 'ChangePercentRealtime', 'ChangeinPercent', 'PercentChange',
              'DaysValueChangeRealtime', 'AfterHoursChangeRealtime', 'DaysHigh', 'DaysLow', 'DaysRange',
              'DaysRangeRealtime', 'ExDividendDate',
              'DividendPayDate', 'DividendShare', 'DividendYield', 'EarningsShare',
              'ErrorIndicationreturnedforsymbolchangedinvalid', 'FiftydayMovingAverage',
              'ChangeFromFiftydayMovingAverage', 'PercentChangeFromFiftydayMovingAverage',
              'TwoHundreddayMovingAverage', 'ChangeFromTwoHundreddayMovingAverage',
              'PercentChangeFromTwoHundreddayMovingAverage',
               'MarketCapRealtime', 'MarketCapitalization',
              'Open', 'PERatio', 'PERatioRealtime', 'PreviousClose', 'BookValue', 'PriceBook', 'PriceSales',
              'Volume', 'AverageDailyVolume',
              'YearHigh', 'ChangeFromYearHigh', 'PercebtChangeFromYearHigh', 'YearLow', 'ChangeFromYearLow',
              'PercentChangeFromYearLow', 'YearRange']

app = Flask(__name__)

def getHistStockData(symbol, startDate, endDate):
    formatArgs = {"symbol" : symbol, "startDate": startDate.isoformat(), "endDate": endDate.isoformat()}

    query = '''select * from yahoo.finance.historicaldata
               where symbol = "{symbol}"
               and startDate = "{startDate}" and endDate = "{endDate}"'''.format(**formatArgs)

    url = urllib.parse.urlencode({
        'q': query,
        'format': 'json',
        'env': 'store://datatables.org/alltableswithkeys'
    })
    url = 'http://query.yahooapis.com/v1/public/yql?' + url

    jsonResp = urllib.request.urlopen(url).read().decode(encoding='UTF-8')
    data = json.loads(jsonResp)["query"]["results"]["quote"]

    return data

def getCurrentStockData(symbol):
    url = urllib.parse.urlencode({
        'q': 'select * from yahoo.finance.quotes where symbol = "{s}"'.format(s=symbol),
        'format': 'json',
        'env': 'store://datatables.org/alltableswithkeys'
    })
    url = 'http://query.yahooapis.com/v1/public/yql?' + url

    jsonResp = urllib.request.urlopen(url).read().decode(encoding='UTF-8')
    data = json.loads(jsonResp)["query"]["results"]["quote"]

    return data

@app.route('/')
@app.route('/<symbol>')
def main(symbol='KO'):
    data = getCurrentStockData(symbol)

    today = date.today()
    startDate = today - timedelta(weeks = 26)

    histData = getHistStockData(symbol, startDate, today)

    return render_template('main.html', data=data, keys = QUOTE_KEYS, histData = histData)
