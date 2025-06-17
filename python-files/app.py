from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

def get_input(prompt, cast_type=str):
    while True:
        try:
            return cast_type(input(prompt).strip())
        except ValueError:
            print("❌ Invalid input. Try again.")

# === USER INPUT ===
print("📊 XAUUSD Signal Image Generator (PRO Version)\n")
symbol = input("Symbol (e.g. XAUUSD): ").strip().upper()
signal_type = input("Signal Type (BUY/SELL): ").strip().upper()
entry_price = get_input("Entry Price: ", float)
targets_input = input("Target(s) (comma-separated): ")
targets = [float(t.strip()) for t in targets_input.split(",")]
stop_loss = get_input("Stop Loss: ", float)
theme = input("Theme (light/dark): ").strip().lower()

# === COLORS & FONTS ===
if theme == "dark":
    bg_color = "#1e1e1e"
    card_color = "#2c2c2c"
    text_color = "white"
else:
    bg_color = "#ffffff"   # ← White background
    card_color = "white"
    text_color = "black"

buy_color = "#16a34a"    # Green for BUY
sell_color = "#dc2626"   # Red for SL
target_color = "#2563eb" # Blue for target

# Make sure these fonts are in the same folder or give full path
font_path_bold = "arialbd.ttf"
font_path = "arial.ttf"

# === CANVAS ===
width, height = 768, 1152
image = Image.new("RGB", (width, height), bg_color)
draw = ImageDraw.Draw(image)

# === CARD ===
card_margin = 80
card_radius = 50
card_bbox = (card_margin, card_margin, width - card_margin, height - card_margin)
draw.rounded_rectangle(card_bbox, radius=card_radius, fill=card_color)

# === FONTS ===
font_title = ImageFont.truetype(font_path_bold, 60)
font_signal = ImageFont.truetype(font_path_bold, 48)
font_price = ImageFont.truetype(font_path_bold, 48)
font_small = ImageFont.truetype(font_path, 40)

# === ICONS ===
icons = {
    "buy": "↑",
    "sell": "↓",
    "target": "🎯",
    "sl": "🛡️",
    "gold": "🪙"
}

# === TITLE ===
x_title = 150
y = 120
draw.text((x_title, y), f"{icons['gold']} {symbol}", font=font_title, fill=text_color)
y += 80
draw.text((x_title, y), f"{signal_type.upper()} SIGNAL", font=font_title, fill=text_color)

# === BUY/SELL BLOCK ===
y += 120
block_height = 100
block_margin = 40
block_width = width - 2 * card_margin - 2 * block_margin
block_x = card_margin + block_margin
color_main = buy_color if signal_type == "BUY" else sell_color
icon_main = icons['buy'] if signal_type == 'BUY' else icons['sell']

draw.rounded_rectangle((block_x, y, block_x + block_width, y + block_height), radius=30, fill=color_main)
draw.text((block_x + 40, y + 20), f"{icon_main} {signal_type}", font=font_signal, fill="white")
draw.text((block_x + block_width - 200, y + 20), f"{entry_price:.2f}", font=font_price, fill="white")

# === TARGET BLOCK ===
y += block_height + 30
draw.rounded_rectangle((block_x, y, block_x + block_width, y + block_height), radius=30, fill=target_color)
draw.text((block_x + 40, y + 20), f"{icons['target']} TARGET", font=font_signal, fill="white")
for i, tgt in enumerate(targets):
    draw.text((block_x + block_width - 200, y + 20 + i * 35), f"{tgt:.2f}", font=font_small, fill="white")

# === STOP LOSS BLOCK ===
y += block_height + 60
draw.rounded_rectangle((block_x, y, block_x + block_width, y + block_height), radius=30, fill=sell_color)
draw.text((block_x + 40, y + 20), f"{icons['sl']} SL", font=font_signal, fill="white")
draw.text((block_x + block_width - 200, y + 20), f"{stop_loss:.2f}", font=font_price, fill="white")

# === DATE STAMP ===
date_str = datetime.now().strftime("%d %b %Y")
draw.text((width - 250, height - 100), date_str, font=font_small, fill=text_color)

# === SAVE IMAGE ===
output_dir = "signals"
os.makedirs(output_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{signal_type.lower()}_{timestamp}.png"
filepath = os.path.join(output_dir, filename)
image.save(filepath)
print(f"✅ Image saved at: {filepath}")
