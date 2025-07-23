import requests
from bs4 import BeautifulSoup
import urllib3
import os
import re
import json
import time
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Configuration File Path ---
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

# --- Global Session for persistence ---
global_session = requests.Session()
global_session.verify = False

# --- Function to load configuration ---
def load_config():
    """Loads configuration from config.json."""
    if not os.path.exists(CONFIG_FILE):
        print(f"[HATA] Konfigürasyon dosyası bulunamadı: {CONFIG_FILE}")
        print("[HATA] Lütfen örnek bir config.json dosyası oluşturun.")
        # Create a dummy config for demonstration if not exists
        sample_config = {
            "EMAIL": "your_email@example.com",
            "PASSWORD": "your_password",
            "TO_PHONE_NUMBER": "5551234567",
            "SEND_CALL_NOTIFICATION": False,
            "REKLAM_DATA_SOURCE": "../testdata.txt",
            "LOGIN_INTERVAL_SECONDS": 2700, # 45 minutes
            "CHECK_INTERVAL_SECONDS": 1, # WARNING: Too frequent, consider increasing
            "NETGSM_USERNAME": "your_netgsm_username",
            "NETGSM_PASSWORD": "your_netgsm_password",
            "NETGSM_MSGHEADER": "HSYNKURKCU",
            "NETGSM_CALLER_ID": "05303878053",
            "COOKIE_FILE": "cookies.txt",
            "FINAL_COOKIE_FILE": "cookies_final.txt",
            "LOGIN_STATUS_FILE": "login_status.txt",
            "ALLOWED_KEYWORDS": {
                "Site Sol/Sağ": 1,
                "site üst": 3
                # Add other keywords and their corresponding IDs as needed
            }
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=4, ensure_ascii=False)
        print(f"[UYARI] Örnek '{CONFIG_FILE}' dosyası oluşturuldu. Lütfen değerleri güncelleyin.")
        exit() # Exit to force user to update config
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    print(f"[UYARI] Konfigürasyon '{CONFIG_FILE}' dosyasından yüklendi.")
    return config_data

# Load configuration at startup
CONFIG = load_config()

# --- Use configuration values ---
COOKIE_FILE_PATH = os.path.join(os.path.dirname(__file__), CONFIG['COOKIE_FILE'])
FINAL_COOKIE_FILE_PATH = os.path.join(os.path.dirname(__file__), CONFIG['FINAL_COOKIE_FILE'])
LOGIN_STATUS_FILE = os.path.join(os.path.dirname(__file__), CONFIG['LOGIN_STATUS_FILE'])
EMAIL = CONFIG['EMAIL']
PASSWORD = CONFIG['PASSWORD']
TO_PHONE_NUMBER = CONFIG['TO_PHONE_NUMBER']
SEND_CALL_NOTIFICATION = CONFIG['SEND_CALL_NOTIFICATION']
REKLAM_DATA_SOURCE = os.path.join(os.path.dirname(__file__), CONFIG['REKLAM_DATA_SOURCE']) # Adjusted path for consistency

LOGIN_INTERVAL_SECONDS = CONFIG['LOGIN_INTERVAL_SECONDS']
CHECK_INTERVAL_SECONDS = CONFIG['CHECK_INTERVAL_SECONDS']

NETGSM_USERNAME = CONFIG['NETGSM_USERNAME']
NETGSM_PASSWORD = CONFIG['NETGSM_PASSWORD']
NETGSM_MSGHEADER = CONFIG['NETGSM_MSGHEADER']
NETGSM_CALLER_ID = CONFIG['NETGSM_CALLER_ID']

allowed_keywords = CONFIG['ALLOWED_KEYWORDS']


# --- Helper Functions (from index.py and satin.py) ---
def save_cookies(session, filename):
    """Saves session cookies to a file."""
    print(f"[UYARI] Cookie'ler '{filename}' dosyasına kaydediliyor...")
    with open(filename, 'w', encoding='utf-8') as f:
        for c in session.cookies:
            f.write(f'{c.name}\t{c.value}\n')
    print(f"[UYARI] Cookie'ler kaydedildi.")

def load_cookies_to_session(session, cookie_file_path):
    """Loads cookies from a file into the session."""
    print(f"[UYARI] Cookie'ler '{cookie_file_path}' dosyasından yükleniyor...")
    if not os.path.exists(cookie_file_path):
        print("[DEBUG] Cookie dosyası bulunamadı, yeni oturum başlatılacak.")
        return False
    try:
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or (line.startswith('#') and not line.startswith('#HttpOnly_')):
                    continue
                # Handle multiple cookie formats
                if '=' in line and ';' in line: # Semicolon-separated cookie string
                    for part in line.split(';'):
                        part = part.strip()
                        if '=' in part:
                            name, value = part.split('=', 1)
                            session.cookies.set(name, value)
                    continue
                parts = line.split('\t') # Tab-separated key-value pairs
                if len(parts) >= 2: # At least name and value
                    name = parts[0]
                    value = parts[1]
                    session.cookies.set(name, value)
                elif len(parts) >= 7: # Full Netscape format (can handle HttpOnly prefix)
                    name = parts[5]
                    if name.startswith('#HttpOnly_'):
                        name = name[len('#HttpOnly_'):]
                    value = parts[6]
                    session.cookies.set(name, value)
        print(f"[UYARI] Cookie'ler '{cookie_file_path}' dosyasından yüklendi.")
        return True
    except Exception as e:
        print(f"[HATA] Cookie yüklenirken hata oluştu: {e}. Yeniden giriş yapılması gerekebilir.")
        return False

def get_csrf_token_from_html(html):
    """Extracts CSRF token from HTML content."""
    soup = BeautifulSoup(html, 'html.parser')
    meta = soup.find('meta', attrs={'name': 'csrf-token'})
    if meta:
        return meta['content']
    m = re.search(r'<meta\s+name="csrf-token"\s+content="([^"]+)"', html)
    if m:
        return m.group(1)
    return None

def get_csrf_token(session, url):
    """Fetches CSRF token from a given URL using the session."""
    print(f"[UYARI] CSRF token çekiliyor: {url}")
    try:
        resp = session.get(url, verify=False)
        soup = BeautifulSoup(resp.text, 'html.parser')
        meta = soup.find('meta', attrs={'name': 'csrf-token'})
        if meta:
            print("[UYARI] CSRF token bulundu.")
            return meta['content']
        print("[UYARI] CSRF token bulunamadı!")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[HATA] CSRF token çekilirken hata oluştu: {e}")
        return None

# --- NetGSM Functions ---
def netgsm_send_sms(to, msg):
    """Sends an SMS using NetGSM API."""
    url = 'https://api.netgsm.com.tr/sms/rest/v2/send'
    data = {
        "msgheader": NETGSM_MSGHEADER,
        "messages": [{"msg": msg, "no": to}],
        "encoding": "TR",
        "iysfilter": "",
        "partnercode": ""
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + requests.auth._basic_auth_str(NETGSM_USERNAME, NETGSM_PASSWORD).split(' ')[1]
    }
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
        print(f"[UYARI] SMS Gönderim Yanıtı: {response.text}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[HATA] SMS gönderilirken hata oluştu: {e}")
        return None

def netgsm_make_call(to):
    """Initiates a call using NetGSM API."""
    url = 'https://api.netgsm.com.tr/voice/arama'
    xml = f"""<?xml version='1.0' encoding='UTF-8'?>\n<mainbody>\n<header>\n<usercode>{NETGSM_USERNAME}</usercode>\n<password>{NETGSM_PASSWORD}</password>\n<startdate></startdate>\n<stopdate></stopdate>\n<type>arama</type>\n<title>Uyari</title>\n</header>\n<body>\n<no>{to}</no>\n<caller>{NETGSM_CALLER_ID}</caller>\n<msg>Reklam alanında boş tarih var. Lütfen kontrol edin.</msg>\n</body>\n</mainbody>"""
    headers = {'Content-Type': 'application/xml'}
    try:
        response = requests.post(url, data=xml.encode('utf-8'), headers=headers, verify=False)
        print(f"[UYARI] Çağrı Başlatma Yanıtı: {response.text}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[HATA] Çağrı başlatılırken hata oluştu: {e}")
        return None

# --- Data Parsing Functions (from satin.py) ---
def clean_value(value):
    """Cleans HTML values, identifying 'DOLU' or 'BOŞ' states."""
    if 'class="full"' in value:
        return 'DOLU'
    if 'class="empty"' in value:
        return 'BOŞ'
    return BeautifulSoup(value, 'html.parser').get_text(strip=True)

def field_to_date_range(field):
    """Converts field names to date range strings."""
    m = re.match(r'field-(\d{4})-(\d{2})-(\d{2})-(\d{4})-(\d{2})-(\d{2})', field)
    if m:
        start = f"{m.group(3)}.{m.group(2)}.{m.group(1)} 00:00"
        end = f"{m.group(6)}.{m.group(5)}.{m.group(4)} 23:59"
        return f"{start} - {end}"
    return field

def is_date_range_title(title):
    """Checks if a title matches the date range format."""
    return re.match(r'\d{2}\.\d{2}\.\d{4} 00:00 - \d{2}\.\d{2}\.\d{4} 23:59', title)


def parse_columns(content):
    """Parses column definitions from the JavaScript content."""
    columns = []
    for col_match in re.finditer(r'columns.push\(\s*{([^}]+)}\s*\)', content):
        col_block = col_match.group(1)
        field = ''
        title = ''
        f = re.search(r"field:\s*'([^']+)'", col_block)
        t = re.search(r"title:\s*'([^']*)'", col_block)
        if f:
            field = f.group(1)
        if t:
            title = t.group(1)
        columns.append({'field': field, 'title': title})
    return columns

def parse_rows(content, columns):
    """Parses row data from the JavaScript content based on columns."""
    rows = []
    field_to_title = {}
    for col in columns:
        if col['field'] == 'first_column':
            field_to_title[col['field']] = 'Reklam Alanı'
        else:
            title = col['title'].strip()
            if title and is_date_range_title(title):
                field_to_title[col['field']] = title
            elif not title:
                field_to_title[col['field']] = field_to_date_range(col['field'])
            else:
                field_to_title[col['field']] = title

    for row_match in re.finditer(r"row\['first_column'\]\s*=\s*'([^']+)';(.*?)data.push\(row\)", content, re.DOTALL):
        row_block = row_match.group(0)
        row = {}
        bos_tarihler = []
        fc = re.search(r"row\['first_column'\]\s*=\s*'([^']+)';", row_block)
        if fc:
            reklam_alani = clean_value(fc.group(1))
            found_keyword = None
            found_id = None
            for keyword, id_ in allowed_keywords.items():
                if keyword.lower() in reklam_alani.lower():
                    found_keyword = keyword
                    found_id = id_
                    break
            if not found_keyword:
                continue
            row['Reklam Alanı'] = reklam_alani
            row['reklamAlanId'] = found_id
        else:
            continue

        for field, value in re.findall(r"row\['([^']+)'\]\s*=\s*'([^']+)';", row_block):
            if field == 'first_column':
                continue
            title = field_to_title.get(field, field)
            value_clean = clean_value(value)
            row[title] = value_clean
            if value_clean == 'BOŞ':
                bos_tarihler.append(title)
        if bos_tarihler:
            row['bos_tarihler'] = bos_tarihler
        rows.append(row)
    return rows

def process_and_notify_reklam(session, file_path, to_phone_number, send_call=False):
    """
    Processes advertisement data, identifies empty slots, and sends notifications.
    Attempts to perform purchase/reservation if empty slots are found.
    """
    print(f"\n[UYARI] Reklam alanları kontrol ediliyor: {file_path}")
    file_content = ""
    try:
        if file_path.startswith('http'):
            file_content = requests.get(file_path).text
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
    except Exception as e:
        print(f"[HATA] Reklam veri kaynağı okunurken hata oluştu: {e}")
        return None, None

    print("[UYARI] Kolonlar parse ediliyor...")
    columns = parse_columns(file_content)
    print("[UYARI] Satırlar parse ediliyor...")
    data = parse_rows(file_content, columns)
    bos_olanlar = {}
    print("[UYARI] Boş tarih kontrolü yapılıyor...")
    for row in data:
        if 'Reklam Alanı' in row and 'bos_tarihler' in row:
            bos_olanlar[row['Reklam Alanı']] = {
                'id': row.get('reklamAlanId', 21), # Default ID if not found
                'tarihler': row['bos_tarihler']
            }
    
    # Remove temporary fields before returning data
    for row in data:
        row.pop('bos_tarihler', None)
        row.pop('reklamAlanId', None)

    sms_response = None
    call_response = None
    if bos_olanlar:
        print("\n[UYARI] Boş reklam alanları bulundu!")
        msg_lines = ["Reklam alanlarında boş tarihler var:"]
        for alan, info in bos_olanlar.items():
            msg_lines.append(f"- {alan}:")
            for tarih in info['tarihler']:
                msg_lines.append(f"  * {tarih}")
        msg = '\n'.join(msg_lines)
        
        print("[UYARI] SMS gönderiliyor...")
        sms_response = netgsm_send_sms(to_phone_number, msg)
        
        if SEND_CALL_NOTIFICATION: # Check if call notification is enabled
            print("[UYARI] Çağrı başlatılıyor...")
            call_response = netgsm_make_call(to_phone_number)
        
        # --- Purchase/Reservation Logic ---
        print("[UYARI] Boş reklam alanları için satın alma/rezervasyon işlemleri başlatılıyor...")
        for reklam_alani, info in bos_olanlar.items():
            plan_id = info['id']
            fields = info['tarihler']
            for field in fields:
                date_range_formatted = None
                # field-YYYY-MM-DD-YYYY-MM-DD formatı
                if field.startswith('field-'):
                    field_without_prefix = field.replace('field-', '')
                    dates = field_without_prefix.split('-', 5)
                    if len(dates) == 6:
                        start_date_fmt = f"{dates[0]}-{dates[1]}-{dates[2]}"
                        end_date_fmt = f"{dates[3]}-{dates[4]}-{dates[5]}"
                        date_range_formatted = f"{start_date_fmt}/{end_date_fmt}"
                    else:
                        print(f"[UYARI] field- ile başlayan tarih formatı hatalı, atlanıyor: {field}")
                        continue
                # DD.MM.YYYY 00:00 - DD.MM.YYYY 23:59 formatı
                elif ' - ' in field and '00:00' in field and '23:59' in field:
                    try:
                        start, end = field.split(' - ')
                        start_date = start.split(' ')[0]
                        end_date = end.split(' ')[0]
                        # dd.mm.yyyy -> yyyy-mm-dd
                        sd = start_date.split('.')
                        ed = end_date.split('.')
                        if len(sd) == 3 and len(ed) == 3:
                            start_date_fmt = f"{sd[2]}-{sd[1]}-{sd[0]}"
                            end_date_fmt = f"{ed[2]}-{ed[1]}-{ed[0]}"
                            date_range_formatted = f"{start_date_fmt}/{end_date_fmt}"
                        else:
                            print(f"[UYARI] Noktalı tarih formatı hatalı, atlanıyor: {field}")
                            continue
                    except Exception as e:
                        print(f"[UYARI] Noktalı tarih formatı ayrıştırılamadı, atlanıyor: {field}. Hata: {e}")
                        continue
                else:
                    print(f"[UYARI] Tanınmayan tarih formatı, atlanıyor: {field}")
                    continue

                print(f"[UYARI] Satın alma/rezervasyon için boş tarih: {reklam_alani} - {date_range_formatted}")
                
                # Dynamic plan_values based on your script's logic
                plan_values = {
                    'selectedPlan': plan_id,
                    'selectedDates': date_range_formatted,
                    'selectedPlanValues': {
                        'id': plan_id,
                        'slug': 'product_bottom', # This might need to be dynamic or configured
                        'name': reklam_alani,
                        'default_photo': '5ecbd6fc292a261e59b39e828711011a.png',
                        'width': '1040',
                        'height': '200',
                        'weekly_price': 3333.3333333333335, # This might need to be dynamic
                        'status': True,
                        'updated_at': '2024-11-26T09:39:50.000000Z',
                        'day': 7,
                        'preview_image': '01df031d6e48fc18c7f7837ff15977f9.jpg',
                        'order': 7,
                        'left_right': False
                    },
                    'image': None,
                    'imageTwo': None,
                    'link': 'https://itemci.com/rek/create',
                    'non_photo': True,
                    'name': '123', # This might need to be dynamic
                    'payment_type': '1'
                }
                
                csrf_token_pay = get_csrf_token(session, 'https://itemci.com/rek/create')
                if csrf_token_pay:
                    print(f"[UYARI] Satın alma için CSRF Token: {csrf_token_pay}")
                else:
                    print("[UYARI] Satın alma için CSRF token bulunamadı, işlem atlanıyor.")
                    continue

                print(f"[UYARI] POST isteği gönderiliyor: {reklam_alani} - {date_range_formatted}")
                post_data = {
                    '_token': csrf_token_pay,
                    'planValues': json.dumps(plan_values, ensure_ascii=False, separators=(',', ':'))
                }
                headers = {
                    'Host': 'itemci.com',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Origin': 'https://itemci.com',
                    'Referer': 'https://itemci.com/rek/create',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
                }
                
                try:
                    response = session.post('https://itemci.com/rek/pay', data=post_data, headers=headers, verify=False)
                    if response.status_code == 200:
                        print(f"[UYARI] İstek başarıyla gönderildi: {reklam_alani} - {date_range_formatted}")
                        print(f"[UYARI] Satın alma/Rezervasyon Response: {response.text}\n")
                    else:
                        print(f"[UYARI] İstek gönderilemedi! HTTP Code: {response.status_code}")
                        print(f"[UYARI] Satın alma/Rezervasyon Response: {response.text}\n")
                except requests.exceptions.RequestException as e:
                    print(f"[HATA] Satın alma/rezervasyon isteği sırasında hata oluştu: {e}")
                    
    else:
        print("[UYARI] Boş tarih bulunamadı, SMS/çağrı yapılmayacak ve satın alma işlemi tetiklenmeyecek.")
    
    return data, bos_olanlar

# --- Login Status File Operations ---
def record_login_status(status_file_path):
    """Records '1' and the current timestamp to the login status file."""
    timestamp = datetime.now().isoformat()
    with open(status_file_path, 'w') as f:
        f.write(f"1 {timestamp}")
    print(f"[UYARI] Giriş durumu '{status_file_path}' dosyasına kaydedildi: 1 {timestamp}")

def get_last_login_timestamp(status_file_path):
    """Reads the last login timestamp from the status file."""
    if not os.path.exists(status_file_path):
        return None
    try:
        with open(status_file_path, 'r') as f:
            content = f.read().strip()
            parts = content.split(' ', 1)
            if len(parts) == 2 and parts[0] == '1':
                return datetime.fromisoformat(parts[1])
    except Exception as e:
        print(f"[HATA] Giriş durumu dosyasından okuma hatası: {e}")
    return None

# --- Login Function ---
def perform_login(session):
    """
    Performs the login process, including OTP validation.
    Returns True if login is successful, False otherwise.
    """
    print('[UYARI] 1. Giriş sayfasına GET isteği atılıyor...')
    try:
        resp = session.get('https://itemci.com/user/login', headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
        })
        resp.raise_for_status() # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"[HATA] Giriş sayfasına erişilemedi: {e}")
        return False

    csrf_token = get_csrf_token_from_html(resp.text)
    if not csrf_token:
        print('CSRF Token bulunamadı! Giriş yapılamadı.')
        return False
    print(f'[UYARI] CSRF Token: {csrf_token}')
    save_cookies(session, COOKIE_FILE_PATH)

    print('[UYARI] 2. Login POST isteği atılıyor...')
    post_data = {
        'email': EMAIL,
        'password': PASSWORD
    }
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://itemci.com',
        'referer': 'https://itemci.com/user/login',
        'x-csrf-token': csrf_token,
        'x-requested-with': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
    }
    try:
        resp = session.post('https://itemci.com/user/login', data=post_data, headers=headers)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[HATA] Login POST isteği başarısız: {e}")
        return False

    print('\n=== Login Response ===\n')
    print(resp.text)
    save_cookies(session, COOKIE_FILE_PATH)

    # Check if OTP is required based on response
    if 'otp' in resp.text or 'validate-otp-code' in resp.text:
        print('\n[UYARI] 3. Lütfen OTP kodunu girin: ', end='', flush=True)
        otp_code = input().strip()

        print('[UYARI] 4. OTP doğrulama POST isteği atılıyor...')
        otp_post_data = {'code': otp_code}
        headers_otp = headers.copy()
        headers_otp['referer'] = 'https://itemci.com/user/otp'
        try:
            resp = session.post('https://itemci.com/user/login/validate-otp-code', data=otp_post_data, headers=headers_otp)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[HATA] OTP doğrulama POST isteği başarısız: {e}")
            return False

        save_cookies(session, FINAL_COOKIE_FILE_PATH)
        print('\n=== OTP Validation Response ===\n')
        print(resp.text)

    # Final check for successful login
    if 'dashboard' in resp.text or 'başarılı' in resp.text or resp.status_code == 200:
        print('\n✅ Giriş başarılı, dashboard yükleniyor...')
        # Attempt to fetch dashboard to confirm session
        headers_dash = {
            'User-Agent': headers['User-Agent'],
            'Referer': 'https://itemci.com/user/otp',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        }
        try:
            resp_dash = session.get('https://itemci.com/user/dashboard', headers=headers_dash)
            resp_dash.raise_for_status()
            print('\n=== Dashboard ===\n')
            print(resp_dash.text)
            # Record successful login
            record_login_status(LOGIN_STATUS_FILE)
            return True
        except requests.exceptions.RequestException as e:
            print(f"[HATA] Dashboard yüklenirken hata oluştu (ancak OTP başarılı görünüyor): {e}")
            return False
    else:
        print('\n❌ OTP başarısız ya da yönlendirme olmadı. Giriş başarısız.')
        return False

# --- Main Automation Loop ---
def main_automation_loop():
    
    print("[UYARI] Otomasyon döngüsü başlatılıyor...")
    
    # Determine if initial login is needed
    needs_initial_login = True
    last_login_timestamp_from_file = get_last_login_timestamp(LOGIN_STATUS_FILE)

    if last_login_timestamp_from_file:
        time_since_last_login = datetime.now() - last_login_timestamp_from_file
        if time_since_last_login.total_seconds() < LOGIN_INTERVAL_SECONDS:
            needs_initial_login = False
            print(f"[UYARI] Son giriş {time_since_last_login.total_seconds():.0f} saniye önce yapılmış. "
                  f"{(LOGIN_INTERVAL_SECONDS / 60):.0f} dakikalık periyot dolmadığı için yeniden giriş yapılmıyor. Cookie'ler yüklenecek.")
            if load_cookies_to_session(global_session, FINAL_COOKIE_FILE_PATH):
                print("[UYARI] Cookie'ler başarıyla yüklendi.")
            else:
                print("[HATA] Cookie yüklenemedi, yeni bir giriş denenecek.")
                needs_initial_login = True
        else:
            print(f"[UYARI] Son giriş {(LOGIN_INTERVAL_SECONDS / 60):.0f} dakikadan fazla zaman önce yapılmış. Yeniden giriş yapılması gerekiyor.")
            
    if needs_initial_login:
        print("[UYARI] İlk giriş denemesi yapılıyor veya yeniden giriş gerekiyor...")
        if perform_login(global_session):
            print("[UYARI] İlk giriş başarılı.")
        else:
            print("[HATA] İlk giriş başarısız oldu. Program sonlandırılıyor.")
            return

    while True:
        current_time = datetime.now()
        last_login_ts = get_last_login_timestamp(LOGIN_STATUS_FILE)

        # Check for re-login every LOGIN_INTERVAL_SECONDS
        if not last_login_ts or (current_time - last_login_ts).total_seconds() >= LOGIN_INTERVAL_SECONDS:
            print(f"\n[UYARI] {(LOGIN_INTERVAL_SECONDS / 60):.0f} dakika geçti veya giriş durumu bulunamadı. Yeniden giriş yapılıyor...")
            if perform_login(global_session):
                print("[UYARI] Yeniden giriş başarılı.")
            else:
                print("[HATA] Yeniden giriş başarısız oldu. Manuel müdahale gerekebilir.")
                # Depending on robustness needs, you might want to exit or retry
                # For now, we'll continue with potentially invalid session for checks
        
        # Perform advertisement slot check and purchase logic
        data, bos_olanlar = process_and_notify_reklam(global_session, REKLAM_DATA_SOURCE, TO_PHONE_NUMBER, SEND_CALL_NOTIFICATION)
        
        if bos_olanlar:
            print("[UYARI] Boş alanlar bulundu ve işlemler yapıldı. Sonraki kontrol bekleniyor.")
        else:
            print("[UYARI] Boş alan bulunamadı. Sonraki kontrol bekleniyor.")
        
        print(f"[UYARI] {CHECK_INTERVAL_SECONDS} saniye bekleniyor...")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == '__main__':
    main_automation_loop()