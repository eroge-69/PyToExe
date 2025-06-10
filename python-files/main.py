import os
import requests
import json
import time
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, RoundedRectangle, Rectangle, InstructionGroup
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import StringProperty, BooleanProperty

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

class SettingsPopup(Popup):
    def __init__(self, main_app, **kwargs):
        super(SettingsPopup, self).__init__(**kwargs)
        self.main_app = main_app
        self.title = 'Настройки PythonAnywhere'
        self.size_hint = (0.9, 0.8)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Токен API
        layout.add_widget(Label(text='API Токен:', size_hint_y=None, height=30))
        self.token_input = TextInput(text=main_app.settings['api_token'], multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.token_input)
        
        # Логин PythonAnywhere
        layout.add_widget(Label(text='Логин PythonAnywhere:', size_hint_y=None, height=30))
        self.username_input = TextInput(text=main_app.settings['pa_username'], multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.username_input)
        
        # Номер консоли
        layout.add_widget(Label(text='Номер консоли:', size_hint_y=None, height=30))
        self.console_num_input = TextInput(text=str(main_app.settings['console_num']), multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.console_num_input)
        
        # Нужен ли cd
        layout.add_widget(Label(text='Использовать cd:', size_hint_y=None, height=30))
        self.cd_toggle = ToggleButton(text='Да' if main_app.settings['use_cd'] else 'Нет', state='down' if main_app.settings['use_cd'] else 'normal', size_hint_y=None, height=40)
        self.cd_toggle.bind(on_press=self.toggle_cd)
        layout.add_widget(self.cd_toggle)
        
        # Директория для cd
        layout.add_widget(Label(text='Директория для cd:', size_hint_y=None, height=30))
        self.cd_dir_input = TextInput(text=main_app.settings['cd_dir'], multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.cd_dir_input)
        
        # Имя файла для запуска
        layout.add_widget(Label(text='Имя файла для запуска:', size_hint_y=None, height=30))
        self.script_name_input = TextInput(text=main_app.settings['script_name'], multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.script_name_input)
        
        # Кнопки сохранить/отмена
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_cancel = RoundedButton(text='Отмена')
        btn_cancel.bind(on_press=self.dismiss)
        btn_save = RoundedButton(text='Сохранить')
        btn_save.bind(on_press=self.save_settings)
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_save)
        layout.add_widget(btn_layout)
        
        self.content = layout
    
    def toggle_cd(self, instance):
        instance.text = 'Да' if instance.state == 'down' else 'Нет'
    
    def save_settings(self, instance):
        self.main_app.settings = {
            'api_token': self.token_input.text,
            'pa_username': self.username_input.text,
            'console_num': int(self.console_num_input.text),
            'use_cd': self.cd_toggle.state == 'down',
            'cd_dir': self.cd_dir_input.text,
            'script_name': self.script_name_input.text
        }
        self.main_app.save_settings()
        self.dismiss()

class RobloxApp(App):
    bot_status = StringProperty("выключен")
    bot_running = BooleanProperty(False)
    
    def build(self):
        self.settings = {
            'api_token': '8512dae7ee24aa6b9eff2b23c612992b61eca068',
            'pa_username': 'Gptbot1',
            'console_num': 39909590,
            'use_cd': True,
            'cd_dir': 'bot',
            'script_name': 'scam.py'
        }
        self.load_settings()
        
        self.bot_status = "выключен"
        self.bot_running = False
        
        # Основной layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        main_layout.bind(size=self._update_rect)
        
        with main_layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)  # Темно-серый фон
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        # Верхняя часть с заголовком и картинкой
        top_layout = BoxLayout(size_hint_y=None, height=100, spacing=10)
        
        # Тексты слева
        text_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        title = Label(text='бесплатные роблоксы🤑', 
                    color=(1, 1, 1, 1), 
                    font_size='20sp', 
                    size_hint_y=0.6, 
                    halign='left', 
                    valign='middle',
                    bold=True)
        title.bind(size=title.setter('text_size'))
        subtitle = Label(text='@Freetobloq_bot', 
                        color=(0.7, 0.7, 0.7, 1), 
                        font_size='16sp', 
                        size_hint_y=0.4, 
                        halign='left', 
                        valign='top',
                        bold=True)
        subtitle.bind(size=subtitle.setter('text_size'))
        text_layout.add_widget(title)
        text_layout.add_widget(subtitle)
        top_layout.add_widget(text_layout)
        
        # Картинка справа с закругленными углами
        img_container = BoxLayout(size_hint_x=0.3)
        with img_container.canvas.before:
            Color(1, 1, 1, 1)
            self.img_rect = RoundedRectangle(radius=[10])
        img = AsyncImage(source='https://s.iimg.su/s/09/XwZ3cyiNJRXcoz20fSKcURBZ4WFwB370S7gROT98.png', 
                        keep_ratio=True, 
                        allow_stretch=True)
        img_container.add_widget(img)
        img_container.bind(pos=self._update_img_rect, size=self._update_img_rect)
        top_layout.add_widget(img_container)
        main_layout.add_widget(top_layout)
        
        # Статус бота в одной строке
        status_layout = BoxLayout(size_hint_y=None, height=40, spacing=0)
        status_label = Label(text='статус бота: ', 
                           color=(1, 1, 1, 1), 
                           font_size='18sp', 
                           size_hint_x=None, 
                           width=120, 
                           halign='left',
                           bold=True)
        status_label.bind(size=status_label.setter('text_size'))
        
        self.status_value = Label(text=self.bot_status, 
                                color=self.get_status_color(), 
                                font_size='18sp', 
                                halign='left',
                                bold=True)
        self.status_value.bind(size=self.status_value.setter('text_size'))
        
        status_layout.add_widget(status_label)
        status_layout.add_widget(self.status_value)
        main_layout.add_widget(status_layout)
        
        # Данные для входа
        creds_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=60, spacing=5)
        login_label = Label(text='|— логин: [ref=login]Gptbot1[/ref]', 
                          color=(0.7, 0.7, 0.7, 1), 
                          font_size='16sp', 
                          markup=True, 
                          halign='left',
                          bold=True)
        login_label.bind(on_ref_press=self.copy_text, size=login_label.setter('text_size'))
        
        password_label = Label(text='|— пароль: [ref=pass]Banan213[/ref]', 
                             color=(0.7, 0.7, 0.7, 1), 
                             font_size='16sp', 
                             markup=True, 
                             halign='left',
                             bold=True)
        password_label.bind(on_ref_press=self.copy_text, size=password_label.setter('text_size'))
        
        creds_layout.add_widget(login_label)
        creds_layout.add_widget(password_label)
        main_layout.add_widget(creds_layout)
        
        # Кнопки управления
        btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.toggle_btn = RoundedButton(text='включить' if not self.bot_running else 'выключить')
        self.toggle_btn.background_color = self.get_button_color()
        self.toggle_btn.bind(on_press=self.toggle_bot)
        
        settings_btn = RoundedButton(text='настройки')
        settings_btn.background_color = get_color_from_hex('#1E90FF')
        settings_btn.bind(on_press=self.show_settings)
        
        btn_layout.add_widget(self.toggle_btn)
        btn_layout.add_widget(settings_btn)
        main_layout.add_widget(btn_layout)
        
        # Лог-панель
        log_panel = BoxLayout(orientation='vertical', size_hint_y=0.3)
        with log_panel.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.log_rect = RoundedRectangle(size=log_panel.size, pos=log_panel.pos, radius=[10])
        
        log_panel.bind(size=self._update_log_rect, pos=self._update_log_rect)
        
        self.log_label = Label(text='Лог событий:', 
                             color=(1, 1, 1, 1), 
                             font_size='14sp', 
                             size_hint_y=None, 
                             height=30, 
                             halign='left', 
                             valign='top',
                             bold=True)
        self.log_label.bind(size=self.log_label.setter('text_size'))
        
        self.log_content = Label(text='', 
                               color=(0.9, 0.9, 0.9, 1), 
                               font_size='12sp', 
                               halign='left', 
                               valign='top')
        self.log_content.bind(size=self.log_content.setter('text_size'))
        
        log_panel.add_widget(self.log_label)
        log_panel.add_widget(self.log_content)
        main_layout.add_widget(log_panel)
        
        return main_layout
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def _update_log_rect(self, instance, value):
        self.log_rect.pos = instance.pos
        self.log_rect.size = instance.size
    
    def _update_img_rect(self, instance, value):
        self.img_rect.pos = instance.pos
        self.img_rect.size = instance.size
    
    def load_settings(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)
    
    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)
    
    def get_status_color(self):
        if self.bot_status == "запущен":
            return (0, 1, 0, 1)  # Зеленый
        elif self.bot_status == "выключен":
            return (1, 0, 0, 1)  # Красный
        else:
            return (1, 0.8, 0, 1)  # Желто-оранжевый
    
    def get_button_color(self):
        if self.bot_status == "запущен":
            return (1, 0, 0, 1)  # Красный
        else:
            return (0, 1, 0, 1)  # Зеленый
    
    def copy_text(self, instance, value):
        original_text = instance.text
        try:
            text_to_copy = original_text.split(']')[1].split('[')[0]
            Clipboard.copy(text_to_copy)
            
            if "логин" in original_text:
                instance.text = '|— логин: текст скопирован!'
            else:
                instance.text = '|— пароль: текст скопирован!'
            
            Clock.schedule_once(lambda dt: setattr(instance, 'text', original_text), 1.5)
            self.add_log("Текст скопирован в буфер обмена")
        except Exception as e:
            self.add_log(f"Ошибка копирования: {str(e)}")
    
    def add_log(self, message):
        current_time = time.strftime("%H:%M:%S", time.localtime())
        log_entry = f"[{current_time}] {message}\n"
        self.log_content.text = log_entry + self.log_content.text
    
    def show_settings(self, instance):
        SettingsPopup(self).open()
    
    def toggle_bot(self, instance):
        if self.bot_running:
            self.show_confirmation_popup()
        else:
            self.start_bot()
    
    def show_confirmation_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text='Бот будет выключен'))
        
        btn_layout = BoxLayout(spacing=10)
        btn_cancel = RoundedButton(text='Отмена')
        btn_confirm = RoundedButton(text='Выключить')
        
        popup = Popup(title='Подтверждение', content=content, size_hint=(0.8, 0.4))
        
        btn_cancel.bind(on_press=popup.dismiss)
        btn_confirm.bind(on_press=lambda x: [popup.dismiss(), self.stop_bot()])
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_confirm)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def start_bot(self):
        self.toggle_btn.text = 'включение...'
        self.toggle_btn.background_color = (0.5, 0.5, 0.5, 1)  # Серый
        self.bot_status = "запуск..."
        self.animate_status_change()
        self.add_log("Попытка запуска бота...")
        
        threading.Thread(target=self._start_bot_thread).start()
    
    def animate_status_change(self):
        anim = Animation(opacity=0, duration=0.2) + Animation(opacity=1, duration=0.2)
        anim.start(self.status_value)
    
    def _start_bot_thread(self):
        time.sleep(2)
        
        try:
            base_url = f"https://www.pythonanywhere.com/api/v0/user/{self.settings['pa_username']}/consoles/{self.settings['console_num']}/"
            headers = {'Authorization': f'Token {self.settings["api_token"]}'}
            
            response = requests.get(f"{base_url}get_latest_output/", headers=headers)
            
            if response.status_code == 404:
                response = requests.post(f"https://www.pythonanywhere.com/api/v0/user/{self.settings['pa_username']}/consoles/", 
                                       headers=headers,
                                       data={'executable': 'bash'})
                if response.status_code == 201:
                    console_num = response.json()['id']
                    self.settings['console_num'] = console_num
                    self.save_settings()
                    base_url = f"https://www.pythonanywhere.com/api/v0/user/{self.settings['pa_username']}/consoles/{console_num}/"
                    self.add_log(f"Создана новая консоль: {console_num}")
            
            commands = []
            if self.settings['use_cd']:
                commands.append(f"cd {self.settings['cd_dir']}")
            commands.append(f"python {self.settings['script_name']}")
            
            for cmd in commands:
                response = requests.post(f"{base_url}send_input/", 
                                       headers=headers,
                                       data={'input': cmd + '\n'})
                
                if response.status_code != 200:
                    raise Exception(f"Ошибка отправки команды: {response.text}")
                self.add_log(f"Отправлена команда: {cmd}")
            
            Clock.schedule_once(lambda dt: self._update_ui_after_start(True))
            self.add_log("Бот успешно запущен")
        
        except Exception as e:
            print(f"Ошибка: {str(e)}")
            self.add_log(f"Ошибка запуска: {str(e)}")
            Clock.schedule_once(lambda dt: self._update_ui_after_start(False))
    
    def _update_ui_after_start(self, success):
        if success:
            self.bot_status = "запущен"
            self.bot_running = True
            self.toggle_btn.text = 'выключить'
            self.toggle_btn.background_color = self.get_button_color()
        else:
            self.bot_status = "выключен"
            self.bot_running = False
            self.toggle_btn.text = 'включить'
            self.toggle_btn.background_color = self.get_button_color()
        
        self.status_value.text = self.bot_status
        self.status_value.color = self.get_status_color()
        self.animate_status_change()
    
    def stop_bot(self):
        try:
            base_url = f"https://www.pythonanywhere.com/api/v0/user/{self.settings['pa_username']}/consoles/{self.settings['console_num']}/"
            headers = {'Authorization': f'Token {self.settings["api_token"]}'}
            
            response = requests.post(f"{base_url}send_input/", 
                                   headers=headers,
                                   data={'input': '\x03'})
            
            if response.status_code != 200:
                raise Exception(f"Ошибка остановки бота: {response.text}")
            
            self.bot_status = "выключен"
            self.bot_running = False
            self.toggle_btn.text = 'включить'
            self.toggle_btn.background_color = self.get_button_color()
            self.status_value.text = self.bot_status
            self.status_value.color = self.get_status_color()
            self.animate_status_change()
            self.add_log("Бот успешно остановлен")
        
        except Exception as e:
            print(f"Ошибка при остановке бота: {str(e)}")
            self.add_log(f"Ошибка остановки бота: {str(e)}")

if __name__ == '__main__':
    RobloxApp().run()