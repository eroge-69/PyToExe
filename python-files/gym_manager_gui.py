import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from tkinter import PhotoImage
import csv
import os
from datetime import datetime

DATA_FILE = 'members.csv'
PLANS_FILE = 'plans.csv'
LOGO_FILE = 'gym_logo.png'  # Placeholder logo file

FIELDS = ['Name', 'Plan', 'DateOfJoining', 'Phone', 'Address', 'FeePaid']

# Ensure the CSV file exists with headers
def init_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)

def load_members():
    members = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                members.append(row)
    return members

def save_members(members):
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(members)

def add_member(data):
    members = load_members()
    for m in members:
        if m['Name'].lower() == data['Name'].lower():
            return False
    members.append(data)
    save_members(members)
    return True

def update_member(name, field, value):
    members = load_members()
    updated = False
    for m in members:
        if m['Name'].lower() == name.lower():
            m[field] = value
            updated = True
            break
    if updated:
        save_members(members)
    return updated

# Plan management
def init_plans_file():
    if not os.path.exists(PLANS_FILE):
        with open(PLANS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Plan', 'MonthlyFee'])
            writer.writerow(['Gold', '5000'])
            writer.writerow(['Silver', '3000'])

def load_plans():
    plans = {}
    if os.path.exists(PLANS_FILE):
        with open(PLANS_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                plans[row['Plan'].lower()] = row['MonthlyFee']
    return plans

def save_plans(plans):
    with open(PLANS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Plan', 'MonthlyFee'])
        writer.writeheader()
        for plan, fee in plans.items():
            writer.writerow({'Plan': plan.capitalize(), 'MonthlyFee': fee})

ATTENDANCE_FILE = 'attendance.csv'

def init_attendance_file():
    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Date', 'Status'])

def mark_attendance(name, date, status):
    records = []
    found = False
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Name'].lower() == name.lower() and row['Date'] == date:
                    row['Status'] = status
                    found = True
                records.append(row)
    if not found:
        records.append({'Name': name, 'Date': date, 'Status': status})
    with open(ATTENDANCE_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'Date', 'Status'])
        writer.writeheader()
        writer.writerows(records)

def remove_member(name):
    members = load_members()
    members = [m for m in members if m['Name'].lower() != name.lower()]
    save_members(members)
    # Remove attendance records for this member
    if os.path.exists(ATTENDANCE_FILE):
        records = []
        with open(ATTENDANCE_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Name'].lower() != name.lower():
                    records.append(row)
        with open(ATTENDANCE_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Name', 'Date', 'Status'])
            writer.writeheader()
            writer.writerows(records)

class PlansManager(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title('Manage Plans')
        self.geometry('300x200')
        self.plans = load_plans()
        self.entries = {}
        row = 0
        for plan in ['gold', 'silver']:
            tk.Label(self, text=f'{plan.capitalize()} Plan Fee:').grid(row=row, column=0, sticky='e', pady=10)
            entry = tk.Entry(self)
            entry.grid(row=row, column=1)
            entry.insert(0, self.plans.get(plan, ''))
            self.entries[plan] = entry
            row += 1
        tk.Button(self, text='Save', command=self.save).grid(row=row, column=0, columnspan=2, pady=20)
    def save(self):
        new_plans = {plan: self.entries[plan].get().strip() for plan in self.entries}
        if not all(new_plans.values()):
            messagebox.showwarning('Input Error', 'Please enter all fees.')
            return
        save_plans(new_plans)
        messagebox.showinfo('Success', 'Plan fees updated!')
        self.destroy()

class DailyAttendanceWindow(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title('Daily Attendance')
        self.geometry('500x500')
        self.date_var = tk.StringVar()
        self.date_var.set(datetime.now().strftime('%Y-%m-%d'))
        tk.Label(self, text='Date (YYYY-MM-DD):').pack(pady=5)
        date_entry = tk.Entry(self, textvariable=self.date_var, width=12)
        date_entry.pack(pady=5)
        tk.Button(self, text='Load', command=self.refresh).pack(pady=5)
        self.members_frame = tk.Frame(self)
        self.members_frame.pack(fill='both', expand=True, pady=10)
        self.refresh()
    def refresh(self):
        for widget in self.members_frame.winfo_children():
            widget.destroy()
        date = self.date_var.get().strip()
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            tk.Label(self.members_frame, text='Invalid date format!').pack()
            return
        members = load_members()
        if not members:
            tk.Label(self.members_frame, text='No members found.').pack()
            return
        tk.Label(self.members_frame, text=f'Attendance for {date}', font=('Arial', 12, 'bold')).pack(pady=5)
        for m in members:
            row = tk.Frame(self.members_frame)
            row.pack(fill='x', pady=2)
            tk.Label(row, text=m['Name'], width=20, anchor='w').pack(side='left')
            status = self.get_attendance(m['Name'], date)
            status_var = tk.StringVar(value=status)
            tk.Label(row, textvariable=status_var, width=10).pack(side='left')
            tk.Button(row, text='Present', command=lambda n=m['Name']: self.set_attendance(n, date, 'Present')).pack(side='left', padx=2)
            tk.Button(row, text='Absent', command=lambda n=m['Name']: self.set_attendance(n, date, 'Absent')).pack(side='left', padx=2)
    def get_attendance(self, name, date):
        if os.path.exists(ATTENDANCE_FILE):
            with open(ATTENDANCE_FILE, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Name'].lower() == name.lower() and row['Date'] == date:
                        return row['Status']
        return ''
    def set_attendance(self, name, date, status):
        mark_attendance(name, date, status)
        self.refresh()

class GymManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Gym Management System')
        self.create_widgets()
        self.refresh_table()
        init_attendance_file()
        init_plans_file()

    def create_widgets(self):
        # Logo
        try:
            self.logo_img = PhotoImage(file=LOGO_FILE)
            tk.Label(self.root, image=self.logo_img).pack(pady=5)
        except Exception:
            pass
        # Search bar
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=2)
        tk.Label(search_frame, text='Search:').pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh_table())
        tk.Entry(search_frame, textvariable=self.search_var, width=20).pack(side='left', padx=2)
        tk.Label(search_frame, text='Plan:').pack(side='left')
        self.plan_var = tk.StringVar()
        self.plan_var.set('All')
        plan_options = ['All', 'Gold', 'Silver']
        tk.OptionMenu(search_frame, self.plan_var, *plan_options, command=lambda _: self.refresh_table()).pack(side='left')
        # Stats
        self.stats_label = tk.Label(self.root, text='', font=('Arial', 10, 'bold'))
        self.stats_label.pack(pady=2)
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # Registration fields
        labels = ['Name', 'Plan (Gold/Silver)', 'Date of Joining (YYYY-MM-DD)', 'Phone', 'Address', 'Fee Paid (Yes/No)']
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(frame, text=label+':').grid(row=i, column=0, sticky='e')
            entry = tk.Entry(frame)
            entry.grid(row=i, column=1)
            self.entries[FIELDS[i]] = entry
        tk.Button(frame, text='Add Member', command=self.add_member).grid(row=len(labels), column=0, columnspan=2, pady=5)
        tk.Button(frame, text='Manage Plans', command=self.open_plans_manager).grid(row=len(labels)+1, column=0, columnspan=2, pady=5)
        tk.Button(frame, text='Daily Attendance', command=self.open_daily_attendance).grid(row=len(labels)+2, column=0, columnspan=2, pady=5)
        tk.Button(frame, text='Remove Member', command=self.remove_selected_member).grid(row=len(labels)+3, column=0, columnspan=2, pady=5)

        # Attendance marking
        att_frame = tk.Frame(self.root)
        att_frame.pack(padx=10, pady=5)
        tk.Label(att_frame, text='Attendance for selected member:').pack(side='left')
        self.att_date_entry = tk.Entry(att_frame, width=12)
        self.att_date_entry.pack(side='left')
        self.att_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        tk.Button(att_frame, text='Mark Present', command=lambda: self.mark_attendance('Present')).pack(side='left', padx=2)
        tk.Button(att_frame, text='Mark Absent', command=lambda: self.mark_attendance('Absent')).pack(side='left', padx=2)

        # Table
        self.tree = ttk.Treeview(self.root, columns=FIELDS, show='headings')
        for field in FIELDS:
            self.tree.heading(field, text=field)
        self.tree.pack(padx=10, pady=10, fill='x')
        self.tree.bind('<Double-1>', self.edit_member)

        tk.Button(self.root, text='Refresh', command=self.refresh_table).pack(pady=5)

    def add_member(self):
        data = {field: self.entries[field].get().strip() for field in FIELDS}
        if not all(data.values()):
            messagebox.showwarning('Input Error', 'Please fill all fields.')
            return
        # Validate date
        try:
            datetime.strptime(data['DateOfJoining'], '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning('Input Error', 'Date of Joining must be YYYY-MM-DD.')
            return
        if data['Plan'].lower() not in ['gold', 'silver']:
            messagebox.showwarning('Input Error', 'Plan must be Gold or Silver.')
            return
        if data['FeePaid'].lower() not in ['yes', 'no']:
            messagebox.showwarning('Input Error', 'Fee Paid must be Yes or No.')
            return
        if add_member(data):
            messagebox.showinfo('Success', f"Member {data['Name']} added.")
            self.refresh_table()
        else:
            messagebox.showerror('Error', 'Member already exists.')

    def get_selected_member(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Selection Error', 'Please select a member from the table.')
            return None
        values = self.tree.item(selected[0])['values']
        member = {FIELDS[i]: values[i] for i in range(len(FIELDS))}
        return member

    def mark_attendance(self, status):
        member = self.get_selected_member()
        if not member:
            return
        date = self.att_date_entry.get().strip()
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning('Input Error', 'Date must be YYYY-MM-DD.')
            return
        mark_attendance(member['Name'], date, status)
        messagebox.showinfo('Success', f"Attendance for {member['Name']} on {date} marked as {status}.")

    def refresh_table(self):
        search = self.search_var.get().strip().lower() if hasattr(self, 'search_var') else ''
        plan_filter = self.plan_var.get().lower() if hasattr(self, 'plan_var') else 'all'
        for row in self.tree.get_children():
            self.tree.delete(row)
        members = load_members()
        filtered = []
        for m in members:
            if search and search not in m['Name'].lower():
                continue
            if plan_filter != 'all' and m['Plan'].lower() != plan_filter:
                continue
            filtered.append(m)
            self.tree.insert('', 'end', values=[m[field] for field in FIELDS])
        # Stats
        today = datetime.now().strftime('%Y-%m-%d')
        present = 0
        absent = 0
        for m in filtered:
            status = ''
            if os.path.exists(ATTENDANCE_FILE):
                with open(ATTENDANCE_FILE, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['Name'].lower() == m['Name'].lower() and row['Date'] == today:
                            status = row['Status']
                            break
            if status == 'Present':
                present += 1
            elif status == 'Absent':
                absent += 1
        self.stats_label.config(text=f'Total Members: {len(filtered)}   Present Today: {present}   Absent Today: {absent}')

    def open_plans_manager(self):
        PlansManager(self.root)

    def open_daily_attendance(self):
        DailyAttendanceWindow(self.root)

    def edit_member(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        values = self.tree.item(item)['values']
        member = {FIELDS[i]: values[i] for i in range(len(FIELDS))}
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Edit Member: {member['Name']}")
        edit_win.geometry('350x300')
        entries = {}
        for i, field in enumerate(['Plan', 'FeePaid']):
            tk.Label(edit_win, text=field+':').grid(row=i, column=0, sticky='e', pady=10)
            entry = tk.Entry(edit_win)
            entry.grid(row=i, column=1)
            entry.insert(0, member[field])
            entries[field] = entry
        def save_edit():
            new_plan = entries['Plan'].get().strip()
            new_fee = entries['FeePaid'].get().strip()
            if new_plan.lower() not in ['gold', 'silver']:
                messagebox.showwarning('Input Error', 'Plan must be Gold or Silver.')
                return
            if new_fee.lower() not in ['yes', 'no']:
                messagebox.showwarning('Input Error', 'Fee Paid must be Yes or No.')
                return
            update_member(member['Name'], 'Plan', new_plan)
            update_member(member['Name'], 'FeePaid', new_fee)
            messagebox.showinfo('Success', 'Member updated!')
            self.refresh_table()
            edit_win.destroy()
        tk.Button(edit_win, text='Save', command=save_edit).grid(row=2, column=0, columnspan=2, pady=20)

    def remove_selected_member(self):
        member = self.get_selected_member()
        if not member:
            return
        if messagebox.askyesno('Confirm', f"Remove member '{member['Name']}'? This will also delete their attendance records."):
            remove_member(member['Name'])
            messagebox.showinfo('Removed', f"Member '{member['Name']}' removed.")
            self.refresh_table()

class SplashScreen(tk.Toplevel):
    def __init__(self, root, on_close):
        super().__init__(root)
        self.on_close = on_close
        self.title('Welcome')
        self.geometry('400x250')
        self.configure(bg='black')
        try:
            self.logo_img = PhotoImage(file=LOGO_FILE)
            tk.Label(self, image=self.logo_img, bg='black').pack(pady=10)
        except Exception:
            pass
        self.label = tk.Label(self, text='', font=('Arial', 20, 'bold'), fg='lime', bg='black')
        self.label.pack(expand=True)
        self.text = 'Welcome to Gym Manager!'
        self.index = 0
        self.after(100, self.animate)
        self.after(2500, self.close)
        self.protocol('WM_DELETE_WINDOW', lambda: None)  # Disable close

    def animate(self):
        if self.index < len(self.text):
            self.label.config(text=self.label.cget('text') + self.text[self.index])
            self.index += 1
            self.after(80, self.animate)

    def close(self):
        self.destroy()
        self.on_close()

def main():
    init_data_file()
    init_attendance_file()
    init_plans_file()
    root = tk.Tk()
    root.withdraw()  # Hide main window initially
    def show_main():
        root.deiconify()
        GymManagerApp(root)
    splash = SplashScreen(root, show_main)
    root.mainloop()

if __name__ == '__main__':
    main() 