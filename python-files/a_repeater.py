import keyboard
import time
import threading

# 标记是否正在处理按键重复，防止重复触发
is_processing = False

def repeat_a():
    global is_processing
    if is_processing:
        return
    
    is_processing = True
    try:
        # 1秒内重复10次，每次间隔0.1秒
        for _ in range(10):
            # 小延迟确保系统能正确处理每次按键
            time.sleep(0.1)
            keyboard.press_and_release('a')
    finally:
        is_processing = False

# 注册A键热键，触发时调用repeat_a函数
keyboard.add_hotkey('a', repeat_a)

print("A键重复器已启动，按下A键将在1秒内重复10次A键")
print("关闭此窗口即可停止程序")

# 保持程序运行，监听按键事件
keyboard.wait()
