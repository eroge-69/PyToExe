import win32com.client
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil
import threading
from datetime import datetime
import math
import psutil
import random

try:
    from PyPDF2 import PdfMerger
except ImportError:
    try:
        from pypdf import PdfMerger
    except ImportError:
        raise SystemExit("Установите: pip install PyPDF2 или pip install pypdf\nТакже: pip install psutil")

# ---------- Глобальные флаги ----------
stop_flag = False
anim_running = False
particles = []
blueprint_lines = []

# ---------- Утилиты ----------
def ts():
    return datetime.now().strftime("%H:%M:%S")

def close_pdf_viewers():
    """Закрывает популярные PDF-просмотрщики, если те самопроизвольно открылись."""
    pdf_apps = {
        "AcroRd32.exe", "Acrobat.exe", "FoxitReader.exe", "FoxitPDFReader.exe",
        "SumatraPDF.exe", "NitroPDF.exe", "PDFXCview.exe", "PDFXEdit.exe",
        "MicrosoftEdge.exe"  # иногда Edge захватывает PDF
    }
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.info["name"] in pdf_apps:
                proc.terminate()
                proc.wait(timeout=2)
        except Exception:
            pass

# ---------- Инженерная анимация ----------
class Particle:
    def __init__(self, x, y, vx, vy, color="#4CAF50", size=2):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.03)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        return self.life > 0

class BlueprintLine:
    def __init__(self, x1, y1, x2, y2, speed=2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.current_length = 0
        self.max_length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        self.speed = speed
        self.angle = math.atan2(y2-y1, x2-x1)
        
    def update(self):
        if self.current_length < self.max_length:
            self.current_length += self.speed
            return True
        return False
    
    def get_current_end(self):
        progress = min(self.current_length / self.max_length, 1.0)
        curr_x = self.x1 + (self.x2 - self.x1) * progress
        curr_y = self.y1 + (self.y2 - self.y1) * progress
        return curr_x, curr_y

def draw_technical_gear(canvas, cx, cy, r, rotation=0):
    """Рисует техническую шестерню с деталями."""
    points = []
    teeth = 12
    inner_r = r * 0.7
    
    # Создаём зубья шестерни
    for i in range(teeth * 2):
        angle = rotation + (math.pi * i) / teeth
        if i % 2 == 0:
            radius = r
        else:
            radius = r * 0.85
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        points.extend([x, y])
    
    # Внешний контур с зубьями
    gear_body = canvas.create_polygon(points, outline="#2196F3", width=2, fill="", stipple="gray25")
    
    # Внутренний круг
    inner_circle = canvas.create_oval(cx-inner_r, cy-inner_r, cx+inner_r, cy+inner_r, 
                                    outline="#FF9800", width=2, fill="")
    
    # Центральная ось
    axis_r = r * 0.2
    axis = canvas.create_oval(cx-axis_r, cy-axis_r, cx+axis_r, cy+axis_r,
                             outline="#F44336", width=3, fill="#F44336")
    
    # Спицы
    spokes = []
    for i in range(6):
        angle = rotation + (math.pi * i) / 3
        x1 = cx + axis_r * math.cos(angle)
        y1 = cy + axis_r * math.sin(angle)
        x2 = cx + inner_r * math.cos(angle)
        y2 = cy + inner_r * math.sin(angle)
        spoke = canvas.create_line(x1, y1, x2, y2, width=2, fill="#9E9E9E")
        spokes.append(spoke)
    
    return {
        "cx": cx, "cy": cy, "r": r, "rotation": rotation,
        "elements": [gear_body, inner_circle, axis] + spokes
    }

def draw_blueprint_elements(canvas):
    """Рисует элементы технического чертежа."""
    global blueprint_lines
    blueprint_lines = []
    
    # Создаём несколько технических линий
    lines_data = [
        (150, 30, 350, 40),   # Верхняя линия
        (350, 40, 500, 35),   # Продолжение
        (150, 130, 300, 140), # Нижняя линия
        (300, 140, 500, 135), # Продолжение
        (150, 30, 150, 130),  # Вертикальная слева
        (500, 35, 500, 135),  # Вертикальная справа
    ]
    
    for x1, y1, x2, y2 in lines_data:
        blueprint_lines.append(BlueprintLine(x1, y1, x2, y2, random.uniform(3, 6)))

def draw_dimension_lines(canvas):
    """Рисует размерные линии."""
    # Горизонтальная размерная линия
    canvas.create_line(160, 50, 340, 50, width=1, fill="#607D8B", dash=(3, 3))
    canvas.create_line(160, 45, 160, 55, width=1, fill="#607D8B")  # Выносная левая
    canvas.create_line(340, 45, 340, 55, width=1, fill="#607D8B")  # Выносная правая
    canvas.create_text(250, 45, text="180mm", font=("Arial", 8), fill="#607D8B")
    
    # Вертикальная размерная линия
    canvas.create_line(130, 40, 130, 120, width=1, fill="#607D8B", dash=(3, 3))
    canvas.create_line(125, 40, 135, 40, width=1, fill="#607D8B")  # Выносная верхняя
    canvas.create_line(125, 120, 135, 120, width=1, fill="#607D8B")  # Выносная нижняя
    canvas.create_text(120, 80, text="80mm", font=("Arial", 8), fill="#607D8B", angle=90)

def create_particle_burst(canvas, x, y, count=8):
    """Создаёт вспышку частиц."""
    global particles
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        color = random.choice(["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"])
        particles.append(Particle(x, y, vx, vy, color, random.randint(2, 4)))

def update_particles(canvas):
    """Обновляет частицы."""
    global particles
    if not anim_running:
        return
    
    # Очищаем старые частицы
    canvas.delete("particle")
    
    # Обновляем существующие частицы
    active_particles = []
    for particle in particles:
        if particle.update():
            alpha = int(255 * particle.life)
            canvas.create_oval(
                particle.x - particle.size, particle.y - particle.size,
                particle.x + particle.size, particle.y + particle.size,
                fill=particle.color, outline="", tags="particle"
            )
            active_particles.append(particle)
    
    particles = active_particles
    canvas.after(50, lambda: update_particles(canvas))

def update_blueprint_lines(canvas):
    """Обновляет рисование чертежных линий."""
    global blueprint_lines
    if not anim_running:
        return
    
    canvas.delete("blueprint")
    
    active_lines = []
    for line in blueprint_lines:
        if line.update():
            curr_x, curr_y = line.get_current_end()
            canvas.create_line(
                line.x1, line.y1, curr_x, curr_y,
                width=1, fill="#03A9F4", tags="blueprint", dash=(2, 2)
            )
            active_lines.append(line)
    
    # Перезапускаем линии если они закончились
    if not active_lines and anim_running:
        draw_blueprint_elements(canvas)
    
    canvas.after(80, lambda: update_blueprint_lines(canvas))

def draw_gear(canvas, cx, cy, r, spokes=8):
    """Создаёт техническую шестерню."""
    gear_data = draw_technical_gear(canvas, cx, cy, r, 0)
    return {
        "cx": cx, "cy": cy, "r": r, "spokes": spokes, 
        "rotation": 0.0, "elements": gear_data["elements"]
    }

def update_gear(canvas, gear, dx=5, ddeg=15, left=120, right=540):
    """Обновляет положение и вращение шестерни."""
    if not anim_running:
        return
    
    # Движение по X
    old_cx = gear["cx"]
    gear["cx"] += dx
    if gear["cx"] >= right:
        gear["cx"] = left
        # Создаём вспышку частиц при "перерождении"
        create_particle_burst(canvas, right, gear["cy"], 12)
    
    # Поворот
    gear["rotation"] = (gear["rotation"] + math.radians(ddeg)) % (2*math.pi)
    
    # Удаляем старые элементы
    for elem_id in gear["elements"]:
        try:
            canvas.delete(elem_id)
        except:
            pass
    
    # Создаём частицы при движении
    if random.random() < 0.3:  # 30% шанс создать частицу
        create_particle_burst(canvas, old_cx, gear["cy"], 2)
    
    # Перерисовываем в новой позиции
    new_gear = draw_technical_gear(canvas, gear["cx"], gear["cy"], gear["r"], gear["rotation"])
    gear["elements"] = new_gear["elements"]
    
    # Следующий кадр
    canvas.after(60, lambda: update_gear(canvas, gear, dx, ddeg, left, right))

def start_animation():
    global anim_running
    anim_running = True
    update_gear(canvas, gear_obj, dx=4, ddeg=18, left=140, right=560)
    update_particles(canvas)
    update_blueprint_lines(canvas)

def stop_animation():
    global anim_running
    anim_running = False
    canvas.delete("particle")
    canvas.delete("blueprint")

# ---------- Основная логика ----------
def process_folder():
    global stop_flag
    stop_flag = False

    folder = filedialog.askdirectory(title="Выберите папку с DWG")
    if not folder:
        btn_start.config(state="normal")
        return

    # Папка для временных листов в той же директории, где DWG
    temp_root = os.path.join(folder, "_DWG2PDF_temp")
    os.makedirs(temp_root, exist_ok=True)

    try:
        delay = float(delay_entry.get() or "1.0")
    except ValueError:
        delay = 1.0

    dwg_files = [f for f in os.listdir(folder) if f.lower().endswith(".dwg")]
    if not dwg_files:
        messagebox.showinfo("Нет файлов", "DWG файлы не найдены в папке.")
        btn_start.config(state="normal")
        return

    log_text.delete(1.0, tk.END)
    log(f"Найдено {len(dwg_files)} DWG файлов.")
    progress_bar["value"] = 0
    progress_bar["maximum"] = len(dwg_files)

    # Запускаем анимацию и блокируем кнопку «Старт»
    start_animation()
    btn_start.config(state="disabled")
    btn_stop.config(state="normal")

    # Запускаем AutoCAD
    try:
        acad = win32com.client.Dispatch("AutoCAD.Application")
        acad.Visible = True
    except Exception as e:
        stop_animation()
        btn_start.config(state="normal")
        log(f"❌ Не удалось запустить AutoCAD: {e}")
        return

    for idx, dwg_file in enumerate(dwg_files, 1):
        if stop_flag:
            log("⛔ Обработка прервана пользователем.")
            break

        dwg_path = os.path.join(folder, dwg_file)
        dwg_name = os.path.splitext(dwg_file)[0]
        log(f"🔧 Обрабатываем: {dwg_file}")

        # Создаём эффект обработки файла
        create_particle_burst(canvas, gear_obj["cx"], gear_obj["cy"], 15)

        # Для каждого DWG — своя подпапка временных листов
        temp_folder = os.path.join(temp_root, dwg_name)
        if os.path.isdir(temp_folder):
            # чистим, если осталась с прошлых запусков
            try:
                shutil.rmtree(temp_folder)
            except Exception:
                pass
        os.makedirs(temp_folder, exist_ok=True)

        try:
            doc = acad.Documents.Open(dwg_path)
        except Exception as e:
            log(f"   ❌ Не удалось открыть DWG: {e}")
            continue

        time.sleep(1.5)  # даём AutoCAD загрузиться
        plot = doc.Plot
        pdf_files = []

        # Экспорт всех листов, кроме Model
        for layout in doc.Layouts:
            if layout.Name.lower() == "model":
                continue
            if stop_flag:
                break

            log(f"   📐 Лист: {layout.Name} → PDF")
            root.update_idletasks()
            doc.ActiveLayout = layout
            pdf_path = os.path.join(temp_folder, f"{layout.Name}.pdf")

            try:
                plot.PlotToFile(pdf_path, "DWG To PDF.pc3")
                # Небольшая задержка — чтобы AutoCAD гарантированно докинул файл
                time.sleep(max(0.2, delay))
                pdf_files.append(pdf_path)
                # На всякий случай закрыть внезапно открывшиеся PDF-читалки
                close_pdf_viewers()
                log(f"      ✅ Сохранено: {pdf_path}")
                
                # Эффект успешного сохранения
                create_particle_burst(canvas, 580, 85, 8)
                
            except Exception as e:
                log(f"      ❌ Ошибка печати: {e}")

        # Закрываем DWG без сохранения
        try:
            doc.Close(False)
        except Exception:
            pass

        if stop_flag:
            break

        # Объединяем листы в один PDF рядом с исходным DWG
        if pdf_files:
            merged_pdf = os.path.join(folder, f"{dwg_name}.pdf")
            try:
                merger = PdfMerger()
                for p in sorted(pdf_files):
                    merger.append(p)
                merger.write(merged_pdf)
                merger.close()
                log(f"🎉 Объединено: {merged_pdf}")
                
                # Большой эффект при объединении
                create_particle_burst(canvas, 350, 85, 20)
                
            except Exception as e:
                log(f"❌ Ошибка объединения: {e}")

            # Удаляем временную подпапку DWG
            try:
                shutil.rmtree(temp_folder)
                log("🗑️ Временные листы удалены")
            except Exception as e:
                log(f"⚠️ Не удалось удалить временную папку {temp_folder}: {e}")

        progress_bar["value"] = idx
        root.update_idletasks()

    stop_animation()
    btn_start.config(state="normal")
    btn_stop.config(state="disabled")

    if not stop_flag:
        log("✅ Готово: все выбранные DWG обработаны!")
        messagebox.showinfo("Готово", "Все DWG обработаны!")
        # Финальная вспышка
        create_particle_burst(canvas, 350, 85, 30)

    # сброс
    stop_flag = False

def start_processing():
    threading.Thread(target=process_folder, daemon=True).start()

def stop_processing():
    global stop_flag
    stop_flag = True

def log(msg):
    log_text.insert(tk.END, f"[{ts()}] {msg}\n")
    log_text.see(tk.END)

# ---------- UI ----------
root = tk.Tk()
root.title("🔧 DWG → PDF Инженерный Конвертер  •  MADE BY HHA")
root.geometry("760x650")
root.configure(bg="#263238")

# Заголовок с градиентным эффектом
title_frame = tk.Frame(root, bg="#263238", height=50)
title_frame.pack(fill=tk.X, pady=5)

title = tk.Label(title_frame, text="🔧 DWG → PDF Инженерный Конвертер", 
                font=("Segoe UI", 18, "bold"), fg="#00E676", bg="#263238")
title.pack()

subtitle = tk.Label(title_frame, text="Профессиональная конвертация чертежей", 
                   font=("Segoe UI", 10), fg="#B0BEC5", bg="#263238")
subtitle.pack()

# Канва с технической анимацией
canvas = tk.Canvas(root, width=700, height=170, bg="#37474F", highlightthickness=1, 
                  highlightbackground="#546E7A")
canvas.pack(pady=10)

# Технический фон
canvas.create_rectangle(0, 0, 700, 170, fill="#37474F", outline="")

# Основной трек конвейера
canvas.create_rectangle(120, 75, 580, 95, fill="#455A64", outline="#607D8B", width=2)
canvas.create_line(120, 85, 580, 85, fill="#78909C", width=1, dash=(5, 5))

# Метки DWG и PDF с техническим стилем
canvas.create_rectangle(60, 70, 110, 100, fill="#1976D2", outline="#2196F3", width=2)
canvas.create_text(85, 85, text="DWG", font=("Segoe UI", 12, "bold"), fill="#FFFFFF")

canvas.create_rectangle(590, 70, 640, 100, fill="#D32F2F", outline="#F44336", width=2)
canvas.create_text(615, 85, text="PDF", font=("Segoe UI", 12, "bold"), fill="#FFFFFF")

# Рисуем размерные линии и технические элементы
draw_dimension_lines(canvas)

# Инициализация чертежных линий
draw_blueprint_elements(canvas)

# Создаём техническую шестерню
gear_obj = draw_gear(canvas, cx=140, cy=85, r=25)

# Панель управления
controls_frame = tk.Frame(root, bg="#263238")
controls_frame.pack(pady=15)

btn_start = tk.Button(controls_frame, text="▶  Начать конвертацию", 
                     font=("Segoe UI", 12, "bold"), fg="#FFFFFF", bg="#4CAF50", 
                     activebackground="#66BB6A", padx=20, pady=10, 
                     command=start_processing, relief="flat", cursor="hand2")
btn_start.grid(row=0, column=0, padx=10)

btn_stop = tk.Button(controls_frame, text="⛔  Прервать", 
                    font=("Segoe UI", 12, "bold"), fg="#FFFFFF", bg="#F44336", 
                    activebackground="#EF5350", padx=20, pady=10, 
                    command=stop_processing, relief="flat", state="disabled", cursor="hand2")
btn_stop.grid(row=0, column=1, padx=10)

# Настройки
settings_frame = tk.Frame(root, bg="#263238")
settings_frame.pack(pady=8)

delay_label = tk.Label(settings_frame, text="⚙️ Задержка печати (сек):", 
                      font=("Segoe UI", 11), fg="#B0BEC5", bg="#263238")
delay_label.pack(side=tk.LEFT)

delay_entry = tk.Entry(settings_frame, font=("Segoe UI", 11), width=8, 
                      relief="solid", justify="center", bg="#455A64", fg="#FFFFFF",
                      insertbackground="#FFFFFF", bd=1)
delay_entry.insert(0, "0.5")
delay_entry.pack(side=tk.LEFT, padx=10)

# Прогресс бар с техническим стилем
progress_frame = tk.Frame(root, bg="#263238")
progress_frame.pack(pady=5)

progress_label = tk.Label(progress_frame, text="Прогресс обработки:", 
                         font=("Segoe UI", 10), fg="#B0BEC5", bg="#263238")
progress_label.pack()

style = ttk.Style()
style.theme_use('clam')
style.configure("TProgressbar", background="#4CAF50", troughcolor="#455A64", 
               borderwidth=0, lightcolor="#4CAF50", darkcolor="#4CAF50")

progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=700, 
                              mode="determinate", style="TProgressbar")
progress_bar.pack(pady=5)

# Лог с техническим стилем
log_frame = tk.Frame(root, bg="#263238")
log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

log_label = tk.Label(log_frame, text="📊 Журнал операций:", 
                    font=("Segoe UI", 11, "bold"), fg="#00E676", bg="#263238")
log_label.pack(anchor=tk.W)

log_text = tk.Text(log_frame, height=14, width=88, bg="#1E1E1E", fg="#00E676",
                  insertbackground="#00E676", relief="solid", font=("Consolas", 9),
                  selectbackground="#37474F", selectforeground="#FFFFFF", bd=1)
log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

# Скроллбар для лога
scrollbar = tk.Scrollbar(log_text, orient=tk.VERTICAL, command=log_text.yview)
log_text.configure(yscrollcommand=scrollbar.set)

# Футер
footer_frame = tk.Frame(root, bg="#1A1A1A", height=30)
footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

footer = tk.Label(footer_frame, text="⚡ MADE BY HHA • Инженерные решения", 
                 font=("Segoe UI", 10, "bold"), fg="#00E676", bg="#1A1A1A")
footer.pack(pady=6)

# Начальное сообщение в логе
log("🚀 Система готова к работе. Выберите папку с DWG файлами для начала конвертации.")
log("💡 Совет: Убедитесь, что AutoCAD установлен и настроен для печати в PDF.")

root.mainloop()
