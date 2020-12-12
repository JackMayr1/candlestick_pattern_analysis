# Created By Jack Mayr
import csv
import os
import datetime
import pandas as pd
import talib
import yfinance as yf
from patterns import patterns

pd.set_option('display.max_columns', 10)


# take the the 500 companies from the S&P 500 and download their daily data from yahoo finance
# output is a csv file for every company in the S&P 500
def download_csv_files():
    today = datetime.date.today()
    curr_date = today.strftime("%Y-%m-%d")
    print(curr_date)
    with open('datasets/companies.csv') as f:
        companies = f.read().splitlines()
        for company in companies:
            symbol = company.split(',')[0]
            df = yf.download(symbol, start="2020-01-01", end=curr_date)
            df.to_csv('datasets/daily/{}.csv'.format(symbol))
    return


# take downloaded datasets and use a technical analysis library to identify dates where certain candlestick patterns
# occur and analyze other momentum indicators for that specific day
# output is datafiles for each of the 62 candlestick patterns, and the data points for each occurence with both data
# from yahoo finance and from added technical indicators from TA-LIB
def analysis():
    rank_file = 'datasets/allpats.csv'
    with open(rank_file, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        allpats_fields = ['Pattern', 'Trend', 'Open', 'High', 'Low', 'Close', 'ADOSC', 'Percent Change', 'BB Upper',
                          'BB Middle', 'BB Lower']
        csvwriter.writerow(allpats_fields)
        for numpats in patterns:
            pattern = numpats
            datafiles = os.listdir('datasets/daily')
            pattern_engulfing_days = 0
            pattern_occurences = 0
            pattern_total = 0
            pattern_pat_days = 0
            pattern_function = getattr(talib, pattern)
            rank_file = 'datasets/rankings/simple_pattern_rank.csv'
            with open(rank_file, 'w') as csvfile1:
                csvwriter1 = csv.writer(csvfile1)
                # writing the fields
                fields = ['Pattern', 'Average Percent Gain']
                csvwriter1.writerow(fields)
                fields = ['Date', 'Symbol', 'Open', 'Close', 'Trend', 'Profit', 'Percent Change',
                          'Avg Directional Movement']
                pattern_filename = 'datasets/pattern_outputs/{}_records.csv'.format(pattern)
                with open(pattern_filename, 'w') as csvfile2:
                    # creating a csv writer object
                    csvwriter2 = csv.writer(csvfile2)
                    # writing the fields
                    csvwriter2.writerow(fields)

                    for filename in datafiles:
                        pattern_list = {'symbol': [], 'occurences': [], 'avg_profit': []}
                        stock_historical_data = 'datasets/daily/{}'.format(filename)
                        symbol = filename.split('.')[0]
                        # print test
                        # print(symbol)

                        df = pd.read_csv(stock_historical_data)

                        try:
                            pat_result = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
                            wma_result = talib.WMA(df['Close'], timeperiod=30)
                            adx_result = talib.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
                            apo_result = talib.APO(df['Close'])
                            dx_result = talib.DX(df['High'], df['Low'], df['Close'], timeperiod=14)
                            adosc_result = talib.ADOSC(df['High'], df['Low'], df['Close'], df['Volume'], fastperiod=3,
                                                       slowperiod=10)
                            natr_result = talib.NATR(df['High'], df['Low'], df['Close'], timeperiod=14)
                            df['CDL Pattern'] = pattern
                            df[pattern] = pat_result
                            df['Trend'] = 'None'
                            df['Profit'] = 0.0
                            df['Percent Change'] = 0.0
                            df['WMA'] = wma_result
                            df['ADX'] = adx_result
                            df['APO'] = apo_result
                            df['DX'] = dx_result
                            df['ADOSC'] = adosc_result
                            df['ADOSC'] = natr_result
                            bb_upper, bb_middle, bb_lower = talib.BBANDS(df['Close'], timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
                            df['bb upper'] = bb_upper
                            df['bb middle'] = bb_middle
                            df['bb lower'] = bb_lower
                            midprice = talib.MIDPRICE()
                            df['midprice'] = midprice

                            # print(df)

                            for i, row in df.iterrows():
                                try:
                                    df.at[i, 'Open'] = round(df.at[i, 'Open'], 2)
                                    df.at[i, 'Close'] = round(df.at[i, 'Close'], 2)
                                    if df.at[i, pattern] > 0:
                                        df.at[i, 'Trend'] = 'Bullish'
                                        # print(df.at[i+1, 'Close'], ' | ',  df.at[i+1, 'Open'])
                                        df.at[i, 'Profit'] = round(df.at[i + 1, 'Close'] - df.at[i + 1, 'Open'], 2)
                                        df.at[i, 'Percent Change'] = round(
                                            (df.at[i, 'Profit'] / df.at[i + 1, 'Open']) * 100, 2)
                                        flagged_row = [df.at[i, 'Date'], symbol, df.at[i, 'Open'], df.at[i, 'Close'],
                                                       df.at[i, 'Trend'], df.at[i, 'Profit'],
                                                       df.at[i, 'Percent Change'],
                                                       df.at[i, 'Avg Directional Movement']]
                                        csvwriter2.writerow(flagged_row)
                                        all_pats_flagged_row = [pattern, df.at[i, 'Trend'], df.at[i, 'Open'],
                                                                df.at[i, 'High'], df.at[i, 'Low'], df.at[i, 'Close'],
                                                                df.at[i, 'Volume'], df.at[i, 'Percent Change']]
                                    elif df.at[i, '{}'.format(pattern)] < 0:
                                        # print(df.at[i + 1, 'Close'], ' | ', df.at[i + 1, 'Open'])
                                        df.at[i, 'Trend'] = 'Bearish'
                                        df.at[i, 'Profit'] = round(-(df.at[i + 1, 'Close'] - df.at[i + 1, 'Open']), 2)
                                        df.at[i, 'Percent Change'] = round(
                                            (df.at[i, 'Profit'] / df.at[i + 1, 'Open']) * 100, 2)

                                        flagged_row = [df.at[i, 'Date'], symbol, df.at[i, 'Open'], df.at[i, 'Close'],
                                                       df.at[i, 'Trend'], df.at[i, 'Profit'],
                                                       df.at[i, 'Percent Change'],
                                                       df.at[i, 'Avg Directional Movement']]
                                        csvwriter2.writerow(flagged_row)
                                except:
                                    pass
                            stock_pat_days = df[df[pattern] != 0]
                            stock_occurences = len(stock_pat_days)
                            stock_total = sum(df['Percent Change'])
                            pattern_occurences += stock_occurences
                            pattern_total += stock_total
                        except:
                            pass
                if pattern_occurences > 0:
                    pattern_average = pattern_total / pattern_occurences
                else:
                    pattern_average = 0
                row = [pattern, pattern_average]
                csvwriter1.writerow(row)
                print(pattern, ': ', pattern_average)


# runs through each of the output files from analysis() and demonstrates performance if we acted on just that
# candlestick pattern.  point of comparison between patterns as well as for neural network later.
def pattern_analysis():
    datafiles = os.listdir('datasets/pattern_outputs')
    for filename in datafiles:
        file = 'datasets/pattern_outputs/{}'.format(filename)
        print(filename)
        split = filename.split("_")
        pat_name = split[0]
        pattern_filename = 'datasets/profit_table/{}_profit_tracker.csv'.format(pat_name)
        print(pattern_filename)
        balance = 10000
        df = pd.read_csv(file)
        print('opening ', file)
        df = df.sort_values(by='Date')
        df = df.drop_duplicates(subset='Date', keep='first')
        try:
            with open(pattern_filename, 'w') as csv_writing_file:
                csvwriter = csv.writer(csv_writing_file)
                fields = ['Date', 'Symbol', 'Open', 'Close', 'Trend', 'Percent Change', 'Balance']
                csvwriter.writerow(fields)
                for i, row in df.iterrows():
                    # print(df.at[i, 'Date'], dif df.at[i] != df.at[i+1]:

                    balance += (balance * float(df.at[i, 'Percent Change'])) / 100
                    add_row = [df.at[i, 'Date'], df.at[i, 'Symbol'], round(df.at[i, 'Open'], 2),
                               round(df.at[i, 'Close'], 2), df.at[i, 'Trend'],
                               round(df.at[i, 'Percent Change'], 2), round(balance, 2)]
                    csvwriter.writerow(add_row)
        except:
            pass
        print(pat_name, ", End Balance: ", balance)


# ranks candlestick patterns just off their average return
# a candlestick pattern is a potential indicator for stock activity the next day, and profit is calculated
# depending on whether we see a bullish or bearish signal from pattern
# if it is bullish, we calculate profit by taking the next days close price - open price
# if it is bearish, we calculate profit by taking open price - close price
# to calculate percent profit, we take profit / open price
def pattern_rank():
    datafiles = os.listdir('datasets/pattern_outputs')
    pat_rank = []
    rankings_filename = 'datasets/rankings/basic_avg_profit_rankings.csv'
    with open(rankings_filename, 'w') as csv_writing_file:
        csvwriter = csv.writer(csv_writing_file)
        d = {'Pattern': [], 'Average Change': []}
        df2 = pd.DataFrame(data=d)

        for filename in datafiles:
            file = 'datasets/pattern_outputs/{}'.format(filename)
            print(file)
            split = filename.split("_")
            pat_name = split[0]
            df = pd.read_csv(file)
            index = df.index
            number_of_rows = len(index)
            perc_profit_avg = sum(df.at['Percent Change']) / number_of_rows
            row = [pat_name, perc_profit_avg]
            df2.append(row)
        df2 = df2.sort_values(by='Average Change')
        csvwriter.writerows(df2)
        print(df2)


# takes each of the 62 candlestick patterns and creates a potential buy-sell plan by arbitrarily deleting instances of
# the same date
def combine_patterns():
    datafiles = os.listdir('datasets/profit_table')
    combined_pattern_filename = 'datasets/rankings/total_file.csv'
    df3 = pd.dataframe
    for filename in datafiles:
        df = pd.read_csv(filename)
        df2 = pd.read_csv('datasets/rankings/basic_avg_profit_rankings.csv')
        split = filename.split("_")
        pat_name = split[0]
        df['Pattern'] = pat_name
        df3.append(df)
    df3.sort_values('Date')
    for i, row in df3.iterrows():
        if df3.at[i, 'Date'] == df3.at[i + 1, 'Date']:
            if df2(df3.at[i, 'Pattern']).index < df2(df3.at[i + 1, 'Pattern']).index:
                df3 = df3.remove(df3.at[i + 1])
            else:
                df3 = df3.remove(df3.at[i])


#Function calls for creating datasets

# download_csv_files()
analysis()
pattern_analysis()
# pattern_rank()
# combine_patterns()


# analyze_patterns()
