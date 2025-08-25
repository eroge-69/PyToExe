import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json

class APITester:
    def __init__(self, root):
        self.root = root
        self.root.title("RESTful API测试工具")
        self.root.geometry("800x600")
        
        self.create_widgets()
        
    def create_widgets(self):
        # 方法选择
        method_frame = ttk.Frame(self.root)
        method_frame.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Label(method_frame, text="方法:").pack(side=tk.LEFT)
        self.method_var = tk.StringVar(value="GET")
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self.method_combo = ttk.Combobox(method_frame, textvariable=self.method_var, values=methods, width=10)
        self.method_combo.pack(side=tk.LEFT, padx=5)
        
        # URL输入
        url_frame = ttk.Frame(self.root)
        url_frame.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Label(url_frame, text="URL:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar(value="http://localhost:8000/static")
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=70)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 请求头
        headers_frame = ttk.LabelFrame(self.root, text="请求头")
        headers_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.headers_text = scrolledtext.ScrolledText(headers_frame, height=5)
        self.headers_text.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        self.headers_text.insert(tk.END, "Content-Type: application/json")
        
        # 请求体
        body_frame = ttk.LabelFrame(self.root, text="请求体 (JSON)")
        body_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.body_text = scrolledtext.ScrolledText(body_frame, height=8)
        self.body_text.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        self.body_text.insert(tk.END, '{\n    "key": "value"\n}')
        
        # 按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="发送请求", command=self.send_request).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清除", command=self.clear).pack(side=tk.LEFT, padx=5)
        
        # 响应框架
        response_frame = ttk.LabelFrame(self.root, text="响应")
        response_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # 状态码
        status_frame = ttk.Frame(response_frame)
        status_frame.pack(pady=5, padx=5, fill=tk.X)
        
        ttk.Label(status_frame, text="状态码:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 响应内容
        self.response_text = scrolledtext.ScrolledText(response_frame, height=10)
        self.response_text.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        
    def send_request(self):
        url = self.url_var.get().strip()
        method = self.method_var.get()
        
        if not url:
            messagebox.showerror("错误", "请输入URL")
            return
        
        try:
            # 解析请求头
            headers = {}
            headers_text = self.headers_text.get("1.0", tk.END).strip()
            if headers_text:
                for line in headers_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip()] = value.strip()
            
            # 解析请求体
            data = None
            body_text = self.body_text.get("1.0", tk.END).strip()
            if body_text and method in ["POST", "PUT", "PATCH"]:
                try:
                    data = json.loads(body_text)
                except json.JSONDecodeError as e:
                    messagebox.showerror("错误", f"JSON格式错误: {e}")
                    return
            
            # 发送请求
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data
            )
            
            # 显示响应
            self.status_var.set(f"{response.status_code} {response.reason}")
            
            # 尝试格式化JSON响应
            try:
                formatted_response = json.dumps(response.json(), indent=2, ensure_ascii=False)
            except:
                formatted_response = response.text
            
            self.response_text.delete("1.0", tk.END)
            self.response_text.insert(tk.END, formatted_response)
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("错误", f"请求失败: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"发生未知错误: {e}")
    
    def clear(self):
        self.response_text.delete("1.0", tk.END)
        self.status_var.set("")

def main():
    root = tk.Tk()
    app = APITester(root)
    root.mainloop()

if __name__ == "__main__":
    main()