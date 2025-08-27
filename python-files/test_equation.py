import math
import tkinter as tk




def on_submit():
    # Get values from text fields
    val1 = float(entry1.get())
    val2 = float(entry2.get())
    val3 = float(entry3.get())
    pitchCorr, rollCorr = tiltCorrection(val1,val2,val3)
    entry4.delete(0, tk.END)      # clear old value
    entry4.insert(0, str(pitchCorr)) # insert new value
    entry5.delete(0, tk.END)      # clear old value
    entry5.insert(0, str(rollCorr)) # insert new value

    

# Create main window
root = tk.Tk()
root.title("Corrections")
root.geometry("240x210")

# Text fields
tk.Label(root, text="Heading :").grid(row=0, column=0, padx=5, pady=5)
entry1 = tk.Entry(root)
entry1.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Pitch :").grid(row=1, column=0, padx=5, pady=5)
entry2 = tk.Entry(root)
entry2.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Roll :").grid(row=2, column=0, padx=5, pady=5)
entry3 = tk.Entry(root)
entry3.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="Pitch + :").grid(row=3, column=0, padx=5, pady=5)
entry4 = tk.Entry(root)
entry4.grid(row=3, column=1, padx=5, pady=5)

tk.Label(root, text="Gun Head :").grid(row=4, column=0, padx=5, pady=5)
entry5 = tk.Entry(root)
entry5.grid(row=4, column=1, padx=5, pady=5)

# Button
submit_btn = tk.Button(root, text="Calculate", command=on_submit)
submit_btn.grid(row=5, column=0, columnspan=2, pady=10)



def tiltCorrection(val1,val2,val3):

    Pitch = val2 * math.pi / 180
    Roll = val3 * math.pi / 180
    Head = val1 * math.pi / 180

    SinP = math.sin(Pitch)
    CosP = math.cos(Pitch)
    SinR = math.sin(Roll)
    CosR = math.cos(Roll)
    SinH = math.sin(Head)
    CosH = math.cos(Head)

    X1 = 0                     # must be zero  (Orgin)
    Y1 = 0                     # must be zero  (Orgin)
    Z1 = 0                     # must be zero  (Orgin)

    X2 = CosR * 100
    Y2 = SinR * SinP * 100
    Z2 = SinR * CosP * -100

    X3 = 0                     #  must be zero
    Y3 = CosP * 100
    Z3 = SinP * 100

    A = Y1 * (Z2 - Z3) + Y2 * (Z3 - Z1) + Y3 * (Z1 - Z2)
    B = Z1 * (X2 - X3) + Z2 * (X3 - X1) + Z3 * (X1 - X2)
    C = X1 * (Y2 - Y3) + X2 * (Y3 - Y1) + X3 * (Y1 - Y2)
    D = -(X1 * (Y2 * Z3 - Y3 * Z2) + X2 * (Y3 * Z1 - Y1 * Z3) + X3 * (Y1 * Z2 - Y2 * Z1))

    X4 = 100 * SinH         # -100 * SinH
    Y4 = 100 * CosH
    Z4 = 0

    if C != 0:
        Z4 = (D - A * X4 - B * Y4) / C
    else:
        Z4 = 0

    TiltCorrectionP = -math.atan(Z4 / 100) * 180 / math.pi

    #print(Z4)
    pitchValue = format(TiltCorrectionP, ".6f")
    print("Pitch+ = " ,pitchValue)



    Z4 = 0
    #-------------------  Roll
    Px = X4 * CosR - Z4 * SinR
    Pz = X4 * SinR + Z4 * CosR
    Py = Y4
    X4, Y4, Z4 = Px, Py, Pz
    #-------------------  pitch
    Pz = Z4 * CosP - Y1 * SinP
    Py = Z4 * SinP + Y4 * CosP
    Px = X4
    X4, Y4, Z4 = Px, Py, Pz
    #-------------------  Head   ' Not Required
    #Px = Y4 * SinH + X4 * CosH
    #Pz = Z4
    #-------------------- Calculate Z
    if C != 0:
        Pz = (D - A * Px - B * Py) / C
    else:
        Pz = 0

    #---------------------------------------------------------------------------------------------------------
    TiltCorrectionH = val1 + ((math.atan(Px / Py) * 180 / math.pi) - val1)

    print("val1 : ", val1)
    
    if val1 > 0 and val1 < 180 and TiltCorrectionH < 0 or val1 == 180:
        TiltCorrectionH += 180
    elif val1 > 180 and val1 < 360:
        TiltCorrectionH += 360
    elif val1 < 0 and val1 > -180:
        TiltCorrectionH += 360

    if TiltCorrectionH > 360:
        TiltCorrectionH -= 180

    #print(Pz)
    rollValue = format(TiltCorrectionH, ".6f")
    print("Gun Heading = ",rollValue)

    return pitchValue, rollValue






    


# Run the app
root.mainloop()