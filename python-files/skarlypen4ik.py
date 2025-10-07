import tkinter as tk
from tkinter import ttk, messagebox
import math
import time

class SolarSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Солнечная система")
        self.root.geometry("1200x800")
        self.root.configure(bg='black')
        
        # Данные о планетах
        self.planets_data = {
            "Меркурий": {
                "type": "Планета",
                "диаметр": "4,879 км",
                "масса": "3.3×10²³ кг",
                "расстояние от Солнца": "57.9 млн км",
                "период обращения": "88 дней",
                "температура": "-173°C до 427°C",
                "спутники": 0,
                "описание": "Самая маленькая и ближайшая к Солнцу планета."
            },
            "Венера": {
                "type": "Планета",
                "диаметр": "12,104 км",
                "масса": "4.87×10²⁴ кг",
                "расстояние от Солнца": "108.2 млн км",
                "период обращения": "225 дней",
                "температура": "462°C",
                "спутники": 0,
                "описание": "Самая горячая планета с плотной атмосферой из углекислого газа."
            },
            "Земля": {
                "type": "Планета",
                "диаметр": "12,742 км",
                "масса": "5.97×10²⁴ кг",
                "расстояние от Солнца": "149.6 млн км",
                "период обращения": "365.25 дней",
                "температура": "-88°C до 58°C",
                "спутники": 1,
                "описание": "Единственная известная планета с жизнью."
            },
            "Марс": {
                "type": "Планета",
                "диаметр": "6,779 км",
                "масса": "6.42×10²³ кг",
                "расстояние от Солнца": "227.9 млн км",
                "период обращения": "687 дней",
                "температура": "-87°C до -5°C",
                "спутники": 2,
                "описание": "Красная планета с самыми большими вулканами в Солнечной системе."
            },
            "Юпитер": {
                "type": "Планета-гигант",
                "диаметр": "139,820 км",
                "масса": "1.90×10²⁷ кг",
                "расстояние от Солнца": "778.5 млн км",
                "период обращения": "11.86 лет",
                "температура": "-108°C",
                "спутники": 95,
                "описание": "Самая большая планета в Солнечной системе."
            },
            "Сатурн": {
                "type": "Планета-гигант",
                "диаметр": "116,460 км",
                "масса": "5.68×10²⁶ кг",
                "расстояние от Солнца": "1.43 млрд км",
                "период обращения": "29.46 лет",
                "температура": "-139°C",
                "спутники": 146,
                "описание": "Известен своими красивыми кольцами."
            },
            "Уран": {
                "type": "Ледяной гигант",
                "диаметр": "50,724 км",
                "масса": "8.68×10²⁵ кг",
                "расстояние от Солнца": "2.87 млрд км",
                "период обращения": "84.01 лет",
                "температура": "-197°C",
                "спутники": 28,
                "описание": "Планета, которая вращается 'на боку'."
            },
            "Нептун": {
                "type": "Ледяной гигант",
                "диаметр": "49,244 км",
                "масса": "1.02×10²⁶ кг",
                "расстояние от Солнца": "4.5 млрд км",
                "период обращения": "164.8 лет",
                "температура": "-201°C",
                "спутники": 16,
                "описание": "Самая ветреная планета со скоростью ветра до 2100 км/ч."
            }
        }
        
        # Данные о спутниках
        self.moons_data = {
            "Луна": {
                "планета": "Земля",
                "диаметр": "3,474 км",
                "масса": "7.35×10²² кг",
                "расстояние от планеты": "384,400 км",
                "период обращения": "27.3 дня",
                "описание": "Единственный естественный спутник Земли."
            },
            "Фобос": {
                "планета": "Марс",
                "диаметр": "22.5 км",
                "масса": "1.08×10¹⁶ кг",
                "расстояние от планеты": "9,377 км",
                "период обращения": "7.66 часа",
                "описание": "Ближайший спутник Марса, постепенно приближается к планете."
            },
            "Деймос": {
                "планета": "Марс",
                "диаметр": "12.4 км",
                "масса": "2.0×10¹⁵ кг",
                "расстояние от планеты": "23,460 км",
                "период обращения": "30.35 часа",
                "описание": "Второй и меньший спутник Марса."
            },
            "Ио": {
                "планета": "Юпитер",
                "диаметр": "3,643 км",
                "масса": "8.93×10²² кг",
                "расстояние от планеты": "421,700 км",
                "период обращения": "1.77 дня",
                "описание": "Самый вулканически активный объект в Солнечной системе."
            },
            "Европа": {
                "планета": "Юпитер",
                "диаметр": "3,122 км",
                "масса": "4.80×10²² кг",
                "расстояние от планеты": "671,034 км",
                "период обращения": "3.55 дня",
                "описание": "Имеет подледный океан, возможное место для жизни."
            },
            "Ганимед": {
                "планета": "Юпитер",
                "диаметр": "5,262 км",
                "масса": "1.48×10²³ кг",
                "расстояние от планеты": "1,070,400 км",
                "период обращения": "7.15 дня",
                "описание": "Крупнейший спутник в Солнечной системе."
            },
            "Каллисто": {
                "планета": "Юпитер",
                "диаметр": "4,821 км",
                "масса": "1.08×10²³ кг",
                "расстояние от планеты": "1,882,700 км",
                "период обращения": "16.69 дня",
                "описание": "Сильно кратерированный спутник с древней поверхностью."
            },
            "Титан": {
                "планета": "Сатурн",
                "диаметр": "5,151 км",
                "масса": "1.35×10²³ кг",
                "расстояние от планеты": "1,221,850 км",
                "период обращения": "15.95 дня",
                "описание": "Единственный спутник с плотной атмосферой, имеет озера из метана."
            },
            "Энцелад": {
                "планета": "Сатурн",
                "диаметр": "504 км",
                "масса": "1.08×10²⁰ кг",
                "расстояние от планеты": "238,020 км",
                "период обращения": "1.37 дня",
                "описание": "Имеет подледный океан и гейзеры водяного пара."
            },
            "Тритон": {
                "планета": "Нептун",
                "диаметр": "2,707 км",
                "масса": "2.14×10²² кг",
                "расстояние от планеты": "354,759 км",
                "период обращения": "5.88 дня",
                "описание": "Крупнейший спутник Нептуна, движется в обратном направлении."
            }
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        # Создаем вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка с планетами
        planets_frame = ttk.Frame(notebook)
        notebook.add(planets_frame, text="Планеты")
        
        # Вкладка со спутниками
        moons_frame = ttk.Frame(notebook)
        notebook.add(moons_frame, text="Спутники")
        
        # Вкладка с солнечной системой
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text="Солнечная система")
        
        self.setup_planets_tab(planets_frame)
        self.setup_moons_tab(moons_frame)
        self.setup_system_tab(system_frame)
    
    def setup_planets_tab(self, parent):
        # Левая часть - список планет
        left_frame = ttk.Frame(parent)
        left_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        ttk.Label(left_frame, text="Выберите планету:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        self.planets_listbox = tk.Listbox(left_frame, width=20, height=15, font=('Arial', 11))
        self.planets_listbox.pack(pady=10, padx=5, fill='both', expand=True)
        
        for planet in self.planets_data.keys():
            self.planets_listbox.insert(tk.END, planet)
        
        self.planets_listbox.bind('<<ListboxSelect>>', self.on_planet_select)
        
        # Правая часть - информация о планете
        self.planet_info_frame = ttk.Frame(parent)
        self.planet_info_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        self.planet_title = ttk.Label(self.planet_info_frame, text="Выберите планету", 
                                    font=('Arial', 16, 'bold'))
        self.planet_title.pack(pady=10)
        
        self.planet_info_text = tk.Text(self.planet_info_frame, width=60, height=20, 
                                      font=('Arial', 11), wrap='word')
        self.planet_info_text.pack(pady=10, padx=5, fill='both', expand=True)
        
        # Добавляем прокрутку для текста
        scrollbar = ttk.Scrollbar(self.planet_info_text)
        scrollbar.pack(side='right', fill='y')
        self.planet_info_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.planet_info_text.yview)
    
    def setup_moons_tab(self, parent):
        # Левая часть - список спутников
        left_frame = ttk.Frame(parent)
        left_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        ttk.Label(left_frame, text="Выберите спутник:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        self.moons_listbox = tk.Listbox(left_frame, width=20, height=15, font=('Arial', 11))
        self.moons_listbox.pack(pady=10, padx=5, fill='both', expand=True)
        
        for moon in self.moons_data.keys():
            self.moons_listbox.insert(tk.END, moon)
        
        self.moons_listbox.bind('<<ListboxSelect>>', self.on_moon_select)
        
        # Правая часть - информация о спутнике
        self.moon_info_frame = ttk.Frame(parent)
        self.moon_info_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        self.moon_title = ttk.Label(self.moon_info_frame, text="Выберите спутник", 
                                  font=('Arial', 16, 'bold'))
        self.moon_title.pack(pady=10)
        
        self.moon_info_text = tk.Text(self.moon_info_frame, width=60, height=20, 
                                    font=('Arial', 11), wrap='word')
        self.moon_info_text.pack(pady=10, padx=5, fill='both', expand=True)
        
        # Добавляем прокрутку для текста
        scrollbar = ttk.Scrollbar(self.moon_info_text)
        scrollbar.pack(side='right', fill='y')
        self.moon_info_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.moon_info_text.yview)
    
    def setup_system_tab(self, parent):
        # Canvas для отрисовки солнечной системы
        self.canvas = tk.Canvas(parent, width=1000, height=600, bg='black')
        self.canvas.pack(pady=20)
        
        # Информационная панель
        self.info_label = ttk.Label(parent, text="Наведите курсор на объект для получения информации", 
                                  font=('Arial', 12))
        self.info_label.pack(pady=10)
        
        # Кнопка анимации
        self.animate_button = ttk.Button(parent, text="Запустить анимацию", 
                                       command=self.toggle_animation)
        self.animate_button.pack(pady=5)
        
        self.animation_running = False
        self.draw_solar_system()
    
    def on_planet_select(self, event):
        selection = self.planets_listbox.curselection()
        if selection:
            planet_name = self.planets_listbox.get(selection[0])
            planet_data = self.planets_data[planet_name]
            
            self.planet_title.config(text=planet_name)
            
            info_text = f"Тип: {planet_data['type']}\n\n"
            info_text += f"Диаметр: {planet_data['диаметр']}\n"
            info_text += f"Масса: {planet_data['масса']}\n"
            info_text += f"Расстояние от Солнца: {planet_data['расстояние от Солнца']}\n"
            info_text += f"Период обращения: {planet_data['период обращения']}\n"
            info_text += f"Температура: {planet_data['температура']}\n"
            info_text += f"Количество спутников: {planet_data['спутники']}\n\n"
            info_text += f"Описание:\n{planet_data['описание']}"
            
            self.planet_info_text.delete(1.0, tk.END)
            self.planet_info_text.insert(1.0, info_text)
    
    def on_moon_select(self, event):
        selection = self.moons_listbox.curselection()
        if selection:
            moon_name = self.moons_listbox.get(selection[0])
            moon_data = self.moons_data[moon_name]
            
            self.moon_title.config(text=f"{moon_name} ({moon_data['планета']})")
            
            info_text = f"Планета: {moon_data['планета']}\n\n"
            info_text += f"Диаметр: {moon_data['диаметр']}\n"
            info_text += f"Масса: {moon_data['масса']}\n"
            info_text += f"Расстояние от планеты: {moon_data['расстояние от планеты']}\n"
            info_text += f"Период обращения: {moon_data['период обращения']}\n\n"
            info_text += f"Описание:\n{moon_data['описание']}"
            
            self.moon_info_text.delete(1.0, tk.END)
            self.moon_info_text.insert(1.0, info_text)
    
    def draw_solar_system(self):
        self.canvas.delete("all")
        
        # Центр canvas
        center_x = 500
        center_y = 300
        
        # Солнце
        sun_radius = 30
        self.canvas.create_oval(center_x - sun_radius, center_y - sun_radius,
                              center_x + sun_radius, center_y + sun_radius,
                              fill='yellow', outline='orange', width=2)
        self.canvas.create_text(center_x, center_y - sun_radius - 10, 
                              text="Солнце", fill='white', font=('Arial', 10, 'bold'))
        
        # Орбиты и планеты (масштабировано для отображения)
        planets = [
            ("Меркурий", 60, 5, 'gray'),
            ("Венера", 90, 8, 'orange'),
            ("Земля", 120, 9, 'blue'),
            ("Марс", 150, 7, 'red'),
            ("Юпитер", 200, 18, 'brown'),
            ("Сатурн", 260, 16, 'yellow'),
            ("Уран", 320, 12, 'lightblue'),
            ("Нептун", 380, 12, 'blue')
        ]
        
        self.planet_positions = {}
        
        for i, (name, radius, size, color) in enumerate(planets):
            # Орбита
            self.canvas.create_oval(center_x - radius, center_y - radius,
                                  center_x + radius, center_y + radius,
                                  outline='gray', width=1, dash=(2, 2))
            
            # Положение планеты на орбите
            angle = i * 45 * math.pi / 180  # Равномерное распределение
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Планета
            planet_id = self.canvas.create_oval(x - size, y - size,
                                              x + size, y + size,
                                              fill=color, outline='white', width=1)
            
            # Название планеты
            text_id = self.canvas.create_text(x, y + size + 15, 
                                            text=name, fill='white', font=('Arial', 8))
            
            # Сохраняем позиции для анимации
            self.planet_positions[name] = {
                'id': planet_id,
                'text_id': text_id,
                'radius': radius,
                'size': size,
                'color': color,
                'angle': angle,
                'speed': 0.5 + (i * 0.1)  # Разная скорость для каждой планеты
            }
            
            # Привязываем события наведения
            self.canvas.tag_bind(planet_id, '<Enter>', 
                               lambda e, n=name: self.show_object_info(n))
            self.canvas.tag_bind(planet_id, '<Leave>', 
                               lambda e: self.info_label.config(
                                   text="Наведите курсор на объект для получения информации"))
            self.canvas.tag_bind(text_id, '<Enter>', 
                               lambda e, n=name: self.show_object_info(n))
            self.canvas.tag_bind(text_id, '<Leave>', 
                               lambda e: self.info_label.config(
                                   text="Наведите курсор на объект для получения информации"))
    
    def show_object_info(self, object_name):
        if object_name == "Солнце":
            info = "Солнце - звезда в центре Солнечной системы\nДиаметр: 1,391,000 км\nТемпература ядра: 15 млн °C"
        elif object_name in self.planets_data:
            data = self.planets_data[object_name]
            info = f"{object_name}\nДиаметр: {data['диаметр']}\nТемпература: {data['температура']}"
        else:
            info = f"{object_name} - выберите объект из списка для подробной информации"
        
        self.info_label.config(text=info)
    
    def toggle_animation(self):
        self.animation_running = not self.animation_running
        if self.animation_running:
            self.animate_button.config(text="Остановить анимацию")
            self.animate_planets()
        else:
            self.animate_button.config(text="Запустить анимацию")
    
    def animate_planets(self):
        if not self.animation_running:
            return
        
        center_x = 500
        center_y = 300
        
        for name, data in self.planet_positions.items():
            # Обновляем угол
            data['angle'] += data['speed'] * 0.05
            
            # Вычисляем новую позицию
            x = center_x + data['radius'] * math.cos(data['angle'])
            y = center_y + data['radius'] * math.sin(data['angle'])
            
            # Перемещаем планету
            self.canvas.coords(data['id'],
                             x - data['size'], y - data['size'],
                             x + data['size'], y + data['size'])
            
            # Перемещаем текст
            self.canvas.coords(data['text_id'], x, y + data['size'] + 15)
        
        # Планируем следующий кадр
        self.root.after(50, self.animate_planets)

def main():
    root = tk.Tk()
    app = SolarSystemApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
