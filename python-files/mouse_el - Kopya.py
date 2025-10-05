import cv2
import mediapipe as mp
import pyautogui
import time

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

screen_width, screen_height = pyautogui.size()
prev_x, prev_y = 0, 0
smooth_factor = 5
clicking = False  # Tıklama durumu

# Ekran köşelerine rahat ulaşmak için ölçek
scale_x = 1.2 # X ekseni hassasiyeti
scale_y = 1.2  # Y ekseni hassasiyeti

with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            orta1 = hand_landmarks.landmark[12].y
            orta2 = hand_landmarks.landmark[9].y

            x = hand_landmarks.landmark[8].x
            y = hand_landmarks.landmark[8].y
            thumb_y = hand_landmarks.landmark[4].y

            # Ekran koordinatlarını ölçekle
            screen_x = int(x * screen_width * scale_x)
            screen_y = int(y * screen_height * scale_y)

            # Ekran dışına taşmayı engelle
            screen_x = max(0, min(screen_x, screen_width - 1))
            screen_y = max(0, min(screen_y, screen_height - 1))

            # Smooth hareket
            smooth_factor = 3
            smooth_x = prev_x + (screen_x - prev_x) / smooth_factor
            smooth_y = prev_y + (screen_y - prev_y) / smooth_factor

            if orta1 > orta2:
                pyautogui.moveTo(smooth_x, smooth_y)

            prev_x, prev_y = smooth_x, smooth_y

            # Tıklama kontrolü (işaret parmağı ve başparmak ucu yakınsa bas)
            distance = abs(hand_landmarks.landmark[8].y - hand_landmarks.landmark[4].y)
            if distance < 0.05 and not clicking:
                pyautogui.mouseDown()
                clicking = True
            elif distance >= 0.03 and clicking:
                pyautogui.mouseUp()
                clicking = False

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Hand Mouse Control", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
