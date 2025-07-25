import cv2
import threading
import win32ts
import win32gui
import win32api
import time
from typing import Union, Any
import datetime
import os
import win32process
import psutil
from pathlib import Path, PurePosixPath
import io
import numpy as np
import requests
from ultralytics import YOLO
from sklearn.preprocessing import Normalizer
from scipy.spatial.distance import cosine
from tensorflow import keras
import pickle
import ast
import configparser
from PIL import ImageGrab


class RealEventMonitoringSystem:
    def __init__(self) -> None:
        self.config_path = PurePosixPath(Path.cwd().joinpath("app.config")).as_posix()
        self.parser = configparser.ConfigParser()
        self.parser.read(self.config_path)
        self.camera_running: bool = False
        self.camera_thread: Any = None
        self.stop_event = threading.Event()
        self.stop = False
        self.capture = None
        self.device_index = None
        self.locked = False
        self.on_teams = False
        self.save_interval = 2
        self.last_saved_time = time.time()
        self.remaining_time = self.save_interval
        self.machine_name = os.getlogin()
        self.__proto_path = PurePosixPath(Path.cwd().joinpath("deploy.prototxt")).as_posix()
        self.__model_path = PurePosixPath(Path.cwd().joinpath("res10_300x300_ssd_iter_140000.caffemodel")).as_posix()
        self.__net = cv2.dnn.readNetFromCaffe(self.__proto_path, self.__model_path)
        self.yolov11_openvino_model = self.parser.get("app", "openvino_model_folder") # PurePosixPath(Path.cwd().joinpath('best_openvino_model')).as_posix()  # 'best_openvino_model'
        self.mobile_class_id = 1
        self.l2_normalizer = Normalizer("l2")
        self.required_size = (160, 160)
        self.face_model = keras.models.load_model(r"facenet_keras_weights_and_architecturenew.h5")
        self.__standard_dt_format = "%Y-%m-%d %H:%M:%S"
        self.frame_session_log_file = PurePosixPath(Path.cwd().joinpath("frame_log_times.txt")).as_posix()
        self.model = YOLO(self.yolov11_openvino_model, task="detect", verbose=False)

        # Camera loop settings
        self.__wait_duration = self.parser.getint("delay", "frame_wait_duration")

    def get_data_read_from_appconfig_settings(self):
        """This reads the config file and parses the required params from the file."""
        return self.parser
    
    def get_encode(self, faces):
        """Performs Face Recognition after detection, and returns the encodings."""
        len = round(faces.shape[0])
        faces = faces[:len]
        encode = self.face_model.predict(faces)
        return encode
    
    def load_pickle(self, path):
        """Loads the pickle file containing the face encodings."""
        with open(path, 'rb') as f:
            encoding_dict = pickle.load(f)
        return encoding_dict
    
    def extract_raw_time_data_from_dt_timestamps(self, start_time_dt: datetime.datetime, end_time_dt: datetime.datetime) -> Union[str, datetime.datetime]:
        """Takes 2 Timezones, i.e start and end times, extracts metadata like hrs, mins, seconds from those, and returns them as tuple."""
        process_total_time = (end_time_dt - start_time_dt)
        total_secs = int(process_total_time.total_seconds())
        hours, remainder = divmod(total_secs, 3600)
        minutes, seconds = divmod(remainder, 60)
        return hours, minutes, seconds
    
    def detect_face_dnn(self, frame: np.ndarray, conf_face_detection: float) -> Union[bool, None]:
        """ Performs Face Detection using DNN Module, and plots bounding boxes over the image. """
        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        self.__net.setInput(blob)
        detections = self.__net.forward()
        face_detected: bool = False

        face_count = 0
        bbox_info = []

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_face_detection:
                face_detected = True
                box = detections[0, 0, i, 3:7] * [width, height, width, height]
                (x1, y1, x2, y2) = box.astype('int')

                # Draw rectangle and label
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                face_count += 1
                bbox_info.append((x1, y1, x2, y2))
                label = f'Face-{int(confidence * 100)}%'
                y_offset = y1 - 10 if y1 - 10 > 10 else y1 + 20
                cv2.putText(frame, label, (x1, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 2)

        return frame, face_count
    
    def draw_frame_performance_metrics(self, frame: np.ndarray) -> np.ndarray:
        """Extracts all necessary metrics related to CPU Stats, and logs all of them in a separate file."""
        process = psutil.Process(os.getpid())
        app_mem = process.memory_info().rss / (1024 * 1024) # Convert to MB
        thread_count = process.num_threads()

        cpu_percent = psutil.cpu_percent(interval=0.0)
        ram_percent = psutil.virtual_memory().percent
        uptime_secs = int(datetime.datetime.now().timestamp() - psutil.boot_time())
        uptime_str = str(datetime.timedelta(seconds=uptime_secs))

        # Battery info
        battery_info = psutil.sensors_battery()
        if battery_info:
            battery_percent = battery_info.percent
            battery_status = "Charging" if battery_info.power_plugged else "On Battery"
            battery_line = f"Battery: {battery_percent}% ({battery_status})"
        else:
            battery_line = "Battery: N/A"
        metrics = [f"CPU Usage: {cpu_percent:.1f}%", f"RAM Usage: {ram_percent:.1f}%", f"App Memory: {app_mem:.1f} MB"]     # f"Threads: {thread_count}", f"Uptime: {uptime_str}", battery_line

        # Display metrics on frame
        alpha = 0.4
        overlay = frame.copy()
        box_height = 30 + 30 * len(metrics)
        logs_dict = {
            "Application Memory": round(app_mem, 2),
            "Active Threads": thread_count,
            "Battery Status": battery_line
        }
        self.log_event("\n\n---------------- CPU Performance Metrics Per Frame ----------------")
        for log_key, log_val in logs_dict.items():
            self.log_event(f"{log_key}: {log_val}")
        for log_idx, log in enumerate(metrics, start=1):
            self.log_event(f"{log_idx}> {log}")
        self.log_event("---------------- CPU Performance Metrics Ended ----------------\n")
        # cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        # cv2.rectangle(overlay, (5, 5), (380, box_height), (0, 0, 0), -1)
        # for idx, metric in enumerate(metrics):
        #     y = 30 + idx * 30
        #     cv2.putText(overlay, metric, (10, y), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        return overlay
    
    def start_face_recognition(self, frame: np.ndarray, conf_recog_t: float, face_det_t_for_recognition: float) -> tuple:
        facedata = []
        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 177, 123], swapRB=False, crop=False)
        self.__net.setInput(blob)
        detections = self.__net.forward()
        face_recognized = False
        encode = ''

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > face_det_t_for_recognition:
                box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                (x1, y1, x2, y2) = box.astype('int')
                face = frame[y1: y2, x1: x2]
                norm_image = (face - face.mean()) / face.std()
                face = cv2.resize(norm_image, self.required_size)
                facedata.append(face)
                face_encoding = self.get_encode(np.array(facedata))

                # Convert the face_data into the required dictionary format
                # converted_encodings = {name: encoding for name, encoding in self.face_data.items()}

                # Save the converted data
                # pkl_download_dir = os.path.normpath(os.path.join(os.getcwd(), 'pkl_downloads'))
                # encoding_name = Path(self.encodings_pkl_file).stem.split("_")[0]
                # face_data_final_pkl_file = os.path.normpath(os.path.join(pkl_download_dir, f"{encoding_name}_final.pkl"))  # 'pkl_downloads/face_data_final.pkl'

                # with open(face_data_final_pkl_file, 'wb') as f:
                #     pickle.dump(converted_encodings, f)

                encode = self.load_pickle(self.parser.get("app", "encoder_file"))
                distance = float('inf')
                name = 'unknown'

                for db_name, db_encode in encode.items():
                    for en in face_encoding:
                        encodes = self.l2_normalizer.transform(en.reshape(1, -1))[0]
                        dist = cosine(db_encode, encodes)
                        if dist <= conf_recog_t and dist < distance:
                            face_recognized = True
                            name = db_name
                            distance = dist
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, f"{name} ({distance:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        else:
                            face_recognized = False
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
                            cv2.putText(frame, f"{name}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                            # face_region = frame[y1:y2, x1:x2]
                            # if face_region.size > 0:
                            #     blurred_face = cv2.GaussianBlur(face_region, (51, 51), 30)
                            #     frame[y1:y2, x1:x2] = blurred_face

        return face_recognized, frame
    
    def upload_frame_to_api(self, frame: np.ndarray, use_case: str, screenshot: str):
        """Uses External API Call to save the image based on specific use-cases (Face(s) (0, 1, F > 1),
        Mobile Detection and Recognition)"""
        _, img_encoded = cv2.imencode(".jpg", frame)
        _, img_encoded1 = cv2.imencode(".jpg", screenshot)
        img_bytes = img_encoded.tobytes()
        img_bytes1 = img_encoded1.tobytes()

        # Build payload
        payload = {
            "use_case": use_case,
            "machine_name": self.machine_name,
            "timestamp": datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        
        try:
            response = requests.post(self.parser.get("app", "api_url"), data=payload, files={
                "image": ("frame.jpg", io.BytesIO(img_bytes), "image/jpeg"),
                "image1": ("frame1.jpg", io.BytesIO(img_bytes1), "image/jpeg")
            }, timeout=5)

            if response.status_code == 200:
                pass
                # saved_file = response.json()["filename"]
                # # print(f"[INFO] Uploaded Non-Compliance image: {saved_file}")
                # self.log_event(f"[SUCCESS] Uploaded {use_case} -> API Path: {response.json().get('Path')}")   # Image uploaded and saved as: {saved_file}
            else:
                # # print(f"[INFO] Image Upload failed for file: {saved_file}")
                self.log_event(f"[FAILED] {response.status_code}: {response.text}")

        except Exception as e:
            self.log_event(f"[ERROR] Exception during image upload: {str(e)}")

    def get_available_camera_index(self, max_devices: int = 10) -> Union[int, None]:
        """ tries device indices from 0 to max-devices-1 and returns the first
        available one. Returns none if no camera is found."""
        for idx in range(max_devices):
            cap = cv2.VideoCapture(idx)
            if cap is not None and cap.isOpened():
                cap.release()
                return idx
        return None
    
    def get_active_app_name(self, log=False):
        """Gets the active window's name"""
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            if log:
                self.log_event("No active window detected.")
            return None
        
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            raw_name = process.name()
            app_map = dict(self.parser.items("application_map"))
            app_name = app_map.get(raw_name, raw_name)

            if log:
                self.log_event(f"Active Application: {app_name}")

            return app_name
        
        except Exception as e:
            if log:
                self.log_event(f"Error detecting active application: {e}")
            return None

    def capture_camera(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return
        
        self.camera_running = True

        while not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                break

            # cv2.imshow("Live Camera Feed", frame)

            if cv2.waitKey(self.__wait_duration) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.camera_running = False

    def start_camera(self):
        """This starts the camera loop by fetching the active camera device index dynamically, and runs on that device.
        Throws an exception if no camera is found."""
        if self.camera_running:
            return
        
        # Dynamically fetches the camera location in a user's system, with max devices limit to 10.
        self.device_index = self.get_available_camera_index()

        # Throws exception if no device is found on the user's system
        if self.device_index is None:
            self.log_event("Camera not found.")
            return
        
        # Starts the video with the active camera traced.
        self.capture = cv2.VideoCapture(self.device_index)

        # Throws exception in the case of active camera device not being traceable after repeated attempts.
        if not self.capture.isOpened():
            self.log_event(f"[ERROR] Failed to open camera at index {self.device_index}")
            return
        
        # Triggers success logs once it grabs the active device.
        self.log_event(f"[INFO] Camera started on device {self.device_index}")
        self.camera_running = True
        self.stop_event.clear()

        # Resumes camera from the last saved interval in the case of a pause/teams switch over event.
        self.last_saved_time = time.time() - (self.save_interval - self.remaining_time)
        self.camera_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.camera_thread.start()

    def detect_mobile_objects_using_openvino(self, frame_arr: np.ndarray, mobile_labels: list, mobile_conf_threshold: float):  # Mihir's version
        result = self.model(frame_arr)[0]  
        boxes = result.boxes
        names = result.names
        mobile_detected = False

        for box in boxes:
            class_id = int(box.cls[0])
            label = names[class_id] if isinstance(names, dict) else names[class_id]
            conf = float(box.conf[0])

            if label in mobile_labels and conf > mobile_conf_threshold:
                mobile_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame_arr, (x1, y1), (x2, y2), (0, 0, 170), 2)
                cv2.putText(frame_arr, f"{str(label).capitalize()}: {conf:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 170), 2)

        return mobile_detected, frame_arr

    def _capture_loop(self):
        """This is the main function that performs all the detection use cases in a pipeline in a single frame, and logs all timestamps for each scenario, along with
        the entire frame time captured. This also detects active application focus, and tracks user activity in each app switch over. """
        frame_start_time_log = datetime.datetime.now().isoformat().split(".")[0].split("T")
        frame_start_time = ' '.join(frame_start_time_log)
        total_detection_hrs = []
        total_detection_mins = []
        total_detection_secs = []

        # Config file set up to read settings in live detection
        # conf_reader = self.get_data_read_from_appconfig_settings()

        while not self.stop_event.is_set():
            config_path = PurePosixPath(Path.cwd().joinpath("app.config")).as_posix()
            parser = configparser.ConfigParser()
            parser.read(config_path)
            confidence_t_for_clearfaces = parser.getfloat("app", "confidence_t_for_clearfaces")
            face_detection_t_for_recognition = parser.getfloat("app", "face_detection_t_for_recognition")
            recognition_t = parser.getfloat("app", "recognition_t")
            MOBILE_PHONE_LABELS = ast.literal_eval(self.parser.get("app", "mobile_phone_labels"))
            mobile_conf_threshold = parser.getfloat("app", "mobile_confidence")

            frame_start_time_log = datetime.datetime.now().isoformat().split(".")[0].split("T")
            print("start_time", frame_start_time_log)

            ret, frame = self.capture.read()
            if not ret:
                continue

            # Detect faces and Log Entries
            face_detection_start_log = datetime.datetime.now().isoformat().split(".")[0].split("T")
            frame, face_count = self.detect_face_dnn(frame, confidence_t_for_clearfaces)
            face_detection_stop_log = datetime.datetime.now().isoformat().split(".")[0].split("T")
            face_detection_start_time = ' '.join(face_detection_start_log)
            face_detection_stop_time = ' '.join(face_detection_stop_log)

            # ---/ Scenario Validator: NoFace / One Face / Multiple Faces /---
            face_detection_total_start_time = datetime.datetime.strptime(face_detection_start_time, self.__standard_dt_format)
            face_detection_total_stop_time = datetime.datetime.strptime(face_detection_stop_time, self.__standard_dt_format)
            face_hrs, face_mins, face_secs = self.extract_raw_time_data_from_dt_timestamps(face_detection_total_start_time, face_detection_total_stop_time)
            total_detection_hrs.append(face_hrs)
            total_detection_mins.append(face_mins)
            total_detection_secs.append(face_secs)
            face_dt_str = f"{face_hrs} hrs {face_mins} mins {face_secs} secs"

            if face_count == 0:
                self.log_event(f"[DNN][NO_FACE] No face detected. Total duration: {face_dt_str}")
            elif face_count == 1:
                # print("[DNN][ONE_FACE]", face_count, "face detected.", "Total Duration:", face_dt_str)
                self.log_event(f"[DNN][ONE_FACE] {face_count} Face Detected.")
            else:
                # print("[DNN][MULTIPLE_FACE]", face_count, "face(s) detected.", "Total Duration:", face_dt_str)
                self.log_event(f"[DNN][MULTIPLE_FACE] {face_count} faces detected.")

            # Detect Mobiles and Log Entries
            mobile_detection_start_log = datetime.datetime.now().isoformat().split(".")[0].split("T")
            mobile_detected, frame = self.detect_mobile_objects_using_openvino(frame, MOBILE_PHONE_LABELS, mobile_conf_threshold)
            mobile_detection_stop_log = datetime.datetime.now().isoformat().split(".")[0].split("T")
            mobile_detection_start_time = ' '.join(mobile_detection_start_log)
            mobile_detection_stop_time = ' '.join(mobile_detection_stop_log)
            mobile_detection_start_time_dt = datetime.datetime.strptime(mobile_detection_start_time, self.__standard_dt_format)
            mobile_detection_stop_time_dt = datetime.datetime.strptime(mobile_detection_start_time, self.__standard_dt_format)
            mobile_hrs, mobile_mins, mobile_secs = self.extract_raw_time_data_from_dt_timestamps(mobile_detection_start_time_dt, mobile_detection_stop_time_dt)
            total_detection_hrs.append(mobile_hrs)
            total_detection_mins.append(mobile_mins)
            total_detection_secs.append(mobile_secs)
            # print(f"Face(s) Detection started at: {face_detection_start_time}")
            # print(f"Face(s) Detection ended at: {face_detection_stop_time}")
            # print(f"Mobile(s) Detection started at: {mobile_detection_start_time}")
            # print(f"Mobile(s) Detection ended at: {mobile_detection_stop_time}")
            self.log_event(f"Face(s) Detection started at: {face_detection_start_time}")
            self.log_event(f"Face(s) Detection ended at: {face_detection_stop_time}")
            self.log_event(f"Mobile(s) Detection started at: {mobile_detection_start_time}")
            self.log_event(f"Mobile(s) Detection ended at: {mobile_detection_stop_time}")

            # Overlay Performance metrics on both frames
            frame = self.draw_frame_performance_metrics(frame)
            current_time = time.time()

            # ------------- Face Recognition Starts ---------------
            recog_start_time_log = datetime.datetime.now().isoformat().split(".")[0].split("T")
            recog_start_time = ' '.join(recog_start_time_log)
            face_recognized, frame = self.start_face_recognition(frame, recognition_t, face_detection_t_for_recognition)
            recog_stop_time_log = datetime.datetime.now().isoformat().split(".")[0].split("T")
            recog_stop_time = ' '.join(recog_stop_time_log)
            recog_start_time_dt = datetime.datetime.strptime(recog_start_time, self.__standard_dt_format)
            recog_stop_time_dt = datetime.datetime.strptime(recog_stop_time, self.__standard_dt_format)
            recog_hrs, recog_mins, recog_secs = self.extract_raw_time_data_from_dt_timestamps(recog_start_time_dt, recog_stop_time_dt)
            total_detection_hrs.append(recog_hrs)
            total_detection_mins.append(recog_mins)
            total_detection_secs.append(recog_secs)
            self.log_event(f"Recognition started at: {recog_start_time}")
            self.log_event(f"Recognition Ended at: {recog_stop_time}")
            # print(f"Recognition started at: {recog_start_time}")
            # print(f"Recognition Ended at: {recog_stop_time}")
            # ------------- Face Recognition Ends ---------------

            # Create folder based on the scenario
            if face_count == 0:
                folder = "No_Face"
            elif face_count > 1:
                folder = "Multiple_Faces"
            elif mobile_detected:
                folder = "Mobile"
            elif face_recognized == False:
                folder = "FaceNotRecognized"
            else:
                folder = None

            if folder:
                # Capture the entire screen
                screenshot = ImageGrab.grab()

                # Convert PIL Image to NumPy array
                screenshot_np = np.array(screenshot)

                # Convert RGB to BGR (OpenCV uses BGR)
                screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

                if current_time - self.last_saved_time >= self.save_interval:
                    self.upload_frame_to_api(frame, folder, screenshot_cv)

            self.last_saved_time = current_time
            self.remaining_time = self.save_interval

            # Adding delay of 1s to check performance
            # time.sleep(1)

            # Get the clearance to Toggle Frame settings to ON/OFF
            frame_show_check = parser.getboolean("app", "frame_show")

            # Frame shows when set active
            if frame_show_check:
                cv2.imshow("Live Camera Feed", frame)
                # self.log_event(f"Frame show: ON")
            else:
                cv2.destroyAllWindows()
                # pass

            # Detections active until the keyboard key press.
            if cv2.waitKey(27) & 0xFF == ord('q'):
                self.capture.release()
                cv2.destroyAllWindows()
                # break
            frame_stop_time_log = datetime.datetime.now().isoformat().split(".")[0].split("T")
            print("stop time", frame_stop_time_log)

            delay = self.parser.getint("delay", "duration")
            time.sleep(delay)
        self._cleanup_camera()

        # Convert Mobile and Recognition Detection Timestamps to DT format
        frame_stop_time_log = datetime.datetime.now().isoformat().split(".")[0].split("T")
        frame_stop_time = ' '.join(frame_stop_time_log)
        total_time_taken_start_log = frame_start_time_log
        total_time_taken_ended_log = recog_stop_time_log
        total_start_times = total_time_taken_start_log[len(total_time_taken_start_log) - 1].split(":")
        start_time_hrs = total_start_times[0]
        start_time_mins = total_start_times[1]
        start_time_secs = total_start_times[len(total_start_times) - 1]
        total_stop_times = total_time_taken_ended_log[len(total_time_taken_ended_log) - 1].split(":")
        stop_time_hrs = total_stop_times[0]
        stop_time_mins = total_stop_times[1]
        stop_time_secs = total_stop_times[len(total_stop_times) - 1]
        total_hrs_diff = abs(int(start_time_hrs) - int(stop_time_hrs)) if int(start_time_hrs) != int(stop_time_hrs) else 0
        total_mins_diff = abs(int(start_time_mins) - int(stop_time_mins)) if int(start_time_mins) != int(stop_time_mins) else 0
        total_secs_diff = abs(int(start_time_secs) - int(stop_time_secs)) if int(start_time_secs) != int(stop_time_secs) else 0
        total_time_diff = f"{total_hrs_diff} Hrs {total_mins_diff} Mins {total_secs_diff} Secs"
        total_scenario_time = f"{sum(set(total_detection_hrs))} hrs, {sum(set(total_detection_mins))} mins, {sum(set(total_detection_secs))} secs"
        self.log_event(f"Capture started at: {frame_start_time}")
        self.log_event(f"Capture Ended at: {frame_stop_time}")
        self.log_event(f"Total Process Time (Frame Start -> Frame End) took place for: {total_time_diff}.")
        self.log_event(f"Total Detections of All Events duration: {total_scenario_time}")

    def _cleanup_camera(self):
        if self.capture:
            self.capture.release()
            cv2.destroyAllWindows()
            self.capture = None
        self.camera_running = False
        # print("[INFO] Camera cleaned up")

    def stop_camera(self):
        if self.camera_running:
            # print("[INFO] Stopping camera...")
            self.log_event("Camera stopped.")
            self.stop_event.set()
            
            # Save remaining time before next frame
            self.remaining_time = max(0, self.save_interval - (time.time() - self.last_saved_time))
            if self.camera_thread and threading.current_thread() != self.camera_thread:
                self.camera_thread.join()

    def win_event_filter(self, hwnd, msg, wparam, lparam):
        if msg == 0x02B1:   # WM_WTSESSION_CHANGE
            if wparam == 0x7:  # win32con.WTS_SESSION_LOCK
                self.locked = True
                # print("[EVENT] Session locked")
                self.log_event("Session locked")
                self.stop_camera()
            elif wparam == 0x8:    # win32con.WTS_SESSION_UNLOCK
                self.locked = False
                # print("[EVENT] Session unlocked")
                self.log_event("Session Unlocked")
                if not self.on_teams:
                    self.start_camera()
        return True
    
    def log_event(self, event_type: str):
        """This logs the timestamps of each event in particular during the camera run,
        along with the type of event occured at that specific moment."""
        timestamp = datetime.datetime.now().isoformat().split(".")[0].split("T")
        log_line = f"[{' '.join(timestamp)}] {event_type}\n"
        with open("session_log.txt", "a") as f:
            f.write(log_line)

    def log_event_for_full_frame_duration(self, event_type: str):
        """This logs the timestamp only for the start and end duration of the frame in the capture loop function."""
        timestamp = datetime.datetime.now().isoformat().split(".")[0].split("T")
        log_line = f"[{' '.join(timestamp)}] {event_type}\n"
        with open(self.frame_session_log_file, "a") as frame_log_file:
            frame_log_file.write(log_line)
            # if not frame_log_file.closed:
            #     frame_log_file.close()

    def monitor_foreground_app(self):
        """This tracks the current window navigated to, by the user during the camera detection event.
          Also, this logs the entry of that particular window the user switched over to.
          This also tracks, if the user switched over to MS-Teams or not, if so, it toggles camera start/stop events only during Teams switch.
          Logs entry for the same after MS-Teams switch over."""
        
        prev_app = str()
        while True:
            app_name = self.get_active_app_name(log=False)
            if app_name:
                if "teams" in app_name.lower():
                    if not self.on_teams:
                        self.on_teams = True
                        self.log_event("Switched to Microsoft Teams")
                        self.stop_camera()
                else:
                    if self.on_teams:
                        self.on_teams = False
                        self.log_event("Switched away from Microsoft Teams")
                        if not self.locked:
                            self.start_camera()

                # Only log if app has changed
                if app_name != prev_app:
                    self.log_event(f"Active Application: {app_name}")
                    prev_app = app_name

            time.sleep(1)
    
    def main(self):
        def _event_filter(hwnd, msg, wparam, lparam):
            return self.win_event_filter(hwnd, msg, wparam, lparam)
        
        # Create a hidden window to listen to Windows session messages
        hInstance = win32api.GetModuleHandle()
        className = "SessionMonitorWindow"

        wndClass = win32gui.WNDCLASS()
        wndClass.lpfnWndProc = _event_filter
        wndClass.hInstance = hInstance
        wndClass.lpszClassName = className

        try:
            win32gui.RegisterClass(wndClass)
        except Exception:
            pass    # Already Registered

        hwnd = win32gui.CreateWindow(className, className, 0, 0, 0, 0, 0, 0, 0, hInstance, None)

        # Register for session notification
        win32ts.WTSRegisterSessionNotification(hwnd, win32ts.NOTIFY_FOR_THIS_SESSION)

        # print("[INFO] Monitoring started...")

        # Start camera initially
        self.start_camera()
        self.monitor_thread = threading.Thread(target=self.monitor_foreground_app, daemon=True)
        self.monitor_thread.start()

        # Message loop
        # print("[INFO] Monitoring session lock/unlock...")
        try:
            while True:
                win32gui.PumpWaitingMessages()
                time.sleep(0.1)
        except KeyboardInterrupt:
            # print("[INFO] Application terminated by user.")
            self.stop_camera()


if __name__ == "__main__":
    event = RealEventMonitoringSystem()
    event.main()