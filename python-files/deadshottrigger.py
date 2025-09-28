import tkinter as tk
from tkinter import colorchooser, ttk
import threading
import time
import pyautogui
import keyboard
import numpy as np

# Cấu hình màu sắc cho giao diện tối (Dark Mode)
BG_PRIMARY = "#1e1e1e"
FG_PRIMARY = "#ffffff"
ACCENT_COLOR = "#00ff7f"  # Màu xanh neon sáng
BTN_NORMAL = "#3a3a3a"
BTN_ACTIVE = "#555555"

class ColorCircleApp:
    """
    Ứng dụng DinoTriggerBot phát hiện màu sắc trên màn hình với vòng tròn overlay.
    Sử dụng multithreading để chạy logic phát hiện màu nền.
    """
    def __init__(self, root):
        self.root = root
        # THAY ĐỔI: Đổi tên ứng dụng
        self.root.title("DinoTriggerBot")
        # THAY ĐỔI: Tăng kích thước cửa sổ để chứa hai checkbox mới
        self.root.geometry("350x720") # Tăng chiều cao để chứa phần Hex mới
        self.root.attributes("-topmost", True)
        # THAY ĐỔI: Sử dụng màu nền tối
        self.root.configure(bg=BG_PRIMARY)
        # THAY ĐỔI: Cho phép thay đổi kích thước cửa sổ (ngang và dọc)
        self.root.resizable(True, True)

        # --- Cấu hình Ban đầu ---
        self.target_color = (255, 68, 68)  # mặc định #ff4444
        # CẬP NHẬT MỚI: Biến lưu trữ mã Hex
        self.hex_code_var = tk.StringVar(value="#ff4444") 
        # Sử dụng StringVar/IntVar/DoubleVar để liên kết trực tiếp với UI
        self.radius = tk.IntVar(value=100)
        self.delay = tk.DoubleVar(value=0.08)
        self.tolerance = tk.IntVar(value=30)
        self.mode_var = tk.StringVar(value="Shotgun (Kích hoạt 1 lần)")
        
        # CHỨC NĂNG MỚI ĐƯỢC TÁCH RỜI
        self.jump_enabled = tk.BooleanVar(value=False)
        self.drag_enabled = tk.BooleanVar(value=False)

        # Sử dụng Event để điều khiển luồng phát hiện màu an toàn (thay thế boolean)
        self.stop_event = threading.Event()
        self.detection_thread = None
        
        # THÊM MỚI: Biến lưu trữ ID của công việc 'after' để có thể hủy
        self._update_circle_job_id = None 

        self._setup_ui()
        self._setup_overlay()
        
        # Đảm bảo luồng dừng khi đóng cửa sổ chính
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_circle() # Bắt đầu vòng lặp cập nhật UI

    def _setup_ui(self):
        """Thiết lập giao diện người dùng chính (Dark Mode) với giao diện nâng cấp."""
        
        # Cài đặt font chung
        HEADER_FONT = ("Arial", 18, "bold")
        LABEL_FONT = ("Arial", 10, "bold")
        
        main_frame = tk.Frame(self.root, padx=20, pady=15, bg=BG_PRIMARY)
        main_frame.pack(fill="both", expand=True)
        
        # Tiêu đề 
        tk.Label(main_frame, text="🦖 DinoTriggerBot", font=HEADER_FONT, bg=BG_PRIMARY, fg=ACCENT_COLOR).pack(pady=(0, 25))

        # --- Khung Cài đặt Màu (Target Settings Frame) ---
        # Sử dụng LabelFrame để nhóm giao diện trực quan hơn
        target_frame = tk.LabelFrame(main_frame, text="CÀI ĐẶT MỤC TIÊU (TARGET)", font=LABEL_FONT, bg=BG_PRIMARY, fg=ACCENT_COLOR, bd=1, relief=tk.SOLID, padx=10, pady=10)
        target_frame.pack(pady=10, fill="x")

        # Khung Chọn Màu và Preview
        color_select_frame = tk.Frame(target_frame, bg=BG_PRIMARY)
        color_select_frame.pack(pady=5, fill="x")
        
        tk.Label(color_select_frame, text="Màu mục tiêu:", bg=BG_PRIMARY, fg=FG_PRIMARY, font=LABEL_FONT).pack(side="left", padx=(0, 10))
        
        # Màu xem trước với border neon
        self.color_preview = tk.Label(color_select_frame, width=3, relief="flat", bg="#ff4444", bd=2, highlightbackground=ACCENT_COLOR, highlightthickness=1)
        self.color_preview.pack(side="left", padx=10)
        
        # Nút Chọn màu
        tk.Button(color_select_frame, text="Chọn màu", command=self.choose_color, 
                  relief="flat", bg=BTN_NORMAL, fg=FG_PRIMARY, activebackground=BTN_ACTIVE, activeforeground=FG_PRIMARY, bd=0, padx=10).pack(side="left")

        # CẬP NHẬT MỚI: Khung nhập mã màu Hex
        hex_frame = tk.Frame(target_frame, bg=BG_PRIMARY)
        hex_frame.pack(pady=(15, 5), fill="x")

        tk.Label(hex_frame, text="Mã Hex (#RRGGBB):", bg=BG_PRIMARY, fg=FG_PRIMARY, font=LABEL_FONT).pack(side="left")
        
        self.hex_entry = tk.Entry(hex_frame, textvariable=self.hex_code_var, width=10, bg=BTN_NORMAL, fg=FG_PRIMARY, insertbackground=ACCENT_COLOR, relief="flat")
        self.hex_entry.pack(side="left", padx=10, fill="x", expand=True)

        tk.Button(hex_frame, text="Áp dụng", command=self.apply_hex_color,
                  relief="flat", bg=ACCENT_COLOR, fg=BG_PRIMARY, activebackground=BTN_ACTIVE, activeforeground=FG_PRIMARY, bd=0, padx=10).pack(side="right")
        # END CẬP NHẬT MỚI
        
        # Thanh trượt Sai số màu (Tolerance)
        tk.Label(target_frame, text="Sai số màu (Tolerance 1-100):", bg=BG_PRIMARY, fg=FG_PRIMARY).pack(pady=(15, 0), anchor="w")
        tk.Scale(target_frame, from_=1, to=100, orient="horizontal", variable=self.tolerance, 
                 bg=BG_PRIMARY, fg=FG_PRIMARY, highlightthickness=0, troughcolor=BTN_NORMAL, activebackground=ACCENT_COLOR, bd=0).pack(fill="x", padx=10)
        self.tolerance.set(30)
        
        # --- Khung Cài đặt Hành động (Action Settings Frame) ---
        action_frame = tk.LabelFrame(main_frame, text="CÀI ĐẶT HÀNH ĐỘNG (ACTION)", font=LABEL_FONT, bg=BG_PRIMARY, fg=ACCENT_COLOR, bd=1, relief=tk.SOLID, padx=10, pady=10)
        action_frame.pack(pady=10, fill="x")

        # Thanh trượt Bán kính
        tk.Label(action_frame, text="Bán kính quét (10-500):", bg=BG_PRIMARY, fg=FG_PRIMARY).pack(pady=(5, 0), anchor="w")
        tk.Scale(action_frame, from_=10, to=500, orient="horizontal", variable=self.radius, 
                 bg=BG_PRIMARY, fg=FG_PRIMARY, highlightthickness=0, troughcolor=BTN_NORMAL, activebackground=ACCENT_COLOR, bd=0).pack(fill="x", padx=10)

        # Thanh trượt Delay
        tk.Label(action_frame, text="Delay quét (giây - 0.01 đến 1.0):", bg=BG_PRIMARY, fg=FG_PRIMARY).pack(pady=(15, 0), anchor="w")
        tk.Scale(action_frame, from_=0.01, to=1, resolution=0.01, orient="horizontal", variable=self.delay, 
                 bg=BG_PRIMARY, fg=FG_PRIMARY, highlightthickness=0, troughcolor=BTN_NORMAL, activebackground=ACCENT_COLOR, bd=0).pack(fill="x", padx=10)

        # Menu Chế độ
        tk.Label(action_frame, text="Chế độ bắn:", bg=BG_PRIMARY, fg=FG_PRIMARY).pack(pady=(15, 5), anchor="w")
        mode_options = ["Shotgun (Kích hoạt 1 lần)", "AR (Giữ phím K)", "Sniper (Giữ phím L & Nhấn K)"]
        
        # Sử dụng OptionMenu và tùy chỉnh
        self.mode_menu = tk.OptionMenu(action_frame, self.mode_var, *mode_options)
        self.mode_menu.config(width=30, bg=BTN_NORMAL, fg=FG_PRIMARY, relief="flat", bd=0,
                              activebackground=BTN_ACTIVE, activeforeground=FG_PRIMARY)
        self.mode_menu["menu"].config(bg=BTN_NORMAL, fg=FG_PRIMARY, activebackground=ACCENT_COLOR, activeforeground=BG_PRIMARY)
        self.mode_menu.pack(pady=5, fill="x")
        
        # --- Khung Tùy chọn Đặc biệt (Feature Checkboxes) ---
        feature_frame = tk.LabelFrame(main_frame, text="TÙY CHỌN ĐẶC BIỆT", font=LABEL_FONT, bg=BG_PRIMARY, fg=ACCENT_COLOR, bd=1, relief=tk.SOLID, padx=10, pady=5)
        feature_frame.pack(pady=10, fill="x")
        
        # CHECKBOX 1 MỚI: Auto Jump
        jump_check = tk.Checkbutton(feature_frame, text="1. Tự động Nhảy (Auto Jump - Space)", variable=self.jump_enabled,
                                    bg=BG_PRIMARY, fg=FG_PRIMARY, selectcolor=BTN_NORMAL, activebackground=BG_PRIMARY,
                                    activeforeground=ACCENT_COLOR, cursor="hand2")
        jump_check.pack(pady=2, anchor="w")

        # CHECKBOX 2 MỚI: Auto Drag
        drag_check = tk.Checkbutton(feature_frame, text="2. Tự động Kéo tâm (Auto Drag - Move Mouse)", variable=self.drag_enabled,
                                    bg=BG_PRIMARY, fg=FG_PRIMARY, selectcolor=BTN_NORMAL, activebackground=BG_PRIMARY,
                                    activeforeground=ACCENT_COLOR, cursor="hand2")
        drag_check.pack(pady=2, anchor="w")
        
        # --- Khung Điều khiển Chính ---
        control_frame = tk.Frame(main_frame, bg=BG_PRIMARY)
        control_frame.pack(pady=10, fill="x")
        
        # Trạng thái
        self.status_label = tk.Label(control_frame, text="Trạng thái: OFF", fg="#ff4444", font=("Arial", 12, "bold"), bg=BG_PRIMARY)
        self.status_label.pack(pady=(15, 5))

        # Nút Bật/Tắt
        self.toggle_btn = tk.Button(control_frame, text="Bật (F6)", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=self.toggle, 
                                    relief="flat", padx=15, pady=8, activebackground="#388e3c", activeforeground="white")
        self.toggle_btn.pack(pady=5, ipadx=30)
        
        # Thiết lập phím tắt
        try:
            keyboard.add_hotkey('f6', self.toggle)
        except Exception as e:
            # Lưu ý: Hotkey có thể không hoạt động trên một số hệ điều hành/quyền hạn
            print(f"Lỗi thiết lập hotkey F6: {e}")


    def _setup_overlay(self):
        """Thiết lập cửa sổ overlay trong suốt cho vòng tròn."""
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes("-transparentcolor", "black")
        self.overlay.attributes("-topmost", True)
        self.overlay.overrideredirect(True)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.overlay.geometry(f"{screen_w}x{screen_h}+0+0")

        self.canvas = tk.Canvas(self.overlay, width=screen_w, height=screen_h, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True) # Đảm bảo canvas lấp đầy overlay
        self.circle = None

    def hex_to_rgb(self, hex_code):
        """Chuyển đổi mã hex (ví dụ: #ff4444) sang tuple RGB."""
        # Loại bỏ ký tự '#' nếu có
        hex_code = hex_code.lstrip('#')
        # Đảm bảo mã có 6 ký tự
        if len(hex_code) != 6:
            raise ValueError("Mã Hex không hợp lệ (cần 6 ký tự).")
            
        # Chuyển đổi từng cặp ký tự sang giá trị thập phân
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
        return (r, g, b)

    def apply_hex_color(self):
        """Áp dụng màu từ mã Hex do người dùng nhập."""
        hex_code = self.hex_code_var.get().strip()
        
        try:
            # Chuyển đổi và cập nhật màu mục tiêu
            rgb_color = self.hex_to_rgb(hex_code)
            self.target_color = rgb_color
            
            # Cập nhật màu xem trước
            # Đảm bảo mã hex có ký tự #
            final_hex = f'#{hex_code.lstrip("#")}' 
            self.color_preview.config(bg=final_hex)
            
            print(f"Đã áp dụng màu mới: {final_hex}")
            
        except ValueError as e:
            # Xử lý lỗi khi mã hex không hợp lệ (Sử dụng print thay vì alert)
            print(f"Lỗi nhập mã màu: {e}. Vui lòng nhập đúng định dạng #RRGGBB hoặc RRGGBB.")
            # Đặt lại màu preview thành màu mặc định để báo hiệu lỗi
            self.color_preview.config(bg="#ff0000") 

    def choose_color(self):
        """Mở hộp thoại chọn màu và cập nhật màu mục tiêu."""
        initial_color = f'#{self.target_color[0]:02x}{self.target_color[1]:02x}{self.target_color[2]:02x}'
        
        color_info = colorchooser.askcolor(title="Chọn màu", initialcolor=initial_color)
        
        if color_info and color_info[0]:
            rgb, hex_code = color_info
            self.target_color = tuple(map(int, rgb))
            self.color_preview.config(bg=hex_code)
            
            # CẬP NHẬT MỚI: Cập nhật biến hex_code_var
            self.hex_code_var.set(hex_code)

    def toggle(self):
        """Bật/Tắt luồng phát hiện màu."""
        if self.detection_thread and self.detection_thread.is_alive() and not self.stop_event.is_set():
            # Đang ở trạng thái BẬT -> Tắt
            self.stop_event.set()
            self.status_label.config(text="Trạng thái: OFF", fg="#ff4444")
            self.toggle_btn.config(text="Bật (F6)", bg="#4CAF50")
            
            # Đảm bảo nhả phím nếu đang giữ
            try:
                if keyboard.is_pressed("k"):
                    keyboard.release("k")
                if keyboard.is_pressed("l"):
                    keyboard.release("l")
            except Exception as e:
                print(f"Lỗi khi nhả phím: {e}")
            
        else: 
            # Đang ở trạng thái TẮT -> Bật
            self.stop_event.clear()
            
            # Cập nhật trạng thái ON chi tiết
            status_text = f"Trạng thái: ON ({self.mode_var.get().split(' ')[0]})"
            if self.drag_enabled.get():
                status_text += " | Drag ON"
            if self.jump_enabled.get():
                status_text += " | Jump ON"
                
            self.status_label.config(text=status_text, fg=ACCENT_COLOR)
            self.toggle_btn.config(text="Tắt (F6)", bg="#f44336")
            
            self.detection_thread = threading.Thread(target=self.run_detection, daemon=True)
            self.detection_thread.start()
            
    def on_closing(self):
        """Xử lý đóng cửa sổ, đảm bảo dừng luồng an toàn."""
        self.stop_event.set()
        
        # FIX LỖI: Hủy công việc after() đang chờ xử lý để tránh lỗi Tcl
        if self._update_circle_job_id:
            try:
                self.root.after_cancel(self._update_circle_job_id)
            except Exception:
                # Bỏ qua nếu lỗi hủy lệnh (ví dụ: đã bị hủy hoặc root đã bị destroy)
                pass 

        # Chờ luồng kết thúc (timeout ngắn)
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(0.1) 
        
        # Xóa hotkey
        try:
            keyboard.remove_hotkey('f6')
        except:
            pass
            
        self.overlay.destroy()
        self.root.destroy()

    def update_circle(self):
        """
        Vẽ lại vòng tròn cố định tại trung tâm màn hình và cập nhật bán kính.
        
        CẬP NHẬT: Sử dụng canvas.coords() để cập nhật đối tượng canvas thay vì xóa và tạo lại,
        giúp việc cập nhật mượt mà hơn và tránh các lỗi hiển thị.
        """
        # Bán kính được lấy từ self.radius.get()
        r = self.radius.get()
        
        # ĐẶT VÒNG TRÒN CỐ ĐỊNH TẠI TRUNG TÂM MÀN HÌNH
        center_x = self.root.winfo_screenwidth() // 2
        center_y = self.root.winfo_screenheight() // 2
        
        x0, y0 = center_x - r, center_y - r
        x1, y1 = center_x + r, center_y + r
        
        if self.circle:
            # Nếu vòng tròn đã tồn tại, chỉ cập nhật tọa độ
            self.canvas.coords(self.circle, x0, y0, x1, y1)
        else:
            # Lần đầu tiên, tạo vòng tròn
            self.circle = self.canvas.create_oval(
                x0, y0, x1, y1, 
                outline=ACCENT_COLOR, 
                width=2,
                dash=(5, 3) 
            )
        
        # CẬP NHẬT MỚI: Đảm bảo cửa sổ overlay luôn nằm trên cùng (giúp khắc phục lỗi hiển thị)
        self.overlay.lift()

        # Lập lịch gọi lại chính nó
        if not self.stop_event.is_set():
             # CẬP NHẬT: Lưu ID công việc để có thể hủy khi đóng ứng dụng
             self._update_circle_job_id = self.root.after(50, self.update_circle)
        
    def check_for_color(self, img, target_color, tolerance):
        """
        Sử dụng NumPy để kiểm tra màu sắc hiệu quả và trả về vị trí của pixel khớp (nếu tìm thấy).
        Trả về (found_bool, relative_x, relative_y)
        Tìm pixel khớp GẦN TÂM NHẤT của vùng quét.
        """
        target_np = np.array(target_color, dtype=np.uint8)
        img_rgb = img[:, :, :3]
        
        # Tính sự khác biệt tuyệt đối
        diff = np.abs(img_rgb.astype(np.int16) - target_np.astype(np.int16))
        
        # Tạo mặt nạ nơi tất cả 3 kênh RGB đều nằm trong phạm vi Tolerance
        mask = np.all(diff <= tolerance, axis=-1)
        
        if np.any(mask):
            # Tìm vị trí (chỉ mục) của tất cả các pixel khớp (hàng, cột)
            match_indices = np.argwhere(mask)
            
            # Tính toán vị trí tâm tương đối của ảnh chụp
            center_x = img.shape[1] // 2
            center_y = img.shape[0] // 2
            
            # Tính khoảng cách từ mỗi điểm khớp đến tâm
            distances = np.sqrt((match_indices[:, 1] - center_x)**2 + (match_indices[:, 0] - center_y)**2)
            
            # Tìm chỉ mục của điểm có khoảng cách nhỏ nhất
            closest_index = np.argmin(distances)
            
            # Lấy tọa độ tương đối (x, y)
            best_match_y, best_match_x = match_indices[closest_index]
            
            return True, best_match_x, best_match_y
        
        return False, 0, 0

    def run_detection(self):
        """Vòng lặp phát hiện màu chính, chạy trong một luồng riêng."""
        # TÍNH TOÁN VỊ TRÍ TRUNG TÂM MÀN HÌNH CỐ ĐỊNH CHO VÙNG QUÉT
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        fixed_center_x = screen_w // 2
        fixed_center_y = screen_h // 2

        # THAM SỐ ĐIỀU CHỈNH ĐỘ CHÍNH XÁC KÉO CHUỘT 
        # Giá trị 5 pixel hướng xuống để nhắm vào thân (Centre Mass)
        # HƯỚNG DẪN TINH CHỈNH: Tăng giá trị này (ví dụ: 8 hoặc 10) nếu kéo quá cao (nhắm vào đầu).
        # Giảm giá trị này (ví dụ: 2 hoặc 0) nếu kéo quá thấp.
        VERTICAL_OFFSET = 5 
        
        # THAM SỐ ĐIỀU CHỈNH TỐC ĐỘ KÉO CHUỘT
        # ĐÃ SỬA: Giảm xuống 0.03s để phản hồi nhanh và nhạy hơn
        DRAG_DURATION = 0.03 
        
        # THAM SỐ ĐIỀU CHỈNH DELAY SAU KHI NHẢY 
        # 0.05s để game có thời gian xử lý cú nhảy trước khi aim
        JUMP_DELAY = 0.05 
        
        # THAM SỐ MỚI: Độ dài thời gian nhấn phím Jump (space)
        JUMP_PRESS_DURATION = 0.01 
        
        while not self.stop_event.is_set():
            try:
                current_radius = self.radius.get()
                current_delay = self.delay.get()
                current_mode = self.mode_var.get()
                current_tolerance = self.tolerance.get()

                # VỊ TRÍ QUÉT CỐ ĐỊNH: Sử dụng vị trí trung tâm màn hình
                center_x, center_y = fixed_center_x, fixed_center_y
                
                # Chụp màn hình vùng quanh trung tâm
                screenshot = pyautogui.screenshot(
                    region=(center_x - current_radius, center_y - current_radius, 
                            current_radius * 2, current_radius * 2)
                )
                img = np.array(screenshot)

                # Kiểm tra màu và lấy tọa độ tương đối
                found, relative_x, relative_y = self.check_for_color(img, self.target_color, current_tolerance)
                
                # --- XỬ LÝ HÀNH VI (Nếu màu được tìm thấy) ---
                if found:
                    
                    # 1. TỰ ĐỘNG KÉO TÂM (Auto Drag)
                    # Chức năng này chỉ kích hoạt nếu checkbox "Auto Drag" được bật
                    if self.drag_enabled.get():
                        # Tính toán tọa độ tuyệt đối của điểm khớp gần nhất
                        abs_target_x = (center_x - current_radius) + relative_x
                        # Áp dụng Vertical Offset để nhắm vào thân
                        abs_target_y = (center_y - current_radius) + relative_y + VERTICAL_OFFSET

                        # Di chuyển chuột mượt mà hơn (0.03s) để game nhận diện tốt hơn
                        pyautogui.moveTo(abs_target_x, abs_target_y, duration=DRAG_DURATION)

                    # 2. TỰ ĐỘNG NHẢY (Auto Jump - Phím Space)
                    # Chức năng này chỉ kích hoạt nếu checkbox "Auto Jump" được bật.
                    # Luôn chạy trước lệnh BẮN.
                    if self.jump_enabled.get():
                        # SỬA LỖI: Thay thế press_and_release bằng press/release thủ công để đảm bảo game nhận diện input
                        keyboard.press('space')
                        time.sleep(JUMP_PRESS_DURATION)
                        keyboard.release('space')
                        
                        # Delay ngắn sau khi nhảy
                        time.sleep(JUMP_DELAY) 
                        
                    # 3. KÍCH HOẠT BẮN (Shot) - BẤT KỂ Drag hay Jump có bật hay không
                    # Luôn chạy sau lệnh Jump và Drag.
                    if current_mode.startswith("Shotgun"):
                        keyboard.press_and_release("k")
                        # Thêm delay sau khi bắn nếu có thao tác Drag/Jump
                        if self.drag_enabled.get() or self.jump_enabled.get():
                            time.sleep(0.15) 

                    elif current_mode.startswith("AR"):
                        if not keyboard.is_pressed("k"):
                            keyboard.press("k")
                    
                    elif current_mode.startswith("Sniper"):
                        # Logic Sniper: Giữ L, Bắn K, Thả L (Quick Scope)
                        if not keyboard.is_pressed("l"):
                            keyboard.press("l")
                            time.sleep(0.05) # Giả lập thời gian mở scope
                            
                        keyboard.press_and_release("k")
                        
                        # Thả L ngay sau khi bắn để scope ra
                        if keyboard.is_pressed("l"):
                            keyboard.release("l")
                
                else: # Màu KHÔNG được tìm thấy
                    # Đảm bảo nhả phím bắn AR nếu không tìm thấy màu
                    if current_mode.startswith("AR") and keyboard.is_pressed("k"):
                        keyboard.release("k")

            except Exception as e:
                # Xử lý các lỗi bất ngờ và tiếp tục vòng lặp
                print(f"Lỗi trong luồng phát hiện: {e}")

            # Đảm bảo luồng tạm dừng theo giá trị delay hiện tại. 
            time.sleep(current_delay)

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorCircleApp(root)
    root.mainloop()
