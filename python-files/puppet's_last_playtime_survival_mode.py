import time
import random

# CONFIGURAÇÃO DOS AMBIENTES
salas = [f"sala_{i}" for i in range(1, 23)]
tubulacoes = [f"tubulacao_{i}" for i in range(1, 6)]
sala_secreta = "sala_secreta"
ambientes = salas + tubulacoes + [sala_secreta]

# JOGADOR
jogador = {
    "local": "sala_1",
    "energia": 100,
    "fôlego": 100,
    "vivo": True,
    "pontos": 0,
    "tempo_inicio": time.time()
}

# MASCOTES
mascotes = {
    "Buba": "sala_22",
    "Puppy": "sala_5",
    "Tico": "sala_10",
    "Zilla": "tubulacao_2",
    "Chomp": "sala_7",
    "Lurk": "tubulacao_4",
    "Sombra": "sala_3",
    "Grito": "sala_6"
}
tempo_chegada = {}
portas_bloqueadas = set()
detector_movimento = {}

# TEMPO E DIFICULDADE
tempo_inicio_energia = time.time()
tempo_sem_energia = None
gerador_recarga = False
movimento_mascotes_intervalo = 9
tempo_movimento_proximo = time.time() + movimento_mascotes_intervalo
nivel_dificuldade = 1
tempo_ultimo_nivel = time.time()

# FUNÇÕES DO JOGO
def mover_jogador(destino):
    if destino in ambientes:
        if destino in portas_bloqueadas:
            print(f"A porta para {destino} está bloqueada!")
        else:
            jogador["local"] = destino
            jogador["pontos"] += 1
            print(f"Você foi para {destino}.")
    else:
        print("Local inválido.")

def bloquear_porta(alvo):
    portas_bloqueadas.add(alvo)
    print(f"Você bloqueou {alvo}.")

def desbloquear_porta(alvo):
    portas_bloqueadas.discard(alvo)
    print(f"Você desbloqueou {alvo}.")

def status():
    print("\n--- STATUS ---")
    print(f"Local: {jogador['local']} | Energia: {jogador['energia']} | Fôlego: {jogador['fôlego']}")
    print(f"Pontos: {jogador['pontos']} | Sobrevivência: {int(time.time() - jogador['tempo_inicio'])}s")
    print("Portas bloqueadas:", ', '.join(portas_bloqueadas) if portas_bloqueadas else "nenhuma")
    for amb, masc in detector_movimento.items():
        print(f"[{amb}] - Detecção: {', '.join(masc)}")

def recarregar_gerador():
    global gerador_recarga, tempo_inicio_energia
    print("⚡ Recarregando o gerador... (10 segundos)")
    gerador_recarga = True
    for i in range(10):
        print(f"{i+1}...", end=" ", flush=True)
        time.sleep(1)
    print("\n✅ Gerador restaurado.")
    jogador["energia"] = 100
    tempo_inicio_energia = time.time()
    gerador_recarga = False

def atualizar_energia():
    global tempo_sem_energia
    jogador["energia"] = max(0, 100 - int((time.time() - tempo_inicio_energia) / 2))
    if jogador["energia"] == 0:
        if tempo_sem_energia is None:
            tempo_sem_energia = time.time()
        elif time.time() - tempo_sem_energia >= 60:
            print("🔌 Energia esgotada! Você foi pego no escuro!")
            jogador["vivo"] = False
    else:
        tempo_sem_energia = None

def mover_mascotes():
    global tempo_movimento_proximo
    if time.time() >= tempo_movimento_proximo:
        for nome in mascotes:
            if nome == "Sombra":
                mascotes[nome] = random.choice(salas)
            elif nome == "Grito":
                if random.random() < 0.2:
                    portas_bloqueadas.add(random.choice(salas))
            else:
                mascotes[nome] = random.choice(ambientes)
            tempo_chegada[nome] = time.time() + 10 if mascotes[nome] == jogador["local"] else None
        tempo_movimento_proximo = time.time() + movimento_mascotes_intervalo

def atualizar_detectores():
    global detector_movimento
    detector_movimento = {}
    for nome, local in mascotes.items():
        if local not in detector_movimento:
            detector_movimento[local] = []
        detector_movimento[local].append(nome)

def verificar_colisao():
    for nome, local in mascotes.items():
        if local == jogador["local"]:
            print(f"👾 {nome} alcançou você! Fim do jogo.")
            jogador["vivo"] = False
            break

def atualizar_dificuldade():
    global nivel_dificuldade, movimento_mascotes_intervalo, tempo_ultimo_nivel
    if time.time() - tempo_ultimo_nivel > 60:
        nivel_dificuldade += 1
        movimento_mascotes_intervalo = max(3, movimento_mascotes_intervalo - 1)
        tempo_ultimo_nivel = time.time()
        print(f"\n⚠ DIFICULDADE AUMENTOU! Nível {nivel_dificuldade}")

def mostrar_minimapa():
    print("\n--- MINIMAPA ---")
    for amb in ambientes:
        linha = f"{amb:<15}"
        if jogador["local"] == amb:
            linha += "🧍 VOCÊ"
        elif amb in detector_movimento:
            linha += "👾 " + ','.join(detector_movimento[amb])
        elif amb in portas_bloqueadas:
            linha += "🚪 BLOQUEADA"
        print(linha)

def eventos_aleatorios():
    chance = random.randint(1, 12)
    if chance == 1:
        bloqueada = random.choice(salas)
        portas_bloqueadas.add(bloqueada)
        print(f"⚠ Evento: A sala {bloqueada} foi trancada misteriosamente!")
    elif chance == 2:
        print("👻 Evento: Um sussurro te paralisa. Você perde esta rodada.")
        time.sleep(3)
    elif chance == 3 and jogador["pontos"] > 15:
        print("🕳️ Você encontrou uma passagem secreta para a SALA SECRETA!")
        jogador["local"] = sala_secreta

def avisos_mascotes():
    agora = time.time()
    for nome, t in tempo_chegada.items():
        if t and 0 < t - agora <= 10:
            print(f"⚠ Alerta! {nome} está se aproximando de sua sala em até 10 segundos!")

# LOOP PRINCIPAL
def modo_survival():
    print("🎮 MODO SURVIVAL INICIADO 🎮")
    print("Dica: use números para agir. Vá até a sala_1 para recarregar energia.")
    while jogador["vivo"]:
        atualizar_energia()
        mover_mascotes()
        atualizar_detectores()
        verificar_colisao()
        atualizar_dificuldade()
        avisos_mascotes()
        eventos_aleatorios()
        if not jogador["vivo"]:
            break

        print("\n1. Mover | 2. Bloquear | 3. Desbloquear | 4. Status | 5. Recarregar | 6. Minimapa")
        acao = input("> ").strip()

        if acao == "1":
            print("Escolha o destino:")
            for i, amb in enumerate(ambientes):
                print(f"{i+1}. {amb}")
            escolha = input("> ").strip()
            try:
                mover_jogador(ambientes[int(escolha)-1])
            except:
                print("Destino inválido.")
        elif acao == "2":
            bloquear_porta(input("Bloquear qual sala? ").strip())
        elif acao == "3":
            desbloquear_porta(input("Desbloquear qual sala? ").strip())
        elif acao == "4":
            status()
        elif acao == "5":
            if jogador["local"] == "sala_1":
                recarregar_gerador()
            else:
                print("Você precisa estar na sala_1 para acessar o gerador.")
        elif acao == "6":
            mostrar_minimapa()
        else:
            print("Ação inválida.")

    print("\n💀 GAME OVER 💀")
    print(f"🏁 Tempo: {int(time.time() - jogador['tempo_inicio'])} segundos")
    print(f"🎯 Pontuação final: {jogador['pontos']}")

modo_survival()