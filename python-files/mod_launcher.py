
import os, json, zipfile, shutil
from tkinter import StringVar, Listbox, END, messagebox
import ttkbootstrap as tb
from tkinterdnd2 import TkinterDnD, DND_FILES

# Lokasi tetap untuk folder mod
MOD_BASE = os.path.join(os.getenv("APPDATA"), "OptiCraft", "games", "com.mojang")
PACK_TYPES = {
    "Behavior Pack": "behavior_packs",
    "Resource Pack": "resource_packs",
    "Skin Pack": "skin_packs",
    "World": "minecraftWorlds"
}

class ModInstaller(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minecraft Bedrock Mod Installer")
        self.geometry("600x400")
        try:
            self.iconbitmap(default="launcher.ico")
        except:
            pass

        self.style = tb.Style("flatly")

        self.zip_path = None
        self.manifest_data = {}
        self.selected_type = StringVar(value="Behavior Pack")
        self.mod_info = StringVar(value="Drop mod .zip/.mcpack/.mcworld ke sini")

        self.build_ui()
        self.update_mod_list()

    def build_ui(self):
        tb.Label(self, textvariable=self.mod_info, wraplength=550, justify="center").pack(pady=10)

        drop_frame = tb.LabelFrame(self, text="Drop Area", width=500, height=80)
        drop_frame.pack(pady=5)
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind("<<Drop>>", self.on_drop)

        tb.Combobox(self, values=list(PACK_TYPES.keys()), textvariable=self.selected_type, state="readonly").pack(pady=5)
        tb.Button(self, text="Install", command=self.install_mod, bootstyle="success").pack(pady=5)

        self.mod_list = Listbox(self)
        self.mod_list.pack(pady=5, fill="both", expand=True)

        tb.Button(self, text="Hapus Mod", command=self.delete_selected_mod, bootstyle="danger").pack(pady=5)

    def on_drop(self, event):
        path = event.data.strip("{}")
        if path.endswith((".zip", ".mcpack", ".mcworld")):
            self.zip_path = path
            self.read_manifest()
        else:
            self.mod_info.set("Format tidak didukung!")

    def read_manifest(self):
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                if "manifest.json" in zip_ref.namelist():
                    with zip_ref.open("manifest.json") as mf:
                        self.manifest_data = json.load(mf)
                        name = self.manifest_data["header"]["name"]
                        desc = self.manifest_data["header"].get("description", "")
                        self.mod_info.set(f"{name}\n{desc}")
                else:
                    self.mod_info.set("manifest.json tidak ditemukan!")
        except:
            self.mod_info.set("Gagal membaca manifest!")

    def get_target_folder(self):
        ext = os.path.splitext(self.zip_path)[1].lower()
        if ext == ".mcworld":
            return "minecraftWorlds"
        elif ext == ".mcpack":
            return "resource_packs"
        else:
            return PACK_TYPES[self.selected_type.get()]

    def install_mod(self):
        if not self.zip_path:
            return self.mod_info.set("Belum ada file!")

        folder_type = self.get_target_folder()
        install_path = os.path.join(MOD_BASE, folder_type)
        os.makedirs(install_path, exist_ok=True)

        mod_name = os.path.splitext(os.path.basename(self.zip_path))[0]
        final_path = os.path.join(install_path, mod_name)

        if os.path.exists(final_path):
            shutil.rmtree(final_path)

        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(final_path)
            self.mod_info.set(f"Mod '{mod_name}' berhasil diinstal ke {folder_type}")
            self.update_mod_list()
        except:
            self.mod_info.set("Gagal ekstrak file!")

    def update_mod_list(self):
        self.mod_list.delete(0, END)
        selected = PACK_TYPES[self.selected_type.get()]
        folder = os.path.join(MOD_BASE, selected)
        if os.path.exists(folder):
            for item in os.listdir(folder):
                self.mod_list.insert(END, item)

    def delete_selected_mod(self):
        selection = self.mod_list.curselection()
        if not selection:
            return messagebox.showwarning("Pilih mod", "Pilih mod yang ingin dihapus.")

        mod_name = self.mod_list.get(selection[0])
        folder = os.path.join(MOD_BASE, PACK_TYPES[self.selected_type.get()], mod_name)

        if messagebox.askyesno("Konfirmasi", f"Hapus mod '{mod_name}'?"):
            shutil.rmtree(folder)
            self.update_mod_list()
            self.mod_info.set(f"Mod '{mod_name}' dihapus.")

if __name__ == "__main__":
    app = ModInstaller()
    app.mainloop()
