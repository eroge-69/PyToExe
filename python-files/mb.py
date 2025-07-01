import ctypes
from datetime import datetime

def to_jalali(gy, gm, gd):
    g_d_m = [0,31,59,90,120,151,181,212,243,273,304,334]
    if(gy > 1600):
        jy=979
        gy-=1600
    else:
        jy=0
        gy-=621
    if(gm > 2):
        gy2=gy+1
    else:
        gy2=gy
    days=(365*gy) + ((gy2+3)//4) - ((gy2+99)//100) + ((gy2+399)//400) - 80 + gd + g_d_m[gm-1]
    jy+=33*(days//12053)
    days%=12053
    jy+=4*(days//1461)
    days%=1461
    if(days > 365):
        jy+= (days-1)//365
        days=(days-1)%365
    if(days < 186):
        jm=1+(days//31)
        jd=1+(days%31)
    else:
        jm=7+((days-186)//30)
        jd=1+((days-186)%30)
    return jy, jm, jd

now = datetime.now()
gy, gm, gd = now.year, now.month, now.day
jy, jm, jd = to_jalali(gy, gm, gd)

message = f"📅 Gregorian: {gy}-{gm:02}-{gd:02}\n📅 Persian: {jy}/{jm}/{jd}"

ctypes.windll.user32.MessageBoxW(0, message, "Date Viewer", 0)
