import sys
import requests
import tkinter as tk
from tkinter import filedialog

def send_file(token, chat_id, file_path):
    url = f'https://api.telegram.org/bot{token}/sendDocument'
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': chat_id}
        response = requests.post(url, files=files, data=data)
    return response.ok

def main():
    if len(sys.argv) < 3:
        print("Usage: python send_files_to_telegram.py <BOT_TOKEN> <CHAT_ID>")
        return

    token = sys.argv[1]
    chat_id = sys.argv[2]

    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select file(s) to send")

    if not file_paths:
        print("No files selected.")
        return

    for path in file_paths:
        success = send_file(token, chat_id, path)
        print(f"{'✅ Sent' if success else '❌ Failed'}: {path}")

if __name__ == '__main__':
    main()
