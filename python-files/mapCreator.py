import sys, os, time
import pandas as pd
import folium
from geopy.geocoders import Nominatim

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QListWidget, QColorDialog, QMessageBox, QProgressBar,
    QSystemTrayIcon, QStyle, QListWidgetItem
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl


class TransportApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚚 Cartographie Transporteurs")
        self.resize(1200, 800)

        # Layout principal
        layout = QVBoxLayout(self)

        self.label = QLabel("📂 Veuillez charger un fichier Excel (.xlsx ou .csv)")
        layout.addWidget(self.label)

        self.btn_file = QPushButton("1️⃣ - Choisir un fichier Excel/CSV")
        self.btn_file.clicked.connect(self.load_file)
        layout.addWidget(self.btn_file)

        self.btn_colors = QPushButton("2️⃣ - Configurer les couleurs 🎨")
        self.btn_colors.clicked.connect(self.set_colors)
        self.btn_colors.setEnabled(False)
        layout.addWidget(self.btn_colors)

        self.error_list = QListWidget()
        layout.addWidget(QLabel("⚠️ Villes non trouvées :"))
        layout.addWidget(self.error_list)

        layout.addWidget(QLabel("🎨 Couleurs attribuées :"))
        self.color_preview = QListWidget()
        layout.addWidget(self.color_preview)

        self.btn_generate_map = QPushButton("3️⃣ - Générer la carte 🗺️")
        self.btn_generate_map.clicked.connect(self.generate_map)
        self.btn_generate_map.setEnabled(False)
        layout.addWidget(self.btn_generate_map)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray_icon.setVisible(True)

        # Data
        self.df = None
        self.aggregated_df = None
        self.location_coords = {}
        self.carrier_colors = {}
        self.status_colors = {}
        self.origin_coords = None

    def load_file(self):
        """Charger fichier Excel ou CSV"""
        file, _ = QFileDialog.getOpenFileName(
            self, "Choisir un fichier", "", "Fichiers Excel/CSV (*.xlsx *.csv)"
        )
        if not file:
            return

        self.label.setText(f"📂 Fichier chargé : {file}")

        try:
            if file.endswith(".xlsx"):
                df = pd.read_excel(file)
            elif file.endswith(".csv"):
                df = pd.read_csv(file, encoding="latin-1", sep=";")
            else:
                QMessageBox.critical(self, "Erreur", "Format non supporté (uniquement .xlsx ou .csv).")
                return
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de lire le fichier : {e}")
            return

        expected_cols = ["NB_Pieces", "TPS", "Localisation", "Statut"]
        if not all(col in df.columns for col in expected_cols):
            QMessageBox.critical(self, "Erreur", f"Colonnes attendues : {expected_cols}")
            return

        self.df = df
        self.aggregated_df = df.groupby(['TPS', 'Localisation', 'Statut']).agg(
            Total_Pieces=('NB_Pieces', 'sum')
        ).reset_index()

        self.geocode_locations()
        self.btn_colors.setEnabled(True)

        self.tray_icon.showMessage(
            "Cartographie Transporteurs",
            "✅ Données chargées avec succès !",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def geocode_locations(self):
        """Géocodage avec barre de progression"""
        geolocator = Nominatim(user_agent="carte_pyqt6_app")
        origin_location = geolocator.geocode("Bordeaux, France")
        self.origin_coords = (origin_location.latitude, origin_location.longitude)

        self.location_coords = {}
        self.error_list.clear()

        unique_locs = self.aggregated_df['Localisation'].unique()
        total = len(unique_locs)

        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.progress.setMaximum(total)

        for i, loc in enumerate(unique_locs, start=1):
            try:
                location = geolocator.geocode(loc, timeout=10)
                if location:
                    self.location_coords[loc] = (location.latitude, location.longitude)
                else:
                    self.location_coords[loc] = (None, None)
                    self.error_list.addItem(f"❌ {loc}")
                time.sleep(1)
            except Exception:
                self.location_coords[loc] = (None, None)
                self.error_list.addItem(f"❌ {loc}")

            self.progress.setValue(i)
            QApplication.processEvents()

        self.progress.setVisible(False)

    def set_colors(self):
        """Choix des couleurs avec récap"""
        self.color_preview.clear()
        self.carrier_colors.clear()
        self.status_colors.clear()

        for t in self.aggregated_df['TPS'].unique():
            QMessageBox.information(self, "Choix de couleur", f"🎨 Choisissez une couleur pour le transporteur : {t}")
            color = QColorDialog.getColor(title=f"Couleur pour {t}")
            self.carrier_colors[t] = color.name() if color.isValid() else "grey"
            item = QListWidgetItem(f"Transporteur : {t}")
            item.setBackground(color)
            self.color_preview.addItem(item)

        for s in self.aggregated_df['Statut'].unique():
            QMessageBox.information(self, "Choix de couleur", f"🎨 Choisissez une couleur pour le statut : {s}")
            color = QColorDialog.getColor(title=f"Couleur pour {s}")
            self.status_colors[s] = color.name() if color.isValid() else "grey"
            item = QListWidgetItem(f"Statut : {s}")
            item.setBackground(color)
            self.color_preview.addItem(item)

        self.btn_generate_map.setEnabled(True)

    def generate_map(self):
        """Création de la carte avec filtres, slider et switch couleurs"""
        m = folium.Map(location=self.origin_coords, zoom_start=5)
        features = []

        for _, row in self.aggregated_df.iterrows():
            dest_loc = row['Localisation']
            dest_coords = self.location_coords.get(dest_loc)
            if dest_coords and all(dest_coords):
                properties = {
                    'tps': row['TPS'], 'statut': row['Statut'], 'volume': row['Total_Pieces'],
                    'tps_color': self.carrier_colors.get(row['TPS'], 'grey'),
                    'statut_color': self.status_colors.get(row['Statut'], 'grey'),
                    'popup': f"<b>{row['TPS']} ({row['Statut']})</b><br>{row['Total_Pieces']} pièces vers<br>{dest_loc}"
                }
                features.append({
                    'type': 'Feature',
                    'geometry': {'type': 'LineString',
                                 'coordinates': [[self.origin_coords[1], self.origin_coords[0]],
                                                 [dest_coords[1], dest_coords[0]]]},
                    'properties': properties
                })
                features.append({
                    'type': 'Feature',
                    'geometry': {'type': 'Point', 'coordinates': [dest_coords[1], dest_coords[0]]},
                    'properties': properties
                })

        point_to_layer_js = """
        function(feature, latlng) {
            return L.circleMarker(latlng, {
                radius: Math.sqrt(feature.properties.volume) * 0.25,
                color: feature.properties.tps_color,
                fillColor: feature.properties.tps_color,
                fillOpacity: 0.6,
                weight: 0
            });
        }
        """

        geojson_layer = folium.GeoJson(
            {'type': 'FeatureCollection', 'features': features},
            style_function=lambda x: {'color': x['properties']['tps_color'], 'weight': 2, 'opacity': 1},
            popup=folium.GeoJsonPopup(fields=['popup']),
            point_to_layer=folium.JsCode(point_to_layer_js)
        ).add_to(m)

        all_tps = sorted(self.df['TPS'].unique())
        all_statut = sorted(self.df['Statut'].unique())

        filter_html = f'''
        <style>
            .legend-color {{ display: inline-block; width: 12px; height: 12px; margin-right: 5px; border: 1px solid #777; vertical-align: middle; }}
            .filter-container label {{ display: flex; align-items: center; margin-bottom: 5px; }}
            .filter-container input[type="checkbox"] {{ margin-right: 5px; }}
            .filter-container .slider-label {{ font-size: 12px; margin-bottom: 5px; color: #333; }}
            #colorModeBtn {{ width: 100%; padding: 8px; margin-top: 10px; cursor: pointer; background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 4px; }}
            #colorModeBtn:hover {{ background-color: #e0e0e0; }}
        </style>
        <div class="filter-container" style="position: fixed; top: 10px; right: 10px; z-index:1000; background-color: white; border: 2px solid grey; padding: 10px; border-radius: 5px; font-family: sans-serif;">
            <h4>Filtres</h4>
            <strong>Transporteur (TPS)</strong><br>
            {''.join([f'<label for="{tps}"><input type="checkbox" id="{tps}" class="filter-tps" checked onchange="applyFilters()"><span class="legend-color" style="background-color:{self.carrier_colors.get(tps, "grey")};"></span>{tps}</label>' for tps in all_tps])}
            <hr>
            <strong>Statut</strong><br>
            {''.join([f'<label for="{statut}"><input type="checkbox" id="{statut}" class="filter-statut" checked onchange="applyFilters()"><span class="legend-color" style="background-color:{self.status_colors.get(statut, "grey")};"></span>{statut}</label>' for statut in all_statut])}
            <hr>
            <div class="slider-label">Ajuster la taille des cercles</div>
            <input type="range" id="sizeSlider" min="0.05" max="0.8" step="0.05" value="0.25" style="width: 100%;" oninput="applyFilters()">
            <button id="colorModeBtn" onclick="toggleColorMode()">Passer en Vue par Statut</button>
        </div>
        '''

        filter_js = f"""
        <script type="text/javascript">
            let colorMode = 'tps';
            function toggleColorMode() {{
                const btn = document.getElementById('colorModeBtn');
                colorMode = (colorMode === 'tps') ? 'statut' : 'tps';
                btn.textContent = (colorMode === 'tps') ? 'Passer en Vue par Statut' : 'Passer en Vue par Transporteur';
                applyFilters();
            }}

            function applyFilters() {{
                const checkedTps = Array.from(document.querySelectorAll('.filter-tps:checked')).map(el => el.id);
                const checkedStatut = Array.from(document.querySelectorAll('.filter-statut:checked')).map(el => el.id);
                const sizeMultiplier = document.getElementById('sizeSlider').value;
                const layerToFilter = {geojson_layer.get_name()};

                layerToFilter.eachLayer(function(layer) {{
                    const props = layer.feature.properties;
                    const isVisible = checkedTps.includes(props.tps) && checkedStatut.includes(props.statut);
                    const newColor = (colorMode === 'tps') ? props.tps_color : props.statut_color;

                    if (isVisible) {{
                        if (layer.setStyle) {{
                            layer.setStyle({{ opacity: 1, fillOpacity: 0.6, color: newColor, fillColor: newColor }});
                        }}
                        if (layer.setRadius) {{
                            const newRadius = Math.sqrt(props.volume) * sizeMultiplier;
                            layer.setRadius(Math.min(newRadius, 40));
                        }}
                    }} else {{
                        if (layer.setStyle) {{ layer.setStyle({{ opacity: 0, fillOpacity: 0 }}); }}
                    }}
                }});
            }}
            document.addEventListener("DOMContentLoaded", function() {{
                applyFilters();
            }});
        </script>
        """

        m.get_root().html.add_child(folium.Element(filter_html + filter_js))

        output_filename = "carte_finale.html"
        m.save(output_filename)

        self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath(output_filename)))
        QMessageBox.information(self, "Succès", f"✅ Carte générée : {output_filename}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = TransportApp()
    win.show()
    sys.exit(app.exec())
