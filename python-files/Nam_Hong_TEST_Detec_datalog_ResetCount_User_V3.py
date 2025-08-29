from ultralytics import YOLO
import cv2
import torch
from torchvision.ops import nms
import numpy as np
import os
import csv
from datetime import datetime, timedelta

# -----------------------------
# ตั้งค่าโฟลเดอร์หลักเป็นที่อยู่ของไฟล์ exe / py
base_dir = os.path.dirname(os.path.abspath(__file__))

# โหลดโมเดล
model_path = os.path.join(base_dir, "best.pt")
model = YOLO(model_path)
model.fuse()

# วิดีโอ
video_path = os.path.join(base_dir, "N1.mp4")

# Log folder (สร้างในโฟลเดอร์เดียวกับ exe)
log_folder = os.path.join(base_dir, "logs")
os.makedirs(log_folder, exist_ok=True)
# -----------------------------

# ตัวแปรสำหรับ Data Logger
last_log_time = datetime.now()
log_interval = timedelta(minutes=5)
current_date = datetime.now().date()
csv_file_path = os.path.join(log_folder, f"palm_log_{current_date.strftime('%Y%m%d')}.csv")

# ตัวแปรสำหรับติดตามวันปัจจุบัน
current_day = datetime.now().date()

# สร้างไฟล์ CSV ใหม่หากยังไม่มี
if not os.path.exists(csv_file_path):
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Time", "Unique Palms Count"])


def calculate_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def check_new_day():
    global current_day, unique_palm_count, tracked_palms, next_id
    today = datetime.now().date()
    if today != current_day:
        print(f"🔄 วันที่เปลี่ยนจาก {current_day} เป็น {today} รีเซ็ตการนับปาล์ม")
        current_day = today
        unique_palm_count = 0
        tracked_palms = {}
        next_id = 1
        return True
    return False


def log_data():
    global csv_file_path, current_date, unique_palm_count
    check_new_day()
    today = datetime.now().date()
    if today != current_date:
        current_date = today
        csv_file_path = os.path.join(log_folder, f"palm_log_{current_date.strftime('%Y%m%d')}.csv")
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Time", "Unique Palms Count"])
    now = datetime.now()
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), unique_palm_count])
    print(f"📝 บันทึกข้อมูลแล้ว: {now.strftime('%Y-%m-%d %H:%M:%S')} - จำนวนปาล์ม: {unique_palm_count}")


# ตัวแปรสถิติ
frame_count = 0
unique_palm_count = 0
tracked_palms = {}
next_id = 1
max_distance = 50
max_disappear = 30
cooldown_seconds = 2

# --- อ่าน FPS ของวิดีโอเพื่อ adaptive cooldown ---
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("ไม่สามารถเปิดวิดีโอได้")
    exit()
fps = cap.get(cv2.CAP_PROP_FPS)
cooldown_frames = int(fps * cooldown_seconds)

print(f"▶️ เริ่มประมวลผลวิดีโอ ({fps:.1f} FPS)")

while True:
    ret, frame = cap.read()
    if not ret:
        print("🔁 วิดีโอจบแล้ว")
        break

    frame_count += 1
    check_new_day()

    current_time = datetime.now()
    if current_time - last_log_time >= log_interval:
        log_data()
        last_log_time = current_time

    # ตัดขอบ 6%
    height, width = frame.shape[:2]
    margin_x = int(width * 0.06)
    margin_y = int(height * 0.06)
    cropped_frame = frame[margin_y:height - margin_y, margin_x:width - margin_x]

    # ตรวจจับ YOLO
    results = model.predict(
        source=cropped_frame,
        save=False,
        conf=0.001,
        stream=True,
        imgsz=320
    )

    current_frame_palms = []

    for result in results:
        boxes = result.boxes
        xyxy = boxes.xyxy
        confs = boxes.conf
        clses = boxes.cls
        palm_indices = [i for i in range(len(clses))
                        if model.names[int(clses[i])] == 'Unripe' and confs[i] >= 0.07]
        if palm_indices:
            palm_boxes = xyxy[palm_indices]
            palm_scores = confs[palm_indices]
            keep = nms(palm_boxes, palm_scores, iou_threshold=0.25)
            for i in keep:
                x1, y1, x2, y2 = map(int, palm_boxes[i])
                center = calculate_center((x1, y1, x2, y2))
                current_frame_palms.append(center)
                cv2.rectangle(cropped_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(cropped_frame, f"palm {float(palm_scores[i]):.2f}", (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)

    # --- Anti-flicker / Tracking ---
    new_palms = 0
    matched_ids = set()
    for palm_center in current_frame_palms:
        is_new = True
        matched_id = None
        for pid, data in tracked_palms.items():
            if calculate_distance(palm_center, data["center"]) < max_distance:
                is_new = False
                matched_id = pid
                break

        if is_new:
            recently_counted = False
            for pid, data in tracked_palms.items():
                if (frame_count - data["created_frame"]) < cooldown_frames and \
                   calculate_distance(palm_center, data["center"]) < max_distance * 1.5:
                    recently_counted = True
                    break
            if not recently_counted:
                new_palms += 1
                tracked_palms[next_id] = {
                    "center": palm_center,
                    "last_seen": frame_count,
                    "disappear_count": 0,
                    "created_frame": frame_count
                }
                next_id += 1
        else:
            tracked_palms[matched_id]["center"] = palm_center
            tracked_palms[matched_id]["last_seen"] = frame_count
            tracked_palms[matched_id]["disappear_count"] = 0
            matched_ids.add(matched_id)

    unique_palm_count += new_palms

    # ลบวัตถุหาย
    to_remove = [pid for pid, data in tracked_palms.items() if pid not in matched_ids and data["disappear_count"] > max_disappear]
    for pid in to_remove:
        del tracked_palms[pid]

    # แสดงผล
    cv2.putText(cropped_frame, f"Unique Palms: {unique_palm_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    cv2.putText(cropped_frame, f"Next log: {(last_log_time + log_interval).strftime('%H:%M:%S')}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(cropped_frame, f"Date: {current_day}", (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow("Video Detection", cropped_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
log_data()
cv2.destroyAllWindows()

print(f"🔢 Unique Palms: {unique_palm_count}")
print(f"📊 Total frames processed: {frame_count}")
print(f"💾 CSV saved at: {csv_file_path}")
