import time
import os
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO

# تنظیمات Tesseract (مسیر را بر اساس سیستم خود تغییر دهید)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # ویندوز
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # لینوکس/مک

# مشخصات کاربری
USERNAME = "09123456789"  # شماره موبایل یا نام کاربری
PASSWORD = "yourpassword"  # رمز عبور

# مسیر ChromeDriver
CHROME_DRIVER_PATH = "./chromedriver"  # اگر در کنار فایل پایتون است

# آدرس سایت
LOGIN_URL = "https://nobatdehi.epolice.ir/login"

# تنظیمات WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)

def solve_captcha(image_element):
    """حل کپچا با استفاده از Tesseract OCR"""
    # اسکرین‌شات از عنصر کپچا
    location = image_element.location
    size = image_element.size
    screenshot = driver.get_screenshot_as_png()
    screenshot = Image.open(BytesIO(screenshot))

    # بریدن تصویر کپچا از اسکرین‌شات
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    captcha_image = screenshot.crop((left, top, right, bottom))

    # ذخیره موقت برای تست (اختیاری)
    captcha_image.save("captcha.png")

    # استخراج متن با Tesseract
    captcha_text = pytesseract.image_to_string(captcha_image, config='--psm 6')
    return captcha_text.strip()

try:
    # باز کردن سایت
    driver.get(LOGIN_URL)

    # انتظار برای بارگذاری فرم ورود
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    # وارد کردن نام کاربری
    username_field = driver.find_element(By.NAME, "username")
    username_field.send_keys(USERNAME)

    # وارد کردن رمز عبور
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(PASSWORD)

    # حل کپچا
    captcha_img = driver.find_element(By.CLASS_NAME, "captcha_image")
    captcha_text = solve_captcha(captcha_img)

    captcha_field = driver.find_element(By.NAME, "sec_code_login")
    captcha_field.send_keys(captcha_text)

    # کلیک روی دکمه ورود
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()

    # انتظار برای ورود موفق
    time.sleep(5)

    print("✅ ورود با موفقیت انجام شد.")

except Exception as e:
    print(f"❌ خطا در اجرای ربات: {e}")

finally:
    # بستن مرورگر
    driver.quit()