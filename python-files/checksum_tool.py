import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import hashlib
import secrets
import time
import sys

# Import BLAKE3 với error handling
try:
    from blake3 import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False

class ChecksumTool:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Thiết lập cửa sổ chính"""
        self.root.title("🔐 Checksum Tool Pro")
        # ===== KÍCH THƯỚC THEO YÊU CẦU =====
        self.root.geometry("800x900")  # Tăng lên để giống ảnh
        self.root.resizable(True, True)
        self.root.minsize(800,900)    # Minimum size giống với default
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Set style
        try:
            style = ttk.Style()
            style.theme_use('clam')
        except:
            pass
    
    def create_widgets(self):
        """Tạo giao diện với kích thước phù hợp"""
        
        # Main frame với padding lớn hơn
        main_frame = ttk.Frame(self.root, padding="20")  # Tăng padding
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title với khoảng cách lớn hơn
        title_label = ttk.Label(main_frame, text="🔐 Checksum Tool Pro", 
                               font=("Arial", 20, "bold"))  # Tăng font size
        title_label.pack(pady=(0, 20))  # Tăng khoảng cách
        
        # Top section - Input và controls
        top_section = ttk.Frame(main_frame)
        top_section.pack(fill=tk.X, pady=(0, 20))  # Tăng khoảng cách
        
        # Input section với kích thước lớn hơn
        input_frame = ttk.LabelFrame(top_section, text="📝 Nhập chuỗi cần hash", padding="12")
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.input_text = scrolledtext.ScrolledText(input_frame, height=4, font=("Consolas", 11))  # Tăng height và font
        self.input_text.pack(fill=tk.X)
        
        # Character count
        self.char_count_var = tk.StringVar(value="0 ký tự")
        char_label = ttk.Label(input_frame, textvariable=self.char_count_var, 
                              font=("Arial", 9), foreground="gray")
        char_label.pack(anchor=tk.E, pady=(5, 0))
        
        self.input_text.bind('<KeyRelease>', self.update_char_count)
        
        # Private key section với kích thước lớn hơn
        key_frame = ttk.LabelFrame(top_section, text="🔑 Private Key", padding="12")
        key_frame.pack(fill=tk.X, pady=(0, 15))
        
        key_container = ttk.Frame(key_frame)
        key_container.pack(fill=tk.X)
        
        self.private_key = tk.Entry(key_container, show="*", font=("Consolas", 11))  # Tăng font
        self.private_key.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Key buttons với kích thước lớn hơn
        key_buttons = ttk.Frame(key_container)
        key_buttons.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(key_buttons, text="🎲 Tạo Key", command=self.generate_key, width=12).pack(side=tk.TOP, pady=(0, 3))
        ttk.Button(key_buttons, text="👁️ Hiện/Ẩn", command=self.toggle_key_visibility, width=12).pack(side=tk.TOP)
        
        # Algorithm selection với kích thước lớn hơn
        algo_frame = ttk.LabelFrame(top_section, text="🔧 Chọn thuật toán", padding="12")
        algo_frame.pack(fill=tk.X, pady=(0, 15))
        
        algorithms = ["MD5", "SHA-256"]
        if BLAKE3_AVAILABLE:
            algorithms.append("BLAKE3")
        else:
            algorithms.append("BLAKE3 (Không khả dụng)")
        
        algo_container = ttk.Frame(algo_frame)
        algo_container.pack(fill=tk.X)
        
        self.algo_choice = ttk.Combobox(algo_container, values=algorithms, state="readonly", 
                                       width=30, font=("Arial", 10))  # Tăng width và font
        self.algo_choice.current(1)  # Default to SHA-256
        self.algo_choice.pack(side=tk.LEFT)
        
        # Algorithm info
        self.algo_info = ttk.Label(algo_container, text="", foreground="blue", font=("Arial", 10))
        self.algo_info.pack(side=tk.LEFT, padx=(15, 0))
        
        self.algo_choice.bind('<<ComboboxSelected>>', self.on_algorithm_change)
        self.on_algorithm_change()
        
        # Control buttons với kích thước lớn hơn
        button_frame = ttk.Frame(top_section)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="🔐 TÍNH CHECKSUM", command=self.calculate_checksum,
                  style="Accent.TButton", width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🗑️ XÓA", command=self.clear_all, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📋 COPY", command=self.copy_result, width=12).pack(side=tk.LEFT)
        
        # ===== KHU VỰC KẾT QUẢ VỚI KÍCH THƯỚC LỚN =====
        result_frame = ttk.LabelFrame(main_frame, text="📊 Kết quả", padding="15")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.output_text = scrolledtext.ScrolledText(
            result_frame, 
            height=30,      # Kích thước vừa phải
            width=100,       # Rộng hơn
            font=("Consolas", 11),  # Font lớn hơn
            wrap=tk.WORD,
            bg="#f8f9fa",
            fg="#212529",
            selectbackground="#007bff",
            selectforeground="white",
            padx=10,        # Padding nội dung
            pady=8
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar với kích thước lớn hơn
        self.status_var = tk.StringVar(value="Sẵn sàng - Nhập dữ liệu và nhấn 'TÍNH CHECKSUM'")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 10),
                              padding="8")
        status_bar.pack(fill=tk.X)
        
        # Keyboard shortcuts
        self.root.bind('<Return>', lambda e: self.calculate_checksum())
        self.root.bind('<Control-n>', lambda e: self.clear_all())
        self.root.bind('<Control-c>', lambda e: self.copy_result())
        
        # Welcome message đơn giản
        welcome_msg = """🔐 CHECKSUM TOOL PRO

Hướng dẫn sử dụng:
1. Nhập chuỗi cần hash vào ô trên
2. Nhập private key (hoặc nhấn "Tạo Key" để tạo tự động)
3. Chọn thuật toán hash (MD5, SHA-256, BLAKE3)
4. Nhấn "TÍNH CHECKSUM" để tạo hash

Phím tắt:
• Enter: Tính checksum
• Ctrl+N: Xóa tất cả
• Ctrl+C: Copy kết quả

Sẵn sàng tạo checksum!"""
        
        self.output_text.insert("1.0", welcome_msg)
    
    def update_char_count(self, event=None):
        """Cập nhật số ký tự"""
        text = self.input_text.get("1.0", tk.END).strip()
        char_count = len(text)
        byte_count = len(text.encode('utf-8'))
        self.char_count_var.set(f"{char_count} ký tự ({byte_count} bytes)")
    
    def on_algorithm_change(self, event=None):
        """Cập nhật thông tin thuật toán"""
        algorithm = self.algo_choice.get()
        
        info_map = {
            "MD5": "⚠️ 128-bit, không an toàn",
            "SHA-256": "✅ 256-bit, an toàn cao", 
            "BLAKE3": "🚀 256-bit, nhanh nhất",
            "BLAKE3 (Không khả dụng)": "❌ Cần cài đặt"
        }
        
        self.algo_info.config(text=info_map.get(algorithm, ""))
    
    def generate_key(self):
        """Tạo private key ngẫu nhiên"""
        try:
            key = secrets.token_hex(32)
            self.private_key.delete(0, tk.END)
            self.private_key.insert(0, key)
            self.status_var.set("Đã tạo private key 256-bit an toàn")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo key: {e}")
    
    def toggle_key_visibility(self):
        """Hiện/ẩn private key"""
        if self.private_key.cget('show') == '*':
            self.private_key.config(show='')
        else:
            self.private_key.config(show='*')
    
    def calculate_checksum(self):
        """Tính checksum với kết quả đơn giản"""
        try:
            # Validate input
            text = self.input_text.get("1.0", tk.END).strip()
            key = self.private_key.get().strip()
            algorithm = self.algo_choice.get()
            
            if not text:
                messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập chuỗi cần hash!")
                self.input_text.focus()
                return
                
            if not key:
                messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập private key!")
                self.private_key.focus()
                return
            
            # Check BLAKE3 availability
            if algorithm == "BLAKE3" and not BLAKE3_AVAILABLE:
                messagebox.showerror("Lỗi", "BLAKE3 không khả dụng!\nVui lòng chọn MD5 hoặc SHA-256.")
                return
            
            # Update status
            self.status_var.set("Đang tính checksum...")
            self.root.update()
            
            # Combine text and key
            combined = (text + key).encode('utf-8')
            
            # Calculate checksum
            if algorithm == "MD5":
                result = hashlib.md5(combined).hexdigest()
            elif algorithm == "SHA-256":
                result = hashlib.sha256(combined).hexdigest()
            elif algorithm == "BLAKE3":
                result = blake3(combined).hexdigest()
            else:
                raise ValueError(f"Thuật toán không hỗ trợ: {algorithm}")
            
            # ===== KẾT QUẢ ĐƠN GIẢN =====
            simple_result = f"""📊 KẾT QUẢ CHECKSUM

📝 Dữ liệu đầu vào:
{text}

🔑 Private Key:
{key}

🔧 Thuật toán:
{algorithm}

🔐 Kết quả:
{result}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Checksum đã được tạo thành công!
📋 Nhấn "COPY" để sao chép kết quả."""
            
            # Clear and display result
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", simple_result)
            
            # Scroll to top
            self.output_text.see("1.0")
            
            # Update status
            self.status_var.set(f"✅ Checksum tạo thành công - {algorithm}")
            
        except Exception as e:
            error_msg = f"Lỗi: {str(e)}"
            
            # Display simple error
            self.output_text.delete("1.0", tk.END)
            error_display = f"""❌ LỖI TÍNH CHECKSUM

Chi tiết lỗi: {error_msg}

Vui lòng kiểm tra:
• Dữ liệu đầu vào có hợp lệ không
• Thuật toán đã chọn có khả dụng không
• Thử khởi động lại ứng dụng nếu cần

Liên hệ hỗ trợ nếu lỗi vẫn tiếp tục."""
            
            self.output_text.insert("1.0", error_display)
            messagebox.showerror("Lỗi", error_msg)
            self.status_var.set("❌ Lỗi khi tính checksum")
    
    def clear_all(self):
        """Xóa tất cả dữ liệu"""
        if messagebox.askyesno("Xác nhận xóa", "Bạn có chắc muốn xóa tất cả dữ liệu?"):
            self.input_text.delete("1.0", tk.END)
            self.private_key.delete(0, tk.END)
            self.output_text.delete("1.0", tk.END)
            self.char_count_var.set("0 ký tự")
            self.status_var.set("Đã xóa tất cả dữ liệu - Sẵn sàng nhập mới")
            self.input_text.focus()
    
    def copy_result(self):
        """Copy checksum result"""
        try:
            result_content = self.output_text.get("1.0", tk.END).strip()
            if not result_content:
                messagebox.showwarning("Cảnh báo", "Không có kết quả để copy!")
                return
            
            # Tìm dòng chứa kết quả checksum
            lines = result_content.split('\n')
            checksum_line = None
            
            # Tìm dòng sau "🔐 Kết quả:"
            found_result_section = False
            for line in lines:
                if "🔐 Kết quả:" in line:
                    found_result_section = True
                    continue
                if found_result_section and line.strip() and not line.startswith('━'):
                    checksum_line = line.strip()
                    break
            
            if checksum_line:
                # Copy chỉ checksum
                self.root.clipboard_clear()
                self.root.clipboard_append(checksum_line)
                self.root.update()
                
                self.status_var.set("📋 Đã copy checksum vào clipboard")
                messagebox.showinfo("Copy thành công", f"Checksum đã được copy:\n\n{checksum_line}")
            else:
                # Copy toàn bộ
                self.root.clipboard_clear()
                self.root.clipboard_append(result_content)
                self.root.update()
                
                self.status_var.set("📋 Đã copy toàn bộ kết quả vào clipboard")
                messagebox.showinfo("Copy thành công", "Toàn bộ kết quả đã được copy!")
                
        except Exception as e:
            messagebox.showerror("Lỗi copy", f"Không thể copy: {str(e)}")

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = ChecksumTool(root)
        root.mainloop()
    except Exception as e:
        print(f"ERROR: {e}")
        messagebox.showerror("Lỗi khởi động", f"Không thể khởi động ứng dụng:\n{str(e)}")

if __name__ == "__main__":
    main()
