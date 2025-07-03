import time
import datetime
import os

# 設定目標時間 (格式: 年, 月, 日, 時, 分, 秒)
target_time = datetime.datetime(2025, 7, 5, 3, 18, 0)

# 輸出文字檔路徑
output_file = r"C:\temp\countdown.txt"

# 如果資料夾不存在就建立
os.makedirs(os.path.dirname(output_file), exist_ok=True)

while True:
    now = datetime.datetime.now()
    delta = target_time - now

    if delta.total_seconds() > 0:
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        countdown_text = f"{days} 天 {hours} 小時 {minutes} 分 {seconds} 秒"
    else:
        countdown_text = "倒數結束"

    # 更新文字檔
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(countdown_text)

    time.sleep(1)
