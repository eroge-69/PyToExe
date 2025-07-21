
import requests
from bs4 import BeautifulSoup
import csv
import datetime
import random
import tkinter as tk
from tkinter import messagebox
from collections import Counter

# 1. 抓取最近十期六合彩開獎號碼（正選號碼）
def fetch_recent_draws():
    url = "https://marksixinfo.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    draws = []
    for row in soup.select(".result-table tr")[1:11]:  # 抓取前10期
        tds = row.select("td")
        if len(tds) >= 3:
            numbers_text = tds[2].text.strip().split("+")[0].strip()
            numbers = [int(n) for n in numbers_text.split() if n.isdigit()]
            if len(numbers) == 6:
                draws.append(numbers)
    return draws

# 2. 根據熱號與冷號策略預測號碼
def predict_numbers(draws):
    flat = [num for draw in draws for num in draw]
    counter = Counter(flat)
    most_common = [num for num, _ in counter.most_common(4)]
    least_common = [num for num, _ in counter.most_common()[-2:]]
    prediction = sorted(most_common + least_common)
    return prediction

# 3. 模擬開獎（實際應從網站獲取）
def simulate_draw():
    return sorted(random.sample(range(1, 50), 6))

# 4. 比對中獎情況
def check_winnings(predicted, actual):
    matched = set(predicted) & set(actual)
    count = len(matched)
    prize = {
        6: 8000000,
        5: 100000,
        4: 9000,
        3: 300,
        2: 20
    }.get(count, 0)
    return count, prize

# 5. 顯示彈出視窗
def show_popup(predicted, actual, matched, prize):
    root = tk.Tk()
    root.withdraw()
    message = (
        f"預測號碼：{predicted}\n"
        f"實際號碼：{actual}\n"
        f"命中數量：{matched} 個\n"
        f"中獎金額：${prize} 港元"
    )
    messagebox.showinfo("六合彩預測結果", message)

# 主程式流程
def main():
    today = datetime.date.today()
    draws = fetch_recent_draws()
    predicted = predict_numbers(draws)
    actual = simulate_draw()  # 可替換為實際開獎號碼
    matched, prize = check_winnings(predicted, actual)

    # 記錄至 CSV
    with open("lotto_predictor_record.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([today, predicted, actual, matched, prize])

    # 顯示彈出視窗
    show_popup(predicted, actual, matched, prize)

# 執行主程式
if __name__ == "__main__":
    main()
