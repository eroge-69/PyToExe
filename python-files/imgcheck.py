import hashlib
import subprocess
import sys
import time
import os
import ctypes
import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab

def get_motherboard_uuid():
    try:
        output = subprocess.check_output([
            'powershell', 
            '-Command', 
            '(Get-CimInstance -Class Win32_ComputerSystemProduct).UUID'
        ], shell=True)
        
        uuid = output.decode().strip()
        return uuid
    except Exception as e:
        print("HWID alınamadı:", e)
        return None

def validate_license():
    salt = "3233!" 
    stored_license_key = "4b628f0c850d9f6048b087aa5924d1f9c34ac9b113f1c8cd5f0af3470d3f0b54"
    
    uuid = get_motherboard_uuid()
    if not uuid:
        return False
    
    raw = f"{salt}{uuid}{salt}"
    computed = hashlib.sha256(raw.encode()).hexdigest()
    
    return computed == stored_license_key

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_skill_images(kahraman_adi):
    # Kahraman adı ile 'skills' klasöründen doğru yolu buluyoruz
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    kahraman_folder = os.path.join(script_dir, "skills", kahraman_adi)
    
    if not os.path.exists(kahraman_folder):
        return None, f"'{kahraman_folder}' klasörü bulunamadı."
    
    image_files = []
    missing_files = []
    
    for i in range(1, 5):
        image_path = os.path.join(kahraman_folder, f"skil{i}.png")
        if os.path.exists(image_path):
            try:
                test_img = cv2.imread(image_path)
                if test_img is not None:
                    image_files.append(image_path)
                else:
                    missing_files.append(f"skil{i}.png (bozuk dosya)")
            except:
                missing_files.append(f"skil{i}.png (okunamadı)")
        else:
            missing_files.append(f"skil{i}.png")
    
    if len(image_files) == 4:
        return image_files, None
    else:
        error_msg = f"'{kahraman_folder}' klasöründe eksik dosyalar: {', '.join(missing_files)}"
        return None, error_msg

def capture_area(x1, y1, x2, y2):
    try:
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Ekran görüntüsü alınamadı: {e}")
        return None

def match_template(screen_img, template_img, threshold=0.88):
    if screen_img is None or template_img is None:
        return False, 0

    try:
        for scale in np.linspace(0.5, 1.5, 20):
            resized = cv2.resize(template_img, (0, 0), fx=scale, fy=scale)
            if resized.shape[0] > screen_img.shape[0] or resized.shape[1] > screen_img.shape[1]:
                continue
            
            result = cv2.matchTemplate(screen_img, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            match_percentage = max_val  
            
            if match_percentage >= threshold:
                return True, match_percentage  
        return False, 0
    except Exception as e:
        print(f"Template matching hatası: {e}")
        return False, 0


def main():
    print("Lisans kontrolü yapılıyor...")
    if not validate_license():
        print("Lisans geçersiz. Program kapatılıyor.")
        ctypes.windll.user32.MessageBoxW(0, "Lisans geçersiz! Program kapatılıyor.", "Lisans Hatası", 0)
        time.sleep(2)
        os._exit(1)
    
    print("Lisans geçerli. Görsel tarama başlatılıyor...")

    if len(sys.argv) < 2:
        error_msg = "Kahraman adı argüman olarak verilmelidir!\n\nKullanım: python script.py [kahraman_adi]"
        print(error_msg)
        ctypes.windll.user32.MessageBoxW(0, error_msg, "Argüman Hatası", 0)
        os._exit(1)
    
    kahraman_adi = sys.argv[1]
    
    print(f"Skills klasöründe {kahraman_adi} için 4 görsel dosyası kontrol ediliyor...")
    image_files, error_msg = get_skill_images(kahraman_adi)
    
    if image_files is None:
        print(f"Hata: {error_msg}")
        ctypes.windll.user32.MessageBoxW(0, f"Dosya Hatası!\n\n{error_msg}", "Görsel Dosya Hatası", 0)
        os._exit(1)
    
    print(f"4 görsel dosyası başarıyla bulundu:")
    for img_path in image_files:
        print(f"  - {os.path.basename(img_path)}")
    
    search_area = (518, 715, 825, 791)  
    threshold = 0.88
    check_interval = 0.9
    
    print("Görsel arama döngüsü başlatılıyor...")

    try:
        while True:
            screen = capture_area(*search_area)
            if screen is None:
                time.sleep(check_interval)
                continue
            
            match_count = 0
            matched_files = []
            
            for img_path in image_files:
                try:
                    template = cv2.imread(img_path)
                    if template is None:
                        continue
                    
                    match_found, match_percentage = match_template(screen, template, threshold)
                    if match_found:
                        match_count += 1
                        matched_files.append(f"{os.path.basename(img_path)} ({match_percentage*100:.2f}%)")
                        print(f"Eşleşme: {os.path.basename(img_path)} ({match_percentage*100:.2f}%)")
                except Exception as e:
                    print(f"Görsel kontrol hatası {os.path.basename(img_path)}: {e}")
            
            if match_count >= 2:
                print(f"{match_count} eşleşme bulundu: {', '.join(matched_files)}")
                print("ESC tuşu gönderiliyor...")
                pyautogui.press('esc')
                print("2+ görsel eşleşmesi tespit edildi - tıklamalar durdurulacak!")
                break
            elif match_count > 0:
                print(f"{match_count} eşleşme: {', '.join(matched_files)}")
            
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu (Ctrl+C)")
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        ctypes.windll.user32.MessageBoxW(0, f"Beklenmeyen hata oluştu:\n{e}", "Hata", 0)
    
    print("Program sonlandırılıyor...")
    os._exit(0)

if __name__ == "__main__":
    main()
