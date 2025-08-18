import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, font

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("pottery.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pottery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            code TEXT,
            pottery_type TEXT,
            email TEXT,
            phone TEXT,
            kiln_fired TEXT DEFAULT 'No',
            text_sent TEXT DEFAULT 'No',
            collected TEXT DEFAULT 'No'
        )
    """)
    conn.commit()
    conn.close()

# --- GLOBAL FONTS ---
LABEL_FONT = ("Arial", 18)
ENTRY_FONT = ("Arial", 18)
BUTTON_FONT = ("Arial", 20, "bold")
TABLE_FONT = ("Arial", 18)

# --- FUNCTIONS ---
def add_pottery():
    def save_record():
        conn = sqlite3.connect("pottery.db")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pottery (name, code, pottery_type, email, phone, kiln_fired, text_sent, collected)
            VALUES (?, ?, ?, ?, ?, 'No', 'No', 'No')
        """, (entry_name.get(), entry_code.get(), entry_type.get(), entry_email.get(), entry_phone.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Saved", "Pottery record added!")
        add_win.destroy()

    add_win = tk.Toplevel(root)
    add_win.title("Add Pottery")
    add_win.attributes("-fullscreen", True)
    add_win.bind("<Escape>", lambda e: add_win.attributes("-fullscreen", False))

    frame = tk.Frame(add_win)
    frame.pack(expand=True)

    tk.Label(frame, text="Name", font=LABEL_FONT).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_name = tk.Entry(frame, font=ENTRY_FONT); entry_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame, text="Code", font=LABEL_FONT).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_code = tk.Entry(frame, font=ENTRY_FONT); entry_code.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame, text="Pottery Type", font=LABEL_FONT).grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry_type = tk.Entry(frame, font=ENTRY_FONT); entry_type.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(frame, text="Email", font=LABEL_FONT).grid(row=3, column=0, padx=5, pady=5, sticky="e")
    entry_email = tk.Entry(frame, font=ENTRY_FONT); entry_email.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(frame, text="Phone Number", font=LABEL_FONT).grid(row=4, column=0, padx=5, pady=5, sticky="e")
    entry_phone = tk.Entry(frame, font=ENTRY_FONT); entry_phone.grid(row=4, column=1, padx=5, pady=5)

    tk.Button(frame, text="Save", font=BUTTON_FONT, command=save_record).grid(row=5, column=0, columnspan=2, pady=15)

    tk.Button(add_win, text="Back", font=BUTTON_FONT, command=add_win.destroy).pack(side="left", anchor="s", padx=10, pady=10)


def modify_pottery():
    def search():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect("pottery.db")
        cur = conn.cursor()
        code_val = entry_code.get().strip()
        if code_val:
            cur.execute("SELECT * FROM pottery WHERE code=? ORDER BY id DESC", (code_val,))
        else:
            cur.execute("SELECT * FROM pottery ORDER BY id DESC")
        records = cur.fetchall()
        conn.close()
        for r in records:
            tree.insert("", "end", values=r)

    def update_record():
        selected = tree.selection()
        if not selected: return
        record = tree.item(selected[0], "values")
        id = record[0]
        kiln = kiln_var.get()
        text = text_var.get()
        collected = collected_var.get()
        conn = sqlite3.connect("pottery.db")
        cur = conn.cursor()
        cur.execute("UPDATE pottery SET kiln_fired=?, text_sent=?, collected=? WHERE id=?",
                    (kiln, text, collected, id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", f"Record ID {id} updated!")
        search()
        mod_win.lift(); mod_win.focus_force()

    def delete_record():
        selected = tree.selection()
        if not selected: return
        record = tree.item(selected[0], "values")
        id = record[0]
        confirm = messagebox.askyesno("Delete", f"Are you sure you want to delete record ID {id}?")
        if confirm:
            conn = sqlite3.connect("pottery.db")
            cur = conn.cursor()
            cur.execute("DELETE FROM pottery WHERE id=?", (id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", f"Record ID {id} deleted!")
            search()
            mod_win.lift(); mod_win.focus_force()

    def on_row_select(event):
        selected = tree.selection()
        if not selected: return
        record = tree.item(selected[0], "values")
        kiln_var.set(record[6])
        text_var.set(record[7])
        collected_var.set(record[8])

    mod_win = tk.Toplevel(root)
    mod_win.title("Modify Pottery")
    mod_win.attributes("-fullscreen", True)
    mod_win.bind("<Escape>", lambda e: mod_win.attributes("-fullscreen", False))
    mod_win.lift(); mod_win.focus_force()

    tk.Label(mod_win, text="Enter 3-digit code (leave blank for all)", font=LABEL_FONT).pack()
    entry_code = tk.Entry(mod_win, font=ENTRY_FONT); entry_code.pack()
    tk.Button(mod_win, text="Search", font=BUTTON_FONT, command=search).pack()

    columns = ("id","name","code","pottery_type","email","phone","kiln_fired","text_sent","collected")
    headers = ["ID","Name","Code","Pottery Type","Email","Phone Number","Fired","Text Sent","Collected"]

    tree = ttk.Treeview(mod_win, columns=columns, show="headings")
    style = ttk.Style()
    style.configure("Treeview", font=TABLE_FONT, rowheight=30)
    style.configure("Treeview.Heading", font=("Arial", 18, "bold"))

    for col, head in zip(columns, headers):
        tree.heading(col, text=head)
        tree.column(col, width=150, anchor="center")
    tree.pack(fill="both", expand=True, pady=10)

    tree.bind("<<TreeviewSelect>>", on_row_select)

    frame = tk.Frame(mod_win)
    frame.pack(pady=10)

    tk.Label(frame, text="Kiln Fired:", font=LABEL_FONT).grid(row=0, column=0, padx=5, sticky="e")
    kiln_var = tk.StringVar(value="No")
    ttk.Combobox(frame, textvariable=kiln_var, values=["Yes","No","Damaged"], font=ENTRY_FONT, state="readonly").grid(row=0, column=1)

    tk.Label(frame, text="Text Sent:", font=LABEL_FONT).grid(row=1, column=0, padx=5, sticky="e")
    text_var = tk.StringVar(value="No")
    ttk.Combobox(frame, textvariable=text_var, values=["Yes","No"], font=ENTRY_FONT, state="readonly").grid(row=1, column=1)

    tk.Label(frame, text="Collected:", font=LABEL_FONT).grid(row=2, column=0, padx=5, sticky="e")
    collected_var = tk.StringVar(value="No")
    ttk.Combobox(frame, textvariable=collected_var, values=["Yes","No","Binned"], font=ENTRY_FONT, state="readonly").grid(row=2, column=1)

    tk.Button(mod_win, text="Update Record", font=BUTTON_FONT, command=update_record).pack(pady=5)
    tk.Button(mod_win, text="Delete Record", font=BUTTON_FONT, command=delete_record).pack(pady=30)

    tk.Button(mod_win, text="Back", font=BUTTON_FONT, command=mod_win.destroy).pack(side="left", anchor="s", padx=10, pady=10)

    search()


def generate_report():
    def mark_sent(item_id):
        conn = sqlite3.connect("pottery.db")
        cur = conn.cursor()
        cur.execute("UPDATE pottery SET text_sent='Yes' WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        refresh_report()
        rep_win.lift(); rep_win.focus_force()

    def refresh_report():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect("pottery.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM pottery WHERE kiln_fired='Yes' AND text_sent='No' ORDER BY id DESC")
        records = cur.fetchall()
        conn.close()
        for r in records:
            tree.insert("", "end", values=r)

    rep_win = tk.Toplevel(root)
    rep_win.title("Text Report")
    rep_win.attributes("-fullscreen", True)
    rep_win.bind("<Escape>", lambda e: rep_win.attributes("-fullscreen", False))
    rep_win.lift(); rep_win.focus_force()

    columns = ("id","name","code","pottery_type","email","phone","kiln_fired","text_sent","collected")
    headers = ["ID","Name","Code","Pottery Type","Email","Phone Number","Fired","Text Sent","Collected"]

    tree = ttk.Treeview(rep_win, columns=columns, show="headings")
    style = ttk.Style()
    style.configure("Treeview", font=TABLE_FONT, rowheight=30)
    style.configure("Treeview.Heading", font=("Arial", 18, "bold"))

    for col, head in zip(columns, headers):
        tree.heading(col, text=head)
        tree.column(col, width=150, anchor="center")
    tree.pack(fill="both", expand=True, pady=10)

    def mark_selected_sent():
        selected = tree.selection()
        if not selected: return
        record = tree.item(selected[0], "values")
        mark_sent(record[0])

    tk.Button(rep_win, text="Mark Selected as Sent", font=BUTTON_FONT, command=mark_selected_sent).pack(pady=10)

    tk.Button(rep_win, text="Back", font=BUTTON_FONT, command=rep_win.destroy).pack(side="left", anchor="s", padx=10, pady=10)

    refresh_report()


def mark_collection():
    def mark_collected(item_id):
        conn = sqlite3.connect("pottery.db")
        cur = conn.cursor()
        cur.execute("UPDATE pottery SET collected='Yes' WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        refresh_collection()
        col_win.lift(); col_win.focus_force()

    def refresh_collection():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect("pottery.db")
        cur = conn.cursor()
        code_val = entry_code.get().strip()
        if code_val:
            cur.execute("""
                SELECT * FROM pottery 
                WHERE kiln_fired='Yes' AND text_sent='Yes' AND collected='No' AND code=? 
                ORDER BY id DESC
            """, (code_val,))
        else:
            cur.execute("""
                SELECT * FROM pottery 
                WHERE kiln_fired='Yes' AND text_sent='Yes' AND collected='No' 
                ORDER BY id DESC
            """)
        records = cur.fetchall()
        conn.close()
        for r in records:
            tree.insert("", "end", values=r)

    col_win = tk.Toplevel(root)
    col_win.title("Mark Collection")
    col_win.attributes("-fullscreen", True)
    col_win.bind("<Escape>", lambda e: col_win.attributes("-fullscreen", False))
    col_win.lift(); col_win.focus_force()

    tk.Label(col_win, text="Enter 3-digit code (leave blank for all)", font=LABEL_FONT).pack()
    entry_code = tk.Entry(col_win, font=ENTRY_FONT); entry_code.pack()
    tk.Button(col_win, text="Search", font=BUTTON_FONT, command=refresh_collection).pack()

    columns = ("id","name","code","pottery_type","email","phone","kiln_fired","text_sent","collected")
    headers = ["ID","Name","Code","Pottery Type","Email","Phone Number","Fired","Text Sent","Collected"]

    tree = ttk.Treeview(col_win, columns=columns, show="headings")
    style = ttk.Style()
    style.configure("Treeview", font=TABLE_FONT, rowheight=30)
    style.configure("Treeview.Heading", font=("Arial", 18, "bold"))

    for col, head in zip(columns, headers):
        tree.heading(col, text=head)
        tree.column(col, width=150, anchor="center")
    tree.pack(fill="both", expand=True, pady=10)

    def mark_selected_collected():
        selected = tree.selection()
        if not selected: return
        record = tree.item(selected[0], "values")
        mark_collected(record[0])

    tk.Button(col_win, text="Mark Selected as Collected", font=BUTTON_FONT, command=mark_selected_collected).pack(pady=10)

    tk.Button(col_win, text="Back", font=BUTTON_FONT, command=col_win.destroy).pack(side="left", anchor="s", padx=10, pady=10)

    refresh_collection()

# --- MAIN APP ---
init_db()

root = tk.Tk()
root.title("Pottery Tracker")
root.attributes("-fullscreen", True)

# Make everything quit fullscreen with ESC
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

# A frame that expands to centre everything inside
main_frame = tk.Frame(root)
main_frame.pack(expand=True)   # expands vertically and horizontally

# Now pack the buttons into the middle frame
tk.Button(main_frame, text="Add Pottery", font=BUTTON_FONT, command=add_pottery, width=30).pack(pady=10)
tk.Button(main_frame, text="Modify Pottery Record", font=BUTTON_FONT, command=modify_pottery, width=30).pack(pady=10)
tk.Button(main_frame, text="Generate Text Report", font=BUTTON_FONT, command=generate_report, width=30).pack(pady=10)
tk.Button(main_frame, text="Collection Screen", font=BUTTON_FONT, command=mark_collection, width=30).pack(pady=10)

root.mainloop()
