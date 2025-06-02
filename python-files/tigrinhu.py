
import random
import os
import time
import json 

def carregar_dinheiro():
    try:
        with open('dinheiro.json', 'r') as f:
            data = json.load(f)
            return data.get('dinheiro', 20)
    except FileNotFoundError:
        return 20

def salvar_dinheiro(valor):
    with open('dinheiro.json', 'w') as f:
        json.dump({'dinheiro': valor}, f)

usuario = os.environ.get("USERNAME")
dinheiro = carregar_dinheiro()

print(35*"=")
print(f"Olá {usuario}, Bem-Vindo ao Jogo do Tigrinho!")
print(35*"=")
time.sleep(2)

if dinheiro <= 0:
    print("Parece que Você Gastou Todo seu Sustento do Mês em Apostas\nOpa! Bolsa Familia Caiu! + R$5, Jogue Mais Consiente Desta Vez!")
    dinheiro = 5



while True:
    try:
        aposta = float(input(f"Quanto Você Quer Apostar? Dinheiro Restante: {dinheiro}\n"))
        if aposta > dinheiro:
            print("Você Não Pode Gastar Mais Do Que Tem!")
            continue
        else:
            break
        break
    except ValueError:
        print("Por Favor, Coloque somente Números")
        continue

dinheiro = dinheiro-aposta
print(f"Você Ainda tem: R${dinheiro}")
time.sleep(2)

while True:
    try:
        dif = int(input("Escolha a Dificuldade:\n1- Facil (50%)\n2- Médio (100%)\n3- Dificil (200%)\n4- Impossivel (1000%)\n"))
        if dif > 4:
            continue
        else:
            break
        break
    except ValueError:
        print("Por Favor, Coloque somente Números")
        continue

if dif == 1:
    ganho = 1.5
    rnd = random.randint(1, 5)
    limite = 5
elif dif == 2:
    ganho = 2
    rnd = random.randint(1, 10)
    limite = 10
elif dif == 3:
    ganho = 3
    rnd = random.randint(1, 20)
    limite = 20
elif dif == 4:
    ganho = 11
    rnd = random.randint(1, 1000)
    limite = 1000

while True:
    try:
        num = int(input(f"Escolha um Número de (1-{limite}): "))
        if num > limite:
            continue
        else:
            break
        break
    except ValueError:
        print("Por Favor, Coloque somente Números")
        continue

print("E o Número Sorteado é...")
time.sleep(3)

if rnd == num:
    dinheiro += aposta*ganho
    print(50*".")
    print("Parabéns! Você Acertou!")
    print(f"Seu Saldo Atual é R${dinheiro}")
    print(50*".")
else:
    print(50*".")
    print(f"Que Pena, Não Foi Dessa Vez!\nO Número Sorteado Era {rnd}")
    print(f"Seu Saldo Atual é R${dinheiro}")
    print(50*".")

salvar_dinheiro(dinheiro)

input("Pressione Qualquer Tecla Para Sair...")