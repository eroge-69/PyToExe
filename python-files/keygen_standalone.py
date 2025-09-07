# keygen_app.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.core.window import Window
import hashlib
class OIDTextInput(BoxLayout):
    """
    TextInput با محدودیت طول ورودی HEX و dash اتوماتیک
    """

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.size_hint_y = None
        self.height = dp(40)

        # الگو
        self.oid_hint = "YYYY-MM-DD-HH-MM-XXXX-XXXX-XXXX"
        self.pattern_blocks = [4, 2, 2, 2, 2, 4, 4, 4]
        self.max_chars = sum(self.pattern_blocks)  # 24

        self.label_hint = Label(
            text=self.oid_hint,
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        self.label_hint.bind(size=self.label_hint.setter('text_size'))

        self.text_input = TextInput(
            text="",
            multiline=False,
            foreground_color=(0, 0, 0, 1),
            background_color=(1, 1, 1, 1),
            cursor_color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(30),
        )
        self.text_input.bind(text=self.on_text_change)

        self.add_widget(self.label_hint)
        self.add_widget(self.text_input)

    def on_text_change(self, instance, value):
        # فقط HEX
        value = ''.join(c.upper() for c in value if c.upper() in "0123456789ABCDEF")

        # محدودیت طول
        value = value[:self.max_chars]

        # ساخت رشته فرمت شده با dash
        formatted = ""
        idx = 0
        for block_i, block_len in enumerate(self.pattern_blocks):
            for _ in range(block_len):
                if idx < len(value):
                    formatted += value[idx]
                    idx += 1
                else:
                    formatted += self.oid_hint[len(formatted)]
            if block_i < len(self.pattern_blocks) - 1:
                formatted += '-'

        # بروزرسانی
        self.text_input.text = value
        self.label_hint.text = formatted

    def get_text(self):
        return self.text_input.text


class KeygenDialog(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(10), padding=dp(12), **kwargs)
        self.oid_input = OIDTextInput()
        self.add_widget(Label(text="Enter OID :", size_hint_y=None, height=dp(20)))
        self.add_widget(self.oid_input)

        self.state_selector = Spinner(
            text="Select State",
            values=["State 1", "State 2", "State 3"],
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(Label(text="Select State:", size_hint_y=None, height=dp(30)))
        self.add_widget(self.state_selector)

        self.gen_btn = Button(text="Generate Password", size_hint_y=None, height=dp(40))
        self.gen_btn.bind(on_press=self.generate_password)
        self.add_widget(self.gen_btn)

        self.result_label = Label(text="", size_hint_y=None, height=dp(30))
        self.add_widget(self.result_label)

        self._fixed_seed = 8737

    def generate_password(self, *_):
        oid = self.oid_input.get_text()
        state_map = {"State 1": 1, "State 2": 2, "State 3": 3}
        state_text = self.state_selector.text
        if state_text not in state_map:
            self.result_label.text = "[color=ff0000]Please select a state[/color]"
            return
        state = state_map[state_text]
        pwd = self._generate_password(oid, state)
        self.result_label.text = f"Generated Password: {pwd}"

    def _generate_password(self, oid: str, state: int) -> str:
        """
        تولید پسورد 8 رقمی حساس به تمام کاراکترهای OID و state
        """
        # OID بدون dash
        oid_clean = oid.replace('-', '')

        # ترکیب OID و state با seed ثابت
        combined = f"{self._fixed_seed}-{state}-{oid_clean}".encode('utf-8')

        # هش SHA256 می‌گیریم
        digest = hashlib.sha256(combined).hexdigest()  # رشته هگز 64 کاراکتری

        # تولید پسورد 8 رقمی با تبدیل هر بخش از هش به عدد و گرفتن ماژول 10
        digits = []
        for i in range(8):
            # انتخاب 4 کاراکتر پشت سر هم از digest و تبدیل به عدد هگز -> دهدهی
            segment = digest[i * 4:(i + 1) * 4]
            num = int(segment, 16) % 10
            digits.append(str(num))

        return ''.join(digits)


class KeygenApp(App):
    def build(self):
        # نصف کردن سایز پنجره
        Window.size = (Window.size[0] // 2, Window.size[1] // 2)
        return KeygenDialog()


if __name__ == "__main__":
    KeygenApp().run()
