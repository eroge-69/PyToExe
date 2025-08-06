import win32gui
import win32ui
from ctypes import windll
from PIL import Image
import time
import os
import configparser
from discord_webhook import DiscordWebhook
import pytesseract
from diffimg import diff
from loguru import logger
import sys

# Simple ARK bot
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Setup logging like original
LOG_LEVEL = "DEBUG"
logger.remove()
logger.add(sys.stderr,
           format="<g>{time:HH:mm:ss}</g> <lvl>{message}</lvl>",
           level=LOG_LEVEL)

who = os.path.splitext(os.path.basename(__file__))[0]

# Load config
config = configparser.ConfigParser()
config.read("Tribelog bot.ini")
alert_urls = config.get("Log_Alert", "alert_urls")
roles = config.get("Role", "roles")

def is_ark_running():
    hwnd = win32gui.FindWindow(None, "ArkAscended")
    if hwnd == 0:
        logger.error("ArkAscended is not running, please start the game")
        return False
    return True

def take_screenshot():
    try:
        logger.info("Taking SS")
        hwnd = win32gui.FindWindow(None, "ArkAscended")
        if hwnd == 0:
            logger.error("ArkAscended window not found")
            return None
        
        left, top, right, bot = win32gui.GetWindowRect(hwnd)
        w = right - left
        h = bot - top
        
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        saveDC.SelectObject(saveBitMap)
        
        windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
        
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
        
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        
        img.save("screenshot.png")
        return img
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        return None

def check_logs_open(img):
    # Check TRIBES area: 100,100 to 400,200
    tribes_area = img.crop((100, 100, 400, 200))
    tribes_area = tribes_area.convert('L')
    tribes_area.save("tribes_check.png")
    
    try:
        text = pytesseract.image_to_string("tribes_check.png")
        text_clean = text.replace('\n', '').replace(' ', '').upper()
        return "TRIBES" in text_clean or "TRIBE" in text_clean
    except:
        return False

def is_scrolled_to_old_logs(img):
    # Check scroll slider at exact position 1176,216 to 1176,285
    # If light slider color is at these coords = at bottom (current logs)
    # If NOT at these coords = scrolled up (old logs)
    try:
        slider_pixels_found = 0
        total_pixels_checked = 0
        
        slider_color = (183, 246, 253)  # B7F6FD - light slider color
        
        # Check the exact vertical range
        for y in range(216, 286):  # 216 to 285 inclusive
            try:
                pixel = img.getpixel((1176, y))
                total_pixels_checked += 1
                
                # Check if pixel matches slider color (with tolerance)
                color_diff = sum(abs(a - b) for a, b in zip(pixel, slider_color))
                if color_diff < 30:  # Tighter tolerance
                    slider_pixels_found += 1
                    
            except:
                continue
        
        # If we find slider color in this exact area, we're at bottom (current logs)
        # If not, we're scrolled up (old logs)
        is_at_bottom = slider_pixels_found >= 68  # Need 68+ pixels to be at bottom
        
        # Only report if slider has 68+ pixels
        if slider_pixels_found >= 68:
            logger.debug(f"Newest logs shown")
        
        return not is_at_bottom  # Return True if scrolled to old logs
        
    except Exception as e:
        logger.debug(f"Scroll detection error: {e}")
        return False
        
    except Exception as e:
        logger.debug(f"Scroll detection error: {e}")
        return False


def create_log_report(img):
    # Create log report image for Discord
    try:
        # Get larger log area for Discord
        log_report_area = img.crop((760, 190, 1160, 500))
        log_report_area.save("log_report.png")
        return "log_report.png"
    except:
        return None

def check_for_changes(img):
    # Check if scrolled to old logs first
    if is_scrolled_to_old_logs(img):
        logger.debug("Scrolled to old logs, ignoring changes")
        return False
    
    # Monitor top of log area where new logs appear: 760,190 to 1160,230
    log_area = img.crop((760, 190, 1160, 230))
    log_area.save("log_new.png")
    
    if not os.path.exists("log_old.png"):
        log_area.save("log_old.png")
        return False
    
    try:
        diff_result = diff("log_new.png", "log_old.png", delete_diff_file=True)
        if diff_result >= 0.07:
            log_area.save("log_old.png")
            return True
    except:
        pass
    
    return False

def check_parasaur(img):
    # Parasaur area: top 30y coords
    parasaur_area = img.crop((400, 0, 756, 30))
    pixels = list(parasaur_area.getdata())
    return (0, 255, 234) in pixels  # Cyan color

def send_alert(message, image_path=None):
    try:
        webhook = DiscordWebhook(url=alert_urls, content=message)
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                webhook.add_file(file=f.read(), filename=os.path.basename(image_path))
        webhook.execute()
        logger.debug("Alert sent to Discord")
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")

def main_loop():
    logger.info(f"Starting {who}")
    failed_attempts = 0
    quick_retries = 0
    
    while True:
        try:
            if not is_ark_running():
                time.sleep(10)
                continue
            
            img = take_screenshot()
            if not img:
                time.sleep(5)
                continue
            
            if not check_logs_open(img):
                logger.debug("Logs not open, retrying in 2 seconds")
                time.sleep(2)
                continue
                
            # Reset counters when logs are open
            failed_attempts = 0
            quick_retries = 0
            
            # Check for parasaur
            if check_parasaur(img):
                logger.error("Alert Found: Parasaur Ping Detected")
                log_image = create_log_report(img)
                send_alert(f"{roles} - Parasaur, Simply Too Close - {who}", log_image)
            
            # Check for log changes
            if check_for_changes(img):
                logger.error("New log entry detected")
                log_image = create_log_report(img)
                # Get current time as Unix timestamp for Discord
                unix_timestamp = int(time.time())
                send_alert(f"<t:{unix_timestamp}:F>", log_image)
            
            logger.debug("Nothing new to report")
            time.sleep(2)
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main_loop()