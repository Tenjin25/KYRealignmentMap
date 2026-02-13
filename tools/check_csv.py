import pandas as pd
import os

csv_path = 'data/20121106__ky__general__county.csv'
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print(df.head(20))
    print("\nColumns:", df.columns.tolist())
else:
    print("CSV not found")
