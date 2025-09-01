"""
POCKET OPTION AUTO TRADING (EDUCATIONAL) — UPDATED
-------------------------------------------------
SUMMARY / PURPOSE
- This script automates Pocket Option in two modes:
  1) **Real browser mode** (uses undetected-chromedriver + selenium) when your Python environment supports it.
  2) **Simulation mode** (no browser required) for development / sandboxed environments where SSL / Selenium is unavailable.

IMPORTANT: In the environment where the user ran the original file the run failed with:

    ModuleNotFoundError: No module named 'ssl'

`ssl` is a core Python module. When SSL support is missing (commonly because Python was built without OpenSSL headers), many packages (including Selenium/undetected-chromedriver) will fail to import. This updated file does the following to fix that situation:

1. **Removes top-level imports of selenium/undetected-chromedriver** so the module import won't crash the whole file on import-time.
2. **Detects if SSL or browser automation imports are available** and sets `BROWSER_AVAILABLE = False` when not.
3. When browser automation is *not* available this script automatically falls back to a **fast simulation mode** which allows you to test strategies (RSI, logic, unit-tests) without launching a browser.
4. Provides clear on-screen guidance about how to fix SSL in your environment (install OpenSSL dev libraries and rebuild Python) and an option `--simulate` to force simulation.

Security / Legal
- Pocket Option does not provide an official public trading API for automation in this manner. This script uses (when available) browser automation — check and respect Pocket Option's Terms of Service and local regulations.
- **Always** test on a demo account first.

QUICK START (SIMULATED MODE works even when SSL is missing):
1) Python 3.10+
2) pip install -r requirements.txt  # will be useful when browser mode is possible
3) Create `.env` (if you want to run non-simulated mode later):
   PO_EMAIL="your@email.com"
   PO_PASSWORD="your_password"
   PO_ASSET="EURUSD"
   PO_TIMEFRAME="1m"
   PO_EXPIRY_SECONDS=60
   PO_AMOUNT=1.0
   PO_PROXY=""  # optional
   HEADLESS=true
4) To run in simulate mode (no browser needed):
   python pocket_option_bot.py --simulate
5) To run tests:
   python pocket_option_bot.py --test

HOW TO FIX ssl (if you need real browser mode):
- On Debian/Ubuntu: install required packages and rebuild Python with OpenSSL support. Example (run as root):
  apt-get update && apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
  Then rebuild Python from source or use a distribution-provided Python that includes SSL.
- Or run the script on your local machine or a Docker image that already has SSL-enabled Python.

This file also adds unit-tests for the RSI utility and a small simulated-bot test so you can validate logic without a browser.

"""

import os
import sys
import time
import math
import contextlib
import random
import argparse
from typing import Optional, Callable, Literal, Deque
from collections import deque
from dotenv import load_dotenv
import numpy as np

# ---------- Detect SSL and Browser Automation Availability ----------
try:
    import ssl  # this will fail in some broken sandboxed Python builds
    SSL_AVAILABLE = True
    SSL_IMPORT_ERROR = None
except Exception as e:
    SSL_AVAILABLE = False
    SSL_IMPORT_ERROR = e

# Try to import undetected_chromedriver + selenium **only if** SSL is available.
BROWSER_AVAILABLE = False
BROWSER_IMPORT_ERROR = None
uc = None
By = None
WebDriverWait = None
EC = None
Options = None
TimeoutException = None
NoSuchElementException = None
WebDriverException = None

if SSL_AVAILABLE:
    try:
        import undetected_chromedriver as uc  # imported dynamically; may fail
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
        BROWSER_AVAILABLE = True
    except Exception as e:
        BROWSER_AVAILABLE = False
        BROWSER_IMPORT_ERROR = e
else:
    BROWSER_AVAILABLE = False
    BROWSER_IMPORT_ERROR = SSL_IMPORT_ERROR

if not BROWSER_AVAILABLE:
    print("[WARN] Browser automation unavailable in this environment.")
    print("[WARN] Import error:", repr(BROWSER_IMPORT_ERROR))
    print("[INFO] You can still run this script in simulated mode with --simulate.\n")

Direction = Literal["CALL", "PUT", "HOLD"]

# -----------------------------
# Utility: RSI calculation
# -----------------------------
def rsi(values, period: int = 14) -> float:
    """Return latest RSI value for given price series.
    - If there are not enough samples returns NaN.
    """
    arr = np.array(values, dtype=float)
    if arr.size < period + 1:
        return float('nan')
    deltas = np.diff(arr)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    down = 1e-12 if down == 0 else down
    rs = up / down
    rsi_series = np.zeros_like(arr)
    rsi_series[:period] = 100. - 100. / (1. + rs)

    upvals = deltas[period:]
    downvals = -deltas[period:]
    upvals[upvals < 0] = 0
    downvals[downvals < 0] = 0
    up_avg = up
    down_avg = down
    idx = period
    for upval, downval in zip(upvals, downvals):
        up_avg = (up_avg * (period - 1) + upval) / period
        down_avg = (down_avg * (period - 1) + downval) / period
        down_avg = 1e-12 if down_avg == 0 else down_avg
        rs = up_avg / down_avg
        rsi_series[idx] = 100. - 100. / (1. + rs)
        idx += 1
    # idx - 1 is the last computed index
    return float(rsi_series[idx - 1])

# -----------------------------
# PocketOption Web Bot (Selenium) with Simulation Fallback
# -----------------------------
class PocketOptionWebBot:
    def __init__(
        self,
        email: str,
        password: str,
        headless: bool = True,
        proxy: Optional[str] = None,
        asset: str = "EURUSD",
        timeframe: str = "1m",
        expiry_seconds: int = 60,
        amount: float = 1.0,
        simulate_override: Optional[bool] = None,
    ) -> None:
        self.email = email
        self.password = password
        self.asset = asset
        self.timeframe = timeframe
        self.expiry_seconds = expiry_seconds
        self.amount = amount
        self.price_buffer: Deque[float] = deque(maxlen=500)

        # decide simulation mode: explicit override > environment availability
        if simulate_override is None:
            self.sim_mode = not BROWSER_AVAILABLE
        else:
            self.sim_mode = bool(simulate_override)

        self.sim_trades = []  # records of trades when in sim mode

        if not self.sim_mode:
            try:
                self.driver = self._build_driver(headless=headless, proxy=proxy)
            except Exception as e:
                print(f"[WARN] Failed to start real browser mode: {e}. Falling back to simulation.")
                self.driver = None
                self.sim_mode = True
        else:
            self.driver = None

        # simple simulator: random walk starting from a plausible FX price
        self._simulator_price = random.uniform(0.9, 1.5)

    def _build_driver(self, headless: bool, proxy: Optional[str]):
        """Build the undetected-chromedriver browser.
        This is only called if BROWSER_AVAILABLE == True.
        """
        if not BROWSER_AVAILABLE or uc is None:
            raise RuntimeError("Browser automation modules are not available in this environment.")
        options = uc.ChromeOptions()
        if headless:
            # use the newer headless mode flag where supported
            options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1400,900")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(60)
        return driver

    # ---------------------
    # Core UI helpers (work in both real and sim modes)
    # ---------------------
    def open(self):
        if self.sim_mode:
            print("[SIM] open() called — simulation mode, no browser launched.")
            return
        self.driver.get("https://pocketoption.com/en/")
        self._consent_if_any()

    def _consent_if_any(self):
        if self.sim_mode:
            return
        with contextlib.suppress(Exception):
            btns = self.driver.find_elements(By.CSS_SELECTOR, "button, .btn, .Button")
            for b in btns:
                if any(k in (b.get_attribute("innerText") or "").lower() for k in ["accept", "agree", "allow", "i agree", "ok"]):
                    b.click()
                    break

    def login(self):
        if self.sim_mode:
            print(f"[SIM] login() — would log in as {self.email}")
            return
        try:
            login_btn = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/login'], .login, .js-login, [data-target='login']"))
            )
            login_btn.click()
        except Exception:
            pass

        email_input = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email']")))
        pwd_input = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'], input[name='password']")))
        email_input.clear(); email_input.send_keys(self.email)
        pwd_input.clear(); pwd_input.send_keys(self.password)
        submit = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button.login, .auth__submit")
        submit.click()
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#terminal, .terminal, canvas")))

    def select_asset(self, asset: str):
        self.asset = asset
        if self.sim_mode:
            print(f"[SIM] select_asset({asset})")
            return
        try:
            asset_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='asset-selector'], .asset-button, .js-asset-select")))
            asset_btn.click()
            search = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search'], input[placeholder*='Search']")))
            search.clear(); search.send_keys(asset)
            time.sleep(0.5)
            first = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{asset}')][not(self::script)]")))
            first.click()
        except Exception:
            print("[WARN] Could not reliably set asset; please adjust selectors.")

    def set_timeframe(self, timeframe: str):
        self.timeframe = timeframe
        if self.sim_mode:
            print(f"[SIM] set_timeframe({timeframe})")
            return
        try:
            tf_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='timeframe'], .timeframe, .tf-selector")))
            tf_btn.click()
            opt = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{timeframe}')][not(self::script)]")))
            opt.click()
        except Exception:
            print("[WARN] Could not set timeframe; adjust selectors.")

    def set_expiry(self, seconds: int):
        self.expiry_seconds = seconds
        if self.sim_mode:
            print(f"[SIM] set_expiry({seconds})s")
            return
        try:
            exp = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='expiry'], .expiry, .expiration")))
            exp.click()
            opt = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{seconds}') and contains(text(), 's')][not(self::script)]")))
            opt.click()
        except Exception:
            print("[WARN] Could not set expiry; adjust selectors.")

    def set_amount(self, amount: float):
        self.amount = amount
        if self.sim_mode:
            print(f"[SIM] set_amount({amount})")
            return
        try:
            amt = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='amount'], [data-test='amount-input'], .amount input")))
            amt.clear(); amt.send_keys(str(amount))
        except Exception:
            print("[WARN] Could not set amount; adjust selectors.")

    # Read last price from UI (heuristic) or from simulator
    def get_last_price(self) -> Optional[float]:
        if self.sim_mode:
            # random walk tick
            self._simulator_price += random.uniform(-0.0005, 0.0005)
            # round to 5 decimal places like typical FX
            return float(round(self._simulator_price, 5))

        with contextlib.suppress(Exception):
            el = self.driver.find_element(By.CSS_SELECTOR, "[data-test='price'], .last-price, .quote, .chart-price")
            txt = el.get_attribute("innerText") or el.text
            v = ''.join(ch for ch in txt if (ch.isdigit() or ch == '.' ))
            return float(v)
        return None

    def click_call(self):
        if self.sim_mode:
            print("[SIM TRADE] CALL")
            self.sim_trades.append((time.time(), "CALL", self.amount))
            return
        btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='call'], .call, .up, .green")))
        btn.click()

    def click_put(self):
        if self.sim_mode:
            print("[SIM TRADE] PUT")
            self.sim_trades.append((time.time(), "PUT", self.amount))
            return
        btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='put'], .put, .down, .red")))
        btn.click()

    # ---------------------
    # Main loop
    # ---------------------
    def warmup_prices(self, seconds: int = 30):
        print(f"[INFO] Warmup collecting prices for ~{seconds}s…")
        t0 = time.time()
        last = None
        while time.time() - t0 < seconds:
            p = self.get_last_price()
            if p is not None and p != last:
                self.price_buffer.append(p)
                last = p
            time.sleep(0.2)
        print(f"[INFO] Collected {len(self.price_buffer)} ticks.")

    def step(self, strategy: Callable[[Deque[float]], Direction]) -> Direction:
        p = self.get_last_price()
        if p is not None:
            self.price_buffer.append(p)
        try:
            return strategy(self.price_buffer)
        except Exception as e:
            print(f"[STRATEGY ERROR] {e}")
            return "HOLD"

    def trade(self, direction: Direction):
        if direction == "CALL":
            print("[TRADE] CALL")
            self.click_call()
        elif direction == "PUT":
            print("[TRADE] PUT")
            self.click_put()
        else:
            pass

    def run(self, strategy: Callable[[Deque[float]], Direction], max_trades: int = 10, wait_between: int = 5, fast_mode: bool = False):
        """Run trading loop.
        - fast_mode=True will drastically shorten sleeps for testing.
        """
        trades = 0
        while trades < max_trades:
            signal = self.step(strategy)
            if signal in ("CALL", "PUT"):
                self.trade(signal)
                trades += 1
                if fast_mode:
                    # tiny sleep for tests
                    time.sleep(0.05)
                else:
                    time.sleep(self.expiry_seconds + 2)  # wait for option to settle roughly
            else:
                time.sleep(wait_between if not fast_mode else 0.01)

    def close(self):
        if self.sim_mode:
            print("[SIM] close() — nothing to close.")
            return
        with contextlib.suppress(Exception):
            self.driver.quit()

# -----------------------------
# Example Strategy: RSI
# -----------------------------
def rsi_strategy_factory(period: int = 14, overbought: float = 70, oversold: float = 30) -> Callable[[Deque[float]], Direction]:
    def _strategy(buffer: Deque[float]) -> Direction:
        if len(buffer) < period + 5:
            return "HOLD"
        current_rsi = rsi(list(buffer), period)
        if math.isnan(current_rsi):
            return "HOLD"
        if current_rsi <= oversold:
            return "CALL"
        if current_rsi >= overbought:
            return "PUT"
        return "HOLD"
    return _strategy

# -----------------------------
# Unit tests (simple asserts)
# -----------------------------

def run_unit_tests():
    print("[TEST] Running unit tests...")

    # Test RSI: too-short series returns NaN
    short = [1.0] * 10
    assert math.isnan(rsi(short, period=14)), "RSI should be NaN for too-short series"

    # Test RSI direction: increasing series -> RSI > 50
    inc = list(range(1, 101))
    rsi_inc = rsi(inc, period=14)
    assert isinstance(rsi_inc, float)
    assert rsi_inc > 50, f"Expected RSI>50 for increasing series, got {rsi_inc}"

    # Test RSI direction: decreasing series -> RSI < 50
    dec = list(range(200, 100, -1))
    rsi_dec = rsi(dec, period=14)
    assert isinstance(rsi_dec, float)
    assert rsi_dec < 50, f"Expected RSI<50 for decreasing series, got {rsi_dec}"

    # Test strategy behavior (hold when not enough samples)
    strat = rsi_strategy_factory(period=14)
    small_buf = deque(maxlen=500)
    for v in [1, 2, 3, 4]:
        small_buf.append(v)
    assert strat(small_buf) == "HOLD"

    # Test simulated bot trades quickly
    bot = PocketOptionWebBot(email="a@b.c", password="pass", expiry_seconds=1, simulate_override=True)
    def always_call(_: Deque[float]) -> Direction:
        return "CALL"
    # run in fast_mode so tests don't sleep long
    bot.run(always_call, max_trades=3, wait_between=0, fast_mode=True)
    assert len(bot.sim_trades) == 3, f"Expected 3 simulated trades, got {len(bot.sim_trades)}"

    print("[TEST] All tests passed.")

# -----------------------------
# Entrypoint
# -----------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description="Pocket Option Auto Trading (with simulation fallback)")
    parser.add_argument("--simulate", action="store_true", help="Force simulation mode (no browser).")
    parser.add_argument("--test", action="store_true", help="Run unit tests and exit.")
    parser.add_argument("--max-trades", type=int, default=5, help="Max trades to execute")
    args = parser.parse_args(argv)

    if args.test:
        run_unit_tests()
        return

    load_dotenv()
    email = os.getenv("PO_EMAIL")
    password = os.getenv("PO_PASSWORD")
    asset = os.getenv("PO_ASSET", "EURUSD")
    timeframe = os.getenv("PO_TIMEFRAME", "1m")
    expiry = int(os.getenv("PO_EXPIRY_SECONDS", "60"))
    amount = float(os.getenv("PO_AMOUNT", "1.0"))
    proxy = os.getenv("PO_PROXY", "").strip() or None
    headless = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")

    simulate = args.simulate or (not BROWSER_AVAILABLE)

    if not simulate and (not email or not password):
        print("[ERROR] PO_EMAIL and PO_PASSWORD must be set in .env for real browser mode. Use --simulate to run without login.")
        return

    if not BROWSER_AVAILABLE and not args.simulate:
        print("[WARN] Browser automation modules are not available. The script will run in simulation mode.")
        print("[INFO] Error details:", repr(BROWSER_IMPORT_ERROR))
        print("[INFO] To fix: ensure your Python has SSL support (see comments at top). Or run locally where SSL is present.")

    bot = PocketOptionWebBot(
        email=email or "",
        password=password or "",
        headless=headless,
        proxy=proxy,
        asset=asset,
        timeframe=timeframe,
        expiry_seconds=expiry,
        amount=amount,
        simulate_override=simulate,
    )

    try:
        bot.open()
        if not bot.sim_mode:
            bot.login()
            bot.select_asset(asset)
            bot.set_timeframe(timeframe)
            bot.set_expiry(expiry)
            bot.set_amount(amount)
        else:
            print("[SIM] Running in simulation mode — no login/selector actions performed.")

        bot.warmup_prices(2 if bot.sim_mode else 30)
        strategy = rsi_strategy_factory(period=14, overbought=70, oversold=30)
        bot.run(strategy=strategy, max_trades=args.max_trades, wait_between=1, fast_mode=bot.sim_mode)

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        bot.close()


if __name__ == "__main__":
    main()
