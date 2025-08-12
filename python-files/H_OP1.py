import sys
import subprocess
import cv2
import mediapipe as mp
import numpy as np
import rk_mcprotocol as mc
import math
import time

def get_system_uuid():
    try:
        cmd = "wmic csproduct get UUID"
        uuid = subprocess.check_output(cmd, shell=True).decode().split("\n")[1].strip()
        return uuid
    except Exception as e:
        print(f"unknown error: {e}")
        return None

def run_program():
    # SCAN
    HOST = '192.168.3.250'
    PORT = 1025
    s = mc.open_socket(HOST, PORT)

    # Initialize Mediapipe Face Mesh
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=2)

    # Thresholds
    EAR_THRESHOLD = 0.2
    EAR_CONSEC_FRAMES = 10
    YAW_PRESENT_RANGE = (-25.0, 25.0)  # Adjusted range for yaw
    PITCH_PRESENT_RANGE = (-5.0, 10.0)  # Adjusted range for pitch

    # State variables
    frame_count = 0
    absent_time = 0
    threshold_time = 2
    last_detection_time = time.time()
    last_present_time = time.time()  # Track the last time the status was "Present"
    machine_status = "Absent"

    # Function to calculate Eye Aspect Ratio (EAR)
    def eye_aspect_ratio(eye_landmarks):
        A = np.linalg.norm(np.array(eye_landmarks[1]) - np.array(eye_landmarks[5]))
        B = np.linalg.norm(np.array(eye_landmarks[2]) - np.array(eye_landmarks[4]))
        C = np.linalg.norm(np.array(eye_landmarks[0]) - np.array(eye_landmarks[3]))
        ear = (A + B) / (2.0 * C)
        return ear

    # Function to calculate yaw and pitch angles
    def calculate_yaw_and_pitch(landmarks, image_width, image_height):
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        nose_tip = landmarks[1]

        left_eye_coords = np.array([left_eye.x * image_width, left_eye.y * image_height])
        right_eye_coords = np.array([right_eye.x * image_width, right_eye.y * image_height])
        nose_tip_coords = np.array([nose_tip.x * image_width, nose_tip.y * image_height])

        eye_midpoint = (left_eye_coords + right_eye_coords) / 2.0
        nose_vector = nose_tip_coords - eye_midpoint

        yaw = math.degrees(math.atan2(nose_vector[0], nose_vector[1]))
        pitch = math.degrees(math.atan2(nose_vector[1], image_height))

        return yaw, pitch

    # Video capture
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
 

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame for a mirror effect
        frame = cv2.flip(frame, 1)

        # Convert frame to RGB for Mediapipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        status_color = (0, 255, 0)  # Default: red for absent

        if results.multi_face_landmarks:
            face_count = len(results.multi_face_landmarks)

            # If more than 1 face is detected
            if face_count > 1:
                machine_status = "Multiple Faces Detected"
                status_color = (255, 0, 255)  # Magenta for multiple faces
            else:
                last_detection_time = time.time()
                absent_time = 0

                # Process the primary face
                face_landmarks = results.multi_face_landmarks[0]
                landmarks = face_landmarks.landmark
                image_height, image_width, _ = frame.shape

                # Calculate yaw and pitch
                yaw, pitch = calculate_yaw_and_pitch(landmarks, image_width, image_height)

                # Check EAR for both eyes
                left_eye_landmarks = [[landmarks[i].x * image_width, landmarks[i].y * image_height] for i in [362, 385, 387, 263, 373, 380]]
                right_eye_landmarks = [[landmarks[i].x * image_width, landmarks[i].y * image_height] for i in [33, 160, 158, 133, 153, 144]]

                left_ear = eye_aspect_ratio(left_eye_landmarks)
                right_ear = eye_aspect_ratio(right_eye_landmarks)
                avg_ear = (left_ear + right_ear) / 2.0

                if avg_ear < EAR_THRESHOLD:
                    frame_count += 1
                    # Only mark as distracted if the frame count exceeds the EAR_CONSEC_FRAMES threshold
                    if frame_count >= EAR_CONSEC_FRAMES:
                        # Add a delay when transitioning from "Present" to "Distracted (Eyes Closed)"
                        if machine_status == "Present" and (time.time() - last_present_time) < 2:
                            continue
                        machine_status = "Distracted (Eyes Closed)"
                        status_color = (0, 255, 255)  # Yellow for distracted
                else:
                    frame_count = 0

                    # Only check yaw and pitch if EAR is above the threshold
                    if frame_count == 0:  # Ensure no EAR-related distraction is active
                        if YAW_PRESENT_RANGE[0] <= yaw <= YAW_PRESENT_RANGE[1] and PITCH_PRESENT_RANGE[0] <= pitch <= PITCH_PRESENT_RANGE[1]:
                            machine_status = "Present"
                            status_color = (0, 255, 0)  # Green for present
                            last_present_time = time.time()  # Update the last present time
                        else:
                            machine_status = "Distracted"
                            status_color = (0, 255, 255)  # Yellow for distracted
        else:
            absent_time = time.time() - last_detection_time
            if absent_time > threshold_time:
                machine_status = "Absent"
                status_color = (0, 0, 255)  # Red for absent

        # Display the status on the frame
        cv2.putText(
            frame, f"Status: {machine_status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2
        )
        cv2.imshow("Frame", frame)

        if machine_status == "Present":
            mc.write_bit(s, headdevice='m110', data_list=[1])
            mc.write_bit(s, headdevice='m111', data_list=[0])
            
        else:
            mc.write_bit(s, headdevice='m110', data_list=[0])
            mc.write_bit(s, headdevice='m111', data_list=[1])
        

        # Break the loop on 'Shift + Q'
        key = cv2.waitKey(1)
        if key == ord('Q') and (cv2.getWindowProperty('Frame', cv2.WND_PROP_VISIBLE) >= 1):
            if cv2.getKeyState(16):  # Check if 'Shift' is held
                break

    cap.release()
    cv2.destroyAllWindows()

def main():
    # Define the authorized UUID
    # authorized_uuid = "4C4C4544-0032-4B10-804A-C4C04F505333F"  # Replace with your actual UUID
    authorized_uuid = "69A9A9EA-926B-4ED3-8DC5-5620C3B212FF"  # Replace with your actual UUID

    # Fetch the current system UUID
    current_uuid = get_system_uuid()

    # Compare UUIDs
    if current_uuid == authorized_uuid:
        print("Connection Established")
        run_program()
    else:
        print("Wait for some time...")
        sys.exit()

    # Directly run the program (UUID check commented out)
    run_program()

if __name__ == "__main__":
    main()
