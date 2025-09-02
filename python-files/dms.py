import cv2
import numpy as np
import mediapipe as mp
import time
import sys, os

# =========================
# Helper to load resources (works in .exe)
# =========================
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):  # PyInstaller temp folder
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# =========================
# Splash screen: Load logo + project name
# =========================
logo_path = resource_path("C:/yolo_inference/elektronika.png")  # we’ll bundle this file with exe
logo = cv2.imread(logo_path)
if logo is None:
    print("Error: Logo not found ->", logo_path)

# Fullscreen window
cv2.namedWindow("Driver Monitoring", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Driver Monitoring", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

if logo is not None:
    screen_h, screen_w = 720, 1280  # adjust to your HDMI resolution
    scale = min(screen_w/logo.shape[1], screen_h/logo.shape[0], 1.0)
    logo_resized = cv2.resize(logo, (int(logo.shape[1]*scale), int(logo.shape[0]*scale)))

    splash = np.zeros((screen_h, screen_w, 3), dtype=np.uint8)

    y_offset = (screen_h - logo_resized.shape[0]) // 2 - 50
    x_offset = (screen_w - logo_resized.shape[1]) // 2
    splash[y_offset:y_offset+logo_resized.shape[0], x_offset:x_offset+logo_resized.shape[1]] = logo_resized

    # Add project name below logo
    text = "Driver Monitoring System"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    thickness = 3
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (screen_w - text_size[0]) // 2
    text_y = y_offset + logo_resized.shape[0] + 60
    cv2.putText(splash, text, (text_x, text_y), font, font_scale, (255,255,255), thickness, cv2.LINE_AA)

    cv2.imshow("Driver Monitoring", splash)
    cv2.waitKey(1500)  # show for 1.5 seconds

# =========================
# Mediapipe setup
# =========================
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# =========================
# Colors and buttons
# =========================
COLOR_INACTIVE = (50, 80, 80)
COLOR_ACTIVE = (0, 0, 255)
WHITE = (255, 255, 255)

buttons = {
    "Yawning": (50, 100, 180, 50),
    "Water Drinking": (250, 100, 200, 50),
    "Smoking": (470, 100, 150, 50),
    "Eyes Closing": (50, 170, 180, 50),
    "On a call": (250, 170, 150, 50),
}

def draw_button(img, text, rect, active=False):
    x, y, w, h = rect
    color = COLOR_ACTIVE if active else COLOR_INACTIVE
    cv2.rectangle(img, (x, y), (x + w, y + h), color, -1, cv2.LINE_AA)
    cv2.rectangle(img, (x, y), (x + w, y + h), WHITE, 3, cv2.LINE_AA)
    cv2.putText(img, text, (x + 15, y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2, cv2.LINE_AA)

def dist(idx1, idx2, lm, w, h):
    p1 = np.array([lm[idx1].x * w, lm[idx1].y * h])
    p2 = np.array([lm[idx2].x * w, lm[idx2].y * h])
    return np.linalg.norm(p1 - p2)

# =========================
# Camera init
# =========================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# =========================
# Detection flags and thresholds
# =========================
det_yawn = det_smoke = det_phone = det_close = det_drink = False
MAR_THRESHOLD = 0.6
EAR_THRESHOLD = 0.2
CONFIRM_FRAMES = 10
yawn_frame_count = 0

print("Driver Monitoring System Started. Press ESC to exit.")

# =========================
# Main loop
# =========================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_mesh.process(rgb_frame)
    hands_res = hands.process(rgb_frame)

    # Reset detections
    det_yawn = det_smoke = det_phone = det_close = det_drink = False

    # Face detections
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            MAR = dist(13, 14, face_landmarks.landmark, w, h) / dist(61, 291, face_landmarks.landmark, w, h)

            ear_left = dist(159, 145, face_landmarks.landmark, w, h) / dist(33, 133, face_landmarks.landmark, w, h)
            ear_right = dist(386, 374, face_landmarks.landmark, w, h) / dist(362, 263, face_landmarks.landmark, w, h)
            EAR = (ear_left + ear_right) / 2

            det_close = EAR < EAR_THRESHOLD

            if MAR > MAR_THRESHOLD:
                yawn_frame_count += 1
                if yawn_frame_count >= CONFIRM_FRAMES:
                    det_yawn = True
            else:
                yawn_frame_count = 0

            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )

    # Hand detections
    if hands_res.multi_hand_landmarks and results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0].landmark
        mouth = (lm[13].x * w, lm[13].y * h)
        earL = (lm[234].x * w, lm[234].y * h)
        earR = (lm[454].x * w, lm[454].y * h)

        for hand in hands_res.multi_hand_landmarks:
            hand_pts = [(pt.x * w, pt.y * h) for pt in hand.landmark]
            hand_center = np.mean(hand_pts, axis=0)

            if np.linalg.norm(hand_center - mouth) < 50:
                det_smoke = True
            if np.linalg.norm(hand_center - earL) < 50 or np.linalg.norm(hand_center - earR) < 50:
                det_phone = True
            if det_smoke and hand_center[1] < mouth[1] - 30:
                det_drink = True

    # Draw buttons
    for name, rect in buttons.items():
        active = {
            "Yawning": det_yawn,
            "Water Drinking": det_drink,
            "Smoking": det_smoke,
            "Eyes Closing": det_close,
            "On a call": det_phone,
        }[name]
        draw_button(frame, name, rect, active)

    cv2.imshow("Driver Monitoring", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

# =========================
# Cleanup
# =========================
cap.release()
cv2.destroyAllWindows()
print("Driver Monitoring System Stopped.")
