import tkinter as tk
from tkinter import scrolledtext, messagebox, Listbox
import json
import os
from datetime import datetime
import random

class CassetteFuturismDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("АНАЛОГОВЫЙ ДНЕВНИК v2.0")
        self.root.geometry("800x600")
        self.root.configure(bg='#000000')
        
        # Цветовая схема в стиле кассетного футуризма
        self.bg_color = '#000000'  # Черный фон
        self.text_color = '#ff8c00'  # Темно-оранжевый текст
        self.green_text = '#556b2f'  # Темно-зеленый текст
        self.beige_text = '#f5f5dc'  # Бежевый текст
        self.accent_color = '#8b4513'  # Коричневый для акцентов
        self.frame_color = '#1a1a1a'  # Темно-серый для рамок
        
        # Заголовок
        title_label = tk.Label(root, 
                              text="≪ АНАЛОГОВЫЙ ДНЕВНИК ≫",
                              font=('Courier New', 16, 'bold'),
                              fg=self.text_color,
                              bg=self.bg_color)
        title_label.pack(pady=10)
        
        # Основной фрейм
        main_frame = tk.Frame(root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Фрейм для списка заметок
        list_frame = tk.Frame(main_frame, bg=self.bg_color)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Заголовок списка
        list_title = tk.Label(list_frame, 
                             text="СПИСОК ЗАПИСЕЙ:",
                             font=('Courier New', 10, 'bold'),
                             fg=self.text_color,
                             bg=self.bg_color)
        list_title.pack(anchor='w')
        
        # Список заметок
        self.notes_list = Listbox(list_frame, 
                                 bg=self.frame_color, 
                                 fg=self.beige_text,
                                 font=('Courier New', 11),
                                 selectbackground=self.green_text,
                                 selectforeground=self.beige_text,
                                 height=20, 
                                 width=35,
                                 relief='sunken',
                                 borderwidth=2)
        self.notes_list.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Фрейм для кнопок
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(side=tk.RIGHT, padx=10)
        
        # Кнопки управления
        self.create_button(button_frame, "НОВАЯ ЗАПИСЬ", self.new_note).pack(pady=5)
        self.create_button(button_frame, "РЕДАКТИРОВАТЬ", self.edit_note).pack(pady=5)
        self.create_button(button_frame, "ПРОСМОТР", self.view_note).pack(pady=5)
        self.create_button(button_frame, "УДАЛИТЬ", self.delete_note).pack(pady=5)
        
        # Статусная строка
        self.status_label = tk.Label(root,
                                    text="СИСТЕМА ГОТОВА",
                                    font=('Courier New', 9),
                                    fg=self.green_text,
                                    bg=self.bg_color)
        self.status_label.pack(side=tk.BOTTOM, pady=5)
        
        # Загрузка заметок
        self.load_notes()
        self.notes_list.bind('<Double-1>', self.view_note)

    def create_button(self, parent, text, command):
        return tk.Button(parent,
                        text=text,
                        font=('Courier New', 10, 'bold'),
                        fg=self.text_color,
                        bg=self.frame_color,
                        activeforeground=self.beige_text,
                        activebackground=self.green_text,
                        relief='raised',
                        borderwidth=2,
                        command=command,
                        width=15)

    def load_notes(self):
        self.notes_list.delete(0, tk.END)
        if os.path.exists('notes.json'):
            try:
                with open('notes.json', 'r', encoding='utf-8') as f:
                    self.notes = json.load(f)
                for note in self.notes:
                    display_date = note['date'][:10]
                    self.notes_list.insert(tk.END, f"{display_date} | {note['title']}")
            except:
                self.notes = []
                self.status_label.config(text="ОШИБКА ЗАГРУЗКИ")
        else:
            self.notes = []

    def new_note(self):
        self.open_editor(None)

    def edit_note(self):
        if self.notes_list.curselection():
            index = self.notes_list.curselection()[0]
            self.open_editor(index)
        else:
            self.status_label.config(text="ВЫБЕРИТЕ ЗАПИСЬ")
            self.root.after(2000, lambda: self.status_label.config(text="СИСТЕМА ГОТОВА"))

    def view_note(self, event=None):
        if self.notes_list.curselection():
            index = self.notes_list.curselection()[0]
            self.open_viewer(index)
        else:
            self.status_label.config(text="ВЫБЕРИТЕ ЗАПИСЬ")
            self.root.after(2000, lambda: self.status_label.config(text="СИСТЕМА ГОТОВА"))

    def delete_note(self):
        if self.notes_list.curselection():
            index = self.notes_list.curselection()[0]
            if messagebox.askyesno("ПОДТВЕРЖДЕНИЕ", "СТЕРЕТЬ ЗАПИСЬ?"):
                del self.notes[index]
                self.save_notes()
                self.load_notes()
                self.status_label.config(text="ЗАПИСЬ УДАЛЕНА")
                self.root.after(2000, lambda: self.status_label.config(text="СИСТЕМА ГОТОВА"))
        else:
            self.status_label.config(text="ВЫБЕРИТЕ ЗАПИСЬ")
            self.root.after(2000, lambda: self.status_label.config(text="СИСТЕМА ГОТОВА"))

    def open_editor(self, index):
        editor = tk.Toplevel(self.root)
        editor.title("РЕДАКТОР" if index is not None else "НОВАЯ ЗАПИСЬ")
        editor.configure(bg=self.bg_color)
        editor.geometry("600x500")
        
        # Заголовок
        tk.Label(editor, 
                text="ЗАГОЛОВОК:",
                fg=self.text_color, 
                bg=self.bg_color,
                font=('Courier New', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        
        title_var = tk.StringVar()
        title_entry = tk.Entry(editor, 
                              textvariable=title_var, 
                              font=('Courier New', 12),
                              width=50, 
                              fg=self.beige_text, 
                              bg=self.frame_color,
                              insertbackground=self.text_color,
                              relief='sunken',
                              borderwidth=2)
        title_entry.pack(padx=10, pady=(0, 10))
        
        # Содержание
        tk.Label(editor, 
                text="СОДЕРЖАНИЕ:",
                fg=self.text_color, 
                bg=self.bg_color,
                font=('Courier New', 10, 'bold')).pack(anchor='w', padx=10, pady=(0, 5))
        
        content_text = scrolledtext.ScrolledText(editor, 
                                                font=('Courier New', 11),
                                                bg=self.frame_color, 
                                                fg=self.beige_text,
                                                insertbackground=self.text_color,
                                                relief='sunken',
                                                borderwidth=2,
                                                width=58, 
                                                height=20)
        content_text.pack(padx=10, pady=(0, 10))
        
        # Заполнение данных если редактируем
        if index is not None:
            title_var.set(self.notes[index]['title'])
            content_text.insert(tk.END, self.notes[index]['content'])
        
        # Кнопки управления
        button_frame = tk.Frame(editor, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        def save_note():
            title = title_var.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            
            if not title:
                self.status_label.config(text="ВВЕДИТЕ ЗАГОЛОВОК")
                return
            
            note_data = {
                'title': title,
                'date': datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                'content': content
            }
            
            if index is None:
                self.notes.append(note_data)
            else:
                self.notes[index] = note_data
            
            self.save_notes()
            self.load_notes()
            self.status_label.config(text="ЗАПИСЬ СОХРАНЕНА")
            editor.destroy()
        
        def cancel_edit():
            editor.destroy()
        
        self.create_button(button_frame, "СОХРАНИТЬ", save_note).pack(side=tk.LEFT, padx=5)
        self.create_button(button_frame, "ОТМЕНА", cancel_edit).pack(side=tk.LEFT, padx=5)

    def open_viewer(self, index):
        viewer = tk.Toplevel(self.root)
        viewer.title("ПРОСМОТР ЗАПИСИ")
        viewer.configure(bg=self.bg_color)
        viewer.geometry("500x400")
        
        # Заголовок и дата
        title_label = tk.Label(viewer,
                              text=self.notes[index]['title'],
                              font=('Courier New', 14, 'bold'),
                              fg=self.text_color,
                              bg=self.bg_color)
        title_label.pack(pady=(10, 5))
        
        date_label = tk.Label(viewer,
                             text=self.notes[index]['date'],
                             font=('Courier New', 10),
                             fg=self.green_text,
                             bg=self.bg_color)
        date_label.pack(pady=(0, 10))
        
        # Разделитель
        separator = tk.Frame(viewer, height=2, bg=self.frame_color)
        separator.pack(fill=tk.X, padx=10, pady=5)
        
        # Содержание
        content_text = scrolledtext.ScrolledText(viewer, 
                                                font=('Courier New', 11),
                                                bg=self.frame_color, 
                                                fg=self.beige_text,
                                                wrap=tk.WORD,
                                                state='disabled',
                                                relief='flat')
        content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Вставляем текст
        content_text.config(state='normal')
        content_text.insert(tk.END, self.notes[index]['content'])
        content_text.config(state='disabled')
        
        # Кнопка закрытия
        self.create_button(viewer, "ЗАКРЫТЬ", viewer.destroy).pack(pady=10)

    def save_notes(self):
        with open('notes.json', 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = CassetteFuturismDiary(root)
    root.mainloop()