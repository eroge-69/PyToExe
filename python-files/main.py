import pandas as pd
import os
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH 
from docx.shared import Pt
from typing import Any


def llegir_dades() -> list[dict[str, str]]:
    df = pd.read_excel(os.getcwd() + "\\horari.xlsx", sheet_name=0)
    horaris: list[dict[str, str]] = [{} for _ in range(7)]

    f = 1
    for i in range(7):
        while df.iloc[f, 1] != "TOTAL HORES":
            nom = str(df.iloc[f, 1])

            horaris[i][nom] = trobar_horari(df, f)

            f += 1
        f += 2
    
    return horaris


def es_nombre(s: str) -> bool:
    try:
        n = float(s)
        return not pd.isna(n)
    except ValueError:
        return False


def trobar_horari(df: Any, f: int) -> str:
    c = 2 #columna on comencen les hores
    hores = {i: i + 5 for i in range(2, 17)}
    iniciat = False
    inici, final = "", ""

    while c <= 16:
        casella = df.iloc[f, c]
        if not iniciat: #buscar inici
            if es_nombre(casella):
                if str(casella) != "0.0" or str(casella) != "0":
                    iniciat = True
                
                if str(casella) == "1.0" or str(casella) == "1":
                    inici = str(hores[c]) + ":00"
                elif str(casella) == "0.5":
                    inici = str(hores[c]) + ":30"
                elif str(casella) == "2.0" or str(casella) == "2": 
                    inici = "6:00"
                elif str(casella) == "1.5":
                    inici = "6:30"

        else:
            if not es_nombre(casella): #casella anterior és la final
                cas_anterior = df.iloc[f, c - 1]
                if str(cas_anterior) == "1.0" or str(cas_anterior) == "1":
                    final = str(hores[c - 1]) + ":00"
                elif str(cas_anterior) == "0.5":
                    final = str(hores[c - 1]) + ":30"
                return f"{inici} a {final}"
            
            elif hores[c] == 21 and es_nombre(casella): #s'acaba el dia:
                if str(casella) == "1.0" or str(casella) == "1":
                    final = str(hores[c]) + ":00"
                elif str(casella) == "0.5":
                    final = str(hores[c]) + ":30"
                return f"{inici} a {final}"

        c += 1

    return "DES"



def crear_taula() -> None:
    document = Document()

    #full en horitzontal
    section = document.sections[0]
    new_width, new_height = section.page_height, section.page_width
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = new_width
    section.page_height = new_height

    #Afegir títol en negreta
    paragraf = document.add_paragraph()
    paragraf.alignment = WD_ALIGN_PARAGRAPH.CENTER 
    run = paragraf.add_run("Setmana ...")
    run.bold = True 
    run.font.name = 'Calibri'
    run.font.size = Pt(11)

    horaris = llegir_dades()

    table = document.add_table(rows = len(horaris[0].keys()) + 1, cols = 8)

    #posar dies de la setmana com a columnes
    hdr_cells = table.rows[0].cells
    dies = ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte", "Diumenge"]
    for i in range(len(dies)):
        hdr_cells[i + 1].text = dies[i]

    #posar treballadors com a files
    noms = table.columns[0].cells
    for i, treballador in enumerate(sorted(horaris[0].keys())):
        noms[i + 1].text = treballador

    for i, horari in enumerate(horaris):
        columna = table.columns[i+1].cells
        for j, nom in enumerate(sorted(horari.keys())):
            columna[j+1].text = horari[nom]


    document.add_page_break()

    document.save('graella.docx')

crear_taula()