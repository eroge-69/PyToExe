
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def kirim_pesan(nomor, pesan):
    url = f"https://web.whatsapp.com/send?phone={nomor}&text={pesan}"
    driver.get(url)
    time.sleep(8)
    try:
        kirim = driver.find_element(By.XPATH, '//span[@data-icon="send"]')
        kirim.click()
        time.sleep(3)
        return True
    except:
        return False

# Baca file Excel
df = pd.read_excel("data.xlsx")
options = Options()
options.add_experimental_option("detach", True)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://web.whatsapp.com")
input("Scan QR lalu tekan Enter di sini untuk mulai mengirim...")

for index, row in df.iterrows():
    no = row["NOMOR_WA"]
    pesan = row["PESAN"]
    status = kirim_pesan(no, pesan)
    print(f"Pesan ke {no}: {'BERHASIL' if status else 'GAGAL'}")

driver.quit()
