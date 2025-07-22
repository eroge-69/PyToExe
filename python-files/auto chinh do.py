import pyautogui, pytesseract, cv2, numpy as np, threading, time, keyboard
from PIL import ImageGrab

# ---- Cấu hình ----
F_DELAY = 3         # thời gian giữa các lần nhấn F
PK_DELAY = 0.5      # thời gian giữa các lần PK
stop_key = '/'      # nút dừng gấp
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Vùng phát hiện nút F và tên người chơi (điều chỉnh nếu khác)
DETECT_F_REGION = (800, 650, 1024, 768)
DETECT_PLAYER_REGION = (40, 130, 300, 300)
running = True

def detect_text(region, keyword):
    img = ImageGrab.grab(bbox=region)
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang='eng')
    return keyword.lower() in text.lower()

def auto_follow_pk():
    global running
    while running:
        # Nếu chưa theo sau thì nhấn F
        if not detect_text(DETECT_F_REGION, "bỏ theo sau"):
            pyautogui.press('f')
            time.sleep(F_DELAY)
            continue
        
        # Nếu có người chơi -> nhấn chuột trái để PK
        if detect_text(DETECT_PLAYER_REGION, ""):
            pyautogui.click()
            time.sleep(PK_DELAY)
        else:
            time.sleep(0.2)

def listen_stop():
    global running
    keyboard.wait(stop_key)
    running = False
    print(">>> Tool đã dừng!")

if __name__ == "__main__":
    print(">>> Tool auto Chinh Đồ đang chạy. Nhấn '/' để dừng.")
    threading.Thread(target=listen_stop, daemon=True).start()
    auto_follow_pk()
