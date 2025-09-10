import time
from datetime import datetime
from playsound import playsound
from PIL import Image

# === SETUP ===
AUDIO_PATH = "D:/Ms Office/New folder/happy_birthday.mp3"    # Replace with your audio file path
IMAGE_PATH = "D:/Ms Office/New folder/birthday_image.jpeg"    # Replace with your image file path
# ==============

def play_audio(audio_path):
    try:
        playsound(audio_path)
    except Exception as e:
        # print(f"Error playing audio: {e}")
        pass

def show_image(image_path):
    try:
        img = Image.open(image_path)
        img.show()
    except Exception as e:
        # print(f"Error showing image: {e}")
        pass

def wish_birthday():
    # print("🎉 It's 12:00 AM! Happy Birthday, Saksham! 🎉")
    show_image(IMAGE_PATH)
    play_audio(AUDIO_PATH)

def wait_until_midnight():
    # print("⏳ Waiting until 12:00 AM to play birthday wish...")

    already_wished = False

    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0 and not already_wished:
            wish_birthday()
            already_wished = True
        elif now.minute != 0:
            already_wished = False  # reset for next day
        time.sleep(1)

if __name__ == "__main__":
    wait_until_midnight()
