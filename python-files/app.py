from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

app = Flask(__name__)

def generate_image(symbol, signal_type, entry_price, targets, stop_loss, theme):
    width, height = 768, 1152
    bg_color = "#1e1e1e" if theme == "dark" else "#ffffff"
    card_color = "#2c2c2c" if theme == "dark" else "white"
    text_color = "white" if theme == "dark" else "black"
    buy_color = "#16a34a"
    sell_color = "#dc2626"
    target_color = "#2563eb"

    font_path_bold = "arialbd.ttf"
    font_path = "arial.ttf"

    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    card_margin = 80
    card_radius = 50
    card_bbox = (card_margin, card_margin, width - card_margin, height - card_margin)
    draw.rounded_rectangle(card_bbox, radius=card_radius, fill=card_color)

    font_title = ImageFont.truetype(font_path_bold, 60)
    font_signal = ImageFont.truetype(font_path_bold, 48)
    font_price = ImageFont.truetype(font_path_bold, 48)
    font_small = ImageFont.truetype(font_path, 40)

    icons = {
        "buy": "↑",
        "sell": "↓",
        "target": "🎯",
        "sl": "🛡️",
        "gold": "🪙"
    }

    x_title = 150
    y = 120
    draw.text((x_title, y), f"{icons['gold']} {symbol}", font=font_title, fill=text_color)
    y += 80
    draw.text((x_title, y), f"{signal_type.upper()} SIGNAL", font=font_title, fill=text_color)

    y += 120
    block_height = 100
    block_margin = 40
    block_width = width - 2 * card_margin - 2 * block_margin
    block_x = card_margin + block_margin
    color_main = buy_color if signal_type.upper() == "BUY" else sell_color
    icon_main = icons["buy"] if signal_type.upper() == "BUY" else icons["sell"]

    draw.rounded_rectangle((block_x, y, block_x + block_width, y + block_height), radius=30, fill=color_main)
    draw.text((block_x + 40, y + 20), f"{icon_main} {signal_type.upper()}", font=font_signal, fill="white")
    draw.text((block_x + block_width - 200, y + 20), f"{entry_price:.2f}", font=font_price, fill="white")

    y += block_height + 30
    draw.rounded_rectangle((block_x, y, block_x + block_width, y + block_height), radius=30, fill=target_color)
    draw.text((block_x + 40, y + 20), f"{icons['target']} TARGET", font=font_signal, fill="white")
    for i, tgt in enumerate(targets):
        draw.text((block_x + block_width - 200, y + 20 + i * 35), f"{tgt:.2f}", font=font_small, fill="white")

    y += block_height + 60
    draw.rounded_rectangle((block_x, y, block_x + block_width, y + block_height), radius=30, fill=sell_color)
    draw.text((block_x + 40, y + 20), f"{icons['sl']} SL", font=font_signal, fill="white")
    draw.text((block_x + block_width - 200, y + 20), f"{stop_loss:.2f}", font=font_price, fill="white")

    date_str = datetime.now().strftime("%d %b %Y")
    draw.text((width - 250, height - 100), date_str, font=font_small, fill=text_color)

    os.makedirs("static/results", exist_ok=True)
    filename = f"static/results/{signal_type.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    image.save(filename)
    return filename

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        symbol = request.form["symbol"]
        signal_type = request.form["signal_type"]
        entry_price = float(request.form["entry_price"])
        targets = [float(t.strip()) for t in request.form["targets"].split(",")]
        stop_loss = float(request.form["stop_loss"])
        theme = request.form["theme"]

        image_path = generate_image(symbol, signal_type, entry_price, targets, stop_loss, theme)
        return render_template("index.html", image_path=image_path)

    return render_template("index.html", image_path=None)

if __name__ == "__main__":
    app.run(debug=True)