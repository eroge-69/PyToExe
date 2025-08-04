
import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
import time
import pandas as pd

def start_scraping():
    try:
        options = Options()
        options.headless = False
        driver = webdriver.Firefox(options=options)
        driver.get("https://sec.kerala.gov.in/public/voters/list")

        time.sleep(2)

        Select(driver.find_element("id", "district")).select_by_index(1)
        time.sleep(1)
        Select(driver.find_element("id", "ac")).select_by_index(1)
        time.sleep(1)
        Select(driver.find_element("id", "part")).select_by_index(1)
        time.sleep(1)
        Select(driver.find_element("id", "language")).select_by_index(1)
        time.sleep(1)

        driver.find_element("id", "submitbtn").click()
        time.sleep(5)

        table = driver.find_element("xpath", "//table")
        rows = table.find_elements("tag name", "tr")

        data = []
        for row in rows:
            cols = row.find_elements("tag name", "td")
            data.append([col.text for col in cols])

        df = pd.DataFrame(data)
        df.to_excel("voter_data.xlsx", index=False)
        messagebox.showinfo("Success", "Data saved to voter_data.xlsx")
        driver.quit()
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Voter List Downloader")

ttk.Label(root, text="Click below to download data").pack(pady=10)
ttk.Button(root, text="Start", command=start_scraping).pack(pady=5)

root.mainloop()
