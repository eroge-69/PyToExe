import os
import time
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def capture_webpage_screenshot():
    # 创建一个简单的tkinter窗口作为主界面
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 提示用户输入URL
    url = simpledialog.askstring("网页截图工具", "请输入要截图的网页URL:")
    
    if not url:
        messagebox.showinfo("提示", "未输入URL，程序退出")
        return
    
    # 确保URL格式正确
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url
    
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # 最大化窗口
    chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--headless")  # 移除无头模式，可能导致截图问题
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    # 指定Chrome浏览器路径
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        messagebox.showerror("错误", f"找不到Chrome浏览器: {chrome_path}")
        return
    
    # 设置Chrome浏览器路径
    chrome_options.binary_location = chrome_path
    
    driver = None
    temp_screenshot_path = "temp_screenshot.png"
    
    try:
        # 初始化WebDriver
        logger.info("初始化WebDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 打开网页
        logger.info(f"打开网页: {url}")
        driver.get(url)
        
        # 等待5秒让页面加载
        messagebox.showinfo("提示", "浏览器已打开网页，正在等待5秒...")
        logger.info("等待5秒让页面加载...")
        time.sleep(5)
        
        # 获取页面总高度和宽度
        logger.info("获取页面尺寸...")
        total_height = (driver.execute_script("return document.body.scrollHeight")+728)
        total_width = (driver.execute_script("return document.body.scrollWidth")+728)
        
        
        # 设置浏览器窗口大小
 #       logger.info(f"设置浏览器窗口大小: {total_width}x{total_height}")
#        driver.set_window_size(total_width, total_height)
        
        # 等待窗口大小调整完成
        time.sleep(1)
        
        # 截图
        logger.info("执行截图...")
        driver.save_screenshot(temp_screenshot_path)
        
        # 关闭浏览器
        logger.info("关闭浏览器...")
        driver.quit()
        
        # 让用户选择保存位置
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG 文件", "*.png"), ("所有文件", "*.*")],
            title="保存截图"
        )
        
        if save_path:
            # 将临时截图移动到用户选择的位置
            logger.info(f"保存截图到: {save_path}")
            with Image.open(temp_screenshot_path) as img:
                img.save(save_path)
            
            # 删除临时文件
            if os.path.exists(temp_screenshot_path):
                os.remove(temp_screenshot_path)
            
            messagebox.showinfo("成功", f"截图已保存至:\n{save_path}")
        else:
            messagebox.showinfo("提示", "未选择保存位置，截图未保存")
            
    except Exception as e:
        error_msg = f"发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        messagebox.showerror("错误", error_msg)
        
        # 确保关闭浏览器
        try:
            if driver:
                driver.quit()
        except:
            pass
        
        # 删除可能存在的临时文件
        if os.path.exists(temp_screenshot_path):
            try:
                os.remove(temp_screenshot_path)
            except:
                pass

if __name__ == "__main__":
    capture_webpage_screenshot()
