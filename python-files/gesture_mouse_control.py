import cv2
import mediapipe as mp
import pyautogui
import time
import json
import os
import sys


# ==== Configuration ====
CAMERA_INDEX = 0
SENSITIVITY = 3.5
SMOOTHING_FACTOR = 0.4
# ========================

# Load gesture config
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(base_path, "gesture_config.json")
with open(config_path, "r") as f:
    config = json.load(f)

# Gesture to Finger Mapping (static map for all known gestures)
FINGER_MAP = {
    "Fist":        [False, False, False, False],
    "Hand Open":   [True, True, True, True],
    "Victory":     [True, True, False, False],
    "Palm":        [True, True, True, True],
    "Swipe Left":  [False, True, True, False],   # You can define this better
    "Swipe Right": [True, False, False, True],   # You can define this better
}

# Load dynamic mappings from config
gesture_to_key = {}
for key, gesture in config.get("KeyMappings", {}).items():
    gesture_to_key[gesture] = key  # Inverse mapping

# Setup
cap = cv2.VideoCapture(CAMERA_INDEX)
hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

last_pressed_time = {}
press_interval = 1.0  # seconds between same key presses

smooth_x, smooth_y = None, None

def get_finger_states(landmarks):
    return [
        landmarks[8].y < landmarks[6].y,
        landmarks[12].y < landmarks[10].y,
        landmarks[16].y < landmarks[14].y,
        landmarks[20].y < landmarks[18].y
    ]

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            fingers_up = get_finger_states(hand_landmarks.landmark)

            for gesture_name, expected_fingers in FINGER_MAP.items():
                if fingers_up == expected_fingers:
                    mapped_key = gesture_to_key.get(gesture_name)
                    if mapped_key:
                        now = time.time()
                        last_time = last_pressed_time.get(mapped_key, 0)
                        if now - last_time > press_interval:
                            pyautogui.press(mapped_key.lower())
                            last_pressed_time[mapped_key] = now
                            print(f"[INFO] Gesture '{gesture_name}' → Key '{mapped_key}'")

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
