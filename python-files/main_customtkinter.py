#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import os
import sys
from datetime import datetime
import csv
import subprocess
import shutil

# Настройка темы
ctk.set_appearance_mode("light")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class NPADatabase:
    """Класс для работы с базой данных"""
    
    def __init__(self):
        # Определяем путь к базе данных
        if getattr(sys, 'frozen', False):
            # Если запущен как exe
            base_path = os.path.dirname(sys.executable)
        else:
            # Если запущен как скрипт
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        self.db_path = os.path.join(base_path, "npa_database.db")
        self.documents_folder = os.path.join(base_path, "documents")
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создаем таблицу документов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS npa_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_type TEXT NOT NULL,
                document_number TEXT NOT NULL,
                document_date TEXT NOT NULL,
                title TEXT NOT NULL,
                effective_date TEXT,
                status TEXT DEFAULT 'Активен',
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создаем таблицу связей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                new_document_id INTEGER,
                cancelled_document_id INTEGER,
                relation_type TEXT DEFAULT 'отменяет',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (new_document_id) REFERENCES npa_documents (id),
                FOREIGN KEY (cancelled_document_id) REFERENCES npa_documents (id)
            )
        ''')
        
        # Миграция: добавляем колонку file_path, если её нет
        try:
            cursor.execute('ALTER TABLE npa_documents ADD COLUMN file_path TEXT')
        except sqlite3.OperationalError:
            # Колонка уже существует
            pass
        
        conn.commit()
        conn.close()
    
    def get_all_documents(self):
        """Получение всех документов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, document_type, document_number, document_date, title, 
                   effective_date, status, file_path, created_at, updated_at
            FROM npa_documents
            ORDER BY 
                CASE 
                    WHEN document_date LIKE '__.__.____' 
                    THEN substr(document_date, 7, 4) || substr(document_date, 4, 2) || substr(document_date, 1, 2)
                    ELSE document_date 
                END DESC,
                created_at DESC
        ''')
        
        columns = [description[0] for description in cursor.description]
        documents = []
        
        for row in cursor.fetchall():
            documents.append(dict(zip(columns, row)))
        
        conn.close()
        return documents
    
    def add_document(self, document_type, document_number, document_date, 
                    title, effective_date, status="Активен", file_path=None, cancelled_documents=None):
        """Добавление нового документа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO npa_documents 
            (document_type, document_number, document_date, title, effective_date, status, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (document_type, document_number, document_date, title, effective_date, status, file_path))
        
        document_id = cursor.lastrowid
        
        # Добавляем связи с отмененными документами и меняем их статус
        if cancelled_documents:
            for cancelled_doc_id in cancelled_documents:
                # Добавляем связь
                cursor.execute('''
                    INSERT INTO document_relations (new_document_id, cancelled_document_id, relation_type)
                    VALUES (?, ?, ?)
                ''', (document_id, cancelled_doc_id, 'отменяет'))
                
                # Меняем статус отмененного документа на "Утратил силу"
                cursor.execute('''
                    UPDATE npa_documents SET status = 'Утратил силу' WHERE id = ?
                ''', (cancelled_doc_id,))
        
        conn.commit()
        conn.close()
        return document_id
    
    def update_document(self, document_id, document_type, document_number, 
                       document_date, title, effective_date, status, file_path=None, cancelled_documents=None):
        """Обновление документа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE npa_documents 
            SET document_type = ?, document_number = ?, document_date = ?, 
                title = ?, effective_date = ?, status = ?, file_path = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (document_type, document_number, document_date, title, effective_date, status, file_path, document_id))
        
        success = cursor.rowcount > 0
        
        # Обновляем связи с отмененными документами
        if success:
            # Получаем старые связи для восстановления статусов
            cursor.execute('SELECT cancelled_document_id FROM document_relations WHERE new_document_id = ?', (document_id,))
            old_cancelled_docs = [row[0] for row in cursor.fetchall()]
            
            # Удаляем старые связи
            cursor.execute('DELETE FROM document_relations WHERE new_document_id = ?', (document_id,))
            
            # Восстанавливаем статус "Активен" для документов, которые больше не отменяются
            for old_doc_id in old_cancelled_docs:
                if old_doc_id not in (cancelled_documents or []):
                    cursor.execute('''
                        UPDATE npa_documents SET status = 'Активен' WHERE id = ?
                    ''', (old_doc_id,))
            
            # Добавляем новые связи и меняем статус
            if cancelled_documents:
                for cancelled_doc_id in cancelled_documents:
                    cursor.execute('''
                        INSERT INTO document_relations (new_document_id, cancelled_document_id, relation_type)
                        VALUES (?, ?, ?)
                    ''', (document_id, cancelled_doc_id, 'отменяет'))
                    
                    # Меняем статус отмененного документа на "Утратил силу"
                    cursor.execute('''
                        UPDATE npa_documents SET status = 'Утратил силу' WHERE id = ?
                    ''', (cancelled_doc_id,))
        
        conn.commit()
        conn.close()
        return success
    
    def delete_document(self, document_id):
        """Удаление документа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Удаляем связи с этим документом
        cursor.execute('DELETE FROM document_relations WHERE new_document_id = ? OR cancelled_document_id = ?', 
                      (document_id, document_id))
        
        # Удаляем сам документ
        cursor.execute('DELETE FROM npa_documents WHERE id = ?', (document_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_document_relations(self, document_id):
        """Получение связей документа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT dr.*, 
                   new_doc.document_type as new_doc_type, new_doc.document_number as new_doc_number,
                   cancelled_doc.document_type as cancelled_doc_type, cancelled_doc.document_number as cancelled_doc_number
            FROM document_relations dr
            LEFT JOIN npa_documents new_doc ON dr.new_document_id = new_doc.id
            LEFT JOIN npa_documents cancelled_doc ON dr.cancelled_document_id = cancelled_doc.id
            WHERE dr.new_document_id = ? OR dr.cancelled_document_id = ?
        ''', (document_id, document_id))
        
        relations = cursor.fetchall()
        conn.close()
        return relations
    
    def add_relation(self, new_document_id, cancelled_document_id, relation_type="отменяет"):
        """Добавление связи между документами"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO document_relations (new_document_id, cancelled_document_id, relation_type)
            VALUES (?, ?, ?)
        ''', (new_document_id, cancelled_document_id, relation_type))
        
        relation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return relation_id
    
    def copy_file_to_documents_folder(self, source_path, doc_id):
        """Копирование файла в папку documents"""
        if not os.path.exists(self.documents_folder):
            os.makedirs(self.documents_folder)
        
        # Получаем расширение файла
        _, ext = os.path.splitext(source_path)
        # Создаем новое имя файла
        new_filename = f"doc_{doc_id}{ext}"
        new_path = os.path.join(self.documents_folder, new_filename)
        
        # Копируем файл
        shutil.copy2(source_path, new_path)
        return new_path
    
    def get_all_document_types(self):
        """Получение всех уникальных типов документов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT document_type FROM npa_documents WHERE document_type IS NOT NULL AND document_type != "" ORDER BY document_type')
        types = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return types

class NPAManager:
    """Главное приложение"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("NPA Manager - Управление нормативно-правовыми актами")
        self.root.geometry("1400x900")
        
        # Инициализация базы данных
        self.database = NPADatabase()
        
        # Создание интерфейса
        self.setup_ui()
        self.load_documents()
        
        # Запуск в полноэкранном режиме
        self.root.after(100, self.maximize_window)
        
        # Инициализация переменной для всплывающих подсказок
        self.tooltip = None
    
    def maximize_window(self):
        """Максимизация окна"""
        self.root.state('zoomed')
    
    def setup_ui(self):
        """Настройка интерфейса"""
        # Главный контейнер
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Заголовок
        self.create_header(main_frame)
        
        # Панель инструментов
        self.create_toolbar(main_frame)
        
        # Панель поиска
        self.create_search_panel(main_frame)
        
        # Таблица документов
        self.create_documents_table(main_frame)
        
        # Статус бар
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Создание заголовка"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Заголовок
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Учет НПА в области пожарной безопасности",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#0078d4"
        )
        title_label.pack(side="left")
        
        # Статистика
        stats_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_frame.pack(side="right")
        
        self.total_label = ctk.CTkLabel(stats_frame, text="Всего: 0", font=ctk.CTkFont(size=14))
        self.active_label = ctk.CTkLabel(stats_frame, text="Активных: 0", font=ctk.CTkFont(size=14))
        self.inactive_label = ctk.CTkLabel(stats_frame, text="Утратили силу: 0", font=ctk.CTkFont(size=14))
        
        self.total_label.pack(side="left", padx=5)
        self.active_label.pack(side="left", padx=5)
        self.inactive_label.pack(side="left", padx=5)
    
    def create_toolbar(self, parent):
        """Создание панели инструментов"""
        toolbar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar_frame.pack(fill="x", padx=10, pady=5)
        
        # Кнопки
        ctk.CTkButton(
            toolbar_frame, 
            text="➕ Добавить документ", 
            command=self.add_document,
            fg_color="#28a745",
            hover_color="#218838"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="✏️ Редактировать", 
            command=self.edit_document,
            fg_color="#007bff",
            hover_color="#0056b3"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="🗑️ Удалить", 
            command=self.delete_document,
            fg_color="#dc3545",
            hover_color="#c82333"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="📊 Статистика", 
            command=self.show_statistics,
            fg_color="#6f42c1",
            hover_color="#5a2d91"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="📤 Экспорт", 
            command=self.export_data,
            fg_color="#fd7e14",
            hover_color="#e55a00"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            toolbar_frame, 
            text="🔄 Обновить", 
            command=self.refresh_table,
            fg_color="#17a2b8",
            hover_color="#138496"
        ).pack(side="left", padx=5)
    
    def load_documents(self):
        """Загрузка документов в таблицу"""
        # Импортируем ttk для кнопок
        import tkinter.ttk as ttk
        
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получаем документы
        documents = self.database.get_all_documents()
        
        # Обновляем список типов документов
        self.update_document_types()
        
        # Фильтруем по поиску
        search_text = self.search_var.get().lower()
        status_filter = self.status_var.get()
        type_filter = self.type_var.get()
        
        filtered_docs = []
        for doc in documents:
            # Фильтр по поиску
            if search_text and search_text not in doc['title'].lower() and search_text not in doc['document_number'].lower():
                continue
            
            # Фильтр по статусу
            if status_filter != "Все" and doc['status'] != status_filter:
                continue
            
            # Фильтр по типу
            if type_filter != "Все" and doc['document_type'] != type_filter:
                continue
            
            filtered_docs.append(doc)
        
        # Словарь для сопоставления номеров строк с ID документов
        self.row_to_id = {}
        
        # Добавляем в таблицу
        for i, doc in enumerate(filtered_docs, 1):
            # Определяем наличие файла
            file_status = "📄" if doc.get('file_path') else ""
            
            # Определяем наличие связей
            relations = self.database.get_document_relations(doc['id'])
            if relations:
                # Определяем тип связей
                cancels_others = any(rel[1] == doc['id'] for rel in relations)  # Этот документ отменяет другие
                cancelled_by_others = any(rel[2] == doc['id'] for rel in relations)  # Этот документ отменен другими
                
                if cancels_others and cancelled_by_others:
                    relations_status = "🔄"  # Отменяет и отменен
                elif cancels_others:
                    relations_status = "➡️"  # Отменяет другие
                else:
                    relations_status = "⬅️"  # Отменен другими
            else:
                relations_status = ""
            
            # Цвет строки в зависимости от статуса
            tags = ()
            if doc['status'] == 'Утратил силу':
                tags = ('inactive',)
            
            item = self.tree.insert('', 'end', values=(
                i,  # Номер по порядку
                doc['document_type'],
                doc['document_number'],
                doc['document_date'],
                doc['title'],
                doc['effective_date'] or '',
                doc['status'],
                file_status,
                relations_status
            ), tags=tags)
            
            # Сохраняем соответствие номера строки и ID документа
            self.row_to_id[item] = doc['id']
        
        # Настройка цветов
        self.tree.tag_configure('inactive', background='#f8d7da')
        
        # Обновляем статистику
        self.update_statistics(documents)
        
        # Обновляем статус
        status_text = f"Загружено документов: {len(filtered_docs)}"
        if any(doc.get('file_path') for doc in filtered_docs):
            status_text += " | 📄 - есть файл"
        if any(self.database.get_document_relations(doc['id']) for doc in filtered_docs):
            status_text += " | ➡️ отменяет другие | ⬅️ отменен другими | 🔄 отменяет и отменен"
        
        self.status_label.configure(text=status_text)
    
    def create_search_panel(self, parent):
        """Создание панели поиска"""
        search_frame = ctk.CTkFrame(parent)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        # Заголовок панели
        ctk.CTkLabel(
            search_frame, 
            text="🔍 Поиск и фильтры", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Содержимое панели
        content_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Поиск
        ctk.CTkLabel(content_frame, text="Поиск:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ctk.CTkEntry(content_frame, textvariable=self.search_var, width=300)
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Статус
        ctk.CTkLabel(content_frame, text="Статус:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.status_var = ctk.StringVar(value="Все")
        status_combo = ctk.CTkComboBox(
            content_frame, 
            values=["Все", "Активен", "Утратил силу"],
            variable=self.status_var,
            command=self.on_search_change
        )
        status_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Тип документа
        ctk.CTkLabel(content_frame, text="Тип:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.type_var = ctk.StringVar(value="Все")
        self.type_combo = ctk.CTkComboBox(
            content_frame, 
            values=["Все"],
            variable=self.type_var,
            command=self.on_search_change
        )
        self.type_combo.grid(row=0, column=5, padx=5, pady=5, sticky="w")
    
    def create_documents_table(self, parent):
        """Создание таблицы документов"""
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Заголовок таблицы
        ctk.CTkLabel(
            table_frame, 
            text="📋 Документы", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Создаем Treeview в отдельном фрейме
        tree_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Импортируем tkinter для Treeview
        import tkinter.ttk as ttk
        
        # Создаем Treeview
        columns = ('№', 'Тип', 'Номер', 'Дата', 'Название', 'Дата вступления', 'Статус', 'Файл', 'Связи')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        self.tree.heading('№', text='№')
        self.tree.heading('Тип', text='Тип документа')
        self.tree.heading('Номер', text='Номер')
        self.tree.heading('Дата', text='Дата')
        self.tree.heading('Название', text='Название')
        self.tree.heading('Дата вступления', text='Дата вступления')
        self.tree.heading('Статус', text='Статус')
        self.tree.heading('Файл', text='Файл')
        self.tree.heading('Связи', text='Связи')
        
        # Ширина колонок
        self.tree.column('№', width=50)
        self.tree.column('Тип', width=120)
        self.tree.column('Номер', width=100)
        self.tree.column('Дата', width=100)
        self.tree.column('Название', width=400)
        self.tree.column('Дата вступления', width=120)
        self.tree.column('Статус', width=100)
        self.tree.column('Файл', width=80)
        self.tree.column('Связи', width=80)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Привязка событий
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<Motion>', self.on_mouse_motion)  # Для всплывающих подсказок
    
    def create_status_bar(self, parent):
        """Создание статус бара"""
        status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="Готово", 
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left")
        
        # Кнопка "О программе"
        ctk.CTkButton(
            status_frame, 
            text="ℹ️ О программе", 
            command=self.show_about,
            width=120,
            height=25
        ).pack(side="right")
    

    
    def update_statistics(self, documents):
        """Обновление статистики"""
        total = len(documents)
        active = len([d for d in documents if d['status'] == 'Активен'])
        inactive = total - active
        
        self.total_label.configure(text=f"Всего: {total}")
        self.active_label.configure(text=f"Активных: {active}")
        self.inactive_label.configure(text=f"Утратили силу: {inactive}")
    
    def get_document_types(self):
        """Получение уникальных типов документов из базы данных"""
        documents = self.database.get_all_documents()
        types = set()
        for doc in documents:
            if doc['document_type']:
                types.add(doc['document_type'])
        return sorted(list(types))
    
    def update_document_types(self):
        """Обновление списков типов документов в интерфейсе"""
        types = self.get_document_types()
        type_values = ["Все"] + types
        
        # Обновляем комбобокс в панели поиска
        if hasattr(self, 'type_combo'):
            self.type_combo.configure(values=type_values)
        
        # Обновляем комбобокс в диалоге добавления/редактирования
        if hasattr(self, 'dialog_type_combo'):
            self.dialog_type_combo.configure(values=types)
    
    def on_search_change(self, *args):
        """Обработка изменения поиска"""
        self.load_documents()
    
    def refresh_table(self):
        """Обновление таблицы"""
        self.load_documents()
        # Принудительно обновляем интерфейс
        self.root.update()
        self.root.update_idletasks()
    
    def add_document(self):
        """Добавление документа"""
        dialog = DocumentDialog(self.root, self.database)
        if dialog.result:
            self.load_documents()
            # Принудительно обновляем интерфейс
            self.root.update()
            self.root.update_idletasks()
    
    def edit_document(self):
        """Редактирование документа"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите документ для редактирования")
            return
        
        doc_id = self.row_to_id.get(selection[0])
        if doc_id:
            self.edit_document_by_id(doc_id)
    
    def edit_document_by_id(self, doc_id):
        """Редактирование документа по ID"""
        # Получаем данные документа
        documents = self.database.get_all_documents()
        doc_data = next((d for d in documents if d['id'] == doc_id), None)
        
        if doc_data:
            dialog = DocumentDialog(self.root, self.database, doc_data)
            if dialog.result:
                self.load_documents()
                # Принудительно обновляем интерфейс
                self.root.update()
                self.root.update_idletasks()
    
    def delete_document(self):
        """Удаление документа"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите документ для удаления")
            return
        
        doc_id = self.row_to_id.get(selection[0])
        if doc_id:
            self.delete_document_by_id(doc_id)
    
    def delete_document_by_id(self, doc_id):
        """Удаление документа по ID"""
        documents = self.database.get_all_documents()
        doc_data = next((d for d in documents if d['id'] == doc_id), None)
        
        if doc_data:
            if messagebox.askyesno("Подтверждение", f"Удалить документ:\n{doc_data['title']}?"):
                if self.database.delete_document(doc_id):
                    self.load_documents()
                    # Принудительно обновляем интерфейс
                    self.root.update()
                    self.root.update_idletasks()
                    messagebox.showinfo("Успех", "Документ удален")
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить документ")
    
    def open_file(self, file_path):
        """Открытие файла"""
        if os.path.exists(file_path):
            try:
                if sys.platform == "win32":
                    os.startfile(file_path)
                else:
                    subprocess.run(['xdg-open', file_path])
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")
        else:
            messagebox.showerror("Ошибка", "Файл не найден")
    
    def show_relations(self, doc_id):
        """Показать связи документа"""
        dialog = RelationsDialog(self.root, self.database, doc_id)
        dialog.dialog.wait_window()  # Делаем окно модальным
    
    def on_double_click(self, event):
        """Двойной клик по документу"""
        selection = self.tree.selection()
        if not selection:
            return
        
        doc_id = self.row_to_id.get(selection[0])
        if doc_id:
            # Получаем данные документа
            documents = self.database.get_all_documents()
            doc_data = next((d for d in documents if d['id'] == doc_id), None)
            
            if doc_data:
                # Если у документа есть файл, открываем его
                if doc_data.get('file_path'):
                    self.open_file(doc_data['file_path'])
                else:
                    # Если файла нет, открываем диалог редактирования
                    self.edit_document_by_id(doc_id)
    
    def on_mouse_motion(self, event):
        """Обработка движения мыши для всплывающих подсказок"""
        # Определяем, над какой ячейкой находится курсор
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            if item and column == "#5":  # Столбец "Название" (индекс 5)
                # Получаем данные ячейки
                item_data = self.tree.item(item)
                values = item_data['values']
                if len(values) > 4:  # Проверяем, что есть значение в столбце названия
                    title = values[4]  # Название документа
                    if title and len(title) > 50:  # Показываем подсказку только для длинных названий
                        # Создаем всплывающую подсказку
                        self.show_tooltip(event.x_root, event.y_root, title)
                        return
        
        # Скрываем подсказку, если курсор не над нужной ячейкой
        self.hide_tooltip()
    
    def show_tooltip(self, x, y, text):
        """Показать всплывающую подсказку"""
        # Скрываем предыдущую подсказку
        self.hide_tooltip()
        
        # Создаем новое окно подсказки
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x+10}+{y+10}")
        
        # Настройка внешнего вида
        self.tooltip.configure(bg='black')
        self.tooltip.attributes('-topmost', True)
        
        # Создаем метку с текстом
        label = tk.Label(self.tooltip, text=text, justify=tk.LEFT,
                        background="black", foreground="white", relief=tk.SOLID, borderwidth=1,
                        font=("TkDefaultFont", 9), wraplength=400)
        label.pack(padx=5, pady=5)
        
        # Автоматически скрываем через 3 секунды
        self.tooltip.after(3000, self.hide_tooltip)
    
    def hide_tooltip(self):
        """Скрыть всплывающую подсказку"""
        if hasattr(self, 'tooltip') and self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        # Определяем, на какой строке был клик
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            doc_id = self.row_to_id.get(item)
            
            # Получаем данные документа
            documents = self.database.get_all_documents()
            doc_data = next((d for d in documents if d['id'] == doc_id), None) if doc_id else None
            
            menu = tk.Menu(self.root, tearoff=0)
            
            if doc_data:
                # Если у документа есть файл, добавляем пункт "Открыть файл"
                if doc_data.get('file_path'):
                    menu.add_command(label="📄 Открыть файл", command=lambda: self.open_file(doc_data['file_path']))
                    menu.add_separator()
                
                menu.add_command(label="✏️ Редактировать", command=lambda: self.edit_document_by_id(doc_id))
                menu.add_command(label="🔗 Показать связи", command=lambda: self.show_relations(doc_id))
                menu.add_separator()
                menu.add_command(label="🗑️ Удалить", command=lambda: self.delete_document_by_id(doc_id))
                menu.add_separator()
            
            menu.add_command(label="➕ Добавить документ", command=self.add_document)
            menu.add_command(label="🔄 Обновить", command=self.refresh_table)
            menu.add_command(label="📊 Статистика", command=self.show_statistics)
            menu.add_command(label="📤 Экспорт", command=self.export_data)
            
            menu.tk_popup(event.x_root, event.y_root)
        else:
            # Если клик был не на строке, показываем общее меню
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="➕ Добавить документ", command=self.add_document)
            menu.add_separator()
            menu.add_command(label="🔄 Обновить", command=self.refresh_table)
            menu.add_command(label="📊 Статистика", command=self.show_statistics)
            menu.add_command(label="📤 Экспорт", command=self.export_data)
            menu.tk_popup(event.x_root, event.y_root)
    
    def export_data(self):
        """Экспорт данных"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Сохранить данные как"
        )
        
        if filename:
            documents = self.database.get_all_documents()
            
            # Используем кодировку UTF-8 с BOM для корректного отображения в Excel
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['ID', 'Тип', 'Номер', 'Дата', 'Название', 'Дата вступления', 'Статус', 'Файл', 'Связи']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                
                writer.writeheader()
                for doc in documents:
                    # Определяем наличие связей
                    relations = self.database.get_document_relations(doc['id'])
                    if relations:
                        cancels_others = any(rel[1] == doc['id'] for rel in relations)
                        cancelled_by_others = any(rel[2] == doc['id'] for rel in relations)
                        
                        if cancels_others and cancelled_by_others:
                            relations_info = "Отменяет и отменен"
                        elif cancels_others:
                            relations_info = "Отменяет другие"
                        elif cancelled_by_others:
                            relations_info = "Отменен другими"
                        else:
                            relations_info = ""
                    else:
                        relations_info = ""
                    
                    writer.writerow({
                        'ID': doc['id'],
                        'Тип': doc['document_type'],
                        'Номер': doc['document_number'],
                        'Дата': doc['document_date'],
                        'Название': doc['title'],
                        'Дата вступления': doc['effective_date'] or '',
                        'Статус': doc['status'],
                        'Файл': 'Да' if doc.get('file_path') else 'Нет',
                        'Связи': relations_info
                    })
            
            messagebox.showinfo("Экспорт", f"Данные экспортированы в файл:\n{filename}\n\nФайл сохранен в кодировке UTF-8 с BOM для корректного отображения в Excel.")
    
    def show_statistics(self):
        """Показать статистику"""
        documents = self.database.get_all_documents()
        
        if not documents:
            messagebox.showinfo("Статистика", "Нет данных для отображения")
            return
        
        # Подсчет статистики
        total = len(documents)
        active = len([d for d in documents if d['status'] == 'Активен'])
        inactive = total - active
        with_files = len([d for d in documents if d.get('file_path')])
        
        # Статистика по типам
        types = {}
        for doc in documents:
            doc_type = doc['document_type']
            types[doc_type] = types.get(doc_type, 0) + 1
        
        stats_text = f"""
📊 ОБЩАЯ СТАТИСТИКА

📋 Всего документов: {total}
✅ Активных документов: {active}
❌ Неактивных документов: {inactive}
📄 Документов с файлами: {with_files}

📈 СТАТИСТИКА ПО ТИПАМ:
"""
        
        for doc_type, count in types.items():
            percentage = (count / total) * 100
            stats_text += f"• {doc_type}: {count} ({percentage:.1f}%)\n"
        
        messagebox.showinfo("Статистика НПА", stats_text)
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """
NPA Manager - Управление нормативно-правовыми актами

Версия: 1.0 от 01.09.2025 г.
Разработано: младшим научным сотрудником ОРМ ППР (СЦ) 
Горбуновым Максимом Николаевичем

Функции:
• Добавление, редактирование и удаление НПА
• Поиск и фильтрация документов
• Прикрепление файлов к документам
• Установление связей между документами
• Экспорт данных
• Статистика и аналитика
        """
        messagebox.showinfo("О программе", about_text)
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

class DocumentDialog:
    """Диалог добавления/редактирования документа"""
    
    def __init__(self, parent, database, document_data=None):
        self.parent = parent
        self.database = database
        self.document_data = document_data
        self.result = False
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Добавить документ" if not document_data else "Редактировать документ")
        self.dialog.geometry("800x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        if document_data:
            self.load_data()
    
    def setup_ui(self):
        """Настройка интерфейса диалога"""
        # Заголовок
        title_text = "Добавить новый документ" if not self.document_data else "Редактировать документ"
        ctk.CTkLabel(
            self.dialog, 
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Основная форма
        form_frame = ctk.CTkScrollableFrame(self.dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Тип документа
        ctk.CTkLabel(form_frame, text="Вид НПА:").pack(anchor="w", padx=10, pady=(10, 5))
        self.type_var = ctk.StringVar()
        self.dialog_type_combo = ctk.CTkComboBox(
            form_frame, 
            values=self.database.get_all_document_types(),
            variable=self.type_var
        )
        self.dialog_type_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        # Номер документа
        ctk.CTkLabel(form_frame, text="Номер:").pack(anchor="w", padx=10, pady=(10, 5))
        self.number_var = ctk.StringVar()
        number_entry = ctk.CTkEntry(
            form_frame, 
            textvariable=self.number_var,
            placeholder_text="Введите только цифры, например: 1052"
        )
        number_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Валидация для ввода только цифр
        def validate_number(P):
            return P.isdigit() or P == ""
        number_entry.configure(validate="key", validatecommand=(number_entry.register(validate_number), '%P'))
        
        # Дата документа
        ctk.CTkLabel(form_frame, text="Дата документа:").pack(anchor="w", padx=10, pady=(10, 5))
        date_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        date_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.date_var = ctk.StringVar()
        date_entry = ctk.CTkEntry(
            date_frame, 
            textvariable=self.date_var,
            placeholder_text="YYYY-MM-DD"
        )
        date_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            date_frame, 
            text="📅", 
            command=self.show_calendar,
            width=50
        ).pack(side="right")
        
        # Название
        ctk.CTkLabel(form_frame, text="Наименование:").pack(anchor="w", padx=10, pady=(10, 5))
        self.title_var = ctk.StringVar()
        title_entry = ctk.CTkEntry(
            form_frame, 
            textvariable=self.title_var,
            placeholder_text="Введите полное наименование документа..."
        )
        title_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Дата вступления в силу
        ctk.CTkLabel(form_frame, text="Дата вступления в силу:").pack(anchor="w", padx=10, pady=(10, 5))
        self.effective_date_var = ctk.StringVar()
        effective_date_entry = ctk.CTkEntry(
            form_frame, 
            textvariable=self.effective_date_var,
            placeholder_text="Например: 1 сентября 2025 или 1 марта 2026 по 1 марта 2032 года"
        )
        effective_date_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Статус
        ctk.CTkLabel(form_frame, text="Статус:").pack(anchor="w", padx=10, pady=(10, 5))
        self.status_var = ctk.StringVar(value="Активен")
        status_combo = ctk.CTkComboBox(
            form_frame, 
            values=["Активен", "Утратил силу"],
            variable=self.status_var
        )
        status_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        # Файл
        ctk.CTkLabel(form_frame, text="Прикрепить файл:").pack(anchor="w", padx=10, pady=(10, 5))
        file_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        file_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.file_path = ctk.StringVar()
        file_entry = ctk.CTkEntry(file_frame, textvariable=self.file_path, state="readonly")
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            file_frame, 
            text="📁 Выбрать", 
            command=self.choose_file,
            width=100
        ).pack(side="right")
        
        # Секция отмены документов (как в PyQt5)
        cancel_frame = ctk.CTkFrame(form_frame)
        cancel_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        ctk.CTkLabel(
            cancel_frame, 
            text="Отмена существующих документов",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Чекбокс для включения отмены
        self.cancel_checkbox = ctk.CTkCheckBox(
            cancel_frame,
            text="Этот документ отменяет существующие документы",
            command=self.toggle_cancel_section
        )
        self.cancel_checkbox.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Секция выбора документов для отмены
        self.cancel_section = ctk.CTkFrame(cancel_frame)
        self.cancel_section.pack(fill="x", padx=10, pady=(0, 10))
        self.cancel_section.pack_forget()  # Скрываем по умолчанию
        
        # Поиск документов
        search_frame = ctk.CTkFrame(self.cancel_section, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(search_frame, text="Поиск:").pack(side="left", padx=(0, 10))
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self.search_documents)
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=300)
        search_entry.pack(side="left", padx=(0, 10))
        
        # Список документов
        docs_label = ctk.CTkLabel(self.cancel_section, text="Доступные документы (двойной клик для добавления):")
        docs_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Создаем Treeview для списка документов
        import tkinter.ttk as ttk
        
        docs_tree_frame = ctk.CTkFrame(self.cancel_section, fg_color="transparent")
        docs_tree_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        columns = ('ID', 'Тип', 'Номер', 'Дата', 'Название')
        self.documents_tree = ttk.Treeview(docs_tree_frame, columns=columns, show='headings', height=6)
        
        self.documents_tree.heading('ID', text='ID')
        self.documents_tree.heading('Тип', text='Тип')
        self.documents_tree.heading('Номер', text='Номер')
        self.documents_tree.heading('Дата', text='Дата')
        self.documents_tree.heading('Название', text='Название')
        
        self.documents_tree.column('ID', width=50)
        self.documents_tree.column('Тип', width=120)
        self.documents_tree.column('Номер', width=100)
        self.documents_tree.column('Дата', width=100)
        self.documents_tree.column('Название', width=300)
        
        # Скроллбар
        v_scrollbar = ttk.Scrollbar(docs_tree_frame, orient="vertical", command=self.documents_tree.yview)
        self.documents_tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.documents_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        
        # Привязка двойного клика
        self.documents_tree.bind('<Double-1>', self.add_to_cancel_list)
        
        # Список выбранных для отмены
        cancel_label = ctk.CTkLabel(self.cancel_section, text="Документы для отмены (двойной клик для удаления):")
        cancel_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        cancel_tree_frame = ctk.CTkFrame(self.cancel_section, fg_color="transparent")
        cancel_tree_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        cancel_columns = ('ID', 'Тип', 'Номер', 'Дата', 'Название')
        self.cancel_tree = ttk.Treeview(cancel_tree_frame, columns=cancel_columns, show='headings', height=4)
        
        self.cancel_tree.heading('ID', text='ID')
        self.cancel_tree.heading('Тип', text='Тип')
        self.cancel_tree.heading('Номер', text='Номер')
        self.cancel_tree.heading('Дата', text='Дата')
        self.cancel_tree.heading('Название', text='Название')
        
        self.cancel_tree.column('ID', width=50)
        self.cancel_tree.column('Тип', width=120)
        self.cancel_tree.column('Номер', width=100)
        self.cancel_tree.column('Дата', width=100)
        self.cancel_tree.column('Название', width=300)
        
        # Скроллбар для списка отмены
        cancel_v_scrollbar = ttk.Scrollbar(cancel_tree_frame, orient="vertical", command=self.cancel_tree.yview)
        self.cancel_tree.configure(yscrollcommand=cancel_v_scrollbar.set)
        
        self.cancel_tree.pack(side="left", fill="both", expand=True)
        cancel_v_scrollbar.pack(side="right", fill="y")
        
        # Привязка двойного клика для удаления
        self.cancel_tree.bind('<Double-1>', self.remove_from_cancel_list)
        
        # Список ID документов для отмены
        self.cancelled_documents = []
        
        # Кнопки
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            button_frame, 
            text="💾 Сохранить", 
            command=self.save,
            fg_color="#28a745",
            hover_color="#218838"
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="❌ Отмена", 
            command=self.cancel
        ).pack(side="right", padx=5)
    
    def choose_file(self):
        """Выбор файла"""
        filename = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[
                ("Все файлы", "*.*"),
                ("Word документы", "*.docx;*.doc"),
                ("PDF файлы", "*.pdf"),
                ("Текстовые файлы", "*.txt")
            ]
        )
        if filename:
            self.file_path.set(filename)
    

    
    def show_calendar(self):
        """Показать календарь для выбора даты"""
        # Создаем диалог календаря
        calendar_dialog = ctk.CTkToplevel(self.dialog)
        calendar_dialog.title("Выберите дату")
        calendar_dialog.geometry("300x350")
        calendar_dialog.transient(self.dialog)
        calendar_dialog.grab_set()
        
        # Импортируем tkcalendar
        try:
            from tkcalendar import Calendar
        except ImportError:
            # Если tkcalendar не установлен, используем простой диалог
            messagebox.showwarning("Предупреждение", "Для календаря установите: pip install tkcalendar")
            return
        
        # Создаем календарь
        cal = Calendar(
            calendar_dialog, 
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            locale='ru_RU'
        )
        cal.pack(padx=20, pady=20)
        
        # Кнопки
        button_frame = ctk.CTkFrame(calendar_dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def select_date():
            selected_date = cal.get_date()
            # Конвертируем в формат dd.MM.yyyy как в PyQt5
            try:
                from datetime import datetime
                date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d.%m.%Y')
                self.date_var.set(formatted_date)
            except:
                self.date_var.set(selected_date)
            calendar_dialog.destroy()
        
        ctk.CTkButton(
            button_frame, 
            text="Выбрать", 
            command=select_date,
            fg_color="#28a745",
            hover_color="#218838"
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame, 
            text="Отмена", 
            command=calendar_dialog.destroy
        ).pack(side="right", padx=5)
    
    
    
    def toggle_cancel_section(self):
        """Показать/скрыть секцию отмены документов"""
        if self.cancel_checkbox.get():
            self.cancel_section.pack(fill="x", padx=10, pady=(0, 10))
            self.load_documents_for_cancel()
        else:
            self.cancel_section.pack_forget()
    
    def load_documents_for_cancel(self):
        """Загрузка документов для возможной отмены"""
        # Очищаем список
        for item in self.documents_tree.get_children():
            self.documents_tree.delete(item)
        
        documents = self.database.get_all_documents()
        
        for doc in documents:
            # Исключаем текущий редактируемый документ и показываем только активные документы
            if doc['status'] == 'Активен' and (not self.document_data or doc['id'] != self.document_data.get('id')):
                self.documents_tree.insert('', 'end', values=(
                    doc['id'],
                    doc['document_type'],
                    doc['document_number'],
                    doc['document_date'],
                    doc['title'][:50] + "..." if len(doc['title']) > 50 else doc['title']
                ))
    
    def search_documents(self, *args):
        """Поиск документов"""
        search_text = self.search_var.get().strip().lower()
        
        # Очищаем список
        for item in self.documents_tree.get_children():
            self.documents_tree.delete(item)
        
        documents = self.database.get_all_documents()
        
        for doc in documents:
            # Исключаем текущий редактируемый документ и показываем только активные документы
            if doc['status'] == 'Активен' and (not self.document_data or doc['id'] != self.document_data.get('id')):
                # Фильтр по поиску
                if search_text and search_text not in doc['title'].lower() and search_text not in doc['document_number'].lower():
                    continue
                
                self.documents_tree.insert('', 'end', values=(
                    doc['id'],
                    doc['document_type'],
                    doc['document_number'],
                    doc['document_date'],
                    doc['title'][:50] + "..." if len(doc['title']) > 50 else doc['title']
                ))
    
    def add_to_cancel_list(self, event):
        """Добавить документ в список для отмены"""
        selection = self.documents_tree.selection()
        if not selection:
            return
        
        item = self.documents_tree.item(selection[0])
        doc_id = item['values'][0]
        
        # Проверяем, не добавлен ли уже
        for child in self.cancel_tree.get_children():
            if self.cancel_tree.item(child)['values'][0] == doc_id:
                return
        
        # Добавляем в список отмены
        self.cancel_tree.insert('', 'end', values=item['values'])
        self.cancelled_documents.append(doc_id)
    
    def remove_from_cancel_list(self, event):
        """Удалить документ из списка отмены"""
        selection = self.cancel_tree.selection()
        if not selection:
            return
        
        item = self.cancel_tree.item(selection[0])
        doc_id = item['values'][0]
        
        self.cancel_tree.delete(selection[0])
        if doc_id in self.cancelled_documents:
            self.cancelled_documents.remove(doc_id)
    
    def load_existing_relations(self):
        """Загрузка существующих связей документа при редактировании"""
        if not self.document_data or not self.database:
            return
        
        # Получаем связи, где текущий документ отменяет другие
        relations = self.database.get_document_relations(self.document_data.get('id'))
        
        if relations:
            # Показываем секцию отмены
            self.cancel_checkbox.select()
            self.cancel_section.pack(fill="x", padx=10, pady=(0, 10))
            
            # Загружаем отмененные документы в список
            for relation in relations:
                if relation[1] == self.document_data.get('id'):  # new_document_id
                    # Этот документ отменяет другой
                    doc_id = relation[2]  # cancelled_document_id
                    
                    # Получаем данные отмененного документа
                    documents = self.database.get_all_documents()
                    cancelled_doc = next((d for d in documents if d['id'] == doc_id), None)
                    
                    if cancelled_doc:
                        self.cancel_tree.insert('', 'end', values=(
                            cancelled_doc['id'],
                            cancelled_doc['document_type'],
                            cancelled_doc['document_number'],
                            cancelled_doc['document_date'],
                            cancelled_doc['title'][:50] + "..." if len(cancelled_doc['title']) > 50 else cancelled_doc['title']
                        ))
                        self.cancelled_documents.append(doc_id)
    
    def load_data(self):
        """Загрузка данных для редактирования"""
        if not self.document_data:
            return
        
        self.type_var.set(self.document_data['document_type'])
        self.number_var.set(self.document_data['document_number'].replace('№ ', ''))
        self.date_var.set(self.document_data['document_date'])
        self.title_var.set(self.document_data['title'])
        self.effective_date_var.set(self.document_data['effective_date'] or '')
        self.status_var.set(self.document_data['status'])
        if self.document_data.get('file_path'):
            self.file_path.set(self.document_data['file_path'])
        
        # Загружаем существующие связи
        self.load_existing_relations()
    
    def save(self):
        """Сохранение документа"""
        # Валидация
        if not self.type_var.get() or not self.number_var.get() or not self.date_var.get() or not self.title_var.get():
            messagebox.showerror("Ошибка", "Заполните все обязательные поля")
            return
        
        try:
            # Проверяем формат даты документа (dd.MM.yyyy как в PyQt5)
            if '.' in self.date_var.get():
                datetime.strptime(self.date_var.get(), '%d.%m.%Y')
            else:
                datetime.strptime(self.date_var.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты документа. Используйте DD.MM.YYYY")
            return
        
        # Подготавливаем данные
        doc_data = {
            'document_type': self.type_var.get(),
            'document_number': f"№ {self.number_var.get()}" if self.number_var.get() else "",
            'document_date': self.date_var.get(),
            'title': self.title_var.get(),
            'effective_date': self.effective_date_var.get() or None,
            'status': self.status_var.get(),
            'file_path': self.file_path.get() if self.file_path.get() else None,
            'cancelled_documents': self.cancelled_documents
        }
        
        try:
            if self.document_data:
                # Обновление
                success = self.database.update_document(
                    self.document_data['id'],
                    doc_data['document_type'],
                    doc_data['document_number'],
                    doc_data['document_date'],
                    doc_data['title'],
                    doc_data['effective_date'],
                    doc_data['status'],
                    doc_data['file_path'],
                    doc_data['cancelled_documents']
                )
                if success:
                    messagebox.showinfo("Успех", "Документ обновлен")
                    self.result = True
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить документ")
            else:
                # Добавление
                doc_id = self.database.add_document(
                    doc_data['document_type'],
                    doc_data['document_number'],
                    doc_data['document_date'],
                    doc_data['title'],
                    doc_data['effective_date'],
                    doc_data['status'],
                    doc_data['file_path'],
                    doc_data['cancelled_documents']
                )
                if doc_id:
                    messagebox.showinfo("Успех", "Документ добавлен")
                    self.result = True
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить документ")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def cancel(self):
        """Отмена"""
        self.dialog.destroy()

class RelationsDialog:
    """Диалог для просмотра связей между документами (как в PyQt5)"""
    
    def __init__(self, parent, database, document_id):
        self.parent = parent
        self.database = database
        self.document_id = document_id
        self.document_data = None
        
        # Получаем данные документа
        documents = self.database.get_all_documents()
        self.document_data = next((d for d in documents if d['id'] == document_id), None)
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Связи документа")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.load_relations()
    
    def setup_ui(self):
        """Настройка интерфейса диалога"""
        # Заголовок с информацией о документе
        if self.document_data:
            title_text = f"Связи документа: {self.document_data['document_type']} {self.document_data['document_number']}"
        else:
            title_text = "Связи документа"
            
        ctk.CTkLabel(
            self.dialog, 
            text=title_text,
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10))
        
        # Информация о документе
        if self.document_data:
            info_text = f"Название: {self.document_data['title']}"
            ctk.CTkLabel(
                self.dialog, 
                text=info_text,
                font=ctk.CTkFont(size=12),
                text_color="#666666"
            ).pack(pady=(0, 20))
        
        # Список связей
        relations_frame = ctk.CTkFrame(self.dialog)
        relations_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            relations_frame, 
            text="Связи документа:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.relations_list = ctk.CTkTextbox(relations_frame, height=250)
        self.relations_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Кнопки
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(
            button_frame, 
            text="Закрыть", 
            command=self.close,
            width=120
        ).pack(side="right", padx=5)
    
    def load_relations(self):
        """Загрузка связей документа"""
        if not self.database or not self.document_id:
            return
            
        relations = self.database.get_document_relations(self.document_id)
        self.relations_list.delete("1.0", "end")
        
        if not relations:
            self.relations_list.insert("1.0", "У этого документа нет связей с другими документами.")
            return
        
        # Разделяем связи на два типа
        cancels_others = []
        cancelled_by_others = []
        
        for relation in relations:
            if relation[1] == self.document_id:  # new_document_id
                # Этот документ отменяет другой
                cancels_others.append(relation)
            else:
                # Этот документ отменен другим
                cancelled_by_others.append(relation)
        
        relations_text = ""
        
        # Документы, которые отменяет этот документ
        if cancels_others:
            relations_text += "➡️ ЭТОТ ДОКУМЕНТ ОТМЕНЯЕТ:\n"
            relations_text += "=" * 50 + "\n"
            for relation in cancels_others:
                # Получаем полную информацию об отмененном документе
                cancelled_doc = self.get_document_info(relation[2])  # cancelled_document_id
                if cancelled_doc:
                    relations_text += f"• {cancelled_doc['document_type']} {cancelled_doc['document_number']}\n"
                    relations_text += f"  Дата: {cancelled_doc['document_date']}\n"
                    relations_text += f"  Название: {cancelled_doc['title']}\n"
                    relations_text += f"  Статус: {cancelled_doc['status']}\n\n"
            relations_text += "\n"
        
        # Документы, которые отменяют этот документ
        if cancelled_by_others:
            relations_text += "⬅️ ЭТОТ ДОКУМЕНТ ОТМЕНЕН:\n"
            relations_text += "=" * 50 + "\n"
            for relation in cancelled_by_others:
                # Получаем полную информацию об отменяющем документе
                cancelling_doc = self.get_document_info(relation[1])  # new_document_id
                if cancelling_doc:
                    relations_text += f"• {cancelling_doc['document_type']} {cancelling_doc['document_number']}\n"
                    relations_text += f"  Дата: {cancelling_doc['document_date']}\n"
                    relations_text += f"  Название: {cancelling_doc['title']}\n"
                    relations_text += f"  Статус: {cancelling_doc['status']}\n\n"
        
        self.relations_list.insert("1.0", relations_text)
    
    def get_document_info(self, doc_id):
        """Получение полной информации о документе по ID"""
        if not self.database:
            return None
            
        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, document_type, document_number, document_date, title, 
                   effective_date, status, file_path, created_at, updated_at
            FROM npa_documents
            WHERE id = ?
        ''', (doc_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = ['id', 'document_type', 'document_number', 'document_date', 'title', 
                      'effective_date', 'status', 'file_path', 'created_at', 'updated_at']
            return dict(zip(columns, row))
        
        return None
    
    def close(self):
        """Закрыть диалог"""
        self.dialog.destroy()

def main():
    """Главная функция"""
    # Создаем необходимые папки
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    for folder in ['documents', 'export']:
        folder_path = os.path.join(base_path, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    
    # Запускаем приложение
    app = NPAManager()
    app.run()

if __name__ == "__main__":
    main()
