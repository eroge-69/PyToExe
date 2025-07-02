import os
import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageDraw
import pystray
import pymysql

try:
    import winreg as reg
except ImportError:
    reg = None  # Non-Windows fallback


class TransactionProcessor:
    def __init__(self, log_function):
        self.log = log_function
        self.running = False
        self.conn = None  # Start with no connection

        self.input_folder = r"C:\ReceiptItAPI-2.0.0\ReceiptItClient\messages"
        self.log_folder = os.path.join(self.input_folder, "logs")
        os.makedirs(self.log_folder, exist_ok=True)

    def connect_edurole(self):
        servername = "41.63.16.56"
        username = "impala"
        password = "1Mp@1@j@m3$$0$1"
        dbname = "edurole"
        port = 3306

        while self.conn is None:
            try:
                self.conn = pymysql.connect(
                    host=servername,
                    user=username,
                    password=password,
                    database=dbname,
                    port=port
                )
                self.log("✅ DB connection established to Edurole successfully!")
            except pymysql.MySQLError as e:
                self.log(f"❌ Failed to connect to MySQL Edurole: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def start_db_connection_loop(self):
        threading.Thread(target=self.connect_edurole, daemon=True).start()

    def check_duplicate(self, transaction_id):
        if not self.conn:
            raise Exception("DB not connected yet!")
        with self.conn.cursor() as cursor:
            sql = "SELECT COUNT(*) FROM transactions WHERE TransactionID = %s"
            cursor.execute(sql, (transaction_id,))
            count = cursor.fetchone()[0]
            return count > 0

    def get_student_name(self, npin):
        with self.conn.cursor() as cursor:
            sql = "SELECT CONCAT(FirstName, ' ', MiddleName, ' ', Surname) FROM `basic-information` WHERE ID = %s"
            cursor.execute(sql, (npin,))
            result = cursor.fetchone()
            return result[0] if result and result[0] else ""

    def get_student_nrc(self, npin):
        with self.conn.cursor() as cursor:
            sql = "SELECT GovernmentID FROM `basic-information` WHERE ID = %s"
            cursor.execute(sql, (npin,))
            result = cursor.fetchone()
            return result[0] if result and result[0] else ""

    def get_student_phone(self, npin):
        with self.conn.cursor() as cursor:
            sql = "SELECT MobilePhone FROM `basic-information` WHERE ID = %s"
            cursor.execute(sql, (npin,))
            result = cursor.fetchone()
            return result[0] if result and result[0] else ""

    def insert_transaction(self, transaction):
        uid = transaction[0][:16] if transaction[0] else ''
        request_id = transaction[1]
        transaction_id = transaction[2]
        student_id = transaction[3][:16] if transaction[3] else ''
        nrc = transaction[4]
        date = transaction[5]
        amount = transaction[6]
        name = transaction[7]
        tx_type = transaction[8]
        tx_hash = transaction[9]
        phone = transaction[10]
        status = transaction[11]
        error = transaction[12]
        data = transaction[13]

        with self.conn.cursor() as cursor:
            sql = """
                INSERT INTO transactions
                (UID, RequestID, TransactionID, StudentID, NRC, TransactionDate, Amount, Name,
                 Type, Hash, Timestamp, Phone, Status, Error, Data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                uid, request_id, transaction_id, student_id, nrc, date, amount, name,
                tx_type, tx_hash, phone, status, error, data
            ))
        self.conn.commit()

    def process_files(self):
        while self.running:
            try:
                if not self.conn:
                    self.log("⚠️ Cannot process files: DB not connected yet.")
                    time.sleep(5)
                    continue

                files = os.listdir(self.input_folder)
                for filename in files:
                    if filename in ['.', '..', 'RCPTIT.TMP', 'logs']:
                        continue

                    file_path = os.path.join(self.input_folder, filename)
                    with open(file_path, 'r') as file:
                        lines = [line.strip() for line in file if line.strip() != '']

                    for i, line in enumerate(lines, 1):
                        reference_number = line[0:15].strip()
                        client_account_number = line[15:38].strip()
                        transaction_type = line[38:39].strip()
                        data = line[78:97].strip()
                        date = line[172:181].strip()
                        paid_amount = line[181:201].strip()
                        npin = line[201:221].strip()
                        trace_id = line[229:244].strip()

                        log_message = (
                            f"\nTransaction {i}:\n"
                            f"  RequestID         : {reference_number}\n"
                            f"  MU Account Number : {client_account_number}\n"
                            f"  Transaction Type  : {transaction_type}\n"
                            f"  Date              : {date}\n"
                        )

                        if paid_amount.isdigit():
                            amount = "%.2f" % (int(paid_amount) / 100)
                        else:
                            amount = paid_amount
                        log_message += f"  Paid Amount       : {amount}\n"
                        log_message += (
                            f"  StudentID         : {npin}\n"
                            f"  TransactionID     : {trace_id}\n"
                            f"  Data              : {data}\n"
                        )
                        self.log(log_message)

                        if self.check_duplicate(trace_id):
                            self.log(f"⚠️ Duplicate found for TransactionID {trace_id}. Skipping.\n")
                            continue

                        student_name = self.get_student_name(npin)
                        student_nrc = self.get_student_nrc(npin)
                        student_phone = self.get_student_phone(npin)

                        transaction = (
                            npin[:16],
                            reference_number,
                            trace_id,
                            npin[:16],
                            student_nrc,
                            date,
                            amount,
                            student_name,
                            'FNB',
                            '',
                            student_phone,
                            '',
                            '',
                            data
                        )

                        self.insert_transaction(transaction)
                        self.log(f"✅ Inserted TransactionID {trace_id} successfully.\n")

                    os.rename(file_path, os.path.join(self.log_folder, filename))
                    self.log(f"📁 Moved processed file: {filename}\n")

                time.sleep(5)
            except Exception as e:
                self.log(f"❌ Error: {e}\n")
                time.sleep(5)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.process_files, daemon=True)
            self.thread.start()
            self.log("▶️ Service started.\n")

    def stop(self):
        self.running = False
        self.log("⏹️ Service stopped.\n")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("FNB Transaction Processor Service")

        self.log_text = ScrolledText(root, width=100, height=30)
        self.log_text.pack(padx=10, pady=10)

        self.start_button = tk.Button(root, text="Start Service", command=self.start_service)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.stop_button = tk.Button(root, text="Stop Service", command=self.stop_service, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.exit_button = tk.Button(root, text="Exit", command=self.exit_app)
        self.exit_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.processor = TransactionProcessor(self.log)
        self.processor.start_db_connection_loop()
        self.start_service_when_db_ready()  # ✅ AUTO START SERVICE

        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        self.setup_tray_icon()
        self.register_startup()

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        print(message)

    def start_service(self):
        if not self.processor.conn:
            self.log("⚠️ Cannot start service: DB not connected yet.")
            return
        self.processor.start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def start_service_when_db_ready(self):
        def wait_and_start():
            while self.processor.conn is None:
                self.log("ℹ️ Waiting for DB connection to start service...")
                time.sleep(2)
            self.processor.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log("✅ Service started automatically after DB connection was established.")

        threading.Thread(target=wait_and_start, daemon=True).start()

    def stop_service(self):
        self.processor.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def exit_app(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.processor.stop()
            self.icon.stop()
            self.root.destroy()
            sys.exit(0)

    def minimize_to_tray(self):
        self.root.withdraw()
        self.log("🔻 Minimized to tray.")

    def restore_window(self, icon, item):
        self.root.deiconify()

    def setup_tray_icon(self):
        image = self.create_icon_image()
        menu = (
            pystray.MenuItem('Restore', self.restore_window),
            pystray.MenuItem('Exit', self.exit_app)
        )
        self.icon = pystray.Icon("TxProcessor", image, "FNB Transaction Processor", pystray.Menu(*menu))
        threading.Thread(target=self.icon.run, daemon=True).start()

    def create_icon_image(self):
        size = (64, 64)
        image = Image.new('RGBA', size, (0, 102, 204, 255))  # Deep blue

        draw = ImageDraw.Draw(image)
        padding = 8
        draw.ellipse([padding, padding, size[0]-padding, size[1]-padding], fill='white')

        draw.text(
            (size[0]//2, size[1]//2),
            "Tx",
            fill=(0, 102, 204),
            anchor='mm'
        )
        return image

    def register_startup(self):
        if reg:
            exe_path = sys.executable
            script_path = os.path.realpath(__file__)
            command = f'"{exe_path}" "{script_path}"'
            key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            try:
                registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_SET_VALUE)
                reg.SetValueEx(registry_key, "FNBTransactionProcessorService", 0, reg.REG_SZ, command)
                reg.CloseKey(registry_key)
                self.log("✅ Registered to run at Windows startup.")
            except Exception as e:
                self.log(f"❌ Failed to register startup: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
