import tkinter as tk
import MetaTrader5 as mt5
import re
import time
import threading

# Connexion
if not mt5.initialize():
    print("Erreur de connexion à MetaTrader 5 :", mt5.last_error())
else:
    print("Connecté à MetaTrader 5")

symbol_map = {
    "GOLD": "XAUUSD",
    # Ajouter plus de mappings si besoin
}

def send_trade():
    lignes = text_box.get("1.0", tk.END).strip().split("\n")
    if not lignes:
        label_resultat.config(text="Erreur : message vide.")
        return

    first_line = lignes[0].strip().upper()
    match = re.match(r"(SELL|BUY)\s+([A-Z]+)\s+([\d.]+)\s*-\s*([\d.]+)", first_line)

    if not match:
        label_resultat.config(text="Format de la 1ʳᵉ ligne invalide.")
        return

    direction_str, symbol_name, price_min, price_max = match.groups()
    symbol = symbol_map.get(symbol_name)

    if not symbol:
        label_resultat.config(text=f"Symbole inconnu : {symbol_name}")
        return

    direction = mt5.ORDER_TYPE_SELL if direction_str == "SELL" else mt5.ORDER_TYPE_BUY
    price_min = float(price_min) - 5  # Marge inférieure
    price_max = float(price_max) + 5  # Marge supérieure


    tp_list = []
    sl = None
    for ligne in lignes[1:]:
        ligne = ligne.replace(" ", "").lower()
        if "takeprofit" in ligne:
            try:
                val = float(ligne.split("=")[1])
                tp_list.append(val)
            except:
                pass
        elif "stoploss" in ligne:
            try:
                sl = float(ligne.split("=")[1])
            except:
                pass

    if not tp_list:
        label_resultat.config(text="Erreur : aucun TakeProfit détecté.")
        return

    if not mt5.symbol_select(symbol, True):
        label_resultat.config(text=f"Erreur : symbole {symbol} indisponible.")
        return

    # Lancer l’attente dans un thread séparé (pour ne pas bloquer l’interface)
    threading.Thread(target=wait_for_price_and_execute, args=(symbol, direction, price_min, price_max, tp_list, sl)).start()
    label_resultat.config(text="⏳ Attente que le prix entre dans la zone...")

def wait_for_price_and_execute(symbol, direction, price_min, price_max, tp_list, sl):
    while True:
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            continue

        current_price = tick.ask if direction == mt5.ORDER_TYPE_BUY else tick.bid
        print(f"[INFO] Prix actuel : {current_price}")

        if price_min <= current_price <= price_max:
            print("💡 Prix dans la zone, envoi du trade.")
            break
        time.sleep(2)

    price = current_price
    success = 0
    for tp in tp_list:
        order = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": 0.1,
            "type": direction,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 10,
            "magic": 123456,
            "comment": f"Zone Entry TP={tp}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(order)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            success += 1
        else:
            print(f"Erreur ordre TP={tp} : code {result.retcode}")

    # Afficher résultat dans interface (depuis le thread principal)
    def update_label():
        if success > 0:
            label_resultat.config(text=f"✅ {success} ordre(s) exécuté(s) avec succès.")
        else:
            label_resultat.config(text="❌ Aucun ordre n’a pu être exécuté.")
    root.after(0, update_label)

# Interface
root = tk.Tk()
root.title("Assistant Trading")

text_box = tk.Text(root, height=10, width=50)
text_box.pack(pady=10)

bouton = tk.Button(root, text="Envoyer le trade", command=send_trade)
bouton.pack(pady=5)

label_resultat = tk.Label(root, text="")
label_resultat.pack(pady=10)

root.mainloop()
