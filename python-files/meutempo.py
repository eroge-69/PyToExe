import requests
import os
import math
import sys
import time
# os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# import pygame
from pygame import mixer

def get_temperature():
    url = "https://api.open-meteo.com/v1/forecast?latitude=-23.55&longitude=-46.63&current_weather=true"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        temp = data['current_weather']['temperature']
        return int(round(temp))
    except Exception as e:
        return None

def play_audio(temp):
    mixer.init()
    audio_file = os.path.join(os.path.dirname(sys.argv[0]), f"{temp}.mp3")
    if not os.path.isfile(audio_file):
        return False
    mixer.music.load(audio_file)
    mixer.music.play()
    while mixer.music.get_busy():
        time.sleep(0.1)
    mixer.quit()
    return True

def main():
    temp = get_temperature()
    if temp is None or temp < 0 or temp > 50:
        return  # Silencioso: não fazer nada
    play_audio(temp)

if __name__ == "__main__":
    main()
