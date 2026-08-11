import os
import pandas as pd
import duckdb

def ingest():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(project_root, "QSR_Agentic_Insights_Dataset.xlsx")
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, "qsr.duckdb")

    if os.path.exists(db_path):
        os.remove(db_path)

    print(f"Reading Excel file: {excel_path}...")
    xl = pd.ExcelFile(excel_path)
    conn = duckdb.connect(db_path)

    sheets = ['Store_Master', 'Product_Master', 'Customer_Master', 'Promotions', 'Calendar', 'Orders', 'Order_Details']

    for sheet in sheets:
        print(f"Ingesting sheet: {sheet}...")
        df = xl.parse(sheet)
        
        # Convert date columns appropriately if needed
        for col in df.columns:
            if 'DATE' in col.upper() or 'TIME' in col.upper():
                df[col] = pd.to_datetime(df[col])
        
        # Save to DuckDB table
        table_name = sheet
        conn.register(f"temp_{table_name}", df)
        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_{table_name}")
        conn.unregister(f"temp_{table_name}")

    # Add indexes or helper views if needed
    print("Creating views and indexes in DuckDB...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_store ON Orders(STORE_ID);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON Orders(ORDER_DATETIME);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_order_details_order ON Order_Details(ORDER_ID);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_order_details_sku ON Order_Details(SKU_ID);")

    # Verify counts
    tables = conn.execute("SHOW TABLES;").fetchall()
    print("\nDuckDB Tables Created:")
    for t in tables:
        tbl = t[0]
        cnt = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f" - {tbl}: {cnt} rows")

    conn.close()
    print(f"\nIngestion successfully completed! Database created at: {db_path}")

if __name__ == "__main__":
    ingest()
