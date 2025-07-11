import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Start webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

for _ in range(10):
    cap.read()

# Repetition variables
count = 0
direction = 0
threshold_up = 160
threshold_down = 40
locked_on = False
blue_lock_frames = 0
blue_lock_required = 15

# Draw arms + shoulders only
selected_connections = [
    (12, 14), (14, 16),
    (11, 13), (13, 15),
    (11, 12)
]

# Angle calculation function
def find_angle(p1, p2, p3):
    a = np.array(p1, dtype=np.float32)
    b = np.array(p2, dtype=np.float32)
    c = np.array(p3, dtype=np.float32)
    try:
        radians = np.arccos(
            np.clip(np.dot(b - a, c - b) /
                    (np.linalg.norm(b - a) * np.linalg.norm(c - b)), -1.0, 1.0))
        return np.degrees(radians)
    except:
        return None

# Detect blue object near wrist
def is_holding_blue(img, wrist_x, wrist_y):
    radius = 60
    x1 = max(wrist_x - radius, 0)
    y1 = max(wrist_y - radius, 0)
    x2 = min(wrist_x + radius, img.shape[1])
    y2 = min(wrist_y + radius, img.shape[0])
    roi = img[y1:y2, x1:x2]

    if roi.size == 0:
        return False

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([95, 80, 40])
    upper_blue = np.array([135, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    blue_ratio = cv2.countNonZero(mask) / (roi.size / 3)

    return blue_ratio > 0.1

# Setup fullscreen window
cv2.namedWindow("Rep Counter", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Rep Counter", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    success, img = cap.read()
    if not success:
        continue

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        try:
            h, w, _ = img.shape
            shoulder = lm[12]
            elbow = lm[14]
            wrist = lm[16]

            p1 = [int(shoulder.x * w), int(shoulder.y * h)]
            p2 = [int(elbow.x * w), int(elbow.y * h)]
            p3 = [int(wrist.x * w), int(wrist.y * h)]

            angle = find_angle(p1, p2, p3)
            if angle is None or np.isnan(angle):
                continue

            if not locked_on:
                if is_holding_blue(img, p3[0], p3[1]):
                    blue_lock_frames += 1
                    cv2.putText(img, f'Detecting dumbbells... ({blue_lock_frames}/{blue_lock_required})',
                                (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    if blue_lock_frames >= blue_lock_required:
                        locked_on = True
                else:
                    blue_lock_frames = 0
                    cv2.putText(img, 'Show blue dumbbells to begin 💪',
                                (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                # Rep tracking mode
                cv2.putText(img, f'Angle: {int(angle)}', (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                if angle > threshold_up and direction == 0:
                    count += 1
                    direction = 1
                if angle < threshold_down and direction == 1:
                    direction = 0

                cv2.putText(img, f'Reps: {count}', (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

                if count >= 10:
                    cv2.putText(img, 'Workout complete! 💪', (50, 160),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    cv2.imshow("Rep Counter", img)
                    cv2.waitKey(3000)
                    break

            # Draw landmarks
            mp_draw.draw_landmarks(
                img,
                results.pose_landmarks,
                selected_connections,
                landmark_drawing_spec=mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2),
                connection_drawing_spec=mp_draw.DrawingSpec(color=(0, 128, 255), thickness=2)
            )

        except:
            pass

    cv2.imshow("Rep Counter", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
