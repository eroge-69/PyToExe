Attendance 
import pyodbc
import json
import requests
from datetime import datetime

# Database connection details
DB_CONFIG = {
    "Driver": "{SQL Server}",
    "Server": "DRIFTACADEMY\\SQLEXPRESS",
    "Database": "ONtime_Att",
    "UID": "sa",
    "PWD": "Soceslive@0571",
}

# API endpoint details
API_URL = "https://portal.driftacademy.in/api/attendance/api-store"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def fetch_data():
    """
    Fetch attendance data from the database.
    """
    try:
        # Connect to SQL Server
        conn = pyodbc.connect(
            f"Driver={DB_CONFIG['Driver']};"
            f"Server={DB_CONFIG['Server']};"
            f"Database={DB_CONFIG['Database']};"
            f"UID={DB_CONFIG['UID']};"
            f"PWD={DB_CONFIG['PWD']};"
        )
        cursor = conn.cursor()

        # Query to fetch attendance data
        query = """
        SELECT Emp_id, Card_Number, Dev_Id, Att_PunchRecDate 
        FROM dbo.Tran_DeviceAttRec
        WHERE status IS NULL -- Process only new records
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Close the connection
        conn.close()

        return rows

    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return []

def prepare_payload(rows):
    """
    Prepare data for API payload.
    """
    payload = []
    institution_id = 1  # Replace with your institution ID

    for row in rows:
        emp_id, card_number, dev_id, punch_date = row

        record = {
            "institution_id": institution_id,
            "student_ids": [emp_id],  # Assuming Emp_id corresponds to a student ID
            "time_of_marking": punch_date.strftime("%Y-%m-%d %H:%M:%S"),
            "date_of_attendance": punch_date.strftime("%Y-%m-%d"),
        }
        payload.append(record)
    
    return payload

def export_to_api(payload):
    """
    Send attendance data to the API.
    """
    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        response.raise_for_status()
        print("Data successfully sent to API.")
        print("Response:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"API error: {e}")

def update_database_status(rows):
    """
    Update the database to mark processed records.
    """
    try:
        # Reconnect to the database
        conn = pyodbc.connect(
            f"Driver={DB_CONFIG['Driver']};"
            f"Server={DB_CONFIG['Server']};"
            f"Database={DB_CONFIG['Database']};"
            f"UID={DB_CONFIG['UID']};"
            f"PWD={DB_CONFIG['PWD']};"
        )
        cursor = conn.cursor()

        # Update the status for each processed record
        for row in rows:
            card_number = row[1]
            update_query = """
            UPDATE dbo.Tran_DeviceAttRec
            SET status = 1
            WHERE Card_Number = ?
            """
            cursor.execute(update_query, (card_number,))

        conn.commit()
        conn.close()
        print("Database status updated successfully.")

    except pyodbc.Error as e:
        print(f"Database update error: {e}")

def main():
    # Step 1: Fetch data from the database
    rows = fetch_data()
    if not rows:
        print("No new records to process.")
        return

    # Step 2: Prepare the API payload
    payload = prepare_payload(rows)

    # Step 3: Export data to API
    export_to_api(payload)

    # Step 4: Update the database status for processed records
    update_database_status(rows)

if _name_ == "_main_":
    main()