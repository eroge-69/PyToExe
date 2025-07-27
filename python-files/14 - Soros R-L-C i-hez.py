import tkinter as tk
import math

def rajzol():
    global f,vonal,uRmax,uLmax,uCmax,ueszogmax,fmax,imax,XLmax,XCmax

    if vonal is not None:
        vaszon.delete('all')
    vonal = 'van'



#Számolás
    XL = 2 * math.pi * f * L
    XC = 1 / (2 * math.pi * f * C)
    Z = math.sqrt(R * R + (XL - XC)*(XL - XC))
#    print(f,XL,XC,Z)
    i = u / Z
    uR = R * i
    uL = XL * i
    uC = XC * i
    ue = math.sqrt(uR * uR + (uL - uC) * (uL - uC))
#    print(i,uR,uL,uC,ue)

    max = 300  # pixel
    ihossz = i * 500 * max / 30
    iszog_fok = 0
    iszog_rad = math.radians(iszog_fok)
    uRhossz = uR * max / 5
    uRszog_fok = 0
    uRszog_rad = math.radians(uRszog_fok)
    uLhossz = uL * max / 5
    uLszog_fok = 90
    uLszog_rad = math.radians(uLszog_fok)
    uChossz = uC * max / 5
    uCszog_fok = -90
    uCszog_rad = math.radians(uCszog_fok)
    ueszog_rad = math.atan((uL - uC) / uR)
    ueszog_fok = math.degrees(ueszog_rad)
    if uR >= uRmax:
        uRmax = uR
        uLmax = uL
        uCmax = uC
        ueszogmax = ueszog_fok
        fmax = f
        imax = i
        XLmax = XL
        XCmax = XC

# Végpontok számítása pixel korrekcióval
    uRx1 = x0 + uRhossz * math.cos(uRszog_rad)
    uRy1 = y0 - uRhossz * math.sin(uRszog_rad)  # mínusz, mert a képernyő y lefelé nő
    ix1 = x0 + ihossz * math.cos(iszog_rad)
    iy1 = y0 - ihossz * math.sin(iszog_rad)  # mínusz, mert a képernyő y lefelé nő
    uLx1 = x0 + uLhossz * math.cos(uLszog_rad)
    uLy1 = y0 - uLhossz * math.sin(uLszog_rad)  # mínusz, mert a képernyő y lefelé nő
    uCx1 = x0 + uChossz * math.cos(uCszog_rad)
    uCy1 = y0 - uChossz * math.sin(uCszog_rad)  # mínusz, mert a képernyő y lefelé nő
    uex1 = x0 + max * math.cos(ueszog_rad)
    uey1 = y0 - max * math.sin(ueszog_rad)


# Nyilak rajzolása
    vaszon.create_line(x0, y0, uRx1, uRy1, fill='red', width=5, arrow=tk.LAST) # piros nyíl (uR)
    vaszon.create_text(uRx1, uRy1 + 10, text="uR", fill='red', font=('Arial', 12, 'bold'))
    vaszon.create_line(x0, y0, ix1, iy1, fill='green', width=5, arrow=tk.LAST) # zöld nyíl (áramerősség)
    vaszon.create_text(ix1, iy1 + 10, text="i", fill='green', font=('Arial', 12, 'bold'))
    vaszon.create_line(x0, y0, uLx1, uLy1, fill='blue', width=5, arrow=tk.LAST) # kék nyíl (uL)
    vaszon.create_text(uLx1 + 20, uLy1, text="uL", fill='blue', font=('Arial', 12, 'bold'))
    vaszon.create_line(x0, y0, uCx1, uCy1, fill='orange', width=5, arrow=tk.LAST) # sárga nyíl (uC)
    vaszon.create_text(uCx1 + 20, uCy1, text="uC", fill='orange', font=('Arial', 12, 'bold'))
    vaszon.create_line(x0, y0, uex1, uey1, fill='purple', width=5, arrow=tk.LAST) # lila nyíl (ug)
    vaszon.create_text(uex1 + 20, uey1, text="ug", fill='purple', font=('Arial', 12, 'bold'))
    vaszon.create_text(450, 280, text="f = "+str(f)+" Hz", fill='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(480, 100, text="ug = 5 V", fill='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(500, 120, text="R = 220 Ohm", fill='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(495, 140, text="L = 100 mH", fill='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(486, 160, text="C = 10 uF", fill='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(450, 400, text="uR = "+str(round(uR,2))+" V", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(450, 420, text="uL = "+str(round(uL,2))+" V", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(450, 440, text="uC = "+str(round(uC,2))+" V", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(450, 460, text="i = "+str(round(1000*i,2))+" mA", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(450, 480, text="XL = "+str(round(XL))+" Ohm", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(450, 500, text="XC = "+str(round(XC))+" Ohm", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(450, 520, text="fi = "+str(round(ueszog_fok))+" fok", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(607, 380, text="Rezonancia:", fill='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(600, 400, text="uR = "+str(round(uRmax,2))+" V", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(600, 420, text="uL = "+str(round(uLmax,2))+" V", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(600, 440, text="uC = "+str(round(uCmax,2))+" V", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(600, 460, text="i = "+str(round(1000*imax,2))+" mA", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(600, 480, text="XL = "+str(round(XLmax))+" Ohm", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(600, 500, text="XC = "+str(round(XCmax))+" Ohm", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(600, 520, text="fi = "+str(round(ueszogmax))+" fok", fill ='black', font=('Arial', 12, 'bold'))
    vaszon.create_text(600, 540, text="f = "+str(fmax)+" Hz", fill ='black', font=('Arial', 12, 'bold'))



# Frekvencia emelés 1 Hz-zel és vége vizsgálat

    f = f + 1
    if f > 550:
        return
    ablak.after(100, rajzol)


# Futtatás

# Ablak létrehozása
ablak = tk.Tk()
ablak.title("Soros R-L-C áramkör (áram és feszültségek)")

# Vászon létrehozása
vaszon = tk.Canvas(ablak, width=700, height=700, bg='white')
vaszon.pack()

f = 10  # 10 Hz-től indulunk
vonal = None

# Alapadatok

u = 5
L = 0.1
C = 0.00001
R = 220
uRmax = 0
uLmax = 0
uCmax = 0
ueszogmax = 0
imax = 0
fmax = 0
XLmax = 0
XCmax = 0

# Kezdőpont
x0, y0 = 80, 350

vaszon.create_text(350, 250, text="Soros R-L-C kör vizsgálata,", fill ='black', font=('Arial', 24, 'bold'))
vaszon.create_text(350, 300, text="rezonancia frekvencia keresés", fill ='black', font=('Arial', 24, 'bold'))
vaszon.create_text(350, 400, text="R = 220 Ohm, L = 100 mH, C = 10 uF, f = 10 ... 550 Hz", fill ='black', font=('Arial', 16, 'bold'))

# Start gomb
gomb = tk.Button(ablak, text="Start", command=rajzol)
gomb.pack(pady=5)

ablak.mainloop()