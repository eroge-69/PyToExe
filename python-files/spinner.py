import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

# ==== CONFIGURE YOUR DATABASES HERE ====
DATABASES = [
    {'name': 'paytm_user', 'user': 'postgres', 'password': '1234', 'host': 'localhost'},
    {'name': 'acres99', 'user': 'postgres', 'password': '1234', 'host': 'localhost'},
    # Add more databases if needed
]

VISIBLE_TAB_COUNT = 7
all_tabs = []
visible_index = 0
is_searching = False

# ==== SEARCH LOGIC ====
def search_data(term):
    term = term.lower()
    results = []
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
                cols = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                matches = [r for r in rows if any(term in str(v).lower() for v in r)]
                if matches:
                    results.append((db['name'], table, cols, matches))
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showwarning("DB Error", f"{db['name']} failed: {e}")
    return results

# ==== UI CALLBACK ====
def on_search():
    global visible_index, all_tabs, is_searching
    term = entry.get().strip()
    if not term:
        messagebox.showinfo("Input required", "Please enter a search term.")
        return

    is_searching = True
    process_btn.config(text="Loading..🧭", state="disabled")
    root.after(100, lambda: run_search(term))

def run_search(term):
    global visible_index, all_tabs, is_searching
    visible_index = 0
    all_tabs.clear()
    for tab in notebook.tabs():
        notebook.forget(tab)

    results = search_data(term)

    is_searching = False
    process_btn.config(text="Search", state="normal")

    if not results:
        messagebox.showinfo("No Results", "🔍 No matches found.")
        return

    for db_name, table, cols, rows in results:
        label = f"{db_name}.{table}"
        frame = ttk.Frame(notebook, style='Result.TFrame')
        tree = ttk.Treeview(frame, columns=cols, show='headings', style='Result.Treeview')
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=110, anchor='w')

        for row in rows:
            tree.insert("", "end", values=[str(v) for v in row])

        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        all_tabs.append((label, frame))

    update_tabs()
    page_spinbox.config(from_=1, to=max(1, (len(all_tabs) + VISIBLE_TAB_COUNT - 1) // VISIBLE_TAB_COUNT))
    page_spinbox.set(1)

def update_tabs():
    for tab in notebook.tabs():
        notebook.forget(tab)

    for label, frame in all_tabs[visible_index:visible_index + VISIBLE_TAB_COUNT]:
        notebook.add(frame, text=label)
        
    prev_btn['state'] = 'normal' if visible_index > 0 else 'disabled'
    next_btn['state'] = 'normal' if visible_index + VISIBLE_TAB_COUNT < len(all_tabs) else 'disabled'

    current_page = (visible_index // VISIBLE_TAB_COUNT) + 1
    page_spinbox.set(current_page)

def shift_tabs(delta):
    global visible_index
    visible_index = max(0, min(len(all_tabs) - VISIBLE_TAB_COUNT, visible_index + delta))
    update_tabs()

def on_spinner_change():
    global visible_index
    try:
        page_num = int(page_spinbox.get())
        max_page = (len(all_tabs) + VISIBLE_TAB_COUNT - 1) // VISIBLE_TAB_COUNT
        page_num = min(max(page_num, 1), max_page)
        visible_index = (page_num - 1) * VISIBLE_TAB_COUNT
        update_tabs()
    except ValueError:
        pass

# ==== UI BUILD ====
root = tk.Tk()
root.geometry("1000x700")
root.title("🔍 DARK FORUM DATA")

style = ttk.Style(root)
style.theme_use('clam')
style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'), foreground="black")
style.configure('Search.TEntry', fieldbackground='black', foreground='white', font=('Arial', 13))
style.configure('Search.TButton', background="gray", foreground="white", font=('Arial', 11, 'bold'))
style.map('Search.TButton', background=[('active', "#518A8A")])
style.configure('Result.TFrame', background="lightblue")
style.configure('Result.Treeview', background='white', fieldbackground='white', font=('Courier New', 10))
style.configure('Nav.TSpinbox', font=('Arial', 10))

ttk.Label(root, text="✨ DARK FORUM DATA", style='Title.TLabel').pack(pady=10)

# Search frame
search_frame = ttk.Frame(root)
search_frame.pack(fill='x', padx=200, pady=10)
entry = ttk.Entry(search_frame, justify='left', width=0, style='Search.TEntry')
entry.pack(side='left', padx=0,expand=True, fill='x')
process_btn = ttk.Button(search_frame, text="🔍Search", style='Search.TButton', command=on_search)
process_btn.pack(side='left')

# Navigation
nav_frame = ttk.Frame(root)
nav_frame.pack(fill='x', padx=5, pady=5)

prev_btn = ttk.Button(nav_frame, text="◀ Previous", command=lambda: shift_tabs(-VISIBLE_TAB_COUNT))
prev_btn.pack(side='left', padx=(0, 5))

page_spinbox = ttk.Spinbox(nav_frame, from_=1, to=1, width=10, style='Nav.TSpinbox', command=on_spinner_change)
page_spinbox.pack(side='left', padx=5)
page_spinbox.bind("<Return>", lambda e: on_spinner_change())
page_spinbox.bind("<FocusOut>", lambda e: on_spinner_change())

ttk.Label(nav_frame).pack(side='left')
max_page_label = ttk.Label(nav_frame, text=" ")
max_page_label.pack(side='left', padx=5)

next_btn = ttk.Button(nav_frame, text="Next ▶", command=lambda: shift_tabs(VISIBLE_TAB_COUNT))
next_btn.pack(side='right')

# Notebook for results
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

root.mainloop()
