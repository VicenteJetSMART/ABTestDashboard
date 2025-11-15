import pandas as pd

def export_to_excel(df, path):
    df.to_excel(path, index=False)

def read_from_excel(path):
    return pd.read_excel(path)
