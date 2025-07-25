import customtkinter
from tkinter import filedialog, messagebox, PhotoImage
import os
import shutil
from PIL import Image, ImageTk
import time

class YuhChuPhotographyApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Yuh Chu Photography - Photo Filter")
        self.geometry("1000x700") # Kích thước cửa sổ ban đầu lớn hơn
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.image_extensions = (".jpg", ".jpeg", ".png", ".cr2", ".nef", ".arw", ".orf", ".sr2", ".dng")

        self.current_display_image_path = None # Biến để lưu đường dẫn ảnh đang hiển thị

        # --- Sidebar ---
        self.sidebar_frame = customtkinter.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) # Cung cấp không gian cho các widget dưới cùng

        # Logo
        try:
            # Load the YUH.png logo
            self.logo_image_pil = Image.open("logo.png")
            # Resize logo for sidebar if needed, e.g., max 150px width
            logo_width, logo_height = self.logo_image_pil.size
            if logo_width > 150:
                self.logo_image_pil = self.logo_image_pil.resize((150, int(logo_height * 150 / logo_width)), Image.Resampling.LANCZOS)
            self.logo_image_tk = ImageTk.PhotoImage(self.logo_image_pil)
            self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, image=self.logo_image_tk, text="")
            self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        except Exception as e:
            self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Yuh Chu Photography", font=customtkinter.CTkFont(size=18, weight="bold"))
            self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
            print(f"Không tìm thấy hoặc lỗi khi tải YUH.png: {e}")

        self.label_title = customtkinter.CTkLabel(self.sidebar_frame, text="Cài đặt lọc ảnh", font=customtkinter.CTkFont(size=16, weight="bold"))
        self.label_title.grid(row=1, column=0, padx=20, pady=10)

        self.button_select_folder = customtkinter.CTkButton(self.sidebar_frame, text="Chọn thư mục ảnh gốc", command=self.select_source_folder)
        self.button_select_folder.grid(row=2, column=0, padx=20, pady=10)

        self.button_select_output_folder = customtkinter.CTkButton(self.sidebar_frame, text="Chọn thư mục đích", command=self.select_output_folder)
        self.button_select_output_folder.grid(row=3, column=0, padx=20, pady=10)

        self.label_operation = customtkinter.CTkLabel(self.sidebar_frame, text="Thao tác:", font=customtkinter.CTkFont(size=14))
        self.label_operation.grid(row=4, column=0, padx=20, pady=(15, 5), sticky="w")

        self.operation_choices = ["Sao chép", "Di chuyển"]
        self.operation_var = customtkinter.StringVar(value=self.operation_choices [0])
        self.operation_menu = customtkinter.CTkComboBox(self.sidebar_frame, values=self.operation_choices, variable=self.operation_var)
        self.operation_menu.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        self.label_source_folder = customtkinter.CTkLabel(self.sidebar_frame, text="Thư mục gốc: Chưa chọn", wraplength=160, justify="left")
        self.label_source_folder.grid(row=6, column=0, padx=20, pady=5, sticky="sw")
        self.label_output_folder = customtkinter.CTkLabel(self.sidebar_frame, text="Thư mục đích: Chưa chọn", wraplength=160, justify="left")
        self.label_output_folder.grid(row=7, column=0, padx=20, pady=5, sticky="nw")


        # --- Main Content Frame ---
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1) # Dòng này dành cho khung hiển thị ảnh, cho phép nó co giãn

        self.label_instruction = customtkinter.CTkLabel(self.main_frame, text="Dán danh sách tên ảnh cần lọc (mỗi tên một dòng):", font=customtkinter.CTkFont(size=14))
        self.label_instruction.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.textbox_image_names = customtkinter.CTkTextbox(self.main_frame, height=100, wrap="word")
        self.textbox_image_names.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.button_start_filter = customtkinter.CTkButton(self.main_frame, text="Bắt đầu lọc ảnh", command=self.start_filter_process)
        self.button_start_filter.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.label_current_image_title = customtkinter.CTkLabel(self.main_frame, text="Ảnh đang xử lý:", font=customtkinter.CTkFont(size=14, weight="bold"))
        self.label_current_image_title.grid(row=3, column=0, padx=10, pady=(10, 5), sticky="w")

        self.image_display_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.image_display_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        self.image_display_frame.grid_columnconfigure(0, weight=1)
        self.image_display_frame.grid_rowconfigure(0, weight=1)

        self.current_image_label = customtkinter.CTkLabel(self.image_display_frame, text="")
        self.current_image_label.grid(row=0, column=0, sticky="nsew")
        # Bind the configure event to resize the image
        self.image_display_frame.bind("<Configure>", self.resize_image_on_configure)

        self.progress_bar = customtkinter.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.label_status = customtkinter.CTkLabel(self.main_frame, text="Trạng thái: Sẵn sàng", font=customtkinter.CTkFont(size=14))
        self.label_status.grid(row=6, column=0, padx=10, pady=5, sticky="w")

        self.label_time_taken = customtkinter.CTkLabel(self.main_frame, text="Thời gian xử lý: 0.00 giây", font=customtkinter.CTkFont(size=14))
        self.label_time_taken.grid(row=7, column=0, padx=10, pady=5, sticky="w")

        # Initial values
        self.source_folder = ""
        self.output_folder = ""

    def select_source_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.source_folder = folder_selected
            self.label_source_folder.configure(text=f"Thư mục gốc: {os.path.basename(folder_selected)}")
            messagebox.showinfo("Thông báo", f"Đã chọn thư mục gốc: {folder_selected}")

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder = folder_selected
            self.label_output_folder.configure(text=f"Thư mục đích: {os.path.basename(folder_selected)}")
            messagebox.showinfo("Thông báo", f"Đã chọn thư mục đích: {folder_selected}")

    def display_image(self, image_path):
        self.current_display_image_path = image_path # Lưu đường dẫn ảnh hiện tại
        try:
            pil_image = Image.open(image_path)
            # Get the current size of the image_display_frame
            available_width = self.image_display_frame.winfo_width()
            available_height = self.image_display_frame.winfo_height()

            # Fallback for initial state before widgets are fully rendered
            if available_width == 1 or available_height == 1:
                available_width = 600
                available_height = 400

            # Resize the image to fit the available space while maintaining aspect ratio
            pil_image.thumbnail((available_width, available_height), Image.Resampling.LANCZOS)
            tk_image = ImageTk.PhotoImage(pil_image)

            self.current_image_label.configure(image=tk_image)
            self.current_image_label.image = tk_image # Keep a reference!
            self.label_current_image_title.configure(text=f"Ảnh đang xử lý: {os.path.basename(image_path)}")
        except Exception as e:
            self.current_image_label.configure(image=None)
            self.label_current_image_title.configure(text=f"Không thể hiển thị: {os.path.basename(image_path)} (Lỗi: {e})")
            print(f"Lỗi khi hiển thị ảnh {image_path}: {e}")

    def resize_image_on_configure(self, event):
        # This function is called when the image_display_frame is resized
        if self.current_display_image_path:
            self.display_image(self.current_display_image_path)


    def start_filter_process(self):
        if not self.source_folder:
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục ảnh gốc.")
            return
        if not self.output_folder:
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục đích.")
            return

        image_names_text = self.textbox_image_names.get("1.0", "end-1c").strip()
        if not image_names_text:
            messagebox.showerror("Lỗi", "Vui lòng dán danh sách tên ảnh cần lọc.")
            return

        target_names = [name.strip().split('.')[0] for name in image_names_text.split('\n') if name.strip()]
        operation = self.operation_var.get()

        self.label_status.configure(text="Trạng thái: Đang tiến hành lọc...")
        self.progress_bar.set(0)
        self.update_idletasks() # Cập nhật GUI ngay lập tức

        start_time = time.time()
        filtered_count = 0
        all_files = [f for f in os.listdir(self.source_folder) if os.path.isfile(os.path.join(self.source_folder, f)) and f.lower().endswith(self.image_extensions)]
        total_files_to_check = len(all_files)

        if total_files_to_check == 0:
            messagebox.showinfo("Thông báo", "Không tìm thấy ảnh nào trong thư mục gốc để lọc.")
            self.label_status.configure(text="Trạng thái: Hoàn thành.")
            self.label_time_taken.configure(text="Thời gian xử lý: 0.00 giây")
            return

        for i, filename in enumerate(all_files):
            base_name, ext = os.path.splitext(filename)
            file_number_match = False

            # Lọc theo 4 số cuối của tên file
            if len(base_name) >= 4:
                last_four_digits = base_name[-4:]
                if last_four_digits.isdigit() and last_four_digits in target_names:
                    file_number_match = True

            # Also check if the full basename matches any of the target names directly
            if base_name in target_names:
                 file_number_match = True

            if file_number_match:
                source_path = os.path.join(self.source_folder, filename)
                destination_path = os.path.join(self.output_folder, filename)

                try:
                    self.display_image(source_path)
                    if operation == "Sao chép":
                        shutil.copy2(source_path, destination_path)
                    elif operation == "Di chuyển":
                        # For moving, ensure destination doesn't exist to avoid shutil.Error
                        if os.path.exists(destination_path):
                            os.remove(destination_path) # Or handle conflict as per user preference
                        shutil.move(source_path, destination_path)
                    filtered_count += 1
                except Exception as e:
                    print(f"Lỗi khi {operation.lower()} file {filename}: {e}")
                    self.label_status.configure(text=f"Lỗi khi {operation.lower()}: {filename}. Xem console.")
                    continue

            progress = (i + 1) / total_files_to_check
            self.progress_bar.set(progress)
            self.update_idletasks() # Cập nhật GUI để hiển thị tiến độ và ảnh hiện tại

        end_time = time.time()
        time_taken = end_time - start_time

        self.label_status.configure(text=f"Trạng thái: Đã lọc xong! Đã tìm thấy {filtered_count} ảnh.")
        self.label_time_taken.configure(text=f"Thời gian xử lý: {time_taken:.2f} giây")
        self.progress_bar.set(1) # Đảm bảo thanh tiến độ đầy
        self.current_image_label.configure(image=None) # Xóa hiển thị ảnh
        self.label_current_image_title.configure(text="Ảnh đang xử lý: Hoàn thành")
        messagebox.showinfo("Hoàn thành", f"Quá trình lọc đã hoàn tất. Đã {operation.lower()} được {filtered_count} ảnh vào thư mục:\n{self.output_folder}")

if __name__ == "__main__":
    app = YuhChuPhotographyApp()
    app.mainloop()