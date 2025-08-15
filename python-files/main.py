#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import shutil
import tempfile
import threading
import unicodedata
import subprocess
import webbrowser
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel

try:
    from ttkbootstrap import Style
    from ttkbootstrap.widgets import Button, Label, Combobox, Progressbar
    from ttkbootstrap.scrolled import ScrolledText
    from ttkbootstrap.constants import DISABLED, NORMAL
except Exception:
    print("[错误] 需要安装 ttkbootstrap：pip install ttkbootstrap")
    raise

# ===== 版本配置 =====
VERSION = 1
REMOTE_VERSION_URL = (
    "https://gh.llkk.cc/https://github.com/yijiacloud/xrsdownload/raw/refs/heads/main/vision.txt"
)
MISMATCH_REDIRECT_URL = "https://www.123912.com/s/BlEEjv-fRgMv"

APP_TITLE = "学而思工具箱 - yijia"
PKG_INSTALLER = "com.tal.pad.znxxservice"
TMP_REMOTE_DIR = "/data/local/tmp"


def log_run(cmd, capture_output=True):
    try:
        proc = subprocess.run(cmd, capture_output=capture_output, text=True, check=False)
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return 127, "", f"命令未找到：{cmd[0]}"


def adb_cmd(args, serial=None):
    cmd = ["adb"]
    if serial:
        cmd += ["-s", serial]
    cmd += args
    return cmd


def list_adb_devices():
    rc, out, err = log_run(["adb", "devices"])
    if rc != 0:
        raise RuntimeError(err or out or "adb devices 执行失败")
    devices = []
    for line in out.splitlines()[1:]:
        parts = re.split(r"\s+", line.strip())
        if len(parts) >= 2 and parts[1] == "device":
            devices.append((parts[0], parts[1]))
    return devices


def to_ascii_filename(original: str) -> str:
    stem = Path(original).stem
    suffix = Path(original).suffix.lower()
    ascii_only = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode("ascii")
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", ascii_only)
    if not safe:
        safe = "app"
    if suffix != ".apk":
        suffix = ".apk"
    return safe + suffix


def push_and_install(apk_paths, serial, logger):
    for src in apk_paths:
        src = Path(src)
        if not src.exists():
            logger(f"[跳过] {src} 不存在\n")
            continue
        safe_name = to_ascii_filename(src.name)
        logger(f"\n==> 处理：{src.name} → {safe_name}\n")
        tmpdir = Path(tempfile.mkdtemp(prefix="xes_apk_"))
        local_tmp = tmpdir / safe_name
        try:
            shutil.copy2(src, local_tmp)
        except Exception as e:
            logger(f"[错误] 复制到临时目录失败：{e}\n")
            continue
        remote_path = f"{TMP_REMOTE_DIR}/{safe_name}"
        logger(f"[推送] {local_tmp} → {remote_path}\n")
        rc, out, err = log_run(adb_cmd(["push", str(local_tmp), remote_path], serial))
        if rc != 0:
            logger(f"[失败] push 失败\n{err or out}\n")
            shutil.rmtree(tmpdir, ignore_errors=True)
            continue

        install_args = ["shell", "pm", "install", "-r", "-i", PKG_INSTALLER, remote_path]

        rc, out, err = log_run(adb_cmd(install_args, serial))
        msg = (out or "") + ("\n" + err if err else "")
        if rc == 0 and "Success" in msg:
            logger("[成功] 应用安装成功\n")
        elif "Success" in msg:
            logger("[可能成功] 返回码异常但输出包含 Success\n")
        else:
            logger(f"[失败] 安装失败\n{msg}\n")

        shutil.rmtree(tmpdir, ignore_errors=True)
    logger("\n全部处理完成。\n")


def disable_packages(serial, logger):
    packages = [
        "com.tal.dataupload",
        "com.tal.pad.ota",
        "com.tal.init.ota",
        "com.tal.pad.app_upgrade",
    ]
    for pkg in packages:
        logger(f"[禁用] {pkg}\n")
        rc, out, err = log_run(adb_cmd(["shell", "pm", "disable-user", pkg], serial))
        if rc == 0 and not err:
            logger(f"[成功] {pkg} 已禁用\n")
        else:
            logger(f"[失败] 禁用 {pkg} 失败\n{err or out}\n")


# =================== 主应用 ===================
class App:
    def __init__(self, parent=None):
        if parent:
            self.win = Toplevel(parent)
        else:
            self.win = tk.Tk()
        self.win.title(APP_TITLE)
        self.win.geometry("840x560")
        self.win.minsize(720, 480)

        self.style = Style(theme="flatly")

        Label(self.win, text="ADB 设备：").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.device_box = Combobox(self.win, width=40, state="readonly")
        self.device_box.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        self.btn_refresh = Button(self.win, text="检测设备", command=self.on_refresh)
        self.btn_refresh.grid(row=0, column=2, padx=8, pady=10)

        self.btn_pick = Button(self.win, text="选择 APK（可多选）", command=self.on_pick)
        self.btn_pick.grid(row=0, column=3, padx=8, pady=10)

        self.btn_install = Button(self.win, text="安装到设备", command=self.on_install, state=DISABLED)
        self.btn_install.grid(row=0, column=4, padx=8, pady=10)

        self.btn_optimize = Button(self.win, text="一键优化", command=self.on_optimize, state=DISABLED)
        self.btn_optimize.grid(row=0, column=5, padx=8, pady=10)

        self.log = ScrolledText(self.win, autohide=False, height=24, width=100)
        self.log.grid(row=1, column=0, columnspan=6, padx=12, pady=10, sticky="nsew")

        self.apk_list = []
        self.devices = []
        self.win.grid_columnconfigure(1, weight=1)
        self.win.grid_rowconfigure(1, weight=1)

        self.log_write("欢迎使用 学而思工具箱（作者：yijia）\n")
        self.log_write(f"本地版本：{VERSION}\n")

    def log_write(self, text: str):
        self.log.insert("end", text)
        self.log.see("end")
        self.win.update_idletasks()

    def on_refresh(self):
        self.btn_refresh.configure(state=DISABLED)
        self.log_write("正在检测设备…\n")
        try:
            self.devices = list_adb_devices()
        except Exception as e:
            messagebox.showerror("ADB 错误", str(e))
            self.devices = []
        finally:
            self.btn_refresh.configure(state=NORMAL)

        if not self.devices:
            self.device_box.configure(values=[])
            self.device_box.set("")
            self.log_write("未发现处于 device 状态的设备\n")
            self.btn_install.configure(state=DISABLED)
            self.btn_optimize.configure(state=DISABLED)
            return

        serials = [s for s, st in self.devices]
        self.device_box.configure(values=serials)
        self.device_box.set(serials[0])
        self.log_write(f"发现 {len(serials)} 台设备：{', '.join(serials)}\n")
        self.btn_install.configure(state=NORMAL)
        self.btn_optimize.configure(state=NORMAL)

    def on_pick(self):
        files = filedialog.askopenfilenames(title="选择 APK 文件", filetypes=[("Android 应用包", "*.apk")])
        if files:
            self.apk_list = list(files)
            self.log_write("已选择：\n  - " + "\n  - ".join(self.apk_list) + "\n")
        else:
            self.log_write("未选择任何文件\n")

    def on_install(self):
        if not self.device_box.get():
            messagebox.showwarning("提示", "请先检测并选择一个设备！")
            return
        if not self.apk_list:
            messagebox.showwarning("提示", "请先选择至少一个 APK 文件！")
            return
        self.btn_install.configure(state=DISABLED)
        serial = self.device_box.get()
        threading.Thread(
            target=lambda: (
                push_and_install(self.apk_list, serial, self.log_write),
                self.btn_install.configure(state=NORMAL),
            ),
            daemon=True,
        ).start()

    def on_optimize(self):
        if not self.device_box.get():
            messagebox.showwarning("提示", "请先检测并选择一个设备！")
            return
        root_dir = Path(__file__).parent
        files = [root_dir / f"{i}.apk" for i in range(1, 6)]
        existing = [str(f) for f in files if f.exists()]
        if not existing:
            self.log_write("未找到 1~5.apk 文件\n")
            return
        serial = self.device_box.get()
        self.btn_optimize.configure(state=DISABLED)

        def task():
            push_and_install(existing, serial, self.log_write)
            disable_packages(serial, self.log_write)
            self.btn_optimize.configure(state=NORMAL)

        threading.Thread(target=task, daemon=True).start()

    def run(self):
        self.win.deiconify()
        self.win.mainloop()


# =================== 启动动画 & 版本校验 ===================
class Splash:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("学而思工具箱 正在启动…")
        self.win.geometry("420x240")
        self.win.resizable(False, False)

        self.style = Style(theme="flatly")

        self.label_title = Label(self.win, text="学而思工具箱", font=("Microsoft YaHei", 16, "bold"))
        self.label_title.pack(pady=18)

        self.progress = Progressbar(self.win, mode="indeterminate")
        self.progress.pack(fill="x", padx=28, pady=8)

        self.label_tip = Label(self.win, text="正在准备环境…")
        self.label_tip.pack(pady=6)

        self._tips = ["yijia制作…", "校验版本…", "优化界面…", "连接设备…"]
        self._tip_idx = 0

        self.progress.start(12)
        self._tick()

        # 开线程进行版本检查
        threading.Thread(target=self._check_version_thread, daemon=True).start()
        self.win.mainloop()

    def _tick(self):
        self.label_tip.configure(text=self._tips[self._tip_idx % len(self._tips)])
        self._tip_idx += 1
        self.win.after(500, self._tick)

    def _fetch_remote_version(self) -> int | None:
        """尝试获取远端版本，失败返回 None"""
        try:
            req = Request(REMOTE_VERSION_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=5) as resp:
                data = resp.read().decode("utf-8", errors="ignore")
                m = re.search(r"(-?\d+)", data)
                if m:
                    return int(m.group(1))
        except Exception as e:
            print(f"[版本获取失败] {e}")
            return None
        return None

    def _check_version_thread(self):
        remote = self._fetch_remote_version()
        if remote is None or remote > VERSION:
            # 请求失败或远端版本高 → 强制跳转升级
            action = "redirect"
        else:
            # 本地版本 >= 远端 → 正常进入
            action = "enter"
        self.win.after(0, lambda: self._finish(action, remote))

    def _finish(self, action: str, remote: int | None):
        self.progress.stop()

        def start_app():
            App(self.win).run()

        if action == "enter":
            self.win.withdraw()
            start_app()
            self.win.destroy()
        else:
            # redirect 分支统一处理
            if remote is not None:
                messagebox.showwarning(
                    "版本不匹配",
                    f"检测到远端版本({remote}) 与本地版本({VERSION}) 不一致，正在为您打开页面…",
                )
            else:
                messagebox.showwarning(
                    "版本未知",
                    "未能获取远端版本，已为您打开页面以获取最新信息。",
                )
            webbrowser.open(MISMATCH_REDIRECT_URL, new=2)
            self.win.destroy()
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)

if __name__ == "__main__":
    Splash()
