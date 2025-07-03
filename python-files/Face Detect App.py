import cv2
import time
import asyncio
import os
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

# ====== НАСТРОЙКИ ======
TELEGRAM_BOT_TOKEN   = "8155988167:AAGaPSkvYrEdMVJ7HCGaKkujckhPoOF8UEc"
TELEGRAM_CHAT_ID     = "7305085377"
FACE_DETECTION_TIME  = 7                   # секунд до срабатывания
CAMERA_ID = 0                   # ID камеры
WINDOW_NAME  = "Камера ▶ Лицо"     # название окна
LOG_DIR  = "logs"              # папка для логов
ENTER_COUNT  = 5                   # сколько раз нажать Enter перед стартом

class FaceAlertApp:
    def __init__(self):
        # Telegram-бот
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        # Каскад Хаара для лиц
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            raise RuntimeError("Не удалось загрузить каскад для лиц")
        # Захват видео
        self.cap = cv2.VideoCapture(CAMERA_ID)
        if not self.cap.isOpened():
            raise RuntimeError("Камера не доступна")
        # Логика детекции
        self.face_detected = False
        self.face_timer    = 0.0
        self.loop          = asyncio.get_event_loop()
        # Папка сессии для снимков и логов
        os.makedirs(LOG_DIR, exist_ok=True)
        ts = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        self.session_dir = os.path.join(LOG_DIR, ts)
        os.makedirs(self.session_dir, exist_ok=True)
        print(f"Логи будут сохраняться в: {self.session_dir}")

    def detect_and_draw(self, frame):
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "Face", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        if len(faces) > 0:
            if not self.face_detected:
                self.face_detected = True
                self.face_timer    = time.time()
            elif time.time() - self.face_timer >= FACE_DETECTION_TIME:
                snap = frame.copy()
                asyncio.ensure_future(self.send_alert(snap))
                self.face_detected = False
        else:
            self.face_detected = False
        return frame

    async def send_alert(self, frame):
        # Имя файла по дате-времени
        fn   = datetime.now().strftime("detect_%Y%m%d_%H%M%S.jpg")
        path = os.path.join(self.session_dir, fn)
        cv2.imwrite(path, frame)

        # Запись в лог
        log_line = f"{datetime.now().isoformat()} — лицо обнаружено\n"
        with open(os.path.join(self.session_dir, "log.txt"), "a", encoding="utf-8") as log:
            log.write(log_line)

        # Отправка в Telegram (до 3 попыток)
        for attempt in range(1, 4):
            try:
                with open(path, "rb") as img:
                    await self.bot.send_photo(
                        chat_id=TELEGRAM_CHAT_ID,
                        photo=img,
                        caption="Обнаружено лицо"
                    )
                print(f"Уведомление отправлено ({fn})")
                break
            except TelegramError as e:
                print(f"TelegramError (попытка {attempt}): {e}")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Ошибка при отправке: {e}")
                break

    def run(self):
        # Предстартовое сообщение с предупреждением
        print(f"Нажмите Enter {ENTER_COUNT} раз, чтобы начать. Warning: There is no coming back")
        for i in range(ENTER_COUNT):
            input(f"  Нажмите Enter ({i+1}/{ENTER_COUNT})")
        print("Запуск...")

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        print("Нажмите 'q' для выхода")
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Не удалось получить кадр")
                    break

                frame = self.detect_and_draw(frame)

                if self.face_detected:
                    elapsed = int(time.time() - self.face_timer)
                    cv2.putText(frame, f"{elapsed}s", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                cv2.imshow(WINDOW_NAME, frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # Даем asyncio-таскам время на выполнение
                self.loop.run_until_complete(asyncio.sleep(0))

        finally:
            self.cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    app = FaceAlertApp()
    app.run()
