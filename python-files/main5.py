import os
import cv2
import torch
from datetime import datetime
import json
import pyodbc
import easyocr
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import numpy as np
from hezar.models import Model 
import re 

FRAMES_DIR = "saved_frames"

# Load YOLOv5 models for plate and chars
plate_model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/plateYolo.pt')
chars_model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/CharsYolo.pt')
reader = easyocr.Reader(['fa', 'en'], gpu=False)

# TrOCR setup for English
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
trocr_model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')

# For YOLOv8x, use official ultralytics API
from ultralytics import YOLO
vehicle_model = YOLO('models/yolov8x.pt')

# Load the specific Hezar OCR model for Persian license plates
hezar_lp_ocr_model = Model.load("hezarai/crnn-fa-license-plate-recognition-v2")


def detect_language_easyocr(plate_img):
    result = reader.readtext(plate_img)
    texts = [r[1] for r in result]
    full_text = " ".join(texts)

    is_farsi = any('\u0600' <= ch <= '\u06FF' for ch in full_text)
    is_english = any('A' <= ch <= 'Z' or 'a' <= ch <= 'z' for ch in full_text)

    if is_farsi and not is_english:
        return 'fa'
    elif is_english and not is_farsi:
        return 'en'
    elif is_farsi and is_english:
        # If both are present, prioritize Farsi based on typical plate scenarios
        return 'fa' 
    return 'unknown'

def extract_plate_text_farsi(plate_img):
    results_chars = chars_model(plate_img)
    labels = results_chars.names
    detected = results_chars.xyxy[0].cpu().numpy()
    
    if len(detected) == 0:
        return ""
    
    detected = sorted(detected, key=lambda x: x[0]) 
    
    plate_text = ""
    for det in detected:
        cls_id = int(det[5])
        char_label = labels.get(cls_id, "")
        plate_text += char_label
    return plate_text

def extract_plate_text_farsi_hezar(plate_img):
    pil_img = Image.fromarray(cv2.cvtColor(plate_img, cv2.COLOR_BGR2RGB))
    try:
        hezar_result = hezar_lp_ocr_model.predict(pil_img)
        # بررسی اینکه آیا نتیجه یک لیست از دیکشنری است یا نه
        if isinstance(hezar_result, list) and len(hezar_result) > 0:
            if isinstance(hezar_result[0], dict) and 'text' in hezar_result[0]:
                return hezar_result[0]['text'].strip()
        # اگر خود نتیجه یک دیکشنری باشد
        elif isinstance(hezar_result, dict) and 'text' in hezar_result:
            return hezar_result['text'].strip()
        # در غیر این صورت به صورت string تبدیل کن
        else:
            result_str = str(hezar_result).strip()
            # حذف کاراکترهای اضافی مثل [{'text': ' و '}]
            if result_str.startswith("[{'text': '") and result_str.endswith("'}]"):
                return result_str[11:-3]
            return result_str
    except Exception as e:
        print(f"خطا در استفاده از Hezar OCR (مدل پلاک): {e}")
        return ""

def extract_plate_text_english(plate_img):
    pil_img = Image.fromarray(cv2.cvtColor(plate_img, cv2.COLOR_BGR2RGB))
    pixel_values = processor(images=pil_img, return_tensors="pt").pixel_values
    generated_ids = trocr_model.generate(pixel_values)
    plate_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return plate_text.strip()

def load_db_config(config_file='dbConfig.json'):
    with open(config_file, 'r') as f:
        return json.load(f)

def insert_traffic_record(plate, plateX1, plateY1, plateX2, plateY2, vehicleX1, vehicleY1, vehicleX2, vehicleY2, pass_datetime, plate_language, camera_time):
    config = load_db_config()
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={config['server']};"
        f"DATABASE={config['database']};"
        f"UID={config['username']};"
        f"PWD={config['password']};"
        f"TrustServerCertificate={'yes' if config.get('TrustServerCertificate') else 'no'};"
    )
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dbo.MahdiTest 
                (PlateText, PlateX1, PlateY1, PlateX2, PlateY2, VehicleX1, VehicleY1, VehicleX2, VehicleY2, PassDateTime, PlateLanguage, CameraTime)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (plate, plateX1, plateY1, plateX2, plateY2, vehicleX1, vehicleY1, vehicleX2, vehicleY2, pass_datetime, plate_language, camera_time))
            cursor.execute("SELECT @@IDENTITY")
            result = cursor.fetchone()
            conn.commit()
            if result and result[0] is not None:
                return int(result[0])
    except Exception as e:
        print("خطا در درج اطلاعات:", e)
    return None

def contains_persian_char(text):
    """Checks if the given text contains any Persian characters."""
    return any('\u0600' <= ch <= '\u06FF' for ch in text)

def is_persian_plate_format(text):
    """
    Checks if the given text matches a typical Iranian license plate format 
    (1 Persian letter and 7 digits), considering the total character count.
    """
    cleaned_text = re.sub(r'[^\d\u0600-\u06FF]', '', text) 
    persian_chars_count = len(re.findall(r'[\u0600-\u06FF]', cleaned_text))
    digits_count = len(re.findall(r'\d', cleaned_text))
    
    return persian_chars_count == 1 and digits_count == 7 and len(cleaned_text) == 8


def show_all_images():
    files = [f for f in os.listdir(FRAMES_DIR) if f.lower().endswith(('.jpg', '.png', '.bmp'))]
    files.sort()
    print(f"تعداد فریم‌ها: {len(files)}")

    for idx, file in enumerate(files):
        try:
            path = os.path.join(FRAMES_DIR, file)
            img = cv2.imread(path)
            if img is None:
                print(f"فایل {file} قابل خواندن نیست. رد شد.")
                continue

            # استخراج زمان و زمان دوربین از نام فایل
            filename_core = os.path.splitext(file)[0]
            parts = filename_core.split('_')
            if len(parts) >= 3:
                datetime_part = "_".join(parts[0:2])
                camera_time_str = parts[2]
                try:
                    PassDateTime = datetime.strptime(datetime_part, "%Y-%m-%d_%H-%M-%S-%f")
                    camera_time = int(camera_time_str)
                except Exception as e:
                    print(f"خطا در تبدیل تاریخ یا زمان دوربین در فایل {file}: {e}")
                    PassDateTime = datetime.now()
                    camera_time = 0
            else:
                print(f"ساختار نام فایل نامعتبر است: {file}")
                PassDateTime = datetime.now()
                camera_time = 0

            # تشخیص خودرو با YOLO
            results_vehicle = vehicle_model(img)
            vehicle_boxes_list = []
            if isinstance(results_vehicle, list):
                for res in results_vehicle:
                    if hasattr(res, 'boxes') and res.boxes is not None:
                        vehicle_boxes_list.extend(res.boxes.xyxy.cpu().numpy())
            else:
                if hasattr(results_vehicle, 'boxes') and results_vehicle.boxes is not None:
                    vehicle_boxes_list.extend(results_vehicle.boxes.xyxy.cpu().numpy())

            vehicle_boxes = np.array(vehicle_boxes_list)
            vehicle_x1, vehicle_y1, vehicle_x2, vehicle_y2 = (0, 0, img.shape[1], img.shape[0])
            if len(vehicle_boxes) > 0:
                best_vehicle = max(vehicle_boxes, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))
                vehicle_x1, vehicle_y1, vehicle_x2, vehicle_y2 = map(int, best_vehicle[:4])
                cv2.rectangle(img, (vehicle_x1, vehicle_y1), (vehicle_x2, vehicle_y2), (0, 255, 0), 2)

            # تشخیص پلاک
            results_plate = plate_model(img)
            plate_boxes = results_plate.xyxy[0].cpu().numpy()

            if len(plate_boxes) == 0:
                print(f"پلاک در فریم {file} پیدا نشد! رد شد.")
                continue

            best_plate = max(plate_boxes, key=lambda x: x[4])
            x1, y1, x2, y2 = map(int, best_plate[:4])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

            plate_crop = img[y1:y2, x1:x2]
            if plate_crop.shape[0] == 0 or plate_crop.shape[1] == 0:
                print(f"تصویر پلاک برش خورده در فریم {file} خالی است. رد شد.")
                continue

            # مرحله OCR
            plate_text_yolo_chars = extract_plate_text_farsi(plate_crop)
            easyocr_lang = detect_language_easyocr(plate_crop)

            plate_text = ""
            final_plate_language = 'unknown'

            if contains_persian_char(plate_text_yolo_chars) and is_persian_plate_format(plate_text_yolo_chars):
                plate_text = plate_text_yolo_chars
                final_plate_language = 'fa'
            else:
                if easyocr_lang == 'fa':
                    plate_text_hezar = extract_plate_text_farsi_hezar(plate_crop)
                    if contains_persian_char(plate_text_hezar) and is_persian_plate_format(plate_text_hezar):
                        plate_text = plate_text_hezar
                        final_plate_language = 'fa'
                    else:
                        plate_text_eng = extract_plate_text_english(plate_crop)
                        if re.search(r'\d', plate_text_eng):
                            plate_text = plate_text_eng
                            final_plate_language = 'en'
                        else:
                            plate_text_retry = extract_plate_text_farsi_hezar(plate_crop)
                            if contains_persian_char(plate_text_retry):
                                plate_text = plate_text_retry
                                final_plate_language = 'fa'
                            else:
                                plate_text = plate_text_eng
                                final_plate_language = 'en'
                else:
                    plate_text_eng = extract_plate_text_english(plate_crop)
                    if re.search(r'\d', plate_text_eng):
                        plate_text = plate_text_eng
                        final_plate_language = 'en'
                    else:
                        plate_text_retry = extract_plate_text_farsi_hezar(plate_crop)
                        if contains_persian_char(plate_text_retry):
                            plate_text = plate_text_retry
                            final_plate_language = 'fa'
                        else:
                            plate_text = plate_text_eng
                            final_plate_language = 'en'

            print("-----------------------------------------------------")
            print(f"پلاک نهایی: {plate_text}")
            print(f"زبان تشخیص داده‌شده: {final_plate_language}")
            print(f"زمان دوربین: {camera_time}")

            # ثبت در پایگاه داده
            idValue = insert_traffic_record(
                plate_text, x1, y1, x2, y2,
                vehicle_x1, vehicle_y1, vehicle_x2, vehicle_y2,
                PassDateTime, final_plate_language, camera_time
            )

            if idValue is not None:
                save_dir = "images"
                os.makedirs(save_dir, exist_ok=True)
                cv2.imwrite(os.path.join(save_dir, f"{idValue}_Vehicle.jpg"), img)
                cv2.imwrite(os.path.join(save_dir, f"{idValue}_Plate.jpg"), plate_crop)
                print(f"ثبت موفق. ID = {idValue}")

            print(f"({idx+1}/{len(files)}) - {file}")
            key = cv2.waitKey(300)
            if key in [27, ord('q')]:
                break

        except Exception as e:
            print(f"خطای غیرمنتظره در پردازش فایل {file}: {e}")
            continue

    cv2.destroyAllWindows()


if __name__ == "__main__":
    show_all_images()
