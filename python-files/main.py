import tkinter as tk
from tkinter import font, messagebox
import math


# --- 第1部分: 核心计算逻辑 ---

def calculate_queue_length(lambda_rate, t_red, s_flow_rate, t_green):
    """
    计算期望排队长度，并返回中间过程值。
    """
    arrived_vehicles = lambda_rate * t_red
    service_capacity = s_flow_rate * t_green
    queue_length = max(0, arrived_vehicles - service_capacity)
    # 返回最终结果和两个中间值
    return queue_length, arrived_vehicles, service_capacity


def calculate_average_delay(lambda_rate, t_red, s_flow_rate):
    """计算每辆车的平均延误时间"""
    if lambda_rate >= s_flow_rate:
        return float('inf')

    if s_flow_rate == 0 or (1 - (lambda_rate / s_flow_rate)) == 0:
        return float('inf')

    numerator = lambda_rate * (t_red ** 2)
    denominator = 2 * (1 - (lambda_rate / s_flow_rate))
    average_delay = numerator / denominator
    return average_delay


# --- 第2部分: GUI界面功能 ---

def perform_calculation():
    """
    当用户点击按钮时，此函数被调用。
    它从输入框获取数据，执行计算，并更新包含中间过程的结果标签。
    """
    try:
        # 1. 从输入框获取值
        lambda_val = float(entry_lambda.get())
        t_red_val = float(entry_t_red.get())
        t_green_val = float(entry_t_green.get())
        s_val = float(entry_s_flow.get())

        # 2. 调用核心函数进行计算
        # 获取最终排队长度和中间过程值
        queue, arrived, capacity = calculate_queue_length(lambda_val, t_red_val, s_val, t_green_val)
        delay = calculate_average_delay(lambda_val, t_red_val, s_val)

        # 3. 计算额外的中间值：交通饱和度
        if s_val > 0:
            saturation_val = lambda_val / s_val
            saturation_text = f"{saturation_val:.2f} ({saturation_val:.0%})"
        else:
            saturation_text = "无法计算 (s=0)"

        # 4. 格式化最终的、包含所有过程的输出字符串
        # 最终结果
        queue_result_final = f"{math.ceil(queue)} 辆 (精确值: {queue:.2f})"
        if math.isinf(delay):
            delay_result_final = "无穷大 (系统不稳定, λ ≥ s)"
        else:
            delay_result_final = f"{delay:.2f} 秒/辆"

        # 组合所有文本
        full_result_text = (
            f"--- 中间过程 ---\n\n"
            f"红灯期间平均到达车辆数: {arrived:.2f} 辆\n"
            f"绿灯期间可通过车辆数: {capacity:.2f} 辆\n"
            f"交通饱和度 (λ/s): {saturation_text}\n"
            f"\n--- 最终结果 ---\n\n"
            f"预测排队长度 (L): {queue_result_final}\n\n"
            f"平均延误时间 (d): {delay_result_final}"
        )

        # 5. 更新结果显示区的文本
        result_text.set(full_result_text)

    except ValueError:
        messagebox.showerror("输入错误", "所有参数都必须是有效的数字！")
    except Exception as e:
        messagebox.showerror("计算错误", f"发生未知错误: {e}")


# --- 第3部分: 创建和布局GUI窗口 ---

# 初始化主窗口
root = tk.Tk()
root.title("交通模型计算器")
root.geometry("450x480")  # 增加了窗口高度以容纳更多文本
root.resizable(False, False)

# 创建一个主框架
main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(fill="both", expand=True)

# 定义字体
label_font = font.Font(family="Helvetica", size=12)
entry_font = font.Font(family="Helvetica", size=12)
button_font = font.Font(family="Helvetica", size=12, weight="bold")
result_font = font.Font(family="Courier", size=12)  # 使用等宽字体，方便对齐

# --- 输入区 (无变化) ---
input_frame = tk.Frame(main_frame)
input_frame.pack(pady=10)

params = {
    "车辆到达率 λ (辆/秒):": "0.4",
    "饱和流率 s (辆/秒):": "0.5",
    "红灯时长 t_red (秒):": "50",
    "绿灯时长 t_green (秒):": "50",
}

entries = {}
for i, (text, default_val) in enumerate(params.items()):
    label = tk.Label(input_frame, text=text, font=label_font)
    label.grid(row=i, column=0, sticky="w", pady=5, padx=5)

    entry = tk.Entry(input_frame, font=entry_font, width=15)
    entry.grid(row=i, column=1, sticky="e", pady=5, padx=5)
    entry.insert(0, default_val)
    entries[text] = entry

entry_lambda = entries["车辆到达率 λ (辆/秒):"]
entry_s_flow = entries["饱和流率 s (辆/秒):"]
entry_t_red = entries["红灯时长 t_red (秒):"]
entry_t_green = entries["绿灯时长 t_green (秒):"]

# --- 操作按钮 (无变化) ---
calculate_button = tk.Button(
    main_frame, text="运行计算", font=button_font,
    bg="#4CAF50", fg="white", command=perform_calculation
)
calculate_button.pack(pady=20, ipadx=10, ipady=5)

# --- 结果显示区 ---
result_text = tk.StringVar()
result_label = tk.Label(
    main_frame, textvariable=result_text, font=result_font,
    justify="left", bg="#f0f0f0", padx=10, pady=10, wraplength=400
)
result_label.pack(fill="both", expand=True)

result_text.set("请填写参数，然后点击“运行计算”按钮。")

# --- 启动GUI主循环 ---
root.mainloop()