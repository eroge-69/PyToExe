
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ---------- الإعدادات ----------
GROUP_NAME = "فواتير شركة مساكن فيو 🏠"
BASE_DOWNLOAD_DIR = "WhatsApp_Downloads_PDF"

# ---------- إعداد متصفح كروم ----------
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ---------- فتح واتساب ويب ----------
driver.get("https://web.whatsapp.com")
input("📷 امسح رمز QR ثم اضغط Enter بعد تسجيل الدخول...")

# ---------- البحث عن القروب ----------
search_box = driver.find_element(By.XPATH, '//div[@title="بحث"]')
search_box.click()
search_box.send_keys(GROUP_NAME)
time.sleep(2)

group = driver.find_element(By.XPATH, f'//span[@title="{GROUP_NAME}"]')
group.click()
time.sleep(2)

# ---------- فتح "الوسائط والروابط والمستندات" ----------
menu = driver.find_element(By.XPATH, '//span[@data-icon="menu"]')
menu.click()
time.sleep(1)

media_option = driver.find_element(By.XPATH, '//div[@title="الوسائط، الروابط والمستندات"]')
media_option.click()
time.sleep(2)

# ---------- تبويب المستندات ----------
docs_tab = driver.find_element(By.XPATH, '//div[text()="المستندات"]')
docs_tab.click()
time.sleep(2)

# ---------- تحميل ملفات PDF ----------
print("⏳ جاري تحميل روابط ملفات PDF...")

pdf_links = set()
scroll_area = driver.find_element(By.CLASS_NAME, "_3Bc7H")

for _ in range(10):  # زيد الرقم حسب عدد الملفات
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_area)
    time.sleep(3)

    items = driver.find_elements(By.XPATH, '//div[contains(@class, "_2AOIt")]')
    for item in items:
        try:
            filename_element = item.find_element(By.XPATH, './/span[contains(text(), ".pdf")]')
            sender_element = item.find_element(By.XPATH, './/span[contains(@class, "_1VzZY") or contains(@class, "_1tceJ")]')
            file_link = item.find_element(By.TAG_NAME, "a").get_attribute("href")

            if ".pdf" in filename_element.text.lower() and file_link:
                pdf_links.add((file_link, filename_element.text, sender_element.text))
        except:
            continue

print(f"✅ تم العثور على {len(pdf_links)} ملف PDF")

# ---------- تنزيل الملفات ----------
for link, filename, sender in pdf_links:
    try:
        folder_path = os.path.join(BASE_DOWNLOAD_DIR, sender.strip())
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, filename)

        response = requests.get(link)
        with open(file_path, 'wb') as f:
            f.write(response.content)

        print(f"✔️ تم تحميل: {file_path}")
    except Exception as e:
        print(f"❌ فشل تحميل {filename}: {e}")

driver.quit()
print("🎉 انتهى التحميل.")
