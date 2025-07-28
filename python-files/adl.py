from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle

Window.size = (400, 700)

ROSA_BEBE = (1, 0.894, 0.941, 1)
ROSA_FORTE = (1, 0.411, 0.705, 1)
BRANCO = (1, 1, 1, 1)
PRETO = (0, 0, 0, 1)
CINZA_CLARO = (0.9, 0.9, 0.9, 1)

produtos = [
    {"nome": "Colar rosa e verde", "preco": 25.90, "img": "colar.png"},
    {"nome": "kit pulseira azul e laranja", "preco": 15.00, "img": "pulseira.png"},
    {"nome": "conjunto pulsera rubi", "preco": 25.50, "img": "brinco.png"},
    {"nome": "pulera ursinhos coloridos", "preco": 15.00, "img": "anel.png"},
    {"nome": "bobby goods", "preco": 35.00, "img": "tiara.png"},
]

class ProdutoItem(BoxLayout):
    nome = StringProperty()
    preco = NumericProperty()
    img_source = StringProperty()
    add_callback = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 140  # aumentado de 90
        self.padding = 10
        self.spacing = 10

        with self.canvas.before:
            Color(*ROSA_BEBE)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        try:
            self.img = Image(source=self.img_source, size_hint=(None, None), size=(120, 120))  # aumentado de 80x80
        except Exception:
            self.img = Image(size_hint=(None, None), size=(120, 120), color=ROSA_FORTE)

        self.add_widget(self.img)

        box_info = BoxLayout(orientation='vertical')
        box_info.add_widget(Label(text=self.nome, color=PRETO, font_size=26, bold=True, halign='left', valign='middle', size_hint_y=None, height=60))
        box_info.add_widget(Label(text=f"R$ {self.preco:.2f}", color=ROSA_FORTE, font_size=22, size_hint_y=None, height=60))
        self.add_widget(box_info)

        btn = Button(text="Comprar", size_hint=(None, None), size=(120, 45), background_color=ROSA_FORTE)
        btn.bind(on_release=self.on_add)
        self.add_widget(btn)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_add(self, instance):
        if self.add_callback:
            self.add_callback(self)

class TelaLoja(BoxLayout):
    carrinho = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*ROSA_BEBE)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        self.title = Label(text="Lara Biju 💖", font_size=32, bold=True, color=ROSA_FORTE, size_hint_y=None, height=70)
        self.add_widget(self.title)

        self.scroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 160))
        self.produtos_box = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.produtos_box.bind(minimum_height=self.produtos_box.setter('height'))

        for p in produtos:
            item = ProdutoItem(nome=p['nome'], preco=p['preco'], img_source=p['img'], add_callback=self.adicionar_carrinho)
            self.produtos_box.add_widget(item)

        self.scroll.add_widget(self.produtos_box)
        self.add_widget(self.scroll)

        self.btn_carrinho = Button(text=f"Ver Carrinho ({len(self.carrinho)})", size_hint_y=None, height=70, background_color=ROSA_FORTE)
        self.btn_carrinho.bind(on_release=self.ver_carrinho)
        self.add_widget(self.btn_carrinho)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def adicionar_carrinho(self, produto_item):
        self.carrinho.append({"nome": produto_item.nome, "preco": produto_item.preco, "img": produto_item.img_source})
        self.btn_carrinho.text = f"Ver Carrinho ({len(self.carrinho)})"

    def ver_carrinho(self, instance):
        popup = PopupCarrinho(self.carrinho, self)
        popup.open()

class ProdutoCarrinhoItem(BoxLayout):
    nome = StringProperty()
    preco = NumericProperty()
    img_source = StringProperty()
    remove_callback = ObjectProperty()
    index = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 110  # aumentado de 70
        self.padding = 10
        self.spacing = 10
        self.index = kwargs.get('index', 0)

        with self.canvas.before:
            Color(*ROSA_BEBE)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        try:
            self.img = Image(source=self.img_source, size_hint=(None, None), size=(90, 90))  # aumentado de 60x60
        except Exception:
            self.img = Image(size_hint=(None, None), size=(90, 90), color=ROSA_FORTE)

        self.add_widget(self.img)

        box_info = BoxLayout(orientation='vertical')
        box_info.add_widget(Label(text=self.nome, color=PRETO, font_size=22, halign='left', valign='middle', size_hint_y=None, height=50))
        box_info.add_widget(Label(text=f"R$ {self.preco:.2f}", color=ROSA_FORTE, font_size=20, size_hint_y=None, height=50))
        self.add_widget(box_info)

        btn_remover = Button(text="X", size_hint=(None, None), size=(60, 35), background_color=(1, 0.39, 0.39, 1))
        btn_remover.bind(on_release=self.remover)
        self.add_widget(btn_remover)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def remover(self, instance):
        if self.remove_callback:
            self.remove_callback(self.index)

class PopupCarrinho(Popup):
    carrinho = ListProperty()
    tela_loja = ObjectProperty()

    def __init__(self, carrinho, tela_loja, **kwargs):
        super().__init__(**kwargs)
        self.title = "Carrinho 🛒"
        self.size_hint = (0.9, 0.8)
        self.carrinho = carrinho
        self.tela_loja = tela_loja

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        with layout.canvas.before:
            Color(*ROSA_BEBE)
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)

        self.produtos_box = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.produtos_box.bind(minimum_height=self.produtos_box.setter('height'))

        for i, p in enumerate(self.carrinho):
            item = ProdutoCarrinhoItem(nome=p['nome'], preco=p['preco'], img_source=p['img'], remove_callback=self.remover_item, index=i)
            self.produtos_box.add_widget(item)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.produtos_box)
        layout.add_widget(scroll)

        total = sum(p['preco'] for p in self.carrinho)
        self.lbl_total = Label(text=f"Total: R$ {total:.2f}", font_size=26, color=ROSA_FORTE, size_hint_y=None, height=50)
        layout.add_widget(self.lbl_total)

        btns = BoxLayout(size_hint_y=None, height=70, spacing=20)
        btn_voltar = Button(text="Voltar", background_color=ROSA_FORTE, size_hint=(None, None), size=(150, 60))
        btn_finalizar = Button(text="Finalizar", background_color=ROSA_FORTE, size_hint=(None, None), size=(150, 60))
        btn_voltar.bind(on_release=self.dismiss)
        btn_finalizar.bind(on_release=self.finalizar_compra)
        btns.add_widget(btn_voltar)
        btns.add_widget(btn_finalizar)

        layout.add_widget(btns)
        self.content = layout

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def remover_item(self, index):
        self.carrinho.pop(index)
        self.produtos_box.clear_widgets()
        for i, p in enumerate(self.carrinho):
            item = ProdutoCarrinhoItem(nome=p['nome'], preco=p['preco'], img_source=p['img'], remove_callback=self.remover_item, index=i)
            self.produtos_box.add_widget(item)
        total = sum(p['preco'] for p in self.carrinho)
        self.lbl_total.text = f"Total: R$ {total:.2f}"
        self.tela_loja.btn_carrinho.text = f"Ver Carrinho ({len(self.carrinho)})"

    def finalizar_compra(self, instance):
        self.dismiss()
        popup = PopupQRCode(self.carrinho, self.tela_loja)
        popup.open()

class PopupQRCode(Popup):
    carrinho = ListProperty()
    tela_loja = ObjectProperty()

    def __init__(self, carrinho, tela_loja, **kwargs):
        super().__init__(**kwargs)
        self.title = "Pague com Pix 💖"
        self.size_hint = (0.9, 0.9)
        self.carrinho = carrinho
        self.tela_loja = tela_loja

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        with layout.canvas.before:
            Color(*ROSA_BEBE)
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)

        try:
            img = Image(source="qrcode.png", size_hint=(None, None), size=(280, 280))  # maior que antes
            layout.add_widget(img)
        except Exception:
            layout.add_widget(Label(text="QR Code não encontrado.", color=(1, 0, 0, 1)))

        texto = (
            "Após o pagamento, envie um e-mail\n"
            "guilhermelclfreire@gmail.com\n\n"
            "Anexe o comprovante e o nome\n"
            "do(s) item(ns) comprado(s).\n"
            "para finalizar a compra\n"
            "Obrigado pela preferência! 💖"
        )
        layout.add_widget(Label(text=texto, color=ROSA_FORTE, font_size=22))

        btn_ok = Button(text="Ok", size_hint=(1, None), height=60, background_color=ROSA_FORTE)
        btn_ok.bind(on_release=self.ok)
        layout.add_widget(btn_ok)

        self.content = layout

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def ok(self, instance):
        self.dismiss()
        self.tela_loja.carrinho.clear()
        self.tela_loja.btn_carrinho.text = f"Ver Carrinho (0)"

class LaraBijusApp(App):
    def build(self):
        return TelaLoja()

if __name__ == '__main__':
    LaraBijusApp().run()
