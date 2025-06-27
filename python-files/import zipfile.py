import zipfile
import os

# Siapkan folder tempat file akan dikumpulkan
folder_path = "/mnt/data/wa_blast_package"
os.makedirs(folder_path, exist_ok=True)

# Buat file Excel dummy (data.xlsx)
import pandas as pd

data = {
    "NO": [1, 2],
    "NOMOR_WA": ["6281234567890", "6289876543210"],
    "PESAN": [
        "Halo, ini pesan promo dari kami.",
        "Hai Kak! Yuk cek promo terbaru di website kami."
    ]
}

df = pd.DataFrame(data)
excel_path = os.path.join(folder_path, "data.xlsx")
df.to_excel(excel_path, index=False)

# Tambahkan placeholder script Python yang nanti akan di-convert ke .exe
script_code = """
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
"""

# Simpan script sebagai .py file
script_path = os.path.join(folder_path, "wa_blast.py")
with open(script_path, "w") as f:
    f.write(script_code)

# Kompres semua file jadi satu .zip untuk didownload
zip_path = "/mnt/data/WA_Blast_Package.zip"
with zipfile.ZipFile(zip_path, 'w') as zipf:
    zipf.write(excel_path, arcname="data.xlsx")
    zipf.write(script_path, arcname="wa_blast.py")

zip_path
