import pandas as pd
import numpy as np

df = pd.read_csv('Dataset/mandaue_data_clean.csv')

print("Data shape:", df.shape)
print("\nColumn types:")
print(df.dtypes)

print("\n\nMissing values:")
print(df.isnull().sum())

print("\n\nNumeric columns:")
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
print(list(numeric_cols))
