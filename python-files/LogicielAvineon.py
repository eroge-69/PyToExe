import os
import time
import numpy as np
import laspy
import rasterio
from rasterio.transform import from_origin
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tqdm import tqdm
from scipy.ndimage import median_filter
from scipy.spatial import cKDTree
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from scipy.ndimage import label, binary_erosion, binary_dilation, binary_opening, binary_closing, binary_fill_holes

def calculate_optimal_resolution(x, y, max_resolution=0.025):
    area = (x.max() - x.min()) * (y.max() - y.min())
    avg_resolution = np.sqrt(area / len(x))
    return min(avg_resolution, max_resolution)

def fill_holes_with_progress(arr, desc="Filling holes"):
    height, width = arr.shape
    flat = arr.flatten()
    mask = flat == 0
    indices = np.where(mask)[0]

    for idx in tqdm(indices, desc=desc, unit='px'):
        i = idx // width
        j = idx % width
        neighbors = arr[max(0,i-1):i+2, max(0,j-1):j+2].flatten()
        nonzero = neighbors[neighbors != 0]
        if len(nonzero) > 0:
            arr[i,j] = nonzero.mean()
    return arr

def classify_vegetation_simple(r, g, b):
    """
    Classification ULTRA SIMPLE et PERMISSIVE :
    - Végétation = SEULEMENT les points très verts
    - Tout le reste (y compris poteaux orange) = NON-végétation avec priorité
    """
    print("🌿 Classification simple : végétation évidente vs tout le reste...")
    
    # Normalisation
    r_norm = r.astype(np.float32) / 65535.0
    g_norm = g.astype(np.float32) / 65535.0  
    b_norm = b.astype(np.float32) / 65535.0
    
    # Végétation = SEULEMENT couleur très verte ET dominante verte forte
    very_green = (g_norm > 0.5) & (g_norm > r_norm * 1.3) & (g_norm > b_norm * 1.3)
    
    # Statistiques
    print(f"🌿 Végétation évidente: {np.sum(very_green):,} ({100*np.sum(very_green)/len(r):.1f}%)")
    print(f"🏗️  Tout le reste (priorité): {np.sum(~very_green):,} ({100*np.sum(~very_green)/len(r):.1f}%)")
    
    return very_green

def estimate_ground_level_adaptive(x, y, z, grid_size=2.0, percentile=5):
    """Estimation du sol"""
    xmin, ymin, xmax, ymax = x.min(), y.min(), x.max(), y.max()
    nx = int(np.ceil((xmax - xmin) / grid_size))
    ny = int(np.ceil((ymax - ymin) / grid_size))
    
    ground_grid = np.full((ny, nx), np.nan)
    
    print(f"🔍 Analyse du sol par grille {nx}x{ny} (résolution {grid_size}m)...")
    
    for i in tqdm(range(nx), desc="Estimation du sol"):
        for j in range(ny):
            x1, x2 = xmin + i*grid_size, xmin + (i+1)*grid_size
            y1, y2 = ymin + j*grid_size, ymin + (j+1)*grid_size
            mask = (x >= x1) & (x < x2) & (y >= y1) & (y < y2)
            
            if np.sum(mask) > 3:
                z_cell = z[mask]
                ground_grid[j, i] = np.percentile(z_cell, percentile)
    
    # Interpolation
    from scipy.interpolate import griddata
    valid_mask = ~np.isnan(ground_grid)
    if np.sum(valid_mask) > 0:
        yi, xi = np.mgrid[0:ny, 0:nx]
        valid_points = np.column_stack([xi[valid_mask], yi[valid_mask]])
        valid_values = ground_grid[valid_mask]
        
        if len(valid_values) > 3:
            all_points = np.column_stack([xi.ravel(), yi.ravel()])
            interpolated = griddata(valid_points, valid_values, all_points, method='linear', fill_value=np.nanmedian(valid_values))
            ground_grid = interpolated.reshape((ny, nx))
    
    return ground_grid, xmin, ymin, grid_size

def get_local_ground_level(x_pt, y_pt, ground_grid, xmin, ymin, grid_size):
    """Obtient le niveau du sol local"""
    nx = ground_grid.shape[1]
    ny = ground_grid.shape[0]
    
    i = int((x_pt - xmin) / grid_size)
    j = int((y_pt - ymin) / grid_size)
    
    i = np.clip(i, 0, nx-1)
    j = np.clip(j, 0, ny-1)
    
    return ground_grid[j, i]

def create_raster_simple_priority(x, y, r, g, b, z, resolution, xmin, ymin, xmax, ymax, 
                                 output_file, crs, desc="Raster", ground_grid=None, 
                                 ground_params=None, height_range=None, vegetation_mask=None):
    """
    Logique TRÈS SIMPLE :
    - Si NON-végétation (poteaux, etc.) : PRIORITÉ ABSOLUE + limite très permissive
    - Si végétation : limite stricte
    """
    width = int(np.ceil((xmax - xmin) / resolution))
    height = int(np.ceil((ymax - ymin) / resolution))

    col = ((x - xmin) / resolution).astype(int)
    row = ((ymax - y) / resolution).astype(int)
    col = np.clip(col, 0, width - 1)
    row = np.clip(row, 0, height - 1)

    # Structures de données
    raster_r = np.zeros(height*width, dtype=np.float64)
    raster_g = np.zeros(height*width, dtype=np.float64)
    raster_b = np.zeros(height*width, dtype=np.float64)
    raster_z = np.full(height*width, -np.inf, dtype=np.float64)
    pixel_has_non_vegetation = np.zeros(height*width, dtype=bool)  # Track objets prioritaires
    pixel_count = np.zeros(height*width, dtype=np.int32)

    indices = row * width + col
    batch_size = max(len(indices)//100, 1)

    print(f"📊 Création du raster {width}x{height} (résolution: {resolution:.3f}m)")
    
    for i in tqdm(range(0, len(indices), batch_size), desc=desc, unit='pts'):
        batch_idx = indices[i:i+batch_size]
        batch_z = z[i:i+batch_size]
        batch_r = r[i:i+batch_size]
        batch_g = g[i:i+batch_size]
        batch_b = b[i:i+batch_size]
        batch_x = x[i:i+batch_size]
        batch_y = y[i:i+batch_size]
        batch_is_vegetation = vegetation_mask[i:i+batch_size] if vegetation_mask is not None else np.zeros(len(batch_idx), dtype=bool)
        
        for j, idx in enumerate(batch_idx):
            current_z = batch_z[j]
            is_vegetation = batch_is_vegetation[j]
            
            # Filtrage par hauteur
            if height_range is not None and ground_grid is not None:
                local_ground = get_local_ground_level(batch_x[j], batch_y[j], ground_grid, 
                                                    ground_params[0], ground_params[1], ground_params[2])
                height_above_ground = current_z - local_ground
                
                if is_vegetation:
                    # Végétation : limite stricte
                    if not (height_range[0] <= height_above_ground <= height_range[1]):
                        continue
                else:
                    # NON-végétation (poteaux, etc.) : très permissif
                    if height_above_ground < -1.0 or height_above_ground > 25.0:  # Très large pour poteaux
                        continue
            
            # Logique par pixel ULTRA SIMPLE
            if pixel_count[idx] == 0:
                # Premier point
                raster_z[idx] = current_z
                raster_r[idx] = batch_r[j]
                raster_g[idx] = batch_g[j]
                raster_b[idx] = batch_b[j]
                pixel_has_non_vegetation[idx] = not is_vegetation
                pixel_count[idx] = 1
            else:
                # Règle simple : NON-végétation gagne TOUJOURS
                should_replace = False
                
                if not is_vegetation and not pixel_has_non_vegetation[idx]:
                    # Non-végétation remplace végétation : OUI
                    should_replace = True
                elif not is_vegetation and pixel_has_non_vegetation[idx]:
                    # Entre non-végétation : le plus haut
                    should_replace = current_z > raster_z[idx]
                elif is_vegetation and not pixel_has_non_vegetation[idx]:
                    # Entre végétation : le plus haut
                    should_replace = current_z > raster_z[idx]
                # Végétation ne remplace JAMAIS non-végétation
                
                if should_replace:
                    raster_z[idx] = current_z
                    raster_r[idx] = batch_r[j]
                    raster_g[idx] = batch_g[j]
                    raster_b[idx] = batch_b[j]
                    pixel_has_non_vegetation[idx] = not is_vegetation
                
                pixel_count[idx] += 1

    # Finalisation
    raster_r = raster_r.reshape((height, width)).astype(np.uint16)
    raster_g = raster_g.reshape((height, width)).astype(np.uint16)
    raster_b = raster_b.reshape((height, width)).astype(np.uint16)
    pixel_count = pixel_count.reshape((height, width))
    pixel_has_non_vegetation = pixel_has_non_vegetation.reshape((height, width))

    print(f"📊 Pixels remplis : {np.sum(pixel_count > 0):,} / {height*width:,}")
    print(f"🏗️  Pixels avec objets prioritaires : {np.sum(pixel_has_non_vegetation):,}")

    # Remplissage des trous
    raster_r = fill_holes_with_progress(raster_r, desc="R channel")
    raster_g = fill_holes_with_progress(raster_g, desc="G channel")
    raster_b = fill_holes_with_progress(raster_b, desc="B channel")

    # Sauvegarde
    transform = from_origin(xmin, ymax, resolution, resolution)
    with rasterio.open(
        output_file, "w", driver="GTiff", height=height, width=width,
        count=3, dtype="uint16", crs=crs, transform=transform
    ) as dst:
        dst.write(raster_r, 1)
        dst.write(raster_g, 2)
        dst.write(raster_b, 3)

    print(f"✅ Fichier généré : {output_file}")

def create_raster_improved(x, y, r, g, b, z, resolution, xmin, ymin, xmax, ymax, 
                          output_file, crs, desc="Raster", ground_grid=None, 
                          ground_params=None, height_range=None):
    """Version originale pour comparaison"""
    width = int(np.ceil((xmax - xmin) / resolution))
    height = int(np.ceil((ymax - ymin) / resolution))

    col = ((x - xmin) / resolution).astype(int)
    row = ((ymax - y) / resolution).astype(int)
    col = np.clip(col, 0, width - 1)
    row = np.clip(row, 0, height - 1)

    raster_r = np.zeros(height*width, dtype=np.float64)
    raster_g = np.zeros(height*width, dtype=np.float64)
    raster_b = np.zeros(height*width, dtype=np.float64)
    raster_z = np.full(height*width, -np.inf, dtype=np.float64)
    pixel_count = np.zeros(height*width, dtype=np.int32)

    indices = row * width + col
    batch_size = max(len(indices)//100, 1)

    print(f"📊 Création du raster {width}x{height} (résolution: {resolution:.3f}m)")
    
    for i in tqdm(range(0, len(indices), batch_size), desc=desc, unit='pts'):
        batch_idx = indices[i:i+batch_size]
        batch_z = z[i:i+batch_size]
        batch_r = r[i:i+batch_size]
        batch_g = g[i:i+batch_size]
        batch_b = b[i:i+batch_size]
        batch_x = x[i:i+batch_size]
        batch_y = y[i:i+batch_size]
        
        for j, idx in enumerate(batch_idx):
            current_z = batch_z[j]
            
            if height_range is not None and ground_grid is not None:
                local_ground = get_local_ground_level(batch_x[j], batch_y[j], ground_grid, 
                                                    ground_params[0], ground_params[1], ground_params[2])
                height_above_ground = current_z - local_ground
                
                if not (height_range[0] <= height_above_ground <= height_range[1]):
                    continue
            
            if pixel_count[idx] == 0:
                raster_z[idx] = current_z
                raster_r[idx] = batch_r[j]
                raster_g[idx] = batch_g[j]
                raster_b[idx] = batch_b[j]
                pixel_count[idx] = 1
            else:
                if current_z > raster_z[idx]:
                    raster_z[idx] = current_z
                    raster_r[idx] = batch_r[j]
                    raster_g[idx] = batch_g[j]
                    raster_b[idx] = batch_b[j]
                pixel_count[idx] += 1

    raster_r = raster_r.reshape((height, width)).astype(np.uint16)
    raster_g = raster_g.reshape((height, width)).astype(np.uint16)
    raster_b = raster_b.reshape((height, width)).astype(np.uint16)

    print(f"📊 Pixels remplis : {np.sum(pixel_count > 0):,} / {height*width:,}")

    raster_r = fill_holes_with_progress(raster_r, desc="R channel")
    raster_g = fill_holes_with_progress(raster_g, desc="G channel")
    raster_b = fill_holes_with_progress(raster_b, desc="B channel")

    transform = from_origin(xmin, ymax, resolution, resolution)
    with rasterio.open(
        output_file, "w", driver="GTiff", height=height, width=width,
        count=3, dtype="uint16", crs=crs, transform=transform
    ) as dst:
        dst.write(raster_r, 1)
        dst.write(raster_g, 2)
        dst.write(raster_b, 3)

    print(f"✅ Fichier généré : {output_file}")

def process_las_file(input_file, output_dir, export_options):
    """Traitement d'un fichier LAS avec options d'export configurables"""
    print(f"\n🔄 Traitement : {os.path.basename(input_file)}")
    
    try:
        las = laspy.read(input_file)
        x, y, z = las.x, las.y, las.z
        r, g, b = las.red, las.green, las.blue

        if r is None or g is None or b is None:
            raise ValueError(f"{input_file} ne contient pas de couleurs RGB.")

        resolution = calculate_optimal_resolution(x, y, max_resolution=0.025)
        xmin, ymin, xmax, ymax = x.min(), y.min(), x.max(), y.max()
        crs = las.header.parse_crs() if las.header.parse_crs() else None
        base_name = os.path.splitext(os.path.basename(input_file))[0]

        print(f"📊 Points totaux : {len(z):,}")
        print(f"📊 Résolution calculée : {resolution:.3f}m")
        print(f"📊 Zone : {xmax-xmin:.1f}m x {ymax-ymin:.1f}m")

        # Classification simple (toujours nécessaire)
        vegetation_mask = classify_vegetation_simple(r, g, b)
        
        # Estimation du sol si nécessaire
        ground_grid = None
        ground_params = None
        if any(opt in export_options for opt in ['seuil_strict', 'poteaux_visibles']):
            print(f"\n🔄 Estimation du terrain...")
            ground_grid, grid_xmin, grid_ymin, grid_size = estimate_ground_level_adaptive(x, y, z, 
                                                                                          grid_size=2.0, percentile=3)
            ground_params = (grid_xmin, grid_ymin, grid_size)
        
        # Exports selon les options choisies
        if 'sans_seuil' in export_options:
            out_no_limit = os.path.join(output_dir, base_name + "_ortho_sans_seuil.tif")
            print(f"\n🔄 Version SANS seuil")
            create_raster_simple_priority(x, y, r, g, b, z, resolution, xmin, ymin, xmax, ymax, 
                                         out_no_limit, crs, desc="Sans seuil", vegetation_mask=vegetation_mask)

        if 'seuil_strict' in export_options:
            height_range = (-0.5, 1.5)
            out_original = os.path.join(output_dir, base_name + "_ortho_seuil_strict_1m5.tif")
            print(f"\n🔄 Version seuil strict (1.5m pour tout)")
            
            create_raster_improved(x, y, r, g, b, z, resolution, xmin, ymin, xmax, ymax,
                                  out_original, crs, desc="Seuil strict 1.5m",
                                  ground_grid=ground_grid, ground_params=ground_params,
                                  height_range=height_range)

        if 'poteaux_visibles' in export_options:
            height_range = (-0.5, 1.5)
            poteaux_visibles_file = os.path.join(output_dir, base_name + "_ortho_POTEAUX_VISIBLES.tif")
            print(f"\n🔄 Version POTEAUX VISIBLES (priorité absolue aux objets)")
            print(f"    ➡️ Végétation évidente: limite stricte 1.5m")
            print(f"    ➡️ Tout le reste (poteaux, etc.): limite très permissive 25m")
            
            create_raster_simple_priority(x, y, r, g, b, z, resolution, xmin, ymin, xmax, ymax,
                                         poteaux_visibles_file, crs, desc="POTEAUX VISIBLES",
                                         ground_grid=ground_grid, ground_params=ground_params,
                                         height_range=height_range, vegetation_mask=vegetation_mask)

        print(f"✅ Traitement terminé pour {base_name}")
        
    except Exception as e:
        print(f"❌ Erreur lors du traitement de {input_file}: {str(e)}")

class FileWatcher(FileSystemEventHandler):
    """Surveillance du dossier d'entrée pour traitement automatique"""
    
    def __init__(self, output_dir, export_options, callback=None):
        self.output_dir = output_dir
        self.export_options = export_options
        self.callback = callback
        super().__init__()
    
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            if file_path.lower().endswith(('.las', '.laz')):
                print(f"\n🆕 Nouveau fichier détecté: {os.path.basename(file_path)}")
                if self.callback:
                    self.callback(f"Traitement automatique: {os.path.basename(file_path)}")
                
                # Attendre que le fichier soit complètement copié
                time.sleep(2)
                
                # Lancer le traitement
                threading.Thread(target=process_las_file, 
                               args=(file_path, self.output_dir, self.export_options)).start()

class LiDARProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Processeur LiDAR")
        self.root.geometry("800x600")
        
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.auto_process = tk.BooleanVar()
        
        # Variables pour les options d'export
        self.export_complet = tk.BooleanVar(value=True)
        self.export_sans_seuil = tk.BooleanVar()
        self.export_seuil_strict = tk.BooleanVar()
        self.export_poteaux_visibles = tk.BooleanVar()
        
        self.watcher = None
        self.observer = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Titre
        title_frame = ttk.Frame(self.root)
        title_frame.pack(pady=10, padx=20, fill='x')
        
        title_label = ttk.Label(title_frame, text="🛰️ Processeur LiDAR", 
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        # Sélection des dossiers
        dirs_frame = ttk.LabelFrame(self.root, text="📁 Dossiers", padding=10)
        dirs_frame.pack(pady=10, padx=20, fill='x')
        
        # Dossier d'entrée
        ttk.Label(dirs_frame, text="Dossier d'entrée (fichiers LAS/LAZ):").pack(anchor='w')
        input_frame = ttk.Frame(dirs_frame)
        input_frame.pack(fill='x', pady=5)
        
        ttk.Entry(input_frame, textvariable=self.input_dir, state='readonly').pack(side='left', fill='x', expand=True)
        ttk.Button(input_frame, text="Parcourir", command=self.select_input_dir).pack(side='right', padx=(5,0))
        
        # Dossier de sortie
        ttk.Label(dirs_frame, text="Dossier de sortie:").pack(anchor='w', pady=(10,0))
        output_frame = ttk.Frame(dirs_frame)
        output_frame.pack(fill='x', pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_dir, state='readonly').pack(side='left', fill='x', expand=True)
        ttk.Button(output_frame, text="Parcourir", command=self.select_output_dir).pack(side='right', padx=(5,0))
        
        # Options d'export
        export_frame = ttk.LabelFrame(self.root, text="📋 Options d'export", padding=10)
        export_frame.pack(pady=10, padx=20, fill='x')
        
        # Export complet
        ttk.Checkbutton(export_frame, text="🎯 Export complet (3 TIFFs)", 
                       variable=self.export_complet, command=self.on_export_complet_change).pack(anchor='w', pady=2)
        
        # Séparateur
        ttk.Separator(export_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Exports spécifiques
        ttk.Label(export_frame, text="Ou sélectionner des exports spécifiques:", font=('Arial', 10, 'bold')).pack(anchor='w')
        
        ttk.Checkbutton(export_frame, text="🌍 Ortho sans seuil (tous les points)", 
                       variable=self.export_sans_seuil).pack(anchor='w', pady=2, padx=20)
        
        ttk.Checkbutton(export_frame, text="✂️ Ortho seuil strict (1.5m pour tout)", 
                       variable=self.export_seuil_strict).pack(anchor='w', pady=2, padx=20)
        
        ttk.Checkbutton(export_frame, text="🏗️ Ortho poteaux visibles (priorité objets)", 
                       variable=self.export_poteaux_visibles).pack(anchor='w', pady=2, padx=20)
        
        # Traitement automatique
        auto_frame = ttk.LabelFrame(self.root, text="⚡ Traitement automatique", padding=10)
        auto_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Checkbutton(auto_frame, text="🔄 Surveiller le dossier d'entrée et traiter automatiquement les nouveaux fichiers", 
                       variable=self.auto_process, command=self.toggle_auto_process).pack(anchor='w')
        
        auto_info = ttk.Label(auto_frame, text="ℹ️ Quand activé, tout nouveau fichier .las/.laz dans le dossier d'entrée sera traité automatiquement", 
                             foreground='gray')
        auto_info.pack(anchor='w', pady=(5,0))
        
        # Boutons de contrôle
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=20, padx=20, fill='x')
        
        ttk.Button(control_frame, text="▶️ Traiter les fichiers existants", 
                  command=self.process_existing_files).pack(side='left', padx=(0,10))
        
        ttk.Button(control_frame, text="🛑 Arrêter surveillance", 
                  command=self.stop_auto_process).pack(side='left', padx=(0,10))
        
        ttk.Button(control_frame, text="❌ Quitter", 
                  command=self.root.quit).pack(side='right')
        
        # Zone de statut
        status_frame = ttk.LabelFrame(self.root, text="📊 Statut", padding=10)
        status_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.status_text = tk.Text(status_frame, height=8, wrap='word')
        scrollbar = ttk.Scrollbar(status_frame, orient='vertical', command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.log_message("🚀 Application démarrée")
        self.log_message("📁 Sélectionnez les dossiers d'entrée et de sortie.")
    
    def on_export_complet_change(self):
        """Gestion de la checkbox export complet"""
        if self.export_complet.get():
            # Désactiver les exports spécifiques
            self.export_sans_seuil.set(False)
            self.export_seuil_strict.set(False)
            self.export_poteaux_visibles.set(False)
    
    def select_input_dir(self):
        """Sélection du dossier d'entrée"""
        directory = filedialog.askdirectory(title="Sélectionner le dossier d'entrée (fichiers LAS/LAZ)")
        if directory:
            self.input_dir.set(directory)
            self.log_message(f"📁 Dossier d'entrée: {directory}")
            
            # Compter les fichiers existants
            las_files = [f for f in os.listdir(directory) if f.lower().endswith(('.las', '.laz'))]
            self.log_message(f"📁 {len(las_files)} fichier(s) LAS/LAZ trouvé(s)")
    
    def select_output_dir(self):
        """Sélection du dossier de sortie"""
        directory = filedialog.askdirectory(title="Sélectionner le dossier de sortie")
        if directory:
            self.output_dir.set(directory)
            self.log_message(f"📁 Dossier de sortie: {directory}")
    
    def get_export_options(self):
        """Récupère les options d'export sélectionnées"""
        if self.export_complet.get():
            return ['sans_seuil', 'seuil_strict', 'poteaux_visibles']
        
        options = []
        if self.export_sans_seuil.get():
            options.append('sans_seuil')
        if self.export_seuil_strict.get():
            options.append('seuil_strict')
        if self.export_poteaux_visibles.get():
            options.append('poteaux_visibles')
        
        return options
    
    def log_message(self, message):
        """Ajoute un message au log avec horodatage"""
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        self.status_text.insert(tk.END, full_message)
        self.status_text.see(tk.END)
        self.root.update()
    
    def validate_inputs(self):
        """Validation des entrées utilisateur"""
        if not self.input_dir.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier d'entrée")
            return False
        
        if not self.output_dir.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de sortie")
            return False
        
        if not os.path.exists(self.input_dir.get()):
            messagebox.showerror("Erreur", "Le dossier d'entrée n'existe pas")
            return False
        
        if not os.path.exists(self.output_dir.get()):
            messagebox.showerror("Erreur", "Le dossier de sortie n'existe pas")
            return False
        
        export_options = self.get_export_options()
        if not export_options:
            messagebox.showerror("Erreur", "Veuillez sélectionner au moins une option d'export")
            return False
        
        return True
    
    def process_existing_files(self):
        """Traite tous les fichiers existants dans le dossier d'entrée"""
        if not self.validate_inputs():
            return
        
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        export_options = self.get_export_options()
        
        # Trouver tous les fichiers LAS/LAZ
        las_files = []
        for file in os.listdir(input_dir):
            if file.lower().endswith(('.las', '.laz')):
                las_files.append(os.path.join(input_dir, file))
        
        if not las_files:
            messagebox.showinfo("Info", "Aucun fichier LAS/LAZ trouvé dans le dossier d'entrée")
            return
        
        self.log_message(f"Démarrage du traitement de {len(las_files)} fichier(s)")
        self.log_message(f"Options d'export: {', '.join(export_options)}")
        
        # Traitement en thread séparé pour ne pas bloquer l'interface
        def process_thread():
            for las_file in las_files:
                try:
                    self.log_message(f"Traitement: {os.path.basename(las_file)}")
                    process_las_file(las_file, output_dir, export_options)
                    self.log_message(f"Terminé: {os.path.basename(las_file)}")
                except Exception as e:
                    self.log_message(f"Erreur {os.path.basename(las_file)}: {str(e)}")
            
            self.log_message("Traitement de tous les fichiers terminé!")
        
        threading.Thread(target=process_thread, daemon=True).start()
    
    def toggle_auto_process(self):
        """Active/désactive le traitement automatique"""
        if self.auto_process.get():
            self.start_auto_process()
        else:
            self.stop_auto_process()
    
    def start_auto_process(self):
        """Démarre la surveillance automatique"""
        if not self.validate_inputs():
            self.auto_process.set(False)
            return
        
        if self.observer:
            self.stop_auto_process()
        
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        export_options = self.get_export_options()
        
        self.watcher = FileWatcher(output_dir, export_options, self.log_message)
        self.observer = Observer()
        self.observer.schedule(self.watcher, input_dir, recursive=False)
        self.observer.start()
        
        self.log_message(f"Surveillance automatique activée sur: {input_dir}")
        self.log_message(f"Options: {', '.join(export_options)}")
    
    def stop_auto_process(self):
        """Arrête la surveillance automatique"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.watcher = None
            self.log_message("Surveillance automatique arrêtée")
        
        self.auto_process.set(False)

def main():
    """Point d'entrée principal avec interface graphique"""
    root = tk.Tk()
    app = LiDARProcessorGUI(root)
    
    # Gestion de la fermeture
    def on_closing():
        if app.observer:
            app.stop_auto_process()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    # Vérifier les dépendances
    try:
        import sklearn
        import watchdog
        import skimage
    except ImportError as e:
        print(f"Dépendance manquante: {e}")
        print("\nInstallez les dépendances avec:")
        print("pip install scikit-learn watchdog scikit-image")
        exit(1)
    
    main()