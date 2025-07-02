import os
import cx_Oracle
import tkinter as tk
import time
import threading
from tkinter import scrolledtext, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
from pyzbar.pyzbar import decode

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
            # Check if file exists, is large enough, and hasn't been processed recently
            if (os.path.exists(file_path) and 
                os.path.getsize(file_path) >= self.min_file_size and
                (file_path not in self.last_processed or 
                 (current_time - self.last_processed[file_path]) > self.debounce_time)):
                self.last_processed[file_path] = current_time
                self.app.process_qr_image(file_path)

    def on_created(self, event):
        if not event.is_directory and self.is_image_file(event.src_path):
            # Skip temporary files created by Windows Explorer
            if not event.src_path.lower().endswith('tmp') and not '~' in event.src_path:
                threading.Thread(
                    target=self.delayed_processing,
                    args=(event.src_path,),
                    daemon=True
                ).start()

    def on_modified(self, event):
        if not event.is_directory and self.is_image_file(event.src_path):
            # Skip temporary files and thumbnails
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

        # Create a label for the watched folder
        folder_label = tk.Label(master, text=f"Watching folder: {WATCHED_FOLDER}", font=("Helvetica", 12))
        folder_label.pack(pady=10)

        # Add a label for database connection status
        self.db_status = tk.Label(master, text="Database: Not connected", fg="red", font=("Helvetica", 10))
        self.db_status.pack()

        # Create a text box with scrollbar for QR output
        self.text_box = scrolledtext.ScrolledText(master, width=90, height=25, font=("Courier", 10))
        self.text_box.pack(padx=20, pady=15)

        # Add a label for current file status
        self.current_file_label = tk.Label(master, text="No QR image processed yet", font=("Helvetica", 10, "italic"))
        self.current_file_label.pack(pady=5)

        # Set up folder watcher
        self.observer = Observer()
        self.event_handler = QrEventHandler(self)
        self.observer.schedule(self.event_handler, WATCHED_FOLDER, recursive=False)
        self.observer.start()

        # Test database connection
        self.test_db_connection()

        # Graceful shutdown
        master.protocol("WM_DELETE_WINDOW", self.on_close)

    def test_db_connection(self):
        """Test database connection on startup"""
        try:
            connection = cx_Oracle.connect(DB_USERNAME, DB_PASSWORD, DB_DSN)
            connection.close()
            self.db_status.config(text="Database: Connected", fg="green")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            self.db_status.config(text=f"Database: Not connected (Error: {error.message})", fg="red")
            self.log_message(f"Database connection error: {error.message}")

    def process_qr_image(self, file_path):
        """Process the QR image and handle DB operations in a separate thread"""
        def worker():
            try:
                # Step 1: Read QR code from image
                self.log_message(f"\nProcessing file: {os.path.basename(file_path)}")
                
                # Open image and decode QR code
                image = Image.open(file_path)
                decoded_objects = decode(image)
                
                if not decoded_objects:
                    self.log_message("Error: No QR code detected in the image")
                    self.current_file_label.config(text="No QR code detected")
                    return

                # Get QR code content (use first QR if multiple)
                qr_content = decoded_objects[0].data.decode('utf-8')
                self.log_message(f"QR Code Content: {qr_content}")

                # Step 2: Connect to Oracle DB and call function
                connection = None
                cursor = None
                try:
                    connection = cx_Oracle.connect(DB_USERNAME, DB_PASSWORD, DB_DSN)
                    cursor = connection.cursor()

                    # Call the function with QR code content
                    self.log_message("Calling assort_update_lot_symbol function...")
                    result = cursor.callfunc("assort_update_lot_symbol", cx_Oracle.STRING, [qr_content])
                    
                    if result == '-1':
                        self.log_message("Error: આ પેકેટ તમને ઇસ્યુ કરેલ નથી !")
                        self.current_file_label.config(text="Not your packet")
                        # Show warning message box
                        self.master.after(0, lambda: messagebox.showwarning(
                            "Invalid Packet",
                            "આ પેકેટ તમને ઇસ્યુ કરેલ નથી !.........."
                        ))
                    else:
                        self.log_message("Update successful!")
                        self.current_file_label.config(text="Update successful")
                    
                except cx_Oracle.DatabaseError as e:
                    error, = e.args
                    self.log_message(f"Database Error: {error.message}")
                    if connection:
                        connection.rollback()
                
                finally:
                    if cursor is not None:
                        cursor.close()
                    if connection is not None:
                        connection.close()
            
            except Exception as e:
                self.log_message(f"Error processing file: {str(e)}")
        
        # Run the worker in a separate thread to avoid UI freezing
        threading.Thread(target=worker, daemon=True).start()

    def log_message(self, message):
        """Thread-safe method to log messages to the text box"""
        def update_text():
            self.text_box.insert(tk.END, f"{message}\n")
            self.text_box.see(tk.END)
        self.master.after(0, update_text)

    def on_close(self):
        """Handle window close event"""
        self.observer.stop()
        self.observer.join()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QrReaderApp(root)
    root.mainloop()
