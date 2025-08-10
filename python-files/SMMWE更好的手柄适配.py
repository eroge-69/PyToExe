import pygame
import time
import sys
from pynput.mouse import Button, Controller
from pynput.keyboard import Controller as KeyboardController, Key

# 初始化鼠标和键盘控制器
mouse = Controller()
keyboard = KeyboardController()

# 初始化pygame
pygame.init()

# 检测手柄
if pygame.joystick.get_count() == 0:
    print("未检测到手柄，请连接手柄后重试")
    exit()

# 初始化第一个手柄
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"已连接手柄: {joystick.get_name()}")

# 根据映射图定义按钮索引
# 主要按钮
A_BUTTON = 0     # B按钮
B_BUTTON = 1     # A按钮
X_BUTTON = 3     # X按钮
Y_BUTTON = 2     # Y按钮

# 肩键和扳机键
L_BUTTON = 10     # R按钮
ZL_BUTTON = 123    # ZL按钮
R_BUTTON = 9     # L按钮
ZR_BUTTON = 5    # ZR按钮

# 功能按钮
MINUS_BUTTON = 4   # -按钮
PLUS_BUTTON = 6    # +按钮
HOME_BUTTON = 5   # Home按钮
CAPTURE_BUTTON = 15  # 截图按钮

# 方向键
DPAD_UP = 11       # 上
DPAD_DOWN = 12     # 下
DPAD_RIGHT = 14    # 右
DPAD_LEFT = 13     # 左

# 摇杆设置
LEFT_STICK_X = 0  # 左摇杆X轴
LEFT_STICK_Y = 1  # 左摇杆Y轴
RIGHT_STICK_X = 2  # 右摇杆X轴
RIGHT_STICK_Y = 3  # 右摇杆Y轴

INNER_DEADZONE = 0.2  # 内死区阈值
OUTER_DEADZONE = 0.9  # 外死区阈值
SCROLL_DEADZONE = 0.3  # 滚轮死区阈值
DEFAULT_SENSITIVITY = 10  # 默认鼠标移动灵敏度
FAST_SENSITIVITY = 16.5  # 快速移动灵敏度
SCROLL_SENSITIVITY = 0.5  # 滚轮滚动灵敏度

current_sensitivity = DEFAULT_SENSITIVITY  # 当前灵敏度

# 获取屏幕尺寸
try:
    import tkinter as tk
    root = tk.Tk()
    SCREEN_WIDTH = root.winfo_screenwidth()
    SCREEN_HEIGHT = root.winfo_screenheight()
    root.destroy()
except:
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    print(f"警告: 使用默认屏幕尺寸 {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

print(f"屏幕分辨率: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
print(f"默认鼠标灵敏度: {DEFAULT_SENSITIVITY}")
print(f"快速鼠标灵敏度: {FAST_SENSITIVITY}")
print(f"滚轮灵敏度: {SCROLL_SENSITIVITY}")
print(f"内死区阈值: {INNER_DEADZONE} (防止轻微偏移)")
print(f"外死区阈值: {OUTER_DEADZONE} (确保推到边缘才响应)")
print(f"滚轮死区阈值: {SCROLL_DEADZONE} (防止滚轮误触发)")

# 状态跟踪
mouse_pressed = False
r_button_pressed = False  # R按钮状态
dpad_states = {
    DPAD_UP: False,
    DPAD_DOWN: False,
    DPAD_LEFT: False,
    DPAD_RIGHT: False
}
key_states = {}  # 跟踪按键状态

# 摇杆值缩放函数


def scale_joystick_value(value, inner_deadzone, outer_deadzone):
    """
    缩放摇杆值，解决内外死区问题
    - 内死区：防止摇杆轻微偏移
    - 外死区：确保摇杆推到边缘才响应
    """
    abs_value = abs(value)
    sign = 1 if value >= 0 else -1

    # 在内死区范围内，返回0
    if abs_value < inner_deadzone:
        return 0.0

    # 在外死区范围外，返回最大值
    if abs_value > outer_deadzone:
        return sign * 1.0

    # 在死区之间，进行线性缩放
    return sign * ((abs_value - inner_deadzone) / (outer_deadzone - inner_deadzone))

# 模拟键盘按键


def press_key(button, key):
    if button not in key_states or not key_states[button]:
        keyboard.press(key)
        key_states[button] = True
        print(f"按下键盘按键: {key}")


def release_key(button, key):
    if button in key_states and key_states[button]:
        keyboard.release(key)
        key_states[button] = False
        print(f"释放键盘按键: {key}")


try:
    print("--------------------------")
    print("程序已启动。按Home按钮退出")
    print("功能说明:")
    print("  - 左摇杆: 控制鼠标移动")
    print("  - 右摇杆: 控制鼠标滚轮")
    print("  - A按钮: 鼠标左键")
    print("  - R按钮: 快速鼠标移动")
    print("  - 方向键: 键盘方向键")
    print("  - B按钮: 键盘Z键")
    print("  - X/Y按钮: 键盘X键")
    print("  - ZL/ZR/L按钮: 键盘Shift键")
    print("  - +/-按钮: 键盘Enter键")
    print("  - Home按钮: 退出程序")
    print("BY: muyuyv")
    print("--------------------------")

    # 初始化事件处理
    pygame.event.set_allowed(
        [pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYAXISMOTION])

    # 初始化滚轮状态
    last_scroll_time = time.time()
    scroll_cooldown = 0.1  # 滚轮滚动冷却时间（秒）

    while True:
        current_time = time.time()

        # 处理事件
        for event in pygame.event.get():
            # 手柄按钮事件
            if event.type == pygame.JOYBUTTONDOWN:
                # A按钮按下 - 鼠标左键
                if event.button == A_BUTTON:
                    mouse.press(Button.left)
                    mouse_pressed = True
                    print("鼠标左键按下")

                # R按钮按下 - 快速鼠标移动
                elif event.button == R_BUTTON:
                    r_button_pressed = True
                    current_sensitivity = FAST_SENSITIVITY
                    print(f"R键按下，鼠标灵敏度设置为: {current_sensitivity}")

                # Home按钮退出
                elif event.button == HOME_BUTTON:
                    print("退出程序")
                    pygame.quit()
                    sys.exit()

                # B按钮按下 - 键盘Z键
                elif event.button == B_BUTTON:
                    press_key(B_BUTTON, 'z')

                # X按钮按下 - 键盘X键
                elif event.button == X_BUTTON:
                    press_key(X_BUTTON, 'x')

                # Y按钮按下 - 键盘X键
                elif event.button == Y_BUTTON:
                    press_key(Y_BUTTON, 'x')

                # ZL按钮按下 - 键盘Shift键
                elif event.button == ZL_BUTTON:
                    press_key(ZL_BUTTON, Key.shift)

                # ZR按钮按下 - 键盘Shift键
                elif event.button == ZR_BUTTON:
                    press_key(ZR_BUTTON, Key.shift)

                # L按钮按下 - 键盘Shift键
                elif event.button == L_BUTTON:
                    press_key(L_BUTTON, Key.shift)

                # -按钮按下 - 键盘Enter键
                elif event.button == MINUS_BUTTON:
                    press_key(MINUS_BUTTON, Key.enter)

                # +按钮按下 - 键盘Enter键
                elif event.button == PLUS_BUTTON:
                    press_key(PLUS_BUTTON, Key.enter)

                # 方向键按下 - 键盘方向键
                elif event.button == DPAD_UP:
                    dpad_states[DPAD_UP] = True
                    press_key(DPAD_UP, Key.up)

                elif event.button == DPAD_DOWN:
                    dpad_states[DPAD_DOWN] = True
                    press_key(DPAD_DOWN, Key.down)

                elif event.button == DPAD_LEFT:
                    dpad_states[DPAD_LEFT] = True
                    press_key(DPAD_LEFT, Key.left)

                elif event.button == DPAD_RIGHT:
                    dpad_states[DPAD_RIGHT] = True
                    press_key(DPAD_RIGHT, Key.right)

            elif event.type == pygame.JOYBUTTONUP:
                # A按钮释放
                if event.button == A_BUTTON:
                    mouse.release(Button.left)
                    mouse_pressed = False
                    print("鼠标左键释放")

                # R按钮释放
                elif event.button == R_BUTTON:
                    r_button_pressed = False
                    current_sensitivity = DEFAULT_SENSITIVITY
                    print(f"R键释放，鼠标灵敏度恢复为: {current_sensitivity}")

                # B按钮释放
                elif event.button == B_BUTTON:
                    release_key(B_BUTTON, 'z')

                # X按钮释放
                elif event.button == X_BUTTON:
                    release_key(X_BUTTON, 'x')

                # Y按钮释放
                elif event.button == Y_BUTTON:
                    release_key(Y_BUTTON, 'x')

                # ZL按钮释放
                elif event.button == ZL_BUTTON:
                    release_key(ZL_BUTTON, Key.shift)

                # ZR按钮释放
                elif event.button == ZR_BUTTON:
                    release_key(ZR_BUTTON, Key.shift)

                # L按钮释放
                elif event.button == L_BUTTON:
                    release_key(L_BUTTON, Key.shift)

                # -按钮释放
                elif event.button == MINUS_BUTTON:
                    release_key(MINUS_BUTTON, Key.enter)

                # +按钮释放
                elif event.button == PLUS_BUTTON:
                    release_key(PLUS_BUTTON, Key.enter)

                # 方向键释放
                elif event.button == DPAD_UP:
                    dpad_states[DPAD_UP] = False
                    release_key(DPAD_UP, Key.up)

                elif event.button == DPAD_DOWN:
                    dpad_states[DPAD_DOWN] = False
                    release_key(DPAD_DOWN, Key.down)

                elif event.button == DPAD_LEFT:
                    dpad_states[DPAD_LEFT] = False
                    release_key(DPAD_LEFT, Key.left)

                elif event.button == DPAD_RIGHT:
                    dpad_states[DPAD_RIGHT] = False
                    release_key(DPAD_RIGHT, Key.right)

        # 获取左摇杆原始值（控制鼠标移动）
        raw_left_x_axis = joystick.get_axis(LEFT_STICK_X)
        raw_left_y_axis = joystick.get_axis(LEFT_STICK_Y)

        # 应用死区缩放
        x_axis = scale_joystick_value(
            raw_left_x_axis, INNER_DEADZONE, OUTER_DEADZONE)
        y_axis = scale_joystick_value(
            raw_left_y_axis, INNER_DEADZONE, OUTER_DEADZONE)

        # 计算鼠标移动距离
        dx = x_axis * current_sensitivity
        dy = y_axis * current_sensitivity

        # 移动鼠标
        if dx != 0 or dy != 0:
            current_x, current_y = mouse.position
            new_x = current_x + dx
            new_y = current_y + dy

            # 限制鼠标在屏幕范围内
            new_x = max(0, min(new_x, SCREEN_WIDTH))
            new_y = max(0, min(new_y, SCREEN_HEIGHT))

            mouse.position = (new_x, new_y)

        # 获取右摇杆原始值（控制滚轮）
        raw_right_y_axis = joystick.get_axis(RIGHT_STICK_Y)

        # 应用滚轮死区过滤
        if abs(raw_right_y_axis) < SCROLL_DEADZONE:
            raw_right_y_axis = 0.0

        # 计算滚轮滚动量（反转方向，向上推是负值，对应向上滚动）
        scroll_amount = -raw_right_y_axis * SCROLL_SENSITIVITY

        # 触发滚轮滚动
        if scroll_amount != 0 and (current_time - last_scroll_time) > scroll_cooldown:
            mouse.scroll(0, scroll_amount)
            last_scroll_time = current_time

        # 降低CPU占用
        time.sleep(0.01)

except KeyboardInterrupt:
    print("程序已手动终止")
except Exception as e:
    print(f"发生错误: {str(e)}")
finally:
    # 释放所有按下的键盘按键
    for button, pressed in key_states.items():
        if pressed:
            # 这里我们不知道具体是哪个键，所以无法释放
            # 在实际应用中，应该记录每个按钮对应的键
            pass
    pygame.quit()
