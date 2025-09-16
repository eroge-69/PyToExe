# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

pdfmetrics.registerFont(TTFont('Arial',      r'C:\Windows\Fonts\arial.ttf'))    
pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\Windows\Fonts\arialbd.ttf'))    
registerFontFamily('Arial', normal='Arial', bold='Arial-Bold')

import datetime
date = datetime.datetime.now()

doc = SimpleDocTemplate("dodatek_motywacyjny.pdf", pagesize=A4,
                        leftMargin=25*mm, rightMargin=25*mm, topMargin=25*mm, bottomMargin=25*mm)

styles = getSampleStyleSheet()

normal = ParagraphStyle('normal', parent=styles['Normal'], fontName='Arial', fontSize=11, leading=14)
right = ParagraphStyle('right', normal, alignment=2)

story = []



def add_page(imie_nazwisko, kwota, kwota_slownie):
    story.append(Paragraph('PLO PŁ-IV.119.6.42.2025 ' + ("&nbsp;" * 66) + f' Łódź dnia {date.strftime("%d")}.{date.strftime("%m")}.{date.year}', normal))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"<b>Sz. P. {imie_nazwisko}</b><br/>"
                        "nauczyciel Publicznego Liceum Ogólnokształcącego<br/>"
                        "Politechniki Łódzkiej<br/>"
                        "im.prof.Jana Krysińskiego", right))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Na podstawie art. 7 ust. 1 i 7 Regulaminu wynagradzania zatrudnionych "
                        "w Publicznym Liceum Ogólnokształcącym Politechniki Łódzkiej z dnia "
                        "01 kwietnia 2022 r. przyznaję za okres kwiecień 2025 - sierpień 2025 r. "
                        "dodatek motywacyjny.", normal))
    story.append(Spacer(1, 10))

    story.append(Paragraph(f"<b>Do wypłaty w miesiącach od 01 września 2025 do 31 grudnia 2025 "
                        f"dodatek motywacyjny w wysokości {kwota} zł "
                        f"(słownie zł {kwota_slownie}).</b>", normal))

    story.append(Spacer(1, 50))
    story.append(Paragraph("...............................................<br/>podpis pracodawcy", right))
    story.append(PageBreak())


import pandas as pd

dataframe = pd.read_excel('Dodatki 01.04_31.08.2025.xlsx')
dataframe.to_csv('dane.csv')

with open('dane.csv', mode ='r', encoding='utf-8') as file:
    csv = [x.strip().split(',')[2:] for x in file.readlines()]
    csv = csv[2:-1]
    for line in csv:
        add_page(line[0], line[1], line[2])


doc.build(story)
