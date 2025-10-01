from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import math

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        sections = [
            ('العمليات الأساسية', 'basic'),
            ('أدوات المثلثات', 'triangle'),
            ('المعادلة التربيعية', 'quadratic'),
            ('الدوال المثلثية', 'trig'),
            ('الإحداثيات', 'coordinates'),
            ('نظريات التناسب', 'proportions'),
            ('معدلات التشابه', 'similarity')
        ]
        for name, key in sections:
            btn = Button(text=name, font_size=24)
            btn.bind(on_press=lambda instance, k=key: self.manager.current = k)
            layout.add_widget(btn)
        self.add_widget(layout)

class BasicOperations(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.input1 = TextInput(hint_text='الرقم الأول', multiline=False, font_size=20)
        self.input2 = TextInput(hint_text='الرقم الثاني', multiline=False, font_size=20)
        self.result = Label(text='النتيجة', font_size=24)
        for op in ['+', '-', '*', '/']:
            btn = Button(text=op, font_size=24)
            btn.bind(on_press=self.calculate)
            layout.add_widget(btn)
        layout.add_widget(self.input1)
        layout.add_widget(self.input2)
        layout.add_widget(self.result)
        self.add_widget(layout)

    def calculate(self, instance):
        try:
            a = float(self.input1.text)
            b = float(self.input2.text)
            op = instance.text
            res = {'+': a + b, '-': a - b, '*': a * b, '/': a / b}[op]
            self.result.text = f'النتيجة: {res}'
        except:
            self.result.text = 'خطأ في الإدخال'

class TriangleTools(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='أدوات المثلثات قيد التطوير', font_size=24))
        self.add_widget(layout)

class QuadraticEquation(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.a = TextInput(hint_text='المعامل a', multiline=False, font_size=20)
        self.b = TextInput(hint_text='المعامل b', multiline=False, font_size=20)
        self.c = TextInput(hint_text='المعامل c', multiline=False, font_size=20)
        self.result = Label(text='النتيجة', font_size=24)
        btn = Button(text='حل المعادلة', font_size=24)
        btn.bind(on_press=self.solve)
        layout.add_widget(self.a)
        layout.add_widget(self.b)
        layout.add_widget(self.c)
        layout.add_widget(btn)
        layout.add_widget(self.result)
        self.add_widget(layout)

    def solve(self, instance):
        try:
            a = float(self.a.text)
            b = float(self.b.text)
            c = float(self.c.text)
            d = b**2 - 4*a*c
            if d > 0:
                x1 = (-b + math.sqrt(d)) / (2*a)
                x2 = (-b - math.sqrt(d)) / (2*a)
                self.result.text = f'جذران حقيقيان: {x1}, {x2}'
            elif d == 0:
                x = -b / (2*a)
                self.result.text = f'جذر واحد: {x}'
            else:
                self.result.text = 'جذران مركبان'
        except:
            self.result.text = 'خطأ في الإدخال'

class TrigFunctions(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.angle = TextInput(hint_text='الزاوية بالدرجات', multiline=False, font_size=20)
        self.result = Label(text='النتائج', font_size=24)
        btn = Button(text='احسب الدوال', font_size=24)
        btn.bind(on_press=self.calculate)
        layout.add_widget(self.angle)
        layout.add_widget(btn)
        layout.add_widget(self.result)
        self.add_widget(layout)

    def calculate(self, instance):
        try:
            deg = float(self.angle.text)
            rad = math.radians(deg)
            s = math.sin(rad)
            c = math.cos(rad)
            t = math.tan(rad)
            self.result.text = f'جيب: {s}\nجيب تمام: {c}\nظل: {t}'
        except:
            self.result.text = 'خطأ في الإدخال'

class Coordinates(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='الإحداثيات قيد التطوير', font_size=24))
        self.add_widget(layout)

class Proportions(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='نظريات التناسب قيد التطوير', font_size=24))
        self.add_widget(layout)

class Similarity(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='معدلات التشابه قيد التطوير', font_size=24))
        self.add_widget(layout)

class CalculatorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name='menu'))
        sm.add_widget(BasicOperations(name='basic'))
        sm.add_widget(TriangleTools(name='triangle'))
        sm.add_widget(QuadraticEquation(name='quadratic'))
        sm.add_widget(TrigFunctions(name='trig'))
        sm.add_widget(Coordinates(name='coordinates'))
        sm.add_widget(Proportions(name='proportions'))
        sm.add_widget(Similarity(name='similarity'))
        return sm

CalculatorApp().run()
