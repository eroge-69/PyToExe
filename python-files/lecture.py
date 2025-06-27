from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.core.window import Window

Window.size = (400, 700)

test_data = {
    "Математика": [
        {"date": "20/06/2025", "content": "Производная функции"},
        {"date": "21/06/2025", "content": "Интегралы"},
    ],
    "История": [
        {"date": "24/06/2025", "content": "Вторая мировая война"},
        {"date": "26/06/2025", "content": "Холодная война"},
    ],
    "Физика": [
        {"date": "23/06/2025", "content": "Закон кулона"},
    ]
}

class LectureApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.spinner.bind(text=self.on_subject_selected)
        self.root.add_widget(self.spinner)

        self.scroll = ScrollView()
        self.lecture_label = Label(
            size_hint_y=None,
            text="[i]Выберете предмет для просмотра лекций[/i]",
            murkup=True,
            font_size=16
        )
        self.lecture_label.bind(texture_size=self.update_label_height)
        self.scroll.add_widget(self.lecture_label)
        self.root.add_widget(self.scroll)

        return self.root
    
    def update_label_height(self, instance, value):
        self.lecture_label.height = value[1]

    def on_subject_selced(self, spinner, text):
        lectures = text_data.get(text, [])
        output = ""
        for lec in sorted(lectures, key=lambda x: x['date']):
            output += f"[b]{lec['date']}[/b]\n{lec['content']}\n\n"
        self.lecture_label.text = output if output else "[i]Нет лекций для отображения"

if __name__ == "__main__":
    LectureApp().run()