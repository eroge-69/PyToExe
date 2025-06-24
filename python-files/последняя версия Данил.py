import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import os
import subprocess
from pathlib import Path
import json
import shutil


class BaseView(tk.Frame):
    """Базовый класс для всех view"""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#2c2c2c")
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        """Метод для создания элементов интерфейса"""
        pass

    def update_data(self, *args):
        """Метод для обновления данных"""
        pass


class MainMenu(BaseView):
    def create_widgets(self):
        # Main container for centering
        center_frame = tk.Frame(self, bg="#2c2c2c")
        center_frame.pack(expand=True, fill="both", padx=100, pady=50)

        # Header
        header_frame = tk.Frame(center_frame, bg="#ff8c00")
        header_frame.pack(fill="x", pady=(0, 20))
        tk.Label(header_frame, text="Библиотека для школьников",
                 bg="#ff8c00", fg="black", font=("Arial", 24)).pack(pady=10)

        # Поиск
        search_frame = tk.Frame(center_frame, bg="#2c2c2c")
        search_frame.pack(fill="x", pady=10)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 12))
        search_entry.pack(side="left", fill="x", expand=True)

        tk.Button(search_frame, text="Поиск",
                  command=self.perform_search,
                  font=("Arial", 12), bg="#ff8c00", fg="black").pack(side="left", padx=5)

        # Категории
        categories_frame = tk.Frame(center_frame, bg="#2c2c2c")
        categories_frame.pack(fill="both", expand=True, pady=10)

        for i, category in enumerate(self.controller.categories.keys()):
            row = i // 3
            col = i % 3

            btn_container = tk.Frame(categories_frame, bg="#2c2c2c")
            btn_container.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            btn_container.grid_rowconfigure(0, weight=1)
            btn_container.grid_columnconfigure(0, weight=1)

            tk.Button(btn_container, text=category,
                      command=lambda cat=category: self.controller.show_frame("CategoryView", cat),
                      font=("Arial", 14), bg="#ff8c00", fg="black",
                      width=20, height=2).grid(sticky="nsew")

        for i in range(2):
            categories_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            categories_frame.grid_columnconfigure(i, weight=1)

        # Кнопки внизу
        bottom_frame = tk.Frame(center_frame, bg="#2c2c2c")
        bottom_frame.pack(fill="x", pady=10)

        tk.Button(bottom_frame, text="Добавленные книги",
                  command=lambda: self.controller.show_frame("AddedBooksView"),
                  font=("Arial", 12), bg="#ff8c00", fg="black").pack(side="left", padx=10)

        tk.Button(bottom_frame, text="Выход",
                  command=self.controller.root.quit,
                  font=("Arial", 12), bg="#ff8c00", fg="black").pack(side="right", padx=10)

    def perform_search(self):
        query = self.search_var.get().strip()
        if query:
            results = self.controller.search_books(query)
            if results:
                self.controller.show_frame("SearchResultsView", results)
            else:
                messagebox.showinfo("Результаты поиска", "Ничего не найдено")


class CategoryView(BaseView):
    def create_widgets(self):
        # Main container for centering
        center_frame = tk.Frame(self, bg="#2c2c2c")
        center_frame.pack(expand=True, fill="both", padx=100, pady=20)

        # Header
        self.header_frame = tk.Frame(center_frame, bg="#ff8c00")
        self.header_frame.pack(fill="x", pady=(0, 20))

        self.back_button = tk.Button(self.header_frame, text="Назад",
                                     command=lambda: self.controller.show_frame("MainMenu"),
                                     font=("Arial", 12), bg="#ff8c00", fg="black")
        self.back_button.pack(side="left", padx=10)

        self.title_label = tk.Label(self.header_frame, text="",
                                    bg="#ff8c00", fg="black", font=("Arial", 20))
        self.title_label.pack(side="left", fill="x", expand=True, padx=10)

        # Контейнер для авторов
        self.authors_container = tk.Frame(center_frame, bg="#2c2c2c")
        self.authors_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.authors_container, bg="#2c2c2c", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.authors_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#2c2c2c")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.center_frame = tk.Frame(self.scrollable_frame, bg="#2c2c2c")
        self.center_frame.pack(expand=True)

    def update_data(self, category):
        self.category = category
        self.title_label.config(text=category)

        for widget in self.center_frame.winfo_children():
            widget.destroy()

        authors = self.controller.categories.get(category, [])
        num_columns = 3

        for i, author in enumerate(authors):
            row = i // num_columns
            col = i % num_columns

            if col == 0:
                row_frame = tk.Frame(self.center_frame, bg="#2c2c2c")
                row_frame.pack(fill="x", pady=5)

            btn_frame = tk.Frame(row_frame, bg="#2c2c2c")
            btn_frame.pack(side="left", expand=True, padx=10)

            tk.Button(btn_frame, text=author,
                      command=lambda a=author: self.controller.show_frame("AuthorView", a),
                      font=("Arial", 14), bg="#ff8c00", fg="black",
                      width=25).pack(pady=5)


class AuthorView(BaseView):
    def create_widgets(self):
        # Main container for centering
        center_frame = tk.Frame(self, bg="#2c2c2c")
        center_frame.pack(expand=True, fill="both", padx=100, pady=20)

        # Header
        self.header_frame = tk.Frame(center_frame, bg="#ff8c00")
        self.header_frame.pack(fill="x", pady=(0, 20))

        self.back_button = tk.Button(self.header_frame, text="Назад",
                                     command=lambda: self.controller.show_frame("CategoryView", self.category),
                                     font=("Arial", 12), bg="#ff8c00", fg="black")
        self.back_button.pack(side="left", padx=10)

        self.title_label = tk.Label(self.header_frame, text="",
                                    bg="#ff8c00", fg="black", font=("Arial", 20))
        self.title_label.pack(side="left", fill="x", expand=True, padx=10)

        # Книги
        self.books_frame = tk.Frame(center_frame, bg="#2c2c2c")
        self.books_frame.pack(fill="both", expand=True, pady=10)

        # Scrollbar
        self.canvas = tk.Canvas(self.books_frame, bg="#2c2c2c", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.books_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#2c2c2c")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def update_data(self, author):
        self.author = author
        self.category = self.get_author_category(author)
        self.title_label.config(text=author)

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if author in self.controller.books:
            for work in self.controller.books[author]["works"]:
                tk.Button(self.scrollable_frame, text=work,
                          command=lambda w=work: self.controller.show_frame("BookView", author, w),
                          font=("Arial", 14), bg="#ff8c00", fg="black",
                          width=40).pack(pady=5)
        else:
            tk.Label(self.scrollable_frame, text="Информация о произведениях отсутствует",
                     bg="#2c2c2c", fg="white", font=("Arial", 14)).pack(pady=20)

        tk.Button(self.scrollable_frame, text="Добавить книгу этого автора",
                  command=lambda: self.controller.show_frame("AddedBooksView", author),
                  font=("Arial", 12), bg="#ff8c00", fg="black").pack(pady=10)

    def get_author_category(self, author):
        for category, authors in self.controller.categories.items():
            if author in authors:
                return category
        return ""


class BookView(BaseView):
    def create_widgets(self):
        # Main container for centering
        center_frame = tk.Frame(self, bg="#2c2c2c")
        center_frame.pack(expand=True, fill="both", padx=100, pady=20)

        # Header
        self.header_frame = tk.Frame(center_frame, bg="#ff8c00")
        self.header_frame.pack(fill="x", pady=(0, 20))

        self.back_button = tk.Button(self.header_frame, text="Назад",
                                     command=lambda: self.controller.show_frame("AuthorView", self.author),
                                     font=("Arial", 12), bg="#ff8c00", fg="black")
        self.back_button.pack(side="left", padx=10)

        self.title_label = tk.Label(self.header_frame, text="",
                                    bg="#ff8c00", fg="black", font=("Arial", 20))
        self.title_label.pack(side="left", fill="x", expand=True, padx=10)

        # Информация о книге
        self.info_frame = tk.Frame(center_frame, bg="#2c2c2c")
        self.info_frame.pack(fill="both", expand=True, pady=20)

        self.book_info = tk.Label(self.info_frame, text="",
                                  bg="#2c2c2c", fg="white", font=("Arial", 14),
                                  justify="left")
        self.book_info.pack(fill="both", expand=True)

        # Кнопки
        self.buttons_frame = tk.Frame(center_frame, bg="#2c2c2c")
        self.buttons_frame.pack(fill="x", pady=10)

        self.open_button = tk.Button(self.buttons_frame, text="Открыть книгу (PDF)",
                                     command=self.open_book,
                                     font=("Arial", 12), bg="#ff8c00", fg="black")
        self.open_button.pack(pady=5)

        self.add_pdf_button = tk.Button(self.buttons_frame, text="Добавить PDF к книге",
                                        command=self.add_pdf_to_book,
                                        font=("Arial", 12), bg="#ff8c00", fg="black")
        self.add_pdf_button.pack(pady=5)

    def update_data(self, author, title):
        self.author = author
        self.title = title
        self.title_label.config(text=title)

        pdf_path = self.controller.get_book_pdf_path(author, title)
        if pdf_path:
            self.open_button.config(state="normal")
            self.book_info.config(text=f"Автор: {author}\nНазвание: {title}\n\nPDF файл доступен")
        else:
            self.open_button.config(state="disabled")
            self.book_info.config(text=f"Автор: {author}\nНазвание: {title}\n\nPDF файл отсутствует")

            is_added = any(b["author"] == author and b["title"] == title for b in self.controller.added_books)
            if is_added:
                self.add_pdf_button.config(state="normal")
            else:
                self.add_pdf_button.config(state="disabled")

    def open_book(self):
        pdf_path = self.controller.get_book_pdf_path(self.author, self.title)
        if pdf_path:
            self.controller.open_pdf(pdf_path)
        else:
            messagebox.showwarning("Ошибка", "PDF файл не найден")

    def add_pdf_to_book(self):
        pdf_path = filedialog.askopenfilename(
            title="Выберите PDF файл",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if not pdf_path:
            return

        for book in self.controller.added_books:
            if book["author"] == self.author and book["title"] == self.title:
                pdf_filename = f"{self.author}_{self.title}.pdf".replace(" ", "_").lower()
                dest_path = self.controller.library_folder / pdf_filename

                try:
                    shutil.copy(pdf_path, dest_path)
                    book["pdf_file"] = pdf_filename
                    self.controller.save_added_books()
                    messagebox.showinfo("Успех", "PDF файл успешно добавлен к книге!")
                    self.update_data(self.author, self.title)
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось скопировать файл: {e}")
                return

        messagebox.showwarning("Ошибка", "Книга не найдена в добавленных")


class AddedBooksView(BaseView):
    def create_widgets(self):
        # Main container for centering
        center_frame = tk.Frame(self, bg="#2c2c2c")
        center_frame.pack(expand=True, fill="both", padx=100, pady=20)

        # Header
        self.header_frame = tk.Frame(center_frame, bg="#ff8c00")
        self.header_frame.pack(fill="x", pady=(0, 20))

        self.back_button = tk.Button(self.header_frame, text="Назад",
                                     command=lambda: self.controller.show_frame("MainMenu"),
                                     font=("Arial", 12), bg="#ff8c00", fg="black")
        self.back_button.pack(side="left", padx=10)

        self.title_label = tk.Label(self.header_frame, text="Добавленные книги",
                                    bg="#ff8c00", fg="black", font=("Arial", 20))
        self.title_label.pack(side="left", fill="x", expand=True, padx=10)

        # Книги
        self.books_frame = tk.Frame(center_frame, bg="#2c2c2c")
        self.books_frame.pack(fill="both", expand=True, pady=10)

        # Scrollbar
        self.canvas = tk.Canvas(self.books_frame, bg="#2c2c2c", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.books_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#2c2c2c")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Кнопка добавления
        self.add_button = tk.Button(center_frame, text="Добавить новую книгу",
                                    command=self.add_book,
                                    font=("Arial", 12), bg="#ff8c00", fg="black")
        self.add_button.pack(pady=10)

    def update_data(self, preset_author=None):
        self.preset_author = preset_author
        if preset_author:
            self.title_label.config(text=f"Добавить книгу автора: {preset_author}")

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for i, book in enumerate(self.controller.added_books):
            if self.preset_author and book["author"] != self.preset_author:
                continue

            book_frame = tk.Frame(self.scrollable_frame, bg="#3c3c3c")
            book_frame.pack(fill="x", pady=5, padx=10)

            tk.Label(book_frame,
                     text=f"{book['title']} - {book['author']}",
                     bg="#3c3c3c", fg="white", font=("Arial", 12),
                     anchor="w").pack(side="left", fill="x", expand=True)

            btn_frame = tk.Frame(book_frame, bg="#3c3c3c")
            btn_frame.pack(side="right")

            if book.get("pdf_file"):
                tk.Button(btn_frame, text="Открыть",
                          command=lambda b=book: self.open_book(b),
                          font=("Arial", 10), bg="#ff8c00", fg="black").pack(side="left", padx=2)

            tk.Button(btn_frame, text="Удалить",
                      command=lambda idx=i: self.delete_book(idx),
                      font=("Arial", 10), bg="#ff8c00", fg="black").pack(side="left", padx=2)

    def add_book(self):
        add_window = tk.Toplevel(self.controller.root)
        add_window.title("Добавить книгу")
        add_window.geometry("400x300")
        add_window.configure(bg="#2c2c2c")

        tk.Label(add_window, text="Добавить новую книгу",
                 bg="#2c2c2c", fg="#ff8c00",
                 font=("Arial", 16)).pack(pady=10)

        tk.Label(add_window, text="Автор:", bg="#2c2c2c", fg="white").pack()
        author_entry = tk.Entry(add_window, font=("Arial", 12))
        if self.preset_author:
            author_entry.insert(0, self.preset_author)
            author_entry.config(state='readonly')
        author_entry.pack(pady=5)

        tk.Label(add_window, text="Название:", bg="#2c2c2c", fg="white").pack()
        title_entry = tk.Entry(add_window, font=("Arial", 12))
        title_entry.pack(pady=5)

        pdf_path = tk.StringVar()
        tk.Label(add_window, text="PDF файл (необязательно):", bg="#2c2c2c", fg="white").pack()
        tk.Button(add_window, text="Выбрать файл",
                  command=lambda: self.select_pdf_file(pdf_path),
                  font=("Arial", 12), bg="#ff8c00", fg="black").pack(pady=5)
        tk.Label(add_window, textvariable=pdf_path, bg="#2c2c2c", fg="white", wraplength=300).pack()

        tk.Button(add_window, text="Добавить",
                  command=lambda: self.save_book(
                      author_entry.get(),
                      title_entry.get(),
                      pdf_path.get(),
                      add_window
                  ),
                  font=("Arial", 14), bg="#ff8c00", fg="black").pack(pady=20)

    def select_pdf_file(self, pdf_path_var):
        file_path = filedialog.askopenfilename(
            title="Выберите PDF файл",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            pdf_path_var.set(file_path)

    def save_book(self, author, title, pdf_path, add_window):
        if not author or not title:
            messagebox.showwarning("Ошибка", "Укажите автора и название книги!")
            return

        for book in self.controller.added_books:
            if book["author"].lower() == author.lower() and book["title"].lower() == title.lower():
                messagebox.showwarning("Ошибка", "Такая книга уже существует!")
                return

        pdf_filename = None
        if pdf_path:
            pdf_filename = f"{author}_{title}.pdf".replace(" ", "_").lower()
            dest_path = self.controller.library_folder / pdf_filename

            try:
                shutil.copy(pdf_path, dest_path)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось скопировать файл: {e}")
                return

        self.controller.added_books.append({
            "author": author,
            "title": title,
            "pdf_file": pdf_filename
        })

        self.controller.save_added_books()
        add_window.destroy()
        self.update_data(self.preset_author)
        messagebox.showinfo("Успех", "Книга успешно добавлена!")

    def open_book(self, book):
        pdf_path = self.controller.library_folder / book["pdf_file"]
        if pdf_path.exists():
            self.controller.open_pdf(pdf_path)
        else:
            messagebox.showwarning("Ошибка", "PDF файл не найден!")

    def delete_book(self, index):
        book = self.controller.added_books[index]

        if book.get("pdf_file"):
            pdf_path = self.controller.library_folder / book["pdf_file"]
            try:
                if pdf_path.exists():
                    pdf_path.unlink()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить файл: {e}")

        self.controller.added_books.pop(index)
        self.controller.save_added_books()

        self.update_data(self.preset_author)
        messagebox.showinfo("Успех", "Книга удалена!")


class SearchResultsView(BaseView):
    def create_widgets(self):
        # Main container for centering
        center_frame = tk.Frame(self, bg="#2c2c2c")
        center_frame.pack(expand=True, fill="both", padx=100, pady=20)

        # Header
        self.header_frame = tk.Frame(center_frame, bg="#ff8c00")
        self.header_frame.pack(fill="x", pady=(0, 20))

        self.back_button = tk.Button(self.header_frame, text="Назад",
                                     command=lambda: self.controller.show_frame("MainMenu"),
                                     font=("Arial", 12), bg="#ff8c00", fg="black")
        self.back_button.pack(side="left", padx=10)

        self.title_label = tk.Label(self.header_frame, text="Результаты поиска",
                                    bg="#ff8c00", fg="black", font=("Arial", 20))
        self.title_label.pack(side="left", fill="x", expand=True, padx=10)

        # Результаты
        self.results_frame = tk.Frame(center_frame, bg="#2c2c2c")
        self.results_frame.pack(fill="both", expand=True, pady=10)

        # Scrollbar
        self.canvas = tk.Canvas(self.results_frame, bg="#2c2c2c", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.results_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#2c2c2c")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def update_data(self, results):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for result in results:
            result_type, author, title = result

            result_frame = tk.Frame(self.scrollable_frame, bg="#3c3c3c")
            result_frame.pack(fill="x", pady=5, padx=10)

            tk.Label(result_frame,
                     text=f"{title} - {author}",
                     bg="#3c3c3c", fg="white", font=("Arial", 12),
                     anchor="w").pack(side="left", fill="x", expand=True)

            tk.Button(result_frame, text="Открыть",
                      command=lambda a=author, t=title: self.open_book(a, t),
                      font=("Arial", 10), bg="#ff8c00", fg="black").pack(side="right", padx=2)

    def open_book(self, author, title):
        pdf_path = self.controller.get_book_pdf_path(author, title)
        if pdf_path:
            self.controller.open_pdf(pdf_path)
        else:
            info_window = tk.Toplevel(self.controller.root)
            info_window.title(title)
            info_window.geometry("400x200")
            info_window.configure(bg="#2c2c2c")

            tk.Label(info_window, text=f"{title}\nАвтор: {author}",
                     bg="#2c2c2c", fg="white", font=("Arial", 16)).pack(pady=20)

            if any(b["author"] == author and b["title"] == title for b in self.controller.added_books):
                tk.Button(info_window, text="Добавить PDF к этой книге",
                          command=lambda: self.add_pdf_to_book(author, title, info_window),
                          font=("Arial", 12), bg="#ff8c00", fg="black").pack(pady=10)

            tk.Button(info_window, text="Закрыть", command=info_window.destroy,
                      font=("Arial", 14), bg="#ff8c00", fg="black").pack(pady=10)

    def add_pdf_to_book(self, author, title, parent_window):
        pdf_path = filedialog.askopenfilename(
            title="Выберите PDF файл",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if not pdf_path:
            return

        for book in self.controller.added_books:
            if book["author"] == author and book["title"] == title:
                pdf_filename = f"{author}_{title}.pdf".replace(" ", "_").lower()
                dest_path = self.controller.library_folder / pdf_filename

                try:
                    shutil.copy(pdf_path, dest_path)
                    book["pdf_file"] = pdf_filename
                    self.controller.save_added_books()
                    messagebox.showinfo("Успех", "PDF файл успешно добавлен к книге!")
                    parent_window.destroy()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось скопировать файл: {e}")
                return

        messagebox.showwarning("Ошибка", "Книга не найдена в добавленных")


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Библиотека для школьников")
        self.root.state('zoomed')  # Открытие окна на весь экран
        self.root.configure(bg="#2c2c2c")

        # Основная папка для хранения книг
        self.library_folder = Path(r"Y:\Программист\книги")
        self.library_folder.mkdir(exist_ok=True, parents=True)

        # Файл для хранения добавленных книг
        self.added_books_file = self.library_folder / "added_books.json"

        # Загрузка добавленных книг
        self.added_books = self.load_added_books()

        # Расширенная база данных книг
        self.categories = {
            "Русская классика": [
                "Лев Толстой", "Федор Достоевский", "Александр Пушкин",
                "Николай Гоголь", "Антон Чехов", "Иван Тургенев",
                "Михаил Лермонтов", "Иван Бунин", "Александр Островский"
            ],
            "Зарубежная классика": [
                "Уильям Шекспир", "Чарльз Диккенс", "Марк Твен",
                "Эрнест Хемингуэй", "Джек Лондон", "Джейн Остин",
                "Артур Конан Дойл", "Жюль Верн", "Герман Мелвилл"
            ],
            "Поэзия": [
                "Александр Пушкин", "Михаил Лермонтов", "Сергей Есенин",
                "Анна Ахматова", "Марина Цветаева", "Борис Пастернак",
                "Владимир Маяковский", "Иосиф Бродский", "Александр Блок"
            ],
            "Фантастика": [
                "Аркадий и Борис Стругацкие", "Станислав Лем", "Айзек Азимов",
                "Рэй Брэдбери", "Роберт Хайнлайн", "Филип Дик",
                "Джордж Оруэлл", "Герберт Уэллс", "Кир Булычёв"
            ],
            "Детская литература": [
                "Корней Чуковский", "Агния Барто", "Самуил Маршак",
                "Николай Носов", "Виктор Драгунский", "Эдуард Успенский",
                "Астрид Линдгрен", "Алан Милн", "Туве Янссон"
            ],
            "Современная проза": [
                "Виктор Пелевин", "Борис Акунин", "Людмила Улицкая",
                "Захар Прилепин", "Дина Рубина", "Татьяна Толстая",
                "Михаил Шишкин", "Алексей Иванов", "Гузель Яхина"
            ]
        }

        self.books = {
            "Лев Толстой": {
                "works": ["Война и мир", "Анна Каренина", "Воскресение"],
                "pdf_files": ["tolstoy_voyna_i_mir.pdf", "tolstoy_anna_karenina.pdf", "tolstoy_voskresenie.pdf"]
            },
            "Федор Достоевский": {
                "works": ["Преступление и наказание", "Идиот", "Братья Карамазовы"],
                "pdf_files": ["dostoevsky_prestuplenie_i_nakazanie.pdf", "dostoevsky_idiot.pdf",
                              "dostoevsky_bratya_karamazovy.pdf"]
            },
            "Александр Пушкин": {
                "works": ["Евгений Онегин", "Сказка о царе Салтане", "Руслан и Людмила"],
                "pdf_files": ["pushkin_evgenyi_onegin.pdf", "pushkin_skazka_o_tsare_saltane.pdf",
                              "pushkin_ruslan_i_lyudmila.pdf"]
        },
            "Николай Гоголь": {
                "works": ["Тарас Бульба", "Мёртвые души", "Ревизор"],
                "pdf_files": ["gogol_taras_bulba.pdf", "gogol_mertvie_dushi.pdf",
                              "gogol_revizor.pdf"]
            },
            "Антон Чехов": {
                "works": ["Палата №6", "Человек в футляре", "Каштанка"],
                "pdf_files": ["Chekhov_Palata_6.pdf", "Chekhov_Chelovek_v_futlyare.pdf",
                              "Chekhov_Kashtanka.pdf"]
            },
            "Иван Тургенев": {
                "works": ["Отцы и дети", "Дворянское гнездо", "Ася"],
                "pdf_files": ["Turgenev_Otcy_i_deti.pdf", "Turgenev_Dvoryanskoe_gnezdo.pdf",
                              "Turgenev_Asya.pdf"]
            },
            "Михаил Лермонтов": {
                "works": ["Герой нашего времени", "Бородино", "Демон"],
                "pdf_files": ["Lermontov_Geroi_nashego_vremeni.pdf", "Lermontov_Borodino.pdf",
                              "Lermontov_Demon.pdf"]
            },
            "Иван Бунин": {
                "works": ["Тёмные аллеи", "Жизнь Арсеньева", "Антоновские яблоки"],
                "pdf_files": ["Bunin_Temnye_allei.pdf", "Bunin_Zisn_Arsenieva.pdf",
                              "bunin_antonovskie.pdf"]
            },
            "Александр Островский": {
                "works": ["Гроза", "Свои люди — сочтёмся!", "Снегурочка"],
                "pdf_files": ["Ostrovski_Groza.pdf", "Ostrovsky_Svoi_lyudi_sochtemsya.pdf",
                              "Ostrovsky_Snegurochka.pdf"]
            },
            "Уильям Шекспир": {
                "works": ["Ромео и Джульетта", "Гамлет", "Отелло"],
                "pdf_files": ["Shakespeare_Romeo_i_Dzhuletta.pdf", "Shakespeare_Hamlet.pdf",
                              "Shakespeare_Othello.pdf"]
            },
            "Чарльз Диккенс": {
                "works": ["Приключения Оливера Твиста", "Большие надежды", "Домби и Сын"],
                "pdf_files": ["Dikkens_Priklyucheniya_Olivera_Tvista.pdf", "Dikkens_Bolshie_nadezhdy.pdf",
                              "Dikkens_Dombi_i_syn.pdf"]
            },
            "Марк Твен": {
                "works": ["Приключения Тома Сойера", "Янки при дворе короля Артура", "Принц и нищий"],
                "pdf_files": ["Tven_Priklyucheniya_Toma_Soiera.pdf", "mark-tven-yanki-pri-dvore-korolya-artura.pdf",
                              "Twen_Prints_i_nishii.pdf"]
            },
            "Эрнест Хемингуэй": {
                "works": ["Старик и море", "Прощай, оружие!", "По ком звонит колокол"],
                "pdf_files": ["bt_0018.pdf", "143.pdf",
                              "3028d27c639560210f52cbdbb3de71db.pdf"]
            },
            "Джек Лондон": {
                "works": ["Мартин Иден", "Белый клык", "Зов предков"],
                "pdf_files": ["London_Martin_Iden.pdf", "London_Belyi_klyk.pdf",
                              "Д.Лондон-Зов-предков.pdf"]
            },
            "Джейн Остин": {
                "works": ["Гордость и предубеждение", "Чувство и чувствительность", "Мэнсфилд-парк"],
                "pdf_files": ["Austen_Gordost_i_predubezhdenie.pdf", "Austen_Chuvstvo_i_chuvstvitelnost_(razum_i_chuvstvo).pdf",
                              "Austen_Mensfild_park.pdf"]
            },
            "Артур Конан Дойл": {
                "works": ["Этюд в багровых тонах", "Знак четырёх", "Собака Баскервилей"],
                "pdf_files": ["Konan_Doyle_Etyud_v_bagrovyh_tonah.pdf", "Konan_Doyle_Znak_chetyreh.pdf",
                              "Konan_Doil_Sobaka_Baskervilei.pdf"]
            },
            "Жюль Верн": {
                "works": ["Двадцать тысяч лье под водой", "Вокруг света в восемьдесят дней", "Путешествие к центру Земли"],
                "pdf_files": ["Vern_Dvadtsat_tysyach_lie_pod_vodoi.pdf", "Verne_Vokrug_sveta_za_vosemdesyat_dnei.pdf",
                              "Vern_Puteshestvie_k_tsentru_Zemli.pdf"]
            },
            "Герман Мелвилл": {
                "works": ["Моби Дик, или Белый кит", "Пьер, или Двусмысленности", "Писец Бартлби"],
                "pdf_files": ["Melville_Mobi_Dik_ili_belyi_kit.pdf", "94698625.a4.pdf",
                              "70773880.a4.pdf"]
            },
        }

        # Создаем главный контейнер
        self.main_container = tk.Frame(root, bg="#2c2c2c")
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Все фреймы будут храниться здесь
        self.frames = {}

        # Создаем все экраны
        for F in (MainMenu, CategoryView, AuthorView, BookView, AddedBooksView, SearchResultsView):
            frame = F(self.main_container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Показываем главное меню
        self.show_frame("MainMenu")

    def load_added_books(self):
        try:
            if self.added_books_file.exists():
                with open(self.added_books_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
        return []

    def save_added_books(self):
        try:
            with open(self.added_books_file, 'w', encoding='utf-8') as f:
                json.dump(self.added_books, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def show_frame(self, frame_name, *args):
        frame = self.frames[frame_name]
        if hasattr(frame, 'update_data'):
            frame.update_data(*args)
        frame.tkraise()

    def open_pdf(self, pdf_path):
        try:
            if os.name == 'nt':
                os.startfile(pdf_path)
            elif os.name == 'posix':
                subprocess.run(['xdg-open', str(pdf_path)])
            else:
                subprocess.run(['open', str(pdf_path)], check=True)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def search_books(self, query):
        query = query.lower().strip()
        results = []

        for author, data in self.books.items():
            if query in author.lower():
                for work in data["works"]:
                    results.append(("author", author, work))

            for work in data["works"]:
                if query in work.lower():
                    results.append(("author", author, work))

        for book in self.added_books:
            if (query in book["author"].lower() or
                    query in book["title"].lower()):
                results.append(("added", book["author"], book["title"]))

        return results

    def get_book_pdf_path(self, author, title):
        if author in self.books:
            works = self.books[author]["works"]
            if title in works:
                index = works.index(title)
                pdf_files = self.books[author].get("pdf_files", [])
                if index < len(pdf_files):
                    pdf_path = self.library_folder / pdf_files[index]
                    if pdf_path.exists():
                        return pdf_path

        for book in self.added_books:
            if book["author"] == author and book["title"] == title and book.get("pdf_file"):
                pdf_path = self.library_folder / book["pdf_file"]
                if pdf_path.exists():
                    return pdf_path

        return None


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()