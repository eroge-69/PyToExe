import math
import sys
import json
from datetime import datetime, timezone, timedelta
# Use built-in `urllib` instead of `requests` (no extra installs)
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# --------------------------
# Configuration Constants
# --------------------------
SIGMA = 5.67e-8  # Stefan-Boltzmann constant (W/m²K⁴)
# Expiration Time: 23:59:59 HKT, 31 Dec 2025 (HKT = UTC+8)
EXPIRATION_HKT = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone(timedelta(hours=8)))
# Public UTC time APIs (no API key required; built-in urllib compatible)
UTC_TIME_APIS = [
    "https://worldtimeapi.org/api/timezone/Etc/UTC",  # Reliable free API
    "https://api.timezonedb.com/v2.1/get-time-zone?key=B5U5N1G46U9S&format=json&by=zone&zone=Etc/UTC"  # Backup (free key)
]
# HKT timezone definition (UTC+8, no external dependencies)
HKT_TZ = timezone(timedelta(hours=8))

# 公制 ↔ 英制對照 (Unmodified)
IMPERIAL_TABLE = {
    4.76:'3/16"', 6.35:'1/4"', 7.94:'5/16"', 9.52:'3/8"', 12.7:'1/2"',
    15.88:'5/8"', 19.05:'3/4"', 22.22:'7/8"', 25.4:'1"', 28.58:'1 1/8"',
    31.75:'1 1/4"', 34.92:'1 3/8"', 38.1:'1 1/2"', 41.28:'1 5/8"', 50.8:'2"',
    53.98:'2 1/8"', 66.68:'2 5/8"', 76.2:'3"', 101.6:'4"', 104.78:'4 1/8"',
    10.2:'1/8"', 13.5:'1/4"', 17.2:'3/8"', 21.3:'1/2"', 26.9:'3/4"',
    33.7:'1"', 42.4:'1 1/4"', 48.3:'1 1/2"', 60.3:'2"', 76.1:'2 1/2"',
    88.9:'3"', 101.6:'3 1/2"', 114.3:'4"', 139.7:'5"', 165.1:'6"',
    219.1:'8"', 273:'10"', 323.9:'12"', 355.6:'14"', 406.4:'16"'
}

# 管系數據 (Unmodified)
PIPE_SETS = {
    1: ("Steel Tube (BS 1387)",
        [10.2, 13.5, 17.2, 21.3, 26.9, 33.7, 42.4, 48.3, 60.3, 76.1, 88.9,
         101.6, 114.3, 139.7, 165.1, 219.1, 273, 323.9, 355.6, 406.4]),
    2: ("Copper Tube (AS 1571)",
        [4.76, 6.35, 7.94, 9.52, 12.7, 15.88, 19.05, 22.22, 25.4, 28.58,
         31.75, 34.92, 38.1, 41.28, 50.8, 53.98, 66.68, 76.2, 101.6, 104.78])
}

# 默認參數 (Unmodified)
DEFAULTS = {
    "T_fluid": 7,
    "Td": 27,# 26.99
    "k": 0.036,
    "ε": 0.95,
    "T_amb": 28.9,#28.9,
    "wind": 0.0
}

# --------------------------
# New Function: Get HKT via Public Time APIs (No Extra Libraries)
# --------------------------
def get_hkt_internet_time():
    """
    Fetch HKT (Hong Kong Time, UTC+8) using public UTC time APIs (built-in urllib only).
    No external libraries (ntplib/requests) required.
    Falls back to system time → HKT if APIs fail.
    """
    # Add user-agent to avoid API blocking (some APIs reject empty user-agents)
    headers = {"User-Agent": "Python/urllib (thermal insulation calculator)"}
    
    # Try each UTC API in order
    for api_url in UTC_TIME_APIS:
        try:
            # Send request to API (with headers)
            request = Request(api_url, headers=headers)
            with urlopen(request, timeout=8) as response:
                # Read and parse JSON response
                api_data = json.loads(response.read().decode("utf-8"))
                
                # Extract UTC time (handle different API response formats)
                if "datetime" in api_data:
                    # WorldTimeAPI format (e.g., "2024-05-20T12:34:56.789Z")
                    utc_str = api_data["datetime"].split(".")[0]  # Remove milliseconds
                    utc_time = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%S")
                elif "formatted" in api_data:
                    # TimezoneDB API format (e.g., "2024-05-20 12:34:56")
                    utc_time = datetime.strptime(api_data["formatted"], "%Y-%m-%d %H:%M:%S")
                else:
                    continue  # Skip if time field not found
                
                # Add UTC timezone and convert to HKT
                utc_time_tz = utc_time.replace(tzinfo=timezone.utc)
                hkt_time = utc_time_tz.astimezone(HKT_TZ)
                return hkt_time
        
        # Handle API errors (timeouts, HTTP errors, invalid JSON)
        except (URLError, HTTPError, json.JSONDecodeError, KeyError, ValueError):
            continue  # Try next API if current fails
    
    # Fallback: Convert local system time to HKT (if all APIs fail)
    local_tz_aware = datetime.now().astimezone()  # Get local time with timezone
    hkt_fallback = local_tz_aware.astimezone(HKT_TZ)
    return hkt_fallback

# --------------------------
# Original Helper Functions (Unmodified)
# --------------------------
def prompt(prompt, default, cast=float, rng=None):
    val = cast(input(f"{prompt} (預設 {default}): ") or default)
    if rng and (val < rng[0] or val > rng[1]):
        raise ValueError("超出範圍")
    return val

def combined_h(T_s, T_a, v, ε):
    Ts, Ta = T_s + 273.15, T_a + 273.15
    h_rad = ε * SIGMA * (Ts + Ta) * (Ts ** 2 + Ta ** 2)
    delta = abs(T_s - T_a)
    h_conv = 25 + 12 * math.sqrt(v) if v > 0.1 else 1.31 * delta ** (1 / 3)
    return h_conv + h_rad

# --------------------------
# Main Logic (Silent Expiry Check + No Dependencies)
# --------------------------
def main():
    # Step 1: Silent HKT fetch + expiry check (no user-facing messages)
    current_hkt = get_hkt_internet_time()
    if current_hkt > EXPIRATION_HKT:
        print("The program is expired.")
        sys.exit(1)

    # Step 2: Original Calculation Workflow (Unmodified)
    print("=== 防凝露外表面溫度 & 熱損失表 (逐毫米) ===")
    key = int(input("選擇管系 (1:Steel[預設]/2:Copper): ") or 1)
    name, diameters = PIPE_SETS[key]
    T_fluid = prompt("管內流體溫度 °C", DEFAULTS["T_fluid"], rng=(0, 30))
    Td = DEFAULTS["Td"]
    k = prompt("導熱率 W/mK", DEFAULTS["k"], rng=(0.02, 0.06))
    ε = prompt("表面放射率", DEFAULTS["ε"], rng=(0, 0.98))
    T_amb = DEFAULTS["T_amb"]
    wind = prompt("風速 m/s", DEFAULTS["wind"], rng=(0, 3))
    min_thick = int(prompt("厚度起始 mm", 10))
    max_thick = int(prompt("厚度結束 mm", 75))
    summary = []

    # Use HKT for report filename (consistent time standard)
    report_filename = f"insulation_report_{current_hkt.strftime('%Y%m%d%H%M%S')}.txt"
    
    with open(report_filename, "w", encoding="utf-8") as f:
        # 報告開頭資訊
        f.write("=== INSULATION CALCULATION REPORT ===\n")
        f.write(f"Python Version: {sys.version.split()[0]}\n")
        f.write(f"Performed Date & Time (HKT): {current_hkt.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("DISCLAIMER: Results are theoretical; consult local standards.\n\n")
        f.write("=== CALCULATION PARAMETERS ===\n")
        f.write(f"Fluid Temp   : {T_fluid} °C\n")
        f.write(f"Dew Point    : {Td} °C\n")
        f.write(f"Conductivity : {k}  W/m·K\n")
        f.write(f"Emissivity   : {ε}\n")
        f.write(f"Ambient Temp : {T_amb} °C\n")
        f.write(f"Wind Speed   : {wind} m/s\n")
        f.write(f"Range        : {min_thick}-{max_thick} mm\n\n")

        # 原始管道計算邏輯
        for d in diameters:
            inch = IMPERIAL_TABLE.get(d, "")
            f.write(f"{inch} ({d} mm)\n")
            f.write("Thickness  Surface Temp  Heat Loss  Status\n")
            min_safe = None
            for t in range(min_thick, max_thick + 1):
                t_m = t / 1000
                r_i = d / 2000
                r_o = r_i + t_m
                R_ins = math.log(r_o / r_i) / (2 * math.pi * k)
                h = combined_h(T_fluid, T_amb, wind, ε)
                loss = (T_fluid - T_amb) / (R_ins + 1 / (h * 2 * math.pi * r_o))
                Ts = T_fluid - loss * R_ins
                marker = "OK" if Ts >= Td and min_safe is None else ""
                if Ts >= Td and min_safe is None:
                    min_safe = t
                    summary.append((inch, d, t, loss))
                f.write(f"{t:<10} {Ts:>6.2f} °C {loss*1000:>7.1f} W/km{marker}\n")
            f.write("\n")

        # 計算摘要
        f.write("==== MINIMUM THICKNESS & THERMAL LOSSES SUMMARY ====\n")
        f.write("Dia.               Min. Thickness  Thermal Losses\n")
        for inch, d, t, loss in summary:
            f.write(f"{inch:<12} ({d} mm)  {t:>3} mm        {loss*1000:.1f} W/km\n")
    
    print(f"\n✅ 結果已寫入：{report_filename}")

if __name__ == "__main__":
    main()