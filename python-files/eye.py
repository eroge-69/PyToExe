import cv2
import mediapipe as mp
import pyautogui
import time
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
screen_w, screen_h = pyautogui.size()
prev_x, prev_y = 0, 0
smoothing = 5
blink_counter = 0
blink_start_time = 0
blink_time_window = 1.5
def eye_aspect_ratio(landmarks, eye_indices, frame_w, frame_h):
    points = [(int(landmarks[idx].x * frame_w), int(landmarks[idx].y * frame_h)) for idx in eye_indices]
    vertical_1 = ((points[1][1] - points[5][1]) ** 2) ** 0.5
    vertical_2 = ((points[2][1] - points[4][1]) ** 2) ** 0.5
    horizontal = ((points[0][0] - points[3][0]) ** 2) ** 0.5
    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return ear
right_eye_indices = [33, 160, 158, 133, 153, 144]
EAR_THRESHOLD = 0.25
eye_closed = False
while True:
    success, frame = cam.read()
    if not success:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb_frame)
    landmarks = result.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape
    if landmarks:
        face = landmarks[0]
        lm = face.landmark
        nose_tip = lm[1]
        x = int(nose_tip.x * frame_w)
        y = int(nose_tip.y * frame_h)
        cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)
        target_x = nose_tip.x * screen_w
        target_y = nose_tip.y * screen_h
        smooth_x = prev_x + (target_x - prev_x) / smoothing
        smooth_y = prev_y + (target_y - prev_y) / smoothing
        pyautogui.moveTo(smooth_x, smooth_y)
        prev_x, prev_y = smooth_x, smooth_y
        ear = eye_aspect_ratio(lm, right_eye_indices, frame_w, frame_h)
        cv2.putText(frame, f"EAR: {ear:.2f}", (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        if ear < EAR_THRESHOLD:
            if not eye_closed:
                eye_closed = True
                blink_counter += 1
                if blink_counter == 1:
                    blink_start_time = time.time()
        else:
            eye_closed = False
        if blink_counter > 0 and (time.time() - blink_start_time) > blink_time_window:
            if blink_counter == 2:
                print("Left Click triggered")
                pyautogui.click(button='left')
            elif blink_counter == 3:
                print("Right Click triggered")
                pyautogui.click(button='right')
            blink_counter = 0
    cv2.imshow("Nose Tracker with Blink Click", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()