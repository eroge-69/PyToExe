import cv2          
import mediapipe as mp
import pyautogui
import time
import math

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

prev_y_right = None
last_scroll_time = 0
cooldown = 1.0
last_left_gesture = None
volume_base_y = None
volume_mode = None


def count_fingers(hand, handedness):
    cnt = 0
    thresh = (hand.landmark[0].y * 100 - hand.landmark[9].y * 100) / 2

    if (hand.landmark[5].y * 100 - hand.landmark[8].y * 100) > thresh:
        cnt += 1
    if (hand.landmark[9].y * 100 - hand.landmark[12].y * 100) > thresh:
        cnt += 1
    if (hand.landmark[13].y * 100 - hand.landmark[16].y * 100) > thresh:
        cnt += 1
    if (hand.landmark[17].y * 100 - hand.landmark[20].y * 100) > thresh:
        cnt += 1
    if (handedness == "Right" and (hand.landmark[4].x < hand.landmark[3].x)) or \
       (handedness == "Left" and (hand.landmark[4].x > hand.landmark[3].x)):
        cnt += 1
    return cnt


def is_pinch(hand):
    tip = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    thumb = hand.landmark[mp_hands.HandLandmark.THUMB_TIP]
    dist = math.hypot(tip.x - thumb.x, tip.y - thumb.y)
    return dist < 0.07

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks and result.multi_handedness:
        for i, hand_landmarks in enumerate(result.multi_hand_landmarks):
            handedness = result.multi_handedness[i].classification[0].label
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if handedness == "Right":
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_y = index_tip.y * h

                if prev_y_right is not None:
                    dy = index_y - prev_y_right
                    if dy > 40:
                        current_time = time.time()
                        if current_time - last_scroll_time > cooldown:
                            pyautogui.scroll(-400)
                            last_scroll_time = current_time
                prev_y_right = index_y

                if is_pinch(hand_landmarks):
                    wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * h
                    if volume_base_y is None:
                        volume_base_y = wrist_y
                        volume_mode = "up"
                    delta = volume_base_y - wrist_y
                    if delta > 10:
                        pyautogui.press("volumeup")
                        volume_base_y = wrist_y
                    elif delta < -10:
                        pyautogui.press("volumedown")
                        volume_base_y = wrist_y
                else:
                    volume_base_y = None
                    volume_mode = None

            elif handedness == "Left":
                fingers = count_fingers(hand_landmarks, handedness)
                if fingers != last_left_gesture:
                    last_left_gesture = fingers
                    if fingers == 1:
                        pyautogui.press("space")

    else:
        prev_y_right = None
        volume_base_y = None
        volume_mode = None
        last_left_gesture = None

    cv2.imshow("Gesture Controller", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
