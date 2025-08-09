#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف إعداد تحويل البرنامج إلى EXE
نظام إدارة تأجير الشقق والفواتير
"""

import sys
import os
from cx_Freeze import setup, Executable

# إعدادات البناء المحسنة
build_exe_options = {
    "packages": [
        "PyQt5", 
        "PyQt5.QtCore", 
        "PyQt5.QtGui", 
        "PyQt5.QtWidgets",
        "sqlite3", 
        "datetime", 
        "os", 
        "sys",
        "ui",  # إضافة مجلد ui
        "database"  # إضافة ملف database
    ],
    "excludes": [
        "tkinter", 
        "matplotlib", 
        "numpy", 
        "scipy",
        "test",
        "unittest",
        "email",
        "http",
        "urllib",
        "xml",
        "pydoc",
        "doctest",
        "argparse"
    ],
    "include_files": [
        ("assets/", "assets/"),
        ("ui/", "ui/"),
        ("database.py", "database.py"),
        # إضافة قاعدة البيانات إذا كانت موجودة
        ("rental_management.db", "rental_management.db") if os.path.exists("rental_management.db") else None,
        # إضافة ملفات Excel إذا كانت موجودة
        ("5عمائر.xls", "5عمائر.xls") if os.path.exists("5عمائر.xls") else None,
        ("5عمائر.xlsm", "5عمائر.xlsm") if os.path.exists("5عمائر.xlsm") else None,
    ],
    "include_msvcrt": True,  # تضمين مكتبات Visual C++
    "optimize": 2,
    "build_exe": "dist/RentalManagement",  # مجلد الإخراج
}

# تنظيف القائمة من العناصر الفارغة
build_exe_options["include_files"] = [f for f in build_exe_options["include_files"] if f is not None]

# إعدادات الملف التنفيذي
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # لإخفاء نافذة الكونسول في Windows

# معلومات البرنامج
setup(
    name="RentalManagement",
    version="1.0.0",
    description="نظام شامل لإدارة عقود الإيجار والفواتير والمدفوعات",
    author="نظام إدارة العقارات",
    author_email="",
    url="",
    license="MIT",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="RentalManagement.exe",
            icon="assets/icon.ico" if os.path.exists("assets/icon.ico") else None,
            shortcut_name="نظام إدارة تأجير الشقق",
            shortcut_dir="DesktopFolder",
        )
    ],
)