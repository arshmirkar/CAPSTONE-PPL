## data cleaning
# 1--Standardize the Format
->Rename Columns: The price columns contain a URL-encoded space (_x0020_). Rename Min_x0020_Price, Max_x0020_Price, and Modal_x0020_Price to Min_Price, Max_Price, and Modal_Price for readability.
->Type Conversion: The Arrival_Date column is currently stored as a string (object). Convert this to a proper Pandas datetime object.

# 2--Handle Outliers
->Identify: The 75th percentile for max prices is ₹4,880, but the maximum value in the dataset spikes to ₹90,000.
->Action & Justification: You need to detect these extreme values. Calculate the Interquartile Range (IQR) or use Z-scores to isolate them. In your report or code comments, justify whether you are keeping them (e.g., classifying them as luxury/high-value commodities that genuinely cost that much) or capping/removing them (if they are data entry errors).

# 3--Handle Invalid and Missing Data
->Address Zeroes: While the dataset does not contain standard NaN values, there are exactly 9 rows where both the Minimum and Maximum prices are 0. A commodity price of 0 is invalid.
->Action & Justification: You can either drop these 9 rows (justifying that they make up a statistically insignificant portion of the 2,733 total rows) or impute them by using a groupby operation to fill the 0s with the average price of that specific Commodity in that specific State/District. Using groupby here will specifically check off a requirement for the highest rubric tier.

# 4--Demonstrate Efficient Operations
To meet the rubric's efficiency requirements, strictly avoid for-loops when modifying the dataframe. Use:   
->Vectorized operations for math (e.g., df['Price_Range'] = df['Max_Price'] - df['Min_Price']).
->loc/iloc for filtering and outlier extraction instead of chained indexing (e.g., df.loc[df['Max_Price'] > upper_bound]).
