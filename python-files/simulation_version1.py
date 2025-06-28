# -*- coding: utf-8 -*-
"""
Created on Sat Jun 28 19:10:10 2025

@author: yesun
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd
import math
import random
# 每站 HTP（每人每小時處理量）
htp_per_station = {
    'Pick': 100,
    'Rebatch': 500,
    'Single Pack': 95,
    'Rebin': 460,
    'Multi Pack': 230,
    'HUB': 360,
    'Issue':0,
    'WS':0,
    'Project':0
}
# 單流程順序
single_flow = ['Pick', 'Rebatch', 'Single Pack', 'HUB']
multi_flow = ['Pick', 'Rebatch', 'Rebin', 'Multi Pack', 'HUB']
# 時間列表：08:00 ~ 02:00（共 19 小時）
time_slots = [f"{(8 + i)%24:02d}:00" for i in range(19)]
# 計算每小時人力分配
def compute_labor_per_hour(order_count, single_ratio, fixed_people):
    single_orders = order_count * single_ratio
    multi_orders = order_count * (1 - single_ratio)
    station_workload = {s: 0 for s in htp_per_station}
    for s in single_flow:
        station_workload[s] += single_orders
    for s in multi_flow:
        station_workload[s] += multi_orders
    station_people = {}
    total_people = 0
    for s, workload in station_workload.items():
        htp = htp_per_station[s]
        if s in fixed_people and fixed_people[s] is not None:
            people = fixed_people[s]
        else:
            people = math.ceil(workload / htp)
        station_people[s] = people
        total_people += people
    overall_htp = order_count / total_people if total_people > 0 else 0
    station_people["HTP"] = round(overall_htp, 2)
    return station_people

# 建立主介面
def run_gui():
    window = tk.Tk()
    window.title("每日多時段出貨人力配置工具")
    # 標題欄位
    tk.Label(window, text="時間").grid(row=0, column=0)
    tk.Label(window, text="進單量").grid(row=0, column=1)
    tk.Label(window, text="Single 比例").grid(row=0, column=2)
    # 每小時輸入欄位
    order_entries = []
    ratio_entries = []
    for i, t in enumerate(time_slots):
        tk.Label(window, text=t).grid(row=i + 1, column=0)
        order_entry = tk.Entry(window, width=10)
        ratio_entry = tk.Entry(window, width=10)
        order_entry.insert(0, random.randint(3000,10000))
        ratio_entry.insert(0, "0.35")
        order_entry.grid(row=i + 1, column=1)
        ratio_entry.grid(row=i + 1, column=2)
        order_entries.append(order_entry)
        ratio_entries.append(ratio_entry)
    # 固定人力輸入區
    tk.Label(window, text="站別").grid(row=0, column=4)
    tk.Label(window, text="固定人力（Issue,WS,Project不可空白）").grid(row=0, column=5)
    fixed_entries = {}
    for j, station in enumerate(htp_per_station):
        tk.Label(window, text=station).grid(row=j + 1, column=4)
        entry = tk.Entry(window, width=10)
        entry.grid(row=j + 1, column=5)
        fixed_entries[station] = entry
    # 計算並輸出結果
    output_text = tk.Text(window, width=110, height=25)
    output_text.grid(row=22, columnspan=6)
    def calculate_all():
        output_text.delete('1.0', tk.END)
        # 讀取固定人力輸入
        fixed_input = {}
        for s, entry in fixed_entries.items():
            try:
                fixed_input[s] = int(entry.get())
            except:
                fixed_input[s] = None
        results = []
        for i in range(19):
            try:
                orders = int(order_entries[i].get())
                ratio = float(ratio_entries[i].get())
                per_hour = compute_labor_per_hour(orders, ratio, fixed_input)
                per_hour["時間"] = time_slots[i]
                results.append(per_hour)
            except Exception as e:
                output_text.insert(tk.END, f"[{time_slots[i]}] 錯誤：{e}\n")
        df = pd.DataFrame(results)
        df = df[['時間'] + list(htp_per_station.keys()) + ['HTP']]
        output_text.insert(tk.END, df.to_string(index=False))
    def clear_orders():
        for entry in order_entries:
            entry.delete(0, tk.END)
    def clear_ratios():
        for entry in ratio_entries:
            entry.delete(0,tk.END)
    # 計算按鈕
    tk.Button(window, text="計算每日人力配置", command=calculate_all).grid(row=21, columnspan=10, pady=10)
    tk.Button(window, text='清除進單量', command=clear_orders).grid(row=21, column=1)
    tk.Button(window, text='清除Single比例', command=clear_ratios).grid(row=21, column=2)
    window.mainloop()
run_gui()