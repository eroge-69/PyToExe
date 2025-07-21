#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 安裝腳本
自動安裝所需的依賴項並設定環境
"""

import subprocess
import sys
import os

def install_requirements():
    """安裝所需的Python套件"""
    requirements = [
        'camelot-py[cv]',
        'opencv-python',
        'pandas',
        'openpyxl',
        'pypdf',
        'pdfminer-six',
        'chardet',
        'pypdfium2'
    ]
    
    print("正在安裝所需的Python套件...")
    
    for package in requirements:
        try:
            print(f"安裝 {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ {package} 安裝成功")
        except subprocess.CalledProcessError:
            print(f"✗ {package} 安裝失敗")
            return False
    
    print("\n所有套件安裝完成!")
    return True

def main():
    print("=== PDF 轉 Excel 工具 - Windows 安裝程式 ===\n")
    
    # 檢查Python版本
    if sys.version_info < (3, 7):
        print("錯誤: 需要 Python 3.7 或更高版本")
        print("請從 https://www.python.org/downloads/ 下載並安裝最新版本的Python")
        input("按 Enter 鍵退出...")
        return
    
    print(f"Python 版本: {sys.version}")
    print("開始安裝依賴項...\n")
    
    if install_requirements():
        print("\n安裝完成!")
        print("您現在可以執行 'python pdf_to_excel_gui.py' 來啟動程式")
        print("或者直接雙擊 'run_tool.bat' 檔案")
    else:
        print("\n安裝過程中發生錯誤")
        print("請檢查網路連線並重新執行此腳本")
    
    input("\n按 Enter 鍵退出...")

if __name__ == "__main__":
    main()

