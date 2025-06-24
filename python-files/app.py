import face_recognition
import cv2
import numpy as np
import pandas as pd
from datetime import datetime, date
import pickle
import os
from pathlib import Path
from tqdm import tqdm
import calendar
import threading
import queue
import logging

# ตั้งค่า logging เพื่อ debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ตัวแปรเก็บข้อมูลการบันทึกเพื่อป้องกันการบันทึกซ้ำในวันเดียวกัน
last_saved = {}  # {name: date}
# ตัวแปรเก็บข้อมูลล่าสุดที่ตรวจจับได้
latest_detection = None
# คิวสำหรับเก็บเฟรมและผลลัพธ์
frame_queue = queue.Queue(maxsize=1)
result_queue = queue.Queue(maxsize=1)

# ฟังก์ชันแปลงวันที่เป็นชื่อวันภาษาอังกฤษ
def get_english_day_name(date_obj):
    return calendar.day_name[date_obj.weekday()]

# ฟังก์ชันโหลดข้อมูลใบหน้าจากไฟล์ .dat
def load_known_faces(dat_file="known_faces.dat"):
    known_face_encodings = []
    known_face_names = []
    
    if os.path.exists(dat_file):
        with open(dat_file, 'rb') as f:
            data = pickle.load(f)
            known_face_encodings = data['encodings']
            known_face_names = data['names']
    
    return known_face_encodings, known_face_names

# ฟังก์ชันบันทึกข้อมูลลง Excel
def save_to_excel(name, confidence, excel_file="face_log.xlsx"):
    current_time = datetime.now()
    date_str = current_time.strftime("%Y-%m-%d")
    time_str = current_time.strftime("%H:%M:%S")
    day_name = get_english_day_name(current_time.date())
    data = {
        'Date': [date_str],
        'Time': [time_str],
        'Day': [day_name],
        'Name': [name],
        'Confidence (%)': [confidence*100]
    }
    df = pd.DataFrame(data)
    
    if os.path.exists(excel_file):
        existing_df = pd.read_excel(excel_file)
        df = pd.concat([existing_df, df], ignore_index=True)
    
    df.to_excel(excel_file, index=False)
    
    # อัปเดตข้อมูลล่าสุด
    global latest_detection
    latest_detection = {
        'name': name,
        'confidence': confidence*100,
        'date': date_str,
        'time': time_str,
        'day': day_name
    }
    logging.debug(f"Updated latest_detection: {name}, Confidence: {confidence*100:.2f}%")

# ฟังก์ชันเพิ่มข้อมูลใบหน้าจากโฟลเดอร์พร้อม progress bar
def add_faces_from_folder(folder_path, dat_file="known_faces.dat"):
    known_face_encodings = []
    known_face_names = []
    
    folder = Path(folder_path)
    image_extensions = ['.jpg', '.jpeg', '.png']
    image_files = [f for f in folder.glob('*') if f.suffix.lower() in image_extensions]
    
    if not image_files:
        logging.error("No image files found in the folder")
        return known_face_encodings, known_face_names
    
    print(f"Processing {len(image_files)} images...")
    for image_path in tqdm(image_files, desc="Creating face data", unit="image"):
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            
            if encodings:
                encoding = encodings[0]
                name = image_path.stem
                known_face_encodings.append(encoding)
                known_face_names.append(name)
            else:
                logging.warning(f"No face found in: {image_path}")
        except Exception as e:
            logging.error(f"Error processing {image_path}: {e}")
    
    # บันทึกข้อมูลลง .dat
    data = {'encodings': known_face_encodings, 'names': known_face_names}
    with open(dat_file, 'wb') as f:
        pickle.dump(data, f)
    
    print(f"Created {dat_file} successfully, saved {len(known_face_names)} faces")
    return known_face_encodings, known_face_names

# ฟังก์ชันวาดกรอบและเครื่องหมายถูก
def draw_face_box(frame, top, right, bottom, left, name, confidence):
    # ปรับพิกัดสำหรับภาพขนาดเต็ม
    scale = 2  # จากการ resize 1/2
    top, right, bottom, left = [int(x * scale) for x in [top, right, bottom, left]]
    # วาดกรอบสีเขียว
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    
    # วาดพื้นหลังสำหรับข้อความ
    cv2.rectangle(frame, (left, bottom + 35), (right, bottom), (0, 255, 0), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    text = f"{name} ({confidence*100:.2f}%)"
    cv2.putText(frame, text, (left + 6, bottom + 25), font, 0.5, (0, 0, 0), 1)
    
    # วาดเครื่องหมายถูก
    checkmark_points = np.array([[right - 30, bottom - 10], [right - 20, bottom], [right - 10, bottom - 20]])
    cv2.polylines(frame, [checkmark_points], False, (0, 255, 0), 2)

# ฟังก์ชันแสดงข้อมูลล่าสุดบนจอกล้อง (ไม่มีรูปภาพ)
def draw_latest_detection(frame):
    if latest_detection:
        name = latest_detection['name']
        text = f"{name} ({latest_detection['confidence']:.2f}%)"
        text2 = f"{latest_detection['date']} {latest_detection['time']} {latest_detection['day']}"
        # วาดพื้นหลังสำหรับข้อความ
        cv2.rectangle(frame, (10, 10), (400, 80), (0, 0, 0), cv2.FILLED)
        # วาดพื้นหลังสีเขียวเข้มสำหรับชื่อ
        cv2.rectangle(frame, (15, 15), (165, 45), (0, 128, 0), cv2.FILLED)
        # แสดงชื่อด้วยฟอนต์ใหญ่และสีขาว
        cv2.putText(frame, text, (20, 38), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        # แสดงวันที่และเวลา
        cv2.putText(frame, text2, (15, 65), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1)

# ฟังก์ชันประมวลผลใบหน้าใน thread แยก
def process_faces(known_face_encodings, known_face_names):
    frame_count = 0
    process_every_n_frames = 2  # ประมวลผลทุก 2 เฟรม
    
    while True:
        try:
            frame = frame_queue.get(timeout=1)
            frame_count += 1
            
            # ประมวลผลเฉพาะทุก ๆ n เฟรม
            if frame_count % process_every_n_frames != 0:
                result_queue.put([])
                continue
                
            # ลดขนาดภาพเพื่อประมวลผลเร็วขึ้น
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # ตรวจจับใบหน้า
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            results = []
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                confidence = 0.0
                
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                        confidence = 1.0 - face_distances[best_match_index]
                    
                    if name != "Unknown" and confidence >= 0.7:
                        current_date = date.today()
                        if name not in last_saved or last_saved[name] != current_date:
                            save_to_excel(name, confidence)
                            last_saved[name] = current_date
                            print(f"Saved: {name}, Confidence: {confidence*100:.2f}%")
                            results.append((top, right, bottom, left, name, confidence))
            
            result_queue.put(results)
        except queue.Empty:
            continue
        except Exception as e:
            logging.error(f"Error in face processing: {e}")
            break

# ฟังก์ชันหลักสำหรับตรวจจับใบหน้า
def main(folder_path):
    global last_saved
    
    # ปิด OpenCL เพื่อลดคำเตือน
    cv2.ocl.setUseOpenCL(False)
    
    # สร้างหรือโหลดข้อมูลใบหน้าจากโฟลเดอร์
    if not os.path.exists("known_faces.dat"):
        print("Creating known_faces.dat from folder...")
        add_faces_from_folder(folder_path)
    
    known_face_encodings, known_face_names = load_known_faces()
    
    if not known_face_encodings:
        logging.error("No face data found in known_faces.dat")
        return
    
    # เริ่ม thread สำหรับประมวลผลใบหน้า
    face_thread = threading.Thread(target=process_faces, args=(known_face_encodings, known_face_names), daemon=True)
    face_thread.start()
    
    # เริ่มต้นกล้อง
    video_capture = cv2.VideoCapture(0)
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            logging.error("Failed to capture frame from camera")
            break
            
        # ใส่เฟรมลงคิว
        try:
            frame_queue.put_nowait(frame.copy())
        except queue.Full:
            pass
        
        # ดึงผลลัพธ์จากคิว
        try:
            results = result_queue.get_nowait()
            for top, right, bottom, left, name, confidence in results:
                draw_face_box(frame, top, right, bottom, left, name, confidence)
        except queue.Empty:
            pass
        
        # แสดงข้อมูลล่าสุด
        draw_latest_detection(frame)
        
        # แสดงผลลัพธ์
        cv2.imshow('Video', frame)
        
        # กด 'q' เพื่อออก
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # ปิดกล้องและหน้าต่าง
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # ระบุโฟลเดอร์ที่มีรูปภาพ
    FOLDER_PATH = "C:/known_face"  # Change to your image folder path
    main(FOLDER_PATH)