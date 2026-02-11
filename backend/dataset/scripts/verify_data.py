import pandas as pd
import glob
import os

print("Verifying data files...")
files = glob.glob('data/*.csv')
for f in files:
    try:
        df = pd.read_csv(f)
        if not df.empty:
            start = df['datetime'].iloc[0]
            end = df['datetime'].iloc[-1]
            print(f"{os.path.basename(f)}: {len(df)} rows, from {start} to {end}")
        else:
            print(f"{os.path.basename(f)}: EMPTY")
    except Exception as e:
        print(f"Error reading {f}: {e}")
