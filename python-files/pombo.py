import time
import os

# Define a arte ASCII do pombo
pigeon_art = [
    "   \\\\\\",
    "   (o>",
    "\\\\_//)",
    " \\_/_)",
    "  _|_"
]

# Função para limpar o terminal
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Função para animar o pombo a voar
def animate_pigeon():
    width = 60  # Largura do voo
    for pos in range(width):
        clear_screen()
        for line in pigeon_art:
            print(" " * pos + line)
        time.sleep(0.05)
    print("\n" + " " * pos + "sou um pombo do Graça!")
    time.sleep(3)  # Mantém a mensagem visível por 3 segundos

# Executar a animação
if __name__ == "__main__":
    animate_pigeon()
