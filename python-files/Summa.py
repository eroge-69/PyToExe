import os
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pythoncom
import win32com.client as win32
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys

# Redirect stdout to GUI
class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.after(0, lambda: self._append(message))

    def _append(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

def wait_until_file_is_ready(file_path, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb'):
                    return True
            except IOError:
                time.sleep(0.5)
        else:
            time.sleep(0.5)
    return False

def normalize_path(path):
    return path.replace('/', '\\')

class ExcelConverterHandler(FileSystemEventHandler):
    def __init__(self, logger):
        self.logger = logger

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = normalize_path(event.src_path)
        if file_path.lower().endswith('.xls') and not file_path.lower().endswith('.xlsx'):
            self.logger.write(f"🔄 Converting: {file_path}\n")
            if not wait_until_file_is_ready(file_path):
                self.logger.write(f"⚠️ Skipped (file not ready): {file_path}\n")
                return
            try:
                pythoncom.CoInitialize()
                excel = win32.DispatchEx('Excel.Application')
                excel.Visible = False
                excel.DisplayAlerts = False

                wb = excel.Workbooks.Open(file_path)
                new_path = file_path.replace('.xls', '.xlsx')
                wb.SaveAs(new_path, FileFormat=51)
                wb.Close(False)
                self.logger.write(f"✅ Saved as: {new_path}\n")
                os.remove(file_path)
                self.logger.write(f"🗑️ Deleted original file: {file_path}\n")
            except Exception as e:
                self.logger.write(f"❌ Error: {e}\n")
            finally:
                excel.Quit()
                pythoncom.CoUninitialize()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Auto Converter")
        self.folder_path = tk.StringVar()
        self.observer = None
        self.monitoring = False

        # Folder selection
        tk.Label(root, text="Select Folder to Monitor:").pack(pady=5)
        path_frame = tk.Frame(root)
        path_frame.pack()
        tk.Entry(path_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(path_frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT)

        # Control buttons
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)
        self.start_button = tk.Button(control_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(control_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.export_button = tk.Button(control_frame, text="Export Log", command=self.export_log)
        self.export_button.pack(side=tk.LEFT, padx=5)

        # Log output
        tk.Label(root, text="Status:").pack()
        self.log_text = scrolledtext.ScrolledText(root, height=15, width=80)
        self.log_text.pack(padx=10, pady=5)
        sys.stdout = TextRedirector(self.log_text)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def start_monitoring(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.monitoring = True
        threading.Thread(target=self.run_observer, args=(folder,), daemon=True).start()

    def stop_monitoring(self):
        self.monitoring = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        print("🛑 Monitoring stopped.\n")

    def run_observer(self, folder):
        print(f"👀 Watching folder: {folder}\n")
        event_handler = ExcelConverterHandler(logger=self)
        self.observer = Observer()
        self.observer.schedule(event_handler, path=folder, recursive=False)
        self.observer.start()
        try:
            while self.monitoring:
                time.sleep(1)
        except Exception as e:
            print(f"❌ Observer error: {e}\n")

    def write(self, message):
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)

    def export_log(self):
        log_content = self.log_text.get("1.0", tk.END)
        save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt")])
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as file:
                    file.write(log_content)
                messagebox.showinfo("Success", f"Log exported to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export log:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
