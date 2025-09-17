import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import os

try:
    import win32print
    import win32api
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

# Database setup
conn = sqlite3.connect("Panda billiards.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS canteen_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    price REAL
)
""")
conn.commit()

# Preload items
cursor.execute("SELECT COUNT(*) FROM canteen_items")
if cursor.fetchone()[0] == 0:
    items = [
        ("ABC", "Beer", 5000),
        ("Heineken", "Beer", 5000),
        ("Tiger", "Beer", 4500),
        ("Chang", "Beer", 4000),
        ("RedBull", "Energy", 3500),
        ("CaraBao", "Energy", 5000),
        ("Shark", "Energy", 3000),
        ("Speed", "Energy", 1500),
        ("Cola", "Drink", 2500),
        ("Sunkite", "Drink", 2000),
        ("Sprite", "Drink", 2000),
        ("Royal-D", "Drink", 2000),
        ("Tamarind", "Drink", 2000),
        ("Passion", "Drink", 1500),
        ("Chips", "Food", 1500),
        ("Mild-7", "Drug", 12000),
        ("Napole", "Drug", 5000),
        ("Mild-7", "Drug", 2000),
        ("Napole", "Drug", 1000)
    ]
    cursor.executemany("INSERT INTO canteen_items (name,type,price) VALUES (?,?,?)", items)
    conn.commit()

# Tables
BIG_TABLES, SMALL_TABLES = 8,5
BIG_RATE, SMALL_RATE = 8500,6500

tables = {}
for i in range(1,BIG_TABLES+1):
    tables[f'B{i}'] = {'type':'Big','rate':BIG_RATE,'customer':'','date':None,'start':None,'end':None,'orders':{}}
for i in range(1,SMALL_TABLES+1):
    tables[f'S{i}'] = {'type':'Small','rate':SMALL_RATE,'customer':'','date':None,'start':None,'end':None,'orders':{}}

# ESC/POS cut command (for thermal POS printers)
CUT_PAPER = "\x1dV0"

# Functions

def refresh_table_view():
    for i in table_overview.get_children():
        table_overview.delete(i)
    for t,data in tables.items():
        table_fee,canteen_fee,grand_total,start_str,end_str,total_time_str = calc_fees(t)
        status,color = ('Available','lightgreen')
        if data['start'] and not data['end']:
            status,color = 'Active','yellow'
        elif data['end']:
            status,color = 'Ended','tomato'
        table_overview.insert('','end',values=(t,data['type'],data['customer'],data['date'],start_str,end_str,total_time_str,table_fee,canteen_fee,grand_total,status),tags=(color,))
    table_overview.tag_configure('lightgreen', background='lightgreen')
    table_overview.tag_configure('yellow', background='yellow')
    table_overview.tag_configure('tomato', background='tomato')
    root.after(1000, refresh_table_view)

def refresh_current_orders():
    for i in order_tree.get_children():
        order_tree.delete(i)
    t = table_var.get()
    if not t: return
    for name,data in tables[t]['orders'].items():
        total = data['price']*data['qty']
        note = data.get('note','')
        order_tree.insert('', 'end', values=(name,data['type'],data['qty'],total,note))

def add_customer():
    t = table_var.get()
    if not t: messagebox.showwarning("Select Table","Please select a table"); return
    tables[t]['customer'] = customer_name.get()
    if tables[t]['date'] is None: tables[t]['date'] = datetime.now().strftime('%Y-%m-%d')
    refresh_table_view()

def start_table():
    t = table_var.get()
    if not t: messagebox.showwarning("Select Table","Please select a table"); return
    tables[t]['start'] = datetime.now()
    if tables[t]['date'] is None: tables[t]['date'] = tables[t]['start'].strftime('%Y-%m-%d')
    tables[t]['end'] = None
    refresh_table_view()

def end_table():
    t = table_var.get()
    if not t or not tables[t]['start']: return
    tables[t]['end'] = datetime.now()
    refresh_table_view()

def add_canteen_item():
    t = table_var.get()
    if not t: messagebox.showwarning("Select Table","Please select a table"); return
    sel = item_tree.selection()
    if not sel: return
    name,typ,price = item_tree.item(sel[0],'values')
    price = float(price)
    note_val = note_text.get()
    if name in tables[t]['orders']:
        tables[t]['orders'][name]['qty'] += 1
        if note_val: tables[t]['orders'][name]['note'] = note_val
    else:
        tables[t]['orders'][name] = {'type':typ,'price':price,'qty':1,'note':note_val}
    note_text.set("")
    refresh_table_view()
    refresh_current_orders()

def calc_fees(t):
    table = tables[t]
    table_fee = 0; total_time_str='-'; start_str='-'; end_str='-'
    if table['start']:
        end_time = table['end'] if table['end'] else datetime.now()
        start_str = table['start'].strftime('%H:%M:%S')
        end_str = end_time.strftime('%H:%M:%S')
        mins = int((end_time - table['start']).total_seconds()/60)
        table_fee = round((mins/60)*table['rate'])
        total_time_str = f"{mins//60}h{mins%60}m"
    canteen_fee = sum(i['price']*i['qty'] for i in table['orders'].values())
    grand_total = table_fee + canteen_fee
    return table_fee,canteen_fee,grand_total,start_str,end_str,total_time_str

def print_receipt():
    t = table_var.get()
    if not t: return
    table = tables[t]
    table_fee,canteen_fee,grand_total,start_str,end_str,total_time_str = calc_fees(t)
    lines=["-----------------------------------------------",
           "         PANDA (2) BILLIARDS & SNOOKER         ",
           "  MyoThitKyi Qt; NaungHkam Main Road, 10 street ",
           "   **************  CASH RECEIPT  ************** ",
            f"Table      : {table['type']}",
            f"Customer   : {table['customer']}", f"Date       : {table['date']}",
            f"Start Time : {start_str}", f"End Time   : {end_str}", f"Total Time : {total_time_str}", f"Table Fee  : Ks {table_fee}",
            "------------ Canteen ----------"]
    for name,data in table['orders'].items():
        note = f" ({data.get('note','')})" if data.get('note') else ''
        total = data['price']*data['qty']
        lines.append(f"{name} x{data['qty']} @ Ks {data['price']}{note} = Ks {total}")
    lines.append(f"Canteen Fee: Ks {canteen_fee}") 
    lines.append("-----------------------------") 
    lines.append(f"Grand Total: Ks {grand_total}")
    lines.append("~~~~~~~~~~~ Thank you, please visit ~~~~~~~~~~")
    lines.append("") 
    text='\n'.join(lines)+ "\n\n\n\n" +CUT_PAPER
     # Add paper cut command for POS printer
    if HAS_WIN32:
        printer_name = win32print.GetDefaultPrinter(); h = win32print.OpenPrinter(printer_name)
        win32print.StartDocPrinter(h,1,("Receipt",None,"RAW")); win32print.StartPagePrinter(h)
        win32print.WritePrinter(h,text.encode('utf-8')+b'\x1D\x56\x00'); win32print.EndPagePrinter(h); win32print.EndDocPrinter(h); win32print.ClosePrinter(h)
    else:
        fname=f"receipt_{t}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"; open(fname,'w',encoding='utf-8').write(text); os.startfile(fname,'print')
   
      
# GUI
root=tk.Tk(); root.title("PANDA II Billiards & Snooker POS")

left_frame=ttk.Frame(root); left_frame.pack(side='left',fill='y',padx=5,pady=5)
table_var=tk.StringVar()
table_cb=ttk.Combobox(left_frame,textvariable=table_var,values=list(tables.keys())); table_cb.pack(pady=5)

ttk.Label(left_frame,text="Customer Name").pack(); customer_name=tk.StringVar(); tk.Entry(left_frame,textvariable=customer_name).pack(pady=5)
ttk.Button(left_frame,text="Add Customer",command=add_customer).pack(pady=5)
ttk.Button(left_frame,text="Start Table",command=start_table).pack(pady=5)
ttk.Button(left_frame,text="End Table",command=end_table).pack(pady=5)
ttk.Button(left_frame,text="Print Receipt",command=print_receipt).pack(pady=5)

# Canteen Items
item_tree=ttk.Treeview(left_frame,columns=("Name","Type","Price"),show='headings',height=8)
for c in ("Name","Type","Price"): item_tree.heading(c,text=c); item_tree.column(c,width=100)
item_tree.pack(pady=5)
cursor.execute("SELECT name,type,price FROM canteen_items"); [item_tree.insert('', 'end', values=row) for row in cursor.fetchall()]

# Note Entry
note_text=tk.StringVar(); tk.Label(left_frame,text="Note").pack(); tk.Entry(left_frame,textvariable=note_text).pack(pady=5)
ttk.Button(left_frame,text="Add Item to Table",command=add_canteen_item).pack(pady=5)

# Current Orders
order_tree=ttk.Treeview(left_frame,columns=("Item","Type","Qty","Total","Note"),show='headings',height=8)
for c in ("Item","Type","Qty","Total","Note"): order_tree.heading(c,text=c); order_tree.column(c,width=100)
order_tree.pack(pady=5)

# Tables overview
right_frame=ttk.Frame(root); right_frame.pack(side='left',fill='both',expand=True,padx=5,pady=5)
cols=("Table","Type","Customer","Date","Start Time","End Time","Total Time","Table Fee","Canteen Fee","Grand Total","Status")
table_overview=ttk.Treeview(right_frame,columns=cols,show='headings')
for c in cols: table_overview.heading(c,text=c); table_overview.column(c,width=100)
table_overview.pack(fill='both',expand=True)

refresh_table_view()
root.mainloop()