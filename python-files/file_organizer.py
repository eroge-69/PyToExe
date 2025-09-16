#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import hashlib
import shutil
import os

# Optional: AI classification placeholder (requires openai package and API key)
def ai_classify_file(filepath, openai_api_key=None):
    """
    Placeholder for AI-based file classification.
    If you want to enable, install openai package and set openai_api_key.
    The function should return a string label like 'invoice' or 'resume'.
    Currently returns None (disabled).
    """
    # Example implementation (disabled by default):
    # import openai
    # openai.api_key = openai_api_key
    # with open(filepath, "rb") as f:
    #     content = f.read(20000).decode('utf-8', errors='ignore')
    # prompt = f"Classify the following document into one of: invoice, resume, contract, report, other:\\n\\n{content}"
    # resp = openai.Completion.create(model='text-davinci-003', prompt=prompt, max_tokens=10)
    # return resp.choices[0].text.strip().lower()
    return None

EXT_MAP = {
    'Images': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff'],
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.ppt', '.pptx', '.xls', '.xlsx', '.csv'],
    'Videos': ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv'],
    'Audio': ['.mp3', '.wav', '.aac', '.flac', '.m4a'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
}

def file_hash(path, chunk_size=8192):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def organize_folder(folder_path, remove_duplicates=False, openai_api_key=None, progress_callback=None):
    folder = Path(folder_path)
    if not folder.is_dir():
        raise ValueError("Not a directory")
    # create subfolders map
    mapping = {}
    for file in folder.rglob('*'):
        if file.is_file():
            ext = file.suffix.lower()
            placed = False
            # AI classification attempt (optional)
            label = None
            if openai_api_key:
                try:
                    label = ai_classify_file(str(file), openai_api_key=openai_api_key)
                except Exception:
                    label = None
            if label:
                dest_folder = folder / label
            else:
                for cat, exts in EXT_MAP.items():
                    if ext in exts:
                        dest_folder = folder / cat
                        placed = True
                        break
                if not placed:
                    dest_folder = folder / 'Others'
            mapping.setdefault(str(dest_folder), []).append(str(file))
    # handle duplicates
    hash_map = {}
    actions = []
    for dest, files in mapping.items():
        os.makedirs(dest, exist_ok=True)
        for f in files:
            h = file_hash(f)
            if h in hash_map:
                # duplicate detected
                if remove_duplicates:
                    # remove the duplicate file
                    os.remove(f)
                    actions.append(f"Removed duplicate: {f}")
                else:
                    # leave it but rename
                    base = Path(f).stem
                    newname = base + '_dup' + Path(f).suffix
                    newpath = Path(f).with_name(newname)
                    shutil.move(f, newpath)
                    actions.append(f"Renamed duplicate: {f} -> {newpath}")
                    # move to appropriate folder
                    shutil.move(str(newpath), os.path.join(dest, Path(newpath).name))
            else:
                hash_map[h] = f
                shutil.move(f, os.path.join(dest, Path(f).name))
                actions.append(f"Moved: {f} -> {dest}")
            if progress_callback:
                progress_callback(actions[-1])
    return actions

# GUI
class App:
    def __init__(self, root):
        self.root = root
        root.title("Simple File Organizer")
        root.geometry("640x420")
        self.folder_var = tk.StringVar(value="")
        self.remove_dup = tk.BooleanVar(value=False)
        self.openai_key = tk.StringVar(value="")  # optional
        frm = ttk.Frame(root, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        row = 0
        ttk.Label(frm, text="Select folder to organize:").grid(column=0, row=row, sticky=tk.W)
        ttk.Entry(frm, textvariable=self.folder_var, width=60).grid(column=0, row=row+1, sticky=tk.W)
        ttk.Button(frm, text="Browse", command=self.browse).grid(column=1, row=row+1, sticky=tk.W, padx=6)

        row += 2
        ttk.Checkbutton(frm, text="Remove exact duplicates (permanent delete)", variable=self.remove_dup).grid(column=0, row=row, sticky=tk.W, pady=6)
        row += 1
        ttk.Label(frm, text="(Optional) OpenAI API Key for AI classification:").grid(column=0, row=row, sticky=tk.W)
        ttk.Entry(frm, textvariable=self.openai_key, width=60, show='*').grid(column=0, row=row+1, sticky=tk.W)
        ttk.Label(frm, text="Note: AI classification is optional and requires 'openai' package and internet connection.").grid(column=0, row=row+2, sticky=tk.W, pady=4)

        row += 3
        ttk.Button(frm, text="Organize Now", command=self.organize_now).grid(column=0, row=row, sticky=tk.W+tk.E, pady=8)
        ttk.Button(frm, text="Quit", command=root.quit).grid(column=1, row=row, sticky=tk.E)

        row += 1
        self.log = tk.Text(frm, height=10, wrap='word')
        self.log.grid(column=0, row=row, columnspan=2, sticky=tk.NSEW, pady=8)
        frm.rowconfigure(row, weight=1)
        frm.columnconfigure(0, weight=1)

    def browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def append_log(self, text):
        self.log.insert(tk.END, text + "\\n")
        self.log.see(tk.END)
        self.root.update_idletasks()

    def organize_now(self):
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showerror("Error", "Please select a folder")
            return
        remove_dup = self.remove_dup.get()
        key = self.openai_key.get().strip() or None
        try:
            self.append_log(f"Starting organization on: {folder}")
            actions = organize_folder(folder, remove_duplicates=remove_dup, openai_api_key=key, progress_callback=self.append_log)
            self.append_log("Done. Actions:")
            for a in actions:
                self.append_log(a)
            messagebox.showinfo("Completed", f"Organization complete. {len(actions)} actions performed. See log for details.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
