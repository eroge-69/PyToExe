import cv2
from ffpyplayer.player import MediaPlayer
import os

def shutdown_computer():
    # Выключение компьютера (Windows)
    os.system("shutdown /s /t 0")

def play_video_fullscreen(video_path):
    # Создаем медиаплеер для воспроизведения видео со звуком
    player = MediaPlayer(video_path)

    # Открываем видео с помощью OpenCV для получения размеров
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Не удалось открыть видео")
        return

    # Получаем размеры видео (не обязательно, если не используете)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Создаем окно в полноэкранном режиме
    window_name = "Gabriel"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        grabbed, frame = cap.read()
        if not grabbed:
            break

        # Получаем текущий статус воспроизведения для звука
        audio_frame, val = player.get_frame()
        if val != 'eof' and audio_frame is not None:
            pass  # Можно обработать аудио при необходимости

        # Отображаем кадр
        cv2.imshow(window_name, frame)

        # Ждем 25 мс или закрытия окна
        key = cv2.waitKey(25) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # После окончания воспроизведения вызываем функцию выключения
    shutdown_computer()

if __name__ == "__main__":
    video_path = r"C:\Users\MindStealer\Desktop\Эй! Хватит листать!.mp4"  # замените на ваш путь
    play_video_fullscreen(video_path)