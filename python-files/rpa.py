# -*- coding: utf-8 -*-
"""
10 步全自动：截图 → OCR 找字 → 点击（部分步骤只识别）
"""
import time
import pyautogui
from cnocr import CnOcr
import cv2
import numpy as np

# ---------------- 1. 配置 ----------------
STEPS = [
    {"txt": "保存",      "click": True},
    {"txt": "保存",      "click": True},
    {"txt": "命名修改",  "click": True},
    {"txt": "保存",      "click": True},
    {"txt": "已修改",    "click": False},   # 第 8 步只识别
    {"txt": "提交",      "click": True},    # 第 9 步
    {"txt": "确定",      "click": True},    # 第 10 步（新增）
]
PAUSE   = 0.5          # 每次点击后暂停
DEBUG   = True         # 是否把每步识别结果画框截图
FAILSAFE = True        # 鼠标移到左上角紧急中断

# ---------------- 2. 初始化 ----------------
ocr = CnOcr()
pyautogui.FAILSAFE = FAILSAFE

# ---------------- 3. 工具函数 ----------------
def screenshot():
    """返回 cnocr 需要的 BGR 数组"""
    img = pyautogui.screenshot()
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def find_center(img, target):
    """返回第一个包含 target 的框中心 (cx, cy)，找不到抛 ValueError"""
    outs = ocr.ocr(img)
    for *box, txt, score in outs:
        if target in txt.replace(" ", ""):   # ← 包含匹配
            xs, ys = zip(*box)
            cx, cy = int(sum(xs) / 4), int(sum(ys) / 4)
            if DEBUG:
                cv2.polylines(img, [np.array(box, np.int32)], True, (0, 0, 255), 2)
                cv2.putText(img, f"{target}:{score:.2f}", (cx - 20, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            return cx, cy
    raise ValueError(f"未找到含【{target}】的文本")

def click_xy(x, y):
    pyautogui.moveTo(x, y, duration=0.2)
    pyautogui.click()

# ---------------- 4. 主流程 ----------------
def main():
    for idx, step in enumerate(STEPS, 1):
        txt, do_click = step["txt"], step["click"]
        print(f"步骤 {idx}: 查找 '{txt}'")
        img = screenshot()
        try:
            cx, cy = find_center(img, txt)
        except ValueError as e:
            print(e)
            if DEBUG:
                cv2.imwrite(f"debug_step{idx}.png", img)
            return          # 找不到就停住，方便调试
        if do_click:
            print(f"  点击 ({cx}, {cy})")
            click_xy(cx, cy)
            time.sleep(PAUSE)
        else:
            print(f"  仅识别，不点击")
        if DEBUG:
            cv2.imwrite(f"debug_step{idx}.png", img)
    print("10 步流程全部完成！")

if __name__ == "__main__":
    main()