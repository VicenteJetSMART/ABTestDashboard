import pandas as pd

def extract_data(conn):
    query = "SELECT * FROM your_table LIMIT 100"
    return pd.read_sql(query, conn)

def transform_data(df):
    # Example transformation
    df = df.dropna()
    return df
