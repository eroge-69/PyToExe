# main.py
import os
import json
import asyncio
import requests
import subprocess
from dotenv import load_dotenv
from telethon import TelegramClient, events
from formatos import detectar_sinal

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
DESTINO_ID = int(os.getenv("DESTINO_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_CHAT_ID = int(os.getenv("BOT_CHAT_ID"))

client = TelegramClient('session', API_ID, API_HASH)

# 1️⃣ Perguntar uma vez ao iniciar
def configurar_trailing():
    trailing = input("🟡 Ativar trailing stop? (sim/nao): ").strip().lower()
    if trailing != "sim":
        return False, "imediato"
    tp_inicio = input("🟡 Iniciar ordem a partir de qual TP? (tp1, tp2, tp3...): ").strip().lower()
    return True, tp_inicio

TRAILING_GLOBAL, INICIO_EM_GLOBAL = configurar_trailing()

def carregar_canais_do_json():
    try:
        with open("canais.json", "r", encoding="utf-8") as f:
            pastas = json.load(f)
        canais = []
        for pasta in pastas:
            for canal in pasta.get("canais", []):
                canais.append({"id": canal["id"], "nome": canal["nome"]})
        return canais
    except Exception as e:
        print("❌ Erro ao carregar canais.json:", e)
        return []

def enviar_para_bot(texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": BOT_CHAT_ID, "text": texto, "parse_mode": "HTML"}
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print("❌ Falha ao enviar para o bot:", response.text)
    except Exception as e:
        print("❌ Erro ao enviar para o bot:", e)

def enviar_para_trade(dados, origem):
    try:
        ativo = dados["ativo"]
        direcao = dados["acao"].lower()
        sl = float(dados["sl"])
        tps = [float(tp) for tp in dados["tp"] if tp.replace(".", "", 1).isdigit()]

        if not tps:
            print("❌ Nenhum TP numérico válido encontrado.")
            return

        tp_final = tps[-1]
        tps_json = json.dumps(tps)

        comando = [
            "python", "trade.py", ativo, direcao, str(tp_final), str(sl), tps_json,
            str(TRAILING_GLOBAL), INICIO_EM_GLOBAL
        ]

        print(f"🚀 Enviando para trade.py com comando: {comando}")
        subprocess.Popen(comando)
    except Exception as e:
        print(f"❌ Erro ao preparar envio para trade.py: {e}")

def registrar_handlers(canais):
    for canal in canais:
        @client.on(events.NewMessage(chats=canal["id"]))
        async def handler(event, canal=canal):
            try:
                mensagem = event.message.message
                print(f"📩 Mensagem recebida de {canal['nome']}")
                await client.send_message(DESTINO_ID, f"📥 <b>Mensagem do grupo <i>{canal['nome']}</i></b>:\n\n{mensagem}", parse_mode="html")

                dados_sinal = detectar_sinal(mensagem)
                if dados_sinal:
                    print(f"📈 Sinal detectado em {canal['nome']}")
                    enviar_para_bot(mensagem)
                    enviar_para_trade(dados_sinal, canal["nome"])
            except Exception as e:
                print("❌ Erro ao processar mensagem:", e)

canais = carregar_canais_do_json()
registrar_handlers(canais)
client.start()
client.run_until_disconnected()
