from src.db import get_redshift_connection
from src.etl import extract_data, transform_data
from src.excel_io import export_to_excel

if __name__ == "__main__":
    conn = get_redshift_connection()
    df_raw = extract_data(conn)
    df_clean = transform_data(df_raw)
    export_to_excel(df_clean, "./outputs/cleaned_data.xlsx")
