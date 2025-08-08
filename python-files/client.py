import socket
import pyautogui
import io

SERVER_IP = "127.0.0.1"  # غيّر هذا إلى IP جهاز الـ Mac
SERVER_PORT = 5000
PASSWORD = "Bmw_m3"  # كلمة مرور بسيطة للمصادقة

def send_screenshot():
    screenshot = pyautogui.screenshot()
    img_bytes = io.BytesIO()
    screenshot.save(img_bytes, format='PNG')
    img_data = img_bytes.getvalue()
    return img_data

def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, SERVER_PORT))
        s.send(PASSWORD.encode())  # تحقق كلمة المرور

        while True:
            command = s.recv(1024).decode()
            if command == "screenshot":
                img_data = send_screenshot()
                s.sendall(len(img_data).to_bytes(4, 'big'))
                s.sendall(img_data)
            elif command == "exit":
                break
    except Exception as e:
        pass
    finally:
        s.close()

if __name__ == "__main__":
    main()
