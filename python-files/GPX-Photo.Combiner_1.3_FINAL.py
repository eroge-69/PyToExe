import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import datetime
import webbrowser
import sys
import shutil
import json
from PIL import Image

# Prüfen ob gpxpy installiert ist, falls nicht, versuchen zu installieren
try:
    import gpxpy
    import gpxpy.gpx
except ImportError:
    print("gpxpy nicht gefunden. Versuche zu installieren...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gpxpy"])
        import gpxpy
        import gpxpy.gpx
        print("gpxpy erfolgreich installiert!")
    except:
        print("Konnte gpxpy nicht installieren. Bitte manuell installieren: pip install gpxpy")
        sys.exit(1)

class GeotaggingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("GPX-Foto-Geotagging Tool")
        self.root.geometry("800x650")
        
        # ZUERST alle Variablen initialisieren
        self.gpx_file = tk.StringVar()
        self.photo_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.tolerance = tk.IntVar(value=120)
        self.progress = tk.DoubleVar()
        self.title_text = tk.StringVar(value="GPX Track mit Fotos")
        
        # GUI Widgets (werden später initialisiert)
        self.log_text = None
        self.progress_bar = None
        self.status_label = None
        
        # GUI erstellen
        self.create_widgets()
        
    def create_widgets(self):
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Konfiguration der Grid-Gewichtung
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Titel-Eingabe
        ttk.Label(main_frame, text="Titel:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(main_frame, textvariable=self.title_text, width=50).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # GPX-Dateiauswahl
        ttk.Label(main_frame, text="GPX-Datei:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(main_frame, textvariable=self.gpx_file, width=50).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Durchsuchen", command=self.browse_gpx).grid(row=1, column=2, padx=5, pady=5)
        
        # Fotoordnerauswahl
        ttk.Label(main_frame, text="Fotoordner:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(main_frame, textvariable=self.photo_dir, width=50).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Durchsuchen", command=self.browse_photo_dir).grid(row=2, column=2, padx=5, pady=5)
        
        # Ausgabeordnerauswahl
        ttk.Label(main_frame, text="Ausgabeordner:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(main_frame, textvariable=self.output_dir, width=50).grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Durchsuchen", command=self.browse_output_dir).grid(row=3, column=2, padx=5, pady=5)
        
        # Toleranz-Einstellung
        ttk.Label(main_frame, text="Zeittoleranz (Sekunden):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(main_frame, textvariable=self.tolerance, width=10).grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Startbutton
        ttk.Button(main_frame, text="Starte Verarbeitung", command=self.start_processing).grid(row=5, column=1, pady=10)
        
        # Fortschrittsbalken
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # Statusanzeige
        self.status_label = ttk.Label(main_frame, text="Bereit")
        self.status_label.grid(row=7, column=0, columnspan=3, padx=5, pady=5)
        
        # Log-Ausgabe
        ttk.Label(main_frame, text="Log:").grid(row=8, column=0, padx=5, pady=5, sticky="nw")
        
        # Text widget für Log
        self.log_text = tk.Text(main_frame, height=10, width=70)
        self.log_text.grid(row=9, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # Scrollbar für Log
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=9, column=3, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # Erste Nachricht NACH der Initialisierung von log_text
        self.log_message("Programm gestartet. Bitte wählen Sie die Dateien aus.")
        
    def log_message(self, message):
        """Fügt eine Nachricht zum Log hinzu"""
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        else:
            print(message)
        
    def browse_gpx(self):
        filename = filedialog.askopenfilename(
            title="GPX-Datei auswählen",
            filetypes=[("GPX files", "*.gpx"), ("Alle Dateien", "*.*")]
        )
        if filename:
            self.gpx_file.set(filename)
            self.log_message(f"GPX-Datei ausgewählt: {filename}")
            
    def browse_photo_dir(self):
        directory = filedialog.askdirectory(title="Fotoordner auswählen")
        if directory:
            self.photo_dir.set(directory)
            self.log_message(f"Fotoordner ausgewählt: {directory}")
            
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Ausgabeordner auswählen")
        if directory:
            self.output_dir.set(directory)
            self.log_message(f"Ausgabeordner ausgewählt: {directory}")
            
    def start_processing(self):
        if not all([self.gpx_file.get(), self.photo_dir.get(), self.output_dir.get()]):
            self.log_message("Fehler: Bitte wählen Sie alle Pfade aus!")
            messagebox.showerror("Fehler", "Bitte wählen Sie alle Pfade aus!")
            return
            
        if not os.path.exists(self.gpx_file.get()):
            self.log_message("Fehler: GPX-Datei existiert nicht!")
            messagebox.showerror("Fehler", "GPX-Datei existiert nicht!")
            return
            
        if not os.path.exists(self.photo_dir.get()):
            self.log_message("Fehler: Fotoordner existiert nicht!")
            messagebox.showerror("Fehler", "Fotoordner existiert nicht!")
            return
            
        self.root.after(100, self.process_data)
        
    def process_data(self):
        try:
            self.log_message("="*50)
            self.log_message("Starte Verarbeitung...")
            self.status_label.config(text="Lese GPX-Daten...")
            self.root.update_idletasks()
            
            # GPX-Daten einlesen
            try:
                with open(self.gpx_file.get(), 'r', encoding='utf-8') as gpx_file:
                    gpx = gpxpy.parse(gpx_file)
                self.log_message("GPX-Datei erfolgreich gelesen")
            except Exception as e:
                self.log_message(f"Fehler beim Lesen der GPX-Datei: {str(e)}")
                return
            
            # Track-Start- und Endzeit ermitteln
            start_time, end_time = self.get_gpx_time_range(gpx)
            start_date_str = start_time.strftime('%d.%m.%Y') if start_time else "Unbekannt"
            start_time_str = start_time.strftime('%H:%M:%S') if start_time else "Unbekannt"
            end_time_str = end_time.strftime('%H:%M:%S') if end_time else "Unbekannt"
                
            # Trackpunkte extrahieren
            points = []
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        if point.time:
                            try:
                                point_time = point.time
                                if hasattr(point_time, 'tzinfo') and point_time.tzinfo is not None:
                                    point_time = point_time.replace(tzinfo=None)
                                    
                                points.append({
                                    'time': point_time,
                                    'latitude': point.latitude,
                                    'longitude': point.longitude,
                                    'elevation': point.elevation if point.elevation else 0
                                })
                            except:
                                continue
            
            if not points:
                self.log_message("Fehler: Keine Trackpunkte mit Zeitstempel in der GPX-Datei gefunden!")
                messagebox.showerror("Fehler", "Keine Trackpunkte mit Zeitstempel gefunden!")
                return
                
            self.log_message(f"{len(points)} GPX-Trackpunkte mit Zeitstempel gefunden")
            
            self.status_label.config(text="Verarbeite Fotos...")
            self.progress.set(0)
            self.root.update_idletasks()
            
            # Ordner erstellen
            photo_output_dir = os.path.join(self.output_dir.get(), "photos")
            thumbs_output_dir = os.path.join(self.output_dir.get(), "thumbs")
            os.makedirs(photo_output_dir, exist_ok=True)
            os.makedirs(thumbs_output_dir, exist_ok=True)
            
            # Fotos verarbeiten
            photo_files = []
            for f in os.listdir(self.photo_dir.get()):
                if f.lower().endswith(('.jpg', '.jpeg', '.tiff', '.png', '.heic', '.bmp')):
                    photo_files.append(f)
            
            total_photos = len(photo_files)
            
            if total_photos == 0:
                self.log_message("Fehler: Keine Fotos im ausgewählten Ordner gefunden!")
                messagebox.showerror("Fehler", "Keine Fotos gefunden!")
                return
                
            self.log_message(f"{total_photos} Fotos gefunden")
            
            processed_photos = 0
            photo_markers = []
            matched_photos = 0
            gps_data = []
            
            for photo_file in photo_files:
                photo_path = os.path.join(self.photo_dir.get(), photo_file)
                output_photo_path = os.path.join(photo_output_dir, photo_file)
                
                try:
                    # EXIF-Daten lesen
                    with Image.open(photo_path) as img:
                        exif_data = img._getexif() or {}
                    
                    # Aufnahmezeit aus EXIF extrahieren
                    datetime_original = None
                    for tag, value in exif_data.items():
                        tag_name = self.get_exif_tag_name(tag)
                        if tag_name == 'DateTimeOriginal' and value:
                            try:
                                datetime_original = datetime.datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                                break
                            except (ValueError, TypeError):
                                continue
                    
                    if datetime_original:
                        # Nächsten GPX-Punkt finden
                        closest_point = self.find_closest_point(points, datetime_original)
                        
                        if closest_point:
                            # Kopiere Originalfoto
                            shutil.copy2(photo_path, output_photo_path)
                            
                            # Erstelle Thumbnail
                            thumb_path = self.create_thumbnail(photo_path, thumbs_output_dir, photo_file)
                            
                            # GPS-Daten speichern
                            photo_gps_data = {
                                'filename': photo_file,
                                'latitude': closest_point['latitude'],
                                'longitude': closest_point['longitude'],
                                'elevation': closest_point['elevation'],
                                'timestamp': datetime_original.strftime('%Y-%m-%d %H:%M:%S'),
                                'gpx_time': closest_point['time'].strftime('%Y-%m-%d %H:%M:%S'),
                                'time_difference': abs((closest_point['time'] - datetime_original).total_seconds())
                            }
                            gps_data.append(photo_gps_data)
                            
                            # Marker für Webseite
                            photo_markers.append({
                                'lat': closest_point['latitude'],
                                'lon': closest_point['longitude'],
                                'thumb_path': f"thumbs/{os.path.basename(thumb_path)}",
                                'original_path': f"photos/{photo_file}",
                                'time': datetime_original.strftime('%Y-%m-%d %H:%M:%S'),
                                'name': photo_file
                            })
                            matched_photos += 1
                            self.log_message(f"✓ {photo_file}: GPS-Daten zugewiesen")
                        else:
                            self.log_message(f"✗ {photo_file}: Kein passender GPX-Punkt (Toleranz: {self.tolerance.get()}s)")
                    else:
                        self.log_message(f"✗ {photo_file}: Kein EXIF-Zeitstempel gefunden")
                        
                except Exception as e:
                    self.log_message(f"Fehler bei {photo_file}: {str(e)}")
                
                # Fortschritt aktualisieren
                processed_photos += 1
                progress_percent = (processed_photos / total_photos) * 100
                self.progress.set(progress_percent)
                self.status_label.config(text=f"Verarbeite Foto {processed_photos}/{total_photos}")
                self.root.update_idletasks()
            
            # GPS-Daten speichern
            if gps_data:
                gps_json_path = os.path.join(self.output_dir.get(), 'gps_data.json')
                with open(gps_json_path, 'w', encoding='utf-8') as f:
                    json.dump(gps_data, f, indent=2, ensure_ascii=False)
                self.log_message(f"GPS-Daten gespeichert: {gps_json_path}")
            
            # Webseite generieren
            if photo_markers:
                self.status_label.config(text="Generiere Webseite...")
                self.root.update_idletasks()
                
                self.generate_webpage(points, photo_markers, start_date_str, start_time_str, end_time_str)
                
                self.log_message("="*50)
                self.log_message(f"ABGESCHLOSSEN! {matched_photos} von {total_photos} Fotos verarbeitet")
                self.status_label.config(text="Abgeschlossen!")
                self.progress.set(100)
                
                messagebox.showinfo("Fertig", 
                    f"Verarbeitung abgeschlossen!\n"
                    f"{matched_photos} von {total_photos} Fotos wurden verarbeitet.\n"
                    f"Webseite wurde erstellt.")
                
            else:
                self.log_message("Keine Fotos mit GPS-Daten gefunden")
                messagebox.showinfo("Fertig", "Keine Fotos konnten zugeordnet werden.")
                
        except Exception as e:
            self.log_message(f"FEHLER: {str(e)}")
            import traceback
            self.log_message(traceback.format_exc())
            self.status_label.config(text="Fehler aufgetreten")
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten:\n{str(e)}")
    
    def get_gpx_time_range(self, gpx):
        """Ermittelt Start- und Endzeit des GPX-Tracks"""
        start_time = None
        end_time = None
        
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.time:
                        point_time = point.time
                        if hasattr(point_time, 'tzinfo') and point_time.tzinfo is not None:
                            point_time = point_time.replace(tzinfo=None)
                        
                        if start_time is None or point_time < start_time:
                            start_time = point_time
                        if end_time is None or point_time > end_time:
                            end_time = point_time
        
        return start_time, end_time
    
    def create_thumbnail(self, photo_path, output_dir, filename):
        """Erstellt eine Vorschauversion des Bildes für die Webseite"""
        try:
            name, ext = os.path.splitext(filename)
            thumb_name = f"{name}_thumb{ext}"
            thumb_path = os.path.join(output_dir, thumb_name)
            
            with Image.open(photo_path) as img:
                # Größe für Thumbnail (max 400x300)
                img.thumbnail((400, 300))
                
                # Speichere Thumbnail
                if ext.lower() in ['.jpg', '.jpeg']:
                    img.save(thumb_path, 'JPEG', quality=90)
                elif ext.lower() == '.png':
                    img.save(thumb_path, 'PNG', optimize=True)
                else:
                    # Für andere Formate als JPEG/PNG
                    img.convert('RGB').save(thumb_path, 'JPEG', quality=90)
            
            return thumb_path
        except Exception as e:
            self.log_message(f"Fehler beim Erstellen des Thumbnails für {filename}: {e}")
            # Fallback: Kopiere Original
            fallback_path = os.path.join(output_dir, filename)
            shutil.copy2(photo_path, fallback_path)
            return fallback_path
            
    def get_exif_tag_name(self, tag):
        """Hilfsfunktion zum Abrufen von EXIF-Tag-Namen"""
        exif_tags = {
            36867: 'DateTimeOriginal',
            36868: 'DateTimeDigitized',
            306: 'DateTime',
            271: 'Make',
            272: 'Model',
        }
        return exif_tags.get(tag, f'Tag_{tag}')
            
    def find_closest_point(self, points, target_time):
        closest_point = None
        min_time_diff = float('inf')
        
        for point in points:
            if point['time']:
                try:
                    time_diff = abs((point['time'] - target_time).total_seconds())
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        closest_point = point
                except:
                    continue
                
        if min_time_diff <= self.tolerance.get():
            return closest_point
        return None
        
    def generate_webpage(self, track_points, photo_markers, start_date, start_time, end_time):
        try:
            # Erstelle track points für JavaScript
            track_points_js = "[\n"
            for i, point in enumerate(track_points):
                if i > 0:
                    track_points_js += ",\n"
                track_points_js += f"        [{point['latitude']}, {point['longitude']}]"
            track_points_js += "\n    ]"
            
            html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title_text.get()}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body {{ 
            margin: 0; 
            padding: 0; 
            font-family: Arial, sans-serif;
        }}
        #map {{ 
            position: absolute; 
            top: 0; 
            bottom: 0; 
            right: 0; 
            left: 0; 
        }}
        .map-control {{ 
            position: absolute; 
            top: 10px; 
            right: 10px; 
            z-index: 1000; 
            background: white; 
            padding: 10px; 
            border-radius: 4px;
            box-shadow: 0 1px 5px rgba(0,0,0,0.4);
        }}
        .photo-popup {{ 
            text-align: center;
            max-width: 500px;
        }}
        .photo-popup img {{ 
            max-width: 100%; 
            max-height: 300px; 
            margin-bottom: 15px;
            border-radius: 8px;
            border: 3px solid #eee;
            box-shadow: 极 2px 8px rgba(0,0,0,0.2);
        }}
        .photo-popup h3 {{
            margin: 10px 0 5px 0;
            color: #333;
            font-size: 16px;
        }}
        .photo-popup p {{
            margin: 5px 0;
            color: #666;
            font-size: 14px;
        }}
        .info {{ 
            position: absolute; 
            top: 10px; 
            left: 10px; 
            z-index: 1000; 
            background: white; 
            padding: 15px; 
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            max-width: 300px;
        }}
        h1 {{ 
            font-size: 1.3em; 
            margin-top: 0; 
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        .info p {{
            margin: 6px 0;
            font-size: 0.95em;
            color: #555;
        }}
        select {{
            padding: 8px;
            border-radius: 5px;
            border: 2px solid #ddd;
            font-size: 14px;
        }}
        .legend {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background: white;
            padding: 12px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            font-size: 12px;
        }}
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #3498db;
            z-index: 2000;
            text-align: center;
            font-weight: bold;
            color: #2c3e50;
        }}
        .loading.hidden {{
            display: none;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    
    <div class="info">
        <h1>{self.title_text.get()}</h1>
        <p>📸 Fotos: {len(photo_markers)}</p>
        <p>📍 Trackpunkte: {len(track_points)}</p>
        <p>📅 Datum: {start_date}</p>
        <p>⏰ Start: {start_time}</p>
        <p>⏰ Ende: {end_time}</p>
    </div>
    
    <div class="map-control">
        <select id="map-type">
            <option value="osm">OpenStreetMap</option>
            <option value="satellite">Satellit</option>
        </select>
    </div>

    <div class="legend">
        <strong>Legende:</strong><br>
        📍 Foto-Positionen ({len(photo_markers)})<br>
        🔵 GPX-Track
    </div>

    <div id="loading" class="loading">
        📷 Lade Bilder...<br>
        <small>Bitte warten Sie einen Moment</small>
    </div>

    <script>
        // Karte initialisieren
        var trackPoints = {track_points_js};
        
        // Grenzen berechnen (mit etwas Padding)
        var bounds = L.latLngBounds(trackPoints).pad(0.1);
        var map = L.map('map').fitBounds(bounds);
        
        // Layer definieren
        var osmLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap Mitwirkende',
            maxZoom: 19
        }});
        
        var satelliteLayer = L.tileLayer('https://{{s}}.google.com/vt/lyrs=s&x={{x}}&y={{y}}&z={{z}}', {{
            attribution: '© Google',
            subdomains: ['mt0','mt1','mt2','mt3'],
            maxZoom: 21
        }});
        
        // Standardlayer
        osmLayer.addTo(map);
        
        // Track zeichnen
        L.polyline(trackPoints, {{
            color: '#3498db', 
            weight: 5, 
            opacity: 0.8,
            smoothFactor: 1,
            className: 'gpx-track'
        }}).addTo(map);
        
        // Foto-Marker mit custom Icon
        var photoIcon = L.icon({{
            iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
            iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        }});
        
        // Marker erstellen
        var markers = L.layerGroup();
        {self.generate_marker_js(photo_markers)}
        markers.addTo(map);
        
        // Layer-Umschaltung
        document.getElementById('map-type').addEventListener('change', function(e) {{
            map.removeLayer(osmLayer);
            map.removeLayer(satelliteLayer);
            
            if (e.target.value === 'osm') {{
                osmLayer.addTo(map);
            }} else {{
                satelliteLayer.addTo(map);
            }}
        }});
        
        // Kartensteuerung
        L.control.layers({{
            "OpenStreetMap": osmLayer,
            "Satellitenansicht": satelliteLayer
        }}, {{
            "Fotos anzeigen": markers
        }}).addTo(map);
        
        // Maßstabsleiste
        L.control.scale({{imperial: false, metric: true}}).addTo(map);
        
        // Einfache Funktion zum Ausblenden des Ladebildschirms nach Zeit
        function hideLoadingScreen() {{
            var loadingDiv = document.getElementById('loading');
            // Warte 2 Sekunden, dann verstecke den Ladebildschirm
            setTimeout(function() {{
                loadingDiv.classList.add('hidden');
            }}, 2000);
        }}
        
        // Verstecke Ladebildschirm wenn die Karte fertig geladen ist
        map.whenReady(hideLoadingScreen);
        
        // Verstecke Ladebildschirm auch wenn alle Ressourcen geladen sind
        window.addEventListener('load', hideLoadingScreen);
        
        // Fallback: Verstecke Ladebildschirm nach maximal 5 Sekunden
        setTimeout(hideLoadingScreen, 5000);
    </script>
</body>
</html>"""
            
            # HTML-Datei speichern
            html_path = os.path.join(self.output_dir.get(), 'map.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            self.log_message(f"Webseite erstellt: {html_path}")
            
        except Exception as e:
            self.log_message(f"Fehler beim Erstellen der Webseite: {str(e)}")
            
    def generate_marker_js(self, photo_markers):
        js_code = ""
        for marker in photo_markers:
            # Korrekter relativer Pfad für die Webseite
            thumb_path = marker['thumb_path'].replace('\\', '/')
            js_code += f"""
        L.marker([{marker['lat']}, {marker['lon']}], {{
            icon: L.icon({{
                iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34]
            }}),
            title: '{marker['name']}'
        }})
        .addTo(markers)
        .bindPopup(`
            <div class="photo-popup">
                <img src="{thumb_path}" alt="{marker['name']}" 
                     onerror="this.src='https://via.placeholder.com/400x300/eee/999?text=Bild+nicht+gefunden'" 
                     style="cursor: pointer;" 
                     onclick="window.open('photos/{marker['name']}', '_blank')">
                <h3>{marker['name']}</h3>
                <p>📅 {marker['time']}</p>
                <p>📍 {marker['lat']:.6f}, {marker['lon']:.6f}</p>
            </div>
        `, {{maxWidth: 500}});
            """
        return js_code

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = GeotaggingTool(root)
        root.mainloop()
    except Exception as e:
        print(f"Fehler: {e}")
        input("Drücken Sie Enter zum Beenden...")