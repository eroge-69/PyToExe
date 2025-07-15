from tkinter import *
import pyodbc
global status_label
import tkinter.messagebox as messagebox
import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk



# from back1 import signup
root = Tk()

root.title("Boson Systems Pvt. Ltd.")
root.state('zoomed')

form_frame = Frame(root, bg='gray20', bd=5, relief=RIDGE)
form_frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=1600, height=900)

table_var = tk.StringVar()
db_var = tk.StringVar()

Label(form_frame, text="Select Table:-", font=("calibri", 16), bg="gray20", fg="white").place(x=600, y=225)
table_combo = ttk.Combobox(form_frame, textvariable=table_var, state="readonly", width=40)
table_combo.place(x=760, y=220,width=400, height=40)

Label(form_frame, text="Select Database:-", font=("calibri", 16), bg="gray20", fg="white").place(x=600, y=160)
db_combo = ttk.Combobox(form_frame, textvariable=db_var, state="readonly", width=40)
db_combo.place(x=760, y=160,width=400, height=40)




#//////////// Bakend by/////////////////////////////////

def Sqlconfi(esname):
       
        global servername
       
        servername = esname.get()
       
        try:
            mydb = pyodbc.connect(
                f'DRIVER={{SQL Server}};'
                f'SERVER={servername};'
                
                f'Trusted_Connection=yes;'
            )
            sqls = 1
            
            # print("✅ SQL connection successful!")
            status_label.config(text="✅ SQL connection successful!",fg="#51f542",font=("calibri", 18, "bold"))
            
            mydb.close()
            # Create a dictionary from your variables
           
        except Exception as e:
            status_label.config(text="❌ Connection failed:",fg="Red", font=("calibri", 18, "bold"))
            sqls = 2   
            
             
def create_cycle_database(servername, db_name, prefix_base):
    
    try:
        # Allow CREATE DATABASE outside transaction
        connection = pyodbc.connect(
            f"DRIVER={{SQL Server}};SERVER={servername};DATABASE=master;Trusted_Connection=yes;",
            autocommit=True
        )
        cursor = connection.cursor()
        cursor.execute(f"IF DB_ID('{db_name}') IS NULL CREATE DATABASE {db_name};")
        connection.close()

        # Now connect to new database
        connection = pyodbc.connect(
            f"DRIVER={{SQL Server}};SERVER={servername};DATABASE={db_name};Trusted_Connection=yes;",
              autocommit=True
        )
        cursor = connection.cursor()

        # Create base table
        cursor.execute("""
            CREATE TABLE CycleVariables (
                CycleName VARCHAR(30) NULL,
                VariableName VARCHAR(30) NULL
            )
        """)

        # Create all suffix tables (HE, CE, FE)
        for num in range(1, 4):  # 1 to 3
            prefix = f"{prefix_base}{num}"
            for suffix in ["HE", "CE", "FE"]:
                cursor.execute(f"""
                    CREATE TABLE {prefix}_{suffix} (
                        Timestamp DATETIME NULL,
                        Cycle_Name VARCHAR(30) NULL,
                        Varible_name VARCHAR(30) NULL,
                        Value VARCHAR(30) NULL
                    )
                """)

        connection.commit()
        connection.close()
        messagebox.showinfo("Success", f"Database '{db_name}' and tables created successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to create database or tables:\n{e}")


def load_table_names(servername, db_name):
    print(f"Loading table names from database '{db_name}' on server '{servername}'")
    try:
        conn = pyodbc.connect(
            f"DRIVER={{SQL Server}};SERVER={servername};DATABASE={db_name};Trusted_Connection=yes;",
            autocommit=True
        )
        cursor = conn.cursor()
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not tables:
            messagebox.showinfo("No Tables", "No tables found.")
        else:
            table_combo['values'] = tables
            table_combo.current(0)

    except Exception as e:
        messagebox.showerror("Load Error", str(e))


def export_table_data(servername, db_name, table_name):
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        connection = pyodbc.connect(
            f"DRIVER={{SQL Server}};SERVER={servername};DATABASE={db_name};Trusted_Connection=yes;",
            autocommit=True
        )

        df = pd.read_sql(f"SELECT * FROM {table_name}", connection)
        df.to_csv(file_path, index=False)
        connection.close()

        messagebox.showinfo("Export Complete", f"Exported {table_name} to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))

def import_table_data(servername, db_name, table_name):
    try:
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        df = pd.read_csv(file_path)

        connection = pyodbc.connect(
            f"DRIVER={{SQL Server}};SERVER={servername};DATABASE={db_name};Trusted_Connection=yes;",
            autocommit=True
        )
        cursor = connection.cursor()

        # Dynamically build insert query based on columns
        cols = ", ".join(df.columns)
        placeholders = ", ".join("?" * len(df.columns))
        insert_query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

        for _, row in df.iterrows():
            cursor.execute(insert_query, *row)

        connection.commit()
        connection.close()
        messagebox.showinfo("Import Complete", f"Imported into {table_name}")
    except Exception as e:
        messagebox.showerror("Import Error", str(e))

def delete_table_data(servername, db_name, table_name):
    try:
        if not messagebox.askyesno("Confirm Delete", f"Delete all data from {table_name}?"):
            return

        connection = pyodbc.connect(
            f"DRIVER={{SQL Server}};SERVER={servername};DATABASE={db_name};Trusted_Connection=yes;",
            autocommit=True
        )
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM {table_name}")
        connection.commit()
        connection.close()

        messagebox.showinfo("Deleted", f"All data deleted from table '{table_name}'")

    except Exception as e:
        messagebox.showerror("Delete Error", str(e))

def load_databases(servername):
    try:
        conn = pyodbc.connect(
            f"DRIVER={{SQL Server}};SERVER={servername};DATABASE=master;Trusted_Connection=yes;",
            autocommit=True
        )
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")  # Skip system DBs
        dbs = [row[0] for row in cursor.fetchall()]
        conn.close()

        db_combo['values'] = dbs
        if dbs:
            db_combo.current(0)
    except Exception as e:
        messagebox.showerror("Load Databases Error", str(e))


      
   
Label(form_frame, text="Boson Systems Pvt Ltd", font=("calibri", 24, "bold"), bg="gray20", fg="white").place(x=700, y=10)


sname = Label(form_frame,text="SQL Server Name:-",font=("calibri",18,"bold"),bg="gray20",fg="white")
sname.place(x=400,y=75)

# esname = Entry(form_frame,bg="White",font=("calibri",16,),fg="black").place(x=660,y=75,width=400,height=40)

canvas = tk.Canvas(form_frame, height=2, bg="Gray", highlightthickness=0).place(x=0, y=130, width=2000)


canvas = tk.Canvas(form_frame, height=2, bg="Gray", highlightthickness=0).place(x=0, y=130, width=2000)


Label(form_frame,text="CIP Cycle:-",font=("calibri",16,),bg="gray20",fg="white").place(x=50,y=160)
Label(form_frame,text="PHT Cycle:-",font=("calibri",16,),bg="gray20",fg="white").place(x=50,y=220)
Label(form_frame,text="SIP Cycle:-",font=("calibri",16,),bg="gray20",fg="white").place(x=50,y=280)
Label(form_frame,text="Batch Semi Auto Mode:-",font=("calibri",16,),bg="gray20",fg="white").place(x=50,y=340)




Button(form_frame, text="New Database/Table", font=("Arial", 12), command=lambda:create_cycle_database(esname.get(), "CIP_R", "C")).place(x=280, y=160,width=200,height=40)
Button(form_frame, text="New Database/Table", font=("Arial", 12), command=lambda:create_cycle_database(esname.get(), "PHT_R", "P")).place(x=280, y=220,width=200,height=40)
Button(form_frame, text="New Database/Table", font=("Arial", 12), command=lambda:create_cycle_database(esname.get(), "SIP_R", "S")).place(x=280, y=280,width=200,height=40)
Button(form_frame, text="New Database/Table", font=("Arial", 12), command=lambda:create_cycle_database(esname.get(), "BATCH_R", "B")).place(x=280, y=340,width=200,height=40)








# Buttons PHT for table operations
Button(form_frame, text="Load Databases", font=("Arial", 12),command=lambda: load_databases(esname.get())).place(x=1190, y=160, width=200, height=40)
Button(form_frame, text="Load Tables", font=("Arial", 12),command=lambda: load_table_names(esname.get(), db_var.get())).place(x=1190, y=220, width=200, height=40)
Button(form_frame, text="Export Table", font=("Arial", 12),command=lambda: export_table_data(esname.get(), db_var.get(), table_var.get())).place(x=830, y=280, width=200, height=40)
Button(form_frame, text="Import Table", font=("Arial", 12),command=lambda: import_table_data(esname.get(), db_var.get(), table_var.get())).place(x=1060, y=280, width=200, height=40)
Button(form_frame, text="Delete Table Data", font=("Arial", 12),command=lambda: delete_table_data(esname.get(), db_var.get(), table_var.get())).place(x=1290, y=280, width=200, height=40)

esname = Entry(form_frame, bg="white", font=("calibri", 16), fg="black")
esname.place(x=660, y=75, width=400, height=40)

Button(form_frame,text="Connect SQL Server",font=("Arial", 12),command=lambda: Sqlconfi(esname)  ).place(x=1100, y=75, width=200, height=40)







    
status_label = Label(form_frame,text="✅ Server:-{}".format(esname),font=("calibri",18,"bold"),bg="gray20",fg="#51f542",)
status_label.place(x=30,y=600)

# Inside your form_frame or root window
  # Adjust x, y, and width as needed


    

 
    
   


        

 

                            
                              
        














root.mainloop()
