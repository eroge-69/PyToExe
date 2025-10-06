import cv2
import os
import time

def take_photo():
    # مسیر ذخیره عکس
    save_path = r"C:\Users\Sajjad\Pictures\das"
    os.makedirs(save_path, exist_ok=True)  # اگر فولدر وجود نداشت، بسازه

    # فعال‌سازی دوربین
    cam = cv2.VideoCapture(0)
    time.sleep(2)  # تأخیر برای آماده شدن دوربین

    ret, frame = cam.read()
    if ret:
        filename = f"photo_{int(time.time())}.jpg"
        full_path = os.path.join(save_path, filename)
        cv2.imwrite(full_path, frame)
        print(f"Sveeds: {full_path}")
    else:
        print("Filed")

    cam.release()

if __name__ == "__main__":
    take_photo()
