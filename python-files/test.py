import cv2
import mediapipe as mp
import pyautogui

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

finger_tips_ids = [4, 8, 12, 16, 20]
finger_pip_ids = [3, 6, 10, 14, 18]

last_gesture = None  # 'open', 'closed', or None

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    gesture = None

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                lm_list.append((int(lm.x * w), int(lm.y * h)))

            if lm_list:
                fingers_up = []

                # Thumb (horizontal detection)
                if lm_list[4][0] > lm_list[3][0]:
                    fingers_up.append(1)  # thumb up
                else:
                    fingers_up.append(0)

                # Other fingers (vertical detection)
                for tip_id, pip_id in zip(finger_tips_ids[1:], finger_pip_ids[1:]):
                    if lm_list[tip_id][1] < lm_list[pip_id][1]:
                        fingers_up.append(1)
                    else:
                        fingers_up.append(0)

                if fingers_up == [1, 1, 1, 1, 1]:
                    gesture = 'open'
                elif fingers_up == [0, 0, 0, 0, 0]:
                    gesture = 'closed'
                else:
                    gesture = 'other'

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

        # Detect transition from open to closed
        if last_gesture == 'open' and gesture == 'closed':
            print("Action: Open → Closed detected! Minimizing all windows...")
            pyautogui.hotkey('win', 'd')

        # Update last gesture
        if gesture in ['open', 'closed']:
            last_gesture = gesture

    else:
        last_gesture = None

    cv2.imshow("Hand Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
