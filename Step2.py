


import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
# Read the data


# Load the datasets
call_log = pd.read_csv('call_log_top_picks_new.csv')
price_data = pd.read_csv('price_data_pivot_output.csv')

# Convert dates to datetime format
call_log['Date'] = pd.to_datetime(call_log['Date'])
price_data['Date'] = pd.to_datetime(price_data['Date'])
print(call_log['Price'].dtype)

# sys.exit()

# Clean price data in call_log
# call_log['Price'] = call_log['Price'].str.replace(',', '').astype(float)

# Clean price data in call_log
call_log['Price'] = call_log['Price'].astype(float)

# Create a dictionary to track buy/sell dates for each stock
stock_transactions = {}

for _, row in call_log.iterrows():
    date = row['Date']
    stock = row['Stock']
    reco = row['Reco']
    
    if stock not in stock_transactions:
        stock_transactions[stock] = {'buys': [], 'sells': []}
    
    if reco.upper() == 'BUY':
        stock_transactions[stock]['buys'].append(date)
    elif reco.upper() == 'EXIT':
        stock_transactions[stock]['sells'].append(date)

print(stock_transactions)
# Create a new dataframe with the same structure as the price pivot data
timeline_df = price_data.copy()
# Set the date as index
timeline_df.set_index('Date', inplace=True)

# Replace price values with empty strings
for col in timeline_df.columns:
    timeline_df[col] = ''



# Fill in the dataframe with stock names during their active periods
for stock, transactions in stock_transactions.items():
    buys = sorted(transactions['buys'])
    sells = sorted(transactions['sells'])
    
    # Filter out sell dates that occur before the first buy date
    if buys:
        first_buy_date = min(buys)
        sells = [sell_date for sell_date in sells if sell_date >= first_buy_date]
    
    # Handle exit dates before the first buy date
    if sells and (not buys or min(sells) < min(buys)):
        for sell_date in [sell_date for sell_date in sells if not buys or sell_date < min(buys)]:
            # Fill the date range from the start of the timeline to sell_date - 1
            date_mask = (timeline_df.index < sell_date)
            if stock in timeline_df.columns:
                timeline_df.loc[date_mask, stock] = stock
        # Remove these sell dates from the list as they are already handled
        sells = [sell_date for sell_date in sells if not (not buys or sell_date < min(buys))]
    
    # Match each buy with its corresponding sell
    matched_pairs = []
    while buys and sells:
        buy_date = buys.pop(0)
        sell_date = next((sell for sell in sells if sell >= buy_date), pd.Timestamp.max)
        matched_pairs.append((buy_date, sell_date))
        if sell_date in sells:
            sells.remove(sell_date)
    
    # Handle remaining buys as open positions
    for buy_date in buys:
        matched_pairs.append((buy_date, pd.Timestamp.max))
    
    # Fill the timeline dataframe based on matched pairs
    for buy_date, sell_date in matched_pairs:
        # Fill the date range from buy to sell-1
        date_mask = (timeline_df.index >= buy_date) & (timeline_df.index < sell_date)
        
        # Only fill if the stock is a column in our dataframe
        if stock in timeline_df.columns:
            timeline_df.loc[date_mask, stock] = stock

# Reset index to make Date a column again for better display
timeline_df.reset_index(inplace=True)

# Add count of active days for each stock
timeline_df['Active Days'] = timeline_df.apply(lambda row: sum(row[1:] != ''), axis=1)

timeline_df.to_csv('timeline_df.csv', index=False)
