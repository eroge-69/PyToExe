import os
import cx_Oracle
import tkinter as tk
import time
import threading
from tkinter import scrolledtext, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import cv2
import pystray
from PIL import Image
import sys

# Database Configuration
DB_USERNAME = 'assort'
DB_PASSWORD = 'myassort'
DB_DSN = '172.5.1.251/ORCLASSORT'

WATCHED_FOLDER = r"D:\QRDATA\IMG"

class QrEventHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app
        self.last_processed = {}  # To track the last processed time for each file
        self.lock = threading.Lock()  # Lock for thread safety
        self.debounce_time = 2  # Increased debounce time to 2 seconds
        self.min_file_size = 1024  # Minimum file size to process (1KB)
        super().__init__()
        
    def delayed_processing(self, file_path):
        """Process file after a debounce period"""
        time.sleep(self.debounce_time)  # Wait for the debounce time
        with self.lock:
            current_time = time.time()
            if (os.path.exists(file_path) and 
                os.path.getsize(file_path) >= self.min_file_size and
                (file_path not in self.last_processed or 
                 (current_time - self.last_processed[file_path]) > self.debounce_time)):
                self.last_processed[file_path] = current_time
                self.app.process_qr_image(file_path)

    def on_created(self, event):
        if not event.is_directory and self.is_image_file(event.src_path):
            if not event.src_path.lower().endswith('tmp') and not '~' in event.src_path:
                threading.Thread(
                    target=self.delayed_processing,
                    args=(event.src_path,),
                    daemon=True
                ).start()

    def on_modified(self, event):
        if not event.is_directory and self.is_image_file(event.src_path):
            if (not event.src_path.lower().endswith('tmp') and 
                not 'thumb' in event.src_path.lower() and
                not '~' in event.src_path):
                threading.Thread(
                    target=self.delayed_processing,
                    args=(event.src_path,),
                    daemon=True
                ).start()

    @staticmethod
    def is_image_file(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ['.png', '.jpg', '.jpeg']

class QrReaderApp:
    def __init__(self, master):
        self.master = master
        master.title("QR Code to Oracle Database")
        master.geometry("800x700")
        
        # Hide main window immediately
        master.withdraw()
        
        # System tray setup
        self.setup_tray()
        
        # Override close button to minimize to tray
        master.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
        # Setup GUI components (hidden initially)
        folder_label = tk.Label(master, text=f"Watching folder: {WATCHED_FOLDER}", font=("Helvetica", 12))
        folder_label.pack(pady=10)
        self.db_status = tk.Label(master, text="Database: Not connected", fg="red", font=("Helvetica", 10))
        self.db_status.pack()
        self.text_box = scrolledtext.ScrolledText(master, width=90, height=25, font=("Courier", 10))
        self.text_box.pack(padx=20, pady=15)
        self.current_file_label = tk.Label(master, text="No QR image processed yet", font=("Helvetica", 10, "italic"))
        self.current_file_label.pack(pady=5)

        # Start folder watcher
        self.observer = Observer()
        self.event_handler = QrEventHandler(self)
        self.observer.schedule(self.event_handler, WATCHED_FOLDER, recursive=False)
        self.observer.start()

        # Test DB connection
        self.test_db_connection()

    def setup_tray(self):
        """Create system tray icon with menu"""
        # Create tray icon image (16x16 red square as placeholder)
        image = Image.new('RGB', (16, 16), (255, 0, 0))
        menu = (
            pystray.MenuItem('Show QR Scanner', self.show_window),
            pystray.MenuItem('Exit', self.quit_app)
        )
        self.tray_icon = pystray.Icon("qr_scanner", image, "QR Scanner", menu)
        
        # Start tray icon in separate thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def minimize_to_tray(self):
        """Minimize the window to system tray"""
        self.master.withdraw()

    def show_window(self, icon=None, item=None):
        """Show the main window"""
        self.master.deiconify()
        self.master.lift()
        self.master.attributes('-topmost', True)
        self.master.after_idle(self.master.attributes, '-topmost', False)

    def quit_app(self, icon=None, item=None):
        """Clean exit from tray menu"""
        self.observer.stop()
        self.observer.join()
        self.tray_icon.stop()
        self.master.destroy()
        os._exit(0)

    def test_db_connection(self):
        try:
            connection = cx_Oracle.connect(DB_USERNAME, DB_PASSWORD, DB_DSN)
            connection.close()
            self.db_status.config(text="Database: Connected", fg="green")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            self.db_status.config(text=f"Database: Not connected (Error: {error.message})", fg="red")
            self.log_message(f"Database connection error: {error.message}")

    def process_qr_image(self, file_path):
        def worker():
            try:
                self.log_message(f"\nProcessing file: {os.path.basename(file_path)}")
                image = cv2.imread(file_path)
                if image is None:
                    self.log_message("Error: Unable to read image file")
                    self.current_file_label.config(text="Invalid image file")
                    return

                qr_detector = cv2.QRCodeDetector()
                retval, decoded_info, points, _ = qr_detector.detectAndDecodeMulti(image)
                
                if not retval or not decoded_info:
                    self.log_message("Error: No QR code detected in the image")
                    self.current_file_label.config(text="No QR code detected")
                    return

                qr_content = decoded_info[0]
                self.log_message(f"QR Code Content: {qr_content}")

                connection = None
                cursor = None
                try:
                    connection = cx_Oracle.connect(DB_USERNAME, DB_PASSWORD, DB_DSN)
                    cursor = connection.cursor()
                    self.log_message("Calling assort_update_lot_symbol function...")
                    result = cursor.callfunc("assort_update_lot_symbol", cx_Oracle.STRING, [qr_content])
                    
                    if result == '-1':
                        self.log_message("Error: આ પેકેટ તમને ઇસ્યુ કરેલ નથી !")
                        self.current_file_label.config(text="Not your packet")
                        self.show_forceful_warning()
                    else:
                        self.log_message("Update successful!")
                        self.current_file_label.config(text="Update successful")
                    
                except cx_Oracle.DatabaseError as e:
                    error, = e.args
                    self.log_message(f"Database Error: {error.message}")
                    if connection:
                        connection.rollback()
                finally:
                    if cursor:
                        cursor.close()
                    if connection:
                        connection.close()
            
            except Exception as e:
                self.log_message(f"Error processing file: {str(e)}")
        
        threading.Thread(target=worker, daemon=True).start()

    def show_forceful_warning(self):
        warning_window = tk.Toplevel(self.master)
        warning_window.withdraw()
        warning_window.wm_attributes("-topmost", True)
        warning_window.wm_attributes("-disabled", True)
        warning_window.wm_attributes("-toolwindow", True)
        warning_window.wm_attributes("-alpha", 0.9)
        warning_window.deiconify()
        messagebox.showwarning(
            "Invalid Packet",
            "આ પેકેટ તમને ઇસ્યુ કરેલ નથી !..........",
            parent=warning_window
        )
        warning_window.destroy()

    def log_message(self, message):
        def update_text():
            self.text_box.insert(tk.END, f"{message}\n")
            self.text_box.see(tk.END)
        self.master.after(0, update_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = QrReaderApp(root)
    root.mainloop()
