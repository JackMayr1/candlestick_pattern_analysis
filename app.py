# this file gives us a way to look at candlestick patterns that occurred on the most recent completed trading day
# creates a browser tab that allows us to visualize various patterns, and their occurences in stocks
# adapted from Part Time Larry
import csv
import os
import datetime
import pandas as pd
import talib
import yfinance as yf
from flask import Flask, render_template, request

from patterns import patterns

app = Flask(__name__)


@app.route('/')
def index():
    pattern = request.args.get('pattern', None)
    stocks = {}

    with open('datasets/companies.csv') as f:
        for row in csv.reader(f):
            stocks[row[0]] = {'company': row[1]}

    if pattern:
        datafiles = os.listdir('datasets/daily')
        for filename in datafiles:
            df = pd.read_csv('datasets/daily/{}'.format(filename))
            # print(df)
            pattern_function = getattr(talib, pattern)

            symbol = filename.split('.')[0]
            try:
                result = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
                last = result.tail(1).values[0]
                # print(last)
                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    stocks[symbol][pattern] = None
                # print("{} triggered {}".format(filename, pattern))
            except:
                pass
    return render_template('index.html', patterns=patterns, stocks=stocks, current_pattern=pattern)


@app.route('/snapshot')
def snapshot():
    today = datetime.date.today()
    curr_date = today.strftime("%Y-%m-%d")
    print(curr_date)
    with open('datasets/companies.csv') as f:
        companies = f.read().splitlines()
        for company in companies:
            symbol = company.split(',')[0]
            df = yf.download(symbol, start="2020-01-01", end=curr_date)
            df.to_csv('datasets/daily/{}.csv'.format(symbol))
    return {
        'code': 'success'
    }
