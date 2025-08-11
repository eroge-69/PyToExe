import io 
import os 
import subprocess 
import sys 
import time 
import tkinter as tk 
from tkinter import filedialog, messagebox 
import ctypes  # ✅ 用于提权 

# 🛡️ 检查是否管理员权限 
def is_admin(): 
    try: 
        return ctypes.windll.shell32.IsUserAnAdmin() 
    except: 
        return False 

# ✳️ 提权重启自身（管理员） 
def run_as_admin(): 
    ctypes.windll.shell32.ShellExecuteW( 
        None, "runas", sys.executable, ' '.join([sys.argv[0]] + sys.argv[1:]), None, 1 
    ) 

# ⚠️ 非管理员时自动重启脚本 
if not is_admin(): 
    print("⏫ 正在尝试以管理员身份重新运行脚本...") 
    run_as_admin() 
    sys.exit() 

# ✅ 设置标准输出为 UTF-8，防止中文乱码 
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8') 


def run_cmd(cmd_str, ignore_keywords=None): 
    """运行命令并实时打印输出，使用 GBK 解码防乱码""" 
    try: 
        print(f"\n执行命令：{cmd_str}", flush=True) 
        process = subprocess.Popen( 
            cmd_str, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            bufsize=1 
        ) 

        output_lines = [] 
        for line in iter(process.stdout.readline, b''): 
            decoded = line.decode('gbk', errors='ignore').rstrip() 
            output_lines.append(decoded) 
            print(decoded, flush=True) 

        process.stdout.close() 
        process.wait() 

        full_output = "\n".join(output_lines) 

        if process.returncode not in (0, None): 
            if ignore_keywords and any(k in full_output for k in ignore_keywords): 
                print("⚠️ 命令非0退出码，但包含可忽略内容，继续执行。", flush=True) 
                return 
            messagebox.showerror("错误", f"命令执行失败:\n{cmd_str}\n\n输出信息:\n{full_output}") 
            sys.exit(1) 

    except Exception as e: 
        messagebox.showerror("错误", f"执行命令异常:\n{cmd_str}\n\n{e}") 
        sys.exit(1) 


def rule_exists(rule_name): 
    """检查防火墙规则是否存在""" 
    result = subprocess.run( 
        f'netsh advfirewall firewall show rule name="{rule_name}"', 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE 
    ) 
    output = result.stdout.decode('gbk', errors='ignore') 
    return "没有匹配的规则" not in output and "No rules match" not in output 


def select_exe_file(): 
    """弹出窗口选择 .exe 文件""" 
    root = tk.Tk() 
    root.withdraw() 
    file_path = filedialog.askopenfilename( 
        title="请选择 YuanShen.exe", 
        filetypes=[("可执行文件", "*.exe")], 
    ) 
    root.destroy() 
    if not file_path: 
        messagebox.showinfo("取消", "未选择任何文件，程序已退出。") 
        sys.exit(0) 
    return file_path 


def block_network(rule_name, exe_path): 
    """添加防火墙规则阻止网络访问""" 
    run_cmd( 
        f'netsh advfirewall firewall add rule name="{rule_name}" ' 
        f'dir=out program="{exe_path}" action=block enable=yes') 
    run_cmd( 
        f'netsh advfirewall firewall add rule name="{rule_name}" ' 
        f'dir=in program="{exe_path}" action=block enable=yes') 


def unblock_network(rule_name): 
    """删除防火墙规则恢复网络访问（忽略"没有匹配规则"错误）""" 
    run_cmd( 
        f'netsh advfirewall firewall delete rule name="{rule_name}"', 
        ignore_keywords=["没有与指定标准相匹配的规则", "No rules match"] 
    ) 


def main(): 
    exe_path = select_exe_file().replace('/', '\\') 
    rule_name = "Block_YuanShen" 
    total_duration = 480  # 总时长 8 分钟 (8 * 60) 
    elapsed = 0 

    print("🚀 开始断网/联网循环，总时长 8 分钟", flush=True) 

    # 只要累计时间没有达到总时长，就一直循环执行内部的断网/联网序列 
    while elapsed < total_duration: 
        # ---- 开始一个循环周期 ---- 
        if elapsed < total_duration: 
            print(f"\n[{elapsed:>3}s] 断网 15s...", flush=True) 
            block_network(rule_name, exe_path) 
            time.sleep(15) 
            elapsed += 15 

        if elapsed < total_duration: 
            print(f"[{elapsed:>3}s] 恢复网络 30s...", flush=True)  # 修改：130秒改为30秒
            unblock_network(rule_name) 
            time.sleep(30)  # 修改：130秒改为30秒
            elapsed += 30  # 修改：130秒改为30秒
        
        if elapsed < total_duration: 
            print(f"\n[{elapsed:>3}s] 断网 20s...", flush=True) 
            block_network(rule_name, exe_path) 
            time.sleep(20) 
            elapsed += 20 

        if elapsed < total_duration: 
            print(f"[{elapsed:>3}s] 恢复网络 10s...", flush=True) 
            unblock_network(rule_name) 
            time.sleep(10) 
            elapsed += 10 
        
        if elapsed < total_duration: 
            print(f"\n[{elapsed:>3}s] 断网 20s...", flush=True) 
            block_network(rule_name, exe_path) 
            time.sleep(20) 
            elapsed += 20 

        if elapsed < total_duration: 
            print(f"[{elapsed:>3}s] 恢复网络 10s...", flush=True) 
            unblock_network(rule_name) 
            time.sleep(10) 
            elapsed += 10 

        if elapsed < total_duration: 
            print(f"\n[{elapsed:>3}s] 断网 20s...", flush=True) 
            block_network(rule_name, exe_path) 
            time.sleep(20) 
            elapsed += 20 

        if elapsed < total_duration: 
            print(f"[{elapsed:>3}s] 恢复网络 10s...", flush=True) 
            unblock_network(rule_name) 
            time.sleep(10) 
            elapsed += 10 

        if elapsed < total_duration: 
            print(f"\n[{elapsed:>3}s] 断网 20s...", flush=True) 
            block_network(rule_name, exe_path) 
            time.sleep(20) 
            elapsed += 20 

        if elapsed < total_duration: 
            print(f"[{elapsed:>3}s] 恢复网络 10s...", flush=True) 
            unblock_network(rule_name) 
            time.sleep(10) 
            elapsed += 10 
        # ---- 循环周期结束 ---- 


    print("\n🧹 清理防火墙规则，确保网络已恢复...", flush=True) 
    unblock_network(rule_name) 

    print("✅ 脚本执行完成，网络已恢复", flush=True) 
    sys.exit(0) 


if __name__ == "__main__": 
    if os.name != 'nt': 
        print("❌ 此脚本仅支持在 Windows 上运行。", flush=True) 
        sys.exit(1) 
    main() 