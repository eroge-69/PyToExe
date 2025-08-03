import requests, time
from datetime import datetime, timezone

WEBHOOK_URL = "https://discord.com/api/webhooks/1401615792348463276/brZAjXMXaSoKdJAtFAWvUblrTOJZ_rn_R8rRTgaUz2g7OVgzVTU7SetqIokOqqy0eUF7"
CREATOR_NAME = "Fores"  # Aquí pones el nombre del creador

FLAGS = {"USD": "🇺🇸", "VES": "🇻🇪", "COP": "🇨🇴", "PEN": "🇵🇪", "MXN": "🇲🇽"}
SYMBOLS = {"USD": "$", "VES": "bs", "COP": "mil", "PEN": "so", "MXN": "mx"}

BASE = {
    "1000 Robux": 8,
    "TIKTOK 1 000 followers": 6,
    "TIKTOK 10 000 likes": 6,
    "TIKTOK 5 000 saves": 5,
    "TIKTOK 100 000 views": 6,
    "TIKTOK 2 000 shares": 6,
    "TIKTOK 100 custom comments": 7,
    "INSTAGRAM 1 000 followers": 6,
    "INSTAGRAM 10 000 likes": 6,
    "INSTAGRAM 50 000 views": 6,
    "INSTAGRAM 100 custom comments": 6
}

def get_rates():
    try:
        print("[DEBUG] Contactando API...")
        data = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10).json()
        rates = {k: data["rates"][k] for k in ["VES", "COP", "PEN"]}
        print("[DEBUG] Tasas obtenidas:", rates)
        return rates
    except Exception as e:
        print("[ERROR] No se pudo obtener tasas:", e)
        return None

def clean(num, cur):
    """Quita decimales cuando solo hay .0 y formatea COP"""
    if cur == "COP":
        return f"{int(num / 1000)}mil"
    elif cur in ("VES", "COP"):
        return str(int(round(num)))
    return str(int(num) if num == int(num) else round(num, 2))

def build_menu(cur, rate):
    today = datetime.now(timezone.utc).strftime("%d/%m/%Y")
    flag, sym = FLAGS[cur], SYMBOLS[cur]
    lines = [f"{flag} **PRECIOS {cur}** {flag}"]
    lines.append(f"Tonoto Shop 🐱  Menu - {today}\n")
    lines.append("💎 **Robux**")

    rob = clean(BASE["1000 Robux"] * rate, cur)
    if cur == "USD":
        lines.append(f"1000 Robux = {rob} {sym}")
    else:
        lines.append(f"1000 Robux = {rob} {sym} (8 USD)")
    lines.append("")

    lines.append("🚀 **Social Boost** 🚀\n")

    sections = {
        "📱 TIKTOK": [
            "1 000 followers", "10 000 likes", "5 000 saves",
            "100 000 views", "2 000 shares", "100 custom comments"
        ],
        "📸 INSTAGRAM": [
            "1 000 followers", "10 000 likes", "50 000 views", "100 custom comments"
        ]
    }

    for platform, items in sections.items():
        lines.append(platform)
        for item in items:
            key = f"{platform.split()[1]} {item}"
            usd = BASE[key]
            local = clean(usd * rate, cur)
            if cur == "USD":
                lines.append(f"• {item} → {local} {sym}")
            else:
                lines.append(f"• {item} → {local} {sym} ({usd} USD)")
        lines.append("")
    lines.append("₊✩‧₊˚౨ৎ˚₊✩‧₊ ✨")
    return "\n".join(lines)

def send(text):
    print(f"[DEBUG] Enviando: {text[:60]}...")
    r = requests.post(WEBHOOK_URL, json={"content": text})
    if r.status_code in (200, 204):
        print("[DEBUG] ✅ Enviado")
    else:
        print("[ERROR] ❌ Falló:", r.status_code, r.text)

def main():
    print(f"by: {CREATOR_NAME}")
    rates = get_rates()
    if rates is None:
        return

    rates.update({"USD": 1, "MXN": 22})
    currencies = ["USD", "VES", "COP", "PEN", "MXN"]

    # 1) Separador global + creador
    print("[DEBUG] Enviando separador global")
    send(f"|-------------------|\n**MENU BY {CREATOR_NAME.upper()}**")

    # 2) Titular con fecha
    today = datetime.now(timezone.utc).strftime("%d/%m/%Y")
    print("[DEBUG] Enviando titular")
    send(f"📅 **PRECIOS FECHA - {today}**")

    # 3) Menús + separador individual
    for cur in currencies:
        print(f"[DEBUG] Construyendo menú {cur}")
        menu_text = build_menu(cur, rates[cur])
        send(menu_text)
        print(f"[DEBUG] Enviando separador para {cur}")
        send("-------------------")

    # 4) Cierre con cuenta regresiva
    for sec in range(5, 0, -1):
        print(f"Precios enviados, quitting... ({sec})")
        time.sleep(1)

if __name__ == "__main__":
    main()