
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup

class ConviteIrresistivelApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        texto = Label(text="Tenho uma pergunta importante... 💌", font_size=20)
        botao = Button(text="Clique aqui 😳", size_hint=(1, 0.3), background_color=(1, 0.5, 0.7, 1))
        botao.bind(on_press=self.mostrar_convite)

        layout.add_widget(texto)
        layout.add_widget(botao)

        return layout

    def mostrar_convite(self, instance):
        conteudo = BoxLayout(orientation='vertical', spacing=10, padding=10)
        label = Label(text="Quer sair comigo, Junior? 🥺👉👈", font_size=18)

        botoes = BoxLayout(spacing=10, size_hint=(1, 0.3))
        sim = Button(text="Sim 💖")
        claro = Button(text="Claro! 😍")

        botoes.add_widget(sim)
        botoes.add_widget(claro)
        conteudo.add_widget(label)
        conteudo.add_widget(botoes)

        popup = Popup(title="Convite Especial", content=conteudo,
                      size_hint=(None, None), size=(300, 200))

        sim.bind(on_press=lambda x: self.resposta("Aeeee! Já podemos marcar! 🎉", popup))
        claro.bind(on_press=lambda x: self.resposta("Sabia que você ia topar! 💕", popup))

        popup.open()

    def resposta(self, mensagem, popup):
        popup.dismiss()
        resposta_popup = Popup(title="Resposta", content=Label(text=mensagem),
                               size_hint=(None, None), size=(250, 150))
        resposta_popup.open()

ConviteIrresistivelApp().run()
