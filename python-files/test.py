from flask import Flask, render_template_string
import webbrowser
import os
import sys
import time

app = Flask(__name__)

   # صفحه HTML ساده
html_content = """
   <!DOCTYPE html>
   <html lang="fa">
   <head>
       <meta charset="UTF-8">
       <title>برنامه لوکال پایتون</title>
       <style>
           body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
           h1 { color: #333; }
           p { font-size: 18px; }
       </style>
   </head>
   <body>
       <h1>خوش آمدید!</h1>
       <p>این برنامه با کلیک روی فایل اجرایی در کروم باز شده است.</p>
   </body>
   </html>
   """

@app.route('/')
def home():
       return render_template_string(html_content)

if __name__ == '__main__':
       # باز کردن مرورگر کروم
       chrome_path = None
       if sys.platform.startswith('win'):
           # مسیر پیش‌فرض کروم در ویندوز
           chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
       elif sys.platform.startswith('darwin'):
           # مسیر پیش‌فرض کروم در مک
           chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
       elif sys.platform.startswith('linux'):
           # مسیر پیش‌فرض کروم در لینوکس
           chrome_path = "google-chrome"

       try:
           # باز کردن مرورگر کروم با آدرس لوکال
           if chrome_path and os.path.exists(chrome_path):
               webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
               webbrowser.get('chrome').open('http://localhost:5000')
           else:
               # اگر کروم پیدا نشد، مرورگر پیش‌فرض باز می‌شود
               webbrowser.open('http://localhost:5000')
       except Exception as e:
           print(f"خطا در باز کردن مرورگر: {e}")

       # اجرای سرور Flask
       app.run(host='localhost', port=5000, debug=False)