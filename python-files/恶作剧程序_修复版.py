#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐊 小鳄鱼的恶作剧程序 - 修复版
作者: Amidon
修复者: 铃月 (Suzuki) 🐱
功能: 不停播放音频 + 不停弹出图片 + 强制最大音量
依赖: pygame, Pillow, numpy (自动安装)

使用方法:
1. 确保 wodefumusile.mp3 和 wululu.jpg 在同一目录
2. 运行: python 恶作剧程序_修复版.py
3. 按 Ctrl+C 停止程序

警告: 仅供娱乐，请在安全环境中使用！

修复内容:
- 修复了窗口内存泄漏问题
- 改善了线程安全性
- 优化了资源管理
- 增强了错误处理
"""

import sys
import os
import subprocess
import time
import threading
import tkinter as tk
from tkinter import messagebox
import platform
import queue
import random

# 自动安装依赖
def install_dependencies():
    """自动安装必要的依赖包"""
    required_packages = ['pygame', 'Pillow', 'numpy']
    
    for package in required_packages:
        try:
            __import__(package if package != 'Pillow' else 'PIL')
        except ImportError:
            print(f"🔧 正在安装 {package}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError:
                print(f"❌ {package} 安装失败，请手动安装")
                return False
    return True

# 安装依赖
if not install_dependencies():
    print("❌ 依赖安装失败，程序退出")
    sys.exit(1)

# 导入依赖
try:
    import pygame
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    import numpy as np
    import wave
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

class PrankProgram:
    def __init__(self):
        self.running = True
        self.audio_file = "wodefumusile.mp3"
        self.image_file = "wululu.jpg"
        self.popup_windows = []  # 存储弹窗引用，便于管理
        self.max_popups = 50  # 限制最大弹窗数量，防止内存溢出
        self.popup_queue = queue.Queue()  # 线程安全的队列
        
        # 初始化pygame音频
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"⚠️ 音频初始化失败: {e}")
        
        # 设置最大音量
        self.set_max_volume()
        
    def set_max_volume(self):
        """设置系统音量为最大"""
        try:
            system = platform.system()
            if system == "Windows":
                # Windows系统设置音量 - 优化版本
                subprocess.run([
                    "powershell", 
                    "-Command", 
                    "Add-Type -TypeDefinition 'using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, uint dwExtraInfo); }'; for($i=0; $i -lt 50; $i++) { [Win32]::keybd_event(0xAF, 0, 0, 0); [Win32]::keybd_event(0xAF, 0, 2, 0); Start-Sleep -Milliseconds 10 }"
                ], check=False, capture_output=True, timeout=5)
            elif system == "Darwin":  # macOS
                subprocess.run(["osascript", "-e", "set volume output volume 100"], 
                             check=False, capture_output=True, timeout=5)
            elif system == "Linux":
                subprocess.run(["amixer", "set", "Master", "100%"], 
                             check=False, capture_output=True, timeout=5)
        except Exception:
            pass  # 静默失败
    
    def create_sample_audio(self):
        """创建示例音频文件（如果不存在）"""
        try:
            # 生成440Hz的正弦波（A音）
            sample_rate = 44100
            duration = 2  # 2秒
            frequency = 440
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
            
            # 转换为16位整数
            audio_data = (audio_data * 32767).astype(np.int16)
            
            # 保存为WAV文件（pygame支持）
            wav_file = "wodefumusile.wav"
            with wave.open(wav_file, 'w') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                wav.writeframes(audio_data.tobytes())
            
            self.audio_file = wav_file
            print("🎵 已自动生成示例音频文件")
            
        except Exception as e:
            print(f"⚠️ 音频文件创建失败: {e}")
    
    def play_audio_loop(self):
        """循环播放音频"""
        if not os.path.exists(self.audio_file):
            print(f"🎵 音频文件 {self.audio_file} 不存在，创建示例文件...")
            self.create_sample_audio()
        
        try:
            if os.path.exists(self.audio_file):
                pygame.mixer.music.load(self.audio_file)
                pygame.mixer.music.play(-1)  # -1表示无限循环
                
                while self.running:
                    if not pygame.mixer.music.get_busy():
                        pygame.mixer.music.play(-1)
                    time.sleep(0.1)
        except Exception as e:
            print(f"⚠️ 音频播放失败: {e}")
    
    def create_sample_image(self):
        """创建示例图片文件（如果不存在）"""
        try:
            # 创建一个彩色图片
            img = Image.new('RGB', (400, 400), color='lightblue')
            draw = ImageDraw.Draw(img)
            
            # 绘制一些图形
            draw.ellipse([50, 50, 350, 350], fill='yellow', outline='red', width=5)
            draw.rectangle([150, 150, 250, 250], fill='green')
            
            # 添加文字
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            draw.text((200, 200), "WULULU", fill='black', anchor='mm', font=font)
            draw.text((200, 250), "小鳄鱼", fill='red', anchor='mm', font=font)
            
            img.save(self.image_file)
            print("🖼️ 已自动生成示例图片文件")
            
        except Exception as e:
            print(f"⚠️ 图片文件创建失败: {e}")
    
    def cleanup_old_popups(self):
        """清理旧的弹窗，防止内存泄漏"""
        try:
            # 移除已经被销毁的窗口引用
            self.popup_windows = [popup for popup in self.popup_windows 
                                if popup.winfo_exists()]
            
            # 如果弹窗数量超过限制，关闭最旧的
            while len(self.popup_windows) > self.max_popups:
                old_popup = self.popup_windows.pop(0)
                try:
                    old_popup.destroy()
                except:
                    pass
        except Exception:
            # 如果清理失败，重置列表
            self.popup_windows = []
    
    def create_popup_window(self, popup_count):
        """创建单个弹窗窗口"""
        try:
            # 创建新的窗口
            popup = tk.Toplevel()
            popup.title(f"wululu #{popup_count}")
            popup.attributes('-topmost', True)  # 置顶显示
            
            # 随机位置，确保在屏幕范围内
            screen_width = popup.winfo_screenwidth()
            screen_height = popup.winfo_screenheight()
            x = random.randint(0, max(0, screen_width - 300))
            y = random.randint(0, max(0, screen_height - 300))
            popup.geometry(f"300x300+{x}+{y}")
            
            # 加载并显示图片
            try:
                if os.path.exists(self.image_file):
                    image = Image.open(self.image_file)
                    image = image.resize((280, 280), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    
                    label = tk.Label(popup, image=photo)
                    label.image = photo  # 保持引用
                    label.pack()
                else:
                    raise FileNotFoundError("图片文件不存在")
            except Exception:
                # 如果图片加载失败，显示文字
                label = tk.Label(popup, text="WULULU!", 
                               font=("Arial", 16), fg="red")
                label.pack(expand=True)
            
            # 防止窗口被关闭
            popup.protocol("WM_DELETE_WINDOW", lambda: None)
            
            # 添加到窗口列表
            self.popup_windows.append(popup)
            
            # 设置窗口自动销毁时间（10秒后）
            popup.after(10000, lambda: self.safe_destroy_popup(popup))
            
        except Exception as e:
            print(f"⚠️ 创建弹窗失败: {e}")
    
    def safe_destroy_popup(self, popup):
        """安全销毁弹窗"""
        try:
            if popup in self.popup_windows:
                self.popup_windows.remove(popup)
            popup.destroy()
        except Exception:
            pass
    
    def schedule_popup_creation(self, root):
        """在主线程中安排弹窗创建"""
        if not self.running:
            return
            
        if not os.path.exists(self.image_file):
            print(f"🖼️ 图片文件 {self.image_file} 不存在，创建示例文件...")
            self.create_sample_image()
        
        try:
            # 清理旧弹窗
            self.cleanup_old_popups()
            
            # 创建新弹窗
            popup_count = len(self.popup_windows)
            self.create_popup_window(popup_count)
            
        except Exception as e:
            print(f"⚠️ 弹窗创建异常: {e}")
        
        # 安排下一次弹窗创建（800毫秒后）
        if self.running:
            root.after(100, lambda: self.schedule_popup_creation(root))
    
    def start_prank(self):
        """启动恶作剧程序"""
        print("=" * 50)
        
        # 创建主窗口（隐藏）
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 设置信号处理器
        self.setup_signal_handler(root)
        
        # 启动音频播放线程
        audio_thread = threading.Thread(target=self.play_audio_loop, daemon=True)
        audio_thread.start()
        
        # 在主线程中安排第一个弹窗创建
        root.after(1000, lambda: self.schedule_popup_creation(root))  # 1秒后开始
        
        try:
            # 保持程序运行 - 使用mainloop而不是手动update
            root.mainloop()
                    
        except KeyboardInterrupt:
            print("\n🛑 正在停止程序...")
            self.stop_prank()
        except Exception as e:
            print(f"⚠️ 程序异常: {e}")
            self.stop_prank()
        finally:
            try:
                root.destroy()
            except:
                pass
    
    def stop_prank(self, root=None):
        """停止程序"""
        self.running = False
        
        # 停止音频
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass
        
        # 关闭所有弹窗
        try:
            for popup in self.popup_windows:
                try:
                    popup.destroy()
                except:
                    pass
            self.popup_windows.clear()
        except:
            pass
        
        # 退出主循环
        if root:
            try:
                root.quit()
            except:
                pass
            
        print("✅ 恶作剧程序已停止！")
    
    def setup_signal_handler(self, root):
        """设置信号处理器来处理Ctrl+C"""
        import signal
        
        def signal_handler(signum, frame):
            print("🛑 检测到中断信号，正在停止恶作剧程序...")
            self.stop_prank(root)
        
        signal.signal(signal.SIGINT, signal_handler)

def main():
    """主函数"""
    print("⚠️  程序会调至最大音量！")
    print("=" * 50)
    
    # 检查文件
    audio_exists = os.path.exists("wodefumusile.mp3") or os.path.exists("wodefumusile.wav")
    image_exists = os.path.exists("wululu.jpg")
    
    print(f"🎵 音频文件: {'✅ 存在' if audio_exists else '❌ 不存在（将自动生成）'}")
    print(f"🖼️ 图片文件: {'✅ 存在' if image_exists else '❌ 不存在（将自动生成）'}")
    print()
    
    # 启动程序
    try:
        prank = PrankProgram()
        prank.start_prank()
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()