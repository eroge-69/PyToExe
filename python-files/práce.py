import webbrowser
import subprocess
import datetime
import os

# Check if today is Tuesday (1) or Thursday (3)
today = datetime.datetime.today().weekday()

if today in [1, 3]:  # 0=Mon, 1=Tue, ..., 6=Sun
    # List of URLs to open in Chrome
    tabs = [
        "https://docs.google.com/spreadsheets/d/1jVtLowvsT3Z25oUxgZpKT_H5QUeDHx7uXGiz27hLo3M/edit?gid=1849387376#gid=1849387376",
        "https://agenda.clickdoc.be/login",
        "https://posta.banan.cz/?_task=mail&_mbox=INBOX"
    ]

    # Path to Chrome (adjust if needed)
    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

    # Open all tabs in Chrome
    for url in tabs:
        webbrowser.get(f'"{chrome_path}" %s').open_new_tab(url)

    # Path to AnyDesk executable (adjust as necessary)
    anydesk_path = "C:\\Program Files (x86)\\AnyDesk\\AnyDesk.exe"

    # Launch AnyDesk
    subprocess.Popen([anydesk_path])
