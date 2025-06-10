from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
import math

# Настройки цветовой схемы
PRIMARY_COLOR = get_color_from_hex('#4a6fa5')
SECONDARY_COLOR = get_color_from_hex('#166088')
ACCENT_COLOR = get_color_from_hex('#4fc3f7')
BACKGROUND_COLOR = get_color_from_hex('#f0f4f8')
TEXT_COLOR = get_color_from_hex('#333333')

# Адаптивный размер окна
Window.size = (dp(800), dp(600))
Window.minimum_width = dp(300)
Window.minimum_height = dp(500)


class StyledButton(Button):
    """Стилизованная кнопка с адаптивным размером текста"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = PRIMARY_COLOR
        self.color = (1, 1, 1, 1)
        self.font_size = sp(16)
        self.size_hint_y = None
        self.height = dp(50)
        self.border_radius = dp(10)
        self.background_normal = ''
        self.background_down = ''
        self.bind(
            width=lambda *x: self.setter('text_size')(self, (self.width, None)),
            texture_size=lambda *x: self.setter('height')(self, max(self.texture_size[1] + dp(20), dp(50)))
        )


class StyledTextInput(TextInput):
    """Стилизованное поле ввода"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (1, 1, 1, 1)
        self.foreground_color = TEXT_COLOR
        self.font_size = sp(16)
        self.size_hint_y = None
        self.height = dp(45)
        self.multiline = False
        self.padding = [dp(10), dp(10)]
        self.background_normal = ''
        self.background_active = ''
        self.background_disabled = ''


class StyledLabel(Label):
    """Стилизованная метка"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = TEXT_COLOR
        self.font_size = sp(16)
        self.size_hint_y = None
        self.height = dp(40)
        self.halign = 'center'
        self.valign = 'middle'


class HeaderLabel(Label):
    """Заголовок раздела"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = SECONDARY_COLOR
        self.font_size = sp(20)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(60)
        self.halign = 'center'
        self.valign = 'middle'


class NumericalMethodsApp(App):
    def build(self):
        self.title = "Численные методы для повседневных задач"
        Window.clearcolor = BACKGROUND_COLOR

        tabs = TabbedPanel(do_default_tab=False)
        tabs.background_color = SECONDARY_COLOR
        tabs.tab_width = dp(150)
        tabs.border = [0, 0, 0, 0]

        # 1. Расчет времени остывания чая
        tab1 = self.create_tab_tea_cooling()
        tabs.add_widget(TabbedPanelItem(text='Остывание чая', content=tab1))

        # 2. Расчет площади комнаты для покраски
        tab2 = self.create_tab_wall_area()
        tabs.add_widget(TabbedPanelItem(text='Покраска стен', content=tab2))

        # 3. Расчет периода колебаний пружинного маятника
        tab3 = self.create_tab_spring_pendulum()
        tabs.add_widget(TabbedPanelItem(text='Пружинный маятник', content=tab3))

        # 4. Расчет максимальной высоты подъема мяча
        tab4 = self.create_tab_ball_height()
        tabs.add_widget(TabbedPanelItem(text='Полёт мяча', content=tab4))

        return tabs

    def create_tab_tea_cooling(self):
        tab = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        tab.add_widget(HeaderLabel(text='Расчет времени остывания чая\nдо комфортной температуры'))

        self.tea_initial_temp = StyledTextInput(hint_text='Начальная температура чая (°C)')
        tab.add_widget(self.tea_initial_temp)

        self.tea_target_temp = StyledTextInput(hint_text='Желаемая температура (°C)')
        tab.add_widget(self.tea_target_temp)

        self.room_temp = StyledTextInput(hint_text='Температура комнаты (°C)')
        tab.add_widget(self.room_temp)

        btn = StyledButton(text='Рассчитать время')
        btn.bind(on_press=self.calculate_tea_cooling)
        tab.add_widget(btn)

        self.tea_result = StyledLabel(text='Результат:')
        tab.add_widget(self.tea_result)

        return tab

    def create_tab_wall_area(self):
        tab = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        tab.add_widget(HeaderLabel(text='Расчет площади стены\nсложной формы для покраски'))

        self.wall_height = StyledTextInput(hint_text='Высота стены (м)')
        tab.add_widget(self.wall_height)

        self.wall_width = StyledTextInput(hint_text='Ширина стены (м)')
        tab.add_widget(self.wall_width)

        self.wall_shape = StyledTextInput(
            hint_text='Форма стены (функция от x), например: 0.2*math.sin(x/2)')
        tab.add_widget(self.wall_shape)

        btn = StyledButton(text='Рассчитать площадь')
        btn.bind(on_press=self.calculate_wall_area)
        tab.add_widget(btn)

        self.wall_result = StyledLabel(text='Результат:')
        tab.add_widget(self.wall_result)

        return tab

    def create_tab_spring_pendulum(self):
        tab = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        tab.add_widget(HeaderLabel(text='Расчет периода колебаний\nпружинного маятника'))

        self.mass = StyledTextInput(hint_text='Масса груза (кг)')
        tab.add_widget(self.mass)

        self.spring_constant = StyledTextInput(hint_text='Жёсткость пружины (Н/м)')
        tab.add_widget(self.spring_constant)

        btn = StyledButton(text='Рассчитать период')
        btn.bind(on_press=self.calculate_period)
        tab.add_widget(btn)

        self.pendulum_result = StyledLabel(text='Результат:')
        tab.add_widget(self.pendulum_result)

        return tab

    def create_tab_ball_height(self):
        tab = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        tab.add_widget(HeaderLabel(text='Расчет максимальной высоты\nподъема мяча'))

        self.ball_speed = StyledTextInput(hint_text='Начальная скорость (м/с)')
        tab.add_widget(self.ball_speed)

        self.ball_angle = StyledTextInput(hint_text='Угол броска (градусы)')
        tab.add_widget(self.ball_angle)

        btn = StyledButton(text='Рассчитать высоту')
        btn.bind(on_press=self.calculate_ball_height)
        tab.add_widget(btn)

        self.ball_result = StyledLabel(text='Результат:')
        tab.add_widget(self.ball_result)

        return tab

    def show_error(self, message):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(StyledLabel(text=message))

        close_btn = StyledButton(text='Закрыть')
        popup = Popup(title='Ошибка',
                      content=content,
                      size_hint=(0.8, 0.4),
                      separator_color=PRIMARY_COLOR,
                      title_color=TEXT_COLOR,
                      title_size=sp(18))

        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    # Методы расчетов остаются без изменений (calculate_tea_cooling, calculate_wall_area,
    # calculate_period, calculate_ball_height) - они такие же, как в предыдущей версии

    def calculate_tea_cooling(self, instance):
        """Решение дифференциального уравнения остывания по закону Ньютона"""
        try:
            T0 = float(self.tea_initial_temp.text)
            T_target = float(self.tea_target_temp.text)
            T_env = float(self.room_temp.text)

            if T0 <= T_env:
                raise ValueError("Начальная температура должна быть выше комнатной")
            if T_target <= T_env:
                raise ValueError("Желаемая температура должна быть выше комнатной")

            k = 0.1  # Коэффициент остывания

            dt = 0.1  # шаг по времени (мин)
            time = 0
            T = T0

            while T > T_target:
                dT = -k * (T - T_env) * dt
                T += dT
                time += dt

            self.tea_result.text = f'Время остывания: {time:.1f} минут'
        except Exception as e:
            self.show_error(f'Ошибка: {str(e)}')

    def calculate_wall_area(self, instance):
        """Вычисление площади стены сложной формы методом трапеций"""
        try:
            height = float(self.wall_height.text)
            width = float(self.wall_width.text)
            shape_func = self.wall_shape.text

            if not shape_func:
                shape_func = "0"  # если форма не указана - плоская стена

            def f(x):
                return eval(shape_func)

            n = 100  # количество отрезков разбиения
            dx = width / n
            area = 0

            for i in range(n):
                x1 = i * dx
                x2 = (i + 1) * dx
                y1 = height + f(x1)
                y2 = height + f(x2)
                area += (y1 + y2) * dx / 2

            self.wall_result.text = f'Площадь стены: {area:.2f} м²'
        except Exception as e:
            self.show_error(f'Ошибка: {str(e)}')

    def calculate_period(self, instance):
        """Расчет периода колебаний пружинного маятника по гармоническому закону"""
        try:
            m = float(self.mass.text)
            k = float(self.spring_constant.text)

            if m <= 0:
                raise ValueError("Масса должна быть положительной")
            if k <= 0:
                raise ValueError("Жёсткость пружины должна быть положительной")

            # Расчет периода по формуле T = 2π√(m/k)
            period = 2 * math.pi * math.sqrt(m / k)

            # Расчет частоты колебаний
            frequency = 1 / period

            self.pendulum_result.text = f'Период колебаний: {period:.2f} с\nЧастота: {frequency:.2f} Гц'
        except Exception as e:
            self.show_error(f'Ошибка: {str(e)}')

    def calculate_ball_height(self, instance):
        """Расчет максимальной высоты подъема мяча с использованием производной"""
        try:
            v0 = float(self.ball_speed.text)
            angle = float(self.ball_angle.text)

            if v0 <= 0:
                raise ValueError("Скорость должна быть положительной")
            if angle <= 0 or angle >= 90:
                raise ValueError("Угол должен быть между 0 и 90 градусами")

            g = 9.81
            angle_rad = math.radians(angle)

            # Вертикальная компонента скорости
            vy0 = v0 * math.sin(angle_rad)

            # Время подъема (когда вертикальная скорость становится 0)
            t_max = vy0 / g

            # Функция высоты от времени
            def height(t):
                return vy0 * t - 0.5 * g * t ** 2

            # Максимальная высота
            h_max = height(t_max)

            self.ball_result.text = f'Максимальная высота: {h_max:.2f} м\nВремя подъёма: {t_max:.2f} с'
        except Exception as e:
            self.show_error(f'Ошибка: {str(e)}')


if __name__ == '__main__':
    NumericalMethodsApp().run()