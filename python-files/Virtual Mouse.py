import cv2
import mediapipe as mp
import pyautogui

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
screen_w, screen_h = pyautogui.size()  # Get screen size

# Initialize webcam with higher resolution
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Wider frame
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Taller frame

hand_model = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror the frame horizontally
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hand_model.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get index finger tip coordinates
            index_finger = hand_landmarks.landmark[8]  # Landmark ID 8 = Index finger tip
            x, y = int(index_finger.x * screen_w), int(index_finger.y * screen_h)

            # Move mouse cursor
            pyautogui.moveTo(x, y)

    cv2.imshow("Virtual Mouse (Mirrored)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
