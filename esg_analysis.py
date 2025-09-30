import pandas as pd
import sqlite3
import yfinance as yf
import os

# ------------------------------
# 1. Load ESG scores
# ------------------------------
esg_file = "/Users/gharya/Downloads/esg_scores.csv"
if not os.path.exists(esg_file):
    raise FileNotFoundError(f"File not found: {esg_file}")

esg_df = pd.read_csv(esg_file)
esg_df.columns = esg_df.columns.str.strip()
print("ESG Columns:", esg_df.columns)
print(esg_df.head())

# ------------------------------
# 2. Optional: Pull Yahoo Finance data
# ------------------------------
def get_yahoo_data(ticker):
    try:
        data = yf.Ticker(ticker).info
        market_cap = data.get('marketCap', None)
        beta = data.get('beta', None)
        return pd.Series([market_cap, beta])
    except Exception:
        return pd.Series([None, None])

esg_df[['market_cap', 'beta']] = esg_df['ticker'].apply(get_yahoo_data)
print("\nESG + Yahoo Finance data:")
print(esg_df.head())

# ------------------------------
# 3. Optional: Pull risk_score from your DB
# ------------------------------
db_file = "/Users/gharya/Downloads/analytics.db"  # or investment.db
if os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    # Check available tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print("\nTables in database:", tables)

    # Using risk_score from insurance_shipping_analysis as default proxy
    if 'insurance_shipping_analysis' in tables:
        credit_df = pd.read_sql("SELECT risk_score FROM insurance_shipping_analysis", conn)
        if not credit_df.empty:
            # Use the mean risk_score as a simple default
            default_credit = credit_df['risk_score'].mean()
        else:
            default_credit = 50
    else:
        default_credit = 50
    conn.close()
else:
    default_credit = 50

# ------------------------------
# 4. Add credit_rating and calculate investment_score
# ------------------------------
esg_df['credit_rating'] = default_credit
esg_df['investment_score'] = esg_df['esg_score'] * esg_df['credit_rating'] / 5

# ------------------------------
# 5. Save updated CSV
# ------------------------------
output_file = "/Users/gharya/Downloads/esg_analysis_with_scores.csv"
esg_df.to_csv(output_file, index=False)
print(f"\nUpdated DataFrame saved to {output_file}")
print(esg_df.head())

