import cv2
import numpy as np
import pyautogui
import os
import easyocr
from PIL import Image, ImageGrab, ImageEnhance, ImageFilter
import re
from typing import List, Tuple, Optional

#pip install opencv-python numpy pyautogui easyocr pillow

class GameBot:
    def __init__(self, languages=['en'], gpu=True, verbose=False):
        pyautogui.FAILSAFE = True
        
        self.templates = {}
        print("Initializing EasyOCR (this may take a moment on first run)...")
        try:
            self.reader = easyocr.Reader(languages, gpu=gpu, verbose=verbose)
            print("EasyOCR initialized successfully!")
        except Exception as e:
            print(f"Error initializing EasyOCR: {e}")
            print("Falling back to CPU mode...")
            self.reader = easyocr.Reader(languages, gpu=False, verbose=verbose)
        
        self.languages = languages
        
    
    def load_template(self, template_path, name):
        if os.path.exists(template_path):
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            self.templates[name] = template
            print(f"Loaded template: {name}")
            return True
        else:
            print(f"Template not found: {template_path}")
            return False
    
    def capture_screen(self, region=None):
        if region:
            screenshot = ImageGrab.grab(bbox=region)
        else:
            screenshot = ImageGrab.grab()
        
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return screenshot_cv
    
    def find_image_on_screen(self, template_name, threshold=0.8, region=None):
        if template_name not in self.templates:
            print(f"Template {template_name} not loaded!")
            return []
        
        screen = self.capture_screen(region)
        template = self.templates[template_name]
        
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        
        locations = np.where(result >= threshold)
        matches = []
        
        h, w = template.shape[:2]
        
        for pt in zip(*locations[::-1]):
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            
            if region:
                center_x += region[0]
                center_y += region[1]
                
            matches.append((center_x, center_y))
        
        filtered_matches = self.filter_close_matches(matches, min_distance=20)
        
        return filtered_matches
    
    def filter_close_matches(self, matches, min_distance=20):
        if not matches:
            return matches
            
        filtered = []
        for match in matches:
            is_unique = True
            for existing in filtered:
                distance = np.sqrt((match[0] - existing[0])**2 + (match[1] - existing[1])**2)
                if distance < min_distance:
                    is_unique = False
                    break
            if is_unique:
                filtered.append(match)
        
        return filtered
    
    def click_at_position(self, x, y, button='left', clicks=2, ):
        try:
            pyautogui.click(x, y, clicks=clicks, button=button)
            print(f"Clicked at ({x}, {y})")
            return True
        except Exception as e:
            print(f"Failed to click: {e}")
            return False
    
    def click_all_matches(self, template_name, threshold=0.8, region=None, delay=0, clickingBro=True):
        matches = self.find_image_on_screen(template_name, threshold, region)
        
        if not matches:
            print(f"No matches found for {template_name}")
            return 0
        
        print(f"Found {len(matches)} matches for {template_name}")
        
        clicked_count = 0
        for x, y in matches:
            
            if clicked_count >= 8:
                return clicked_count
            if clickingBro:
                y = y + 35
            if self.click_at_position(x, y):
                clicked_count += 1
        
        return clicked_count
    

    def capture_region(self, region: Tuple[int, int, int, int]) -> Optional[Image.Image]:
        try:
            left, top, width, height = region
            bbox = (left, top, left + width, top + height)
            screenshot = ImageGrab.grab(bbox=bbox)
            return screenshot
        except Exception as e:
            print(f"Error capturing region: {e}")
            return None
    
    def preprocess_image(self, image: Image.Image, enhance_contrast=True, 
                        sharpen=True, invert=False, threshold=None, 
                        scale_factor=2) -> np.ndarray:
        if image.mode != 'L':
            image = image.convert('L')
        
        if scale_factor > 1:
            width, height = image.size
            image = image.resize((width * scale_factor, height * scale_factor), Image.LANCZOS)
        
        if enhance_contrast:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
        
        if sharpen:
            image = image.filter(ImageFilter.SHARPEN)
        
        if threshold:
            image = image.point(lambda p: 255 if p > threshold else 0)
        
        if invert:
            image = image.point(lambda p: 255 - p)
        
        return np.array(image)
    
    def read_text_from_region(self, region: Tuple[int, int, int, int], 
                             preprocess=True, confidence_threshold=0.5,
                             detail=0) -> str:
        image = self.capture_region(region)
        if not image:
            return ""
        
        if preprocess:
            image_array = self.preprocess_image(image)
        else:
            image_array = np.array(image)
        
        try:
            results = self.reader.readtext(image_array, detail=1)
            
            texts = []
            for (bbox, text, confidence) in results:
                if confidence >= confidence_threshold:
                    texts.append(text)
            
            full_text = ' '.join(texts).strip()
            
            if detail == 0:
                return full_text
            elif detail == 1:
                return [(text, conf) for (bbox, text, conf) in results if conf >= confidence_threshold]
            else:
                return [(bbox, text, conf) for (bbox, text, conf) in results if conf >= confidence_threshold]
                
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
    
    def save_region_image(self, region: Tuple[int, int, int, int], 
                         filename="region_capture.png"):
        image = self.capture_region(region)
        if not image:
            return False
        image.save(filename)
        print(f"Region saved as {filename}")
        return True
    
    def move_mouse_to_center_and_scroll(self, scroll_clicks=5, scroll_direction='out'):
        try:
            screen_width, screen_height = pyautogui.size()
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            pyautogui.moveTo(center_x, center_y)
            print(f"Moved mouse to center of screen: ({center_x}, {center_y})")
            
            scroll_amount = -scroll_clicks if scroll_direction == 'out' else scroll_clicks
            pyautogui.scroll(scroll_amount)
            print(f"Scrolled {scroll_direction} with {scroll_clicks} clicks")
            
            return True
        except Exception as e:
            print(f"Failed to move mouse and scroll: {e}")
            return False
    
    
def extract_numbers(text: str) -> List[str]:
    matches = re.findall(r'-?\d+\.?\d*', text)
    if len(matches) > 0:
        return int(matches[0])
    return 0

def main():
    bot = GameBot()
    bot.load_template("check.png", "check")
    bot.load_template("accept.png", "accept")
    bot.load_template("HelpTheGuy.png", "HelpTheGuy_button")
    game_region = None
    moves_region = (0,230,122,30)
    gamea_region = (242,93,1410,825) 
    while True:
        try:
            accept = bot.find_image_on_screen("accept", threshold=0.8, region=gamea_region)
            
            if accept:
                x, y = pyautogui.position()
                bot.click_all_matches("accept", threshold=0.8, region=gamea_region,clickingBro=False)
                pyautogui.moveTo(x, y, duration=0)
            else:
                check = bot.find_image_on_screen("check", threshold=0.8, region=game_region)
                
                if(check):
                    print("\n1. Reading score region:")
                    score_text = bot.read_text_from_region(moves_region)
                    print(f"   Raw text: '{score_text}'")
                    numbers = extract_numbers(score_text)
                    if score_text.startswith("X") and not score_text == "X0" and not score_text == "XO":
                        #bot.move_mouse_to_center_and_scroll(scroll_clicks=200000, scroll_direction='out')
                        x, y = pyautogui.position()
                        print(f"   Extracted numbers: {numbers or 1}")
                        print("Looking for HelpTheGuy buttons...")
                        clicked = bot.click_all_matches("HelpTheGuy_button", threshold=0.8, region=gamea_region)
                        if clicked:
                            pyautogui.moveTo(x, y, duration=0)

            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
