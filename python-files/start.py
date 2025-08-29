import os
import requests
from datetime import datetime
import time
import socket
import logging

# تنظیم لاگ برای خروجی ترمینال و فایل
log_file = 'C:\\Scripts\\upload_log.txt'
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# تنظیم هندلر برای ترمینال با کدگذاری utf-8
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
console_handler.setLevel(logging.INFO)
console_handler.stream.reconfigure(encoding='utf-8')  # اطمینان از پشتیبانی کاراکترهای فارسی

# تنظیم هندلر برای فایل
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
file_handler.setLevel(logging.INFO)

# تنظیم لاگر
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

def find_latest_docx_files(root_dir, num_files=100):
    logging.info(f"جستجوی فایل‌های .docx در {root_dir}")
    docx_files = []
    
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.docx'):
                filepath = os.path.join(subdir, file)
                try:
                    mod_time = os.path.getmtime(filepath)
                    docx_files.append((filepath, mod_time))
                    logging.info(f"فایل پیدا شد: {filepath}")
                except OSError as e:
                    logging.error(f"خطا در دسترسی به {filepath}: {str(e)}")
    
    logging.info(f"تعداد فایل‌های پیدا شده: {len(docx_files)}")
    docx_files.sort(key=lambda x: x[1], reverse=True)
    
    selected_files = [filepath for filepath, _ in docx_files[:num_files]]
    if selected_files:
        logging.info(f"{len(selected_files)} فایل انتخاب شد")
    else:
        logging.warning("هیچ فایل .docx پیدا نشد")
    
    return selected_files

def is_internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def upload_files(file_paths, server_url, retry_interval=20, max_attempts=5):
    logging.info(f"آپلود {len(file_paths)} فایل به {server_url}")
    
    for filepath in file_paths:
        logging.info(f"پردازش فایل: {filepath}")
        attempt = 0
        last_error = None
        
        while attempt < max_attempts:
            attempt += 1
            if not is_internet_available():
                if attempt == 1:
                    logging.warning(f"اینترنت قطع است. تلاش مجدد برای {filepath} بعد از {retry_interval} ثانیه")
                time.sleep(retry_interval)
                continue
            
            try:
                logging.info(f"تلاش {attempt} برای آپلود {filepath}")
                with open(filepath, 'rb') as f:
                    files = {'file': (os.path.basename(filepath), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                    response = requests.post(server_url, files=files, timeout=60)
                    if response.status_code == 200:
                        logging.info(f"آپلود موفقیت‌آمیز: {filepath}")
                        break
                    else:
                        last_error = f"خطا در آپلود: کد {response.status_code} - {response.text}"
                        if attempt == 1:
                            logging.error(last_error)
                        time.sleep(retry_interval)
            except requests.exceptions.RequestException as e:
                last_error = f"خطای شبکه: {str(e)}"
                if attempt == 1:
                    logging.error(last_error)
                time.sleep(retry_interval)
            except Exception as e:
                last_error = f"خطای غیرمنتظره: {str(e)}"
                logging.error(last_error)
                time.sleep(retry_interval)
        
        if attempt >= max_attempts:
            logging.error(f"آپلود {filepath} پس از {max_attempts} تلاش ناموفق بود: {last_error}")

# تنظیمات
root_dir = 'C:/Users'
server_url = 'http://3.142.189.155:8000/upload'

logging.info("شروع اسکریپت کلاینت")
file_paths = find_latest_docx_files(root_dir)
upload_files(file_paths, server_url)
logging.info("اسکریپت کلاینت به پایان رسید")