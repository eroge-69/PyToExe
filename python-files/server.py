import sys
import os
import threading
import socket
import sqlite3
import shutil
import hashlib
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QListWidget, QTextEdit, QLabel, QTabWidget, QFrame,
                            QAction, QMenuBar, QDialog, QFormLayout, QLineEdit, QComboBox,
                            QMessageBox, QInputDialog, QGraphicsDropShadowEffect, QStatusBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QSize
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon

def adapt_datetime(dt):
    return dt.isoformat()
sqlite3.register_adapter(datetime, adapt_datetime)

def parse_datetime(s):
    return datetime.fromisoformat(s)
sqlite3.register_converter("DATETIME", parse_datetime)

SERVER_FILES_DIR = 'server_files'
os.makedirs(SERVER_FILES_DIR, exist_ok=True)

def init_db():
    with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS downloads
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      file_name TEXT NOT NULL,
                      client_address TEXT,
                      timestamp DATETIME NOT NULL,
                      user_id TEXT,
                      speed REAL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS files
                     (file_name TEXT PRIMARY KEY,
                      upload_date DATETIME NOT NULL,
                      user_id TEXT,
                      is_private INTEGER DEFAULT 0,
                      size INTEGER,
                      checksum TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY,
                      password TEXT NOT NULL,
                      display_name TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS file_shares
                     (file_name TEXT,
                      shared_with_user TEXT,
                      PRIMARY KEY (file_name, shared_with_user),
                      FOREIGN KEY (file_name) REFERENCES files(file_name))''')
        conn.commit()

class ServerThread(QThread):
    log_message = pyqtSignal(str)
    file_list_updated = pyqtSignal(list)
    stats_updated = pyqtSignal(dict)
    user_list_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.server_socket = None
        self.running = False
        self.host = '0.0.0.0'  # Listen on all interfaces
        self.port = 1253
        self.active_connections = 0
        init_db()

    def calculate_checksum(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def list_server_files(self, user_id):
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT file_name FROM files 
                    WHERE is_private = 0 OR user_id = ? 
                    OR file_name IN (SELECT file_name FROM file_shares WHERE shared_with_user = ?)
                """, (user_id, user_id))
                files = [row[0] for row in cursor.fetchall()]
            return files
        except Exception as e:
            self.log_message.emit(f"Error listing files: {str(e)}")
            return []

    def get_public_and_private_files(self, user_id):
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT file_name FROM files WHERE is_private = 0")
                public_files = [row[0] for row in cursor.fetchall()]
                cursor.execute("""
                    SELECT file_name FROM files WHERE is_private = 1 AND user_id = ?
                    UNION
                    SELECT file_name FROM file_shares WHERE shared_with_user = ?
                """, (user_id, user_id))
                private_files = [row[0] for row in cursor.fetchall()]
            return public_files, private_files
        except Exception as e:
            self.log_message.emit(f"Error listing files: {str(e)}")
            return [], []

    def search_files(self, user_id, query):
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT file_name FROM files 
                    WHERE (is_private = 0 OR user_id = ? OR file_name IN (SELECT file_name FROM file_shares WHERE shared_with_user = ?))
                    AND file_name LIKE ? COLLATE NOCASE
                """, (user_id, user_id, f"%{query}%"))
                files = [row[0] for row in cursor.fetchall()]
                public_files = [f for f in files if not self.is_private_file(f, user_id)]
                private_files = [f for f in files if self.is_private_file(f, user_id)]
            return public_files, private_files
        except Exception as e:
            self.log_message.emit(f"Error searching files: {str(e)}")
            return [], []

    def is_private_file(self, file_name, user_id):
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT is_private, user_id FROM files WHERE file_name = ?", (file_name,))
                result = cursor.fetchone()
                if result:
                    is_private, owner = result
                    return is_private == 1 and owner == user_id
                return False
        except Exception as e:
            self.log_message.emit(f"Error checking file privacy: {str(e)}")
            return False

    def get_stats(self, timeframe='month'):
        stats = {
            'downloads': 0,
            'total_days_with_downloads': 0,
            'total_files': 0,
            'total_storage_gb': 0.0,
            'files_per_user': {},
            'downloads_per_user': {},
            'active_connections': self.active_connections,
            'average_speed': 0.0
        }
        
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                
                if timeframe == 'day':
                    start_date = datetime.now() - timedelta(days=1)
                elif timeframe == 'week':
                    start_date = datetime.now() - timedelta(days=7)
                elif timeframe == 'year':
                    start_date = datetime.now() - timedelta(days=365)
                else:  # month
                    start_date = datetime.now() - timedelta(days=30)
                
                cursor.execute("SELECT COUNT(*) FROM downloads WHERE timestamp >= ?", (start_date,))
                stats['downloads'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT DATE(timestamp)) FROM downloads")
                stats['total_days_with_downloads'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*), SUM(size) FROM files")
                result = cursor.fetchone()
                stats['total_files'] = result[0] or 0
                stats['total_storage_gb'] = (result[1] or 0) / (1024**3)
                
                cursor.execute("SELECT user_id, COUNT(*) FROM files GROUP BY user_id")
                stats['files_per_user'] = dict(cursor.fetchall() or [])
                
                cursor.execute("SELECT user_id, COUNT(*) FROM downloads WHERE timestamp >= ? GROUP BY user_id", (start_date,))
                stats['downloads_per_user'] = dict(cursor.fetchall() or [])
                
                cursor.execute("SELECT AVG(speed) FROM downloads WHERE timestamp >= ?", (start_date,))
                stats['average_speed'] = cursor.fetchone()[0] or 0
                
        except sqlite3.Error as e:
            self.log_message.emit(f"Database error getting stats: {str(e)}")
            
        return stats

    def get_users(self):
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, display_name FROM users")
                users = [f"{row[0]} ({row[1]})" if row[1] else row[0] for row in cursor.fetchall()]
            return users
        except Exception as e:
            self.log_message.emit(f"Error listing users: {str(e)}")
            return []

    def send_file_to_client(self, client_socket, file_name, client_address, user_id, offset=0):
        file_path = os.path.join(SERVER_FILES_DIR, file_name)
        
        if not os.path.exists(file_path):
            client_socket.send(f"Error: File '{file_name}' not found.\n".encode('utf-8'))
            self.log_message.emit(f"Error: File '{file_name}' not found for {client_address}")
            return
            
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT is_private, user_id FROM files WHERE file_name = ?
                """, (file_name,))
                result = cursor.fetchone()
                
                has_access = False
                if result:
                    if result[0] == 0:  # Public file
                        has_access = True
                    elif result[1] == user_id:  # Owner
                        has_access = True
                    else:  # Check shares
                        cursor.execute("SELECT 1 FROM file_shares WHERE file_name = ? AND shared_with_user = ?", 
                                    (file_name, user_id))
                        if cursor.fetchone():
                            has_access = True
                
                if has_access:
                    start_time = datetime.now()
                    if os.path.isdir(file_path):
                        zip_path = file_path + '.zip'
                        shutil.make_archive(file_path, 'zip', file_path)
                        file_size = os.path.getsize(zip_path)
                        header = f"FILE_SIZE:{file_size}:ZIP\n"
                        client_socket.sendall(header.encode('utf-8'))  # Send header explicitly
                        self.log_message.emit(f"Sending header: {header.strip()} for {file_name}")
                        with open(zip_path, 'rb') as f:
                            f.seek(offset)
                            while True:
                                data = f.read(4096)
                                if not data:
                                    break
                                client_socket.sendall(data)
                        os.remove(zip_path)
                    else:
                        file_size = os.path.getsize(file_path)
                        header = f"FILE_SIZE:{file_size}\n"
                        client_socket.sendall(header.encode('utf-8'))  # Send header explicitly
                        self.log_message.emit(f"Sending header: {header.strip()} for {file_name}")
                        with open(file_path, 'rb') as f:
                            f.seek(offset)
                            while True:
                                data = f.read(4096)
                                if not data:
                                    break
                                client_socket.sendall(data)
                    
                    transfer_time = (datetime.now() - start_time).total_seconds()
                    speed = (file_size / (1024 * 1024)) / transfer_time if transfer_time > 0 else 0  # MB/s
                    
                    self.log_message.emit(f"Sent '{file_name}' to {client_address} (Speed: {speed:.2f} MB/s)")
                    
                    conn.execute("""
                        INSERT INTO downloads (file_name, client_address, timestamp, user_id, speed)
                        VALUES (?, ?, ?, ?, ?)
                    """, (file_name, str(client_address), datetime.now(), user_id, speed))
                    
                    self.stats_updated.emit(self.get_stats())
                else:
                    client_socket.send(f"Error: Access denied for file '{file_name}'\n".encode('utf-8'))
                    self.log_message.emit(f"Access denied for '{file_name}' to {client_address}")
                    
        except Exception as e:
            self.log_message.emit(f"Error sending file '{file_name}': {str(e)}")
            try:
                client_socket.send(f"Error: {str(e)}\n".encode('utf-8'))
            except:
                pass

    def receive_file_from_client(self, client_socket, file_name, file_size, client_address, user_id, is_private, is_folder):
        file_path = os.path.join(SERVER_FILES_DIR, file_name)
        temp_path = file_path + '.tmp'
        
        try:
            if is_folder:
                zip_path = temp_path + '.zip'
                received_size = 0
                start_time = datetime.now()
                with open(zip_path, 'wb') as f:
                    while received_size < file_size:
                        data = client_socket.recv(min(4096, file_size - received_size))
                        if not data:
                            break
                        f.write(data)
                        received_size += len(data)
                
                if received_size != file_size:
                    raise Exception(f"Incomplete folder transfer. Expected {file_size} bytes, received {received_size}")
                
                os.makedirs(file_path, exist_ok=True)
                shutil.unpack_archive(zip_path, file_path, 'zip')
                os.remove(zip_path)
                
                transfer_time = (datetime.now() - start_time).total_seconds()
                speed = (file_size / (1024 * 1024)) / transfer_time if transfer_time > 0 else 0  # MB/s
                
                for root, _, files in os.walk(file_path):
                    for fname in files:
                        rel_path = os.path.relpath(os.path.join(root, fname), SERVER_FILES_DIR)
                        full_path = os.path.join(root, fname)
                        checksum = self.calculate_checksum(full_path)
                        with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                            conn.execute("""
                                INSERT OR REPLACE INTO files 
                                (file_name, upload_date, user_id, is_private, size, checksum) 
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (rel_path, datetime.now(), user_id, is_private, os.path.getsize(full_path), checksum))
            else:
                received_size = 0
                start_time = datetime.now()
                with open(temp_path, 'wb') as f:
                    while received_size < file_size:
                        data = client_socket.recv(min(4096, file_size - received_size))
                        if not data:
                            break
                        f.write(data)
                        received_size += len(data)
                
                if received_size != file_size:
                    raise Exception(f"Incomplete file transfer. Expected {file_size} bytes, received {received_size}")
                
                transfer_time = (datetime.now() - start_time).total_seconds()
                speed = (file_size / (1024 * 1024)) / transfer_time if transfer_time > 0 else 0  # MB/s
                
                checksum = self.calculate_checksum(temp_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
                os.rename(temp_path, file_path)
                
                with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO files 
                        (file_name, upload_date, user_id, is_private, size, checksum) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (file_name, datetime.now(), user_id, is_private, file_size, checksum))
            
            client_socket.send(f"File '{file_name}' uploaded successfully (Speed: {speed:.2f} MB/s).".encode('utf-8'))
            self.log_message.emit(f"Received '{file_name}' from {client_address} (Speed: {speed:.2f} MB/s)")
            
            self.file_list_updated.emit(self.list_server_files(user_id))
            self.stats_updated.emit(self.get_stats())
                
        except Exception as e:
            self.log_message.emit(f"Error receiving file '{file_name}': {str(e)}")
            for path in [temp_path, file_path, temp_path + '.zip']:
                if os.path.exists(path):
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
            try:
                client_socket.send(f"Error: {str(e)}".encode('utf-8'))
            except:
                pass

    def handle_client_connection(self, client_socket, client_address):
        self.active_connections += 1
        self.log_message.emit(f"[ACTIVE CONNECTIONS] {self.active_connections}")
        self.log_message.emit(f"New connection from {client_address}")
        
        user_id = None
        
        try:
            while self.running:
                try:
                    data = client_socket.recv(1024).decode('utf-8', errors='ignore')
                    if not data:
                        break
                        
                    self.log_message.emit(f"Received from {client_address}: {data[:100]}...")
                    
                    if data.startswith("LOGIN:"):
                        user_id = self.handle_login(client_socket, data[6:], client_address)
                    elif data.startswith("LOGOUT:"):
                        user_id = self.handle_logout(client_socket, client_address)
                    elif data.startswith("LIST:"):
                        self.handle_list_request(client_socket, user_id)
                    elif data.startswith("DOWNLOAD:"):
                        self.handle_download(client_socket, data[9:], client_address, user_id)
                    elif data.startswith("DOWNLOAD_RESUME:"):
                        self.handle_download_resume(client_socket, data[15:], client_address, user_id)
                    elif data.startswith("UPLOAD:"):
                        self.handle_upload(client_socket, data[7:], client_address, user_id)
                    elif data.startswith("SHARE:"):
                        self.handle_share(client_socket, data[6:], user_id)
                    elif data.startswith("CHANGE_PASSWORD:"):
                        self.handle_password_change(client_socket, data[15:], user_id)
                    elif data.startswith("DELETE_ACCOUNT:"):
                        self.handle_delete_account(client_socket, data[14:], client_address)
                    elif data.startswith("SEARCH:"):
                        self.handle_search(client_socket, data[7:], user_id)
                    elif data.startswith("DELETE_FILE:"):
                        self.handle_delete_file(client_socket, data[12:], user_id)
                    elif data.startswith("GET_DISPLAY_NAME:"):
                        self.handle_get_display_name(client_socket, data[16:])
                    elif data.startswith("UPDATE_DISPLAY_NAME:"):
                        self.handle_update_display_name(client_socket, data[19:], user_id)
                    else:
                        client_socket.send(f"Unknown command: {data[:100]}".encode('utf-8'))
                        
                except ConnectionResetError as e:
                    self.error_occurred.emit(f"Connection reset by {client_address}")
                    break
                except Exception as e:
                    self.error_occurred.emit(f"Error with {client_address}: {str(e)}")
                    try:
                        client_socket.send(f"Error: {str(e)}".encode('utf-8'))
                    except:
                        break
                        
        finally:
            client_socket.close()
            self.active_connections -= 1
            self.log_message.emit(f"Connection closed with {client_address}")
            self.log_message.emit(f"[ACTIVE CONNECTIONS] {self.active_connections}")

    def handle_login(self, client_socket, data, client_address):
        parts = data.split(':')
        if len(parts) != 2:
            client_socket.send("Error: Invalid format. Use 'username:password'".encode('utf-8'))
            return None
            
        username, password = parts
        user_id = None
        
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()
                
            if result and result[0] == password:
                user_id = username
                client_socket.send("Login successful.".encode('utf-8'))
                self.log_message.emit(f"User '{username}' logged in from {client_address}")
                
                public_files, private_files = self.get_public_and_private_files(user_id)
                response = f"PUBLIC:{','.join(public_files)}|PRIVATE:{','.join(private_files)}"
                client_socket.sendall(response.encode('utf-8'))
            else:
                client_socket.send("Error: Invalid username or password.".encode('utf-8'))
                
        except Exception as e:
            client_socket.send(f"Error: {str(e)}".encode('utf-8'))
            
        return user_id

    def handle_logout(self, client_socket, client_address):
        client_socket.send("Logout successful.".encode('utf-8'))
        self.log_message.emit(f"User logged out from {client_address}")
        return None

    def handle_list_request(self, client_socket, user_id):
        if not user_id:
            client_socket.send("Error: Authentication required.".encode('utf-8'))
            return
        public_files, private_files = self.get_public_and_private_files(user_id)
        response = f"PUBLIC:{','.join(public_files)}|PRIVATE:{','.join(private_files)}"
        client_socket.sendall(response.encode('utf-8'))

    def handle_download(self, client_socket, data, client_address, user_id):
        if not user_id:
            client_socket.send("Error: Authentication required.\n".encode('utf-8'))
            self.log_message.emit(f"Download failed: Authentication required for {client_address}")
            return
            
        file_name = data.strip()
        self.log_message.emit(f"Handling download request for '{file_name}' from {client_address}")
        self.send_file_to_client(client_socket, file_name, client_address, user_id)

    def handle_download_resume(self, client_socket, data, client_address, user_id):
        if not user_id:
            client_socket.send("Error: Authentication required.".encode('utf-8'))
            return
            
        parts = data.split(':')
        if len(parts) != 2:
            client_socket.send("Error: Invalid format. Use 'filename:offset'".encode('utf-8'))
            return
            
        file_name, offset = parts
        offset = int(offset)
        self.send_file_to_client(client_socket, file_name, client_address, user_id, offset)

    def handle_upload(self, client_socket, data, client_address, user_id):
        if not user_id:
            client_socket.send("Error: Authentication required.".encode('utf-8'))
            return
            
        parts = data.split(':')
        if len(parts) != 4:
            client_socket.send("Error: Invalid format. Use 'filename:size:is_private:is_folder'".encode('utf-8'))
            return
            
        file_name = parts[0].strip()
        try:
            file_size = int(parts[1].strip())
            is_private = int(parts[2].strip())
            is_folder = int(parts[3].strip())
        except ValueError:
            client_socket.send("Error: Invalid file size, privacy, or folder setting.".encode('utf-8'))
            return
            
        self.receive_file_from_client(client_socket, file_name, file_size, client_address, user_id, is_private, is_folder)
        
        public_files, private_files = self.get_public_and_private_files(user_id)
        response = f"PUBLIC:{','.join(public_files)}|PRIVATE:{','.join(private_files)}"
        client_socket.sendall(response.encode('utf-8'))

    def handle_share(self, client_socket, data, user_id):
        if not user_id:
            client_socket.send("Error: Authentication required.".encode('utf-8'))
            return
            
        parts = data.split(':')
        if len(parts) != 2:
            client_socket.send("Error: Invalid format. Use 'file_name:target_user'".encode('utf-8'))
            return
            
        file_name, target_user = parts
        
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM files WHERE file_name = ? AND is_private = 1", (file_name,))
                result = cursor.fetchone()
                if not result or result[0] != user_id:
                    client_socket.send("Error: You can only share your private files.".encode('utf-8'))
                    return
                    
                cursor.execute("SELECT 1 FROM users WHERE username = ?", (target_user,))
                if not cursor.fetchone():
                    client_socket.send("Error: Target user does not exist.".encode('utf-8'))
                    return
                    
                conn.execute("INSERT INTO file_shares (file_name, shared_with_user) VALUES (?, ?)",
                           (file_name, target_user))
                client_socket.send(f"File '{file_name}' shared with '{target_user}'.".encode('utf-8'))
                self.log_message.emit(f"User '{user_id}' shared '{file_name}' with '{target_user}'")
        except sqlite3.IntegrityError:
            client_socket.send("Error: File already shared with this user.".encode('utf-8'))
        except Exception as e:
            client_socket.send(f"Error: {str(e)}".encode('utf-8'))

    def handle_password_change(self, client_socket, data, user_id):
        if not user_id:
            client_socket.send("Error: Authentication required.".encode('utf-8'))
            return

        new_password = data.strip()
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                conn.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, user_id))
                conn.commit()  # ✅ THIS MUST BE PRESENT
                client_socket.send("Password updated successfully.".encode('utf-8'))
                self.log_message.emit(f"User '{user_id}' updated password")
        except Exception as e:
            client_socket.send(f"Error: {str(e)}".encode('utf-8'))


    def handle_delete_account(self, client_socket, data, client_address):
        if not data:
            client_socket.send("Error: Username required.".encode('utf-8'))
            return
            
        username = data.strip()
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
                if not cursor.fetchone():
                    client_socket.send("Error: User does not exist.".encode('utf-8'))
                    return
                
                conn.execute("DELETE FROM file_shares WHERE file_name IN (SELECT file_name FROM files WHERE user_id = ?)", (username,))
                conn.execute("DELETE FROM files WHERE user_id = ?", (username,))
                conn.execute("DELETE FROM downloads WHERE user_id = ?", (username,))
                conn.execute("DELETE FROM users WHERE username = ?", (username,))
                conn.commit()
                
                client_socket.send("Account deleted successfully.".encode('utf-8'))
                self.log_message.emit(f"User '{username}' deleted account from {client_address}")
                self.user_list_updated.emit(self.get_users())
        except Exception as e:
            client_socket.send(f"Error: {str(e)}".encode('utf-8'))
            self.log_message.emit(f"Error deleting account '{username}': {str(e)}")

    def handle_search(self, client_socket, data, user_id):
        if not user_id:
            client_socket.send("Error: Authentication required.".encode('utf-8'))
            return
        query = data.strip()
        public_files, private_files = self.search_files(user_id, query)
        response = f"PUBLIC:{','.join(public_files)}|PRIVATE:{','.join(private_files)}"
        client_socket.sendall(response.encode('utf-8'))

    def handle_delete_file(self, client_socket, data, user_id):
        if not user_id:
            client_socket.send("Error: Authentication required.".encode('utf-8'))
            return
            
        file_name = data.strip()
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM files WHERE file_name = ?", (file_name,))
                result = cursor.fetchone()
                if not result or result[0] != user_id:
                    client_socket.send(f"Error: You can only delete files you uploaded ('{file_name}').".encode('utf-8'))
                    return
                
                file_path = os.path.join(SERVER_FILES_DIR, file_name)
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                
                conn.execute("DELETE FROM files WHERE file_name = ?", (file_name,))
                conn.execute("DELETE FROM file_shares WHERE file_name = ?", (file_name,))
                conn.commit()
                
                client_socket.send(f"File '{file_name}' deleted successfully.".encode('utf-8'))
                self.log_message.emit(f"User '{user_id}' deleted file '{file_name}'")
                self.file_list_updated.emit(self.list_server_files(user_id))
        except Exception as e:
            client_socket.send(f"Error: {str(e)}".encode('utf-8'))
            self.log_message.emit(f"Error deleting file '{file_name}': {str(e)}")

    def handle_get_display_name(self, client_socket, username):
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT display_name FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()
                display_name = result[0] if result and result[0] else username
                client_socket.send(display_name.encode('utf-8'))
        except Exception as e:
            client_socket.send(username.encode('utf-8'))

    def handle_update_display_name(self, client_socket, data, user_id):
        if not user_id:
            client_socket.send("Error: Authentication required.".encode('utf-8'))
            return
            
        try:
            with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                conn.execute("UPDATE users SET display_name = ? WHERE username = ?", (data, user_id))
                conn.commit()
                client_socket.send("Display name updated successfully.".encode('utf-8'))
                self.log_message.emit(f"User '{user_id}' updated display name to '{data}'")
                self.user_list_updated.emit(self.get_users())
        except Exception as e:
            client_socket.send(f"Error: {str(e)}".encode('utf-8'))

    def run(self):
        if os.geteuid() == 0:
            self.log_message.emit("Warning: Running as root is not recommended. Consider running as a regular user to avoid GUI issues.")
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            self.log_message.emit(f"Server started on {self.host}:{self.port}")
            self.file_list_updated.emit(self.list_server_files(None))
            self.stats_updated.emit(self.get_stats())
            self.user_list_updated.emit(self.get_users())
            
            while self.running:
                try:
                    self.server_socket.settimeout(1)
                    client_socket, client_address = self.server_socket.accept()
                    threading.Thread(
                        target=self.handle_client_connection,
                        args=(client_socket, client_address),
                        daemon=True
                    ).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.log_message.emit(f"Server accept error: {str(e)}")
                        
        except Exception as e:
            self.log_message.emit(f"Server error: {str(e)}")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.log_message.emit("Server stopped.")

# [Previous server code remains the same until the UserDialog class]

class UserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage User")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("Enter display name (optional)")
        
        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        layout.addRow("Display Name:", self.display_name_input)
        
        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        
        layout.addRow(buttons)
        self.setLayout(layout)

    def get_credentials(self):
        return (
            self.username_input.text().strip(),
            self.password_input.text().strip(),
            self.display_name_input.text().strip()
        )

class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Transfer Server")
        self.setGeometry(100, 100, 1000, 700)
        self.server_thread = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QPushButton {
                background-color: #4a6fa5;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a5a8f;
            }
            QPushButton:pressed {
                background-color: #2a4a7f;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QListWidget, QTextEdit, QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                color: #333333;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QTabBar::tab {
                padding: 8px 16px;
                background-color: #e0e0e0;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #4a6fa5;
            }
            QLabel {
                color: #333333;
            }
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #4a6fa5;
                border-radius: 4px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("File Transfer Server Dashboard")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #333333;")
        layout.addWidget(header)

        # Control buttons
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        
        self.start_btn = QPushButton("Start Server")
        self.start_btn.clicked.connect(self.start_server)
        self.start_btn.setFixedHeight(40)
        
        self.stop_btn = QPushButton("Stop Server")
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addStretch()
        
        layout.addWidget(control_frame)

        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Files Tab
        files_tab = QWidget()
        files_layout = QVBoxLayout(files_tab)
        
        files_label = QLabel("Server Files")
        files_label.setStyleSheet("font-weight: bold;")
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        
        files_layout.addWidget(files_label)
        files_layout.addWidget(self.file_list)
        tabs.addTab(files_tab, "Files")

        # Statistics Tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        stats_label = QLabel("Statistics")
        stats_label.setStyleSheet("font-weight: bold;")
        
        timeframe_layout = QHBoxLayout()
        timeframe_label = QLabel("Timeframe:")
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["Day", "Week", "Month", "Year"])
        self.timeframe_combo.currentTextChanged.connect(self.update_stats_timeframe)
        timeframe_layout.addWidget(timeframe_label)
        timeframe_layout.addWidget(self.timeframe_combo)
        timeframe_layout.addStretch()
        
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        
        stats_layout.addWidget(stats_label)
        stats_layout.addLayout(timeframe_layout)
        stats_layout.addWidget(self.stats_display)
        tabs.addTab(stats_tab, "Statistics")

        # User Management Tab
        users_tab = QWidget()
        users_layout = QVBoxLayout(users_tab)
        
        users_label = QLabel("User Management")
        users_label.setStyleSheet("font-weight: bold;")
        
        user_btn_layout = QHBoxLayout()
        add_user_btn = QPushButton("Add User")
        add_user_btn.clicked.connect(self.add_user)
        delete_user_btn = QPushButton("Delete User")
        delete_user_btn.clicked.connect(self.delete_user)
        user_btn_layout.addWidget(add_user_btn)
        user_btn_layout.addWidget(delete_user_btn)
        user_btn_layout.addStretch()
        
        self.user_list = QListWidget()
        
        users_layout.addWidget(users_label)
        users_layout.addLayout(user_btn_layout)
        users_layout.addWidget(self.user_list)
        tabs.addTab(users_tab, "Users")

        # Log Display
        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)
        
        log_label = QLabel("Server Logs")
        log_label.setStyleSheet("font-weight: bold;")
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_display)
        layout.addWidget(log_frame)

        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                border-top: 1px solid palette(mid);
            }
        """)

        # Window shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.shadow.setOffset(0, 0)
        central_widget.setGraphicsEffect(self.shadow)

    def apply_theme(self):
        palette = QPalette()
        if self.dark_mode:
            # Modern dark theme
            palette.setColor(QPalette.Window, QColor("#121212"))
            palette.setColor(QPalette.WindowText, QColor("#E0E0E0"))
            palette.setColor(QPalette.Base, QColor("#1E1E1E"))
            palette.setColor(QPalette.AlternateBase, QColor("#2D2D2D"))
            palette.setColor(QPalette.Text, QColor("#FFFFFF"))
            palette.setColor(QPalette.Button, QColor("#333333"))
            palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
            palette.setColor(QPalette.Highlight, QColor("#BB86FC"))  # Purple accent
            palette.setColor(QPalette.HighlightedText, QColor("#000000"))
            palette.setColor(QPalette.ToolTipBase, QColor("#BB86FC"))
            palette.setColor(QPalette.ToolTipText, QColor("#000000"))
            self.theme_btn.setText("Light Mode")
            
            # Title bar style
            self.title_bar.setStyleSheet("""
                background-color: #1E1E1E;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            """)
            self.title_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 14px;")
        else:
            # Modern light theme
            palette.setColor(QPalette.Window, QColor("#F5F5F5"))
            palette.setColor(QPalette.WindowText, QColor("#212121"))
            palette.setColor(QPalette.Base, QColor("#FFFFFF"))
            palette.setColor(QPalette.AlternateBase, QColor("#F5F5F5"))
            palette.setColor(QPalette.Text, QColor("#212121"))
            palette.setColor(QPalette.Button, QColor("#E0E0E0"))
            palette.setColor(QPalette.ButtonText, QColor("#212121"))
            palette.setColor(QPalette.Highlight, QColor("#6200EE"))  # Purple accent
            palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
            palette.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
            palette.setColor(QPalette.ToolTipText, QColor("#212121"))
            self.theme_btn.setText("Dark Mode")
            
            # Title bar style
            self.title_bar.setStyleSheet("""
                background-color: #FFFFFF;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid #E0E0E0;
            """)
            self.title_label.setStyleSheet("color: #212121; font-weight: bold; font-size: 14px;")
        
        self.setPalette(palette)
        
        # Modern style sheet
        style = """
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QMainWindow {
            background-color: palette(window);
        }
        QFrame {
            border-radius: 8px;
            background-color: palette(base);
        }
        QPushButton {
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            min-width: 80px;
            border: 1px solid palette(button);
        }
        QPushButton:hover {
            background-color: palette(highlight);
            color: palette(highlightedtext);
        }
        QPushButton:pressed {
            background-color: palette(highlight);
            color: palette(highlightedtext);
        }
        QPushButton:disabled {
            color: palette(windowText);
            background-color: palette(window);
        }
        QListWidget, QTextEdit, QLineEdit {
            border-radius: 6px;
            padding: 8px;
            border: 1px solid palette(mid);
            background-color: palette(base);
        }
        QTabWidget::pane {
            border-radius: 6px;
            border: 1px solid palette(mid);
        }
        QTabBar::tab {
            padding: 8px 16px;
            border-radius: 4px;
            margin-right: 4px;
        }
        QTabBar::tab:selected {
            background-color: palette(highlight);
            color: palette(highlightedtext);
        }
        QProgressBar {
            border-radius: 4px;
            border: 1px solid palette(mid);
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: palette(highlight);
            border-radius: 4px;
        }
        QLabel {
            font-weight: 500;
        }
        """
        self.setStyleSheet(style)

        # Apply to all widgets
        for widget in self.findChildren(QWidget):
            widget.setPalette(palette)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def toggle_maximized(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() < 40:
            self.drag_pos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_pos'):
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()
            event.accept()

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'drag_pos'):
            del self.drag_pos

    def start_server(self):
        if not self.server_thread or not self.server_thread.isRunning():
            self.server_thread = ServerThread()
            self.server_thread.log_message.connect(self.append_log)
            self.server_thread.file_list_updated.connect(self.update_file_list)
            self.server_thread.stats_updated.connect(self.update_stats)
            self.server_thread.user_list_updated.connect(self.update_user_list)
            self.server_thread.start()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.statusBar().showMessage("Server started")

    def stop_server(self):
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.stop()
            self.server_thread.wait()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.file_list.clear()
            self.stats_display.clear()
            self.user_list.clear()
            self.statusBar().showMessage("Server stopped")

    def update_file_list(self, files):
        self.file_list.clear()
        self.file_list.addItems(files)

    def update_stats_timeframe(self, timeframe):
        if self.server_thread and self.server_thread.isRunning():
            stats = self.server_thread.get_stats(timeframe.lower())
            self.update_stats(stats)

    def update_stats(self, stats):
        text = (
            f"Downloads (last {self.timeframe_combo.currentText().lower()}): {stats['downloads']}\n"
            f"Total Days with Downloads: {stats['total_days_with_downloads']}\n"
            f"Total Files: {stats['total_files']}\n"
            f"Total Storage: {stats['total_storage_gb']:.2f} GB\n"
            f"Average Transfer Speed: {stats['average_speed']:.2f} MB/s\n"
            f"Files per User: {stats['files_per_user']}\n"
            f"Downloads per User: {stats['downloads_per_user']}\n"
            f"Active Connections: {stats['active_connections']}"
        )
        self.stats_display.setText(text)

    def update_user_list(self, users):
        self.user_list.clear()
        self.user_list.addItems(users)

    # In the ServerGUI class, update the add_user method:

    def add_user(self):
        dialog = UserDialog(self)  # Remove the dark_mode parameter
        if dialog.exec_():
            username, password, display_name = dialog.get_credentials()
            if username and password:
                try:
                    if self.server_thread and self.server_thread.isRunning():
                        with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                            conn.execute("""
                                INSERT INTO users (username, password, display_name) 
                                VALUES (?, ?, ?)
                            """, (username, password, display_name))
                        self.server_thread.user_list_updated.emit(self.server_thread.get_users())
                        self.append_log(f"Added user '{username}'")
                        self.statusBar().showMessage(f"User '{username}' added successfully")
                    else:
                        raise Exception("Server not running")
                except sqlite3.IntegrityError:
                    QMessageBox.critical(self, "Error", "Username already exists.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add user: {str(e)}")

    def delete_user(self):
        selected = self.user_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a user to delete.")
            return
        
        username = selected[0].text().split(' (')[0]  # Extract username from display
        reply = QMessageBox.question(self, "Confirm", f"Delete user '{username}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if self.server_thread and self.server_thread.isRunning():
                    with sqlite3.connect('file_transfer.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                        conn.execute("DELETE FROM users WHERE username = ?", (username,))
                        conn.execute("DELETE FROM file_shares WHERE file_name IN (SELECT file_name FROM files WHERE user_id = ?)", (username,))
                        conn.execute("DELETE FROM files WHERE user_id = ?", (username,))
                        conn.execute("DELETE FROM downloads WHERE user_id = ?", (username,))
                        conn.commit()
                    self.server_thread.user_list_updated.emit(self.server_thread.get_users())
                    self.append_log(f"Deleted user '{username}'")
                    self.statusBar().showMessage(f"User '{username}' deleted successfully")
                else:
                    raise Exception("Server not running")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")

    def append_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())

    def closeEvent(self, event):
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.stop()
            self.server_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    font = QFont()
    font.setFamily("Segoe UI" if sys.platform == "win32" else "Arial")
    font.setPointSize(10)
    app.setFont(font)
    
    window = ServerGUI()
    window.show()
    sys.exit(app.exec_())