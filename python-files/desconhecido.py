import time
import random
import os

def limpar():
    os.system('cls' if os.name == 'nt' else 'clear')

def digitar(texto, delay=0.03):
    for c in texto:
        print(c, end='', flush=True)
        time.sleep(delay)
    print()

def esperar(tecla="Enter"):
    input(f"\nPressione {tecla} para continuar...")

def ascii_jumpscare():
    arte = """ 
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣄⣶⣠⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠛⣿⣿⣿⣶⣶⣤⣤⣤⠀⣹⣿⣿⣇⠀⣤⣤⣤⣴⣾⣿⣶⣾⠟⠛⠀⠀
⠀⠀⠴⢿⣿⡏⠉⠻⣿⣦⡀⡉⠀⣿⣿⣿⣿⠆⢈⢀⣾⣿⡟⠉⣿⣿⡟⠒⠂⠀
⠀⠀⠀⠊⠘⠇⠀⠀⢀⣭⣿⣿⣦⡈⠛⠛⠋⣠⣾⣿⡟⠉⠀⠀⢸⠀⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⣿⣿⣿⣿⣿⡿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⡿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⠀⢻⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡏⠀⢸⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⡇⠀⣸⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠚⢻⠿⡆⠀⣼⢿⡟⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠑⠐⠁⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""
    limpar()
    print(arte)
    digitar("\n🧠 \"Fear... is the only truth.\"", 0.05)
    time.sleep(2)

def inicio():
    limpar()
    digitar("Sistema enigmático iniciado...", 0.05)
    time.sleep(1)
    digitar("Conectando com a sua mente...", 0.05)
    time.sleep(1)
    esperar()

def pergunta1():
    limpar()
    digitar("PERGUNTA 1:", 0.05)
    digitar("Eu apareço no escuro, mas não sou a noite. Sou um amigo do medo, mas não sou real. O que sou?", 0.05)
    resposta = input("Sua resposta: ").strip().lower()
    if "sombra" in resposta or "pesadelo" in resposta:
        digitar("Hm... interessante resposta...", 0.05)
    else:
        digitar("Não era essa, mas o importante é que você tentou...", 0.05)
    time.sleep(2)

def pergunta2():
    limpar()
    digitar("PERGUNTA 2:", 0.05)
    digitar("Se você fosse um enigma, qual seria sua solução?", 0.05)
    time.sleep(0.5)
    print("Sua resposta: ", end="", flush=True)
    resposta = input().strip().lower()
    if not resposta:
        digitar("Nenhuma resposta? Vamos considerar isso um mistério...", 0.05)
    elif "enigma" in resposta or "mistério" in resposta:
        digitar("Interessante... nunca pensei por este ângulo", 0.05)
    else:
        digitar("Não era essa, mas o importante é que você tentou...", 0.05)
    time.sleep(2)

def pergunta3():
    limpar()
    digitar("PERGUNTA 3:", 0.05)
    digitar("Última... mas escolha com sabedoria.", 0.05)
    digitar("Você prefere encarar seus medos... ou fugir com alguém que ama?", 0.05)
    resposta = input("Sua resposta: ").strip().lower()
    if "encarar" in resposta or "medo" in resposta:
        digitar("Coragem... uma escolha ousada.", 0.05)
    elif "fugir" in resposta or "amor" in resposta:
        digitar("Amor... uma fuga que vale a pena.", 0.05)
    else:
        digitar("Uma escolha única, como você.", 0.05)
    time.sleep(2)

def final():
    ascii_jumpscare()
    time.sleep(2)
    limpar()
    digitar("Você chegou até aqui. Nenhum medo te venceu.", 0.05)
    digitar("Ou talvez tenha vencido... mas você continuou mesmo assim.", 0.05)
    digitar("Isso te torna única.", 0.05)
    digitar("\n❤️ Feliz 6 meses. Que venham muitos enigmas a mais.", 0.05)

if __name__ == "__main__":
    inicio()
    pergunta1()
    pergunta2()
    pergunta3()
    final()