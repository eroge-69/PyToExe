import random
import time

# --- Equipas e jogadores inspirados nas primeiras temporadas de Tsubasa ---
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

# --- Mostra plantéis automaticamente ---
def mostrar_plantel(equipa):
    print(f"\n📋 Plantel do {equipa}:")
    for jogador in teams[equipa]:
        print(f"- {jogador['nome']} | Ataque: {jogador['ataque']} | Defesa: {jogador['defesa']}")
    print()

# --- Simula o jogo automaticamente ---
def simular_jogo(equipa1, equipa2):
    print(f"\n⚽ Jogo: {equipa1} vs {equipa2}\n")
    time.sleep(1)

    ataque1 = sum(j["ataque"] for j in teams[equipa1])
    defesa1 = sum(j["defesa"] for j in teams[equipa1])
    ataque2 = sum(j["ataque"] for j in teams[equipa2])
    defesa2 = sum(j["defesa"] for j in teams[equipa2])

    score1 = max(0, int((ataque1 - defesa2) / 20) + random.randint(0, 2))
    score2 = max(0, int((ataque2 - defesa1) / 20) + random.randint(0, 2))

    print(f"Resultado final: {equipa1} {score1} - {score2} {equipa2}")
    if score1 > score2:
        print(f"\n✅ Vitória do {equipa1}! Tsubasa foi decisivo nos minutos finais!\n")
    elif score1 < score2:
        print(f"\n❌ Derrota... Hyuga dominou com toda a sua força!\n")
    else:
        print(f"\n🤝 Empate justo — duelo épico digno de anime!\n")

# --- Execução automática ---
def jogo_automatico():
    equipa1 = "Nankatsu"
    equipa2 = "Meiwa"
    print("🏆 Tsubasa Manager — versão automática\n")
    mostrar_plantel(equipa1)
    mostrar_plantel(equipa2)
    simular_jogo(equipa1, equipa2)
    print("👋 Obrigado por jogar!")

jogo_automatico()