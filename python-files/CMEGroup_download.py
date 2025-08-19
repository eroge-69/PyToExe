from datetime import date, timedelta
from shutil import move
import os
from time import sleep
from tkinter import Tk, Label, Button, Scrollbar, Listbox, VERTICAL, RIGHT, END, Y
from selenium import webdriver
from selenium.webdriver.chrome.options import Options



def get_todays_date():
    today = date.today()
    weekday = today.weekday()
    if weekday == 0 or weekday == 6:
        print("No files to download")
        exit()

    return (today - timedelta(days=1))



def show_error_message(error_message):
    root = Tk()
    root.title("Error")

    root.geometry("500x300")
    
    label = Label(root, text=error_message, padx=20, pady=20)
    label.pack(expand=True)

    button = Button(root, text="OK", command=root.destroy, padx=10, pady=5)
    button.pack(pady=10)

    root.mainloop()



def has_temp_files(path):
    for file in os.listdir(path):
        if file.endswith(".crdownload") or file.endswith(".tmp"):
            return True
    return False



def has_digit(s):
    digits = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    for c in s:
        if c in digits:
            return True
    return False



def only_digits(s):
    s_to_return = ""
    for c in s:
        if c.isdigit():
            s_to_return += c
    return int(s_to_return)



def get_old_files(directory):
    days = 90
    cutoff_date = date.today() - timedelta(days=days)
    old_files = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_mod_date = date.fromtimestamp(os.path.getmtime(file_path))
            if file_mod_date < cutoff_date:
                days_past = (date.today() - file_mod_date).days
                old_files.append((filename, file_mod_date.strftime("%Y-%m-%d"), days_past))
    return old_files



def confirm_delete(files_to_delete, directory):
    window = Tk()
    window.geometry("640x480")
    window.title("Confirm File Deletion")

    scrollbar = Scrollbar(window, orient=VERTICAL)

    file_list = Listbox(window, width=90, height=22)
    file_list.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=file_list.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    for filename, date, days_past in files_to_delete:
        file_list.insert(END, f"{date} -  {days_past} days   |   {filename}")
    file_list.pack(pady=3)

    def delete_files():
        for filename, _, _ in files_to_delete:
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
            except (OSError, PermissionError) as e:
                show_error_message(f"Error. Failed to delete {file_path}: {e}")
        window.destroy()
    
    def cancel():
        window.destroy()

    delete_button = Button(window, text="Confirm Delete", command=delete_files)
    delete_button.pack(pady=10)

    cancel_button = Button(window, text="Cancel", command=cancel)
    cancel_button.pack(pady=10)

    window.mainloop()



def delete_old_files(directory):
    files_to_delete = get_old_files(directory)
    if files_to_delete:
        confirm_delete(files_to_delete, directory)



options = Options()
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=options)



dirs = ["C:\\Диск Д\\FX CME\\CME_data\\", "C:\\Диск Д\\FX CME\\CME_autodownload\\cme_by_month\\"]

'''for d in dirs:
    if not os.path.exists(d):
        os.makedirs(d)'''

file_names = ["VoiTotalsByAssetClassExcelExport", "VoiDetailsForProduct"]
path = "C:\\Users\\aibek\\Downloads\\"

ids = [['2', '7', '4', '3', '6', '8'], ['AUD', 'CAD', 'EUR', 'GBP', 'JPY', 'Gold', 'Silver', 'Wheat', 'Corn', 'Soybearn', 'S&P', 'Nasdaq', 'CL', 'CHF', 'NZD', 'NG']]

urls = [
    "https://www.cmegroup.com/CmeWS/mvc/VoiTotals/V2/AssetClass/2/export?tradeDate=DATE",
    "https://www.cmegroup.com/CmeWS/mvc/VoiTotals/V2/AssetClass/7/export?tradeDate=DATE",
    "https://www.cmegroup.com/CmeWS/mvc/VoiTotals/V2/AssetClass/4/export?tradeDate=DATE",
    "https://www.cmegroup.com/CmeWS/mvc/VoiTotals/V2/AssetClass/3/export?tradeDate=DATE",
    "https://www.cmegroup.com/CmeWS/mvc/VoiTotals/V2/AssetClass/6/export?tradeDate=DATE",
    "https://www.cmegroup.com/CmeWS/mvc/VoiTotals/V2/AssetClass/8/export?tradeDate=DATE",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=37",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=48",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=58",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=42",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=69",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=437",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=458",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=323",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=300",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=320",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=133",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=146",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=425",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=86",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=78",
    "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=DATE&reportType=P&productId=444"
]

today = ''.join(str(get_todays_date()).split(sep='-'))
for i in range(len(urls)):
    urls[i] = urls[i].replace('DATE', today)

try:
    driver.get("about:blank")
    main_window = driver.current_window_handle
    for url in urls:
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(url)
                driver.close()
                driver.switch_to.window(main_window)

    while has_temp_files(path):
        sleep(1)
        pass

    for i in range(2):
        file_name = file_names[i]
        d = dirs[i]
        id = ids[i]
        required_files = []
        for file in os.listdir(path):
            if file_name in file:
                if not has_digit(file):
                    file_with_added = file.replace('.', ' (0).')
                    os.rename(path+file, path+file_with_added)
                    file = file_with_added
                digits = only_digits(file)
                required_files.append([file, digits])
        for file in required_files:
            if i == 0: new_file_name = file[0].split(' ')[0]+f'_{id[file[1]]}_{today}'+'.xls'
            else: new_file_name = f'{id[file[1]]}_{today}'+'.xls'
            os.rename(path+file[0], path+new_file_name)
            move(path+new_file_name, d+new_file_name)


except:
    show_error_message("Downloading and Moving Error")

finally:
    driver.quit()