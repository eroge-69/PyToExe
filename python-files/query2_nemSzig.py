#version 2.0

import re
from re import fullmatch
from re import split as resplit
from sys import argv
import string
import time

#ellenőrző regexek
pid_kut = r'\d+'
lakcim = r'[\w\s\dáéíóöőúüűÁÉÍÓÖŐÚÜŰ,./-]+'
nev = r'[\w\sáéíóöőúüűÁÉÍÓÖŐÚÜŰ.-]+'
szuldat = r'[\d./\\-]+'
adoazonosito = r'\d{10}'
kid = r'\d+'
szemelyi = r'[\w-]+'
bankszamla = r'\d{8}-\d{8}-\d{8}|\d+'
bankszamlaplusz = r'[ ,\w-]+'
telefon = r'[\d /(\)+-]+'
email = r'\S+@\S+\.\S+'
pubweb = r'.+'
iban = r'[a-zA-Z]{2}\d+'
szerzodesszam = r'\d+'
tajszam = r'\d+|\d{3}-\d{3}-\d{3}'
minden = r'.*'
aduser = r'.+'
nemtudom = r'.+'
lakcimkartya = r'[\w ]+'
adoszam = r'[\d-]+'
szoveg = r'[a-zA-ZáéíóöőúüűÁÉÍÓÖŐÚÜŰ ]+'
mind1 = r'.+'
szam = r'\d+'


#már ismert mezők szótára
fields = {
    "NEV": nev,
    "KUTID": pid_kut,
    "PARTNERID": pid_kut,
    "SZULDAT": szuldat,
    "SZULNEV": nev,
    "ANYJANEV": nev,
    "ANYJANEVE": nev,
    "ANYJA_NEVE": nev,
    "TELJES_NEV": nev,
    "ADOAZONOSITO": adoazonosito,
    "SZEMIG": szemelyi,
    "BANKSZAMLASZAM": bankszamla,
    "SZULETESI_IDO": szuldat,
    "PUBWEB_FELHASZ_NEV": pubweb,
    "SZAMLATULAJDONOS": nev,
    "SZERZODESSZAM_1": szerzodesszam,
    "SZERZODESSZAM_2": szerzodesszam,
    "SZERZODESSZAM_3": szerzodesszam,
    "IBAN": iban,
    "ADOAZONOSITO_JEL": adoazonosito,
    "TEL1": telefon,
    "TEL2": telefon,
    "TEL3": telefon,
    "TEL4": telefon,
    "TEL5": telefon,
    "TEL6": telefon,
    "TEL7": telefon,
    "EMAIL": email,
    "EMAIL1": email,
    "EMAIL2": email,
    "EMAIL3": email,
    "EMAIL4": email,
    "ALL_CIM": lakcim,
    "ALLCIM": lakcim,
    "ALL_LAKCIMKARTYA": lakcimkartya,
    "ALLANDO_CIM": lakcim,
    "LEV_CIM": lakcim,
    "LEVELEZESI_CIM": lakcim,
    "LEVC_CIM": lakcim,
    "KEYID": kid,
    "PUBWEBID": pubweb,
    "SZEMELYI_IGAZOLVANY_SZAMA": szemelyi,
    "TELEFONSZAM": telefon,
    "ADUSER": aduser,
    "LEVCIM": lakcim,
    "UTLEVEL": nemtudom,
    "LAKCIMKARTYA": lakcimkartya,
    "JOGOSITVANY": nemtudom,
    "TAJSZAM": nemtudom,
    "ADOSZAM": nemtudom,
    "BANKSZLASZ1": bankszamla,
    "BANKSZLASZ2": iban,
    "SZERZSZ1": szerzodesszam,
    "SZERZSZ2": szerzodesszam,
    "SZERZSZ3": szerzodesszam,
    "ERTEK": szam,
    "SZOVEG": szoveg,
    "REGI_SZEMIG": szemelyi,
    "UJ_SZEMIG": szemelyi,
    "BANKSZAMLASZAM": bankszamlaplusz,
    "BANKSZAMLA_BIC_BEI": bankszamlaplusz,
    "BANKSZAMLA_IBAN": bankszamlaplusz,
    "BANKSZAMLA_KELER": bankszamlaplusz,
    "BANKSZAMLA_PFJ": bankszamlaplusz,
}

#ellenőrzi, van-e a rekordban hibás adat
def JoSorE(line, osszes, format):
    for col_idx in format.keys():
        osszes[list(format.keys()).index(col_idx)] += 1
        if not fullmatch(format[col_idx], line[list(format.keys()).index(col_idx)]):
            return False
    return True

#soronként ellenőrzi a hibás adatokat
def read_input_file(read_file, passed, errors, error_location, counter, elso_sor, rosszak, osszes, format):
    print("hibák keresése...")
    elso_sor = read_file.readline()
    for i, line in enumerate(read_file, 1):
        newline = resplit('[|;]', line.strip())
        if JoSorE(newline, osszes, format):
            passed.append(line)
        else:
            counter += 1
            errors.append(line)
            errsinaline = []
            for col_idx in format.keys():
                if not fullmatch(format[col_idx], newline[list(format.keys()).index(col_idx)]):
                    errsinaline.append(f"{resplit('[|;]', elso_sor.strip())[list(format.keys()).index(col_idx)]}: {newline[list(format.keys()).index(col_idx)]}")
                    rosszak[list(format.keys()).index(col_idx)] += 1
            error_location.append(f"{counter}. sorban ezek a hibák: {errsinaline}\n")
        print(f"\rFeldolgozott sorok: {i}", end="", flush=True)
    return elso_sor

#megadott adatállományban kiszámolja mezőnként a hibás adatok arányát
def rosszaranyok(rosszak, osszes):
    for x in range(len(rosszak)):
        rosszak[x] = (rosszak[x]/osszes[0])*100
        
def tes_szemelyi(elso, masodik):
    if elso == "" or (elso != "" and masodik != ""):
        return masodik
    elif masodik == "":
        return elso
    return ""

def tes_tel(elso, masodik, harmadik):
    if harmadik == "" and masodik == "":
        return elso
    if harmadik == "" and elso == "":
        return masodik
    if harmadik == "" and masodik != "" and elso != "":
        return elso
    if harmadik == "" and masodik == "" and elso == "":
        return ""
    return harmadik

def main():
    try:
        input_file = argv[1]
    except IndexError:
        input_file = input("Melyik adatbázist szeretnéd ellenőrizni: ")
    fajlformatumok = ["txt", "csv"]
    if input_file.split('.')[1] not in fajlformatumok:
        print("Rossz fájlformátum")
        exit(1)
    output_query = "".join([input_file.split(".")[0], "-query.txt"])
    output_rosszak = "".join([input_file.split(".")[0], "-err.txt"])
    output_jok = "".join([input_file.split(".")[0], "-ok.txt"])
    output_rosszhely = "".join([input_file.split(".")[0], "-err-loc.txt"])
    output_hibaarany = "".join([input_file.split(".")[0], "-err-ratio.txt"])
    errors = []
    passed = []
    error_location = []
    elso_sor = ""
    counter = 0
    rosszak = []
    osszes = []
    format = {}
    header = ""
    newdb = "NewDB.txt"
    raw_lines = []
    wrong_data = []
    data = ""
    datalist = []
    separator = ", "
    
    #megadott adatbázis ellenőrzése, ha nem létezik, akkor eldobás
    with open(input_file, 'r', encoding="utf-8") as read_file:
        fejlec = resplit('[|;]', read_file.readline().strip())
        uj_fejlec = []
        nemIsmert_mezok = []
        for x in fejlec:
            if x in fields.keys():
                uj_fejlec.append(x)
            if x not in fields.keys():
                nemIsmert_mezok.append(x)
        for x in uj_fejlec:
            for y in fields.keys():
                if x.__eq__(y):
                    format.update({x: fields.get(y)})
        header = "|".join(format.keys())+"\n"
        data = input(f"A következő adatok közül választhatsz: {header}")
        datalist = resplit('[|,]', data.strip())
        if data != "":
            for x in datalist:
                if x not in format.keys():
                    wrong_data.append(x)
        ures_adat = []
        print("beolvasás folyamatban...")
        if len(wrong_data) != 0:
            header = header.strip() + "|" + "|".join(wrong_data) + "\n"
        with open(newdb, "w", encoding="utf-8") as write_file:
            write_file.write(header)
            for i, line in enumerate(read_file, 1):
                temp_line = resplit('[|;]', line.strip())
                for y in range(len(fejlec)):
                    if fejlec[y] in nemIsmert_mezok:
                        temp_line.remove(temp_line[y]) 
                for x in wrong_data:
                    if x in fields.keys():
                        format.update({x: fields.get(x)})
                    else:
                        format.update({x: mind1})
                    temp_line.append("")                      
                write_file.write("|".join(temp_line) + "\n")
                print(f"\rFeldolgozott sorok: {i}", end="", flush=True)
        print(f"\nA {nemIsmert_mezok} mező(k) nem ismert(ek), helyesség(ük) nem ellenőrizhető")
            
    #adatok ellenőrzése, hibák kiszűrése
    if data == "":
        rosszak = [0] * len(format)
        osszes = [0] * len(format)
        with open(newdb, 'r', encoding="utf-8") as read_file:
            elso_sor = read_input_file(read_file, passed, errors, error_location, counter, elso_sor, rosszak, osszes, format)
        rosszaranyok(rosszak, osszes)
    else:
        newHeader = "|".join(datalist) + "\n"
        current_format = {}
        with open(newdb, "r", encoding="utf-8") as read_file:
            oldheader = resplit('[|;]', read_file.readline().strip())
            for d in datalist:
                for i in oldheader:
                    if d == i:
                        current_format[d] = format.get(i)
            for line in read_file:
                newline = resplit('[|;]', line.strip())
                currentLine = []
                for d in datalist:
                    for i in range(len(oldheader)):
                        if d == oldheader[i]:
                            currentLine.append(newline[i])
                raw_lines.append(currentLine)
        format = current_format
        rosszak = [0] * len(format)
        osszes = [0] * len(format)
        with open(output_query, "w", encoding="utf-8") as write_file:
            write_file.write(newHeader)
            for line in raw_lines:
                write_file.write("|".join(line) + "\n")  
        with open(output_query, "r", encoding="utf-8") as read_file:
            elso_sor = read_input_file(read_file, passed, errors, error_location, counter, elso_sor, rosszak, osszes, format)
        rosszaranyok(rosszak, osszes)
    
    #hiba nélküli sorok kiírása
    with open(output_jok, "w", encoding="utf-8") as write_file:
        print("\njó sorok kiírása folyamatban...")
        output_cnt = 0
        write_file.write(elso_sor)
        while output_cnt < len(passed):
            write_file.write(passed[output_cnt])
            output_cnt += 1
    
    #hibás sorok kiírása
    with open(output_rosszak, "w", encoding="utf-8") as write_file:
        print("rossz sorok kiírása folyamatban...")
        output_cnt = 0
        row_count = 1
        write_file.write(f"SORSZAM|{elso_sor}")
        while output_cnt < len(errors):
            write_file.write(f"{row_count}|{errors[output_cnt]}")
            output_cnt += 1
            row_count += 1
            
    #hibás adatok kiírása    
    with open(output_rosszhely, "w", encoding="utf-8") as write_file:
        print("hibák kiírása folyamatban...")
        output_cnt = 0
        while output_cnt < len(error_location):
            write_file.write(error_location[output_cnt])
            output_cnt += 1
            
    #hibés adatok arányainak kiírása
    with open(output_hibaarany, "w", encoding="utf-8") as write_file:
        print("hibaarányok kiírása...")
        for x in range(len(resplit('[|;]', elso_sor.strip()))):
            write_file.write(f"{resplit('[|;]', elso_sor.strip())[x]}: {(100 - rosszak[x])}%-ban jó\n")
    
    print("A fájlok elkészültek")
    input("Nyomj ENTER-t a kilépéshez")
                    
main() 