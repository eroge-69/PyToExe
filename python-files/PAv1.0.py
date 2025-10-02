from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd
import time
import os
import sys
import ctypes, ctypes.wintypes
from datetime import datetime
import winsound
import logging
import openpyxl
import re

BASE_URL = "https://katalog.profiauto.net/"
USERNAME = "TIM OELSCHLAEGER"
PASSWORD = "EZXdpcEN*#*"

SEARCH_INPUT_CSS = "input#search"
RESULTS_SCOPE_CSS = (
    "body > app-root > div > app-layout > div > div > "
    "app-search-articles > div > div.articles-container.row > "
    "app-articles > div > div > div.articles-right-container"
)
ROW_SELECTOR = "app-articles-list-row"
TITLE_LINK = "a.articles-title-index"
WAREHOUSES_CONTAINER = "div.warehouses-container"
WAREHOUSE_ITEM = "div.warehouse-item-container"
WAREHOUSE_NAME = ".warehouse-name"
WAREHOUSE_VALUE = ".warehouse-value"

SESSION_BATCH_SIZE = 200
AUTOSAVE_EVERY = 50

def get_desktop_path():
    csidl_desktop = 0x0000
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, csidl_desktop, None, 0, buf)
    return buf.value

def msgbox(text, title="Fehler"):
    ctypes.windll.user32.MessageBoxW(0, str(text), str(title), 0x00000010)

def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

def make_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def normalize_part(s: str) -> str:
    if s is None:
        return ""
    s = re.sub(r"\s+", "", str(s)).upper()
    return s

def find_search_input(driver, timeout=20):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, SEARCH_INPUT_CSS))
    )

def install_network_hooks(driver):
    js = r"""
    (function () {
      if (window.__hooksInstalled) return;
      window.__pendingRequests = 0;
      const _fetch = window.fetch;
      window.fetch = function() {
        window.__pendingRequests++;
        return _fetch.apply(this, arguments).finally(function () {
          window.__pendingRequests--;
        });
      };
      const _send = XMLHttpRequest.prototype.send;
      XMLHttpRequest.prototype.send = function() {
        window.__pendingRequests++;
        this.addEventListener('loadend', function () {
          window.__pendingRequests--;
        });
        return _send.apply(this, arguments);
      };
      window.__hooksInstalled = true;
    })();
    """
    driver.execute_script(js)

def wait_network_idle(driver, idle_ms=600, timeout=20):
    end = time.time() + timeout
    last_quiet = None
    while time.time() < end:
        try:
            pending = driver.execute_script("return window.__pendingRequests || 0;")
        except Exception:
            pending = 0
        if pending == 0:
            if last_quiet is None:
                last_quiet = time.time()
            if (time.time() - last_quiet) * 1000 >= idle_ms:
                return True
        else:
            last_quiet = None
        time.sleep(0.05)
    return False

def get_results_signature(driver):
    js = """
      const scope = document.querySelector(arguments[0]);
      if (!scope) return null;
      return scope.innerText.slice(0,400);
    """
    try:
        return driver.execute_script(js, RESULTS_SCOPE_CSS)
    except Exception:
        return None

def wait_results_changed(driver, prev_sig, timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        sig = get_results_signature(driver)
        if sig is not None and sig != prev_sig:
            return True
        time.sleep(0.1)
    return False

def parse_qty(text):
    if text is None:
        return 0
    t = str(text).replace("\xa0", " ").strip()
    m = re.search(r"\d+", t)
    return int(m.group(0)) if m else 0

def check_no_data(driver):
    try:
        scope = driver.find_element(By.CSS_SELECTOR, RESULTS_SCOPE_CSS)
        spans = scope.find_elements(By.CSS_SELECTOR, "span.capitalize")
        for sp in spans:
            if sp.text.strip().lower() == "no data":
                return True
    except Exception:
        return False
    return False

def find_row_for_part(driver, part_number: str, timeout=8):
    target = normalize_part(part_number)
    try:
        scope = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, RESULTS_SCOPE_CSS))
        )
    except TimeoutException:
        return None
    links = scope.find_elements(By.CSS_SELECTOR, TITLE_LINK)
    for a in links:
        try:
            txt = normalize_part(a.text)
            tokens = re.findall(r"[A-Z0-9\-_/\.]+", txt)
            tokens = [normalize_part(x) for x in tokens]
            if target in tokens or txt == target:
                try:
                    row = a.find_element(By.XPATH, "./ancestor::app-articles-list-row[1]")
                    return row
                except Exception:
                    pass
        except Exception:
            continue
    return None

def availability_from_row(row):
    swi_val, chw_val = 0, 0
    try:
        wh_container = row.find_element(By.CSS_SELECTOR, WAREHOUSES_CONTAINER)
    except Exception:
        return None
    items = wh_container.find_elements(By.CSS_SELECTOR, WAREHOUSE_ITEM)
    for it in items:
        try:
            name = (it.find_element(By.CSS_SELECTOR, WAREHOUSE_NAME).text or "").strip().upper()
            val_text = (it.find_element(By.CSS_SELECTOR, WAREHOUSE_VALUE).text or "").strip()
            val = parse_qty(val_text)
            if name == "SWI":
                swi_val = max(swi_val, val)
            elif name == "CHW":
                chw_val = max(chw_val, val)
        except Exception:
            continue
    return swi_val, chw_val

def get_availability_status(driver, part_number: str, timeout=8):
    if check_no_data(driver):
        return "No data"
    row = find_row_for_part(driver, part_number, timeout=timeout)
    if row is None:
        try:
            scope = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, RESULTS_SCOPE_CSS))
            )
        except TimeoutException:
            return "Unbekannt"
        try:
            wh_container = scope.find_element(By.CSS_SELECTOR, WAREHOUSES_CONTAINER)
        except Exception:
            return "Unbekannt"
        try:
            items = wh_container.find_elements(By.CSS_SELECTOR, WAREHOUSE_ITEM)
        except Exception:
            return "Unbekannt"
        swi_val, chw_val = 0, 0
        for it in items:
            try:
                name = (it.find_element(By.CSS_SELECTOR, WAREHOUSE_NAME).text or "").strip().upper()
                val = parse_qty((it.find_element(By.CSS_SELECTOR, WAREHOUSE_VALUE).text or "0"))
                if name == "SWI":
                    swi_val = max(swi_val, val)
                elif name == "CHW":
                    chw_val = max(chw_val, val)
            except Exception:
                continue
    else:
        vals = availability_from_row(row)
        if vals is None:
            return "Unbekannt"
        swi_val, chw_val = vals
    if swi_val > 0 or chw_val > 0:
        return "Verfügbar"
    return "Nicht verfügbar"

def start_session():
    driver = make_driver()
    wait = WebDriverWait(driver, 25)
    driver.set_page_load_timeout(45)
    driver.get(BASE_URL)
    login_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "login")))
    pass_input  = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "password")))
    login_input.clear(); login_input.send_keys(USERNAME)
    pass_input.clear(); pass_input.send_keys(PASSWORD); pass_input.send_keys(Keys.ENTER)
    search_input = find_search_input(driver, timeout=25)
    install_network_hooks(driver)
    return driver, wait, search_input

base_dir = get_base_dir()
Tk().withdraw()
EXCEL_FILENAME = askopenfilename(
    title="Excel-Datei auswählen",
    filetypes=[("Excel-Dateien", "*.xlsx *.xls")]
)
if not EXCEL_FILENAME:
    raise FileNotFoundError("Keine Datei ausgewählt.")

in_base = os.path.splitext(os.path.basename(EXCEL_FILENAME))[0]
log_path = os.path.join(os.path.dirname(EXCEL_FILENAME), f"{in_base}_log.txt")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)
desktop = get_desktop_path()
date_str = datetime.now().strftime("%d.%m.%Y")
output_name = f"{in_base}_updated_{date_str}.xlsx"
OUTPUT_FILENAME = os.path.join(desktop, output_name)
autosave_csv = os.path.join(os.path.dirname(EXCEL_FILENAME), f"{in_base}_autosave.csv")

df = pd.read_excel(EXCEL_FILENAME)
first_col = df.columns[0]
df.rename(columns={first_col: "PartNumber"}, inplace=True)
if "Status" not in df.columns:
    df["Status"] = ""

def is_done(val):
    return str(val).strip() in ("Verfügbar", "Nicht verfügbar", "Unbekannt", "No data")

start_time = time.time()
driver, wait, search_input = start_session()
processed_since_restart = 0
total = len(df)

try:
    for idx, row in df.iterrows():
        part_number = str(row["PartNumber"]).strip()
        if not part_number or part_number.lower() == "nan":
            continue
        if is_done(df.at[idx, "Status"]):
            continue
        if processed_since_restart >= SESSION_BATCH_SIZE:
            try: driver.quit()
            except: pass
            driver, wait, search_input = start_session()
            processed_since_restart = 0
        try:
            prev_sig = get_results_signature(driver)
            try:
                search_input.clear()
            except Exception:
                search_input = find_search_input(driver, timeout=10)
                search_input.clear()
            search_input.send_keys(part_number + "\n")
            changed = wait_results_changed(driver, prev_sig, timeout=12)
            idle_ok = wait_network_idle(driver, idle_ms=600, timeout=12)
            if not changed and not idle_ok:
                status = "Unbekannt"
            else:
                status = get_availability_status(driver, part_number, timeout=6)
            df.at[idx, "Status"] = status
            processed_since_restart += 1
            if (idx + 1) % AUTOSAVE_EVERY == 0:
                try:
                    df[["PartNumber", "Status"]].to_csv(autosave_csv, index=False, encoding="utf-8-sig", sep=";")
                except: pass
        except Exception:
            df.at[idx, "Status"] = "Unbekannt"
    elapsed_all = time.time() - start_time
    duration_text = f"Die Suche dauerte: {time.strftime('%H:%M:%S', time.gmtime(elapsed_all))}"
    out_df = df[["PartNumber", "Status"]].copy()
    out_df.loc[len(out_df)] = {"PartNumber": "", "Status": duration_text}
    try:
        with pd.ExcelWriter(OUTPUT_FILENAME, engine="openpyxl") as writer:
            out_df.to_excel(writer, index=False)
        if not os.path.exists(OUTPUT_FILENAME) or os.path.getsize(OUTPUT_FILENAME) == 0:
            raise RuntimeError("Ausgabedatei ist leer oder nicht vorhanden.")
    except Exception as e:
        msgbox(
            f"Excel-Speicherung fehlgeschlagen:\n{e}\nEs wird eine CSV-Kopie erstellt.",
            "Speicherfehler"
        )
        fallback = os.path.join(
            os.path.dirname(EXCEL_FILENAME),
            os.path.splitext(os.path.basename(OUTPUT_FILENAME))[0] + ".csv"
        )
        try:
            out_df.to_csv(fallback, index=False, encoding="utf-8-sig", sep=";")
            msgbox(f"CSV gespeichert:\n{fallback}", "CSV")
        except Exception as e2:
            msgbox(f"CSV-Speicherung ebenfalls fehlgeschlagen:\n{e2}", "Fehler")
finally:
    try: driver.quit()
    except: pass
    winsound.MessageBeep()