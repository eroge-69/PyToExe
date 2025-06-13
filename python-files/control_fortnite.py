
import cv2
import mediapipe as mp
import pyautogui

mp_face = mp.solutions.face_mesh
mp_hands = mp.solutions.hands

face = mp_face.FaceMesh()
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)

screen_w, screen_h = pyautogui.size()

def fingers_up(hand_landmarks):
    finger_tips = [8, 12, 16, 20]
    fingers = []
    for tip in finger_tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_results = face.process(rgb_frame)
    hand_results = hands.process(rgb_frame)

    h, w, _ = frame.shape

    if face_results.multi_face_landmarks:
        landmarks = face_results.multi_face_landmarks[0].landmark
        nose = landmarks[1]
        x = int(nose.x * screen_w)
        y = int(nose.y * screen_h)
        pyautogui.moveTo(x, y)

        top_lip = landmarks[13]
        bottom_lip = landmarks[14]
        mouth_open = bottom_lip.y - top_lip.y
        if mouth_open > 0.05:
            pyautogui.click()

        left_eye = landmarks[159].y
        left_bottom = landmarks[145].y
        if (left_bottom - left_eye) < 0.01:
            pyautogui.press('q')

    if hand_results.multi_hand_landmarks:
        for hand_landmarks, hand_type in zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness):
            label = hand_type.classification[0].label
            fingers = fingers_up(hand_landmarks)

            if fingers == [1, 0, 0, 0]:
                if label == "Right":
                    pyautogui.keyDown('w')
                elif label == "Left":
                    pyautogui.keyDown('s')
            else:
                if label == "Right":
                    pyautogui.keyUp('w')
                elif label == "Left":
                    pyautogui.keyUp('s')

            if fingers == [0, 1, 1, 1]:
                if label == "Right":
                    pyautogui.press('d')
                elif label == "Left":
                    pyautogui.press('a')

    cv2.imshow("Fortnite Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
