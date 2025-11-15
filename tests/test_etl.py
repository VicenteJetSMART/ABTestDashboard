import pandas as pd
from src.etl import transform_data

def test_transform_data():
    df = pd.DataFrame({"a": [1, None, 3]})
    df_clean = transform_data(df)
    assert df_clean.isnull().sum().sum() == 0
