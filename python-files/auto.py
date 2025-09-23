import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import keyboard
from pynput import keyboard as pynput_keyboard
import os

class KeyboardRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Keyboard Recorder")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Переменные для записи и воспроизведения
        self.recording = False
        self.playing = False
        self.recorded_events = []
        self.start_time = None
        
        # Создание интерфейса
        self.create_widgets()
        
        # Настройка горячих клавиш
        self.setup_hotkeys()
        
        # Загрузка сохраненных действий
        self.load_actions()
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Клавиатурный рекордер", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Кнопки управления
        self.record_btn = ttk.Button(main_frame, text="Начать запись", 
                                    command=self.toggle_recording)
        self.record_btn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.EW)
        
        self.stop_btn = ttk.Button(mainboard, text="Остановить запись", 
                                  command=self.stop_recording, state=tk.DISABLED)
        self.stop_btn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Статус записи
        self.status_label = ttk.Label(main_frame, text="Готов к записи", 
                                     foreground="green")
        self.status_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Список записанных действий
        actions_frame = ttk.LabelFrame(main_frame, text="Записанные действия", padding="5")
        actions_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.EW)
        
        self.actions_listbox = tk.Listbox(actions_frame, height=8)
        self.actions_listbox.grid(row=0, column=0, sticky=tk.EW)
        
        scrollbar = ttk.Scrollbar(actions_frame, orient=tk.VERTICAL, 
                                 command=self.actions_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.actions_listbox.config(yscrollcommand=scrollbar.set)
        
        # Кнопки управления списком
        list_btn_frame = ttk.Frame(main_frame)
        list_btn_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        ttk.Button(list_btn_frame, text="Очистить список", 
                  command=self.clear_actions).grid(row=0, column=0, padx=5)
        ttk.Button(list_btn_frame, text="Сохранить в файл", 
                  command=self.save_actions).grid(row=0, column=1, padx=5)
        ttk.Button(list_btn_frame, text="Загрузить из файла", 
                  command=self.load_actions_from_file).grid(row=0, column=2, padx=5)
        
        # Информация о горячих клавишах
        hotkeys_frame = ttk.LabelFrame(main_frame, text="Горячие клавиши", padding="5")
        hotkeys_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky=tk.EW)
        
        hotkeys_text = "F1 - начать воспроизведение\nF2 - остановить воспроизведение\nF3 - очистить список действий"
        hotkeys_label = ttk.Label(hotkeys_frame, text=hotkeys_text, justify=tk.LEFT)
        hotkeys_label.grid(row=0, column=0, sticky=tk.W)
        
        # Настройка весов строк и столбцов для правильного растягивания
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        actions_frame.columnconfigure(0, weight=1)
    
    def setup_hotkeys(self):
        """Настройка глобальных горячих клавиш"""
        try:
            keyboard.add_hotkey('f1', self.start_playback)
            keyboard.add_hotkey('f2', self.stop_playback)
            keyboard.add_hotkey('f3', self.clear_actions)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось настроить горячие клавиши: {e}")
    
    def on_press(self, key):
        """Обработчик нажатия клавиш при записи"""
        if self.recording:
            current_time = time.time() - self.start_time
            try:
                # Для обычных клавиш
                key_char = key.char
            except AttributeError:
                # Для специальных клавиш
                key_char = str(key).replace('Key.', '')
            
            event = {
                'type': 'press',
                'key': key_char,
                'time': current_time
            }
            self.recorded_events.append(event)
    
    def on_release(self, key):
        """Обработчик отпускания клавиш при записи"""
        if self.recording:
            current_time = time.time() - self.start_time
            try:
                key_char = key.char
            except AttributeError:
                key_char = str(key).replace('Key.', '')
            
            event = {
                'type': 'release',
                'key': key_char,
                'time': current_time
            }
            self.recorded_events.append(event)
            
            # Проверка на остановку записи (Esc)
            if key == pynput_keyboard.Key.esc:
                self.stop_recording()
    
    def toggle_recording(self):
        """Начать/остановить запись"""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Начать запись действий"""
        self.recording = True
        self.recorded_events = []
        self.start_time = time.time()
        
        # Обновление интерфейса
        self.record_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Запись...", foreground="red")
        
        # Запуск слушателя клавиатуры в отдельном потоке
        self.listener = pynput_keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()
        
        messagebox.showinfo("Запись", "Запись начата! Нажмите ESC для остановки.")
    
    def stop_recording(self):
        """Остановить запись действий"""
        if self.recording:
            self.recording = False
            
            # Остановка слушателя
            if hasattr(self, 'listener'):
                self.listener.stop()
            
            # Обновление интерфейса
            self.record_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text=f"Запись завершена. Действий: {len(self.recorded_events)//2}", 
                                   foreground="green")
            
            # Обновление списка действий
            self.update_actions_list()
    
    def start_playback(self):
        """Начать воспроизведение записанных действий"""
        if self.playing or not self.recorded_events:
            return
        
        self.playing = True
        self.status_label.config(text="Воспроизведение...", foreground="blue")
        
        # Запуск воспроизведения в отдельном потоке
        playback_thread = threading.Thread(target=self.playback_thread)
        playback_thread.daemon = True
        playback_thread.start()
    
    def stop_playback(self):
        """Остановить воспроизведение"""
        self.playing = False
        self.status_label.config(text="Воспроизведение остановлено", foreground="green")
    
    def playback_thread(self):
        """Поток для воспроизведения действий"""
        try:
            start_time = time.time()
            
            for i, event in enumerate(self.recorded_events):
                if not self.playing:
                    break
                
                # Ожидание нужного времени
                while time.time() - start_time < event['time']:
                    if not self.playing:
                        break
                    time.sleep(0.001)
                
                if not self.playing:
                    break
                
                # Воспроизведение действия
                try:
                    if event['type'] == 'press':
                        keyboard.press(event['key'])
                    else:
                        keyboard.release(event['key'])
                except Exception as e:
                    print(f"Ошибка при воспроизведении: {e}")
            
            self.playing = False
            self.root.after(0, lambda: self.status_label.config(
                text="Воспроизведение завершено", foreground="green"))
                
        except Exception as e:
            self.playing = False
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка воспроизведения: {e}"))
    
    def update_actions_list(self):
        """Обновление списка записанных действий"""
        self.actions_listbox.delete(0, tk.END)
        
        press_events = [e for e in self.recorded_events if e['type'] == 'press']
        
        for i, event in enumerate(press_events[:20]):  # Показываем первые 20 действий
            self.actions_listbox.insert(tk.END, f"{i+1}. Нажатие: {event['key']} (время: {event['time']:.2f}с)")
        
        if len(press_events) > 20:
            self.actions_listbox.insert(tk.END, f"... и еще {len(press_events) - 20} действий")
    
    def clear_actions(self):
        """Очистить список действий"""
        if messagebox.askyesno("Подтверждение", "Очистить список записанных действий?"):
            self.recorded_events = []
            self.actions_listbox.delete(0, tk.END)
            self.status_label.config(text="Список действий очищен", foreground="green")
    
    def save_actions(self):
        """Сохранить действия в файл"""
        if not self.recorded_events:
            messagebox.showwarning("Предупреждение", "Нет действий для сохранения")
            return
        
        try:
            with open("keyboard_actions.json", "w", encoding="utf-8") as f:
                json.dump(self.recorded_events, f, indent=2)
            messagebox.showinfo("Успех", "Действия сохранены в файл keyboard_actions.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def load_actions_from_file(self):
        """Загрузить действия из файла"""
        try:
            if not os.path.exists("keyboard_actions.json"):
                messagebox.showwarning("Предупреждение", "Файл keyboard_actions.json не найден")
                return
            
            with open("keyboard_actions.json", "r", encoding="utf-8") as f:
                self.recorded_events = json.load(f)
            
            self.update_actions_list()
            messagebox.showinfo("Успех", f"Загружено {len(self.recorded_events)} действий")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
    
    def load_actions(self):
        """Попытка загрузить действия при запуске"""
        try:
            if os.path.exists("keyboard_actions.json"):
                with open("keyboard_actions.json", "r", encoding="utf-8") as f:
                    self.recorded_events = json.load(f)
                self.update_actions_list()
        except:
            pass  # Игнорируем ошибки при загрузке

def main():
    # Проверка прав администратора (может потребоваться для глобальных горячих клавиш)
    try:
        root = tk.Tk()
        app = KeyboardRecorder(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить программу: {e}")

if __name__ == "__main__":
    main()