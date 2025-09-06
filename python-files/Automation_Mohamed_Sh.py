import time
import threading
import tkinter as tk
from tkinter import ttk
import json
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==== GLOBALS ====
USERNAME_FORM = "aboshalab"
PASSWORD_FORM = "Aa123456"
PROCESSING_REELS = set()
DB_FILE = "processed_reels.json"

# ==== LOAD PROCESSED REELS ====
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        PROCESSED_REELS = set(json.load(f))
else:
    PROCESSED_REELS = set()

def save_processed_reels():
    with open(DB_FILE, "w") as f:
        json.dump(list(PROCESSED_REELS), f)

# ==== FUNCTION TO SUBMIT FORM ====
def login_and_submit(reel_link, field_type_value, service_type_value, hours, interval_range, qty_range):
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()
        driver.get("https://foollo.com/")

        wait = WebDriverWait(driver, 15)

        # LOGIN
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME_FORM)
        wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD_FORM + Keys.RETURN)

        # Wait until page fully loads
        time.sleep(3)

        # SELECT DROPDOWNS
        wait.until(EC.element_to_be_clickable((By.ID, "order-category"))).click()
        category_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//button[@onclick='selectCategory({field_type_value})']"))
        )
        category_btn.click()

        wait.until(EC.element_to_be_clickable((By.ID, "order-services"))).click()
        service_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//button[@onclick='selectOrder({service_type_value})']"))
        )
        service_btn.click()

        end_time = time.time() + hours * 3600

        # ==== SUBMISSION LOOP ====
        while time.time() < end_time:
            try:
                # REFRESH ELEMENTS EACH TIME
                link_field = wait.until(EC.presence_of_element_located((By.ID, "field-orderform-fields-link")))
                qty_field = wait.until(EC.presence_of_element_located((By.ID, "field-orderform-fields-quantity")))
                submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))

                # fill link
                link_field.clear()
                link_field.send_keys(reel_link)

                # fill quantity (random within range)
                quantity = random.randint(qty_range[0], qty_range[1])
                qty_field.clear()
                qty_field.send_keys(str(quantity))

                # scroll to button and click
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                time.sleep(0.5)
                try:
                    submit_btn.click()
                except:
                    driver.execute_script("arguments[0].click();", submit_btn)

                print(f"✅ Submitted {reel_link} with qty {quantity}")

                # wait random interval within range
                if time.time() < end_time:
                    wait_min = random.randint(interval_range[0], interval_range[1])
                    print(f"⏱ Waiting {wait_min} minutes before next submission...")
                    time.sleep(wait_min * 60)

            except Exception as e:
                print(f"⚠️ Error during submission of {reel_link}: {e}")
                break

        print(f"🟢 Finished processing {reel_link}")

    except Exception as e:
        print(f"❌ Fatal error for {reel_link}: {e}")

    finally:
        try:
            driver.quit()
        except:
            pass
        PROCESSING_REELS.discard(reel_link)

# ==== THREAD HANDLER ====
def process_reel_from_input():
    reel_link = entry_link.get().strip()
    if not reel_link:
        print("⚠️ Enter a reel link.")
        return

    if reel_link in PROCESSING_REELS or reel_link in PROCESSED_REELS:
        print("⚠️ Reel already processed or processing.")
        return

    try:
        hours = float(entry_hours.get())
        interval_min = int(entry_interval_min.get())
        interval_max = int(entry_interval_max.get())
        if interval_min < 21:
            print("⚠️ Interval min must be >= 21.")
            return
        qty_min = int(entry_qty_min.get())
        qty_max = int(entry_qty_max.get())
        if qty_min > qty_max:
            print("⚠️ Invalid quantity range.")
            return
    except:
        print("⚠️ Invalid numeric inputs.")
        return

    field_type_value = dropdown_field_type.get().split(":")[0]
    service_type_value = dropdown_service_type.get().split(":")[0]

    PROCESSING_REELS.add(reel_link)
    PROCESSED_REELS.add(reel_link)
    save_processed_reels()

    threading.Thread(
        target=login_and_submit,
        args=(reel_link, field_type_value, service_type_value, hours, (interval_min, interval_max), (qty_min, qty_max)),
        daemon=True
    ).start()

    print(f"🎬 Started processing {reel_link}")

# ==== GUI ====
root = tk.Tk()
root.title("Instagram Reel Processor (Advanced)")

tk.Label(root, text="Enter Instagram Reel Link:").pack()
entry_link = tk.Entry(root, width=50)
entry_link.pack()

# Dropdown for field type
tk.Label(root, text="Field Type:").pack()
field_type_options = ["833:Followers TikTok", "834:Likes TikTok"]
dropdown_field_type = ttk.Combobox(root, values=field_type_options)
dropdown_field_type.pack()
dropdown_field_type.current(0)

# Dropdown for service type
tk.Label(root, text="Service Type:").pack()
service_type_options = ["716:30k/day", "717:100k/day"]
dropdown_service_type = ttk.Combobox(root, values=service_type_options)
dropdown_service_type.pack()
dropdown_service_type.current(0)

# Timing interval range
tk.Label(root, text="Interval Min (≥21 mins):").pack()
entry_interval_min = tk.Entry(root, width=10)
entry_interval_min.pack()
tk.Label(root, text="Interval Max (mins):").pack()
entry_interval_max = tk.Entry(root, width=10)
entry_interval_max.pack()

# Number of hours
tk.Label(root, text="Number of Hours:").pack()
entry_hours = tk.Entry(root, width=10)
entry_hours.pack()

# Quantity range
tk.Label(root, text="Quantity Min:").pack()
entry_qty_min = tk.Entry(root, width=10)
entry_qty_min.pack()
tk.Label(root, text="Quantity Max:").pack()
entry_qty_max = tk.Entry(root, width=10)
entry_qty_max.pack()

# Process button
btn = tk.Button(root, text="Process Reel", command=process_reel_from_input)
btn.pack(pady=20)

root.mainloop()

