import math
import PySimpleGUI as sg
import time

sg.theme("DarkAmber")

layout = [[sg.Text("Calcolatrice triangolo rettangolo")],
          [sg.Text("Lunghezza cateto 1"), sg.Input(key='-CAT1-', enable_events=True)],
          [sg.Text("Lunghezza cateto 2"), sg.Input(key='-CAT2-', enable_events=True)],
          [sg.Text("Lunghezza ipotenusa"), sg.Input(key='-IPO-', enable_events=True)],
          [sg.HorizontalSeparator()],
          [sg.Text("Perimetro: ", key='-PERIMETRO-')],
          [sg.Text("Area: ", key='-AREA-')],
          [sg.Button("Calcola", key='-SUBMIT-')]]

window = sg.Window("Calcolatrice", layout)

cat1Output = False
cat2Output = False
ipoOutput = False

while True:
    time.sleep(0.01)
    event, values = window.read()

    if event in (sg.WIN_CLOSED, 'Exit'):
            break
    
    if event == '-SUBMIT-':

        cat1 = float()
        cat2 = float()
        ipo = float()

        if values['-CAT1-'] and values['-CAT2-'] and not values['-IPO-']:
            ipoOutput = True
            cat1 = float(values['-CAT1-'])
            cat2 = float(values['-CAT2-'])
            ipo = math.sqrt((cat1**2) + (cat2**2))
            window['-IPO-'].update(str(ipo))

        if values['-CAT1-'] and values['-IPO-'] and ((not values['-CAT2-']) or values['-CAT2-'] == "Errore"):
            cat2Output = True
            cat1 = float(values['-CAT1-'])
            ipo = float(values['-IPO-'])
            if ipo < cat1:
                window['-CAT2-'].update("Errore")
                continue
            else:
                cat2 = math.sqrt((ipo**2) - (cat1**2))
                window['-CAT2-'].update(str(cat2))

        if values['-IPO-'] and values['-CAT2-'] and ((not values['-CAT1-']) or values['-CAT1-'] == "Errore"):
            cat1Output = True
            ipo = float(values['-IPO-'])
            cat2 = float(values['-CAT2-'])
            if ipo < cat1:
                window['-CAT1-'].update("Errore")
                continue
            else:
                cat1 = math.sqrt((ipo**2) - (cat2**2))
                window['-CAT1-'].update(str(cat1))
        
        perimetro = cat1 + cat2 + ipo
        area = (cat1*cat2)/2

        window['-PERIMETRO-'].update(f"Perimetro: {perimetro}")
        window['-AREA-'].update(f"Area: {area}")
