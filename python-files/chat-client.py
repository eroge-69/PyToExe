import socket
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup

HOST = '127.0.0.1'
PORT = 12345

class ChatClient(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.username = ""
        self.get_username()

    def get_username(self):
        content = BoxLayout(orientation='vertical')
        self.username_input = TextInput(hint_text='Enter your username', multiline=False)
        ok_button = Button(text='OK')
        content.add_widget(self.username_input)
        content.add_widget(ok_button)
        self.popup = Popup(title='Enter Username', content=content,
                           size_hint=(None, None), size=(300, 200), auto_dismiss=False)
        ok_button.bind(on_release=self.set_username)
        self.popup.open()

    def set_username(self, instance):
        self.username = self.username_input.text.strip()
        if self.username:
            self.popup.dismiss()
            self.setup_ui()
            self.connect_to_server()

    def setup_ui(self):
        self.chat_history = Label(size_hint_y=None, text_size=(self.width, None))
        self.chat_history.bind(texture_size=self.update_chat_height)
        scroll = ScrollView(size_hint=(1, 0.85))
        scroll.add_widget(self.chat_history)
        self.add_widget(scroll)

        bottom = BoxLayout(size_hint=(1, 0.15), spacing=5)
        self.message_input = TextInput(hint_text='Type a message', multiline=False)
        send_button = Button(text='Send')
        send_button.bind(on_release=self.send_message)
        self.message_input.bind(on_text_validate=self.send_message)
        bottom.add_widget(self.message_input)
        bottom.add_widget(send_button)
        self.add_widget(bottom)

    def update_chat_height(self, instance, value):
        self.chat_history.height = self.chat_history.texture_size[1]

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((HOST, PORT))
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.update_chat(f"[Erreur] impossible connection : {e}")

    def send_message(self, instance):
        message = self.message_input.text.strip()
        if message:
            full_msg = f"{self.username}: {message}"
            try:
                self.client_socket.send(full_msg.encode('utf-8'))
                self.message_input.text = ''
            except:
                self.update_chat("[Erreur] cannot send")

    def receive_messages(self):
        while True:
            try:
                msg = self.client_socket.recv(1024).decode('utf-8')
                self.update_chat(msg)
            except:
                self.update_chat("[!] disconnected from server")
                break

    def update_chat(self, message):
        self.chat_history.text += message + '\n'

class ChatApp(App):
    def build(self):
        return ChatClient()

if __name__ == '__main__':
    ChatApp().run()