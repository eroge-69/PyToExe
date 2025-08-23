import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import openpyxl

# ------------------ CONFIG ------------------
CONFIG = {
    "login_url": "https://YOUR-LOGIN-URL",
    "report_url": "https://YOUR-REPORT-PAGE-URL",
    "username": "oman",
    "password": "Report22",
    "selectors": {
        "username": ["input[name='username']", "input#username"],
        "password": ["input[name='password']", "input#password"],
        "login_button": ["input[type='submit']", "button[type='submit']"],
        "search_input": ["#TableMain > tbody > tr > td > form > table > tbody > tr:nth-child(3) > td:nth-child(4) > input"],
        "search_button": ["#TableMain > tbody > tr > td > form > table > tbody > tr:nth-child(7) > td > input[type=button]"],
        "datatable": ["#datatable"]
    }
}


# ------------------ SCRAPER FUNCTION ------------------
def run_scraper(from_date, to_date, store_id, excel_path, output_path,
                max_fallback_results, stop_after_matches, status_callback):
    try:
        status_callback("Launching browser...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()

        # 1. Login
        driver.get(CONFIG["login_url"])
        time.sleep(2)

        for sel in CONFIG["selectors"]["username"]:
            try:
                driver.find_element(By.CSS_SELECTOR, sel).send_keys(CONFIG["username"])
                break
            except:
                pass
        for sel in CONFIG["selectors"]["password"]:
            try:
                driver.find_element(By.CSS_SELECTOR, sel).send_keys(CONFIG["password"])
                break
            except:
                pass
        for sel in CONFIG["selectors"]["login_button"]:
            try:
                driver.find_element(By.CSS_SELECTOR, sel).click()
                break
            except:
                pass
        time.sleep(2)

        # 2. Go to Report Page
        driver.get(CONFIG["report_url"])
        time.sleep(2)

        # Fill in dates & store ID (example: adjust selectors if needed)
        try:
            driver.find_element(By.NAME, "fromDate").send_keys(from_date)
            driver.find_element(By.NAME, "toDate").send_keys(to_date)
            driver.find_element(By.NAME, "storeId").send_keys(store_id)
        except:
            status_callback("⚠️ Could not fill date/store fields. Adjust selectors.")

        # 3. Load Excel
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active

        matches_found = 0
        row = 2
        while ws[f"A{row}"].value:
            search_value = str(ws[f"A{row}"].value).strip()
            match_value = str(ws[f"B{row}"].value).strip() if ws[f"B{row}"].value else ""

            status_callback(f"Searching row {row}: {search_value}")

            # Enter search value
            for sel in CONFIG["selectors"]["search_input"]:
                try:
                    box = driver.find_element(By.CSS_SELECTOR, sel)
                    box.clear()
                    box.send_keys(search_value)
                    break
                except:
                    pass

            # Click search button
            for sel in CONFIG["selectors"]["search_button"]:
                try:
                    driver.find_element(By.CSS_SELECTOR, sel).click()
                    break
                except:
                    pass
            time.sleep(2)

            found = False

            # First attempt: table results
            try:
                table = driver.find_element(By.CSS_SELECTOR, CONFIG["selectors"]["datatable"][0])
                rows = table.find_elements(By.TAG_NAME, "tr")
                for i, tr in enumerate(rows, start=1):
                    if match_value and match_value in tr.text:
                        selector = f"#datatable > tbody > tr:nth-child({i}) > td:nth-child(1) > a"
                        ws[f"C{row}"] = selector
                        ws[f"D{row}"] = "MATCH"
                        matches_found += 1
                        found = True
                        break
            except:
                pass

            # Second attempt: fallback Ctrl+F search
            if not found:
                try:
                    body_text = driver.find_element(By.TAG_NAME, "body").text
                    occurrences = [p for p in body_text.split("\n") if search_value.lower() in p.lower()]
                    if occurrences:
                        for idx, occ in enumerate(occurrences[:max_fallback_results], start=1):
                            ws[f"C{row}"] = f"Fallback result {idx}: {occ[:50]}..."
                        ws[f"D{row}"] = f"FALLBACK {len(occurrences[:max_fallback_results])} results"
                        matches_found += len(occurrences[:max_fallback_results])
                        found = True
                except:
                    pass

            if not found:
                ws[f"D{row}"] = "NOT FOUND"

            # Stop condition if enough matches are caught
            if stop_after_matches and matches_found >= stop_after_matches:
                status_callback(f"🛑 Stopped early after {matches_found} matches.")
                break

            row += 1

        # Save Excel output
        if not output_path:
            output_path = os.path.join(os.path.dirname(excel_path), "output.xlsx")
        wb.save(output_path)
        status_callback(f"✅ Done. Results saved to {output_path}")
        driver.quit()

    except Exception as e:
        status_callback(f"❌ Fatal error: {e}")


# ------------------ GUI ------------------
def main():
    def choose_file():
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        excel_path_var.set(path)

    def choose_output():
        path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                            filetypes=[("Excel files", "*.xlsx")],
                                            initialfile="output.xlsx")
        if path:
            output_path_var.set(path)

    def start_scraper():
        if not excel_path_var.get():
            messagebox.showerror("Error", "Please select an Excel file")
            return

        try:
            max_fallback_results = int(max_fallback_var.get())
        except:
            max_fallback_results = 30

        try:
            stop_after_matches = int(stop_after_var.get()) if stop_after_var.get() else None
        except:
            stop_after_matches = None

        threading.Thread(
            target=run_scraper,
            args=(
                from_date_var.get(),
                to_date_var.get(),
                store_id_var.get(),
                excel_path_var.get(),
                output_path_var.get(),
                max_fallback_results,
                stop_after_matches,
                lambda msg: status_var.set(msg)
            ),
            daemon=True
        ).start()

    root = tk.Tk()
    root.title("Portal Scraper Tool")
    root.geometry("520x450")

    tk.Label(root, text="From Date (MM/DD/YY):").pack()
    from_date_var = tk.StringVar(value="8/1/19")
    tk.Entry(root, textvariable=from_date_var).pack()

    tk.Label(root, text="To Date (MM/DD/YY):").pack()
    to_date_var = tk.StringVar(value="8/23/25")
    tk.Entry(root, textvariable=to_date_var).pack()

    tk.Label(root, text="Store ID:").pack()
    store_id_var = tk.StringVar(value="31001")
    tk.Entry(root, textvariable=store_id_var).pack()

    tk.Label(root, text="Excel File:").pack()
    excel_path_var = tk.StringVar()
    tk.Entry(root, textvariable=excel_path_var, width=40).pack()
    tk.Button(root, text="Browse", command=choose_file).pack()

    tk.Label(root, text="Save Output As:").pack()
    output_path_var = tk.StringVar()
    tk.Entry(root, textvariable=output_path_var, width=40).pack()
    tk.Button(root, text="Browse", command=choose_output).pack()

    tk.Label(root, text="Max Fallback Results (default 30):").pack()
    max_fallback_var = tk.StringVar(value="30")
    tk.Entry(root, textvariable=max_fallback_var).pack()

    tk.Label(root, text="Stop After Matches (leave blank = no stop):").pack()
    stop_after_var = tk.StringVar()
    tk.Entry(root, textvariable=stop_after_var).pack()

    tk.Button(root, text="Run Scraper", command=start_scraper).pack(pady=10)

    status_var = tk.StringVar(value="Idle")
    tk.Label(root, textvariable=status_var, fg="blue").pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
