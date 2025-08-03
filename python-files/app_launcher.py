#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة العيادات والمراكز الطبية
تطبيق سطح المكتب

المطور: رشاد الشرعبي
الهاتف: +967777890990
"""

import os
import sys
import threading
import time
import webbrowser
import socket
from pathlib import Path

# إضافة مجلد src إلى مسار Python
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# استيراد التطبيق
from main import app

def find_free_port():
    """البحث عن منفذ متاح"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def open_browser(port):
    """فتح المتصفح بعد تشغيل الخادم"""
    time.sleep(2)  # انتظار تشغيل الخادم
    url = f'http://localhost:{port}'
    webbrowser.open(url)

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    print("=" * 60)
    print("نظام إدارة العيادات والمراكز الطبية")
    print("المطور: رشاد الشرعبي")
    print("الهاتف: +967777890990")
    print("=" * 60)
    
    # البحث عن منفذ متاح
    port = find_free_port()
    print(f"تشغيل النظام على المنفذ: {port}")
    
    # فتح المتصفح في خيط منفصل
    browser_thread = threading.Thread(target=open_browser, args=(port,))
    browser_thread.daemon = True
    browser_thread.start()
    
    # تشغيل التطبيق
    try:
        app.run(
            host='127.0.0.1',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\nتم إيقاف النظام بواسطة المستخدم")
    except Exception as e:
        print(f"خطأ في تشغيل النظام: {e}")
        input("اضغط Enter للخروج...")

if __name__ == '__main__':
    main()

