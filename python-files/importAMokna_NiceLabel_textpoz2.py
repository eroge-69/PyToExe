# utworzony 26.04.2024  / 
import os, glob
import numpy as np
import pandas as pd

def parse(plik):
    dfcols =  dfcols = ['Referencja', 'Szerokosc', 'Wysokosc','budowa', 'pozycja_klienta', 'ref', 'sztuki', 'opis']
    df = pd.DataFrame(columns=dfcols)
    for row in plik[3:-1]:
        szt = int(row[43:49])
        bud1 = row[:40].strip()
        bud2 = row[102:170]
        bud = bud1 +bud2
        szer = int(row[48:57])
        wys = int(row[58:64])
        grubosc = int(row[74:79])
        referencja = row[80:95]
        opis = row[178:-1]
        ref = referencja.strip()
        ref_splited = ref.split()
        ref_2x_spacja = f'{ref_splited[0]}  {ref_splited[1]}'
        df = pd.concat([df, pd.Series([ref_2x_spacja, szer, wys, bud, 0, ref_splited[1], szt, opis], index= dfcols).to_frame().T], ignore_index=True)
    groups =df.groupby(['ref']).indices
    sortedGroups = sorted(groups.items(), key=lambda x:len(x[1]), reverse=True)
    poz_k = 20
    for k, v in sortedGroups:
        poz_k +=1
        for i in v:
            df['pozycja_klienta'].loc[i] = poz_k
    return df

def zapis(df, data, zam):
    naglowek='NumerZamowienia,DataDostawy,Referencja(Komisja),NazwaProduktu,Ilość,Szerokość,Wysokość,UsługiFormatkaEtykiety,Przebieg wzoru,StronaWzoru,SzprosPoziomyArtykuł,Szpr.Poz.IlośćTyczek,Szpr.Poz.Podział,SzprosPionowyArtykuł,Szpr.Pion.IlośćTyczek,Szpr.Pion.Podział,Wolne,TekstZam2,PozycjaKlienta,Opis,Wolne,Text1,Text2,Text3,Text4,Text5,NrModelu,ParametryModelu\n'
    nowy_plik = open(filename, 'w+',)
    nowy_plik.write(naglowek)
    for ind in df.index:
        referencja = df['Referencja'][ind]
        bud = df['budowa'][ind]
        szt = df['sztuki'][ind]
        szerokosc = df['Szerokosc'][ind]
        wysokosc = df['Wysokosc'][ind]
        poz_k = df['pozycja_klienta'][ind]
        opis = df['opis'][ind]
        nowy_plik.write('{0};{1};{2};{3};{4};{5};{6};;;;;;;;;;;;{7};;;;{8};;;;;;;;;;;;;;\n'.format(zam,data, referencja, bud, szt, szerokosc, wysokosc, poz_k, opis))
    nowy_plik.close()

data = input('podaj datę w formacie dd/mm/rrrr  ')
lista = glob.glob('*.txt')
for n in range(len(lista)):
    (filepath, filename) = os.path.split(lista[n])
    (shortname, extension) = os.path.splitext(filename)
    plik =open(filename, 'r',).readlines()
    parsed_file = parse(plik)
    parsed_sorted = parsed_file.sort_values(by=['pozycja_klienta','Szerokosc'], ascending=[True, False])
    x = 100
    for i in parsed_sorted.index:
        x+=1
        parsed_sorted.at[i,'pozycja_klienta']=x
    parsed_file['pozycja_klienta'] = parsed_sorted['pozycja_klienta']
    zapis(parsed_file, data, shortname)
