//+------------------------------------------------------------------+
//|               HABOL Chart Display                                |
//+------------------------------------------------------------------+
#property strict

//-------------------- INPUTS --------------------
input int FontSize       = 12;
input string FontName    = "Arial";
input ENUM_COLOR BullColor = clrLime;
input ENUM_COLOR BearColor = clrRed;

//-------------------- GLOBALS --------------------
string objName = "HABOL_CHART_DISPLAY";

//-------------------- FUNCTION: UPDATE DISPLAY --------------------
void UpdateDisplay()
{
   // Ambil info candle terakhir
   double o = iOpen(_Symbol,PERIOD_CURRENT,0);
   double h = iHigh(_Symbol,PERIOD_CURRENT,0);
   double l = iLow(_Symbol,PERIOD_CURRENT,0);
   double c = iClose(_Symbol,PERIOD_CURRENT,0);

   // Trend sederhana
   string trend="Neutral";
   color tColor=clrWhite;
   if(c>o){ trend="Bullish"; tColor=BullColor;}
   else if(c<o){ trend="Bearish"; tColor=BearColor;}

   // Buat text
   string txt;
   txt=StringFormat("HABOL DISPLAY\nCandle: %s\nO: %.5f H: %.5f\nL: %.5f C: %.5f\nTrend: %s",
                    EnumToString(Period()),o,h,l,c,trend);

   // Jika objek belum ada, buat baru
   if(ObjectFind(0,objName)<0)
   {
      ObjectCreate(0,objName,OBJ_LABEL,0,0,0);
      ObjectSetInteger(0,objName,OBJPROP_CORNER,CORNER_LEFT_LOWER);
      ObjectSetInteger(0,objName,OBJPROP_XDISTANCE,10);
      ObjectSetInteger(0,objName,OBJPROP_YDISTANCE,10);
      ObjectSetInteger(0,objName,OBJPROP_FONTSIZE,FontSize);
      ObjectSetString(0,objName,OBJPROP_FONT,FontName);
      ObjectSetInteger(0,objName,OBJPROP_COLOR,tColor);
   }

   // Update text & warna
   ObjectSetString(0,objName,OBJPROP_TEXT,txt);
   ObjectSetInteger(0,objName,OBJPROP_COLOR,tColor);
}

//-------------------- ON INIT --------------------
int OnInit()
{
   Print("HABOL Chart Display Initialized");
   return(INIT_SUCCEEDED);
}

//-------------------- ON TICK --------------------
void OnTick()
{
   UpdateDisplay();
}

//-------------------- ON DEINIT --------------------
void OnDeinit(const int reason)
{
   ObjectDelete(objName);
}
import tkinter as tk
from tkinter import ttk
import time
import requests
from datetime import datetime, timedelta
import threading

# Lokasi kamu (contoh Jakarta)
LATITUDE = -6.2
LONGITUDE = 106.8
METHOD = 2  # metode perhitungan waktu sholat
GOLD_REFRESH = 5000  # ms

# Ambil harga Gold
def get_gold_price():
    try:
        response = requests.get('https://api.metals.live/v1/spot')
        data = response.json()
        for item in data:
            if 'xau' in item:
                return item['xau']
    except:
        return "N/A"

# Ambil waktu sholat dari API
def get_prayer_times():
    try:
        url = f"http://api.aladhan.com/v1/timings?latitude={LATITUDE}&longitude={LONGITUDE}&method={METHOD}"
        r = requests.get(url)
        data = r.json()['data']['timings']
        prayer_times = {}
        for key, val in data.items():
            h, m = map(int, val.split(':'))
            prayer_times[key] = datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
        return prayer_times
    except:
        return {}

# Tentukan sesi trading aktif
def get_session():
    hour = int(time.strftime('%H'))
    if 7 <= hour < 9:
        return "Tokyo"
    elif 14 <= hour < 19:
        return "London/NY"
    elif 19 <= hour < 22:
        return "New York"
    elif 5 <= hour < 6:
        return "Sydney"
    else:
        return "Tenang"

# Update GUI
def update():
    now = datetime.now()
    time_label.config(text=f"🕒 {now.strftime('%H:%M:%S WIB')}")

    session = get_session()
    session_display = ""
    if session_vars["Tokyo"].get():
        color = "orange" if session=="Tokyo" else "black"
        session_display += f"🌍 Tokyo\n"
        session_label.config(fg=color)
    if session_vars["London/NY"].get():
        color = "red" if session=="London/NY" else "black"
        session_display += f"🌍 London/NY\n"
        session_label.config(fg=color)
    if session_vars["New York"].get():
        color = "red" if session=="New York" else "black"
        session_display += f"🌍 New York\n"
        session_label.config(fg=color)
    if session_vars["Sydney"].get():
        color = "black"
        session_display += f"🌍 Sydney\n"
        session_label.config(fg=color)

    session_label.config(text=session_display.strip())

    gold_label.config(text=f"🥇 XAUUSD: {get_gold_price()}")

    # Waktu sholat & countdown
    next_prayer = None
    min_diff = timedelta(days=1)
    for name, t in prayer_times.items():
        diff = t - now
        if diff.total_seconds() > 0 and diff < min_diff:
            min_diff = diff
            next_prayer = (name, t)
    if next_prayer:
        diff = next_prayer[1] - now
        hours, remainder = divmod(int(diff.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        countdown_label.config(text=f"🕌 {next_prayer[0]} in {hours}h {minutes}m {seconds}s")
    else:
        countdown_label.config(text="🕌 Semua sholat selesai")

    root.after(1000, update)
    root.after(GOLD_REFRESH, lambda: gold_label.config(text=f"🥇 XAUUSD: {get_gold_price()}"))

# GUI
root = tk.Tk()
root.title("Habol Timer")
root.geometry("320x250")
root.attributes('-topmost', True)

time_label = tk.Label(root, font=("Helvetica", 12))
time_label.pack(pady=2)

session_label = tk.Label(root, font=("Helvetica", 12))
session_label.pack(pady=2)

gold_label = tk.Label(root, font=("Helvetica", 12))
gold_label.pack(pady=2)

countdown_label = tk.Label(root, font=("Helvetica", 12))
countdown_label.pack(pady=2)

# Toggle ontop
def toggle_ontop():
    current = root.attributes('-topmost')
    root.attributes('-topmost', not current)
toggle_button = ttk.Button(root, text="Toggle OnTop", command=toggle_ontop)
toggle_button.pack(pady=5)

# Centang sesi trading
session_vars = {
    "Tokyo": tk.BooleanVar(value=True),
    "London/NY": tk.BooleanVar(value=True),
    "New York": tk.BooleanVar(value=True),
    "Sydney": tk.BooleanVar(value=True)
}
session_frame = tk.LabelFrame(root, text="Tampilkan Sesi")
session_frame.pack(pady=5)
for s, var in session_vars.items():
    tk.Checkbutton(session_frame, text=s, variable=var).pack(anchor="w")

# Ambil data sholat di background
def fetch_prayer():
    global prayer_times
    prayer_times = get_prayer_times()
threading.Thread(target=fetch_prayer).start()

update()
root.mainloop()
