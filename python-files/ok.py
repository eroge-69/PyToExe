import cv2
import numpy as np
import mediapipe as mp
import math
from collections import deque

# --- Sozlamalar ---
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
PROCESS_WIDTH = 320
PROCESS_HEIGHT = 240

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)

canvas = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)

# --- O'zgaruvchilar ---
points = deque(maxlen=5)
palette = {
    'green': (0, 255, 0),
    'red': (0, 0, 255),
    'blue': (255, 100, 0),
    'white': (255, 255, 255)
}
current_color = palette['white']
palette_rects = {}

thicknesses = {
    'thin': 5,
    'medium': 12,
    'thick': 25
}
current_thickness = thicknesses['medium']
thickness_circles = {}
is_paused = False

# --- Funksiyalar ---
def draw_ui(frame):
    """Ekranga rang va qalinlik tanlash interfeysini chizadi"""
    # Ranglar (chap tomonda)
    start_x, start_y, rect_size = 10, 10, 50
    for i, (name, color) in enumerate(palette.items()):
        x1 = start_x + i * (rect_size + 10)
        y1 = start_y
        x2 = x1 + rect_size
        y2 = y1 + rect_size
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
        if color == current_color:
            cv2.rectangle(frame, (x1-3, y1-3), (x2+3, y2+3), (255, 255, 255), 3)
        palette_rects[name] = (x1, y1, x2, y2)
    
    # Qalinliklar (o'ng tomonda)
    thickness_start_x = FRAME_WIDTH - (len(thicknesses) * (rect_size + 20)) # O'ng tomondan boshlash
    for i, (name, thickness) in enumerate(thicknesses.items()):
        center_x = thickness_start_x + i * (rect_size + 20)
        center_y = start_y + rect_size // 2
        radius = thickness // 2 + 2
        cv2.circle(frame, (center_x, center_y), radius, (200, 200, 200), -1)
        if thickness == current_thickness:
            cv2.circle(frame, (center_x, center_y), radius+3, (255, 255, 255), 3)
        thickness_circles[name] = (center_x, center_y, radius)

def count_fingers(hand_landmarks):
    tips = [8, 12, 16, 20]
    count = 0
    try:
        if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
            count += 1
    except: pass
    for tip in tips:
        try:
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                count += 1
        except: pass
    return count

# --- Asosiy tsikl ---
while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('p'): is_paused = not is_paused
    if key == ord('c'): canvas.fill(0)
    if key == 27: break

    draw_ui(frame)

    if is_paused:
        cv2.putText(frame, "PAUSED", (FRAME_WIDTH//2 - 100, FRAME_HEIGHT//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
    else:
        small_frame = cv2.resize(frame, (PROCESS_WIDTH, PROCESS_HEIGHT))
        rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                x = int(hand.landmark[8].x * FRAME_WIDTH)
                y = int(hand.landmark[8].y * FRAME_HEIGHT)
                fingers = count_fingers(hand)

                if fingers == 1: # CHIZISH REJIMI
                    points.appendleft((x, y))
                    for i in range(1, len(points)):
                        if points[i-1] is None or points[i] is None: continue
                        cv2.line(canvas, points[i-1], points[i], current_color, current_thickness)

                elif fingers == 2: # KURSOR / TANLASH REJIMI
                    points.clear()
                    cv2.circle(frame, (x, y), 15, current_color, -1)
                    # Rang tanlash
                    for name, (x1, y1, x2, y2) in palette_rects.items():
                        if x1 < x < x2 and y1 < y < y2:
                            current_color = palette[name]
                            break
                    # Qalinlik tanlash
                    for name, (cx, cy, r) in thickness_circles.items():
                        if math.hypot(cx - x, cy - y) < r + 5:
                            current_thickness = thicknesses[name]
                            break
                
                elif fingers >= 4: # O'CHIRG'ICH REJIMI
                    points.clear()
                    cv2.circle(canvas, (x, y), 50, (0, 0, 0), -1)
                    cv2.circle(frame, (x, y), 25, (0, 0, 0), 4)

                else: # BOSHQA HOLATLAR
                    points.clear()

    # Natijani ko'rsatish
    frame_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, inv_mask = cv2.threshold(frame_gray, 1, 255, cv2.THRESH_BINARY_INV)
    frame = cv2.bitwise_and(frame, frame, mask=inv_mask)
    combined = cv2.add(frame, canvas)

    # Brending yozuvini qo'shish
    cv2.putText(combined, "Powered By Shamshodbek", (FRAME_WIDTH - 400, FRAME_HEIGHT - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (150, 150, 150), 2)

    cv2.imshow("Virtual Doska", combined)

cap.release()
cv2.destroyAllWindows()