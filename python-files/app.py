import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime, timedelta
import openpyxl
import os
import sys

# Połączenie z bazą (ścieżka na dysku sieciowym)
DB_PATH = r"S:\DDP\PDK\Certyfikacja\_SPRAWDZENIA\_Oprogramowanie\Baza Danych Wzorców\equipment.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Dodanie kolumny next_calibration jeśli jej brak
try:
    c.execute("ALTER TABLE equipment ADD COLUMN next_calibration DATE")
except sqlite3.OperationalError:
    pass

# Tworzenie tabeli
c.execute('''
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    manufacturer TEXT,
    model TEXT,
    rfid TEXT,
    inventory_number TEXT,
    category TEXT,
    location TEXT,
    station_number TEXT,
    calibration_date DATE,
    status TEXT,
    valid_until DATE,
    certificate_number TEXT,
    certificate_path TEXT,
    sonel_number TEXT,
    remarks TEXT,
    next_calibration DATE
)
''')
conn.commit()

# Kategorie wzorcowania i okres (miesiące)
CATEGORY_PERIODS = {
    "Multimetry": 12, "Rezystory stałe": 24, "Kalibratory": 12,
    "Mierniki produkcji Sonel": 12, "Kalibratory rezystancji": 24,
    "Dekady Rezystancyjne": 12,
    "Termohigrometry": 24, "Sondy pomiarowe (HV)": 24,
    "Elektroniczny symulator RCD": 24, "Cewki LN-1": 60,
    "Oscyloskopy (Przegląd)": 12, "Pozostałe cewko (Przegląd)": 24,
    "Zasilacze (Przegląd)": 12,
    "Wysokonapięciowy tester izolacji (przegląd)": 36
    }

USERS = {"laborant": "laborant1", "kalibracja": "kalibracja1"}
CURRENT_USER = None
EDIT_ID = None

# GUI elements
fields = {}
tree = None
search_var = None

# Pomocnicze funkcje

def calculate_next_calibration(cal_date_str, category):
    try:
        cal = datetime.strptime(cal_date_str, "%Y-%m-%d").date()
        m = CATEGORY_PERIODS.get(category, 12)
        month = cal.month - 1 + m
        year = cal.year + month // 12
        month = month % 12 + 1
        day = min(cal.day, 28)
        return datetime(year, month, day).strftime("%Y-%m-%d")
    except:
        return cal_date_str

# CRUD functions

def clear_fields():
    global EDIT_ID
    EDIT_ID = None
    for widget in fields.values():
        if widget is None:
            continue
        # DateEntry
        if hasattr(widget, 'get_date'):
            try:
                widget.set_date(datetime.today())
            except:
                pass
        # Combobox
        elif isinstance(widget, ttk.Combobox):
            try:
                widget.set('')
            except:
                pass
        # Entry or similar
        elif hasattr(widget, 'delete'):
            try:
                widget.delete(0, tk.END)
            except:
                pass


def save_equipment():
    global EDIT_ID
    vals = {k: (w.get_date().strftime("%Y-%m-%d") if isinstance(w, DateEntry) else w.get()) for k, w in fields.items()}
    # walidacja
    required = ["name","manufacturer","model","station_number","status"]
    missing = [f for f in required if not vals[f]]
    if missing:
        messagebox.showwarning("Błąd", f"Uzupełnij: {', '.join(missing)}")
        return
    # unikalność modelu (serial)
    if EDIT_ID is None and vals['model'].lower() != 'brak':
        c.execute("SELECT 1 FROM equipment WHERE model=?", (vals['model'],))
        if c.fetchone():
            messagebox.showerror("Błąd","Taki numer seryjny już istnieje.")
            return
    # next calibration
    vals['next_calibration'] = calculate_next_calibration(vals['calibration_date'], vals['category'])
    params = (
        vals['name'], vals['manufacturer'], vals['model'], vals['rfid'], vals['inventory_number'],
        vals['category'], vals['location'], vals['station_number'], vals['calibration_date'], vals['status'],
        vals['valid_until'], vals['certificate_number'], vals['certificate_path'], vals['sonel_number'],
        vals['remarks'], vals['next_calibration']
    )
    if EDIT_ID:
        c.execute('''
            UPDATE equipment SET
                name=?, manufacturer=?, model=?, rfid=?, inventory_number=?, category=?, location=?,
                station_number=?, calibration_date=?, status=?, valid_until=?,
                certificate_number=?, certificate_path=?, sonel_number=?, remarks=?, next_calibration=?
            WHERE id=?
        ''', params + (EDIT_ID,))
        messagebox.showinfo("OK","Zaktualizowano.")
        EDIT_ID = None
    else:
        c.execute('''
            INSERT INTO equipment (
                name, manufacturer, model, rfid, inventory_number, category, location,
                station_number, calibration_date, status, valid_until,
                certificate_number, certificate_path, sonel_number, remarks, next_calibration
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', params)
        messagebox.showinfo("OK","Dodano.")
    conn.commit()
    clear_fields()
    refresh_table()


def delete_selected():
    sel = tree.selection()
    if not sel: return
    if not messagebox.askyesno("Potwierdzenie","Czy na pewno usunąć wpis? "): return
    cid = tree.item(sel)['values'][0]
    c.execute("DELETE FROM equipment WHERE id=?", (cid,))
    conn.commit()
    refresh_table()


def edit_selected():
    global EDIT_ID
    sel = tree.selection()
    if not sel: return
    row = tree.item(sel)['values']
    EDIT_ID = row[0]
    keys = list(fields.keys())
    for i, k in enumerate(keys):
        w = fields[k]
        val = row[i+1]
        if isinstance(w, DateEntry):
            w.set_date(val)
        else:
            w.delete(0, tk.END)
            w.insert(0, val)


def refresh_table():
    tree.delete(*tree.get_children())
    today = datetime.today().date()
    for row in c.execute("SELECT * FROM equipment"):
        nc_str = row[-1]
        try:
            nc = datetime.strptime(nc_str, "%Y-%m-%d").date() if nc_str else None
        except:
            nc = None
        tag = ''
        if nc:
            days = (nc - today).days
            if days > 30:
                tag = ''
            elif days >= 10:
                tag = 'yellow'
            elif days >= 1:
                tag = 'orange'
            else:
                tag = 'red'
        tree.insert('', tk.END, values=row, tags=(tag,))
    tree.tag_configure('yellow', background='khaki')
    tree.tag_configure('orange', background='orange')
    tree.tag_configure('red', background='lightcoral')

# Ensure sortby follows

def sortby(tv, col, descending):
    data = [(tv.set(child, col), child) for child in tv.get_children('')]
    try:
        data.sort(key=lambda t: datetime.strptime(t[0], "%Y-%m-%d"), reverse=descending)
    except:
        data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tv.move(item[1], '', ix)
    tv.heading(col, command=lambda: sortby(tv, col, not descending))


def search_equipment():
    kw = search_var.get()
    tree.delete(*tree.get_children())
    q = """
    SELECT * FROM equipment 
    WHERE name LIKE ? OR model LIKE ? OR rfid LIKE ? OR inventory_number LIKE ? OR station_number LIKE ?
    """
    for row in c.execute(q, (f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%")):
        tree.insert('', tk.END, values=row)


def import_from_excel():
    path = filedialog.askopenfilename(filetypes=[("Excel files","*.xlsx")])
    if not path:
        return
    try:
        wb = openpyxl.load_workbook(path)
        ws = wb.active
        # Header mapping
        headers = [cell.value for cell in ws[1]]
        idx = {header: i for i, header in enumerate(headers)}
        # Expected columns
        cols = ["name","manufacturer","model","rfid","inventory_number","category",
                "location","station_number","calibration_date","status","valid_until",
                "certificate_number","certificate_path","sonel_number","remarks"]
        for row in ws.iter_rows(min_row=2, values_only=True):
            values = {}
            for col in cols:
                if col in idx:
                    values[col] = row[idx[col]]
                else:
                    values[col] = None
            # Skip if required missing
            req = ["name","manufacturer","model","station_number","status"]
            if any(not values.get(r) for r in req):
                continue
            cal_date = values.get('calibration_date')
            cal_str = cal_date.strftime("%Y-%m-%d") if isinstance(cal_date, datetime) else str(cal_date) if cal_date else None
            next_cal = calculate_next_calibration(cal_str, values.get('category'))
            params = (
                values.get('name'), values.get('manufacturer'), values.get('model'), values.get('rfid'),
                values.get('inventory_number'), values.get('category'), values.get('location'), values.get('station_number'),
                cal_str, values.get('status'), values.get('valid_until'), values.get('certificate_number'),
                values.get('certificate_path'), values.get('sonel_number'), values.get('remarks'), next_cal
            )
            c.execute('''INSERT INTO equipment (name,manufacturer,model,rfid,inventory_number,category,location,station_number,calibration_date,status,valid_until,certificate_number,certificate_path,sonel_number,remarks,next_calibration) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', params)
        conn.commit()
        refresh_table()
        messagebox.showinfo("Import","Dane zaimportowane.")
    except Exception as e:
        messagebox.showerror("Błąd importu", str(e))

def export_to_excel():
    file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
    if not file:
        return
    wb = openpyxl.Workbook()
    ws = wb.active
    cols = ["id"] + list(fields.keys()) + ["next_calibration"]
    ws.append(cols)
    for item in tree.get_children():
        ws.append(tree.item(item)['values'])
    wb.save(file)
    messagebox.showinfo("Eksport","Zapisano do pliku.")


def login():
    login_win = tk.Tk()
    login_win.title("Logowanie")

    tk.Label(login_win, text="Login:").grid(row=0, column=0)
    entry_login = tk.Entry(login_win)
    entry_login.grid(row=0, column=1)

    tk.Label(login_win, text="Hasło:").grid(row=1, column=0)
    entry_password = tk.Entry(login_win, show="*")
    entry_password.grid(row=1, column=1)

    def check_login():
        global CURRENT_USER
        user = entry_login.get()
        password = entry_password.get()
        if user in USERS and USERS[user] == password:
            CURRENT_USER = user
            login_win.destroy()
            start_main_window(user)
        else:
            messagebox.showerror("Błąd", "Nieprawidłowy login lub hasło")

    tk.Button(login_win, text="Zaloguj", command=check_login).grid(row=2, column=0, columnspan=2)
    login_win.mainloop()


def start_main_window(user):
    global tree, fields, search_var
    root = tk.Tk()
    root.title("Rejestr Sprzętu")
    # Skalowanie
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{int(w*0.8)}x{int(h*0.8)}")
    # Definicja pól
    specs = [
        ("name","Nazwa"), ("manufacturer","Producent"), ("model","Numer seryjny"), ("rfid","RFID"),
        ("inventory_number","Nr inwentarzowy"), ("category","Kategoria wzorca"), ("location","Lokalizacja"),
        ("station_number","Numer stanowiska"), ("calibration_date","Data wzorcowania"), ("valid_until","Data ważności"),
        ("status","Status"), ("certificate_number","Nr świadectwa"), ("certificate_path","Ścieżka świadectwa"),
        ("sonel_number","Nr wew. Sonel"), ("remarks","Uwagi")
    ]
    for i,(key,label) in enumerate(specs):
        tk.Label(root, text=label).grid(row=i, column=0, sticky='e')
        if key in ["calibration_date","valid_until"]:
            widget = DateEntry(root, date_pattern='yyyy-mm-dd')
        elif key == "status":
            widget = ttk.Combobox(root, values=["Naprawa","Wzorcowanie","Kasacja","W użyciu"])
        elif key == "category":
            widget = ttk.Combobox(root, values=list(CATEGORY_PERIODS.keys()))
        elif key == "certificate_path":
            frame = tk.Frame(root)
            widget = tk.Entry(frame)
            btn = tk.Button(frame, text="...", command=lambda e=key: browse_file())
            widget.pack(side='left')
            btn.pack(side='left')
            frame.grid(row=i,column=1)
            fields[key] = widget
            continue
        else:
            widget = tk.Entry(root)
        widget.grid(row=i, column=1, sticky='we')
        fields[key] = widget
        if key in ["name","manufacturer","model","station_number","status"] and user=="kalibracja":
            widget.configure(state='readonly')
    # Buttony
    tk.Button(root, text="Zapisz", command=save_equipment).grid(row=len(specs), column=0)
    tk.Button(root, text="Usuń", command=delete_selected).grid(row=len(specs), column=1)
    tk.Button(root, text="Edytuj", command=edit_selected).grid(row=len(specs), column=2)
    tk.Button(root, text="Importuj z Excela", command=import_from_excel).grid(row=len(specs)+1, column=0)
    tk.Button(root, text="Eksportuj do Excela", command=export_to_excel).grid(row=len(specs)+1, column=1)
    # Search
    search_var = tk.StringVar()
    tk.Entry(root, textvariable=search_var).grid(row=len(specs)+2, column=0)
    tk.Button(root, text="Szukaj", command=search_equipment).grid(row=len(specs)+2, column=1)
    # Tabela
    cols = ["id"] + [k for k,_ in specs] + ["next_calibration"]
    tree = ttk.Treeview(root, columns=cols, show='headings')
    for ccol in cols:
        tree.heading(ccol, text=ccol, command=lambda _c=ccol: sortby(tree,_c,False))
        tree.column(ccol, width=100)
    tree.grid(row=0, column=3, rowspan=len(specs)+3, sticky='nsew')
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(3, weight=1)
    refresh_table()
    root.mainloop()

if __name__ == "__main__":
    login()
