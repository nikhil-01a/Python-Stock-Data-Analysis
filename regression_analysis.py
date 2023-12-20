import wrds
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Connect to WRDS
db = wrds.Connection()

# Variables
stock_symbol = 'AAPL'
index_gvkeyx = '165157' 
start_date = '2000-01-01'
end_date = '2020-12-31'

# Querying the monthly stock and index prices
apple_query = f"""SELECT date, prc as price
                  FROM crsp.msf
                  WHERE permno in (
                      SELECT permno 
                      FROM crsp.msenames 
                      WHERE ticker = '{stock_symbol}'
                  )
                  AND date >= '{start_date}' AND date <= '{end_date}'"""

gspc_query = f"""SELECT datadate as date, prccm as price
                 FROM comp.idx_mth
                 WHERE gvkeyx = '{index_gvkeyx}'
                 AND datadate >= '{start_date}' AND datadate <= '{end_date}'"""

apple_data = db.raw_sql(apple_query)
gspc_data = db.raw_sql(gspc_query)

# Close the WRDS connection
db.close()

# Ensure the dates are in datetime format
apple_data['date'] = pd.to_datetime(apple_data['date'])
gspc_data['date'] = pd.to_datetime(gspc_data['date'])

# Merge the datasets on date
merged_data = pd.merge(apple_data, gspc_data, on='date', suffixes=('_apple', '_gspc'))

# Defining independant and dependant variables
X = merged_data['price_apple'] # Independant
y = merged_data['price_gspc'] # Dependant price_gspc 

# Add a constant to the independent variable
X = sm.add_constant(X)

# Perform the regression
model = sm.OLS(y, X).fit()

# Print out the statistics
print(model.summary())

# Plot the regression
plt.scatter(X['price_apple'], y)  
plt.plot(X['price_apple'], model.predict(X), color='red')  
plt.title('Regression of  GSPC Monthly Closing Price on Apple Monthly Closing Price')
plt.xlabel('AAPL Closing Price') 
plt.ylabel('GSPC Closing Price')
plt.show()