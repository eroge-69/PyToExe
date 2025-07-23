import PySimpleGUI as sg
import pandas as pd
import os
from pathlib import Path

# GUI Theme
sg.theme('DarkBlue3')

def convert_excel_to_csv(input_path, output_folder):
    """Convert single Excel file to CSV"""
    try:
        df = pd.read_excel(input_path)
        csv_name = Path(input_path).stem + '.csv'
        output_path = os.path.join(output_folder, csv_name)
        df.to_csv(output_path, index=False)
        return True, output_path
    except Exception as e:
        return False, str(e)

# Layout
layout = [
    [sg.Text('Excel to CSV Converter', font=('Helvetica', 16))],
    [sg.HSeparator()],
    [sg.Text('Select Excel File(s):')],
    [
        sg.Input(key='-INPUT-'), 
        sg.FilesBrowse(file_types=(("Excel Files", "*.xlsx *.xls"),))
    ],
    [sg.Text('Output Folder:')],
    [
        sg.Input(key='-OUTPUT-', default_text=os.path.expanduser('~/Desktop')), 
        sg.FolderBrowse()
    ],
    [sg.ProgressBar(100, orientation='h', size=(50, 20), key='-PROG-')],
    [sg.Button('Convert'), sg.Button('Exit')],
    [sg.Multiline(size=(70, 10), key='-LOG-', autoscroll=True, disabled=True)]
]

# Create Window
window = sg.Window('Excel to CSV Converter', layout)

# Event Loop
while True:
    event, values = window.read()
    
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
        
    if event == 'Convert':
        input_files = values['-INPUT-'].split(';') if values['-INPUT-'] else []
        output_folder = values['-OUTPUT-']
        
        if not input_files:
            sg.popup_error('Please select Excel files first!')
            continue
            
        if not output_folder:
            sg.popup_error('Please select output folder!')
            continue
            
        # Process files
        success_count = 0
        for i, file in enumerate(input_files):
            window['-PROG-'].update((i+1)/len(input_files)*100)
            window['-LOG-'].update(f'Processing: {os.path.basename(file)}\n', append=True)
            
            success, result = convert_excel_to_csv(file, output_folder)
            if success:
                window['-LOG-'].update(f'Success: Saved as {result}\n', append=True)
                success_count += 1
            else:
                window['-LOG-'].update(f'Failed: {result}\n', append=True)
        
        sg.popup(f'Complete!', f'{success_count}/{len(input_files)} files converted')

window.close()