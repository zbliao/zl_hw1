# PPHA 30538
# Fall 2022
# Homework 1

# Zibing Liao
# zbliao
 
# Due date: Oct 10


#############


# Question 1: Load and merge the data into a panel dataframe, with the columns: "state", "year", 
# and one for each of the 10 industries.  Every state-year combination should 
# uniquely identify a row.  No more and no less than 12 columns should remain.  
# Do any necessary cleaning for the data to be easily usable.

import pandas as pd
import os
from pandas.api.types import is_numeric_dtype
# Import files
base_path = r'/Users/zibingliao/Documents/GitHub/zl_hw1'
total_data = 'SAEMP25N total.csv'
industry_data = 'SAEMP25N by industry.csv'
df_total = pd.read_csv(os.path.join(base_path, total_data), skiprows=4, skipinitialspace = True)
df_industry = pd.read_csv(os.path.join(base_path, industry_data), skiprows=4, skipinitialspace = True)

# Clean and format total file
df_total = df_total.rename(columns={'GeoName':'state'}).drop(columns=['GeoFips']).dropna().replace('(T)', 'NaN').replace('(D)', 'NaN')
df_total_reshaped = df_total.melt(id_vars=['state'])
#df_total = df_total.drop(columns=['GeoFips']).set_index('state').dropna()

# Clean and format industry file
df_industry = df_industry.rename(columns={'GeoName':'state'}).drop(columns=['GeoFips','LineCode']).dropna(0).replace('(T)', 'NaN').replace('(D)', 'NaN')
df_industry_reshaped = df_industry.melt(id_vars=['state','Description'])
df_industry_reshaped['Description'] = df_industry_reshaped['Description'].str.strip()
#df_industry = df_industry.drop(columns=['GeoFips','LineCode']).dropna(0).set_index('state')
# df_industry.stack()

# duplicate the dataframe for percentage calculation
df_reshaped_copy = df_total_reshaped

# merge two datasets and rename columns
df_reshaped_copy = df_reshaped_copy.merge(df_industry_reshaped, on = ['state','variable'], how = 'outer')
df_reshaped_copy = df_reshaped_copy.rename(columns={
    "variable": "year",
    "value_x": "total employment", 
    "value_y": "employment by industry",
    "Description":"industry"})

# calculate percentage employment for the state-year industry
df_reshaped_copy['employment by industry'] = pd.to_numeric(df_reshaped_copy['employment by industry'],errors='coerce')
df_reshaped_copy['percentage employment'] = df_reshaped_copy["employment by industry"].astype(float) / df_reshaped_copy['total employment'].astype(float)

# drop unnecessary columns
df_reshaped_cleaned = df_reshaped_copy.drop(columns=['employment by industry', 'total employment'])

# reshape the dataframe
df_reshaped_cleaned = df_reshaped_cleaned.set_index(['state','year','industry'])
df_final = df_reshaped_cleaned.unstack('industry')
#df_final_clean = df_final.reset_index(['state','year'])
df_final.columns=df_final.columns.droplevel(0)

# save as csv file
df_final.to_csv('data.csv')


# Question 2
# a. Find the states with the top five share of manufacturing employment in the year 2000, 
# then show how their share of employment in manufacturing changed between 2000 and 2017.  
# Use a basic plot to display the information.
df_final_top5_manu_2000 = df_final.sort_values(by=['year']).sort_values(by=['Manufacturing'],ascending=False).head(5)
df_final_top5_manu = df_final['Manufacturing'].loc[["Indiana",'Wisconsin','Michigan','Arkansas','North Carolina']]
df_final_top5_manu = df_final_top5_manu.unstack()
df_final_top5_manu['change'] = df_final_top5_manu['2017'] - df_final_top5_manu['2000']
df_final_top5_manu = df_final_top5_manu.reset_index()
df_final_top5_manu.plot(x='state',y='change',kind = 'scatter')

# b. Show which five states have the highest concentration of employment in a any 
# single industry in each of 2000 and 2017, and what those industries are.
df_final_2000 = df_final.sort_values(by=['year']).iloc[:51] 
df_final_2017 = df_final.sort_values(by=['year']).iloc[51:] 
top5_concentration_2000 = df_final_2000.nlargest(5, columns = 
        ['Arts, entertainment, and recreation',
         'Educational services',
         'Farm employment',
         'Finance and insurance',
         'Government and government enterprises',
         'Health care and social assistance',
         'Information',
         'Manufacturing',
         'Mining, quarrying, and oil and gas extraction',
         'Retail trade'], keep='all')
top5_concentration_2000

####################################
dfs = []

for col in df_final_2000:
    top_values = []
    if is_numeric_dtype(df_final_2000[col]):
        top_values = df_final_2000[col].nlargest(n=5)
        dfs.append(pd.DataFrame({col: top_values}).reset_index(drop=True))
pd.concat(dfs, axis=1)