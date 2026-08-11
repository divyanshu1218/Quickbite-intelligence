import datetime
from dateutil.relativedelta import relativedelta
from backend.data.database import DatabaseManager

def get_latest_order_date() -> datetime.datetime:
    """
    Queries DuckDB to find the maximum order datetime.
    """
    query = "SELECT MAX(ORDER_DATETIME) as max_date FROM Orders;"
    res = DatabaseManager.execute_query(query)
    if res and res[0]['max_date']:
        # Could be string or datetime depending on DuckDB conversion
        val = res[0]['max_date']
        if isinstance(val, str):
            return datetime.datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
        elif isinstance(val, datetime.datetime):
            return val
        else:
            # Handle pandas/numpy timestamp objects
            return datetime.datetime.combine(val.date(), val.time())
    # Fallback default if DB is empty
    return datetime.datetime(2026, 7, 31, 23, 59, 59)

def resolve_period_last_n_months(n_months: int = 3):
    """
    Returns (start_date, end_date, label) for the last N calendar months.
    For n=3 and latest order in July 2026:
    Returns (2026-05-01, 2026-07-31, "May–July 2026")
    """
    latest_dt = get_latest_order_date()
    
    # End date is the end of the day on latest_dt
    end_date = latest_dt.date()
    
    # Start date is the first day of the month (latest_dt - (n_months - 1) months)
    target_start_dt = latest_dt - relativedelta(months=n_months - 1)
    start_date = datetime.date(target_start_dt.year, target_start_dt.month, 1)
    
    # Format the label
    months_map = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }
    
    start_lbl = f"{months_map[start_date.month]} {start_date.year}"
    end_lbl = f"{months_map[end_date.month]} {end_date.year}"
    
    # If the years are same, abbreviate the second or group them
    if start_date.year == end_date.year:
        label = f"{months_map[start_date.month]}–{months_map[end_date.month]} {start_date.year}"
    else:
        label = f"{start_lbl} – {end_lbl}"
        
    return start_date, end_date, label

def get_previous_period(start_date: datetime.date, end_date: datetime.date):
    """
    Finds the adjacent past period of equal duration.
    E.g. if current is 2026-05-01 to 2026-07-31 (92 days),
    previous is 2026-02-01 to 2026-04-30 (89 days).
    We can shift start/end by the number of months.
    """
    delta_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
    prev_start = start_date - relativedelta(months=delta_months)
    prev_end = start_date - relativedelta(days=1)
    return prev_start, prev_end
