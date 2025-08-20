import os
import json
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

modloader_version = "1.1.3"
required_keys = ["mod_version", "title", "description", "modloader_version"]

def load_settings():
    if os.path.isfile("setting.json"):
        with open("setting.json", encoding="utf-8") as f:
            settings = json.load(f)

        if settings["umamusume_path"] == "default":
            base_path = os.path.join("C:\\Users\\", os.getlogin(), "AppData\\LocalLow\\Cygames\\umamusume")
            dat = os.path.join(base_path, "dat")
            backup = os.path.join(base_path, "dat.backup")
        else:
            if os.path.isdir(settings["umamusume_path"]):
                base_path = settings["umamusume_path"]
                dat = os.path.join(base_path, "dat")
                backup = os.path.join(base_path, "dat.backup")
            else:
                messagebox.showerror("Error", "The folder specified in 'umamusume_path' does not exist.\nCheck the path or contact support. Exiting...")
                sys.exit()
    else:
        messagebox.showerror("Error", "'setting.json' not found. Launching with default paths.")
        base_path = os.path.join("C:\\Users\\", os.getlogin(), "AppData\\LocalLow\\Cygames\\umamusume")
        dat = os.path.join(base_path, "dat")
        backup = os.path.join(base_path, "dat.backup")
    return dat, backup

class ModLoaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UMPD Mod Loader GUI")

        self.dat_path, self.backup_path = load_settings()

        self.mod_path = tk.StringVar()
        self.title_text = tk.StringVar()
        self.version_text = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        mod_frame = tk.LabelFrame(self.root, text="Mod Loader")
        mod_frame.pack(fill="x", padx=10, pady=5)
        tk.Entry(mod_frame, textvariable=self.mod_path, width=60).pack(side="left", padx=5)
        tk.Button(mod_frame, text="Browse", command=self.browse_folder).pack(side="left")
        tk.Button(mod_frame, text="Reload", command=self.reload).pack(side="left", padx=5)
        tk.Button(mod_frame, text="Preview", command=self.preview_assets).pack(side="left", padx=5)
        info_frame = tk.LabelFrame(self.root, text="Information")
        info_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(info_frame, textvariable=self.title_text).pack(anchor="w")
        tk.Label(info_frame, textvariable=self.version_text).pack(anchor="w")
        self.description_box = tk.Text(info_frame, height=8, width=70, state="disabled")
        self.description_box.pack()

        control_frame = tk.LabelFrame(self.root, text="Controls")
        control_frame.pack(fill="x", padx=10, pady=5)
        self.assets_load_btn = tk.Button(control_frame, text="Load Assets", state="disabled", command=self.load_assets)
        self.assets_load_btn.pack(side="left", padx=5)
        self.assets_unload_btn = tk.Button(control_frame, text="Unload Assets", state="disabled", command=self.unload_assets)
        self.assets_unload_btn.pack(side="left", padx=5)
        tk.Label(control_frame, text=f"modloader_version : {modloader_version}").pack(side="right")

        progress_frame = tk.LabelFrame(self.root, text="Progress")
        progress_frame.pack(fill="x", padx=10, pady=5)
        self.progress_label = tk.Label(progress_frame, text="Waiting")
        self.progress_label.pack(anchor="w")
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack()
        self.restore_btn = tk.Button(control_frame, text="Restore Original Assets", command=self.restore_original_assets)
        self.restore_btn.pack(side="left", padx=5)

    def preview_assets(self):
        preview_dir = os.path.join(self.mod_path.get(), "preview")
        if not os.path.isdir(preview_dir):
            messagebox.showerror("No Preview", "No 'preview' folder found in the selected mod.")
            return

        images = [f for f in os.listdir(preview_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))]
        if not images:
            messagebox.showinfo("No Images", "No preview images found.")
            return

        index = 0

        preview_win = tk.Toplevel(self.root)
        preview_win.title("Preview Images")

        img_label = tk.Label(preview_win)
        img_label.pack()

        def load_image(idx):
            from PIL import Image, ImageTk
            path = os.path.join(preview_dir, images[idx])
            img = Image.open(path)
            img.thumbnail((600, 400))
            photo = ImageTk.PhotoImage(img)
            img_label.configure(image=photo)
            img_label.image = photo
            preview_win.title(f"Preview - {images[idx]} ({idx+1}/{len(images)})")

        def next_image():
            nonlocal index
            index = (index + 1) % len(images)
            load_image(index)

        def prev_image():
            nonlocal index
            index = (index - 1) % len(images)
            load_image(index)

        nav_frame = tk.Frame(preview_win)
        nav_frame.pack(pady=5)
        tk.Button(nav_frame, text="<< Previous", command=prev_image).pack(side="left", padx=10)
        tk.Button(nav_frame, text="Next >>", command=next_image).pack(side="left", padx=10)

        load_image(index)


    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.mod_path.set(folder)
            self.reload()

    def reset_mod_info(self):
        self.title_text.set("")
        self.version_text.set("")
        self.description_box.configure(state="normal")
        self.description_box.delete("1.0", tk.END)
        self.description_box.configure(state="disabled")
        self.assets_load_btn.config(state="disabled")
        self.assets_unload_btn.config(state="disabled")

    def reload(self):
        mods_setting_path = os.path.join(self.mod_path.get(), "setting.json")

        if not os.path.isfile(mods_setting_path):
            messagebox.showerror("Error", "No 'setting.json' found in selected mod folder.")
            self.reset_mod_info()
            return

        try:
            with open(mods_setting_path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load setting.json:\n{e}")
            self.reset_mod_info()
            return

        if not all(k in data for k in required_keys):
            messagebox.showerror("Error", "'setting.json' is missing required keys.")
            self.reset_mod_info()
            return

        self.title_text.set(data.get("title", "N/A"))
        self.version_text.set(f"mod_version: {data.get('mod_version', 'N/A')}")

        self.description_box.configure(state="normal")
        self.description_box.delete("1.0", tk.END)
        desc = data.get("description", [])
        if isinstance(desc, list):
            self.description_box.insert(tk.END, "\n".join(desc))
        else:
            self.description_box.insert(tk.END, str(desc))
        if data.get("modloader_version") != modloader_version:
            self.description_box.insert(tk.END, f"\n\n[Note] This mod was made for version {data['modloader_version']}")
        self.description_box.configure(state="disabled")

        mod_folder = self.mod_path.get()
        assets_exist = os.path.isdir(os.path.join(mod_folder, "assets"))

        self.assets_load_btn.config(state="normal" if assets_exist else "disabled")
        self.assets_unload_btn.config(state="normal" if assets_exist else "disabled")

    def load_assets(self):
        folder = self.mod_path.get()
        asset_folder = os.path.join(folder, "assets")
        os.makedirs(self.backup_path, exist_ok=True)

        assets = os.listdir(asset_folder)
        self.progress_bar["maximum"] = len(assets)
        self.progress_bar["value"] = 0

        for i, asset in enumerate(assets, start=1):
            src = os.path.join(asset_folder, asset)
            dst = os.path.join(self.dat_path, asset[:2], asset)
            backup = os.path.join(self.backup_path, asset[:2], asset)

            if os.path.isfile(dst):
                #os.makedirs(os.path.dirname(backup), exist_ok=True)
                if not os.path.isfile(backup):
                    os.makedirs(os.path.dirname(backup), exist_ok=True)
                    shutil.move(dst, backup)  # move original to backup only if it doesn't exist
                else:
                    os.remove(dst)
            else:
                messagebox.showerror("Error", "Missing target file in dat folder.\nRun UmaMusume with full data download first.")
                return

            shutil.copy(src, dst)
            self.progress_label.config(text=f"Loading Asset {i} / {len(assets)}")
            self.progress_bar["value"] = i
            self.root.update_idletasks()

        messagebox.showinfo("Success", "Assets loaded successfully.")
        self.progress_label.config(text="Waiting")

    def unload_assets(self):
        folder = self.mod_path.get()
        asset_folder = os.path.join(folder, "assets")

        assets = os.listdir(asset_folder)
        self.progress_bar["maximum"] = len(assets)
        self.progress_bar["value"] = 0

        for i, asset in enumerate(assets, start=1):
            dst = os.path.join(self.dat_path, asset[:2], asset)
            backup = os.path.join(self.backup_path, asset[:2], asset)

            if os.path.isfile(backup):
                if os.path.exists(dst):
                    os.remove(dst)
                shutil.move(backup, dst)

            self.progress_label.config(text=f"Unloading Asset {i} / {len(assets)}")
            self.progress_bar["value"] = i
            self.root.update_idletasks()

        messagebox.showinfo("Success", "Assets unloaded successfully.")
        self.progress_label.config(text="Waiting")

    def restore_original_assets(self):
        if not messagebox.askyesno(
            "Restore Confirmation",
            "Are you sure you want to restore all original assets from backup?\nThis will overwrite all modified files in the dat folder."
        ):
            return

        restored = 0

        for root_dir, dirs, files in os.walk(self.backup_path):
            for file in files:
                backup_file = os.path.join(root_dir, file)
                relative_path = os.path.relpath(backup_file, self.backup_path)
                dat_file = os.path.join(self.dat_path, relative_path)

                os.makedirs(os.path.dirname(dat_file), exist_ok=True)
                if os.path.exists(dat_file):
                    os.remove(dat_file)

                shutil.move(backup_file, dat_file)
                restored += 1

        messagebox.showinfo("Restore Complete", f"Restored {restored} file(s) from backup.")
        self.progress_label.config(text="Waiting")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModLoaderGUI(root)
    root.mainloop()
