import tkinter as tk
from tkinter import messagebox
import pyodbc
import json
import os

CONFIG_FILE = "db_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                entry_server.insert(0, config.get("server", ""))
                entry_db.insert(0, config.get("database", ""))
                entry_user.insert(0, config.get("username", ""))
        except:
            pass

def save_config():
    config = {
        "server": entry_server.get(),
        "database": entry_db.get(),
        "username": entry_user.get()
    }
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        messagebox.showinfo("Saved", "Connection settings saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save config: {e}")

def get_connection():
    server = entry_server.get()
    database = entry_db.get()
    username = entry_user.get()
    password = entry_pass.get()

    if username and password:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
        )
    else:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        )

    return pyodbc.connect(conn_str)

def test_connection():
    try:
        conn = get_connection()
        conn.close()
        messagebox.showinfo("Success", "Database connection successful!")
    except Exception as e:
        messagebox.showerror("Connection Failed", str(e))

def run_re_admit():
    database = entry_db.get()
    doc_code = entry_doc.get()
    rn = entry_rn.get()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = f"""
        DECLARE @WXADMDATE datetime2;
        DECLARE @WXADMNO varchar(255);
        DECLARE @WXBEDCODE varchar(255);
        DECLARE @WXDOCCODE varchar(255);
        DECLARE @WXDOCID bigint;
        DECLARE @WXIC varchar(255);
        DECLARE @WXNAME varchar(255);
        DECLARE @WXPFOLDERID bigint;
        DECLARE @WXRN varchar(255);
        DECLARE @WXROOMCODE varchar(255);
        DECLARE @WXWARDCODE varchar(255);
        DECLARE @WXRDID bigint;
        DECLARE @WXRID bigint;
        DECLARE @LOCATION varchar(255);

        SET @WXDOCCODE = '{doc_code}';
        SET @WXRN = '{rn}';

        select @WXDOCID = UNITID from {database}.dbo.UXINFO where UECODE = @WXDOCCODE;
        select top 1 @WXADMNO = WXADMNO, @WXBEDCODE = WXBEDCODE,@WXIC = WXIC,@WXNAME = WXNAME,
                     @WXPFOLDERID = WXPFOLDERID,@WXROOMCODE = WXROOMCODE,@WXWARDCODE = WXWARDCODE, 
                     @WXRID = WXRID 
        from {database}.dbo.wxadmission where WXRN = @WXRN;
        
        select @WXADMDATE = RVDT, @WXRDID = RDID 
        from {database}.dbo.regdoclink where RDRID = @WXRID and RDUID = @WXDOCID;

        insert into {database}.dbo.wxadmission 
        (WXADMDATE,WXADMNO,WXBEDCODE,WXDOCCODE,WXDOCID,WXIC,WXNAME,WXPFOLDERID,WXRN,WXROOMCODE,WXWARDCODE,WXRDID,WXRID)
        values (@WXADMDATE,@WXADMNO,@WXBEDCODE,@WXDOCCODE,@WXDOCID,@WXIC,@WXNAME,@WXPFOLDERID,@WXRN,@WXROOMCODE,@WXWARDCODE,@WXRDID,@WXRID);

        SET @LOCATION = @WXWARDCODE + '-' + @WXROOMCODE + '-' + @WXBEDCODE;
        insert into {database}.dbo.dischargetrack (DCTADMDT, DCTADMNO, DCTDOCID, DCTLOCATION, DCTRN, DCTTYPE)
        values (@WXADMDATE, @WXADMNO, @WXDOCID, @LOCATION, @WXRN, 'INPATIENT');

        delete {database}.dbo.himdiscinfo 
        where HDIRN = @WXRN and HDIUSERID = @WXDOCID and HDIADMNO = @WXADMNO 
        and HDITYPE = 'OFFCARE' and (HDIFLAG = 'COMPLETE' or HDIFLAG = 'READ');
        """

        cursor.execute(sql)
        conn.commit()
        messagebox.showinfo("Success", f"Patient {rn} re-admitted successfully!")

    except Exception as e:
        messagebox.showerror("Error", str(e))

    finally:
        if 'conn' in locals():
            conn.close()

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Offcare Re-Admission")

# Connection details
tk.Label(root, text="Server:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_server = tk.Entry(root, width=30)
entry_server.grid(row=0, column=1)

tk.Label(root, text="Database:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_db = tk.Entry(root, width=30)
entry_db.insert(0, "originHIS")
entry_db.grid(row=1, column=1)

tk.Label(root, text="Username (leave blank for Windows Auth):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
entry_user = tk.Entry(root, width=30)
entry_user.grid(row=2, column=1)

tk.Label(root, text="Password:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
entry_pass = tk.Entry(root, width=30, show="*")
entry_pass.grid(row=3, column=1)

# Business inputs
tk.Label(root, text="Doctor Code:").grid(row=4, column=0, padx=5, pady=5)
entry_doc = tk.Entry(root, width=30)
entry_doc.insert(0, "LYC")
entry_doc.grid(row=4, column=1)

tk.Label(root, text="RN:").grid(row=5, column=0, padx=5, pady=5)
entry_rn = tk.Entry(root, width=30)
entry_rn.insert(0, "12024779")
entry_rn.grid(row=5, column=1)

# Buttons
btn_test = tk.Button(root, text="Test Connection", command=test_connection)
btn_test.grid(row=6, column=0, columnspan=2, pady=5)

btn_run = tk.Button(root, text="Re-Admit Patient", command=run_re_admit)
btn_run.grid(row=7, column=0, columnspan=2, pady=5)

btn_save = tk.Button(root, text="Save Settings", command=save_config)
btn_save.grid(row=8, column=0, columnspan=2, pady=5)

# Load saved config on startup
load_config()

root.mainloop()
