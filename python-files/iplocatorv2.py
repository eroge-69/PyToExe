import sys
import os
import folium
import requests
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QLineEdit, QPushButton, QTextEdit, QLabel
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer, Qt

class IPLocatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IP Locator - Integrated Map")
        self.setGeometry(100, 100, 1200, 900) # Taille de la fenêtre principale

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- Champ de texte et bouton ---
        self.input_layout = QHBoxLayout()
        self.main_layout.addLayout(self.input_layout)

        self.label = QLabel("Commande:")
        self.input_layout.addWidget(self.label)

        self.entry_command = QLineEdit()
        self.entry_command.setPlaceholderText("Ex: locate 8.8.8.8")
        self.entry_command.returnPressed.connect(self.process_command) # Connecter Entrée
        self.input_layout.addWidget(self.entry_command)

        self.button_execute = QPushButton("Exécuter")
        self.button_execute.clicked.connect(self.process_command)
        self.input_layout.addWidget(self.button_execute)

        # --- Console de sortie ---
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFixedHeight(150) # Hauteur fixe pour la console
        self.console_output.setStyleSheet("background-color: black; color: white;")
        self.main_layout.addWidget(self.console_output)

        # --- Carte WebEngine ---
        self.web_view = QWebEngineView()
        self.main_layout.addWidget(self.web_view)

        # Propriétés de la carte Folium
        self.map_file = "integrated_ip_locator_map.html"
        self.current_lat = 0
        self.current_lon = 0
        self.current_zoom = 2 # Commencer avec un zoom global
        self.zoom_step = 1 # Pour la séquence de zoom

        self.log_to_console("Application démarrée. Tapez 'locate <adresse_ip>' pour localiser une IP.")
        self.log_to_console("La carte sera intégrée dans cette fenêtre.")

        # Charger une carte mondiale par défaut au démarrage
        self.update_map_view(0, 0, 2)

    def log_to_console(self, message):
        """Ajoute un message à la console."""
        self.console_output.append(message)
        # Faire défiler automatiquement vers le bas
        self.console_output.verticalScrollBar().setValue(self.console_output.verticalScrollBar().maximum())

    def save_map_to_html(self, lat, lon, zoom_start, marker_popup=None):
        """Crée et sauvegarde la carte Folium dans un fichier HTML."""
        map_view = folium.Map(location=[lat, lon], zoom_start=zoom_start)
        if marker_popup:
            folium.Marker([lat, lon], popup=marker_popup).add_to(map_view)
        try:
            map_view.save(self.map_file)
            return True
        except Exception as e:
            self.log_to_console(f"Erreur lors de la sauvegarde de la carte HTML: {e}")
            return False

    def update_map_view(self, lat, lon, zoom, marker_popup=None):
        """Met à jour la carte affichée dans QWebEngineView."""
        if self.save_map_to_html(lat, lon, zoom, marker_popup):
            # Charger le fichier HTML local dans le QWebEngineView
            self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath(self.map_file)))
            self.current_lat = lat
            self.current_lon = lon
            self.current_zoom = zoom

    def process_command(self):
        """Traite les commandes entrées par l'utilisateur."""
        command_text = self.entry_command.text().strip()
        self.log_to_console(f"> {command_text}")
        self.entry_command.clear() # Efface le champ d'entrée

        parts = command_text.split()
        if not parts:
            self.log_to_console("Veuillez entrer une commande.")
            return

        command = parts[0].lower()

        if command == "locate":
            if len(parts) > 1:
                ip_address = parts[1]
                self.locate_ip(ip_address)
            else:
                self.log_to_console("Usage: locate <adresse_ip>")
        elif command == "clear":
            self.console_output.clear()
            self.log_to_console("Console effacée.")
        elif command == "exit":
            self.close_application()
        else:
            self.log_to_console(f"Commande inconnue: {command}")

    def locate_ip(self, ip_address):
        """Géolocalise une adresse IP via une API."""
        self.log_to_console(f"Localisation de l'IP: {ip_address}...")
        api_url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "success":
                lat = data["lat"]
                lon = data["lon"]
                city = data["city"]
                country = data["country"]
                isp = data["isp"]

                self.log_to_console(f"Localisé à: {city}, {country}")
                self.log_to_console(f"Latitude: {lat}, Longitude: {lon}")
                self.log_to_console(f"ISP: {isp}")

                # Lancer le zoom progressif
                self.start_progressive_zoom_sequence(lat, lon, city, country)
            else:
                self.log_to_console(f"Erreur de localisation: {data.get('message', 'Impossible de localiser l\'IP.')}")
        except requests.exceptions.RequestException as e:
            self.log_to_console(f"Erreur de connexion à l'API: {e}")
        except json.JSONDecodeError:
            self.log_to_console("Erreur: Réponse JSON invalide de l'API.")
        except Exception as e:
            self.log_to_console(f"Une erreur inattendue est survenue: {e}")

    def start_progressive_zoom_sequence(self, lat, lon, city, country):
        """Démarre la séquence de zoom progressif."""
        self.log_to_console("Démarrage du zoom progressif sur la carte...")
        self.zoom_step = 1 # Réinitialiser l'étape de zoom

        # Utiliser QTimer pour planifier les étapes de zoom
        self.zoom_timer = QTimer(self)
        self.zoom_timer.timeout.connect(lambda: self.perform_zoom_step(lat, lon, city, country))
        self.zoom_timer.start(1500) # Démarrer le timer, premier appel après 1.5s

    def perform_zoom_step(self, lat, lon, city, country):
        """Exécute une étape du zoom progressif."""
        if self.zoom_step > 5: # 5 étapes de zoom
            self.log_to_console("Zoom progressif terminé.")
            self.zoom_timer.stop() # Arrêter le timer
            return

        zoom_level = 0
        message = ""
        popup = f"{city}, {country}<br>Lat: {lat}, Lon: {lon}"

        if self.zoom_step == 1:
            zoom_level = 2
            message = "Zoom 1: Vue globale."
        elif self.zoom_step == 2:
            zoom_level = 6
            message = "Zoom 2: Vue du continent/région."
        elif self.zoom_step == 3:
            zoom_level = 10
            message = "Zoom 3: Vue du pays/grande région."
        elif self.zoom_step == 4:
            zoom_level = 14
            message = "Zoom 4: Vue de la ville."
        elif self.zoom_step == 5:
            zoom_level = 16
            message = "Zoom 5: Détail de la rue/zone approximative."

        self.log_to_console(message)

        # Mettre à jour la carte dans QWebEngineView
        self.update_map_view(lat, lon, zoom_level, popup)

        self.zoom_step += 1

    def close_application(self):
        """Gère la fermeture propre de l'application."""
        if os.path.exists(self.map_file):
            try:
                os.remove(self.map_file)
            except OSError as e:
                self.log_to_console(f"Erreur lors de la suppression du fichier carte: {e}")
        self.close() # Ferme la fenêtre PyQt


if __name__ == "__main__":
    # Nettoyer le fichier HTML de la carte au démarrage si un précédent est resté
    if os.path.exists("integrated_ip_locator_map.html"):
        os.remove("integrated_ip_locator_map.html")

    app = QApplication(sys.argv)
    window = IPLocatorApp()
    window.show()
    sys.exit(app.exec_())