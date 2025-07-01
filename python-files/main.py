import cv2
import mediapipe as mp
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol, max_vol = vol_range[0], vol_range[1]

cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

while True:
    success, frame = cap.read()
    if not success:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        def count_fingers(lm_list):
            fingers = []

            # Thumb
            fingers.append(1 if lm_list[4][1] > lm_list[3][1] else 0)

            # Other 4 fingers
            for tip in [8, 12, 16, 20]:
                fingers.append(1 if lm_list[tip][2] < lm_list[tip - 2][2] else 0)

            return sum(fingers)

        for hand_landmarks in result.multi_hand_landmarks:
            landmark_list = []
            h, w, _ = frame.shape
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmark_list.append((id, cx, cy))
                
        if len(landmark_list) == 21:
            finger_count = count_fingers(landmark_list)
            # print("Fingers up:", finger_count)
            
        current_vol = volume.GetMasterVolumeLevel()
        step = 0.5  # dB per frame

        if finger_count >= 4:
            current_vol = min(current_vol + step, max_vol)
        elif finger_count <= 1:
            current_vol = max(current_vol - step, min_vol)

        volume.SetMasterVolumeLevel(current_vol, None)

    # cv2.imshow("Webcam", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
