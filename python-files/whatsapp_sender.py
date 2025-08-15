import PySimpleGUI as sg
import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.chrome.options import Options

# GUI Theme
sg.theme("SystemDefault")

layout = [
    [sg.Text("Select Excel File:"), sg.Input(key="-FILE-"), sg.FileBrowse(file_types=(("Excel Files", "*.xlsx"),))],
    [sg.Button("Start Sending", key="-START-", disabled=True), sg.Button("Exit")],
    [sg.Multiline(size=(80, 20), key="-LOG-", autoscroll=True)]
]
window = sg.Window("WhatsApp File Sender", layout)
excel_data = None

def log(msg):
    window["-LOG-"].print(msg)

while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break

    # Load Excel when file is chosen
    if values["-FILE-"] and excel_data is None:
        try:
            excel_data = pd.read_excel(values["-FILE-"])
            if not all(col in excel_data.columns for col in ["Phone", "Message", "FilePath"]):
                sg.popup_error("Excel must have columns: Phone, Message, FilePath")
                excel_data = None
            else:
                log("Excel loaded successfully.")
                window["-START-"].update(disabled=False)
        except Exception as e:
            sg.popup_error(f"Error reading Excel: {e}")

    if event == "-START-":
        sg.popup("Ensure Chrome with WhatsApp Web is open (already logged in).")
        chrome_opts = Options()
        chrome_opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=chrome_opts)

        for idx, row in excel_data.iterrows():
            phone = str(row["Phone"]).strip()
            message = str(row["Message"])
            filepath = str(row["FilePath"]).strip()

            if not os.path.exists(filepath):
                log(f"Row {idx+2}: File not found -> {filepath}")
                excel_data.loc[idx, "Status"] = "Failed - File Missing"
                continue

            try:
                driver.get(f"https://web.whatsapp.com/send?phone={phone}&text={message}")
                time.sleep(3)

                attach_btn = driver.find_element(By.CSS_SELECTOR, "span[data-icon='clip']")
                attach_btn.click()
                time.sleep(1)

                file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                file_input.send_keys(filepath)
                time.sleep(2)

                send_btn = driver.find_element(By.CSS_SELECTOR, "span[data-icon='send']")
                send_btn.click()
                time.sleep(3)

                excel_data.loc[idx, "Status"] = "Sent"
                excel_data.loc[idx, "LastSent"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log(f"Row {idx+2}: Sent to {phone}")

            except Exception as e:
                log(f"Row {idx+2}: Failed -> {e}")
                excel_data.loc[idx, "Status"] = "Failed"

        excel_data.to_excel(values["-FILE-"], index=False)
        sg.popup("Process Completed!")

window.close()
