import os
import sys
import numpy as np
import rasterio
from rasterio.plot import show
from sklearn.linear_model import LinearRegression
from mapclassify import NaturalBreaks
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import box
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ----------------------------
# Gestion des chemins PyInstaller
# ----------------------------
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# ----------------------------
# Classe d'analyse
# ----------------------------
class DesertificationAnalysis:
    def __init__(self, image_path, sensor_type, cell_size=100, n_classes=5):
        self.image_path = image_path
        self.sensor_type = sensor_type
        self.cell_size = cell_size
        self.n_classes = n_classes
        self.image = None
        self.profile = None
        self.tc_components = {}
        self.ddi = None
        self.slope_grid = None
        self.classification = None
        self.grid_cells = []

    def load_image(self):
        with rasterio.open(self.image_path) as src:
            self.image = src.read().astype(float)
            self.profile = src.profile
            self.nodata = src.nodata if src.nodata is not None else np.nan

    def calculate_tasseled_cap(self):
        if self.sensor_type == 'Landsat8':
            brightness_coef = [0.3029, 0.2786, 0.4733, 0.5599, 0.508, 0.1872]
            greenness_coef = [-0.2941, -0.243, -0.5424, 0.7276, 0.0713, -0.1608]
            wetness_coef = [0.1511, 0.1973, 0.3283, 0.3407, -0.7117, -0.4559]
        elif self.sensor_type == 'Sentinel2':
            brightness_coef = [0.2381, 0.2569, 0.2934, 0.3070, 0.1603, 0.1016]
            greenness_coef = [-0.2266, -0.2818, -0.4934, 0.7941, -0.0002, -0.1446]
            wetness_coef = [0.1825, 0.1763, 0.1615, 0.0713, -0.0849, -0.8312]
        elif self.sensor_type == 'MODIS':
            brightness_coef = [0.4395, 0.5945, 0.2460, 0.3918, 0.3506, 0.2136]
            greenness_coef = [-0.4064, -0.5129, -0.2744, 0.5223, 0.3506, 0.2136]
            wetness_coef = [0.1147, 0.2489, 0.2408, 0.3132, -0.3122, -0.6416]
        else:
            raise ValueError("Capteur non supporté")

        n_bands = min(len(brightness_coef), self.image.shape[0])
        self.tc_components['brightness'] = np.zeros_like(self.image[0])
        self.tc_components['greenness'] = np.zeros_like(self.image[0])
        self.tc_components['wetness'] = np.zeros_like(self.image[0])

        for i in range(n_bands):
            band = self.image[i]
            mask = np.isnan(band) if np.isnan(self.nodata) else (band == self.nodata)
            self.tc_components['brightness'][~mask] += brightness_coef[i] * band[~mask]
            self.tc_components['greenness'][~mask] += greenness_coef[i] * band[~mask]
            self.tc_components['wetness'][~mask] += wetness_coef[i] * band[~mask]

    def calculate_ddi(self):
        brightness = self.tc_components['brightness']
        greenness = self.tc_components['greenness']
        denominator = brightness + greenness
        denominator[denominator == 0] = np.nan
        self.ddi = (brightness - greenness) / denominator

    def create_regular_grid(self):
        height, width = self.ddi.shape
        transform = self.profile['transform']
        self.grid_cells = []

        for y in range(0, height, self.cell_size):
            for x in range(0, width, self.cell_size):
                x_min = transform[2] + x * transform[0]
                y_max = transform[5] + y * transform[4]
                x_max = x_min + self.cell_size * transform[0]
                y_min = y_max + self.cell_size * transform[4]
                self.grid_cells.append(box(x_min, y_min, x_max, y_min + self.cell_size*transform[4]))

    def calculate_slope_per_cell(self):
        self.slope_grid = np.zeros(len(self.grid_cells))
        height, width = self.ddi.shape

        for i, cell in enumerate(self.grid_cells):
            col_off = int((cell.bounds[0] - self.profile['transform'][2]) / self.profile['transform'][0])
            row_off = int((cell.bounds[3] - self.profile['transform'][5]) / self.profile['transform'][4])
            win_cols = min(self.cell_size, width - col_off)
            win_rows = min(self.cell_size, height - row_off)

            if win_cols <= 0 or win_rows <= 0:
                self.slope_grid[i] = np.nan
                continue

            window = self.ddi[row_off:row_off+win_rows, col_off:col_off+win_cols]
            window = window[~np.isnan(window)]
            if len(window) > 1:
                X = np.arange(len(window)).reshape(-1, 1)
                y = window
                model = LinearRegression()
                model.fit(X, y)
                self.slope_grid[i] = model.coef_[0]
            else:
                self.slope_grid[i] = 0

    def classify_desertification(self):
        valid_slopes = self.slope_grid[~np.isnan(self.slope_grid)]
        if len(valid_slopes) > 0:
            jenks = NaturalBreaks(valid_slopes, k=5)
            classifications = jenks.yb
            self.classification = np.full_like(self.slope_grid, fill_value=0, dtype=int)
            valid_idx = np.where(~np.isnan(self.slope_grid))[0]
            for i, idx in enumerate(valid_idx):
                self.classification[idx] = classifications[i] + 1
        else:
            self.classification = np.zeros_like(self.slope_grid, dtype=int)

    def export_results(self, shapefile_path, raster_path):
        # Export shapefile
        gdf = gpd.GeoDataFrame({
            'slope': self.slope_grid,
            'class': self.classification,
            'geometry': self.grid_cells
        })
        gdf.crs = self.profile['crs']
        gdf.to_file(shapefile_path, driver='ESRI Shapefile')

        # Export raster
        classification_map = np.zeros_like(self.ddi, dtype=int)
        for i, cell in enumerate(self.grid_cells):
            col_off = int((cell.bounds[0] - self.profile['transform'][2]) / self.profile['transform'][0])
            row_off = int((cell.bounds[3] - self.profile['transform'][5]) / self.profile['transform'][4])
            win_cols = min(self.cell_size, classification_map.shape[1] - col_off)
            win_rows = min(self.cell_size, classification_map.shape[0] - row_off)
            classification_map[row_off:row_off+win_rows, col_off:col_off+win_cols] = self.classification[i]

        profile = self.profile.copy()
        profile.update(dtype=rasterio.int32, count=1, compress='lzw')
        with rasterio.open(raster_path, 'w', **profile) as dst:
            dst.write(classification_map, 1)

# ----------------------------
# Interface graphique Tkinter
# ----------------------------
class DesertGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Analyse de désertification")

        # Choix du raster
        tk.Label(self.root, text="Fichier raster:").grid(row=0, column=0, sticky="e")
        self.entry_raster = tk.Entry(self.root, width=50)
        self.entry_raster.grid(row=0, column=1)
        tk.Button(self.root, text="Parcourir", command=self.browse_raster).grid(row=0, column=2)

        # Type de capteur
        tk.Label(self.root, text="Type capteur:").grid(row=1, column=0, sticky="e")
        self.sensor_var = tk.StringVar(value="Landsat8")
        ttk.Combobox(self.root, textvariable=self.sensor_var, values=["Landsat8","Sentinel2","MODIS"]).grid(row=1, column=1)

        # Dossier de sortie
        tk.Label(self.root, text="Dossier résultats:").grid(row=2, column=0, sticky="e")
        self.entry_out = tk.Entry(self.root, width=50)
        self.entry_out.grid(row=2, column=1)
        tk.Button(self.root, text="Parcourir", command=self.browse_out).grid(row=2, column=2)

        # Bouton de lancement
        tk.Button(self.root, text="Lancer analyse", command=self.run_analysis, bg="green", fg="white").grid(row=3, column=1, pady=10)

        self.root.mainloop()

    def browse_raster(self):
        path = filedialog.askopenfilename(filetypes=[("TIFF files","*.tif")])
        if path:
            self.entry_raster.delete(0, tk.END)
            self.entry_raster.insert(0, path)

    def browse_out(self):
        path = filedialog.askdirectory()
        if path:
            self.entry_out.delete(0, tk.END)
            self.entry_out.insert(0, path)

    def run_analysis(self):
        raster_path = self.entry_raster.get()
        sensor = self.sensor_var.get()
        out_dir = self.entry_out.get()

        if not raster_path or not sensor or not out_dir:
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis")
            return

        try:
            shp_path = os.path.join(out_dir, "resultats.shp")
            tif_path = os.path.join(out_dir, "resultats.tif")

            analyzer = DesertificationAnalysis(raster_path, sensor)
            analyzer.load_image()
            analyzer.calculate_tasseled_cap()
            analyzer.calculate_ddi()
            analyzer.create_regular_grid()
            analyzer.calculate_slope_per_cell()
            analyzer.classify_desertification()
            analyzer.export_results(shapefile_path=shp_path, raster_path=tif_path)

            messagebox.showinfo("Terminé", f"Analyse terminée!\nShapefile: {shp_path}\nRaster: {tif_path}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue :\n{str(e)}")

# ----------------------------
# Lancement de l'interface
# ----------------------------
if __name__ == "__main__":
    DesertGUI()
