#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkX11', '3.0')
from gi.repository import Gtk, Gdk, GdkX11, GObject, GLib
import math
import cairo
import os
import configparser
import subprocess
import webbrowser  # Добавлен импорт для работы с браузером

# Базовый масштаб (метров на пиксель) для масштаба 225
BASE_SCALE_225 = 3.722132
BASE_SCALE_VALUE = 225

# Список масштабов карт
MAP_SCALES = [150, 170, 180, 190, 200, 225, 250, 275, 300, 325, 400, 450, 500, 550]

class MapRuler(Gtk.Window):
    def __init__(self):
        super().__init__(title="Дальномер для War Thunder")
        # Увеличиваем высоту окна
        self.set_default_size(500, 480)
        self.set_app_paintable(True)
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_visual(self.get_screen().get_rgba_visual())
        self.set_position(Gtk.WindowPosition.CENTER)

        # Настройки
        self.selected_scale = BASE_SCALE_VALUE  # Масштаб карты по умолчанию
        self.scale_factor = BASE_SCALE_225  # Начальный масштаб
        self.start_point = None
        self.end_point = None
        self.temp_point = None
        self.last_focus = None
        self.horizontal_only = False  # Измерение по всем осям
        self.calibration_mode = False  # Режим калибровки
        self.calibration_result = None  # Результат калибровки

        # Загрузка сохраненных настроек
        self.config_file = os.path.expanduser("~/.wt_map_ruler.ini")
        self.load_config()

        # Пересчитываем масштаб при запуске
        self.recalculate_scale()

        # Создаем основной контейнер
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.add(self.box)

        # Создаем панель управления
        self.create_control_panel()

        # Обработчики событий
        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_button_press)
        self.connect("motion-notify-event", self.on_mouse_move)
        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", self.on_destroy)
        self.connect("realize", self.on_realize)

        # Разрешаем отслеживание движения мыши
        self.set_events(Gdk.EventMask.POINTER_MOTION_MASK)

        # Прозрачность
        self.set_opacity(0.85)

    def on_realize(self, widget):
        # Размещаем окно в правом нижнем углу экрана
        screen = self.get_screen()
        monitor = screen.get_display().get_primary_monitor()
        geometry = monitor.get_geometry()

        width, height = self.get_size()
        x = geometry.x + geometry.width - width
        y = geometry.y + geometry.height - height

        self.move(x, y)
        self.set_keep_above(True)
        self.set_accept_focus(False)

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
            try:
                self.selected_scale = int(config.get('DEFAULT', 'selected_scale', fallback=str(BASE_SCALE_VALUE)))
                # Проверяем, что выбранный масштаб есть в списке
                if self.selected_scale not in MAP_SCALES:
                    self.selected_scale = BASE_SCALE_VALUE
            except (ValueError, configparser.NoSectionError, configparser.NoOptionError) as e:
                print(f"Ошибка загрузки конфига: {e}")

    def save_config(self):
        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            'selected_scale': str(self.selected_scale)
        }

        with open(self.config_file, 'w') as configfile:
            config.write(configfile)

    def recalculate_scale(self):
        """Пересчитываем масштаб на основе выбранного значения карты"""
        self.scale_factor = BASE_SCALE_225 * (self.selected_scale / BASE_SCALE_VALUE)
        if hasattr(self, 'scale_value'):
            self.scale_value.set_text(f"{self.scale_factor:.6f} м/пикс")
        if hasattr(self, 'distance_value') and self.start_point and self.end_point:
            self.update_distance_display()

    def on_destroy(self, widget):
        self.save_config()
        Gtk.main_quit()

    def create_control_panel(self):
        # Панель управления
        self.control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.control_box.set_margin_start(5)
        self.control_box.set_margin_end(5)
        self.control_box.set_margin_top(5)
        self.box.pack_start(self.control_box, False, False, 0)

        # Кнопка переключения режима калибровки
        self.calibration_btn = Gtk.ToggleButton(label="Калибровка")
        self.calibration_btn.set_tooltip_text("Режим калибровки (измерение метров на пиксель)")
        self.calibration_btn.connect("toggled", self.on_calibration_toggled)
        self.control_box.pack_start(self.calibration_btn, False, False, 0)

        # Выбор масштаба карты
        self.scale_label = Gtk.Label(label="Масштаб карты:")
        self.control_box.pack_start(self.scale_label, False, False, 0)

        # Выпадающий список с масштабами
        self.scale_combo = Gtk.ComboBoxText()
        for scale in MAP_SCALES:
            self.scale_combo.append_text(str(scale))
        # Устанавливаем выбранный масштаб (225 по умолчанию)
        self.scale_combo.set_active(MAP_SCALES.index(self.selected_scale))
        self.scale_combo.connect("changed", self.on_scale_changed)
        self.control_box.pack_start(self.scale_combo, False, False, 0)

        # Информация о текущем масштабе
        self.scale_label = Gtk.Label(label="Текущий масштаб:")
        self.control_box.pack_start(self.scale_label, False, False, 0)

        self.scale_value = Gtk.Label(label=f"{self.scale_factor:.6f} м/пикс")
        self.scale_value.get_style_context().add_class("scale-value")
        self.control_box.pack_start(self.scale_value, False, False, 0)

        # Поле вывода расстояния
        self.distance_label = Gtk.Label(label="Дистанция:")
        self.control_box.pack_start(self.distance_label, False, False, 0)

        self.distance_value = Gtk.Label(label="0.00 м")
        self.distance_value.get_style_context().add_class("distance-value")
        self.control_box.pack_start(self.distance_value, False, False, 0)

        # Кнопка сброса точек
        self.reset_btn = Gtk.Button(label="↺")
        self.reset_btn.get_style_context().add_class("reset-btn")
        self.reset_btn.connect("clicked", self.reset_points)
        self.reset_btn.set_tooltip_text("Сбросить точки измерения (R)")
        self.control_box.pack_end(self.reset_btn, False, False, 0)

        # Кнопка YouTube (вместо закрытия)
        self.youtube_btn = Gtk.Button(label="Y")
        self.youtube_btn.get_style_context().add_class("youtube-btn")
        # При нажатии открываем ссылку в браузере
        self.youtube_btn.connect("clicked", lambda w: webbrowser.open("https://www.youtube.com/@EXTRUD/shorts"))
        self.youtube_btn.set_tooltip_text("YouTube канал EXTRUD")
        self.control_box.pack_end(self.youtube_btn, False, False, 0)

        # Кнопка поверх окон
        self.top_btn = Gtk.ToggleButton(label="🔝")
        self.top_btn.set_active(True)
        self.top_btn.connect("toggled", self.on_top_toggled)
        self.top_btn.set_tooltip_text("Всегда поверх других окон")
        self.control_box.pack_end(self.top_btn, False, False, 0)

        # Применяем CSS для стилизации
        css_provider = Gtk.CssProvider()
        css = b"""
        * {
            font-family: 'Sans';
            font-size: 10pt;
        }
        .close-btn {
            font-weight: bold;
            font-size: 14px;
            min-width: 20px;
            min-height: 20px;
            border-radius: 10px;
            background-color: #FF6B6B;
            color: white;
            border: none;
        }
        .reset-btn {
            font-weight: bold;
            font-size: 14px;
            min-width: 20px;
            min-height: 20px;
            border-radius: 10px;
            background-color: #3498DB;
            color: white;
            border: none;
        }
        .youtube-btn {
            font-weight: bold;
            font-size: 14px;
            min-width: 20px;
            min-height: 20px;
            border-radius: 10px;
            background-color: #FF0000;
            color: white;
            border: none;
        }
        .distance-value {
            font-weight: bold;
            color: #27AE60;
            min-width: 80px;
        }
        .scale-value {
            font-weight: bold;
            color: #3498DB;
            min-width: 150px;
        }
        .calibration-active {
            background-color: #FF9800;
            color: white;
        }
        """
        css_provider.load_from_data(css)
        style_context = self.control_box.get_style_context()
        style_context.add_provider(
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_calibration_toggled(self, button):
        """Переключение режима калибровки"""
        self.calibration_mode = button.get_active()
        self.calibration_result = None

        # Обновляем стиль кнопки
        if self.calibration_mode:
            button.get_style_context().add_class("calibration-active")
            # Фиксируем масштаб на 225
            self.scale_combo.set_active(MAP_SCALES.index(225))
            self.scale_combo.set_sensitive(False)
            self.distance_label.set_text("Метров на пиксель:")
            self.distance_value.set_text("0.00")
        else:
            button.get_style_context().remove_class("calibration-active")
            self.scale_combo.set_sensitive(True)
            self.distance_label.set_text("Дистанция:")
            self.distance_value.set_text("0.00 м")

        # Сбрасываем точки при переключении режима
        self.reset_points()
        self.queue_draw()

    def on_top_toggled(self, button):
        self.set_keep_above(button.get_active())
        if self.get_realized():
            self.on_realize(None)

    def on_scale_changed(self, combo):
        scale_str = combo.get_active_text()
        if scale_str:
            try:
                self.selected_scale = int(scale_str)
                self.recalculate_scale()
                self.save_config()
                # Обновляем отображение при изменении масштаба
                self.queue_draw()
            except ValueError:
                pass

    def draw_cross(self, cr, x, y, color, size=10, width=2):
        """Рисует крестик в указанных координатах"""
        cr.set_source_rgba(*color)
        cr.set_line_width(width)

        # Горизонтальная линия
        cr.move_to(x - size, y)
        cr.line_to(x + size, y)
        cr.stroke()

        # Вертикальная линия
        cr.move_to(x, y - size)
        cr.line_to(x, y + size)
        cr.stroke()

    def calculate_meters_per_pixel(self, pixels):
        """Рассчитывает метров на пиксель для калибровки"""
        if pixels <= 0:
            return 0
        return BASE_SCALE_VALUE / pixels

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        # Рисуем фон
        cr.set_source_rgba(0.2, 0.2, 0.2, 0.6)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # Рисуем линии и точки
        if self.start_point:
            # Начальная точка - зеленый крестик
            self.draw_cross(cr, self.start_point.x, self.start_point.y, (0, 1, 0, 1))

            # Линия к текущему положению мыши или конечной точке
            if self.end_point:
                target_point = self.end_point
            elif self.temp_point:
                target_point = self.temp_point
            else:
                return

            # Конечная точка - красный крестик
            if self.end_point:
                self.draw_cross(cr, target_point.x, target_point.y, (1, 0, 0, 1))

            # Линия между точками
            cr.set_source_rgba(1, 1, 1, 1)
            cr.set_line_width(2)
            cr.move_to(self.start_point.x, self.start_point.y)
            cr.line_to(target_point.x, target_point.y)

            # Для временной линии рисуем пунктир
            if not self.end_point:
                cr.set_dash([5, 3], 0)
                cr.stroke()
                cr.set_dash([], 0)
            else:
                cr.stroke()

            # Выводим расстояние на линию
            if self.start_point and target_point:
                dx = target_point.x - self.start_point.x
                dy = target_point.y - self.start_point.y
                pixels = math.sqrt(dx**2 + dy**2)

                if self.calibration_mode:
                    # В режиме калибровки показываем метры на пиксель
                    if self.end_point:
                        # После установки второй точки показываем результат
                        meters_per_pixel = self.calculate_meters_per_pixel(pixels)
                        self.calibration_result = meters_per_pixel
                        display_text = f"{meters_per_pixel:.6f} м/пикс"
                    else:
                        # При перемещении мыши показываем пиксели
                        display_text = f"{pixels:.1f} пикс"
                else:
                    # В обычном режиме показываем расстояние в метрах
                    meters = pixels * self.scale_factor
                    display_text = f"{meters:.1f} м"

                cr.set_font_size(24)
                cr.set_source_rgba(1, 1, 1, 1)

                # Позиция текста - выше линии
                text_x = (self.start_point.x + target_point.x) / 2
                text_y = (self.start_point.y + target_point.y) / 2 - 40

                cr.move_to(text_x, text_y)
                cr.show_text(display_text)

        # Информация для пользователя в режиме калибровки
        if self.calibration_mode and not self.end_point:
            cr.set_font_size(16)
            cr.set_source_rgba(1, 1, 1, 0.8)
            cr.move_to(10, height - 30)
            cr.show_text("Измерьте расстояние 225 м между двумя точками")

    def on_button_press(self, widget, event):
        # Правый клик - начальная точка
        if event.button == 3:
            self.start_point = Gdk.EventButton()
            self.start_point.x = event.x
            self.start_point.y = event.y
            self.end_point = None
            self.queue_draw()

        # Левый клик - конечная точка
        elif event.button == 1 and self.start_point:
            self.end_point = Gdk.EventButton()
            self.end_point.x = event.x
            self.end_point.y = event.y

            self.update_distance_display()
            self.queue_draw()

    def update_distance_display(self):
        if self.start_point and self.end_point:
            dx = self.end_point.x - self.start_point.x
            dy = self.end_point.y - self.start_point.y
            pixels = math.sqrt(dx**2 + dy**2)

            if self.calibration_mode:
                meters_per_pixel = self.calculate_meters_per_pixel(pixels)
                self.calibration_result = meters_per_pixel
                self.distance_value.set_text(f"{meters_per_pixel:.6f}")
            else:
                meters = pixels * self.scale_factor
                self.distance_value.set_text(f"{meters:.1f} м")

    def on_mouse_move(self, widget, event):
        if self.start_point and not self.end_point:
            self.temp_point = Gdk.EventButton()
            self.temp_point.x = event.x
            self.temp_point.y = event.y

            self.queue_draw()

    def on_key_press(self, widget, event):
        keyval = event.keyval
        if keyval == Gdk.KEY_Escape:  # Выход по [Esc]
            self.destroy()
        elif keyval == Gdk.KEY_r:  # Сброс точек
            self.reset_points()
        elif keyval == Gdk.KEY_t:  # Переключение поверх окон
            self.top_btn.set_active(not self.top_btn.get_active())
        elif keyval == Gdk.KEY_h:  # Переключение горизонтального режима
            self.horizontal_only = not self.horizontal_only
            self.queue_draw()
        elif keyval == Gdk.KEY_c:  # Переключение режима калибровки
            self.calibration_btn.set_active(not self.calibration_btn.get_active())
        elif keyval == Gdk.KEY_y:  # Горячая клавиша для YouTube
            webbrowser.open("https://www.youtube.com/@EXTRUD/shorts")
        return False

    def reset_points(self):
        self.start_point = None
        self.end_point = None
        self.temp_point = None
        self.calibration_result = None

        if self.calibration_mode:
            self.distance_value.set_text("0.00")
        else:
            self.distance_value.set_text("0.00 м")

        self.queue_draw()

win = MapRuler()
win.show_all()
Gtk.main()
