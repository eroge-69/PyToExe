#!/usr/bin/env python3
"""
DIT Students Admissions & Fee Management — Professional Tkinter UI

Features:
- Modern toolbar with icon-like buttons, spacing and tooltips
- Edit / Payment / Delete disabled until a row selected
- Keyboard shortcuts: Ctrl+N (Add), Ctrl+E (Edit), Del (Delete), Ctrl+F (Focus Search)
- Search moved to the far right, live filtering and select-first-match behavior
- Alternating row colors, selection highlight, lightweight hover highlight
- About dialog (rightmost toolbar button) with persistent about_info.txt
- File-based storage: students.txt (TSV)
"""
import os
import datetime
import csv
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

# ---------- Config
DATA_FILE = "students.txt"
DELIM = "\t"
APP_TITLE = "IT Point Talash — Students Management (Professional)"
FONT_NORMAL = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 11, "bold")

# ---------- Utilities
class ToolTip:
    """Simple tooltip for widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _e=None):
        if self.tip:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        lbl = ttk.Label(self.tip, text=self.text, background="#333", foreground="white", padding=(6,4))
        lbl.pack()

    def hide(self, _e=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

# ---------- Data layer
class StudentManager:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.ensure_data_file()
        self.students = self.load_students()
        self._build_index()

    def ensure_data_file(self):
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) == 0:
            with open(self.data_file, "w", encoding="utf-8") as f:
                header = ['student_id','name','father_name','class','phone','admission_date','total_fee','paid_amount','notes']
                f.write(DELIM.join(header) + "\n")

    def _build_index(self):
        self._id_index = {(s.get('student_id','') or '').lower(): s for s in self.students if s.get('student_id')}

    def load_students(self):
        self.ensure_data_file()
        rows = []
        with open(self.data_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=DELIM)
            all_rows = list(reader)
            if not all_rows:
                return []
            header = [c.strip().lower() for c in all_rows[0]]
            start = 1 if header == ['student_id','name','father_name','class','phone','admission_date','total_fee','paid_amount','notes'] else 0
            for parts in all_rows[start:]:
                while len(parts) < 9:
                    parts.append('')
                sid, name, father, cls, phone, adm, total_fee, paid_amount, notes = parts[:9]
                try:
                    total_fee = float(total_fee) if total_fee else 0.0
                except:
                    total_fee = 0.0
                try:
                    paid_amount = float(paid_amount) if paid_amount else 0.0
                except:
                    paid_amount = 0.0
                rows.append({
                    'student_id': sid,
                    'name': name,
                    'father_name': father,
                    'class': cls,
                    'phone': phone,
                    'admission_date': adm,
                    'total_fee': total_fee,
                    'paid_amount': paid_amount,
                    'notes': notes,
                })
        return rows

    def save_students(self):
        with open(self.data_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=DELIM)
            writer.writerow(['student_id','name','father_name','class','phone','admission_date','total_fee','paid_amount','notes'])
            for s in self.students:
                writer.writerow([
                    s.get('student_id',''), s.get('name',''), s.get('father_name',''), s.get('class',''), s.get('phone',''),
                    s.get('admission_date',''), f"{s.get('total_fee',0):.2f}", f"{s.get('paid_amount',0):.2f}", s.get('notes','')
                ])
        self._build_index()

    def export_csv(self, path):
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['student_id','name','father_name','class','phone','admission_date','total_fee','paid_amount','notes'])
            for s in self.students:
                writer.writerow([
                    s.get('student_id',''), s.get('name',''), s.get('father_name',''), s.get('class',''), s.get('phone',''),
                    s.get('admission_date',''), f"{s.get('total_fee',0):.2f}", f"{s.get('paid_amount',0):.2f}", s.get('notes','')
                ])

    def generate_student_id(self):
        ids = [s.get('student_id','') for s in self.students if s.get('student_id') and str(s.get('student_id')).startswith('S')]
        maxn = 0
        for sid in ids:
            try:
                n = int(sid[1:])
                if n > maxn:
                    maxn = n
            except:
                continue
        return f"S{maxn+1:03d}"

    # CRUD helpers
    def add_student(self, student):
        self.students.append(student)
        self.save_students()

    def update_student(self, sid, updates):
        for s in self.students:
            if str(s.get('student_id','')).lower() == sid.lower():
                s.update(updates)
                self.save_students()
                return True
        return False

    def delete_student(self, sid):
        before = len(self.students)
        self.students = [s for s in self.students if str(s.get('student_id','')).lower() != sid.lower()]
        if len(self.students) < before:
            self.save_students()
            return True
        return False

    def find_by_id(self, sid):
        if not sid:
            return []
        s = self._id_index.get(sid.lower())
        if s:
            return [s]
        for st in self.students:
            if str(st.get('student_id','')).lower() == sid.lower():
                return [st]
        return []

    def find_by_name(self, name):
        if not name:
            return self.students
        q = name.lower()
        return [s for s in self.students if q in (s.get('name','') or '').lower()]

    def all_ids(self):
        return [s.get('student_id','') for s in self.students if s.get('student_id')]

# ---------- About storage
ABOUT_FILE = 'about_info.txt'

def load_about():
    if not os.path.exists(ABOUT_FILE):
        # return defaults
        return {
            'developer': 'MIFTAH UL ISLAM',
            'education': 'BSCS 3rd Semester  RIPHAH INTERNATIONAL UNIVERSITY',
            'contact': '+92 3485270251',
            'email': 'ulislamk22@gmail.com'
        }
    with open(ABOUT_FILE, 'r', encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f.readlines()]
    # simple parse: each line key:value
    info = {}
    for line in lines:
        if ':' in line:
            k,v = line.split(':',1)
            info[k.strip()] = v.strip()
    # ensure defaults
    defaults = {
        'developer': 'MIFTAH UL ISLAM',
        'education': 'BSCS 3rd Semester  RIPHAH INTERNATIONAL UNIVERSITY',
        'contact': '+92 3485270251',
        'email': 'ulislamk22@gmail.com'
    }
    for k,v in defaults.items():
        info.setdefault(k,v)
    return info

def save_about(info):
    with open(ABOUT_FILE, 'w', encoding='utf-8') as f:
        for k,v in info.items():
            f.write(f"{k}: {v}\n")

class AboutDialog(tk.Toplevel):
    def __init__(self, parent, info=None):
        super().__init__(parent)
        self.title('About / Developer')
        self.resizable(False, False)
        self.info = info or load_about()
        self.result = None
        self.create_widgets()
        self.grab_set()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill='both', expand=True)
        # fields
        labels = [('developer','Developer'), ('education','Education'), ('contact','Contact'), ('email','Email')]
        self.vars = {}
        for i,(k,label) in enumerate(labels):
            ttk.Label(frm, text=label).grid(row=i, column=0, sticky='w', pady=6)
            v = tk.StringVar(value=self.info.get(k,''))
            e = ttk.Entry(frm, textvariable=v, width=56)
            e.grid(row=i, column=1, pady=6, padx=6)
            self.vars[k] = v
        btns = ttk.Frame(frm)
        btns.grid(row=len(labels), column=0, columnspan=2, pady=(10,0))
        ttk.Button(btns, text='Save', command=self.on_save).pack(side='left', padx=6)
        ttk.Button(btns, text='Close', command=self.on_close).pack(side='left', padx=6)

    def on_save(self):
        info = {k: self.vars[k].get().strip() for k in self.vars}
        save_about(info)
        messagebox.showinfo('Saved', 'About details saved.')
        self.destroy()

    def on_close(self):
        self.destroy()

# ---------- Main Application
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry('1150x700')
        self.configure(bg='#f5f7fb')

        # Styles
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except:
            pass
        # HEADER: larger and bold
        self.style.configure('Header.TLabel', background='#2b6ef6', foreground='white', font=("Segoe UI", 18, "bold"), padding=12)
        self.style.configure('Tool.TButton', font=FONT_NORMAL, padding=6)
        self.style.configure('TTreeview', rowheight=26, font=FONT_NORMAL)
        self.style.map('Tool.TButton', foreground=[('disabled','#888')])
        # STATUS (footer): same color as header, larger text
        self.style.configure('Status.TLabel', background='#2b6ef6', foreground='white', font=("Segoe UI", 12), padding=8)

        self.manager = StudentManager()
        self.search_var = tk.StringVar()

        self.create_layout()
        self.bind_shortcuts()
        self.populate_tree()

    def create_layout(self):
        # Header (now larger text and same color later used for footer)
        header = ttk.Label(self, text='IT Point Talash — Student Fee Management System', style='Header.TLabel', anchor='center')
        header.pack(fill='x')

        # Toolbar
        toolbar = ttk.Frame(self, padding=(10,8))
        toolbar.pack(fill='x')

        self.btn_add = ttk.Button(toolbar, text='➕ Add', style='Tool.TButton', command=self.add_student)
        self.btn_add.pack(side='left', padx=4)
        ToolTip(self.btn_add, 'Add new student (Ctrl+N)')

        self.btn_edit = ttk.Button(toolbar, text='✏️ Edit', style='Tool.TButton', command=self.edit_student)
        self.btn_edit.pack(side='left', padx=4)
        ToolTip(self.btn_edit, 'Edit selected student (Ctrl+E)')

        self.btn_payment = ttk.Button(toolbar, text='💳 Payment', style='Tool.TButton', command=self.payment_student)
        self.btn_payment.pack(side='left', padx=4)
        ToolTip(self.btn_payment, 'Record a payment for selected student')

        self.btn_delete = ttk.Button(toolbar, text='🗑️ Delete', style='Tool.TButton', command=self.delete_student)
        self.btn_delete.pack(side='left', padx=4)
        ToolTip(self.btn_delete, 'Delete selected student (Del)')

        self.btn_export = ttk.Button(toolbar, text='📤 Export', style='Tool.TButton', command=self.export_csv)
        self.btn_export.pack(side='left', padx=4)
        ToolTip(self.btn_export, 'Export all students to CSV')

        self.btn_ids = ttk.Button(toolbar, text='📋 IDs', style='Tool.TButton', command=self.open_saved_ids)
        self.btn_ids.pack(side='left', padx=4)
        ToolTip(self.btn_ids, 'Show saved student IDs')

        # spacer -> push search and about to right
        spacer = ttk.Frame(toolbar)
        spacer.pack(side='left', expand=True)

        ttk.Label(toolbar, text='Search', font=FONT_NORMAL).pack(side='left', padx=(0,4))
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=28)
        search_entry.pack(side='left', padx=(0,8))
        search_entry.bind('<KeyRelease>', lambda e: self.populate_tree())
        search_entry.bind('<Return>', lambda e: self.select_first_match())
        ToolTip(search_entry, 'Type name or ID and press Enter to focus the first match (Ctrl+F to focus)')

        # About button at far right
        self.btn_about = ttk.Button(toolbar, text='ℹ️ About', style='Tool.TButton', command=self.open_about)
        self.btn_about.pack(side='left', padx=4)
        ToolTip(self.btn_about, 'About / Developer details')

        # Main area: treeview only (professional card)
        card = ttk.Frame(self, padding=10)
        card.pack(fill='both', expand=True)

        columns = ('student_id','name','father_name','class','phone','paid','total','arrears')
        self.tree = ttk.Treeview(card, columns=columns, show='headings', selectmode='browse')
        headings = {'student_id':'ID','name':'Name','father_name':'Father','class':'Class','phone':'Phone','paid':'Paid','total':'Total','arrears':'Arrears'}
        for c in columns:
            self.tree.heading(c, text=headings[c])
        # column sizing
        self.tree.column('student_id', width=100, anchor='center')
        self.tree.column('name', width=260)
        self.tree.column('father_name', width=220)
        self.tree.column('class', width=100, anchor='center')
        self.tree.column('phone', width=140)
        self.tree.column('paid', width=110, anchor='e')
        self.tree.column('total', width=110, anchor='e')
        self.tree.column('arrears', width=110, anchor='e')

        # scrolling
        vsb = ttk.Scrollbar(card, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(card, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        card.rowconfigure(0, weight=1)
        card.columnconfigure(0, weight=1)

        # tags and styles
        self.tree.tag_configure('ok', foreground='#0a7a2f')   # green
        self.tree.tag_configure('due', foreground='#c92b2b')  # red
        # alternating background
        self.tree.tag_configure('even', background='#ffffff')
        self.tree.tag_configure('odd', background='#fbfdff')

        # events
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.on_select())
        self.tree.bind('<Double-1>', lambda e: self.edit_student())
        self.tree.bind('<Button-3>', self.on_right_click)
        self.tree.bind('<Motion>', self.on_motion)

        # status bar (footer) - now same color as header and larger text
        self.status = ttk.Label(self, text='Ready', anchor='w', style='Status.TLabel')
        self.status.pack(fill='x')

        # initial UI state
        self.set_action_state(selected=False)

    def bind_shortcuts(self):
        self.bind_all('<Control-n>', lambda e: self.add_student())
        self.bind_all('<Control-N>', lambda e: self.add_student())
        self.bind_all('<Control-e>', lambda e: self.edit_student())
        self.bind_all('<Delete>', lambda e: self.delete_student())
        self.bind_all('<Control-f>', lambda e: self.focus_search())

    # ---------- Tree behaviors
    def populate_tree(self):
        # refresh
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self.manager.students = self.manager.load_students()
        self.manager._build_index()

        q = (self.search_var.get() or '').strip()
        if q:
            # if looks like ID attempt id lookup first
            matches = []
            if q.startswith('S') or q.isdigit():
                matches = self.manager.find_by_id(q)
            if not matches:
                matches = self.manager.find_by_name(q)
        else:
            matches = self.manager.students

        for i, s in enumerate(matches):
            arrears = s.get('total_fee',0) - s.get('paid_amount',0)
            tag = 'due' if arrears > 0 else 'ok'
            parity = 'even' if i % 2 == 0 else 'odd'
            vals = (s.get('student_id',''), s.get('name',''), s.get('father_name',''), s.get('class',''), s.get('phone',''), f"{s.get('paid_amount',0):.2f}", f"{s.get('total_fee',0):.2f}", f"{arrears:.2f}")
            self.tree.insert('', 'end', values=vals, tags=(tag, parity))

        self.status.config(text=f"{len(matches)} students shown — Search: '{q}'" if q else f"{len(matches)} students shown")
        self.set_action_state(selected=bool(self.tree.selection()))

    def on_select(self):
        sel = self.tree.selection()
        self.set_action_state(selected=bool(sel))
        if sel:
            sid = self.tree.item(sel[0], 'values')[0]
            self.status.config(text=f"Selected: {sid}")
        else:
            self.status.config(text='Ready')

    def set_action_state(self, selected=False):
        state = '!' + 'disabled' if False else 'disabled'  # no-op placeholder for ttk state API
        # Use ttk.Button.state() with tuple flags to toggle; simpler: enable/disable via state() directly:
        if selected:
            for btn in (self.btn_edit, self.btn_payment, self.btn_delete):
                btn.state(['!disabled'])
        else:
            for btn in (self.btn_edit, self.btn_payment, self.btn_delete):
                btn.state(['disabled'])

    def on_motion(self, event):
        # lightweight hover: highlight row under mouse via temporary tag
        row = self.tree.identify_row(event.y)
        # remove previous hover tag
        for iid in self.tree.get_children():
            current_tags = list(self.tree.item(iid, 'tags'))
            if 'hover' in current_tags:
                current_tags.remove('hover')
                self.tree.item(iid, tags=tuple(current_tags))
        if row:
            tags = list(self.tree.item(row, 'tags'))
            if 'hover' not in tags:
                tags.append('hover')
            self.tree.item(row, tags=tuple(tags))
            # configure hover tag style once
            self.tree.tag_configure('hover', background='#eef6ff')

    def on_right_click(self, event):
        row = self.tree.identify_row(event.y)
        if row:
            self.tree.selection_set(row)
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label='Edit', command=self.edit_student)
            menu.add_command(label='Payment', command=self.payment_student)
            menu.add_separator()
            menu.add_command(label='Delete', command=self.delete_student)
            menu.post(event.x_root, event.y_root)

    def select_first_match(self):
        # select and focus first visible row
        kids = self.tree.get_children()
        if kids:
            self.tree.selection_set(kids[0])
            self.tree.focus(kids[0])
            self.tree.see(kids[0])

    # ---------- Actions
    def focus_search(self):
        # focus the search entry (last widget in toolbar)
        # find entry widget by type
        for w in self.winfo_children():
            for g in w.winfo_children():
                if isinstance(g, ttk.Frame):
                    for ch in g.winfo_children():
                        if isinstance(ch, ttk.Entry):
                            ch.focus_set()
                            return

    def add_student(self):
        dlg = StudentDialog(self, title='Add Student')
        self.wait_window(dlg)
        if dlg.result:
            student = dlg.result
            student['student_id'] = self.manager.generate_student_id()
            student.setdefault('admission_date', datetime.date.today().isoformat())
            self.manager.add_student(student)
            self.populate_tree()
            messagebox.showinfo('Saved', f"Student {student['student_id']} saved.")

    def edit_student(self):
        sid = self.get_selected_id()
        if not sid:
            messagebox.showwarning('No selection', 'Select a student to edit.')
            return
        matches = self.manager.find_by_id(sid)
        if not matches:
            messagebox.showerror('Error', 'Student not found.')
            return
        dlg = StudentDialog(self, title='Edit Student', initial=matches[0])
        self.wait_window(dlg)
        if dlg.result:
            updates = dlg.result
            updates['paid_amount'] = float(updates.get('paid_amount', matches[0].get('paid_amount',0)))
            updates['total_fee'] = float(updates.get('total_fee', matches[0].get('total_fee',0)))
            self.manager.update_student(sid, updates)
            self.populate_tree()
            messagebox.showinfo('Updated', f"Student {sid} updated.")

    def payment_student(self):
        sid = self.get_selected_id()
        if not sid:
            messagebox.showwarning('No selection', 'Select a student for payment.')
            return
        matches = self.manager.find_by_id(sid)
        if not matches:
            messagebox.showerror('Error', 'Student not found.')
            return
        s = matches[0]
        try:
            ans = simpledialog.askfloat('Payment', f"Enter payment amount for {s.get('name','')}:", minvalue=0.0)
        except Exception:
            return
        if ans is None:
            return
        s['paid_amount'] = s.get('paid_amount',0) + float(ans)
        self.manager.save_students()
        self.populate_tree()
        messagebox.showinfo('Payment', f"Payment recorded. New paid amount: {s['paid_amount']:.2f}")

    def delete_student(self):
        sid = self.get_selected_id()
        if not sid:
            messagebox.showwarning('No selection', 'Select a student to delete.')
            return
        if messagebox.askyesno('Confirm', f"Delete {sid}? This cannot be undone."):
            ok = self.manager.delete_student(sid)
            if ok:
                self.populate_tree()
                messagebox.showinfo('Deleted', 'Student deleted.')
            else:
                messagebox.showerror('Error', 'Could not delete student.')

    def export_csv(self):
        fname = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv')], initialfile='students_export.csv')
        if not fname:
            return
        self.manager.export_csv(fname)
        messagebox.showinfo('Exported', f'Exported to: {fname}')

    def open_saved_ids(self):
        ids = self.manager.all_ids()
        win = tk.Toplevel(self)
        win.title('Saved Student IDs')
        win.geometry('360x400')
        ttk.Label(win, text=f'Total saved IDs: {len(ids)}').pack(anchor='w', padx=8, pady=8)
        lb = tk.Listbox(win)
        lb.pack(fill='both', expand=True, padx=8, pady=8)
        for i in ids:
            lb.insert('end', i)

    def open_about(self):
        info = load_about()
        dlg = AboutDialog(self, info=info)
        self.wait_window(dlg)

    def get_selected_id(self):
        sel = self.tree.selection()
        return self.tree.item(sel[0], 'values')[0] if sel else None

# ---------- Dialog (Form)
class StudentDialog(tk.Toplevel):
    def __init__(self, parent, title='Student', initial=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self.initial = initial or {}
        self.create_widgets()
        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self.on_cancel)

    def create_widgets(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill='both', expand=True)
        labels = ['Name','Father','Class','Phone','Admission date (YYYY-MM-DD)','Total fee','Paid amount','Notes']
        self.entries = {}
        for i, lab in enumerate(labels):
            ttk.Label(frm, text=lab).grid(row=i, column=0, sticky='w', pady=4)
            e = ttk.Entry(frm, width=36)
            e.grid(row=i, column=1, pady=4, padx=6)
            self.entries[lab] = e

        # fill initial
        self.entries['Name'].insert(0, self.initial.get('name',''))
        self.entries['Father'].insert(0, self.initial.get('father_name',''))
        self.entries['Class'].insert(0, self.initial.get('class',''))
        self.entries['Phone'].insert(0, self.initial.get('phone',''))
        self.entries['Admission date (YYYY-MM-DD)'].insert(0, self.initial.get('admission_date', datetime.date.today().isoformat()))
        self.entries['Total fee'].insert(0, f"{self.initial.get('total_fee',0):.2f}" if self.initial.get('total_fee') is not None else '')
        self.entries['Paid amount'].insert(0, f"{self.initial.get('paid_amount',0):.2f}" if self.initial.get('paid_amount') is not None else '')
        self.entries['Notes'].insert(0, self.initial.get('notes',''))

        btns = ttk.Frame(frm)
        btns.grid(row=len(labels), column=0, columnspan=2, pady=(10,0))
        ttk.Button(btns, text='Save', command=self.on_save).pack(side='left', padx=6)
        ttk.Button(btns, text='Cancel', command=self.on_cancel).pack(side='left', padx=6)

    def on_save(self):
        try:
            total_fee = float(self.entries['Total fee'].get() or '0')
            paid_amount = float(self.entries['Paid amount'].get() or '0')
        except ValueError:
            messagebox.showerror('Invalid', 'Please enter valid numbers for fees.')
            return
        self.result = {
            'name': self.entries['Name'].get().strip(),
            'father_name': self.entries['Father'].get().strip(),
            'class': self.entries['Class'].get().strip(),
            'phone': self.entries['Phone'].get().strip(),
            'admission_date': self.entries['Admission date (YYYY-MM-DD)'].get().strip() or datetime.date.today().isoformat(),
            'total_fee': total_fee,
            'paid_amount': paid_amount,
            'notes': self.entries['Notes'].get().strip(),
        }
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

# ---------- Run
if __name__ == '__main__':
    app = App()
    app.mainloop()
