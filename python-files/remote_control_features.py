# === تحديث لملف client.py لتفعيل كل ميزات التحكم عن بُعد ===
import socket
import threading
import platform
import sys
import pyautogui
import pyperclip
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

def connect_to_server(server_ip, server_port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_ip, server_port))
        name = platform.node()
        s.send(name.encode())
        s.close()
    except Exception as e:
        print(f"Error connecting to server: {e}")

def command_listener():
    sock = socket.socket()
    sock.bind(("0.0.0.0", 9998))
    sock.listen(1)
    while True:
        conn, addr = sock.accept()
        try:
            cmd = conn.recv(2048).decode()
            if cmd.startswith("move:"):
                x, y = map(int, cmd.split(":")[1].split(","))
                pyautogui.moveTo(x, y)
            elif cmd.startswith("click:"):
                btn = cmd.split(":")[1]
                pyautogui.click(button=btn)
            elif cmd.startswith("type:"):
                text = cmd.split(":", 1)[1]
                pyautogui.write(text)
            elif cmd.startswith("hotkey:"):
                keys = cmd.split(":")[1].split(",")
                pyautogui.hotkey(*keys)
            elif cmd.startswith("paste:"):
                text = cmd.split(":", 1)[1]
                pyperclip.copy(text)
                pyautogui.hotkey("ctrl", "v")
        except Exception as e:
            print(f"Command error: {e}")
        finally:
            conn.close()

class TrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.tray = QSystemTrayIcon(QIcon("icon.png"))
        self.tray.setToolTip("Client App")

        menu = QMenu()
        connect_action = QAction("Connect to Server")
        connect_action.triggered.connect(lambda: connect_to_server("192.168.1.100", 9999))
        menu.addAction(connect_action)
        menu.addAction(QAction("Exit", self.app.quit))

        self.tray.setContextMenu(menu)
        self.tray.show()

        threading.Thread(target=command_listener, daemon=True).start()

        sys.exit(self.app.exec_())

if __name__ == '__main__':
    TrayApp()

# الأوامر الممكن تنفيذها:
# move:100,200          => لتحريك مؤشر الفأرة
# click:left             => للنقر بزر الفأرة الأيسر (أو right/ middle)
# type:hello world       => لكتابة نص
# hotkey:ctrl,c          => لتنفيذ اختصارات مثل نسخ/لصق/حفظ
# paste:some text        => للصق نص باستخدام الحافظة
