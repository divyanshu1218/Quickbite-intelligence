import datetime
from backend.data.database import DatabaseManager
from backend.utils.dates import resolve_period_last_n_months

def get_top_skus(top_n: int = 5, start_date=None, end_date=None):
    """
    Q4: Top N SKUs by quantity sold and top N SKUs by revenue.
    """
    if not start_date or not end_date:
        start_date, end_date, _ = resolve_period_last_n_months(3)
        
    query = """
        SELECT 
            p.SKU_ID as sku_id,
            p.SKU_NAME as sku_name,
            p.CATEGORY as category,
            p.VEG_NONVEG as veg_nonveg,
            COALESCE(SUM(od.QUANTITY), 0) as quantity_sold,
            COALESCE(SUM(od.LINE_NET_VALUE), 0.0) as revenue
        FROM Product_Master p
        JOIN Order_Details od ON od.SKU_ID = p.SKU_ID
        JOIN Orders o ON o.ORDER_ID = od.ORDER_ID
        WHERE CAST(o.ORDER_DATETIME AS DATE) >= ? AND CAST(o.ORDER_DATETIME AS DATE) <= ?
        GROUP BY p.SKU_ID, p.SKU_NAME, p.CATEGORY, p.VEG_NONVEG
    """
    all_skus = DatabaseManager.execute_query(query, [start_date, end_date])
    
    # Sort by quantity sold
    by_quantity = sorted(all_skus, key=lambda x: x["quantity_sold"], reverse=True)[:top_n]
    # Sort by revenue
    by_revenue = sorted(all_skus, key=lambda x: x["revenue"], reverse=True)[:top_n]
    
    def format_row(row, idx):
        return {
            "rank": idx + 1,
            "sku_id": row["sku_id"],
            "sku_name": row["sku_name"],
            "category": row["category"],
            "veg_nonveg": row["veg_nonveg"],
            "quantity_sold": int(row["quantity_sold"]),
            "revenue": round(row["revenue"], 2)
        }
        
    return {
        "top_by_quantity": [format_row(row, i) for i, row in enumerate(by_quantity)],
        "top_by_revenue": [format_row(row, i) for i, row in enumerate(by_revenue)]
    }
