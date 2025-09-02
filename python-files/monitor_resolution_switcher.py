import tkinter as tk
from tkinter import ttk, messagebox
import win32api
import win32con
import win32gui
from ctypes import windll
import sys

class MonitorResolutionSwitcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Переключатель разрешения монитора")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # Переменные для хранения текущих настроек
        self.current_resolution = None
        self.current_frequency = None
        self.available_modes = []
        
        # Переменные для сохраненных разрешений
        self.saved_resolution_1 = None
        self.saved_frequency_1 = None
        self.saved_resolution_2 = None
        self.saved_frequency_2 = None
        
        self.setup_ui()
        self.load_available_modes()
        self.update_current_settings()
    
    def setup_ui(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Переключатель разрешения монитора", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Текущие настройки
        current_frame = tk.LabelFrame(self.root, text="Текущие настройки", font=("Arial", 10, "bold"))
        current_frame.pack(pady=10, padx=20, fill="x")
        
        self.current_info_label = tk.Label(current_frame, text="Загрузка...", 
                                          font=("Arial", 10))
        self.current_info_label.pack(pady=5)
        
        # Выбор разрешения
        resolution_frame = tk.LabelFrame(self.root, text="Выберите разрешение", font=("Arial", 10, "bold"))
        resolution_frame.pack(pady=10, padx=20, fill="x")
        
        # Комбобокс для разрешений
        tk.Label(resolution_frame, text="Разрешение:").pack(anchor="w", padx=5)
        self.resolution_var = tk.StringVar()
        self.resolution_combo = ttk.Combobox(resolution_frame, textvariable=self.resolution_var, 
                                           state="readonly", width=30)
        self.resolution_combo.pack(pady=5, padx=5, fill="x")
        
        # Комбобокс для частоты обновления
        tk.Label(resolution_frame, text="Частота обновления (Hz):").pack(anchor="w", padx=5)
        self.frequency_var = tk.StringVar()
        self.frequency_combo = ttk.Combobox(resolution_frame, textvariable=self.frequency_var, 
                                          state="readonly", width=30)
        self.frequency_combo.pack(pady=5, padx=5, fill="x")
        
        # Сохраненные разрешения
        saved_frame = tk.LabelFrame(self.root, text="Быстрое переключение", font=("Arial", 10, "bold"))
        saved_frame.pack(pady=10, padx=20, fill="x")
        
        # Кнопки для сохранения разрешений
        save_buttons_frame = tk.Frame(saved_frame)
        save_buttons_frame.pack(pady=5)
        
        self.save_1_button = tk.Button(save_buttons_frame, text="Сохранить как 1", 
                                      command=self.save_resolution_1, 
                                      bg="#FF9800", fg="white", 
                                      font=("Arial", 10, "bold"),
                                      width=15)
        self.save_1_button.pack(side="left", padx=5)
        
        self.save_2_button = tk.Button(save_buttons_frame, text="Сохранить как 2", 
                                      command=self.save_resolution_2, 
                                      bg="#FF9800", fg="white", 
                                      font=("Arial", 10, "bold"),
                                      width=15)
        self.save_2_button.pack(side="left", padx=5)
        
        # Отображение сохраненных разрешений
        saved_info_frame = tk.Frame(saved_frame)
        saved_info_frame.pack(pady=5)
        
        self.saved_1_label = tk.Label(saved_info_frame, text="Разрешение 1: Не сохранено", 
                                     font=("Arial", 9), fg="gray")
        self.saved_1_label.pack(anchor="w")
        
        self.saved_2_label = tk.Label(saved_info_frame, text="Разрешение 2: Не сохранено", 
                                     font=("Arial", 9), fg="gray")
        self.saved_2_label.pack(anchor="w")
        
        # Кнопка Swap
        self.swap_button = tk.Button(saved_frame, text="SWAP", 
                                    command=self.swap_resolutions, 
                                    bg="#E91E63", fg="white", 
                                    font=("Arial", 14, "bold"),
                                    width=20, height=2, state="disabled")
        self.swap_button.pack(pady=10)
        
        # Кнопки
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.apply_button = tk.Button(button_frame, text="Применить", 
                                     command=self.apply_resolution, 
                                     bg="#4CAF50", fg="white", 
                                     font=("Arial", 12, "bold"),
                                     width=15, height=2)
        self.apply_button.pack(side="left", padx=10)
        
        self.refresh_button = tk.Button(button_frame, text="Обновить", 
                                       command=self.refresh_settings, 
                                       bg="#2196F3", fg="white", 
                                       font=("Arial", 12, "bold"),
                                       width=15, height=2)
        self.refresh_button.pack(side="left", padx=10)
        
        # Статус
        self.status_label = tk.Label(self.root, text="Готов к работе", 
                                    font=("Arial", 10), fg="green")
        self.status_label.pack(pady=5)
    
    def load_available_modes(self):
        """Загружает доступные режимы монитора"""
        try:
            # Получаем все доступные режимы дисплея
            modes = []
            i = 0
            while True:
                try:
                    mode = win32api.EnumDisplaySettings(None, i)
                    width = mode.PelsWidth
                    height = mode.PelsHeight
                    frequency = mode.DisplayFrequency
                    
                    # Добавляем только уникальные комбинации разрешения
                    resolution_key = f"{width}x{height}"
                    if resolution_key not in [m['resolution'] for m in modes]:
                        modes.append({
                            'resolution': resolution_key,
                            'width': width,
                            'height': height,
                            'frequencies': [frequency]
                        })
                    else:
                        # Добавляем частоту к существующему разрешению
                        for m in modes:
                            if m['resolution'] == resolution_key and frequency not in m['frequencies']:
                                m['frequencies'].append(frequency)
                                break
                    
                    i += 1
                except:
                    break
            
            # Сортируем разрешения по размеру
            modes.sort(key=lambda x: x['width'] * x['height'])
            
            # Сортируем частоты для каждого разрешения
            for mode in modes:
                mode['frequencies'].sort()
            
            self.available_modes = modes
            
            # Заполняем комбобокс разрешений
            resolution_list = [mode['resolution'] for mode in modes]
            self.resolution_combo['values'] = resolution_list
            
            # Привязываем событие изменения разрешения
            self.resolution_combo.bind('<<ComboboxSelected>>', self.on_resolution_changed)
            
            self.status_label.config(text=f"Загружено {len(modes)} разрешений", fg="green")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить режимы монитора: {str(e)}")
            self.status_label.config(text="Ошибка загрузки", fg="red")
    
    def on_resolution_changed(self, event=None):
        """Обработчик изменения разрешения"""
        selected_resolution = self.resolution_var.get()
        if selected_resolution:
            # Находим выбранное разрешение в списке
            for mode in self.available_modes:
                if mode['resolution'] == selected_resolution:
                    # Заполняем комбобокс частот
                    frequency_list = [str(freq) for freq in mode['frequencies']]
                    self.frequency_combo['values'] = frequency_list
                    
                    # Выбираем максимальную частоту по умолчанию
                    if frequency_list:
                        self.frequency_combo.set(frequency_list[-1])
                    break
    
    def update_current_settings(self):
        """Обновляет информацию о текущих настройках"""
        try:
            # Получаем текущие настройки дисплея
            current_mode = win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS)
            width = current_mode.PelsWidth
            height = current_mode.PelsHeight
            frequency = current_mode.DisplayFrequency
            
            self.current_resolution = f"{width}x{height}"
            self.current_frequency = frequency
            
            # Обновляем отображение
            current_text = f"Разрешение: {self.current_resolution} | Частота: {frequency} Hz"
            self.current_info_label.config(text=current_text)
            
            # Устанавливаем текущие значения в комбобоксы
            self.resolution_var.set(self.current_resolution)
            self.on_resolution_changed()
            self.frequency_var.set(str(frequency))
            
        except Exception as e:
            self.status_label.config(text=f"Ошибка получения настроек: {str(e)}", fg="red")
    
    def apply_resolution(self):
        """Применяет выбранное разрешение"""
        try:
            selected_resolution = self.resolution_var.get()
            selected_frequency = self.frequency_var.get()
            
            if not selected_resolution or not selected_frequency:
                messagebox.showwarning("Предупреждение", "Выберите разрешение и частоту обновления")
                return
            
            # Парсим разрешение
            width, height = map(int, selected_resolution.split('x'))
            frequency = int(selected_frequency)
            
            # Создаем структуру для изменения разрешения
            devmode = win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS)
            devmode.PelsWidth = width
            devmode.PelsHeight = height
            devmode.DisplayFrequency = frequency
            devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT | win32con.DM_DISPLAYFREQUENCY
            
            # Применяем изменения
            result = win32api.ChangeDisplaySettings(devmode, 0)
            
            if result == win32con.DISP_CHANGE_SUCCESSFUL:
                self.update_current_settings()
                self.status_label.config(text="Разрешение успешно изменено", fg="green")
            else:
                error_messages = {
                    win32con.DISP_CHANGE_BADMODE: "Неподдерживаемый режим",
                    win32con.DISP_CHANGE_BADFLAGS: "Неверные флаги",
                    win32con.DISP_CHANGE_BADPARAM: "Неверные параметры",
                    win32con.DISP_CHANGE_FAILED: "Не удалось изменить разрешение",
                    win32con.DISP_CHANGE_RESTART: "Требуется перезагрузка"
                }
                error_msg = error_messages.get(result, f"Неизвестная ошибка: {result}")
                messagebox.showerror("Ошибка", f"Не удалось изменить разрешение: {error_msg}")
                self.status_label.config(text="Ошибка изменения разрешения", fg="red")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
            self.status_label.config(text="Ошибка", fg="red")
    
    def refresh_settings(self):
        """Обновляет настройки"""
        self.load_available_modes()
        self.update_current_settings()
        self.status_label.config(text="Настройки обновлены", fg="green")
    
    def save_resolution_1(self):
        """Сохраняет текущее выбранное разрешение как разрешение 1"""
        selected_resolution = self.resolution_var.get()
        selected_frequency = self.frequency_var.get()
        
        if not selected_resolution or not selected_frequency:
            messagebox.showwarning("Предупреждение", "Выберите разрешение и частоту обновления")
            return
        
        self.saved_resolution_1 = selected_resolution
        self.saved_frequency_1 = selected_frequency
        
        self.saved_1_label.config(text=f"Разрешение 1: {selected_resolution} @ {selected_frequency}Hz", 
                                 fg="black")
        self.update_swap_button_state()
        self.status_label.config(text="Разрешение 1 сохранено", fg="green")
    
    def save_resolution_2(self):
        """Сохраняет текущее выбранное разрешение как разрешение 2"""
        selected_resolution = self.resolution_var.get()
        selected_frequency = self.frequency_var.get()
        
        if not selected_resolution or not selected_frequency:
            messagebox.showwarning("Предупреждение", "Выберите разрешение и частоту обновления")
            return
        
        self.saved_resolution_2 = selected_resolution
        self.saved_frequency_2 = selected_frequency
        
        self.saved_2_label.config(text=f"Разрешение 2: {selected_resolution} @ {selected_frequency}Hz", 
                                 fg="black")
        self.update_swap_button_state()
        self.status_label.config(text="Разрешение 2 сохранено", fg="green")
    
    def update_swap_button_state(self):
        """Обновляет состояние кнопки Swap"""
        if self.saved_resolution_1 and self.saved_resolution_2:
            self.swap_button.config(state="normal")
        else:
            self.swap_button.config(state="disabled")
    
    def swap_resolutions(self):
        """Переключается между сохраненными разрешениями"""
        if not self.saved_resolution_1 or not self.saved_resolution_2:
            messagebox.showwarning("Предупреждение", "Сохраните оба разрешения для переключения")
            return
        
        # Определяем, какое разрешение сейчас активно
        current_res = f"{self.current_resolution} @ {self.current_frequency}Hz"
        saved_1_res = f"{self.saved_resolution_1} @ {self.saved_frequency_1}Hz"
        saved_2_res = f"{self.saved_resolution_2} @ {self.saved_frequency_2}Hz"
        
        # Выбираем разрешение для переключения
        if current_res == saved_1_res:
            # Переключаемся на разрешение 2
            target_resolution = self.saved_resolution_2
            target_frequency = self.saved_frequency_2
        elif current_res == saved_2_res:
            # Переключаемся на разрешение 1
            target_resolution = self.saved_resolution_1
            target_frequency = self.saved_frequency_1
        else:
            # Текущее разрешение не совпадает с сохраненными, переключаемся на разрешение 1
            target_resolution = self.saved_resolution_1
            target_frequency = self.saved_frequency_1
        
        # Применяем выбранное разрешение
        try:
            width, height = map(int, target_resolution.split('x'))
            frequency = int(target_frequency)
            
            # Создаем структуру для изменения разрешения
            devmode = win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS)
            devmode.PelsWidth = width
            devmode.PelsHeight = height
            devmode.DisplayFrequency = frequency
            devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT | win32con.DM_DISPLAYFREQUENCY
            
            # Применяем изменения
            result = win32api.ChangeDisplaySettings(devmode, 0)
            
            if result == win32con.DISP_CHANGE_SUCCESSFUL:
                self.update_current_settings()
                self.status_label.config(text="Разрешение переключено", fg="green")
            else:
                error_messages = {
                    win32con.DISP_CHANGE_BADMODE: "Неподдерживаемый режим",
                    win32con.DISP_CHANGE_BADFLAGS: "Неверные флаги",
                    win32con.DISP_CHANGE_BADPARAM: "Неверные параметры",
                    win32con.DISP_CHANGE_FAILED: "Не удалось изменить разрешение",
                    win32con.DISP_CHANGE_RESTART: "Требуется перезагрузка"
                }
                error_msg = error_messages.get(result, f"Неизвестная ошибка: {result}")
                messagebox.showerror("Ошибка", f"Не удалось переключить разрешение: {error_msg}")
                self.status_label.config(text="Ошибка переключения", fg="red")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при переключении: {str(e)}")
            self.status_label.config(text="Ошибка", fg="red")

def main():
    try:
        root = tk.Tk()
        app = MonitorResolutionSwitcher(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
