
import pandas as pd

try:
    df = pd.read_csv("Pharmacies.csv", low_memory=False)
    print(df.columns.tolist())
except Exception as e:
    print(e)
