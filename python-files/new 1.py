#!/usr/bin/env python3
"""
Scrape ForexFactory calendar for HIGH impact (red) USD & EUR events (2023)
and save only Date, Time, Currency, Event Name to CSV.

Requirements:
  pip install selenium pandas webdriver-manager
"""

import time
import datetime as dt
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# === CONFIG ===
START_YEAR = 2023
OUTPUT_CSV = "forexfactory_2023_eur_usd_high.csv"
TARGET_CURRENCIES = {"USD", "EUR"}
DELAY_SHORT = 1.0
DELAY_LONG = 2.5

# === Selenium driver setup ===
def make_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

# === Helper functions ===
def week_url_from_date(d: dt.date) -> str:
    monday = d - dt.timedelta(days=d.weekday())
    month_abbr = monday.strftime("%b").lower()  # e.g., jan, feb
    return f"https://www.forexfactory.com/calendar?week={month_abbr}{monday.day}.2023"

def apply_filters(driver):
    """Apply High impact and USD/EUR filters."""
    time.sleep(DELAY_SHORT)
    # Click "Filters" if needed
    try:
        filters_btn = driver.find_elements(By.XPATH, "//button[contains(., 'Filters') or contains(., 'filter')]")
        if filters_btn:
            filters_btn[0].click()
            time.sleep(DELAY_SHORT)
    except Exception:
        pass
    # Select only High impact
    try:
        high_checkbox = driver.find_elements(By.XPATH, "//label[contains(., 'High')]/input")
        if high_checkbox and not high_checkbox[0].is_selected():
            driver.execute_script("arguments[0].click();", high_checkbox[0])
            time.sleep(DELAY_SHORT)
    except Exception:
        pass
    # Filter currencies to EUR & USD
    try:
        currency_section = driver.find_elements(By.XPATH, "//details[contains(., 'Currency')]")
        if currency_section:
            currency_section[0].click()
            time.sleep(DELAY_SHORT)
        all_cbs = driver.find_elements(By.XPATH, "//label/input[@type='checkbox']")
        for cb in all_cbs:
            label = cb.find_element(By.XPATH, "./..").text.strip().upper()
            if any(cur in label for cur in TARGET_CURRENCIES):
                if not cb.is_selected():
                    driver.execute_script("arguments[0].click();", cb)
            else:
                if cb.is_selected():
                    driver.execute_script("arguments[0].click();", cb)
        time.sleep(DELAY_SHORT)
    except Exception:
        pass

def parse_events(driver):
    """Return a list of dicts with date, time, currency, event"""
    events = []
    rows = driver.find_elements(By.XPATH, "//tr[contains(@class,'calendar__row')]")
    for r in rows:
        try:
            # Currency
            try:
                currency = r.find_element(By.XPATH, ".//td[contains(@class,'calendar__currency')]").text.strip().upper()
            except:
                continue
            if currency not in TARGET_CURRENCIES:
                continue
            # Event name
            try:
                event_name = r.find_element(By.XPATH, ".//td[contains(@class,'calendar__event')]/a").text.strip()
            except:
                event_name = r.find_element(By.XPATH, ".//td[contains(@class,'calendar__event')]").text.strip()
            # Time
            try:
                time_txt = r.find_element(By.XPATH, ".//td[contains(@class,'calendar__time')]").text.strip()
            except:
                time_txt = ""
            # Date: get from nearest date header
            try:
                parent_table = r.find_element(By.XPATH, "./ancestor::table[1]")
                date_header = parent_table.find_element(By.XPATH, ".//th[contains(@class,'calendar__date')]")
                date_txt = date_header.text.strip()
            except:
                date_txt = ""
            events.append({
                "Date": date_txt,
                "Time": time_txt,
                "Currency": currency,
                "Event": event_name
            })
        except Exception:
            continue
    return events

# === Main scraper ===
def scrape_forexfactory_2023():
    driver = make_driver()
    all_events = []
    try:
        current_date = dt.date(START_YEAR, 1, 1)
        end_date = dt.date(START_YEAR, 12, 31)
        seen_weeks = set()
        while current_date <= end_date:
            monday = current_date - dt.timedelta(days=current_date.weekday())
            if monday in seen_weeks:
                current_date += dt.timedelta(days=1)
                continue
            seen_weeks.add(monday)
            url = week_url_from_date(monday)
            driver.get(url)
            time.sleep(DELAY_LONG)
            apply_filters(driver)
            week_events = parse_events(driver)
            all_events.extend(week_events)
            current_date += dt.timedelta(days=7)
    finally:
        driver.quit()
    # Save CSV
    df = pd.DataFrame(all_events)
    df.drop_duplicates(inplace=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(df)} events to {OUTPUT_CSV}")

if __name__ == "__main__":
    scrape_forexfactory_2023()
