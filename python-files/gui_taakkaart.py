import os
import sys

# Fix for PyInstaller bundle
if getattr(sys, 'frozen', False):
    # Set PROJ and GDAL environment variables
    bundle_dir = sys._MEIPASS
    os.environ['PROJ_LIB'] = os.path.join(bundle_dir, 'proj')
    os.environ['GDAL_DATA'] = os.path.join(bundle_dir, 'gdal')
# gui_taakkaart.py - With progress indicator
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import zipfile
import os
import tempfile
import geopandas as gpd
from pyproj import CRS
import threading
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

WGS84_PRJ_CONTENT = CRS.from_epsg(4326).to_wkt()
REQUIRED_EXTENSIONS = {'.dbf', '.prj', '.shp', '.shx'}

class ProgressWindow(tk.Toplevel):
    """Modal progress window for long operations"""
    def __init__(self, parent, title="Processing", message="Please wait..."):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x100")
        self.transient(parent)
        self.grab_set()
        
        self.label = ttk.Label(self, text=message)
        self.label.pack(pady=10)
        
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill=tk.X, padx=20)
        self.progress.start(10)
        
        self.protocol("WM_DELETE_WINDOW", self.disable_close)
        
    def disable_close(self):
        """Prevent closing while processing"""
        pass
    
    def close(self):
        self.grab_release()
        self.destroy()

class ToolTip:
    """Custom tooltip class optimized for performance"""
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        self.text = ""

    def showtip(self, text, x, y):
        """Display text in tooltip window"""
        self.text = text
        if self.tip_window or not self.text:
            return
        x += 25
        y += 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"), wraplength=300)
        label.pack(ipadx=1)

    def hidetip(self):
        """Hide tooltip window"""
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

class ShapefileValidatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shapefile Validator")
        self.root.geometry("500x400")
        self.current_zip = None
        self.check_results = {}
        self.tooltips = {}
        self.cached_gdf = None
        self.cached_components = None
        self.progress_window = None
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        upload_frame = ttk.LabelFrame(main_frame, text="Upload Shapefile ZIP", padding="10")
        upload_frame.pack(fill=tk.X, pady=(0, 10))
        self.upload_btn = ttk.Button(upload_frame, text="Browse...", command=self.upload_file)
        self.upload_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.file_label = ttk.Label(upload_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        checks_frame = ttk.LabelFrame(main_frame, text="Validation Checks", padding="10")
        checks_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("check", "status", "message_indicator")
        self.tree = ttk.Treeview(checks_frame, columns=columns, show="headings", height=6)
        self.tree.column("check", width=120, anchor=tk.W)
        self.tree.column("status", width=80, anchor=tk.CENTER)
        self.tree.column("message_indicator", width=30, anchor=tk.CENTER)
        self.tree.heading("check", text="Check")
        self.tree.heading("status", text="Status")
        self.tree.heading("message_indicator", text="Uitleg")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree_tooltip = ToolTip(self.tree)
        self.tree.bind("<Motion>", self.on_tree_motion)
        self.tree.bind("<Leave>", self.on_tree_leave)

        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        self.fix_all_btn = ttk.Button(button_frame, text="Fix All Issues", 
                                     command=self.fix_all_issues, state=tk.DISABLED)
        self.fix_all_btn.pack(side=tk.RIGHT)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
        if file_path:
            self.current_zip = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.cached_gdf = None
            self.cached_components = None
            
            # Show progress window and run in thread
            self.progress_window = ProgressWindow(
                self.root, 
                message="Validating shapefile, this might take a while..."
            )
            threading.Thread(
                target=self.run_validation_threaded, 
                daemon=True
            ).start()

    def run_validation_threaded(self):
        """Run validation in separate thread"""
        try:
            self.run_validation()
        except Exception as e:
            logging.error(f"Validation failed: {e}")
            messagebox.showerror("Error", f"Validation failed: {str(e)}")
        finally:
            # Close progress window in main thread
            self.root.after(0, self.progress_window.close)

    def run_validation(self):
        """Actual validation logic"""
        if not self.current_zip:
            return

        # Clear previous results in GUI thread
        self.root.after(0, self.clear_results)
        
        # Run checks in optimized order
        checks = [
            ("ZIP File Validity", self.check_zip_validity),
            ("Required Files", self.check_required_files),
            ("WGS84 Projection", self.check_projection),
            ("Check rate 0", self.check_0_polygons),
            ("Geometry Types", self.check_geometries),
            ("Required Columns", self.check_columns)
        ]

        # Run all checks and update GUI
        for name, check_func in checks:
            status, message, fixable = check_func()
            self.root.after(0, self.add_check_result, name, status, message, fixable)
            
        self.root.after(0, self.update_fix_button_state)

    def clear_results(self):
        """Clear treeview results"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tooltips = {}
        self.check_results = {}

    def add_check_result(self, name, status, message, fix_function):
        """Add result to treeview (called from main thread)"""
        symbol = "✅" if status else "❌"
        msg_indicator = "❓" if message else ""

        item_id = self.tree.insert("", tk.END, values=(name, symbol, msg_indicator))
        self.check_results[item_id] = {
            "name": name,
            "status": status,
            "message": message,
            "fix_function": fix_function if not status else None
        }
        if message:
            self.tooltips[item_id] = message

    def update_fix_button_state(self):
        has_fixable = any(
            not result["status"] and result["fix_function"] 
            for result in self.check_results.values()
        )
        self.fix_all_btn.config(state=tk.NORMAL if has_fixable else tk.DISABLED)

    def fix_all_issues(self):
        """Start fix process with progress indicator"""
        self.progress_window = ProgressWindow(
            self.root, 
            message="Applying fixes, please wait..."
        )
        threading.Thread(
            target=self.fix_all_issues_threaded, 
            daemon=True
        ).start()

    def fix_all_issues_threaded(self):
        """Run fixes in background thread"""
        try:
            # Create temporary directory once for all fixes
            with tempfile.TemporaryDirectory() as tmpdir:
                # Extract once for all fixes
                with zipfile.ZipFile(self.current_zip, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
                
                # Apply fixes in optimal order
                for item_id in self.tree.get_children():
                    result = self.check_results.get(item_id)
                    if result and not result["status"] and result["fix_function"]:
                        result["fix_function"](tmpdir)
                
                # Create new zip after all fixes
                new_zip_path = self.get_fixed_zip_path()
                with zipfile.ZipFile(new_zip_path, 'w') as zip_out:
                    for root, _, files in os.walk(tmpdir):
                        for file in files:
                            zip_out.write(os.path.join(root, file), file)

                self.current_zip = new_zip_path
                self.root.after(0, messagebox.showinfo, 
                               "Fixes Applied", 
                               f"All fixes completed successfully. Using new ZIP: {os.path.basename(new_zip_path)}")
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Fix Failed", f"Error during fixes: {str(e)}")
        finally:
            # Clear cache and re-run validation
            self.cached_gdf = None
            self.cached_components = None
            self.root.after(0, self.progress_window.close)
            self.root.after(0, self.run_validation_threaded)

    def on_tree_motion(self, event):
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if row_id and col_id == "#3" and row_id in self.tooltips:
            self.tree_tooltip.showtip(self.tooltips[row_id], event.x_root, event.y_root)
        else:
            self.tree_tooltip.hidetip()

    def on_tree_leave(self, event):
        self.tree_tooltip.hidetip()

    def get_shapefile_components(self):
        """Cached component lookup"""
        if self.cached_components is None:
            with zipfile.ZipFile(self.current_zip, 'r') as zip_ref:
                self.cached_components = {
                    os.path.splitext(f)[1].lower(): f
                    for f in zip_ref.namelist() if not f.endswith('/')
                }
        return self.cached_components

    def get_geodataframe(self):
        """Cached GeoDataFrame access"""
        if self.cached_gdf is None:
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(self.current_zip, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
                shp_file = next(
                    (os.path.join(tmpdir, f) for f in os.listdir(tmpdir) 
                    if f.lower().endswith('.shp')), None
                )
                if shp_file:
                    self.cached_gdf = gpd.read_file(shp_file)
                else:
                    raise FileNotFoundError("No .shp file found in ZIP")
        return self.cached_gdf

    def check_zip_validity(self):
        try:
            valid = zipfile.is_zipfile(self.current_zip)
            return valid, "Valid ZIP file" if valid else "Invalid ZIP file", False
        except Exception as e:
            logging.error(f"Zip validity check failed: {e}")
            return False, f"Error: {str(e)}", False

    def check_required_files(self):
        try:
            file_map = self.get_shapefile_components()
            missing = REQUIRED_EXTENSIONS - set(file_map.keys())
            if not missing:
                return True, "All required files present", self.fix_required_files
            return False, f"Missing files: {', '.join(missing)}", self.fix_required_files
        except Exception as e:
            logging.error(f"Required files check failed: {e}")
            return False, f"Error: {str(e)}", self.fix_required_files

    def check_projection(self):
        try:
            file_map = self.get_shapefile_components()
            if '.prj' not in file_map:
                return False, ".prj file missing", self.fix_projection
            
            with zipfile.ZipFile(self.current_zip, 'r') as zip_ref:
                prj_content = zip_ref.read(file_map['.prj']).decode('utf-8').strip()
            
            if CRS.from_wkt(prj_content).to_epsg() == 4326:
                return True, "Projection is WGS84", False
            return False, "Projection is not WGS84", self.fix_projection
        except Exception as e:
            logging.error(f"Projection check failed: {e}")
            return False, f"Error: {str(e)}", self.fix_projection

    def check_0_polygons(self):
        try:
            gdf = self.get_geodataframe()

            # Case-insensitive 'rate' column lookup
            col_map = {col.lower(): col for col in gdf.columns}
            if "rate" not in col_map:
                return False, "Missing 'rate' column (case-insensitive)", False

            rate_col = col_map["rate"]

            # Check for features with Polygon or MultiPolygon geometry and rate == 0
            count = gdf[
                (gdf.geometry.type.isin(["Polygon", "MultiPolygon"])) & (gdf[rate_col] == 0)
            ].shape[0]

            return (
                count == 0,
                "No polygons or multipolygons with rate=0" if count == 0 else f"{count} feature(s) with rate=0 found",
                self.fix_0_polygons,
            )
        except Exception as e:
            logging.error(f"Rate check failed: {e}")
            return False, f"Error: {str(e)}", False




    def check_geometries(self):
        try:
            gdf = self.get_geodataframe()
            # Optimized multipart check
            multipart_count = sum(
                hasattr(geom, 'geoms') and len(geom.geoms) > 1
                for geom in gdf.geometry
            )
            return (multipart_count == 0,
                    "No multipart geometries" if multipart_count == 0 else f"{multipart_count} multipart geometries",
                    self.fix_geometries)
        except Exception as e:
            logging.error(f"Geometry check failed: {e}")
            return False, f"Error: {str(e)}", False

    def check_columns(self):
        try:
            gdf = self.get_geodataframe()
            required = {"rate"}
            missing = [col for col in required if col.lower() not in map(str.lower, gdf.columns)]
            return (not missing,
                    "All required columns present" if not missing else f"Missing columns: {', '.join(missing)}",
                    False)
        except Exception as e:
            logging.error(f"Column check failed: {e}")
            return False, f"Error: {str(e)}", False

    def get_fixed_zip_path(self):
        base_path, _ = os.path.splitext(self.current_zip)
        return f"{base_path}_fixed.zip"

    # FIX FUNCTIONS (optimized to use shared temp directory)
    def fix_required_files(self, tmpdir):
        try:
            # Find and rewrite shapefile
            shp_file = next(
                os.path.join(tmpdir, f) for f in os.listdir(tmpdir) 
                if f.lower().endswith('.shp')
            )
            if not shp_file:
                raise FileNotFoundError("No .shp file found")
            
            gdf = gpd.read_file(shp_file)
            gdf.to_file(shp_file)  # Rewrites all components
        except Exception as e:
            raise RuntimeError(f"Failed to fix files: {e}")

    def fix_projection(self, tmpdir):
        try:
            shp_file = next(
                os.path.join(tmpdir, f) for f in os.listdir(tmpdir) 
                if f.lower().endswith('.shp')
            )
            if not shp_file:
                raise FileNotFoundError("No .shp file found")
            
            gdf = gpd.read_file(shp_file)
            gdf = gdf.to_crs(epsg=4326)
            gdf.to_file(shp_file)
        except Exception as e:
            raise RuntimeError(f"Failed to fix projection: {e}")

    def fix_geometries(self, tmpdir):
        try:
            shp_file = next(
                os.path.join(tmpdir, f) for f in os.listdir(tmpdir) 
                if f.lower().endswith('.shp')
            )
            if not shp_file:
                raise FileNotFoundError("No .shp file found")
            
            gdf = gpd.read_file(shp_file)
            gdf = gdf.explode(index_parts=False)
            gdf.to_file(shp_file)
        except Exception as e:
            raise RuntimeError(f"Failed to fix geometries: {e}")

    def fix_0_polygons(self, tmpdir):
        try:
            shp_file = next(
                os.path.join(tmpdir, f) for f in os.listdir(tmpdir)
                if f.lower().endswith('.shp')
            )
            if not shp_file:
                raise FileNotFoundError("No .shp file found")

            gdf = gpd.read_file(shp_file)

            # Create case-insensitive column map
            col_map = {col.lower(): col for col in gdf.columns}
            if "rate" not in col_map:
                raise ValueError("Missing 'rate' column (case-insensitive)")

            rate_col = col_map["rate"]

            # Optimized removal of polygons with rate == 0
            original_count = len(gdf)
            gdf = gdf[~((gdf.geometry.type.isin(["Polygon", "MultiPolygon"])) & (gdf[rate_col] == 0))]
            removed_count = original_count - len(gdf)

            if removed_count > 0:
                gdf.to_file(shp_file)
        except Exception as e:
            raise RuntimeError(f"Failed to fix polygons: {e}")



if __name__ == '__main__':
    root = tk.Tk()
    app = ShapefileValidatorApp(root)
    root.mainloop()