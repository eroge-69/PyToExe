import FreeSimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import io
import time
import pymupdf
from PIL import Image

col1 = sg.Column([
    [sg.Frame('Datensatz auswählen:', [[sg.Text(), sg.Column([
        [sg.Text('Excel-Datei:')],
        [sg.Input(key='SOURCE'),
         sg.FileBrowse(target='SOURCE', file_types=((("Excel-Dateien", "*.xlsx"),)))]
    ], size=(400, 76), pad=(0, 0))]])],
    [sg.Frame('Los-Information:', [[sg.Text(), sg.Column([
        [sg.Text('Losnummer / Wafer-ID:')],
        [sg.Input(key='ID', size=(45, 1))],
        [sg.Text('Rezept:')],
        [sg.Input(default_text='cvmess', key='RECIPE', size=(45, 1))],
        [sg.Text('Datum:')],
        [sg.Input(default_text=time.strftime("%H:%M:%S", time.localtime()), key='DATE', size=(45, 1))],
        [sg.Text('Uhrzeit:')],
        [sg.Input(default_text=time.strftime("%Y-%m-%d", time.localtime()), key='TIME', size=(45, 1))],
        [sg.Text('Notiz:')],
        [sg.Input(key='NOTES', size=(45, 1))],
    ], size=(400, 276), pad=(0, 0))]])],
    [sg.Frame('Optionen:', [[sg.Text(), sg.Column([
        [sg.Text('Werte in Wafermap:')],
        [sg.Radio('p-Werte', "RADIO1", key='p', default=True),
         sg.Radio('q-Werte', "RADIO1", key='q')],
        [sg.Text('Fehlende Werte interpolieren?')],
        [sg.Radio('Nein', "RADIO2", key='noint', default=True),
         sg.Radio('Bilinear', "RADIO2", key='intl')],
        [sg.Text('Bericht erzeugen?')],
        [sg.Radio('Nur Wafermap (PNG)', "RADIO3", key='nopdf', default=True),
         sg.Radio('Bericht mit Wafermap (PDF)', "RADIO3", key='yespdf')],
        [sg.Button('Speichern'),
         sg.Text('', key='SUCCESS')]
    ], size=(400, 211), pad=(0, 0))]])]
], pad=(0, 0))
col2 = sg.Column([
    [sg.Frame('Vorschau',[[sg.Text(), sg.Column([
        [sg.Image(key='PREVIEW')],
        ], pad=(0,0))]],key='PREV-WINDOW')],
], pad=(0,0))

layout = [[sg.vtop(col1),sg.vtop(col2)]]
window = sg.Window('Heatmap-Tool', layout, finalize=True)
window['PREV-WINDOW'].update(visible=False)

while True:
    event, values = window.read()
    reportstart = time.time()
    if values['SOURCE'] == '':
        window['SUCCESS'].update('Keine Messdaten hinterlegt!')
    else:
        df = pd.read_excel(values['SOURCE'],sheet_name='DATA')
        # df.dropna(axis=1, inplace=True)
        # df[['p', 'q']] = df['r'].str.split(pat=',', n=1, expand=True)
        # df['p']=pd.to_numeric(df['p'])
        # df['q']=pd.to_numeric(df['q'])
        # df.drop(labels='r', axis=1, inplace=True)

        if values['p'] == True:
            df_p = df.pivot(index='x', columns='y', values='p')
            rounded_values = df_p.round(3)
            avrg = np.round(df.loc[:, 'p'].mean(), decimals=4)
            stabw = np.round(df.loc[:, 'p'].std(), decimals=4)
            min = np.round(df.loc[:, 'p'].min(), decimals=4)
            max = np.round(df.loc[:, 'p'].max(), decimals=4)
            if values['intl'] == True:
                mask = df_p.isna()
                for a in range(1, mask.shape[0]-1):
                    for b in range(1, mask.shape[1]-1):
                        if mask.iloc[a, b] == True:
                            if [mask.iloc[a + 1, b], mask.iloc[a - 1, b], mask.iloc[a, b + 1],mask.iloc[a, b - 1]].count(True) == 0:
                                df_p.iloc[a, b] = np.mean((df_p.iloc[a + 1, b], df_p.iloc[a - 1, b], df_p.iloc[a, b + 1],df_p.iloc[a, b - 1]))
                heatmap = sns.heatmap(df_p, square=True, cbar=True, cmap='viridis')
                plt.title('Wafermap p Messung')
            else:
                heatmap = sns.heatmap(df_p, square=True, cbar=True, cmap='viridis')
                plt.title('Wafermap p Messung')
        elif values['q'] == True:
            df_q = df.pivot(index='x', columns='y', values='q')
            rounded_values = df_q.round(3)
            avrg = np.round(df.loc[:, 'q'].mean(), decimals=4)
            stabw = np.round(df.loc[:, 'q'].std(), decimals=4)
            min = np.round(df.loc[:, 'q'].min(), decimals=4)
            max = np.round(df.loc[:, 'q'].max(), decimals=4)
            if values['intl'] == True:
                a, b = [1, 1]
                mask = df_q.isna()
                for a in range(1, mask.shape[0] - 1):
                    for b in range(1, mask.shape[1] - 1):
                        if mask.iloc[a, b] == True:
                            if [mask.iloc[a + 1, b], mask.iloc[a - 1, b], mask.iloc[a, b + 1],
                                mask.iloc[a, b - 1]].count(True) == 0:
                                df_q.iloc[a, b] = np.mean(
                                    (df_q.iloc[a + 1, b], df_q.iloc[a - 1, b], df_q.iloc[a, b + 1],
                                     df_q.iloc[a, b - 1]))
                heatmap = sns.heatmap(df_q, square=True, cbar=True, cmap='viridis')
                plt.title('Wafermap q Messung')
            else:
                heatmap = sns.heatmap(df_q, square=True, cbar=True, cmap='viridis')
                plt.title('Wafermap q Messung')
        if values['nopdf'] == True:
            plt.savefig("heatmap.png", format='png', dpi=300, bbox_inches='tight', pad_inches=0.2)
            if values['p'] == True:
                plt.title('Wafermap p Messung')
            else:
                plt.title('Wafermap q Messung')
            b = io.BytesIO()
            b.seek(0)
            plt.savefig(b, format='png', dpi=100, bbox_inches='tight', pad_inches=0.2)
            plt.close()
            reporttime = np.round(time.time() - reportstart, decimals=3)
            window['SUCCESS'].update('PNG erzeugt in ' + str(reporttime) + ' s')
            window['PREVIEW'].update(data=b.getvalue())
        elif values['yespdf'] == True:
            b = io.BytesIO()
            plt.savefig(b, format='png', dpi=300, bbox_inches='tight', pad_inches=0.01)
            plt.close()

            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.utils import ImageReader
            from reportlab.pdfbase.pdfmetrics import stringWidth
            from reportlab.rl_config import defaultPageSize
            from reportlab.platypus import Table, TableStyle

            width, height = A4
            pdfmetrics.registerFont(TTFont('Frutiger', 'FRUTIGERLTCOM-LIGHT.ttf'))
            Report = canvas.Canvas('Messwerte.pdf', pagesize=A4)
            Report.setFont('Frutiger', 12)
            PAGE_WIDTH = defaultPageSize[0]

            Header = Report.beginText()
            Header.setTextOrigin(20 * mm, height - 15 * mm)

            # Date and time
            Header.textOut('Datum: ')
            Header.moveCursor(20 * mm, 0)
            Header.textOut(values['DATE'])
            Header.moveCursor(35 * mm, 0)
            Header.textOut('Zeit: ')
            Header.moveCursor(20 * mm, 0)
            Header.textLine(values['TIME'])
            Header.moveCursor(-75 * mm, 0)
            # Wafer-ID and recipe
            Header.textOut('Wafer-ID: ')
            Header.moveCursor(20 * mm, 0)
            Header.textOut(values['ID'])
            Header.moveCursor(35 * mm, 0)
            Header.textOut('Rezept: ')
            Header.moveCursor(20 * mm, 0)
            Header.textLine(values['RECIPE'])
            Header.moveCursor(-75 * mm, 0)
            # Note
            Header.textOut('Notiz:')
            Header.moveCursor(20 * mm, 0)
            Header.textLine(values['NOTES'])
            (Hx, Hy) = Header.getCursor()
            Report.drawText(Header)
            Report.drawImage(
                os.path.join('C://Users/len43450/PycharmProjects/PythonProject/HeatmapTool/ENASLogo.png'),
                width - 80 * mm, Hy / 72 * 25.4 * mm, 74 * mm, 27 * mm)

            Report.line(0 * mm, Hy / 72 * 25.4 * mm, width * mm, Hy / 72 * 25.4 * mm)
            image = ImageReader(b)
            Report.drawImage(image, 24.84 * mm, Hy / 72 * 25.4 * mm - 152 * mm, height=150 * mm, width=160.33 * mm)
            Report.line(0 * mm, Hy / 72 * 25.4 * mm - 154 * mm, width * mm, Hy / 72 * 25.4 * mm - 154 * mm)

            Summary = Report.beginText()
            Summary.setTextOrigin(20 * mm, Hy / 72 * 25.4 * mm - 154 * mm - 20)
            Summary.setFont('Frutiger', 12, leading=None)
            Summary.moveCursor((PAGE_WIDTH - stringWidth('Zusammenfassung:', 'Frutiger', 12)) / 2.0 - 20 * mm, 0)
            Summary.textLine('Zusammenfassung:')
            Summary.moveCursor(-(PAGE_WIDTH - stringWidth('Zusammenfassung:', 'Frutiger', 12)) / 2.0 + 20 * mm,1*mm)
            Summary.setFont('Frutiger', 12, leading=None)
            Summary.textOut('AVG:')
            Summary.moveCursor(stringWidth('AVG: ', 'Frutiger', 12), 0)
            Summary.textOut(str(avrg))
            Summary.moveCursor(35 * mm, 0)
            Summary.textOut('STABW:')
            Summary.moveCursor(stringWidth('STABW: ', 'Frutiger', 12), 0)
            Summary.textOut(str(stabw))
            Summary.moveCursor(35 * mm, 0)
            Summary.textOut('MIN:')
            Summary.moveCursor(stringWidth('MIN: ', 'Frutiger', 12), 0)
            Summary.textOut(str(min))
            Summary.moveCursor(35 * mm, 0)
            Summary.textOut('MAX:')
            Summary.moveCursor(stringWidth('MAX: ', 'Frutiger', 12), 0)
            Summary.textLine(str(max))
            (Sx, Sy) = Summary.getCursor()
            Summary.setTextOrigin(20 * mm, Sy / 72 * 25.4 * mm)
            Summary.setFont('Frutiger', 12, leading=None)
            if values['p'] == True:
                Summary.moveCursor((PAGE_WIDTH - stringWidth('Wertetabelle p', 'Frutiger', 12)) / 2.0 - 20 * mm, 8 * mm)
                Summary.textLine('Wertetabelle p')
            else:
                Summary.moveCursor((PAGE_WIDTH - stringWidth('Wertetabelle q', 'Frutiger', 12)) / 2.0 - 20 * mm, 8 * mm)
                Summary.textLine('Wertetabelle q')
            Report.drawText(Summary)
            Report.line(0 * mm, Sy / 72 * 25.4 * mm-1*mm, width * mm, Sy / 72 * 25.4 * mm-1*mm)

            rounded_values = rounded_values.replace({np.nan: None})
            table_data=[[''] + rounded_values.columns.tolist()] + rounded_values.reset_index().values.tolist()
            top_row = Table(table_data,colWidths=13.077*mm, rowHeights=5.2*mm)
            top_row.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            w, h = top_row.wrapOn(Report, 0, 0)
            top_row.drawOn(Report, 20 * mm, 10 * mm)

            Report.showPage()
            Report.save()
            reporttime = np.round(time.time() - reportstart, decimals=3)

            preview = pymupdf.open(
                "C:/Users/len43450/PycharmProjects/PythonProject/HeatmapTool/Messwerte.pdf")  # open document
            for page in preview:  # iterate the document pages
                pix = page.get_pixmap(dpi=52)  # render page to an image
                mode = "RGBA" if pix.alpha else "RGB"
                img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
            window['SUCCESS'].update('PDF erzeugt in ' + str(reporttime) + ' s')
            window['PREVIEW'].update(data=img_bytes.getvalue())
    window['PREV-WINDOW'].update(visible=True)
    if event == sg.WIN_CLOSED:
        break
window.close()

