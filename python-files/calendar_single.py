import json
import os
import uuid
from datetime import datetime

FILE_NAME = "storage.json"

def load_events():
    if not os.path.exists(FILE_NAME):
        return []
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        return json.load(f)

def save_events(events):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def add_event(events):
    title = input("輸入行程標題：")
    date = input("輸入日期 (YYYY-MM-DD)：")
    time = input("輸入時間 (HH:MM)：")
    desc = input("輸入說明：")

    event = {
        "id": str(uuid.uuid4()),
        "title": title,
        "date": date,
        "time": time,
        "description": desc
    }
    events.append(event)
    save_events(events)
    print("✅ 行程新增完成！")

def list_events(events):
    if not events:
        print("📭 目前沒有任何行程。")
        return

    for event in events:
        print(f"{event['date']} {event['time']} - {event['title']}")

def main():
    events = load_events()

    while True:
        print("\n📅 行事曆選單")
        print("1. 新增行程")
        print("2. 查看行程")
        print("3. 離開")
        choice = input("請選擇操作：")

        if choice == "1":
            add_event(events)
        elif choice == "2":
            list_events(events)
        elif choice == "3":
            break
        else:
            print("❌ 無效選項，請重新輸入")

if __name__ == "__main__":
    main()
