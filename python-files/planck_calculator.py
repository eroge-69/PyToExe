import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import re

# --- 1. 物理常数和核心计算函数 ---
h = 6.62607015e-34  # 普朗克常数 (J·s)
c = 299792458  # 光速 (m/s)
k_B = 1.380649e-23  # 玻尔兹曼常数 (J/K)


def planck_law(wavelength, temperature):
    """
    根据普朗克定律计算光谱辐射亮度。
    参数 wavelength 单位为米 (m), temperature 单位为开尔文 (K)。
    """
    with np.errstate(divide='ignore', over='ignore', invalid='ignore'):
        exponent = (h * c) / (wavelength * k_B * temperature)
        spectral_radiance = (2 * h * c ** 2) / (wavelength ** 5 * (np.exp(exponent) - 1))
    return np.nan_to_num(spectral_radiance)


# --- 2. GUI 主应用类 ---
class PlanckCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("普朗克定律计算器")
        self.root.geometry("500x550")  # 设置一个合适的初始窗口大小

        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 输入控件 ---
        controls_frame = ttk.LabelFrame(main_frame, text="输入参数", padding="10")
        controls_frame.pack(fill=tk.X, expand=False)

        # 温度输入
        temp_frame = ttk.Frame(controls_frame)
        temp_frame.pack(fill=tk.X, pady=5)
        ttk.Label(temp_frame, text="温度 (K):", width=15).pack(side=tk.LEFT, padx=5)
        self.temp_var = tk.StringVar(value="5800")
        ttk.Entry(temp_frame, textvariable=self.temp_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 波长输入
        wl_frame = ttk.Frame(controls_frame)
        wl_frame.pack(fill=tk.X, pady=5)
        ttk.Label(wl_frame, text="波长列表 (nm):", width=15).pack(side=tk.LEFT, anchor='n', padx=5, pady=5)

        # 使用带滚动条的文本框让输入更方便
        self.wl_input_text = scrolledtext.ScrolledText(wl_frame, height=5, wrap=tk.WORD)
        self.wl_input_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.wl_input_text.insert(tk.END, "400 550 700 1550")  # 示例输入

        # 提示标签
        ttk.Label(controls_frame, text="提示：请用空格、逗号或换行分隔多个波长值。", foreground="gray").pack(fill=tk.X,
                                                                                                          pady=(0, 10))

        # 计算按钮
        self.calc_button = ttk.Button(controls_frame, text="开始计算", command=self.calculate_data)
        self.calc_button.pack(pady=10)

        # --- 输出区域 ---
        results_frame = ttk.LabelFrame(main_frame, text="计算结果", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # 使用带滚动条的只读文本框显示结果
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, wrap=tk.WORD, state='disabled')
        self.results_text.pack(fill=tk.BOTH, expand=True)

    def calculate_data(self):
        try:
            # 1. 获取并验证温度
            temp_str = self.temp_var.get()
            if not temp_str:
                messagebox.showerror("输入错误", "请输入温度值！")
                return
            temp = float(temp_str)
            if temp <= 0:
                messagebox.showerror("输入错误", "温度必须是大于零的正数。")
                return

            # 2. 获取并解析波长列表
            wl_string = self.wl_input_text.get("1.0", tk.END)
            if not wl_string.strip():
                messagebox.showerror("输入错误", "请输入至少一个波长值！")
                return

            # 使用正则表达式分隔数字，可以处理空格、逗号、换行等多种情况
            wl_values_str = re.split(r'[\s,;\n]+', wl_string)

            wavelengths_nm = []
            for val in wl_values_str:
                if val.strip():  # 确保不是空字符串
                    wavelengths_nm.append(float(val.strip()))

            if not wavelengths_nm:
                messagebox.showerror("输入错误", "未能从输入中解析出有效的波长数值。")
                return

            # 3. 清空并准备显示结果
            self.results_text.config(state='normal')  # 允许编辑以插入内容
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, f"在温度 T = {temp} K 下的计算结果:\n")
            self.results_text.insert(tk.END, "-" * 40 + "\n\n")

            # 4. 循环计算并显示
            for wl_nm in wavelengths_nm:
                if wl_nm <= 0:
                    result_line = f"波长: {wl_nm:<10.2f} nm  ->  错误：波长必须为正数\n"
                else:
                    wl_m = wl_nm * 1e-9  # 转换为米
                    radiance = planck_law(wl_m, temp)
                    # 使用科学记数法格式化输出
                    result_line = f"波长: {wl_nm:<10.2f} nm  ->  光谱辐射亮度: {radiance:.4e} W·sr⁻¹·m⁻³\n"

                self.results_text.insert(tk.END, result_line)

            self.results_text.config(state='disabled')  # 计算完毕，设为只读

        except ValueError:
            messagebox.showerror("输入错误", "输入无效！请确保温度和所有波长都是有效的数字。")
        except Exception as e:
            messagebox.showerror("发生错误", f"发生未知错误: {e}")


# --- 3. 启动应用 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PlanckCalculatorApp(root)
    root.mainloop()