import numpy as np
import pandas as pd
import requests
import math
from scipy import stats
from statistics import mean
import xlsxwriter
#importing secret
from secrets import IEX_CLOUD_API_TOKEN

#importing list of stocks
stocks = pd.read_csv('sp_500_stocks.csv')

#key stats
symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()
#print(data)


#Parsing API call
#print (data['year1ChangePercent'])

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

#for symbol_string in symbol_strings:
#    print(symbol_string)

#Adding our stocks data to Pandas Data Frame
my_columns = ['Ticker', 'Stock Price', 'One-Year Price Return', 'Number of Shares to Buy']


final_dataframe = pd.DataFrame(columns = my_columns)

#Batch API call
for symbol_string in symbol_strings[:1]:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=stats,price&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    #print (data['AAPL']['price'])
    #print (data['AAPL']['stats'])
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series(
                [
                    symbol, 
                    data[symbol]['price'],
                    data[symbol]['stats']['year1ChangePercent'],
                    'N/A'
                ],
                index = my_columns
            ),
            ignore_index = True
        )

#print (final_dataframe)

#Removing Low momentum stocks
final_dataframe.sort_values('One-Year Price Return', ascending=False, inplace = True)

final_dataframe = final_dataframe[:50]
final_dataframe.reset_index(inplace=True)
#print(final_dataframe)


#Calculating the number of Shares to Buy
def portfolio_input():
    global portfolio_size
    portfolio_size = input('Enter the size of your portfolio: ')
    try:
        float(portfolio_size)
    except:
        print('That is not a number')
        print('Please try again:')
        portfolio_size = input('Enter the size of your portfolio: ')


#print(portfolio_size)




#print(final_dataframe)

#Better and more realistic momentum strategy
#high quality momentum and low quality momnetum strategy


hqm_columns  = [
    'Ticker',
    'Stock Price',
    'Number of Shares to Buy',
    'One-Year Price Return',
    'One-Year Return Percentile',
    'Six-Month Price Return',
    'Six-Month Return Percentile',
    'Three-Month Price Return',
    'Three-Month Return Percentile',
    'One-Month Price Return',
    'One-Month Return Percentile',
    'hqm_score'
]

hqm_dataframe = pd.DataFrame(columns = hqm_columns)

#print(hqm_dataframe)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=stats,price&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    #print (data['AAPL']['price'])
    #print (data['AAPL']['stats'])
    for symbol in symbol_string.split(','):
        hqm_dataframe = hqm_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['price'],
                    'N/A',
                    data[symbol]['stats']['year1ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month6ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month3ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month1ChangePercent'],
                    'N/A',
                    'N/A'
                ],
                index = hqm_columns
            ),
            ignore_index = True
        )
#print(hqm_dataframe)

#Calculating Momentum Percentiles
time_periods = [
    'One-Year',
    'Six-Month',
    'Three-Month',
    'One-Month'
]

for row in hqm_dataframe.index:
    for time_period in time_periods:
        change_col = f'{time_period} Price Return'
        percentile_col = f'{time_period} Return Percentile'
        if hqm_dataframe.loc[row, change_col] == None:
            hqm_dataframe.loc[row, change_col] = 0

for row in hqm_dataframe.index:
    for time_period in time_periods:
        change_col = f'{time_period} Price Return'
        percentile_col = f'{time_period} Return Percentile'
        hqm_dataframe.loc[row, percentile_col] = stats.percentileofscore(hqm_dataframe[change_col], hqm_dataframe.loc[row, change_col])

#print(hqm_dataframe)


#Calculating HQM score
#print (mean ([2,6]))


for row in hqm_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        percentile_col = f'{time_period} Return Percentile'
        momentum_percentiles.append(hqm_dataframe.loc[row, percentile_col])
    hqm_dataframe.loc[row, 'hqm_score'] = mean(momentum_percentiles)




#Selecting 50 best momentum stocks
hqm_dataframe.sort_values('hqm_score', ascending=False, inplace=True)
hqm_dataframe = hqm_dataframe[:50]
hqm_dataframe.reset_index(inplace = True)
#print(hqm_dataframe)


portfolio_input()
position_size = float(portfolio_size)/len(final_dataframe.index)

for i in range(0, len(hqm_dataframe)):
    hqm_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size/hqm_dataframe.loc[i, 'Stock Price'])

#print(hqm_dataframe)


# Formatting our excel output
writer = pd.ExcelWriter('high-momentum.xlsx', engine='xlsxwriter')
hqm_dataframe.to_excel(writer, sheet_name='Recommended', index=False)

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

percent_format = writer.book.add_format(
        {
            'num_format':'0.0%',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
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
    'A':['Ticker', string_format],
    'B':['Stock Price',dollar_format],
    'C':['Number of Shares to Buy',integer_format],
    'D':['One-Year Price Return',percent_format],
    'E':['One-Year Return Percentile',percent_format],
    'F':['Six-Month Price Return',percent_format],
    'G':['Six-Month Return Percentile',percent_format],
    'H':['Three-Month Price Return',percent_format],
    'I':['Three-Month Return Percentile',percent_format],
    'J':['One-Month Price Return',percent_format],
    'K':['One-Month Return Percentile',percent_format],
    'L':['hqm_score',percent_format]
}

for column in column_formats.keys():
    writer.sheets['Recommended'].set_column(f'{column}:{column}', 18, column_formats[column][1])
    writer.sheets['Recommended'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

writer.save()


