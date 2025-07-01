#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arabic File Combiner Pro - AI & Developer Enhanced Version
دمج الملفات العربي المطور - نسخة محسنة للمطورين والذكاء الاصطناعي
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import datetime
import threading
import subprocess
import platform
import json
import re
from pathlib import Path
import zipfile
import base64

class ProArabicFileCombiner:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.create_enhanced_ui()
        self.load_settings()
        
    def setup_window(self):
        """إعداد النافذة المحسنة"""
        self.root.title("دمج الملفات العربي Pro - للمطورين والذكاء الاصطناعي")
        self.root.geometry("1100x800")
        self.root.configure(bg='#1e1e1e')  # Dark theme
        
        # خطوط محسنة
        self.default_font = ('Segoe UI', 10)
        self.title_font = ('Segoe UI', 16, 'bold')
        self.button_font = ('Segoe UI', 9)
        self.code_font = ('Consolas', 9)
        
        # ألوان محسنة (Dark Theme)
        self.colors = {
            'bg_primary': '#1e1e1e',
            'bg_secondary': '#2d2d30', 
            'bg_card': '#3c3c3c',
            'accent_blue': '#007acc',
            'accent_green': '#4ec9b0',
            'accent_orange': '#ce9178',
            'accent_red': '#f44747',
            'accent_purple': '#c586c0',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'text_muted': '#808080'
        }
        
    def setup_variables(self):
        """إعداد المتغيرات المحسنة"""
        self.selected_files = []
        self.selected_folders = []
        self.output_location = str(Path.home() / "Desktop")
        self.processing = False
        
        # إعدادات AI
        self.ai_mode = tk.BooleanVar(value=True)
        self.remove_comments = tk.BooleanVar(value=False)
        self.add_context = tk.BooleanVar(value=True)
        self.split_large_files = tk.BooleanVar(value=True)
        self.include_structure = tk.BooleanVar(value=True)
        
        # إعدادات المطورين
        self.exclude_common = tk.BooleanVar(value=True)
        self.analyze_code = tk.BooleanVar(value=True)
        self.extract_todos = tk.BooleanVar(value=False)
        self.show_stats = tk.BooleanVar(value=True)
        
        # فلاتر الملفات
        self.file_filters = {
            'node_modules': True,
            '.git': True,
            'dist': True,
            'build': True,
            '.env': True,
            'vendor': True,
            '__pycache__': True
        }
        
    def create_enhanced_ui(self):
        """إنشاء واجهة محسنة للمطورين"""
        
        # الحاوية الرئيسية
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # العنوان المحسن
        self.create_header(main_container)
        
        # شريط التبويب المحسن
        self.create_enhanced_notebook(main_container)
        
        # شريط الحالة المحسن
        self.create_enhanced_status(main_container)
        
    def create_header(self, parent):
        """رأس محسن مع معلومات سريعة"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_card'], pady=20)
        header_frame.pack(fill='x', pady=(0, 15))
        
        # العنوان مع أيقونة
        title_frame = tk.Frame(header_frame, bg=self.colors['bg_card'])
        title_frame.pack()
        
        title_label = tk.Label(title_frame,
                              text="🚀 دمج الملفات العربي Pro",
                              font=self.title_font,
                              bg=self.colors['bg_card'],
                              fg=self.colors['text_primary'])
        title_label.pack(side='left')
        
        version_label = tk.Label(title_frame,
                                text="v4.0 AI Enhanced",
                                font=('Segoe UI', 10),
                                bg=self.colors['bg_card'],
                                fg=self.colors['accent_blue'])
        version_label.pack(side='left', padx=(10, 0))
        
        # وصف سريع
        desc_label = tk.Label(header_frame,
                             text="أداة متطورة للمطورين | تجهيز الملفات للذكاء الاصطناعي | تحليل الكود",
                             font=self.default_font,
                             bg=self.colors['bg_card'],
                             fg=self.colors['text_secondary'])
        desc_label.pack(pady=(5, 0))
        
    def create_enhanced_notebook(self, parent):
        """تبويبات محسنة مع ميزات متقدمة"""
        # إنشاء Notebook مخصص
        notebook_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        notebook_frame.pack(fill='both', expand=True)
        
        # شريط التبويبات
        self.create_custom_tabs(notebook_frame)
        
        # محتوى التبويبات
        self.tab_content_frame = tk.Frame(notebook_frame, bg=self.colors['bg_secondary'])
        self.tab_content_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # إنشاء محتوى كل تبويب
        self.create_quick_tab_content()
        self.create_ai_tab_content()
        self.create_dev_tab_content()
        self.create_analysis_tab_content()
        
        # عرض التبويب الأول
        self.show_tab('quick')
        
    def create_custom_tabs(self, parent):
        """شريط تبويبات مخصص"""
        tabs_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        tabs_frame.pack(fill='x')
        
        self.active_tab = 'quick'
        self.tab_buttons = {}
        
        tabs = [
            ('quick', '⚡ سريع', self.colors['accent_blue']),
            ('ai', '🤖 AI Ready', self.colors['accent_green']),
            ('dev', '👨‍💻 المطورين', self.colors['accent_purple']),
            ('analysis', '📊 تحليل', self.colors['accent_orange'])
        ]
        
        for tab_id, text, color in tabs:
            btn = tk.Button(tabs_frame,
                           text=text,
                           font=self.button_font,
                           bg=color if tab_id == self.active_tab else self.colors['bg_card'],
                           fg=self.colors['text_primary'],
                           relief='flat',
                           pady=12,
                           command=lambda t=tab_id: self.show_tab(t),
                           cursor='hand2')
            btn.pack(side='left', fill='x', expand=True, padx=1)
            self.tab_buttons[tab_id] = btn
            
    def show_tab(self, tab_id):
        """عرض تبويب محدد"""
        self.active_tab = tab_id
        
        # تحديث ألوان الأزرار
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                colors = {
                    'quick': self.colors['accent_blue'],
                    'ai': self.colors['accent_green'], 
                    'dev': self.colors['accent_purple'],
                    'analysis': self.colors['accent_orange']
                }
                btn.config(bg=colors[tid])
            else:
                btn.config(bg=self.colors['bg_card'])
                
        # إخفاء جميع المحتويات
        for child in self.tab_content_frame.winfo_children():
            child.pack_forget()
            
        # عرض المحتوى المطلوب
        if hasattr(self, f'{tab_id}_content'):
            getattr(self, f'{tab_id}_content').pack(fill='both', expand=True, padx=15, pady=15)
            
    def create_quick_tab_content(self):
        """محتوى التبويب السريع"""
        self.quick_content = tk.Frame(self.tab_content_frame, bg=self.colors['bg_secondary'])
        
        # قسم الخيارات السريعة المحسن
        quick_frame = tk.LabelFrame(self.quick_content,
                                   text="⚡ خيارات سريعة محسنة",
                                   font=self.default_font,
                                   bg=self.colors['bg_card'],
                                   fg=self.colors['text_primary'],
                                   padx=20, pady=15)
        quick_frame.pack(fill='x', pady=(0, 15))
        
        # وصف محسن
        desc_label = tk.Label(quick_frame,
                             text="اختر من الخيارات التالية للبدء السريع مع ميزات محسنة:",
                             font=self.default_font,
                             bg=self.colors['bg_card'],
                             fg=self.colors['text_secondary'],
                             wraplength=600)
        desc_label.pack(pady=(0, 15))
        
        # أزرار محسنة مع أيقونات ووصف
        buttons_data = [
            {
                'text': '🗂️ مشروع كامل للـ AI',
                'desc': 'دمج مشروع كامل وتحسينه للـ AI مع إزالة الملفات غير المهمة',
                'color': self.colors['accent_green'],
                'command': self.ai_project_combo
            },
            {
                'text': '📄 ملفات مختارة + تحليل',
                'desc': 'اختيار ملفات محددة مع تحليل الكود وإحصائيات مفصلة',
                'color': self.colors['accent_blue'],
                'command': self.smart_files_combo
            },
            {
                'text': '⚡ مجلد سريع مطور',
                'desc': 'دمج المجلد الحالي مع فلترة ذكية وتحسين للمطورين',
                'color': self.colors['accent_orange'],
                'command': self.dev_folder_combo
            }
        ]
        
        for btn_data in buttons_data:
            self.create_enhanced_button(quick_frame, btn_data)
            
        # منطقة النتائج المحسنة
        self.create_results_area(self.quick_content)
        
    def create_ai_tab_content(self):
        """محتوى تبويب AI Ready"""
        self.ai_content = tk.Frame(self.tab_content_frame, bg=self.colors['bg_secondary'])
        
        # إعدادات AI
        ai_settings_frame = tk.LabelFrame(self.ai_content,
                                         text="🤖 إعدادات تحسين للذكاء الاصطناعي",
                                         font=self.default_font,
                                         bg=self.colors['bg_card'],
                                         fg=self.colors['text_primary'],
                                         padx=20, pady=15)
        ai_settings_frame.pack(fill='x', pady=(0, 15))
        
        # خيارات AI في شبكة
        ai_options_frame = tk.Frame(ai_settings_frame, bg=self.colors['bg_card'])
        ai_options_frame.pack(fill='x')
        
        # العمود الأول
        col1 = tk.Frame(ai_options_frame, bg=self.colors['bg_card'])
        col1.pack(side='left', fill='both', expand=True)
        
        self.create_styled_checkbox(col1, "إضافة context للملفات", self.add_context,
                                   "إضافة معلومات السياق لكل ملف (نوع، حجم، وظيفة)")
        
        self.create_styled_checkbox(col1, "تقسيم الملفات الكبيرة", self.split_large_files,
                                   "تقسيم الملفات التي تتجاوز حد معين لتجنب حدود AI")
        
        self.create_styled_checkbox(col1, "إزالة التعليقات غير المفيدة", self.remove_comments,
                                   "إزالة console.log, debug comments, TODO القديمة")
        
        # العمود الثاني
        col2 = tk.Frame(ai_options_frame, bg=self.colors['bg_card'])
        col2.pack(side='left', fill='both', expand=True, padx=(20, 0))
        
        self.create_styled_checkbox(col2, "إنشاء هيكل المشروع", self.include_structure,
                                   "إضافة مخطط شجري للمشروع في بداية الملف")
        
        self.create_styled_checkbox(col2, "تحسين للـ ChatGPT/Claude", self.ai_mode,
                                   "تنسيق خاص محسن للذكاء الاصطناعي")
        
        # قسم تخصيص AI
        ai_custom_frame = tk.LabelFrame(self.ai_content,
                                       text="⚙️ تخصيص متقدم للـ AI",
                                       font=self.default_font,
                                       bg=self.colors['bg_card'],
                                       fg=self.colors['text_primary'],
                                       padx=20, pady=15)
        ai_custom_frame.pack(fill='x', pady=(0, 15))
        
        # حد حجم الملف
        size_frame = tk.Frame(ai_custom_frame, bg=self.colors['bg_card'])
        size_frame.pack(fill='x', pady=5)
        
        tk.Label(size_frame, text="الحد الأقصى لحجم الملف (KB):",
                font=self.default_font, bg=self.colors['bg_card'],
                fg=self.colors['text_secondary']).pack(side='left')
        
        self.max_file_size_var = tk.StringVar(value="100")
        size_entry = tk.Entry(size_frame, textvariable=self.max_file_size_var,
                             font=self.default_font, width=10, bg=self.colors['bg_secondary'],
                             fg=self.colors['text_primary'], insertbackground=self.colors['text_primary'])
        size_entry.pack(side='left', padx=(10, 0))
        
        # نوع AI المستهدف
        ai_type_frame = tk.Frame(ai_custom_frame, bg=self.colors['bg_card'])
        ai_type_frame.pack(fill='x', pady=10)
        
        tk.Label(ai_type_frame, text="نوع AI المستهدف:",
                font=self.default_font, bg=self.colors['bg_card'],
                fg=self.colors['text_secondary']).pack(side='left')
        
        self.ai_target = tk.StringVar(value="general")
        ai_types = [("عام", "general"), ("ChatGPT", "chatgpt"), ("Claude", "claude"), ("Gemini", "gemini")]
        
        for text, value in ai_types:
            tk.Radiobutton(ai_type_frame, text=text, variable=self.ai_target, value=value,
                          font=self.default_font, bg=self.colors['bg_card'],
                          fg=self.colors['text_secondary'], selectcolor=self.colors['bg_secondary'],
                          activebackground=self.colors['bg_card']).pack(side='left', padx=10)
        
        # أزرار AI
        ai_buttons_frame = tk.Frame(ai_custom_frame, bg=self.colors['bg_card'])
        ai_buttons_frame.pack(fill='x', pady=15)
        
        ai_buttons = [
            ("🤖 تحضير للـ AI", self.colors['accent_green'], self.prepare_for_ai),
            ("📋 نسخ للحافظة", self.colors['accent_blue'], self.copy_to_clipboard),
            ("🔗 إنشاء رابط مشاركة", self.colors['accent_purple'], self.create_share_link)
        ]
        
        for text, color, command in ai_buttons:
            btn = tk.Button(ai_buttons_frame, text=text, font=self.button_font,
                           bg=color, fg=self.colors['text_primary'], pady=10,
                           command=command, cursor='hand2', relief='flat')
            btn.pack(side='left', fill='x', expand=True, padx=2)
            
    def create_dev_tab_content(self):
        """محتوى تبويب المطورين"""
        self.dev_content = tk.Frame(self.tab_content_frame, bg=self.colors['bg_secondary'])
        
        # أدوات المطورين
        dev_tools_frame = tk.LabelFrame(self.dev_content,
                                       text="👨‍💻 أدوات المطورين المتقدمة",
                                       font=self.default_font,
                                       bg=self.colors['bg_card'],
                                       fg=self.colors['text_primary'],
                                       padx=20, pady=15)
        dev_tools_frame.pack(fill='x', pady=(0, 15))
        
        # خيارات المطورين
        dev_options_frame = tk.Frame(dev_tools_frame, bg=self.colors['bg_card'])
        dev_options_frame.pack(fill='x')
        
        # العمود الأول
        dev_col1 = tk.Frame(dev_options_frame, bg=self.colors['bg_card'])
        dev_col1.pack(side='left', fill='both', expand=True)
        
        self.create_styled_checkbox(dev_col1, "استبعاد المجلدات الشائعة", self.exclude_common,
                                   "تجاهل node_modules, .git, dist, build تلقائياً")
        
        self.create_styled_checkbox(dev_col1, "تحليل الكود", self.analyze_code,
                                   "إحصائيات مفصلة: عدد الأسطر، الدوال، الكلاسات")
        
        # العمود الثاني  
        dev_col2 = tk.Frame(dev_options_frame, bg=self.colors['bg_card'])
        dev_col2.pack(side='left', fill='both', expand=True, padx=(20, 0))
        
        self.create_styled_checkbox(dev_col2, "استخراج TODO/FIXME", self.extract_todos,
                                   "جمع جميع المهام والملاحظات من الكود")
        
        self.create_styled_checkbox(dev_col2, "عرض الإحصائيات", self.show_stats,
                                   "عرض ملخص شامل للمشروع")
        
        # فلاتر الملفات القابلة للتخصيص
        filters_frame = tk.LabelFrame(self.dev_content,
                                     text="🔍 فلاتر الملفات المتقدمة",
                                     font=self.default_font,
                                     bg=self.colors['bg_card'],
                                     fg=self.colors['text_primary'],
                                     padx=20, pady=15)
        filters_frame.pack(fill='x', pady=(0, 15))
        
        # قائمة الفلاتر
        filters_grid = tk.Frame(filters_frame, bg=self.colors['bg_card'])
        filters_grid.pack(fill='x')
        
        filters_list = [
            ("node_modules", "Node.js modules"),
            (".git", "Git repository"),
            ("dist/build", "Build output"),
            ("vendor", "Vendor libraries"),
            ("__pycache__", "Python cache"),
            (".env", "Environment files")
        ]
        
        row = 0
        col = 0
        for filter_name, description in filters_list:
            var = tk.BooleanVar(value=self.file_filters.get(filter_name, True))
            cb = tk.Checkbutton(filters_grid, text=f"{filter_name} ({description})",
                               variable=var, font=self.default_font,
                               bg=self.colors['bg_card'], fg=self.colors['text_secondary'],
                               selectcolor=self.colors['bg_secondary'],
                               activebackground=self.colors['bg_card'])
            cb.grid(row=row, column=col, sticky='w', padx=10, pady=2)
            
            self.file_filters[filter_name] = var
            
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        # أزرار الأدوات المتقدمة
        advanced_tools_frame = tk.Frame(self.dev_content, bg=self.colors['bg_secondary'])
        advanced_tools_frame.pack(fill='x', pady=15)
        
        tools_buttons = [
            ("🔍 تحليل المشروع", self.colors['accent_orange'], self.analyze_project),
            ("📦 إنشاء Package", self.colors['accent_purple'], self.create_package),
            ("🌳 هيكل المشروع", self.colors['accent_blue'], self.generate_tree),
            ("📋 تقرير شامل", self.colors['accent_green'], self.generate_report)
        ]
        
        for text, color, command in tools_buttons:
            btn = tk.Button(advanced_tools_frame, text=text, font=self.button_font,
                           bg=color, fg=self.colors['text_primary'], pady=12,
                           command=command, cursor='hand2', relief='flat')
            btn.pack(side='left', fill='x', expand=True, padx=2)
            
    def create_analysis_tab_content(self):
        """محتوى تبويب التحليل"""
        self.analysis_content = tk.Frame(self.tab_content_frame, bg=self.colors['bg_secondary'])
        
        # منطقة التحليل
        analysis_frame = tk.LabelFrame(self.analysis_content,
                                      text="📊 تحليل متقدم للملفات والمشاريع",
                                      font=self.default_font,
                                      bg=self.colors['bg_card'],
                                      fg=self.colors['text_primary'],
                                      padx=20, pady=15)
        analysis_frame.pack(fill='both', expand=True)
        
        # منطقة عرض التحليل
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame,
                                                      height=25,
                                                      font=self.code_font,
                                                      bg=self.colors['bg_primary'],
                                                      fg=self.colors['text_primary'],
                                                      wrap=tk.WORD,
                                                      insertbackground=self.colors['text_primary'])
        self.analysis_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # رسالة تعريفية
        welcome_text = """
📊 مرحباً بك في قسم التحليل المتقدم!

هذا القسم يوفر:
🔍 تحليل شامل للكود والمشاريع
📈 إحصائيات مفصلة عن الملفات
🌳 هيكل المشروع بصرياً
📋 تقارير جاهزة للمشاركة
🤖 تحليل محسن للـ AI

لبدء التحليل، استخدم الأزرار في تبويب "المطورين" أو "AI Ready"
        """
        
        self.analysis_text.insert(tk.END, welcome_text)
        self.analysis_text.config(state='disabled')
        
    def create_enhanced_button(self, parent, btn_data):
        """إنشاء زر محسن مع وصف"""
        btn_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        btn_frame.pack(fill='x', pady=8)
        
        # الزر الرئيسي
        main_btn = tk.Button(btn_frame,
                            text=btn_data['text'],
                            font=self.button_font,
                            bg=btn_data['color'],
                            fg=self.colors['text_primary'],
                            pady=12,
                            command=btn_data['command'],
                            cursor='hand2',
                            relief='flat')
        main_btn.pack(fill='x')
        
        # وصف الزر
        desc_label = tk.Label(btn_frame,
                             text=btn_data['desc'],
                             font=('Segoe UI', 8),
                             bg=self.colors['bg_card'],
                             fg=self.colors['text_muted'],
                             wraplength=500)
        desc_label.pack(pady=(5, 0))
        
    def create_styled_checkbox(self, parent, text, variable, description):
        """إنشاء checkbox مع وصف"""
        cb_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        cb_frame.pack(fill='x', pady=5)
        
        cb = tk.Checkbutton(cb_frame,
                           text=text,
                           variable=variable,
                           font=self.default_font,
                           bg=self.colors['bg_card'],
                           fg=self.colors['text_secondary'],
                           selectcolor=self.colors['bg_secondary'],
                           activebackground=self.colors['bg_card'])
        cb.pack(anchor='w')
        
        desc_label = tk.Label(cb_frame,
                             text=description,
                             font=('Segoe UI', 8),
                             bg=self.colors['bg_card'],
                             fg=self.colors['text_muted'],
                             wraplength=300)
        desc_label.pack(anchor='w', padx=(20, 0))
        
    def create_results_area(self, parent):
        """منطقة النتائج المحسنة"""
        results_frame = tk.LabelFrame(parent,
                                     text="📊 نتائج العملية والتحليل",
                                     font=self.default_font,
                                     bg=self.colors['bg_card'],
                                     fg=self.colors['text_primary'],
                                     padx=10, pady=10)
        results_frame.pack(fill='both', expand=True)
        
        # منطقة النص
        self.results_text = scrolledtext.ScrolledText(results_frame,
                                                     height=12,
                                                     font=self.code_font,
                                                     bg=self.colors['bg_primary'],
                                                     fg=self.colors['text_primary'],
                                                     wrap=tk.WORD,
                                                     insertbackground=self.colors['text_primary'])
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # شريط التقدم المحسن
        progress_frame = tk.Frame(results_frame, bg=self.colors['bg_card'])
        progress_frame.pack(fill='x', padx=5, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame,
                                           variable=self.progress_var,
                                           maximum=100,
                                           style='TProgressbar')
        self.progress_bar.pack(fill='x', side='left', expand=True)
        
        self.progress_label = tk.Label(progress_frame,
                                      text="جاهز",
                                      font=('Segoe UI', 8),
                                      bg=self.colors['bg_card'],
                                      fg=self.colors['text_muted'],
                                      width=15)
        self.progress_label.pack(side='right', padx=(10, 0))
        
        # رسالة ترحيب
        welcome_msg = """🎉 مرحباً بك في دمج الملفات العربي Pro!

✨ الميزات الجديدة:
🤖 تحسين خاص للذكاء الاصطناعي
👨‍💻 أدوات متقدمة للمطورين  
📊 تحليل شامل للكود
🔍 فلترة ذكية للملفات
📋 تقارير احترافية

اختر أحد الخيارات أعلاه للبدء...
"""
        self.results_text.insert(tk.END, welcome_msg)
        
    def create_enhanced_status(self, parent):
        """شريط حالة محسن"""
        status_frame = tk.Frame(parent, bg=self.colors['bg_card'], pady=10)
        status_frame.pack(fill='x', pady=(15, 0))
        
        # معلومات سريعة
        info_frame = tk.Frame(status_frame, bg=self.colors['bg_card'])
        info_frame.pack(fill='x')
        
        # الحالة
        self.status_var = tk.StringVar(value="جاهز للاستخدام ✅")
        status_label = tk.Label(info_frame,
                               textvariable=self.status_var,
                               font=self.default_font,
                               bg=self.colors['bg_card'],
                               fg=self.colors['text_primary'])
        status_label.pack(side='left')
        
        # معلومات إضافية
        self.files_count_var = tk.StringVar(value="الملفات: 0")
        files_label = tk.Label(info_frame,
                              textvariable=self.files_count_var,
                              font=('Segoe UI', 9),
                              bg=self.colors['bg_card'],
                              fg=self.colors['text_muted'])
        files_label.pack(side='right', padx=(0, 20))
        
        self.folders_count_var = tk.StringVar(value="المجلدات: 0")
        folders_label = tk.Label(info_frame,
                                textvariable=self.folders_count_var,
                                font=('Segoe UI', 9),
                                bg=self.colors['bg_card'],
                                fg=self.colors['text_muted'])
        folders_label.pack(side='right', padx=(0, 20))
        
    # الدوال الرئيسية المحسنة
    
    def ai_project_combo(self):
        """دمج مشروع كامل للـ AI"""
        folder = filedialog.askdirectory(title="اختر مجلد المشروع للتحسين للـ AI")
        if folder:
            self.update_status("🤖 جاري تحضير المشروع للـ AI...")
            thread = threading.Thread(target=self.process_ai_project, args=(folder,))
            thread.daemon = True
            thread.start()
            
    def smart_files_combo(self):
        """ملفات ذكية مع تحليل"""
        files = filedialog.askopenfilenames(title="اختر الملفات للتحليل والدمج")
        if files:
            self.update_status("🔍 جاري التحليل الذكي...")
            thread = threading.Thread(target=self.process_smart_files, args=(list(files),))
            thread.daemon = True
            thread.start()
            
    def dev_folder_combo(self):
        """مجلد مطور محسن"""
        folder = filedialog.askdirectory(title="اختر مجلد للمعالجة المطورة")
        if folder:
            self.update_status("👨‍💻 جاري المعالجة المطورة...")
            thread = threading.Thread(target=self.process_dev_folder, args=(folder,))
            thread.daemon = True
            thread.start()
            
    def process_ai_project(self, folder):
        """معالجة مشروع للـ AI"""
        try:
            self.progress_var.set(0)
            self.update_results("🤖 بدء معالجة المشروع للذكاء الاصطناعي...\n")
            
            # فحص هيكل المشروع
            project_info = self.analyze_project_structure(folder)
            self.update_results(f"📁 نوع المشروع: {project_info['type']}\n")
            self.update_results(f"📊 إجمالي الملفات: {project_info['total_files']}\n")
            
            # فلترة الملفات للـ AI
            ai_files = self.filter_files_for_ai(folder)
            self.update_results(f"✅ ملفات محسنة للـ AI: {len(ai_files)}\n")
            
            # إنشاء ملف محسن للـ AI
            output_file = self.create_ai_optimized_file(ai_files, folder, project_info)
            
            self.progress_var.set(100)
            self.update_results(f"🎉 تم إنشاء ملف محسن للـ AI: {output_file}\n")
            self.open_file(output_file)
            
        except Exception as e:
            self.update_results(f"❌ خطأ: {str(e)}\n")
        finally:
            self.update_status("انتهت معالجة AI")
            
    def analyze_project_structure(self, folder):
        """تحليل هيكل المشروع"""
        info = {
            'type': 'مشروع عام',
            'total_files': 0,
            'languages': set(),
            'frameworks': set(),
            'structure': {}
        }
        
        # فحص نوع المشروع
        if os.path.exists(os.path.join(folder, 'package.json')):
            info['type'] = 'مشروع Node.js'
            info['frameworks'].add('Node.js')
        elif os.path.exists(os.path.join(folder, 'requirements.txt')):
            info['type'] = 'مشروع Python'
            info['frameworks'].add('Python')
        elif os.path.exists(os.path.join(folder, 'composer.json')):
            info['type'] = 'مشروع PHP'
            info['frameworks'].add('PHP')
        elif os.path.exists(os.path.join(folder, 'index.html')):
            info['type'] = 'مشروع ويب'
            info['frameworks'].add('HTML/CSS/JS')
            
        # عد الملفات وتحديد اللغات
        for root, dirs, files in os.walk(folder):
            for file in files:
                info['total_files'] += 1
                ext = os.path.splitext(file)[1].lower()
                
                lang_map = {
                    '.py': 'Python', '.js': 'JavaScript', '.php': 'PHP',
                    '.html': 'HTML', '.css': 'CSS', '.java': 'Java',
                    '.cpp': 'C++', '.cs': 'C#', '.rb': 'Ruby'
                }
                
                if ext in lang_map:
                    info['languages'].add(lang_map[ext])
                    
        return info
        
    def filter_files_for_ai(self, folder):
        """فلترة الملفات للـ AI"""
        ai_files = []
        excluded_dirs = {'node_modules', '.git', 'dist', 'build', '__pycache__', 'vendor'}
        
        for root, dirs, files in os.walk(folder):
            # تجاهل المجلدات المستبعدة
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # فلترة حسب الامتداد
                ext = os.path.splitext(file)[1].lower()
                allowed_extensions = {
                    '.py', '.js', '.php', '.html', '.css', '.java', '.cpp', 
                    '.cs', '.rb', '.go', '.rs', '.txt', '.md', '.json', '.xml'
                }
                
                if ext in allowed_extensions:
                    # فحص حجم الملف
                    size = os.path.getsize(file_path)
                    max_size = int(self.max_file_size_var.get()) * 1024
                    
                    if size <= max_size:
                        ai_files.append(file_path)
                        
        return ai_files
        
    def create_ai_optimized_file(self, files, project_folder, project_info):
        """إنشاء ملف محسن للـ AI"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"AI_Ready_Project_{timestamp}.md"
        output_path = os.path.join(self.output_location, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as output:
            # رأس محسن للـ AI
            output.write(f"# مشروع {os.path.basename(project_folder)} - محسن للذكاء الاصطناعي\n\n")
            output.write(f"**تاريخ الإنشاء:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            output.write(f"**نوع المشروع:** {project_info['type']}\n")
            output.write(f"**اللغات:** {', '.join(project_info['languages'])}\n")
            output.write(f"**عدد الملفات:** {len(files)}\n\n")
            
            # هيكل المشروع
            if self.include_structure.get():
                output.write("## 📁 هيكل المشروع\n\n")
                output.write("```\n")
                output.write(self.generate_project_tree(project_folder))
                output.write("\n```\n\n")
                
            # ملخص سريع
            output.write("## 📋 ملخص المشروع\n\n")
            output.write("هذا المشروع يحتوي على:\n")
            for lang in project_info['languages']:
                count = sum(1 for f in files if self.get_file_language(f) == lang)
                output.write(f"- **{lang}:** {count} ملف\n")
            output.write("\n")
            
            # الملفات
            output.write("## 📄 محتوى الملفات\n\n")
            
            for i, file_path in enumerate(files):
                rel_path = os.path.relpath(file_path, project_folder)
                file_lang = self.get_file_language(file_path)
                
                output.write(f"### {i+1}. {rel_path}\n\n")
                
                if self.add_context.get():
                    size = os.path.getsize(file_path)
                    output.write(f"**نوع:** {file_lang} | **الحجم:** {size:,} بايت\n\n")
                    
                output.write(f"```{file_lang.lower()}\n")
                
                content = self.read_file_safe(file_path)
                if self.remove_comments.get():
                    content = self.remove_debug_content(content, file_lang)
                    
                output.write(content)
                output.write("\n```\n\n")
                
                # تحديث التقدم
                progress = (i / len(files)) * 100
                self.progress_var.set(progress)
                self.progress_label.config(text=f"{i+1}/{len(files)}")
                self.root.update_idletasks()
                
            # خاتمة للـ AI
            output.write("---\n\n")
            output.write("**ملاحظة للذكاء الاصطناعي:**\n")
            output.write("هذا المشروع تم تحضيره خصيصاً لتحليلك. ")
            output.write("يمكنك تحليل الكود، اقتراح تحسينات، أو الإجابة على أسئلة محددة حوله.\n")
            
        return output_path
        
    def get_file_language(self, file_path):
        """تحديد لغة الملف"""
        ext = os.path.splitext(file_path)[1].lower()
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.php': 'php',
            '.html': 'html', '.css': 'css', '.java': 'java',
            '.cpp': 'cpp', '.cs': 'csharp', '.rb': 'ruby',
            '.go': 'go', '.rs': 'rust', '.txt': 'text',
            '.md': 'markdown', '.json': 'json', '.xml': 'xml'
        }
        return lang_map.get(ext, 'text')
        
    def remove_debug_content(self, content, language):
        """إزالة محتوى debug"""
        if language.lower() == 'javascript':
            # إزالة console.log
            content = re.sub(r'console\.log\([^)]*\);?\n?', '', content)
            content = re.sub(r'console\.debug\([^)]*\);?\n?', '', content)
        elif language.lower() == 'python':
            # إزالة print debug
            content = re.sub(r'print\([^)]*\)\s*#.*debug.*\n?', '', content, flags=re.IGNORECASE)
            
        return content
        
    def generate_project_tree(self, folder):
        """إنشاء شجرة المشروع"""
        tree_lines = []
        excluded_dirs = {'node_modules', '.git', 'dist', 'build', '__pycache__'}
        
        def add_items(directory, prefix=""):
            items = []
            try:
                for item in os.listdir(directory):
                    if item.startswith('.') and item not in {'.env', '.gitignore'}:
                        continue
                    if item in excluded_dirs:
                        continue
                    items.append(item)
            except PermissionError:
                return
                
            items.sort()
            
            for i, item in enumerate(items):
                item_path = os.path.join(directory, item)
                is_last = i == len(items) - 1
                
                current_prefix = "└── " if is_last else "├── "
                tree_lines.append(f"{prefix}{current_prefix}{item}")
                
                if os.path.isdir(item_path):
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    add_items(item_path, next_prefix)
                    
        tree_lines.append(os.path.basename(folder))
        add_items(folder)
        return "\n".join(tree_lines)
        
    # باقي الدوال المساعدة...
    
    def read_file_safe(self, file_path):
        """قراءة آمنة للملفات"""
        try:
            encodings = ['utf-8', 'cp1256', 'windows-1256', 'latin-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            return "[لا يمكن قراءة الملف - ترميز غير مدعوم]"
        except Exception as e:
            return f"[خطأ في القراءة: {str(e)}]"
            
    def open_file(self, file_path):
        """فتح الملف"""
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            else:
                subprocess.run(['open', file_path])
        except Exception as e:
            self.update_results(f"⚠️ لم يتم فتح الملف: {str(e)}\n")
            
    def update_status(self, message):
        """تحديث الحالة"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def update_results(self, message):
        """تحديث النتائج"""
        self.results_text.insert(tk.END, message)
        self.results_text.see(tk.END)
        self.root.update_idletasks()
        
    def load_settings(self):
        """تحميل الإعدادات"""
        pass
        
    # دوال مؤقتة للميزات قيد التطوير
    def process_smart_files(self, files):
        self.update_results("🔍 ميزة التحليل الذكي قيد التطوير...\n")
        
    def process_dev_folder(self, folder):
        self.update_results("👨‍💻 ميزة المعالجة المطورة قيد التطوير...\n")
        
    def prepare_for_ai(self):
        self.update_results("🤖 ميزة التحضير للـ AI قيد التطوير...\n")
        
    def copy_to_clipboard(self):
        self.update_results("📋 ميزة النسخ للحافظة قيد التطوير...\n")
        
    def create_share_link(self):
        self.update_results("🔗 ميزة إنشاء رابط المشاركة قيد التطوير...\n")
        
    def analyze_project(self):
        self.update_results("🔍 ميزة تحليل المشروع قيد التطوير...\n")
        
    def create_package(self):
        self.update_results("📦 ميزة إنشاء Package قيد التطوير...\n")
        
    def generate_tree(self):
        self.update_results("🌳 ميزة هيكل المشروع قيد التطوير...\n")
        
    def generate_report(self):
        self.update_results("📋 ميزة التقرير الشامل قيد التطوير...\n")
        
    def run(self):
        """تشغيل التطبيق"""
        self.root.mainloop()

def main():
    """الدالة الرئيسية"""
    try:
        app = ProArabicFileCombiner()
        app.run()
    except Exception as e:
        print(f"خطأ في تشغيل التطبيق: {e}")
        input("اضغط Enter للإغلاق...")

if __name__ == "__main__":
    main()