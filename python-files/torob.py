Python 3.13.3 (tags/v3.13.3:6280bb5, Apr  8 2025, 14:47:33) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import pandas as pd
... import time
... import os
... from selenium import webdriver
... from selenium.webdriver.chrome.service import Service
... from selenium.webdriver.common.by import By
... from selenium.webdriver.chrome.options import Options
... from tkinter import Tk, filedialog
... from datetime import datetime
... 
... def select_file():
...     root = Tk()
...     root.withdraw()
...     file_path = filedialog.askopenfilename(title="فایل CSV را انتخاب کنید", filetypes=[("CSV Files", "*.csv")])
...     return file_path
... 
... def create_driver():
...     chrome_options = Options()
...     chrome_options.add_argument("--headless")
...     chrome_options.add_argument("--no-sandbox")
...     chrome_options.add_argument("--disable-dev-shm-usage")
...     service = Service()
...     driver = webdriver.Chrome(service=service, options=chrome_options)
...     return driver
... 
... def extract_first_seller(driver, url):
...     try:
...         driver.get(url)
...         time.sleep(2)
...         seller_name = driver.find_element(By.CSS_SELECTOR, 'div.ProductSellerList__seller-name span').text
...         return seller_name, url
...     except Exception as e:
...         return "فروشنده پیدا نشد", url
... 
... def main():
    file_path = select_file()
    if not file_path:
        print("فایلی انتخاب نشد.")
        return

    df = pd.read_csv(file_path, encoding='utf-16', sep='\\t')
    result = []

    driver = create_driver()

    for index, row in df.iterrows():
        title = row.get("نام کالا")
        torob_url = row.get("لینک ترب")
        if pd.isna(torob_url):
            result.append([title, "ندارد", "ندارد"])
            continue
        seller_name, link = extract_first_seller(driver, torob_url)
        print(f"{index+1}: {title} - {seller_name}")
        result.append([title, seller_name, link])

    driver.quit()

    output_df = pd.DataFrame(result, columns=["نام کالا", "اولین فروشنده", "لینک"])
    output_name = f"torob_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    output_df.to_excel(output_name, index=False)
    print(f"\\n✅ فایل خروجی ذخیره شد: {output_name}")

if __name__ == "__main__":
    main()
