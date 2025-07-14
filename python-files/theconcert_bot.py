from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# --- ข้อมูลผู้ใช้ ---
EMAIL = "test123@gmail.com"
PASSWORD = "1234565sds"
CONCERT_URL = "https://www.theconcert.com/concert/4232"
ZONE_NAME = "71"  # ชื่อโซน
# --------------------

def main():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    print("เปิดเว็บ TheConcert...")
    driver.get("https://www.theconcert.com/login")

    # ล็อกอิน
    time.sleep(2)
    driver.find_element(By.NAME, "email").send_keys(EMAIL)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[contains(text(), 'เข้าสู่ระบบ')]").click()

    time.sleep(3)  # รอ redirect

    # เข้าหน้าคอนเสิร์ต
    driver.get(CONCERT_URL)

    # รอปุ่มซื้อบัตร
    print("รอปุ่ม 'ซื้อบัตร' ...")
    while True:
        try:
            buy_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'ซื้อบัตร')]")
            if buy_btn.is_enabled():
                buy_btn.click()
                print("กดซื้อบัตรแล้ว")
                break
        except:
            time.sleep(0.2)

    # รอหน้าเลือกโซนขึ้น แล้วคลิกโซน 71
    print("กำลังเลือกโซน 71 ...")
    while True:
        try:
            zone_btn = driver.find_element(By.XPATH, f"//div[contains(text(), '{ZONE_NAME}')]")
            if zone_btn.is_displayed():
                zone_btn.click()
                print(f"เลือกโซน {ZONE_NAME} แล้ว")
                break
        except:
            time.sleep(0.2)

    print("โปรดเลือกที่นั่ง และกดต่อไป")
    input("กด Enter เมื่อต้องการปิดโปรแกรม...")
    driver.quit()

if __name__ == "__main__":
    main()
