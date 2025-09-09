import pandas as pd
import shutil
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import base64
import smtplib
import time
from datetime import datetime
import math
import jdatetime
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import email.utils
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import webbrowser
from tkinter import font, colorchooser
import re
import logging
import traceback
from functools import wraps, lru_cache
from threading import Thread, Lock
import queue
import concurrent.futures
from contextlib import contextmanager
from typing import Optional, Tuple, List
import tempfile
import hashlib
import mimetypes
import ttkbootstrap as tb
from PIL import Image, ImageTk

# تنظیمات ایمیل پیش‌فرض
DEFAULT_EMAIL_SERVER = 'webmail.nak-mci.ir'
DEFAULT_PORT = 25
DEFAULT_SENDER_EMAIL = 'Aida.Abdi@nak-mci.ir'
DEFAULT_USERNAME = 'Aida.Abdi@naknet2.org'
DEFAULT_PASSWORD = 'Delvinkiani1403'
DEFAULT_LOGO = 'nak_logo.png'
DEFAULT_SIGNATURE = """با تشکر
آیدا عبدی
تیم لیدر پروژه ارس
شرکت نقش اول کیفیت"""
DEFAULT_SENDER_NAME = "Aida Abdi"

# تنظیم سیستم لاگ
def setup_logging():
    """تنظیم سیستم لاگ"""
    log_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    file_handler = logging.FileHandler('email_system.log', encoding='utf-8')
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

setup_logging()

# کلاس‌های Exception سفارشی
class EmailSystemException(Exception):
    """کلاس پایه برای خطاهای سیستم ایمیل"""
    pass

class FileProcessingException(EmailSystemException):
    """خطاهای مربوط به پردازش فایل"""
    pass

class EmailSendingException(EmailSystemException):
    """خطاهای مربوط به ارسال ایمیل"""
    pass

class ValidationException(EmailSystemException):
    """خطاهای اعتبارسنجی"""
    pass

def error_handler(func):
    """دکوریتر برای مدیریت خطاها"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except EmailSystemException:
            raise
        except FileNotFoundError as e:
            logging.error(f"File not found in {func.__name__}: {e}")
            raise FileProcessingException(f"فایل مورد نظر یافت نشد: {e}")
        except PermissionError as e:
            logging.error(f"Permission error in {func.__name__}: {e}")
            raise FileProcessingException(f"عدم دسترسی به فایل: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {e}")
            logging.error(traceback.format_exc())
            raise EmailSystemException(f"خطای غیرمنتظره: {str(e)}")
    return wrapper

class SecureSettings:
    """مدیریت امن تنظیمات"""
    
    def __init__(self):
        self.key = b'nak_email_system_key'
    
    def encrypt_password(self, password: str) -> str:
        """رمزگذاری رمز عبور"""
        try:
            encoded_password = password.encode('utf-8')
            encrypted_bytes = base64.b64encode(encoded_password)
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            logging.error(f"Error encrypting password: {e}")
            return ""

    def decrypt_password(self, encrypted_password: str) -> str:
        """رمزگشایی رمز عبور"""
        try:
            encrypted_bytes = encrypted_password.encode('utf-8')
            decrypted_bytes = base64.b64decode(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logging.error(f"Error decrypting password: {e}")
            return ""
            
    def save_settings_secure(self, settings: dict, file_path: str):
        """ذخیره امن تنظیمات"""
        secure_settings = settings.copy()
        
        if 'password' in secure_settings and secure_settings['password']:
            secure_settings['password'] = self.encrypt_password(secure_settings['password'])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(secure_settings, f, ensure_ascii=False, indent=2)

    def load_settings_secure(self, file_path: str) -> dict:
        """بارگذاری امن تنظیمات"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            if 'password' in settings and settings['password']:
                settings['password'] = self.decrypt_password(settings['password'])
            
            return settings
        except FileNotFoundError:
            return {}
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            return {}

class BackupManager:
    """مدیریت بکاپ و بازیابی"""
    
    def __init__(self, backup_dir="backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, source_path: Path, description: str = ""):
        """ایجاد بکاپ از فایل یا پوشه"""
        if not source_path.exists():
            return None
    
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source_path.stem}_{timestamp}"
        backup_path = self.backup_dir / backup_name
    
        try:
            if source_path.is_file():
                shutil.copy2(source_path, backup_path.with_suffix(source_path.suffix))
            elif source_path.is_dir():
                shutil.copytree(source_path, backup_path)
            
            info = {
                "source": str(source_path),
                "backup_time": timestamp,
                "description": description,
                "type": "file" if source_path.is_file() else "directory"
            }
            
            with open(backup_path.with_suffix('.info'), 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logging.error(f"Failed to create backup: {e}")
            return None

class DataValidator:
    """اعتبارسنجی داده‌ها"""
    
    @staticmethod
    def validate_email_advanced(email: str) -> Tuple[bool, str]:
        """اعتبارسنجی پیشرفته ایمیل"""
        if not email or not email.strip():
            return False, "ایمیل نمی‌تواند خالی باشد"
    
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "فرمت ایمیل نامعتبر است"
    
        suspicious_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
        domain = email.split('@')[1].lower()
        if domain in suspicious_domains:
            return False, "دامنه ایمیل مشکوک است"
    
        return True, "معتبر"
    
    @staticmethod
    def validate_province_data(province_name: str) -> Tuple[bool, str]:
        """اعتبارسنجی داده‌های استان"""
        if not province_name or not str(province_name).strip():
            return False, "نام استان نمی‌تواند خالی باشد"
    
        province_str = str(province_name).strip()
    
        if len(province_str) > 50:
            return False, "نام استان نمی‌تواند بیش از 50 کاراکتر باشد"
    
        invalid_chars = ['<', '>', '|', ':', '*', '?', '"', '/', '\\']
        if any(char in province_str for char in invalid_chars):
            return False, "نام استان حاوی کاراکترهای غیرمجاز است"
    
        return True, "معتبر"
    
    @staticmethod
    def validate_file_size(file_path: Path, max_size_mb: int = 50) -> Tuple[bool, str]:
        """اعتبارسنجی اندازه فایل"""
        try:
            file_size = file_path.stat().st_size
            max_size_bytes = max_size_mb * 1024 * 1024
        
            if file_size > max_size_bytes:
                return False, f"اندازه فایل ({file_size // (1024*1024)} مگابایت) بیش از حد مجاز ({max_size_mb} مگابایت) است"
        
            if file_size == 0:
                return False, "فایل خالی است"
        
            return True, "معتبر"
        
        except Exception as e:
            return False, f"خطا در بررسی فایل: {e}"

class RetryManager:
    """مدیریت تلاش مجدد برای عملیات ناموفق"""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        self.max_retries = max_retries
        self.delay = delay
    
    def retry_operation(self, operation, *args, **kwargs):
        """تلاش مجدد برای انجام عملیات"""
        last_exception = None
    
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {self.delay} seconds...")
                    time.sleep(self.delay * (2 ** attempt))
                else:
                    logging.error(f"All {self.max_retries + 1} attempts failed")
    
        raise last_exception

class EmailQueue:
    """مدیریت صف ارسال ایمیل"""
    
    def __init__(self, max_workers=3):
        self.queue = queue.Queue()
        self.max_workers = max_workers
        self.lock = Lock()
        self.stats = {
            'sent': 0,
            'failed': 0,
            'total': 0,
            'failed_provinces': []
        }
        self.cancelled = False
    
    def add_email(self, email_data):
        """اضافه کردن ایمیل به صف"""
        self.queue.put(email_data)
        with self.lock:
            self.stats['total'] += 1
    
    def cancel(self):
        """لغو پردازش صف"""
        self.cancelled = True
    
    def process_queue(self, callback=None):
        """پردازش صف با استفاده از Thread Pool"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            while not self.queue.empty() and not self.cancelled:
                try:
                    email_data = self.queue.get_nowait()
                    future = executor.submit(self._send_email_worker, email_data)
                    futures.append((future, email_data))
                except queue.Empty:
                    break
            
            for future, email_data in futures:
                if self.cancelled:
                    future.cancel()
                    continue
                
                try:
                    result = future.result(timeout=60)
                    with self.lock:
                        if result:
                            self.stats['sent'] += 1
                        else:
                            self.stats['failed'] += 1
                            self.stats['failed_provinces'].append(email_data['province_name'])
                    
                    if callback:
                        callback(email_data['province_name'], result, self.stats.copy())
                        
                except concurrent.futures.TimeoutError:
                    logging.error(f"Timeout sending email to {email_data['province_name']}")
                    with self.lock:
                        self.stats['failed'] += 1
                        self.stats['failed_provinces'].append(email_data['province_name'])
                except Exception as e:
                    logging.error(f"Error in future result: {e}")
                    with self.lock:
                        self.stats['failed'] += 1
                        self.stats['failed_provinces'].append(email_data['province_name'])
    
    def _send_email_worker(self, email_data):
        """worker برای ارسال ایمیل"""
        try:
            return send_email_with_retry(**email_data)
        except Exception as e:
            logging.error(f"Error in email worker: {e}")
            return False

@contextmanager
def secure_smtp_connection(server, port, username, password):
    """مدیریت امن اتصال SMTP"""
    server_conn = None
    try:
        server_conn = smtplib.SMTP(server, port=port)
        server_conn.ehlo()
        server_conn.starttls()
        server_conn.ehlo()
        server_conn.login(username, password)
        yield server_conn
    except Exception as e:
        logging.error(f"SMTP connection error: {e}")
        raise
    finally:
        if server_conn:
            try:
                server_conn.quit()
            except:
                pass

@lru_cache(maxsize=100)
def get_province_emails_cached(province):
    """نسخه کش شده دریافت ایمیل‌های استان"""
    try:
        df = pd.read_excel('email_list.xlsx', sheet_name=province)
        df = df.astype(str)
    
        to_emails = df[df['نوع'].str.upper() == 'TO']['ایمیل'].replace('nan', '').str.strip().tolist()
        cc_emails = df[df['نوع'].str.upper() == 'CC']['ایمیل'].replace('nan', '').str.strip().tolist()
        bcc_emails = df[df['نوع'].str.upper() == 'BCC']['ایمیل'].replace('nan', '').str.strip().tolist()
    
        to_emails = [email for email in to_emails if email and email != 'nan']
        cc_emails = [email for email in cc_emails if email and email != 'nan']
        bcc_emails = [email for email in bcc_emails if email and email != 'nan']
    
        return to_emails, cc_emails, bcc_emails
    except Exception as e:
        logging.error(f"Error reading emails for province {province}: {e}")
        return [], [], []

@lru_cache(maxsize=1)
def get_logo_base64_cached(logo_path):
    """نسخه کش شده لوگو"""
    try:
        with open(logo_path, 'rb') as img_file:
            base64_data = base64.b64encode(img_file.read()).decode('utf-8')
        return base64_data
    except FileNotFoundError:
        logging.warning(f"Logo file '{logo_path}' not found")
        return ""

def clean_directory(directory):
    """Clean directory contents"""
    if directory.exists() and directory.is_dir():
        for item in directory.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

@error_handler
def create_province_reports(input_files):
    """Create province-specific Excel reports from the provided input files"""
    if not input_files:
        raise ValidationException("هیچ فایل ورودی انتخاب نشده است")
    
    output_dir = Path('Province Report')
    
    if output_dir.exists():
        clean_directory(output_dir)
    else:
        output_dir.mkdir()
    
    logging.info("Province Report folder has been cleaned.")
    
    provinces = set()
    for input_file in input_files:
        excel_file = Path(input_file)
        
        if not excel_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if excel_file.suffix.lower() != '.xlsx':
            logging.warning(f"Skipping non-Excel file: {input_file}")
            continue
        
        is_valid, error_msg = DataValidator.validate_file_size(excel_file)
        if not is_valid:
            raise FileProcessingException(f"فایل {excel_file.name}: {error_msg}")
        
        try:
            excel = pd.ExcelFile(excel_file)
            sheet_names = excel.sheet_names
            
            for sheet_name in sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                if 'استان' not in df.columns:
                    raise ValueError(f"Column 'استان' not found in sheet {sheet_name} of file {input_file}")
                
                for province in df['استان'].unique():
                    if pd.isna(province):
                        continue
                    
                    province_str = str(province).strip()
                    is_valid, error_msg = DataValidator.validate_province_data(province_str)
                    
                    if not is_valid:
                        logging.warning(f"Invalid province data: {province_str} - {error_msg}")
                        continue
                    
                    province_data = df[df['استان'] == province]
                    province_path = output_dir / f"{province_str}.xlsx"
                
                    if province_path.exists():
                        with pd.ExcelWriter(province_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
                            province_data.to_excel(writer, sheet_name=sheet_name, index=False)
                    else:
                        with pd.ExcelWriter(province_path, engine='openpyxl') as writer:
                            province_data.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    provinces.add(province_str)
                    
        except Exception as e:
            logging.error(f"Error processing {input_file}: {str(e)}")
            continue

    logging.info(f"Province-specific files have been created for {len(provinces)} provinces")
    return list(provinces)

def get_all_provinces_from_email_list():
    """Get list of all provinces from email_list.xlsx"""
    try:
        excel = pd.ExcelFile('email_list.xlsx')
        return excel.sheet_names
    except Exception as e:
        logging.error(f"Error reading email_list.xlsx: {e}")
        return []

def create_html_body(province_name, body_text_widget, signature_text_widget, direction, logo_base64, font_family, font_size):
    """
    ایجاد محتوای HTML با استخراج استایل‌ها از تگ‌های Tkinter
    """
    def process_text_widget_content(widget, is_body=True):
        content_with_placeholder = widget.get("1.0", "end-1c")
        content_formatted = content_with_placeholder.format(province_name=province_name)
        output = ""
        
        # Get all tags and their ranges
        tags = sorted(widget.tag_names(), key=lambda t: widget.tag_ranges(t) if widget.tag_ranges(t) else ('z', 'z'))
        
        # Handle formatting tags (bold, italic, color)
        processed_content = content_formatted
        for tag in tags:
            if tag.startswith("formatted_") or tag.startswith("color_"):
                ranges = widget.tag_ranges(tag)
                for start_index, end_index in zip(ranges[0::2], ranges[1::2]):
                    # Extract the selected text from the raw content
                    selected_text = widget.get(start_index, end_index)
                    # Find the position of the selected text in the formatted content
                    start_pos_in_formatted = processed_content.find(selected_text)
                    if start_pos_in_formatted != -1:
                        end_pos_in_formatted = start_pos_in_formatted + len(selected_text)

                        # Apply HTML tags based on Tkinter tags
                        html_tag_start = ''
                        html_tag_end = ''
                        style_attrs = ''

                        if 'formatted_bold' in tag:
                            html_tag_start = '<strong>'
                            html_tag_end = '</strong>'
                        elif 'formatted_italic' in tag:
                            html_tag_start = '<em>'
                            html_tag_end = '</em>'
                        elif tag.startswith('color_foreground'):
                            color = widget.tag_cget(tag, "foreground")
                            style_attrs += f'color:{color};'
                        elif tag.startswith('color_background'):
                            color = widget.tag_cget(tag, "background")
                            style_attrs += f'background-color:{color};'
                        
                        if style_attrs:
                            html_tag_start = f'<span style="{style_attrs}">' + html_tag_start
                            html_tag_end = html_tag_end + '</span>'

                        # Replace text with formatted HTML
                        processed_content = (processed_content[:start_pos_in_formatted] +
                                             html_tag_start + selected_text + html_tag_end +
                                             processed_content[end_pos_in_formatted:])
        
        # Split into lines and wrap in <p> tags
        lines = processed_content.split('\n')
        for line in lines:
            if not line.strip():
                output += '<p class="empty"></p>'
            else:
                output += f'<p>{line}</p>'
        
        return output

    body_html_content = process_text_widget_content(body_text_widget, is_body=True)
    signature_html_content = process_text_widget_content(signature_text_widget, is_body=False)

    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                direction: {direction};
                font-family: '{font_family}', 'Segoe UI', Arial, sans-serif;
                font-size: {font_size}pt;
                line-height: 1.8;
                color: #333;
                background-color: #f9f9f9;
            }}
            .main-content {{
                margin: 20px 0; padding: 15px;
                background-color: #ffffff;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .main-content p {{
                margin: 10px 0;
            }}
            .main-content p.empty {{
                margin: 10px 0; height: 1em;
            }}
            .signature {{
                margin-top: 30px; border-top: 1px solid #ddd;
                padding-top: 20px;
            }}
            .signature-text p {{
                margin: 5px 0;
            }}
            .logo {{
                margin-top: 10px; width: 80px;
                height: auto;
                display: block;
                {'margin-right: 0; margin-left: auto;' if direction == 'rtl' else 'margin-left: 0; margin-right: auto;'}
            }}
            strong {{
                font-weight: bold;
            }}
            em {{
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="main-content">{body_html_content}</div>
        <div class="signature">
            <div class="signature-text">{signature_html_content}</div>
            <div style="text-align: {'right' if direction == 'rtl' else 'left'};">
                {f'<img src="data:image/png;base64,{logo_base64}" alt="" class="logo">' if logo_base64 else ''}
            </div>
        </div>
    </body>
    </html>"""

@error_handler
def send_email_with_retry(province_name, attachment_paths, subject, body_text, signature_text, 
                         direction='rtl', sender_name=DEFAULT_SENDER_NAME, sender_email=DEFAULT_SENDER_EMAIL, 
                         username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD, logo_path=DEFAULT_LOGO, 
                         font_family="B Nazanin", font_size=12, server_host=DEFAULT_EMAIL_SERVER, server_port=DEFAULT_PORT):
    """ارسال ایمیل با قابلیت تلاش مجدد"""
    
    retry_manager = RetryManager(max_retries=3, delay=2.0)
    
    def send_operation():
        return send_email_optimized(
            province_name, attachment_paths, subject, body_text, signature_text,
            direction, sender_name, sender_email, username, password, logo_path,
            font_family, font_size,
            server_host, server_port
        )
    
    try:
        result = retry_manager.retry_operation(send_operation)
        return result
    except Exception as e:
        logging.error(f"Failed to send email to {province_name} after all retries: {e}")
        return False

def send_email_optimized(province_name, attachment_paths, subject, body_text_widget, signature_text_widget, 
                         direction='rtl', sender_name=DEFAULT_SENDER_NAME, sender_email=DEFAULT_SENDER_EMAIL, 
                         username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD, logo_path=DEFAULT_LOGO, 
                         font_family="B Nazanin", font_size=12, server_host=DEFAULT_EMAIL_SERVER, server_port=DEFAULT_PORT):
    """نسخه بهینه شده ارسال ایمیل"""
    
    try:
        logo_base64 = get_logo_base64_cached(logo_path)
        to_emails, cc_emails, bcc_emails = get_province_emails_cached(province_name)
    
        if not to_emails:
            logging.warning(f"No email addresses found for province {province_name}")
            return False

        current_date = jdatetime.datetime.now().strftime('%Y-%m-%d')
    
        with secure_smtp_connection(server_host, server_port, username, password) as server:
            msg = MIMEMultipart('mixed')
            msg['From'] = f'{sender_name}<{sender_email}>'
            msg['To'] = ', '.join(to_emails)
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            msg['Subject'] = subject.format(province_name=province_name, date=current_date)
            msg['Date'] = email.utils.formatdate(localtime=True)
            msg['Message-ID'] = email.utils.make_msgid(domain='nak-mci.ir')
            msg.add_header('X-Mailer', 'NAK Email System v2.0')
            
            html_body = create_html_body(province_name, body_text_widget, signature_text_widget, direction, logo_base64, font_family, font_size)
            
            alt_part = MIMEMultipart('alternative')
            
            plain_text = body_text_widget.get("1.0", tk.END).strip().format(province_name=province_name)
            part1 = MIMEText(plain_text + "\n\n" + signature_text_widget.get("1.0", tk.END).strip(), 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            
            alt_part.attach(part1)
            alt_part.attach(part2)
            msg.attach(alt_part)
            
            if logo_base64 and Path(logo_path).exists():
                with open(logo_path, 'rb') as f:
                    logo_attachment = MIMEImage(f.read())
                logo_attachment.add_header('Content-ID', '<company_logo>')
                logo_attachment.add_header('Content-Disposition', 'inline')
                msg.attach(logo_attachment)
            
            if attachment_paths:
                for attachment_path in attachment_paths:
                    file_path = Path(attachment_path)
                    if not file_path.exists():
                        logging.warning(f"Attachment file not found: {attachment_path}")
                        continue
                        
                    is_valid, error_msg = DataValidator.validate_file_size(file_path)
                    if not is_valid:
                        logging.warning(f"Attachment file validation failed: {error_msg}")
                        continue
                    
                    try:
                        with open(attachment_path, 'rb') as f:
                            ctype, encoding = mimetypes.guess_type(attachment_path)
                            if ctype is None or encoding is not None:
                                ctype = 'application/octet-stream'
                            maintype, subtype = ctype.split('/', 1)
                        
                            part = MIMEApplication(f.read(), _subtype=subtype)
                            part.add_header('Content-Disposition', 'attachment', 
                                            filename=('utf-8', '', file_path.name))
                            msg.attach(part)
                    except Exception as e:
                        logging.error(f"Error attaching file {attachment_path}: {e}")
                        continue
            
            all_recipients = to_emails + cc_emails + bcc_emails + [sender_email]
            server.send_message(msg, 
                                from_addr=sender_email, 
                                to_addrs=all_recipients)
        
        logging.info(f"Email sent successfully for province {province_name}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending email for province {province_name}: {e}")
        return False

class ProgressDialog:
    """پنجره نمایش پیشرفت ارسال ایمیل"""
    
    def __init__(self, parent, total_emails):
        self.parent = parent
        self.total_emails = total_emails
        self.current = 0
        self.cancelled = False
    
        self.window = tb.Toplevel(parent)
        self.window.title("ارسال ایمیل‌ها")
        self.window.geometry("500x250")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
    
        self.center_window()
        self.setup_ui()
    
        self.window.protocol("WM_DELETE_WINDOW", self.cancel)

    def center_window(self):
        """مرکز کردن پنجره روی صفحه"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - self.window.winfo_width()) // 2
        y = (self.window.winfo_screenheight() - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        main_frame = tb.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        self.status_label = tb.Label(main_frame, text="شروع ارسال ایمیل‌ها...", 
                                     font=("Segoe UI", 12))
        self.status_label.pack(pady=10)
    
        self.progress = tb.Progressbar(main_frame, length=400, mode='determinate')
        self.progress['maximum'] = self.total_emails
        self.progress.pack(pady=10)
    
        self.percent_label = tb.Label(main_frame, text="0%", font=("Segoe UI", 10))
        self.percent_label.pack(pady=5)
    
        self.stats_label = tb.Label(main_frame, text="موفق: 0 | ناموفق: 0", 
                                     font=("Segoe UI", 10))
        self.stats_label.pack(pady=5)
    
        self.current_province_label = tb.Label(main_frame, text="", 
                                               font=("Segoe UI", 10), bootstyle="primary")
        self.current_province_label.pack(pady=5)
    
        self.cancel_button = tb.Button(main_frame, text="لغو", command=self.cancel, bootstyle="danger")
        self.cancel_button.pack(pady=10)

    def update_progress(self, province, success, stats):
        """به‌روزرسانی پیشرفت"""
        self.current += 1
        self.progress['value'] = self.current
    
        percent = (self.current / self.total_emails) * 100
        self.percent_label.config(text=f"{percent:.1f}%")
    
        status = "موفق" if success else "ناموفق"
        self.status_label.config(text=f"ارسال برای {province}: {status}")
        self.current_province_label.config(text=f"در حال پردازش: {province}")
    
        self.stats_label.config(text=f"موفق: {stats['sent']} | ناموفق: {stats['failed']}")
    
        self.window.update()
    
        if self.current >= self.total_emails:
            self.finish()

    def cancel(self):
        """لغو عملیات"""
        self.cancelled = True
        self.window.destroy()
    
    def finish(self):
        """پایان عملیات"""
        self.cancel_button.config(text="بستن", bootstyle="secondary")
        self.status_label.config(text="ارسال ایمیل‌ها تکمیل شد!")
        self.current_province_label.config(text="")

class EmailAppImproved:
    """نسخه بهبود یافته اپلیکیشن ایمیل"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ارسال ایمیل استانی - نقش اول کیفیت v2.0")
        self.root.geometry("1200x900")
        
        self.default_subject = "مغایرت طراحی - {province_name} - {date}"
        self.default_body = """همکاران محترم استان {province_name}

مغایرت های طراحی جهت بررسی و رفع در ارس به پیوست ارسال شد. در صورت وجود استثنا به همین ایمیل ارسال فرمایید."""
        self.default_signature = DEFAULT_SIGNATURE
        self.settings_file = "email_settings.json"
        self.logo_path = DEFAULT_LOGO
        self.attachment_paths = []
        self.single_attachment_path = None
        self.server_host = DEFAULT_EMAIL_SERVER
        self.server_port = DEFAULT_PORT
        self.failed_provinces = []

        self.batch_size = 5
        self.wait_time = 300
    
        self.secure_settings = SecureSettings()
        self.email_queue = EmailQueue(max_workers=2)
    
        self.load_settings()

        self.title_font = font.Font(family="B Nazanin", size=12, weight="bold")
        self.label_font = font.Font(family="B Nazanin", size=11)
        self.text_font = font.Font(family="B Nazanin", size=12)

        self.create_menu()
    
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = tb.Scrollbar(self.root, orient="vertical", command=self.canvas.yview, bootstyle="round")
        self.scrollable_frame = tb.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=0)
        self.scrollable_frame.columnconfigure(2, weight=3)
        self.scrollable_frame.columnconfigure(3, weight=0)
        self.scrollable_frame.columnconfigure(4, weight=0)
        self.scrollable_frame.columnconfigure(5, weight=0)
        for i in range(12):
            self.scrollable_frame.rowconfigure(i, weight=1)

        style = tb.Style()
        style.configure("TLabel", font=self.label_font)
        style.configure("TEntry", font=self.text_font)
        style.configure("TFrame", background=style.colors.bg)
        style.configure("TCheckbutton", font=self.label_font)
        style.configure("TRadiobutton", font=self.label_font)

        self.create_ui()
        self.create_status_bar()
        self.create_shortcuts()
    
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def create_context_menu(self, widget):
        """ایجاد منوی کلیک راست برای copy/paste"""
        context_menu = tb.Menu(self.root, tearoff=0)
        
        context_menu.add_command(label="برش (Cut)", 
                                 command=lambda: self.cut_text(widget))
        context_menu.add_command(label="کپی (Copy)", 
                                 command=lambda: self.copy_text(widget))
        context_menu.add_command(label="چسباندن (Paste)", 
                                 command=lambda: self.paste_text(widget))
        context_menu.add_separator()
        context_menu.add_command(label="انتخاب همه (Select All)", 
                                 command=lambda: self.select_all_text(widget))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        widget.bind("<Button-3>", show_context_menu)
        return context_menu

    def setup_text_shortcuts(self, widget):
        """تنظیم میانبرهای صفحه کلید برای متن"""
        widget.bind("<Control-x>", lambda e: self.cut_text(widget))
        widget.bind("<Control-c>", lambda e: self.copy_text(widget))
        widget.bind("<Control-v>", lambda e: self.paste_text(widget))
        widget.bind("<Control-a>", lambda e: self.select_all_text(widget))
        widget.bind("<Control-z>", lambda e: self.undo_text(widget))
        widget.bind("<Control-y>", lambda e: self.redo_text(widget))

    def cut_text(self, widget):
        """برش متن"""
        try:
            if widget.tag_ranges("sel"):
                widget.event_generate("<<Cut>>")
        except Exception as e:
            logging.error(f"Error in cut_text: {e}")

    def copy_text(self, widget):
        """کپی متن"""
        try:
            if widget.tag_ranges("sel"):
                widget.event_generate("<<Copy>>")
        except Exception as e:
            logging.error(f"Error in copy_text: {e}")

    def paste_text(self, widget):
        """چسباندن متن"""
        try:
            widget.event_generate("<<Paste>>")
        except Exception as e:
            logging.error(f"Error in paste_text: {e}")

    def select_all_text(self, widget):
        """انتخاب همه متن"""
        try:
            widget.tag_add("sel", "1.0", "end")
            widget.mark_set("insert", "1.0")
            widget.see("insert")
            return 'break'
        except Exception as e:
            logging.error(f"Error in select_all_text: {e}")

    def undo_text(self, widget):
        """بازگردانی"""
        try:
            if hasattr(widget, 'edit_undo'):
                widget.edit_undo()
            return 'break'
        except Exception as e:
            logging.error(f"Error in undo_text: {e}")

    def redo_text(self, widget):
        """انجام مجدد"""
        try:
            if hasattr(widget, 'edit_redo'):
                widget.edit_redo()
            return 'break'
        except Exception as e:
            logging.error(f"Error in redo_text: {e}")

    def create_menu(self):
        """ایجاد منوی اصلی"""
        menubar = tb.Menu(self.root)
        self.root.config(menu=menubar)
    
        file_menu = tb.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="فایل", menu=file_menu)
        file_menu.add_command(label="تنظیمات جدید", command=self.new_settings)
        file_menu.add_command(label="بارگذاری تنظیمات", command=self.load_settings_file)
        file_menu.add_command(label="ذخیره تنظیمات", command=self.save_settings)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.root.quit)
    
        tools_menu = tb.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ابزارها", menu=tools_menu)
        tools_menu.add_command(label="تست اتصال ایمیل", command=self.test_email_connection)
        tools_menu.add_command(label="پاکسازی کش", command=self.clear_cache)
        tools_menu.add_command(label="نمایش لاگ", command=self.show_logs)
        tools_menu.add_command(label="ارسال دسته‌ای", command=self.send_batch_emails)
    
        help_menu = tb.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="راهنما", menu=help_menu)
        help_menu.add_command(label="راهنمای استفاده", command=self.show_help)
        help_menu.add_command(label="درباره", command=self.show_about)

    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        status_frame = tb.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
        self.status_var = tk.StringVar()
        self.status_var.set("آماده")
    
        status_label = tb.Label(status_frame, textvariable=self.status_var, 
                                 relief=tk.SUNKEN, anchor=tk.W, bootstyle="inverse-light")
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
        self.time_var = tk.StringVar()
        time_label = tb.Label(status_frame, textvariable=self.time_var, 
                               relief=tk.SUNKEN, width=20, bootstyle="inverse-light")
        time_label.pack(side=tk.RIGHT)
    
        self.update_time()

    def create_shortcuts(self):
        """ایجاد میانبرهای صفحه کلید"""
        self.root.bind("<Control-s>", lambda e: self.save_settings())
        self.root.bind("<Control-o>", lambda e: self.select_attachment_files())
        self.root.bind("<Control-p>", lambda e: self.preview_email())
        self.root.bind("<F5>", lambda e: self.populate_provinces())
        self.root.bind("<Control-Return>", lambda e: self.send_emails())

    def create_ui(self):
        """ایجاد رابط کاربری"""
        email_settings_frame = tb.LabelFrame(self.scrollable_frame, text="تنظیمات ایمیل", padding=10, bootstyle="primary")
        email_settings_frame.grid(row=0, column=1, columnspan=5, sticky=(tk.W, tk.E), pady=5, padx=5)

        tb.Label(email_settings_frame, text="نام فرستنده:", bootstyle="primary").grid(row=0, column=0, sticky=tk.E, pady=2)
        self.sender_name_entry = tb.Entry(email_settings_frame, width=30)
        self.sender_name_entry.insert(0, self.sender_name)
        self.sender_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

        tb.Label(email_settings_frame, text="ایمیل فرستنده:", bootstyle="primary").grid(row=1, column=0, sticky=tk.E, pady=2)
        self.sender_email_entry = tb.Entry(email_settings_frame, width=30)
        self.sender_email_entry.insert(0, self.sender_email)
        self.sender_email_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)

        tb.Label(email_settings_frame, text="نام کاربری:", bootstyle="primary").grid(row=2, column=0, sticky=tk.E, pady=2)
        self.username_entry = tb.Entry(email_settings_frame, width=30)
        self.username_entry.insert(0, self.username)
        self.username_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)

        tb.Label(email_settings_frame, text="رمز عبور:", bootstyle="primary").grid(row=3, column=0, sticky=tk.E, pady=2)
        self.password_entry = tb.Entry(email_settings_frame, width=30, show="*")
        self.password_entry.insert(0, self.password)
        self.password_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)

        smtp_settings_frame = tb.LabelFrame(email_settings_frame, text="تنظیمات SMTP", padding=10, bootstyle="primary")
        smtp_settings_frame.grid(row=0, column=2, rowspan=4, padx=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        tb.Label(smtp_settings_frame, text="Host:", bootstyle="primary").grid(row=0, column=0, sticky=tk.E, pady=2)
        self.server_host_entry = tb.Entry(smtp_settings_frame, width=25)
        self.server_host_entry.insert(0, self.server_host)
        self.server_host_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        tb.Label(smtp_settings_frame, text="Port:", bootstyle="primary").grid(row=1, column=0, sticky=tk.E, pady=2)
        self.server_port_entry = tb.Entry(smtp_settings_frame, width=25)
        self.server_port_entry.insert(0, str(self.server_port))
        self.server_port_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)

        batch_settings_frame = tb.LabelFrame(self.scrollable_frame, text="تنظیمات ارسال دسته‌ای", padding=10, bootstyle="primary")
        batch_settings_frame.grid(row=1, column=1, columnspan=5, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        tb.Label(batch_settings_frame, text="تعداد ایمیل در هر دسته:", bootstyle="primary").grid(row=0, column=0, sticky=tk.E, pady=2)
        self.batch_size_var = tk.StringVar(value=str(self.batch_size))
        batch_size_spinbox = tb.Spinbox(batch_settings_frame, from_=1, to=20, width=5, textvariable=self.batch_size_var,
                                         command=self.update_batch_settings, bootstyle="info")
        batch_size_spinbox.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        tb.Label(batch_settings_frame, text="زمان انتظار بین دسته‌ها (ثانیه):", bootstyle="primary").grid(row=0, column=2, sticky=tk.E, pady=2, padx=(20, 0))
        self.wait_time_var = tk.StringVar(value=str(self.wait_time))
        wait_time_spinbox = tb.Spinbox(batch_settings_frame, from_=30, to=3600, width=8, textvariable=self.wait_time_var,
                                       command=self.update_batch_settings, bootstyle="info")
        wait_time_spinbox.grid(row=0, column=3, sticky=tk.W, pady=2)
        
        info_label = tb.Label(batch_settings_frame, text="(توصیه: 5 ایمیل در دسته، 300 ثانیه انتظار)", 
                                 font=("Segoe UI", 9), bootstyle="secondary")
        info_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=2)

        attachment_frame = tb.LabelFrame(self.scrollable_frame, text="پیوست‌ها", padding=10, bootstyle="primary")
        attachment_frame.grid(row=2, column=1, columnspan=5, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        tb.Button(attachment_frame, text="انتخاب فایل‌ها", command=self.select_attachment_files, bootstyle="success").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.attachment_label = tb.Label(attachment_frame, text="هیچ فایلی انتخاب نشده", wraplength=400, bootstyle="secondary")
        self.attachment_label.grid(row=0, column=1, columnspan=4, sticky=(tk.W, tk.E), padx=5)
        
        self.attach_mode_var = tk.StringVar(value="with_attachment")
        attach_mode_frame = tb.Frame(attachment_frame)
        attach_mode_frame.grid(row=1, column=0, columnspan=5, sticky=tk.W, pady=2)
        
        tb.Radiobutton(attach_mode_frame, text="ارسال با پیوست استانی", variable=self.attach_mode_var, value="with_attachment",
                        command=self.populate_provinces, bootstyle="info").pack(side=tk.LEFT, padx=5)
        tb.Radiobutton(attach_mode_frame, text="ارسال با فایل یکسان", variable=self.attach_mode_var, value="with_single_file",
                        command=self.populate_provinces, bootstyle="info").pack(side=tk.LEFT, padx=5)
        tb.Radiobutton(attach_mode_frame, text="ارسال بدون پیوست", variable=self.attach_mode_var, value="without_attachment",
                        command=self.populate_provinces, bootstyle="info").pack(side=tk.LEFT, padx=5)

        province_frame = tb.LabelFrame(self.scrollable_frame, text="استان‌ها", padding=10, bootstyle="primary")
        province_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
    
        self.select_all_var = tk.BooleanVar()
        tb.Checkbutton(province_frame, text="همه را انتخاب کن", variable=self.select_all_var,
                        command=self.toggle_select_all, bootstyle="primary-round-toggle").grid(row=0, column=0, sticky=tk.W, pady=2)
    
        province_scroll_frame = tb.Frame(province_frame)
        province_scroll_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
        self.province_listbox = tk.Listbox(province_scroll_frame, selectmode=tk.MULTIPLE, height=15, font=self.text_font)
        self.province_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        province_scrollbar = tb.Scrollbar(province_scroll_frame, orient=tk.VERTICAL, command=self.province_listbox.yview, bootstyle="round")
        province_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.province_listbox.config(yscrollcommand=province_scrollbar.set)
    
        self.populate_provinces()

        tb.Label(self.scrollable_frame, text="موضوع:", bootstyle="primary").grid(row=3, column=1, sticky=tk.E, pady=5)
        self.subject_entry = tb.Entry(self.scrollable_frame, width=70)
        self.subject_entry.insert(0, self.default_subject)
        self.subject_entry.grid(row=3, column=2, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        tb.Label(self.scrollable_frame, text="جهت متن:", bootstyle="primary").grid(row=4, column=1, sticky=tk.E, pady=5)
        self.direction_var = tk.StringVar(value="rtl")
        direction_frame = tb.Frame(self.scrollable_frame)
        direction_frame.grid(row=4, column=2, sticky=tk.W, pady=5)
        tb.Radiobutton(direction_frame, text="راست به چپ", variable=self.direction_var, value="rtl", bootstyle="info").pack(side=tk.LEFT, padx=5)
        tb.Radiobutton(direction_frame, text="چپ به راست", variable=self.direction_var, value="ltr", bootstyle="info").pack(side=tk.LEFT, padx=5)

        tb.Label(self.scrollable_frame, text="متن:", bootstyle="primary").grid(row=5, column=1, sticky=tk.E, pady=5)
        self.body_text = scrolledtext.ScrolledText(self.scrollable_frame, width=70, height=10, 
                                                   font=self.text_font, wrap=tk.WORD, undo=True)
        self.body_text.insert(tk.END, self.default_body)
        self.body_text.grid(row=5, column=2, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
    
        self.create_context_menu(self.body_text)
        self.setup_text_shortcuts(self.body_text)

        font_families = ["B Nazanin", "Segoe UI", "Calibri", "Arial"]
        font_sizes = list(range(8, 21))
    
        font_frame = tb.Frame(self.scrollable_frame)
        font_frame.grid(row=6, column=2, columnspan=4, sticky=tk.W, pady=2)
    
        tb.Label(font_frame, text="فونت:", bootstyle="primary").pack(side=tk.LEFT, padx=(0, 5))
        self.body_font_var = tk.StringVar(value=self.text_font.actual()['family'])
        font_menu = tb.OptionMenu(font_frame, self.body_font_var, self.body_font_var.get(), *font_families, 
                                     command=lambda x: self.update_font(self.body_text, self.body_font_var.get(), self.body_size_var.get()), bootstyle="info")
        font_menu.pack(side=tk.LEFT, padx=5)
    
        tb.Label(font_frame, text="اندازه:", bootstyle="primary").pack(side=tk.LEFT, padx=(10, 5))
        self.body_size_var = tk.StringVar(value=str(self.text_font.cget("size")))
        size_menu = tb.OptionMenu(font_frame, self.body_size_var, self.body_size_var.get(), *font_sizes, 
                                     command=lambda x: self.update_font(self.body_text, self.body_font_var.get(), self.body_size_var.get()), bootstyle="info")
        size_menu.pack(side=tk.LEFT, padx=5)
        
        format_frame = tb.Frame(font_frame)
        format_frame.pack(side=tk.LEFT, padx=(20, 0))

        tb.Button(format_frame, text="B", width=3, command=lambda: self.apply_formatting_tag(self.body_text, "bold")).pack(side=tk.LEFT, padx=2)
        tb.Button(format_frame, text="I", width=3, command=lambda: self.apply_formatting_tag(self.body_text, "italic")).pack(side=tk.LEFT, padx=2)
        tb.Button(format_frame, text="رنگ فونت", command=lambda: self.choose_color_for_tag(self.body_text, "foreground")).pack(side=tk.LEFT, padx=5)
        tb.Button(format_frame, text="هایلایت", command=lambda: self.choose_color_for_tag(self.body_text, "background")).pack(side=tk.LEFT, padx=5)

        tb.Label(self.scrollable_frame, text="امضا:", bootstyle="primary").grid(row=7, column=1, sticky=tk.E, pady=5)
        self.signature_text = scrolledtext.ScrolledText(self.scrollable_frame, width=70, height=5, 
                                                       font=self.text_font, wrap=tk.WORD, undo=True)
        self.signature_text.insert(tk.END, self.default_signature)
        self.signature_text.grid(row=7, column=2, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
    
        self.create_context_menu(self.signature_text)
        self.setup_text_shortcuts(self.signature_text)

        sig_font_frame = tb.Frame(self.scrollable_frame)
        sig_font_frame.grid(row=8, column=2, columnspan=4, sticky=tk.W, pady=2)
    
        tb.Label(sig_font_frame, text="فونت:", bootstyle="primary").pack(side=tk.LEFT, padx=(0, 5))
        self.signature_font_var = tk.StringVar(value=self.text_font.actual()['family'])
        font_menu_sig = tb.OptionMenu(sig_font_frame, self.signature_font_var, self.signature_font_var.get(), *font_families, 
                                         command=lambda x: self.update_font(self.signature_text, self.signature_font_var.get(), self.signature_size_var.get()), bootstyle="info")
        font_menu_sig.pack(side=tk.LEFT, padx=5)
    
        tb.Label(sig_font_frame, text="اندازه:", bootstyle="primary").pack(side=tk.LEFT, padx=(10, 5))
        self.signature_size_var = tk.StringVar(value=str(self.text_font.cget("size")))
        size_menu_sig = tb.OptionMenu(sig_font_frame, self.signature_size_var, self.signature_size_var.get(), *font_sizes, 
                                         command=lambda x: self.update_font(self.signature_text, self.signature_font_var.get(), self.signature_size_var.get()), bootstyle="info")
        size_menu_sig.pack(side=tk.LEFT, padx=5)

        sig_format_frame = tb.Frame(sig_font_frame)
        sig_format_frame.pack(side=tk.LEFT, padx=(20, 0))
        tb.Button(sig_format_frame, text="B", width=3, command=lambda: self.apply_formatting_tag(self.signature_text, "bold")).pack(side=tk.LEFT, padx=2)
        tb.Button(sig_format_frame, text="I", width=3, command=lambda: self.apply_formatting_tag(self.signature_text, "italic")).pack(side=tk.LEFT, padx=2)

        tb.Label(self.scrollable_frame, text="گیرندگان:", bootstyle="primary").grid(row=9, column=1, sticky=tk.E, pady=5)
        self.recipients_text = scrolledtext.ScrolledText(self.scrollable_frame, width=70, height=6, font=("Segoe UI", 10))
        self.recipients_text.grid(row=9, column=2, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        self.recipients_text.config(state='disabled')

        button_frame = tb.Frame(self.scrollable_frame)
        button_frame.grid(row=10, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=10)
    
        buttons = [
            ("ایجاد گزارش‌ها", self.create_reports, "success"),
            ("پاکسازی گزارش‌ها", self.clear_reports, "danger"),
            ("نمایش گیرندگان", self.show_recipients, "info"),
            ("پیش‌نمایش", self.preview_email, "secondary"),
            ("بازگرداندن پیش‌فرض", self.reset_defaults, "warning"),
            ("ذخیره تنظیمات", self.save_settings, "primary"),
            ("ارسال ایمیل‌ها", self.send_emails, "success"),
            ("ارسال دسته‌ای", self.send_batch_emails, "primary")
        ]
    
        for i, (text, command, style) in enumerate(buttons):
            btn = tb.Button(button_frame, text=text, command=command, bootstyle=style)
            btn.grid(row=0, column=i, padx=5, pady=5)

    def apply_formatting_tag(self, widget, style_type):
        try:
            sel_range = widget.tag_ranges("sel")
            if not sel_range:
                messagebox.showwarning("هشدار", "لطفاً ابتدا متنی را برای اعمال قالب‌بندی انتخاب کنید.")
                return

            selection_start = sel_range[0]
            selection_end = sel_range[1]

            tag_to_apply = f"formatted_{style_type}"

            if tag_to_apply in widget.tag_names(selection_start):
                widget.tag_remove(tag_to_apply, selection_start, selection_end)
            else:
                widget.tag_add(tag_to_apply, selection_start, selection_end)

            if style_type == "bold":
                widget.tag_config(tag_to_apply, font=font.Font(family=self.text_font.cget("family"), size=self.text_font.cget("size"), weight="bold"))
            elif style_type == "italic":
                widget.tag_config(tag_to_apply, font=font.Font(family=self.text_font.cget("family"), size=self.text_font.cget("size"), slant="italic"))

        except Exception as e:
            logging.error(f"Error applying formatting tag: {e}")

    def choose_color_for_tag(self, widget, color_type):
        try:
            color_code = colorchooser.askcolor(title=f"انتخاب رنگ {color_type}")[1]
            if not color_code:
                return

            sel_range = widget.tag_ranges("sel")
            if not sel_range:
                messagebox.showwarning("هشدار", "لطفاً ابتدا متنی را برای اعمال رنگ انتخاب کنید.")
                return
                
            selection_start = sel_range[0]
            selection_end = sel_range[1]
            
            tag_name = f"color_{color_type}_{int(time.time())}"
            widget.tag_add(tag_name, selection_start, selection_end)
            
            if color_type == "foreground":
                widget.tag_config(tag_name, foreground=color_code)
            else:
                widget.tag_config(tag_name, background=color_code)

        except Exception as e:
            logging.error(f"Error choosing color for tag: {e}")

    def update_batch_settings(self):
        """به‌روزرسانی تنظیمات دسته‌ای"""
        try:
            self.batch_size = int(self.batch_size_var.get())
            self.wait_time = int(self.wait_time_var.get())
            logging.info(f"Batch settings updated: size={self.batch_size}, wait_time={self.wait_time}")
        except ValueError:
            logging.warning("Invalid batch settings values")
    
    def populate_provinces(self):
        """Populate province listbox based on attach_file_var and available reports"""
        self.province_listbox.delete(0, tk.END)
        provinces = get_all_provinces_from_email_list()
    
        if not provinces:
            messagebox.showwarning("هشدار", "فایل email_list.xlsx یافت نشد یا خالی است!")
            return
    
        attach_mode = self.attach_mode_var.get()
        if attach_mode == 'with_attachment':
            output_dir = Path('Province Report')
            if output_dir.exists():
                available_provinces = [f.stem for f in output_dir.glob('*.xlsx') if f.is_file()]
                provinces = [p for p in provinces if p in available_provinces]
        elif attach_mode == 'without_attachment' or attach_mode == 'with_single_file':
            pass
    
        for province in provinces:
            self.province_listbox.insert(tk.END, province)

    def send_batch_emails(self):
        """ارسال ایمیل‌ها در دسته‌های قابل تنظیم با فاصله زمانی"""
        selected_provinces = [self.province_listbox.get(i) for i in self.province_listbox.curselection()]
        if not selected_provinces:
            messagebox.showwarning("هشدار", "لطفاً حداقل یک استان انتخاب کنید!")
            return

        self.update_batch_settings()
    
        result = messagebox.askyesno("تأیید ارسال دسته‌ای", 
                                     f"آیا می‌خواهید ایمیل‌ها را در دسته‌های {self.batch_size} تایی " +
                                     f"با فاصله {self.wait_time} ثانیه‌ای ({self.wait_time//60} دقیقه) ارسال کنید؟\n" +
                                     "این عملیات ممکن است چندین ساعت طول بکشد.\n\n" +
                                     "نکته: پنجره پیشرفت نمایش داده خواهد شد.")
    
        if not result:
            return
    
        batch_window = tb.Toplevel(self.root)
        batch_window.title("ارسال دسته‌ای ایمیل‌ها")
        batch_window.geometry("700x500")
        batch_window.resizable(False, False)
        batch_window.transient(self.root)
        batch_window.grab_set()
    
        batch_window.update_idletasks()
        x = (batch_window.winfo_screenwidth() - batch_window.winfo_width()) // 2
        y = (batch_window.winfo_screenheight() - batch_window.winfo_height()) // 2
        batch_window.geometry(f"+{x}+{y}")
    
        main_frame = tb.Frame(batch_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        settings_label = tb.Label(main_frame, 
                                     text=f"تنظیمات: {self.batch_size} ایمیل در هر دسته، {self.wait_time} ثانیه انتظار", 
                                     font=("Segoe UI", 10, "bold"))
        settings_label.pack(pady=5)
    
        status_label = tb.Label(main_frame, text="آماده‌سازی ارسال دسته‌ای...", 
                                 font=("Segoe UI", 12), wraplength=650)
        status_label.pack(pady=10)
    
        log_frame = tb.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
        log_text = tk.Text(log_frame, wrap=tk.WORD, font=("Consolas", 9), height=18)
        log_scrollbar = tb.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_text.yview)
        log_text.configure(yscrollcommand=log_scrollbar.set)
    
        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        stats_label = tb.Label(main_frame, text="موفق: 0 | ناموفق: 0", 
                                 font=("Segoe UI", 11))
        stats_label.pack(pady=5)
    
        cancelled = [False]
    
        def cancel_operation():
            cancelled[0] = True
            batch_window.destroy()
    
        cancel_button = tb.Button(main_frame, text="لغو", command=cancel_operation)
        cancel_button.pack(pady=10)
    
        self.failed_provinces = []
        
        def update_progress(message, is_success):
            if cancelled[0]:
                return
                
            status_label.config(text=message)
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_entry = f"[{timestamp}] {message}\n"
            log_text.insert(tk.END, log_entry)
            log_text.see(tk.END)
            
            stats = self.email_queue.stats
            stats_label.config(text=f"موفق: {stats['sent']} | ناموفق: {stats['failed']}")
            
            batch_window.update()
            
            if "تکمیل شد" in message:
                cancel_button.config(text="بستن")
    
        def batch_worker():
            try:
                if not cancelled[0]:
                    self.send_emails_in_batches(selected_provinces, progress_callback=update_progress, cancelled_flag=cancelled)
            except Exception as e:
                error_msg = f"خطای کلی در ارسال دسته‌ای: {str(e)}"
                logging.error(error_msg)
                if not cancelled[0]:
                    update_progress(error_msg, False)
    
        thread = Thread(target=batch_worker, daemon=True)
        thread.start()

    def send_emails_in_batches(self, selected_provinces, progress_callback=None, cancelled_flag=None):
        """Send emails in batches with configurable intervals"""
        output_dir = Path('Province Report')
    
        attach_mode = self.attach_mode_var.get()
        if attach_mode == 'with_attachment' and not output_dir.exists():
            error_msg = "پوشه Province Report یافت نشد!"
            logging.error(error_msg)
            if progress_callback:
                progress_callback(error_msg, False)
            return False
    
        provinces_to_send = []
        if attach_mode == 'with_attachment':
            for p in selected_provinces:
                file_path = output_dir / f'{p}.xlsx'
                if file_path.exists() and file_path.stat().st_size > 0:
                    provinces_to_send.append(p)
                else:
                    logging.warning(f"Skipping {p}: No valid report file found.")
                    if progress_callback:
                        progress_callback(f"استان {p}: فایل گزارش معتبر یافت نشد.", False)
        elif attach_mode == 'with_single_file':
            if not self.single_attachment_path or not Path(self.single_attachment_path).exists():
                error_msg = "فایل یکسان برای پیوست انتخاب نشده یا وجود ندارد!"
                logging.error(error_msg)
                if progress_callback:
                    progress_callback(error_msg, False)
                return False
            provinces_to_send = selected_provinces
        else:
            provinces_to_send = selected_provinces

        if not provinces_to_send:
            error_msg = "هیچ فایل یا استانی برای ارسال یافت نشد!"
            logging.warning(error_msg)
            if progress_callback:
                progress_callback(error_msg, False)
            return False
            
        total_provinces = len(provinces_to_send)
        num_batches = math.ceil(total_provinces / self.batch_size)
    
        log_msg = f"Found {total_provinces} provinces with data to send in {num_batches} batches (batch size: {self.batch_size}, wait time: {self.wait_time}s)"
        logging.info(log_msg)
        if progress_callback:
            progress_callback(log_msg, True)
    
        try:
            sender_name, sender_email, username, password, server_host, server_port = self.validate_email_settings()
            subject = self.subject_entry.get()
            body_text = self.body_text
            signature_text = self.signature_text
            direction = self.direction_var.get()
            logo_path = self.logo_path
            font_family = self.body_font_var.get()
            font_size = int(self.body_size_var.get())
        
        except Exception as e:
            error_msg = f"خطا در دریافت تنظیمات: {str(e)}"
            logging.error(error_msg)
            if progress_callback:
                progress_callback(error_msg, False)
            return False

        self.email_queue.stats = {'sent': 0, 'failed': 0, 'total': len(provinces_to_send), 'failed_provinces': []}
        
        for batch_num in range(num_batches):
            if cancelled_flag and cancelled_flag[0]:
                logging.info("Batch sending cancelled by user")
                return False
                
            batch_msg = f"شروع دسته {batch_num + 1} از {num_batches}"
            logging.info(batch_msg)
            if progress_callback:
                progress_callback(batch_msg, True)
            
            start_idx = batch_num * self.batch_size
            end_idx = min((batch_num + 1) * self.batch_size, total_provinces)
            
            for i, province in enumerate(provinces_to_send[start_idx:end_idx]):
                if cancelled_flag and cancelled_flag[0]:
                    logging.info("Batch sending cancelled by user")
                    return False
                
                attachment_paths = []
                if attach_mode == 'with_attachment':
                    attachment_paths = self.get_attachment_paths_for_province(province)
                elif attach_mode == 'with_single_file':
                    attachment_paths = [self.single_attachment_path] if self.single_attachment_path else []

                current_time = datetime.now().strftime('%H:%M:%S')
            
                progress_msg = f"{current_time} - ارسال ایمیل برای استان {province} ({start_idx + i + 1}/{total_provinces})"
                logging.info(progress_msg)
                if progress_callback:
                    progress_callback(progress_msg, True)
            
                try:
                    result = send_email_optimized(
                        province_name=province,
                        attachment_paths=attachment_paths,
                        subject=subject,
                        body_text_widget=body_text,
                        signature_text_widget=signature_text,
                        direction=direction,
                        sender_name=sender_name,
                        sender_email=sender_email,
                        username=username,
                        password=password,
                        logo_path=logo_path,
                        font_family=font_family,
                        font_size=font_size,
                        server_host=server_host,
                        server_port=server_port
                    )
                    
                    if result:
                        self.email_queue.stats['sent'] += 1
                        success_msg = f"موفق: ارسال ایمیل برای {province}"
                        logging.info(success_msg)
                    else:
                        self.email_queue.stats['failed'] += 1
                        self.email_queue.stats['failed_provinces'].append(province)
                        fail_msg = f"ناموفق: ارسال ایمیل برای {province}"
                        logging.warning(fail_msg)
                        
                    if progress_callback:
                        progress_callback(f"استان {province}: {'موفق' if result else 'ناموفق'}", result)
                        
                    time.sleep(2)
                        
                except Exception as e:
                    error_msg = f"خطا در ارسال ایمیل برای {province}: {str(e)}"
                    logging.error(error_msg)
                    self.email_queue.stats['failed'] += 1
                    self.email_queue.stats['failed_provinces'].append(province)
                    if progress_callback:
                        progress_callback(error_msg, False)
            
            if batch_num < num_batches - 1:
                wait_msg = f"صبر {self.wait_time} ثانیه قبل از دسته بعدی... (تکمیل شده: {end_idx}/{total_provinces})"
                logging.info(wait_msg)
                if progress_callback:
                    progress_callback(wait_msg, True)
                
                remaining_time = self.wait_time
                while remaining_time > 0:
                    if cancelled_flag and cancelled_flag[0]:
                        logging.info("Batch sending cancelled during wait time")
                        return False
                        
                    minutes = remaining_time // 60
                    seconds = remaining_time % 60
                    countdown_msg = f"باقیمانده تا دسته بعدی: {minutes}:{seconds:02d}"
                    
                    if progress_callback:
                        progress_callback(countdown_msg, True)
                    
                    sleep_interval = min(10, remaining_time)
                    time.sleep(sleep_interval)
                    remaining_time -= sleep_interval
            
        final_msg = f"ارسال دسته‌ای تکمیل شد! موفق: {self.email_queue.stats['sent']}, ناموفق: {self.email_queue.stats['failed']}, کل: {total_provinces}"
        logging.info(final_msg)
        if progress_callback:
            progress_callback(final_msg, self.email_queue.stats['sent'] > 0)
            
        self.root.after(0, lambda: self.show_final_results(self.email_queue.stats))

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def update_time(self):
        """به‌روزرسانی زمان"""
        current_time = time.strftime("%Y/%m/%d %H:%M:%S")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)

    def select_attachment_files(self):
        """Select multiple attachment files and create province reports"""
        attach_mode = self.attach_mode_var.get()
        if attach_mode == 'with_attachment':
            file_paths = filedialog.askopenfilenames(
                title="انتخاب فایل‌های پیوست",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            self.attachment_paths = list(file_paths)
            if self.attachment_paths:
                file_names = [Path(p).name for p in self.attachment_paths]
                self.attachment_label.config(text=", ".join(file_names))
                try:
                    self.status_var.set("در حال ایجاد گزارش‌های استانی...")
                    provinces = create_province_reports(self.attachment_paths)
                    self.populate_provinces()
                    self.status_var.set(f"گزارش‌های {len(provinces)} استان ایجاد شد")
                    messagebox.showinfo("موفقیت", f"گزارش‌های {len(provinces)} استان با موفقیت ایجاد شدند!")
                except Exception as e:
                    self.status_var.set("خطا در ایجاد گزارش‌ها")
                    messagebox.showerror("خطا", f"خطا در ایجاد گزارش‌ها: {str(e)}")
            else:
                self.attachment_label.config(text="هیچ فایلی انتخاب نشده")
                self.populate_provinces()

        elif attach_mode == 'with_single_file':
            file_path = filedialog.askopenfilename(
                title="انتخاب فایل پیوست یکسان",
                filetypes=[("All files", "*.*")]
            )
            if file_path:
                self.single_attachment_path = file_path
                self.attachment_label.config(text=Path(file_path).name)
            else:
                self.single_attachment_path = None
                self.attachment_label.config(text="هیچ فایلی انتخاب نشده")
            self.populate_provinces()

    def create_reports(self):
        """Create province reports from selected attachment files"""
        try:
            if not self.attachment_paths:
                raise ValueError("لطفاً حداقل یک فایل پیوست انتخاب کنید!")
            
            self.status_var.set("در حال ایجاد گزارش‌ها...")
            provinces = create_province_reports(self.attachment_paths)
            self.populate_provinces()
            self.status_var.set(f"گزارش‌های {len(provinces)} استان ایجاد شد")
            messagebox.showinfo("موفقیت", f"گزارش‌های {len(provinces)} استان با موفقیت ایجاد شدند!")
        except Exception as e:
            self.status_var.set("خطا در ایجاد گزارش‌ها")
            messagebox.showerror("خطا", f"خطا در ایجاد گزارش‌ها: {str(e)}")

    def clear_reports(self):
        """Clear the Province Report folder"""
        try:
            output_dir = Path('Province Report')
            if output_dir.exists():
                clean_directory(output_dir)
            
            self.populate_provinces()
            self.status_var.set("گزارش‌ها پاکسازی شدند")
            messagebox.showinfo("موفقیت", "پوشه گزارش‌های استانی با موفقیت پاکسازی شد!")
        except Exception as e:
            self.status_var.set("خطا در پاکسازی")
            messagebox.showerror("خطا", f"خطا در پاکسازی گزارش‌ها: {str(e)}")

    def show_recipients(self):
        """Show recipients for selected provinces"""
        selected_provinces = [self.province_listbox.get(i) for i in self.province_listbox.curselection()]
        self.recipients_text.config(state='normal')
        self.recipients_text.delete(1.0, tk.END)
    
        if not selected_provinces:
            messagebox.showwarning("هشدار", "لطفاً حداقل یک استان انتخاب کنید!")
            return
    
        for province in selected_provinces:
            to_emails, cc_emails, bcc_emails = get_province_emails_cached(province)
            self.recipients_text.insert(tk.END, f"استان {province}:\n")
            self.recipients_text.insert(tk.END, f"TO: {', '.join(to_emails) if to_emails else 'هیچ'}\n")
            self.recipients_text.insert(tk.END, f"CC: {', '.join(cc_emails) if cc_emails else 'هیچ'}\n")
            self.recipients_text.insert(tk.END, f"BCC: {', '.join(bcc_emails) if bcc_emails else 'هیچ'}\n\n")
    
        self.recipients_text.config(state='disabled')

    def preview_email(self):
        """Preview email in HTML format for all selected provinces"""
        selected_provinces = [self.province_listbox.get(i) for i in self.province_listbox.curselection()]
        if not selected_provinces:
            messagebox.showwarning("هشدار", "لطفاً حداقل یک استان انتخاب کنید!")
            return
    
        html_previews = []
        for province_name in selected_provinces:
            html_body = create_html_body(
                province_name, self.body_text, self.signature_text,
                self.direction_var.get(), get_logo_base64_cached(self.logo_path),
                self.body_font_var.get(), int(self.body_size_var.get())
            )
            province_header = f'<div style="font-size: 14pt; font-weight: bold; margin-bottom: 20px; color: #1e88e5;">ایمیل برای استان {province_name}</div>'
            html_previews.append(province_header + html_body + '<hr style="margin: 30px 0;">')
    
        preview_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>پیش‌نمایش ایمیل</title>
        </head>
        <body>
            {''.join(html_previews)}
        </body>
        </html>
        """
    
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding="utf-8") as temp_html:
                temp_html.write(preview_content)
                temp_file_path = temp_html.name
            webbrowser.open(f'file://{Path(temp_file_path).absolute()}')
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ایجاد پیش‌نمایش: {e}")

    def validate_email_settings(self):
        """Validate email settings before sending"""
        sender_name = self.sender_name_entry.get().strip()
        sender_email = self.sender_email_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        server_host = self.server_host_entry.get().strip()
        server_port = self.server_port_entry.get().strip()
    
        if not sender_name:
            raise ValueError("نام فرستنده نمی‌تواند خالی باشد!")
        if not sender_email:
            raise ValueError("ایمیل فرستنده نمی‌تواند خالی باشد!")
    
        is_valid, error_msg = DataValidator.validate_email_advanced(sender_email)
        if not is_valid:
            raise ValueError(f"ایمیل فرستنده: {error_msg}")
        
        if not username:
            raise ValueError("نام کاربری نمی‌تواند خالی باشد!")
        if not password:
            raise ValueError("رمز عبور نمی‌تواند خالی باشد!")
        if not server_host:
            raise ValueError("آدرس سرور SMTP نمی‌تواند خالی باشد!")
        if not server_port or not server_port.isdigit():
            raise ValueError("پورت SMTP نامعتبر است!")

        return sender_name, sender_email, username, password, server_host, int(server_port)

    def save_settings(self):
        """Save email settings to a JSON file"""
        try:
            settings = {
                "subject": self.subject_entry.get(),
                "body": self.body_text.get("1.0", tk.END).strip(),
                "signature": self.signature_text.get("1.0", tk.END).strip(),
                "direction": self.direction_var.get(),
                "sender_name": self.sender_name_entry.get(),
                "sender_email": self.sender_email_entry.get(),
                "username": self.username_entry.get(),
                "password": self.password_entry.get(),
                "server_host": self.server_host_entry.get(),
                "server_port": self.server_port_entry.get(),
                "logo_path": self.logo_path,
                "attach_mode": self.attach_mode_var.get(),
                "attachment_paths": self.attachment_paths,
                "single_attachment_path": self.single_attachment_path,
                "batch_size": self.batch_size,
                "wait_time": self.wait_time
            }
        
            self.secure_settings.save_settings_secure(settings, self.settings_file)
            self.status_var.set("تنظیمات ذخیره شدند")
            messagebox.showinfo("موفقیت", "تنظیمات با موفقیت ذخیره شدند!")
        except Exception as e:
            self.status_var.set("خطا در ذخیره تنظیمات")
            messagebox.showerror("خطا", f"خطا در ذخیره تنظیمات: {e}")

    def load_settings(self):
        """Load email settings from a JSON file"""
        try:
            settings = self.secure_settings.load_settings_secure(self.settings_file)
        
            self.default_subject = settings.get("subject", self.default_subject)
            self.default_body = settings.get("body", self.default_body)
            self.default_signature = settings.get("signature", DEFAULT_SIGNATURE)
            self.direction_var = tk.StringVar(value=settings.get("direction", "rtl"))
            self.sender_name = settings.get("sender_name", DEFAULT_SENDER_NAME)
            self.sender_email = settings.get("sender_email", DEFAULT_SENDER_EMAIL)
            self.username = settings.get("username", DEFAULT_USERNAME)
            self.password = settings.get("password", DEFAULT_PASSWORD)
            self.server_host = settings.get("server_host", DEFAULT_EMAIL_SERVER)
            self.server_port = int(settings.get("server_port", DEFAULT_PORT))
            self.logo_path = settings.get("logo_path", DEFAULT_LOGO)
            self.attachment_paths = settings.get("attachment_paths", [])
            self.single_attachment_path = settings.get("single_attachment_path")
            self.batch_size = settings.get("batch_size", 5)
            self.wait_time = settings.get("wait_time", 300)
            self.attach_mode_var = tk.StringVar(value=settings.get("attach_mode", "with_attachment"))
            
            if hasattr(self, 'subject_entry'):
                self.subject_entry.delete(0, tk.END)
                self.subject_entry.insert(0, self.default_subject)
            if hasattr(self, 'body_text'):
                self.body_text.delete("1.0", tk.END)
                self.body_text.insert(tk.END, self.default_body)
            if hasattr(self, 'signature_text'):
                self.signature_text.delete("1.0", tk.END)
                self.signature_text.insert(tk.END, self.default_signature)
            if hasattr(self, 'sender_name_entry'):
                self.sender_name_entry.delete(0, tk.END)
                self.sender_name_entry.insert(0, self.sender_name)
            if hasattr(self, 'sender_email_entry'):
                self.sender_email_entry.delete(0, tk.END)
                self.sender_email_entry.insert(0, self.sender_email)
            if hasattr(self, 'username_entry'):
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, self.username)
            if hasattr(self, 'password_entry'):
                self.password_entry.delete(0, tk.END)
                self.password_entry.insert(0, self.password)
            if hasattr(self, 'server_host_entry'):
                self.server_host_entry.delete(0, tk.END)
                self.server_host_entry.insert(0, self.server_host)
            if hasattr(self, 'server_port_entry'):
                self.server_port_entry.delete(0, tk.END)
                self.server_port_entry.insert(0, str(self.server_port))
            if hasattr(self, 'attachment_label'):
                if self.attachment_paths:
                    file_names = [Path(p).name for p in self.attachment_paths]
                    self.attachment_label.config(text=", ".join(file_names))
                elif self.single_attachment_path:
                    self.attachment_label.config(text=Path(self.single_attachment_path).name)
                else:
                    self.attachment_label.config(text="هیچ فایلی انتخاب نشده")
            
        except Exception as e:
            logging.warning(f"Could not load settings: {e}")

    def reset_defaults(self):
        """Reset subject, body, and signature to default values"""
        self.subject_entry.delete(0, tk.END)
        self.subject_entry.insert(0, "مغایرت طراحی - {province_name} - {date}")
    
        self.body_text.delete("1.0", tk.END)
        self.body_text.insert(tk.END, """همکاران محترم استان {province_name}

مغایرت های طراحی جهت بررسی و رفع در ارس به پیوست ارسال شد. در صورت وجود استثنا به همین ایمیل ارسال فرمایید.""")
    
        self.signature_text.delete("1.0", tk.END)
        self.signature_text.insert(tk.END, DEFAULT_SIGNATURE)
    
        self.direction_var.set("rtl")
    
        self.sender_name_entry.delete(0, tk.END)
        self.sender_name_entry.insert(0, DEFAULT_SENDER_NAME)
        self.sender_email_entry.delete(0, tk.END)
        self.sender_email_entry.insert(0, DEFAULT_SENDER_EMAIL)
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, DEFAULT_USERNAME)
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, DEFAULT_PASSWORD)
        self.server_host_entry.delete(0, tk.END)
        self.server_host_entry.insert(0, DEFAULT_EMAIL_SERVER)
        self.server_port_entry.delete(0, tk.END)
        self.server_port_entry.insert(0, str(DEFAULT_PORT))

        self.logo_path = DEFAULT_LOGO
        self.attachment_paths = []
        self.single_attachment_path = None
        self.attachment_label.config(text="هیچ فایلی انتخاب نشده")
        self.populate_provinces()
    
        self.status_var.set("تنظیمات بازگردانده شدند")
        messagebox.showinfo("موفقیت", "تنظیمات به حالت پیش‌فرض بازگردانده شدند!")

    def toggle_select_all(self):
        """Select or deselect all provinces"""
        if self.select_all_var.get():
            self.province_listbox.select_set(0, tk.END)
        else:
            self.province_listbox.selection_clear(0, tk.END)

    def get_attachment_paths_for_province(self, province):
        """دریافت مسیر پیوست‌ها برای استان"""
        output_dir = Path('Province Report')
        if output_dir.exists():
            province_file = output_dir / f"{province}.xlsx"
            return [str(province_file)] if province_file.exists() else []
        return []

    def send_emails(self):
        """ارسال ایمیل‌ها با پیشرفت بهبود یافته"""
        selected_provinces = [self.province_listbox.get(i) for i in self.province_listbox.curselection()]
        if not selected_provinces:
            messagebox.showwarning("هشدار", "لطفاً حداقل یک استان انتخاب کنید!")
            return

        try:
            sender_name, sender_email, username, password, server_host, server_port = self.validate_email_settings()
        except ValueError as e:
            messagebox.showerror("خطا", str(e))
            return

        attach_mode = self.attach_mode_var.get()
        if attach_mode == 'with_attachment':
            output_dir = Path('Province Report')
            if not output_dir.exists() or not any(output_dir.glob('*.xlsx')):
                if not messagebox.askyesno("هشدار", "هیچ گزارش استانی یافت نشد. آیا می‌خواهید بدون پیوست ارسال کنید?"):
                    return
        elif attach_mode == 'with_single_file' and (not self.single_attachment_path or not Path(self.single_attachment_path).exists()):
             if not messagebox.askyesno("هشدار", "فایل یکسان برای پیوست انتخاب نشده یا وجود ندارد! آیا می‌خواهید بدون پیوست ارسال کنید?"):
                 return
             self.attach_mode_var.set('without_attachment')

        progress_dialog = ProgressDialog(self.root, len(selected_provinces))
    
        email_queue = EmailQueue(max_workers=2)
    
        for province in selected_provinces:
            attachment_paths = []
            if attach_mode == 'with_attachment':
                attachment_paths = self.get_attachment_paths_for_province(province)
            elif attach_mode == 'with_single_file':
                attachment_paths = [self.single_attachment_path] if self.single_attachment_path else []

            email_data = {
                'province_name': province,
                'attachment_paths': attachment_paths,
                'subject': self.subject_entry.get(),
                'body_text': self.body_text,
                'signature_text': self.signature_text,
                'direction': self.direction_var.get(),
                'sender_name': sender_name,
                'sender_email': sender_email,
                'username': username,
                'password': password,
                'logo_path': self.logo_path,
                'font_family': self.body_font_var.get(),
                'font_size': int(self.body_size_var.get()),
                'server_host': server_host,
                'server_port': server_port
            }
            email_queue.add_email(email_data)
    
        def send_worker():
            try:
                email_queue.process_queue(
                    callback=lambda province, success, stats: 
                        self.root.after(0, lambda: progress_dialog.update_progress(province, success, stats))
                )
                
                final_stats = email_queue.stats
                self.root.after(0, lambda: self.show_final_results(final_stats))
                
            except Exception as e:
                logging.error(f"Error in send worker: {e}")
                self.root.after(0, lambda: messagebox.showerror("خطا", f"خطا در ارسال ایمیل‌ها: {e}"))
    
        thread = Thread(target=send_worker, daemon=True)
        thread.start()
    
        original_cancel = progress_dialog.cancel
        def cancel_with_queue():
            email_queue.cancel()
            original_cancel()
        progress_dialog.cancel = cancel_with_queue

    def show_final_results(self, stats):
        """نمایش نتایج نهایی ارسال"""
        total = stats['total']
        sent = stats['sent']
        failed = stats['failed']
        self.failed_provinces = stats['failed_provinces']
    
        self.status_var.set(f"ارسال تکمیل شد: {sent} موفق، {failed} ناموفق")
    
        if failed == 0:
            messagebox.showinfo("موفقیت", f"همه {total} ایمیل با موفقیت ارسال شدند!")
        else:
            failed_list = "\n".join([f"- {p}" for p in self.failed_provinces])
            resend = messagebox.askyesno(
                "تکمیل با خطا",
                f"از {total} ایمیل، {sent} موفق و {failed} ناموفق بودند.\n\n"
                f"استان‌های ناموفق:\n{failed_list}\n\n"
                "آیا می‌خواهید فقط برای این استان‌ها دوباره ارسال کنید؟"
            )
            if resend:
                self.resend_failed_emails()
    
        self.save_settings()

    def resend_failed_emails(self):
        """انتخاب استان‌های ناموفق برای ارسال مجدد"""
        self.province_listbox.selection_clear(0, tk.END)
        for i, province in enumerate(self.province_listbox.get(0, tk.END)):
            if province in self.failed_provinces:
                self.province_listbox.selection_set(i)
        
        self.failed_provinces = []
        self.status_var.set("آماده برای ارسال مجدد استان‌های ناموفق")
        messagebox.showinfo("ارسال مجدد", "استان‌های ناموفق انتخاب شدند. حالا می‌توانید دکمه 'ارسال ایمیل‌ها' را فشار دهید.")

    def test_email_connection(self):
        """تست اتصال ایمیل"""
        try:
            sender_name, sender_email, username, password, server_host, server_port = self.validate_email_settings()
            
            self.status_var.set("در حال تست اتصال...")
            
            with secure_smtp_connection(server_host, server_port, username, password) as server:
                self.status_var.set("اتصال موفق")
                messagebox.showinfo("موفقیت", "اتصال ایمیل با موفقیت برقرار شد!")
                
        except Exception as e:
            self.status_var.set("خطا در اتصال")
            messagebox.showerror("خطا", f"خطا در اتصال ایمیل: {str(e)}")

    def clear_cache(self):
        """پاکسازی کش"""
        try:
            get_province_emails_cached.cache_clear()
            get_logo_base64_cached.cache_clear()
            self.status_var.set("کش پاکسازی شد")
            messagebox.showinfo("موفقیت", "کش با موفقیت پاکسازی شد!")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در پاکسازی کش: {e}")

    def show_logs(self):
        """نمایش لاگ‌ها"""
        log_window = tb.Toplevel(self.root)
        log_window.title("لاگ‌های سیستم")
        log_window.geometry("900x600")
        log_window.transient(self.root)
        
        frame = tb.Frame(log_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = tb.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        try:
            with open('email_system.log', 'r', encoding='utf-8') as f:
                content = f.read()
                text_widget.insert(tk.END, content)
        except FileNotFoundError:
            text_widget.insert(tk.END, "هیچ لاگی یافت نشد.")
        except Exception as e:
            text_widget.insert(tk.END, f"خطا در خواندن لاگ: {e}")
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tb.Button(log_window, text="بستن", command=log_window.destroy, bootstyle="secondary").pack(pady=5)

    def show_help(self):
        """نمایش راهنما"""
        help_text = """راهنمای استفاده از سیستم ارسال ایمیل استانی v2.0

میانبرهای صفحه کلید:
• Ctrl+S: ذخیره تنظیمات
• Ctrl+O: انتخاب فایل‌های پیوست
• Ctrl+P: پیش‌نمایش ایمیل
• F5: به‌روزرسانی لیست استان‌ها
• Ctrl+Enter: ارسال ایمیل‌ها

میانبرهای متنی:
• Ctrl+C: کپی
• Ctrl+V: چسباندن
• Ctrl+X: برش
• Ctrl+A: انتخاب همه
• Ctrl+Z: بازگردانی
• Ctrl+Y: انجام مجدد

مراحل استفاده:
1. تنظیم اطلاعات ایمیل در بخش "تنظیمات ایمیل"
2. انتخاب فایل‌های پیوست (اختیاری)
3. انتخاب استان‌های مورد نظر
4. تنظیم موضوع و متن ایمیل
5. پیش‌نمایش ایمیل برای بررسی
6. ارسال ایمیل‌ها

ویژگی‌های جدید v2.0:
• ارسال همزمان چندگانه
• نمایش پیشرفت real-time
• سیستم مدیریت خطای پیشرفته
• کش بهینه شده
• لاگ گذاری کامل
• Copy/Paste کامل
• ارسال دسته‌ای

نکات مهم:
• فایل email_list.xlsx باید در مسیر برنامه موجود باشد
• لوگوی شرکت در فایل nak_logo.png ذخیره شده باشد
• اتصال اینترنت برای ارسال ایمیل ضروری است
• تنظیمات به صورت امن ذخیره می‌شوند

پشتیبانی:
در صورت بروز مشکل، لاگ‌های سیستم را بررسی کنید."""

        messagebox.showinfo("راهنمای استفاده", help_text)

    def show_about(self):
        """نمایش اطلاعات برنامه"""
        about_text = """سیستم ارسال ایمیل استانی v2.0

توسعه یافته برای شرکت نقش اول کیفیت
© تمامی حقوق محفوظ است

ویژگی‌های کلیدی:
✓ ارسال همزمان چندگانه
✓ نمایش پیشرفت
✓ مدیریت خطای پیشرفته
✓ کش بهینه شده
✓ رابط کاربری بهبود یافته
✓ لاگ گذاری کامل
✓ ذخیره امن تنظیمات
✓ Copy/Paste کامل
✓ ارسال دسته‌ای

کتابخانه‌های استفاده شده:
• pandas - پردازش داده
• openpyxl - کار با فایل‌های Excel
• tkinter - رابط کاربری
• smtplib - ارسال ایمیل
• jdatetime - تاریخ شمسی

نسخه Python مورد نیاز: 3.7+"""

        messagebox.showinfo("درباره برنامه", about_text)

    def new_settings(self):
        """ایجاد تنظیمات جدید"""
        if messagebox.askyesno("تأیید", "آیا می‌خواهید تنظیمات فعلی را پاک کرده و از نو شروع کنید؟"):
            self.reset_defaults()

    def load_settings_file(self):
        """بارگذاری تنظیمات از فایل"""
        file_path = filedialog.askopenfilename(
            title="انتخاب فایل تنظیمات",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.settings_file = file_path
                self.load_settings()
                messagebox.showinfo("موفقیت", "تنظیمات با موفقیت بارگذاری شدند!")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در بارگذاری تنظیمات: {e}")

    def update_font(self, widget, family, size):
        """Update font of the given text widget"""
        try:
            new_font = font.Font(family=family, size=int(size))
            widget.config(font=new_font)
        except Exception as e:
            logging.error(f"Error updating font: {e}")

if __name__ == "__main__":
    try:
        root = tb.Window(themename="cosmo")
        app = EmailAppImproved(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Critical error in program execution: {e}")
        logging.error(traceback.format_exc())
        print(f"خطای بحرانی در اجرای برنامه: {e}")
        input("برای خروج Enter را فشار دهید...")