import pandas as pd
import numpy as np

filepath = 'commodity_price.csv'

df = pd.read_csv(filepath)
df.rename(columns={
    'Min_x0020_Price': 'Min_Price',
    'Max_x0020_Price': 'Max_Price',
    'Modal_x0020_Price': 'Modal_Price'
}, inplace=True)


df['Arrival_Date'] = pd.to_datetime(df['Arrival_Date'], format='%d/%m/%Y')
categorical_cols = ['State', 'District', 'Market', 'Commodity', 'Variety', 'Grade']
for col in categorical_cols:
    df[col] = df[col].astype('category')    

price_cols = ['Min_Price', 'Max_Price', 'Modal_Price']
df[price_cols] = df[price_cols].replace(0, np.nan)

for col in price_cols:
    df[col] = df[col].fillna(
        df.groupby('Commodity')[col].transform('mean')
    )
df.dropna(subset=price_cols, inplace=True)
df.drop_duplicates(inplace=True)


Q1 = df['Modal_Price'].quantile(0.25)
Q3 = df['Modal_Price'].quantile(0.75)
IQR = Q3 - Q1   
upper_bound = Q3 + 1.5 * IQR
df.loc[df['Modal_Price'] > upper_bound, 'Modal_Price'] = upper_bound
df_cleaned = df

df_cleaned.to_csv('cleaned_commodity_price.csv', index=False)
