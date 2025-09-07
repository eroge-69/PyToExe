import pyodbc
import pandas as pd
import os
from datetime import datetime
import requests

# ========================
OUTPUT_DIR = "exports"
# ========================

def connect_odbc(dsn_name):
    try:
        conn = pyodbc.connect(f"DSN={dsn_name};")
        print("✅ Connected to Tally ODBC successfully.")
        return conn
    except Exception as e:
        print("❌ Error connecting to Tally ODBC:", e)
        return None

def fetch_outstanding_odbc(conn):
    try:
        sql = """
        SELECT $Name AS LedgerName,
               $ClosingBalance AS Outstanding
        FROM Ledger
        """
        return pd.read_sql(sql, conn)
    except Exception as e:
        print("❌ Error fetching outstanding (ODBC):", e)
        return pd.DataFrame()

def fetch_ledger_odbc(conn):
    try:
        sql = """
        SELECT $Name AS LedgerName,
               $Parent AS GroupName,
               $ClosingBalance AS Balance
        FROM Ledger
        """
        return pd.read_sql(sql, conn)
    except Exception as e:
        print("❌ Error fetching ledger (ODBC):", e)
        return pd.DataFrame()

def save_to_csv_excel(df, report_name):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = os.path.join(OUTPUT_DIR, f"{report_name}_{ts}.csv")
    xlsx_file = os.path.join(OUTPUT_DIR, f"{report_name}_{ts}.xlsx")
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_file, index=False)
    print(f"✅ Exported {report_name} to:\n   {csv_file}\n   {xlsx_file}")

def fetch_api(port):
    try:
        url = f"http://localhost:{port}"
        headers = {"Content-Type": "application/xml"}
        xml_req = """
        <ENVELOPE>
            <HEADER>
                <TALLYREQUEST>Export Data</TALLYREQUEST>
            </HEADER>
            <BODY>
                <EXPORTDATA>
                    <REQUESTDESC>
                        <REPORTNAME>Outstanding</REPORTNAME>
                    </REQUESTDESC>
                </EXPORTDATA>
            </BODY>
        </ENVELOPE>
        """
        res = requests.post(url, data=xml_req.encode("utf-8"), headers=headers)
        if res.status_code == 200:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            file = os.path.join(OUTPUT_DIR, f"outstanding_api_{ts}.xml")
            with open(file, "wb") as f:
                f.write(res.content)
            print(f"✅ Exported Outstanding via API to: {file}")
        else:
            print("❌ API Error:", res.status_code)
    except Exception as e:
        print("❌ Error fetching via API:", e)

def main():
    print("=== Tally Extractor ===")
    mode = input("Choose mode: (1=ODBC, 2=API): ").strip()

    if mode == "1":
        dsn = input("Enter ODBC DSN name (default=TALLYODBC64): ").strip() or "TALLYODBC64"
        conn = connect_odbc(dsn)
        if not conn:
            return
        print("1 = Outstanding, 2 = Ledger, 3 = All Reports")
        choice = input("Select report: ").strip()

        if choice == "1":
            df = fetch_outstanding_odbc(conn)
            if not df.empty:
                save_to_csv_excel(df, "outstanding")
        elif choice == "2":
            df = fetch_ledger_odbc(conn)
            if not df.empty:
                save_to_csv_excel(df, "ledger")
        elif choice == "3":
            df1 = fetch_outstanding_odbc(conn)
            if not df1.empty:
                save_to_csv_excel(df1, "outstanding")
            df2 = fetch_ledger_odbc(conn)
            if not df2.empty:
                save_to_csv_excel(df2, "ledger")
        else:
            print("⚠️ Invalid choice")

        conn.close()

    elif mode == "2":
        port = input("Enter Tally API port (default=9000): ").strip() or "9000"
        fetch_api(port)

    else:
        print("⚠️ Invalid mode selected")

    print("✅ Task completed.")

if __name__ == "__main__":
    main()
