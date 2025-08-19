import os
import re
import json
import tempfile
import requests
import threading
import time
from queue import Queue
from tkinter import Tk, Text, Button, END, filedialog, Scrollbar, RIGHT, Y, LEFT, BOTH, messagebox, Frame, Label

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ======= Rules & thresholds =======
rules = [
    ("DDE", re.compile(r"\bDDE(AUTO)?\b", re.IGNORECASE), 30),
    ("INCLUDETEXT", re.compile(r"\bINCLUDETEXT\b", re.IGNORECASE), 15),
    ("INCLUDEPICTURE", re.compile(r"\bINCLUDEPICTURE\b", re.IGNORECASE), 8),
    ("HYPERLINK", re.compile(r"\bhlinkClick\b|\bHYPERLINK\b", re.IGNORECASE), 5),
    ("PowerShell", re.compile(r"powershell\b|FromBase64String\(", re.IGNORECASE), 40),
    ("WScript/Shell", re.compile(r"WScript\.Shell|Shell\(", re.IGNORECASE), 25),
    ("VBADownload", re.compile(r"URLDownloadToFile|XMLHTTP|WinHttp", re.IGNORECASE), 20),
    ("AutoOpen Macro", re.compile(r"AutoOpen", re.IGNORECASE), 30),
    ("CreateObject", re.compile(r"CreateObject", re.IGNORECASE), 20),
    ("ShellExecute", re.compile(r"ShellExecute", re.IGNORECASE), 25),
    ("Base64 Strings", re.compile(r"[A-Za-z0-9+/]{40,}={0,2}", re.IGNORECASE), 10),
    ("Eval/Execute", re.compile(r"\beval\b|\bExecute\b|\bExecuteGlobal\b", re.IGNORECASE), 35),
    ("WMI Access", re.compile(r"GetObject\(.*WMI.*\)", re.IGNORECASE), 20),
]

HIGH_THRESHOLD = 70
MEDIUM_THRESHOLD = 35

# ======= Scanner Functions =======

def analyze_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return 0
    score = sum(s for _, pattern, s in rules if pattern.search(content))
    return score

def scan_files(paths):
    results = []
    for path in paths:
        if not os.path.isfile(path):
            continue
        size = os.path.getsize(path)
        score = analyze_file(path)
        severity = (
            "High" if score >= HIGH_THRESHOLD else
            "Medium" if score >= MEDIUM_THRESHOLD else
            "Low"
        )
        results.append({
            "path": path,
            "size": size,
            "score": score,
            "severity": severity
        })
    return results

def save_results_to_file(results):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"docguard_scan_{timestamp}.json"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        return filename
    except Exception as e:
        print(f"Error saving results: {e}")
        return None

def download_file(url, dest):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            f.write(resp.content)
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False

# ======= Real-time file system event handler =======
class FileEventHandler(FileSystemEventHandler):
    def __init__(self, output_text):
        self.output_text = output_text

    def on_created(self, event):
        if event.is_directory:
            return
        results = scan_files([event.src_path])
        self.output_text.insert(END, f"\n[Real-Time Scan] {event.src_path}:\n")
        self.output_text.insert(END, json.dumps(results, indent=2) + "\n")
        self.output_text.see(END)

# ======= Multithreaded system scanner =======
def system_scan_worker(q, results_list, lock):
    while True:
        path = q.get()
        if path is None:
            break
        if os.path.isfile(path):
            size = os.path.getsize(path)
            score = analyze_file(path)
            severity = (
                "High" if score >= HIGH_THRESHOLD else
                "Medium" if score >= MEDIUM_THRESHOLD else
                "Low"
            )
            res = {"path": path, "size": size, "score": score, "severity": severity}
            with lock:
                results_list.append(res)
        q.task_done()

def system_scan(root_folders, thread_count=8):
    file_queue = Queue()
    results = []
    lock = threading.Lock()

    # Spawn workers
    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=system_scan_worker, args=(file_queue, results, lock), daemon=True)
        t.start()
        threads.append(t)

    # Walk directories recursively and enqueue files
    for root_folder in root_folders:
        for root, _, files in os.walk(root_folder):
            for f in files:
                full_path = os.path.join(root, f)
                file_queue.put(full_path)

    # Block until all files are processed
    file_queue.join()

    # Stop workers
    for _ in range(thread_count):
        file_queue.put(None)
    for t in threads:
        t.join()

    return results

# ======= Main GUI App =======
class DocGuardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DocGuard - The Total Document Scanner")

        Label(root, text="Drag files or paste file paths / URLs below").pack(pady=2)

        self.input_text = Text(root, height=5)
        self.input_text.pack(fill=BOTH, expand=True, padx=5)

        # Try drag & drop support
        try:
            from tkinterdnd2 import DND_FILES
            self.input_text.drop_target_register(DND_FILES)
            self.input_text.dnd_bind('<<Drop>>', self.on_drop)
        except ImportError:
            print("Drag & Drop requires 'tkinterdnd2' (install via pip)")

        btn_frame = Frame(root)
        btn_frame.pack(pady=3)

        Button(btn_frame, text="Scan Files", command=self.scan_files).pack(side=LEFT, padx=4)
        Button(btn_frame, text="Download + Scan", command=self.download_and_scan).pack(side=LEFT, padx=4)
        Button(btn_frame, text="Full System Scan", command=self.full_system_scan).pack(side=LEFT, padx=4)
        Button(btn_frame, text="Start Real-Time Scan", command=self.start_real_time_scan).pack(side=LEFT, padx=4)
        Button(btn_frame, text="Clear", command=self.clear_all).pack(side=LEFT, padx=4)

        Label(root, text="Scan Results").pack(pady=2)

        self.output_text = Text(root, height=15)
        self.output_text.pack(fill=BOTH, expand=True, padx=5, pady=5)
        scrollbar = Scrollbar(self.output_text, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.observer = None

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        for file in files:
            self.input_text.insert(END, file + "\n")

    def scan_files(self):
        lines = self.input_text.get("1.0", END).strip().splitlines()
        paths = [line.strip() for line in lines if line.strip()]
        results = scan_files(paths)
        self.output_text.delete("1.0", END)
        self.output_text.insert(END, json.dumps(results, indent=2))

        saved = save_results_to_file(results)
        if saved:
            self.output_text.insert(END, f"\n[Results saved to {saved}]\n")

    def download_and_scan(self):
        urls = self.input_text.get("1.0", END).strip().splitlines()
        tmp_dir = tempfile.mkdtemp(prefix="docguard_")
        downloaded = []
        for i, url in enumerate(urls):
            dest = os.path.join(tmp_dir, f"file_{i}")
            if download_file(url.strip(), dest):
                downloaded.append(dest)
        results = scan_files(downloaded)
        self.output_text.delete("1.0", END)
        self.output_text.insert(END, json.dumps(results, indent=2))

        saved = save_results_to_file(results)
        if saved:
            self.output_text.insert(END, f"\n[Results saved to {saved}]\n")

    def full_system_scan(self):
        user_folders = []
        home = os.path.expanduser("~")
        # Common user folders to scan
        for folder_name in ["Desktop", "Documents", "Downloads", "Pictures"]:
            path = os.path.join(home, folder_name)
            if os.path.exists(path):
                user_folders.append(path)

        if not user_folders:
            messagebox.showinfo("DocGuard", "No common user folders found to scan.")
            return

        self.output_text.insert(END, "[Starting full system scan in user folders...]\n")
        self.output_text.update()

        # Run scanning in separate thread to avoid freezing UI
        def run_scan():
            results = system_scan(user_folders)
            self.output_text.insert(END, "[Full system scan completed]\n")
            self.output_text.insert(END, json.dumps(results, indent=2) + "\n")

            saved = save_results_to_file(results)
            if saved:
                self.output_text.insert(END, f"[Results saved to {saved}]\n")

        threading.Thread(target=run_scan, daemon=True).start()

    def start_real_time_scan(self):
        folder = filedialog.askdirectory(title="Select Folder to Monitor")
        if not folder:
            return

        if messagebox.askyesno("Background Mode", "Minimize app during real-time scanning?"):
            self.root.iconify()

        if self.observer:
            self.observer.stop()
            self.observer.join()

        handler = FileEventHandler(self.output_text)
        self.observer = Observer()
        self.observer.schedule(handler, folder, recursive=False)
        self.observer.start()
        self.output_text.insert(END, f"[Real-Time] Monitoring folder: {folder}\n")

    def clear_all(self):
        self.input_text.delete("1.0", END)
        self.output_text.delete("1.0", END)

    def on_close(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.root.destroy()

if __name__ == "__main__":
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        root = Tk()
        print("Drag and drop support unavailable. Install tkinterdnd2 via pip.")

    app = DocGuardApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()