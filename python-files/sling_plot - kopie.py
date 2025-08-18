# sling_plot.py
import matplotlib.pyplot as plt
import numpy as np
import xlwings as xw
xw.Book.caller()  # activeert xlwings context
from mpl_toolkits.mplot3d import Axes3D
import tempfile
import os
from datetime import datetime
import plotly.graph_objects as go
import trimesh
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm

def dispatch_plot():
    wb = xw.Book.caller()
    sht_input = wb.sheets["input sheet"]
   
    keuze = sht_input.range("E16").value  # controleer inhoud op 1 of 2
    
    if keuze == 1:
        make_plot()
    elif keuze == 2:
        make_plot_with_unequal_heights()
    else:
        raise ValueError(f"Onbekende waarde in L20: {keuze}. Verwacht 1 of 2.")
    
    make_3d_plot_matplotlib()

import os
import tempfile
import matplotlib.pyplot as plt
import xlwings as xw

def make_plot():
    timestamp = datetime.now().strftime('%H%M%S')
    temp_dir = tempfile.gettempdir()

    wb = xw.Book.caller()
    sht_input = wb.sheets["input sheet"]
    sht_plot = wb.sheets["input sheet"]
    sht_plot_report = wb.sheets["Report"]

    # Lees waarden uit Excel
    l1 = sht_input.range("E22").value or 0
    l2 = sht_input.range("E23").value or 0
    h = sht_input.range("E24").value or 0
    lx = sht_input.range("E29").value or 0
    ly = sht_input.range("E30").value or 0
    lxss = sht_input.range("E27").value or 0
    lyss = sht_input.range("E28").value or 0
    z = sht_input.range("E45").value or 0

    # Bovenaanzicht (XY)
    x_box = np.array([0, l1, l1, 0, 0])
    y_box = np.array([0, 0, l2, l2, 0])
    xy_cog = np.array([l1 / 2 + lx, l2 / 2 + ly])
    xy_ss = np.array([l1 / 2 + lxss, l2 / 2 + lyss])

    L_1line = np.array([[0, xy_ss[0]], [l2, xy_ss[1]]])
    L_2line = np.array([[0, xy_ss[0]], [0, xy_ss[1]]])
    L_3line = np.array([[l1, xy_ss[0]], [l2, xy_ss[1]]])
    L_4line = np.array([[l1, xy_ss[0]], [0, xy_ss[1]]])

    # Zijaanzicht XZ (zonder kader)
    x_side = np.array([0, l1, l1, 0, 0])
    z_side = np.array([0, 0, h, h, 0])
    x_ss_side = l1 / 2 + lxss
    z_ss_side = z

    # Zijaanzicht YZ (zonder kader)
    y_side = np.array([0, 0, l2, l2, 0])
    z_side_yz = np.array([0, h, h, 0, 0])
    y_ss_side = l2 / 2 + lyss
    z_ss_side = z

    fig1, axs1 = plt.subplots(figsize=(5, 5))

    axs1.plot(x_box, y_box, 'k', linewidth=2)
    axs1.plot(L_1line[0], L_1line[1], '-or', linewidth=1, markersize=3)
    axs1.plot(L_2line[0], L_2line[1], '-or', linewidth=1, markersize=3)
    axs1.plot(L_3line[0], L_3line[1], '-or', linewidth=1, markersize=3)
    axs1.plot(L_4line[0], L_4line[1], '-or', linewidth=1, markersize=3)
    axs1.plot(xy_cog[0], xy_cog[1], '+b', markersize=10)
    # Lichtgrijze stippellijnen door het midden
    axs1.plot([l1/2, l1/2], [0, l2], linestyle='--', color='lightgray', linewidth=1)  # verticale lijn
    axs1.plot([0, l1], [l2/2, l2/2], linestyle='--', color='lightgray', linewidth=1)  # horizontale lijn

    # Zet breedte en hoogte voor beide aanzichten gelijk
    max_width = max(l1, l2) *1.2
    max_height = max(z_ss_side, z_ss_side) *1.2 
    
    # Hoekpunten container A t/m D
    hoekpunten = {'A': (-100,0), 'B': (l1+400,0), 'C': (l1+400,l2), 'D': (-100,l2) , 'l;1': (l1/2,-650), 'l;2': (l1+700, l2/2)}
    for label, (x, y) in hoekpunten.items():
        axs1.text(x, y, label, fontsize=12, fontweight='bold', color='black', 
                    verticalalignment='bottom', horizontalalignment='right')
    
    # Labels slinglijnen L1 t/m L4 (plaatsen bij het midden van elke lijn)
    L_labels = {
        'L1': ((0 + xy_ss[0]) / 2, (l2 + xy_ss[1]-800) / 2),
        'L2': ((0 + xy_ss[0]) / 2, (0 + xy_ss[1]+400) / 2),
        'L3': ((l1 + xy_ss[0]) / 2, (l2 + xy_ss[1]-800) / 2),
        'L4': ((l1 + xy_ss[0]) / 2, (0 + xy_ss[1]+400) / 2),
    }
    for label, (x, y) in L_labels.items():
        axs1.text(x, y, label, fontsize=10, color='red', fontweight='bold',
                    verticalalignment='bottom', horizontalalignment='center')
    
    axs1.set_aspect('equal')
    axs1.axis('off')
    axs1.set_title('Top view (XY)', fontsize=16, fontname='Arial')
    axs1.set_xlim(-50, (l1 *1.2))
    axs1.set_ylim(-50, (l2 *1.2))
    axs1.set_aspect('equal')

    file1 = os.path.join(temp_dir, f"sling_top_{timestamp}.png")
    fig1.savefig(file1, bbox_inches='tight')
    plt.close(fig1)

    # Verwijder bestaande afbeelding in sht_plot
    for pic in sht_plot.pictures:
        if pic.name == "SlingPlotXY":
            pic.delete()

    # Verwijder bestaande afbeelding in sht_plot_report
    for pic in sht_plot_report.pictures:
        if pic.name == "SlingPlotXY":
            pic.delete()

    # Voeg daarna pas de nieuwe toe
    sht_plot.pictures.add(file1, name="SlingPlotXY", update=True, left=650, top=250)
    # pic = sht_plot_report.pictures.add(file1, name="SlingPlotXY", update=True, anchor=sht_plot_report.range("A28"))
    # pic.width = 150
    # pic.height = 225

    # Nieuwe afbeelding in sht_plot_report (gecentreerd in merge-cel A28)
    rng = sht_plot_report.range("A29").merge_area
    cell_left = rng.left
    cell_top = rng.top
    cell_width = rng.width
    cell_height = rng.height

    pic = sht_plot_report.pictures.add(file1, name="SlingPlotXY", update=True)
    pic.width = 150
    pic.height = 225

    # Centreer afbeelding in merge-bereik
    pic.left = cell_left + (cell_width - pic.width) / 2
    pic.top = cell_top + (cell_height - pic.height) / 2

    # Zijaanzicht XZ
    fig2, axs2 = plt.subplots(figsize=(5, 5))

    axs2.plot([100, l1], [100, 100], 'k', linewidth=2)
    axs2.plot([100, x_ss_side], [100, z_ss_side], '-or', linewidth=1, markersize=3)
    axs2.plot([l1, x_ss_side], [100, z_ss_side], '-or', linewidth=1, markersize=3)

    # Hoogtelijn tekenen (bij sling-top Z)
    axs2.plot([x_ss_side, x_ss_side], [100, z_ss_side], '--k', linewidth=1)
    axs2.text(x_ss_side + 0.05 * l1, z_ss_side / 2, 'l;3', fontsize=10, color='black',
                verticalalignment='center', horizontalalignment='left')
    
    # Hoekpunten container A en B
    hoekpunten = {'A': (-100,0), 'B': (l1+400,0)}
    for label, (x, y) in hoekpunten.items():
        axs2.text(x, y, label, fontsize=12, fontweight='bold', color='black', 
                    verticalalignment='bottom', horizontalalignment='right')

    # Labels slinglijnen L2 en L4 (deze twee lijnen in zijaanzicht)
    axs2.text(x_ss_side / 2, (z_ss_side / 2)-800, 'L2', fontsize=10, color='red', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')
    axs2.text((l1 + x_ss_side) / 2, (z_ss_side / 2)-800, 'L4', fontsize=10, color='red', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')
    
    # Label top Z (hoogte midden container)
    axs2.text(x_ss_side, z+100, 'Z', fontsize=12, color='blue', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')
    # Korte lichtgrijze stippellijn midden XZ-breedteh
    axs2.plot([l1/2, l1/2], [0, 0.13*z], linestyle='--', color='lightgray', linewidth=1)
    
    axs2.axis('off')
    axs2.set_title('Side view (XZ)', x = (x_ss_side/l1)*0.6, fontsize=16, fontname='Arial')
    axs2.set_xlim(-50, (l1 *1.2))
    axs2.set_ylim(-50, (z *1.2))
    axs2.set_aspect('equal')

    file2 = os.path.join(temp_dir, f"sling_xz_{timestamp}.png")
    fig2.savefig(file2, bbox_inches='tight')
    plt.close(fig2)

    # Verwijder bestaande afbeelding in sht_plot
    for pic in sht_plot.pictures:
        if pic.name == "SlingPlotXZ":
            pic.delete()

    # Verwijder bestaande afbeelding in sht_plot_report
    for pic in sht_plot_report.pictures:
        if pic.name == "SlingPlotXZ":
            pic.delete()

    # Voeg daarna pas de nieuwe toe
    sht_plot.pictures.add(file2, name="SlingPlotXZ", update=True, left=950, top=250)
    # pic2 = sht_plot_report.pictures.add(file2, name="SlingPlotXZ", update=True, anchor=sht_plot_report.range("A68"))
    # pic2.width = 150
    # pic2.height = 225

    # Nieuwe afbeelding in sht_plot_report (gecentreerd in merge-cel A28)
    rng = sht_plot_report.range("A68").merge_area
    cell_left = rng.left
    cell_top = rng.top
    cell_width = rng.width
    cell_height = rng.height

    pic2 = sht_plot_report.pictures.add(file2, name="SlingPlotXZ", update=True)
    pic2.width = 150
    pic2.height = 225

    # Centreer afbeelding in merge-bereik
    pic2.left = cell_left + (cell_width - pic2.width) / 2
    pic2.top = cell_top + (cell_height - pic2.height) / 2

    # Zijaanzicht YZ
    fig3, axs3 = plt.subplots(figsize=(5, 5))

    axs3.plot([100, l2], [100, 100], 'k', linewidth=2)
    axs3.plot([100, y_ss_side], [100, z_ss_side], '-or', linewidth=1, markersize=3)
    axs3.plot([l2, y_ss_side], [100, z_ss_side], '-or', linewidth=1, markersize=3)

    # Hoogtelijn tekenen (bij sling-top Z)
    axs3.plot([y_ss_side, y_ss_side], [100, z_ss_side], '--k', linewidth=1)
    axs3.text(y_ss_side + 0.05 * l2, z_ss_side / 2, 'l;3', fontsize=10, color='black',
                verticalalignment='center', horizontalalignment='left')

    # Hoekpunten container B en C
    hoekpunten = {'B': (-100,0), 'C': (l2+400,0)}
    for label, (x, y) in hoekpunten.items():
        axs3.text(x, y, label, fontsize=12, fontweight='bold', color='black', 
                    verticalalignment='bottom', horizontalalignment='right')

    # Labels slinglijnen L4 en L3 (deze lijnen in YZ aanzicht)
    axs3.text(y_ss_side / 2, (z_ss_side / 2)-800, 'L4', fontsize=10, color='red', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')
    axs3.text((l2 + y_ss_side) / 2, (z_ss_side / 2) -800, 'L3', fontsize=10, color='red', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')
    
    # Label top Z (hoogte midden container)
    axs3.text(y_ss_side, z+100, 'Z', fontsize=12, color='blue', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')

    # Korte lichtgrijze stippellijn midden XZ-breedte
    axs3.plot([l2/2, l2/2], [0, 0.13*z], linestyle='--', color='lightgray', linewidth=1)

    axs3.axis('off')
    axs3.set_title('Side view (YZ)', x = ((y_ss_side/l2)*0.6), fontsize=16, fontname='Arial')
    axs3.set_xlim(-50, (l2 *1.2))
    axs3.set_ylim(-50, (z *1.2))
    axs3.set_aspect('equal')

    file3 = os.path.join(temp_dir, f"sling_yz_{timestamp}.png")
    fig3.savefig(file3, bbox_inches='tight')
    plt.close(fig3)

    # Verwijder bestaande afbeelding in sht_plot
    for pic in sht_plot.pictures:
        if pic.name == "SlingPlotYZ":
            pic.delete()

    # Verwijder bestaande afbeelding in sht_plot_report
    for pic in sht_plot_report.pictures:
        if pic.name == "SlingPlotYZ":
            pic.delete()

    # Voeg daarna pas de nieuwe toe
    sht_plot.pictures.add(file3, name="SlingPlotYZ", update=True, left=1250, top=250)
    # pic3 = sht_plot_report.pictures.add(file3, name="SlingPlotYZ", update=True, anchor=sht_plot_report.range("D68"))
    # pic3.width = 150
    # pic3.height = 225

    # Nieuwe afbeelding in sht_plot_report (gecentreerd in merge-cel A28)
    rng = sht_plot_report.range("D68").merge_area
    cell_left = rng.left
    cell_top = rng.top
    cell_width = rng.width
    cell_height = rng.height

    pic3 = sht_plot_report.pictures.add(file3, name="SlingPlotYZ", update=True)
    pic3.width = 150
    pic3.height = 225

    # Centreer afbeelding in merge-bereik
    pic3.left = cell_left + (cell_width - pic3.width) / 2
    pic3.top = cell_top + (cell_height - pic3.height) / 2

    return file1, file2, file3

def make_plot_with_unequal_heights():
    wb = xw.Book.caller()
    sht_input = wb.sheets["input sheet"]
    sht_plot = wb.sheets["input sheet"]

    # Lees waarden uit Excel
    l1 = sht_input.range("E20").value or 0
    l2 = sht_input.range("E21").value or 0
    lx = sht_input.range("E27").value or 0
    ly = sht_input.range("E28").value or 0
    lxss = sht_input.range("E25").value or 0
    lyss = sht_input.range("E26").value or 0
    h_left = sht_input.range("E22").value or 0
    h_right = sht_input.range("E23").value or 0
    z = sht_input.range("E80").value or 0

    h_diff = abs(h_left - h_right)

    # Zet breedte en hoogte voor beide aanzichten gelijk
    max_width = max(l1, l2) *1.2
    max_height = z *1.2 

    # Bovenaanzicht (XY)
    x_box = np.array([0, l1, l1, 0, 0])
    y_box = np.array([0, 0, l2, l2, 0])
    xy_cog = np.array([l1 / 2 + lx, l2 / 2 + ly])
    xy_ss = np.array([l1 / 2 + lxss, l2 / 2 + lyss])

    L_1line = np.array([[0, xy_ss[0]], [l2, xy_ss[1]]])
    L_2line = np.array([[0, xy_ss[0]], [0, xy_ss[1]]])
    L_3line = np.array([[l1, xy_ss[0]], [l2, xy_ss[1]]])
    L_4line = np.array([[l1, xy_ss[0]], [0, xy_ss[1]]])

    x_ss_side = l1 / 2 + lxss
    y_ss_side = l2 / 2 + lyss

    fig, axs = plt.subplots(1, 3, figsize=(15, 4))

    # Top view
    axs[0].plot(x_box, y_box, 'k', linewidth=2)
    axs[0].plot(L_1line[0], L_1line[1], '-or', linewidth=1, markersize=3)
    axs[0].plot(L_2line[0], L_2line[1], '-or', linewidth=1, markersize=3)
    axs[0].plot(L_3line[0], L_3line[1], '-or', linewidth=1, markersize=3)
    axs[0].plot(L_4line[0], L_4line[1], '-or', linewidth=1, markersize=3)
    axs[0].plot(xy_cog[0], xy_cog[1], '+b', markersize=10)
    axs[0].plot([l1/2, l1/2], [0, l2], linestyle='--', color='lightgray', linewidth=1)
    axs[0].plot([0, l1], [l2/2, l2/2], linestyle='--', color='lightgray', linewidth=1)

    hoekpunten = {'A': (-100,0), 'B': (l1+400,0), 'C': (l1+400,l2), 'D': (-100,l2) , 'l;1': (l1/2,-650), 'l;2': (l1+700, l2/2)}
    for label, (x, y) in hoekpunten.items():
        axs[0].text(x, y, label, fontsize=12, fontweight='bold', color='black', 
                    verticalalignment='bottom', horizontalalignment='right')

    L_labels = {
        'L1': ((0 + xy_ss[0]) / 2, (l2 + xy_ss[1]-800) / 2),
        'L2': ((0 + xy_ss[0]) / 2, (0 + xy_ss[1]+400) / 2),
        'L3': ((l1 + xy_ss[0]) / 2, (l2 + xy_ss[1]-800) / 2),
        'L4': ((l1 + xy_ss[0]) / 2, (0 + xy_ss[1]+400) / 2),
    }
    for label, (x, y) in L_labels.items():
        axs[0].text(x, y, label, fontsize=10, color='red', fontweight='bold',
                    verticalalignment='bottom', horizontalalignment='center')
    
    axs[0].set_aspect('equal')
    axs[0].axis('off')
    axs[0].set_title('Top view (XY)')
    axs[0].set_xlim(-lijnlengte, (l1 *1.2))
    axs[0].set_ylim(-lijnlengte, (l2 *1.2))
    axs[0].set_aspect('equal')

    # Side view XZ

    lijnlengte = 800  # of schaalbaar zoals l1 * 0.05
    # A: gecentreerd rond x = 100
    axs[1].plot([100 - lijnlengte / 2, 100 + lijnlengte / 2], [100 + h_diff, 100 + h_diff], '--k', linewidth=1)
    # B: gecentreerd rond x = l1
    axs[1].plot([l1 - lijnlengte / 2, l1 + lijnlengte / 2], [100, 100], '--k', linewidth=1)
    axs[1].plot([0 - lijnlengte / 2, l1 + lijnlengte / 2], [100-h_left, 100-h_left], linestyle='--', color='black', linewidth=1)

    axs[1].plot([100, x_ss_side], [(100 + h_diff), z], '-or', linewidth=1, markersize=3)
    axs[1].plot([l1, x_ss_side], [100, z], '-or', linewidth=1, markersize=3)

    axs[1].plot([100, 100], [100-h_left, 100+h_diff], '--k', linewidth=1)
    
    axs[1].text(0 + 0.05 * l1, ((100-h_left) + (100+h_diff))/2, 'l;3;1', fontsize=10, color='black',
                verticalalignment='center', horizontalalignment='left')
    
    axs[1].plot([l1, l1], [100-h_left, 100], '--k', linewidth=1)

    axs[1].text(l1 + 0.05 * l1, ((100-h_left) + 100)/2, 'l;3;2', fontsize=10, color='black',
                verticalalignment='center', horizontalalignment='left')
    
    axs[1].text(x_ss_side, z+100, 'Z', fontsize=12, color='blue', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')

    hoekpunten = {'A': (-100,100 + h_diff), 'B': (l1+400,100)}
    for label, (x, y) in hoekpunten.items():
        axs[1].text(x, y, label, fontsize=12, fontweight='bold', color='black', 
                    verticalalignment='bottom', horizontalalignment='right')

    axs[1].text(x_ss_side / 2, (z / 2)-800, 'L2', fontsize=10, color='red', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')
    axs[1].text((l1 + x_ss_side) / 2, (z / 2)-800, 'L4', fontsize=10, color='red', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')

    axs[1].axis('off')
    axs[1].set_title('Side view (XZ)', x = (x_ss_side/l1))
    axs[1].set_xlim(0, (l1 *1.2))
    axs[1].set_ylim(0, (z *1.2))
    #axs[1].set_aspect('equal')

    # Side view YZ
    axs[2].plot([100, l2], [100, 100], 'k', linewidth=2)
    axs[2].plot([100, l2], [100 + h_diff, 100+ h_diff], '--k', linewidth=2)
    axs[2].plot([100, y_ss_side], [100 + h_diff, z], '--or', linewidth=1, markersize=3) # L4
    axs[2].plot([l2, y_ss_side], [100 + h_diff, z], '--or', linewidth=1, markersize=3) # L3
    axs[2].plot([100, y_ss_side], [100 , z], '-or', linewidth=1, markersize=3) # L2
    axs[2].plot([l2, y_ss_side], [100, z], '-or', linewidth=1, markersize=3) # L1
    
    axs[2].text(y_ss_side, z+100, 'Z', fontsize=12, color='blue', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')

    hoekpunten = {'A': (-100,h_diff), 'D': (l2+400,h_diff),'B': (-100,0), 'C': (l2+400,0)}
    for label, (x, y) in hoekpunten.items():
        axs[2].text(x, y, label, fontsize=12, fontweight='bold', color='black', 
                    verticalalignment='bottom', horizontalalignment='right')

    axs[2].text(y_ss_side / 2, (z / 2)+ h_diff, 'L2', fontsize=10, color='red', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')
    axs[2].text((l2 + y_ss_side) / 2, (z / 2)+h_diff, 'L1', fontsize=10, color='red', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')
    axs[2].text((y_ss_side / 2)+300, (z / 2)-800, 'L4', fontsize=10, color='red', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')
    axs[2].text(((l2 + y_ss_side) / 2)-300, (z / 2) -800, 'L3', fontsize=10, color='red', fontweight='bold',
                verticalalignment='bottom', horizontalalignment='center')

    axs[2].axis('off')
    axs[2].set_title('Side view (YZ)', x = ((y_ss_side/l2)*0.5))
    axs[2].set_xlim(0, (l2 *1.2))
    axs[2].set_ylim(0, (z *1.2))
    axs[2].set_aspect('equal')

    # Verwijder bestaande afbeelding uit Excel
    if "SlingPlot" in [pic.name for pic in sht_plot.pictures]:
        sht_plot.pictures["SlingPlot"].delete()

    # Maak tijdelijk pad
    import tempfile
    import os
    from datetime import datetime
    temp_dir = tempfile.gettempdir()
    filename = f"sling_plot_unequal_{datetime.now().strftime('%H%M%S')}.png"
    img_path = os.path.join(temp_dir, filename)

    # Sla figuur op
    fig.savefig(img_path, bbox_inches='tight')

    # Voeg afbeelding toe in Excel
    sht_plot.pictures.add(img_path, name='SlingPlot', update=True, left=650, top=240)

    plt.close()

def make_3d_plot_matplotlib():
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import numpy as np
    import os, tempfile
    from datetime import datetime
    import xlwings as xw

    wb = xw.Book.caller()
    sht_input = wb.sheets["input sheet"]

    # Waarden uit Excel
    l1 = sht_input.range("E22").value or 0  # lengte
    l2 = sht_input.range("E23").value or 0  # breedte
    h = sht_input.range("E24").value or 0   # hoogte
    lx = sht_input.range("E27").value or 0  # offset COG x
    ly = sht_input.range("E29").value or 0  # offset COG y
    lxss = sht_input.range("E28").value or 0 # offset sling x
    lyss = sht_input.range("E30").value or 0 # offset sling y
    z_ss_side = sht_input.range("E45").value or 0  # slingpunt hoogte

    # Coördinaten slingpunt en COG
    x_cog = l1/2 + lx
    y_cog = l2/2 + ly
    z_cog = h/2

    x_ss = l1/2 + lxss
    y_ss = l2/2 + lyss
    z_ss = z_ss_side

    # Container hoekpunten
    corners = np.array([
        [0, 0, 0], [l1, 0, 0], [l1, l2, 0], [0, l2, 0],  # onderzijde
        [0, 0, h], [l1, 0, h], [l1, l2, h], [0, l2, h],  # bovenzijde
    ])

    edges = [
        (0,1), (1,2), (2,3), (3,0),  # bodem
        (4,5), (5,6), (6,7), (7,4),  # bovenkant
        (0,4), (1,5), (2,6), (3,7)   # verticaal
    ]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Teken container-randen
    for i, j in edges:
        ax.plot(
            [corners[i][0], corners[j][0]],
            [corners[i][1], corners[j][1]],
            [corners[i][2], corners[j][2]],
            'gray'
        )

    # Teken slinglijnen (van container naar slingpunt)
    for i in [4,5,6,7]:  # bovenzijde hoekpunten
        ax.plot(
            [corners[i][0], x_ss],
            [corners[i][1], y_ss],
            [corners[i][2], z_ss],
            'r--'
        )

    # Slingpunt
    ax.scatter(x_ss, y_ss, z_ss, color='red', s=50)
    ax.text(x_ss, y_ss, z_ss + 100, "Slingpunt", color='red')

    # Zwaartepunt
    ax.scatter(x_cog, y_cog, z_cog, color='blue', s=50)
    ax.text(x_cog, y_cog, z_cog + 100, "COG", color='blue')

    # Labels & zicht
    ax.set_xlabel('X (Lengte)')
    ax.set_ylabel('Y (Breedte)')
    ax.set_zlabel('Z (Hoogte)')
    ax.set_title('3D Sling Visualisatie')

    ax.view_init(elev=20, azim=45)
    ax.set_box_aspect([l1, l2, h])  # gelijke schaal

    # Verwijder bestaande afbeelding uit Excel
    if "SlingPlot3D" in [pic.name for pic in sht_input.pictures]:
        sht_input.pictures["SlingPlot3D"].delete()

    # Sla afbeelding tijdelijk op
    temp_dir = tempfile.gettempdir()
    filename = f"sling_plot_3D_{datetime.now().strftime('%H%M%S')}.png"
    img_path_3D = os.path.join(temp_dir, filename)
    fig.savefig(img_path_3D, bbox_inches='tight')
    plt.close()

    # Voeg toe aan Excel
    sht_input.pictures.add(img_path_3D, name='SlingPlot3D', update=True, left=650, top=600)
    #sht_input.pictures.add(img_path_3D, name='SlingPlot3D', update=True)

    return img_path_3D