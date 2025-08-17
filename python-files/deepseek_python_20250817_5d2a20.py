import pygame
import gtts
import os
import re
import win32gui
import win32process
import psutil
from playsound import playsound
import threading
import time

class DyingLightVoiceOver:
    def __init__(self):
        pygame.init()
        self.tts = gtts.gTTS("", lang='tr')
        self.active = False
        self.current_subtitle = ""
        self.last_subtitle = ""
        self.game_volume = 0
        self.original_volume = None
        
    def get_game_window(self):
        """Dying Light penceresini bulur"""
        def callback(hwnd, pid):
            if win32process.GetWindowThreadProcessId(hwnd)[1] == pid:
                if "Dying Light" in win32gui.GetWindowText(hwnd):
                    return hwnd
            return None

        for proc in psutil.process_iter(['pid', 'name']):
            if "DyingLight.exe" in proc.info['name']:
                return win32gui.EnumWindows(callback, proc.info['pid'])
        return None

    def capture_subtitles(self):
        """Ekrandaki altyazıları yakalar (OCR ile)"""
        # Bu kısım OCR kütüphaneleri gerektirir (pytesseract gibi)
        # Basit örnek:
        game_window = self.get_game_window()
        if game_window:
            rect = win32gui.GetWindowRect(game_window)
            screenshot = pygame.image.fromstring(
                pygame.display.get_surface().subsurface(rect).tobytes(),
                (rect[2]-rect[0], rect[3]-rect[1]), "RGB"
            )
            # OCR işlemi burada yapılacak
            # text = pytesseract.image_to_string(screenshot)
            # return text
        return ""

    def adjust_game_audio(self, mute=True):
        """Oyun sesini ayarlar"""
        if mute:
            # Oyun sesini kısma/kapatma
            self.original_volume = self.get_current_volume()
            self.set_volume(0)
        else:
            # Orijinal sesi geri yükleme
            if self.original_volume is not None:
                self.set_volume(self.original_volume)

    def text_to_speech(self, text):
        """Metni sese dönüştürür"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
            self.tts.text = text
            self.tts.save(fp.name)
            playsound(fp.name)
            os.unlink(fp.name)

    def run(self):
        """Ana çalışma döngüsü"""
        while True:
            current_text = self.capture_subtitles()
            if current_text and current_text != self.last_subtitle:
                self.adjust_game_audio(mute=True)
                self.text_to_speech(current_text)
                self.last_subtitle = current_text
                self.adjust_game_audio(mute=False)
            time.sleep(0.1)

if __name__ == "__main__":
    vo = DyingLightVoiceOver()
    vo.run()