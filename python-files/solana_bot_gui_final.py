
import requests
import tkinter as tk
from tkinter import messagebox
import threading
import time

API_KEY = "2cda3deb563c4e81bfc8577a1ee0a991"
MONITOR_INTERVAL = 30
LUCRO_MINIMO = 2.0

def get_new_tokens():
    url = "https://public-api.birdeye.so/public/tokenlist?sort=createdAt&sort_type=desc"
    headers = {"x-api-key": API_KEY}
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        tokens = res.json()['data']['tokens']
        return tokens[:5]
    except:
        return []

def is_token_safe(token):
    try:
        if token['liquidity'] < 5000:
            return False
        if 'owner' in token and token['owner'] != "":
            return False
        return True
    except:
        return False

def verificar_valor_e_alertar(token_address, preco_compra):
    try:
        url = f"https://public-api.birdeye.so/public/price?address={token_address}"
        headers = {"x-api-key": API_KEY}
        r = requests.get(url, headers=headers)
        preco_atual = float(r.json()['data']['value'])
        if preco_atual >= preco_compra * LUCRO_MINIMO:
            messagebox.showinfo("💰 Alerta de Lucro!", f"Lucro de {LUCRO_MINIMO}x alcançado! Preço atual: ${preco_atual:.6f}")
        else:
            messagebox.showinfo("⏳ Ainda não...", f"Aguardando valorização... Preço atual: ${preco_atual:.6f}")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def monitorar_tokens():
    vistos = set()
    while True:
        tokens = get_new_tokens()
        for token in tokens:
            address = token['address']
            if address not in vistos and is_token_safe(token):
                vistos.add(address)
                texto = f"{token['name']} ({token['symbol']})\nPreço: ${token['price']:.8f}\nLiquidez: ${token['liquidity']:.2f}\nEndereço: {address}\n\n"
                caixa.insert(tk.END, texto)
        time.sleep(MONITOR_INTERVAL)

def criar_interface():
    global caixa, entrada_endereco, entrada_preco

    root = tk.Tk()
    root.title("Bot Solana Inteligente")
    root.geometry("600x500")

    caixa = tk.Text(root, height=20, width=70)
    caixa.pack(pady=10)

    tk.Label(root, text="Endereço do Token:").pack()
    entrada_endereco = tk.Entry(root, width=60)
    entrada_endereco.pack()

    tk.Label(root, text="Preço que pagou:").pack()
    entrada_preco = tk.Entry(root, width=20)
    entrada_preco.pack()

    def acionar_alerta():
        endereco = entrada_endereco.get()
        try:
            preco = float(entrada_preco.get())
            verificar_valor_e_alertar(endereco, preco)
        except:
            messagebox.showerror("Erro", "Digite um valor válido")

    tk.Button(root, text="Verificar lucro agora", command=acionar_alerta).pack(pady=10)

    threading.Thread(target=monitorar_tokens, daemon=True).start()
    root.mainloop()

criar_interface()
