import time
import random
import subprocess

import string

time.sleep(3)
# 15 haneli bir sayı üret
imei = random.randint(10 ** 14, 10 ** 15 - 1)
imsi = random.randint(10 ** 14, 10 ** 15 - 1)
serial = random.randint(10 ** 19, 10 ** 20 - 1)


def androidi_id(length=16):
    characters = string.ascii_uppercase + string.digits  # A-Z + 0-9
    return ''.join(random.choices(characters, k=length))


def mac(length=12):
    characters = string.ascii_uppercase + string.digits  # A-Z + 0-9
    return ''.join(random.choices(characters, k=length))


brands = ["Samsung", "Apple", "Huawei", "Xiaomi", "OnePlus", "Google"]

# Marka bazlı modeller sözlüğü
models = {
    "Samsung": ["Galaxy S21a", "Galaxy Note 20a", "Galaxy A52a", "Galaxy Z Fold3a"],
    "Apple": ["iPhone 13a", "iPhone 12a", "iPhone SEa", "iPhone 11a"],
    "Huawei": ["P50 Proa", "Mate 40a", "Nova 8a", "Y9aa"],
    "Xiaomi": ["Mi 11a", "Redmi Note 10a", "Poco X3a", "Mi Mix 4a"],
    "OnePlus": ["9 Proa", "Nord 2a", "8aT", "7aT Pro"],
    "Google": ["Pixel a6", "Pixel 5aa", "Pixel 4aa", "Pixel 4 XaL"]
}


def random_brand():
    return random.choice(brands)


def random_model(brand):
    return random.choice(models.get(brand, [])) if brand in models else None


# Kullanım örneği
brand = random_brand()
model = random_model(brand)

print("RANDOM IMEİ NUMARASI:", imei)
time.sleep(1)
print("RANDOM IMSİ NUMARASI:", imsi)
time.sleep(1)
print("RANDOM SERİAL NUMARASI:", serial)
time.sleep(1)
print("RANDOM ANDORİD İD NUMARASI:", androidi_id())
time.sleep(1)
print("RANDOM TELEFON MARKASI:", brand)
time.sleep(1)
print("RANDOM TELEFON MODELİ:", model)
time.sleep(1)
print("RANDOM MAC ADRESİ:", mac())
time.sleep(1)
filename = "C:/LDPlayer/LDPlayer9/vms/config/leidian0.config"

with open(filename, "r", encoding="utf-8") as file:
    lines = file.readlines()

# Örneğin 3. satırı (index 2) güncelle
lines[1] = '    "propertySettings.phoneIMEI": "' + str(imei) + '",\n'
lines[2] = '    "propertySettings.phoneIMSI": "' + str(imsi) + '",\n'
lines[3] = '    "propertySettings.phoneSimSerial": "' + str(serial) + '",\n'
lines[4] = '    "propertySettings.phoneAndroidId": "' + androidi_id() + '",\n'
lines[5] = '    "propertySettings.phoneModel": "' + model + '",\n'
lines[6] = '    "propertySettings.phoneManufacturer": "' + brand + '",\n'
lines[7] = '    "propertySettings.macAddress": "' + mac() + '",\n'

with open(filename, "w", encoding="utf-8") as file:
    file.writelines(lines)

print("EMİLETÖR BİLGİLERİ DEĞİŞTİRİLDİ")
time.sleep(2)

exe_yolu = r"C:/LDPlayer/LDPlayer9/dnplayer.exe"
subprocess.Popen([exe_yolu])
print("EMİLETÖR BAŞLATILIYOR BİLGİSAYAR HIZINA GÖRE DEĞİŞİR LÜTFEN BEKLEYİN")


time.sleep(1000)


def kapat_exe(program_adi):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] and program_adi.lower() in process.info['name'].lower():
            print(f"{process.info['name']} kapatılıyor... (PID: {process.info['pid']})")
            process.kill()

kapat_exe("dnplayer.exe")