from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class WelcomeScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.label = Label(text="Welcome to the Demo App!", font_size='24sp')
        self.button = Button(text="Continue", size_hint=(1, 0.3))
        self.button.bind(on_press=self.show_thank_you)
        self.add_widget(self.label)
        self.add_widget(self.button)

    def show_thank_you(self, instance):
        self.clear_widgets()
        self.add_widget(Label(text="Thank you for using the app!", font_size='24sp'))

class DemoApp(App):
    def build(self):
        return WelcomeScreen()

if __name__ == '__main__':
    DemoApp().run()
