import cv2
import mediapipe as mp
import pyautogui

# راه‌اندازی MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# تابع شمارش انگشت‌ها
def count_fingers(hand_landmarks):
    tips_ids = [8, 12, 16, 20]
    fingers = []

    for tip_id in tips_ids:
        is_open = hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y
        fingers.append(is_open)

    thumb_open = hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x
    fingers.insert(0, thumb_open)

    return sum(fingers)

# اجرای دوربین
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        continue

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            finger_count = count_fingers(hand_landmarks)

            if finger_count == 1:
                pyautogui.scroll(50)
                print("⬆️ اسکرول بالا")

            elif finger_count == 2:
                pyautogui.scroll(-50)
                print("⬇️ اسکرول پایین")

            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("🖐️ Gesture Scroll", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
