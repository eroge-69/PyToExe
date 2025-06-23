import time
import sys

def loading_bar(iterations, bar_length=50):
    """
    Hiển thị một thanh loading động.
    
    Args:
        iterations (int): Tổng số bước lặp (tải xong khi lặp hết).
        bar_length (int): Độ dài của thanh loading.
    """
    for i in range(iterations + 1):
        # Tính toán phần trăm hoàn thành
        percent = 100.0 * i / iterations
        
        # Tính toán số lượng ký tự "█" cần hiển thị
        filled_length = int(bar_length * i // iterations)
        
        # Tạo chuỗi thanh loading
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        # In thanh loading và phần trăm ra màn hình
        # \r di chuyển con trỏ về đầu dòng để lần in tiếp theo ghi đè lên
        sys.stdout.write(f'Đang tải |{bar}| {percent:.1f}% \r')
        sys.stdout.flush() # Đảm bảo nội dung được in ra ngay lập tức
        
        # Giả lập công việc đang được thực hiện
        time.sleep(0.02)

while True:
    try:
        # Yêu cầu người dùng nhập và thử chuyển đổi sang số nguyên
        Server = int(input("Bạn chọn máy chủ nào? (1, 2, 3): "))

        # Kiểm tra xem số nhập vào có phải là 1, 2, hoặc 3 không
        if Server in [1, 2, 3]:
            # Nếu là lựa chọn hợp lệ, thoát khỏi vòng lặp
            break
        else:
            # Nếu là số nhưng không hợp lệ, in thông báo
            print("Lựa chọn không hợp lệ. Vui lòng chỉ chọn 1, 2, hoặc 3.")

    except ValueError:
        # Nếu người dùng nhập vào không phải là số, in thông báo lỗi
        print("Bạn đã nhập sai, vui lòng chỉ nhập số (1, 2, 3).")

# Sau khi thoát khỏi vòng lặp, biến Server chắc chắn là một lựa chọn hợp lệ
# Sử dụng f-string để in code gọn hơn và gán biến PlayerServer
if Server == 1:
    print("Bạn đã chọn máy chủ 1.")
    PlayerServer = 1
elif Server == 2:
    print("Bạn đã chọn máy chủ 2.")
    PlayerServer = 2
elif Server == 3:
    print("Bạn đã chọn máy chủ 3.")
    PlayerServer = 3

print(f"Đang kết nối đến máy chủ {Server}...")
loading_bar(150)
print(f"\nĐã kết nối thành công đến máy chủ {Server}!")


# Giờ bạn có thể sử dụng biến PlayerServer cho các tác vụ tiếp theo
# print(f"Biến PlayerServer đã được đặt thành: {PlayerServer}")