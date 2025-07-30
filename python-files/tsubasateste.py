import random
import time

# --- Base de dados de equipas e jogadores inspirados em Tsubasa ---
teams = {
    "Nankatsu": [
        {"nome": "Tsubasa Ozora", "ataque": 95, "defesa": 70},
        {"nome": "Taro Misaki", "ataque": 88, "defesa": 65},
        {"nome": "Genzo Wakabayashi", "ataque": 30, "defesa": 95},
    ],
    "Meiwa": [
        {"nome": "Kojiro Hyuga", "ataque": 92, "defesa": 60},
        {"nome": "Takeshi Sawada", "ataque": 80, "defesa": 68},
        {"nome": "Ken Wakashimazu", "ataque": 40, "defesa": 90},
    ]
}

# --- Funções ---
def introducao():
    print("🏆 Bem-vindo ao Tsubasa Manager!\n")
    print("Escolhe a tua equipa:")
    for i, nome in enumerate(teams.keys()):
        print(f"{i + 1}. {nome}")
    escolha = int(input("\nNúmero da equipa: ")) - 1
    team_name = list(teams.keys())[escolha]
    adversary = list(teams.keys())[1 - escolha]
    print(f"\nIrás liderar o {team_name} contra o {adversary}!\n")
    return team_name, adversary

def mostrar_plantel(team):
    print(f"\n📋 Plantel do {team}:")
    for jogador in teams[team]:
        print(f"- {jogador['nome']} | Ataque: {jogador['ataque']} | Defesa: {jogador['defesa']}")
    print()

def simular_jogo(time1, time2):
    print("🎮 Simulando jogo...\n")
    time.sleep(1)
    ataque1 = sum([j["ataque"] for j in teams[time1]])
    defesa1 = sum([j["defesa"] for j in teams[time1]])
    ataque2 = sum([j["ataque"] for j in teams[time2]])
    defesa2 = sum([j["defesa"] for j in teams[time2]])
    score1 = max(0, int((ataque1 - defesa2) / 20) + random.randint(0, 2))
    score2 = max(0, int((ataque2 - defesa1) / 20) + random.randint(0, 2))

    print(f"{time1} {score1} - {score2} {time2}")
    if score1 > score2:
        print(f"\n✅ Vitória para o {time1}! Tsubasa está em êxtase!\n")
    elif score1 < score2:
        print(f"\n❌ Derrota... Hyuga comemorou com pose dramática.\n")
    else:
        print(f"\n⚖️ Empate! Um duelo equilibrado até ao fim.\n")

# --- Loop principal ---
def iniciar_jogo():
    time1, time2 = introducao()
    while True:
        print("Menu:")
        print("1. Ver Plantel")
        print("2. Simular Jogo")
        print("3. Sair")
        escolha = input("Escolhe uma opção: ")
        if escolha == "1":
            mostrar_plantel(time1)
        elif escolha == "2":
            simular_jogo(time1, time2)
        elif escolha == "3":
            print("👋 Até à próxima, treinador!")
            break
        else:
            print("Opção inválida.\n")

iniciar_jogo()