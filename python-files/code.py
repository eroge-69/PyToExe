
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.widgets import Button, TextBox, RadioButtons
from shapely.geometry import Polygon

class InteractivePolygonDrawer:
    def __init__(self):
        # Инициализация графического интерфейса
        self.fig, self.ax = plt.subplots(figsize=(12, 9))
        self.fig.canvas.manager.set_window_title('Расчет площади сложных участков')
        self.ax.set_position([0.1, 0.2, 0.8, 0.75])
        
        # Настройка области рисования
        self.ax.set_title('Построение участка сложной формы', fontsize=14, pad=20)
        self.ax.set_xlabel('Координата X (метры)', fontsize=12)
        self.ax.set_ylabel('Координата Y (метры)', fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.set_axisbelow(True)
        self.ax.set_aspect('equal')
        
        # Элементы данных
        self.points = []
        self.lines = []
        self.distance_annotations = []
        self.polygon_patch = None
        self.area_text = None
        self.area_value = 0.0
        self.current_segment_length = 0.0
        self.manual_input_mode = False
        self.last_direction = None
        self.last_segment_angle = 0  # угол последнего сегмента в радианах
        
        # Создаем панель управления
        self.create_control_panel()
        
        # Привязка событий
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Статус
        self.update_status("Готов к работе. Добавьте первую точку кликом мыши")
        
        # Инструкция
        print("="*80)
        print("ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ".center(80))
        print("="*80)
        print("Автоматический режим:")
        print(" - Клик левой кнопкой: добавить точку в указанном месте")
        print("Ручной режим:")
        print(" 1. Нажмите 'Ручной ввод' для активации режима")
        print(" 2. Кликните для добавления начальной точки")
        print(" 3. Введите длину сегмента и угол в градусах")
        print(" 4. Выберите тип угла: Абсолютный (0°=восток, 90°=север) или Относительный (от предыдущего сегмента)")
        print(" 5. Нажмите 'Применить длину'")
        print("Общие команды:")
        print(" - Enter: завершить фигуру | d: удалить последнюю точку")
        print(" - c: очистить холст | r: повернуть направление на 180°")
        print("="*80)
        
        plt.show()

    def create_control_panel(self):
        """Создает панель управления с кнопками и полем ввода"""
        # Панель для кнопок
        button_ax = plt.axes([0.15, 0.05, 0.15, 0.06])
        self.manual_btn = Button(button_ax, 'Ручной ввод', color='#e6f7ff', hovercolor='#91d5ff')
        self.manual_btn.on_clicked(self.toggle_manual_mode)
        
        # Поле для ввода длины
        length_ax = plt.axes([0.35, 0.05, 0.15, 0.06])
        self.length_input = TextBox(length_ax, "Длина (м): ", initial="10.0")
        self.length_input.label.set_fontsize(10)
        
        # Кнопка применения длины
        apply_ax = plt.axes([0.55, 0.05, 0.15, 0.06])
        self.apply_btn = Button(apply_ax, 'Применить длину', color='#f6ffed', hovercolor='#b7eb8f')
        self.apply_btn.on_clicked(self.apply_manual_segment)  # Изменено название метода
        
        # Поле для ввода угла
        angle_ax = plt.axes([0.35, 0.12, 0.15, 0.06])
        self.angle_input = TextBox(angle_ax, "Угол (°): ", initial="0.0")
        self.angle_input.label.set_fontsize(10)
        
        # Выпадающий список для типа угла
        angle_type_ax = plt.axes([0.55, 0.12, 0.15, 0.06])
        self.angle_type_dropdown = RadioButtons(angle_type_ax, ('Абсолютный', 'Относительный'))
        angle_type_ax.set_title("Тип угла", fontsize=9)
        self.angle_type = "Абсолютный"  # значение по умолчанию
        
        # Обработчик для выбора типа угла
        def angle_type_handler(label):
            self.angle_type = label
        self.angle_type_dropdown.on_clicked(angle_type_handler)
        
        # Текстовое поле статуса
        self.status_text = self.fig.text(0.5, 0.18, "", 
                                       ha='center', fontsize=11,
                                       bbox=dict(boxstyle="round,pad=0.3", facecolor='#f0f0f0', alpha=0.9))
        
        # Информация о площади
        self.area_info = self.fig.text(0.5, 0.01, "Площадь: 0.00 м² (0.0000 га)", 
                                     ha='center', fontsize=12, weight='bold',
                                     bbox=dict(boxstyle="round,pad=0.4", facecolor='white', edgecolor='#096dd9', alpha=0.9))

    def toggle_manual_mode(self, event):
        """Переключает режим ручного ввода"""
        self.manual_input_mode = not self.manual_input_mode
        if self.manual_input_mode:
            self.manual_btn.color = '#b7eb8f'
            self.update_status("Ручной режим: кликните для добавления начальной точки")
        else:
            self.manual_btn.color = '#e6f7ff'
            self.update_status("Автоматический режим: кликните для добавления точки")
        self.fig.canvas.draw_idle()

    def apply_manual_segment(self, event):
        """Применяет введенные длину и угол для создания нового сегмента"""
        if not self.points:
            self.update_status("Ошибка: сначала добавьте начальную точку")
            return
            
        try:
            length = float(self.length_input.text)
            angle = float(self.angle_input.text)
            if length <= 0:
                raise ValueError
        except ValueError:
            self.update_status("Ошибка: введите корректные числовые значения")
            return
            
        # Конвертируем угол в радианы
        angle_rad = np.deg2rad(angle)
        
        last_x, last_y = self.points[-1]
        
        if self.angle_type == "Абсолютный":
            # 0° = восток (положительное направление X)
            # 90° = север (положительное направление Y)
            dx = np.cos(angle_rad) * length
            dy = np.sin(angle_rad) * length
        else:  # Относительный
            if len(self.points) < 2:
                self.update_status("Предупреждение: для первой точки относительный угол недоступен. Используется абсолютный.")
                dx = np.cos(angle_rad) * length
                dy = np.sin(angle_rad) * length
            else:
                # Определяем направление предыдущего сегмента
                prev_x, prev_y = self.points[-2]
                seg_dx = last_x - prev_x
                seg_dy = last_y - prev_y
                seg_length = np.sqrt(seg_dx**2 + seg_dy**2)
                
                if seg_length > 0:
                    # Угол предыдущего сегмента
                    seg_angle = np.arctan2(seg_dy, seg_dx)
                    # Новый угол = угол предыдущего сегмента + введенный угол
                    new_angle = seg_angle + angle_rad
                    dx = np.cos(new_angle) * length
                    dy = np.sin(new_angle) * length
                else:
                    dx = np.cos(angle_rad) * length
                    dy = np.sin(angle_rad) * length
        
        new_x = last_x + dx
        new_y = last_y + dy
        self.add_point(new_x, new_y)
        self.update_status(f"Добавлена точка по ручному вводу: ({new_x:.2f}, {new_y:.2f})")
        self.fig.canvas.draw_idle()

    def update_status(self, message):
        """Обновляет статусное сообщение"""
        mode = "Ручной" if self.manual_input_mode else "Авто"
        self.status_text.set_text(f"{message}\nРежим: {mode} | Точки: {len(self.points)}")
        self.fig.canvas.draw_idle()

    def update_area_info(self):
        """Обновляет информацию о площади"""
        self.area_info.set_text(f"Площадь: {self.area_value:.2f} м² ({self.area_value/10000:.4f} га)")
        self.fig.canvas.draw_idle()

    def on_mouse_move(self, event):
        """Обрабатывает движение мыши"""
        if not event.inaxes or not self.points:
            return
            
        # Обновляем длину и угол в реальном времени для ручного режима
        if self.manual_input_mode and self.points:
            last_x, last_y = self.points[-1]
            x, y = event.xdata, event.ydata
            dx, dy = x - last_x, y - last_y
            distance = np.sqrt(dx*dx + dy*dy)
            self.current_segment_length = distance
            self.length_input.set_val(f"{distance:.2f}")
            
            # Рассчитываем и отображаем угол
            angle_deg = np.rad2deg(np.arctan2(dy, dx))
            self.angle_input.set_val(f"{angle_deg:.2f}")

    def add_point(self, x, y):
        """Добавляет точку и соединяет ее с предыдущей"""
        self.points.append((x, y))
        point_plot = self.ax.plot(x, y, 'ro', markersize=7, zorder=3)[0]
        self.lines.append(point_plot)
        
        # Рисуем линию, если есть предыдущая точка
        if len(self.points) > 1:
            prev_x, prev_y = self.points[-2]
            line, = self.ax.plot([prev_x, x], [prev_y, y], 'b-', linewidth=1.5, zorder=2)
            self.lines.append(line)
            
            # Отображаем длину сегмента
            length = np.sqrt((x - prev_x)**2 + (y - prev_y)**2)
            mid_x, mid_y = (prev_x + x)/2, (prev_y + y)/2
            annotation = self.ax.text(mid_x, mid_y, f"{length:.2f} м", 
                                     fontsize=9, ha='center', va='center',
                                     bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
            self.distance_annotations.append(annotation)
            
            # Обновляем информацию о направлении
            dx = x - prev_x
            dy = y - prev_y
            self.last_segment_angle = np.arctan2(dy, dx)
        
        self.update_status(f"Добавлена точка: ({x:.2f}, {y:.2f})")

    def on_click(self, event):
        """Обработка клика мыши"""
        if event.inaxes != self.ax or event.button != 1:
            return
            
        x, y = event.xdata, event.ydata
        
        if self.manual_input_mode:
            if not self.points:
                self.add_point(x, y)
                self.update_status("Ручной режим: введите длину и угол, затем нажмите 'Применить длину'")
            else:
                # В ручном режиме дополнительные клики игнорируем
                self.update_status("Ручной режим: используйте поля ввода для добавления сегментов")
        else:
            # Автоматический режим
            self.add_point(x, y)
            
        self.fig.canvas.draw_idle()

    def calculate_area(self):
        """Вычисляет площадь полигона"""
        if len(self.points) < 3:
            return 0.0
            
        try:
            polygon = Polygon(self.points)
            return polygon.area
        except:
            return 0.0

    def finish_polygon(self):
        """Завершает построение полигона"""
        if len(self.points) < 3:
            self.update_status("Ошибка: нужно минимум 3 точки для создания полигона")
            return
            
        # Замыкаем полигон
        first_x, first_y = self.points[0]
        last_x, last_y = self.points[-1]
        
        if (last_x, last_y) != (first_x, first_y):
            closing_line, = self.ax.plot([last_x, first_x], [last_y, first_y], 'b-', linewidth=1.5, zorder=2)
            self.lines.append(closing_line)
            
            # Отображаем длину последнего сегмента
            length = np.sqrt((last_x - first_x)**2 + (last_y - first_y)**2)
            mid_x, mid_y = (last_x + first_x)/2, (last_y + first_y)/2
            annotation = self.ax.text(mid_x, mid_y, f"{length:.2f} м", 
                                    fontsize=9, ha='center', va='center',
                                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
            self.distance_annotations.append(annotation)
            
            self.points.append((first_x, first_y))
        
        # Вычисляем площадь
        self.area_value = self.calculate_area()
        
        # Отображаем заполненный полигон
        if self.polygon_patch:
            self.polygon_patch.remove()
        poly_patch = MplPolygon(self.points, closed=True, alpha=0.3, color='#52c41a', zorder=1)
        self.ax.add_patch(poly_patch)
        self.polygon_patch = poly_patch
        
        # Отображаем площадь
        if self.area_text:
            self.area_text.remove()
        if self.points:
            polygon = Polygon(self.points)
            centroid_x, centroid_y = polygon.centroid.coords[0]
            self.area_text = self.ax.text(centroid_x, centroid_y, 
                                         f"Площадь: {self.area_value:.2f} м²\n({self.area_value/10000:.4f} га)",
                                         fontsize=12, ha='center', va='center', weight='bold',
                                         bbox=dict(boxstyle="round,pad=0.4", facecolor='white', edgecolor='#096dd9', alpha=0.9))
        
        self.update_area_info()
        self.update_status(f"Фигура завершена! Площадь: {self.area_value:.2f} м²")
        
        # Вывод результатов в консоль
        print("\n" + "="*70)
        print(" РАСЧЕТ ПЛОЩАДИ ЗАВЕРШЕН ".center(70, '='))
        print("="*70)
        print(f"Количество вершин: {len(self.points)}")
        print(f"Координаты вершин:")
        for i, (x, y) in enumerate(self.points, 1):
            print(f"  Точка {i}: ({x:.2f}, {y:.2f})")
        print("-"*70)
        print(f"Общая площадь: {self.area_value:.2f} квадратных метров")
        print(f"              = {self.area_value/10000:.4f} гектаров")
        print("="*70)

    def on_key_press(self, event):
        """Обработка нажатия клавиш"""
        if event.key == 'enter':
            self.finish_polygon()
            
        elif event.key == 'd' and self.points:
            # Удаление последней точки
            if self.lines:
                self.lines.pop().remove()
            self.points.pop()
            if self.lines:  # Удаляем точку только если есть что удалять
                self.ax.lines[-1].remove()
            
            # Удаление аннотации если есть
            if self.distance_annotations:
                self.distance_annotations.pop().remove()
            
            # Обновляем угол последнего сегмента
            if len(self.points) > 1:
                last_x, last_y = self.points[-1]
                prev_x, prev_y = self.points[-2]
                dx = last_x - prev_x
                dy = last_y - prev_y
                self.last_segment_angle = np.arctan2(dy, dx)
            else:
                self.last_segment_angle = 0
            
            self.update_status("Последняя точка удалена. Продолжайте построение")
            self.area_value = self.calculate_area()
            self.update_area_info()
            self.fig.canvas.draw_idle()
        
        elif event.key == 'c':
            # Очистка всего холста
            self.ax.clear()
            self.ax.set_title('Построение участка сложной формы', fontsize=14, pad=20)
            self.ax.set_xlabel('Координата X (метры)', fontsize=12)
            self.ax.set_ylabel('Координата Y (метры)', fontsize=12)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.set_axisbelow(True)
            self.ax.set_aspect('equal')
            
            self.points = []
            self.lines = []
            self.distance_annotations = []
            self.polygon_patch = None
            self.area_text = None
            self.area_value = 0.0
            self.last_direction = None
            self.last_segment_angle = 0
            self.manual_input_mode = False
            self.manual_btn.color = '#e6f7ff'
            self.angle_type = "Абсолютный"
            
            self.update_status("Холст очищен. Начните построение нового участка")
            self.update_area_info()
            self.fig.canvas.draw_idle()
        
        elif event.key == 'r' and self.last_direction and self.points:
            # Поворот направления на 180 градусов
            last_x, last_y = self.points[-1]
            dir_x, dir_y = self.last_direction
            # Вычисляем противоположное направление
            self.last_direction = (2*last_x - dir_x, 2*last_y - dir_y)
            self.update_status("Направление изменено на противоположное")
            self.fig.canvas.draw_idle()

# Запуск приложения
if __name__ == "__main__":
    print("Запуск программы для расчета площади сложных участков...")
    print("Пожалуйста, подождите, пока инициализируется интерфейс...\n")
    app = InteractivePolygonDrawer()