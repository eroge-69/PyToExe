# -*- coding: utf-8 -*-
"""
Created on Wed Jul  9 13:30:13 2025

@author: Giovanni
"""

from fpdf import FPDF

class PDF(FPDF):
    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('helvetica', 'I', 8)
        # Page number
        self.cell(0, 10,'SoftWare © Hytek srl versione 1.2 nov-2025' +
                  '                     Page ' + str(self.page_no()) + '/{nb}' + 
                  '                Progetto: Hytek' + '14/07/2025', 0, 0, 'L')
       

# Create instance of FPDF class
pdf = PDF()
#pdf.set_margins(left=100, top=10)

# Add a page
pdf.add_page()

pdf.set_draw_color(0, 0, 0)  # Nero (RGB)

# Disegna un rettangolo per il bordo
pdf.rect(x=10, y=10, w=190, h=270)  # Margini: 10mm, dimensioni standard A4 (210x297mm)
# Set font
pdf.set_font("helvetica", size = 12)

# Add a title


# Add a line break

# Add an image
pdf.image("hytek.png", x = 74, y = 20, w = 61)
# Add an image
pdf.image("cattura software.jpg", x = 60.5, y = 40, w = 87)

pdf.image("copy1.png", x = 139, y = 40, w = 10)

# Add some text

pdf.set_xy(17, 60)
pdf.multi_cell(text = "SoftWare è un programma sviluppato da Hytek srl come ausilio al corretto dimensionamento di impianti di addolcimento delle acque primarie. SoftWare non può sostituire la competenza tecnica di un progettista esperto e tutte le indicazioni fornite devono essere sempre verificate tenendo in attenta considerazione le norme legislative, la situazione locale e lo specifico problema che ci si appresta a risolvere.",
               w = 180.0, h = 5, align = 'J')
# Save the PDF to a file
pdf.set_xy(60, 87)
pdf.set_font("helvetica", size = 16)
pdf.cell(75, 10, 'REPORT DI DIMENSIONAMENTO', border=0, align='L' )

pdf.set_font("helvetica", size = 12)
pdf.set_fill_color(255, 255, 255)
pdf.set_xy(20, 100)
pdf.cell(60, 8, 'Compilato da:', border=0, align='L', fill=True )
pdf.cell(60, 8, 'Giovanni Servi', border=0, align='L', fill=True )
pdf.set_xy(20, 106)
pdf.cell(60, 8, 'Compilato in data:', border=0, align='L', fill=True )
pdf.cell(60, 8, '28 Novembre 2025', border=0, align='L', fill=True )
pdf.set_xy(20, 112)
pdf.cell(60, 8, 'Cliente:', border=0, align='L', fill=True )
pdf.cell(60, 8, 'Hytek srl', border=0, align='L', fill=True )
pdf.set_xy(20, 118)
pdf.cell(60, 8, 'Denominazione progetto', border=0, align='L', fill=True )
pdf.cell(60, 8, 'Addolcitore centrale termica', border=0, align='L', fill=True )
pdf.set_xy(20, 124)
pdf.cell(60, 8, 'Note:', border=0, align='L', fill=True )
pdf.set_xy(80, 125)
pdf.multi_cell(text = "Alla faccia della miseria caro mio, come faccio a fare delle note se ancora non so bene di cosa stiamo parlando!!", w = 100, h = 5, align = 'J')



#pdf.set_xy(20, 200)

var0=1
var1=2
var2=2 
varcapex=2

results_dur={'durezza': 30.0}

results_come={'portata_giorno': 25.0,
 'portata_progetto': 3.0,
 'portata_massima': 4.0,
 'durezza_ingresso': 30.0,
 'durezza_uscita': 5.0,
 'partenza': 2,
 'portata_ciclo':25,
 'ciclica':1200}

risult={'por_ciclo': 10.0, 'por_progetto': 1.8, 'por_max': 2.7, 'cap_scambio': 5, 'resina': 75, 'tank': '13x54', 'valvola': '5600', 'dp_esercizio': 0.3780727763476164, 'dp_punta': 0.5872669912236494, 'riserva': 4.0, 'diametro_tubazioni': '1"', 'tino': 150, 'consumo_sale': 9.0, 'consumo_acqua': 0.75}

delta_dur= round(float(results_dur['durezza']) - float(results_come['durezza_uscita']), 1)
#testa = ['Colonna 1', 'Colonna 2']
pdf.set_xy(20, 150)
pdf.set_fill_color(200, 220, 255)  # Light blue background
pdf.cell(60, 8, 'Dati in ingresso', border=0, align='C', fill=True )

pdf.set_xy(20, 158)
data=[]
partenza=var1  ####   Da gettare
if partenza==1:
    imp_tipo='Simplex'
    rig_tipo='Temporizzata giornaliera'
    tim_tipo= 'giorni'   
if partenza==2:
    imp_tipo='Simplex'
    rig_tipo='Volumetrica ritardata'
    tim_tipo= 'giorni'
if partenza==3:
    imp_tipo='Simplex'
    rig_tipo='Volumetrica immediata'  
    tim_tipo= 'ore'
if partenza==4:
    imp_tipo='Duplex'
    rig_tipo='Volumetrica immediata'
    tim_tipo= 'ore'
if partenza==5:
    imp_tipo='Multiplex'
    rig_tipo='Volumetrica immediata'
    tim_tipo= 'ore'
tim_valo= var2   ###  da gettare  

riga=["Impianto tipo", 'Addolcitore ' + imp_tipo ]
data.append(riga)
riga=['Partenza rigenerazione', rig_tipo]
data.append(riga)

ciclo=var0
if ciclo==1:
    riga= ['Portata giornaliera', str(results_come['portata_giorno']) + " M3"]
    data.append(riga)
    riga= ['Frequenza richiesta ', str(var2) + " giorni"]
    data.append(riga)
    riga= ['Portata per ciclo ', str(risult['por_ciclo']) + " M3"]
    data.append(riga)
    
if ciclo==2:
    riga= ['Portata per ciclo ', str(risult['por_ciclo']) + " M3"]
    data.append(riga)  
    
if ciclo==3:
    riga= ['Capacità ciclica richiesta', str(results_come['ciclica']) + " M3"]
    data.append(riga)    

riga=["Durezza acqua in ingresso", str(results_dur['durezza']) + " °F"]
data.append(riga)
riga=['Durezza acqua in uscita', str(results_come['durezza_uscita']) + " °F"]
data.append(riga)

if ciclo==3:
    riga= ['Portata per ciclo ', str(round(float(results_come['ciclica'] / delta_dur), 1)) + " M3"]
    data.append(riga)  
    
riga= ['Portata di progetto ', str(results_come['portata_progetto']) + " M3/h" ]
data.append(riga)
riga= ['Portata massima di punta ', str(results_come['portata_massima']) + " M3/h" ]
data.append(riga)
if varcapex==1:
    conf_tipo='minimizza i costi operativi'
if varcapex==2:
    conf_tipo='minimizza i costi di impianto'
riga= ['Configurazione', conf_tipo ]
data.append(riga)


# Larghezza delle colonne
col_widths = [60, 60]

# Disegno dell'intestazione
#for i, col_name in enumerate(testa):
    #pdf.set_fill_color(200, 220, 255)  # Colore di sfondo
    #pdf.cell(col_widths[i], 10, col_name, border=1, align='L', fill=True)
    
# Disegno delle righe
n=1
for row in data:
    
    for i, cell in enumerate(row):
        print(i)
        if n==1:
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(col_widths[i], 8, cell, border=1, align='L', fill=True )
        elif n%2 != 0:
            print(n//2)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(col_widths[i], 8, cell, border=1, align='L', fill=True )           
        else:
            pdf.set_fill_color(255, 255, 255)
            pdf.cell(col_widths[i], 8, cell, border=1, align='L', fill=True )  
    pdf.set_xy(20, 158+8*n)
    n=n+1


pdf.add_page()
pdf.rect(x=10, y=10, w=190, h=270)
pdf.set_xy(20, 20)
pdf.set_fill_color(200, 220, 255)  # Light blue background
pdf.cell(60, 8, 'Parametri di dimensionamento', border=0, align='C', fill=True )

data=[]
if imp_tipo=='Simplex':
    int(risult['por_ciclo'] * results_dur['durezza'])
    riga= ['Capacità ciclica necessaria', str(int(risult['por_ciclo'] * results_dur['durezza'])) + " M3 °F"]
    data.append(riga)
    
    riga= ['Capacità di scambio ', str(risult['cap_scambio']) + " Kg CaCo3/Lt resina"]
    data.append(riga)
    
    riga= ['Resina calcolata ', str(risult['resina']) + " Litri"]
    data.append(riga)
    
    riga= ['Capacità ciclica effettiva', str(int(risult['resina'] * risult['cap_scambio'])) + " M3 °F"]
    data.append(riga)
    
    riga= ['Riserva', str(int(risult['riserva'])) + " %"]
    data.append(riga)
    
    riga= ['Dimensione bombola ', str(risult['tank']) + " Pollici"]
    data.append(riga)
    
    riga= ['Modello valvola ', str(risult['valvola']) + " SXT - Pentair Fleck"]
    data.append(riga)
    
    riga= ['Diametro tubazioni ', str(risult['diametro_tubazioni'])]
    data.append(riga)
    
    riga= ['DP alla portata di progetto ', str(round(risult['dp_esercizio'],1)) + " Bar"]
    data.append(riga)
    
    riga= ['DP alla portata di punta ', str(round(risult['dp_punta'],1)) + " Bar"]
    data.append(riga)
    
    riga= ['Tino salamoia ', str(risult['tino']) + " Litri"]
    data.append(riga)
    
    
pdf.set_xy(20, 20)
pdf.set_fill_color(200, 220, 255)  # Light blue background
pdf.cell(60, 8, 'Parametri di dimensionamento', border=0, align='C', fill=True )

data=[]
if imp_tipo=='Duplex':
    int(risult['por_ciclo'] * results_dur['durezza'])
    riga= ['Capacità ciclica necessaria', str(int(risult['por_ciclo'] * results_dur['durezza'])) + " M3 °F"]
    data.append(riga)
    
    riga= ['Capacità di scambio ', str(risult['cap_scambio']) + " Kg CaCo3/Lt resina"]
    data.append(riga)
    
    riga= ['Resina calcolata (per bombola) ', str(risult['resina']) + " Litri"]
    data.append(riga)
    
    riga= ['Capacità ciclica effettiva', str(int(risult['resina'] * risult['cap_scambio'])) + " M3 °F"]
    data.append(riga)
    
    riga= ['Durata stimata ciclo', str(int(risult['riserva'])) + " %"]
    data.append(riga)
    
    riga= ['Dimensione bombole ', str(risult['tank']) + " Pollici"]
    data.append(riga)
    
    riga= ['Modello valvola ', str(risult['valvola']) + " SXT - Pentair Fleck"]
    data.append(riga)
    
    riga= ['Diametro tubazioni ', str(risult['diametro_tubazioni'])]
    data.append(riga)
    
    riga= ['DP alla portata di progetto ', str(round(risult['dp_esercizio'],1)) + " Bar"]
    data.append(riga)
    
    riga= ['DP alla portata di punta ', str(round(risult['dp_punta'],1)) + " Bar"]
    data.append(riga)
    
    riga= ['Tino salamoia ', 2 * str(risult['tino']) + " Litri"]
    data.append(riga)   
    
    
    
    #riga= ['Consumo di sale (indicativo) ']
    #, str(risult['consumo_sale']) + " Kg/ciclo"]
    #pdf.cell(20, 140, riga, border=0, align='L' )
    #riga= ['', str(risult['consumo_sale']) + " Kg/mese"]
   # pdf.cell(20, 140, riga, border=0, align='L' )

pdf.set_xy(20, 28)    
n=1
for row in data:
    
    for i, cell in enumerate(row):
        print(i)
        if n==1:
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(col_widths[i], 8, cell, border=1, align='L', fill=True )
        elif n%2 != 0:
            print(n//2)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(col_widths[i], 8, cell, border=1, align='L', fill=True )           
        else:
            pdf.set_fill_color(255, 255, 255)
            pdf.cell(col_widths[i], 8, cell, border=1, align='L', fill=True )  
    pdf.set_xy(20, 28+8*n)
    n=n+1

pdf_file_path = "pdf_with_image.pdf"
pdf.output(pdf_file_path)

print("PDF with image created successfully!")