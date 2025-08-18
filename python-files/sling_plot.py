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

    #test_add_picture()
    
    keuze = sht_input.range("E16").value  # controleer inhoud op 1 of 2
    
    if keuze == 1:
        make_plot()
    elif keuze == 2:
        make_plot_with_unequal_heights()
    else:
        raise ValueError(f"Onbekende waarde in L20: {keuze}. Verwacht 1 of 2.")
    
    #make_3d_plot()

    #make_3d_plot_plotly()

    #make_stl()

    make_3d_plot_matplotlib()

    #make_pdf_report()

import os
import tempfile
import matplotlib.pyplot as plt
import xlwings as xw

def _debug_write(wb, msg):
    # schrijf debug in A1 (handig als Excel vastloopt zie je laatste stap)
    try:
        wb.sheets[0].range("A1").value = str(msg)
    except Exception:
        pass

def test_add_picture():
    wb = xw.Book.caller()
    sht = wb.sheets["input sheet"]  # pas aan indien andere naam
    temp_dir = tempfile.gettempdir()
    file = os.path.join(temp_dir, "test_small_image.png")

    # maak een heel kleine test-afbeelding
    fig, ax = plt.subplots(figsize=(1.5, 1.0))
    ax.plot([0,1,2],[0,1,0])
    ax.axis('off')
    fig.savefig(file, dpi=60, bbox_inches='tight')
    plt.close(fig)

    _debug_write(wb, f"saved:{file}")

    # probeer Shapes.AddPicture (vaak stabieler dan pictures.add)
    try:
        rng = sht.range("K2")
        left, top, width, height = rng.left, rng.top, rng.width, rng.height

        # screen updating uit (vermindert risico op freeze)
        wb.app.api.ScreenUpdating = False

        # verwijder shape met zelfde naam indien aanwezig
        shape_name = "TEST_SlingPic"
        try:
            shp = sht.api.Shapes.Item(shape_name)
            shp.Delete()
            _debug_write(wb, "deleted existing shape")
        except Exception:
            _debug_write(wb, "no existing shape to delete")

        # AddPicture(Filename, LinkToFile, SaveWithDocument, Left, Top, Width, Height)
        shp = sht.api.Shapes.AddPicture(file, False, True, left, top, width, height)
        shp.Name = shape_name
        shp.Placement = 1   # xlMoveAndSize
        try:
            shp.LockAspectRatio = False
        except Exception:
            pass

        _debug_write(wb, "shape_added_ok")

    except Exception as e:
        _debug_write(wb, f"ERROR:{e}")
        raise
    finally:
        wb.app.api.ScreenUpdating = True

    return file


def _add_picture_anchor(sht, image_path, cell_addr, pic_name, scale_to_cell=True, dpi=120):
    """
    Veilig: verwijder bestaande picture met dezelfde naam, voeg nieuwe toe
    en anchor/scale naar gegeven cel.
    """
    # Verwijder bestaande picture met die naam (indien aanwezig)
    try:
        existing = sht.pictures[pic_name]
        existing.delete()
    except Exception:
        pass

    rng = sht.range(cell_addr)

    # Voeg toe (gebruik update=False — we verwijderen eerst dus updaten niet nodig)
    pic = sht.pictures.add(image_path, name=pic_name, update=False,
                           left=rng.left, top=rng.top)

    # Probeer aspect ratio unlock en plaatsing (move and size)
    try:
        # Soms direct op api, soms op ShapeRange required depending on Excel version
        try:
            pic.api.LockAspectRatio = False
        except Exception:
            pic.api.ShapeRange.LockAspectRatio = 0
    except Exception:
        pass

    # if scale_to_cell:
    #     # Schaal exact naar celgrootte. Als je wil dat aspect ratio behouden blijft,
    #     # zet height/of width alleen op één waarde of bereken aspect.
    #     pic.width = rng.width
    #     pic.height = rng.height

    # Zet placement zodat de afbeelding met cellen meebeweegt en -schaalt
    try:
        pic.api.Placement = 1  # xlMoveAndSize
    except Exception:
        try:
            pic.api.ShapeRange.Placement = 1
        except Exception:
            pass

    return pic

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

def make_3d_plot():
    # Dummywaardes – vervang deze door Excel input indien nodig
    l1, l2, h = 6000, 2500, 2600  # lengte, breedte, hoogte container
    lxss, lyss = 200, -100        # slingpunt offset X en Y
    z_ss_side = h                 # slingpunt op top

    # Hoekpunten van de kubus (container)
    x = [0, l1, l1, 0, 0, l1, l1, 0]
    y = [0, 0, l2, l2, 0, 0, l2, l2]
    z = [0, 0, 0, 0, h, h, h, h]

    # Slingpunt
    x_ss = l1/2 + lxss
    y_ss = l2/2 + lyss
    z_ss = z_ss_side

    # Start 3D plot
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    # Plot randen van de container
    edges = [
        (0,1), (1,2), (2,3), (3,0),  # bodem
        (4,5), (5,6), (6,7), (7,4),  # top
        (0,4), (1,5), (2,6), (3,7)   # verticale lijnen
    ]
    for i,j in edges:
        ax.plot([x[i], x[j]], [y[i], y[j]], [z[i], z[j]], 'k')

    # Plot slingpunt
    ax.scatter(x_ss, y_ss, z_ss, color='red', s=50)
    ax.text(x_ss, y_ss, z_ss + 200, 'Slingpunt', color='red')

    # Labels
    ax.set_xlabel('X (lengte)')
    ax.set_ylabel('Y (breedte)')
    ax.set_zlabel('Z (hoogte)')
    ax.set_title('3D Sling Visualisatie')

    # Aanzicht instellen
    ax.view_init(elev=20, azim=45)  # draaihoek van de camera

    # Maak tijdelijk pad
    import tempfile
    import os
    from datetime import datetime
    temp_dir = tempfile.gettempdir()
    filename = f"sling_plot_3D_{datetime.now().strftime('%H%M%S')}.png"
    img_path = os.path.join(temp_dir, filename)

    # Sla figuur op
    fig.savefig(img_path, bbox_inches='tight')

    # Voeg afbeelding toe in Excel
    wb = xw.Book.caller()
    sht_plot = wb.sheets["input sheet"]
    sht_plot.pictures.add(img_path, name='SlingPlot_3D', update=True, left=650, top=540)
    plt.close()

def make_3d_plot_plotly():
        # Haal gegevens uit Excel
    wb = xw.Book.caller()
    sht = wb.sheets["input sheet"]

    l1 = sht.range("E20").value or 0
    l2 = sht.range("E21").value or 0
    h = sht.range("E22").value or 0
    lxss = sht.range("E26").value or 0
    lyss = sht.range("E28").value or 0
    z = sht.range("E80").value or 0

    # Bereken slingpunt
    x_ss = l1 / 2 + lxss
    y_ss = l2 / 2 + lyss
    z_ss = z

    # Containerhoeken (onder + boven)
    corners = [
        (0, 0, 0), (l1, 0, 0), (l1, l2, 0), (0, l2, 0),
        (0, 0, h), (l1, 0, h), (l1, l2, h), (0, l2, h)
    ]
    x, y, z_vals = zip(*corners)

    # Containerlijnen
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]
    lines = []
    for i, j in edges:
        lines.append(go.Scatter3d(
            x=[x[i], x[j]], y=[y[i], y[j]], z=[z_vals[i], z_vals[j]],
            mode='lines',
            line=dict(color='black', width=4),
            showlegend=False
        ))

    # Slinglijnen van 4 bovenhoeken naar slingpunt
    bovenhoeken = [4, 5, 6, 7]
    for i in bovenhoeken:
        lines.append(go.Scatter3d(
            x=[x[i], x_ss], y=[y[i], y_ss], z=[z_vals[i], z_ss],
            mode='lines',
            line=dict(color='red', width=3),
            showlegend=False
        ))

    # Slingpunt
    slingpunt = go.Scatter3d(
        x=[x_ss], y=[y_ss], z=[z_ss],
        mode='markers+text',
        marker=dict(size=6, color='red'),
        text=["Slingpunt"],
        textposition="top center",
        name="Slingpunt"
    )

    # Plot alles
    layout = go.Layout(
        scene=dict(
            xaxis_title='X (lengte)',
            yaxis_title='Y (breedte)',
            zaxis_title='Z (hoogte)',
            aspectmode='data'
        ),
        title="Interactieve 3D-visualisatie slingopstelling"
    )

    fig = go.Figure(data=lines + [slingpunt], layout=layout)
    fig.show()

def make_cylinder(start, end, radius=50, sections=16):
    vec = np.array(end) - np.array(start)
    height = np.linalg.norm(vec)
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)

    direction = vec / height
    z_axis = np.array([0, 0, 1])
    rot_matrix = trimesh.geometry.align_vectors(z_axis, direction)

    if rot_matrix is not None:
        cyl.apply_transform(rot_matrix)

    cyl.apply_translation(start)
    return cyl

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


def make_stl():
    # Excel lezen
    wb = xw.Book.caller()
    sht = wb.sheets["input sheet"]

    l1 = sht.range("E20").value or 0
    l2 = sht.range("E21").value or 0
    h = sht.range("E22").value or 0
    lxss = sht.range("E26").value or 0
    lyss = sht.range("E28").value or 0
    z_ss = sht.range("E80").value or 0
    lx = sht.range("E25").value or 0
    ly = sht.range("E27").value or 0

    x_ss = l1/2 + lxss
    y_ss = l2/2 + lyss
    x_cog = l1/2 + lx
    y_cog = l2/2 + ly
    z_cog = h

    # Container als box
    container = trimesh.creation.box(extents=(l1, l2, h))
    container.apply_translation((l1/2, l2/2, h/2))

    # Slinglijnen als cilinders
    corners = [
        (0, 0, h),
        (l1, 0, h),
        (l1, l2, h),
        (0, l2, h)
    ]
    sling_lines = []
    for corner in corners:
        cyl = make_cylinder(corner, (x_ss, y_ss, z_ss), radius=h*0.01)
        sling_lines.append(cyl)

    # Slingpunt als bol
    sling_ball = trimesh.creation.icosphere(radius=h*0.02)
    sling_ball.apply_translation((x_ss, y_ss, z_ss))

    # COG als bol
    cog_ball = trimesh.creation.icosphere(radius=h*0.02)
    cog_ball.apply_translation((x_cog, y_cog, z_cog))

    # Combineren
    combined = container
    for part in sling_lines:
        combined += part
    combined += sling_ball
    combined += cog_ball

    # Bestandspad
    save_dir = r"R:\Schoondijke\Temp Jelle Voogdt\Excel automatisatie\Sling calculation"
    filename = f"slingopstelling_{datetime.now().strftime('%Y%m%d_%H%M%S')}.stl"
    full_path = os.path.join(save_dir, filename)

    # Opslaan
    combined.export(full_path)

    # Bevestiging terug in Excel
    sht.range("I2").value = f"STL opgeslagen op:\n{full_path}"
    print(f"STL opgeslagen: {full_path}")


    import xlwings as xw

def make_pdf_report():
    # 📥 1. Data uit Excel
    wb = xw.Book.caller()
    sht = wb.sheets["input sheet"]

    # Invoerwaarden
    l1 = sht.range("E20").value or 0
    l2 = sht.range("E21").value or 0
    h = sht.range("E22").value or 0
    lxss = sht.range("E26").value or 0
    lyss = sht.range("E28").value or 0
    z = sht.range("E80").value or 0
    lx = sht.range("E25").value or 0
    ly = sht.range("E27").value or 0

    sling_angles = [sht.range(f"E{33+i}").value or 0 for i in range(4)]
    sling_forces_actual = [sht.range(f"E{45+i}").value or 0 for i in range(4)]
    sling_forces_design = [sht.range(f"E{50+i}").value or 0 for i in range(4)]
    sling_lengths = [sht.range(f"E{75+i}").value or 0 for i in range(4)]

    # 📸 2. Haal afbeeldingen uit Excel en sla tijdelijk op
    img_dir = os.environ['TEMP']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def export_picture(picture_name, filename):
        path = os.path.join(img_dir, filename)
        pic = sht.pictures[picture_name]
        pic.api.Copy()
        img = xw.apps.active.api.ActiveSheet.Paste()
        img_shape = xw.apps.active.api.Selection
        img_shape.CopyPicture(Format=2)  # bitmap
        import PIL.ImageGrab
        pil_img = PIL.ImageGrab.grabclipboard()
        pil_img.save(path)
        img_shape.Delete()
        return path

    # 📤 Exporteer afbeeldingen      
    img_sling_3d = make_3d_plot_matplotlib()
    img_sling_2d = make_plot()


    # 📄 3. Maak PDF
    pdf_path = os.path.join(
        r"R:\Schoondijke\Temp Jelle Voogdt\Excel automatisatie\Sling calculation",
        "Sling_Report.pdf"
    )
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Slingopstelling - Rapport", styles["Title"]))
    content.append(Spacer(1, 12))

    # Invoerwaarden-tabel
    table_data = [
        ["Parameter", "Waarde", "Eenheid"],
        ["Lengte (L1)", f"{l1:.0f}", "mm"],
        ["Breedte (L2)", f"{l2:.0f}", "mm"],
        ["Hoogte (H)", f"{h:.0f}", "mm"],
        ["Slingpunt", f"({l1/2 + lxss:.0f}, {l2/2 + lyss:.0f}, {z:.0f})", "mm"],
        ["COG", f"({l1/2 + lx:.0f}, {l2/2 + ly:.0f}, {h:.0f})", "mm"],
    ]
    for i in range(4):
        table_data.append([f"Sling angle L{i+1}", f"{sling_angles[i]:.1f}", "°"])
    for i in range(4):
        table_data.append([f"Sling force L{i+1} (actual)", f"{sling_forces_actual[i]:.1f}", "kN"])
    for i in range(4):
        table_data.append([f"Sling force L{i+1} (design)", f"{sling_forces_design[i]:.1f}", "kN"])
    for i in range(4):
        table_data.append([f"Sling length L{i+1}", f"{sling_lengths[i]:.0f}", "mm"])

    table = Table(table_data, colWidths=[120, 100, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ]))
    content.append(table)
    content.append(Spacer(1, 12))

    # Voeg afbeeldingen toe
    content.append(Paragraph("3D overzicht", styles["Heading3"]))
    content.append(Image(img_sling_3d, width=160 * mm, height=100 * mm))
    content.append(Spacer(1, 12))

    content.append(Paragraph("Top- en zijaanzichten", styles["Heading3"]))
    content.append(Image(img_sling_2d, width=160 * mm, height=100 * mm))
    content.append(Spacer(1, 12))

    doc.build(content)

    # Terugkoppeling naar Excel
    sht.range("I2").value = f"PDF opgeslagen:\n{pdf_path}"
    print(f"PDF rapport gegenereerd: {pdf_path}")








