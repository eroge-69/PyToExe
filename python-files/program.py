import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, scrolledtext
from tkinterdnd2 import TkinterDnD, DND_FILES
from ppadb.client import Client
import sys
import getpass
from datetime import datetime
from operator import itemgetter
import time
import threading

class PhoneManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Telefon Yöneticisi")
        self.root.geometry("900x600")
        self.adb = Client(host="127.0.0.1", port=5037)
        self.device = None
        self.file_list = []
        self.current_category = "Müzik"
        self.phone_files = {}
        self.install_dir = os.path.expanduser("~/TelefonYoneticisi")
        self.has_sdcard = False
        self.sdcard_path = "/mnt/sdcard/"

        # Dosya türü uzantıları
        self.valid_extensions = {
            "Müzik": [".mp3", ".m4a", ".wav", ".ogg"],
            "Fotoğraf": [".jpg", ".jpeg", ".png", ".gif"],
            "Video": [".mp4", ".mkv", ".avi", ".mov"],
            "Belge": [".pdf", ".doc", ".docx", ".txt"],
            "Ses Kayıtları": [".amr", ".aac", ".m4a"],
            "Her Şey": [".mp3", ".m4a", ".wav", ".ogg", ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mkv", ".avi", ".mov", ".pdf", ".doc", ".docx", ".txt", ".amr", ".aac"]
        }

        # Kategorilere göre cihaz yolları (dahili depolama ve hafıza kartı için)
        self.category_paths = {
            "Müzik": ["Music/", "Music/"],
            "Fotoğraf": ["Pictures/", "Pictures/"],
            "Video": ["Movies/", "Movies/"],
            "Belge": ["Documents/", "Documents/"],
            "Ses Kayıtları": ["Recordings/", "Recordings/"],
            "Her Şey": ["", ""]
        }

        # Cihaz bağlantısını ve hafıza kartını kontrol et
        self.connect_device()
        self.check_sdcard()

        # GUI Arayüzü
        self.setup_ui()

    def connect_device(self):
        try:
            devices = self.adb.devices()
            if devices:
                self.device = devices[0]
                print("Cihaz bağlandı:", self.device.serial)
            else:
                messagebox.showwarning("Bağlantı Hatası", "Lütfen USB ile bir Android cihaz bağlayın ve USB hata ayıklama modunu etkinleştirin.")
        except Exception as e:
            messagebox.showerror("Hata", f"Cihaz bağlanamadı: {e}")

    def check_sdcard(self):
        if not self.device:
            return
        try:
            result = self.device.shell("ls /mnt/sdcard/")
            if result.strip():
                self.has_sdcard = True
                messagebox.showinfo("Hafıza Kartı", "Hafıza kartı algılandı!", parent=self.root)
            else:
                self.has_sdcard = False
                messagebox.showinfo("Hafıza Kartı", "Telefonda hafıza kartı yok!", parent=self.root)
        except Exception:
            self.has_sdcard = False
            messagebox.showinfo("Hafıza Kartı", "Telefonda hafıza kartı yok!", parent=self.root)

    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5)
        tk.Button(top_frame, text="Dosya/Klasör Ekle", command=self.add_files_dialog).pack(side=tk.LEFT, padx=5)
        
        tk.Label(top_frame, text="Sırala:").pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar(value="Ad (A-Z)")
        sort_options = ["Ad (A-Z)", "Ad (Z-A)", "Tür (A-Z)", "Tür (Z-A)", "Boyut (Küçük-Büyük)", "Boyut (Büyük-Küçük)", "Tarih (Yeni-Eski)", "Tarih (Eski-Yeni)"]
        tk.OptionMenu(top_frame, self.sort_var, *sort_options, command=self.sort_files).pack(side=tk.LEFT, padx=5)

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tabs_frame = tk.Frame(self.main_frame)
        self.tabs_frame.pack(side=tk.LEFT, fill=tk.Y)

        categories = ["Müzik", "Fotoğraf", "Video", "Belge", "Ses Kayıtları", "Her Şey", "Telefonum"]
        for category in categories:
            btn = tk.Button(self.tabs_frame, text=category, command=lambda c=category: self.switch_category(c))
            btn.pack(fill=tk.X, pady=5)

        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(self.content_frame, width=60, height=20)
        self.listbox.pack(pady=10)
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind("<<Drop>>", self.drop_files)

        self.phone_tabs = ttk.Notebook(self.content_frame)
        self.phone_tabs.pack(fill=tk.BOTH, expand=True)
        self.phone_tabs.hide()

        self.phone_lists = {}
        for category in list(self.valid_extensions.keys()):
            frame = tk.Frame(self.phone_tabs)
            self.phone_tabs.add(frame, text=category)
            listbox = tk.Listbox(frame, width=60, height=20)
            listbox.pack(pady=5)
            btn_frame = tk.Frame(frame)
            btn_frame.pack(pady=5)
            tk.Button(btn_frame, text="Seçileni Sil", command=lambda c=category, lb=listbox: self.delete_file(c, lb)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Bilgisayara At", command=lambda c=category, lb=listbox: self.transfer_to_pc(c, lb)).pack(side=tk.LEFT, padx=5)
            self.phone_lists[category] = listbox

        btn_frame = tk.Frame(self.content_frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Telefona At", command=self.transfer_files).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Listeyi Temizle", command=self.clear_list).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Programı Kaldır", command=self.uninstall_program).pack(side=tk.LEFT, padx=5)

    def switch_category(self, category):
        self.current_category = category
        self.listbox.delete(0, tk.END)
        self.file_list = []
        self.root.title(f"Telefon Yöneticisi - {category}")

        if category == "Telefonum":
            self.listbox.pack_forget()
            self.phone_tabs.pack(fill=tk.BOTH, expand=True)
            self.load_phone_files()
        else:
            self.phone_tabs.pack_forget()
            self.listbox.pack(pady=10)
            self.sort_files(self.sort_var.get())

    def add_files_dialog(self):
        if self.current_category == "Telefonum":
            messagebox.showwarning("Hata", "Telefonum sekmesinde dosya eklenemez!")
            return
        files = filedialog.askopenfilenames(title="Dosya Seç", filetypes=[("Tüm Dosyalar", "*.*")])
        folders = filedialog.askdirectory(title="Klasör Seç", mustexist=True)
        if files:
            self.add_files(files)
        if folders:
            self.add_files([folders])

    def drop_files(self, event):
        if self.current_category == "Telefonum":
            messagebox.showwarning("Hata", "Telefonum sekmesinde dosya eklenemez!")
            return
        files = self.root.splitlist(event.data)
        self.add_files(files)

    def add_files(self, files):
        for file in files:
            if os.path.exists(file):
                if os.path.isfile(file):
                    ext = os.path.splitext(file)[1].lower()
                    if self.current_category != "Her Şey" and ext not in self.valid_extensions[self.current_category]:
                        messagebox.showerror("Hata", f"Bu konuma {ext} dosyası atılamaz! {self.current_category} için uygun dosya türleri: {', '.join(self.valid_extensions[self.current_category])}")
                        continue
                    if file not in self.file_list:
                        self.file_list.append(file)
                else:
                    valid = True
                    for root, _, subfiles in os.walk(file):
                        for f in subfiles:
                            ext = os.path.splitext(f)[1].lower()
                            if self.current_category != "Her Şey" and ext not in self.valid_extensions[self.current_category]:
                                valid = False
                                messagebox.showerror("Hata", f"Klasörde {ext} dosyası bulundu! {self.current_category} için uygun dosya türleri: {', '.join(self.valid_extensions[self.current_category])}")
                                break
                        if not valid:
                            break
                    if valid and file not in self.file_list:
                        self.file_list.append(file)
        self.sort_files(self.sort_var.get())

    def clear_list(self):
        if self.current_category == "Telefonum":
            messagebox.showwarning("Hata", "Telefonum sekmesinde liste temizlenemez!")
            return
        if messagebox.askyesno("Listeyi Temizle", f"{self.current_category} listesi temizlensin mi? Telefonunuza hiçbir şey yüklenmeyecek veya telefonunuzdaki veriler silinmeyecek."):
            self.listbox.delete(0, tk.END)
            self.file_list = []

    def get_storage_path(self, operation="at"):
        if not self.has_sdcard:
            return "/sdcard/"
        choice = messagebox.askyesno("Depolama Seçimi", f"Dosyaları {'hafıza kartına' if operation == 'at' else 'hafıza kartından'} mı yoksa {'dahili depolamaya' if operation == 'at' else 'dahili depolamadan'} mı {operation == 'at' and 'atmak' or 'almak'} istiyorsunuz?\nEvet: Hafıza Kartı\nHayır: Dahili Depolama")
        return self.sdcard_path if choice else "/sdcard/"

    def get_target_path(self, file):
        ext = os.path.splitext(file)[1].lower()
        for category, extensions in self.valid_extensions.items():
            if category != "Her Şey" and ext in extensions:
                return f"{self.category_paths[category][0]}{os.path.basename(file)}"
        return f"Download/{os.path.basename(file)}"  # Varsayılan klasör

    def transfer_files(self):
        if self.current_category == "Telefonum":
            messagebox.showwarning("Hata", "Telefonum sekmesinde dosya aktarımı yapılamaz!")
            return
        if not self.device:
            messagebox.showerror("Hata", "Cihaz bağlı değil!")
            return
        if not self.file_list:
            messagebox.showwarning("Hata", "Aktarılacak dosya yok!")
            return

        base_path = self.get_storage_path("at")
        try:
            for file in self.file_list:
                target_path = base_path + (self.category_paths[self.current_category][0] if self.current_category != "Her Şey" else "")
                if self.current_category == "Her Şey":
                    target_file = self.get_target_path(file)
                    target_path = f"{base_path}{target_file}"
                    self.device.shell(f"mkdir -p {os.path.dirname(target_path)}")
                else:
                    target_path = f"{target_path}{os.path.basename(file)}"
                    self.device.shell(f"mkdir -p {os.path.dirname(target_path)}")
                if os.path.isdir(file):
                    for root, _, files in os.walk(file):
                        for f in files:
                            src = os.path.join(root, f)
                            dest = f"{base_path}{self.get_target_path(f) if self.current_category == 'Her Şey' else self.category_paths[self.current_category][0] + os.path.basename(f)}"
                            self.device.push(src, dest)
                else:
                    self.device.push(file, target_path)
            messagebox.showinfo("Başarılı", f"Dosyalar {self.current_category} klasörüne aktarıldı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya aktarılamadı: {e}")

    def load_phone_files(self):
        if not self.device:
            messagebox.showerror("Hata", "Cihaz bağlı değil!")
            return
        self.phone_files = {}
        for category in self.valid_extensions.keys():
            self.phone_files[category] = []
            listbox = self.phone_lists[category]
            listbox.delete(0, tk.END)
            paths = [f"/sdcard/{self.category_paths[category][0]}"]
            if self.has_sdcard:
                paths.append(f"{self.sdcard_path}{self.category_paths[category][0]}")
            if category == "Her Şey":
                paths = []
                for cat, path in self.category_paths.items():
                    if cat != "Her Şey":
                        paths.append(f"/sdcard/{path[0]}")
                        if self.has_sdcard:
                            paths.append(f"{self.sdcard_path}{path[0]}")
            for path in paths:
                try:
                    files = self.device.shell(f"ls -l {path}").splitlines()
                    for line in files:
                        parts = line.split()
                        if len(parts) >= 8:
                            name = parts[-1]
                            size = int(parts[4]) if parts[4].isdigit() else 0
                            date_str = f"{parts[5]} {parts[6]} {parts[7]}"
                            try:
                                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                            except:
                                date = datetime.now()
                            ext = os.path.splitext(name)[1].lower()
                            self.phone_files[category].append({
                                "name": name,
                                "size": size,
                                "date": date,
                                "type": ext,
                                "path": f"{path}{name}"
                            })
                except Exception:
                    listbox.insert(tk.END, f"Dosyalar listelenemedi: {path}")
        self.sort_files(self.sort_var.get())

    def delete_file(self, category, listbox):
        if not self.device:
            messagebox.showerror("Hata", "Cihaz bağlı değil!")
            return
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("Hata", "Silmek için bir dosya seçin!")
            return
        file = listbox.get(selection[0])
        file_path = next(f["path"] for f in self.phone_files[category] if f["name"] == file)
        if messagebox.askyesno("Dosya Sil", f"{file} dosyası cihazdan silinsin mi?"):
            try:
                self.device.shell(f"rm \"{file_path}\"")
                listbox.delete(selection[0])
                self.phone_files[category] = [f for f in self.phone_files[category] if f["name"] != file]
                messagebox.showinfo("Başarılı", f"{file} silindi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya silinemedi: {e}")

    def transfer_to_pc(self, category, listbox):
        if not self.device:
            messagebox.showerror("Hata", "Cihaz bağlı değil!")
            return
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("Hata", "Aktarmak için bir dosya seçin!")
            return
        file = listbox.get(selection[0])
        file_path = next(f["path"] for f in self.phone_files[category] if f["name"] == file)
        dest_path = filedialog.askdirectory(title="Bilgisayarda Kaydetme Konumu Seç", mustexist=True)
        if not dest_path:
            return
        try:
            dest_file = os.path.join(dest_path, file)
            self.device.pull(file_path, dest_file)
            messagebox.showinfo("Başarılı", f"{file} bilgisayara aktarıldı: {dest_file}")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya aktarılamadı: {e}")

    def sort_files(self, sort_option):
        self.listbox.delete(0, tk.END)
        if self.current_category == "Telefonum":
            for category, listbox in self.phone_lists.items():
                listbox.delete(0, tk.END)
                files = self.phone_files.get(category, [])
                if sort_option == "Ad (A-Z)":
                    files.sort(key=lambda x: x["name"])
                elif sort_option == "Ad (Z-A)":
                    files.sort(key=lambda x: x["name"], reverse=True)
                elif sort_option == "Tür (A-Z)":
                    files.sort(key=lambda x: x["type"])
                elif sort_option == "Tür (Z-A)":
                    files.sort(key=lambda x: x["type"], reverse=True)
                elif sort_option == "Boyut (Küçük-Büyük)":
                    files.sort(key=lambda x: x["size"])
                elif sort_option == "Boyut (Büyük-Küçük)":
                    files.sort(key=lambda x: x["size"], reverse=True)
                elif sort_option == "Tarih (Yeni-Eski)":
                    files.sort(key=lambda x: x["date"], reverse=True)
                elif sort_option == "Tarih (Eski-Yeni)":
                    files.sort(key=lambda x: x["date"])
                for file in files:
                    listbox.insert(tk.END, file["name"])
        else:
            files = []
            for file in self.file_list:
                size = os.path.getsize(file) if os.path.isfile(file) else 0
                date = datetime.fromtimestamp(os.path.getmtime(file)) if os.path.isfile(file) else datetime.now()
                ext = os.path.splitext(file)[1].lower() if os.path.isfile(file) else ""
                files.append({
                    "name": os.path.basename(file),
                    "size": size,
                    "date": date,
                    "type": ext,
                    "path": file
                })
            if sort_option == "Ad (A-Z)":
                files.sort(key=lambda x: x["name"])
            elif sort_option == "Ad (Z-A)":
                files.sort(key=lambda x: x["name"], reverse=True)
            elif sort_option == "Tür (A-Z)":
                files.sort(key=lambda x: x["type"])
            elif sort_option == "Tür (Z-A)":
                files.sort(key=lambda x: x["type"], reverse=True)
            elif sort_option == "Boyut (Küçük-Büyük)":
                files.sort(key=lambda x: x["size"])
            elif sort_option == "Boyut (Büyük-Küçük)":
                files.sort(key=lambda x: x["size"], reverse=True)
            elif sort_option == "Tarih (Yeni-Eski)":
                files.sort(key=lambda x: x["date"], reverse=True)
            elif sort_option == "Tarih (Eski-Yeni)":
                files.sort(key=lambda x: x["date"])
            self.file_list = [f["path"] for f in files]
            for file in files:
                self.listbox.insert(tk.END, file["name"])

    def show_install_window(self):
        install_window = tk.Toplevel(self.root)
        install_window.title("Telefon Yöneticisi Kurulum")
        install_window.geometry("600x400")
        install_window.configure(bg="#1E90FF")

        tk.Label(install_window, text="Yıldız Teknolojileri Üretimi", font=("Arial", 16, "bold"), bg="#1E90FF", fg="white").pack(pady=10)
        progress = ttk.Progressbar(install_window, length=400, mode="determinate")
        progress.pack(pady=10)
        log_text = scrolledtext.ScrolledText(install_window, width=70, height=10, state="disabled", bg="black", fg="white")
        log_text.pack(pady=10)
        info_button = tk.Button(install_window, text="Ek Bilgi", command=lambda: self.show_file_info(install_window))
        info_button.pack(pady=5)

        file_info = []

        def extract_files():
            if getattr(sys, 'frozen', False):
                files = os.listdir(sys._MEIPASS)
                total_files = len(files)
                for i, file in enumerate(files):
                    src = os.path.join(sys._MEIPASS, file)
                    dest = os.path.join(self.install_dir, file)
                    os.makedirs(self.install_dir, exist_ok=True)
                    size = os.path.getsize(src) / (1024 * 1024)
                    date = datetime.fromtimestamp(os.path.getmtime(src)).strftime("%Y-%m-%d %H:%M")
                    file_info.append(f"Dosya: {file}, Konum: {dest}, Boyut: {size:.2f} MB, Tarih: {date}")
                    shutil.copy2(src, dest)
                    progress["value"] = (i + 1) / total_files * 100
                    log_text.configure(state="normal")
                    log_text.insert(tk.END, f"Dosya ayıklanıyor: {file} -> {dest}\n")
                    log_text.configure(state="disabled")
                    log_text.see(tk.END)
                    install_window.update()
                    time.sleep(0.1)
                progress["value"] = 100
                if messagebox.askyesno("Yönetimsel Erişim", "Kurulum için yönetimsel erişim izni gerekiyor. Devam edilsin mi?", parent=install_window):
                    self.install_components(install_window, log_text)
                else:
                    install_window.destroy()
                    sys.exit()

        def show_file_info(window):
            info_window = tk.Toplevel(window)
            info_window.title("Ayıklama Bilgileri")
            info_window.geometry("600x300")
            text = scrolledtext.ScrolledText(info_window, width=70, height=15)
            text.pack(pady=10)
            for info in file_info:
                text.insert(tk.END, info + "\n")
            text.configure(state="disabled")

        threading.Thread(target=extract_files, daemon=True).start()

    def install_components(self, install_window, log_text):
        log_text.configure(state="normal")
        log_text.delete(1.0, tk.END)
        log_text.insert(tk.END, "Kurulum başlıyor...\n")
        log_text.configure(state="disabled")
        components = ["Ana Uygulama", "ADB Desteği", "Kısayol Oluşturucu"]
        for component in components:
            log_text.configure(state="normal")
            log_text.insert(tk.END, f"{component} kuruluyor...\n")
            log_text.configure(state="disabled")
            log_text.see(tk.END)
            install_window.update()
            time.sleep(0.5)
            if component == "Kısayol Oluşturucu":
                self.create_shortcut()
            log_text.configure(state="normal")
            log_text.insert(tk.END, f"{component} kuruldu.\n")
            log_text.configure(state="disabled")
            log_text.see(tk.END)
            install_window.update()
            time.sleep(0.5)
        log_text.configure(state="normal")
        log_text.insert(tk.END, "Kurulum tamamlandı!\n")
        log_text.configure(state="disabled")
        install_window.destroy()

    def create_shortcut(self):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_name = "Telefon Yöneticisi.lnk"
        shortcut_path = os.path.join(desktop, shortcut_name)
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)

        if os.name == "nt":
            from win32com.client import Dispatch
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.IconLocation = exe_path
            shortcut.save()

    def uninstall_program(self):
        uninstall_window = tk.Toplevel(self.root)
        uninstall_window.title("Telefon Yöneticisi Kaldırma")
        uninstall_window.geometry("600x400")
        tk.Label(uninstall_window, text="Kaldırma sihirbazı, program dosyalarını topluyor...", font=("Arial", 12)).pack(pady=10)
        log_text = scrolledtext.ScrolledText(uninstall_window, width=70, height=15, state="disabled", bg="black", fg="white")
        log_text.pack(pady=10)

        def remove_files():
            if messagebox.askyesno("Programı Kaldır", "Telefon Yöneticisi'ni kaldırmak istediğinize emin misiniz?", parent=uninstall_window):
                log_text.configure(state="normal")
                log_text.insert(tk.END, "Kaldırma başlıyor...\n")
                log_text.configure(state="disabled")
                log_text.see(tk.END)
                uninstall_window.update()
                try:
                    if os.path.exists(self.install_dir):
                        for file in os.listdir(self.install_dir):
                            file_path = os.path.join(self.install_dir, file)
                            log_text.configure(state="normal")
                            log_text.insert(tk.END, f"Dosya kaldırılıyor: {file_path}\n")
                            log_text.configure(state="disabled")
                            log_text.see(tk.END)
                            uninstall_window.update()
                            os.remove(file_path)
                            time.sleep(0.1)
                        shutil.rmtree(self.install_dir)
                        log_text.configure(state="normal")
                        log_text.insert(tk.END, "Program dosyaları kaldırıldı.\n")
                        log_text.configure(state="disabled")
                    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                    shortcut_path = os.path.join(desktop, "Telefon Yöneticisi.lnk")
                    if os.path.exists(shortcut_path):
                        os.remove(shortcut_path)
                        log_text.configure(state="normal")
                        log_text.insert(tk.END, "Kısayol kaldırıldı.\n")
                        log_text.configure(state="disabled")
                    log_text.configure(state="normal")
                    log_text.insert(tk.END, "Kaldırma tamamlandı!\n")
                    log_text.configure(state="disabled")
                    uninstall_window.destroy()
                    sys.exit()
                except Exception as e:
                    log_text.configure(state="normal")
                    log_text.insert(tk.END, f"Kaldırma hatası: {e}\n")
                    log_text.configure(state="disabled")
            else:
                uninstall_window.destroy()

        threading.Thread(target=remove_files, daemon=True).start()

def main():
    root = TkinterDnD.Tk()
    app = PhoneManager(root)
    if not os.path.exists(os.path.expanduser("~/TelefonYoneticisi")):
        app.show_install_window()
    root.mainloop()

if __name__ == "__main__":
    main()