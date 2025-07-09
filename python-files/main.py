import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
import json
from pathlib import Path
import hashlib
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.backends import default_backend
class SSHKeyGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("SSH密钥生成工具")
        master.geometry("335x290+{}+{}".format(
            (master.winfo_screenwidth() - 335) // 2,
            (master.winfo_screenheight() - 290) // 2
        ))
        # 样式配置
        self.style = tb.Style(theme="darkly")
        # 创建主框架
        self.main_frame = tb.Frame(master, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        # 密钥类型选择
        tb.Label(self.main_frame, text="密钥类型:").grid(row=0, column=0, sticky="w", pady=5)
        self.key_type = tb.StringVar(value="ed25519")
        self.type_frame = tb.Frame(self.main_frame)
        self.type_frame.grid(row=0, column=1, sticky="w", pady=5)
        
        tb.Radiobutton(
            self.type_frame,
            text="ED25519",
            variable=self.key_type,
            value="ed25519",
            bootstyle="success"
        ).pack(side="left", padx=5)
        
        tb.Radiobutton(
            self.type_frame,
            text="RSA",
            variable=self.key_type,
            value="rsa",
            bootstyle="success"
        ).pack(side="left", padx=5)
        
        # RSA密钥长度
        tb.Label(self.main_frame, text="RSA密钥长度:").grid(row=1, column=0, sticky="w", pady=5)
        self.bits = tb.IntVar(value=4096)
        self.bits_frame = tb.Frame(self.main_frame)
        self.bits_frame.grid(row=1, column=1, sticky="w", pady=5)
        
        for bits in [2048, 3072, 4096]:
            tb.Radiobutton(
                self.bits_frame,
                text=str(bits),
                variable=self.bits,
                value=bits,
                bootstyle="success"
            ).pack(side="left", padx=5)
        # 输出目录
        tb.Label(self.main_frame, text="输出目录:").grid(row=2, column=0, sticky="w", pady=5)
        self.output_dir = tb.StringVar(value=".ssh")
        self.dir_entry = tb.Entry(self.main_frame, textvariable=self.output_dir,bootstyle="danger")
        self.dir_entry.grid(row=2, column=1, sticky="ew", pady=5)
        # 浏览按钮
        self.browse_btn = tb.Button(
            self.main_frame,
            text="浏览...",
            command=self.browse_directory,
            bootstyle="danger"
        )
        self.browse_btn.grid(row=2, column=2, padx=5)
        # 密钥注释
        tb.Label(self.main_frame, text="密钥注释:").grid(row=3, column=0, sticky="w", pady=5)
        self.comment = tb.StringVar()
        self.comment_entry = tb.Entry(self.main_frame, textvariable=self.comment, bootstyle="success")
        self.comment_entry.grid(row=3, column=1, sticky="ew", pady=5)
        # 生成按钮
        self.generate_btn = tb.Button(
            self.main_frame,
            text="生成密钥",
            command=self.generate_keys,
            bootstyle="success",
            width=15
        )
        self.generate_btn.grid(row=4, column=0, columnspan=3, pady=20)
        # 状态栏
        self.status_var = tb.StringVar()
        self.status_bar = tb.Label(
            self.main_frame,
            textvariable=self.status_var,
            bootstyle="inverse-dark"
        )
        self.status_bar.grid(row=5, column=0, columnspan=3, sticky="ew")
        # 加载上次配置
        self.load_config()
    def browse_directory(self):
        """选择输出目录"""
        from tkinter import filedialog
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir.set(dir_path)
    def generate_keys(self):
        """生成密钥"""
        try:
            # 保存当前配置
            self.save_config()
            # 获取参数
            params = {
                "key_type": self.key_type.get(),
                "bits": self.bits.get(),
                "output_dir": self.output_dir.get(),
                "comment": self.comment.get()
            }
            # 生成密钥
            self.status_var.set("正在生成密钥...")
            self.master.update()
            result = generate_ssh_key(**params)
            # 显示结果
            self.status_var.set(
                f"成功生成{params['key_type'].upper()}密钥！\n"
                f"私钥路径: {result['private_path']}\n"
                f"公钥路径: {result['public_path']}"
            )
        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")
    def save_config(self):
        """保存配置到文件"""
        config = {
            "key_type": self.key_type.get(),
            "bits": self.bits.get(),
            "output_dir": self.output_dir.get(),
            "comment": self.comment.get()
        }
        config_path = Path("ssh_keygen_config.json")
        with open(config_path, "w") as f:
            json.dump(config, f)
    def load_config(self):
        """从文件加载配置"""
        config_path = Path("ssh_keygen_config.json")
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                self.key_type.set(config.get("key_type", "ed25519"))
                self.bits.set(config.get("bits", 4096))
                self.output_dir.set(config.get("output_dir", "."))
                self.comment.set(config.get("comment", ""))
            except:
                pass

def generate_ssh_key(key_type: str = "ed25519", bits: int = 4096, output_dir: str = ".", comment: str = "") -> dict:
    """
    生成SSH密钥对
    :param key_type: 密钥类型 (rsa, ed25519)
    :param bits: RSA密钥长度 (对于ed25519忽略)
    :param output_dir: 输出目录
    :param comment: 密钥注释
    :return: 包含密钥信息的字典
    """
    key_name = f"id_{key_type}"
    private_key_path = str(Path(output_dir) / key_name)
    public_key_path = f"{private_key_path}.pub"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成密钥
    if key_type == "ed25519":
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
    else:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=bits,
            backend=default_backend()
        )
        public_key = private_key.public_key()
    
    # 序列化私钥
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # 序列化公钥
    public_ssh = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )
    
    # 添加注释
    if comment:
        public_ssh = public_ssh + b' ' + comment.encode('utf-8')
    
    # 写入文件
    with open(private_key_path, 'wb') as f:
        f.write(private_pem)
    with open(public_key_path, 'wb') as f:
        f.write(public_ssh)
    
    # 计算指纹
    fingerprint = hashlib.md5(public_ssh).hexdigest()
    fingerprint = ':'.join([fingerprint[i:i+2] for i in range(0, len(fingerprint), 2)])
    
    return {
        "type": key_type,
        "bits": bits,
        "private_key": private_pem.decode('utf-8'),
        "public_key": public_ssh.decode('utf-8'),
        "fingerprint": f"256 MD5:{fingerprint} (RSA)" if key_type == "rsa" else f"256 MD5:{fingerprint} (ED25519)",
        "private_path": private_key_path,
        "public_path": public_key_path
    }
if __name__ == "__main__":
    root = tb.Window()
    app = SSHKeyGeneratorApp(root)
    root.mainloop()