"""
keep-network-gui.py
Windows 11 息屏不断网 一键 GUI 工具（Python + Tkinter）

说明：
- 这个脚本通过调用 powercfg 来应用/恢复电源设置，适用于 Windows 11。
- 请以管理员权限运行此脚本（右键 -> 以管理员身份运行 Python 或者用生成的 EXE 双击右键以管理员权限运行）。
- 若要打包为 EXE：安装 PyInstaller（pip install pyinstaller），然后运行：
    pyinstaller --onefile --windowed keep-network-gui.py

功能：
- 应用“息屏不断网”优化
- 恢复默认/常用设置
- 查看当前关键 powercfg 设置

注意：对系统配置进行修改有风险，脚本会在执行前提示确认。
"""

import os
import sys
import subprocess
import ctypes
import tkinter as tk
from tkinter import messagebox, scrolledtext

# -------------------- 辅助函数 --------------------

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_cmd(cmd):
    """以管理员上下文执行命令并返回 (returncode, stdout, stderr)"""
    try:
        completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return completed.returncode, completed.stdout.strip(), completed.stderr.strip()
    except Exception as e:
        return -1, "", str(e)


# -------------------- powercfg 操作 --------------------

OPT_COMMANDS = [
    ('关闭睡眠（AC）', 'powercfg /change standby-timeout-ac 0'),
    ('关闭睡眠（DC）', 'powercfg /change standby-timeout-dc 0'),
    ('屏幕关闭时间 AC=10', 'powercfg /change monitor-timeout-ac 10'),
    ('屏幕关闭时间 DC=5', 'powercfg /change monitor-timeout-dc 5'),
    # 无线适配器最高性能（请注意：子项 GUID 在不同系统/厂商可能不同，但 sub_wireless 通常可用）
    ('无线适配器最高性能 (AC)', 'powercfg /setacvalueindex scheme_current sub_wireless 001 000'),
    ('无线适配器最高性能 (DC)', 'powercfg /setdcvalueindex scheme_current sub_wireless 001 000'),
    # Connected Standby（如果支持）
    ('启用待机时保持网络(AC)', 'powercfg /setacvalueindex scheme_current sub_sleep standbyconnected 1'),
    ('启用待机时保持网络(DC)', 'powercfg /setdcvalueindex scheme_current sub_sleep standbyconnected 1'),
    # 关闭 PCI-E 链接状态省电
    ('关闭 PCIe 链接省电 (AC)', 'powercfg /setacvalueindex scheme_current sub_pciexpress aspmopt 0'),
    ('关闭 PCIe 链接省电 (DC)', 'powercfg /setdcvalueindex scheme_current sub_pciexpress aspmopt 0'),
    # 禁用混合睡眠
    ('禁用混合睡眠 (AC)', 'powercfg /setacvalueindex scheme_current sub_sleep hybridoff 0'),
    ('禁用混合睡眠 (DC)', 'powercfg /setdcvalueindex scheme_current sub_sleep hybridoff 0'),
    # 关闭休眠以释放空间并避免从休眠恢复中断网络
    ('关闭休眠', 'powercfg -h off'),
    # 应用当前配置
    ('应用电源计划', 'powercfg /setactive scheme_current'),
]


RESTORE_COMMANDS = [
    # 恢复为常见默认值（这些值对不同用户可能不一致；作为保守恢复）
    ('恢复睡眠（AC 30分钟）', 'powercfg /change standby-timeout-ac 30'),
    ('恢复睡眠（DC 15分钟）', 'powercfg /change standby-timeout-dc 15'),
    ('恢复屏幕关闭时间 AC=10', 'powercfg /change monitor-timeout-ac 10'),
    ('恢复屏幕关闭时间 DC=5', 'powercfg /change monitor-timeout-dc 5'),
    ('启用 PCIe 链接省电 (AC)', 'powercfg /setacvalueindex scheme_current sub_pciexpress aspmopt 1'),
    ('启用 PCIe 链接省电 (DC)', 'powercfg /setdcvalueindex scheme_current sub_pciexpress aspmopt 1'),
    ('允许混合睡眠 (AC)', 'powercfg /setacvalueindex scheme_current sub_sleep hybridoff 1'),
    ('允许混合睡眠 (DC)', 'powercfg /setdcvalueindex scheme_current sub_sleep hybridoff 1'),
    ('启用休眠', 'powercfg -h on'),
    ('应用电源计划', 'powercfg /setactive scheme_current'),
]


def apply_optimizations(log_widget):
    if not messagebox.askyesno('确认', '确定要应用息屏不断网优化吗？\n建议在接通电源时执行。'):
        return
    log_widget.delete('1.0', tk.END)
    for desc, cmd in OPT_COMMANDS:
        log_widget.insert(tk.END, f"执行: {desc}\n    {cmd}\n")
        log_widget.see(tk.END)
        code, out, err = run_cmd(cmd)
        if code == 0:
            if out:
                log_widget.insert(tk.END, f"    输出: {out}\n")
        else:
            log_widget.insert(tk.END, f"    失败 (code={code}): {err}\n")
        log_widget.insert(tk.END, "\n")
    messagebox.showinfo('完成', '优化命令已执行完毕。请测试息屏时代理是否继续工作。')


def restore_defaults(log_widget):
    if not messagebox.askyesno('确认', '确定要恢复默认/保守设置吗？'):
        return
    log_widget.delete('1.0', tk.END)
    for desc, cmd in RESTORE_COMMANDS:
        log_widget.insert(tk.END, f"执行: {desc}\n    {cmd}\n")
        code, out, err = run_cmd(cmd)
        if code == 0:
            if out:
                log_widget.insert(tk.END, f"    输出: {out}\n")
        else:
            log_widget.insert(tk.END, f"    失败 (code={code}): {err}\n")
        log_widget.insert(tk.END, "\n")
    messagebox.showinfo('完成', '恢复命令已执行完毕。')


def query_status(log_widget):
    """查询一些关键 powercfg 设置并显示"""
    log_widget.delete('1.0', tk.END)
    queries = [
        ('当前电源方案 GUID', 'powercfg /getactivescheme'),
        ('睡眠超时(AC)', 'powercfg /q | findstr /i "Standby" || powercfg /q'),
        ('无线适配器设置', 'powercfg /energy'),
    ]
    # 注意: powercfg /q 输出复杂，这里只尝试运行并显示部分信息
    for desc, cmd in queries:
        log_widget.insert(tk.END, f"查询: {desc}\n    {cmd}\n")
        log_widget.see(tk.END)
        code, out, err = run_cmd(cmd)
        if code == 0:
            if out:
                # 截断太长的输出
                if len(out) > 8000:
                    out = out[:8000] + '\n...[输出被截断]'
                log_widget.insert(tk.END, f"    输出:\n{out}\n")
        else:
            log_widget.insert(tk.END, f"    查询失败 (code={code}): {err}\n")
        log_widget.insert(tk.END, "\n")


# -------------------- GUI --------------------

def create_gui():
    root = tk.Tk()
    root.title('息屏不断网 - Windows 优化工具')
    root.geometry('720x520')

    frm_top = tk.Frame(root, pady=8)
    frm_top.pack(fill=tk.X)

    lbl = tk.Label(frm_top, text='说明：以管理员权限运行。点击“应用优化”后会执行一系列 powercfg 命令。', anchor='w')
    lbl.pack(fill=tk.X, padx=10)

    frm_btn = tk.Frame(root, pady=6)
    frm_btn.pack(fill=tk.X)

    btn_apply = tk.Button(frm_btn, text='应用优化', width=16, command=lambda: apply_optimizations(txt_log))
    btn_apply.pack(side=tk.LEFT, padx=10)

    btn_restore = tk.Button(frm_btn, text='恢复默认/保守', width=16, command=lambda: restore_defaults(txt_log))
    btn_restore.pack(side=tk.LEFT, padx=10)

    btn_query = tk.Button(frm_btn, text='查看当前设置', width=16, command=lambda: query_status(txt_log))
    btn_query.pack(side=tk.LEFT, padx=10)

    btn_about = tk.Button(frm_btn, text='关于/帮助', width=12, command=lambda: messagebox.showinfo('关于', '息屏不断网优化工具\n作者: 自动生成脚本\n请以管理员身份运行。'))
    btn_about.pack(side=tk.RIGHT, padx=10)

    # 日志区
    frm_log = tk.Frame(root)
    frm_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

    txt_log = scrolledtext.ScrolledText(frm_log, wrap=tk.WORD)
    txt_log.pack(fill=tk.BOTH, expand=True)

    # 启动时检测管理员权限
    if not is_admin():
        messagebox.showwarning('权限不足', '本程序需要管理员权限才能修改电源设置。\n请以管理员身份重新运行。')
        txt_log.insert(tk.END, '警告：当前不是管理员，部分命令可能失败。\n')

    root.mainloop()


if __name__ == '__main__':
    if sys.platform != 'win32':
        print('此脚本仅适用于 Windows。')
        sys.exit(1)

    create_gui()
