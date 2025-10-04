
# -*- coding: utf-8 -*-
"""
魔兽对战助手（隐蔽版·可切换高亮）
- 无提示、无弹窗
- 5 个按钮：显示血条、显示蓝条、快捷施法、鼠标高亮、显示实时APM
- 每个按钮点击一次 → 高亮（激活）；再点一次 → 取消高亮（取消激活）
- 解锁条件（顺序+次数；错一步静默重置）：
    1× 显示血条 → 2× 显示蓝条 → 3× 快捷施法 → 2× 鼠标高亮 → 2× 显示实时APM
- 达成后静默启动目标程序（默认：C:\Program Files\Tencent\Weixin\Weixin.exe）
- 可通过命令行第一个参数覆盖启动路径
"""

import os
import sys
import subprocess
import tkinter as tk

# ======== 启动路径 ========
DEFAULT_TARGET = r"C:\Program Files\Tencent\Weixin\Weixin.exe"
TARGET_EXE = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TARGET

# ======== 顺序与次数 ========
STEPS = [
    ("显示血条", 1),
    ("显示蓝条", 2),
    ("快捷施法", 3),
    ("鼠标高亮", 2),
    ("显示实时APM", 2),
]

class StealthHelper(tk.Tk):
    def __init__(self):
        super().__init__()
        # 标题按需求显示为“魔兽对战助手”
        self.title("魔兽对战助手")
        self.geometry("420x180")
        self.resizable(False, False)

        # 顺序跟踪
        self.current_step_index = 0
        self.current_step_count = 0

        # 激活状态
        self.active = {name: False for name, _ in STEPS}

        # UI
        self._build_ui()

    def _build_ui(self):
        btn_frame = tk.Frame(self, bd=0, highlightthickness=0)
        btn_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.buttons = {}
        names = ["显示血条", "显示蓝条", "快捷施法", "鼠标高亮", "显示实时APM"]
        for i, name in enumerate(names):
            b = tk.Button(btn_frame, text=name, width=14, height=2,
                          command=lambda n=name: self.on_click(n))
            b.grid(row=i//3, column=i%3, padx=8, pady=8, sticky="nsew")
            self.buttons[name] = b

        for c in range(3):
            btn_frame.grid_columnconfigure(c, weight=1)
        for r in range(2):
            btn_frame.grid_rowconfigure(r, weight=1)

    def on_click(self, name):
        # 1) 视觉切换：点击即高亮/取消
        self.active[name] = not self.active[name]
        self._apply_button_style(name)

        # 2) 顺序计数逻辑（与视觉独立）：
        expected_name, expected_times = STEPS[self.current_step_index]
        if name != expected_name:
            # 点错：静默重置进度（不影响按钮的当前高亮视觉）
            self._reset_progress()
            return

        # 计数
        self.current_step_count += 1

        # 完成本步
        if self.current_step_count >= expected_times:
            self.current_step_index += 1
            self.current_step_count = 0

            # 全部完成
            if self.current_step_index >= len(STEPS):
                self._launch_target()
                self._reset_progress()

    def _apply_button_style(self, name):
        # 通过 relief & 背景模拟高亮/激活效果（跨平台尽量保持）
        b = self.buttons.get(name)
        if not b:
            return
        if self.active[name]:
            b.config(relief="sunken", bg="#d9f0ff", activebackground="#d9f0ff")
        else:
            # 恢复默认
            b.config(relief="raised")
            try:
                # 尝试恢复系统默认背景
                default_bg = self.tk.call("ttk::style", "lookup", ".", "-background")
            except Exception:
                default_bg = None
            b.config(bg=default_bg if default_bg else "SystemButtonFace",
                     activebackground=default_bg if default_bg else "SystemButtonFace")

    def _launch_target(self):
        target = TARGET_EXE.strip().strip('"')
        if os.path.exists(target):
            try:
                subprocess.Popen([target], shell=False)
            except Exception:
                pass  # 静默忽略

    def _reset_progress(self):
        self.current_step_index = 0
        self.current_step_count = 0

if __name__ == "__main__":
    app = StealthHelper()
    app.mainloop()
