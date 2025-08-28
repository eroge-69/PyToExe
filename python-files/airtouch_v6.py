import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
import webbrowser
import winsound

# Mediapipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

# Keyboard layout (Right hand typing)
typing_keys = [
    ["1","2","3","4","5","6","7","8","9","0"],
    ["Q","W","E","R","T","Y","U","I","O","P"],
    ["A","S","D","F","G","H","J","K","L"],
    ["Z","X","C","V","B","N","M","Space"]
]

# Left-hand control bar (added arrows)
control_keys = ["Google", "YouTube", "Instagram", "Enter", "Bksp",
                "Shift", "Caps", "←", "↑", "↓", "→"]

# Colors
key_color = (0, 255, 255)
text_color = (0, 0, 0)

# Typing buffer
typed_text = ""

# Caps / Shift states
caps_lock = False
shift_active = False

# Cooldown
last_action_time = 0
cooldown = 1.0

def play_beep():
    winsound.Beep(1000, 150)

# Draw typing keyboard (bottom)
def draw_typing_keyboard(img):
    frame_h, frame_w = img.shape[:2]
    rows = len(typing_keys)
    max_cols = max(len(r) for r in typing_keys)
    key_w = frame_w // (max_cols + 1)
    key_h = frame_h // (rows + 4)
    start_x = 10
    start_y = frame_h - (key_h * rows) - 150
    for row_idx, row in enumerate(typing_keys):
        for col_idx, key in enumerate(row):
            x1 = start_x + col_idx * key_w
            y1 = start_y + row_idx * key_h
            x2 = x1 + key_w - 5
            y2 = y1 + key_h - 5
            cv2.rectangle(img, (x1, y1), (x2, y2), key_color, -1)
            cv2.putText(img, key, (x1 + 15, y1 + key_h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
    return img, key_w, key_h, start_x, start_y

# Draw control keys (top row)
def draw_control_bar(img):
    frame_h, frame_w = img.shape[:2]
    key_w = frame_w // (len(control_keys) + 1)
    key_h = 70
    start_x = 10
    start_y = 50
    for idx, key in enumerate(control_keys):
        x1 = start_x + idx * key_w
        y1 = start_y
        x2 = x1 + key_w - 5
        y2 = y1 + key_h
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 200, 100), -1)
        cv2.putText(img, key, (x1 + 10, y1 + key_h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
    return img, key_w, key_h, start_x, start_y

# Get index finger tip
def get_finger_pos(hand_landmarks, frame_w, frame_h):
    index_finger = hand_landmarks.landmark[8]
    return int(index_finger.x * frame_w), int(index_finger.y * frame_h)

# Pinch check
def is_pinch(hand_landmarks):
    thumb = hand_landmarks.landmark[4]
    index = hand_landmarks.landmark[8]
    dist = np.sqrt((thumb.x - index.x)**2 + (thumb.y - index.y)**2)
    return dist < 0.05

# Detect left vs right hand
def get_hand_label(hand_info):
    if hand_info.classification[0].label == "Left":
        return "Left"
    return "Right"

# Main loop
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cv2.namedWindow("AirTouch Keyboard", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    frame_h, frame_w = frame.shape[:2]

    # Draw keyboards
    frame, t_key_w, t_key_h, t_start_x, t_start_y = draw_typing_keyboard(frame)
    frame, c_key_w, c_key_h, c_start_x, c_start_y = draw_control_bar(frame)

    if result.multi_hand_landmarks and result.multi_handedness:
        for hand_landmarks, hand_info in zip(result.multi_hand_landmarks, result.multi_handedness):
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            x, y = get_finger_pos(hand_landmarks, frame_w, frame_h)
            cv2.circle(frame, (x, y), 15, (255, 0, 0), -1)

            if is_pinch(hand_landmarks) and time.time() - last_action_time > cooldown:
                hand_label = get_hand_label(hand_info)

                # Left hand → control keys
                if hand_label == "Left":
                    for idx, key in enumerate(control_keys):
                        x1 = c_start_x + idx * c_key_w
                        y1 = c_start_y
                        x2 = x1 + c_key_w - 5
                        y2 = y1 + c_key_h
                        if x1 < x < x2 and y1 < y < y2:
                            play_beep()
                            if key == "Enter":
                                pyautogui.press('enter')
                            elif key == "Bksp":
                                pyautogui.press('backspace')
                                typed_text = typed_text[:-1]
                            elif key == "Google": webbrowser.open("https://www.google.com")
                            elif key == "YouTube": webbrowser.open("https://www.youtube.com")
                            elif key == "Instagram": webbrowser.open("https://www.instagram.com")
                            elif key == "Shift": shift_active = True
                            elif key == "Caps": caps_lock = not caps_lock
                            elif key in ["←", "↑", "↓", "→"]:
                                pyautogui.press({'←':'left','↑':'up','↓':'down','→':'right'}[key])

                            last_action_time = time.time()

                # Right hand → typing keys
                elif hand_label == "Right":
                    for row_idx, row in enumerate(typing_keys):
                        for col_idx, key in enumerate(row):
                            x1 = t_start_x + col_idx * t_key_w
                            y1 = t_start_y + row_idx * t_key_h
                            x2 = x1 + t_key_w - 5
                            y2 = y1 + t_key_h - 5
                            if x1 < x < x2 and y1 < y < y2:
                                play_beep()
                                char = key
                                if char == "Space":
                                    typed_text += " "
                                    pyautogui.press('space')
                                else:
                                    if shift_active ^ caps_lock:
                                        char = char.upper()
                                    else:
                                        char = char.lower()
                                    typed_text += char
                                    pyautogui.typewrite(char)
                                if shift_active:  # reset after one use
                                    shift_active = False
                                last_action_time = time.time()

    # Show typed text
    cv2.putText(frame, typed_text, (30, frame_h - 250),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 2)

    cv2.imshow("AirTouch Keyboard", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
