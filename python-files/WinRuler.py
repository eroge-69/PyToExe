#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GObject, GLib
import math
import cairo
import os
import configparser
import webbrowser

# Базовый масштаб (метров на пиксель) для масштаба 225
BASE_SCALE_225 = 3.722132
BASE_SCALE_VALUE = 225

# Список масштабов карт
MAP_SCALES = [150, 170, 180, 190, 200, 225, 250, 275, 300, 325, 400, 450, 500, 550]

class MapRuler(Gtk.Window):
    def __init__(self):
        super().__init__(title="Дальномер для War Thunder")
        self.set_default_size(500, 480)
        self.set_app_paintable(True)
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)
        self.set_decorated(False)

        # Совместимость с Windows
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.set_position(Gtk.WindowPosition.CENTER)

        # Настройки
        self.selected_scale = BASE_SCALE_VALUE
        self.scale_factor = BASE_SCALE_225
        self.start_point = None
        self.end_point = None
        self.temp_point = None
        self.horizontal_only = False
        self.calibration_mode = False
        self.calibration_result = None

        # Загрузка конфига
        self.config_file = os.path.expanduser("~/.wt_map_ruler.ini")
        self.load_config()
        self.recalculate_scale()

        # Основной контейнер
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.add(self.box)

        # Панель управления
        self.create_control_panel()

        # Обработчики событий
        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_button_press)
        self.connect("motion-notify-event", self.on_mouse_move)
        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", self.on_destroy)
        self.connect("realize", self.on_realize)

        self.set_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self.set_opacity(0.85)

    def on_realize(self, widget):
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
                scale = config.getint('DEFAULT', 'selected_scale', fallback=BASE_SCALE_VALUE)
                self.selected_scale = scale if scale in MAP_SCALES else BASE_SCALE_VALUE
            except Exception as e:
                print(f"Ошибка конфига: {e}")

    def save_config(self):
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'selected_scale': str(self.selected_scale)}
        with open(self.config_file, 'w') as configfile:
            config.write(configfile)

    def recalculate_scale(self):
        self.scale_factor = BASE_SCALE_225 * (self.selected_scale / BASE_SCALE_VALUE)
        if hasattr(self, 'scale_value'):
            self.scale_value.set_text(f"{self.scale_factor:.6f} м/пикс")
        if hasattr(self, 'distance_value') and self.start_point and self.end_point:
            self.update_distance_display()

    def on_destroy(self, widget):
        self.save_config()
        Gtk.main_quit()

    def create_control_panel(self):
        self.control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.control_box.set_margin_start(5)
        self.control_box.set_margin_end(5)
        self.control_box.set_margin_top(5)
        self.box.pack_start(self.control_box, False, False, 0)

        # Кнопка калибровки
        self.calibration_btn = Gtk.ToggleButton(label="Калибровка")
        self.calibration_btn.set_tooltip_text("Режим калибровки (измерение метров на пиксель)")
        self.calibration_btn.connect("toggled", self.on_calibration_toggled)
        self.control_box.pack_start(self.calibration_btn, False, False, 0)

        # Выбор масштаба карты
        self.control_box.pack_start(Gtk.Label(label="Масштаб карты:"), False, False, 0)

        self.scale_combo = Gtk.ComboBoxText()
        for scale in MAP_SCALES:
            self.scale_combo.append_text(str(scale))
        self.scale_combo.set_active(MAP_SCALES.index(self.selected_scale))
        self.scale_combo.connect("changed", self.on_scale_changed)
        self.control_box.pack_start(self.scale_combo, False, False, 0)

        # Текущий масштаб
        self.control_box.pack_start(Gtk.Label(label="Текущий масштаб:"), False, False, 0)

        self.scale_value = Gtk.Label(label=f"{self.scale_factor:.6f} м/пикс")
        self.scale_value.get_style_context().add_class("scale-value")
        self.control_box.pack_start(self.scale_value, False, False, 0)

        # Дистанция
        self.control_box.pack_start(Gtk.Label(label="Дистанция:"), False, False, 0)

        self.distance_value = Gtk.Label(label="0.00 м")
        self.distance_value.get_style_context().add_class("distance-value")
        self.control_box.pack_start(self.distance_value, False, False, 0)

        # Кнопки
        self.reset_btn = Gtk.Button(label="↺")
        self.reset_btn.get_style_context().add_class("reset-btn")
        self.reset_btn.connect("clicked", self.reset_points)
        self.reset_btn.set_tooltip_text("Сбросить точки (R)")
        self.control_box.pack_end(self.reset_btn, False, False, 0)

        self.youtube_btn = Gtk.Button(label="Y")
        self.youtube_btn.get_style_context().add_class("youtube-btn")
        self.youtube_btn.connect("clicked", lambda w: webbrowser.open("https://www.youtube.com/@EXTRUD/shorts"))
        self.youtube_btn.set_tooltip_text("YouTube канал EXTRUD")
        self.control_box.pack_end(self.youtube_btn, False, False, 0)

        self.top_btn = Gtk.ToggleButton(label="🔝")
        self.top_btn.set_active(True)
        self.top_btn.connect("toggled", self.on_top_toggled)
        self.top_btn.set_tooltip_text("Всегда поверх окон")
        self.control_box.pack_end(self.top_btn, False, False, 0)

        # CSS стили
        css_provider = Gtk.CssProvider()
        css = b"""
        * {
            font-family: 'Sans';
            font-size: 10pt;
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
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def on_calibration_toggled(self, button):
        self.calibration_mode = button.get_active()
        self.calibration_result = None

        if self.calibration_mode:
            button.get_style_context().add_class("calibration-active")
            self.scale_combo.set_active(MAP_SCALES.index(225))
            self.scale_combo.set_sensitive(False)
            self.distance_label.set_text("Метров на пиксель:")
            self.distance_value.set_text("0.00")
        else:
            button.get_style_context().remove_class("calibration-active")
            self.scale_combo.set_sensitive(True)
            self.distance_label.set_text("Дистанция:")
            self.distance_value.set_text("0.00 м")

        self.reset_points()

    def on_top_toggled(self, button):
        self.set_keep_above(button.get_active())
        if self.get_realized():
            self.on_realize(None)

    def on_scale_changed(self, combo):
        if scale_str := combo.get_active_text():
            try:
                self.selected_scale = int(scale_str)
                self.recalculate_scale()
                self.save_config()
                self.queue_draw()
            except ValueError:
                pass

    def draw_cross(self, cr, x, y, color, size=10, width=2):
        cr.set_source_rgba(*color)
        cr.set_line_width(width)
        cr.move_to(x - size, y)
        cr.line_to(x + size, y)
        cr.stroke()
        cr.move_to(x, y - size)
        cr.line_to(x, y + size)
        cr.stroke()

    def calculate_meters_per_pixel(self, pixels):
        return BASE_SCALE_VALUE / pixels if pixels > 0 else 0

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        # Фон
        cr.set_source_rgba(0.2, 0.2, 0.2, 0.6)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        if self.start_point:
            self.draw_cross(cr, self.start_point.x, self.start_point.y, (0, 1, 0, 1))

            if self.end_point:
                target_point = self.end_point
            elif self.temp_point:
                target_point = self.temp_point
            else:
                return

            if self.end_point:
                self.draw_cross(cr, target_point.x, target_point.y, (1, 0, 0, 1))

            cr.set_source_rgba(1, 1, 1, 1)
            cr.set_line_width(2)
            cr.move_to(self.start_point.x, self.start_point.y)
            cr.line_to(target_point.x, target_point.y)

            if not self.end_point:
                cr.set_dash([5, 3], 0)
                cr.stroke()
                cr.set_dash([], 0)
            else:
                cr.stroke()

            if self.start_point and target_point:
                dx = target_point.x - self.start_point.x
                dy = target_point.y - self.start_point.y
                pixels = math.sqrt(dx**2 + dy**2)

                if self.calibration_mode:
                    if self.end_point:
                        meters_per_pixel = self.calculate_meters_per_pixel(pixels)
                        self.calibration_result = meters_per_pixel
                        display_text = f"{meters_per_pixel:.6f} м/пикс"
                    else:
                        display_text = f"{pixels:.1f} пикс"
                else:
                    meters = pixels * self.scale_factor
                    display_text = f"{meters:.1f} м"

                cr.set_font_size(24)
                cr.set_source_rgba(1, 1, 1, 1)
                text_x = (self.start_point.x + target_point.x) / 2
                text_y = (self.start_point.y + target_point.y) / 2 - 40
                cr.move_to(text_x, text_y)
                cr.show_text(display_text)

        if self.calibration_mode and not self.end_point:
            cr.set_font_size(16)
            cr.set_source_rgba(1, 1, 1, 0.8)
            cr.move_to(10, height - 30)
            cr.show_text("Измерьте расстояние 225 м между двумя точками")

    def on_button_press(self, widget, event):
        if event.button == 3:  # Правая кнопка
            self.start_point = Gdk.EventButton()
            self.start_point.x, self.start_point.y = event.x, event.y
            self.end_point = None
            self.queue_draw()

        elif event.button == 1 and self.start_point:  # Левая кнопка
            self.end_point = Gdk.EventButton()
            self.end_point.x, self.end_point.y = event.x, event.y
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
            self.temp_point.x, self.temp_point.y = event.x, event.y
            self.queue_draw()

    def on_key_press(self, widget, event):
        keyval = event.keyval
        if keyval == Gdk.KEY_Escape:
            self.destroy()
        elif keyval == Gdk.KEY_r:
            self.reset_points()
        elif keyval == Gdk.KEY_t:
            self.top_btn.set_active(not self.top_btn.get_active())
        elif keyval == Gdk.KEY_h:
            self.horizontal_only = not self.horizontal_only
            self.queue_draw()
        elif keyval == Gdk.KEY_c:
            self.calibration_btn.set_active(not self.calibration_btn.get_active())
        elif keyval == Gdk.KEY_y:
            webbrowser.open("https://www.youtube.com/@EXTRUD/shorts")
        return False

    def reset_points(self):
        self.start_point = self.end_point = self.temp_point = None
        self.calibration_result = None
        self.distance_value.set_text("0.00" if self.calibration_mode else "0.00 м")
        self.queue_draw()

if __name__ == "__main__":
    win = MapRuler()
    win.show_all()
    Gtk.main()
