import cv2
import mediapipe as mp
import numpy as np
import time
import random
import datetime

mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# --- MODE SELECTION ---
# Use hand gestures to change mode:
# Single Open Hand: Eye tracks face (with Glitch effect) -> current_mode = 1
# Two Open Hands: Clock mode (with Glitch effect) -> current_mode = 2
# Other Hand Poses: MediaPipe lines of the whole body (Theme-compatible background) -> current_mode = 3
current_mode = 1
last_mode_change_time = 0
MODE_CHANGE_DELAY = 2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

# Set up the window for full screen
cv2.namedWindow('Virtual Eye Tracking', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('Virtual Eye Tracking', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

with mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh, \
    mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7) as hands, \
    mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:

    last_iris_draw_x = None
    last_iris_draw_y = None

    FINGER_TIPS = [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.INDEX_FINGER_TIP,
                   mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP,
                   mp_hands.HandLandmark.PINKY_TIP]
    FINGER_P_JOINTS = [mp_hands.HandLandmark.THUMB_IP, mp_hands.HandLandmark.INDEX_FINGER_PIP,
                       mp_hands.HandLandmark.MIDDLE_FINGER_PIP, mp_hands.HandLandmark.RING_FINGER_PIP,
                       mp_hands.HandLandmark.PINKY_PIP]

    def is_finger_extended(hand_landmarks, tip_idx, pip_idx):
        return hand_landmarks.landmark[tip_idx].y < hand_landmarks.landmark[pip_idx].y

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        frame = cv2.flip(frame, 1)
        img_h, img_w, _ = frame.shape

        if current_mode == 3:
            canvas = np.full((img_h, img_w, 3), (20, 0, 20), dtype=np.uint8)
        else:
            purple_color = (200, 0, 200)
            canvas = np.full((img_h, img_w, 3), purple_color, dtype=np.uint8)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_results = face_mesh.process(rgb_frame)
        hand_results = hands.process(rgb_frame)
        pose_results = pose.process(rgb_frame)

        current_time_for_mode_change = time.time()
        if hand_results.multi_hand_landmarks and (current_time_for_mode_change - last_mode_change_time > MODE_CHANGE_DELAY):
            num_open_hands = 0

            for hand_landmarks in hand_results.multi_hand_landmarks:
                thumb_extended = is_finger_extended(hand_landmarks, FINGER_TIPS[0], FINGER_P_JOINTS[0])
                index_extended = is_finger_extended(hand_landmarks, FINGER_TIPS[1], FINGER_P_JOINTS[1])
                middle_extended = is_finger_extended(hand_landmarks, FINGER_TIPS[2], FINGER_P_JOINTS[2])
                ring_extended = is_finger_extended(hand_landmarks, FINGER_TIPS[3], FINGER_P_JOINTS[3])
                pinky_extended = is_finger_extended(hand_landmarks, FINGER_TIPS[4], FINGER_P_JOINTS[4])

                if thumb_extended and index_extended and middle_extended and ring_extended and pinky_extended:
                    num_open_hands += 1

            if num_open_hands >= 2:
                if current_mode != 2:
                    current_mode = 2
                    last_mode_change_time = current_time_for_mode_change
                    print("Mode 2: Clock Mode (Two Open Hands)")
            elif num_open_hands == 1:
                if current_mode != 1:
                    current_mode = 1
                    last_mode_change_time = current_time_for_mode_change
                    print("Mode 1: Face Tracking (Single Open Hand)")
            else:
                if current_mode != 3:
                    current_mode = 3
                    last_mode_change_time = current_time_for_mode_change
                    print("Mode 3: MediaPipe Lines (Other Hand Poses)")

        fixed_eye_center = (img_w // 2, img_h // 2)
        fixed_eye_axes = (150, 100)
        fixed_iris_radius = 40
        fixed_pupil_radius = int(fixed_iris_radius * 0.4)
        highlight_radius = int(fixed_iris_radius * 0.3)

        max_iris_horizontal_move = fixed_eye_axes[0] - fixed_iris_radius - 10
        max_iris_vertical_move = fixed_eye_axes[1] - fixed_iris_radius - 10

        if current_mode == 1:
            if face_results.multi_face_landmarks:
                face_landmarks = face_results.multi_face_landmarks[0]

                face_target_lm = face_landmarks.landmark[1]
                face_target_x = int(face_target_lm.x * img_w)
                face_target_y = int(face_target_lm.y * img_h)

                dx = face_target_x - fixed_eye_center[0]
                dy = face_target_y - fixed_eye_center[1]

                dist = np.sqrt(dx**2 + dy**2)
                if dist > 0:
                    max_detection_distance = img_w / 3
                    movement_scale = min(1.0, dist / max_detection_distance)

                    iris_offset_x = int(dx / dist * max_iris_horizontal_move * movement_scale)
                    iris_offset_y = int(dy / dist * max_iris_vertical_move * movement_scale)
                else:
                    iris_offset_x = 0
                    iris_offset_y = 0

                iris_draw_x = fixed_eye_center[0] + iris_offset_x
                iris_draw_y = fixed_eye_center[1] + iris_offset_y

                last_iris_draw_x = iris_draw_x
                last_iris_draw_y = iris_draw_y
            elif last_iris_draw_x is not None and last_iris_draw_y is not None:
                iris_draw_x = last_iris_draw_x
                iris_draw_y = last_iris_draw_y
            else:
                iris_draw_x = fixed_eye_center[0]
                iris_draw_y = fixed_eye_center[1]

            cv2.ellipse(canvas, fixed_eye_center, fixed_eye_axes, 0, 0, 360, (255, 255, 255), thickness=-1)

            cv2.circle(canvas, (iris_draw_x, iris_draw_y), fixed_iris_radius, (0, 0, 0), thickness=-1)

            cv2.circle(canvas, (iris_draw_x, iris_draw_y), fixed_pupil_radius, (50, 50, 50), thickness=-1)

            highlight_center_x = iris_draw_x - int(fixed_iris_radius * 0.5)
            highlight_center_y = iris_draw_y - int(fixed_iris_radius * 0.5)
            cv2.circle(canvas, (highlight_center_x, highlight_center_y), highlight_radius, (255, 255, 255), thickness=-1)

            cv2.ellipse(canvas, fixed_eye_center, fixed_eye_axes, 0, 0, 360, (0, 0, 0), thickness=2)

        elif current_mode == 2:
            now = datetime.datetime.now()
            time_string = now.strftime("%H:%M:%S")

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2.5
            font_thickness = 4
            text_color = (0, 255, 255)

            (text_width, text_height), baseline = cv2.getTextSize(time_string, font, font_scale, font_thickness)

            text_x = (img_w - text_width) // 2
            text_y = (img_h + text_height) // 2

            cv2.putText(canvas, time_string, (text_x, text_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

        elif current_mode == 3:
            tesselation_color = (255, 150, 0)
            contours_color = (200, 50, 200)
            iris_color = (255, 255, 255)
            hand_color = (0, 255, 255)
            pose_color = (0, 200, 255)

            if face_results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=canvas,
                    landmark_list=face_results.multi_face_landmarks[0],
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=tesselation_color, thickness=1, circle_radius=1),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=tesselation_color, thickness=1))
                mp_drawing.draw_landmarks(
                    image=canvas,
                    landmark_list=face_results.multi_face_landmarks[0],
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=contours_color, thickness=2, circle_radius=2),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=contours_color, thickness=2))
                mp_drawing.draw_landmarks(
                    image=canvas,
                    landmark_list=face_results.multi_face_landmarks[0],
                    connections=mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=iris_color, thickness=1, circle_radius=1),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=iris_color, thickness=1))

            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image=canvas,
                        landmark_list=hand_landmarks,
                        connections=mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing.DrawingSpec(color=hand_color, thickness=2, circle_radius=2),
                        connection_drawing_spec=mp_drawing.DrawingSpec(color=hand_color, thickness=2))

            if pose_results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image=canvas,
                    landmark_list=pose_results.pose_landmarks,
                    connections=mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=pose_color, thickness=2, circle_radius=2),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=pose_color, thickness=2))

        if current_mode in [1, 2]:
            num_line_shifts = 3
            max_line_shift_pixels = 15

            for _ in range(num_line_shifts):
                y_start = random.randint(0, img_h - 1)
                line_height = random.randint(1, 3)
                y_end = min(img_h, y_start + line_height)
                shift_amount = random.randint(-max_line_shift_pixels, max_line_shift_pixels)

                if shift_amount > 0:
                    canvas[y_start:y_end, shift_amount:] = canvas[y_start:y_end, :-shift_amount]
                    canvas[y_start:y_end, :shift_amount] = purple_color
                elif shift_amount < 0:
                    canvas[y_start:y_end, :shift_amount] = canvas[y_start:y_end, -shift_amount:]
                    canvas[y_start:y_end, shift_amount:] = purple_color

            num_noise_blocks = 5
            max_block_size = 20
            for _ in range(num_noise_blocks):
                x = random.randint(0, img_w - max_block_size)
                y = random.randint(0, img_h - max_block_size)
                w = random.randint(5, max_block_size)
                h = random.randint(5, max_block_size)

                if random.random() < 0.5:
                    random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    cv2.rectangle(canvas, (x, y), (x + w, y + h), random_color, -1)
                else:
                    channel_shift = random.randint(-30, 30)
                    canvas[y:y+h, x:x+w, 0] = np.clip(canvas[y:y+h, x:x+w, 0] + channel_shift, 0, 255)
                    canvas[y:y+h, x:x+w, 1] = np.clip(canvas[y:y+h, x:x+w, 1] + channel_shift, 0, 255)
                    canvas[y:y+h, x:x+w, 2] = np.clip(canvas[y:y+h, x:x+w, 2] + channel_shift, 0, 255)

        cv2.imshow('Virtual Eye Tracking', canvas)

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
