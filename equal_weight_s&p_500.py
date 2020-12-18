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
    #print(symbol_strings[i])


final_dataframe = pd.DataFrame(columns = my_columns)
# print (final_dataframe)
for symbol_string in symbol_strings:
    #print (symbol_string)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    #print(batch_api_call_url)
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

#print (final_dataframe)


#Calculating the number of Shares to buy
portfolio_size = input('Enter the value of your portfolio')
try:
    val = float(portfolio_size)
    print(val)
except ValueError:
    print ('That is not a number')
    portfolio_size = input('Enter the value of your portfolio')
    val = float(portfolio_size)

position_size = val/len(final_dataframe.index)
#print(position_size)
#number_of_apple_shares = position_size/500
#print(math.floor(number_of_apple_shares))
for i in range(0, len(final_dataframe.index)):
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size/final_dataframe.loc[i, 'Stock Price'])

#print(final_dataframe)

# Formatting our excel output
writer = pd.ExcelWriter('trades.xlsx', engine='xlsxwriter')
final_dataframe.to_excel(writer, 'Recommended', index=False)

#Creating the formats
background_color = '#0a0a23'
font_color = 'ffffff'

string_format = writer.book.add_format(
    {
        'font_color':font_color,
        'bg_color': background_color,
        'border':1
    }
)

dollar_format = writer.book.add_format(
    {
        'num_format': '$0.00',
        'font_color':font_color,
        'bg_color': background_color,
        'border':1
    }
)

integer_format = writer.book.add_format(
    {
        'num_format': '0',
        'font_color':font_color,
        'bg_color': background_color,
        'border':1
    }
)

# writer.sheets['Recommended'].set_column('A:A', #This tells the method to apply the format to column B
#                      18, #This tells the method to apply a column width of 18 pixels
#                      string_format #This applies the format 'string_template' to the column
#                     )
# writer.sheets['Recommended'].set_column('B:B', #This tells the method to apply the format to column B
#                      18, #This tells the method to apply a column width of 18 pixels
#                      string_format #This applies the format 'string_template' to the column
#                     )
# writer.sheets['Recommended'].set_column('C:C', #This tells the method to apply the format to column B
#                      18, #This tells the method to apply a column width of 18 pixels
#                      string_format #This applies the format 'string_template' to the column
#                     )
# writer.sheets['Recommended'].set_column('D:D', #This tells the method to apply the format to column B
#                      18, #This tells the method to apply a column width of 18 pixels
#                      string_format #This applies the format 'string_template' to the column
#                     )
# writer.save()

# writer.sheets['Recommended'].write('A1', 'Ticker', string_format)
# writer.sheets['Recommended'].write('B1', 'Stock Price', dollar_format)
# writer.sheets['Recommended'].write('C1', 'Market Capitalization', dollar_format)
# writer.sheets['Recommended'].write('D1', 'Number of Shares to Buy', integer_format)

column_formats = {
    'A': ['Ticker', string_format],
    'B': ['Stock Price', dollar_format],
    'C': ['Market Capitalization', dollar_format],
    'D': ['Number of Shares to Buy', integer_format]
}

for column in column_formats.keys():
    writer.sheets['Recommended'].set_column(f'{column}:{column}', 18, column_formats[column][1])
    writer.sheets['Recommended'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

writer.save()