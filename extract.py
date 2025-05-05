import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

# Load your Socrata App Token from .env
load_dotenv()
TOKEN = os.getenv("SODA_APP_TOKEN")

# CSV endpoint and page size
CSV_URL = "https://data.cambridgema.gov/resource/2z9k-mv9g.csv"
PAGE_SIZE = 50000

def extract_all_csv():
    """
    Extracts service request data from the Socrata CSV endpoint in paginated chunks.
    Combines all chunks into a single DataFrame and loads the data into a SQLite table.

    Steps:
    1. Paginate through the CSV endpoint using the Socrata App Token.
    2. Fetch data in chunks of size defined by PAGE_SIZE.
    3. Concatenate all chunks into a single DataFrame.
    4. Write the combined data to the 'service_requests' table in the SQLite database.
    """
    chunks = []
    offset = 0

    while True:
        # Build the paginated CSV URL
        url = (
            f"{CSV_URL}"
            f"?$$app_token={TOKEN}"
            f"&$limit={PAGE_SIZE}"
            f"&$offset={offset}"
        )
        # Read current page
        chunk = pd.read_csv(url)
        if chunk.empty:
            break

        print(f" → Fetched {len(chunk)} rows (offset {offset})")
        chunks.append(chunk)
        offset += PAGE_SIZE

    # Concatenate all pages
    df = pd.concat(chunks, ignore_index=True)
    print(f"Total records fetched: {len(df)}")

    # Write to SQLite
    conn = sqlite3.connect("commonwealth_connect.db")
    df.to_sql("service_requests", conn, if_exists="replace", index=False)
    conn.close()
    print("Loaded all records into 'service_requests' table.")

if __name__ == "__main__":
    extract_all_csv()
