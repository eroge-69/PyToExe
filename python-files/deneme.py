
import sys
import subprocess
import re
import time
import os
import base64
import requests
import cv2
import numpy as np
import json
import threading
from datetime import datetime
from collections import Counter
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QLineEdit, QScrollArea, QFrame, QSizePolicy, QSpacerItem, QMessageBox, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, QRect, QPoint, QEasingCurve
from PyQt5.QtGui import QFont, QPalette, QColor, QBrush, QImage, QPixmap
OPENROUTER_API_KEY = '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'
MODEL_NAME = 'google/gemini-2.0-flash-001'
OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'
APP_LOGO_IMAGE_NAME = 'app_logo.png'
HI_BUTTON_IMAGE_NAME = 'hibutton.png'
CLICK_X_MESSAGE_BOX = 500
CLICK_Y_MESSAGE_BOX = 1765
CLICK_X_SEND_BUTTON = 1000
CLICK_Y_SEND_BUTTON = 1760
WAIT_TIME_AFTER_CLICK = 1.0
WAIT_TIME_AFTER_TYPE = 0.5
WAIT_TIME_FOR_SCREEN_UPDATE = 2.0
COLOR_CHECK_COORDS = [(1078, 1645), (1078, 1610), (1078, 1490)]
TAP_X_ANASAYFA = 110
TAP_Y_ANASAYFA = 1850
TAP_X_SOHBET = 800
TAP_Y_SOHBET = 1840
TAP_X_BEFORE_TEXT = 200
TAP_Y_BEFORE_TEXT = 1770
TAP_X_AFTER_TEXT = 1018
TAP_Y_AFTER_TEXT = 1770
TAP_X_YENI_1 = 30
TAP_Y_YENI_1 = 90
TAP_X_YENI_2 = 50
TAP_Y_YENI_2 = 90
SETTINGS_FILE = 'settings.json'
device_automation_status = {}

def load_settings():
    """Ayarları settings.json dosyasından yükler."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
                return {'text_to_write_main_loop': 'hayattan cok biktim ama sen bunu degistirebilirsin bence mesaj et sansimizi deneyelim askim'}
        except json.JSONDecodeError:
            print(f"Hata: '{SETTINGS_FILE}' dosyası bozuk. Varsayılan ayarlar yükleniyor.")
            return {'text_to_write_main_loop': 'hayattan cok biktim ama sen bunu degistirebilirsin bence mesaj et sansimizi deneyelim askim'}
    return {'text_to_write_main_loop': 'hayattan cok biktim ama sen bunu degistirebilirsin bence mesaj et sansimizi deneyelim askim'}

def save_settings(settings):
    """Ayarları settings.json dosyasına kaydeder."""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)
current_settings = load_settings()

def sanitize_text_for_adb(text_to_sanitize):
    if not text_to_sanitize:
        return ''
    temp_sanitized_text = text_to_sanitize
    turkish_to_ascii_map = {'ı': 'i', 'İ': 'I', 'ü': 'u', 'Ü': 'U', 'ç': 'c', 'Ç': 'C', 'ğ': 'g', 'Ğ': 'G', 'ş': 's', 'Ş': 'S', 'ö': 'o', 'Ö': 'O'}
    for tr_char, ascii_char in turkish_to_ascii_map.items():
        temp_sanitized_text = temp_sanitized_text.replace(tr_char, ascii_char)
    final_sanitized_text = re.sub('[^a-zA-Z0-9 ]', '', temp_sanitized_text)
    final_sanitized_text = re.sub(' +', ' ', final_sanitized_text).strip()
    return final_sanitized_text

def run_adb_command(command_parts, device_id=None, check=True, timeout=15):
    if device_id:
        cmd = ['adb', '-s', device_id] + command_parts
    else:
        cmd = ['adb'] + command_parts
    try:
        process = subprocess.run(cmd, capture_output=True, text=True, check=check, timeout=timeout, encoding='utf-8')
        return (process.stdout.strip(), process.stderr.strip())
    except subprocess.CalledProcessError as e:
        print(f"❌ HATA: ADB komutu başarısız oldu ('{' '.join(cmd)}').")
        print(f'   Return Code: {e.returncode}')
        print(f"   Stdout: {(e.stdout.strip() if e.stdout else '(yok)')}")
        print(f"   Stderr: {(e.stderr.strip() if e.stderr else '(yok)')}")
        return (None, e.stderr.strip() if e.stderr else str(e))
    except subprocess.TimeoutExpired:
        print(f"❌ HATA: ADB komutu zaman aşımına uğradı ('{' '.join(cmd)}').")
        return (None, 'Zaman aşımı')
    except FileNotFoundError:
        print("❌ HATA: 'adb' komutu bulunamadı. Android SDK Platform Tools kurulu ve PATH'de mi?")
        return (None, 'ADB bulunamadı')
    except Exception as e:
        print(f'💥 ADB komutu çalıştırılırken beklenmedik bir hata oluştu: {e}')
        return (None, str(e))

def list_adb_devices():
    """ADB cihazlarını listeler ve ID'lerini döndürür."""
    try:
        process = subprocess.run(['adb', 'devices', '-l'], capture_output=True, text=True, check=False, timeout=15)
        output = process.stdout.strip()
        error_output = process.stderr.strip()
        devices = []
        if process.returncode != 0 and (not output):
            if 'adb server version' in error_output and "doesn't match this client" in error_output:
                return ([], 'ADB sunucu versiyonu uyumsuz. Yeniden başlatmayı deneyin.')
            return ([], f'ADB komutu çalıştırılırken sorun oluştu: {error_output}')
        output_lines = output.split('\n')
        started_listing_devices = False
        for line in output_lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            if 'List of devices attached' in line_stripped:
                started_listing_devices = True
                continue
            if not started_listing_devices or line_stripped.startswith('*') or 'adb server version' in line_stripped:
                continue
            parts = line_stripped.split(maxsplit=2)
            if len(parts) < 2:
                continue
            device_id_val, device_state = (parts[0], parts[1])
            description_extra = ''
            if len(parts) > 2:
                additional_info = parts[2]
                model_match = re.search('model:(?P<model>\\S+)', additional_info)
                if model_match:
                    description_extra += f" (Model: {model_match.group('model')})"
                product_match = re.search('product:(?P<product>\\S+)', additional_info)
                if product_match:
                    description_extra += f" (Product: {product_match.group('product')})"
            devices.append({'id': device_id_val, 'state': device_state, 'description': f'{device_id_val} [{device_state}]{description_extra}'})
        return (devices, None)
    except subprocess.TimeoutExpired:
        return ([], 'ADB komutu zaman aşımına uğradı.')
    except FileNotFoundError:
        return ([], "'adb' komutu bulunamadı. Android SDK Platform Tools kurulu ve PATH'de mi?")
    except Exception as e:
        return ([], f'Cihaz listelemede beklenmedik hata: {e}')

def tap_on_screen(device_id, x, y, action_description=''):
    description = f' ({action_description})' if action_description else ''
    print(f'📱 Cihaz ({device_id}) üzerinde ({x}, {y}){description} koordinatlarına tıklanıyor...')
    try:
        x_int = max(0, int(x))
        y_int = max(0, int(y))
        stdout, stderr = run_adb_command(['shell', 'input', 'tap', str(x_int), str(y_int)], device_id=device_id)
        if stdout is None and stderr:
            print(f'   Tıklama başarısız oldu. Hata: {stderr}')
            return False
        print(f'✅ ({x_int},{y_int}) koordinatlarına başarıyla dokunuldu.')
        return True
    except ValueError:
        print(f'❌ Hata: ({x},{y}) koordinatları geçerli sayılara dönüştürülemedi.')
        return False
    except Exception as e:
        print(f'❌ Ekrana dokunulurken ({x},{y}) beklenmedik bir genel hata oluştu: {e}')
        return False

def type_text_on_device(device_id, text_to_type):
    print(f"⌨️ Cihaza metin yazılıyor (topluca ve hızlıca): '{text_to_type}'")
    processed_text = text_to_type.replace('"', '\\"')
    adb_command = ['shell', 'input', 'text', f'"{processed_text}"']
    stdout, stderr = run_adb_command(adb_command, device_id=device_id)
    if stdout is None and stderr:
        print(f"   Metin '{text_to_type}' yazılırken sorun oluştu. Stderr: {stderr}")
        if 'error' in stderr.lower() or 'failed' in stderr.lower() or 'aborted' in stderr.lower() or ('exception' in stderr.lower()):
            print('   ❌ Metin yazma kesin olarak başarısız oldu.')
            return False
    print(f"✅ Tüm metin ('{text_to_type}') cihaza başarıyla iletildi.")
    return True

def take_and_save_screenshot(device_id, device_choice_index, base_filename='ekran_goruntusu'):
    if not device_id:
        print('Ekran görüntüsü almak için cihaz seçilmedi.')
        return
    try:
        device_screenshot_path = '/sdcard/screenshot_temp.png'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S%f')
        safe_device_id_part = re.sub('[^a-zA-Z0-9_-]', '_', device_id)
        screenshots_dir = 'screenshots'
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
            print(f"📂 '{screenshots_dir}' klasörü oluşturuldu.")
        local_filename = f'{base_filename}_dev{device_choice_index}_{safe_device_id_part}_{timestamp}.png'
        local_filepath = os.path.join(screenshots_dir, local_filename)
        _, stderr_cap = run_adb_command(['shell', 'screencap', '-p', device_screenshot_path], device_id)
        if stderr_cap and 'error' in stderr_cap.lower():
            print(f'   Ekran görüntüsü alma (screencap) sırasında potansiyel hata: {stderr_cap}')
        _, stderr_pull = run_adb_command(['pull', device_screenshot_path, local_filepath], device_id)
        if stderr_pull and 'error' in stderr_pull.lower():
            print(f'   Ekran görüntüsü çekme (pull) başarısız. Hata: {stderr_pull}')
            return
        run_adb_command(['shell', 'rm', device_screenshot_path], device_id, check=False, timeout=5)
        if os.path.exists(local_filepath) and os.path.getsize(local_filepath) > 0:
            print(f"✅ Ekran görüntüsü '{local_filepath}' olarak kaydedildi.")
            return local_filepath
        if not os.path.exists(local_filepath):
            print(f"❌ HATA: Ekran görüntüsü yerel yola kaydedilemedi ('{local_filepath}' bulunamadı).")
            return
        if os.path.getsize(local_filepath) == 0:
            print(f"❌ HATA: Ekran görüntüsü dosyası '{local_filepath}' boş.")
            try:
                os.remove(local_filepath)
            except OSError:
                return
    except Exception as e:
        print(f'❌ Ekran görüntüsü ({base_filename}) alınırken beklenmedik bir genel hata: {e}')

def _cleanup_screenshot(screenshot_path):
    if screenshot_path:
        if os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
            except OSError as e:
                print(f"⚠️ Hata: '{screenshot_path}' silinirken sorun oluştu: {e}")
pass
pass
pass
pass

def find_image_and_click_offset(device_id, device_choice_index, template_image_path, threshold=0.8, offset_x=0, offset_y=0, click_message_suffix='', search_y_start=None, search_y_end=None, screenshot_base_name='template_search_ss'):
    if not os.path.exists(template_image_path):
        print(f"❌ HATA: Şablon resim '{template_image_path}' bulunamadı.")
        return False
    print(f"\n🖼️ '{device_id}' cihazında '{os.path.basename(template_image_path)}' (eşik: {threshold}) aranıyor...")
    search_desc = []
    if search_y_start is not None:
        search_desc.append(f'Y={search_y_start} sonrası')
    if search_y_end is not None:
        search_desc.append(f'Y={search_y_end} öncesi')
    if search_desc:
        print(f"   Arama alanı sınırlandırıldı: {' ve '.join(search_desc)}.")
    screenshot_path = take_and_save_screenshot(device_id, device_choice_index, base_filename=screenshot_base_name)
    if not screenshot_path:
        print('   Görüntü arama için ekran görüntüsü alınamadı.')
        return False
    try:
        screen_img_bgr_full = cv2.imread(screenshot_path)
        if screen_img_bgr_full is None:
            print(f"❌ HATA: Ekran görüntüsü dosyası '{screenshot_path}' yüklenemedi/bozuk.")
            _cleanup_screenshot(screenshot_path)
            return False
        template_img_bgr = cv2.imread(template_image_path)
        if template_img_bgr is None:
            print(f"❌ HATA: Şablon resim '{template_image_path}' yüklenemedi/bozuk.")
            _cleanup_screenshot(screenshot_path)
            return False
        original_screen_h, original_screen_w = screen_img_bgr_full.shape[:2]
        template_h, template_w = template_img_bgr.shape[:2]
        y_start_slice = 0
        y_end_slice = original_screen_h
        if search_y_start is not None and isinstance(search_y_start, int) and (0 <= search_y_start < original_screen_h):
            y_start_slice = search_y_start
        if search_y_end is not None and isinstance(search_y_end, int) and (0 < search_y_end <= original_screen_h):
            y_end_slice = search_y_end
        if y_start_slice >= y_end_slice:
            print(f'   ⚠️ Uyarı: Arama alanı başlangıcı ({y_start_slice}) bitişinden ({y_end_slice}) büyük veya eşit. Arama atlanıyor.')
            _cleanup_screenshot(screenshot_path)
            return False
        image_to_search_on = screen_img_bgr_full[y_start_slice:y_end_slice, :]
        y_offset_for_coordinates = y_start_slice
        search_area_h, search_area_w = image_to_search_on.shape[:2]
        if search_area_h < template_h or search_area_w < template_w:
            print(f'   ⚠️ Uyarı: Şablon ( {template_w}x{template_h} ) arama alanından ( {search_area_w}x{search_area_h} ) büyük. Eşleşme imkansız.')
            _cleanup_screenshot(screenshot_path)
            return False
        result = cv2.matchTemplate(image_to_search_on, template_img_bgr, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        print(f'   Şablon eşleşme en yüksek güven skoru: {max_val:.4f}')
        if max_val >= threshold:
            actual_top_left_x = max_loc[0]
            actual_top_left_y = max_loc[1] + y_offset_for_coordinates
            center_x = actual_top_left_x + template_w // 2
            center_y = actual_top_left_y + template_h // 2
            target_x = max(0, min(center_x + offset_x, original_screen_w - 1))
            target_y = max(0, min(center_y + offset_y, original_screen_h - 1))
            print(f"   ✅ '{os.path.basename(template_image_path)}' bulundu. Hedeflenen tıklama noktası ({target_x},{target_y}){click_message_suffix}.")
            clicked = tap_on_screen(device_id, target_x, target_y, f"'{os.path.basename(template_image_path)}' şablonu için")
            _cleanup_screenshot(screenshot_path)
            return clicked
        print(f"   ❌ '{os.path.basename(template_image_path)}' ekranda bulunamadı (güven: {max_val:.4f} < eşik: {threshold}).")
        _cleanup_screenshot(screenshot_path)
        return False
    except cv2.error as e:
        print(f'   OpenCV hatası (muhtemelen resim boyutları/formatları uyumsuz): {e}')
        _cleanup_screenshot(screenshot_path)
        return False
    except Exception as e:
        print(f'   Şablon eşleştirme sırasında beklenmedik bir hata oluştu: {e}')
        _cleanup_screenshot(screenshot_path)
        return False

def find_image_on_screen_and_click(device_id, device_choice_index, template_image_path, threshold=0.8, search_y_start=None, search_y_end=None, screenshot_base_name='find_click_ss'):
    return find_image_and_click_offset(device_id, device_choice_index, template_image_path, threshold, offset_x=0, offset_y=0, click_message_suffix=' (merkezine)', search_y_start=search_y_start, search_y_end=search_y_end, screenshot_base_name=screenshot_base_name)

def close_current_app_adb(device_id):
    if not device_id:
        print('Uygulamayı kapatmak için cihaz seçilmedi.')
        return False
    try:
        print(f"\n'{device_id}' cihazında mevcut uygulamaları kapatma/temizleme denemesi...")
        print('   Son uygulamalar ekranı açılıyor (KEYCODE_APP_SWITCH)...')
        run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_APP_SWITCH'], device_id, timeout=5)
        time.sleep(1.5)
        swipe_x, swipe_y_start, swipe_y_end, swipe_duration = (540, 800, 1850, 500)
        print(f'   Aşağı doğru kaydırma yapılıyor ({swipe_x},{swipe_y_start} -> {swipe_x},{swipe_y_end}, {swipe_duration}ms)...')
        run_adb_command(['shell', 'input', 'swipe', str(swipe_x), str(swipe_y_start), str(swipe_x), str(swipe_y_end), str(swipe_duration)], device_id, timeout=5)
        time.sleep(1.0)
        clear_all_x, clear_all_y = (1000, 150)
        print(f"   'Tümünü Temizle' butonuna tıklanıyor (Tahmini Koordinat: {clear_all_x},{clear_all_y})...")
        tap_on_screen(device_id, clear_all_x, clear_all_y, "'Tümünü Temizle' Butonu")
        time.sleep(1.5)
        print('   Ana ekrana dönülüyor (KEYCODE_HOME)...')
        run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_HOME'], device_id, timeout=3)
        print('✅ Uygulamaları kapatma/temizleme komutları başarıyla gönderildi.')
        return True
    except Exception as e:
        print(f'❌ Uygulamayı kapatma/temizleme sırasında bir hata oluştu: {e}')
        print('   Son çare olarak sadece ana ekrana dönülüyor...')
        try:
            run_adb_command(['shell', 'input', 'keyevent', 'KEYCODE_HOME'], device_id, timeout=3)
        except Exception as home_e:
            print(f'    Ana ekrana dönme de başarısız oldu: {home_e}')
        return False

def encode_image_to_base64(image_path):
    try:
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Hata: '{image_path}' resim dosyası bulunamadı.")
        return None
    except Exception as e:
        print(f'Resim kodlanırken hata: {e}')
        return None

def get_relevant_response_from_image_chat(image_path):
    if not OPENROUTER_API_KEY or 'YOUR_API_KEY' in OPENROUTER_API_KEY:
        print('Hata: Lütfen OPENROUTER_API_KEY değişkenine geçerli bir API anahtarı girin.')
        return
    base64_image = encode_image_to_base64(image_path)
    if not base64_image:
        return
    headers = {'Authorization': f'Bearer {OPENROUTER_API_KEY}', 'Content-Type': 'application/json'}
    prompt_text = 'Bir önceki mesaja [veya belirli bir senaryoya/konuya] yanıt olarak, aşağıdaki özelliklere sahip bir mesaj oluştur:\n***SOLDAKI MESAJLAR KARŞI TARAFTAKI ERKEĞİN - SAĞ TARAFTAKI MESAJLAR BENIM KIZIM*** SOLDAKI MESAJLARA YANIT OLARAK CEVAP VERECEĞIM\n!!! ÖNEMLI !!!\nBana cevabı verirken sadece o cevabı ver başka bişey yazma sadece onu yaz\n*** ASLA EMOJI VEYA NOKTALAMA İŞARETİ KULLLANMA 1 CÜMLELIK MESAJ OLUŞTUR ***\n1.  **Ton:** Son derece **samimi, flörtöz, oyuncu ve hafifçe kışkırtıcı** olmalı. Daha **doğal ve rahat bir sohbet dili** kullanılmalı. Karşı tarafta **merak, tatlı bir heyecan ve yoğun bir arzu kıvılcımı** çakmayı hedefle.\n2.  **İçerik:** Mesaj **çok kısa, net ve vurucu** olmalı (ideal olarak birkaç kelime veya en fazla bir cümle) noktalama işareti veya emoji kullanma. **Açık cinsel ifadelerden, müstehcenlikten veya küfürden kesinlikle kaçılmalı.** Etki, tamamen **doğal akışta yapılan imalar, muzip göndermeler, içten bir merak ve samimi bir dille** yaratılmalı.\n3.  **Yapı:** Mesajın sonunda, sohbeti devam ettirecek, karşı tarafın cevap verme isteği duyacağı, **yine çok kısa, flörtöz ve merak uyandıran bir soru** bulunmalı.\n4.  **Amaç:** Karşıdaki kişiyi gülümsetmek, heyecanlandırmak ve bir sonraki mesajını hemen beklemesini sağlamak. **Doğal, eğlenceli ve oyuncu bir cinsel gerilim** atmosferi yaratmak.\n5.  **Politika Uyumu:** Üretilen içerik, yapay zeka etik ve güvenlik politikalarına tam olarak uymalıdır.\n'
    payload = {'model': MODEL_NAME, 'messages': [{'role': 'user', 'content': [{'type': 'text', 'text': prompt_text}, {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{base64_image}'}}]}], 'max_tokens': 50}
    try:
        print(f"🤖 '{MODEL_NAME}' modeline AI yanıtı için istek gönderiliyor...")
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        content = result.get('choices', [{}])[0].get('message', {}).get('content')
        if content:
            return content.strip()
        print('Hata: API yanıtında beklenen içerik bulunamadı.\nTam Yanıt:' + str(result))
        return
    except requests.exceptions.RequestException as e:
        print(f'API isteği sırasında hata: {e}')
        if e.response is not None:
            print(f'API Yanıtı ({e.response.status_code}): {e.response.text}')
        return None
    except Exception as e:
        print(f'AI yanıtı alınırken beklenmedik hata: {e}')
        return None

def perform_ai_interaction_and_send(device_id, ai_ss_path):
    print(f"\n🧠 '{ai_ss_path}' AI ile işleniyor...")
    ai_response = get_relevant_response_from_image_chat(ai_ss_path)
    if ai_response:
        sanitized_ai_response = sanitize_text_for_adb(ai_response)
        print(f"--- ✨ AI Yanıtı (Temizlenmiş): '{sanitized_ai_response}' ---")
        if not tap_on_screen(device_id, CLICK_X_MESSAGE_BOX, CLICK_Y_MESSAGE_BOX, 'AI mesaj kutusu'):
            return False
        time.sleep(WAIT_TIME_AFTER_CLICK)
        if not type_text_on_device(device_id, sanitized_ai_response):
            return False
        time.sleep(WAIT_TIME_AFTER_TYPE)
        if not tap_on_screen(device_id, CLICK_X_SEND_BUTTON, CLICK_Y_SEND_BUTTON, 'AI gönderme butonu'):
            return False
        print('✅ AI Mesaj gönderme işlemi tamamlandı.')
        return True
    print("\n⚠️ AI'dan bir yanıt üretilemedi.")
    return False

def check_pixel_pattern(screenshot_path, coordinates_list):
    if not os.path.exists(screenshot_path):
        print(f"❌ Hata (check_pixel_pattern): Ekran görüntüsü '{screenshot_path}' bulunamadı.")
        return {'match': False, 'reason': 'Ekran görüntüsü yok'}
    if len(coordinates_list) != 3:
        print(f'❌ Hata (check_pixel_pattern): Tam olarak 3 koordinat gerekli, {len(coordinates_list)} adet verildi.')
        return {'match': False, 'reason': 'Geçersiz koordinat sayısı'}
    pixel_colors_details, bgr_values = ([], [])
    try:
        img = cv2.imread(screenshot_path)
        if img is None:
            print(f"❌ Hata: SS '{screenshot_path}' yüklenemedi.")
            return {'match': False, 'reason': 'SS yüklenemedi'}
        img_h, img_w = img.shape[:2]
        for x, y in coordinates_list:
            if not (0 <= x < img_w and 0 <= y < img_h):
                print(f'⚠️ Uyarı: Koordinat ({x},{y}) ekran ({img_w}x{img_h}) dışında.')
                return {'match': False, 'reason': 'Koordinat sınır dışı'}
            pixel_bgr_tuple = tuple((int(c) for c in img[y, x]))
            pixel_colors_details.append(((x, y), pixel_bgr_tuple))
            bgr_values.append(pixel_bgr_tuple)
        else:
            num_unique_colors = len(set(bgr_values))
            match_condition, reason_text = (False, '')
            if num_unique_colors == 2:
                match_condition, reason_text = (True, '2 renk aynı, 1 farklı')
            elif num_unique_colors == 1:
                reason_text = '3 renk de aynı'
            elif num_unique_colors == 3:
                reason_text = '3 renk de farklı'
            else:
                reason_text = 'Geçersiz renk durumu'
            if match_condition:
                print(f'✅ Piksel deseni koşulu sağlandı: {reason_text}.')
            else:
                print(f'⚠️ Piksel deseni koşulu sağlanamadı: {reason_text}.')
            return {'match': match_condition, 'reason': reason_text, 'pixel_colors_details': pixel_colors_details}
    except Exception as e:
        print(f'💥 check_pixel_pattern hatası: {e}')
        return {'match': False, 'reason': 'İstisna'}

def find_unique_color_coordinate(pattern_result):
    if not pattern_result or not pattern_result.get('match') or (not pattern_result.get('pixel_colors_details')):
        return None
    colors = [details[1] for details in pattern_result['pixel_colors_details']]
    color_counts = Counter(colors)
    unique_color = None
    for color, count in color_counts.items():
        if count == 1:
            unique_color = color
            break
    if unique_color is None:
        return
    for coord, color in pattern_result['pixel_colors_details']:
        if color == unique_color:
            print(f"   🎯 Benzersiz renkli ('Sonraki' butonu) koordinat bulundu: {coord}")
            return coord
    else:
        return None

class AutomationSignals(QObject):
    """Otomasyon thread'inden GUI'ye sinyal göndermek için."""
    log_updated = pyqtSignal(str, str)
    status_updated = pyqtSignal(str, bool)
    notification_requested = pyqtSignal(str)

def automation_workflow_for_device(device_id, device_choice_index, stop_event, signals: AutomationSignals):
    """
    Belirli bir cihaz için otomasyon iş akışını çalıştırır.
    stop_event: Dışarıdan durdurma sinyali almak için bir threading.Event nesnesi.
    signals: GUI'ye log ve durum güncellemeleri göndermek için sinyal nesnesi.
    """

    def log_callback(dev_id, message, is_error=False):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f'[{timestamp}] {message}'
        if dev_id not in device_automation_status:
            device_automation_status[dev_id] = {'running': False, 'thread': None, 'stop_event': None, 'log': []}
        device_automation_status[dev_id]['log'].append(log_entry)
        if len(device_automation_status[dev_id]['log']) > 100:
            device_automation_status[dev_id]['log'] = device_automation_status[dev_id]['log'][-100:]
        signals.log_updated.emit(dev_id, log_entry)
    log_callback(device_id, '🤖 Otomasyon Başlatıldı...')
    print(f"🟢 '{device_id}' ID'li cihaz (Seçim No: {device_choice_index}) ana otomasyon için seçildi.")
    text_to_write_main_loop = current_settings.get('text_to_write_main_loop', '')
    sanitized_main_loop_text = sanitize_text_for_adb(text_to_write_main_loop)
    main_loop_count = 0
    first_app_open = True
    try:
        while not stop_event.is_set():
            main_loop_count += 1
            log_callback(device_id, f'\n======= ANA DÖNGÜ #{main_loop_count} BAŞLIYOR =======')
            if first_app_open:
                log_callback(device_id, '   İlk açılış: Uygulama logosu aranıyor...')
                if not find_image_on_screen_and_click(device_id, device_choice_index, APP_LOGO_IMAGE_NAME, threshold=0.5, screenshot_base_name=f'main_logo_d{main_loop_count}'):
                    log_callback(device_id, f"   Uygulama logosu '{APP_LOGO_IMAGE_NAME}' bulunamadı. devam ediliyor")
                time.sleep(8)
                log_callback(device_id, '   Ana sayfaya çift tıklanıyor...')
                tap_on_screen(device_id, TAP_X_ANASAYFA, TAP_Y_ANASAYFA, 'Ana Sayfa')
                tap_on_screen(device_id, TAP_X_ANASAYFA, TAP_Y_ANASAYFA, 'Ana Sayfa')
                time.sleep(1)
                first_app_open = False
            log_callback(device_id, f"   Aşama 1: '{HI_BUTTON_IMAGE_NAME}' aranıyor (soluna tıklanacak)...")
            if not find_image_and_click_offset(device_id, device_choice_index, HI_BUTTON_IMAGE_NAME, threshold=0.45, offset_x=-300, offset_y=0, click_message_suffix=' (-300px soluna)', search_y_end=1750, screenshot_base_name=f'main_hibutton_d{main_loop_count}'):
                log_callback(device_id, f"   '{HI_BUTTON_IMAGE_NAME}' bulunamadı. Uygulama kapatılıp döngü yeniden denenecek.")
                close_current_app_adb(device_id)
                first_app_open = True
                time.sleep(3)
                continue
            if stop_event.is_set():
                break
            log_callback(device_id, "   'Hi Button' adımı başarılı. 2sn bekleniyor...")
            time.sleep(2)
            log_callback(device_id, '   Aşama 2: Sohbet butonuna tıklanıyor...')
            if not tap_on_screen(device_id, TAP_X_SOHBET, TAP_Y_SOHBET, 'Sohbet'):
                log_callback(device_id, '   Sohbet butonu tıklanamadı. Başa dönülüyor...')
                continue
            if stop_event.is_set():
                break
            time.sleep(1)
            log_callback(device_id, '   Aşama 3: Metin yazma alanı ve metin yazma...')
            if not tap_on_screen(device_id, TAP_X_BEFORE_TEXT, TAP_Y_BEFORE_TEXT, 'Metin Yazma Alanı'):
                log_callback(device_id, '   Metin yazma alanı tıklanamadı. Başa dönülüyor...')
                continue
            if stop_event.is_set():
                break
            time.sleep(1)
            if not type_text_on_device(device_id, sanitized_main_loop_text):
                log_callback(device_id, f"   Metin ('{sanitized_main_loop_text}') yazılamadı. Başa dönülüyor.")
                continue
            if stop_event.is_set():
                break
            log_callback(device_id, '   Aşama 4: Gönder butonuna tıklanıyor...')
            time.sleep(0.5)
            if not tap_on_screen(device_id, TAP_X_AFTER_TEXT, TAP_Y_AFTER_TEXT, 'Gönder Butonu'):
                log_callback(device_id, '   Gönder butonu tıklanamadı. Başa dönülüyor.')
                continue
            if stop_event.is_set():
                break
            log_callback(device_id, '   Mesaj gönderildi. 2sn bekleniyor...')
            time.sleep(2)
            if stop_event.is_set():
                break
            log_callback(device_id, "\n   Aşama 5: 'Sonraki' butonu için renk deseni kontrol ediliyor...")
            color_ss_path = take_and_save_screenshot(device_id, device_choice_index, base_filename='color_check_ss')
            if not color_ss_path:
                log_callback(device_id, '   Renk kontrolü için SS alınamadı. Döngü atlanıyor.')
                continue
            if stop_event.is_set():
                break
            pattern_result = check_pixel_pattern(color_ss_path, COLOR_CHECK_COORDS)
            _cleanup_screenshot(color_ss_path)
            if pattern_result.get('match'):
                log_callback(device_id, "   ✅ 'Sonraki' butonu TESPİT EDİLDİ. Yapay zeka sohbet döngüsü başlıyor...")
                ai_loop_active = True
                ai_next_button_clicks = 0
                if ai_loop_active and ai_next_button_clicks < 10:
                    while not stop_event.is_set():
                        log_callback(device_id, f'   --- AI Döngüsü Adım: {ai_next_button_clicks + 1}/10 ---')
                        next_button_coords = find_unique_color_coordinate(pattern_result)
                        if not next_button_coords:
                            log_callback(device_id, "   'Sonraki' butonu deseni bulundu ama tıklanacak benzersiz koordinat tespit edilemedi. AI döngüsü sonlandırılıyor.")
                            break
                        tap_on_screen(device_id, next_button_coords[0], next_button_coords[1], "Dinamik 'Sonraki' Butonu")
                        ai_next_button_clicks += 1
                        time.sleep(WAIT_TIME_FOR_SCREEN_UPDATE)
                        if stop_event.is_set():
                            break
                        ai_ss_path = take_and_save_screenshot(device_id, device_choice_index, 'ai_chat_ss')
                        if not ai_ss_path:
                            log_callback(device_id, '   AI etkileşimi için SS alınamadı. AI döngüsü sonlandırılıyor.')
                            break
                        if stop_event.is_set():
                            break
                        if not perform_ai_interaction_and_send(device_id, ai_ss_path):
                            log_callback(device_id, '   AI mesaj gönderme işlemi başarısız. AI döngüsü sonlandırılıyor.')
                            _cleanup_screenshot(ai_ss_path)
                            break
                        _cleanup_screenshot(ai_ss_path)
                        time.sleep(WAIT_TIME_FOR_SCREEN_UPDATE)
                        if stop_event.is_set():
                            break
                        if ai_next_button_clicks >= 10:
                            log_callback(device_id, "   🏁 Maksimum 'Sonraki' butonu tıklama limitine (10) ulaşıldı.")
                            break
                        log_callback(device_id, "   Sohbet devam ediyor, yeni 'Sonraki' butonu tekrar kontrol ediliyor...")
                        next_color_ss_path = take_and_save_screenshot(device_id, device_choice_index, 'next_color_check_ss')
                        if not next_color_ss_path:
                            log_callback(device_id, '   Sonraki renk kontrolü için SS alınamadı. AI döngüsü sonlandırılıyor.')
                            break
                        if stop_event.is_set():
                            break
                        pattern_result = check_pixel_pattern(next_color_ss_path, COLOR_CHECK_COORDS)
                        _cleanup_screenshot(next_color_ss_path)
                        if not pattern_result.get('match'):
                            log_callback(device_id, "   ✅ AI sohbeti tamamlandı, artık 'Sonraki' butonu yok.")
                            ai_loop_active = False
                if ai_next_button_clicks >= 10:
                    log_callback(device_id, "   AI döngüsü 10 'Sonraki' butonu tıklama sınırına ulaşıldığı için sonlandırıldı.")
                log_callback(device_id, '   AI döngüsü bitti. Ana sayfaya dönülüyor.')
                log_callback(device_id, f'   Adım 5a: ({TAP_X_YENI_1},{TAP_Y_YENI_1}) tıklanıyor (Yeni Tık 1)...')
                tap_on_screen(device_id, TAP_X_YENI_1, TAP_Y_YENI_1, 'Yeni Tık 1')
                time.sleep(0.5)
                if stop_event.is_set():
                    break
                log_callback(device_id, f'   Adım 5b: ({TAP_X_YENI_2},{TAP_Y_YENI_2}) tıklanıyor (Yeni Tık 2)...')
                tap_on_screen(device_id, TAP_X_YENI_2, TAP_Y_YENI_2, 'Yeni Tık 2')
                time.sleep(0.5)
                if stop_event.is_set():
                    break
                log_callback(device_id, '   Adım 5c: Ana sayfaya 3 kez tıklanıyor...')
                tap_on_screen(device_id, TAP_X_ANASAYFA, TAP_Y_ANASAYFA, 'Ana Sayfa (1/3)')
                time.sleep(0.3)
                tap_on_screen(device_id, TAP_X_ANASAYFA, TAP_Y_ANASAYFA, 'Ana Sayfa (2/3)')
                time.sleep(0.3)
                tap_on_screen(device_id, TAP_X_ANASAYFA, TAP_Y_ANASAYFA, 'Ana Sayfa (3/3)')
                time.sleep(1)
                if stop_event.is_set():
                    break
            else:
                log_callback(device_id, "   ❌ 'Sonraki' butonu TESPİT EDİLEMEDİ. Standart sıfırlama adımları uygulanıyor.")
                log_callback(device_id, f'   Adım 5a: ({TAP_X_YENI_1},{TAP_Y_YENI_1}) tıklanıyor (Yeni Tık 1)...')
                tap_on_screen(device_id, TAP_X_YENI_1, TAP_Y_YENI_1, 'Yeni Tık 1')
                time.sleep(0.5)
                if stop_event.is_set():
                    break
                log_callback(device_id, f'   Adım 5b: ({TAP_X_YENI_2},{TAP_Y_YENI_2}) tıklanıyor (Yeni Tık 2)...')
                tap_on_screen(device_id, TAP_X_YENI_2, TAP_Y_YENI_2, 'Yeni Tık 2')
                time.sleep(0.5)
                if stop_event.is_set():
                    break
                log_callback(device_id, '   Adım 5c: Ana sayfaya 3 kez tıklanıyor...')
                tap_on_screen(device_id, TAP_X_ANASAYFA, TAP_Y_ANASAYFA, 'Ana Sayfa (1/3)')
                time.sleep(0.3)
                tap_on_screen(device_id, TAP_X_ANASAYFA, TAP_Y_ANASAYFA, 'Ana Sayfa (2/3)')
                time.sleep(0.3)
                tap_on_screen(device_id, TAP_X_ANASAYFA, TAP_Y_ANASAYFA, 'Ana Sayfa (3/3)')
                time.sleep(1)
                if stop_event.is_set():
                    break
            log_callback(device_id, f'--- Ana Döngü #{main_loop_count} Tamamlandı. ---')
            time.sleep(1)
            if stop_event.is_set():
                break
    except Exception as e:
        import traceback
        log_callback(device_id, f'💥 Ana işlem sırasında beklenmedik bir genel hata oluştu: {e}\n{traceback.format_exc()}', is_error=True)
    finally:
        log_callback(device_id, '👋 Otomasyon tamamlandı veya durduruldu.')
        if device_id in device_automation_status:
            device_automation_status[device_id]['running'] = False
            device_automation_status[device_id]['thread'] = None
            device_automation_status[device_id]['stop_event'] = None
            signals.status_updated.emit(device_id, False)

class Notification(QWidget):

    def __init__(self, message, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.BypassWindowManagerHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowOpacity(0.9)
        self.setFixedSize(300, 70)
        layout = QVBoxLayout(self)
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet('color: white; font-size: 14px; padding: 5px;')
        layout.addWidget(self.label)
        self.setStyleSheet('\n            QWidget {\n                background-color: #333;\n                border: 1px solid #555;\n                border-radius: 10px;\n            }\n        ')
        self.animation = QPropertyAnimation(self, b'geometry')
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b'opacity')
        self.opacity_animation.setDuration(500)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_notification)

    def show_notification(self, start_pos, end_pos):
        self.setGeometry(QRect(start_pos, self.size()))
        self.animation.setStartValue(QRect(start_pos, self.size()))
        self.animation.setEndValue(QRect(end_pos, self.size()))
        self.animation.start()
        self.opacity_effect.setOpacity(0.0)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(0.9)
        self.opacity_animation.start()
        self.show()
        self.timer.start(3000)

    def hide_notification(self):
        self.opacity_animation.stop()
        self.opacity_animation.setStartValue(self.opacity_effect.opacity())
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.finished.connect(self.close)
        self.opacity_animation.start()

class MainApp(QWidget):

    def __init__(self):
        super().__init__()
        self.automation_signals = AutomationSignals()
        self.automation_signals.log_updated.connect(self.update_device_log)
        self.automation_signals.status_updated.connect(self.update_device_status_ui)
        self.automation_signals.notification_requested.connect(self.show_notification)
        self.init_ui()
        self.load_initial_settings()
        self.check_required_files()
        self.refresh_devices()
        self.device_refresh_timer = QTimer(self)
        self.device_refresh_timer.setInterval(5000)
        self.device_refresh_timer.timeout.connect(self.refresh_devices)
        self.device_refresh_timer.start()

    def init_ui(self):
        self.setWindowTitle('OZDADEV ADB Otomasyonu')
        self.setGeometry(100, 100, 1200, 800)
        palette = self.palette()
        brush = QBrush(QColor(30, 30, 30))
        palette.setBrush(QPalette.Background, brush)
        self.setPalette(palette)
        self.background_label = QLabel(self)
        self.background_label.setFont(QFont('Arial', 72, QFont.Bold))
        self.background_label.setStyleSheet('color: rgba(255, 255, 255, 15);')
        self.background_label.setText('OZDADEV\nOZDADEV\nOZDADEV\nOZDADEV\nOZDADEV')
        self.background_label.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout = QHBoxLayout(self)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        left_panel.setContentsMargins(20, 20, 20, 20)
        title_label = QLabel('ADB Otomasyon Kontrol Paneli')
        title_label.setFont(QFont('Arial', 24, QFont.Bold))
        title_label.setStyleSheet('color: #4CAF50;')
        title_label.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(title_label)
        left_panel.addSpacing(20)
        settings_group_box = QFrame()
        settings_group_box.setFrameShape(QFrame.StyledPanel)
        settings_group_box.setStyleSheet('QFrame { background-color: #333; border-radius: 10px; padding: 15px; }')
        settings_layout = QVBoxLayout(settings_group_box)
        settings_label = QLabel('Ana Döngü Mesajı:')
        settings_label.setFont(QFont('Arial', 12, QFont.Bold))
        settings_label.setStyleSheet('color: #E0E0E0;')
        settings_layout.addWidget(settings_label)
        self.main_loop_text_input = QLineEdit()
        self.main_loop_text_input.setPlaceholderText('Buraya ana döngüde yazılacak metni girin...')
        self.main_loop_text_input.setStyleSheet('\n            QLineEdit {\n                background-color: #444;\n                color: #FFF;\n                border: 1px solid #555;\n                border-radius: 5px;\n                padding: 8px;\n                font-size: 14px;\n            }\n            QLineEdit:focus {\n                border: 1px solid #4CAF50;\n            }\n        ')
        settings_layout.addWidget(self.main_loop_text_input)
        save_settings_button = QPushButton('Ayarları Kaydet')
        save_settings_button.setFont(QFont('Arial', 12, QFont.Bold))
        save_settings_button.setStyleSheet('\n            QPushButton {\n                background-color: #007BFF;\n                color: white;\n                border-radius: 8px;\n                padding: 10px 15px;\n                margin-top: 10px;\n            }\n            QPushButton:hover {\n                background-color: #0056b3;\n            }\n            QPushButton:pressed {\n                background-color: #004085;\n            }\n        ')
        save_settings_button.clicked.connect(self.save_current_settings)
        settings_layout.addWidget(save_settings_button)
        left_panel.addWidget(settings_group_box)
        left_panel.addSpacing(20)
        global_controls_group_box = QFrame()
        global_controls_group_box.setFrameShape(QFrame.StyledPanel)
        global_controls_group_box.setStyleSheet('QFrame { background-color: #333; border-radius: 10px; padding: 15px; }')
        global_controls_layout = QVBoxLayout(global_controls_group_box)
        global_label = QLabel('Tüm Cihazlar İçin Kontroller:')
        global_label.setFont(QFont('Arial', 12, QFont.Bold))
        global_label.setStyleSheet('color: #E0E0E0;')
        global_controls_layout.addWidget(global_label)
        all_devices_layout = QHBoxLayout()
        self.start_all_button = QPushButton('Tümünü Başlat')
        self.start_all_button.setFont(QFont('Arial', 12, QFont.Bold))
        self.start_all_button.setStyleSheet('\n            QPushButton {\n                background-color: #28A745;\n                color: white;\n                border-radius: 8px;\n                padding: 10px 15px;\n            }\n            QPushButton:hover {\n                background-color: #218838;\n            }\n            QPushButton:pressed {\n                background-color: #1E7E34;\n            }\n        ')
        self.start_all_button.clicked.connect(self.start_all_automations)
        all_devices_layout.addWidget(self.start_all_button)
        self.stop_all_button = QPushButton('Tümünü Durdur')
        self.stop_all_button.setFont(QFont('Arial', 12, QFont.Bold))
        self.stop_all_button.setStyleSheet('\n            QPushButton {\n                background-color: #DC3545;\n                color: white;\n                border-radius: 8px;\n                padding: 10px 15px;\n            }\n            QPushButton:hover {\n                background-color: #C82333;\n            }\n            QPushButton:pressed {\n                background-color: #BD2130;\n            }\n        ')
        self.stop_all_button.clicked.connect(self.stop_all_automations)
        all_devices_layout.addWidget(self.stop_all_button)
        global_controls_layout.addLayout(all_devices_layout)
        left_panel.addWidget(global_controls_group_box)
        left_panel.addStretch(1)
        main_layout.addLayout(left_panel, 1)
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        right_panel.setContentsMargins(20, 20, 20, 20)
        devices_label = QLabel('Bağlı Cihazlar:')
        devices_label.setFont(QFont('Arial', 18, QFont.Bold))
        devices_label.setStyleSheet('color: #4CAF50;')
        right_panel.addWidget(devices_label)
        self.device_list_layout = QVBoxLayout()
        self.device_list_scroll = QScrollArea()
        self.device_list_scroll.setWidgetResizable(True)
        self.device_list_scroll.setStyleSheet('\n            QScrollArea {\n                border: 1px solid #555;\n                border-radius: 10px;\n                background-color: #222;\n            }\n            QScrollArea > QWidget > QWidget {\n                background-color: #222;\n            }\n        ')
        self.device_list_container = QWidget()
        self.device_list_container.setLayout(self.device_list_layout)
        self.device_list_scroll.setWidget(self.device_list_container)
        right_panel.addWidget(self.device_list_scroll, 3)
        log_label = QLabel('Cihaz Logları:')
        log_label.setFont(QFont('Arial', 18, QFont.Bold))
        log_label.setStyleSheet('color: #4CAF50;')
        right_panel.addWidget(log_label)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("\n            QTextEdit {\n                background-color: #1A1A1A;\n                color: #00FF00; /* Yeşil log metni */\n                border: 1px solid #555;\n                border-radius: 10px;\n                padding: 10px;\n                font-family: 'Consolas', 'Monospace';\n                font-size: 12px;\n            }\n        ")
        right_panel.addWidget(self.log_display, 2)
        main_layout.addLayout(right_panel, 2)
        self.setLayout(main_layout)
        self.notifications = []
        self.notification_spacing = 10
        self.notification_width = 300
        self.notification_height = 70

    def resizeEvent(self, event):
        font_metrics = self.background_label.fontMetrics()
        text_height = font_metrics.boundingRect(self.background_label.text()).height()
        self.background_label.setGeometry(0, self.height() - text_height, self.width(), text_height)
        super().resizeEvent(event)

    def load_initial_settings(self):
        self.main_loop_text_input.setText(current_settings.get('text_to_write_main_loop', ''))

    def save_current_settings(self):
        new_text = self.main_loop_text_input.text()
        current_settings['text_to_write_main_loop'] = new_text
        save_settings(current_settings)
        self.show_notification('Ayarlar başarıyla kaydedildi!')

    def check_required_files(self):
        missing_files = [f for f in [APP_LOGO_IMAGE_NAME, HI_BUTTON_IMAGE_NAME] if not os.path.exists(f)]
        if missing_files:
            QMessageBox.critical(self, 'Hata: Eksik Dosyalar', f"Gerekli şablon dosyaları bulunamadı:\n{', '.join(missing_files)}\nLütfen bu dosyaların uygulamanın çalıştığı dizinde olduğundan emin olun.")
            sys.exit(1)

    def show_notification(self, message):
        notification = Notification(message, self)
        x = self.width() - self.notification_width - self.notification_spacing
        y = self.notification_spacing
        for existing_notification in self.notifications:
            if existing_notification.isVisible():
                y += existing_notification.height() + self.notification_spacing
        start_pos = QPoint(x, y - notification.height())
        end_pos = QPoint(x, y)
        notification.show_notification(start_pos, end_pos)
        self.notifications.append(notification)
        notification.opacity_animation.finished.connect(lambda n=notification: self.notifications.remove(n) if n in self.notifications else None)

    def refresh_devices(self):
        while self.device_list_layout.count():
            child = self.device_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        devices, error = list_adb_devices()
        if error:
            self.log_display.append(f"<span style='color: red;'>[HATA] Cihaz listeleme: {error}</span>")
            return
        if not devices:
            no_device_label = QLabel('Bağlı cihaz bulunamadı. Lütfen bir emülatör başlatın veya cihaz bağlayın.')
            no_device_label.setStyleSheet('color: #FFC107; font-size: 14px; padding: 10px;')
            no_device_label.setAlignment(Qt.AlignCenter)
            self.device_list_layout.addWidget(no_device_label)
            return
        for i, dev in enumerate(devices):
            device_id = dev['id']
            device_frame = QFrame()
            device_frame.setFrameShape(QFrame.StyledPanel)
            device_frame.setStyleSheet('\n                QFrame {\n                    background-color: #2A2A2A;\n                    border: 1px solid #444;\n                    border-radius: 8px;\n                    padding: 10px;\n                    margin-bottom: 5px;\n                }\n            ')
            device_layout = QHBoxLayout(device_frame)
            status = device_automation_status.get(device_id, {})
            is_running = status.get('running', False)
            status_indicator = QLabel('●')
            status_indicator.setFont(QFont('Arial', 16, QFont.Bold))
            status_indicator.setFixedSize(20, 20)
            status_indicator.setStyleSheet(f"color: {('#28A745' if is_running else '#DC3545')};")
            device_layout.addWidget(status_indicator)
            device_info_label = QLabel(f"ID: {dev['id']}\nDurum: {dev['state']}\n{dev['description']}")
            device_info_label.setStyleSheet('color: #E0E0E0; font-size: 12px;')
            device_layout.addWidget(device_info_label)
            device_layout.addStretch(1)
            start_button = QPushButton('Başlat')
            start_button.setFont(QFont('Arial', 10, QFont.Bold))
            start_button.setStyleSheet('\n                QPushButton {\n                    background-color: #28A745;\n                    color: white;\n                    border-radius: 5px;\n                    padding: 5px 10px;\n                }\n                QPushButton:hover {\n                    background-color: #218838;\n                }\n                QPushButton:disabled {\n                    background-color: #6C757D;\n                }\n            ')
            start_button.clicked.connect(lambda _, d_id=device_id, d_idx=i: self.start_automation_for_device(d_id, d_idx))
            start_button.setEnabled(not is_running)
            device_layout.addWidget(start_button)
            stop_button = QPushButton('Durdur')
            stop_button.setFont(QFont('Arial', 10, QFont.Bold))
            stop_button.setStyleSheet('\n                QPushButton {\n                    background-color: #DC3545;\n                    color: white;\n                    border-radius: 5px;\n                    padding: 5px 10px;\n                }\n                QPushButton:hover {\n                    background-color: #C82333;\n                }\n                QPushButton:disabled {\n                    background-color: #6C757D;\n                }\n            ')
            stop_button.clicked.connect(lambda _, d_id=device_id: self.stop_automation_for_device(d_id))
            stop_button.setEnabled(is_running)
            device_layout.addWidget(stop_button)
            self.device_list_layout.addWidget(device_frame)
        self.device_list_layout.addStretch(1)

    def start_automation_for_device(self, device_id, device_choice_index):
        if device_automation_status.get(device_id, {}).get('running'):
            self.show_notification(f"Otomasyon zaten '{device_id}' üzerinde çalışıyor.")
            return
        if device_id not in device_automation_status:
            device_automation_status[device_id] = {'running': False, 'thread': None, 'stop_event': None, 'log': []}
        stop_event = threading.Event()
        device_automation_status[device_id]['stop_event'] = stop_event
        thread = threading.Thread(target=automation_workflow_for_device, args=(device_id, device_choice_index, stop_event, self.automation_signals))
        thread.daemon = True
        thread.start()
        device_automation_status[device_id]['running'] = True
        device_automation_status[device_id]['thread'] = thread
        self.update_device_log(device_id, f"[{datetime.now().strftime('%H:%M:%S')}] Otomasyon başlatma isteği alındı.")
        self.update_device_status_ui(device_id, True)
        self.automation_signals.notification_requested.emit(f"Otomasyon '{device_id}' üzerinde başlatıldı.")

    def stop_automation_for_device(self, device_id):
        status = device_automation_status.get(device_id)
        if status and status.get('running') and status.get('stop_event'):
            status['stop_event'].set()
            status['running'] = False
            self.update_device_log(device_id, f"[{datetime.now().strftime('%H:%M:%S')}] Otomasyon durdurma sinyali gönderildi.")
            self.update_device_status_ui(device_id, False)
            self.automation_signals.notification_requested.emit(f"Otomasyon '{device_id}' için durdurma sinyali gönderildi.")
        else:
            self.automation_signals.notification_requested.emit(f"Otomasyon '{device_id}' üzerinde çalışmıyor veya bulunamadı.")

    def start_all_automations(self):
        devices, _ = list_adb_devices()
        if not devices:
            self.automation_signals.notification_requested.emit('Başlatılacak bağlı cihaz bulunamadı.')
            return
        for i, dev in enumerate(devices):
            device_id = dev['id']
            if not device_automation_status.get(device_id, {}).get('running'):
                self.start_automation_for_device(device_id, i)
            else:
                self.update_device_log(device_id, f"[{datetime.now().strftime('%H:%M:%S')}] Otomasyon zaten çalışıyor, atlandı.")

    def stop_all_automations(self):
        devices, _ = list_adb_devices()
        if not devices:
            self.automation_signals.notification_requested.emit('Durdurulacak bağlı cihaz bulunamadı.')
            return
        for dev in devices:
            device_id = dev['id']
            self.stop_automation_for_device(device_id)

    def update_device_log(self, device_id, log_message):
        self.log_display.append(f"<span style='color: #ADD8E6;'>[{device_id}]</span> {log_message}")
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())

    def update_device_status_ui(self, device_id, is_running):
        for i in range(self.device_list_layout.count()):
            widget = self.device_list_layout.itemAt(i).widget()
            if isinstance(widget, QFrame):
                info_label = widget.findChild(QLabel)
                if info_label and device_id in info_label.text():
                    status_indicator = widget.findChild(QLabel)
                    if status_indicator:
                        status_indicator.setStyleSheet(f"color: {('#28A745' if is_running else '#DC3545')};")
                    start_button = widget.findChildren(QPushButton)[0]
                    stop_button = widget.findChildren(QPushButton)[1]
                    start_button.setEnabled(not is_running)
                    stop_button.setEnabled(is_running)
                    break
if __name__ == '__main__':
    try:
        son_kullanma_tarihi = datetime(2030, 7, 9, 23, 0, 0)
        son_kullanma_timestamp = son_kullanma_tarihi.timestamp()
        mevcut_timestamp = time.time()
        if mevcut_timestamp > son_kullanma_timestamp:
            print('\n────────────────────────────────────────────────────────────')
            print('❌ HATA: Bu betiğin kullanım süresi dolmuştur.')
            print(f"   (Son Kullanma Tarihi: {son_kullanma_tarihi.strftime('%d %B %Y, %H:%M:%S')})")
            print('────────────────────────────────────────────────────────────')
            while True:
                pass
    except Exception as e:
        print(f'💥 Zaman kontrolü sırasında kritik bir hata oluştu: {e}')
        sys.exit(1)
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())