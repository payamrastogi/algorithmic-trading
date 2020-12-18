import numpy as np
import pandas as pd
import requests
import xlsxwriter 
import math



# importing list of stocks
# ideal world connect to an API that gives a list of all S&P indexes

stocks = pd.read_csv('sp_500_stocks.csv')
print (stocks)

# acquiring an API token - sandbox of IEX Cloud API (randomized data)
from secrets import IEX_CLOUD_API_TOKEN


# making first api call
# market capitalization for each stock
# Price of each stock
# testing sandbox
symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}'
# print(api_url)
data = requests.get(api_url).json()
# print(type(data))
# print(data.status_code)
# print (data)

# Parsing our API call
price = data['latestPrice']
market_cap = data['marketCap']
print(price)
print(market_cap)

#Adding our stocks data to Pandas Data Frame
my_columns = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of Shares to Buy']
final_dataframe = pd.DataFrame(columns = my_columns)
# print (final_dataframe)
to_append = pd.DataFrame([],columns = my_columns)
# print (to_append)
final_dataframe = final_dataframe.append(
    pd.Series(
        [symbol, price, market_cap, 'N/A'], index = my_columns
    ),
    ignore_index=True
)

# print (final_dataframe)

# Looping Through the tickers in List of stocks
final_dataframe = pd.DataFrame(columns=my_columns)
for stock in stocks['Ticker'][:1]:
    # print (stock)
    api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(api_url).json()
    final_dataframe = final_dataframe.append(
        pd.Series(
            [stock, data['latestPrice'], data['marketCap'], 'N/A'], index = my_columns
        ),
        ignore_index=True
    )

print (final_dataframe)

# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(stocks['Ticker'],100))
# print (symbol_groups)
symbol_strings = []
for i in range (0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
    print(symbol_strings[i])


final_dataframe = pd.DataFrame(columns = my_columns)
# print (final_dataframe)
for symbol_string in symbol_strings[:1]:
    #print (symbol_string)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    print(batch_api_call_url)
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series(
                [
                    symbol, 
                    data[symbol]['quote']['latestPrice'], 
                    data[symbol]['quote']['marketCap'], 
                    'N/A'
                ], index = my_columns
            ),
            ignore_index=True
        )

print (final_dataframe)