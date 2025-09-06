import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import zipfile
import os
import json

class XAPKConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XAPK to APK & OBB Converter")
        self.root.geometry("500x500")
        self.root.resizable(False, False)
        self.xapk_path = None
        self.extracted_files = []  # List of (filename, data)
        self.package_name = None

        self.create_widgets()
        self.setup_drag_and_drop()

    def create_widgets(self):
        # Choose XAPK
        self.choose_btn = tk.Button(self.root, text="Choose XAPK", command=self.choose_xapk, width=40)
        self.choose_btn.pack(pady=10)

        # Checkboxes for APK and OBB extraction
        self.extract_apk = tk.BooleanVar(value=True)
        self.extract_obb = tk.BooleanVar(value=True)

        checkbox_frame = tk.Frame(self.root)
        checkbox_frame.pack()
        tk.Checkbutton(checkbox_frame, text="Extract APK", variable=self.extract_apk).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(checkbox_frame, text="Extract OBB", variable=self.extract_obb).pack(side=tk.LEFT, padx=10)

        # Convert
        self.convert_btn = tk.Button(self.root, text="Convert to APK/OBB", command=self.convert_xapk, state=tk.DISABLED, width=40)
        self.convert_btn.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=10)

        # Package name label
        self.package_label = tk.Label(self.root, text="Package: N/A")
        self.package_label.pack(pady=5)

        # Listbox for extracted files
        self.file_listbox = tk.Listbox(self.root, width=60, height=10)
        self.file_listbox.pack(pady=5)

        # Download
        self.download_btn = tk.Button(self.root, text="Download Files", command=self.save_files, state=tk.DISABLED, width=40)
        self.download_btn.pack(pady=10)

        # Drag-and-drop label
        self.drag_label = tk.Label(self.root, text="(Drag .xapk file here)", fg="gray")
        self.drag_label.pack(pady=5)

    def setup_drag_and_drop(self):
        def drop(event):
            files = self.root.tk.splitlist(event.data)
            for f in files:
                if f.lower().endswith(".xapk"):
                    self.set_xapk_path(f)
                    break

        try:
            import tkinterdnd2 as tkdnd
            self.root.drop_target_register(tkdnd.DND_FILES)
            self.root.dnd_bind('<<Drop>>', drop)
        except ImportError:
            self.drag_label.config(text="(Drag-and-drop unavailable: install 'tkinterdnd2')")

    def choose_xapk(self):
        path = filedialog.askopenfilename(filetypes=[("XAPK files", "*.xapk")])
        if path:
            self.set_xapk_path(path)

    def set_xapk_path(self, path):
        self.xapk_path = path
        self.convert_btn.config(state=tk.NORMAL)
        self.download_btn.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.extracted_files.clear()
        self.package_name = None
        self.package_label.config(text="Package: N/A")
        self.file_listbox.delete(0, tk.END)

    def convert_xapk(self):
        if not self.xapk_path:
            messagebox.showerror("Error", "No XAPK file selected.")
            return

        self.convert_btn.config(state=tk.DISABLED)
        self.download_btn.config(state=tk.DISABLED)
        self.progress["value"] = 10
        self.root.update_idletasks()

        try:
            with zipfile.ZipFile(self.xapk_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()

                # Detect manifest.json (case-insensitive)
                manifest_file = next((f for f in file_list if f.lower() == "manifest.json"), None)
                if manifest_file:
                    try:
                        manifest_data = zip_ref.read(manifest_file)
                        manifest = json.loads(manifest_data)
                        self.package_name = manifest.get("package_name", "unknown.package")
                    except Exception:
                        self.package_name = "unknown.package"
                else:
                    self.package_name = "unknown.package"

                self.package_label.config(text=f"Package: {self.package_name}")

                # Filter APKs and OBBs
                apk_files = [f for f in file_list if f.endswith(".apk")]
                obb_files = [f for f in file_list if f.endswith(".obb")]

                tasks = []
                if self.extract_apk.get():
                    tasks += [("apk", f) for f in apk_files]
                if self.extract_obb.get():
                    tasks += [("obb", f) for f in obb_files]

                if not tasks:
                    raise Exception("No files selected for extraction or none found.")

                total_files = len(tasks)
                progress_step = 80 / total_files
                progress = 20

                for file_type, file_path in tasks:
                    try:
                        data = zip_ref.read(file_path)
                        name = os.path.basename(file_path)

                        if file_type == "apk":
                            if len(apk_files) > 1:
                                name = f"{self.package_name}_{name}"
                            save_path = name
                        else:  # obb
                            save_path = os.path.join("Android", "obb", self.package_name, name)

                        self.extracted_files.append((save_path, data))
                        self.file_listbox.insert(tk.END, save_path)

                    except Exception as e:
                        print(f"Failed to extract {file_path}: {e}")
                        continue

                    progress += progress_step
                    self.progress["value"] = progress
                    self.root.update_idletasks()

                self.progress["value"] = 100
                self.download_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Success", "Files extracted successfully.")

        except Exception as e:
            self.progress["value"] = 0
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
        finally:
            self.convert_btn.config(state=tk.NORMAL)

    def save_files(self):
        if not self.extracted_files:
            messagebox.showerror("Error", "No files to save.")
            return

        folder = filedialog.askdirectory()
        if not folder:
            return

        for rel_path, data in self.extracted_files:
            try:
                full_path = os.path.join(folder, rel_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "wb") as f:
                    f.write(data)
            except Exception as e:
                print(f"Failed to save {rel_path}: {e}")

        messagebox.showinfo("Saved", f"All files saved to:\n{folder}")

if __name__ == "__main__":
    root = tk.Tk()
    app = XAPKConverterApp(root)
    root.mainloop()