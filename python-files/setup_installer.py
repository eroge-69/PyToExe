#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إنشاء مثبت لنظام إدارة العيادات والمراكز الطبية
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

def create_installer_script():
    """إنشاء سكريبت المثبت"""
    installer_content = '''@echo off
chcp 65001 > nul
title مثبت نظام إدارة العيادات والمراكز الطبية

echo =======================================
echo مثبت نظام إدارة العيادات والمراكز الطبية
echo المطور: رشاد الشرعبي
echo الهاتف: +967777890990
echo =======================================
echo.

:: التحقق من صلاحيات المدير
net session >nul 2>&1
if %errorLevel% == 0 (
    echo تم التحقق من صلاحيات المدير...
) else (
    echo يتطلب تشغيل المثبت بصلاحيات المدير
    echo يرجى النقر بالزر الأيمن واختيار "تشغيل كمدير"
    pause
    exit /b 1
)

echo.
echo اختر مجلد التثبيت:
echo 1. المجلد الافتراضي: C:\\ClinicSystem
echo 2. مجلد مخصص
echo.
set /p choice="اختر (1 أو 2): "

if "%choice%"=="1" (
    set "install_dir=C:\\ClinicSystem"
) else if "%choice%"=="2" (
    set /p install_dir="أدخل مسار مجلد التثبيت: "
) else (
    echo اختيار غير صحيح
    pause
    exit /b 1
)

echo.
echo سيتم تثبيت النظام في: %install_dir%
echo.
set /p confirm="هل تريد المتابعة؟ (y/n): "
if /i not "%confirm%"=="y" (
    echo تم إلغاء التثبيت
    pause
    exit /b 0
)

echo.
echo جاري إنشاء مجلد التثبيت...
if not exist "%install_dir%" mkdir "%install_dir%"

echo جاري نسخ ملفات النظام...
xcopy /E /I /Y "dist\\*" "%install_dir%\\"

echo جاري إنشاء اختصار على سطح المكتب...
set "desktop=%USERPROFILE%\\Desktop"
set "shortcut=%desktop%\\نظام إدارة العيادات.lnk"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcut%'); $Shortcut.TargetPath = '%install_dir%\\ClinicManagementSystem.exe'; $Shortcut.WorkingDirectory = '%install_dir%'; $Shortcut.Description = 'نظام إدارة العيادات والمراكز الطبية'; $Shortcut.Save()"

echo جاري إنشاء اختصار في قائمة ابدأ...
set "startmenu=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs"
set "startshortcut=%startmenu%\\نظام إدارة العيادات.lnk"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%startshortcut%'); $Shortcut.TargetPath = '%install_dir%\\ClinicManagementSystem.exe'; $Shortcut.WorkingDirectory = '%install_dir%'; $Shortcut.Description = 'نظام إدارة العيادات والمراكز الطبية'; $Shortcut.Save()"

echo.
echo =======================================
echo تم تثبيت النظام بنجاح!
echo =======================================
echo.
echo معلومات التثبيت:
echo - مجلد التثبيت: %install_dir%
echo - اختصار سطح المكتب: تم إنشاؤه
echo - اختصار قائمة ابدأ: تم إنشاؤه
echo.
echo بيانات الدخول الأولي:
echo - اسم المستخدم: Rashad
echo - كلمة المرور: Rashad@733836909@
echo.
echo للدعم الفني:
echo - المطور: رشاد الشرعبي
echo - الهاتف: +967777890990
echo - (للتواصل أو عبر واتساب)
echo.
set /p run="هل تريد تشغيل النظام الآن؟ (y/n): "
if /i "%run%"=="y" (
    start "" "%install_dir%\\ClinicManagementSystem.exe"
)

echo.
echo شكراً لاستخدام نظام إدارة العيادات والمراكز الطبية
pause
'''
    
    with open('installer.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("تم إنشاء ملف installer.bat")

def create_uninstaller():
    """إنشاء أداة إلغاء التثبيت"""
    uninstaller_content = '''@echo off
chcp 65001 > nul
title إلغاء تثبيت نظام إدارة العيادات والمراكز الطبية

echo =======================================
echo إلغاء تثبيت نظام إدارة العيادات والمراكز الطبية
echo المطور: رشاد الشرعبي
echo =======================================
echo.

echo تحذير: سيتم حذف جميع ملفات النظام
echo يُنصح بعمل نسخة احتياطية من البيانات قبل المتابعة
echo.
set /p confirm="هل أنت متأكد من إلغاء التثبيت؟ (y/n): "
if /i not "%confirm%"=="y" (
    echo تم إلغاء العملية
    pause
    exit /b 0
)

echo.
echo جاري إلغاء تثبيت النظام...

:: حذف الاختصارات
echo حذف الاختصارات...
del /f /q "%USERPROFILE%\\Desktop\\نظام إدارة العيادات.lnk" 2>nul
del /f /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\نظام إدارة العيادات.lnk" 2>nul

:: حذف ملفات النظام
echo حذف ملفات النظام...
set "current_dir=%~dp0"
cd /d "%current_dir%\\.."
rmdir /s /q "%current_dir%" 2>nul

echo.
echo تم إلغاء تثبيت النظام بنجاح
echo شكراً لاستخدام نظام إدارة العيادات والمراكز الطبية
pause
'''
    
    dist_dir = Path('dist')
    if dist_dir.exists():
        with open(dist_dir / 'uninstall.bat', 'w', encoding='utf-8') as f:
            f.write(uninstaller_content)
        print("تم إنشاء ملف uninstall.bat")

def create_package():
    """إنشاء حزمة التثبيت المضغوطة"""
    print("إنشاء حزمة التثبيت...")
    
    # إنشاء مجلد الحزمة
    package_dir = Path('package')
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # نسخ ملفات dist
    dist_dir = Path('dist')
    if dist_dir.exists():
        shutil.copytree(dist_dir, package_dir / 'dist')
    
    # نسخ المثبت
    if Path('installer.bat').exists():
        shutil.copy('installer.bat', package_dir)
    
    # إنشاء ملف معلومات الحزمة
    info_content = f"""
نظام إدارة العيادات والمراكز الطبية
=====================================

تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
المطور: رشاد الشرعبي
الهاتف: +967777890990

محتويات الحزمة:
- installer.bat: مثبت النظام
- dist/: ملفات النظام
- README.txt: تعليمات الاستخدام

تعليمات التثبيت:
1. تشغيل installer.bat كمدير
2. اتباع التعليمات على الشاشة
3. استخدام بيانات المطور للدخول الأول

للدعم الفني:
رشاد الشرعبي - +967777890990
(للتواصل أو عبر واتساب)
"""
    
    with open(package_dir / 'معلومات_الحزمة.txt', 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    # إنشاء ملف مضغوط
    zip_name = f'ClinicSystem_Setup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(package_dir)
                zipf.write(file_path, arc_path)
    
    print(f"تم إنشاء حزمة التثبيت: {zip_name}")
    
    # تنظيف مجلد package المؤقت
    shutil.rmtree(package_dir)
    
    return zip_name

def main():
    """الدالة الرئيسية"""
    print("=" * 60)
    print("إعداد مثبت نظام إدارة العيادات والمراكز الطبية")
    print("المطور: رشاد الشرعبي")
    print("=" * 60)
    
    try:
        # التحقق من وجود مجلد dist
        if not Path('dist').exists():
            print("خطأ: مجلد dist غير موجود")
            print("يرجى تشغيل build_exe.py أولاً")
            return 1
        
        # إنشاء المثبت
        create_installer_script()
        create_uninstaller()
        
        # إنشاء الحزمة
        package_name = create_package()
        
        print("\n" + "=" * 60)
        print("تم إعداد المثبت بنجاح!")
        print(f"حزمة التثبيت: {package_name}")
        print("=" * 60)
        
    except Exception as e:
        print(f"خطأ في إعداد المثبت: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

