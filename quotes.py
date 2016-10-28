# coding=utf-8

import flask
from flask import Flask
from flask import render_template
import os.path
import urllib.request
import urllib.parse
import json

from datetime import date, timedelta
from collections import Counter, OrderedDict
from operator import itemgetter

PFOLIO_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'pfolio.json')

QUOTE_KEYS = ['Name', 'symbol', 'Symbol', 'StockExchange', 'LastTradePriceOnly',
              'TradeDate', 'LastTradeDate', 'LastTradeTime',
              'Change', 'ChangeRealtime', 'DaysValueChange', 'ChangePercentRealtime', 'ChangeinPercent', 'PercentChange',
              'DaysValueChangeRealtime', 'AfterHoursChangeRealtime', 'DaysHigh', 'DaysLow', 'DaysRange',
              'DaysRangeRealtime', 'ExDividendDate',
              'DividendPayDate', 'DividendShare', 'DividendYield', 'EarningsShare',
              'ErrorIndicationreturnedforsymbolchangedinvalid',
              'MarketCapRealtime', 'MarketCapitalization',
              'Open', 'PERatio', 'PERatioRealtime', 'PreviousClose', 'BookValue', 'PriceBook', 'PriceSales',
              'Volume', 'AverageDailyVolume',
              'YearHigh', 'ChangeFromYearHigh', 'PercebtChangeFromYearHigh', 'YearLow', 'ChangeFromYearLow',
              'PercentChangeFromYearLow', 'YearRange']

SELECTED_TAGS = ['stocks', 'bonds', 'gold_silver', 'commodities', 'real_estate', 'mining']

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
        data = json.loads(jsonResp)['query']['results']['quote']
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
        data = json.loads(jsonResp)['query']['results']['quote']
    except:
        return None

    return data

def hasDataError(data):
    return ERROR_KEY in data and data[ERROR_KEY] is not None

def avg(nums):
    cnt = len(nums)
    return sum(nums) / float(cnt) if cnt != 0 else 0.0

@app.route('/pfolio')
def pfolio():
    totalValue = 0
    with open(PFOLIO_FILE_PATH) as dataFile:
        pfolioData = json.load(dataFile)

    tagToVal = Counter()

    for position in pfolioData['positions']:
        posQuote = getCurrentStockData(position['symbol'])
        if posQuote:
            price = float(posQuote['LastTradePriceOnly'])
            positionValue = position['count'] * price
            position['price'] = price
            position['value'] = positionValue
            totalValue += positionValue
            for tag in position['tags']:
                tagToVal[tag] += positionValue
    pfolioData['totalValue'] = totalValue
    tagToValOrd = OrderedDict((t , tagToVal[t]) for t in SELECTED_TAGS)
    tagToValOrd.update(sorted(tagToVal.items(), key=itemgetter(0)))
    pfolioData['tagValues'] = tagToValOrd
    return render_template('pfolio.html', data=pfolioData)

@app.route('/')
@app.route('/<symbol>')
def quote(symbol='KO'):
    data = getCurrentStockData(symbol)

    if data is None or hasDataError(data):
        app.logger.error('API did not return any current data for ' + symbol)
        if hasDataError(data) :
            app.logger.error(data['ErrorIndicationreturnedforsymbolchangedinvalid'])
        flask.abort(404)

    currPrice = float(data['LastTradePriceOnly'])

    today = date.today()
    startDate = today - timedelta(days = 366)

    histData = getHistStockData(symbol, startDate, today)
    daysToDma = {}

    if histData is None:
        app.logger.error('API did not return any historical data for ' + symbol)
    else:
        histPrices = [float(dayData['Close']) for dayData in histData]
        daysToDma = {cnt : (avg(histPrices[:cnt])) for cnt in [20, 50, 100, 200]}
        app.logger.error(daysToDma)
        dmaDiffPct = {cnt : 100 * (currPrice - dmaVal) / dmaVal for (cnt, dmaVal) in daysToDma.items()}

    debug = {}

    return render_template('main.html', data=data, keys = QUOTE_KEYS, histData = histData, dma = daysToDma, dmaDiffPct = dmaDiffPct, currPrice = currPrice, debug = debug)

def main():
    app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()
