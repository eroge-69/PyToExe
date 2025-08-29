# -*- coding: utf-8 -*-
"""
Created on Wed Jul  2 07:25:01 2025

@author: #genxcode - SolveReport GUI
"""
# Imports
import socket
import ssl
import http
import urllib
import _socket
import select
import errno

# Webview
from webview.dom import DOMEventHandler
import webview.menu as wm
import webview

# Streamlit
import streamlit as st
import streamlit
import streamlit_option_menu

#request
import requests

# Thread
import threading

# Subprocess URL
import subprocess

# Alternative à Subprocess
import streamlit.web.cli as stcli

# Convertor
import base64

# Time
import time

# OS
import os

# SYS
import sys

# Path / Copy&Paste Files
import shutil

# License
from license.license_manager import initialize_license_system, get_license_manager

# Atexit
import atexit


# Lang dictionnary
dict_lang={
    "Create" : "Créer",
    "Languages" : "Langues",
    "French" : "Français",
    "English" : "Anglais",
    "Return" : "Retour",
    "Select a language" : "Sélectionnez une langue",
    "Cleart data" : "Nettoyer les données",
    "Success" : "Succès",
    }


# Path Assets
path_screen = 'en'
base_path = os.path.dirname(path_screen)

# Transform Picture to inject in HTML
def get_base64_image(path):
    with open(path, "rb") as img_file:
        b64_data = base64.b64encode(img_file.read()).decode('utf-8')
    return f"data:image/png;base64,{b64_data}"

# ScreenShots
normsch_path = os.path.join(base_path, 'screen', 'norm_scsh.png')
normsch_img = get_base64_image(normsch_path)

avsch_path = os.path.join(base_path, 'screen', 'av_scsh.png')
avsch_image = get_base64_image(avsch_path)

apsch_path = os.path.join(base_path, 'screen', 'ap_scsh.png')
apsch_image = get_base64_image(apsch_path)

# App Icone
ico_path = os.path.join(base_path, 'assets', 'Icons', 'sr.png')

class API:
    
    def __init__(self):
        
        self.website = "en.py" #en.py
        self.word = list(dict_lang.keys())
        self.streamlit_menu = None
      
    
    def get_html_template(self):

        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>SolveReport</title>
            <style>
                
                /* Styles pour le contenu principal */
                .main-content {{
                    display: none;
                }}
        
                .main-content.loaded {{
                    display: block;
                    animation: fadeIn 0.5s ease-in-out;
                }}
        
                @keyframes fadeIn {{
                    from {{ opacity: 0; }}
                    to {{ opacity: 1; }}
                }}
                
                @-webkit-keyframes tracking-in-expand-fwd {{
                  0% {{
                    letter-spacing: -0.5em;
                    -webkit-transform: translateZ(-700px);
                    transform: translateZ(-700px);
                    opacity: 0;
                  }}
                  40% {{
                    opacity: 0.6;
                  }}
                  100% {{
                    -webkit-transform: translateZ(0);
                    transform: translateZ(0);
                    opacity: 1;
                  }}
                }}
                
                @keyframes tracking-in-expand-fwd {{
                  0% {{
                    letter-spacing: -0.5em;
                    -webkit-transform: translateZ(-700px);
                    transform: translateZ(-700px);
                    opacity: 0;
                  }}
                  40% {{
                    opacity: 0.6;
                  }}
                  100% {{
                    -webkit-transform: translateZ(0);
                    transform: translateZ(0);
                    opacity: 1;
                  }}
                }}
                
                body {{
                    background: linear-gradient(45deg, #0f0c29 30%, #302b63 45%, #24243e 55%, #302b63 90%);
                    animation: my_animation 20s ease infinite;
                    background-size: 200% 200%;
                    background-attachment: fixed;
                    font-family: Helvetica, sans-serif;
                    text-align: center;
                    background-color: #202124;
                    margin-top : 10;
                    padding: 0;
                    overflow-x: hidden; /* Empêche le scroll horizontal */
                }}
                                                
                @keyframes my_animation {{
                    0% {{
                        background-position: 0% 50% !important;
                    }}
                    50% {{
                        background-position: 100% 50% !important;
                    }}
                    100% {{
                        background-position: 0% 50% !important;
                    }}
                }}
               
        
                #title {{
                    color: #000000;
                    font-size: 90px;
                    font-weight: bold;
                    font-style: italic;
                    margin-top: 30px;
                    opacity: 0;
                    transform: translateZ(-700px);
                    
                }}
        
                #title.animate {{
                
                    -webkit-animation: tracking-in-expand-fwd 0.7s cubic-bezier(0.215, 0.610, 0.355, 1.000) both;
                    animation: tracking-in-expand-fwd 0.7s cubic-bezier(0.215, 0.610, 0.355, 1.000) both;
                }}
        
                #greeting {{
                
                    color: #000000;
                    font-weight: bold;
                    font-family: 'Comic Sans MS', cursive;
                    font-size: 20pt;
                    margin-top: 30px;
                }}
        
                button {{
                    
                    margin: 80px auto;
                    padding: 24px 32px;
                    border: 0;
                    text-decoration: none;
                    border-radius: 15px;
                    background-color: rgba(0, 0, 0, 0.1);
                    border: 1px solid rgba(255,255,255,0.1);
                    backdrop-filter: blur(30px);
                    color: rgba(255,255,255,0.8);
                    letter-spacing: 2px;
                    display: block;
                    min-width: 350px;
                    min-height: 100px;
                    max-width: 500px;
                    max-height: 200px;
                    font-size: 40px;
                    cursor: pointer;
                    text-transform: uppercase;
                    -webkit-transition-duration: 0.8s;
                    transition-duration: 0.8s;
                }}
                
                button:hover {{
                  box-shadow: 0 12px 16px 0 rgba(0,0,0,0.34),0 17px 50px 0 rgba(0,0,0,0.19);
                  background-color: rgba(255,2,255,0.2);
                  color: #000000
                }}
                
                .cards-wrapper {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 10px auto;
                    max-width: 1200px;
                    width: 100%;
                }}
                
                .card-stack {{
                    position: relative;
                    width: 250px;
                    height: 350px;
                    perspective: 1000px;
                }}
                
                .card {{
                    position: absolute;
                    top: 70px;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    border-radius: 20px;
                    background-size: cover;
                    background-position: center;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
                    transform-style: preserve-3d;
                    opacity: 0;
                    transition: transform 2s ease, opacity 1s ease;
                }}
                
                /* Effet éventail gauche */
                .left-stack .card.open:nth-child(1) {{
                    transform: rotateY(0deg) translateX(0px) translateZ(-10px);
                    opacity: 1;
                }}
                .left-stack .card.open:nth-child(2) {{
                    transform: rotateY(-10deg) translateX(-40px) translateZ(0px);
                    opacity: 1;
                }}
                .left-stack .card.open:nth-child(3) {{
                    transform: rotateY(-20deg) translateX(-80px) translateZ(10px);
                    opacity: 1;
                }}
                
                /* Effet éventail droite (symétrique) */
                .right-stack .card.open:nth-child(1) {{
                    transform: rotateY(0deg) translateX(0px) translateZ(-10px);
                    opacity: 1;
                }}
                .right-stack .card.open:nth-child(2) {{
                    transform: rotateY(10deg) translateX(40px) translateZ(0px);
                    opacity: 1;
                }}
                .right-stack .card.open:nth-child(3) {{
                    transform: rotateY(20deg) translateX(80px) translateZ(10px);
                    opacity: 1;
                }}

        
                /* Styles pour le skeleton loader */
                .skeleton-container {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    overflow-x: hidden;
                }}
        
                .skeleton-container.hidden {{
                    display: none;
                    overflow-x: hidden;
                }}
        
                .skeleton {{
                    background: linear-gradient(90deg, #333 25%, #444 50%, #333 75%);
                    background-size: 200% 100%;
                    animation: loading 1.5s infinite;
                    border-radius: 8px;
                    overflow-x: hidden;
                }}
        
                @keyframes loading {{
                    0% {{ background-position: 200% 0; }}
                    100% {{ background-position: -200% 0; }}
                }}
        
                .skeleton-title {{
                    width: 400px;
                    height: 90px;
                    margin-top: 30px;
                    margin-bottom: 40px;
                    border-radius: 12px;
                }}
        
                .skeleton-greeting {{
                    width: 200px;
                    height: 30px;
                    margin-top: 30px;
                    margin-bottom: 40px;
                    border-radius: 6px;
                }}
        
                .skeleton-button {{
                    width: 350px;
                    height: 100px;
                    margin-top: 50px ;
                    margin-bottom : 40px;
                    border-radius: 15px;
                }}
                
                /* Container principal pour le skeleton (comme cards-wrapper) */
                .skeleton-cards-wrapper {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 10px auto;
                    max-width: 1200px;
                    width: 100%;
                }}
                
                /* Skeleton pour imiter card-stack */
                .skeleton-left-card, .skeleton-right-card {{
                    position: relative;
                    width: 250px;
                    height: 350px;
                    perspective: 1000px;
                }}
                
                /* Une seule carte skeleton par côté */
                .skeleton-card {{
                    position: absolute;
                    top: -30px;
                    left: 0;
                    width: 100%;
                    height: 350px; /* Ajuster selon vos vraies cartes */
                    border-radius: 20px;
                    background: linear-gradient(90deg, #333 25%, #444 50%, #333 75%);
                    background-size: 200% 100%;
                    animation: loading 1.5s infinite;
                    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
                }}
                
                @keyframes loading {{
                    0% {{ background-position: 200% 0; }}
                    100% {{ background-position: -200% 0; }}
                }}
                
                
            </style>
        </head>
        <body>
        
            <!-- Skeleton Loader (affiché par défaut) -->
            <div id="skeleton" class="skeleton-container">
                <div class="skeleton skeleton-title"></div>
                <div class="skeleton skeleton-greeting"></div>
                
                <!-- Structure avec cartes + boutons au centre -->
                <div class="skeleton-cards-wrapper">
                    <div class="skeleton-left-card">
                        <div class="skeleton-card"></div>
                    </div>
                    
                    <!-- Boutons au centre -->
                    <div class="skeleton-center">
                        <div class="skeleton skeleton-button"></div>
                        <div class="skeleton skeleton-button"></div>
                    </div>
                    
                    <div class="skeleton-right-card">
                        <div class="skeleton-card"></div>
                    </div>
                </div>
            </div>
            
            <!-- Image cascade -->
                <div class="cards-wrapper">
                    <div class="card-stack right-stack">
                        <div class="card" style="background-image: url('{apsch_image}');"></div>
                        <div class="card" style="background-image: url('{avsch_image}');"></div>
                        <div class="card" style="background-image: url('{normsch_img}');"></div>

                    </div>
                
                    <!-- Contenu principal (caché par défaut) -->
                    <div id="mainContent" class="main-content">
                        <h1 id="title">SolveReport</h1>
                        <p id="greeting">Hello World</p>
                        <button onclick="createReport()">{self.word[0]}</button>
                        <button onclick="changeLanguage()">{self.word[1]}</button>
                    </div>
                
                    <div class="card-stack left-stack">
                        <div class="card" style="background-image: url('{apsch_image}');"></div>
                        <div class="card" style="background-image: url('{avsch_image}');"></div>
                        <div class="card" style="background-image: url('{normsch_img}');"></div>

                    </div>
                </div>
        
            <script>
                const greetings = ["Hallo Welt", "Привет мир", "Hei maailma", "Hola Mundo", "Bonjour le monde"];
            
                // Démarrer immédiatement quand le DOM est prêt
                document.addEventListener('DOMContentLoaded', function () {{
                    // Affiche le skeleton loader immédiatement
                    document.getElementById('skeleton').classList.remove('hidden');
            
                    // Montre la fenêtre pywebview
                    if (window.pywebview) {{
                        pywebview.api.show_window();
                    }}
            
                    // Change le greeting aléatoirement
                    const randomGreeting = greetings[Math.floor(Math.random() * greetings.length)];
                    document.getElementById("greeting").innerText = randomGreeting;
            
                    // Après 3 secondes (loader), afficher le contenu principal
                    setTimeout(function () {{
                        // Cacher le skeleton
                        document.getElementById('skeleton').classList.add('hidden');
            
                        // Montrer le contenu principal
                        document.getElementById('mainContent').classList.add('loaded');
            
                        // Animation du titre après un court délai
                        setTimeout(function () {{
                            document.getElementById('title').classList.add('animate');
                        }}, 300);
                    
                    // Animer les cartes après apparition du contenu principal
                    setTimeout(() => {{
                        const leftCards = document.querySelectorAll('.left-stack .card');
                        const rightCards = document.querySelectorAll('.right-stack .card');
                    
                        leftCards.forEach((card, i) => {{
                            setTimeout(() => {{
                                card.classList.add('open');
                            }}, i * 200);
                        }});
                    
                        rightCards.forEach((card, i) => {{
                            setTimeout(() => {{
                                card.classList.add('open');
                            }}, i * 200);
                        }});
                    }}, 500); // décalage après #mainContent affiché
                    }}, 3000); // <- durée du skeleton loader
                }});
            
                async function createReport() {{
                    if (window.pywebview) {{
                        try {{
                            const result = await pywebview.api.build_report();
                            console.log('Report created:', result);
                        }} catch (error) {{
                            console.error('Error creating report:', error);
                        }}
                    }} else {{
                        alert("build_report called (mock)");
                    }}
                }}
            
                function changeLanguage() {{
                    document.body.innerHTML = `
                        <h1 style="font-size:50px; font-style:italic; text-align:center;">{self.word[5]}</h1>
                        <button onclick="setLanguage('Fr')">{self.word[2]}</button>
                        <button onclick="setLanguage('En')">{self.word[3]}</button>
                    `;
                }}
            
                function setLanguage(lang) {{
                    if (window.pywebview) {{
                        pywebview.api.set_language(lang);
                    }} else {{
                        alert("Language set to " + lang);
                    }}
                    location.reload();
                }}
            
                async function returnToMain() {{
                    try {{
                        await pywebview.api.return_window();
                    }} catch (error) {{
                        console.error('Error:', error);
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
    # Language
    def set_language(self, lang):
                
        if lang == "Fr":
            
            self.website = "fr.py"
            self.greeting = "Bonjour le monde"
            self.word = list(dict_lang.values())
            return_window()
            
            return {"status": "success", "language": "French"}
            
        elif lang == "En":
            
            self.website = "en.py"
            self.greeting = "Hello World"
            self.word = list(dict_lang.keys())
            return_window()
            
            return {"status": "success", "language": "English"}
        
        active_window = webview.active_window()
        if active_window:
            active_window.load_html(self.get_html_template())
            
        return {"status": "success", "language": "French" if lang == "Fr" else "English"}
        
    # Start Streamlit       
    def start_streamlit(self):
        
        print("Démarrage")
        
        base_path = os.path.abspath(os.path.dirname(__file__))
        print("Fichier en recherche")
        
        lang_dir = 'fr' if 'fr.py' in self.website else 'en'
        streamlit_dir = os.path.join(base_path, lang_dir)

        subprocess.Popen([
            "streamlit", "run", self.website,
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--browser.serverAddress", "localhost"
        ], cwd=streamlit_dir)
            

    # Create frame
    def build_report(self):
        print("Démarrage build_report...")
        
        # Launch Streamlit in another Thread
        threading.Thread(target=self.start_streamlit, daemon=True).start()
        
        time.sleep(1)
        
        try:
            
            # Récupérer l'URL depuis la session Streamlit
            port = st.get_option('server.port')
            url = f"http://localhost:{port}"
            
        except:
            
            # Fallback
            url = "http://localhost:8501"
        
        # Display Streamlit in the active window !
        active_window = webview.active_window()
        if active_window:
            active_window.load_url(url)

# Save API class      
api = API()

def return_window():
    active_window = webview.active_window()
    if active_window:
        active_window.load_html(api.get_html_template())
        
def show_window(self):
    if webview.windows:
        webview.windows[0].show()

# App Exit
def on_app_exit():
    """Function called when app close"""
    license_manager = get_license_manager()
    license_manager.shutdown()      
        
def main():
    
    dropped_files = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if dropped_files:
        public_key_file = None
        license_sr_file = None
        
        # Trier les fichiers selon leur type
        for file_path in dropped_files:
            filename = os.path.basename(file_path).lower()
            
            if filename.endswith('.key') or 'public_key' in filename:
                public_key_file = file_path
            elif filename.endswith('.sr') or 'license.sr' in filename:
                license_sr_file = file_path
            else:
                print("Error")
        
        # Traitement selon ce qui a été trouvé
        if public_key_file and license_sr_file:
            process_license_files(public_key_file, license_sr_file) #warning
        elif public_key_file:
            process_public_key(public_key_file)
        elif license_sr_file:
            process_license_sr(license_sr_file)
        
        else:
            print("Error")
    
    
    try:
        valid, message = initialize_license_system()
        if not valid:
            print(f"Licence Error: {message}")
            return
    except Exception as e:
        print(f"Fatal Error: {e}")
        return
    
    # Enregistre la fonction de nettoyage
    atexit.register(on_app_exit)
    
    # To download all the files
    webview.settings['ALLOW_DOWNLOADS'] = True
    
    # Window Streamlit
    master_window = webview.create_window('SolveReport', html=api.get_html_template(), 
                                          js_api=api, width=900, 
                                          height=800,
                                          confirm_close=True)

    # Adding the widgets
    webview.start(master_window)
    
def process_license_files(key_file, sr_file):
    # Pour la clé - spécifier le nom du fichier de destination
    key_destination = os.path.join(base_path, os.path.basename(key_file)) #
    shutil.copyfile(key_file, key_destination)
    
    # Pour le fichier .sr - créer les dossiers s'ils n'existent pas
    data_path = os.path.join(base_path, 'data')
    en_data_path = os.path.join(base_path, 'en', 'data')
    
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(en_data_path, exist_ok=True)
    
    sr_destination1 = os.path.join(data_path, os.path.basename(sr_file))
    sr_destination2 = os.path.join(en_data_path, os.path.basename(sr_file))
    
    shutil.copyfile(sr_file, sr_destination1)
    shutil.copyfile(sr_file, sr_destination2)

def process_public_key(key_file):
    key_destination = os.path.join(base_path, os.path.basename(key_file))
    shutil.copyfile(key_file, key_destination)

def process_license_sr(sr_file):
    data_path = os.path.join(base_path, 'data')
    en_data_path = os.path.join(base_path, 'en', 'data')
    
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(en_data_path, exist_ok=True)
    
    sr_destination1 = os.path.join(data_path, os.path.basename(sr_file))
    sr_destination2 = os.path.join(en_data_path, os.path.basename(sr_file))
    
    shutil.copyfile(sr_file, sr_destination1)
    shutil.copyfile(sr_file, sr_destination2)
    

if __name__ == '__main__':
    
    main()