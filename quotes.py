
# A very simple Flask Hello World app for you to get started with...
import flask
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

ERROR_KEY = 'ErrorIndicationreturnedforsymbolchangedinvalid'

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

    try:
        data = json.loads(jsonResp)["query"]["results"]["quote"]
    except:
        return None

    return data

def getCurrentStockData(symbol):
    url = urllib.parse.urlencode({
        'q': 'select * from yahoo.finance.quotes where symbol = "{s}"'.format(s=symbol),
        'format': 'json',
        'env': 'store://datatables.org/alltableswithkeys'
    })
    url = 'http://query.yahooapis.com/v1/public/yql?' + url

    jsonResp = urllib.request.urlopen(url).read().decode(encoding='UTF-8')

    try:
        data = json.loads(jsonResp)["query"]["results"]["quote"]
    except:
        return None

    return data

def hasDataError(data):
    return ERROR_KEY in data and data[ERROR_KEY] is not None

@app.route('/')
@app.route('/<symbol>')
def main(symbol='KO'):
    data = getCurrentStockData(symbol)

    if data is None or hasDataError(data):
        app.logger.error('API did not return any current data for ' + symbol)
        if hasDataError(data) :
            app.logger.error(data['ErrorIndicationreturnedforsymbolchangedinvalid'])
        flask.abort(404)

    today = date.today()
    startDate = today - timedelta(weeks = 26)

    histData = getHistStockData(symbol, startDate, today)

    if histData is None:
        app.logger.error('API did not return any historical data for ' + symbol)

    return render_template('main.html', data=data, keys = QUOTE_KEYS, histData = histData)
