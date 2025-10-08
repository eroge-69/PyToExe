from datetime import date, datetime
from zk import ZK
import json
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import DateEntry
from ttkbootstrap.dialogs import Messagebox


class DeviceUsers():
    def get_attendance(device):
        try:
            with ConnectToDevice(device["ip_address"], device["port"], device["device_password"]) as conn:
                print("Connection Successfully")
                attendances = conn.get_attendance()
                device_attendance = [[x.user_id, x.timestamp, x.punch] for x in attendances]
            return device_attendance
        except:
            Messagebox.show_error(message="Can't reach Fingerprint Device", title="Error")
            return []

class ConnectToDevice(object):
    def __init__(self, ip_address, port, device_password):
        try:
            zk = ZK(ip_address, port,timeout = 10, password=device_password, force_udp=False, ommit_ping=True)
            conn = zk.connect()
        except Exception as e:
            raise print(e)
        conn.disable_device()
        self.conn = conn

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.enable_device()

def test_connection():
    if not all(f.get() for f in entries):
        Messagebox.show_error(message="Please Fill All Field", title="Error")
        return
    try:
        with ConnectToDevice(entries[0].get(), int(entries[1].get()), int(entries[2].get())) as conn:
            if conn:
                Messagebox.show_info(title="Success", message="Fingerprint Device Connected!")
    except:
        Messagebox.show_error(message="Can't reach Fingerprint Device", title="Error")
        return

# # Clear form
def clear_fields():
    all_entries = entries + entries_date
    for f in all_entries:
        f.delete(0, tk.END)

# Move to next field
def focus_next(entry):
    entry.focus_set()

def from_fingerprint_to_array():
    data = {}
    with open('fingerprint_data.json', 'r') as f:
        attendances = json.load(f)
        for attendance in attendances:
            fingerprint = attendance['fingerprint']
            datetime_from_data = attendance['datetime']
            punch = attendance['punch']
            date_from_attendance = datetime_from_data.split()[0]
            if not fingerprint in data:
                data[fingerprint] = {}
            if not date_from_attendance in data[fingerprint]:
                data[fingerprint][date_from_attendance] = []
            data[fingerprint][date_from_attendance].append([datetime_from_data, punch])
        with open('attendance_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def processed_data_from_array():
    processed_data = []
    with open('attendance_data.json', 'r') as f:
        data = json.load(f)
        for fingerprint in data:
            attendances = data[fingerprint]
            for key_date in attendances:
                check_in = ''
                check_out = ''
                for attendance in attendances[key_date]:
                    if attendance[1] == 0 and int(attendance[0].split()[1][0:2]) < 17:
                        check_in = attendance[0]
                    if attendance[1] == 1 or int(attendance[0].split()[1][0:2]) > 17:
                        check_out = attendance[0]
                if check_in == '':
                    check_in = '%s 08:00:00' % key_date
                if check_out == '':
                    check_out = '%s 17:30:00' % key_date 
                processed_data.append({
                    'check_in': check_in,
                    'check_out': check_out,
                    'date': key_date,
                    'fingerprint': fingerprint
                })
        with open('processed_data.json', 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)

def export_json():
    ip_address = entries[0].get()
    port = int(entries[1].get())
    device_password = int(entries[2].get())

    data = []
    device = {
        "ip_address": ip_address,
        "port": port,
        "device_password": device_password,
    }
    attendances = DeviceUsers.get_attendance(device)
    start_date = entries_date[0].get_date().date()
    end_date = entries_date[1].get_date().date()
    for attendance in attendances:
        attendance_date = attendance[1].date()
        if not (attendance_date < start_date or attendance_date > end_date):
            data.append({
                "fingerprint": attendance[0],
                "datetime": attendance[1].strftime('%Y-%m-%d %H:%M:%S'),
                'punch': attendance[2]
            })
    with open('fingerprint_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def export_data():
    try:
        export_json()
        from_fingerprint_to_array()
        processed_data_from_array()
        Messagebox.show_info(title="Success", message="Successfully Export Data!")
    except Exception as e:
        Messagebox.show_error(message="Failed to export data %s" % str(e), title="Error")
        return

# Create the main window
root = tk.Tk()
root.title("Export Data Fingerprint")
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

# Create a label
label = tk.Label(root, text="Please Fill Form!")
label.grid(row=0, column=0, columnspan=2, pady=20)

# form
labels = ["IP Device", "Port Device", "Password Device"]
entries = [tk.Entry(root) for _ in labels]
labels_date = ["Start Date", "End Date"]
entries_date = [DateEntry(root, dateformat="%Y-%m-%d") for _ in labels_date]

last_row = 0
for i, lbl in enumerate(labels):
    tk.Label(root, text=lbl).grid(row=i+1, column=0, sticky='W', padx=5, pady=5)
    entries[i].grid(row=i+1, column=1, sticky='EW', padx=5, pady=5)
    if lbl == 'IP Device':
        entries[i].insert(END, '192.168.1.3')
    if lbl == 'Port Device':
        entries[i].insert(END, '4370')
    if lbl == 'Password Device':
        entries[i].insert(END, '0')
    if i < len(labels) - 1:
        entries[i].bind("<Return>", lambda e, nf=entries[i+1]: focus_next(nf))
    last_row += 1

for i, lbl in enumerate(labels_date):
    tk.Label(root, text=lbl).grid(row=i+last_row+1, column=0, sticky='W', padx=5, pady=5)
    entries_date[i].grid(row=i+last_row+1, column=1, sticky='EW', padx=5, pady=5)
    if i < len(labels_date) - 1:
        entries_date[i].bind("<Return>", lambda e, nf=entries_date[i+1]: focus_next(nf))
    last_row += 1

button = ttk.Button(root, text="Export Data", bootstyle=SUCCESS, command=export_data)
button.grid(row=last_row + 2, column=1, pady=5, padx=5, sticky='EW')

button = ttk.Button(root, text="Test Connection", bootstyle=(INFO, OUTLINE), command=test_connection)
button.grid(row=last_row + 3, column=1, pady=5, padx=5, sticky='EW')

root.mainloop()