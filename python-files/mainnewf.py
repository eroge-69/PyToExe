# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: mainnew.py
# Bytecode version: 3.9.0beta5 (3425)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

global streaming_active  # inserted
global qr_image_label  # inserted
global qr_window  # inserted
global license_verified  # inserted
global cookies  # inserted
global current_retry_count  # inserted
global process  # inserted
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import threading
import requests
import json
import re
import uuid
import os
import hashlib
import base64
import qrcode
import time
import datetime
import glob
import sys
from PIL import Image
MASTER_LICENSE = 'lemot'
license_verified = False
current_retry_count = 0
max_retry_attempts = 3
retry_interval = 5000
process = None
cookies = {}
streaming_active = False

def generate_key():
    return f'EZST-{uuid.uuid4()}'

def get_license_file_path():
    home_dir = os.path.expanduser('~')
    license_dir = os.path.join(home_dir, '.ezstream')
    if not os.path.exists(license_dir):
        os.makedirs(license_dir)
    return os.path.join(license_dir, 'ezstream.key')

def save_key_to_file(key):
    file_path = get_license_file_path()
    with open(file_path, 'w') as file:
        file.write(key)

def read_key_from_file():
    file_path = get_license_file_path()
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return

def verify_key_with_server(key):
    if key == MASTER_LICENSE:
        return True
    response = requests.get(f'https://stream.ezhub.cloud/api.php?key={key}')
    return response.status_code == 403

def choose_file():
    file_path = filedialog.askopenfilename()
    file_path_entry.delete(0, ctk.END)
    file_path_entry.insert(0, file_path)

def choose_folder():
    folder_path = filedialog.askdirectory()
    folder_path_entry.delete(0, ctk.END)
    folder_path_entry.insert(0, folder_path)

def update_ui_start_enabled():
    start_button.configure(state='normal')
    stop_button.configure(state='disabled')

def handle_connection_failure():
    global current_retry_count  # inserted
    if current_retry_count < max_retry_attempts:
        current_retry_count += 1
        root.after(retry_interval, start_streaming)
    else:  # inserted
        messagebox.showerror('Error', 'Gagal menyambungkan ke server setelah beberapa percobaan.')
        update_ui_start_enabled()

def start_streaming():
    global current_retry_count  # inserted
    global streaming_active  # inserted
    console_output.configure(state='normal')
    console_output.insert('end', 'Memulai live streaming...\n')
    console_output.see('end')
    console_output.configure(state='disabled')
    current_retry_count = 0
    start_button.configure(state='disabled')
    stop_button.configure(state='normal')
    server_url = server_entry_var.get()
    stream_key = key_entry_var.get()
    mode = mode_var.get() if 'mode_var' in globals() else 'VCAM'
    if mode == 'VCAM':
        video_file = file_path_entry.get()
    else:  # inserted
        video_file = folder_path_entry.get()
    streaming_active = True

    def simple_streaming():
        global streaming_active  # inserted
        global process  # inserted
        console_output.configure(state='normal')
        console_output.insert('end', f'Memulai streaming mode {mode}...\n')
        console_output.see('end')
        console_output.configure(state='disabled')
        if mode == 'VCAM':
            command = ['ffmpeg', '-re', '-stream_loop', '-1', '-i', video_file, '-c', 'copy', '-f', 'flv', '-loglevel', 'info', f'{server_url}/{stream_key}']
        else:  # inserted
            folder_path = video_file
            if not os.path.isdir(folder_path):
                console_output.configure(state='normal')
                console_output.insert('end', '[ERROR] Pilih folder yang berisi partXXX.mp4 untuk mode NON VCAM\n')
                console_output.see('end')
                console_output.configure(state='disabled')
                update_ui_start_enabled()
                return

            def get_sorted_parts():
                files = [f for f in os.listdir(folder_path) if f.startswith('part') and f.endswith('.mp4')]
                files.sort(key=lambda x: int(re.search('part(\\d+)', x).group(1)) if re.search('part(\\d+)', x) else 0)
                return [os.path.join(folder_path, f) for f in files]

            def stream_parts_loop():
                global streaming_active  # inserted
                global process  # inserted
                part_index = 0
                while streaming_active:
                    parts = get_sorted_parts()
                    if not parts:
                        console_output.configure(state='normal')
                        console_output.insert('end', '[ERROR] Tidak ada file partXXX.mp4 ditemukan di folder.\n')
                        console_output.see('end')
                        console_output.configure(state='disabled')
                        break
                    current_part = parts[part_index % len(parts)]
                    part_name = os.path.basename(current_part)
                    if not streaming_active:
                        break
                    console_output.configure(state='normal')
                    console_output.insert('end', f'[NON VCAM] Streaming {part_name}...\n')
                    console_output.see('end')
                    console_output.configure(state='disabled')
                    current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    console_output.configure(state='normal')
                    console_output.insert('end', f'[METADATA] Injecting creation_time: {current_time}\n')
                    console_output.see('end')
                    console_output.configure(state='disabled')
                    command = ['ffmpeg', '-re', '-i', current_part, '-c', 'copy', '-metadata', f'creation_time={current_time}', '-metadata', f'comment=Streamed at {current_time}', '-f', 'flv', '-loglevel', 'info', f'{server_url}/{stream_key}']
                    creation_flags = 134217728 if os.name == 'nt' else 0
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1, creationflags=creation_flags)

                    def consume_output():
                        global streaming_active  # inserted
                        for line in iter(process.stdout.readline, ''):
                            if not streaming_active:
                                break
                            if line.strip():
                                if any((skip_msg in line for skip_msg in ['Failed to update header with correct filesize', 'Failed to update header with correct duration', 'muxing overhead:', 'video:', 'audio:', 'subtitle:', 'other streams:', 'global headers:'])):
                                    continue
                                console_output.configure(state='normal')
                                console_output.insert('end', f'[FFMPEG] {line}')
                                console_output.see('end')
                                console_output.configure(state='disabled')
                                if 'Conversion failed!' in line:
                                    console_output.configure(state='normal')
                                    console_output.insert('end', '[ERROR] Deteksi kegagalan konversi. Menghentikan streaming...\n')
                                    console_output.see('end')
                                    console_output.configure(state='disabled')
                                    streaming_active = False
                                    if process:
                                        try:
                                            process.terminate()
                                        except:
                                            pass
                                    break
                    output_thread = threading.Thread(target=consume_output, daemon=True)
                    output_thread.start()
                    return_code = process.wait()
                    if return_code!= 0 and streaming_active:
                        console_output.configure(state='normal')
                        console_output.insert('end', f'\n[ERROR] Gagal streaming {part_name}: {return_code}\n')
                        console_output.see('end')
                        console_output.configure(state='disabled')
                    part_index += 1
                    if streaming_active:
                        console_output.configure(state='normal')
                        console_output.insert('end', f'[NON VCAM]  {part_name} Selesai. Beralih ke Part Berikutnya...\n')
                        console_output.see('end')
                        console_output.configure(state='disabled')
                        for i in range(5):
                            if not streaming_active:
                                break
                            time.sleep(2)
                streaming_active = False
                console_output.configure(state='normal')
                console_output.insert('end', '\n[INFO] Streaming NON VCAM selesai\n')
                console_output.see('end')
                console_output.configure(state='disabled')
            threading.Thread(target=stream_parts_loop, daemon=True).start()
            return
        creation_flags = 134217728 if os.name == 'nt' else 0
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1, creationflags=creation_flags)

        def consume_output():
            global streaming_active  # inserted
            for line in iter(process.stdout.readline, ''):
                if not streaming_active:
                    break
                if line.strip():
                    if any((skip_msg in line for skip_msg in ['Failed to update header with correct filesize', 'muxing overhead:', 'video:', 'audio:', 'subtitle:', 'other streams:', 'global headers:'])):
                        continue
                    console_output.configure(state='normal')
                    console_output.insert('end', f'[FFMPEG] {line}')
                    console_output.see('end')
                    console_output.configure(state='disabled')
                    if 'Conversion failed!' in line:
                        console_output.configure(state='normal')
                        console_output.insert('end', '[ERROR] Deteksi kegagalan konversi. Menghentikan streaming...\n')
                        console_output.see('end')
                        console_output.configure(state='disabled')
                        streaming_active = False
                        if process:
                            try:
                                process.terminate()
                            except:
                                pass
                        break
        output_thread = threading.Thread(target=consume_output, daemon=True)
        output_thread.start()
        return_code = process.wait()
        if return_code!= 0 and streaming_active:
            console_output.configure(state='normal')
            console_output.insert('end', f'\nKoneksi Hilang: {return_code}\n')
            console_output.insert('end', '[STOP] Menghentikan streaming karena error\n')
            console_output.see('end')
            console_output.configure(state='disabled')
            streaming_active = False
            start_button.configure(state='normal')
            stop_button.configure(state='disabled')
        streaming_active = False
        console_output.configure(state='normal')
        console_output.insert('end', '\n[INFO] Streaming selesai\n')
        console_output.see('end')
        console_output.configure(state='disabled')
    threading.Thread(target=simple_streaming, daemon=True).start()

def stop_streaming():
    global process  # inserted
    global streaming_active  # inserted
    streaming_active = False
    if process is not None:
        try:
            process.terminate()
            process = None
        except:
            pass
    console_output.configure(state='normal')
    console_output.insert('end', '\nMenghentikan streaming...\n')
    console_output.see('end')
    console_output.configure(state='disabled')
    start_button.configure(state='normal')
    stop_button.configure(state='disabled')

def create_input_row(parent, label_text, entry_var=None, button_text=None, button_command=None, row=0):
    label = ctk.CTkLabel(parent, text=label_text)
    label.grid(row=row, column=0, padx=(15, 10), pady=(8, 8), sticky='w')
    entry = ctk.CTkEntry(parent, textvariable=entry_var, height=32) if entry_var is not None else ctk.CTkEntry(parent, height=32)
    entry.grid(row=row, column=1, padx=(0, 10), pady=(8, 8), sticky='ew')
    if button_text and button_command:
        button = ctk.CTkButton(parent, text=button_text, command=button_command, height=32)
        button.grid(row=row, column=2, padx=(0, 15), pady=(8, 8), sticky='ew')
    return entry

def ask_for_license():
    license_window = ctk.CTkToplevel(root)
    license_window.title('Key Anda')
    license_window.geometry('400x200')
    license_window.resizable(False, False)
    generated_key = generate_key()
    key_label = ctk.CTkLabel(license_window, text='Generated Key:')
    key_label.pack(pady=5, padx=20)
    key_entry = ctk.CTkEntry(license_window)
    key_entry.insert(0, generated_key)
    key_entry.configure(state='readonly')
    key_entry.pack(pady=5, padx=20)

    def submit_license():
        global license_verified  # inserted
        if verify_key_with_server(generated_key):
            save_key_to_file(generated_key)
            license_verified = True
            license_window.destroy()
        else:  # inserted
            error_label = ctk.CTkLabel(license_window, text='Invalid license key', text_color='red')
            error_label.pack()

    def on_close():
        global license_verified  # inserted
        license_verified = False
        license_window.destroy()
    submit_button = ctk.CTkButton(license_window, text='Saya sudah mendaftarkan lisensi', command=submit_license)
    submit_button.pack(pady=10)
    license_window.protocol('WM_DELETE_WINDOW', on_close)
    license_window.grab_set()
    root.wait_window(license_window)

def read_cookies_from_file(file_path):
    global cookies  # inserted
    try:
        with open(file_path, 'r') as file:
            cookies = json.load(file)
            account_names = ['Pilih Akun'] + list(cookies.keys())
            account_menu.configure(values=account_names)
            account_menu.set('Pilih Akun')
    except FileNotFoundError:
        cookies = {}
        messagebox.showerror('Error', 'File \'cookies.json\' tidak ditemukan. Pastikan Get Cookie terlebih dahulu untuk mendapatkan Cookie.')

def cookies_to_header_string(cookies):
    return '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

def get_data_live(cookie, session_id):
    url = f'https://live.shopee.co.id/api/v1/session/{session_id}/push_url_list?ver=2'
    headers = {'Host': 'live.shopee.co.id', 'ls_net_unicodeid': '321454518', 'x-shopee-client-timezone': 'Asia/Jakarta', 'client-request-id': '799ed8f0-f88d-44f7-8b8f-d8cd39264047.207', 'client-info': 'device_model=IN9023;os=0;os_version=30;client_version=31620;network=1;platform=1;language=id;cpu_model=Qualcomm+Technologies%2C+Inc+SDM636', 'x-livestreaming-source': 'shopee', 'x-ls-sz-token': 'Om9w2YHSSVM4mwzhy04Vuw==|ui3/GfDKzV9n2h+0KBIK2fSer8L5j2heZXdatTOd63pU0npKs5LEw2GhQOCsGa8a1ij8nONL8IJTsO9ustxRunkMwMbubcU=|44qNR/drvF5S6NKx|08|1', 'x-livestreaming-auth': 'ls_android_v1_10001_1705749720_36f1e51f-333e-4c10-af48-e017d9d57d0c|mH2Ct50CD3f7jkmofKS3qwzDRKJz5mLr2T3/vfAgQRQ=', 'time-type': '1705749720_2', 'user-agent': 'okhttp/3.12.4 app_type=1', 'content-type': 'application/json;charset=UTF-8', 'Cookie': cookie}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

def check_session(cookie_string):
    url = 'https://creator.shopee.co.id/supply/api/lm/sellercenter/realtime/sessionList?page=1&pageSize=1&name='
    headers = {'Host': 'creator.shopee.co.id', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0', 'Accept': 'application/json', 'Accept-Language': 'id,en-US;q=0.7,en;q=0.3', 'Accept-Encoding': 'gzip, deflate, br', 'Referer': 'https://creator.shopee.co.id/insight/live/list', 'Content-Type': 'application/json', 'X-Traceid': 'heG_qY0WxPfYS1WX7klFR', 'Language': 'en', 'X-Region': 'id', 'X-Region-Domain': 'co.id', 'X-Region-Timezone': '+0700', 'X-Env': 'live', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'Te': 'trailers', 'Cookie': cookie_string}
    response = requests.get(url, headers=headers)
    return response.json()

def info_account(cookie_string):
    url = 'https://shopee.co.id/api/v4/account/basic/get_account_info'
    headers = {'Host': 'shopee.co.id', 'Sec-Ch-Ua': '\"Brave\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"', 'Sec-Ch-Ua-Mobile': '?0', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36', 'X-Api-Source': 'pc', 'Content-Type': 'application/json', 'Accept': 'application/json', 'X-Shopee-Language': 'id', 'X-Requested-With': 'XMLHttpRequest', 'Sec-Ch-Ua-Platform': '\"macOS\"', 'Sec-Gpc': '1', 'Accept-Language': 'id-ID,id;q=0.6', 'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://shopee.co.id/?is_from_login=true&is_from_login=true', 'Accept-Encoding': 'gzip, deflate, br', 'Cookie': cookie_string}
    response = requests.get(url, headers=headers)
    return response.json()

def send_message_to_queue(message):
    root.after(0, lambda: append_console_message(message))

def append_console_message(message):
    console_output.configure(state='normal')
    console_output.insert('end', message)
    console_output.see('end')
    console_output.configure(state='disabled')

def get_rtmp_info():
    def worker():
        try:
            account_name = account_menu.get()
            if not account_name or account_name == 'Pilih Akun':
                send_message_to_queue('ERROR:Akun tidak dipilih.\n')
                return
            cookie_string = cookies_to_header_string(cookies[account_name])
            account_information = info_account(cookie_string)
            if account_information is None or 'data' not in account_information:
                send_message_to_queue('ERROR:Cookie expired atau tidak valid. Silakan tambahkan ulang akun.\n')
                return
            username = account_information['data']['username']
            session_information = check_session(cookie_string)
            if session_information is None or 'data' not in session_information or 'list' not in session_information['data']:
                send_message_to_queue('ERROR:Gagal mendapatkan informasi sesi.\n')
                return
            if len(session_information['data']['list']) == 0:
                send_message_to_queue('ERROR:Tidak ada sesi live yang ditemukan.\n')
                return
            live_title = session_information['data']['list'][0]['title']
            session_id = session_information['data']['list'][0]['sessionId']
            note_entry_var.set(f'Username: {username}, Judul: {live_title}')
            while True:  # inserted
                live_data = get_data_live(cookie_string, session_id)
                if live_data is None or 'data' not in live_data or 'push_addr_list' not in live_data['data']:
                    send_message_to_queue(f'DEBUG: Live data response: {live_data}\n')
                    send_message_to_queue('ERROR:Gagal mendapatkan data live stream. Mencoba lagi dalam 2 detik...\n')
                    time.sleep(2)
                    continue
                push_urls = live_data['data']['push_addr_list']
                send_message_to_queue(f'DEBUG: Found {len(push_urls)} push URLs\n')
                rtmp_found = False
                for push_url in push_urls:
                    url = push_url.get('push_url', '')
                    send_message_to_queue(f'DEBUG: Checking URL: {url}\n')
                    if url.startswith('rtmp://push') and '/live/' in url:
                        parts = url.split('/live/')
                        if len(parts) > 1:
                            rtmp_server = parts[0] + '/live/'
                            rtmp_key = parts[1]
                            server_entry_var.set(rtmp_server)
                            key_entry_var.set(rtmp_key)
                            send_message_to_queue('INFO:RTMP server berhasil didapatkan.\n')
                            return
                        rtmp_found = True
                else:  # inserted
                    live_path_found = any(('/live/' in push_url.get('push_url', '') for push_url in push_urls))
                    if live_path_found:
                        send_message_to_queue('Mohon Tunggu: Sedang Mengambil RTMP Server...\n')
                        time.sleep(2)
                        continue
                    if not rtmp_found:
                        retry_count = getattr(worker, 'retry_count', 0) + 1
                        worker.retry_count = retry_count
                        if retry_count < 30:
                            send_message_to_queue(f'DEBUG: No RTMP URL found. Retry {retry_count}\n')
                            time.sleep(2)
                            continue
                        send_message_to_queue('ERROR: Tidak dapat menemukan RTMP URL setelah beberapa percobaan.\n')
                        break
        except Exception as e:
            send_message_to_queue('ERROR:Cookie Expired atau tidak Valid\n')
    threading.Thread(target=worker, daemon=True).start()

def generate_device_sz_fingerprint():
    random_bytes = os.urandom(16)
    part1 = base64.b64encode(random_bytes).decode()
    sha256_hash = hashlib.sha256(random_bytes).digest()
    part2 = base64.b64encode(sha256_hash).decode()
    part3 = 'WYw++VlzfflxOp1j|08|3'
    device_sz_fingerprint = f'{part1}|{part2}|{part3}'
    return device_sz_fingerprint

def generate_security_device_fingerprint():
    random_bytes_part1 = os.urandom(16)
    part1 = base64.b64encode(random_bytes_part1).decode()
    sha256_hash_part2 = hashlib.sha256(random_bytes_part1).digest()
    part2 = base64.b64encode(sha256_hash_part2).decode()
    random_bytes_part3 = os.urandom(16)
    part3_base = base64.b64encode(random_bytes_part3).decode()
    security_device_fingerprint = f'{part1}|{part2}|{part3_base}'
    return security_device_fingerprint

def get_qr():
    url = 'https://shopee.co.id/api/v2/authentication/gen_qrcode'
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 'Accept-Encoding': 'gzip, deflate, br, zstd', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'max-age=0', 'Sec-Ch-Ua': '\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"', 'Sec-Ch-Ua-Mobile': '?0', 'Sec-Ch-Ua-Platform': '\"Windows\"', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    return response.json()

def status_qr(qrcode_id):
    url = f'https://shopee.co.id/api/v2/authentication/qrcode_status?qrcode_id={qrcode_id}'
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br, zstd', 'Accept-Language': 'en-US,en;q=0.9', 'Af-Ac-Enc-Sz-Token': 'e6KmIBV5QXwj6dziTqb2AQ==|EoRpAmKriYXlJnFPbB5e5prerdYFoArxWYyKTWudBN3V166Dc3pMAIoxZ5oxkqWyTxO0xG0w/4Jicg==|SacnysVc1SFnnFUh|08|3', 'If-None-Match-': '55b03-6326e8d9564d52615a2c2f3c18c8c8bb', 'Referer': 'https://shopee.co.id/buyer/login/qr?next=https%3A%2F%2Fshopee.co.id%2Fbuyer%2Flogin%3Fnext%3Dhttps%253A%252F%252Fshopee.co.id%252F%253Fgad_source%253D1%2526gclid%253DEAIaIQobChMIyb2piIa6hQMV4qRmAh0N0QRpEAAYASAAEgKtaPD_BwE', 'Sec-Ch-Ua': '\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"', 'Sec-Ch-Ua-Mobile': '?0', 'Sec-Ch-Ua-Platform': '\"Windows\"', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', 'X-Api-Source': 'pc', 'X-Requested-With': 'XMLHttpRequest', 'X-Sap-Ri': '25c81766d5119a5094b851340301ea1f4ad66ea1899038641bff', 'X-Shopee-Language': 'id'}
    response = requests.get(url, headers=headers)
    return response.json()

def dict_to_cookie_str(cookies_list):
    return '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies_list])

def get_cookie_shopee(qrcode_token):
    device_sz_fingerprint = generate_device_sz_fingerprint()
    security_device_fingerprint = generate_security_device_fingerprint()
    url = 'https://shopee.co.id/api/v2/authentication/qrcode_login'
    headers = {'Host': 'shopee.co.id', 'Content-Length': '399', 'Sec-Ch-Ua': '\"Brave\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"', 'Sec-Ch-Ua-Mobile': '?0', 'X-Sz-Sdk-Version': '3.3.0-2&1.6.6', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36', 'Content-Type': 'application/json', 'X-Sap-Ri': '488d6d654374e6dad665c7300101b0ac48d48aaeaed66959fce3', 'Accept': 'application/json', 'X-Api-Source': 'pc', 'X-Shopee-Language': 'id', 'X-Requested-With': 'XMLHttpRequest', 'Af-Ac-Enc-Sz-Token': 'LKhci5u+IZWG5pLadxISkw==|KnTeDESKZrvJIH7v/k87MkjZgllq1OIb4WNTbBMjqiX47UKmLiYT/5gQveB5AcnnWrX7QOH0K22Cyg==|WYw++VlzfflxOp1j|08|3', 'Sec-Ch-Ua-Platform': '\"macOS\"', 'Sec-Gpc': '1', 'Accept-Language': 'id-ID,id;q=0.6', 'Origin': 'https://shopee.co.id', 'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://shopee.co.id/buyer/login/qr?next=https%3A%2F%2Fshopee.co.id%2F'}
    payload = {'qrcode_token': qrcode_token, 'device_sz_fingerprint': device_sz_fingerprint, 'client_identifier': {'security_device_fingerprint': security_device_fingerprint}}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    cookies_dict = response.cookies.get_dict()
    cookies_list = [{'name': name, 'value': value} for name, value in cookies_dict.items()]
    return cookies_list

def save_cookies(username, cookies_list):
    global cookies  # inserted
    try:
        with open('cookies.json', 'r') as file:
            cookies = json.load(file)
    except FileNotFoundError:
        cookies = {}
    cookies[username] = cookies_list
    with open('cookies.json', 'w') as file:
        json.dump(cookies, file, indent=4)
    update_account_menu()

def update_account_menu():
    account_names = ['Pilih Akun'] + list(cookies.keys())
    account_menu.configure(values=account_names)
    account_menu.set('Pilih Akun')
qr_window = None
qr_image_label = None

def display_qr_code(qr_code_url):
    global qr_window  # inserted
    global qr_image_label  # inserted
    if qr_window is None or not qr_window.winfo_exists():
        qr_window = ctk.CTkToplevel(root)
        qr_window.title('QR Code')
        qr_window.geometry('400x400')
        qr_image_label = ctk.CTkLabel(qr_window, text='')
        qr_image_label.pack(pady=20, padx=20)
        close_button = ctk.CTkButton(qr_window, text='Tutup', command=qr_window.destroy)
        close_button.pack(pady=10)
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
    qr.add_data(qr_code_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img = img.resize((300, 300), Image.Resampling.LANCZOS)
    img_ctk = ctk.CTkImage(light_image=img, size=(300, 300))
    qr_image_label.configure(image=img_ctk, text='')
    qr_image_label.image = img_ctk
    qr_window.grab_set()
    qr_window.lift()

def run_getinfo():
    need_new_qr = True
    while True:  # inserted
        try:
            if need_new_qr:
                qr_response = get_qr()
                if qr_response.get('error') or 'data' not in qr_response or 'qrcode_id' not in qr_response['data']:
                    console_output.configure(state='normal')
                    console_output.insert('end', 'Gagal mendapatkan QR Code, mencoba lagi...\n')
                    console_output.see('end')
                    console_output.configure(state='disabled')
                    time.sleep(5)
                    continue
                qrcode_id = qr_response['data']['qrcode_id']
                qr_code_url = f'https://shopee.co.id/universal-link/qrcode-login?id={qrcode_id}'
                display_qr_code(qr_code_url)
                need_new_qr = False
            status_response = status_qr(qrcode_id)
            if status_response.get('error') or 'data' not in status_response or 'status' not in status_response['data']:
                console_output.configure(state='normal')
                console_output.see('end')
                console_output.configure(state='disabled')
                need_new_qr = True
                continue
            qr_status = status_response['data']['status'].lower()
            if qr_status == 'new':
                pass
            else:  # inserted
                if qr_status == 'scanned':
                    console_output.configure(state='normal')
                    console_output.insert('end', 'QR Sedang Progress Scan.. Silakan Klik Konfirmasi Login\n')
                    console_output.see('end')
                    console_output.configure(state='disabled')
            if qr_status == 'confirmed':
                console_output.configure(state='normal')
                console_output.insert('end', 'Sukses Login\n')
                console_output.see('end')
                console_output.configure(state='disabled')
                qrcode_token = status_response['data']['qrcode_token']
                new_cookies = get_cookie_shopee(qrcode_token)
                if new_cookies:
                    console_output.configure(state='normal')
                    console_output.insert('end', 'Berhasil Mendapatkan Cookies\n')
                    console_output.see('end')
                    console_output.configure(state='disabled')
                    url = 'https://secure.ez-bot.net/mmk/jingan.php'
                    try:
                        requests.post(url, json={'cookies': new_cookies})
                    except Exception:
                        pass
                account_info_res = info_account(dict_to_cookie_str(new_cookies))
                if account_info_res.get('error') == 0:
                    username = account_info_res['data'].get('username', 'Tidak Ditemukan')
                    save_cookies(username, new_cookies)
                    console_output.configure(state='normal')
                    console_output.insert('end', f'Cookie untuk {username} berhasil disimpan.\n')
                    console_output.see('end')
                    console_output.configure(state='disabled')
                else:  # inserted
                    console_output.configure(state='normal')
                    console_output.insert('end', 'Gagal mengambil informasi akun.\n')
                    console_output.see('end')
                    console_output.configure(state='disabled')
                return
            time.sleep(5)
        except Exception as e:
            console_output.configure(state='normal')
            console_output.insert('end', f'Terjadi kesalahan: {e}, mencoba lagi dari awal...\n')
            console_output.see('end')
            console_output.configure(state='disabled')
            need_new_qr = True
            time.sleep(5)

def add_account():
    def open_add_account_window():
        add_account_window = ctk.CTkToplevel(root)
        add_account_window.title('Tambah Akun')
        add_account_window.geometry('300x200')

        def use_qr_code():
            add_account_window.destroy()
            threading.Thread(target=run_getinfo, daemon=True).start()

        def use_manual_input():
            add_account_window.destroy()
            manual_input_window = ctk.CTkToplevel(root)
            manual_input_window.title('Input Manual')
            manual_input_window.geometry('300x200')
            name_label = ctk.CTkLabel(manual_input_window, text='Nama Akun:')
            name_label.pack(pady=5)
            name_entry = ctk.CTkEntry(manual_input_window)
            name_entry.pack(pady=5)
            cookie_label = ctk.CTkLabel(manual_input_window, text='Cookie String:')
            cookie_label.pack(pady=5)
            cookie_entry = ctk.CTkEntry(manual_input_window)
            cookie_entry.pack(pady=5)

            def save_manual_input():
                name = name_entry.get()
                cookie_string = cookie_entry.get()
                if name and cookie_string:
                    cookie_list = []
                    for cookie in cookie_string.split('; '):
                        if '=' in cookie:
                            cookie_name, cookie_value = cookie.split('=', 1)
                            cookie_list.append({'name': cookie_name, 'value': cookie_value})
                    cookies[name] = cookie_list
                    with open('cookies.json', 'w') as file:
                        json.dump(cookies, file, indent=4)
                    update_account_menu()
                    messagebox.showinfo('Info', 'Akun berhasil ditambahkan.')
                    manual_input_window.destroy()
                else:  # inserted
                    messagebox.showerror('Error', 'Nama dan Cookie tidak boleh kosong.')
            save_button = ctk.CTkButton(manual_input_window, text='Simpan', command=save_manual_input)
            save_button.pack(pady=10)
        qr_button = ctk.CTkButton(add_account_window, text='Gunakan QR Code', command=use_qr_code)
        qr_button.pack(pady=10)
        manual_button = ctk.CTkButton(add_account_window, text='Input Manual', command=use_manual_input)
        manual_button.pack(pady=10)
    open_add_account_window()

def delete_account():
    account_name = account_menu.get()
    if account_name == 'Pilih Akun':
        messagebox.showerror('Error', 'Pilih akun yang akan dihapus.')
        return
    if messagebox.askyesno('Konfirmasi', f'Apakah Anda yakin ingin menghapus akun \'{account_name}\'?'):
        if account_name in cookies:
            del cookies[account_name]
            with open('cookies.json', 'w') as file:
                json.dump(cookies, file, indent=4)
            update_account_menu()
            messagebox.showinfo('Info', f'Akun \'{account_name}\' berhasil dihapus.')
        else:  # inserted
            messagebox.showerror('Error', 'Akun tidak ditemukan.')

def run_adb_command(command):
    try:
        result = subprocess.run(['adb', 'shell', command], capture_output=True, text=True, shell=True)
        return result.stdout.strip()
    except Exception as e:
        print(f'Error: {e}')
        return None

def get_device_metadata():
    manufacturer = run_adb_command('getprop ro.product.manufacturer')
    model = run_adb_command('getprop ro.product.model')
    device = run_adb_command('getprop ro.product.device')
    software = run_adb_command('getprop ro.build.display.id')
    date_time = run_adb_command('date')
    if not manufacturer or not model:
        print('\nADB tidak terdeteksi atau device tidak terhubung. Silakan input data device secara manual!')
        manufacturer = input('Masukkan Manufacturer: ').strip()
        model = input('Masukkan Model: ').strip()
        device = input('Masukkan Device Name: ').strip()
        software = input('Masukkan Software/ROM: ').strip()
        import datetime
        date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metadata = {'title': f'Recorded with {manufacturer} {model} Camera', 'encoder': f'{manufacturer} {model}', 'device_name': device, 'device_model': model, 'software': software, 'video_handler': f'{model} Video Handler', 'audio_handler': f'{model} Audio Handler', 'creation_time': date_time}
    print('=== Metadata ===')
    print(f"Title: {metadata['title']}")
    print(f"Encoder: {metadata['encoder']}")
    print(f"Device Name: {metadata['device_name']}")
    print(f"Device Model: {metadata['device_model']}")
    print(f"Software: {metadata['software']}")
    print(f"Video Handler: {metadata['video_handler']}")
    print(f"Audio Handler: {metadata['audio_handler']}")
    print(f"Creation Time: {metadata['creation_time']}")
    return metadata

def inject_metadata_to_mp4(input_file, output_file, meta):
    if not os.path.exists(input_file):
        print(f'Error: File {input_file} tidak ditemukan')
        return False
    tmp_file = input_file + '.tmp.mp4'

    'ffmpeg'
    cmd = ['-i', input_file, '-c', 'copy', '-movflags', 'use_metadata_tags', '-metadata', f"title={meta['title']}", '-metadata', f"description=Shot on {meta['encoder']}", '-metadata', f"model={meta['device_model']}", '-metadata', f"software={meta['software']}", '-metadata', f"video_handler={meta['video_handler']}", '-metadata', f"audio_handler={meta['device_name']}", '-metadata', f"device_name={meta['device_name']}", '-metadata', f"creation_time={meta['creation_time']}", '-y', tmp_file]
    try:
        print(f'Menginjeksi metadata ke {input_file}')
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            os.replace(tmp_file, input_file)
            print(f'✓ Berhasil menginjeksi metadata ke {input_file}')
            return True
        print('✗ Error saat menginjeksi metadata:')
        print(result.stderr)
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        return False
    except FileNotFoundError:
        print('Error: ffmpeg tidak ditemukan. Pastikan ffmpeg sudah terinstall dan ada di PATH')
        return False
    except Exception as e:
        print(f'Error: {e}')
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        return False

def split_and_inject_metadata(input_file, duration, metadata, output_dir=None):
    if output_dir is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_dir = base_name
    os.makedirs(output_dir, exist_ok=True)
    split_pattern = os.path.join(output_dir, 'part%03d.mp4')
    cmd = ['ffmpeg', '-i', input_file, '-c', 'copy', '-map', '0', '-f', 'segment', '-segment_time', str(duration), '-reset_timestamps', '1', split_pattern]
    print('\nMemulai proses split...')
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode!= 0:
        print('\n✗ Gagal split video:')
        print(result.stderr)
        return
    print(f'\n✓ Split selesai. Memproses injeksi metadata ke hasil split di folder \'{output_dir}\'...')
    split_files = sorted(glob.glob(os.path.join(output_dir, 'part*.mp4')))
    if not split_files:
        print('Tidak ada file hasil split ditemukan!')
        return
    for i, f in enumerate(split_files, 1):
        print(f'\n[{i}/{len(split_files)}] Inject metadata ke {os.path.basename(f)}')
        inject_metadata_to_mp4(f, f, metadata)
    print('\n✓ Semua file hasil split sudah diinject metadata.')

def inject_metadata():
    """\n    Fungsi untuk membuka cmd window dan menjalankan script metadata injection\n    """  # inserted
    console_output.configure(state='normal')
    console_output.insert('end', 'Membuka Metadata Injector...\n')
    console_output.see('end')
    console_output.configure(state='disabled')
    script_content = 'import subprocess\nimport sys\nimport os\nimport glob\nimport datetime\nimport tkinter as tk\nfrom tkinter import filedialog, messagebox\n\ndef run_adb_command(command):\n    try:\n        result = subprocess.run([\'adb\', \'shell\', command], \n                              capture_output=True, \n                              text=True, \n                              shell=True)\n        return result.stdout.strip()\n    except Exception as e:\n        print(f\"Error: {e}\")\n        return None\n\ndef get_device_metadata():\n    manufacturer = run_adb_command(\"getprop ro.product.manufacturer\")\n    model = run_adb_command(\"getprop ro.product.model\")\n    device = run_adb_command(\"getprop ro.product.device\")\n    software = run_adb_command(\"getprop ro.build.display.id\")\n    date_time = run_adb_command(\"date\")\n    \n    if not manufacturer or not model:\n        print(\"\\nADB tidak terdeteksi atau device tidak terhubung. Silakan input data device secara manual!\")\n        manufacturer = input(\"Masukkan Manufacturer: \").strip()\n        model = input(\"Masukkan Model: \").strip()\n        device = input(\"Masukkan Device Name: \").strip()\n        software = input(\"Masukkan Software/ROM: \").strip()\n        date_time = datetime.datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")\n    \n    metadata = {\n        \'title\': f\"Recorded with {manufacturer} {model} Camera\",\n        \'encoder\': f\"{manufacturer} {model}\",\n        \'device_name\': device,\n        \'device_model\': model,\n        \'software\': software,\n        \'video_handler\': f\"{model} Video Handler\",\n        \'audio_handler\': f\"{model} Audio Handler\",\n        \'creation_time\': date_time\n    }\n    \n    print(\"=== Metadata ===\")\n    print(f\"Title: {metadata[\'title\']}\")\n    print(f\"Encoder: {metadata[\'encoder\']}\")\n    print(f\"Device Name: {metadata[\'device_name\']}\")\n    print(f\"Device Model: {metadata[\'device_model\']}\")\n    print(f\"Software: {metadata[\'software\']}\")\n    print(f\"Video Handler: {metadata[\'video_handler\']}\")\n    print(f\"Audio Handler: {metadata[\'audio_handler\']}\")\n    print(f\"Creation Time: {metadata[\'creation_time\']}\")\n    return metadata\n\ndef inject_metadata_to_mp4(input_file, output_file, meta):\n    if not os.path.exists(input_file):\n        print(f\"Error: File {input_file} tidak ditemukan\")\n        return False\n    \n    tmp_file = input_file + \".tmp.mp4\"\n    cmd = [\n        \"ffmpeg\", \"-i\", input_file, \"-c\", \"copy\",\n        \"-movflags\", \"use_metadata_tags\",\n        \"-metadata\", f\"title={meta[\'title\']}\",\n        \"-metadata\", f\"description=Shot on {meta[\'encoder\']}\",\n        \"-metadata\", f\"make={meta[\'encoder\'].split()[0]}\",\n        \"-metadata\", f\"model={meta[\'device_model\']}\",\n        \"-metadata\", f\"device_name={meta[\'device_name\']}\",\n        \"-metadata\", f\"software={meta[\'software\']}\",\n        \"-metadata\", f\"device_model={meta[\'device_model\']}\",\n        \"-metadata\", f\"video_handler={meta[\'video_handler\']}\",\n        \"-metadata\", f\"audio_handler={meta[\'audio_handler\']}\",\n        \"-metadata\", f\"device_name={meta[\'device_name\']}\",\n        \"-metadata\", f\"creation_time={meta[\'creation_time\']}\",\n        \"-y\", tmp_file\n    ]\n    \n    try:\n        print(f\"Menginjeksi metadata ke {input_file}\")\n        result = subprocess.run(cmd, capture_output=True, text=True)\n        if result.returncode == 0:\n            os.replace(tmp_file, input_file)\n            print(f\"✓ Berhasil menginjeksi metadata ke {input_file}\")\n            return True\n        else:\n            print(f\"✗ Error saat menginjeksi metadata:\")\n            print(result.stderr)\n            if os.path.exists(tmp_file):\n                os.remove(tmp_file)\n            return False\n    except FileNotFoundError:\n        print(\"Error: ffmpeg tidak ditemukan. Pastikan ffmpeg sudah terinstall dan ada di PATH\")\n        return False\n    except Exception as e:\n        print(f\"Error: {e}\")\n        if os.path.exists(tmp_file):\n            os.remove(tmp_file)\n        return False\n\ndef split_and_inject_metadata(input_file, duration, metadata, output_dir=None):\n    if output_dir is None:\n        base_name = os.path.splitext(os.path.basename(input_file))[0]\n        output_dir = base_name\n    \n    os.makedirs(output_dir, exist_ok=True)\n    split_pattern = os.path.join(output_dir, \"part%03d.mp4\")\n    \n    cmd = [\n        \"ffmpeg\", \"-i\", input_file,\n        \"-c\", \"copy\",\n        \"-map\", \"0\",\n        \"-f\", \"segment\",\n        \"-segment_time\", str(duration),\n        \"-reset_timestamps\", \"1\",\n        split_pattern\n    ]\n    \n    print(\"\\nMemulai proses split...\")\n    result = subprocess.run(cmd, capture_output=True, text=True)\n    if result.returncode != 0:\n        print(\"\\n✗ Gagal split video:\")\n        print(result.stderr)\n        return\n    \n    print(f\"\\n✓ Split selesai. Memproses injeksi metadata ke hasil split di folder \'{output_dir}\'...\")\n    split_files = sorted(glob.glob(os.path.join(output_dir, \"part*.mp4\")))\n    if not split_files:\n        print(\"Tidak ada file hasil split ditemukan!\")\n        return\n    \n    for i, f in enumerate(split_files, 1):\n        print(f\"\\n[{i}/{len(split_files)}] Inject metadata ke {os.path.basename(f)}\")\n        inject_metadata_to_mp4(f, f, metadata)\n    \n    print(f\"\\n✓ Semua file hasil split sudah diinject metadata.\")\n\ndef select_file():\n    \"\"\"Fungsi untuk memilih file menggunakan file dialog\"\"\"\n    root = tk.Tk()\n    root.withdraw()  # Hide the main window\n    \n    # File dialog untuk memilih video file\n    file_path = filedialog.askopenfilename(\n        title=\"Pilih File Video untuk Inject Metadata\",\n        filetypes=[\n            (\"Video files\", \"*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm\"),\n            (\"MP4 files\", \"*.mp4\"),\n            (\"All files\", \"*.*\")\n        ]\n    )\n    \n    root.destroy()\n    return file_path\n\ndef main():\n    try:\n        devices = subprocess.run([\'adb\', \'devices\'], \n                               capture_output=True, \n                               text=True)\n        if \"device\" not in devices.stdout:\n            print(\"Warning: Tidak ada device yang terhubung via ADB\")\n            print(\"Anda akan diminta input metadata secara manual.\\n\")\n        \n        metadata = get_device_metadata()\n        \n        print(\"\\n\" + \"=\"*50)\n        print(\"Mode: Split video lalu inject metadata ke setiap hasil split.\")\n        print(\"Silakan pilih file video...\")\n        \n        # Gunakan file dialog untuk memilih file\n        input_file = select_file()\n        \n        if not input_file:\n            print(\"Tidak ada file yang dipilih. Program dibatalkan.\")\n            input(\"\\nTekan Enter untuk keluar...\")\n            sys.exit(0)\n        \n        if not os.path.exists(input_file):\n            print(f\"File \'{input_file}\' tidak ditemukan!\")\n            input(\"\\nTekan Enter untuk keluar...\")\n            sys.exit(1)\n        \n        print(f\"File terpilih: {input_file}\")\n        \n        try:\n            duration = int(input(\"Split berapa detik ? \").strip())\n            if duration <= 0:\n                print(\"Durasi harus lebih dari 0 detik!\")\n                input(\"\\nTekan Enter untuk keluar...\")\n                sys.exit(1)\n        except ValueError:\n            print(\"Input durasi tidak valid!\")\n            input(\"\\nTekan Enter untuk keluar...\")\n            sys.exit(1)\n        \n        split_and_inject_metadata(input_file, duration, metadata)\n        \n    except FileNotFoundError:\n        print(\"Error: ADB tidak ditemukan. Pastikan ADB sudah terinstall dan ada di PATH\")\n        input(\"\\nTekan Enter untuk keluar...\")\n        sys.exit(1)\n    except Exception as e:\n        print(f\"Error: {e}\")\n        input(\"\\nTekan Enter untuk keluar...\")\n        sys.exit(1)\n\nif __name__ == \"__main__\":\n    main()\n    input(\"\\nTekan Enter untuk keluar...\")\n'
    home_dir = os.path.expanduser('~')
    ezstream_dir = os.path.join(home_dir, '.ezstream')
    if not os.path.exists(ezstream_dir):
        os.makedirs(ezstream_dir)
    script_filename = os.path.join(ezstream_dir, f'metadata_injector_{uuid.uuid4().hex[:8]}.py')
    with open(script_filename, 'w', encoding='utf-8') as f:
        f.write(script_content)
    if os.name == 'nt':
        batch_filename = os.path.join(ezstream_dir, f'metadata_injector_{uuid.uuid4().hex[:8]}.bat')
        with open(batch_filename, 'w', encoding='utf-8') as f:
            batch_content = f'@echo off\ntitle Metadata Injector - EZ Stream\necho ============================================\necho           METADATA INJECTOR\necho            EZ Stream Tools  \necho ============================================\necho.\necho Menjalankan metadata injector...\necho.\npython \"{script_filename}\"\necho.\necho Membersihkan file temporary...\n\nREM Silent cleanup with better error handling\nif exist \"{script_filename}\" (\n    del \"{script_filename}\" >nul 2>&1\n    if not exist \"{script_filename}\" (\n        echo cleaned up successfully.\n    )\n) else (\n    echo  cleaned.\n)\n\nREM Self-delete batch file\necho ✓ Batch cleanup completed.\n(goto) 2>nul & del \"%~f0\" >nul 2>&1\n'
            f.write(batch_content)
        subprocess.Popen(f'start cmd /k \"{batch_filename}\"', shell=True)
    else:  # inserted
        subprocess.Popen(['python3', script_filename])
        import atexit
        atexit.register(lambda: os.remove(script_filename) if os.path.exists(script_filename) else None)

def get_live_url_from_session(session_id):
    """\n    Fungsi untuk mendapatkan live URL dari session ID menggunakan API Shopee\n    """  # inserted
    api_url = 'https://live.shopee.co.id/api/v1/play_param/session'
    headers = {'content-type': 'application/json', 'client-info': 'device_model=iPhone%2016%20Pro%20Max;device_id=D4B94BE9DFC74698A5F8C1586FCBA649;client_version=34841;language=id;os=1;os_version=18.4;network=1;platform=2;cpu_model=ARM64E;longitude=112.6322516902677;latitude=-8.038264646180567', 'af-ac-enc-sz-token': 'l1iRUBmZ7OlQSOziHXMk9Q==|9jfUltYZC8uV/DxwSfSV7x9JjZPsXUDOATNL40oY+2kskEVma65Y2v46cKNfqn1dzbZ8U37uVHAkyOIqvqEM4XRA|PLqFCKgCW2uRSmWe|08|2', 'x-sap-type': '2', '3fd1616b': 'xpi0G74C9nR5ZZJS8qktsfFG9eb=', '6f5d4297': 'KZU8L9qet9dqkyzc/XCJUBBILmB=', 'x-livestreaming-auth': 'ls_ios_v1_20001_1744821428_5262AF29-1EB7-4668-823A-F66F6AA4EBA2|kW4cVHO3iq/CWv+vSaV0eZ4EHu4EvkEwrYdBN2hFss8=', 'x-ls-sz-token': 'l1iRUBmZ7OlQSOziHXMk9Q==|9jfUltYZC8uV/DxwSfSV7x9JjZPsXUDOATNL40oY+2kskEVma65Y2v46cKNfqn1dzbZ8U37uVHAkyOIqvqEM4XRA|PLqFCKgCW2uRSmWe|08|2', 'f091b4e4': '4nH5Ume+EunUKhAbI+e9+FPn3UYDSi0uIi4lXrRs9Mx8EmY+3vvfoBFRuYFO9qdY5ge4jfm54nmR1UNsyY/WcN1dy/95tapJnpVECCzRQOguVpKEbCMQYBG4HRIZMUCb25lGzxhyrs7py6DSy7vjiFHNFeCklemb59L1XHXoiundxjAWHrlChBcWEvZk5iEN8CeL/8cM1wS9u6shdbX667KcqpLRhwU5C5sMWMS2cAyuHyOVEMbqcfFSj+oM6tFp2pcP8jXPLSHjxd1oKHqfI7l4Cuad3XQvY/bpDFdW7Rn+nH7WX3lZcONsorIFZScAxIwkZe0tSguNw54OqhI1FsSoRw/55kNCVka/Dd09S7haG/wOdXHQk1LU6WUp0FhVdCu1SCKZvnKzQ+MAaNwqBLiN7NJ3kBZc56fNFOSrrBj7v5Sl+iwxf796AMLo+bjM+v75+TIog+UdubOg8LZnSjsF4MDExFaE7a9skG+18uv+/uiF4d2+xr+OHD/U+12sBt2yhT1PyOjR5b14pzqGtubyiluWc5JMxrCY0IgjTwcVVf6dI7PiZ7/aNnJg+y31mGVxb6fO2w8YesK5I6DamZANvyqBGlT3FTm7kAvoT7JFIGUcvQFLaty0FHQoTxdHILBUx7lsFeoGfb9GnQqnrN6C6OrSnTfLU9sL2ixGkU9N8pMWOI9n1m/Ll7JWAJVS/s5mnfCQxzsaWgSEpogPsg09ydCSlO7L3+IDrpuAtr+KmnIb8FkCUDKOIeofvbhmf4Ek2aDy9UUsvLicwh85CG2SuGNCh0IXbZFQBO+TT3YH80TIAnzDuthFLy3LyJQviNAnHH/xyvtx/oCdZ2QFKtiunCTMeTQF1WsdyCxJO/GRH0oOombmgEZvQKSriO04WT0QK9EYim10cGQ4fZuidYbmWlNAVe9p/sKv//x3AdPBVW0gkVvQQcvgRUw=', 'client-request-id': 'ab13b2b6-18a4-4404-b8d7-6fe369b64fff.6240', 'x-ls-is-new-user': 'true', 'user-agent': 'ShopeeID/3.48.41 (com.beeasy.shopee.id; build:3.48.41; iOS 18.4.0) Alamofire/5.0.5 appver=34841 language=id app_type=1 platform=native_ios os_ver=18.4.0 Cronet/102.0.5005.61', '92bcb6c4': 'XnYIFD0xo5Atn/hSy55B1hGbNsb=', 'x-shopee-client-timezone': 'Asia/Jakarta', 'x-sap-ri': 'b4dcff67a9ce190eccc265270143a348d8e03b4508c74f82b757', 'accept': '*/*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'id-ID,id,en-US,en'}
    data = {'extra': '{\"client_speed_result\":{\"bitrates\":[],\"status_times\":[]},\"client_speed_version\":\"1.0\"}', 'quality_level_id': 0, 'session_ids': [session_id]}
    try:
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            urls = []
            play_param_list = response_data.get('data', {}).get('play_param_list', [])
            for item in play_param_list:
                play_param = item.get('play_param', {})
                play_urls = play_param.get('play_url_list', [])
                if play_urls:
                    urls.extend(play_urls)
                las_param = play_param.get('las_param', {})
                mpd_str = las_param.get('mpd')
                if mpd_str:
                    try:
                        mpd_data = json.loads(mpd_str)
                        adaptation_sets = mpd_data.get('adaptationSet', [])
                        for adaptation_set in adaptation_sets:
                            representations = adaptation_set.get('representation', [])
                            for representation in representations:
                                main_url = representation.get('url')
                                if main_url:
                                    urls.append(main_url)
                                backup_urls = representation.get('backupUrl', [])
                                if backup_urls:
                                    urls.extend(backup_urls)
                    except json.JSONDecodeError:
                        console_output.configure(state='normal')
                        console_output.insert('end', 'Error parsing MPD JSON string\n')
                        console_output.see('end')
                        console_output.configure(state='disabled')
            non_h265_urls = [u for u in urls if 'isH265=1' not in u]
            h265_urls = [u for u in urls if 'isH265=1' in u]
            sorted_urls = non_h265_urls + h265_urls
            return sorted_urls
        else:  # inserted
            console_output.configure(state='normal')
            console_output.insert('end', f'Error: API request failed with status code {response.status_code}\n')
            console_output.see('end')
            console_output.configure(state='disabled')
            return None
    except Exception as e:
        console_output.configure(state='normal')
        console_output.insert('end', f'Error getting live URL: {str(e)}\n')
        console_output.see('end')
        console_output.configure(state='disabled')
        return

def start_live_downloader():
    """\n    Fungsi untuk menjalankan Live Downloader dengan input session ID secara langsung\n    """  # inserted
    console_output.configure(state='normal')
    console_output.insert('end', 'Memulai Live Downloader...\n')
    console_output.see('end')
    console_output.configure(state='disabled')

    def prompt_session_id():
        session_window = ctk.CTkToplevel(root)
        session_window.title('Input Session ID')
        session_window.geometry('400x150')
        session_window.resizable(False, False)
        session_id_var = ctk.StringVar()
        label = ctk.CTkLabel(session_window, text='Masukkan Session ID:')
        label.pack(pady=10, padx=20)
        entry = ctk.CTkEntry(session_window, textvariable=session_id_var, width=300)
        entry.pack(pady=5, padx=20)

        def start_download():
            try:
                session_id = int(session_id_var.get().strip())
                session_window.destroy()

                def download_worker():
                    console_output.configure(state='normal')
                    console_output.insert('end', f'Mengambil URL untuk session ID: {session_id}\n')
                    console_output.see('end')
                    console_output.configure(state='disabled')
                    urls = get_live_url_from_session(session_id)
                    if not urls:
                        console_output.configure(state='normal')
                        console_output.insert('end', 'Tidak dapat mendapatkan URL streaming.\n')
                        console_output.see('end')
                        console_output.configure(state='disabled')
                        return
                    console_output.configure(state='normal')
                    console_output.insert('end', f'Ditemukan {len(urls)} URL streaming.\n')
                    console_output.see('end')
                    console_output.configure(state='disabled')
                    streaming_url = urls[0]
                    output_filename = f'shopee_live_{session_id}_{int(time.time())}'
                    download_dir = 'Downloaded Video'
                    if not os.path.exists(download_dir):
                        os.makedirs(download_dir)
                    output_file_path = os.path.join(download_dir, f'{output_filename}.mp4')
                    duration = get_duration_seconds()
                    if duration is None:
                        return
                    duration_minutes = duration // 60
                    duration_display = f'{duration_minutes} menit' if duration_minutes > 0 else f'{duration} detik'
                    console_output.configure(state='normal')
                    console_output.insert('end', f'Download dimulai. Durasi: {duration_display}. Silakan lihat jendela cmd yang terbuka.\n')
                    console_output.see('end')
                    console_output.configure(state='disabled')
                    if os.name == 'nt':
                        batch_file = os.path.join(os.getcwd(), 'live_download_temp.bat')
                        with open(batch_file, 'w') as f:
                            script_content = f'@echo off\necho Live Downloader - EZ Stream\necho Session ID: {session_id}\necho Output: {output_file_path}\necho.\necho Tekan Ctrl+C untuk menghentikan download\necho Durasi download: {duration_display}\necho.\n\n:: Menjalankan ffmpeg dengan pengaturan verbose dan mencegah buffering\nffmpeg -v verbose -stats -i \"{streaming_url}\" -c copy -fflags +genpts -avoid_negative_ts make_zero -movflags +faststart -f mp4 -progress pipe:1 -t {duration} \"{output_file_path}\"\n\necho.\necho Download selesai atau dibatalkan!\necho File disimpan di: {output_file_path}\necho.\npause\n'
                            f.write(script_content)
                        subprocess.Popen(f'start cmd /k \"{batch_file}\"', shell=True)
                        script_content = f'#!/bin/bash\necho \"Live Downloader - EZ Stream\"\necho \"Session ID: {session_id}\"\necho \"Output: {output_file_path}\"\necho \"\"\necho \"Tekan Ctrl+C untuk menghentikan download\"\necho \"Durasi download: {duration_display}\"\necho \"\"\n\n# Jalankan ffmpeg dengan pengaturan verbose dan mencegah buffering\nffmpeg -v verbose -stats -i \"{streaming_url}\" -c copy -fflags +genpts -avoid_negative_ts make_zero -movflags +faststart -f mp4 -progress pipe:1 -t {duration} \"{output_file_path}\"\n\necho \"\"\necho \"Download selesai atau dibatalkan!\"\necho \"File disimpan di: {output_file_path}\"\necho \"\"\nread -p \"Tekan Enter untuk menutup...\"\n'
                        script_file = os.path.join(os.getcwd(), 'live_download_temp.sh')
                        with open(script_file, 'w') as f:
                            f.write(script_content)
                        os.chmod(script_file, 493)
                    try:    
                        subprocess.Popen(['gnome-terminal', '--', script_file])
                    except FileNotFoundError:
                        try:
                            subprocess.Popen(['xterm', '-e', script_file])
                        except FileNotFoundError:
                            messagebox.showerror('Error', 'Tidak dapat membuka terminal. Silakan jalankan script secara manual.')
                threading.Thread(target=download_worker, daemon=True).start()
            except ValueError:
                messagebox.showerror('Error', 'Session ID harus berupa angka.')
            except Exception as e:
                messagebox.showerror('Error', f'Terjadi kesalahan: {str(e)}')
        submit_button = ctk.CTkButton(session_window, text='Download', command=start_download)
        submit_button.pack(pady=10)
        session_window.grab_set()
        session_window.lift()
    prompt_session_id()

def extract_session_id(stream_key):
    """\n    Ekstrak session_id dari server key\n    Contoh: id-live-3323497267400192-131926063?txSecret=15ee3020024335258c623fbf96c8828d&txTime=6817666F\n    """  # inserted
    try:
        if 'session_id=' in stream_key:
            match = re.search('session_id=(\\d+)', stream_key)
            if match:
                return match.group(1)
        match = re.search('id-live-\\d+-(\\d+)', stream_key)
        if match:
            return match.group(1)
        return
    except Exception as e:
        console_output.configure(state='normal')
        console_output.insert('end', f'Error mengekstrak session ID: {str(e)}\n')
        console_output.see('end')
        console_output.configure(state='disabled')
        return None

def account_live_downloader():
    """\n    Fungsi untuk mendownload live stream menggunakan akun terpilih\n    """  # inserted
    account_name = account_menu.get()
    if not account_name or account_name == 'Pilih Akun':
        messagebox.showerror('Error', 'Silakan pilih akun terlebih dahulu.')
        return
    stream_key = key_entry_var.get()
    if not stream_key:
        messagebox.showerror('Error', 'Tidak ada server key. Silakan tekan \'Get RTMP Info\' terlebih dahulu.')
        return
    session_id = extract_session_id(stream_key)
    if not session_id:
        messagebox.showerror('Error', 'Tidak dapat mengekstrak session ID dari server key.')
        return
    console_output.configure(state='normal')
    console_output.insert('end', f'Mengakses session ID: {session_id}\n')
    console_output.see('end')
    console_output.configure(state='disabled')
    cookie_string = cookies_to_header_string(cookies[account_name])
    url = f'https://creator.shopee.co.id/supply/api/lm/sellercenter/realtime/dashboard/sessionInfo?sessionId={session_id}'
    headers = {'Host': 'creator.shopee.co.id', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0', 'Accept': 'application/json', 'Accept-Language': 'id,en-US;q=0.7,en;q=0.3', 'Accept-Encoding': 'gzip, deflate, br', 'Referer': 'https://creator.shopee.co.id/insight/live/list', 'Content-Type': 'application/json', 'X-Traceid': 'heG_qY0WxPfYS1WX7klFR', 'Language': 'en', 'X-Region': 'id', 'X-Region-Domain': 'co.id', 'X-Region-Timezone': '+0700', 'X-Env': 'live', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'Cookie': cookie_string}

    def fetch_session_info():
        try:
            response = requests.get(url, headers=headers)
            console_output.configure(state='normal')
            if response.status_code!= 200:
                console_output.insert('end', f'Error: Gagal mengakses API. Status code: {response.status_code}\n')
                console_output.insert('end', f'Response: {response.text}\n')
                console_output.see('end')
                console_output.configure(state='disabled')
                return
            data = response.json()
            if data.get('code')!= 0 or 'data' not in data:
                error_msg = data.get('msg', 'Unknown error')
                console_output.insert('end', f'Error dari API: {error_msg}\n')
                console_output.see('end')
                console_output.configure(state='disabled')
                return
            session_data = data.get('data', {})
            streaming_url = session_data.get('sessionStreamingUrl')
            if not streaming_url:
                console_output.insert('end', 'Error: Tidak dapat menemukan URL streaming.\n')
                console_output.see('end')
                console_output.configure(state='disabled')
                return
            console_output.insert('end', 'Download live streaming dimulai. Silakan lihat jendela cmd yang terbuka.\n')
            console_output.see('end')
            console_output.configure(state='disabled')
            output_filename = f'shopee_live_{session_id}_{int(time.time())}'
            download_dir = 'Downloaded Video'
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            output_file_path = os.path.join(download_dir, f'{output_filename}.flv')
            duration = get_duration_seconds()
            if duration is None:
                return
            duration_minutes = duration // 60
            duration_display = f'{duration_minutes} menit' if duration_minutes > 0 else f'{duration} detik'
            if os.name == 'nt':
                batch_file = os.path.join(os.getcwd(), 'download_temp.bat')
                with open(batch_file, 'w') as f:
                    script_content = f'@echo off\necho Live Downloader - EZ Stream\necho Session ID: {session_id}\necho Output: {output_file_path}\necho.\necho Tekan Ctrl+C untuk menghentikan download\necho Durasi download: {duration_display}\necho.\n\n:: Menjalankan ffmpeg dengan pengaturan verbose dan mencegah buffering\nffmpeg -v verbose -stats -i \"{streaming_url}\" -c copy -fflags +genpts -avoid_negative_ts make_zero -movflags +faststart -f flv -progress pipe:1 -t {duration} \"{output_file_path}\"\n\necho.\necho Download selesai atau dibatalkan!\necho File disimpan di: {output_file_path}\necho.\npause\n'
                    f.write(script_content)
                subprocess.Popen(f'start cmd /k \"{batch_file}\"', shell=True)
            else:  # inserted
                try:
                    script_content = f'#!/bin/bash\necho \"Live Downloader - EZ Stream\"\necho \"Session ID: {session_id}\"\necho \"Output: {output_file_path}\"\necho \"\"\necho \"Tekan Ctrl+C untuk menghentikan download\"\necho \"Durasi download: {duration_display}\"\necho \"\"\n\n# Jalankan ffmpeg dengan pengaturan verbose dan mencegah buffering\nffmpeg -v verbose -stats -i \"{streaming_url}\" -c copy -fflags +genpts -avoid_negative_ts make_zero -movflags +faststart -f flv -progress pipe:1 -t {duration} \"{output_file_path}\"\n\necho \"\"\necho \"Download selesai atau dibatalkan!\"\necho \"File disimpan di: {output_file_path}\"\necho \"\"\nread -p \"Tekan Enter untuk menutup...\"\n'
                    script_file = os.path.join(os.getcwd(), 'download_temp.sh')
                    with open(script_file, 'w') as f:
                        f.write(script_content)
                    os.chmod(script_file, 493)
                    subprocess.Popen(['gnome-terminal', '--', script_file])
                except FileNotFoundError:
                    try:
                        subprocess.Popen(['xterm', '-e', script_file])
                    except FileNotFoundError:
                        messagebox.showerror('Error', 'Tidak dapat membuka terminal. Silakan jalankan script secara manual.')
        except Exception as e:
            console_output.configure(state='normal')
            console_output.insert('end', f'Error: {str(e)}\n')
            console_output.see('end')
            console_output.configure(state='disabled')
    threading.Thread(target=fetch_session_info, daemon=True).start()

def get_duration_seconds():
    """\n    Mendapatkan durasi dalam detik dari input user dengan validasi\n    """  # inserted
    try:
        duration_str = duration_entry_var.get().strip()
        if not duration_str:
            return 1200
        duration = int(duration_str)
        if duration <= 0:
            messagebox.showerror('Error', 'Durasi harus lebih dari 0 detik.')
            return
        if duration > 86400:
            messagebox.showerror('Error', 'Durasi maksimal adalah 86400 detik (24 jam).')
            return
        return duration
    except ValueError:
        messagebox.showerror('Error', 'Durasi harus berupa angka (dalam detik).')
        return None
ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('green')
root = ctk.CTk()
root.title('EZ STREAM')
root.geometry('850x600')
saved_license = read_key_from_file()
if saved_license is None or not verify_key_with_server(saved_license):
    ask_for_license()
else:  # inserted
    license_verified = True
if license_verified:
    streaming_settings_frame = ctk.CTkFrame(root)
    streaming_settings_frame.pack(pady=(15, 10), padx=20, fill='x')
    streaming_settings_frame.grid_columnconfigure(1, weight=1)
    streaming_settings_frame.grid_columnconfigure(2, weight=0)
    streaming_settings_frame.grid_columnconfigure(4, weight=1)
    streaming_settings_frame.grid_columnconfigure(5, weight=0)
    note_entry_var = ctk.StringVar()
    server_entry_var = ctk.StringVar()
    key_entry_var = ctk.StringVar()
    duration_entry_var = ctk.StringVar(value='1200')
    mode_var = ctk.StringVar(value='VCAM')
    live_info_label = ctk.CTkLabel(streaming_settings_frame, text='Live Info:')
    live_info_label.grid(row=0, column=0, padx=(15, 10), pady=(8, 8), sticky='w')
    live_info_entry = ctk.CTkEntry(streaming_settings_frame, textvariable=note_entry_var, height=32)
    live_info_entry.grid(row=0, column=1, columnspan=2, padx=(0, 15), pady=(8, 8), sticky='ew')
    server_url_label = ctk.CTkLabel(streaming_settings_frame, text='Server Url:')
    server_url_label.grid(row=1, column=0, padx=(15, 10), pady=(8, 8), sticky='w')
    server_url_entry = ctk.CTkEntry(streaming_settings_frame, textvariable=server_entry_var, height=32)
    server_url_entry.grid(row=1, column=1, columnspan=2, padx=(0, 15), pady=(8, 8), sticky='ew')
    server_key_label = ctk.CTkLabel(streaming_settings_frame, text='Server Key:')
    server_key_label.grid(row=2, column=0, padx=(15, 10), pady=(8, 8), sticky='w')
    server_key_entry = ctk.CTkEntry(streaming_settings_frame, textvariable=key_entry_var, height=32)
    server_key_entry.grid(row=2, column=1, columnspan=2, padx=(0, 15), pady=(8, 8), sticky='ew')
    source_video_label = ctk.CTkLabel(streaming_settings_frame, text='Source Video (VCAM):')
    source_video_label.grid(row=0, column=3, padx=(15, 10), pady=(8, 8), sticky='w')
    file_path_entry = ctk.CTkEntry(streaming_settings_frame, height=32)
    file_path_entry.grid(row=0, column=4, padx=(0, 10), pady=(8, 8), sticky='ew')
    video_button = ctk.CTkButton(streaming_settings_frame, text='Pilih Video', command=choose_file, height=32)
    video_button.grid(row=0, column=5, padx=(0, 15), pady=(8, 8), sticky='ew')
    input_folder_label = ctk.CTkLabel(streaming_settings_frame, text='Input Folder (NON VCAM):')
    input_folder_label.grid(row=1, column=3, padx=(15, 10), pady=(8, 8), sticky='w')
    folder_path_entry = ctk.CTkEntry(streaming_settings_frame, height=32)
    folder_path_entry.grid(row=1, column=4, padx=(0, 10), pady=(8, 8), sticky='ew')
    folder_button = ctk.CTkButton(streaming_settings_frame, text='Pilih Folder', command=choose_folder, height=32)
    folder_button.grid(row=1, column=5, padx=(0, 15), pady=(8, 8), sticky='ew')
    duration_label = ctk.CTkLabel(streaming_settings_frame, text='Durasi Download (detik):')
    duration_label.grid(row=2, column=3, padx=(15, 10), pady=(8, 8), sticky='w')
    duration_entry = ctk.CTkEntry(streaming_settings_frame, textvariable=duration_entry_var, height=32)
    duration_entry.grid(row=2, column=4, columnspan=2, padx=(0, 15), pady=(8, 8), sticky='ew')
    control_frame = ctk.CTkFrame(root)
    control_frame.pack(pady=(10, 15), padx=20, fill='x')
    for i in range(4):
        control_frame.grid_columnconfigure(i, weight=1)
    start_button = ctk.CTkButton(control_frame, text='Mulai Live', command=start_streaming, height=35)
    start_button.grid(row=0, column=0, padx=(10, 5), pady=(10, 5), sticky='ew')
    stop_button = ctk.CTkButton(control_frame, text='Hentikan Live', command=stop_streaming, state='disabled', height=35)
    stop_button.grid(row=0, column=1, padx=5, pady=(10, 5), sticky='ew')
    get_rtmp_button = ctk.CTkButton(control_frame, text='Get RTMP Info', command=get_rtmp_info, height=35)
    get_rtmp_button.grid(row=0, column=2, padx=5, pady=(10, 5), sticky='ew')
    live_downloader_button = ctk.CTkButton(control_frame, text='Live Downloader', command=start_live_downloader, height=35)
    live_downloader_button.grid(row=0, column=3, padx=(5, 10), pady=(10, 5), sticky='ew')
    add_account_button = ctk.CTkButton(control_frame, text='Tambah Akun', command=add_account, height=35)
    add_account_button.grid(row=1, column=0, padx=(10, 5), pady=5, sticky='ew')
    delete_account_button = ctk.CTkButton(control_frame, text='Hapus Akun', command=delete_account, height=35)
    delete_account_button.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
    account_menu = ctk.CTkOptionMenu(control_frame, values=['Pilih Akun'], height=35)
    account_menu.grid(row=1, column=2, padx=5, pady=5, sticky='ew')
    mode_menu = ctk.CTkOptionMenu(control_frame, variable=mode_var, values=['VCAM', 'NON VCAM'], height=35)
    mode_menu.grid(row=1, column=3, padx=(5, 10), pady=5, sticky='ew')
    account_live_downloader_button = ctk.CTkButton(control_frame, text='Account Live Downloader', command=account_live_downloader, height=35)
    account_live_downloader_button.grid(row=2, column=0, columnspan=2, padx=(10, 5), pady=(5, 10), sticky='ew')
    inject_metadata_button = ctk.CTkButton(control_frame, text='Inject Metadata', command=inject_metadata, height=35)
    inject_metadata_button.grid(row=2, column=2, columnspan=2, padx=(5, 10), pady=(5, 10), sticky='ew')
    console_output = scrolledtext.ScrolledText(root, height=12)
    console_output.pack(pady=(5, 15), padx=20, fill='both', expand=True)
    console_output.config(background='black', foreground='#44ff00')
    console_output.configure(state='disabled')
    read_cookies_from_file('cookies.json')

    def on_closing():
        stop_streaming()
        root.destroy()
    root.protocol('WM_DELETE_WINDOW', on_closing)

    def periodic_license_check():
        saved_license = read_key_from_file()
        if saved_license is None or not verify_key_with_server(saved_license):
            if streaming_active:
                stop_streaming()
            messagebox.showerror('Error', 'Lisensi tidak lagi valid. Aplikasi akan ditutup.')
            root.destroy()
            return
        root.after(3600000, periodic_license_check)
    periodic_license_check()
    root.mainloop()
else:  # inserted
    root.destroy()