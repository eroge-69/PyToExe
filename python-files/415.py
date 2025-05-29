import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone
import uuid

def replace_comma_on_entry(event):
    """Автоматическая замена запятой на точку при вводе"""
    widget = event.widget
    current_text = widget.get()
    if ',' in current_text:
        new_text = current_text.replace(',', '.')
        cursor_pos = widget.index(tk.INSERT)
        widget.delete(0, tk.END)
        widget.insert(0, new_text)
        widget.icursor(cursor_pos)

def show_sgtin_context_menu(event):
    try:
        sgtin_context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        sgtin_context_menu.grab_release()

def paste_sgtin():
    try:
        clipboard_text = app.clipboard_get()
        sgtin_text.insert(tk.INSERT, clipboard_text)
    except tk.TclError:
        messagebox.showwarning("Буфер обмена", "Буфер обмена пуст или содержит не текст")

def paste_sgtin_replace():
    try:
        clipboard_text = app.clipboard_get()
        sgtin_text.delete("1.0", tk.END)
        sgtin_text.insert(tk.END, clipboard_text)
    except tk.TclError:
        messagebox.showwarning("Буфер обмена", "Буфер обмена пуст или содержит не текст")

def copy_sgtin():
    try:
        selected_text = sgtin_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        app.clipboard_clear()
        app.clipboard_append(selected_text)
    except tk.TclError:
        pass

def cut_sgtin():
    try:
        selected_text = sgtin_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        app.clipboard_clear()
        app.clipboard_append(selected_text)
        sgtin_text.delete(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        pass

def delete_sgtin():
    try:
        sgtin_text.delete(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        pass

def select_all_sgtin(event=None):
    sgtin_text.tag_add(tk.SEL, "1.0", tk.END)
    sgtin_text.mark_set(tk.INSERT, "1.0")
    sgtin_text.see(tk.INSERT)
    return 'break'

def check_id_length(widget, length):
    """Проверка длины ID"""
    value = widget.get().strip()
    if len(value) == length and value.isdigit():
        widget.config(bg='white')
    else:
        widget.config(bg='#ffcccc')

def validate_numeric_input(new_value):
    if not new_value:
        return True
    
    allowed_chars = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ','}
    if not all(c in allowed_chars for c in new_value):
        return False
    
    if ',' in new_value:
        new_value = new_value.replace(',', '.')
    
    if new_value.count('.') > 1:
        return False
    
    return True

def format_numeric_input(event):
    widget = event.widget
    current_text = widget.get()
    
    if not current_text:
        return
    
    cleaned = ''.join(c for c in current_text if c.isdigit() or c == '.')
    parts = cleaned.split('.')
    if len(parts) > 1:
        cleaned = parts[0] + '.' + ''.join(parts[1:])
    
    if cleaned.startswith('.'):
        cleaned = '0' + cleaned
    
    if not cleaned:
        cleaned = '0'
    
    widget.delete(0, tk.END)
    widget.insert(0, cleaned)

def auto_format_date(event):
    widget = event.widget
    text = widget.get().replace('.', '')
    
    if len(text) == 6 and text.isdigit():
        day = text[:2]
        month = text[2:4]
        year = text[4:]
        formatted_date = f"{day}.{month}.{year}"
        widget.delete(0, tk.END)
        widget.insert(0, formatted_date)
    elif len(text) == 8 and text.isdigit():
        day = text[:2]
        month = text[2:4]
        year = text[4:]
        formatted_date = f"{day}.{month}.{year}"
        widget.delete(0, tk.END)
        widget.insert(0, formatted_date)

def validate_date_input(new_value):
    if not new_value:
        return True
    
    if not all(c.isdigit() or c == '.' for c in new_value):
        return False
    
    if new_value.count('.') > 2:
        return False
    
    return True

def format_date_input(event):
    widget = event.widget
    current_text = widget.get()
    
    if not current_text:
        return
    
    cleaned = ''.join(c for c in current_text if c.isdigit())
    
    if len(cleaned) == 6:
        cleaned = '0' + cleaned[0] + '0' + cleaned[1] + cleaned[2:]
    elif len(cleaned) == 7:
        if len(cleaned[:2]) == 1:
            cleaned = '0' + cleaned
        else:
            cleaned = cleaned[:2] + '0' + cleaned[2:]
    
    formatted = []
    if len(cleaned) > 0:
        formatted.append(cleaned[:2].zfill(2))
    if len(cleaned) > 2:
        formatted.append(cleaned[2:4].zfill(2))
    if len(cleaned) > 4:
        formatted.append(cleaned[4:8])
    
    formatted_date = '.'.join(formatted)
    widget.delete(0, tk.END)
    widget.insert(0, formatted_date)

def update_operation_time():
    # Получаем текущее время с часовым поясом
    now = datetime.now().astimezone()
    # Форматируем с учетом часового пояса
    current_time = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    # Вставляем двоеточие в часовой пояс (из +0300 в +03:00)
    current_time = current_time[:-2] + ':' + current_time[-2:]
    operation_time_var.set(current_time)
    messagebox.showinfo("Время обновлено", f"Установлено текущее время:\n{current_time}")

def validate_input():
    errors = []
    
    # Проверка ID отправителя и получателя
    subject_id = subject_id_entry.get().strip()
    if len(subject_id) != 14 or not subject_id.isdigit():
        errors.append("ID отправителя должно содержать ровно 14 цифр")
    
    receiver_id = receiver_id_entry.get().strip()
    if len(receiver_id) != 14 or not receiver_id.isdigit():
        errors.append("ID получателя должно содержать ровно 14 цифр")
    
    # Проверка стоимости и НДС
    try:
        float(cost_entry.get().strip())
    except ValueError:
        errors.append("Некорректное значение цены")
    
    try:
        float(vat_entry.get().strip())
    except ValueError:
        errors.append("Некорректное значение НДС")
    
    # Проверка даты документа
    doc_date = doc_date_entry.get().strip()
    try:
        datetime.strptime(doc_date, "%d.%m.%Y")
    except ValueError:
        errors.append("Неверный формат даты! Используйте ДД.ММ.ГГГГ")
    
    # Проверка SGTIN
    sgtin_list = sgtin_text.get("1.0", tk.END).strip().split("\n")
    if not any(sgtin.strip() for sgtin in sgtin_list):
        errors.append("Добавьте хотя бы один SGTIN")
    
    # Проверка номера документа
    if not doc_number_entry.get().strip():
        errors.append("Введите номер документа")
    
    # Проверка дополнительных параметров
    for field, name in [(turnover_type_entry, "Тип оборота"), 
                        (source_entry, "Источник"), 
                        (contract_type_entry, "Тип контракта")]:
        value = field.get().strip()
        if not value:
            errors.append(f"Поле '{name}' не может быть пустым")
        elif not value.isdigit():
            errors.append(f"Поле '{name}' должно содержать только цифры")
    
    return errors

def generate_xml():
    errors = validate_input()
    if errors:
        messagebox.showerror("Ошибки ввода", "\n".join(errors))
        return

    # Получение значений из полей
    sgtin_list = [sgtin.strip() for sgtin in sgtin_text.get("1.0", tk.END).strip().split("\n") if sgtin.strip()]
    cost = cost_entry.get().strip().replace(",", ".")
    vat_value = vat_entry.get().strip().replace(",", ".")
    subject_id = subject_id_entry.get().strip()
    receiver_id = receiver_id_entry.get().strip()
    doc_number = doc_number_entry.get().strip()
    doc_date = doc_date_entry.get().strip()
    operation_time = operation_time_var.get()
    turnover_type = turnover_type_entry.get().strip()
    source = source_entry.get().strip()
    contract_type = contract_type_entry.get().strip()

    # Создание XML структуры для 415
    root = ET.Element("documents")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("session_ui", str(uuid.uuid4()).upper())
    root.set("version", "1.38")
    
    move_order = ET.SubElement(root, "move_order")
    move_order.set("action_id", "415")
    
    # Основные элементы
    ET.SubElement(move_order, "subject_id").text = subject_id
    ET.SubElement(move_order, "receiver_id").text = receiver_id
    ET.SubElement(move_order, "operation_date").text = operation_time
    ET.SubElement(move_order, "doc_num").text = doc_number
    ET.SubElement(move_order, "doc_date").text = doc_date
    ET.SubElement(move_order, "turnover_type").text = turnover_type
    ET.SubElement(move_order, "source").text = source
    ET.SubElement(move_order, "contract_type").text = contract_type
    
    # Детали заказа
    order_details = ET.SubElement(move_order, "order_details")
    
    # Добавление каждого SGTIN
    for sgtin in sgtin_list:
        union = ET.SubElement(order_details, "union")
        ET.SubElement(union, "sgtin").text = sgtin
        ET.SubElement(union, "cost").text = cost
        ET.SubElement(union, "vat_value").text = vat_value

    # Форматирование XML
    xml_str = ET.tostring(root, encoding="UTF-8")
    dom = minidom.parseString(xml_str)
    xml_pretty = dom.toprettyxml(indent="\t", encoding="UTF-8")

    # Сохранение файла
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xml",
        filetypes=[("XML files", "*.xml")],
        initialfile="415.xml"
    )
    if file_path:
        try:
            with open(file_path, "wb") as f:
                f.write(xml_pretty)
            messagebox.showinfo("Успешно", f"Файл успешно сохранён:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

# Создание графического интерфейса
app = tk.Tk()
app.title("Генератор XML для схемы 415 (Перемещение)")
app.geometry("450x570")
app.resizable(False, False)

# Настройка сетки
app.grid_columnconfigure(1, weight=1)

# Переменные
operation_time_var = tk.StringVar()
# Устанавливаем текущее время с часовым поясом
now = datetime.now().astimezone()
current_time = now.strftime("%Y-%m-%dT%H:%M:%S%z")
current_time = current_time[:-2] + ':' + current_time[-2:]
operation_time_var.set(current_time)

# Регистрация функций валидации
validate_num_cmd = app.register(validate_numeric_input)
validate_date_cmd = app.register(validate_date_input)

# ID отправителя
tk.Label(app, text="ID отправителя (subject_id):*", anchor="w").grid(row=0, column=0, sticky="ew", padx=5, pady=2)
subject_id_entry = tk.Entry(app, width=20)
subject_id_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
subject_id_entry.insert(0, "00000000002030")
subject_id_entry.bind("<KeyRelease>", lambda e: check_id_length(subject_id_entry, 14))
tk.Label(app, text="(14 цифр)", fg="gray").grid(row=0, column=2, sticky="w", padx=5)

# ID получателя
tk.Label(app, text="ID получателя (receiver_id):*", anchor="w").grid(row=1, column=0, sticky="ew", padx=5, pady=2)
receiver_id_entry = tk.Entry(app, width=20)
receiver_id_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
receiver_id_entry.insert(0, "00000000000009")
receiver_id_entry.bind("<KeyRelease>", lambda e: check_id_length(receiver_id_entry, 14))
tk.Label(app, text="(14 цифр)", fg="gray").grid(row=1, column=2, sticky="w", padx=5)

# Время операции
tk.Label(app, text="Время операции (operation_date):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
tk.Entry(app, textvariable=operation_time_var, state='readonly').grid(row=2, column=1, sticky="ew", padx=5, pady=2)
tk.Button(app, text="Обновить время", command=update_operation_time).grid(row=2, column=2, padx=5)

# Контекстное меню для SGTIN
sgtin_context_menu = tk.Menu(app, tearoff=0)
sgtin_context_menu.add_command(label="Вставить", command=paste_sgtin)
sgtin_context_menu.add_command(label="Копировать", command=copy_sgtin)
sgtin_context_menu.add_command(label="Вырезать", command=cut_sgtin)
sgtin_context_menu.add_command(label="Удалить", command=delete_sgtin)
sgtin_context_menu.add_separator()
sgtin_context_menu.add_command(label="Выделить всё", command=select_all_sgtin)

# Поле для SGTIN
tk.Label(app, text="Список SGTIN:*", anchor="w").grid(row=3, column=0, sticky="nw", padx=5, pady=2)

# Фрейм для кнопки вставки
sgtin_frame = tk.Frame(app)
sgtin_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=5)
tk.Button(sgtin_frame, text="Вставить SGTIN (заменить всё)", command=paste_sgtin_replace, width=25).pack(side=tk.LEFT, pady=(0, 2))

sgtin_text = tk.Text(app, height=10, width=60)
sgtin_text.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=5, pady=2)
sgtin_text.insert("1.0", "04601808014105DcNW14M91EKwj\n04601808014105IHJe2IhLAe2bz")

# Привязка контекстного меню
sgtin_text.bind("<Button-3>", show_sgtin_context_menu)
sgtin_text.bind("<Control-a>", select_all_sgtin)

tk.Label(app, text="(каждый код с новой строки)", fg="gray").grid(row=6, column=0, columnspan=3, sticky="w", padx=5)

# Стоимость и НДС
tk.Label(app, text="Стоимость (cost):*", anchor="w").grid(row=7, column=0, sticky="w", padx=5, pady=2)
cost_entry = tk.Entry(app, width=20, validate="key", validatecommand=(validate_num_cmd, '%P'))
cost_entry.grid(row=7, column=1, sticky="w", padx=5, pady=2)
cost_entry.insert(0, "0.00")
cost_entry.bind("<KeyRelease>", replace_comma_on_entry)
cost_entry.bind("<FocusOut>", format_numeric_input)

tk.Label(app, text="НДС (vat_value):*", anchor="w").grid(row=8, column=0, sticky="w", padx=5, pady=2)
vat_entry = tk.Entry(app, width=20, validate="key", validatecommand=(validate_num_cmd, '%P'))
vat_entry.grid(row=8, column=1, sticky="w", padx=5, pady=2)
vat_entry.insert(0, "0.00")
vat_entry.bind("<KeyRelease>", replace_comma_on_entry)
vat_entry.bind("<FocusOut>", format_numeric_input)

# Документ
tk.Label(app, text="Номер документа (doc_num):*", anchor="w").grid(row=9, column=0, sticky="w", padx=5, pady=2)
doc_number_entry = tk.Entry(app)
doc_number_entry.grid(row=9, column=1, sticky="ew", padx=5, pady=2)
doc_number_entry.insert(0, "123456")

tk.Label(app, text="Дата документа (doc_date):*", anchor="w").grid(row=10, column=0, sticky="w", padx=5, pady=2)
doc_date_entry = tk.Entry(app, validate="key", validatecommand=(validate_date_cmd, '%P'))
doc_date_entry.grid(row=10, column=1, sticky="ew", padx=5, pady=2)
doc_date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
doc_date_entry.bind("<KeyRelease>", auto_format_date)
doc_date_entry.bind("<FocusOut>", format_date_input)
tk.Label(app, text="(формат ДД.ММ.ГГГГ)", fg="gray").grid(row=10, column=2, sticky="w", padx=5)

# Дополнительные параметры
tk.Label(app, text="Тип оборота (turnover_type):*", anchor="w").grid(row=11, column=0, sticky="w", padx=5, pady=2)
turnover_type_entry = tk.Entry(app, width=5)
turnover_type_entry.grid(row=11, column=1, sticky="w", padx=5, pady=2)
turnover_type_entry.insert(0, "1")

tk.Label(app, text="Источник (source):*", anchor="w").grid(row=12, column=0, sticky="w", padx=5, pady=2)
source_entry = tk.Entry(app, width=5)
source_entry.grid(row=12, column=1, sticky="w", padx=5, pady=2)
source_entry.insert(0, "1")

tk.Label(app, text="Тип контракта (contract_type):*", anchor="w").grid(row=13, column=0, sticky="w", padx=5, pady=2)
contract_type_entry = tk.Entry(app, width=5)
contract_type_entry.grid(row=13, column=1, sticky="w", padx=5, pady=2)
contract_type_entry.insert(0, "1")

# Кнопка генерации
generate_btn = tk.Button(app, text="Сгенерировать XML 415", command=generate_xml)
generate_btn.grid(row=14, column=0, columnspan=3, pady=10, sticky="ew")

# Подпись обязательных полей
tk.Label(app, text="* - обязательные поля", fg="gray").grid(row=15, column=0, columnspan=3, sticky="w", padx=5)

# Первоначальная проверка ID
check_id_length(subject_id_entry, 14)
check_id_length(receiver_id_entry, 14)

app.mainloop()