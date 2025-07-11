import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard  # Dla kopiowania
from openai import OpenAI  # Dla Grok API
import plyer  # Dla sensorów
from plyer import tts as plyer_tts
from plyer import stt
import requests


# Ustaw API key
os.environ['OPENAI_API_KEY'] = 'xai-yXA7ikG5xVU3HC5nhATLJdyx9dJsiEvtmxlGv6oQGaN4YyOTzilZe2Gpcy2SzFJnctSpylqd5nj6IsVd'

class JarvisApp(App):
    def build(self):
        self.client = OpenAI(base_url='https://api.x.ai/v1')
        self.listening = True  # Default: ciągły nasłuch on
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)  # Większe padding/spacing dla lepszego klikania
        
        # Chat history (większy, dynamic)
        self.chat_scroll = ScrollView(size_hint=(1, 0.75))  # Więcej miejsca na fullscreen
        self.chat_label = Label(text='Witaj! Jestem Jarvis 2.0. Mów do mnie... (sprawdź permisje mikrofonu jeśli nie działa)', size_hint_y=None, height=600, valign='top', halign='left', font_size=20)  # Większy font
        self.chat_label.bind(texture_size=self.chat_label.setter('size'))
        self.chat_label.text_size = (self.chat_label.width, None)
        self.chat_scroll.add_widget(self.chat_label)
        layout.add_widget(self.chat_scroll)
        
        # Input area (wyżej, focus)
        input_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.input = TextInput(hint_text='Wpisz jeśli chcesz...', multiline=False, focus=True, font_size=18)
        input_layout.add_widget(self.input)
        
        send_button = Button(text='>', size_hint=(0.25, 1), font_size=24)  # Większy przycisk
        send_button.bind(on_press=self.send_message)
        input_layout.add_widget(send_button)
        layout.add_widget(input_layout)
        
        # Bottom buttons (większe, wyższe, z większym spacing)
        bottom_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)  # Większe spacing
        self.toggle_button = Button(text='🔊 Zawsze słuchaj (ON)', size_hint=(0.33, 1), font_size=20)
        self.toggle_button.bind(on_press=self.toggle_listen)
        bottom_layout.add_widget(self.toggle_button)
        
        copy_button = Button(text='📋 Kopiuj logi', size_hint=(0.33, 1), font_size=20)
        copy_button.bind(on_press=self.copy_logs)
        bottom_layout.add_widget(copy_button)
        
        improve_button = Button(text='🔄 Ulepsz', size_hint=(0.33, 1), font_size=20)
        improve_button.bind(on_press=self.self_improve)
        bottom_layout.add_widget(improve_button)
        layout.add_widget(bottom_layout)
        
        # Auto-start: Powitanie i ciągły nasłuch
        Clock.schedule_once(self.auto_start, 1)
        
        return layout
    
    def auto_start(self, dt):
        self.speak('Witaj! Jestem Jarvis. Mów do mnie, słucham zawsze. Jeśli głos nie działa, sprawdź permisje mikrofonu.')
        self.continuous_listen()
    
    def continuous_listen(self, dt=None):
        if not self.listening:
            return
        try:
            stt.start()
            Clock.schedule_once(self.process_stt_results, 5)  # Po 5 sek stop i pobierz results
        except Exception as e:
            self.chat_label.text += f'\nBłąd STT: {str(e)}. Sprawdź permisje mikrofonu w ustawieniach.'
            Clock.schedule_once(self.continuous_listen, 2)  # Restart po błędzie
    
    def process_stt_results(self, dt):
        try:
            stt.stop()
            results = stt.results
            if results:
                self.input.text = results[0]
                self.send_message(None)
            # Restart nasłuchu natychmiast
            Clock.schedule_once(self.continuous_listen, 0.1)
        except Exception as e:
            self.chat_label.text += f'\nBłąd STT: {str(e)}'
            Clock.schedule_once(self.continuous_listen, 2)
    
    def toggle_listen(self, instance):
        self.listening = not self.listening
        self.toggle_button.text = '🔊 Zawsze słuchaj (ON)' if self.listening else '🔇 Zawsze słuchaj (OFF)'
        if self.listening:
            self.continuous_listen()
    
    def copy_logs(self, instance):
        try:
            Clipboard.copy(self.chat_label.text)
            self.chat_label.text += '\nJarvis: Logi skopiowane do schowka!'
            self.speak('Logi skopiowane do schowka!')
        except Exception as e:
            self.chat_label.text += f'\nBłąd kopiowania: {str(e)}'
    
    def send_message(self, instance):
        user_msg = self.input.text
        if not user_msg:
            return
        self.chat_label.text += f'\nTy: {user_msg}'
        self.input.text = ''
        
        try:
            completion = self.client.chat.completions.create(
                model='grok-beta',
                messages=[
                    {'role': 'system', 'content': 'Jesteś Jarvisem, super-asystentem. Odpowiadaj po polsku.'},
                    {'role': 'user', 'content': user_msg}
                ]
            )
            ai_response = completion.choices[0].message.content
            self.chat_label.text += f'\nJarvis: {ai_response}'
            self.speak(ai_response)
            
            if 'bateria' in user_msg.lower():
                battery = plyer.battery.status
                resp = f'Poziom baterii: {battery["percentage"]}%'
                self.chat_label.text += f'\nJarvis: {resp}'
                self.speak(resp)
            elif 'pogoda' in user_msg.lower():
                response = requests.get('https://api.openweathermap.org/data/2.5/weather?q=Warszawa&appid=TWÓJ_WEATHER_KEY')
                data = response.json()
                if 'weather' in data:
                    desc = data["weather"][0]["description"]
                    resp = f'Pogoda w Warszawie: {desc}'
                    self.chat_label.text += f'\nJarvis: {resp}'
                    self.speak(resp)
        except Exception as e:
            self.chat_label.text += f'\nBłąd: {str(e)}'
        
        Clock.schedule_once(self.scroll_to_bottom, 0.1)
    
    def scroll_to_bottom(self, dt):
        self.chat_scroll.scroll_y = 0
    
    def speak(self, text):
        try:
            plyer_tts.speak(text)
        except Exception as e:
            self.chat_label.text += f'\nBłąd TTS: {str(e)}'
    
    def self_improve(self, instance):
        user_msg = self.input.text or 'Ulepsz appkę o nową funkcję.'
        try:
            completion = self.client.chat.completions.create(
                model='grok-beta',
                messages=[
                    {'role': 'system', 'content': 'Wygeneruj kod Python Kivy do ulepszenia appki.'},
                    {'role': 'user', 'content': user_msg}
                ]
            )
            new_code = completion.choices[0].message.content
            self.chat_label.text += f'\nJarvis: Kod ulepszenia:\n{new_code}'
            with open(__file__, 'a') as f:
                f.write('\n# Ulepszenie:\n' + new_code)
            self.chat_label.text += '\nUlepszono! Restartuj appkę.'
        except Exception as e:
            self.chat_label.text += f'\nBłąd: {str(e)}'

if __name__ == '__main__':
    Window.size = (360, 640)
    Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Ciemny background
    Window.fullscreen = 'auto'  # Fullscreen mode - cały ekran
    JarvisApp().run()