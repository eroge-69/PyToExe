import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

# ==== CONFIGURE YOUR DATABASES HERE ====
DATABASES = [
    {'name': 'acre99', 'user': 'postgres', 'password': '1234', 'host': 'localhost'},
    {'name': 'acres99', 'user': 'postgres', 'password': '1234', 'host': 'localhost'}
]

# ==== SEARCH LOGIC returns structured results ====
def search_data(term):
    term = term.lower()
    all_results = []
    for db in DATABASES:
        try:
            conn = psycopg2.connect(
                dbname=db['name'], user=db['user'],
                password=db['password'], host=db['host']
            )
            cur = conn.cursor()
            cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
            for (table,) in cur.fetchall():
                cur.execute(f'SELECT * FROM "{table}" LIMIT 1000')
                cols = [d[0] for d in cur.description]
                rows = cur.fetchall()
                matches = [r for r in rows if any(term in str(v).lower() for v in r)]
                if matches:
                    all_results.append((db['name'], table, cols, matches))
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showwarning("DB Error", f"Failed on {db['name']}: {e}")
    return all_results

# ==== UI CALLBACK ====
def on_search():
    term = entry.get().strip()
    if not term:
        messagebox.showinfo("Input needed", "Please enter a search term.")
        return
    for tab in notebook.tabs():
        notebook.forget(tab)
    results = search_data(term)
    if not results:
        messagebox.showinfo("No Results", "🔍 No matches found.")
        return
    for db_name, table, cols, rows in results:
        tab = f"{db_name}.{table}"
        frame = ttk.Frame(notebook, style='Result.TFrame')
        notebook.add(frame, text=tab)
        tree = ttk.Treeview(frame, columns=cols, show='headings', style='Result.Treeview')
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120, anchor='w')
        for row in rows:
            vals = []
            for v in row:
                s = str(v)
                if term in s.lower():
                    s = s.replace(term, f"[{term.upper()}]")
                vals.append(s)
            tree.insert("", "end", values=vals)
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

# ==== BUILD MAIN WINDOW ====
root = tk.Tk()
root.title("🔍 DARK FORUM DATA")
root.geometry("900x600")

style = ttk.Style(root)
style.theme_use('clam')

# Title Styling
style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'), foreground="#B16E6E", background="white")
# Frame background
style.configure('TFrame', background='#f0f0f0')
# Search bar styling
style.configure('Search.TEntry', fieldbackground='white', foreground='#B16E6E', font=('Arial', 20), padding=10)
# Button styling
style.configure('Search.TButton', background="#CE7C7C", foreground="#110505", font=('Arial', 13, 'bold'), padding=7)
style.map('Search.TButton', background=[('active', "#C24545")])
# Notebook Tab styling
style.configure('TNotebook', background='#f0f0f0', borderwidth=0)
style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'), padding=[10, 5])
# Results frame
style.configure('Result.TFrame', background="#FAE2E0")
# Treeview styling
style.configure('Result.Treeview', background='#e6f2ff', fieldbackground='#e6f2ff', foreground='black', font=('Courier New', 10))
#style.configure('Result.Treeview.Heading', font=('Arial', 10, 'bold'), background='#004080', foreground='white')
style.map('Result.Treeview', background=[('selected', '#99ccff')])

# Top Frame
top = ttk.Frame(root)
top.pack(fill='x', padx=10, pady=10)
# Title Label
ttk.Label(top, text="🔍 Database Search", style='Title.TLabel').pack(pady=10)
# Search controls
entry = ttk.Entry(top, width=70, style='Search.TEntry')
entry.pack(side='left', padx=(0,5))
ttk.Button(top, text="Search", style='Search.TButton', command=on_search).pack(side='left')

# Tabs for results
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=(0,10))

root.mainloop()
