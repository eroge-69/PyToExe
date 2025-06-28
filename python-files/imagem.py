import random
import ctypes

mensagens = [
    "Você é incrível!",
    "Sorria mais hoje!",
    "Tenha um ótimo dia!",
    "Cuidado com os patos!",
    "Nada é real. Ou é?"
]

mensagem = random.choice(mensagens)
ctypes.windll.user32.MessageBoxW(0, mensagem, "Mensagem Aleatória", 1)
