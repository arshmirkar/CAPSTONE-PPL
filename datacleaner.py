import pandas as pd
import numpy as np

def load_and_standardize(filepath):
    """Loads the dataset and standardizes column names."""
    df = pd.read_csv(filepath)
    
    # Rename columns to remove URL-encoded spaces
    df.rename(columns={
        'Min_x0020_Price': 'Min_Price',
        'Max_x0020_Price': 'Max_Price',
        'Modal_x0020_Price': 'Modal_Price'
    }, inplace=True)
    
    return df

def optimize_datatypes(df):
    """Converts datatypes for memory efficiency and time-series analysis."""
    # Convert string dates to datetime objects
    df['Arrival_Date'] = pd.to_datetime(df['Arrival_Date'], format='%d/%m/%Y')
    
    # Convert categorical columns to 'category' type for memory efficiency
    categorical_cols = ['State', 'District', 'Market', 'Commodity', 'Variety', 'Grade']
    for col in categorical_cols:
        df[col] = df[col].astype('category')
        
    return df

def handle_missing_and_invalid(df):
    """Handles invalid 0 prices using vectorized grouping operations."""
    # Replace invalid 0 prices with NaN to utilize pandas imputation methods
    price_cols = ['Min_Price', 'Max_Price', 'Modal_Price']
    df[price_cols] = df[price_cols].replace(0, np.nan)
    
    # Impute missing values with the mean price of that specific Commodity
    # This uses efficient groupby and transform instead of slow loops
    for col in price_cols:
        df[col] = df[col].fillna(
            df.groupby('Commodity')[col].transform('mean')
        )
        
    # Drop any remaining NaNs (e.g., if a commodity only had 0s)
    df.dropna(subset=price_cols, inplace=True)
    
    # Remove exact duplicate rows if any exist
    df.drop_duplicates(inplace=True)
    
    return df

def handle_outliers_iqr(df):
    """Caps extreme outliers using the Interquartile Range (IQR) method."""
    # We will cap outliers in Modal_Price to retain the data but reduce skew
    Q1 = df['Modal_Price'].quantile(0.25)
    Q3 = df['Modal_Price'].quantile(0.75)
    IQR = Q3 - Q1
    
    upper_bound = Q3 + 1.5 * IQR
    
    # Use .loc for efficient, vectorized assignment instead of chained indexing
    df.loc[df['Modal_Price'] > upper_bound, 'Modal_Price'] = upper_bound
    
    return df

def clean_commodity_data(filepath):
    """Main execution function demonstrating modularity."""
    print("Starting data pipeline...")
    df = load_and_standardize(filepath)
    df = optimize_datatypes(df)
    df = handle_missing_and_invalid(df)
    df_cleaned = handle_outliers_iqr(df)
    
    print(f"Cleaning complete. Final dataset shape: {df_cleaned.shape}")
    return df_cleaned

# Execute the pipeline
cleaned_data = clean_commodity_data('commodity_price.csv')

# Save the cleaned dataset to a new file
cleaned_data.to_csv('cleaned_commodity_price.csv', index=False)
print("Saved successfully as 'cleaned_commodity_price.csv'")