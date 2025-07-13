import socket
import threading
import json
import base64
import os
import time
import datetime
from PIL import Image, ImageDraw, ImageGrab
import io

class RemoteDesktopServer:
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.running = False
        
    def log_message(self, message):
        """Print timestamped log message"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.log_message(f"🚀 الخادم يعمل على {self.host}:{self.port}")
            self.log_message("⏳ في انتظار الاتصالات...")
            self.running = True
            
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    self.log_message(f"🔗 اتصال جديد من {addr[0]}:{addr[1]}")
                    
                    # Create client thread
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                    self.clients.append({
                        'socket': client_socket,
                        'address': addr,
                        'thread': client_thread
                    })
                    
                except Exception as e:
                    if self.running:
                        self.log_message(f"❌ خطأ في قبول الاتصال: {e}")
                        
        except Exception as e:
            self.log_message(f"❌ فشل في بدء الخادم: {e}")
            
    def handle_client(self, client_socket, addr):
        self.log_message(f"👤 بدء معالجة العميل {addr[0]}:{addr[1]}")
        
        try:
            while self.running:
                try:
                    # Receive length
                    length_bytes = client_socket.recv(4)
                    if not length_bytes:
                        break
                        
                    length = int.from_bytes(length_bytes, byteorder='big')
                    
                    # Receive message
                    message_bytes = b''
                    while len(message_bytes) < length:
                        chunk = client_socket.recv(length - len(message_bytes))
                        if not chunk:
                            break
                        message_bytes += chunk
                        
                    if len(message_bytes) != length:
                        break
                        
                    message = json.loads(message_bytes.decode('utf-8'))
                    self.log_message(f"📨 استقبال أمر من {addr[0]}: {message.get('command')}")
                    
                    self.process_command(message, client_socket, addr)
                    
                except json.JSONDecodeError:
                    self.log_message(f"❌ خطأ في تحليل JSON من {addr[0]}")
                    break
                except Exception as e:
                    self.log_message(f"❌ خطأ في معالجة العميل {addr[0]}: {e}")
                    break
                    
        except Exception as e:
            self.log_message(f"❌ خطأ عام مع العميل {addr[0]}: {e}")
        finally:
            self.log_message(f"🔌 انتهاء الاتصال مع {addr[0]}:{addr[1]}")
            client_socket.close()
            
            # Remove client from list
            self.clients = [c for c in self.clients if c['socket'] != client_socket]
            
    def process_command(self, message, client_socket, addr):
        command = message.get('command')
        data = message.get('data', {})
        
        try:
            if command == 'screenshot':
                self.log_message(f"📸 طلب لقطة شاشة من {addr[0]}")
                self.send_screenshot(client_socket)
                
            elif command == 'list_files':
                path = data.get('path', '.')
                self.log_message(f"📋 طلب قائمة ملفات من {addr[0]}: {path}")
                self.send_file_list(client_socket, path)
                
            elif command == 'download_file':
                filename = data.get('filename')
                self.log_message(f"⬇️ طلب تحميل ملف من {addr[0]}: {filename}")
                self.send_file(client_socket, filename)
                
            else:
                self.log_message(f"❓ أمر غير معروف من {addr[0]}: {command}")
                self.send_error(client_socket, f"Unknown command: {command}")
                
        except Exception as e:
            self.log_message(f"❌ خطأ في معالجة الأمر {command}: {e}")
            self.send_error(client_socket, str(e))
            
    def send_response(self, client_socket, command, data):
        try:
            response = {
                'command': command,
                'data': data
            }
            
            response_json = json.dumps(response)
            response_bytes = response_json.encode('utf-8')
            length = len(response_bytes)
            
            client_socket.send(length.to_bytes(4, byteorder='big'))
            client_socket.send(response_bytes)
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ خطأ في إرسال الرد: {e}")
            return False
            
    def send_error(self, client_socket, error_message):
        self.send_response(client_socket, 'error', error_message)
        
    def send_screenshot(self, client_socket):
        try:
            # Try to capture actual screen (Windows/Linux)
            try:
                # Use PIL to capture screen
                screenshot = ImageGrab.grab()
                self.log_message("✅ تم التقاط الشاشة الفعلية")
                
            except Exception as e:
                # Fallback to demo image if screen capture fails
                self.log_message(f"⚠️ فشل في التقاط الشاشة، استخدام صورة تجريبية: {e}")
                screenshot = self.create_demo_screenshot()
                
            # Resize for better performance
            screenshot = screenshot.resize((800, 600), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG', optimize=True)
            img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            self.send_response(client_socket, 'screenshot', img_data)
            self.log_message("✅ تم إرسال لقطة الشاشة")
            
        except Exception as e:
            self.log_message(f"❌ خطأ في إرسال لقطة الشاشة: {e}")
            self.send_error(client_socket, f"Screenshot error: {e}")
            
    def create_demo_screenshot(self):
        """Create a demo screenshot when real capture fails"""
        img = Image.new('RGB', (800, 600), color='#2c3e50')
        draw = ImageDraw.Draw(img)
        
        # Title
        draw.text((50, 50), "Remote Desktop Server Demo", 
                 fill='white', font=None)
        
        # System info
        draw.text((50, 100), f"Server: {self.host}:{self.port}", 
                 fill='#3498db', font=None)
        draw.text((50, 130), f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                 fill='#e74c3c', font=None)
        draw.text((50, 160), f"Connected clients: {len(self.clients)}", 
                 fill='#27ae60', font=None)
        
        # Warning
        draw.text((50, 220), "هذا برنامج تعليمي للتحكم عن بعد", 
                 fill='#f39c12', font=None)
        draw.text((50, 250), "Educational Remote Desktop Software", 
                 fill='#f39c12', font=None)
        
        # Draw some graphics
        draw.rectangle([50, 300, 200, 400], outline='#9b59b6', width=2)
        draw.ellipse([250, 300, 400, 400], outline='#e67e22', width=2)
        
        return img
        
    def send_file_list(self, client_socket, path):
        try:
            if not os.path.exists(path):
                self.send_error(client_socket, f"Path does not exist: {path}")
                return
                
            if not os.path.isdir(path):
                self.send_error(client_socket, f"Path is not a directory: {path}")
                return
                
            files = []
            file_count = 0
            
            # Add parent directory option
            if path != '.' and path != '/':
                files.append({
                    'name': '..',
                    'size': 0,
                    'modified': '',
                    'is_dir': True
                })
            
            for item in os.listdir(path):
                try:
                    item_path = os.path.join(path, item)
                    stat = os.stat(item_path)
                    
                    files.append({
                        'name': item,
                        'size': stat.st_size,
                        'modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'is_dir': os.path.isdir(item_path)
                    })
                    
                    file_count += 1
                    
                except (OSError, PermissionError) as e:
                    self.log_message(f"⚠️ تعذر الوصول للملف {item}: {e}")
                    continue
                    
            self.send_response(client_socket, 'file_list', files)
            self.log_message(f"✅ تم إرسال قائمة {file_count} ملف/مجلد")
            
        except Exception as e:
            self.log_message(f"❌ خطأ في إرسال قائمة الملفات: {e}")
            self.send_error(client_socket, f"File list error: {e}")
            
    def send_file(self, client_socket, filename):
        try:
            if not filename:
                self.send_error(client_socket, "No filename provided")
                return
                
            if not os.path.exists(filename):
                self.send_error(client_socket, f"File not found: {filename}")
                return
                
            if not os.path.isfile(filename):
                self.send_error(client_socket, f"Not a file: {filename}")
                return
                
            file_size = os.path.getsize(filename)
            
            # Check file size limit (10MB)
            if file_size > 10 * 1024 * 1024:
                self.send_error(client_socket, f"File too large: {file_size} bytes (max 10MB)")
                return
                
            with open(filename, 'rb') as f:
                content = f.read()
                
            file_data = {
                'filename': os.path.basename(filename),
                'content': base64.b64encode(content).decode('utf-8'),
                'size': file_size
            }
            
            self.send_response(client_socket, 'file_download', file_data)
            self.log_message(f"✅ تم إرسال الملف: {filename} ({file_size} bytes)")
            
        except PermissionError:
            self.log_message(f"❌ لا يوجد صلاحية لقراءة الملف: {filename}")
            self.send_error(client_socket, f"Permission denied: {filename}")
        except Exception as e:
            self.log_message(f"❌ خطأ في إرسال الملف {filename}: {e}")
            self.send_error(client_socket, f"File send error: {e}")
            
    def stop(self):
        self.log_message("🛑 إيقاف الخادم...")
        self.running = False
        
        # Close all client connections
        for client in self.clients:
            try:
                client['socket'].close()
            except:
                pass
                
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
            
        self.log_message("✅ تم إيقاف الخادم")
        
    def get_server_info(self):
        return {
            'host': self.host,
            'port': self.port,
            'running': self.running,
            'clients': len(self.clients)
        }

def main():
    print("🖥️ Remote Desktop Server")
    print("=" * 50)
    
    # Server configuration
    HOST = 'localhost'  # Change to '0.0.0.0' to accept connections from any IP
    PORT = 9999
    
    server = RemoteDesktopServer(HOST, PORT)
    
    try:
        print(f"🚀 بدء تشغيل الخادم على {HOST}:{PORT}")
        print("📝 للإيقاف اضغط Ctrl+C")
        print("-" * 50)
        
        server.start()
        
    except KeyboardInterrupt:
        print("\n🛑 تم استقبال إشارة الإيقاف")
        server.stop()
        
    except Exception as e:
        print(f"❌ خطأ في الخادم: {e}")
        server.stop()

if __name__ == "__main__":
    main()