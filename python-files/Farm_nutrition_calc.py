import FreeSimpleGUI as sg

sg.theme('DarkGreen6')  

# 1 layout of the window
layout = [
    [sg.Text("How many of the same plants do you have on the plot?:"), sg.Input(key='-INPUT1-')],
    [sg.Text('How many farm plots do you have?:'), sg.Input(key='-INPUT2-')],
    [sg.Text('How much nutrition does your item give?:'), sg.Input(key='-INPUT3-')],
    [sg.Text('How much nutrition does your plant take?:'), sg.Input(key='-INPUT4-')],
    [sg.Button('Calculate'), sg.Button('Exit')],
    [sg.Text('Amount of items:'), sg.Text('', size=(50, 1), key='-OUTPUT-')]
]
# 2 create the window
window = sg.Window('Farm nutrition calculator', layout)

# 3 Event loop to keep the window open
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
# 4 The calculation process
    if event == 'Calculate':
        try:
            PlantsAM = float(values['-INPUT1-'])
            PlotsAM = float(values['-INPUT2-'])
            NutrIT = float(values['-INPUT3-'])
            NutrPL = float(values['-INPUT4-'])

            result = ((PlantsAM * PlotsAM * NutrPL) * 4) / NutrIT
            window['-OUTPUT-'].update(f"Amout of nutrition items is {result}")
        except ValueError:
            sg.popup('Please enter a number')
window.close()
