import os
import sys
import wmi
import ftplib
import hashlib
import tempfile
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

class DiskImager:
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Imager & FTP Uploader")
        self.root.geometry("600x400")
        
        self.ftp_host = tk.StringVar()
        self.ftp_user = tk.StringVar()
        self.ftp_pass = tk.StringVar()
        self.ftp_path = tk.StringVar(value="/")
        self.disk_letter = tk.StringVar()
        self.status = tk.StringVar(value="Готов к работе")
        self.progress_value = tk.IntVar()
        self.stop_flag = False
        
        self.create_ui()
        self.populate_disks()
    
    def create_ui(self):
        # FTP Settings Frame
        ftp_frame = ttk.LabelFrame(self.root, text="FTP Настройки", padding=10)
        ftp_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(ftp_frame, text="Сервер:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(ftp_frame, textvariable=self.ftp_host).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(ftp_frame, text="Пользователь:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(ftp_frame, textvariable=self.ftp_user).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(ftp_frame, text="Пароль:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(ftp_frame, textvariable=self.ftp_pass, show="*").grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        
        ttk.Label(ftp_frame, text="Путь на сервере:").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(ftp_frame, textvariable=self.ftp_path).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Disk Selection Frame
        disk_frame = ttk.LabelFrame(self.root, text="Выбор диска", padding=10)
        disk_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(disk_frame, text="Диск:").grid(row=0, column=0, sticky=tk.W)
        self.disk_combo = ttk.Combobox(disk_frame, textvariable=self.disk_letter, state="readonly")
        self.disk_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Progress Frame
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, variable=self.progress_value, maximum=100)
        self.progress.pack(fill=tk.X, expand=True)
        ttk.Label(progress_frame, textvariable=self.status).pack()
        
        # Button Frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_btn = ttk.Button(button_frame, text="Старт", command=self.start_process)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Стоп", command=self.stop_process, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
    
    def populate_disks(self):
        try:
            c = wmi.WMI()
            disks = []
            for disk in c.Win32_LogicalDisk():
                if disk.DriveType == 3:  # Fixed disks only
                    disks.append(f"{disk.DeviceID} ({disk.VolumeName})" if disk.VolumeName else disk.DeviceID)
            self.disk_combo['values'] = disks
            if disks:
                self.disk_combo.current(0)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список дисков: {str(e)}")
    
    def start_process(self):
        if not all([self.ftp_host.get(), self.ftp_user.get(), self.disk_letter.get()]):
            messagebox.showwarning("Предупреждение", "Заполните все обязательные поля")
            return
        
        disk = self.disk_letter.get()[0] if self.disk_letter.get() else ''
        if not disk.isalpha():
            messagebox.showwarning("Предупреждение", "Выберите корректный диск")
            return
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.stop_flag = False
        
        threading.Thread(target=self.create_and_upload_image, daemon=True).start()
    
    def stop_process(self):
        self.stop_flag = True
        self.status.set("Остановка...")
    
    def create_and_upload_image(self):
        disk = self.disk_letter.get()[0].upper()
        image_path = os.path.join(tempfile.gettempdir(), f"disk_{disk}_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.img")
        
        try:
            # Step 1: Create disk image
            self.status.set(f"Создание образа диска {disk}:...")
            self.create_disk_image(disk, image_path)
            if self.stop_flag:
                self.cleanup(image_path)
                return
            
            # Step 2: Upload to FTP
            self.status.set("Подключение к FTP серверу...")
            self.upload_to_ftp(image_path)
            
            messagebox.showinfo("Успех", "Процесс завершен успешно!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        finally:
            self.cleanup(image_path)
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.progress_value.set(0)
            self.status.set("Готов к работе")
    
    def create_disk_image(self, disk, output_path):
        disk_path = f"\\\\.\\{disk}:"
        total_bytes = os.path.getsize(disk_path)
        chunk_size = 1024 * 1024  # 1MB chunks
        bytes_read = 0
        
        try:
            with open(disk_path, "rb") as disk_file, open(output_path, "wb") as image_file:
                while not self.stop_flag:
                    chunk = disk_file.read(chunk_size)
                    if not chunk:
                        break
                    
                    image_file.write(chunk)
                    bytes_read += len(chunk)
                    
                    # Update progress
                    progress = int((bytes_read / total_bytes) * 100)
                    self.progress_value.set(progress)
                    self.status.set(f"Создание образа: {progress}% ({bytes_read/1024/1024:.1f} MB / {total_bytes/1024/1024:.1f} MB)")
                    
                    # Allow UI to update
                    self.root.update()
        
        except PermissionError:
            raise Exception("Недостаточно прав для доступа к диску. Запустите программу от имени администратора.")
    
    def upload_to_ftp(self, file_path):
        try:
            file_size = os.path.getsize(file_path)
            uploaded = 0
            chunk_size = 1024 * 1024  # 1MB chunks
            
            with ftplib.FTP(self.ftp_host.get(), self.ftp_user.get(), self.ftp_pass.get()) as ftp, open(file_path, 'rb') as file:
                ftp.cwd(self.ftp_path.get())
                remote_filename = os.path.basename(file_path)
                
                def callback(data):
                    nonlocal uploaded
                    uploaded += len(data)
                    progress = int((uploaded / file_size) * 100)
                    self.progress_value.set(progress)
                    self.status.set(f"Загрузка на FTP: {progress}% ({uploaded/1024/1024:.1f} MB / {file_size/1024/1024:.1f} MB)")
                    self.root.update()
                    return not self.stop_flag
                
                ftp.storbinary(f"STOR {remote_filename}", file, blocksize=chunk_size, callback=callback)
                
                if self.stop_flag:
                    ftp.delete(remote_filename)
                    raise Exception("Загрузка прервана пользователем")
        
        except ftplib.all_errors as e:
            raise Exception(f"Ошибка FTP: {str(e)}")
    
    def cleanup(self, file_path):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

if __name__ == "__main__":
    try:
        import wmi
    except ImportError:
        print("Установите модуль wmi: pip install wmi")
        sys.exit(1)
    
    root = tk.Tk()
    app = DiskImager(root)
    root.mainloop()