import cv2
from cvzone.HandTrackingModule import HandDetector
import mediapipe as mp
import math
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import numpy as np

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

volume = interface.QueryInterface(IAudioEndpointVolume)

min_vol, max_vol, increment = volume.GetVolumeRange()
print(f"Volume range: {min_vol} dB to {max_vol} dB")

current_vol = volume.GetMasterVolumeLevel()
print(f"Current volume: {current_vol} dB")


#################################################################

cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands()
#################################################################
#################################################################

while True:
    succsses, img = cap.read()
    #################################################################
    #################################################################

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        mp.solutions.drawing_utils.draw_landmarks(img, hand, mpHands.HAND_CONNECTIONS)
        lm_list = []
        for id, lm in enumerate(hand.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            #################################################################
            #################################################################

            lm_list.append([id, cx, cy])

            print(lm_list)
            #################################################################
            #################################################################

            if len(lm_list) > 8:
                x1, y1 = lm_list[4][1], lm_list[4][2]
                x2, y2 = lm_list[8][1], lm_list[8][2]

                cx, cy = int(x1 + x2) // 2, int(y1 + y2) // 2
                #################################################################
                #################################################################

                cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
                cv2.circle(img, (cx, cy), 10, (255, 255, 0), cv2.FILLED)

                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                length = int(math.hypot(x2 - x1, y2 - y1))
                #
                #
                hand_range = [30, 110]
                #
                vol = int(np.interp(length, hand_range, [-50.0, 0.0]))
                #
                volume.SetMasterVolumeLevel(vol, None)


    #################################################################
    #################################################################

    cv2.imshow("Image", img)
    cv2.waitKey(1)





#################################################################
#################################################################
#################################################################


# # راه‌اندازی تشخیص‌دهنده دست
# detector = HandDetector(detectionCon=0.8, maxHands=2)
# cap = cv2.VideoCapture(0)
# while True:
#     success, img = cap.read()
#     if not success:
#         break
#     # پیدا کردن دست‌ها
#     hands, img = detector.findHands(img)
#     if hands:
#         for hand in hands:
#             # اطلاعات کلی دست
#             handType = hand["type"]  # Left یا Right
#             lmList = hand["lmList"]  # مختصات نقاط لندمارک
#             bbox = hand["bbox"]      # باکس دور دست
#             center = hand["center"]  # مرکز دست
#             # print(f"Hand: {handType}, Center: {center}")
# 
#     cv2.imshow("Hand Detection", img)
#     if cv2.waitKey(1) & 0xFF == 27:  # ESC برای خروج
#         break
# cap.release()
# cv2.destroyAllWindows()

#################################################################
#################################################################
#################################################################

# import cv2
# import mediapipe as mp
#
# mpHands = mp.solutions.hands
# hands = mpHands.Hands(max_num_hands=1)
# mpDraw = mp.solutions.drawing_utils
#
# cap = cv2.VideoCapture(0)
#
# def fingers_up(hand_landmarks):
#     tips_ids = [4, 8, 12, 16, 20]
#     fingers = []
#     # Thumb
#     if hand_landmarks.landmark[tips_ids[0]].x < hand_landmarks.landmark[tips_ids[0] - 1].x:
#         fingers.append(1)
#     else:
#         fingers.append(0)
#     # 4 Fingers
#     for id in range(1,5):
#         if hand_landmarks.landmark[tips_ids[id]].y < hand_landmarks.landmark[tips_ids[id] - 2].y:
#             fingers.append(1)
#         else:
#             fingers.append(0)
#     return fingers
#
# while True:
#     success, img = cap.read()
#     imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     results = hands.process(imgRGB)
#
#     if results.multi_hand_landmarks:
#         handLms = results.multi_hand_landmarks[0]
#         mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
#
#         fingers = fingers_up(handLms)
#         # اگر همه انگشت ها باز بودند (برای سلام ساده)
#         if fingers == [1,1,1,1,1]:
#             cv2.putText(img, "Salam (Hello)", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 3)
#
#     cv2.imshow("Image", img)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()

#################################################################
#################################################################
#################################################################










