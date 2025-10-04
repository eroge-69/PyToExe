import asyncio
import aiohttp
from datetime import datetime, timedelta
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import getpass
import time

# ---------------------- CONFIG ----------------------
LOGIN_URL = "https://qxbroker.com/en/sign-in/"
DEMO_PAGE_URL = "https://market-qx.trade/en/demo-trade"

EMAIL_SELECTOR = "#tab-1 input[name='email']"
PASSWORD_SELECTOR = "#tab-1 input[name='password']"
LOGIN_BUTTON_SELECTOR = "#tab-1 button.modal-sign__block-button"

BUY_BUTTON_SELECTOR = "button.call-btn.section-deal__button"
SELL_BUTTON_SELECTOR = "button.put-btn.section-deal__button"

# Only the Investment input (ignore disabled time field)
AMOUNT_INPUT_SELECTOR = ".section-deal__investment input.input-control__input"

CLOSED_TRADE_SELECTOR = ".trades-list-item__close"
API_URL = "https://sweetex.org/luc.php?type=odd&pair=USDBDT-OTC"

BASE_AMOUNT = 1
last_signal_time = None

driver = None

# ---------------------- CUSTOM MTG ----------------------
MTG_SEQUENCE = [1, 2, 4, 9, 19, 42, 91, 198]

# ---------------------- PAIR CHECK ----------------------
PAIR_NAME_SELECTOR = ".section-deal__name"
REQUIRED_PAIR = "USD/BDT (OTC)"

def set_trade_amount(driver, amount):
    """Set trade amount properly in the Investment field."""
    wait = WebDriverWait(driver, 30)

    amount_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, AMOUNT_INPUT_SELECTOR))
    )
    print("[DEBUG] Found trade investment input")

    # Scroll into view & focus
    driver.execute_script("arguments[0].scrollIntoView(true);", amount_input)
    driver.execute_script("arguments[0].click();", amount_input)
    time.sleep(0.5)

    # Replace value using Ctrl+A
    amount_input.send_keys(Keys.CONTROL, "a")
    amount_input.send_keys(str(amount))

    # Trigger React/Vue/Angular listeners
    driver.execute_script("""
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, amount_input, str(amount))

    print(f"[DEBUG] Trade amount set to: {amount}")


def get_trade_result(driver):
    """Wait for the most recent closed trade and return 'profit' or 'loss'."""
    wait = WebDriverWait(driver, 90)
    closed_trade = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, CLOSED_TRADE_SELECTOR)))
    delta_text = closed_trade.find_element(By.CSS_SELECTOR, ".trades-list-item__delta-right").text.strip()
    print(f"[DEBUG] Trade result text: {delta_text}")
    return "profit" if delta_text.startswith("+") else "loss"


def update_trade_amount_after_result(driver, last_amount):
    # wait extra 5 seconds before checking result (fixes "too fast" issue)
    print("[DEBUG] Waiting 5s before reading trade result...")
    time.sleep(5)

    result = get_trade_result(driver)

    if result == "profit":
        print("✅ PROFIT detected — reset to $1")
        new_amount = MTG_SEQUENCE[0]  # reset to first step
    else:
        print("❌ LOSS detected — moving to next step")
        try:
            idx = MTG_SEQUENCE.index(last_amount)
            new_amount = MTG_SEQUENCE[idx + 1]  # next step
        except (ValueError, IndexError):
            print("⚠️ Amount not in sequence or at max step — resetting to $1")
            new_amount = MTG_SEQUENCE[0]

    set_trade_amount(driver, new_amount)
    return new_amount


def check_pair(driver):
    """Ensure the correct trading pair is selected before starting."""
    try:
        wait = WebDriverWait(driver, 15)
        pair_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, PAIR_NAME_SELECTOR))
        )
        pair_text = pair_element.text.strip()
        print(f"[DEBUG] Current pair: {pair_text}")
        return pair_text == REQUIRED_PAIR
    except Exception as e:
        print(f"⚠️ Could not verify pair: {e}")
        return False


# ---------------------- LOGIN ----------------------
async def browser_login(email, password):
    global driver
    driver = uc.Chrome()
    driver.maximize_window()
    wait = WebDriverWait(driver, 60)

    print("[INFO] Opening login page...")
    driver.get(LOGIN_URL)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, EMAIL_SELECTOR)))

    print("[INFO] Filling credentials...")
    driver.find_element(By.CSS_SELECTOR, EMAIL_SELECTOR).send_keys(email)
    driver.find_element(By.CSS_SELECTOR, PASSWORD_SELECTOR).send_keys(password)

    print("[INFO] Clicking sign in...")
    driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON_SELECTOR).click()

    wait.until(EC.url_contains("/trade"))
    print("[INFO] Logged in successfully, on /trade page")

    print("[INFO] Navigating to demo-trade page...")
    driver.get(DEMO_PAGE_URL)
    wait.until(EC.url_contains("/demo-trade"))
    print("✅ On demo-trade page now")


# ---------------------- SIGNAL FETCH ----------------------
async def fetch_signal():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_URL) as resp:
                if "application/json" in resp.headers.get("Content-Type", ""):
                    return await resp.json()
                else:
                    text = await resp.text()
                    print(f"⚠️ Unexpected response: {text[:200]}...")
                    return None
        except Exception as e:
            print(f"⚠️ Fetch signal error: {e}")
            return None


# ---------------------- TRADE CYCLE ----------------------
async def trade_cycle():
    global last_signal_time
    trade_amount = BASE_AMOUNT

    # 🔒 Wait until required pair is visible before first trade
    while not check_pair(driver):
        print(f"❌ Required pair '{REQUIRED_PAIR}' not found! Waiting...")
        time.sleep(5)

    print(f"✅ Found required pair: {REQUIRED_PAIR}")
    set_trade_amount(driver, trade_amount)  # initialize input

    wait = WebDriverWait(driver, 20)

    while True:
        try:
            signal = await fetch_signal()
            if not signal:
                await asyncio.sleep(2)
                continue

            sig_time = signal["time"]
            sig_hour, sig_min = map(int, sig_time.split(":"))
            direction = signal["direction"].lower()

            if sig_time == last_signal_time:
                await asyncio.sleep(1)
                continue
            last_signal_time = sig_time

            now = datetime.now()
            target_time = now.replace(hour=sig_hour, minute=sig_min, second=0, microsecond=0) - timedelta(seconds=2)

            fetch_window_start = target_time.replace(second=0, microsecond=0)
            fetch_window_end = fetch_window_start + timedelta(seconds=30)
            if not (fetch_window_start <= now <= fetch_window_end):
                print(f"⚠️ Signal {signal} received outside fetch window, skipping...")
                await asyncio.sleep(1)
                continue

            wait_seconds = max(0, (target_time - now).total_seconds())
            print(f"📩 Signal received: {signal}")
            print(f"⏳ Waiting {wait_seconds:.1f}s until trade at {target_time.time()}")
            await asyncio.sleep(wait_seconds)

            if direction in ["call", "up"]:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, BUY_BUTTON_SELECTOR))).click()
                print(f"🚀 TRADE: BUY | Amount ${trade_amount}")
            elif direction in ["put", "down"]:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SELL_BUTTON_SELECTOR))).click()
                print(f"🚀 TRADE: SELL | Amount ${trade_amount}")
            else:
                print(f"⚠️ Unknown direction: {direction}")
                continue

            # wait for result and update amount
            time.sleep(60)  # wait for trade to end
            trade_amount = update_trade_amount_after_result(driver, trade_amount)

            # 🔒 Re-check pair after every trade
            if not check_pair(driver):
                print(f"❌ Pair changed! Waiting for '{REQUIRED_PAIR}' again...")
                while not check_pair(driver):
                    time.sleep(5)
                print(f"✅ Pair restored: {REQUIRED_PAIR}")
                set_trade_amount(driver, trade_amount)

            try:
                balance = driver.execute_script("return window.settings.demoBalance;")
                print(f"💰 Balance after trade: {balance}")
            except Exception as balance_e:
                print(f"⚠️ Could not retrieve balance: {balance_e}")

        except Exception as e:
            print(f"⚠️ Error in trade cycle: {e}")
            await asyncio.sleep(5)


# ---------------------- MAIN ----------------------
async def main():
    email = input("Email: ")
    password = getpass.getpass("Password: ")

    await browser_login(email, password)
    print("✅ Starting trading loop (demo mode)...")
    await trade_cycle()

if __name__ == "__main__":
    asyncio.run(main())
