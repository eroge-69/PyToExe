import os
from pathlib import Path
from datetime import datetime, timedelta
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import Image, ImageDraw, ImageFont
import textwrap

# ---------- Config ----------
SMTP_SERVER = "smtp.irco.com"
SMTP_PORT = 25
SMTP_USER = "hr_noreply@irco.com"

EXCEL_PATH = Path("Birthdetails.xlsx")
TEMPLATE_PATH = Path("C://Birthday//Template.png")
FONT_PATHS = [
    Path("ariblk.ttf"),
    Path("Arial.ttf"),
    Path("C://Windows//Fonts//arial.ttf")
]
OUTPUT_DIR = Path("C://Birthday")
CID_VALUE = "MyId1"

# ---------- Helpers ----------
def load_font(size=20):
    for fp in FONT_PATHS:
        if fp.exists():
            try:
                return ImageFont.truetype(str(fp), size)
            except Exception:
                pass
    return ImageFont.load_default()

def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def make_image(name: str, loc: str, out_path: Path):
    with Image.open(TEMPLATE_PATH) as im:
        back = im.copy()
    draw = ImageDraw.Draw(back)
    font = load_font(20)
    text = f"{name}, {loc}".strip().strip(",")
    wrapped = textwrap.wrap(text, width=50)

    W, H = back.size
    y = 500
    for line in wrapped:
        # Get text size using textbbox (Pillow 8.0+)
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (W - w) // 2
        draw.text((x, y), line, font=font, fill=(0, 50, 134))
        y += h + 20

    back.save(out_path)


def send_email_smtp(to_addr: str, bcc_list: list[str], subject: str, image_path: Path):
    recipients = [to_addr] + bcc_list if to_addr else bcc_list
    recipients = [r for r in recipients if r]

    msg = MIMEMultipart("related")
    msg["From"] = SMTP_USER
    msg["To"] = to_addr
    if bcc_list:
        msg["Bcc"] = ", ".join(bcc_list)
    msg["Subject"] = subject

    html = f"""
    <html>
      <body style="font-family:Arial; background-color:#F2F2F2; text-align:center;">
        <h2>🎉 Happy Birthday 🎂</h2>
        <p>Wishing you a wonderful day!</p>
        <img src="cid:{CID_VALUE}">
      </body>
    </html>
    """
    msg.attach(MIMEText(html, "html"))

    with open(image_path, "rb") as img:
        img_data = img.read()
    image = MIMEImage(img_data)
    image.add_header("Content-ID", f"<{CID_VALUE}>")
    msg.attach(image)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        # No login or TLS, assuming internal relay
        server.sendmail(SMTP_USER, recipients, msg.as_string())

# ---------- Main ----------
def run_birthday_wishes():
    print("Starting Birthday Wish Program (SMTP, Port 25)...")
    weekday = datetime.now().strftime("%A")
    days_to_cover = 2 if weekday == "Friday" else 0

    ensure_output_dir()
    df = pd.read_excel(EXCEL_PATH, engine="openpyxl")

    for d in range(days_to_cover + 1):
        target_dt = datetime.now() + timedelta(days=d)
        today_str = target_dt.strftime("%d/%m")
        year_str = target_dt.strftime("%Y")
        matches = []

        for i in range(len(df)):
            bday = pd.to_datetime(df["Birthday"].iloc[i]).strftime("%d/%m")
            if bday == today_str:
                matches.append(i)

        if not matches:
            print(f"No birthdays on {today_str}")
            continue

        for i in matches:
            name = df.at[i, "Name"]
            loc = df.at[i, "Location"]
            email = str(df.at[i, "Email"]).strip()
            mgr = str(df.at[i, "Manager_Mail"]).strip()
            status = str(df.at[i, "Status"]).strip()

            if status == year_str:
                print(f"Already wished {name} for {year_str}")
                continue

            to_addr = email if email.lower() != "none" else ""
            bcc = []
            for z in range(len(df)):
                em = str(df.at[z, "Email"]).strip()
                if em.lower() not in ("none", ""):
                    bcc.append(em)
            if mgr.lower() not in ("none", ""):
                bcc.append(mgr)
            bcc = list(set(bcc) - {to_addr})

            img_path = OUTPUT_DIR / f"Birthdaywish_{i}.png"
            make_image(name, loc, img_path)
            subject = ("Advance Birthday Wish - " if d else "Birthday Wish - ") + target_dt.strftime("%d %B, %Y")

            try:
                send_email_smtp(to_addr, bcc, subject, img_path)
                print(f"✅ Sent to {name} ({to_addr})")
                df.at[i, "Status"] = year_str
            except Exception as e:
                print(f"❌ Failed to send to {name}: {e}")

    df.to_excel(EXCEL_PATH, index=False)
    print("🎉 Done! Excel updated.")

if __name__ == "__main__":
    run_birthday_wishes()
