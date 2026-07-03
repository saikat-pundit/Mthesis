import pandas as pd
import os

filename = "data/yield_history.csv"
if not os.path.exists(filename):
    print("❌ CSV file not found.")
    exit(1)

df = pd.read_csv(filename)

# Add new columns with None (if they don't exist)
new_columns = ["DXY", "FEDFUNDS", "M2SL", "WALCL"]
for col in new_columns:
    if col not in df.columns:
        df[col] = None

# Save back to CSV
df.to_csv(filename, index=False)
print(f"✅ Added columns: {', '.join(new_columns)}")
print(f"📊 Total rows: {len(df)}")
