import sqlite3
import pandas as pd

def transform():
    """
    Transforms the raw service request data by parsing datetime columns, 
    extracting date parts, and computing additional features such as 
    time to close in hours. The transformed data is saved to a new table 
    in the SQLite database.
    """
    conn = sqlite3.connect('commonwealth_connect.db')
    
    # Define which columns to parse as datetime
    datetime_cols = [
        'ticket_created_date_time',
        'ticket_closed_date_time',
        'ticket_last_updated_date_time'
    ]
    
    # Load the raw service request data and parse datetime columns
    df = pd.read_sql(
        'SELECT * FROM service_requests',
        conn,
        parse_dates=datetime_cols
    )

    # For each datetime column, add derived date parts (e.g., year, month, weekday, hour)
    for col in datetime_cols:
        df[f'{col}_date']    = df[col].dt.date
        df[f'{col}_year']    = df[col].dt.year
        df[f'{col}_month']   = df[col].dt.month
        df[f'{col}_day']     = df[col].dt.day
        df[f'{col}_weekday'] = df[col].dt.day_name()
        df[f'{col}_hour']    = df[col].dt.hour

    # Create a string version of the created timestamp for tooltips
    df['created_str'] = df['ticket_created_date_time'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Compute time to close in hours (only where both timestamps exist)
    df['time_to_close_hours'] = (
        df['ticket_closed_date_time'] - df['ticket_created_date_time']
    ).dt.total_seconds() / 3600.0

    # Write the transformed data to a new table in the SQLite database
    df.to_sql('service_requests_transformed', conn, if_exists='replace', index=False)
    conn.close()
    print("Loaded transformed data into 'service_requests_transformed' table.")

if __name__ == '__main__':
    transform()
