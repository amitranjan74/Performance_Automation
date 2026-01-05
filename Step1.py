

import pandas as pd



# Importing price_data
price_data = pd.read_csv('price_data.csv')
# Importing call_log_top_picks data
call_log_top_picks = pd.read_excel('Call_Log_Top_Picks_copy.xlsx', sheet_name= 'Sheet1')
# Orderting the columns as per Manual_file_stock_order.csv
stock_order = pd.read_excel('Manual_file_stock_order.xlsx', sheet_name= 'Sheet1')

price_data.rename(columns={'CO_NAME': 'co_name', '[Date': 'Date', '[Close Price': 'Price'}, inplace=True)
price_data['Date'] = pd.to_datetime(price_data['Date'], format='%m/%d/%Y')

# Create Date as index for the DataFrame
price_data.set_index('Date', inplace=True)

# Droping Capitaline Code column from the Dataframe
price_data.drop('CAPITALINE CODE', axis=1, inplace=True)


price_data_pivot = price_data.pivot(columns='co_name', values='Price')



call_log_top_picks = call_log_top_picks[['Date', 'Stock', 'Reco', 'Price']]

# Ensure the Date column in call_log_top_picks is in datetime format
call_log_top_picks['Date'] = pd.to_datetime(call_log_top_picks['Date'], format='%d-%b-%y')

call_log_top_picks.to_csv('call_log_top_picks_new.csv', index=False)

# Iterate through the rows of price_data_pivot
for date in price_data_pivot.index:
    if date in call_log_top_picks['Date'].values:
        # Filter rows in call_log_top_picks for the matching date
        matching_rows = call_log_top_picks[call_log_top_picks['Date'] == date]
        for stock in price_data_pivot.columns:
            if stock in matching_rows['Stock'].values:
                # Get the price from call_log_top_picks
                new_price = matching_rows[matching_rows['Stock'] == stock]['Price'].values[0]
                # Update the price in price_data_pivot
                price_data_pivot.loc[date, stock] = new_price



stock_order = stock_order['co_name'].tolist()
price_data_pivot = price_data_pivot[stock_order]  
price_data_pivot.to_csv('price_data_pivot_output.csv', index=True)