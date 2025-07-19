from kivy.lang import Builder
from kivymd.app import MDApp

KV = '''
MDScreen:
    md_bg_color: 0, 0, 0, 1  # black background

    # LOGO + Sidebar
    MDBoxLayout:
        orientation: 'horizontal'

        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.3
            padding: 20, 30
            spacing: 15

            MDBoxLayout:
                spacing: 10
                adaptive_height: True
                MDIcon:
                    icon: "cube"
                    theme_text_color: "Custom"
                    text_color: 1, 0, 1, 1
                MDLabel:
                    text: "Wardiere, Inc."
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1

            MDBoxLayout:
                spacing: 10
                MDTextField:
                    hint_text: "Nama Gedung"
                    mode: "rectangle"
                    text_color: 1, 1, 1, 1
                    line_color_focus: 0.6, 0.3, 1, 1
                MDRaisedButton:
                    text: "+"
                    md_bg_color: 0.2, 0.6, 1, 1
                    size_hint_x: None
                    width: "40dp"

            MDBoxLayout:
                spacing: 10
                MDTextField:
                    hint_text: "nama Alat"
                    mode: "rectangle"
                    text_color: 1, 1, 1, 1
                    line_color_focus: 0.2, 0.6, 1, 1
                MDTextField:
                    hint_text: ""
                    mode: "rectangle"
                    line_color_focus: 0.2, 0.6, 1, 1

            MDRaisedButton:
                text: "+"
                md_bg_color: 0.2, 0.6, 1, 1
                size_hint: None, None
                size: "40dp", "40dp"
                pos_hint: {"center_x": 0.5}

        # KANAN (Main content)
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.7
            padding: 20
            spacing: 20

            # Navbar atas
            MDBoxLayout:
                adaptive_height: True
                spacing: 20
                MDRaisedButton:
                    text: "Home"
                    md_bg_color: 1, 0, 1, 1
                    text_color: 1, 1, 1, 1
                    size_hint: None, None
                    height: "30dp"
                    width: "80dp"
                    pos_hint: {"center_y": 0.5}
                MDLabel:
                    text: "About"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    halign: "center"
                MDLabel:
                    text: "Content"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    halign: "center"
                MDLabel:
                    text: "Others"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    halign: "center"

            # Kotak Preview
            MDBoxLayout:
                md_bg_color: 1, 1, 1, 1
                radius: [10]
                padding: 10
                MDLabel:
                    text: ""
                    theme_text_color: "Custom"
                    text_color: 0, 0, 0, 1

            # Tombol Download
            MDRaisedButton:
                text: "Dowload"
                md_bg_color: 1, 0, 1, 1
                pos_hint: {"center_x": 0.5}
                size_hint: None, None
                size: "120dp", "40dp"
'''

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        return Builder.load_string(KV)

MainApp().run()
