import pandas as pd
from sqlalchemy import create_engine
import pymysql

# Configuration
excel_file = 'absensi.xls'  # Replace with your Excel file path
db_user = 'admininfo'       # Replace with your MySQL username
db_password = 'infoadmin'   # Replace with your MySQL password
db_host = '192.168.4.30'    # Replace with your MySQL host (e.g., 'localhost' or IP)
db_name = 'infodisplay'     # Database name
table_name = 'absence_sby'  # Table name

# Read Excel data (columns 1-14 starting from row 3)
df = pd.read_excel(
    excel_file,
    header=None,              # No header row in Excel
    skiprows=2,               # Skip first 2 rows (start at row 3)
    usecols="A:N",            # Columns 1-14 (A to N)
    names=['emp_id', 'emp_name', 'atd_date','atd_day','shift','shift_time_in','shift_time_out','roster','actual_in','actual_out','actual_in_ori','actual_out_ori','atd_next_day','atd_in']  # Your 14 column names
)

# Create database connection
engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}')

# Transfer data to MySQL
# The 'replace' argument will drop the table and recreate it,
# effectively clearing old data before inserting new data.
df.to_sql(
    name=table_name,
    con=engine,
    if_exists='replace',        # Use 'replace' to clear and insert
    index=False,                # Don't write DataFrame index
    chunksize=1000              # Insert in batches of 1000 rows
)

print(f"Successfully cleared and transferred {len(df)} rows to {table_name}")
