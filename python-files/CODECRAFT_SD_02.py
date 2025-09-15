import random

def guessing_game():
    print("Bem-vindo ao Jogo da Adivinhação!")
    numero_secreto = random.randint(1, 100)
    tentativas = 0

    while True:
        try:
            palpite = int(input("Adivinhe o número entre 1 e 100: "))
            tentativas += 1

            if palpite < 1 or palpite > 100:
                print("Por favor, digite um número entre 1 e 100.")
                continue

            if palpite < numero_secreto:
                print("Muito baixo! Tente novamente.")
            elif palpite > numero_secreto:
                print("Muito alto! Tente novamente.")
            else:
                print(f"Parabéns! Você acertou o número {numero_secreto} em {tentativas} tentativas!")
                break
        except ValueError:
            print("Entrada inválida! Por favor digite um número inteiro.")

if __name__ == "__main__":
    guessing_game()
