import tkinter as tk
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import sys
import re
import subprocess
import os
import time
import pyautogui
import math
import threading
from tkinter import messagebox, filedialog
import http.server
import socketserver
import webbrowser
import cv2
from collections import Counter
import fitz  # PyMuPDF
import win32com.client
import glob
from lxml import etree
import lxml.html
import pandas as pd
from tkinter import ttk
import shutil
from pathlib import Path

PORT = 8000
x_cursor_live = 0
y_cursor_live = 0

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''''''''''''''COMPARAISON HTML TOP - XML'''''''''''''''''''''''''''''''''''''''''



def choose_file_dialog(title="SÃ©lectionnez un fichier", filetypes=(("All files", "*.*"),)):
    root = tk.Tk()
    filepath = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return filepath

def extract_xml_fields(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Erreur lors du parsing XML : {e}", file=sys.stderr)
        return None

    valeurs = {
        "Page.Titre": "",
        "Page.Repere": "",
        "Page.Objectif": ""
    }
    for elem in root.iter():
        if elem.tag == "Champ" or elem.tag.endswith("Champ"):
            id_attr = elem.attrib.get("id", "")
            if id_attr in valeurs:
                val = elem.attrib.get("value", "")
                if id_attr == "Page.Repere":
                    if len(val) > 1:
                        if val.startswith('-'):
                            val = val[1:]
                        if val.endswith('-'):
                            val = val[:-1]
                valeurs[id_attr] = val

    texte_pos0 = ""
    for g in root.iter():
        if (g.tag == "Gabarit" or g.tag.endswith("Gabarit")) and g.attrib.get("id", "") == "MOP_textuel":
            for desc in g.iter():
                if (desc.tag == "Texte" or desc.tag.endswith("Texte")) and desc.attrib.get("position", "") == "0":
                    val = desc.attrib.get("valeur", "")
                    texte_pos0 = val
                    break
            if texte_pos0:
                break

    # Version brute (pour affichage)
    concat_brut = " ".join(
    champ for champ in [
        valeurs["Page.Titre"],
        valeurs["Page.Repere"],
        texte_pos0,
        valeurs["Page.Objectif"]
    ] if champ
)


    # Version normalisÃ©e (pour comparaison)
    concat = concat_brut.replace("&#xA;&#xA;", "")
    concat = concat.replace("\n\n", "")
    concat = concat.replace("\r", "").replace("\n", "")
    concat = concat.lower().replace(" ", "")
    page_repere_clean = valeurs["Page.Repere"].lower().replace(" ", "")
    return concat, page_repere_clean, concat_brut


def extract_html_fields(html_path, xml_repere_clean=None):
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Erreur de lecture du fichier HTML : {e}", file=sys.stderr)
        return None

    soup = BeautifulSoup(content, "html.parser")
    td_list = soup.find_all('td')
    total_td = len(td_list)
    if total_td < 11:
        print(f"Attention : le document HTML contient moins de 11 balises <td> (trouvÃ© {total_td}).", file=sys.stderr)

    # 2. RÃ©cupÃ©rer le chiffre de la 6áµ‰ <td>
    page_num_digit = ""
    idx6 = 6 - 1
    if idx6 < total_td:
        td6 = td_list[idx6]
        input_el = td6.find('input', attrs={"value": True})
        val = None
        if input_el and input_el.has_attr('value'):
            val = input_el['value']
        else:
            any_with_value = td6.find(attrs={"value": True})
            if any_with_value and any_with_value.has_attr('value'):
                val = any_with_value['value']
        if val:
            # Extraire le premier caractÃ¨re s'il est chiffre
            first_char = val.strip()[0] if val.strip() else ""
            if first_char.isdigit():
                page_num_digit = first_char
            else:
                m = re.search(r'\d', val)
                if m:
                    page_num_digit = m.group(0)
    else:
        print("Avertissement : 6áµ‰ <td> non trouvÃ©e pour extraire le chiffre.", file=sys.stderr)

    # Extraire et nettoyer le texte dâ€™un <td> donnÃ©
    def get_td_text_by_index(idx_1based, remove_leading_digit=False):
        zero_idx = idx_1based - 1
        if zero_idx < 0 or zero_idx >= total_td:
            print(f"Avertissement : <td> numÃ©ro {idx_1based} non trouvÃ© (total {total_td}).", file=sys.stderr)
            return ""
        td = td_list[zero_idx]
        # Supprimer les <br>
        for br in td.find_all('br'):
            br.decompose()
        # Extraire texte brut
        text = td.get_text(separator="", strip=False)
        # Nettoyer retours Ã  la ligne, tabulations
        text = text.replace("\n", "").replace("\r", "").replace("\t", "")
        # Si on demande de supprimer le premier caractÃ¨re s'il est chiffre
        if remove_leading_digit and text and text[0].isdigit():
            text = text[1:]
        return text

    # 3. Extraction des diffÃ©rents td : td2, td1, td10, td11
    # td2 : idx 2, et on supprime le 1er caractÃ¨re si c'est chiffre
    td2_text = get_td_text_by_index(2, remove_leading_digit=False)
    td1_text = get_td_text_by_index(1, remove_leading_digit=True)
    td1_text_clean = td1_text.lower().replace(" ", "")

    # td10 et td11 : extraction simple
    td10_text = get_td_text_by_index(10, remove_leading_digit=False)
    td11_text = get_td_text_by_index(11, remove_leading_digit=False)

    # 4. concatÃ©nation et minuscules, suppression des espaces
    concat = "".join([td2_text, td1_text, td10_text, td11_text])
    concat = concat.lower().replace(" ", "")
    return concat, td1_text, td2_text, td10_text, td11_text





''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''''''''DETECTION DES CASES'''''''''''''''''''''''''''''''''''''''''''''''





def extract_tickbox_coordinates(html):
    pattern = re.compile(
        r'#Layer_TICKBOX(\d+)\s*{[^}]*?left:\s*(\d+)px;\s*top:\s*(\d+)px',
        re.MULTILINE
    )
    matches = pattern.findall(html)
    return [(int(m[1]), int(m[2])) for m in matches]
 
def euclidean_distance(point1, point2):
    return math.sqrt((int(point1[0]) - int(point2[0])) ** 2 + (int(point1[1])- int(point2[1])) ** 2)
 
def smallest_distance(point, points_list):
    if not points_list:
        print("Avertissement : la liste des points est vide, impossible de calculer la distance.")
        return None
    closest_point = points_list[0]
    min_distance = euclidean_distance(point, closest_point)
    for p in points_list:
        dist = euclidean_distance(point, p)
        if dist < min_distance:
            min_distance = dist
            closest_point = p
    return closest_point




def insert_script_in_html(html_body_path):
    # JavaScript Ã  insÃ©rer
    script = """
<script>
    document.addEventListener('mousemove', function(event) {
        var x = event.pageX;
        var y = event.pageY;
        fetch('/mouse_position?x=' + x + '&y=' + y);
    });
</script>
</body>
"""
 
# Parcours des fichiers HTML dans le dossier
    filepath = html_body_path
 
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    if "fetch('/mouse_position?x=' + x + '&y=' + y);" in content:
         print(f"âœ… Script dÃ©jÃ  insÃ©rÃ©")
    else:
        if '</body>' in content:
            content = content.replace('</body>', script)
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"âœ… Script insÃ©rÃ©")
        else:
            print(f"âš ï¸ Pas de </body> trouvÃ©")
 
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global x_cursor_live, y_cursor_live
        if self.path.startswith('/mouse_position'):
            query = self.path.split('?')[1]
            params = dict(qc.split('=') for qc in query.split('&'))
            x = params.get('x')
            y = params.get('y')
            #print(f"Mouse position - X: {x}, Y: {y}")
            x_cursor_live = x
            y_cursor_live = y
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            super().do_GET()  # GÃ¨re les fichiers HTML, images, CSS, etc.

def demarrage_serveur():      
    with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
        print(f"Serving on port {PORT}")
        httpd.serve_forever()



def render_html_to_pdf(html_file_path):
    nombre_cases_total = 0
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
 
    command = [
        chrome_path,
        html_file_path
    ]
 
    subprocess.Popen(command)
 
def find_black_pixel(image_path, threshold_distance):
    time.sleep(5)
    location = pyautogui.locateOnScreen(image_path)
    pyautogui.moveTo(location.left + location.width, location.top)

    root = tkinter.Tk()
    root.withdraw()  # Hide the root window

    if location:
        start_x = location.left + location.width
        start_y = location.top
        angle = 0
 
        direction_x = math.cos(math.radians(angle))
        direction_y = math.sin(math.radians(angle))
        current_x, current_y = start_x, start_y
        distance = 0
 
        screenshot = pyautogui.screenshot()
        while distance <= threshold_distance:
            pixel_color = screenshot.getpixel((int(current_x), int(current_y)))
            print(pixel_color)
            #pyautogui.moveTo((int(current_x), int(current_y)))
            #time.sleep(1)
            if pixel_color[0] < 200:
                print(f"Found black pixel at ({int(current_x)}, {int(current_y)}) after {distance} pixels.")
                distance = 0
                pyautogui.moveTo(start_x, start_y)
                angle -= 1
                direction_x = math.cos(math.radians(angle))
                direction_y = math.sin(math.radians(angle))
                current_x, current_y = start_x, start_y
            nbr_pixel = 3
            current_x += direction_x * nbr_pixel
            current_y += direction_y * nbr_pixel
            distance += nbr_pixel
        print(str(angle))


def find_and_move_to_all_images(image_path_1,image_path_2,image_path_3,image_path_4, threshold_distance, html_body_path, output_folder):
    # Pause de 3 secondes
    time.sleep(7)
    nombre_cases_total = 0

   
    # Recherche de toutes les occurrences de l'image Ã  l'Ã©cran
    locations = []
    try:
        locations_case_1 = list(pyautogui.locateAllOnScreen(image_path_1, confidence=0.8))
    except Exception:
        locations_case_1 = []
    try:
        locations_case_2 = list(pyautogui.locateAllOnScreen(image_path_2, confidence=0.8))
    except Exception:
        locations_case_2 = []
    try:
        locations_case_3 = list(pyautogui.locateAllOnScreen(image_path_3, confidence=0.8))
    except Exception:
        locations_case_3 = []
    try:
        locations_case_4 = list(pyautogui.locateAllOnScreen(image_path_4, confidence=0.8))
    except Exception:
        locations_case_4 = []

    locations = locations_case_1

    location_case_2_extrait = locations_case_2.copy()
    if locations != []:
        for k in locations_case_2:
            print(euclidean_distance(smallest_distance([k[0],k[1]],[sublist[0:2] for sublist in locations]),[k[0],k[1]]))
            if euclidean_distance(smallest_distance([k[0],k[1]],[sublist[0:2] for sublist in locations]),[k[0],k[1]]) < 10:
                location_case_2_extrait.remove(k)
   
    locations = locations_case_1 + location_case_2_extrait

    location_case_3_extrait = locations_case_3.copy()

    if locations != []:
        for k in locations_case_3:
            print(euclidean_distance(smallest_distance([k[0],k[1]],[sublist[0:2] for sublist in locations]),[k[0],k[1]]))
            if euclidean_distance(smallest_distance([k[0],k[1]],[sublist[0:2] for sublist in locations]),[k[0],k[1]]) < 10:
                location_case_3_extrait.remove(k)

    location_case_4_extrait = locations_case_4.copy()

    if locations != []:
        for k in locations_case_4:
            print(euclidean_distance(smallest_distance([k[0],k[1]],[sublist[0:2] for sublist in locations]),[k[0],k[1]]))
            if euclidean_distance(smallest_distance([k[0],k[1]],[sublist[0:2] for sublist in locations]),[k[0],k[1]]) < 10:
                location_case_4_extrait.remove(k)

    locations = locations + location_case_4_extrait

    print("-------------&&&&&&&&")  
    print(len(location_case_2_extrait))
    print("-----------------&&&&&&&&&&&&&")
    liste_angle = []
    liste_distance = []
    liste_x = []
    liste_y = []
    liste_defaut_x_angle = []
    liste_defaut_y_angle = []
    liste_defaut_x_distance = []
    liste_defaut_y_distance = []
    nombre_case = 0
    if locations:
        for location in locations:
            #print("point : " + str(location))
            #print("----")
           
            time.sleep(1)
            nombre_case = nombre_case + 1
            pyautogui.moveTo(location.left + location.width, location.top)
            start_x = location.left + location.width - 2
            start_y = location.top + 1
            angle = 0
   
            direction_x = math.cos(math.radians(angle))
            direction_y = math.sin(math.radians(angle))
            current_x, current_y = start_x, start_y
            distance = 0
   
            screenshot = pyautogui.screenshot()

            pixel_noir_trouve = 0
            while distance <= threshold_distance and angle > -10:
                pixel_color = screenshot.getpixel((int(current_x), int(current_y)))
                #print(pixel_color)
                #pyautogui.moveTo((int(current_x), int(current_y)))
                #time.sleep(0.5)
                if pixel_color[0] < 185 and distance > 1:
                    pixel_noir_trouve = 1
                    if angle == 0:
                        #print("------------")
                        liste_distance.append(distance)
                        if distance < 9 or distance > 25:
                            time.sleep(0.5)
                            liste_defaut_x_distance.append(x_cursor_live)
                            liste_defaut_y_distance.append(y_cursor_live)
                        #print(distance)
                    #print(f"Found black pixel at ({int(current_x)}, {int(current_y)}) after {distance} pixels.")
                    distance = 0
                    pyautogui.moveTo(start_x, start_y)
                    angle -= 0.5
                    direction_x = math.cos(math.radians(angle))
                    direction_y = math.sin(math.radians(angle))
                    current_x, current_y = start_x, start_y
                nbr_pixel = 1
                current_x += direction_x * nbr_pixel
                current_y += direction_y * nbr_pixel
                distance += nbr_pixel
                #print(str(distance))
                #print(str(angle))
           
            liste_angle.append(angle)
            if angle <= -7 :
                time.sleep(0.5)
                liste_defaut_x_angle.append(x_cursor_live)
                liste_defaut_y_angle.append(y_cursor_live)
            if pixel_noir_trouve == 0 :
                time.sleep(0.5)
                liste_defaut_x_distance.append(x_cursor_live)
                liste_defaut_y_distance.append(y_cursor_live)
            pyautogui.moveTo(location.left + location.width / 2, location.top + location.height / 2)
            time.sleep(0.5)
            liste_x.append(x_cursor_live)
            liste_y.append(y_cursor_live)

            #time.sleep(0.5)
        # Display an alert box

        #pyautogui.moveTo(start_x, start_y)
        # Scroll vers le haut (valeurs positives)
        #update x/y position

        derniere_valeur_obtenu_x = x_cursor_live
        derniere_valeur_obtenu_y = y_cursor_live

        pyautogui.scroll(-500)
        print(liste_angle)
        print(liste_distance)
        print("nombre trouvÃ© : " + str(nombre_case))
        #print("est passÃ©")
        #print(liste_angle)
        #time.sleep(1)
        time.sleep(1)
       
        locations = []
        try:
            locations_case_1 = list(pyautogui.locateAllOnScreen(image_path_1, confidence=0.8))
        except Exception:
            locations_case_1 = []
        try:
            locations_case_2 = list(pyautogui.locateAllOnScreen(image_path_2, confidence=0.8))
        except Exception:
            locations_case_2 = []
        try:
            locations_case_3 = list(pyautogui.locateAllOnScreen(image_path_3, confidence=0.8))
        except Exception:
            locations_case_3 = []
        try:
            locations_case_4 = list(pyautogui.locateAllOnScreen(image_path_4, confidence=0.8))
        except Exception:
            locations_case_4 = []

        locations = locations_case_1
        location_case_2_extrait = locations_case_2.copy()
        if locations != []:
            for k in locations_case_2:
                print(euclidean_distance(smallest_distance([k[0],k[1]],[sublist[0:2] for sublist in locations]),[k[0],k[1]]))
                if euclidean_distance(smallest_distance([k[0],k[1]],[sublist[0:2] for sublist in locations]),[k[0],k[1]]) < 10:
                    location_case_2_extrait.remove(k)
       
        locations = locations_case_1 + location_case_2_extrait

        location_case_3_extrait = locations_case_3.copy()

        if locations != []:
            for k in locations_case_3:
                print(euclidean_distance(smallest_distance([k[0],k[1]],[sublist[0:2] for sublist in locations]),[k[0],k[1]]))
                if euclidean_distance(smallest_distance([k[0],k[1]],[sublist[0:2] for sublist in locations]),[k[0],k[1]]) < 10:
                    location_case_3_extrait.remove(k)

        locations = locations + location_case_3_extrait

        location_case_4_extrait = locations_case_4.copy()

        if locations != []:
            for k in locations_case_4:
                print(euclidean_distance(smallest_distance([k[0],k[1]],[sublist[0:2] for sublist in locations]),[k[0],k[1]]))
                if euclidean_distance(smallest_distance([k[0],k[1]],[sublist[0:2] for sublist in locations]),[k[0],k[1]]) < 10:
                    location_case_4_extrait.remove(k)

        locations = locations + location_case_4_extrait

        trouve_en_plus = 0
        if locations:
            for location in locations:
                pyautogui.moveTo(location.left + location.width, location.top)
                #time.sleep(1)
                print(y_cursor_live)
                print(derniere_valeur_obtenu_y)
                if int(y_cursor_live) > int(derniere_valeur_obtenu_y):
                    print("----------------------")
                    print(y_cursor_live)
                    print(derniere_valeur_obtenu_y)
                    print("-----------------------")
                    #ok = input("c bon ?")
                    trouve_en_plus = trouve_en_plus + 1
                    #pyautogui.moveTo(location.left + location.width, location.top)
                    start_x = location.left + location.width - 2
                    start_y = location.top + 1
                    angle = 0
           
                    direction_x = math.cos(math.radians(angle))
                    direction_y = math.sin(math.radians(angle))
                    current_x, current_y = start_x, start_y
                    distance = 0
           
                    screenshot = pyautogui.screenshot()
                    pixel_noir_trouve = 0
                    while distance <= threshold_distance and angle > -10:
                        pixel_color = screenshot.getpixel((int(current_x), int(current_y)))
                        #print(pixel_color)
                        #pyautogui.moveTo((int(current_x), int(current_y)))
                        #time.sleep(0.1)
                        if pixel_color[0] < 185 and distance > 1 :
                            pixel_noir_trouve = 1
                            if angle == 0:
                                liste_distance.append(distance)
                                if distance < 9 or distance > 25:
                                    time.sleep(0.5)
                                    liste_defaut_x_distance.append(x_cursor_live)
                                    liste_defaut_y_distance.append(y_cursor_live)
                            #print(f"Found black pixel at ({int(current_x)}, {int(current_y)}) after {distance} pixels.")
                            distance = 0
                            pyautogui.moveTo(start_x, start_y)
                            angle -= 0.5
                            direction_x = math.cos(math.radians(angle))
                            direction_y = math.sin(math.radians(angle))
                            current_x, current_y = start_x, start_y
                        nbr_pixel = 3
                        current_x += direction_x * nbr_pixel
                        current_y += direction_y * nbr_pixel
                        distance += nbr_pixel
                        #print(str(angle))
                    liste_angle.append(angle)
                    if angle <= -7:
                        time.sleep(0.5)
                        liste_defaut_x_angle.append(x_cursor_live)
                        liste_defaut_y_angle.append(y_cursor_live)
                    if pixel_noir_trouve == 0 :
                        time.sleep(0.5)
                        liste_defaut_x_angle.append(x_cursor_live)
                        liste_defaut_y_angle.append(y_cursor_live)
                    print("------" + str(pixel_noir_trouve) + " ------")
                   
                    pyautogui.moveTo(location.left + location.width / 2, location.top + location.height / 2)
                    time.sleep(0.5)
                    liste_x.append(x_cursor_live)
                    liste_y.append(y_cursor_live)
        #print("trouvÃ© en plus : " + str(trouve_en_plus))
       
        print(liste_angle)
        #print(len(liste_angle))
        print(liste_distance)
       
        # Read the original HTML content once
        with open(html_body_path, 'r', encoding='utf-8') as file:
            content = file.read()
       
        liste_x = [str((int(x)-10)) for x in liste_x]
        liste_y = [str((int(y)-10)) for y in liste_y]
        liste_defaut_x_angle = [str((int(x)-13)) for x in liste_defaut_x_angle]
        liste_defaut_y_angle = [str((int(x)- 3)) for x in liste_defaut_y_angle]
        liste_defaut_x_distance = [str((int(x)-14)) for x in liste_defaut_x_distance]
        liste_defaut_y_distance = [str((int(x)- 2)) for x in liste_defaut_y_distance]

        coordinates_des_box = extract_tickbox_coordinates(content)
        coordinates_des_box = [(x + 10, y + 10) for x, y in coordinates_des_box]
        print("nombre de cases dÃ©tectÃ©es " + str(len(liste_x)))
        print("nombre de box totales : " + str(len(coordinates_des_box)))
        compteur_rep = 0
        test = 0
        for i in range(0, len(liste_x)):
            if not coordinates_des_box:
                print("Aucune box restante pour le point", i)
                continue
            point_a_remove = smallest_distance([liste_x[i], liste_y[i]], coordinates_des_box)
            if point_a_remove is None:
                print("Pas de box Ã  associer pour le point", i)
                continue
            test = 0
            if point_a_remove in coordinates_des_box:
                coordinates_des_box.remove(point_a_remove)
                compteur_rep += 1
                test = 1
            if test == 0:
                print("le point x = " + point_a_remove[0] + " et y = " + point_a_remove[1] + " n'a pas Ã©tÃ© retirÃ©")
        print("compteur a comptÃ© qu'on a enlevÃ© : " + str(compteur_rep) + " Ã©lements !")
       
        coordinates_des_box_str = [(str(row[0]), str(row[1])) for row in coordinates_des_box]
        coordonnee_test_x = []
        coordonnee_test_y = []
        for i in range(len(coordinates_des_box)):
            coordonnee_test_x.append(coordinates_des_box[i][0])
            coordonnee_test_y.append(coordinates_des_box[i][1])
        #print(coordonnee_test_x)
        #print(coordonnee_test_y)
        svg_block = '<svg width="100%" height="100%" style="position:absolute; top:0; left:0;">\n'
        # Create a copy of the original HTML file to modify
        output_file = html_body_path.replace('.html', '_modified.html')
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(content)
       
        with open(output_file, 'r', encoding='utf-8') as file:
            content = file.read()
       
        for i in range(len(liste_defaut_x_angle)):
            svg_block += f'<circle cx="{liste_defaut_x_angle[i]}" cy="{liste_defaut_y_angle[i]}" r="14" fill="none" stroke="black" stroke-width="3" />\n'
        for i in range(len(liste_defaut_x_distance)):
            svg_block += f'<circle cx="{liste_defaut_x_distance[i]}" cy="{liste_defaut_y_distance[i]}" r="11" fill="none" stroke="green" stroke-width="3" />\n'
        if len(coordinates_des_box ) > 0 :
            for i in range(len(coordinates_des_box)):
                x = int(coordinates_des_box[i][0])
                y = int(coordinates_des_box[i][1])
                svg_block += f'<circle cx="{x}" cy="{y}" r="16" fill="none" stroke="red" stroke-width="3" />\n'
            svg_block += '</svg>'


        # Calcul des nombres Ã  reporter
        nombre_cases_total = len(liste_x)
        nombre_mal_alignees = len(liste_defaut_x_angle)
        nombre_trop_distantes = len(liste_defaut_x_distance)
       
        if '</body>' in content:
            content = content.replace('</body>', svg_block + '\n</body>')
        else:
            content += svg_block

        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(content)
           
    return nombre_cases_total, nombre_mal_alignees, nombre_trop_distantes





''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''''''''''''''''''''''''BOUTONS'''''''''''''''''''''''''''''''''''''''''''''''''''




def remplissage_extract_html(output_folder, excel_app, spec_file_path, macro_workbook_name):

    compteur_barre_chargement = 0
   
    html_files = find_all_files_with_extension(output_folder, ('-body.html',))
    compteur_glob = 1
    for file_path in html_files:
        file_name = os.path.basename(file_path)
        extract_html_to_excel(file_path, compteur_glob, output_folder, file_name, excel_app, spec_file_path, macro_workbook_name)
        compteur_glob += 1

                   

def extract_html_to_excel(htmlpath, compteur_glob, output_folder, file_name, excel_app, spec_file_path, macro_workbook_name):
    colonne_1 = ""
    for i in range(len(file_name) - 1, -1, -1):
       if file_name[i].isdigit():
           if file_name[i - 1] == "_":
               start = max(0, i - 7)
               colonne_1 = file_name[start:i + 1]
               colonne_1 = colonne_1.replace("_","")
               break
           else:
               start = max(0, i - 3)
               colonne_1 = file_name[start:i + 3]
               break
    print(colonne_1)
    with open(htmlpath, 'r', encoding='utf-8') as file:
        html_content = file.read()
   
   
    td_html_bis = str(html_content).replace(chr(9), "")
    td_html_bis = td_html_bis.replace(chr(10)," ")
    # Parse the HTML content
    soup = BeautifulSoup(td_html_bis, 'html.parser')
   
    liste_entete = ["Button"]
    compteur = 1
   
    divs = soup.find_all('div', id=re.compile("Layer_LINKS"))
   
    colonne_c_valeur = ""
    display_redirection = ""
    # Extract and print the content of each matching div
    for div in divs:
        inner_div = div.find('div',attrs={'display-id' : True})
        if inner_div:
            display_redirection = display_redirection + inner_div['display-id'] + "\n"
        else:
            inner_div = div.find('div',attrs={'sheet-id' : True})
            if inner_div:
                display_redirection = display_redirection + inner_div['sheet-id'] + "\n"
            else:
                for attr_name, attr_value in inner_div.attrs.items():
                    if 'id' in attr_name.lower():
                        display_redirection = display_redirection + attr_value + "\n"
                        break  # Only take the first matching attribute
        colonne_c_valeur = colonne_c_valeur + div.get_text(strip=True) + "\n"
    if len(colonne_c_valeur) > 0:
        colonne_c_valeur = colonne_c_valeur[:-1]
    if len(display_redirection) > 0:
        display_redirection = display_redirection[:-1]
    print(display_redirection)
    print("&&&&&&&&&")
    print(colonne_c_valeur)
    print("***********")
    excel_app.Application.Run(f"{macro_workbook_name}!button_function", spec_file_path, colonne_1, colonne_c_valeur, compteur_glob, output_folder, display_redirection)




def batch_extract_html_to_excel(output_folder, macro_file_path, spec_file_path):
    macro_workbook_name = os.path.basename(macro_file_path)

    # Lancement Excel
    excel_app = win32com.client.Dispatch("Excel.Application")
    workbook = excel_app.Workbooks.Open(macro_file_path)

    # Appel de ta fonction de remplissage
    remplissage_extract_html(output_folder, excel_app, spec_file_path, macro_workbook_name)




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''''''''''''''''''''''''''''''''COMPARAISON HTML BODY - XML'''''''''''''''''''''''''''''''''''''''


def extract_text_file(text_file_path):
    with open(text_file_path, 'r', encoding='utf-8') as f:
        texte = f.read()
    extrait = texte.split("\n")
    if len(extrait)>0 :
        element_precedent = extrait[0]
    concatene = ""
    if extrait[0] != "\n" and extrait[0] != "END" and extrait[0] != "ENDEND" and extrait[0] != "START" and extrait[0] != "STARTSTART":
        concatene+=element_precedent
    for k in extrait:
        if k != element_precedent and k != "\n" and k!= "END" and k!="ENDEND" and k!="START" and k!="STARTSTART":
            concatene+=k+"\n"
            element_precedent = k
    concatene = concatene.replace("\n","").replace(" ","").replace(chr(12),"").lower()


    return concatene, text_file_path
   



def extract_xml_text(xml_path):
    import xml.etree.ElementTree as ET
    concatene = ""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    calques_list = root.findall('.//Calques')
    if not calques_list:
        print("Aucune balise <Calques> trouvÃ©e dans le XML.")
        return ""
    last_calques = calques_list[-1]

    # 1. Boucle sur <TexteSimple>
    for elem in last_calques.iter('TexteSimple'):
        # Cherche un enfant <Texte> position 0 ou 3
        texte_enfant = None
        for t in elem.findall('Texte'):
            if t.get('position') in ("0", "3"):
                texte_enfant = t
                break

        if texte_enfant is not None:
            valeur = texte_enfant.get('valeur')
            if valeur and len(valeur) > 1 and valeur.lower() not in ("start", "end"):
                concatene += valeur
        else:
            if elem.text and len(elem.text) > 1 and elem.text.lower() not in ("start", "end"):
                concatene += elem.text

    # 2. Collecte des <Texte> enfants de <TexteSimple>
    texte_enfants_de_textesimple = set()
    for elem in last_calques.iter('TexteSimple'):
        for t in elem.findall('Texte'):
            if t.get('position') in ("0", "3"):
                texte_enfants_de_textesimple.add(id(t))

    # 3. Boucle sur tous les <Texte> position 0 ou 3 qui NE sont PAS enfants de <TexteSimple>
    for elem in last_calques.iter('Texte'):
        if elem.get('position') in ("0", "3"):
            if id(elem) not in texte_enfants_de_textesimple:
                valeur = elem.get('valeur')
                if valeur and len(valeur) > 1 and valeur.lower() not in ("start", "end"):
                    concatene += valeur

    # 4. Boucle sur InstanceGabarit (inchangÃ©)
    for instance in last_calques.iter('InstanceGabarit'):
        if instance.get('gabarit') == "217":
            champs = instance.find('Champs')
            if champs is not None:
                for champ in champs.findall('Champ'):
                    value = champ.get('value')
                    if value and len(value) > 1 and value.lower() not in ("start", "end"):
                        concatene += value

    concatene = concatene.lower().replace("\n", "").replace(" ", "").replace("Â ", "")
    return concatene




def comparer_frequences(texte1, texte2, liste_probleme_html=None, liste_probleme_xml=None):
    freq1 = Counter(texte1)
    freq2 = Counter(texte2)
    messages = []

    if freq1 == freq2:
        print("\nLes deux textes contiennent exactement les mÃªmes caractÃ¨res avec les mÃªmes frÃ©quences.")
        messages.append("IDENTICAL")
        return "\n".join(messages)
    else:
        print("\nDiffÃ©rences trouvÃƒÂ©es dans les frÃ©quences de caractÃ¨res :")
        messages.append("DIFFERENT")

        # CaractÃ¨res en plus dans texte1 (et donc en moins dans texte2)
        diff1 = freq1 - freq2
        if diff1:
            print("\nCaractÃ¨res en plus dans le texte 1 (et donc en moins dans le texte 2) :")
            for char, count in diff1.items():
                print(f"  '{char}' : {count} times")

        # CaractÃ¨res en plus dans texte2 (et donc en moins dans texte1)
        diff2 = freq2 - freq1
        if diff2:
            print("\nCaractÃ¨res en plus dans le texte 2 (et donc en moins dans le texte 1) :")
            for char, count in diff2.items():
                print(f"  '{char}' : {count} times")


        # Ajout des phrases problÃ©matiques
        if liste_probleme_html is not None and liste_probleme_xml is not None:
            messages.append("\nProblem located in the HTML Body in the following sentences:")
            for phrase in liste_probleme_html:
                messages.append(f"  - {phrase}")
            messages.append("\nProblem located in the SPEC in the following sentences:")
            for phrase in liste_probleme_xml:
                messages.append(f"  - {phrase}")
            messages.append(f"\n______________________________\n")

        return "\n\n".join(messages)
       

def find_files_with_substring(directory, substring, extensions):
    matching_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            #print(file)
            if substring in file and file.lower().endswith(extensions):
                matching_files.append(os.path.join(root, file))
    return matching_files


def comparaison(text_file_path, xml_path, concatene_html, concatene_xml):
    import xml.etree.ElementTree as ET

    with open(text_file_path, 'r', encoding='utf-8') as f:
        texte = f.read()
    last_start_pos = texte.rfind("START")
    if last_start_pos == -1:
        extrait = texte
    else:
        extrait = texte[last_start_pos + len("START"):]
    extrait = extrait.split("\n")
    if len(extrait) > 0:
        element_precedent = extrait[0]
    phrase_html = []
    phrase_html_propre = []
    phrase_html.append(element_precedent.lower().replace(" ", ""))
    phrase_html_propre.append(element_precedent)

    for k in extrait:
        if k != element_precedent and k.strip() != "" and k != "\n" and k != "END" and k != "ENDEND" and k != "START" and k != "STARTSTART":
            phrase_html_propre.append(k)
            phrase_html.append(k.lower().replace(" ", "").replace(chr(12), "").replace(chr(10), ""))
            element_precedent = k

    # VÃ©rification extraction TXT
    if not phrase_html_propre or all(s.strip() == "" for s in phrase_html_propre):
        print("Aucun texte extrait du fichier TXT !")
    else:
        print(f"{len(phrase_html_propre)} Ã©lÃ©ments extraits du fichier TXT.")

    # RÃ©cupÃ©ration phrase XML
    phrase_xml = []
    phrase_xml_propre = []
   
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Erreur lors de la lecture du XML : {e}")
        return [], []

    calques_list = root.findall('.//Calques')
    if not calques_list:
        print("Aucune balise <Calques> trouvÃ©e dans le XML.")
        return [], []
    last_calques = calques_list[-1]



    for elem in last_calques.iter('TexteSimple'):
        # Cherche un enfant <Texte> position 0 ou 3
        texte_enfant = None
        for t in elem.findall('Texte'):
            if t.get('position') in ("0", "3"):
                texte_enfant = t
                break

        # Si <Texte> enfant trouvÃ©, on ne garde que sa valeur
        if texte_enfant is not None:
            valeur = texte_enfant.get('valeur')
            if valeur and len(valeur) > 1 and valeur.lower() not in ("start", "end"):
                phrase_xml.append(valeur.lower().replace(" ", "").replace(chr(12), "").replace(chr(10), "").replace("\xa0", "").replace("\x0c", ""))
                phrase_xml_propre.append(valeur)
        else:
            # Sinon, on garde le texte de <TexteSimple>
            if elem.text and len(elem.text) > 1 and elem.text.lower() not in ("start", "end"):
                phrase_xml.append(elem.text.lower().replace(" ", "").replace(chr(12), "").replace(chr(10), "").replace("\xa0", "").replace("\x0c", ""))
                phrase_xml_propre.append(elem.text)


    # Collecte les <Texte> enfants de <TexteSimple> (position 0 ou 3)
    texte_enfants_de_textesimple = set()
    for elem in last_calques.iter('TexteSimple'):
        for t in elem.findall('Texte'):
            if t.get('position') in ("0", "3"):
                texte_enfants_de_textesimple.add(id(t))


    for elem in last_calques.iter('Texte'):
        if elem.get('position') in ("0", "3"):
            # On ne prend que ceux qui NE sont PAS enfants de <TexteSimple>
            if id(elem) not in texte_enfants_de_textesimple:
                valeur = elem.get('valeur')
                if valeur and len(valeur) > 1 and valeur.lower() not in ("start", "end"):
                    phrase_xml.append(valeur.lower().replace(" ", "").replace(chr(12), "").replace(chr(10), "").replace("\xa0", "").replace("\x0c", ""))
                    phrase_xml_propre.append(valeur)



    for instance in last_calques.iter('InstanceGabarit'):
        if instance.get('gabarit') == "217":
            champs = instance.find('Champs')
            if champs is not None:
                for champ in champs.findall('Champ'):
                    value = champ.get('value')
                    if value and len(value) > 1 and value.lower() not in ("start", "end"):
                        phrase_xml.append(value.lower().replace(" ", "").replace(chr(12), "").replace(chr(10), "").replace("\xa0", "").replace("\x0c", ""))
                        phrase_xml_propre.append(value)

    # VÃ©rification extraction XML
    if not phrase_xml_propre or all(s.strip() == "" for s in phrase_xml_propre):
        print("Aucun texte extrait du XML !")
    else:
        print(f"{len(phrase_xml_propre)} Ã©lÃ©ments extraits du XML.")

    # Comparaison
    liste_probleme_html = []
    liste_probleme_xml = []
    for k in range(len(phrase_html)):
        if not (phrase_html[k] in concatene_xml):
            liste_probleme_html.append(phrase_html_propre[k])
    print("\n\n ------------------- \n\n")
    for k in range(len(phrase_xml)):
        if not (phrase_xml[k] in concatene_html):
            liste_probleme_xml.append(phrase_xml_propre[k])

    # Comparaison sur la version nettoyÃ©e (concatÃ©nÃ©e)
    liste_probleme_html = []
    for ph in phrase_html_propre:
        ph_nettoye = ph.lower().replace(" ", "").replace("\n", "").replace("\xa0", "").replace("\x0c", "")
        if ph_nettoye and ph_nettoye not in concatene_xml:
            liste_probleme_html.append(ph)

    liste_probleme_xml = []
    for ph in phrase_xml_propre:
        ph_nettoye = ph.lower().replace(" ", "").replace("\n", "").replace("\xa0", "").replace("\x0c", "")
        if ph_nettoye and ph_nettoye not in concatene_html:
            liste_probleme_xml.append(ph)

    print("\n==== PHRASES TXT ORIGINALES ====")
    for ph in phrase_html_propre:
        print(f"- {ph}")
    print("\n==== PHRASES XML ORIGINALES ====")
    for ph in phrase_xml_propre:
        print(f"- {ph}")

    print("\n==== CONCATENE_HTML (TXT nettoyÃ©) ====")
    print(concatene_html)
    print("\n==== CONCATENE_XML (XML nettoyÃ©) ====")
    print(concatene_xml)



    print("problÃ¨me situÃ© dans le html aux phrases suivantes : ")
    print(liste_probleme_html)
    print("problÃ¨me situÃ© aux phrases xml suivantes : ")
    print(liste_probleme_xml)
    return liste_probleme_html, liste_probleme_xml




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''''''''''''''''''''SUPERPOSITION'''''''''''''''''''''''''''''''''''''''''''''''

def extract_letter_characteristics(pdf_path):
    import fitz
    letter_characteristics = []
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        raw_dict = page.get_text("dict")
        for block in raw_dict["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    bbox = span["bbox"]
                    for char in span["text"]:
                        letter_characteristics.append({
                            "letter": char,
                            "bbox": bbox,
                        })
    return letter_characteristics


def unique_preserve_order(seq):
    seen = set()
    result = []
    for item in seq:
        if item not in seen and item.strip() != "":
            seen.add(item)
            result.append(item)
    return result


def analyse_pdf_letter_overlap(pdf_path):
    text_attributes = extract_letter_characteristics(pdf_path)
    print(f"DEBUG extract_letter_characteristics pour {pdf_path} : {len(text_attributes)} lettres trouvÃ©es")
    if not text_attributes:
        print(f"Aucune lettre trouvÃ©e dans {pdf_path}")
        return []

    ancien_rect_comp = text_attributes[0]["bbox"]
    k = 0
    rectangle_pas_bon = []
    mots_superposes = []  # <-- Liste des mots/lettres superposÃ©s

    for attr in text_attributes:
        rectanglex1, rectangley1, rectanglex2, rectangley2 = attr["bbox"]
        rectangle = [rectanglex1, rectangley1, rectanglex2, rectangley2]
        l = -1
        for attr_compr in text_attributes:
            l += 1
            rectanglecompx1, rectanglecompy1, rectanglecompx2, rectanglecompy2 = attr_compr["bbox"]
            rectangle_comp = [rectanglecompx1, rectanglecompy1, rectanglecompx2, rectanglecompy2]
            if rectangle_comp == ancien_rect_comp:
                continue
            if rectanglex2 < rectanglecompx1 or rectanglecompx2 < rectanglex1:
                continue
            if (rectanglex2 > rectanglecompx1 and abs(rectangle[3] - rectangle_comp[1]) < 10) or (rectanglecompx2 > rectanglex1 and abs(rectangle[1] - rectangle_comp[3]) < 10):
                continue
            if rectangley2 < rectanglecompy1 or rectanglecompy2 < rectangley1:
                continue
            if (rectangley2 > rectanglecompy1 and abs(rectangle[2] - rectangle_comp[0]) < 10) or (rectanglecompy2 > rectangley1 and abs(rectangle[0] - rectangle_comp[2]) < 10):
                continue
            if rectangle == rectangle_comp:
                continue
            if k > 5 and l > 5 and (not(rectangle in rectangle_pas_bon) or not(rectangle_comp in rectangle_pas_bon)):
                # RÃ©cupÃ¨re les lettres superposÃ©es dans les deux contextes
                lettres1 = [text_attributes[k+i]["letter"] for i in range(-5, 6) if 0 <= k+i < len(text_attributes)]
                lettres2 = [text_attributes[l+i]["letter"] for i in range(-5, 6) if 0 <= l+i < len(text_attributes)]
                mot1 = "".join(lettres1).replace('\n', '').strip()
                mot2 = "".join(lettres2).replace('\n', '').strip()
                # Ajoute les deux mots/lettres superposÃ©s Ã  la liste
                mots_superposes.append(mot1)
                mots_superposes.append(mot2)
                # Affichage console (inchangÃ©)
                print("&&&&&&&&&&&&&&&&&&&&")
                for i in range(-5, 6):
                    if 0 <= k+i < len(text_attributes):
                        print(text_attributes[k+i])
                print("--------------------------")
                for i in range(-5, 6):
                    if 0 <= l+i < len(text_attributes):
                        print(text_attributes[l+i])
                print("&&&&&&&&&&&&&&&&&&&&&")
                ancien_rect_comp = rectangle_comp
                rectangle_pas_bon.append(rectangle)
                rectangle_pas_bon.append(rectangle_comp)
        k += 1
    print("Page faite : " + os.path.basename(pdf_path))
    return mots_superposes





















def batch_compare_text_xml_pdf(output_folder):
    text_files = find_files_with_substring(output_folder, 'YP', ('.txt'))
    xml_files = find_files_with_substring(output_folder, 'YP', ('.xml'))
    pairs = []

    print(f"{len(text_files)} fichiers texte trouvÃ©s.")
    for text_path in text_files:
        matched = False
        if text_path[-5] == "P":
            mot = text_path[-10:-4] + "-"
            print(mot + "mot1-------------------------------")
            for path_xml in xml_files:
                if mot in path_xml:
                    pairs.append((text_path, path_xml))
                    matched = True
                    break
            if not matched:
                mot = text_path[-10:-4] + "1"
                print(mot + "mot2-------------------------------")
                for path_xml in xml_files:
                    if mot in path_xml:
                        pairs.append((text_path, path_xml))
                        break
        else:
            mot = text_path[-12:-4].replace("_", "")
            print(mot + "mot3-------------------------------")
            for path_xml in xml_files:
                if mot in path_xml:
                    pairs.append((text_path, path_xml))
                    break

        print("\n\n------------------------- IMAGE FAITE : " + os.path.basename(text_path) + " ----------------------------\n")

    print("fini")
    return pairs







def clean_string_for_match(s: str) -> str:
    if s is None:
        return ''
    # Mettre en minuscules
    s_clean = s.lower()
    # Retirer espaces, underscores, tirets
    for ch in [' ', '_', '-']:
        s_clean = s_clean.replace(ch, '')
    return s_clean

def extract_group_and_suffix(xml_filename):
    m = re.search(r'([A-Za-z0-9]+YP)(\d?)_', xml_filename)
    if m:
        group = m.group(1)
        suffix = m.group(2)
        return group, suffix
    parts = xml_filename.split("_")
    if len(parts) > 0:
        base = parts[0].replace("-", "")
        if "YP" in base:
            idx = base.index("YP")
            group = base[:idx+2]
            suffix = base[idx+2:]
            return group, suffix
    return None, None

def detect_html_paths_for_xml(folder, xml_filename):
    html_top_path = None
    html_body_path = None

    group, suffix = extract_group_and_suffix(os.path.basename(xml_filename))
    if not group:
        print(f"Impossible d'extraire le groupe pour {xml_filename}")
        return None, None

    group_clean = clean_string_for_match(group)
    suffix_clean = clean_string_for_match(suffix)
    html_variants = [clean_string_for_match(v) for v in generate_html_variants(group, suffix)]

    # Pour le top : seulement la variante sans suffixe
    top_variant = clean_string_for_match(group)

    # Recherche du HTML TOP (toujours nettoyÃ©, sans suffixe)
    for full_path in find_all_files_with_extension(folder, ('.html', '.htm')):
        fname = os.path.basename(full_path)
        name_no_ext = os.path.splitext(fname)[0]
        name_clean = clean_string_for_match(name_no_ext)
        if top_variant in name_clean and "top" in name_clean:
            html_top_path = full_path
            break

    # Recherche du HTML BODY (toutes variantes, avec suffixe)
    for full_path in find_all_files_with_extension(folder, ('.html', '.htm')):
        fname = os.path.basename(full_path)
        name_no_ext = os.path.splitext(fname)[0]
        name_clean = clean_string_for_match(name_no_ext)
        if "body" in name_clean:
            # Cas du body "par dÃ©faut" (pas de suffixe ou suffixe "1")
            if suffix_clean in ["", "1"]:
                # Cherche un fichier qui contient juste le group (sans chiffre) et "body"
                if group_clean in name_clean and not re.search(rf"{group_clean}\d+body", name_clean):
                    html_body_path = full_path
                    break
            # Cas du body avec suffixe explicite
            else:
                if any(variant in name_clean for variant in html_variants):
                    html_body_path = full_path
                    break

    return html_top_path, html_body_path






'''def find_all_files_with_extension(root_folder, extensions):
    matches = []
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(extensions):
                matches.append(os.path.join(dirpath, filename))
    return matches
'''
def find_all_files_with_extension(root_folder, extensions):
    matched_files = []
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(extensions):
                matched_files.append(os.path.join(dirpath, filename))
    return matched_files



def get_page_name_from_html(html_path):

    try:
        filename = os.path.splitext(os.path.basename(html_path))[0]  # nom sans extension
        if '-body' in filename:
            page_name = filename.split('-body')[0]
        else:
            page_name = filename  # fallback si pas de '-body'
        return page_name
    except Exception as e:
        print(f"Erreur extraction nom page : {e}")
        return os.path.splitext(os.path.basename(html_path))[0]



def write_report_for_page(html_path, output_folder, nombre_cases_total, nombre_mal_alignees, nombre_trop_distantes, mots_superposes_texte, diff_html_top_xml=None, diff_html_body_xml=None):
    rapport_path = os.path.join(output_folder, "Report_A3C.txt")
    page_name = get_page_name_from_html(html_path)
    print("ENTREEEEEEEEEEEEEEEEEEEEEEEEEE")
    with open(rapport_path, 'a', encoding='utf-8') as f:
        f.write(f"View: {page_name}\n\n______________________________\n")
        f.write(f"\nBoxes analysis:\n\n")
        f.write(f"Total number of boxes detected: {nombre_cases_total}\n")
        f.write(f"Number of misaligned boxes: {nombre_mal_alignees}\n")
        f.write(f"Number of boxes too far apart: {nombre_trop_distantes}\n______________________________\n")
        f.write(f"\nOverlapping analysis:\n")
        if mots_superposes_texte:
            f.write(f"\nWords overlapping: {mots_superposes_texte}\n______________________________\n")
        else:
            f.write("\n" + "No overlapping words\n______________________________\n")
        if diff_html_top_xml:
            f.write(f"\nText differences analysis (TOP):\n")
            f.write(diff_html_top_xml + "\n\n")
        if diff_html_body_xml:
            f.write(f"Text differences analysis (BODY):\n")
            f.write(diff_html_body_xml + "\n")
        f.write("\n\n******************************\n\n")
        f.write("******************************\n\n\n")








def generate_html_variants(group, suffix):
    variants = []
    group = group.strip()
    suffix = suffix.strip()
    if not suffix:
        variants.append(group)
    else:
        variants.append(f"{group}{suffix}")
        variants.append(f"{group}_{suffix}")
        variants.append(f"{group}-{suffix}")
    return variants


def diff_strict(a: str, b: str, label: str, orig_a: str = None, orig_b: str = None) -> str:
    def get_word_containing_index(text: str, index: int) -> tuple:
        """
        Retourne le mot contenant l'index donnÃ© et l'indice du mot dans la liste.
        """
        words = text.split()
        current_pos = 0
        for idx, word in enumerate(words):
            start = current_pos
            end = current_pos + len(word)
            if start <= index < end:
                return word, idx
            current_pos = end + 1  # +1 pour l'espace
        return "", -1

    if a == b:
        return f"IDENTICAL"
    min_len = min(len(a), len(b))
    for i in range(min_len):
        if a[i] != b[i]:
            # Si on a les textes originaux, on retrouve le mot d'origine
            if orig_a and orig_b:
                orig_i_a = map_index_to_original(a, orig_a, i)
                orig_i_b = map_index_to_original(b, orig_b, i)
                word_a, idx_a = get_word_containing_index(orig_a, orig_i_a)
                word_b, idx_b = get_word_containing_index(orig_b, orig_i_b)
            else:
                word_a, idx_a = "", -1
                word_b, idx_b = "", -1
            return (f"Differences{label}:\n"
                    f"First different character:\n"
                    f"  XML = '{b[i]}' (word : '{word_b}')\n"
                    f"  HTML = '{a[i]}' (word : '{word_a}')\n______________________________")
    # Si tout est identique jusqu'au plus court, mais longueurs diffÃ©rentes
    extra = a[min_len:] if len(a) > len(b) else b[min_len:]
    longer = "a" if len(a) > len(b) else "b"
    return (f"{label} : Both texts are identical up to position {min_len}, "
            f"but the text '{longer}' is longer (lenghts : a={len(a)}, b={len(b)}).\n"
            f"Additional text in '{longer}' : '{extra}'")

def map_index_to_original(norm_text, orig_text, diff_index):
    """
    Trouve la position dans le texte original correspondant Ã  l'index diff_index
    dans le texte normalisÃ© (espaces supprimÃ©s).
    """
    count = 0
    for orig_idx, char in enumerate(orig_text):
        if char != " ":
            if count == diff_index:
                return orig_idx
            count += 1
    return -1  # Pas trouvÃ© (ne devrait pas arriver)



def find_file_by_extension(folder, extension):
    # Cherche dans le dossier racine uniquement
    files = glob.glob(os.path.join(folder, f"*{extension}"))
    return files[0] if files else None

def find_matching_pdf_for_html(html_body_path, root_folder):
    html_name = Path(html_body_path).name
    pdf_name = html_name.replace('-body.html', '.pdf')
    all_pdfs = find_all_files_with_extension(root_folder, ('.pdf',))
    for pdf_path in all_pdfs:
        if Path(pdf_path).name == pdf_name:
            return pdf_path
    return None




def main():
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
        import traceback

        print("Select the folder containing the XML, HTML, TXT, PDF files:")
        root = tk.Tk()
        root.withdraw()
        output_folder = filedialog.askdirectory(title="Select the folder containing the files")
        if not output_folder:
            print("No folder selected. Script terminated.")
            return

        dossier_nom = os.path.basename(output_folder.rstrip('/\\'))

        print("Please select the macro file (.xlsm):")
        macro_file_path = filedialog.askopenfilename(
            title="Select the macro file (.xlsm)",
            filetypes=[("Excel Macro File", "*.xlsm")],
            initialdir=output_folder
        )
        if not macro_file_path:
            print("No macro file selected. Script terminated.")
            return

        print("Please select the SPEC file (.xlsx):")
        spec_file_path = filedialog.askopenfilename(
            title="Select the SPEC file (.xlsx)",
            filetypes=[("SPEC Excel File", "*.xlsx")],
            initialdir=output_folder
        )
        if not spec_file_path:
            print("No SPEC file selected. Script terminated.")
            return

        carre_images = [
            str(p) for p in Path(output_folder).rglob("*.png")
            if "image_carre" in p.name
        ]
        if len(carre_images) != 4:
            print(f"Error: {len(carre_images)} 'image_carre*.png' found. Expected exactly 4.")
            return
        image_path_1, image_path_2, image_path_3, image_path_4 = carre_images

        rapport_path = os.path.join(output_folder, "Report_A3C.txt")
        with open(rapport_path, 'w', encoding='utf-8') as f:
            f.write(f"REPORT: {dossier_nom}

")
            f.write("- - - - - - -

")

        os.chdir(output_folder)

        pairs = batch_compare_text_xml_pdf(output_folder)

        xml_files = find_all_files_with_extension(output_folder, ('.xml',))
        if not xml_files:
            print("No XML files found. Terminating.")
            return

        for text_path, xml_path in pairs:
            try:
                print(f"Processing TXT: {os.path.basename(text_path)} and XML: {os.path.basename(xml_path)}")

                xml_processed, xml_repere_clean, xml_concat_brut = extract_xml_fields(xml_path)
                if xml_processed is None or not xml_repere_clean:
                    print(f"Skipping {xml_path} due to extraction failure.")
                    continue

                html_top_path, html_body_path = detect_html_paths_for_xml(output_folder, os.path.basename(xml_path))

                diff_html_top_xml = None
                if html_top_path:
                    result = extract_html_fields(html_top_path, xml_repere_clean)
                    if result:
                        concat, td1_text, td2_text, td10_text, td11_text = result
                        html_processed_original = "".join([td2_text, td1_text, td10_text, td11_text])
                        html_processed = html_processed_original

                        if xml_repere_clean and xml_repere_clean[-1].isdigit():
                            td1_mod = td1_text
                            if not td1_mod.lower().replace(" ", "").endswith(xml_repere_clean[-1]):
                                td1_mod += xml_repere_clean[-1]
                            html_processed = "".join([td2_text, td1_mod, td10_text, td11_text])

                        norm_html_top = html_processed.lower().replace(" ", "")
                        norm_xml = xml_processed.lower().replace(" ", "")
                        diff_html_top_xml = diff_strict(norm_html_top, norm_xml, "", html_processed_original, xml_concat_brut)

                if html_body_path:
                    insert_script_in_html(html_body_path)
                    server_thread = threading.Thread(target=demarrage_serveur)
                    server_thread.daemon = True
                    server_thread.start()
                    time.sleep(5)

                    relative_path = os.path.relpath(html_body_path, output_folder).replace("\", "/").replace(" ", "%20")
                    render_html_to_pdf(f"http://localhost:8000/{relative_path}")

                    nombre_cases_total, nombre_mal_alignees, nombre_trop_distantes = find_and_move_to_all_images(
                        image_path_1, image_path_2, image_path_3, image_path_4, 30, html_body_path, output_folder
                    )

                    pdf_path = find_matching_pdf_for_html(html_body_path, output_folder)
                    mots_superposes_texte = ""
                    if pdf_path and os.path.exists(pdf_path):
                        mots_superposes = analyse_pdf_letter_overlap(pdf_path)
                        mots_superposes_uniques = unique_preserve_order(mots_superposes)
                        mots_superposes_texte = ", ".join(mots_superposes_uniques)

                    condense_HTML_body = extract_text_file(text_path)[0]
                    condense_SPEC = extract_xml_text(xml_path)
                    liste_probleme_html, liste_probleme_xml = comparaison(text_path, xml_path, condense_HTML_body, condense_SPEC)
                    diff_html_body_xml = comparer_frequences(condense_HTML_body, condense_SPEC, liste_probleme_html, liste_probleme_xml)

                    write_report_for_page(
                        html_body_path,
                        output_folder,
                        nombre_cases_total,
                        nombre_mal_alignees,
                        nombre_trop_distantes,
                        mots_superposes_texte,
                        diff_html_top_xml=diff_html_top_xml,
                        diff_html_body_xml=diff_html_body_xml
                    )
            except Exception as inner_e:
                with open("error_log.txt", "a", encoding="utf-8") as log:
                    log.write(traceback.format_exc())
                print(f"Error while processing {xml_path}: {inner_e}")

        try:
            batch_extract_html_to_excel(output_folder, macro_file_path, spec_file_path)
        except Exception as e:
            print("Excel automation failed. Possibly Excel is not installed.")
            with open("error_log.txt", "a", encoding="utf-8") as log:
                log.write(traceback.format_exc())

        print("All processing completed.")
        messagebox.showinfo("Done", "Generation completed successfully!")

    except Exception as e:
        with open("error_log.txt", "a", encoding="utf-8") as log:
            import traceback
            log.write(traceback.format_exc())
        print("A fatal error occurred. Check error_log.txt for details.")


if __name__ == "__main__":
    main()