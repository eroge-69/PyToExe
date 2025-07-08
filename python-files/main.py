import cv2
import mediapipe as mp
import math
import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Volume setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
minVol, maxVol = volume_ctrl.GetVolumeRange()[:2]

# Hand tracking setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
play_state = False  # To prevent repeated key presses

def get_distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

while True:
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lmList = []
            h, w, _ = img.shape
            for lm in hand_landmarks.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((cx, cy))

            if len(lmList) >= 21:
                # Volume control based on index and pinky
                index_tip = lmList[8]
                pinky_tip = lmList[4]
                distance = get_distance(index_tip, pinky_tip)

                vol = (distance - 30) / 150
                vol = max(0.0, min(1.0, vol))
                volume_ctrl.SetMasterVolumeLevelScalar(vol, None)

                # Draw visuals
                cv2.circle(img, index_tip, 10, (0, 255, 0), cv2.FILLED)
                cv2.circle(img, pinky_tip, 10, (0, 255, 0), cv2.FILLED)
                cv2.line(img, index_tip, pinky_tip, (255, 0, 0), 3)
                cv2.putText(img, f'Vol: {int(vol * 100)}%', (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                # Play/Pause detection: check if middle, ring, and pinky fingers are folded
                folded = []
                for tip_id, pip_id in [(12, 10), (16, 14), (20, 18)]:
                    folded.append(lmList[tip_id][1] > lmList[pip_id][1])  # tip lower than joint

                if all(folded):
                    if not play_state:
                        pyautogui.press('F1')
                        play_state = True  # To avoid multiple presses
                        cv2.putText(img, 'Play/Pause Triggered', (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    play_state = False

            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Hand Volume + Play/Pause", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
