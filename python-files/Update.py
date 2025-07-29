import pyodbc
import configparser
import logging
from pathlib import Path
import os
import sys
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import chardet
import threading
selected_servers = []
root_dir = Path("~").expanduser() #PROGRAMIN ÇALIŞTIĞI USER

if getattr(sys, 'frozen', False):
    root_dir = Path(sys._MEIPASS)
else:
    root_dir = Path(__file__).parent

# Eğer yine masaüstüne erişmen gerekiyorsa:
os.chdir(root_dir)

def create_server_checkboxes(window, config, server_vars):
    checkbox_frame = tk.Frame(window)
    checkbox_frame.pack(pady=5, fill='x')

    tk.Label(checkbox_frame, text="Güncellenecek Databaseler:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky='w', padx=5, pady=2, columnspan=3)

    # Tümünü Seç checkbox
    select_all_var = tk.BooleanVar()

    def toggle_all():
        for var in server_vars.values():
            var.set(select_all_var.get())

    select_all_checkbox = tk.Checkbutton(
        checkbox_frame,
        text="Tümünü Seç",
        variable=select_all_var,
        command=toggle_all,
        font=("Arial", 10)
    )
    select_all_checkbox.grid(row=1, column=0, sticky='w', padx=5, pady=2, columnspan=3)

    # Çok sütunlu checkbox yapısı
    columns = 4  # Kaç sütun istiyorsan buradan ayarla
    row = 2
    col = 0

    for idx, server in enumerate(config.sections()):
        var = tk.BooleanVar()
        chk = tk.Checkbutton(checkbox_frame, text=server, variable=var)
        chk.grid(row=row, column=col, sticky='w', padx=5, pady=2)
        server_vars[server] = var

        col += 1
        if col >= columns:
            col = 0
            row += 1
        
def read_sql_file(file_path):
    # Encoding'i tespit et
    with open(file_path, 'rb') as raw_file:
        raw_data = raw_file.read()
        encoding_result = chardet.detect(raw_data)
        detected_encoding = encoding_result['encoding']

    # Doğru encoding ile tekrar aç
    with open(file_path, 'r', encoding=detected_encoding) as file:
        return file.read()
def get_configurations(file_path='Servers.ini'):
    full_path = os.path.abspath(file_path)
    print(f"[DEBUG] ini dosyası buradan okunuyor: {full_path}")
    config = configparser.ConfigParser()
    config.read(full_path, encoding='utf-8')
    sorted_config = configparser.ConfigParser()
    for section in sorted(config.sections()):  # Section'lar alfabetik
        sorted_config.add_section(section)
        for key in sorted(config[section]):  # Anahtarlar da alfabetik
            sorted_config[section][key] = config[section][key]
    return sorted_config

def log_message(textbox, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_message = f"[{timestamp}] {message}\n"

    def insert_log():
        textbox.insert(tk.END, full_message)
        textbox.see(tk.END)
    
    textbox.after(0, insert_log)


def connect_and_deploy(server_name, config, sql_script, sql_file_name, textbox):
    print(f"[CONNECT] server_name = {server_name}")
    print(f"[CONNECT] keys = {list(config[server_name].keys())}")
    required_keys = ['host', 'port', 'database']
    for key in required_keys:
        if key not in config[server_name]:
            if textbox:
                log_message(textbox, f"[HATA] {server_name} içinde '{key}' tanımı eksik. Atlanıyor.")
            else:
                print(f"[HATA] {server_name} içinde '{key}' tanımı eksik. Atlanıyor.")
            return
    host = config[server_name]['host']
    port = config[server_name]['port']
    database = config[server_name]['database']
    auth_type = config[server_name].get('auth', 'sql')
    city_code = config[server_name].get('city_code', '')
    city_name = config[server_name].get('city_name', '')

    # Placeholder değişimleri
    sql_script = sql_script.replace('{{CITY_CODE}}', city_code)
    sql_script = sql_script.replace('{{CITY_NAME}}', city_name)
    sql_script = sql_script.replace('{{DATABASE}}', database)

    if auth_type == 'windows':
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={host},{port};DATABASE={database};'
            f'Trusted_Connection=yes;'
        )
    else:
        username = config[server_name]['username']
        password = config[server_name]['password']
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={host},{port};DATABASE={database};'
            f'UID={username};PWD={password};'
        )

    try:
        conn = pyodbc.connect(conn_str, timeout=40)
        cursor = conn.cursor()
        cursor.execute(sql_script)
        log_message(textbox, f"{server_name} - {database} - {sql_file_name} ✅ başarı ile çalıştı.")
        conn.commit()
    except Exception as e:
        log_message(textbox, f"{server_name} - {database} - {sql_file_name} ❌ hata: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
    log_message(textbox, f"İşlem tamamlandı.")
      
    

def main(textbox):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    sql_folder = "sql"
    config = get_configurations()
    sql_count=0
    for file_name in os.listdir(sql_folder):
        if file_name.endswith(".sql"):
            sql_count=1
            file_path = os.path.join(sql_folder, file_name)
            sql_script = read_sql_file(file_path)

            for server in config.sections():
                print(f"[DEBUG] Aktif section: {server}")
                print(f"[DEBUG] Keys: {list(config[server].keys())}")
                try:
                    connect_and_deploy(server, config, sql_script, file_name, textbox)
                except Exception as e:
                    log_message(textbox, f"[EXCEPTION] {server} için beklenmeyen hata: {e}")
    if sql_count==0:
        log_message(f"SQL Dosyası tespit edilemedi. ❌")

def run_deployment(textbox, selected_servers):
    log_message(textbox, f"Program çalışmaya başladı")
    sql_folder = str(root_dir)+os.sep+'sql'
    config = get_configurations()
    log_message(textbox, f"Server bilgileri alındı.")
    sql_count = 0

    for file_name in os.listdir(sql_folder):
        if file_name.endswith(".sql"):
            sql_count = 1
            file_path = os.path.join(sql_folder, file_name)
            sql_script = read_sql_file(file_path)

            for server in selected_servers:
                connect_and_deploy(server, config, sql_script, file_name, textbox)
                

    if sql_count == 0:
        log_message(textbox, f"SQL Dosyası tespit edilemedi. ❌")
        log_message(textbox, f"Dosyanın uzantısının .sql olduğunu kontrol edin.")
def start_deployment_thread(textbox, server_vars):
    selected = [server for server, var in server_vars.items() if var.get()]
    if not selected:
        log_message(textbox, f"Hiçbir Database seçilmedi ❌")
        log_message(textbox, f"Yukarıdaki checkboxlardan scriptin çalışmasını istediğiniz Databasei seçin.")
        return
    thread = threading.Thread(target=run_deployment, args=(textbox, selected))
    
    thread.start()

def start_gui():
    window = tk.Tk()
    window.title("SQL Toplu Script Çalıştırma")
    window.geometry("1000x900")

    config = get_configurations()
    server_vars = {}

    create_server_checkboxes(window, config, server_vars)

    textbox = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Consolas", 9), height=20)
    textbox.pack(expand=False, fill='both')

    start_button = tk.Button(window, text="Scripti Çalıştır", command=lambda: start_deployment_thread(textbox, server_vars))
    start_button.pack(pady=10)
    log_message(textbox, f"""SQL klasörünün içerisine, Databaselerde çalıştırmak istediğiniz scripti .sql uzantısı ile koyarak "Scripti Çalıştır" butonuna basın.""")
    window.mainloop()
if __name__ == "__main__":
    start_gui()