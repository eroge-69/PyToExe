import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from llama_cpp import Llama
from PyPDF2 import PdfReader
from docx import Document
from typing import List
import re
from PIL import Image, ImageDraw, ImageFont
import math

# завантаження моделі
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

model_path = resource_path("model/uamindmap.gguf")
llm = Llama(model_path=model_path, n_ctx=1024)

# поділ тексту на частини
def split_text(text: str, chunk_size: int = 512) -> List[str]:
    words = text.split()
    chunks, current_chunk, current_length = [], [], 0
    for word in words:
        if current_length + len(word) + 1 > chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk, current_length = [], 0
        current_chunk.append(word)
        current_length += len(word) + 1
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

# завантаження файлу
def load_txt(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def load_pdf(filepath: str) -> str:
    reader = PdfReader(filepath)
    return '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])

def load_docx(filepath: str) -> str:
    doc = Document(filepath)
    return '\n'.join([para.text for para in doc.paragraphs])

def process_file_chunks(text: str):
    """Обробляє текст по частинах і генерує ментальну карту"""
    chunks = split_text(text)
    
    # Обробляємо перші 3 частини для кращого результату
    processed_chunks = chunks[:3]
    combined_text = "\n\n".join(processed_chunks)
    
    # Відображаємо оброблений текст
    user_input.delete("1.0", tk.END)
    user_input.insert(tk.END, combined_text)
    
    # Автоматично генеруємо ментальну карту
    generate_response_from_text(combined_text)

def load_file():
    filetypes = [('Text files', '*.txt'), ('PDF files', '*.pdf'), ('Word documents', '*.docx'), ('All files', '*.*')]
    filepath = filedialog.askopenfilename(filetypes=filetypes)
    if not filepath:
        return
    try:
        if filepath.endswith('.txt'):
            text = load_txt(filepath)
        elif filepath.endswith('.pdf'):
            text = load_pdf(filepath)
        elif filepath.endswith('.docx'):
            text = load_docx(filepath)
        else:
            messagebox.showerror("Помилка", "Непідтримуваний формат файлу")
            return
        
        # Автоматично обробляємо файл по частинах
        process_file_chunks(text)
        
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося завантажити файл: {str(e)}")

# створення ментальної карти за відповіддю
def parse_mindmap_list(text):
    lines = text.strip().split("\n")
    tree = []
    node_stack = []
    for line in lines:
        match = re.match(r"^(\d+(?:\.\d+)*)(?:\s*)(.+)$", line.strip())
        if not match:
            continue
        level_id, content = match.groups()
        level = level_id.count(".")
        node = {"label": content.strip(), "children": []}
        if level == 0:
            tree.append(node)
            node_stack = [node]
        else:
            while len(node_stack) > level:
                node_stack.pop()
            if node_stack:
                node_stack[-1]["children"].append(node)
                node_stack.append(node)
    return tree

def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=10, fill='white', outline='black', width=1):
    """Малює закруглений прямокутник"""
    # Створюємо закруглені кути
    canvas.create_arc(x1, y1, x1 + 2*radius, y1 + 2*radius, start=90, extent=90, fill=fill, outline=outline, width=width)
    canvas.create_arc(x2 - 2*radius, y1, x2, y1 + 2*radius, start=0, extent=90, fill=fill, outline=outline, width=width)
    canvas.create_arc(x2 - 2*radius, y2 - 2*radius, x2, y2, start=270, extent=90, fill=fill, outline=outline, width=width)
    canvas.create_arc(x1, y2 - 2*radius, x1 + 2*radius, y2, start=180, extent=90, fill=fill, outline=outline, width=width)
    
    # Заповнюємо центральну частину
    canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill=fill, outline="")
    canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, fill=fill, outline="")
    
    # Малюємо лінії контуру
    canvas.create_line(x1 + radius, y1, x2 - radius, y1, fill=outline, width=width)
    canvas.create_line(x1 + radius, y2, x2 - radius, y2, fill=outline, width=width)
    canvas.create_line(x1, y1 + radius, x1, y2 - radius, fill=outline, width=width)
    canvas.create_line(x2, y1 + radius, x2, y2 - radius, fill=outline, width=width)

def wrap_text(text, max_width=15):
    """Перенесення тексту на новий рядок"""
    words = text.split()
    if len(words) <= 1:
        return text

    if len(text) > max_width:
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    return text

def draw_mindmap(canvas, tree):
    """Малює ментальну карту"""
    canvas.update_idletasks()
    canvas_width = canvas.winfo_width()
    start_x = canvas_width // 2
    y_start = 50
    spacing_x = 220 
    spacing_y = 120
    
    colors = {
        0: {"fill": "#8fc0f1", "text": "#2c3e50", "outline": "#34495e"},
        1: {"fill": "#b1e1e1", "text": "#2c3e50", "outline": "#094167"},
        2: {"fill": "#89bac1", "text": "#2c3e50", "outline": "#396f73"},
        3: {"fill": "#ecf0f1", "text": "#25486b", "outline": "#1f3e52"},
        4: {"fill": "#819CCD", "text": "#2c3e50", "outline": "#263a4f"},
        5: {"fill": "#8cbcb7", "text": "#2c3e50", "outline": "#2273a9"},
        6: {"fill": "#4dabb2", "text": "#2c3e50", "outline": "#334446"},
        7: {"fill": "#d0e6e1", "text": "#25486b", "outline": "#08314d"}
    }

    def _draw_node(node, x, y, level):
        # перенесення тексту на новий рядок
        wrapped_text = wrap_text(node["label"], max_width=15)
        
        # обчислення розміру елемента
        temp_text = canvas.create_text(0, 0, text=wrapped_text, font=("Arial", 10, "bold"), justify=tk.CENTER)
        bbox = canvas.bbox(temp_text)
        canvas.delete(temp_text)
        
        if not bbox:
            return y
            
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        padding = 15
        rect_width = max(text_width + 2 * padding, 100) 
        rect_height = text_height + 2 * padding
        
        x1 = x - rect_width // 2
        y1 = y - rect_height // 2
        x2 = x + rect_width // 2
        y2 = y + rect_height // 2
        
        color_scheme = colors.get(level, colors[3])
        
        draw_rounded_rect(canvas, x1, y1, x2, y2, radius=8, 
                         fill=color_scheme["fill"], 
                         outline=color_scheme["outline"], 
                         width=2)
        
        canvas.create_text(x, y, text=wrapped_text, anchor="center", 
                          font=("Arial", 10, "bold"), 
                          fill=color_scheme["text"],
                          justify=tk.CENTER)
        
        next_y = y + rect_height // 2 + spacing_y
        
        if node["children"]:
            if level == 0:
                total_width = (len(node["children"]) - 1) * spacing_x
                child_x = x - total_width // 2
                child_y = next_y
                max_child_y = child_y
                
                for child in node["children"]:
                    canvas.create_line(x, y2, child_x, child_y - 30, 
                                     fill="#7f8c8d", width=2,
                                     arrow=tk.LAST, arrowshape=(8, 8, 3))
                    child_bottom = _draw_node(child, child_x, child_y, level + 1)
                    max_child_y = max(max_child_y, child_bottom)
                    child_x += spacing_x
                return max_child_y
            else:
                child_x = x - (len(node["children"]) - 1) * (spacing_x // 2) // 2
                max_child_y = next_y
                
                for child in node["children"]:
                    canvas.create_line(x, y2, child_x, next_y - 30, 
                                     fill="#7f8c8d", width=2,
                                     arrow=tk.LAST, arrowshape=(8, 8, 3))
                    child_bottom = _draw_node(child, child_x, next_y, level + 1)
                    max_child_y = max(max_child_y, child_bottom)
                    child_x += spacing_x // 2
                    next_y = max_child_y + 20
                return max_child_y
        
        return y + rect_height // 2 + 20

    canvas.delete("all")
    max_y = y_start
    
    # малювання елементів
    for i, node in enumerate(tree):
        node_x = start_x + (i - len(tree) // 2) * 300 if len(tree) > 1 else start_x
        max_y = max(max_y, _draw_node(node, node_x, y_start, 0))
    
    canvas.configure(scrollregion=(0, 0, max(canvas_width, 2000), max_y + 100))

def save_canvas_as_image(canvas):
    """Зберігає лише ментальну карту як зображення"""
    # Вибір місця збереження
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")],
        title="Зберегти ментальну карту як зображення"
    )
    if not file_path:
        return

    try:
        # Отримуємо розміри області прокрутки
        canvas.update_idletasks()
        scroll_region = canvas.cget("scrollregion").split()
        if len(scroll_region) == 4:
            x1, y1, x2, y2 = map(int, map(float, scroll_region))
        else:
            x1, y1, x2, y2 = 0, 0, canvas.winfo_width(), canvas.winfo_height()
        
        # Створюємо зображення з білим фоном
        width = max(x2 - x1, canvas.winfo_width())
        height = max(y2 - y1, canvas.winfo_height())
        
        image = Image.new('RGB', (width, height), 'white')
        
        # Створюємо PostScript файл з карти
        ps_file = file_path.replace('.png', '.ps')
        canvas.postscript(file=ps_file, colormode='color', width=width, height=height)
        
        # Конвертуємо PostScript в PNG за допомогою PIL
        try:
            from PIL import Image
            # Для конвертації PS в PNG потрібен Ghostscript
            # Альтернативний метод через tkinter
            
            # Тимчасове рішення: використовуємо screenshot області canvas
            canvas.update()
            x = canvas.winfo_rootx()
            y = canvas.winfo_rooty()
            x1_screen = x
            y1_screen = y
            x2_screen = x + canvas.winfo_width()
            y2_screen = y + canvas.winfo_height()
            
            from PIL import ImageGrab
            image = ImageGrab.grab(bbox=(x1_screen, y1_screen, x2_screen, y2_screen))
            image.save(file_path)
            
            # Видаляємо тимчасовий PS файл
            if os.path.exists(ps_file):
                os.remove(ps_file)
                
        except ImportError:
            messagebox.showerror("Помилка", "Не вдалося імпортувати необхідні бібліотеки для збереження")
            return
            
        messagebox.showinfo("Успіх", f"Ментальна карта збережена як {file_path}")
        
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося зберегти зображення: {e}")

def generate_response_from_text(text):
    """Генерує відповідь на основі тексту"""
    prompt_prefix = """Ти — система створення ментальних карт.
На основі ТІЛЬКИ введеного користувачем тексту нижче створи багаторівневий список (ментальну карту) за такими правилами:

1. Використовуй лише слова та фрази з тексту без перефразування.
2. Усі підпункти мають бути логічно пов'язані з одним головним поняттям — лише один пункт "1 ".
3. Не додавай нову інформацію, якої немає у тексті.
4. Не вигадуй кілька тем — всі деталі повинні бути частиною однієї структури.
5. Використовуй лише українську мову.
6. Склади багаторівневий список за таким прикладом:
Приклад тексту:
Соняшник — це рослина. Він має жовті пелюстки та чорне насіння.
Ментальна карта за цим текстом:
1 Соняшник
    1.1 Рослина
    1.2 Пелюстки
        1.2.1 Жовті
    1.3 Насіння
        1.3.1 Чорне

Склади ментальну карту за для цього 1 тексту: """
    prompt = prompt_prefix + text
    try:
        output = llm(prompt, max_tokens=512)
        output_text = output["choices"][0]["text"].strip()
        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, output_text)

        tree_data = parse_mindmap_list(output_text)
        draw_mindmap(canvas, tree_data)
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося згенерувати карту: {str(e)}")

def generate_response():
    """Генерує відповідь на основі тексту з поля введення"""
    text = user_input.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Увага", "Введіть текст для аналізу")
        return
    generate_response_from_text(text)

# створення вікна
root = tk.Tk()
root.title("Генератор ментальних карт")
root.geometry("1400x900")
root.configure(bg="#f8f9fa")
style = ttk.Style()
style.theme_use('clam')
style.configure('Formal.TFrame', background='#f8f9fa')
style.configure('Formal.TLabel', background='#f8f9fa', foreground='#2c3e50', font=('Arial', 11))
style.configure('Formal.TButton', font=('Arial', 10, 'bold'))

# заголовок
header_frame = ttk.Frame(root, style='Formal.TFrame')
header_frame.pack(fill=tk.X, pady=10, padx=20)
title_label = ttk.Label(header_frame, text="ГЕНЕРАТОР МЕНТАЛЬНИХ КАРТ", 
                       font=('Arial', 16, 'bold'), 
                       foreground='#2c3e50', 
                       background="#bbd2e8")
title_label.pack()

# поле введення
input_section = ttk.Frame(root, style='Formal.TFrame')
input_section.pack(fill=tk.X, pady=10, padx=20)

ttk.Label(input_section, text="Текст для аналізу:", style='Formal.TLabel').pack(anchor=tk.W)
user_input = tk.Text(input_section, height=6, width=120, font=('Arial', 10),
                     relief=tk.SOLID, borderwidth=1, highlightthickness=1,
                     highlightcolor='#3498db', bg='white')
user_input.pack(fill=tk.X, pady=(5, 10))

# кнопки
control_frame = ttk.Frame(root, style='Formal.TFrame')
control_frame.pack(fill=tk.X, pady=10, padx=20)
button_style = {"style": "Formal.TButton"}
btn_frame_left = ttk.Frame(control_frame, style='Formal.TFrame')
btn_frame_left.pack(side=tk.LEFT)
ttk.Button(btn_frame_left, text="Завантажити і обробити файл", command=load_file, **button_style).pack(side=tk.LEFT, padx=(0, 10))
ttk.Button(btn_frame_left, text="Створити карту", command=generate_response, **button_style).pack(side=tk.LEFT, padx=(0, 10))
btn_frame_right = ttk.Frame(control_frame, style='Formal.TFrame')
btn_frame_right.pack(side=tk.RIGHT)
ttk.Button(btn_frame_right, text="Зберегти карту як зображення", command=lambda: save_canvas_as_image(canvas), **button_style).pack()

# відповідь моделі
output_section = ttk.Frame(root, style='Formal.TFrame')
output_section.pack(fill=tk.X, pady=10, padx=20)

ttk.Label(output_section, text="Відповідь:", style='Formal.TLabel').pack(anchor=tk.W)
response_text = tk.Text(output_section, height=5, width=120, font=('Arial', 10),
                       relief=tk.SOLID, borderwidth=1, highlightthickness=1,
                       highlightcolor='#3498db', bg='#f8f9fa')
response_text.pack(fill=tk.X, pady=(5, 10))

# ментальна карта
canvas_section = ttk.Frame(root, style='Formal.TFrame')
canvas_section.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)

ttk.Label(canvas_section, text="Ментальна карта:", style='Formal.TLabel').pack(anchor=tk.W)

# додавання стрічок прокручування
canvas_frame = ttk.Frame(canvas_section)
canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
canvas = tk.Canvas(canvas_frame, bg='white', relief=tk.SOLID, borderwidth=1, 
                   highlightthickness=1, highlightcolor='#bdc3c7')
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# вертикальні стрічки прокручування
v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=v_scrollbar.set)

# горизонтальні стрічки прокручування
h_scrollbar = ttk.Scrollbar(canvas_section, orient=tk.HORIZONTAL, command=canvas.xview)
h_scrollbar.pack(fill=tk.X, pady=(2, 0))
canvas.configure(xscrollcommand=h_scrollbar.set)

# прокручування колесом мишки
def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
canvas.bind("<MouseWheel>", on_mousewheel)

# вставка тексту
def enable_paste(event):
    event.widget.event_generate('<<Paste>>')
root.bind_class("Text", "<Button-3><ButtonRelease-3>", enable_paste)

root.mainloop()