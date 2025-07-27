pip install ursina
from ursina import *

app = Ursina()

# Carregar modelo
kirby = Entity(model='kirby_kirby_64.glb', scale=2, position=(0, 0, 0))
girar = False

# Função chamada ao clicar no botão
def click_do_botao():
    
    global girar
    girar = True

# Botão inútil
botao = Button(text='NÃO CLIQUE AQUI', color=color.red, scale=(0.3, 0.1), position=(-0.6, 0.4))
botao.on_click = click_do_botao

# Texto explicando o nada
texto = Text("Kirby está parado. E isso é tudo.", origin=(0, 0), y=0.45, x=-0.3)

def update():
    if girar:
        kirby.rotation_y += 100 * time.dt  # gira bem rápido

app.run()
