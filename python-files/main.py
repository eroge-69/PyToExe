from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup

class StitchMatchLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text='StitchMatch AI – Smart Embroidery', font_size=24))
        self.image = Image(size_hint=(1, 0.5))
        self.add_widget(self.image)
        self.file_chooser = FileChooserIconView(size_hint=(1, 0.4))
        self.file_chooser.bind(on_selection=self.load_image)
        self.add_widget(self.file_chooser)
        self.inputs = {}
        for label in ['Height', 'Width', 'Sleeve Length', 'Neck Circumference']:
            box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
            box.add_widget(Label(text=label, size_hint=(0.5, 1)))
            input_field = TextInput(multiline=False)
            self.inputs[label] = input_field
            box.add_widget(input_field)
            self.add_widget(box)
        self.add_widget(Button(text='Generate Mock Suggestion', on_press=self.generate_suggestion))
        self.add_widget(Button(text='Export as PNG', on_press=self.export_png))

    def load_image(self, chooser, selection):
        if selection:
            self.image.source = selection[0]
            self.image.reload()

    def generate_suggestion(self, instance):
        content = Label(text="(Mock) Suggestion: Try a gold border or curved collar.")
        popup = Popup(title="AI Suggestion", content=content, size_hint=(0.8, 0.3))
        popup.open()

    def export_png(self, instance):
        content = Label(text="(Mock) Exported to device as PNG.")
        popup = Popup(title="Export", content=content, size_hint=(0.6, 0.3))
        popup.open()

class StitchMatchApp(App):
    def build(self):
        return StitchMatchLayout()

if __name__ == '__main__':
    StitchMatchApp().run()
