import keyboard
import time

def automate_sequence():
    """
    Chương trình 1:
    Gửi một chuỗi tổ hợp phím phức tạp với độ trễ giữa các phím.
    """
    sequence = [
        '0',
        'backspace',
        'backspace',
        'backspace',
        '0',
        'tab',
        'backspace',
        '0',
        'tab',
        'backspace',
        '1',
        'tab',
        'backspace',
        '1',
        'tab',
        'backspace',
        '2',
        'tab',
        'backspace',
        '2'
    ]

    for key in sequence:
        keyboard.press_and_release(key)
        time.sleep(0.075)

def enter_sequence():
    """
    Chương trình 0:
    Gửi chuỗi phím: 0 → Enter → Enter → Enter, mỗi lần cách nhau 0.1s.
    """
    sequence = [
        '0',
        'backspace',
        'backspace',
        'backspace',
        '0',
        'enter',
        'enter',
        'enter',
    ]

    for key in sequence:
        keyboard.press_and_release(key)
        time.sleep(0.075)

def main():
    # Đăng ký các phím tắt
    keyboard.add_hotkey('ctrl+shift+alt+a', automate_sequence)
    keyboard.add_hotkey('alt+q', enter_sequence)

    print("=== Auto Key Tool ===")
    print("[✓] Ctrl + Shift + Alt + A → Chạy chương trình 1 (chuỗi phím phức tạp)")
    print("[✓] Ctrl + Shift + Alt + Q → Chạy chương trình 0 (0 + Enter x3)")
    print("[✕] Nhấn ESC để thoát chương trình.")
    
    keyboard.wait('esc')
    print("Đã thoát chương trình.")

if __name__ == "__main__":
    main()
