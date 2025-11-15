def calculate_kpis(df):
    return {
        "total_rows": len(df),
        "null_values": df.isnull().sum().to_dict()
    }
