import tkinter as tk
from tkinter import messagebox
import time
import threading

class ENOMTimerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Đồng Hồ ENOM")
        master.geometry("400x500") # Kích thước cửa sổ
        master.resizable(False, False) # Không cho phép thay đổi kích thước

        self.is_running = False
        self.is_paused = False # Thêm biến để kiểm soát trạng thái tạm dừng
        self.current_round = 0
        self.remaining_time = 0
        self.timer_thread = None

        # Liên kết sự kiện nhấn phím Spacebar với hàm pause_resume_timer
        master.bind('<space>', self.pause_resume_timer) 

        # --- Tạo các widget ---

        # Tiêu đề
        self.title_label = tk.Label(master, text="ĐỒNG HỒ TẬP ENOM", font=("Helvetica", 16, "bold"), fg="blue")
        self.title_label.pack(pady=10)

        # Khung nhập liệu
        input_frame = tk.Frame(master)
        input_frame.pack(pady=5)

        # Thời gian tập mỗi round
        tk.Label(input_frame, text="Thời gian tập (phút:giây):", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", pady=2)
        self.round_min_entry = tk.Entry(input_frame, width=5)
        self.round_min_entry.grid(row=0, column=1)
        tk.Label(input_frame, text=":").grid(row=0, column=2)
        self.round_sec_entry = tk.Entry(input_frame, width=5)
        self.round_sec_entry.grid(row=0, column=3)
        self.round_min_entry.insert(0, "1") # Giá trị mặc định
        self.round_sec_entry.insert(0, "00")

        # Thời gian nghỉ
        tk.Label(input_frame, text="Thời gian nghỉ (phút:giây):", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=2)
        self.rest_min_entry = tk.Entry(input_frame, width=5)
        self.rest_min_entry.grid(row=1, column=1)
        tk.Label(input_frame, text=":").grid(row=1, column=2)
        self.rest_sec_entry = tk.Entry(input_frame, width=5)
        self.rest_sec_entry.grid(row=1, column=3)
        self.rest_min_entry.insert(0, "0") # Giá trị mặc định
        self.rest_sec_entry.insert(0, "30")

        # Số lượng round
        tk.Label(input_frame, text="Số lượng round:", font=("Helvetica", 10)).grid(row=2, column=0, sticky="w", pady=2)
        self.num_rounds_entry = tk.Entry(input_frame, width=5)
        self.num_rounds_entry.grid(row=2, column=1, columnspan=3, sticky="w")
        self.num_rounds_entry.insert(0, "5") # Giá trị mặc định

        # --- Nút chức năng ---
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="BẮT ĐẦU", command=self.start_timer, bg="green", fg="white", font=("Helvetica", 12, "bold"), width=10)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(button_frame, text="KẾT THÚC", command=self.stop_timer, bg="red", fg="white", font=("Helvetica", 12, "bold"), width=10, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Thêm nút TẠM DỪNG / TIẾP TỤC
        self.pause_button = tk.Button(button_frame, text="TẠM DỪNG (Space)", command=self.pause_resume_timer, bg="orange", fg="white", font=("Helvetica", 12, "bold"), width=18, state=tk.DISABLED)
        self.pause_button.grid(row=1, column=0, columnspan=2, pady=5)


        # --- Hiển thị trạng thái và thời gian ---
        display_frame = tk.Frame(master)
        display_frame.pack(pady=20)

        self.status_label = tk.Label(display_frame, text="Sẵn sàng...", font=("Helvetica", 14), fg="black")
        self.status_label.pack()

        self.round_label = tk.Label(display_frame, text="Round: 0/0", font=("Helvetica", 18, "bold"), fg="purple")
        self.round_label.pack(pady=10)

        self.time_display = tk.Label(display_frame, text="00:00", font=("Helvetica", 48, "bold"), bg="black", fg="lime", width=6)
        self.time_display.pack(pady=10)

        self.countdown_label = tk.Label(display_frame, text="", font=("Helvetica", 12))
        self.countdown_label.pack()


    def start_timer(self):
        if self.is_running:
            messagebox.showinfo("Thông báo", "Đồng hồ đang chạy rồi trai đẹp cư bụ ơi!")
            return

        try:
            self.round_duration = int(self.round_min_entry.get()) * 60 + int(self.round_sec_entry.get())
            self.rest_duration = int(self.rest_min_entry.get()) * 60 + int(self.rest_sec_entry.get())
            self.num_rounds = int(self.num_rounds_entry.get())

            if self.round_duration <= 0 or self.num_rounds <= 0:
                messagebox.showerror("Lỗi", "Thời gian tập và số round phải lớn hơn 0 nhé trai đẹp cư bụ!")
                return

        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ vào các trường thời gian và số round.")
            return

        self.is_running = True
        self.is_paused = False
        self.current_round = 0
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL, text="TẠM DỪNG (Space)")
        
        self.timer_thread = threading.Thread(target=self._run_timer)
        self.timer_thread.start()

    def stop_timer(self):
        if not self.is_running and not self.is_paused:
            messagebox.showinfo("Thông báo", "Đồng hồ chưa chạy mà trai đẹp cư bụ!")
            return
        
        confirm = messagebox.askyesno("Kết thúc Buổi tập", "Trai đẹp cư bụ có chắc muốn kết thúc buổi tập không?")
        if confirm:
            self.is_running = False
            self.is_paused = False # Đảm bảo không ở trạng thái tạm dừng khi dừng hoàn toàn
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.DISABLED, text="TẠM DỪNG (Space)")
            self.status_label.config(text="Đã kết thúc.")
            self.time_display.config(text="00:00")
            self.round_label.config(text="Round: 0/0")
            self.countdown_label.config(text="")
            # Không cần chờ thread kết thúc, nó sẽ tự thoát khi is_running = False

    def pause_resume_timer(self, event=None): # event=None để nó có thể được gọi từ nút bấm hoặc phím tắt
        if not self.is_running and not self.is_paused: # Chỉ khi timer đang chạy hoặc tạm dừng thì mới xử lý
            return

        if self.is_paused:
            self.is_paused = False
            self.pause_button.config(text="TẠM DỪNG (Space)", bg="orange")
            self.status_label.config(text="TIẾP TỤC!")
            # Khi tiếp tục, cần khởi động lại đếm ngược từ thời gian còn lại
            # Logic này được xử lý trong _countdown bằng cách kiểm tra self.is_paused
            self._resume_countdown()
        else:
            self.is_paused = True
            self.pause_button.config(text="TIẾP TỤC (Space)", bg="blue")
            self.status_label.config(text="ĐÃ TẠM DỪNG...")
            self.countdown_label.config(text="Nhấn Space để tiếp tục!")


    def _run_timer(self):
        for i in range(1, self.num_rounds + 1):
            if not self.is_running:
                break

            self.current_round = i
            self.round_label.config(text=f"Round: {self.current_round}/{self.num_rounds}")
            
            # Thời gian tập
            self.status_label.config(text="BẮT ĐẦU TẬP LUYỆN!", fg="green")
            self.countdown_label.config(text=f"Round {self.current_round} - Tập")
            self._countdown(self.round_duration)

            if not self.is_running:
                break

            if i < self.num_rounds:
                # Thời gian nghỉ
                self.status_label.config(text="THỜI GIAN NGHỈ NGƠI!", fg="blue")
                self.countdown_label.config(text=f"Round {self.current_round} - Nghỉ")
                self._countdown(self.rest_duration)
                if not self.is_running:
                    break
            
            # Nếu tất cả các round đã hoàn thành và timer vẫn đang chạy
            if i == self.num_rounds and self.is_running:
                self.status_label.config(text="BUỔI TẬP ĐÃ HOÀN THÀNH!", fg="purple")
                self.countdown_label.config(text="Chúc mừng trai đẹp cư bụ!")
                self.time_display.config(text="HOÀN THÀNH!")
                self.is_running = False
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                self.pause_button.config(state=tk.DISABLED, text="TẠM DỪNG (Space)")
                messagebox.showinfo("Hoàn thành", "Chúc mừng trai đẹp cư bụ đã hoàn thành buổi tập!")
                return # Thoát khỏi hàm _run_timer

        # Trường hợp dừng đột ngột hoặc kết thúc buổi tập nhưng không phải round cuối cùng
        if not self.is_running:
            self.status_label.config(text="Đã kết thúc.", fg="red")
            self.countdown_label.config(text="Buổi tập bị ngắt.")
        
        self.is_running = False
        self.is_paused = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED, text="TẠM DỪNG (Space)")


    def _countdown(self, duration):
        self.remaining_time = duration
        while self.remaining_time >= 0 and self.is_running:
            while self.is_paused and self.is_running: # Nếu đang tạm dừng thì chờ
                time.sleep(0.1) # Kiểm tra liên tục nhưng không tốn tài nguyên
                if not self.is_running: # Nếu bị dừng khi đang tạm dừng
                    break

            if not self.is_running: # Sau khi thoát tạm dừng mà bị dừng hoàn toàn
                break

            mins, secs = divmod(self.remaining_time, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            self.time_display.config(text=time_str)
            time.sleep(1)
            self.remaining_time -= 1
        
        # Đảm bảo hiển thị 00:00 khi kết thúc đếm ngược nếu không bị dừng
        if self.is_running and not self.is_paused: # Chỉ cập nhật nếu không bị dừng hoặc tạm dừng đột ngột
             self.time_display.config(text="00:00")

    def _resume_countdown(self):
        # Hàm này chỉ để "đánh thức" vòng lặp _countdown chính
        # Vì vòng lặp đã có kiểm tra self.is_paused, chỉ cần thay đổi biến là đủ
        pass # Không cần làm gì ở đây, vòng lặp _countdown sẽ tự tiếp tục

if __name__ == "__main__":
    root = tk.Tk()
    app = ENOMTimerGUI(root)
    root.mainloop()