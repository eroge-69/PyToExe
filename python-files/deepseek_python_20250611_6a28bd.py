import pyautogui
import cv2
import numpy as np
import time
import random
import keyboard
import os
import sys
import base64
import json
from io import BytesIO
from PIL import Image, ImageGrab

# ===== تنظیمات اصلی =====
CONFIG_FILE = "albion_bot_config.json"
BOT_ACTIVE = False
DEBUG_MODE = True

# ===== الگوهای تصویری تعبیه شده =====
def create_template_images():
    templates = {}
    
    # الگوی درخت (Tree)
    tree_b64 = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAABKElEQVRIie2WQQ7CIBBFX8Gdu/gI9OQN2Ju4dO9dPIoLb+AJXHgDL2J6A0Niw0ATCBgXkz8paZn+ef+1A0EQ3KcDtgACUAApMAFdQ7sC2ABDpVYAK2BfqU3A3qJdgI1F+4D3aFfg7tGuwM2jXYG7R7sCN492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYH/Af0G1c5qJ2Xa0YcAAAAASUVORK5CYII="
    templates['tree'] = base64.b64decode(tree_b64)
    
    # الگوی سنگ (Rock)
    rock_b64 = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAABFklEQVRIie2W0QqDMAxFPcGdu/gI9OQN2Ju4dO9dPIoLb+AJXHgDL2J6A0Niw0ATCBgXkz8paZn+ef+1A0EQ3KcDtgACUAApMAFdQ7sC2ABDpVYAK2BfqU3A3qJdgI1F+4D3aFfg7tGuwM2jXYG7R7sCN492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sC/wB9AcHqJ2Xa0YcAAAAASUVORK5CYII="
    templates['rock'] = base64.b64decode(rock_b64)
    
    # الگوی الیاف (Fiber)
    fiber_b64 = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAABFUlEQVRIie2W0QqDMAxFz8Gdu/gI9OQN2Ju4dO9dPIoLb+AJXHgDL2J6A0Niw0ATCBgXkz8paZn+ef+1A0EQ3KcDtgACUAApMAFdQ7sC2ABDpVYAK2BfqU3A3qJdgI1F+4D3aFfg7tGuwM2jXYG7R7sCN492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sC/wB9AcHqJ2Xa0YcAAAAASUVORK5CYII="
    templates['fiber'] = base64.b64decode(fiber_b64)
    
    # الگوی پوست (Hide)
    hide_b64 = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAABFUlEQVRIie2W0QqDMAxFz8Gdu/gI9OQN2Ju4dO9dPIoLb+AJXHgDL2J6A0Niw0ATCBgXkz8paZn+ef+1A0EQ3KcDtgACUAApMAFdQ7sC2ABDpVYAK2BfqU3A3qJdgI1F+4D3aFfg7tGuwM2jXYG7R7sCN492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sC/wB9AcHqJ2Xa0YcAAAAASUVORK5CYII="
    templates['hide'] = base64.b64decode(hide_b64)
    
    # الگوی سنگ معدن (Ore)
    ore_b64 = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAABFUlEQVRIie2W0QqDMAxFz8Gdu/gI9OQN2Ju4dO9dPIoLb+AJXHgDL2J6A0Niw0ATCBgXkz8paZn+ef+1A0EQ3KcDtgACUAApMAFdQ7sC2ABDpVYAK2BfqU3A3qJdgI1F+4D3aFfg7tGuwM2jXYG7R7sCN492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sC/wB9AcHqJ2Xa0YcAAAAASUVORK5CYII="
    templates['ore'] = base64.b64decode(ore_b64)
    
    # الگوی شهر Bridgewatch
    bridgewatch_b64 = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEkSURBVEhL7ZS9DoIwFIXP6z/AxMQNExMTExMTExMTExMTExMTExMTExMTExMTE2N4A0Niw0ATCBgXkz8paZn+ef+1A0EQ3KcDtgACUAApMAFdQ7sC2ABDpVYAK2BfqU3A3qJdgI1F+4D3aFfg7tGuwM2jXYG7R7sCN492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sCd492Be4e7QrcPdoVuHu0K3D3aFfg7tGuwN2jXYG7R7sC/wB9AcHqJ2Xa0YcAAAAASUVORK5CYII="
    templates['bridgewatch'] = base64.b64decode(bridgewatch_b64)
    
    return templates

TEMPLATE_IMAGES = create_template_images()

# ===== سیستم تشخیص منابع =====
class ResourceDetector:
    @staticmethod
    def find_resource(resource_type, threshold=0.7):
        screen = np.array(ImageGrab.grab())
        template_bytes = TEMPLATE_IMAGES.get(resource_type)
        
        if not template_bytes:
            if DEBUG_MODE:
                print(f"⚠️ الگوی {resource_type} یافت نشد!")
            return None
        
        # تبدیل بایت‌ها به تصویر
        template = cv2.imdecode(np.frombuffer(template_bytes, np.uint8), cv2.IMREAD_COLOR)
        
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val > threshold:
            return max_loc
        return None

# ===== سایر کلاس‌ها (همانند نسخه قبلی) =====
class InventoryManager:
    @staticmethod
    def is_inventory_full(threshold=0.8):
        try:
            screenshot = np.array(ImageGrab.grab(bbox=(1620, 980, 1920, 1050)))
            red_pixels = np.where((screenshot[:, :, 0] > 200) & 
                                 (screenshot[:, :, 1] < 50) & 
                                 (screenshot[:, :, 2] < 50))
            fill_ratio = len(red_pixels[0]) / (screenshot.shape[0] * screenshot.shape[1])
            return fill_ratio >= threshold
        except Exception as e:
            if DEBUG_MODE:
                print(f"خطا در بررسی کیف: {e}")
            return False

class CityNavigator:
    @staticmethod
    def navigate_to_city():
        try:
            keyboard.press('m')
            time.sleep(1)
            keyboard.release('m')
            time.sleep(2)
            
            screen = np.array(ImageGrab.grab())
            city_bytes = TEMPLATE_IMAGES.get('bridgewatch')
            
            if city_bytes:
                template = cv2.imdecode(np.frombuffer(city_bytes, np.uint8), cv2.IMREAD_COLOR)
                result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                
                if max_val > 0.7:
                    pyautogui.moveTo(max_loc[0] + 15, max_loc[1] + 15, 
                                    duration=random.uniform(0.5, 1.5))
                    pyautogui.click()
                    if DEBUG_MODE:
                        print("مسیریابی به شهر Bridgewatch")
                    time.sleep(15)
                    return True
            return False
        finally:
            keyboard.press('m')
            time.sleep(1)
            keyboard.release('m')

class MarketManager:
    @staticmethod
    def sell_resources():
        try:
            keyboard.press('n')
            time.sleep(2)
            keyboard.release('n')
            time.sleep(1)
            
            pyautogui.click(1300, 250)
            time.sleep(1)
            
            pyautogui.click(1100, 400)
            time.sleep(0.5)
            
            pyautogui.click(1800, 800)
            time.sleep(1)
            
            pyautogui.click(1700, 600)
            time.sleep(2)
            
            keyboard.press('esc')
            time.sleep(0.5)
            keyboard.release('esc')
            return True
        except Exception as e:
            if DEBUG_MODE:
                print(f"خطا در فروش: {e}")
            return False

class GearUpgrader:
    TIER_COORDINATES = {2: (1450, 350), 3: (1450, 400), 4: (1450, 450), 
                        5: (1450, 500), 6: (1450, 550), 7: (1450, 600), 8: (1450, 650)}
    
    @staticmethod
    def upgrade_gear():
        try:
            keyboard.press('l')
            time.sleep(2)
            keyboard.release('l')
            
            pyautogui.click(1200, 300)
            time.sleep(1)
            
            current_tier = random.randint(2, 4)
            next_tier = current_tier + 1 if current_tier < 8 else 8
            
            if next_tier in GearUpgrader.TIER_COORDINATES:
                x, y = GearUpgrader.TIER_COORDINATES[next_tier]
                pyautogui.click(x, y)
                time.sleep(0.5)
                
                pyautogui.click(1700, 900)
                time.sleep(1)
                
                pyautogui.rightClick(1200, 950)
                time.sleep(0.5)
                pyautogui.click(1250, 900)
                time.sleep(1)
                return True
            return False
        finally:
            keyboard.press('esc')
            time.sleep(0.5)
            keyboard.release('esc')

# ===== سیستم اصلی ربات =====
class AlbionGatheringBot:
    def __init__(self):
        self.state = "GATHERING"
        self.active = False
        self.config = {
            "gathering_resources": ["tree", "rock", "fiber"],
            "min_delay": 0.5,
            "max_delay": 2.0
        }
        keyboard.add_hotkey('F2', self.toggle_active)
    
    def toggle_active(self):
        self.active = not self.active
        print(f"وضعیت ربات: {'فعال' if self.active else 'غیرفعال'}")
    
    def gather_resources(self):
        for resource in self.config["gathering_resources"]:
            location = ResourceDetector.find_resource(resource)
            if location:
                x, y = location
                pyautogui.moveTo(
                    x + random.randint(5, 20),
                    y + random.randint(5, 20),
                    duration=random.uniform(0.3, 1.0)
                )
                pyautogui.click()
                time.sleep(random.uniform(3.0, 6.0))
                
                if random.random() > 0.7:
                    pyautogui.moveRel(
                        random.randint(-50, 50),
                        random.randint(-50, 50),
                        duration=random.uniform(0.2, 0.5)
                    )
                return

    def run(self):
        print("ربات آماده است. برای شروع F2 را فشار دهید...")
        print("رزولوشن پیشنهادی: 1920x1080")
        
        while True:
            if not self.active:
                time.sleep(1)
                continue
                
            try:
                if self.state == "GATHERING":
                    self.gather_resources()
                    
                    if InventoryManager.is_inventory_full():
                        self.state = "GOING_TO_CITY"
                        if DEBUG_MODE:
                            print("کیف 80% پر شده! رفتن به شهر...")
                
                elif self.state == "GOING_TO_CITY":
                    if CityNavigator.navigate_to_city():
                        self.state = "SELLING"
                    elif DEBUG_MODE:
                        print("شهر یافت نشد! تلاش مجدد...")
                        time.sleep(5)
                
                elif self.state == "SELLING":
                    if MarketManager.sell_resources():
                        self.state = "UPGRADING"
                        if DEBUG_MODE:
                            print("موارد با موفقیت فروخته شد!")
                    elif DEBUG_MODE:
                        print("خطا در فروش! تلاش مجدد...")
                        time.sleep(5)
                
                elif self.state == "UPGRADING":
                    if GearUpgrader.upgrade_gear():
                        if DEBUG_MODE:
                            print("تجهیزات ارتقا یافت!")
                        self.state = "GATHERING"
                        # بازگشت به منطقه منابع
                        keyboard.press('m')
                        time.sleep(1)
                        pyautogui.click(1000, 300)
                        time.sleep(1)
                        keyboard.press('m')
                    elif DEBUG_MODE:
                        print("خطا در ارتقا! تلاش مجدد...")
                        time.sleep(5)
                
                delay = random.uniform(
                    self.config["min_delay"], 
                    self.config["max_delay"]
                )
                time.sleep(delay)
                
            except Exception as e:
                print(f"خطای سیستمی: {str(e)}")
                time.sleep(5)

# ===== راه‌اندازی ربات =====
if __name__ == "__main__":
    bot = AlbionGatheringBot()
    bot.run()