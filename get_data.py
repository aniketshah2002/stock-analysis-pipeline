import pandas as pd
import yfinance as yf 
import pandas_gbq      # Import pandas-gbq

# --- 1. CONFIGURATION ---
# (!! EDIT THESE 3 VARIABLES !!)

# 1. Paste your Google Cloud Project ID
PROJECT_ID = 'stock-dashboard-project-476115'

# 2. Set your BigQuery destination dataset
DATASET_ID = 'stock_analysis'

# 3. Set your BigQuery destination table
TABLE_ID = 'raw_stock_data'
# ------------------------------

# This is the full BigQuery table name
DESTINATION_TABLE = f"{DATASET_ID}.{TABLE_ID}"

# yfinance uses ".NS" for National Stock Exchange tickers
TICKERS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'SBIN.NS', 'BAJFINANCE.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS'
]

# --- 2. DATA FETCHING SCRIPT (with yfinance) ---

print(f"--- Starting Data Pipeline (using yfinance) ---")
print(f"Target BigQuery Table: {PROJECT_ID}.{DESTINATION_TABLE}")
print(f"Fetching 5 years of data for {len(TICKERS)} stocks...")

try:
    # 1. Download all data in one command
    # period="5y" gets 5 years. interval="1d" gets daily data.
    data = yf.download(TICKERS, period="5y", interval="1d")
    
    if data.empty:
        print("No data downloaded from yfinance. Check tickers.")
        exit()

    print("Download complete. Cleaning and formatting data...")

    # 2. Clean the data
    # The data downloads in a "multi-index" format. We need to "stack" it
    # to make it a normal, flat table for BigQuery.
    
    # We only care about these columns
    cleaned_data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    # 'stack()' moves the Tickers (e.g., 'TCS.NS') from columns into a row
    cleaned_data = cleaned_data.stack().reset_index()

    # 3. Rename columns to be BigQuery-friendly
    cleaned_data = cleaned_data.rename(columns={
        'Date': 'date',
        'level_1': 'symbol',  # 'level_1' is the new column with the ticker
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    # 4. Ensure date is in the correct format
    cleaned_data['date'] = pd.to_datetime(cleaned_data['date'])
    
    print(f"Cleaning complete. Uploading {len(cleaned_data)} rows to BigQuery...")

    # --- 3. UPLOADING TO BIGQUERY ---
    
    pandas_gbq.to_gbq(
        cleaned_data,
        destination_table=DESTINATION_TABLE,
        project_id=PROJECT_ID,
        if_exists='replace' # 'replace' deletes the old table and creates a new one
    )
    
    print("\n--- SUCCESS! ---")
    print(f"All data has been uploaded to {PROJECT_ID}.{DESTINATION_TABLE}")
    print("\nFinal DataFrame sample:")
    print(cleaned_data.head())

except Exception as e:
    print(f"\n--- AN ERROR OCCURRED ---")
    print(e)
    print("\n--- TROUBLESHOOTING ---")
    print("1. Did you run 'pip install yfinance'?")
    print("2. Are your PROJECT_ID and DATASET_ID correct?")
    print("3. Did you run 'gcloud auth application-default set-quota-project ...'?")