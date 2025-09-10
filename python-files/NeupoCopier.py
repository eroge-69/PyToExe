import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import re
import threading
import time

class FolderCopier:
    def __init__(self, root):
        self.root = root
        self.root.title("Копировщик папок для VFX")
        self.root.geometry("800x600")
        
        self.source_path = tk.StringVar()
        self.destination_path = tk.StringVar()
        self.is_copying = False
        self.is_paused = False
        self.pause_event = threading.Event()
        self.current_shot_progress = 0
        self.current_shot_total = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Source path selection
        tk.Label(self.root, text="Исходный путь:").pack(pady=5)
        source_frame = tk.Frame(self.root)
        source_frame.pack(pady=5, padx=20, fill='x')
        
        tk.Entry(source_frame, textvariable=self.source_path, width=70).pack(side='left', padx=5)
        tk.Button(source_frame, text="Обзор", command=self.browse_source).pack(side='left', padx=5)
        
        # Destination path selection
        tk.Label(self.root, text="Целевой путь:").pack(pady=5)
        dest_frame = tk.Frame(self.root)
        dest_frame.pack(pady=5, padx=20, fill='x')
        
        tk.Entry(dest_frame, textvariable=self.destination_path, width=70).pack(side='left', padx=5)
        tk.Button(dest_frame, text="Обзор", command=self.browse_destination).pack(side='left', padx=5)
        
        # Progress frames
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=15, padx=20, fill='x')
        
        # Overall progress
        tk.Label(progress_frame, text="Общий прогресс:").pack(anchor='w')
        self.overall_progress = ttk.Progressbar(progress_frame, orient='horizontal', length=400, mode='determinate')
        self.overall_progress.pack(fill='x', pady=5)
        self.overall_label = tk.Label(progress_frame, text="Обработано: 0/0")
        self.overall_label.pack(anchor='w')
        
        # Current shot progress
        tk.Label(progress_frame, text="Текущий шот:").pack(anchor='w', pady=(10, 0))
        self.shot_progress = ttk.Progressbar(progress_frame, orient='horizontal', length=400, mode='determinate')
        self.shot_progress.pack(fill='x', pady=5)
        self.shot_label = tk.Label(progress_frame, text="Готов к работе")
        self.shot_label.pack(anchor='w')
        
        # Status label
        self.status_label = tk.Label(self.root, text="Готов к работе", font=('Arial', 10, 'bold'))
        self.status_label.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Copy button
        self.copy_button = tk.Button(button_frame, text="Начать копирование", command=self.start_copying, 
                                   bg='#4CAF50', fg='white', font=('Arial', 10), relief='raised')
        self.copy_button.pack(side='left', padx=5)
        
        # Pause button
        self.pause_button = tk.Button(button_frame, text="Пауза", command=self.toggle_pause,
                                    bg='#FF9800', fg='white', font=('Arial', 10), relief='raised', state='disabled')
        self.pause_button.pack(side='left', padx=5)
        
        # Stop button
        self.stop_button = tk.Button(button_frame, text="Остановить", command=self.stop_copying,
                                   bg='#F44336', fg='white', font=('Arial', 10), relief='raised', state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        # Log text area
        tk.Label(self.root, text="Лог операций:").pack(pady=5)
        log_frame = tk.Frame(self.root)
        log_frame.pack(pady=5, padx=20, fill='both', expand=True)
        
        self.log_text = tk.Text(log_frame, height=12, width=90)
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def browse_source(self):
        if self.is_copying:
            return
        path = filedialog.askdirectory(title="Выберите исходную папку")
        if path:
            self.source_path.set(path)
            
    def browse_destination(self):
        if self.is_copying:
            return
        path = filedialog.askdirectory(title="Выберите целевую папку")
        if path:
            self.destination_path.set(path)
            
    def log_message(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_progress(self, current, total, shot_name="", shot_current=0, shot_total=0):
        """Update progress bars"""
        if total > 0:
            self.overall_progress['value'] = current
            self.overall_progress['maximum'] = total
            self.overall_label.config(text=f"Обработано: {current}/{total}")
        
        if shot_total > 0:
            self.shot_progress['value'] = shot_current
            self.shot_progress['maximum'] = shot_total
            self.shot_label.config(text=f"{shot_name}: {shot_current}/{shot_total} файлов")
        
        self.root.update_idletasks()
        
    def check_pause(self):
        """Check if paused and wait if needed"""
        while self.is_paused and self.is_copying:
            time.sleep(0.1)
            self.root.update_idletasks()
        
    def get_latest_version(self, folder_path, shot_name):
        """Find the latest version folder in out directory"""
        version_folders = []
        
        try:
            for item in os.listdir(folder_path):
                if item.startswith(shot_name) and '_comp_v' in item:
                    # Extract version number
                    version_match = re.search(r'_v(\d+)$', item)
                    if version_match:
                        version = int(version_match.group(1))
                        version_folders.append((version, item))
        except Exception as e:
            self.log_message(f"Ошибка при чтении папки {folder_path}: {str(e)}")
            return None
            
        if not version_folders:
            return None
            
        # Get folder with highest version number
        latest_version = max(version_folders, key=lambda x: x[0])
        return latest_version[1]
    
    def copy_folder_with_progress(self, src, dst, shot_name):
        """Copy folder with progress tracking"""
        try:
            if os.path.exists(dst):
                shutil.rmtree(dst)
            
            # Count total files for progress
            total_files = 0
            for root, dirs, files in os.walk(src):
                total_files += len(files)
            
            if total_files == 0:
                shutil.copytree(src, dst)
                return True
            
            copied_files = 0
            os.makedirs(dst, exist_ok=True)
            
            for root, dirs, files in os.walk(src):
                # Create directories
                for dir in dirs:
                    if not self.is_copying:  # Check if stopped
                        return False
                    self.check_pause()  # Check if paused
                    
                    src_dir = os.path.join(root, dir)
                    dst_dir = os.path.join(dst, os.path.relpath(src_dir, src))
                    os.makedirs(dst_dir, exist_ok=True)
                
                # Copy files
                for file in files:
                    if not self.is_copying:  # Check if stopped
                        return False
                    self.check_pause()  # Check if paused
                    
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dst, os.path.relpath(src_file, src))
                    
                    shutil.copy2(src_file, dst_file)
                    copied_files += 1
                    
                    # Update progress every 10 files or so to avoid UI lag
                    if copied_files % 10 == 0:
                        self.update_progress(
                            self.overall_progress['value'], 
                            self.overall_progress['maximum'],
                            shot_name,
                            copied_files,
                            total_files
                        )
                        time.sleep(0.01)  # Small delay to keep UI responsive
            
            return True
        except Exception as e:
            self.log_message(f"Ошибка копирования {src} -> {dst}: {str(e)}")
            return False
    
    def should_skip_copying(self, shot_dest_path, plates_exists, hi_res_version):
        """Check if we should skip copying based on existing files"""
        # Check if hi-res already exists
        if hi_res_version:
            hi_res_dest = os.path.join(shot_dest_path, "out", hi_res_version)
            if os.path.exists(hi_res_dest):
                return True, "Хайрез уже существует в целевой папке"
        
        # Check if plates already exists (only if we have plates to copy)
        if plates_exists:
            plates_dest = os.path.join(shot_dest_path, "plates")
            if os.path.exists(plates_dest):
                return True, "Plates папка уже существует в целевой папке"
        
        return False, ""
    
    def copy_thread(self):
        """Main copying function running in separate thread"""
        source = self.source_path.get()
        destination = self.destination_path.get()
        
        try:
            # Find all shot folders
            shot_folders = []
            for item in os.listdir(source):
                if not self.is_copying:  # Check if stopped
                    break
                self.check_pause()  # Check if paused
                
                item_path = os.path.join(source, item)
                if os.path.isdir(item_path) and '_' in item and item[0].isdigit():
                    shot_folders.append(item)
            
            total_folders = len(shot_folders)
            if total_folders == 0:
                self.log_message("Не найдено папок с шотами")
                return
                
            self.overall_progress['maximum'] = total_folders
            copied_count = 0
            skipped_no_hi_res = 0
            skipped_already_exists = 0
            
            for i, shot_folder in enumerate(shot_folders):
                if not self.is_copying:  # Check if stopped
                    break
                self.check_pause()  # Check if paused
                    
                self.status_label.config(text=f"Проверка: {shot_folder}")
                self.update_progress(i, total_folders, "Проверка...", 0, 0)
                
                shot_source_path = os.path.join(source, shot_folder)
                shot_dest_path = os.path.join(destination, shot_folder)
                
                # Check for hi-res versions
                has_hi_res = False
                hi_res_version = None
                out_source = os.path.join(shot_source_path, "out")
                
                if os.path.exists(out_source):
                    hi_res_version = self.get_latest_version(out_source, f"mon2_{shot_folder}_comp")
                    has_hi_res = hi_res_version is not None
                
                # Если нет хайреза - пропускаем ВСЮ папку
                if not has_hi_res:
                    self.log_message(f"✗ {shot_folder}: Не найдено версий хайреза - пропускаем")
                    skipped_no_hi_res += 1
                    continue
                
                # Check if plates exists
                has_plates = os.path.exists(os.path.join(shot_source_path, "plates"))
                
                # Check if files already exist in destination
                skip, reason = self.should_skip_copying(shot_dest_path, has_plates, hi_res_version)
                if skip:
                    self.log_message(f"✗ {shot_folder}: {reason} - пропускаем")
                    skipped_already_exists += 1
                    continue
                
                # Start copying this shot
                self.status_label.config(text=f"Копирование: {shot_folder}")
                self.log_message(f"✓ {shot_folder}: Начинаю копирование...")
                
                # Create destination folder
                os.makedirs(shot_dest_path, exist_ok=True)
                
                # Copy plates folder if exists
                if has_plates:
                    plates_source = os.path.join(shot_source_path, "plates")
                    plates_dest = os.path.join(shot_dest_path, "plates")
                    
                    self.log_message(f"  Копирую plates папку...")
                    if not self.copy_folder_with_progress(plates_source, plates_dest, shot_folder):
                        if not self.is_copying:
                            break
                        self.log_message("  ✗ Ошибка копирования plates папки")
                
                # Copy hi-res version
                out_source = os.path.join(shot_source_path, "out")
                out_dest = os.path.join(shot_dest_path, "out")
                
                version_source = os.path.join(out_source, hi_res_version)
                version_dest = os.path.join(out_dest, hi_res_version)
                
                self.log_message(f"  Копирую хайрез: {hi_res_version}")
                
                if self.copy_folder_with_progress(version_source, version_dest, shot_folder):
                    self.log_message("  ✓ Хайрез скопирован")
                    copied_count += 1
                else:
                    if not self.is_copying:
                        break
                    self.log_message("  ✗ Ошибка копирования хайреза")
                
                self.update_progress(i + 1, total_folders, "Завершено", 0, 0)
            
            # Final update
            status_text = "Копирование завершено" if self.is_copying else "Копирование остановлено"
            if self.is_paused:
                status_text = "Копирование приостановлено"
                
            self.status_label.config(text=status_text)
            self.log_message("\n" + "="*50)
            self.log_message(f"{status_text}!")
            self.log_message(f"Обработано папок: {total_folders}")
            self.log_message(f"Скопировано шотов: {copied_count}")
            self.log_message(f"Пропущено (нет хайреза): {skipped_no_hi_res}")
            self.log_message(f"Пропущено (уже существуют): {skipped_already_exists}")
            
        except Exception as e:
            self.log_message(f"Критическая ошибка: {str(e)}")
        finally:
            self.is_copying = False
            self.is_paused = False
            self.copy_button.config(state='normal')
            self.pause_button.config(state='disabled', text="Пауза")
            self.stop_button.config(state='disabled')
            self.shot_label.config(text="Готов к работе")
    
    def start_copying(self):
        if self.is_copying:
            return
            
        source = self.source_path.get()
        destination = self.destination_path.get()
        
        if not source or not destination:
            messagebox.showerror("Ошибка", "Пожалуйста, укажите исходный и целевой пути")
            return
            
        if not os.path.exists(source):
            messagebox.showerror("Ошибка", "Исходный путь не существует")
            return
            
        # Reset UI
        self.is_copying = True
        self.is_paused = False
        self.copy_button.config(state='disabled')
        self.pause_button.config(state='normal')
        self.stop_button.config(state='normal')
        self.overall_progress['value'] = 0
        self.shot_progress['value'] = 0
        self.log_text.delete(1.0, tk.END)
        
        self.log_message("="*50)
        self.log_message("Начало копирования...")
        self.log_message("Копирование ТОЛЬКО если есть хайрез в out папке")
        
        # Start copying in separate thread
        thread = threading.Thread(target=self.copy_thread)
        thread.daemon = True
        thread.start()
    
    def toggle_pause(self):
        """Toggle pause state"""
        if not self.is_copying:
            return
            
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_button.config(text="Продолжить", bg='#2196F3')
            self.status_label.config(text="Копирование приостановлено")
            self.log_message("\n⏸️  Копирование приостановлено")
        else:
            self.pause_button.config(text="Пауза", bg='#FF9800')
            self.status_label.config(text="Копирование продолжается")
            self.log_message("\n▶️  Копирование продолжается")
    
    def stop_copying(self):
        if self.is_copying:
            self.is_copying = False
            self.is_paused = False
            self.status_label.config(text="Останавливаю...")
            self.log_message("\n⏹️  Остановка копирования...")

def main():
    root = tk.Tk()
    app = FolderCopier(root)
    root.mainloop()

if __name__ == "__main__":
    main()