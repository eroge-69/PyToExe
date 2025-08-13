import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# Global connection parameters
db_config = {}

# Connect using SQL Server Authentication
def connect_to_db():
    try:
        conn = pyodbc.connect(
            f"DRIVER={{SQL Server}};"
            f"SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};"
            f"UID={db_config['username']};"
            f"PWD={db_config['password']};"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Connection Error", str(e))
        return None

# Load users into dropdown
def load_users():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT UserID, FullName FROM Users")
            users = cursor.fetchall()
            user_map.clear()
            user_dropdown['values'] = [row.FullName for row in users]
            for row in users:
                user_map[row.FullName] = row.UserID
        except Exception as e:
            messagebox.showerror("User Load Error", str(e))
        finally:
            conn.close()

# Extract values query
def run_extract_query():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        query = """
        WITH ExtractedValues AS (
            SELECT
                CASE
                    WHEN CHARINDEX('$i', Vals) > 0 AND CHARINDEX('$g', Vals, CHARINDEX('$i', Vals)) > 0 THEN
                        SUBSTRING(
                            Vals,
                            CHARINDEX('$i', Vals) + 2,
                            CHARINDEX('$g', Vals, CHARINDEX('$i', Vals)) - CHARINDEX('$i', Vals) - 2
                        )
                    ELSE NULL
                END AS ValueBetween
            FROM Records 
            WHERE TagID = '=949'
        )
        SELECT DISTINCT ValueBetween
        FROM ExtractedValues
        WHERE ValueBetween != ''
        ORDER BY ValueBetween;
        """
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            listbox.delete(0, tk.END)
            for row in results:
                listbox.insert(tk.END, row[0])
        except Exception as e:
            messagebox.showerror("Query Error", str(e))
        finally:
            conn.close()

# Count by user query
def run_count_query():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        selected_user = user_dropdown.get()
        user_id = user_map.get(selected_user)
        field = field_var.get()

        try:
            if user_id:
                query = f"SELECT COUNT(*) FROM Records WHERE {field} = ?"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                listbox.delete(0, tk.END)
                listbox.insert(tk.END, f"{field} = {selected_user} → {result[0]} records")
            else:
                query = f"SELECT {field}, COUNT(*) FROM Records GROUP BY {field} ORDER BY COUNT(*) DESC"
                cursor.execute(query)
                results = cursor.fetchall()
                listbox.delete(0, tk.END)
                for row in results:
                    listbox.insert(tk.END, f"UserID: {row[0]} → {row[1]} records")
        except Exception as e:
            messagebox.showerror("Query Error", str(e))
        finally:
            conn.close()

# --- Login Window ---
def show_login_window():
    login = tk.Tk()
    login.title("Database Login")
    login.geometry("400x250")

    tk.Label(login, text="SQL Server:").pack(pady=5)
    server_entry = tk.Entry(login)
    server_entry.pack()

    tk.Label(login, text="Database Name:").pack(pady=5)
    db_entry = tk.Entry(login)
    db_entry.pack()

    tk.Label(login, text="Username:").pack(pady=5)
    user_entry = tk.Entry(login)
    user_entry.pack()

    tk.Label(login, text="Password:").pack(pady=5)
    pass_entry = tk.Entry(login, show="*")
    pass_entry.pack()

    def try_login():
        db_config['server'] = server_entry.get()
        db_config['database'] = db_entry.get()
        db_config['username'] = user_entry.get()
        db_config['password'] = pass_entry.get()

        conn = connect_to_db()
        if conn:
            conn.close()
            login.destroy()
            show_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials or connection error")

    tk.Button(login, text="Login", command=try_login).pack(pady=20)
    login.mainloop()

# --- Main App UI ---
def show_main_app():
    global user_dropdown, listbox, field_var

    root = tk.Tk()
    root.title("SQL Server Query App")
    root.geometry("700x500")

    top_frame = tk.Frame(root)
    top_frame.pack(pady=10)

    tk.Button(top_frame, text="Run Extract Query", command=run_extract_query).grid(row=0, column=0, padx=10)

    field_var = tk.StringVar(value='CreatedBy')
    tk.OptionMenu(top_frame, field_var, 'CreatedBy', 'UpdatedBy').grid(row=0, column=1, padx=5)

    user_dropdown = ttk.Combobox(top_frame, width=30, state="readonly")
    user_dropdown.grid(row=0, column=2, padx=5)
    user_dropdown.set("Select user or leave empty")

    tk.Button(top_frame, text="Run Count Query", command=run_count_query).grid(row=0, column=3, padx=10)

    # Results
    listbox = tk.Listbox(root, width=100, height=20)
    listbox.pack(pady=10)

    load_users()
    root.mainloop()

# --- Start Here ---
user_map = {}
show_login_window()
