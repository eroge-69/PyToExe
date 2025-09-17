{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww29740\viewh16100\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import time\
import sys\
import os\
\
# ANSI: gr\'f8nn tekst\
GREEN = "\\033[92m"\
RESET = "\\033[0m"\
\
chat_log = [\
    "<ZeroGhost>: You logged in?",\
    "<NullByte>: Confirmed. Masking running.",\
    "<ZeroGhost>: Good. No traces.",\
    "<NullByte>: Always. What\'92s the package?",\
    "",\
    "<ZeroGhost>: Shipment. Same route as last time. Different payload.",\
    "<NullByte>: Risk level?",\
    "<ZeroGhost>: High. Eyes everywhere.",\
    "",\
    "<NullByte>: Payment?",\
    "<ZeroGhost>: 3 BTC upfront. Rest after drop.",\
    "<NullByte>: Price doubled last week. Market\'92s burning.",\
    "",\
    "<ZeroGhost>: Then don\'92t play.",\
    "<NullByte>: \'85 I\'92m in. Where\'92s the drop?",\
    "",\
    "<ZeroGhost>: Coordinates will self-delete in 60 sec.",\
    "*** ZeroGhost uploaded an encrypted file ***",\
    "",\
    "<NullByte>: Got it. See you in the shadows.",\
    "<ZeroGhost>: If you see me, it\'92s already too late."\
]\
\
last_message = "<ZeroGhost>: Payment received."\
\
def type_out(text, delay=0.05):\
    for ch in text:\
        sys.stdout.write(GREEN + ch + RESET)\
        sys.stdout.flush()\
        time.sleep(delay)\
    sys.stdout.write("\\n")\
    sys.stdout.flush()\
\
def blinking_cursor(duration=10):\
    start = time.time()\
    while time.time() - start < duration:\
        sys.stdout.write(GREEN + "_" + RESET)\
        sys.stdout.flush()\
        time.sleep(0.5)\
        sys.stdout.write("\\b \\b")  # fjern blink\
        sys.stdout.flush()\
        time.sleep(0.5)\
\
def main():\
    os.system("cls" if os.name == "nt" else "clear")\
    print(GREEN + "=== DARKNET CHAT NODE: ObsidianMarket/Room7 ===\\n" + RESET)\
    time.sleep(1)\
\
    for line in chat_log:\
        type_out(line, delay=0.03)\
        time.sleep(0.6)\
\
    # Blink i 10 sekunder, deretter STOPP blinkingen\
    blinking_cursor(10)\
\
    # Skriv siste melding uten videre blinking\
    type_out(last_message, delay=0.03)\
\
    # La vinduet st\'e5 \'e5pent\
    input("\\nPress ENTER to close...")\
\
if __name__ == "__main__":\
    main()\
}