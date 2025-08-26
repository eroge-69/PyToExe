
import sys
import math
import numpy as np
import traceback

import pyvista as pv
from pyvistaqt import QtInteractor

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QFileDialog, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFormLayout,
    QCheckBox, QSpinBox, QTextEdit, QDockWidget, QGroupBox, QWidget, QRadioButton,
    QToolBar, QAction, QStyle, QStatusBar, QShortcut
)
from PyQt5.QtGui import  QKeySequence, QFont
from PyQt5.QtCore import Qt,QTimer
from PyQt5 import QtCore  # for QSize in toolbar

from scipy.spatial import ConvexHull, cKDTree
from matplotlib.path import Path

# Optional acceleration
try:
    import cupy as cp
    CUPY_AVAILABLE = True
except Exception:
    cp = np
    CUPY_AVAILABLE = False

# Optional boolean / mesh ops (not required)
try:
    import trimesh
    TRIMESH_AVAILABLE = True
except Exception:
    trimesh = None
    TRIMESH_AVAILABLE = False

# Optional ICP alignment
try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except Exception:
    OPEN3D_AVAILABLE = False

VTK_HEXAHEDRON = 12

# ---- Performance knobs ----
MAX_PASS_POINTS_PER_COLOR = 60000   # subsample pass point clouds per color
MAX_FACET_LABELS = 120              # cap clickable labels (VTK text is heavy)
DECIMATE_TARGET_CELLS = 200_000     # display-only mesh budget
RESET_CAMERA_ONCE_AFTER_LOAD = True # avoid frequent camera resets

# ---- Production knobs: removal rates & overheads ----
MRR_COARSE = 150.0   # mm^3/min
MRR_MEDIUM = 80.0
MRR_FINE   = 30.0
SETUP_PENALTY_SEC = 10.0  # setup overhead per facet per pass

# ---- Robust facet extraction defaults ----
DEFAULT_GIRDLE_TOL_FRAC = 0.02005  # 0.4% of mesh diagonal (scale-aware)
MAX_AUTO_RETRIES = 3
SCALE_TO_MM = 1.0

def fmt_mm(x: float) -> str:
    try: return f"{float(x):.3f} mm"
    except Exception: return "0.000 mm"

def fmt_mm2(x: float) -> str:
    try: return f"{float(x):.3f} mm²"
    except Exception: return "0.000 mm²"

def fmt_mm3(x: float) -> str:
    try: return f"{float(x):.3f} mm³"
    except Exception: return "0.000 mm³"

# ---- Polished facet classification knobs ----
POLISH_CLASS_PARAMS = {
    # Crown thresholds (existing)
    "crown_star_frac": 0.65,
    "crown_upper_frac": 0.35,
    "star_area_q": 0.35,

    # Pavilion thresholds (existing)
    "pav_lower_frac": 0.35,

    # Arrow direction (existing)
    "arrow_dir_deg": 25.0,

    # --- NEW: Table / Culet detection ---
    "table_frac": 0.85,        # crown height fraction near table
    "culet_frac": 0.90,        # pavilion depth fraction near culet (if present)
    "parallel_tol": 0.97,      # |dot(n, ±ng)| >= this => nearly parallel
    "center_tol": 0.22,        # <= this => near center
    "culet_area_q": 0.30,      # bottom 30% of pavilion areas
}


def _extract_feature_edges(mesh,
                            angle_deg=30.0,
                            feature_edges=True,
                            boundary_edges=False,
                            non_manifold_edges=True,
                            manifold_edges=False):
        """
        Version-safe wrapper for PyVista's extract_feature_edges.
        Newer PyVista:   extract_feature_edges(angle=...)
        Older PyVista:   extract_feature_edges(feature_angle=...)
        """
        try:
            # Newer API (>= ~0.43)
            return mesh.extract_feature_edges(
                angle=float(angle_deg),
                feature_edges=bool(feature_edges),
                boundary_edges=bool(boundary_edges),
                non_manifold_edges=bool(non_manifold_edges),
                manifold_edges=bool(manifold_edges),
            )
        except TypeError:
            # Older API
            return mesh.extract_feature_edges(
                feature_angle=float(angle_deg),
                feature_edges=bool(feature_edges),
                boundary_edges=bool(boundary_edges),
                non_manifold_edges=bool(non_manifold_edges),
                manifold_edges=bool(manifold_edges),
            )
def build_azimuth_cell_scalars(mesh: pv.PolyData, facets, scalar_name='AzimuthDeg'):
        """
        Create per-cell azimuth scalars (0..360) on a *copy* of mesh
        using facet['faces_idx'] (cell indices). Girdle cells are left as NaN.
        """
        if mesh is None or not facets:
            return mesh, scalar_name
        mcopy = mesh.copy(deep=True)
        n_cells = int(mcopy.n_cells)
        scalars = np.full((n_cells,), np.nan, dtype=float)

        for f in facets:
            az = f.get('azimuth_deg', None)
            if az is None:
                continue
            cids = f.get('faces_idx') or []
            for cid in cids:
                ic = int(cid)
                if 0 <= ic < n_cells:
                    scalars[ic] = az

        mcopy.cell_data.set_array(scalars, scalar_name)
        return mcopy, scalar_name

def _mesh_diag(mesh) -> float:
    """Bounding-box diagonal used to scale tolerances."""
    b = np.array(mesh.bounds, dtype=float).reshape(3, 2)
    return float(np.linalg.norm(b[:, 1] - b[:, 0]))


# -------- Modern theme (Dark/Light) + helpers --------
class ModernTheme:
    DARK_QSS = """
    /* base */
    QWidget {
        background-color: #0d1117;
        color: #d0d7de;
        font-family: "Segoe UI", "Inter", Arial, sans-serif;
        font-size: 10.5pt;
    }
    QDockWidget {
        titlebar-close-icon: none; titlebar-normal-icon: none;
        font-weight: 600;
        border: 1px solid #30363d; border-radius: 10px;
        background: #0d1117;
    }
    QDockWidget::title {
        text-transform: uppercase;
        background: #161b22;
        padding: 6px 10px;
        border-bottom: 1px solid #30363d;
    }
    QScrollArea, QGroupBox, QFrame {
        background: #0f141b;
    }
    QGroupBox {
        margin-top: 12px;
        border: 1px solid #30363d; border-radius: 10px;
        padding: 10px; 
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px; padding: 0 4px;
        color: #8b949e; font-weight: 600; text-transform: uppercase;
    }
    QLabel { color: #c9d1d9; }
    QToolBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0d1117, stop:1 #0f141b);
        border-bottom: 1px solid #30363d;
        spacing: 6px;
    }
    QStatusBar {
        background: #0f141b; color: #8b949e; border-top: 1px solid #30363d;
    }
    QToolButton, QPushButton {
        background: #1b2230;
        border: 1px solid #30363d;
        border-radius: 8px; padding: 6px 10px;
    }
    QToolButton:hover, QPushButton:hover {
        background: #1f6feb22; border: 1px solid #1f6feb77;
    }
    QToolButton:pressed, QPushButton:pressed {
        background: #1f6feb44; border: 1px solid #1f6febaa;
    }
    QCheckBox, QRadioButton { spacing: 8px; }
    QSpinBox, QComboBox, QLineEdit, QTextEdit, QPlainTextEdit {
        background: #0f1622; color: #d0d7de;
        border: 1px solid #30363d; border-radius: 8px; padding: 4px 8px;
        selection-background-color: #1f6feb; selection-color: #ffffff;
    }
    QSpinBox::up-button, QSpinBox::down-button {
        background: #182033; border: none; width: 18px;
        border-left: 1px solid #30363d;
    }
    QTabWidget::pane { border: 1px solid #30363d; }
    QTabBar::tab {
        background: #0f141b; border: 1px solid #30363d; border-bottom: none;
        padding: 6px 10px; margin-right: 2px;
        border-top-left-radius: 8px; border-top-right-radius: 8px;
    }
    QTabBar::tab:selected { background: #141b22; border-bottom: 1px solid #141b22; }
    """

    LIGHT_QSS = """
    QWidget { background: #f7f7fa; color: #202124; font-family: "Segoe UI", Arial; font-size: 10.5pt; }
    QDockWidget { background: #ffffff; border: 1px solid #e4e6ef; border-radius: 10px; }
    QDockWidget::title { background: #f1f3f9; padding: 6px 10px; }
    QGroupBox { background: #ffffff; border: 1px solid #e4e6ef; border-radius: 10px; padding: 10px; }
    QGroupBox::title { color: #5f6368; font-weight: 600; text-transform: uppercase; left: 12px; }
    QToolBar { background: #ffffff; border-bottom: 1px solid #e4e6ef; }
    QStatusBar { background: #ffffff; color: #5f6368; border-top: 1px solid #e4e6ef; }
    QPushButton, QToolButton { background: #ffffff; border: 1px solid #e4e6ef; border-radius: 8px; padding: 6px 10px; }
    QPushButton:hover, QToolButton:hover { background: #f3f6ff; border: 1px solid #90c2ff; }
    QSpinBox, QComboBox, QLineEdit, QTextEdit, QPlainTextEdit {
        background: #ffffff; color: #202124; border: 1px solid #d7dae0; border-radius: 8px; padding: 4px 8px;
        selection-background-color: #1967d2; selection-color: #ffffff;
    }
    """

# ---------------- Utilities ----------------
def to_cp(x):
    if CUPY_AVAILABLE:
        return cp.asarray(x)
    return np.asarray(x)

def to_np(x):
    if CUPY_AVAILABLE and isinstance(x, cp.ndarray):
        return cp.asnumpy(x)
    return np.asarray(x)

def _norm(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / (n + 1e-18)

# --- Azimuth helpers (relative to Table facet; 0..360 around girdle plane) ---

def _project_to_plane(v: np.ndarray, n: np.ndarray) -> np.ndarray:
    n = np.asarray(n, float)
    v = np.asarray(v, float)
    return v - np.dot(v, n) * n

def _signed_angle_deg_on_plane(u: np.ndarray, v: np.ndarray, plane_normal: np.ndarray) -> float:
    """Angle from u -> v around plane_normal (RH rule), returned in [0,360)."""
    u = np.asarray(u, float); v = np.asarray(v, float); n = np.asarray(plane_normal, float)
    # Normalize
    u = u / (np.linalg.norm(u) + 1e-18)
    v = v / (np.linalg.norm(v) + 1e-18)
    n = n / (np.linalg.norm(n) + 1e-18)
    dotp = float(np.clip(np.dot(u, v), -1.0, 1.0))
    ang = math.degrees(math.acos(dotp))
    s = float(np.dot(np.cross(u, v), n))
    if s < 0:
        ang = 360.0 - ang
    if ang >= 360.0: ang -= 360.0
    if ang < 0.0: ang += 360.0
    return ang

def _principal_plane_normal(points: np.ndarray) -> np.ndarray:
    """PCA: return eigenvector with smallest variance as plane normal."""
    P = np.asarray(points, float)
    if P.ndim != 2 or P.shape[0] < 3:
        return np.array([0.0, 0.0, 1.0], float)
    P0 = P - P.mean(axis=0)
    C = np.cov(P0.T)
    w, V = np.linalg.eigh(C)
    n = V[:, int(np.argmin(w))]
    n = n / (np.linalg.norm(n) + 1e-18)
    return n

def _pick_table_facet(facets):
    # Prefer explicit 'Table' label; fallback to largest area facet
    cand = [f for f in facets if str(f.get('facet_type','')).lower() == 'table']
    if cand:
        return cand[0]
    if not facets:
        return None
    return max(facets, key=lambda x: float(x.get('footprint_area', 0.0)))

def _compute_girdle_plane_from_facets(facets):
    """Return (girdle_normal, girdle_centroid) or safe defaults if unavailable."""
    try:
        facets = facets or []
        # Prefer explicit girdle facets
        girdles = [f for f in facets if str(f.get('facet_type','')).lower() == 'girdle']
        if girdles:
            ng = np.mean([np.asarray(f['normal'], float)   for f in girdles], axis=0)
            cg = np.mean([np.asarray(f['centroid'], float) for f in girdles], axis=0)
            ng = ng / (np.linalg.norm(ng) + 1e-18)
            return ng, cg

        # Otherwise, estimate from all facet centroids (need >=3)
        C = np.array([np.asarray(f['centroid'], float) for f in facets], float)
        if C.ndim == 2 and C.shape[0] >= 3:
            return _principal_plane_normal(C), C.mean(axis=0)

        # Last resort: safe defaults (avoid NaNs/warnings)
        return np.array([0.0, 0.0, 1.0], float), np.zeros(3, float)
    except Exception:
        # Always return valid numbers
        return np.array([0.0, 0.0, 1.0], float), np.zeros(3, float)


def compute_facet_azimuth_single(facet, table_normal, girdle_normal, girdle_centroid):
    """
    Return azimuth in degrees [0,360) for 'facet' relative to TABLE reference axis.
    Reference axis = projection of TABLE normal into girdle plane.
    Angle is measured around 'girdle_normal' and based on the projected centroid vector.
    """
    ng = np.asarray(girdle_normal, float); ng = ng / (np.linalg.norm(ng) + 1e-18)
    # Reference axis (Table normal projected into girdle plane)
    ref = _project_to_plane(np.asarray(table_normal, float), ng)
    if np.linalg.norm(ref) < 1e-14:
        # Rarely, table normal ~ parallel to girdle normal; build a stable axis
        t = np.array([1.0, 0.0, 0.0])
        if abs(np.dot(t, ng)) > 0.95: t = np.array([0.0, 1.0, 0.0])
        ref = _project_to_plane(t, ng)
    ref /= (np.linalg.norm(ref) + 1e-18)

    # Target direction = centroid vector projected to girdle plane
    vec = np.asarray(facet['centroid'], float) - np.asarray(girdle_centroid, float)
    vecp = _project_to_plane(vec, ng)
    if np.linalg.norm(vecp) < 1e-14:
        return 0.0
    return _signed_angle_deg_on_plane(ref, vecp, ng)

def annotate_facets_with_azimuth(facets, cg=None, ng=None, table_facet=None):
    if not facets:
        return facets

    if table_facet is None:
        table_facet = _pick_table_facet(facets)
    if table_facet is None:
        for f in facets: f['azimuth_deg'] = None
        return facets

    if cg is None or ng is None:
        ng, cg = _compute_girdle_plane_from_facets(facets)

    # Guard against NaNs/Infs
    if (not np.all(np.isfinite(ng))) or (not np.all(np.isfinite(cg))):
        for f in facets: f['azimuth_deg'] = None
        return facets

    tnorm = np.asarray(table_facet['normal'], float)
    tnorm = tnorm / (np.linalg.norm(tnorm) + 1e-18)

    for f in facets:
        try:
            f['azimuth_deg'] = float(compute_facet_azimuth_single(f, tnorm, ng, cg))
        except Exception:
            f['azimuth_deg'] = None
    return facets



def decimate_for_view(poly, target_cells=DECIMATE_TARGET_CELLS):
    """Return a lighter copy for display; keep original for computation."""
    try:
        pd = poly.triangulate().clean()
        if pd.n_cells > target_cells:
            ratio = 1.0 - float(target_cells) / float(pd.n_cells)
            dec = pd.decimate_proportion(
                ratio, preserve_topology=True, target_reduction=ratio
            ).clean()
            return dec if dec.n_cells > 0 else pd
        return pd
    except Exception:
        return poly

def _fit_plane_svd(points):
    """
    Least-squares plane fit using SVD.
    Returns (centroid, normal), where normal is unit-length.
    """
    P = np.asarray(points, dtype=float)
    c = P.mean(axis=0)
    U, S, VT = np.linalg.svd(P - c, full_matrices=False)
    n = VT[-1, :]
    n = _norm(n)
    if n[2] < 0:
        n = -n
    return c, n

def _fit_plane_ransac(points, n_iter=300, inlier_tol=0.02, min_inliers_ratio=0.6, random_state=42):
    rng = np.random.default_rng(random_state)
    P = np.asarray(points, dtype=float)
    N = P.shape[0]
    if N < 3:
        c, n = _fit_plane_svd(P)
        return c, n, np.ones(N, dtype=bool)

    best_inliers = None
    best_count = -1
    indices = np.arange(N)

    for _ in range(n_iter):
        tri = rng.choice(indices, size=3, replace=False)
        a, b, cpt = P[tri[0]], P[tri[1]], P[tri[2]]
        n = np.cross(b - a, cpt - a)
        if np.linalg.norm(n) < 1e-12:
            continue
        n = _norm(n)
        d = np.dot(P - a, n)
        inliers = np.abs(d) <= inlier_tol
        count = int(np.count_nonzero(inliers))
        if count > best_count:
            best_count = count
            best_inliers = inliers

    if best_inliers is None or best_count < 3:
        c, n = _fit_plane_svd(P)
        return c, n, np.ones(N, dtype=bool)

    Pin = P[best_inliers]
    c, n = _fit_plane_svd(Pin)
    return c, n, best_inliers

def _compute_3d_convex_hull_area(points):
    """
    Compute the surface area of a convex hull in 3D.
    """
    try:
        hull = ConvexHull(points)
        area = hull.area
    except Exception as e:
        print(f"Error in ConvexHull area calculation: {e}")
        area = 0.0
    return float(area)

# ---------------- Target Container ----------------
class TargetBundle:
    """
    Holds per-target state so 'polished' and 'rough' can each be processed.
    """
    def __init__(self, name: str):
        self.name = name  # "polished" or "rough"

        # Mesh and actor
        self.mesh = None
        self.actor = None
        self.highlight_actor = None

        # Facet data for this target
        self.facets = []              # list of facet dicts
        self.facet_results = {}       # fid -> result dict
        self.visible_facet_ids = []   # ids of non-girdle facets for navigation

        # Per-target selected facet view actors
        self.facet_poly_actor = None
        self.points_actor = None
        self.dim_label_actor = None
        self.edge_line_actors = []

        # Label picking
        self._facet_labels_actor = None
        self._facet_label_points = None
        self._facet_label_fids = None
        self._facet_label_kd = None
        self._facet_label_picker = None
        self._facet_label_pick_tag = None
        self._facet_label_pick_cb = None

        # Pass-point clouds
        self.pass_red_actor = None
        self.pass_green_actor = None
        self.pass_blue_actor = None

        # Cutting volume (global) for this target
        self.cut_volume_actor = None
        self.cut_volume_grid = None

        # Extrusion (per selected)
        self.extruded_actor = None
        self.extruded_grid = None
        self.view_mesh = None  # lightweight mesh only for rendering

        # Heatmap overlay
        self._heat_actor = None
                # Facet boundary overlay (feature edges)
        self.facet_edges_actor = None

        self.axes_actors = []        # list of mesh actors (arrows/lines)
        self.axes_labels_actor = None
        self.az_glyph_actors = []
        self.ray_actors = []  # debug-only ray lines for visualization (never exported)


class PolishPlanner(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.calc_locked = False
        self.setWindowTitle("Polish/Rough Projection — Voxel Volumes + Sequence + Cutting/Extrusion")
        self._fit_to_screen(1720, 1040)

        self.plotter = QtInteractor(self)
        self.setCentralWidget(self.plotter)
        pv.set_plot_theme("document")
        self.plotter.set_background("#0c0c14", top="#1a1f2e")
        try:
            self.plotter.enable_anti_aliasing()         # FXAA (if available)
            self.plotter.enable_depth_peeling()         # you already call this – keep it
            # reduce shimmer on fast moves
            if hasattr(self.plotter, "iren"):
                self.plotter.iren.setDesiredUpdateRate(60.0)
        except Exception:
            pass
        self._apply_polished_rendering_once()


        # Modern UI polish
        self._init_fonts()
        self._build_toolbar()
        self._build_statusbar()
        self.apply_theme("dark")   # "dark" or "light"
        self._wire_shortcuts()

        # ----- Right dock -----
        dock = QDockWidget("Controls", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        panel = QWidget()
        scroll.setWidget(panel)
        dock.setWidget(scroll)

        root = QVBoxLayout(panel)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        # ============ LOAD & ALIGN ============
        grp_load = QGroupBox("Load & Align")
        v = QVBoxLayout(grp_load)

        row = QHBoxLayout()
        self.load_polished_btn = QPushButton("Load Polished (stencil)")
        self.load_polished_btn.clicked.connect(self.load_polished)
        row.addWidget(self.load_polished_btn)

        self.load_rough_btn = QPushButton("Load Rough")
        self.load_rough_btn.clicked.connect(self.load_rough)
        row.addWidget(self.load_rough_btn)
        v.addLayout(row)

        row = QHBoxLayout()
        self.center_cb = QCheckBox("Center visually")
        self.center_cb.setChecked(True)
        self.center_cb.setToolTip("Shift both meshes to a shared visual center.")
        self.center_cb.stateChanged.connect(self.update_visual_center)
        row.addWidget(self.center_cb)

        self.icp_cb = QCheckBox("ICP (Open3D)")
        self.icp_cb.setChecked(False)
        if not OPEN3D_AVAILABLE:
            self.icp_cb.setEnabled(False)
            self.icp_cb.setToolTip("Install open3d to enable ICP")
        row.addWidget(self.icp_cb)

        self.align_btn = QPushButton("Align")
        self.align_btn.setEnabled(False)
        self.align_btn.setToolTip("Align rough to polished (centroid; optional ICP).")
        self.align_btn.clicked.connect(self.align_models)
        row.addWidget(self.align_btn)
        v.addLayout(row)

        root.addWidget(grp_load)

        # ============ ACTIVE TARGET ============
        grp_target = QGroupBox("Active Target")
        vt = QVBoxLayout(grp_target)
        rowt = QHBoxLayout()
        self.rb_polished = QRadioButton("Work on: Polished")
        self.rb_rough = QRadioButton("Work on: Rough")
        self.rb_polished.setChecked(True)
        self.rb_polished.toggled.connect(self.on_target_changed)
        self.rb_rough.toggled.connect(self.on_target_changed)
        rowt.addWidget(self.rb_polished)
        rowt.addWidget(self.rb_rough)
        vt.addLayout(rowt)
        root.addWidget(grp_target)

        # ============ FACETS ============
        grp_facet = QGroupBox("Facets")
        v = QVBoxLayout(grp_facet)

        row = QHBoxLayout()
        row.addWidget(QLabel("Facet index:"))
        self.facet_spin = QSpinBox()
        self.facet_spin.setMinimum(0)
        self.facet_spin.setValue(0)
        self.facet_spin.setEnabled(False)
        row.addWidget(self.facet_spin)

        self.prev_btn = QPushButton("Prev")
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self.prev_facet)
        row.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.next_facet)
        row.addWidget(self.next_btn)
        v.addLayout(row)

        row = QHBoxLayout()
        self.compute_selected_btn = QPushButton("Compute Selected Facet")
        self.compute_selected_btn.setEnabled(False)
        self.compute_selected_btn.clicked.connect(self.compute_selected_facet)
        row.addWidget(self.compute_selected_btn)

        self.compute_all_btn = QPushButton("Compute All Facets (summary + voxel)")
        self.compute_all_btn.setEnabled(False)
        self.compute_all_btn.clicked.connect(self.compute_all_facets)
        row.addWidget(self.compute_all_btn)
        v.addLayout(row)

        root.addWidget(grp_facet)

        # Extract/classify facets button
        self.extract_facets_btn = QPushButton("Extract and Classify Facets (Active)")
        self.extract_facets_btn.clicked.connect(self.extract_facets_from_active_mesh)
        root.addWidget(self.extract_facets_btn)

        # ============ DEPTH, VOXELS & CUTTING ============
        grp_depth = QGroupBox("Depth, Voxels & Cutting Volume")
        v = QVBoxLayout(grp_depth)

        row = QHBoxLayout()
        row.addWidget(QLabel("Grid cells/axis (uniform voxel):"))
        self.grid_cells_spin = QSpinBox()
        self.grid_cells_spin.setRange(8, 2000)
        self.grid_cells_spin.setValue(120)
        self.grid_cells_spin.setToolTip("Resolution of voxel grid if uniform voxelization is used.")
        row.addWidget(self.grid_cells_spin)

        self.use_voxel_cb = QCheckBox("Use voxel integration")
        self.use_voxel_cb.setChecked(True)
        row.addWidget(self.use_voxel_cb)
        v.addLayout(row)

        row = QHBoxLayout()
        self.use_adaptive_cb = QCheckBox("Use adaptive voxels (quadtree)")
        self.use_adaptive_cb.setChecked(True)
        self.use_adaptive_cb.setToolTip("Faster, more accurate volume via adaptive tiles.")
        row.addWidget(self.use_adaptive_cb)

        self.show_volume_cb = QCheckBox("Show cutting volume")
        self.show_volume_cb.setChecked(False)
        self.show_volume_cb.stateChanged.connect(self.toggle_cutting_volume)
        row.addWidget(self.show_volume_cb)

        self.build_volume_btn = QPushButton("Build / Update Cutting Volume")
        self.build_volume_btn.setEnabled(False)
        self.build_volume_btn.clicked.connect(self.build_cutting_volume)
        row.addWidget(self.build_volume_btn)
        v.addLayout(row)

        root.addWidget(grp_depth)

        # ============ EXTRUSION ============
        grp_ex = QGroupBox("Per-Facet Exact Extrusion (Active)")
        v = QVBoxLayout(grp_ex)

        row = QHBoxLayout()
        row.addWidget(QLabel("Samples/axis (extrude):"))
        self.extrude_samples_spin = QSpinBox()
        self.extrude_samples_spin.setRange(10, 800)
        self.extrude_samples_spin.setValue(80)
        self.extrude_samples_spin.setToolTip("Node resolution across the facet; higher = smoother extruded surface.")
        row.addWidget(self.extrude_samples_spin)

        self.build_extruded_btn = QPushButton("Build Extruded Volume (Selected)")
        self.build_extruded_btn.setEnabled(False)
        self.build_extruded_btn.setToolTip("Cast rays from the facet plane along multiple directions until first hit with the other mesh.")
        self.build_extruded_btn.clicked.connect(self.build_extruded_selected)
        row.addWidget(self.build_extruded_btn)
        v.addLayout(row)

        row = QHBoxLayout()
        self.show_extruded_cb = QCheckBox("Show extruded volume")
        self.show_extruded_cb.setChecked(False)
        self.show_extruded_cb.setEnabled(False)
        self.show_extruded_cb.stateChanged.connect(self.toggle_extruded_visibility)
        row.addWidget(self.show_extruded_cb)

        self.export_extruded_btn = QPushButton("Export Extruded STL")
        self.export_extruded_btn.setEnabled(False)
        self.export_extruded_btn.clicked.connect(self.export_extruded_stl)
        row.addWidget(self.export_extruded_btn)
        v.addLayout(row)

        root.addWidget(grp_ex)

        # ============ VIEW TOGGLES ============
        grp_view = QGroupBox("View")
        v = QVBoxLayout(grp_view)

        row = QHBoxLayout()
        self.see_through_cb = QCheckBox("See-through surfaces")
        self.see_through_cb.setChecked(True)
        self.see_through_cb.setToolTip("Make both meshes translucent while keeping facet edges & overlays crisp.")
        self.see_through_cb.stateChanged.connect(self.toggle_see_through)
        row.addWidget(self.see_through_cb)
        v.addLayout(row)

        row = QHBoxLayout()
        self.show_points_cb = QCheckBox("Show projected points")
        self.show_points_cb.setChecked(True)
        self.show_points_cb.stateChanged.connect(lambda _: self.refresh_selected_overlay())
        row.addWidget(self.show_points_cb)

        self.show_dims_cb = QCheckBox("Show dimension labels")
        self.show_dims_cb.setChecked(True)
        self.show_dims_cb.setToolTip("Edge lengths + centroid area/depth labels (always visible).")
        self.show_dims_cb.stateChanged.connect(lambda _: self.refresh_selected_overlay())
        row.addWidget(self.show_dims_cb)
        v.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Pass regions (RGB):"))
        self.show_coarse_cb = QCheckBox("Red")
        self.show_coarse_cb.setChecked(False)
        self.show_coarse_cb.setEnabled(False)
        self.show_coarse_cb.stateChanged.connect(self.update_pass_actors_visibility)
        row.addWidget(self.show_coarse_cb)

        self.show_medium_cb = QCheckBox("Green")
        self.show_medium_cb.setChecked(False)
        self.show_medium_cb.setEnabled(False)
        self.show_medium_cb.stateChanged.connect(self.update_pass_actors_visibility)
        row.addWidget(self.show_medium_cb)

        self.show_fine_cb = QCheckBox("Blue")
        self.show_fine_cb.setChecked(False)
        self.show_fine_cb.setEnabled(False)
        self.show_fine_cb.stateChanged.connect(self.update_pass_actors_visibility)
        row.addWidget(self.show_fine_cb)
        v.addLayout(row)

        row = QHBoxLayout()
        self.show_labels_cb = QCheckBox("Show facet labels (slow)")
        self.show_labels_cb.setChecked(False)
        self.show_labels_cb.stateChanged.connect(lambda _: self.build_clickable_facet_labels())
        row.addWidget(self.show_labels_cb)

        
        self.lock_calc_cb = QCheckBox("Lock facet calculations")
        self.lock_calc_cb.setToolTip("Freeze facet calculations and selection")
        self.lock_calc_cb.setChecked(False)
        row.addWidget(self.lock_calc_cb)

        self.clear_calc_btn = QPushButton("Clear all calculations")
        self.clear_calc_btn.setToolTip("Clear overlays, labels, highlights and computed values")
        row.addWidget(self.clear_calc_btn)

        # Connect signals
        self.lock_calc_cb.toggled.connect(self.on_lock_calc_toggled)
        self.clear_calc_btn.clicked.connect(self.clear_all_calculations)
        self.show_heatmap_cb = QCheckBox("Show work heatmap")
        self.show_heatmap_cb.setChecked(True)
        self.show_heatmap_cb.stateChanged.connect(self.toggle_heatmap_visibility)
        row.addWidget(self.show_heatmap_cb)

        # in __init__ -> grp_view section, after show_heatmap_cb
        self.show_facet_edges_cb = QCheckBox("Show facet outlines")
        self.show_facet_edges_cb.setChecked(False)  # default OFF (no black lines)
        self.show_facet_edges_cb.stateChanged.connect(self.toggle_facet_edges)
        row.addWidget(self.show_facet_edges_cb)
    
        row = QHBoxLayout()
        self.show_az_legend_cb = QCheckBox("Azimuth legend")
        self.show_az_legend_cb.setChecked(True)
        self.show_az_legend_cb.stateChanged.connect(self.on_toggle_az_legend)
        row.addWidget(self.show_az_legend_cb)

        self.show_az_glyphs_cb = QCheckBox("Azimuth glyphs")
        self.show_az_glyphs_cb.setChecked(True)
        self.show_az_glyphs_cb.stateChanged.connect(lambda _: self.refresh_selected_overlay())
        row.addWidget(self.show_az_glyphs_cb)

        self.show_axes_cb = QCheckBox("Show diamond axes")
        self.show_axes_cb.setChecked(True)
        self.show_axes_cb.stateChanged.connect(self.toggle_axes_visibility)
        row.addWidget(self.show_axes_cb)

        self.show_axis_labels_cb = QCheckBox("Axis labels")
        self.show_axis_labels_cb.setChecked(True)
        self.show_axis_labels_cb.stateChanged.connect(self.toggle_axes_visibility)
        row.addWidget(self.show_axis_labels_cb)
        v.addLayout(row)

        root.addWidget(grp_view)

        # ============ CAMERA & ORTHO VIEWS ============
        grp_cam = QGroupBox("Camera & Ortho Views")
        vcam = QVBoxLayout(grp_cam)

        row = QHBoxLayout()
        self.ortho_cb = QCheckBox("Orthographic projection")
        self.ortho_cb.setChecked(True)
        self.ortho_cb.stateChanged.connect(self.on_toggle_ortho)
        row.addWidget(self.ortho_cb)

        self.iso_btn = QPushButton("Iso")
        self.iso_btn.clicked.connect(self.view_iso)
        row.addWidget(self.iso_btn)
        vcam.addLayout(row)

        row = QHBoxLayout()
        self.top_btn = QPushButton("Top")
        self.top_btn.clicked.connect(self.view_top)
        row.addWidget(self.top_btn)

        self.bottom_btn = QPushButton("Bottom")
        self.bottom_btn.clicked.connect(self.view_bottom)
        row.addWidget(self.bottom_btn)

        self.front_btn = QPushButton("Front")
        self.front_btn.clicked.connect(self.view_front)
        row.addWidget(self.front_btn)

        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.view_back)
        row.addWidget(self.back_btn)

        self.left_btn = QPushButton("Left")
        self.left_btn.clicked.connect(self.view_left)
        row.addWidget(self.left_btn)

        self.right_btn = QPushButton("Right")
        self.right_btn.clicked.connect(self.view_right)
        row.addWidget(self.right_btn)
        vcam.addLayout(row)

        root.addWidget(grp_cam)

        # ============ EXPORTS / SEQUENCE ============
        grp_seq = QGroupBox("Exports & Sequence (Active)")
        v = QVBoxLayout(grp_seq)

        row = QHBoxLayout()
        self.export_csv_btn = QPushButton("Export Facets CSV")
        self.export_csv_btn.setEnabled(False)
        self.export_csv_btn.clicked.connect(self.export_csv)
        row.addWidget(self.export_csv_btn)

        self.export_selected_csv_btn = QPushButton("Export Selected Facet CSV")
        self.export_selected_csv_btn.setEnabled(False)
        self.export_selected_csv_btn.clicked.connect(self.export_selected_facet_csv)
        row.addWidget(self.export_selected_csv_btn)
        v.addLayout(row)

        row = QHBoxLayout()
        self.generate_seq_btn = QPushButton("Generate Sequence")
        self.generate_seq_btn.setEnabled(False)
        self.generate_seq_btn.clicked.connect(self.generate_sequence)
        row.addWidget(self.generate_seq_btn)

        self.export_seq_btn = QPushButton("Export Sequence CSV")
        self.export_seq_btn.setEnabled(False)
        self.export_seq_btn.clicked.connect(self.export_sequence_csv)
        row.addWidget(self.export_seq_btn)
        v.addLayout(row)

        root.addWidget(grp_seq)

        # ============ SEQUENCE PANEL ============
        seq_box = QGroupBox("Planned Sequence (per pass, Active)")
        v = QVBoxLayout(seq_box)
        self.sequence_text = QTextEdit()
        self.sequence_text.setReadOnly(True)
        self.sequence_text.setPlaceholderText("Generate Sequence to see the plan…")
        v.addWidget(self.sequence_text)
        root.addWidget(seq_box, stretch=1)

        # ============ INFO ============
        info_box = QGroupBox("Selected Facet — Stats (Active)")
        form = QFormLayout(info_box)
        self.info_facet_type = QLabel("-")
        self.info_facet = QLabel("-")
        self.info_max_depth = QLabel("-")
        self.info_mean_depth = QLabel("-")
        self.info_depth_p95 = QLabel("-")
        self.info_depth_rms = QLabel("-")
        self.info_area = QLabel("-")
        self.info_perimeter = QLabel("-")
        self.info_points_inside = QLabel("-")
        self.info_approx_volume = QLabel("-")
        self.info_voxel_volume = QLabel("-")
        self.info_passes = QLabel("-")
        self.info_time = QLabel("-")
        self.info_azimuth = QLabel("-")
        form.addRow("Azimuth (° from Table):", self.info_azimuth)
        form.addRow("Facet Type:", self.info_facet_type)
        form.addRow("Facet:", self.info_facet)
        form.addRow("Max depth:", self.info_max_depth)
        form.addRow("Mean depth:", self.info_mean_depth)
        form.addRow("Depth p95:", self.info_depth_p95)
        form.addRow("Depth RMS:", self.info_depth_rms)
        form.addRow("Footprint area:", self.info_area)
        form.addRow("Perimeter:", self.info_perimeter)
        form.addRow("Points inside:", self.info_points_inside)
        form.addRow("Approx vol (area×mean):", self.info_approx_volume)
        form.addRow("Voxel volume:", self.info_voxel_volume)
        form.addRow("Passes:", self.info_passes)
        form.addRow("Est. time:", self.info_time)
        root.addWidget(info_box)

        # --------- Data holders ---------
        self.target_polished = TargetBundle("polished")
        self.target_rough = TargetBundle("rough")

        self.polished_mesh = None
        self.rough_mesh = None

        self.polished_actor = None
        self.rough_actor = None

        # The trimesh cache is for the "other" mesh used for ray/voxel queries
        self._rough_trimesh = None
        self._other_trimesh_cache = None

        # Current facet (index within active target's visible facet list)
        self.current_facet = 0

        pv.set_plot_theme("document")
        self.update_status("Ready")


        try:
            self.focus_camera_on_facet(self.current_facet)
        except Exception:
            pass
    # ---- PyVista compatibility shims ----
    
        # ---------- Camera smoothing (60 FPS tweening) ----------
    def _cam_state(self):
        cam = self.plotter.camera
        # return numpy arrays for vector math
        return (np.array(cam.position, dtype=float),
                np.array(cam.focal_point, dtype=float),
                np.array(cam.view_up, dtype=float))

    def _apply_cam_state(self, state):
        p, f, u = state
        cam = self.plotter.camera
        cam.position = p.tolist()
        cam.focal_point = f.tolist()
        cam.view_up = u.tolist()
        self.plotter.render()

    def _ease(self, t: float, kind: str = "smooth"):
        # t in [0,1]; smoothstep / cubic ease-in-out
        t = max(0.0, min(1.0, float(t)))
        if kind == "linear":
            return t
        # default: ease in-out cubic
        return 3*t**2 - 2*t**3

    def animate_camera_to(self, pos, focal, view_up=None, duration: float = 0.65, easing: str = "smooth"):
        """Tween camera to (pos, focal, view_up) over duration seconds."""
        # stop previous animation if any
        try:
            if hasattr(self, "_cam_timer") and self._cam_timer is not None:
                self._cam_timer.stop()
                self._cam_timer.deleteLater()
        except Exception:
            pass

        start_p, start_f, start_u = self._cam_state()
        target_p = np.array(pos, dtype=float)
        target_f = np.array(focal, dtype=float)
        target_u = np.array(view_up if view_up is not None else start_u, dtype=float)

        self._cam_alpha = 0.0
        dt = 16  # ms ~ 60 FPS
        total = max(0.05, float(duration))  # never 0
        step = (dt/1000.0) / total

        def tick():
            try:
                self._cam_alpha += step
                a = self._ease(self._cam_alpha, easing)
                p = start_p + (target_p - start_p) * a
                f = start_f + (target_f - start_f) * a
                u = start_u + (target_u - start_u) * a
                self._apply_cam_state((p, f, u))
                if self._cam_alpha >= 1.0:
                    self._cam_timer.stop()
                    self._cam_timer.deleteLater()
                    self._cam_timer = None
            except Exception:
                # fail safe
                try:
                    self._apply_cam_state((target_p, target_f, target_u))
                finally:
                    if self._cam_timer:
                        self._cam_timer.stop()
                        self._cam_timer.deleteLater()
                        self._cam_timer = None

        self._cam_timer = QTimer(self)
        self._cam_timer.timeout.connect(tick)
        self._cam_timer.start(dt)

    def fly_to_bounds(self, bounds, duration: float = 0.65):
        """Compute a nice default cam pose for bounds and animate to it."""
        try:
            pos, focal, up = self.plotter.get_default_cam_pos(bounds)
        except Exception:
            # PyVista can also return a list-like triple
            cp = self.plotter.get_default_cam_pos(bounds)
            pos, focal, up = cp[0], cp[1], cp[2]
        self.animate_camera_to(pos, focal, up, duration=duration, easing="smooth")

    def smooth_reset(self, duration: float = 0.65):
        """Animated reset to the current scene bounds."""
        try:
            b = self.plotter.bounds  # union of actors
            if b is None:
                self.plotter.reset_camera(); return
            self.fly_to_bounds(b, duration=duration)
        except Exception:
            self.plotter.reset_camera()
# --------------------------------------------------------


    def _dedup_poly2d(self, poly: np.ndarray, eps: float = 1e-9) -> np.ndarray:
        if poly is None or len(poly) < 2:
            return poly
        out = [poly[0]]
        for p in poly[1:]:
            if np.linalg.norm(p - out[-1]) > eps:
                out.append(p)
        if len(out) >= 3 and np.linalg.norm(out[0] - out[-1]) <= eps:
            out = out[:-1]
        return np.asarray(out, float)

    def _facet_outline_polygon_2d(self,
                                base_mesh: pv.PolyData,
                                cell_ids,
                                centroid: np.ndarray,
                                u: np.ndarray,
                                v: np.ndarray,
                                angle_deg: float = 1.0) -> np.ndarray:
        """
        Return the facet's true boundary loop in local 2D (concave OK),
        by extracting boundary edges of the selected-cell submesh.
        """
        try:
            sub = base_mesh.extract_cells(np.asarray(cell_ids, dtype=int)).triangulate().clean()
            edg = _extract_feature_edges(
            sub,
            angle_deg=angle_deg,
            boundary_edges=True,    # boundary of this facet selection
            feature_edges=False,    # ignore creases inside
            non_manifold_edges=True,
            manifold_edges=False
            )

            if edg.n_points < 3 or edg.lines.size == 0:
                return None

            pts = np.asarray(edg.points)
            lines = np.asarray(edg.lines)

            # Parse VTK polyline cells into segments (supports polylines & 2-pt lines)
            segs = []
            i = 0
            L = len(lines)
            while i < L:
                n = int(lines[i])
                ids = lines[i+1:i+1+n]
                if n >= 2:
                    for j in range(n - 1):
                        a, b = int(ids[j]), int(ids[j + 1])
                        segs.append((a, b))
                i += n + 1
            if not segs:
                return None

            # Build adjacency and walk closed loops
            from collections import defaultdict
            nbr = defaultdict(list)
            for a, b in segs:
                if b not in nbr[a]: nbr[a].append(b)
                if a not in nbr[b]: nbr[b].append(a)

            visited_e = set()
            loops = []
            for a, b in segs:
                if (a, b) in visited_e or (b, a) in visited_e:
                    continue
                loop = [a]
                prev, cur = a, b
                visited_e.add((a, b))
                max_steps = len(segs) * 2 + 10
                steps = 0
                while steps < max_steps:
                    loop.append(cur)
                    steps += 1
                    nxts = [x for x in nbr[cur] if x != prev]
                    if not nxts:
                        break
                    # choose the neighbor that best continues the direction
                    pv3 = pts[cur] - pts[prev]
                    best, bestcos = nxts[0], -2.0
                    for cand in nxts:
                        vv = pts[cand] - pts[cur]
                        denom = (np.linalg.norm(pv3) * np.linalg.norm(vv) + 1e-18)
                        c = float(np.dot(pv3, vv) / denom)
                        if c > bestcos:
                            bestcos, best = c, cand
                    nxt = best
                    if nxt == loop[0]:
                        loop.append(nxt)
                        break
                    visited_e.add((cur, nxt))
                    prev, cur = cur, nxt

                if len(loop) >= 4 and loop[0] == loop[-1]:
                    loops.append(loop[:-1])

            if not loops:
                return None

            # Pick loop with largest projected area
            def proj_area(ids):
                bw = pts[ids]
                poly2d = np.column_stack([ (bw - centroid) @ u, (bw - centroid) @ v ])
                x, y = poly2d[:, 0], poly2d[:, 1]
                return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))

            best_ids = max(loops, key=proj_area)
            boundary = pts[best_ids]
            poly2d = np.column_stack([ (boundary - centroid) @ u, (boundary - centroid) @ v ])

            # Cleanup: dedup consecutive, force CCW
            poly2d = self._dedup_poly2d(poly2d)
            x, y = poly2d[:, 0], poly2d[:, 1]
            signed = 0.5 * (np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
            if signed < 0:
                poly2d = poly2d[::-1]
            return poly2d
        except Exception as e:
            print("facet outline failed:", e)
            return None

        # ---------------- Modern UI helpers (toolbar, statusbar, theme, shortcuts) ----------------
    def _init_fonts(self):
        """Set a clean default font early (before building widgets)."""
        try:
            base = QFont("Segoe UI", 10)
        except Exception:
            base = QFont()
            base.setPointSize(10)
        self.setFont(base)

    def _build_toolbar(self):
        """Compact toolbar with the most-used actions wired to existing slots."""
        tb = QToolBar("Main")
        tb.setIconSize(QtCore.QSize(18, 18))
        tb.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, tb)

        style = self.style()
        def add_action(text, icon, handler, checkable=False, checked=False, tip=None, shortcut=None):
            act = QAction(icon, text, self)
            if checkable:
                act.setCheckable(True)
                act.setChecked(checked)
            if tip:
                act.setToolTip(tip)
                act.setStatusTip(tip)
            if shortcut:
                act.setShortcut(shortcut)
            act.triggered.connect(handler)
            tb.addAction(act)
            return act

        # File / align
        add_action("Load Polished", style.standardIcon(QStyle.SP_DialogOpenButton),
                   self.load_polished, tip="Open polished (stencil) mesh")
        add_action("Load Rough", style.standardIcon(QStyle.SP_DialogOpenButton),
                   self.load_rough, tip="Open rough mesh")
        tb.addSeparator()
        add_action("Align", style.standardIcon(QStyle.SP_ArrowForward),
                   self.align_models, tip="Align rough to polished")

        # Facets
        tb.addSeparator()
        add_action("Extract Facets", style.standardIcon(QStyle.SP_BrowserReload),
                   self.extract_facets_from_active_mesh,
                   tip="Extract + classify facets for the ACTIVE mesh")
        add_action("Compute Selected", style.standardIcon(QStyle.SP_MediaPlay),
                   self.compute_selected_facet, tip="Compute metrics for the selected facet")
        add_action("Compute All", style.standardIcon(QStyle.SP_MediaSkipForward),
                   self.compute_all_facets, tip="Compute metrics for all facets (summary + voxel)")

        # Volumes / extrusion
        tb.addSeparator()
        add_action("Cutting Volume", style.standardIcon(QStyle.SP_FileDialogListView),
                   self.build_cutting_volume, tip="Build/update cutting volume for ACTIVE target")
        add_action("Extrude Selected", style.standardIcon(QStyle.SP_FileDialogDetailedView),
                   self.build_extruded_selected, tip="Build per-facet extruded volume (ACTIVE vs OTHER)")

        # Ortho toggle + quick views
        tb.addSeparator()
        self._act_ortho = add_action(
            "Ortho", style.standardIcon(QStyle.SP_DesktopIcon),
            lambda checked: self._set_ortho(checked),
            checkable=True, checked=True, tip="Toggle orthographic projection (parallel camera)"
        )
        add_action("Iso", style.standardIcon(QStyle.SP_ComputerIcon),
                   self.view_iso, tip="Isometric view")
        add_action("Working Facet", self.style().standardIcon(QStyle.SP_FileDialogInfoView),
                   self.open_working_facet, tip="Open the Working Facet window (facet data + extruded preview)")


    def open_working_facet(self):
        try:
            from working_facet_window import WorkingFacetWindow as _WF
        except Exception:
            _WF = None

        if _WF is None and "WorkingFacetWindow" in globals():
            _WF = _WF

        if _WF is None:
            try:
                QtWidgets.QMessageBox.warning(self, "Working Facet", "WorkingFacetWindow not available")
            except Exception:
                print("WorkingFacetWindow not available")
            return

        need_new = False
        win = getattr(self, "working_win", None)
        if win is None:
            need_new = True
        else:
            # Probe the existing window; if its underlying C++ object was deleted, create a new one
            try:
                _ = win.isVisible()
            except Exception:
                need_new = True

        if need_new:
            try:
                self.working_win = _WF(self)
                # match theme
                try:
                    self.working_win.setStyleSheet(self.styleSheet())
                except Exception:
                    pass
            except Exception as e:
                try:
                    QtWidgets.QMessageBox.warning(self, "Working Facet", f"Could not create window: {e}")
                except Exception:
                    print("Could not create Working Facet window:", e)
                return

        # show / raise / refresh
        try:
            self.working_win.show()
            self.working_win.raise_()
            try:
                self.working_win.refresh()
            except Exception:
                pass
        except Exception as e:
            # If something went wrong (e.g., stale reference), try once more with a fresh window
            try:
                self.working_win = _WF(self)
                self.working_win.show()
                self.working_win.raise_()
                try:
                    self.working_win.setStyleSheet(self.styleSheet())
                except Exception:
                    pass
                try:
                    self.working_win.refresh()
                except Exception:
                    pass
            except Exception as ee:
                try:
                    QtWidgets.QMessageBox.warning(self, "Working Facet", f"Could not open window: {ee}")
                except Exception:
                    print("Could not open Working Facet window:", ee)
            return

    def  _build_statusbar(self):
            sb = QStatusBar(self)
            self.setStatusBar(sb)
            self.update_status("Ready")

    def _apply_polished_rendering_once(self):
    # Anti-aliasing (best effort across backends)
        for mode in ("ssaa", "fxaa", "msaa"):
            try:
                self.plotter.enable_anti_aliasing(mode)
            except Exception:
                pass
        # Nice default lights
        try:
            self.plotter.lighting = "light_kit"
        except Exception:
            pass


    def _apply_faceted_look(self, target: TargetBundle, color_hex: str, opacity: float = 0.65):
        """Flat-shaded translucent surface; back-face culled so inner mesh/backsides don't bleed."""
        if target.actor is not None:
            try: self.plotter.remove_actor(target.actor)
            except Exception: pass
            target.actor = None

        mesh_for_view = target.view_mesh if target.view_mesh is not None else target.mesh
        if mesh_for_view is None:
            return

        target.actor = self.plotter.add_mesh(
            mesh_for_view,
            color=color_hex,
            opacity=float(opacity),    # keep translucency
            smooth_shading=False,      # crisp, faceted
            show_edges=False,          # no triangle grid
            culling='back',            # hides back faces ⇒ no inside lines
            specular=0.35, specular_power=18, ambient=0.12, diffuse=0.85,
            name=f'{target.name}',
        )

        # Only real facet boundarie
        if getattr(self, "show_facet_edges_cb", None) and self.show_facet_edges_cb.isChecked():
            self._add_or_update_facet_edges(
                target, angle_deg=22.0, edge_color="#0b0b0b", edge_width=1, tube_radius=None
            )



    def toggle_facet_edges(self, *_):
        want = bool(self.show_facet_edges_cb.isChecked())
        if want:
            self._refresh_edge_overlays()
        else:
            self._remove_edges(self.target_polished)
            self._remove_edges(self.target_rough)
            try: self.plotter.render()
            except Exception: pass

    def toggle_see_through(self, *_):
        """Toggle translucent 'x-ray' look while preserving feature-edge overlays."""
        pol_op = 0.35 if self.see_through_cb.isChecked() else 0.98
        rough_op = 0.25 if self.see_through_cb.isChecked() else 0.95

        if self.target_polished.mesh is not None:
            self._apply_faceted_look(self.target_polished, color_hex="#00ff0d", opacity=pol_op)
        if self.target_rough.mesh is not None:
            self._apply_faceted_look(self.target_rough, color_hex="#c9c9c9", opacity=rough_op)
        if self.target_polished.mesh is not None:
            self._apply_azimuth_coloring_if_available(self.target_polished)
        if self.target_rough.mesh is not None:
            self._apply_azimuth_coloring_if_available(self.target_rough)

        # Rebuild feature edges so they sit crisply on top
        if getattr(self, "show_facet_edges_cb", None) and self.show_facet_edges_cb.isChecked():
            self._refresh_edge_overlays()

        try:
            self.plotter.render()
        except Exception:
            pass

    def _inset_polygon_2d(self, poly2d: np.ndarray, inset: float) -> np.ndarray:
        """
        Parallel-offset (inset) a simple CCW polygon by 'inset' toward its interior.
        Robust for convex / mostly-convex facet hulls.
        """
        P = np.asarray(poly2d, float)
        n = len(P)
        if n < 3 or inset <= 0:
            return P.copy()

        # Ensure CCW
        area2 = 0.0
        for i in range(n):
            x1, y1 = P[i]
            x2, y2 = P[(i + 1) % n]
            area2 += x1 * y2 - y1 * x2
        if area2 < 0:  # clockwise → flip to CCW
            P = P[::-1]

        def unit(v):
            L = np.linalg.norm(v)
            return v / (L + 1e-18)

        out = []
        for i in range(n):
            p_prev = P[(i - 1) % n]
            p      = P[i]
            p_next = P[(i + 1) % n]

            e1 = unit(p - p_prev)
            e2 = unit(p_next - p)

            # CCW inward normals (left normals)
            n1 = np.array([-e1[1], e1[0]])
            n2 = np.array([-e2[1], e2[0]])

            # Offset lines:  (p + n1*inset) + t*e1   and   (p + n2*inset) + s*e2
            A = np.column_stack((e1, -e2))
            b = (p + n2 * inset) - (p + n1 * inset)

            try:
                t_s = np.linalg.solve(A, b)
                q   = (p + n1 * inset) + e1 * t_s[0]
            except np.linalg.LinAlgError:
                # Near-parallel; fallback to average normal shift
                q = p + (n1 + n2) * (0.5 * inset)
            out.append(q)

        return np.asarray(out, float)


    def update_status(self, text: str):
        try:
            self.statusBar().showMessage(text, 5000)
        except Exception:
            pass

    def apply_theme(self, mode: str = "dark"):
        """Apply ModernTheme QSS. Call-safe even before dock/widgets exist."""
        mode = (mode or "dark").lower()
        if mode == "light":
            self.setStyleSheet(ModernTheme.LIGHT_QSS)
            try:
                self.plotter.set_background("#f7f7fa", top="#ffffff")
            except Exception:
                pass
        else:
            self.setStyleSheet(ModernTheme.DARK_QSS)
            try:
                self.plotter.set_background("#0c0c14", top="#1a1f2e")
            except Exception:
                pass

    def _set_ortho(self, enabled: bool):
        """Toolbar-driven ortho toggle (keeps checkbox, if present, in sync)."""
        try:
            if enabled:
                self.plotter.enable_parallel_projection()
            else:
                self.plotter.disable_parallel_projection()
            # sync checkbox if it already exists
            cb = getattr(self, "ortho_cb", None)
            if cb is not None and cb.isChecked() != bool(enabled):
                cb.blockSignals(True)
                cb.setChecked(bool(enabled))
                cb.blockSignals(False)
            self.plotter.reset_camera()
        except Exception:
            pass

    def _wire_shortcuts(self):
        """Global keyboard shortcuts. Keep these generic so we don't depend on widgets built later."""
        def sc(seq, fn):
            try:
                s = QShortcut(QKeySequence(seq), self)
                s.activated.connect(fn)
                return s
            except Exception:
                return None

        # Facet navigation
        sc("[", self.prev_facet)
        sc("]", self.next_facet)

        # Compute
        sc("F5", self.compute_selected_facet)
        sc("Shift+F5", self.compute_all_facets)

        # Volumes
        sc("Ctrl+E", self.build_extruded_selected)
        sc("Ctrl+Shift+V", self.build_cutting_volume)

        # Ortho + views
        sc("O", lambda: self._set_ortho(not getattr(self, "_act_ortho", None).isChecked()
                                        if getattr(self, "_act_ortho", None) else True))
        sc("Ctrl+1", self.view_top)
        sc("Ctrl+2", self.view_bottom)
        sc("Ctrl+3", self.view_front)
        sc("Ctrl+4", self.view_back)
        sc("Ctrl+5", self.view_left)
        sc("Ctrl+6", self.view_right)
        sc("Ctrl+0", self.view_iso)

    def _fit_to_screen(self, w, h):
        screen = QtWidgets.QApplication.primaryScreen()
        if screen is None:
            self.resize(w, h); return
        avail = screen.availableGeometry()   # excludes taskbar
        w = min(w, avail.width())
        h = min(h, avail.height())
        x = avail.x() + (avail.width() - w) // 2
        y = avail.y() + (avail.height() - h) // 2
        self.setGeometry(x, y, w, h)


        # ---------------- Facet boundary overlay (feature edges) ----------------
    def _remove_edges(self, target: TargetBundle):
        if getattr(target, "facet_edges_actor", None) is not None:
            try:
                self.plotter.remove_actor(target.facet_edges_actor)
            except Exception:
                pass
            target.facet_edges_actor = None

    def _add_or_update_facet_edges(
    self,
    target: TargetBundle,
    angle_deg: float = 22.0,
    edge_color: str = "#0b0b0b",
    edge_width: int = 1,
    tube_radius: float = None,
    ):
        """
        Draw only the 'between facet' lines: edges whose dihedral angle exceeds angle_deg.
        No triangle wireframe, no boundary clutter, no interior backface lines.
        """
        mesh = target.mesh 
        if mesh is None:
            return

        # Remove previous overlay
        self._remove_edges(target)

        try:
            base = mesh.triangulate().clean()

            # Only crease edges between facets. Boundary edges off for closed diamonds.
            edges = _extract_feature_edges(
            base,
            angle_deg=angle_deg,
            feature_edges=False,
            boundary_edges=True,   # closed solids -> keep OFF
            non_manifold_edges=True,
            manifold_edges=False
        )
            if edges.n_points == 0:
                return

            # Scale-aware thickness so it looks right for any stone size
            # AFTER (replace lines 55–68 region)
            diag = _mesh_diag(base)
            if tube_radius is not None and tube_radius > 0:
                edge_geo = edges.tube(radius=float(tube_radius), n_sides=12)
                target.facet_edges_actor = self.plotter.add_mesh(
                    edge_geo, color=edge_color, lighting=False,
                    name=f"{target.name}_facet_edges", smooth_shading=False
                )
            else:
                # crisp, pixel-width lines
                target.facet_edges_actor = self.plotter.add_mesh(
                    edges, color=edge_color, line_width=int(edge_width),
                    lighting=False, name=f"{target.name}_facet_edges",
                    render_lines_as_tubes=False, smooth_shading=False
                )

            r = tube_radius if tube_radius is not None else max(1e-6, 0.002 * diag)

            # Use tubes so thickness is consistent from any camera distance
            edge_geo = edges.tube(radius=r, n_sides=12)

            target.facet_edges_actor = self.plotter.add_mesh(
                edge_geo,
                color=edge_color,
                lighting=False,             # keep lines uniformly dark
                name=f"{target.name}_facet_edges",
                smooth_shading=False
            )
        except Exception:
            # very safe fallback: simple lines (pixel-width), still feature-only
            try:
                target.facet_edges_actor = self.plotter.add_mesh(
                    edges, color=edge_color, line_width=edge_width, lighting=False,
                    name=f"{target.name}_facet_edges"
                )
            except Exception:
                target.facet_edges_actor = None


    def _refresh_edge_overlays(self):
        self._add_or_update_facet_edges(self.target_polished, angle_deg=10.0, edge_color="#0b0b0b", edge_width=1, tube_radius=None)
        self._add_or_update_facet_edges(self.target_rough,    angle_deg=10.0, edge_color="#0b0b0b", edge_width=1, tube_radius=None)


    # ---------------- Active target helpers ----------------
    def get_active_target(self) -> TargetBundle:
        return self.target_polished if self.rb_polished.isChecked() else self.target_rough

    def get_other_target(self) -> TargetBundle:
        return self.target_rough if self.rb_polished.isChecked() else self.target_polished

    def on_target_changed(self):
        # Refresh UI and overlays to reflect active target
        self._update_visible_facet_ids()
        self.refresh_selected_overlay()
        self.update_pass_actors_visibility()
        if self.target_polished.mesh is not None and self.target_polished.actor is None:
            self._apply_faceted_look(self.target_polished, color_hex="#00ff0d", opacity=0.70)
        if self.target_rough.mesh is not None and self.target_rough.actor is None:
            self._apply_faceted_look(self.target_rough,    color_hex="#c9c9c9", opacity=0.55)
        if self.target_polished.mesh is not None:
             self._apply_azimuth_coloring_if_available(self.target_polished)
        if self.target_rough.mesh is not None:
            self._apply_azimuth_coloring_if_available(self.target_rough)
        self.update_status("Target toggled")
        self._rebuild_axes_for_targets()


    # ---------------- Loading ----------------
    def load_polished(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open polished stencil", "", "STL/PLY/OBJ Files (*.stl *.ply *.obj)")
        if not fname:
            return
        mesh = pv.read(fname)
        mesh.points *= SCALE_TO_MM
        self.target_polished.mesh = mesh.copy()
        self.target_polished.view_mesh = decimate_for_view(mesh)
        self.polished_mesh = self.target_polished.mesh
        op = 0.45 if getattr(self, 'see_through_cb', None) and self.see_through_cb.isChecked() else 0.98
        self._apply_faceted_look(self.target_polished, color_hex="#00ff0d", opacity=op)  

        if RESET_CAMERA_ONCE_AFTER_LOAD:
            self.plotter.reset_camera()
        self._maybe_enable_after_load()
        self.update_status("Polished loaded")
        self._rebuild_axes_for_targets()


    def load_rough(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open rough mesh", "", "STL/PLY/OBJ Files (*.stl *.ply *.obj)")
        if not fname:
            return
        mesh = pv.read(fname)
        self.target_rough.mesh = mesh.copy()
        self.target_rough.view_mesh = decimate_for_view(mesh)
        self.rough_mesh = self.target_rough.mesh

        op = 0.25 if getattr(self, 'see_through_cb', None) and self.see_through_cb.isChecked() else 0.95
        self._apply_faceted_look(self.target_rough, color_hex="#c9c9c9", opacity=op)
        if RESET_CAMERA_ONCE_AFTER_LOAD:
            self.plotter.reset_camera()

        # Invalidate caches
        self._rough_trimesh = None
        self._other_trimesh_cache = None

        self._maybe_enable_after_load()
        self.update_status("Rough loaded")
        self._rebuild_axes_for_targets()


    def _maybe_enable_after_load(self):
        if self.target_polished.mesh is not None and self.target_rough.mesh is not None:
            self.align_btn.setEnabled(True)
            self.compute_all_btn.setEnabled(True)
            self.compute_selected_btn.setEnabled(True)
            self.facet_spin.setEnabled(True)
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(True)
            self.build_extruded_btn.setEnabled(True)

    # ---------------- Alignment ----------------
    def align_models(self):
        if self.target_polished.mesh is None or self.target_rough.mesh is None:
            QtWidgets.QMessageBox.warning(self, "Error", "Load both polished and rough meshes first")
            return

        pc = np.mean(self.target_polished.mesh.points, axis=0)
        rc = np.mean(self.target_rough.mesh.points, axis=0)
        self.target_rough.mesh.translate(pc - rc, inplace=True)

        if self.icp_cb.isChecked() and OPEN3D_AVAILABLE:
            try:
                src = o3d.geometry.PointCloud(); tgt = o3d.geometry.PointCloud()
                src.points = o3d.utility.Vector3dVector(self.target_rough.mesh.points)
                tgt.points = o3d.utility.Vector3dVector(self.target_polished.mesh.points)

                voxel_size = max(np.linalg.norm(self.target_polished.mesh.bounds[1::2] - self.target_polished.mesh.bounds[0::2]) / 800.0, 1e-6)
                src_down = src.voxel_down_sample(voxel_size); tgt_down = tgt.voxel_down_sample(voxel_size)
                reg = o3d.pipelines.registration.registration_icp(
                    src_down, tgt_down, voxel_size*2.5, np.eye(4),
                    o3d.pipelines.registration.TransformationEstimationPointToPoint()
                )
                T = reg.transformation
                pts = np.asarray(self.target_rough.mesh.points)
                pts_h = np.hstack([pts, np.ones((pts.shape[0],1))])
                pts_t = (T @ pts_h.T).T[:, :3]
                self.target_rough.mesh.points = pts_t
            except Exception as e:
                print("ICP failed:", e)

        # update actors
        try:
            if self.target_rough.actor:
                self.plotter.update_coordinates(self.target_rough.mesh.points, mesh=self.target_rough.actor)
        except Exception:
            try:
                self.plotter.remove_actor(self.target_rough.actor)
            except Exception:
                pass
            self.target_rough.actor = self.plotter.add_mesh(self.target_rough.mesh, color='lightgrey', opacity=0.55)

        self.plotter.reset_camera()
                # refresh edge overlays (geometry changed)
        self._refresh_edge_overlays()

        # invalidate caches
        self._rough_trimesh = None
        self._other_trimesh_cache = None
        self.update_status("Aligned")
        self._rebuild_axes_for_targets()

    # ---------------- Facet extraction for ACTIVE mesh ----------------
    def extract_facets_from_active_mesh(self):
        tgt = self.get_active_target()
        if tgt.mesh is None:
            QtWidgets.QMessageBox.warning(self, "Error", f"Load a {tgt.name} mesh first")
            return

        # Advanced region-growing extractor (replaces naive clustering)
        tgt.facets = self.extract_facets(tgt, angle_tol_deg=1.0)
        self._apply_azimuth_coloring_if_available(tgt)

        self._update_visible_facet_ids()
        if not tgt.visible_facet_ids:
            QtWidgets.QMessageBox.information(self, "No non-girdle facets",
                                              "Facets were detected, but all are 'Girdle'. The index excludes girdle facets.")
            self.update_status("No non-girdle facets")
            return

        # If the other mesh exists, precompute; else show first
        if self.get_other_target().mesh is not None:
            self.compute_all_facets()
        else:
            self.show_selected_facet(0)

        if getattr(self, "show_labels_cb", None) and self.show_labels_cb.isChecked():
            self.build_clickable_facet_labels()
        self.update_status("Facets extracted")
        self._rebuild_axes_for_targets()

    # --------- Advanced region-growing extraction ---------
    def extract_facets(self,
        target: TargetBundle,
        angle_tol_deg=0.5,
        min_faces_per_facet=1,
        min_relative_area=1e-4,
        consider_girdle_as='Girdle',
        girdle_nearness_tol=None,
        robust_girdle=True,
        __retry: int = 0
    ):
        """
        Extract planar facets from a target mesh by clustering cells with similar normals,
        then computing per-facet centroid/normal/footprint area and classifying vs. a fitted girdle plane.

        Scale-aware and self-healing: if 0 non-girdle facets are found, auto-tune tolerances and retry.
        Also auto-orients the girdle normal so +ng points to crown/table; provides an optional manual flip.
        """
        if target.mesh is None:
            return []

        # --- Scale-aware tolerances -------------------------------------------------
        diag = _mesh_diag(target.mesh)
        if not np.isfinite(diag) or diag <= 0:
            diag = 1.0
        # default girdle tol ~0.4% of size if not provided
        if girdle_nearness_tol is None or girdle_nearness_tol <= 0:
            girdle_nearness_tol = DEFAULT_GIRDLE_TOL_FRAC * diag

        # Sanity-clamp angle tolerance (too small will fragment facets)
        angle_tol_deg = max(0.25, float(angle_tol_deg))
        angle_tol_rad = math.radians(angle_tol_deg)
        cos_tol = math.cos(angle_tol_rad)

        # --- Compute per-cell normals ---------------------------------------------
        try:
            m = target.mesh.compute_normals(cell_normals=True, point_normals=False, inplace=False)
            cell_normals = np.asarray(m.cell_normals)
        except Exception:
            # fallback if normals fail (rare)
            m = target.mesh.triangulate().clean()
            m = m.compute_normals(cell_normals=True, point_normals=False, inplace=False)
            cell_normals = np.asarray(m.cell_normals)

        n_cells = int(m.n_cells)
        used = np.zeros(n_cells, dtype=bool)
        facets = []

        # --- Cluster by normal similarity (fast spherical threshold) ---------------
        for ci in range(n_cells):
            if used[ci]:
                continue
            base = cell_normals[ci]
            dots = cell_normals @ base
            group = np.where(dots >= cos_tol)[0].tolist()
            for g in group:
                used[g] = True

            # Extract points for this group's geometry
            try:
                sub = m.extract_cells(np.array(group, dtype=int))
                pts = np.asarray(sub.points)
            except Exception:
                try:
                    faces = m.faces.reshape(-1, 4)[group][:, 1:4]
                    pidx = np.unique(faces.flatten())
                    pts = m.points[pidx]
                except Exception:
                    pts = np.zeros((0, 3), dtype=float)

            if pts.shape[0] < 3:
                continue

            # centroid & plane normal via SVD (robust for slightly noisy triangles)
            centroid = pts.mean(axis=0)
            _, _, VT = np.linalg.svd(pts - centroid, full_matrices=False)
            normal = _norm(VT[-1, :])

            # Reject degenerate tiny spans
            if np.linalg.norm(pts.max(axis=0) - pts.min(axis=0)) < 1e-6 * diag:
                continue

            # Build 2D local basis and project
            arbitrary = np.array([1.0, 0.0, 0.0], dtype=float)
            if abs(np.dot(arbitrary, normal)) > 0.9:
                arbitrary = np.array([0.0, 1.0, 0.0], dtype=float)
            u = _norm(np.cross(normal, arbitrary))
            v = _norm(np.cross(normal, u))
            proj2d = np.column_stack([(pts - centroid) @ u, (pts - centroid) @ v])

            # 2D convex hull area (with safe fallback)
            try:
                ch = ConvexHull(proj2d)
                hull2d = proj2d[ch.vertices]
                footprint_area = float(ConvexHull(hull2d).volume)
            except Exception:
                xy = proj2d
                if xy.shape[0] >= 3:
                    x, y = xy[:, 0], xy[:, 1]
                    footprint_area = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
                else:
                    footprint_area = _compute_3d_convex_hull_area(pts)

            facets.append({
                'faces_idx': group,
                'centroid': centroid,
                'normal': normal,
                'points': pts,
                'footprint_area': footprint_area,
                'facet_type': 'Unknown'
            })

        if len(facets) == 0:
            # If nothing at all was clustered, try once with a looser angle
            if __retry < MAX_AUTO_RETRIES:
                print(f"[{target.name}] No facets at all — retrying with angle_tol={angle_tol_deg*2:.2f}°")
                return self.extract_facets(
                    target,
                    angle_tol_deg=angle_tol_deg * 2.0,
                    min_faces_per_facet=max(1, min_faces_per_facet // 2),
                    min_relative_area=min_relative_area * 0.25,
                    consider_girdle_as=consider_girdle_as,
                    girdle_nearness_tol=girdle_nearness_tol * 0.75,
                    robust_girdle=robust_girdle,
                    __retry=__retry + 1,
                )
            return []

        # Remove tiny facets relative to typical area
        areas = np.array([f['footprint_area'] for f in facets], dtype=float)
        positive = areas[areas > 0]
        median_area = float(np.median(positive)) if positive.size else 0.0
        abs_area_thresh = max(1e-8 * diag * diag, min_relative_area * (median_area if median_area > 0 else 1.0))
        facets = [f for f in facets if f['footprint_area'] >= abs_area_thresh and len(f['faces_idx']) >= min_faces_per_facet]
        if not facets:
            # Try relaxing once more if we filtered everything out
            if __retry < MAX_AUTO_RETRIES:
                print(f"[{target.name}] All facets filtered by area — retrying with looser thresholds")
                return self.extract_facets(
                    target,
                    angle_tol_deg=angle_tol_deg * 1.5,
                    min_faces_per_facet=1,
                    min_relative_area=min_relative_area * 0.25,
                    consider_girdle_as=consider_girdle_as,
                    girdle_nearness_tol=girdle_nearness_tol,
                    robust_girdle=robust_girdle,
                    __retry=__retry + 1,
                )
            return []

        # --- Fit girdle plane on centroids -----------------------------------------
        all_centroids = np.array([f['centroid'] for f in facets], dtype=float)
        cg, ng = _fit_plane_svd(all_centroids)

        # Candidates "near" the girdle plane (scale-aware)
        d0 = (all_centroids - cg) @ ng
        near_mask = np.abs(d0) <= girdle_nearness_tol

        if robust_girdle and np.count_nonzero(near_mask) >= 6:
            try:
                cg, ng, _ = _fit_plane_ransac(
                    all_centroids[near_mask],
                    n_iter=500,
                    inlier_tol=girdle_nearness_tol,
                    min_inliers_ratio=0.5,
                    random_state=777,
                )
            except Exception as e:
                print("RANSAC girdle refine failed, using SVD:", e)

        # Orient +ng toward the larger parallel crown-like side
        parallel_thresh = 0.92
        sum_plus = 0.0
        sum_minus = 0.0
        for f, d in zip(facets, (all_centroids - cg) @ ng):
            a = float(f.get('footprint_area', 0.0))
            align = float(np.dot(_norm(f['normal']), ng))
            if d > girdle_nearness_tol and align > parallel_thresh:
                sum_plus += a
            elif d < -girdle_nearness_tol and align < -parallel_thresh:
                sum_minus += a
        if sum_minus > sum_plus:
            ng = -ng  # ensure +ng points toward crown/table side

        # --- Manual override: optional UI checkbox to flip crown/pavilion ----------
        if getattr(self, "flip_crown_cb", None) and self.flip_crown_cb.isChecked():
            ng = -ng

        # --- Classify Crown / Pavilion / Girdle ------------------------------------
        for f in facets:
            d = float(np.dot(f['centroid'] - cg, ng))
            if abs(d) <= girdle_nearness_tol:
                f['facet_type'] = consider_girdle_as  # 'Girdle' or 'Touching Girdle'
            elif d > 0:
                f['facet_type'] = 'Crown'
            else:
                f['facet_type'] = 'Pavilion'

            # Orient facet normals consistently with girdle normal direction
            dotn = float(np.dot(f['normal'], ng))
            if f['facet_type'] == 'Crown' and dotn < 0:
                f['normal'] = -f['normal']
            elif f['facet_type'] == 'Pavilion' and dotn > 0:
                f['normal'] = -f['normal']

        non_girdle_facets = [f for f in facets if f['facet_type'] != 'Girdle']

        # If everything was classified as Girdle, auto-relax & retry
        if len(non_girdle_facets) == 0 and __retry < MAX_AUTO_RETRIES:
            print(f"[{target.name}] All facets landed in Girdle (diag={diag:.4f}, tol={girdle_nearness_tol:.4f}). "
                f"Retrying with tighter girdle tol and looser angle.")
            return self.extract_facets(
                target,
                angle_tol_deg=max(angle_tol_deg * 1.5, angle_tol_deg + 1.0),
                min_faces_per_facet=max(1, min_faces_per_facet // 2),
                min_relative_area=min_relative_area,
                consider_girdle_as='Touching Girdle',           # keep them if still near
                girdle_nearness_tol=girdle_nearness_tol * 0.5,  # make plane-near stricter
                robust_girdle=robust_girdle,
                __retry=__retry + 1,
            )

        print(f"[{target.name}] Total facets before exclusion: {len(facets)}")
        print(f"[{target.name}] Excluded girdle facets count: {len(facets) - len(non_girdle_facets)}")
        print(f"[{target.name}] Total non-girdle facets: {len(non_girdle_facets)}")

        # (Optional) refined polished labels
        if getattr(target, "name", "").lower() == "polished" and hasattr(self, "_refine_polished_labels"):
            try:
                self._refine_polished_labels(non_girdle_facets, cg, ng)
            except Exception as e:
                print("Polished facet refinement failed:", e)

        return non_girdle_facets

    def _update_visible_facet_ids(self):
        tgt = self.get_active_target()
        # --- ADD 'Table' and 'Culet' so they appear in the spin / navigation ---
        allowed = {
            'Crown','Pavilion','Bezel','Star','Upper Girdle','Lower Girdle',
            'Arrow','Main','Table','Culet'
        }
        tgt.visible_facet_ids = [i for i, f in enumerate(tgt.facets) if f.get('facet_type') in allowed]
        has_any = len(tgt.visible_facet_ids) > 0
        self.facet_spin.setEnabled(has_any)
        self.prev_btn.setEnabled(has_any)
        self.next_btn.setEnabled(has_any)
        self.compute_selected_btn.setEnabled(has_any)
        self.build_extruded_btn.setEnabled(has_any)

        if has_any:
            self.facet_spin.setMaximum(len(tgt.visible_facet_ids) - 1)
            self.facet_spin.setValue(0)
            self.current_facet = 0
        else:
            self.facet_spin.setMaximum(0)
            self.facet_spin.setValue(0)
        self.current_facet = 0

    def _actual_fid(self, vis_idx: int):
        tgt = self.get_active_target()
        if not tgt.visible_facet_ids:
            return None
        vis_idx = max(0, min(vis_idx, len(tgt.visible_facet_ids) - 1))
        return tgt.visible_facet_ids[vis_idx]

    # ---------------- Adaptive voxelization ----------------
    def compute_facet_volume_adaptive(self, centroid, normal, u, v, hull2d,
                                      other_np, other_kd, max_depth,
                                      min_tile=0.25,   # local units
                                      max_depth_err=0.01, # stop subdividing when depth range small
                                      max_level=6):
        """
        Returns (tiles, volume). tiles = [ (x0,y0,x1,y1, d_mean) ] in facet-local 2D.
        """
        if hull2d is None or hull2d.shape[0]<3 or max_depth<=1e-12:
            return [], 0.0

        poly = Path(hull2d)
        min_x, min_y = np.min(hull2d, axis=0)
        max_x, max_y = np.max(hull2d, axis=0)

        def depth_at_local(x, y):
            p0 = centroid + u*x + v*y
            steps = 8
            zs = np.linspace(0.0, max_depth, steps)
            pts = p0[None,:] + zs[:,None]*normal[None,:]
            dists,_ = other_kd.query(pts)
            thr = max((max_x-min_x + max_y-min_y)/200.0, 1e-3)
            mask = dists < thr
            if not np.any(mask):
                return 0.0
            return float(zs[np.where(mask)[0].max()])

        tiles = []
        vol = 0.0

        def recurse(x0,y0,x1,y1, level):
            cx = 0.5*(x0+x1); cy = 0.5*(y0+y1)
            samples = [(x0,y0),(x1,y0),(x1,y1),(x0,y1),(cx,cy)]
            if not any(poly.contains_point(s) for s in samples):
                return
            ds = [depth_at_local(x,y) for (x,y) in samples]
            dmin, dmax = min(ds), max(ds)
            if level>=max_level or max(x1-x0, y1-y0)<=min_tile or (dmax-dmin)<=max_depth_err:
                dmean = float(np.mean(ds))
                tiles.append((x0,y0,x1,y1,dmean))
                area = max((x1-x0)*(y1-y0), 0.0)
                nonlocal vol
                vol += area * dmean
                return
            mx, my = cx, cy
            recurse(x0,y0,mx,my,level+1)
            recurse(mx,y0,x1,my,level+1)
            recurse(mx,my,x1,y1,level+1)
            recurse(x0,my,mx,y1,level+1)

        recurse(min_x, min_y, max_x, max_y, 0)
        return tiles, vol

    # ---------------- Uniform per-facet voxel integration (kept for fallback/display) ----------------
    def compute_facet_volume_voxel(self, centroid, normal, u, v, hull2d, other_pts_np, other_kd, max_depth, grid_cells):

        # bounding box in local coords
        if hull2d is None or hull2d.shape[0] < 3:
            return None, None, None, 0.0, None, None

        min_x, min_y = np.min(hull2d, axis=0)
        max_x, max_y = np.max(hull2d, axis=0)

        # choose nx, ny preserving aspect ratio
        longer = max(max_x - min_x, max_y - min_y)
        nx = max(1, int(math.ceil((max_x - min_x) / longer * grid_cells))) if longer > 0 else 1
        ny = max(1, int(math.ceil((max_y - min_y) / longer * grid_cells))) if longer > 0 else 1

        xs = (np.linspace(min_x + (max_x - min_x) / (2 * nx),
                        max_x - (max_x - min_x) / (2 * nx), nx)
            if nx > 1 else np.array([(min_x + max_x) / 2.0], dtype=float))
        ys = (np.linspace(min_y + (max_y - min_y) / (2 * ny),
                        max_y - (max_y - min_y) / (2 * ny), ny)
            if ny > 1 else np.array([(min_y + max_y) / 2.0], dtype=float))

        depth_map = np.zeros((ny, nx), dtype=np.float32)
        polygon = Path(hull2d)

        dx = (max_x - min_x) / nx if nx > 0 else 0.0
        dy = (max_y - min_y) / ny if ny > 0 else 0.0
        cell_area = max(dx * dy, 0.0)

        if dx <= 0 or dy <= 0:
            step = max_depth / 8.0 if max_depth > 0 else 1e-6
        else:
            step = min(dx, dy) / 2.0
        if step <= 1e-9:
            step = max_depth / 8.0 if max_depth > 0 else 1e-6

        nz = max(2, int(math.ceil(max_depth / step)) + 2)
        zs = np.linspace(step / 2.0, max_depth + step / 2.0, nz)

        dist_threshold = math.sqrt(dx * dx + dy * dy + (step * step)) * 1.5 if (dx > 0 and dy > 0) else step * 1.5

        if other_kd is None:
            other_kd = cKDTree(other_pts_np)
        elif not isinstance(other_kd, cKDTree):
            other_kd = cKDTree(other_pts_np)

        for iy, y in enumerate(ys):
            XY = np.stack([xs, np.full_like(xs, y)], axis=1)  # (nx, 2)
            inside_xy = polygon.contains_points(XY)
            if not np.any(inside_xy):
                continue

            xs_in = xs[inside_xy]
            if xs_in.size == 0:
                continue

            base_worlds = np.stack([centroid + u * x + v * y for x in xs_in], axis=0)
            pts_row = base_worlds[:, None, :] + zs[None, :, None] * normal[None, None, :]
            pts_row_flat = pts_row.reshape(-1, 3)

            dists, _ = other_kd.query(pts_row_flat)
            inside_flat = (dists < dist_threshold).reshape(xs_in.shape[0], nz)

            for j, x in enumerate(xs_in):
                col_inside = inside_flat[j]
                if not np.any(col_inside):
                    continue
                idx_last = np.where(col_inside)[0].max()
                thickness = float(zs[idx_last])
                ix_candidates = np.where(np.isclose(xs, x))[0]
                if ix_candidates.size == 0:
                    ix_global = int(np.argmin(np.abs(xs - x)))
                else:
                    ix_global = int(ix_candidates[0])
                depth_map[iy, ix_global] = thickness

        voxel_volume = float(np.sum(depth_map) * cell_area)
        return depth_map, xs, ys, voxel_volume, dx, dy

    # ---------------- Suggest per-facet polishing passes (data-driven) ----------------
    def suggest_passes_smart(self, depths, footprint_area, n_passes=3):
        depths = np.asarray(depths, float)
        depths = depths[depths>0]
        if depths.size==0:
            return [("Coarse",0.0,0.0),("Medium",0.0,0.0),("Fine",0.0,0.0)][:n_passes]
        try:
            from sklearn.mixture import GaussianMixture
            X = depths.reshape(-1,1)
            gmm = GaussianMixture(n_components=n_passes, random_state=0).fit(X)
            labels = gmm.predict(X)
            order = np.argsort(gmm.means_.ravel())[::-1]  # high depth = coarse
            name_map = {0:"Coarse",1:"Medium",2:"Fine"}
            passes=[]
            for rank,k in enumerate(order[:n_passes]):
                d_mean = float(X[labels==k].mean()) if np.any(labels==k) else 0.0
                vol = footprint_area * d_mean
                passes.append((name_map.get(rank, f"Pass{rank+1}"), d_mean, vol))
            return passes
        except Exception:
            # fallback: quantiles
            qs = np.quantile(depths, [0.66, 0.33, 0.0])
            bins = [depths>=qs[0], (depths<qs[0])&(depths>=qs[1]), depths<qs[1]]
            names = ["Coarse","Medium","Fine"]
            out=[]
            for i,mask in enumerate(bins[:n_passes]):
                d = float(depths[mask].mean()) if np.any(mask) else 0.0
                out.append((names[i], d, footprint_area*d))
            return out

    # ---------------- Time estimates from passes ----------------
    def estimate_times_for_passes(self, passes):
        rates = {"Coarse":MRR_COARSE,"Medium":MRR_MEDIUM,"Fine":MRR_FINE}
        out=[]
        for name, d, vol in passes:
            mrr = rates.get(name, MRR_MEDIUM)
            minutes = (vol / max(mrr,1e-9)) if vol>0 else 0.0
            seconds = minutes*60.0 + SETUP_PENALTY_SEC
            out.append((name, d, vol, seconds))
        return out

    # ---------------- Compute all facets (summary + optional voxel integration) ----------------
    def compute_all_facets(self):
        active = self.get_active_target()
        other = self.get_other_target()

        if active.mesh is None or other.mesh is None:
            QtWidgets.QMessageBox.warning(self, "Error", "Load both meshes first")
            return

        # extract facets with advanced method
        active.facets = self.extract_facets(active, angle_tol_deg=1.0)

        active.facets = [f for f in active.facets if f['facet_type'] != 'Girdle']
        if len(active.facets) == 0:
            QtWidgets.QMessageBox.warning(self, "No facets", f"Couldn't extract facets from {active.name} mesh")
            self.update_status("Compute all: no facets")
            return

        other_np = np.asarray(other.mesh.points)
        other_cp = to_cp(other_np)
        other_kd = cKDTree(other_np)

        grid_cells = int(self.grid_cells_spin.value())
        use_voxel = bool(self.use_voxel_cb.isChecked())
        use_adaptive = bool(self.use_adaptive_cb.isChecked())

        active.facet_results = {}

        for fid, f in enumerate(active.facets):
            try:
                pts = np.asarray(f['points'])
                centroid = np.asarray(f['centroid'])
                normal = _norm(np.asarray(f['normal']))

                # local basis
                arbitrary = np.array([1.0, 0.0, 0.0])
                if abs(np.dot(arbitrary, normal)) > 0.9:
                    arbitrary = np.array([0.0, 1.0, 0.0])
                u = _norm(np.cross(normal, arbitrary))
                v = _norm(np.cross(normal, u))

                proj2d = np.column_stack([(pts - centroid) @ u, (pts - centroid) @ v])
                hull2d = self._facet_outline_polygon_2d(active.mesh, f['faces_idx'], centroid, u, v)
                if hull2d is None or len(hull2d) < 3:
                    try:
                        ch = ConvexHull(proj2d)
                        hull2d = proj2d[ch.vertices]
                    except Exception:
                        hull2d = proj2d

                if hull2d is None or hull2d.shape[0] < 3:
                    active.facet_results[fid] = {
                        'max_depth': 0.0, 'mean_depth': 0.0, 'approx_volume': 0.0, 'voxel_volume': 0.0,
                        'points_inside_idx': np.array([], dtype=int), 'centroid': centroid, 'normal': normal, 'u': u, 'v': v,
                        'hull2d': np.zeros((0, 2)), 'footprint_area': 0.0, 'perimeter': 0.0, 'depths_array': np.array([]),
                        'depth_map': None, 'xs': None, 'ys': None, 'dx': None, 'dy': None, 'passes': self.suggest_passes_smart(np.array([]), 0.0),
                        'planarity_rms': f.get('planarity_rms', 0.0), 'depth_p95': 0.0, 'depth_rms': 0.0,
                        'pass_times_sec': [], 'time_total_sec': 0.0, 'adaptive_tiles': []
                    }
                    continue

                poly = Path(hull2d)

                # project other points into local coords
                if CUPY_AVAILABLE:
                    centroid_cp = cp.asarray(centroid); u_cp = cp.asarray(u); v_cp = cp.asarray(v)
                    rel_cp = other_cp - centroid_cp
                    rx_cp = rel_cp @ u_cp; ry_cp = rel_cp @ v_cp
                    other_2d = to_np(cp.stack([rx_cp, ry_cp], axis=1))
                else:
                    rel = other_np - centroid
                    rx = rel @ u; ry = rel @ v
                    other_2d = np.column_stack([rx, ry])

                inside_mask = poly.contains_points(other_2d)
                inside_idx = np.where(inside_mask)[0]

                if inside_idx.size == 0:
    # perimeter from the facet hull in world coords
                    hull_world = np.array([centroid + u * p[0] + v * p[1] for p in hull2d])
                    perimeter = float(np.sum(np.linalg.norm(np.roll(hull_world, -1, axis=0) - hull_world, axis=1)))

                    active.facet_results[fid] = {
                        'max_depth': 0.0,
                        'mean_depth': 0.0,
                        'approx_volume': 0.0,
                        'voxel_volume': 0.0,
                        'points_inside_idx': inside_idx,
                        'centroid': centroid,
                        'normal': normal,
                        'u': u,
                        'v': v,
                        'hull2d': hull2d,
                        'footprint_area': float(ConvexHull(hull2d).volume) if hull2d.shape[0] >= 3 else 0.0,  # << keep area
                        'perimeter': perimeter,
                        'depths_array': np.array([]),
                        'depth_map': None, 'xs': None, 'ys': None, 'dx': None, 'dy': None,
                        'passes': self.suggest_passes_smart(np.array([]), float(ConvexHull(hull2d).volume) if hull2d.shape[0] >= 3 else 0.0),
                        'planarity_rms': f.get('planarity_rms', 0.0),
                        'depth_p95': 0.0,
                        'depth_rms': 0.0,
                        'pass_times_sec': [],
                        'time_total_sec': 0.0,
                        'adaptive_tiles': []
                    }
                    continue

                inside_pts = other_np[inside_idx]
                signed = np.dot(inside_pts - centroid, normal)
                depths = np.maximum(0.0, signed)
                max_depth = float(np.max(depths)) if depths.size > 0 else 0.0
                mean_depth = float(np.mean(depths)) if depths.size > 0 else 0.0
                p95 = float(np.percentile(depths, 95)) if depths.size > 0 else 0.0
                rms = float(np.sqrt(np.mean((depths - mean_depth)**2))) if depths.size > 0 else 0.0

                # footprint area (2D)
                try:
                    fh = ConvexHull(hull2d)
                    footprint_area = float(fh.volume)
                except Exception:
                    xy = hull2d
                    x, y = xy[:, 0], xy[:, 1]
                    footprint_area = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))

                approx_vol = footprint_area * mean_depth

                # perimeter world coords
                hull_world = np.array([centroid + u * p[0] + v * p[1] for p in hull2d])
                perimeter = float(np.sum(np.linalg.norm(np.roll(hull_world, -1, axis=0) - hull_world, axis=1)))

                voxel_vol = 0.0
                depth_map = None; xs = ys = None; dx = dy = None
                adaptive_tiles = []

                if use_voxel and max_depth > 1e-12:
                    if use_adaptive:
                        adaptive_tiles, voxel_vol = self.compute_facet_volume_adaptive(
                            centroid, normal, u, v, hull2d, other_np, other_kd, max_depth,
                            min_tile=0.25, max_depth_err=0.01, max_level=6
                        )
                    else:
                        depth_map, xs, ys, voxel_vol, dx, dy = self.compute_facet_volume_voxel(
                            centroid, normal, u, v, hull2d, other_np, other_kd, max_depth, grid_cells
                        )

                passes = self.suggest_passes_smart(depths, footprint_area, n_passes=3)
                times = self.estimate_times_for_passes(passes)
                total_time = float(sum(t for (_,_,_,t) in times))

                active.facet_results[fid] = {
                    'max_depth': max_depth,
                    'mean_depth': mean_depth,
                    'approx_volume': approx_vol,
                    'voxel_volume': voxel_vol,
                    'points_inside_idx': inside_idx,
                    'centroid': centroid,
                    'normal': normal,
                    'u': u,
                    'v': v,
                    'hull2d': hull2d,
                    'footprint_area': footprint_area,
                    'perimeter': perimeter,
                    'depths_array': depths,
                    'depth_map': depth_map,
                    'xs': xs,
                    'ys': ys,
                    'dx': dx,
                    'dy': dy,
                    'passes': passes,
                    'pass_times_sec': times,
                    'time_total_sec': total_time,
                    'depth_p95': p95,
                    'depth_rms': rms,
                    'planarity_rms': f.get('planarity_rms', 0.0),
                    'adaptive_tiles': adaptive_tiles
                }

            except Exception as e:
                print(f"Error computing facet {fid} on {active.name}:", e)
                traceback.print_exc()
                active.facet_results[fid] = {
                    'max_depth': 0.0, 'mean_depth': 0.0, 'approx_volume': 0.0, 'voxel_volume': 0.0,
                    'points_inside_idx': np.array([], dtype=int), 'centroid': None, 'normal': None,
                    'u': None, 'v': None, 'hull2d': np.zeros((0, 2)),
                    'footprint_area': 0.0, 'perimeter': 0.0, 'depths_array': np.array([]),
                    'depth_map': None, 'xs': None, 'ys': None, 'dx': None, 'dy': None, 'passes': [],
                    'pass_times_sec': [], 'time_total_sec': 0.0, 'depth_p95': 0.0, 'depth_rms': 0.0,
                    'planarity_rms': 0.0, 'adaptive_tiles': []
                }

        # finalize UI
        nfac = len(active.facets)
        self.facet_spin.setMaximum(max(0, nfac - 1))
        self.facet_spin.setValue(0)
        self.current_facet = 0
        self.prev_btn.setEnabled(True); self.next_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)
        self.generate_seq_btn.setEnabled(True)
        self.build_volume_btn.setEnabled(True)

        # build pass point clouds (for toggles) for active
        self.build_pass_point_clouds()

        # enable pass toggles
        self.show_coarse_cb.setEnabled(True)
        self.show_medium_cb.setEnabled(True)
        self.show_fine_cb.setEnabled(True)

        try:
            self.plotter.reset_camera()
        except Exception:
            pass

        QtWidgets.QMessageBox.information(self, "Done", f"Computed {nfac} facets on {active.name} (voxel integration used: {use_voxel}, adaptive: {use_adaptive})")

        # Paint heatmap if requested
        self.paint_active_heatmap(active, other)
        if not self.show_heatmap_cb.isChecked():
            self.toggle_heatmap_visibility()

        self.show_selected_facet(0)
        self._apply_azimuth_coloring_if_available(active)

        if getattr(self, "show_labels_cb", None) and self.show_labels_cb.isChecked():
            self.build_clickable_facet_labels()
        self.update_status(f"Computed all facets ({nfac})")
        self._rebuild_axes_for_targets()

    # ---------------- Compute selected facet (detailed, active) ----------------
    def compute_selected_facet(self):
        active = self.get_active_target()
        other = self.get_other_target()

        if active.mesh is None or other.mesh is None:
            QtWidgets.QMessageBox.warning(self, "Error", "Load both meshes first")
            return

        if not active.facets:
            active.facets = self.extract_facets(active, angle_tol_deg=1.0)

            if not active.facets:
                QtWidgets.QMessageBox.warning(self, "No facets", f"Couldn't extract facets from {active.name} mesh.")
                self.update_status("Compute selected: no facets")
                return

        fid_vis = int(self.facet_spin.value())
        if fid_vis < 0 or fid_vis >= len(active.visible_facet_ids):
            QtWidgets.QMessageBox.warning(self, "Invalid facet", "Choose a valid facet index")
            return
        fid = active.visible_facet_ids[fid_vis]

        if fid in active.facet_results and active.facet_results[fid].get('hull2d', None) is not None:
            self.export_selected_csv_btn.setEnabled(True)
            self.show_selected_facet(fid)
            self.update_status(f"Selected facet ready (fid={fid})")
            return

        f = active.facets[fid]
        other_np = np.asarray(other.mesh.points)
        other_kd = cKDTree(other_np)

        pts = np.asarray(f['points'])
        centroid = np.asarray(f['centroid'])
        normal = _norm(np.asarray(f['normal']))

        arbitrary = np.array([1.0, 0.0, 0.0])
        if abs(np.dot(arbitrary, normal)) > 0.9:
            arbitrary = np.array([0.0, 1.0, 0.0])
        u = _norm(np.cross(normal, arbitrary))
        v = _norm(np.cross(normal, u))

        proj2d = np.column_stack([(pts - centroid) @ u, (pts - centroid) @ v])
        try:
            ch = ConvexHull(proj2d)
            hull2d = proj2d[ch.vertices]
        except Exception:
            hull2d = proj2d

        if hull2d.shape[0] < 3:
            QtWidgets.QMessageBox.information(self, "Degenerate facet", "Facet hull has fewer than 3 vertices")
            return

        poly = Path(hull2d)
        # project other points
        if CUPY_AVAILABLE:
            centroid_cp = cp.asarray(centroid); u_cp = cp.asarray(u); v_cp = cp.asarray(v)
            rel_cp = to_cp(other_np) - centroid_cp
            rx_cp = rel_cp @ u_cp; ry_cp = rel_cp @ v_cp
            other_2d = to_np(cp.stack([rx_cp, ry_cp], axis=1))
        else:
            rel = other_np - centroid
            rx = rel @ u; ry = rel @ v
            other_2d = np.column_stack([rx, ry])

        inside_mask = poly.contains_points(other_2d)
        inside_idx = np.where(inside_mask)[0]              # <— important
        inside_pts = other_np[inside_idx] if inside_idx.size > 0 else np.zeros((0, 3))

        signed = np.dot(inside_pts - centroid, normal) if inside_pts.size > 0 else np.array([])
        depths = np.maximum(0.0, signed) if inside_pts.size > 0 else np.array([])
        max_depth = float(np.max(depths)) if depths.size > 0 else 0.0
        mean_depth = float(np.mean(depths)) if depths.size > 0 else 0.0
        p95 = float(np.percentile(depths, 95)) if depths.size > 0 else 0.0
        rms = float(np.sqrt(np.mean((depths - mean_depth)**2))) if depths.size > 0 else 0.0

        # footprint area
        try:
            fh = ConvexHull(hull2d)
            footprint_area = float(fh.volume)
        except Exception:
            xy = hull2d
            x, y = xy[:, 0], xy[:, 1]
            footprint_area = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))

        approx_vol = footprint_area * mean_depth

        hull_world = np.array([centroid + u * p[0] + v * p[1] for p in hull2d])
        perimeter = float(np.sum(np.linalg.norm(np.roll(hull_world, -1, axis=0) - hull_world, axis=1)))

        passes = self.suggest_passes_smart(depths, footprint_area, n_passes=3)
        times = self.estimate_times_for_passes(passes)
        total_time = float(sum(t for (_,_,_,t) in times))

        res = {
            'max_depth': max_depth,
            'mean_depth': mean_depth,
            'approx_volume': approx_vol,
            'voxel_volume': 0.0,
            'points_inside_idx': inside_idx,
            'centroid': centroid,
            'normal': normal,
            'u': u,
            'v': v,
            'hull2d': hull2d,
            'footprint_area': footprint_area,
            'perimeter': perimeter,
            'depths_array': depths,
            'depth_map': None,
            'xs': None,
            'ys': None,
            'dx': None,
            'dy': None,
            'passes': passes,
            'pass_times_sec': times,
            'time_total_sec': total_time,
            'depth_p95': p95,
            'depth_rms': rms,
            'planarity_rms': f.get('planarity_rms', 0.0),
            'adaptive_tiles': []
        }

        active.facet_results[fid] = res
        self.export_selected_csv_btn.setEnabled(True)

        # update pass clouds to include this facet's points if needed
        self.build_pass_point_clouds()
        self.show_selected_facet(fid)
        self.update_status(f"Computed selected facet (fid={fid})")
        # Working Facet window: keep in sync
        if getattr(self, "working_win", None):
            try:
                self.working_win.refresh()
            except Exception:
                pass

    def _remove_azimuth_legend(self):
        try:
            if hasattr(self, "_azimuth_scalar_bar") and self._azimuth_scalar_bar is not None:
                self.plotter.remove_scalar_bar(self._azimuth_scalar_bar)
        except Exception:
            pass
        self._azimuth_scalar_bar = None

    def _ensure_azimuth_legend(self, title="Azimuth (°)", cmap="hsv"):
        try:
            self._remove_azimuth_legend()
            self._azimuth_scalar_bar = self.plotter.add_scalar_bar(
                title=title, n_labels=5, clim=(0.0, 360.0), cmap=cmap,
                position_x=0.02, position_y=0.02, width=0.26, height=0.08,
                italic=False, bold=False, title_font_size=10, label_font_size=9,
            )
        except Exception:
            self._azimuth_scalar_bar = None

    def on_toggle_az_legend(self, *_):
        if getattr(self, "show_az_legend_cb", None) and self.show_az_legend_cb.isChecked():
            # only show if azimuth coloring exists
            tgt = self.get_active_target()
            if tgt and tgt.facets and any(f.get('azimuth_deg') is not None for f in tgt.facets):
                self._ensure_azimuth_legend()
        else:
            self._remove_azimuth_legend()


    def _apply_azimuth_coloring_if_available(self, target: 'TargetBundle', cmap: str = "hsv"):
        """Color by facet azimuth; keep POLISHED opaque (solid), respect see-through only for ROUGH."""
        try:
            if target is None or target.mesh is None or not target.facets:
                self._remove_azimuth_legend()
                return
            if all(f.get('azimuth_deg') is None for f in target.facets):
                self._remove_azimuth_legend()
                return

            mesh_for_view = target.view_mesh if target.view_mesh is not None else target.mesh
            mesh_az, az_name = build_azimuth_cell_scalars(mesh_for_view, target.facets)

            # ✅ Force polished to be solid/opaque; only rough follows the see-through toggle.
            if str(target.name).lower() == "polished":
                opacity = 0.98
            else:
                opacity = 0.25 if self.see_through_cb.isChecked() else 0.95

            # Replace existing actor
            if target.actor is not None:
                try:
                    self.plotter.remove_actor(target.actor)
                except Exception:
                    pass
                target.actor = None

            # Add colored mesh (flat shading, no wireframe, hide back faces)
            target.actor = self.plotter.add_mesh(
                mesh_az,
                scalars=az_name,
                cmap=cmap,
                clim=(0.0, 360.0),
                nan_color=(200, 200, 200),
                opacity=float(opacity),
                smooth_shading=False,
                show_edges=False,
                render_lines_as_tubes=False,
                lighting=True,
                ambient=0.25,
                diffuse=0.8,
                specular=0.15,
                specular_power=20.0,
                culling='back',          # prevents inside faces from bleeding through
                show_scalar_bar=False,
            )

            # Legend, only if requested and azimuth exists
            if getattr(self, "show_az_legend_cb", None) and self.show_az_legend_cb.isChecked():
                self._ensure_azimuth_legend(cmap=cmap)
            else:
                self._remove_azimuth_legend()

        except Exception:
            return


    # ==== NEW: per-facet reference & rotation glyphs ============================

    def _draw_azimuth_reference_glyphs(self, active: 'TargetBundle', fid: int, res: dict):
        """
        Draws:
        - a white arrow along the TABLE reference axis (table normal projected to girdle plane)
        - a small yellow arc + arrowhead showing the positive azimuth direction (RH about girdle normal)
        """
        try:
            # clean up old glyphs for this target
            if not hasattr(active, "az_glyph_actors"):
                active.az_glyph_actors = []
            for a in active.az_glyph_actors:
                try: self.plotter.remove_actor(a)
                except Exception: pass
            active.az_glyph_actors = []

            if not active.facets:
                return

            # girdle plane and table facet
            ng, cg = _compute_girdle_plane_from_facets(active.facets)
            ng = _norm(np.asarray(ng, float))
            table = _pick_table_facet(active.facets)
            if table is None:
                return
            tnorm = _norm(np.asarray(table['normal'], float))

            # reference axis = project table normal into girdle plane
            ref = _project_to_plane(tnorm, ng)
            if np.linalg.norm(ref) < 1e-14:
                # stable fallback axis
                t = np.array([1.0, 0.0, 0.0])
                if abs(np.dot(t, ng)) > 0.95: t = np.array([0.0, 1.0, 0.0])
                ref = _project_to_plane(t, ng)
            ref = _norm(ref)

            # facet-local size for scaling
            hull2d = res.get('hull2d', None)
            centroid = np.asarray(res.get('centroid'), float)
            if hull2d is None or hull2d.shape[0] < 3:
                return
            ext_x = float(np.max(hull2d[:,0]) - np.min(hull2d[:,0]))
            ext_y = float(np.max(hull2d[:,1]) - np.min(hull2d[:,1]))
            L = max(ext_x, ext_y)
            if not np.isfinite(L) or L <= 0:
                L = 1.0
            # arrow/arc scales
            ref_len = 0.35 * L
            arc_r   = 0.40 * L
            arc_deg = 70.0

            # --- white reference arrow ---
            try:
                ref_arrow = pv.Arrow(
                    start=centroid,
                    direction=ref,
                    tip_length=0.30,
                    tip_radius=0.05,
                    shaft_radius=0.015,
                    scale=ref_len,
                )
                a1 = self.plotter.add_mesh(
                    ref_arrow, color="white", opacity=0.95, lighting=False,
                    name=f"{active.name}_az_refarrow_{fid}"
                )
                active.az_glyph_actors.append(a1)
            except Exception:
                pass

            # --- yellow positive-azimuth arc + arrowhead ---
            # Build orthonormal basis on the girdle plane: a = ref, b = ng x a
            a = ref
            b = _norm(np.cross(ng, a))
            if np.linalg.norm(b) < 1e-12:
                # degenerate; pick any perpendicular
                tmp = np.array([1.0, 0.0, 0.0])
                if abs(np.dot(tmp, ng)) > 0.95: tmp = np.array([0.0, 1.0, 0.0])
                a = _norm(_project_to_plane(tmp, ng))
                b = _norm(np.cross(ng, a))

            thetas = np.linspace(0.0, np.deg2rad(arc_deg), 64)
            arc_pts = np.array([centroid + arc_r*(np.cos(t)*a + np.sin(t)*b) for t in thetas], float)
            try:
                arc_line = pv.Spline(arc_pts, n_points=arc_pts.shape[0])
            except Exception:
                # fallback: polyline
                arc_line = pv.PolyData(arc_pts)
                n = arc_pts.shape[0]
                lines = np.hstack([[n], np.arange(n, dtype=np.int64)])
                arc_line.lines = lines

            a2 = self.plotter.add_mesh(
                arc_line, color="yellow", line_width=3, lighting=False,
                name=f"{active.name}_az_arc_{fid}"
            )
            active.az_glyph_actors.append(a2)

            # arrowhead at arc tip: tangent direction
            t_end = thetas[-1]
            tangent = _norm(-np.sin(t_end)*a + np.cos(t_end)*b)
            tip_start = arc_pts[-1]
            try:
                tip_arrow = pv.Arrow(
                    start=tip_start,
                    direction=tangent,
                    tip_length=0.45,
                    tip_radius=0.06,
                    shaft_radius=0.0,   # triangle-ish look
                    scale=0.18 * L,
                )
                a3 = self.plotter.add_mesh(
                    tip_arrow, color="yellow", opacity=0.95, lighting=False,
                    name=f"{active.name}_az_arctip_{fid}"
                )
                active.az_glyph_actors.append(a3)
            except Exception:
                pass

        except Exception:
            # don't let glyph errors break facet display
            return

    def _clear_axes(self, target: 'TargetBundle'):
        if target is None:
            return
        if target.axes_actors:
            for a in target.axes_actors:
                try: self.plotter.remove_actor(a)
                except Exception: pass
        target.axes_actors = []
        if target.axes_labels_actor is not None:
            try: self.plotter.remove_actor(target.axes_labels_actor)
            except Exception: pass
        target.axes_labels_actor = None

    def _build_diamond_axes(self, target: 'TargetBundle'):
        """
        Draws the standard axes used for a cut diamond:
        • Table axis (T): table facet normal (cyan)
        • Girdle normal (G): normal of girdle plane, oriented toward table (magenta)
        • Azimuth 0° reference: table normal projected into girdle plane (white)
        • Girdle major/minor in-plane axes from PCA (major=red, minor=green)
        • Pavilion/Culet axis: toward culet if detected, else opposite table (yellow)
        All arrows originate at the girdle centroid.
        """
        if target is None or target.mesh is None:
            return

        # wipe previous
        self._clear_axes(target)

        # --- girdle plane & centroid
        facets = target.facets or []
        ng, cg = _compute_girdle_plane_from_facets(facets)
        ng = _norm(np.asarray(ng, float)); cg = np.asarray(cg, float)

        # --- table facet
        table = _pick_table_facet(facets)
        if table is None:
            return
        tnorm = _norm(np.asarray(table['normal'], float))
        # orient girdle normal toward table
        if np.dot(tnorm, ng) < 0:
            ng = -ng

        # --- azimuth 0 reference (table normal projected to girdle plane)
        ref = _project_to_plane(tnorm, ng); 
        if np.linalg.norm(ref) < 1e-12:
            tmp = np.array([1.0,0.0,0.0]); 
            if abs(np.dot(tmp, ng))>0.95: tmp=np.array([0.0,1.0,0.0])
            ref = _project_to_plane(tmp, ng)
        ref = _norm(ref)

        # --- girdle in-plane PCA for major/minor axes
        pts = np.asarray(target.mesh.points, float)
        rel = pts - cg
        rel_in_plane = rel - (rel @ ng)[:, None] * ng
        # Orthonormal basis on girdle plane
        gx = _norm(np.cross(ng, np.array([1.0,0.0,0.0]))); 
        if np.linalg.norm(gx) < 1e-6:
            gx = _norm(np.cross(ng, np.array([0.0,1.0,0.0])))
        gy = _norm(np.cross(ng, gx))
        uv = np.column_stack([rel_in_plane @ gx, rel_in_plane @ gy])
        try:
            C = np.cov(uv.T) if uv.shape[0] >= 3 else np.eye(2)
            w, V2 = np.linalg.eigh(C)
            order = np.argsort(w)[::-1]  # major first
            v_major_2d = V2[:, order[0]]
            v_minor_2d = V2[:, order[1]]
        except Exception:
            v_major_2d = np.array([1.0, 0.0]); v_minor_2d = np.array([0.0, 1.0])
        a_major = _norm(v_major_2d[0]*gx + v_major_2d[1]*gy)
        a_minor = _norm(v_minor_2d[0]*gx + v_minor_2d[1]*gy)

        # --- pavilion/culet axis
        culet = None
        for f in facets:
            if str(f.get('facet_type','')).lower() == 'culet':
                culet = f
                break
        pav_dir = None
        if culet is not None:
            pav_dir = _norm(np.asarray(culet['centroid'], float) - cg)
            # ensure it points generally opposite table normal
            if np.dot(pav_dir, tnorm) > 0:
                pav_dir = -pav_dir
        else:
            pav_dir = -tnorm  # opposite the table axis

        # --- scale
        diag = _mesh_diag(target.mesh)
        L = max(1e-6, 0.25 * diag)  # arrow length

        def add_arrow(start, direction, color, scale=L, tip=0.30, tipr=0.06, shaft=0.018, name=None):
            try:
                arr = pv.Arrow(start=start, direction=direction, tip_length=tip, tip_radius=tipr, shaft_radius=shaft, scale=scale)
                act = self.plotter.add_mesh(arr, color=color, opacity=0.98, lighting=False, name=name)
                target.axes_actors.append(act)
            except Exception:
                pass

        # center for axes
        origin = cg

        # draw arrows
        add_arrow(origin, tnorm,  "cyan",    name=f"{target.name}_axis_table")
        add_arrow(origin,  ng,    "magenta", name=f"{target.name}_axis_girdle_up")
        add_arrow(origin, -ng,    "magenta", name=f"{target.name}_axis_girdle_down")
        add_arrow(origin,  ref,   "white",   name=f"{target.name}_axis_ref0")
        add_arrow(origin,  a_major, "red",   name=f"{target.name}_axis_major")
        add_arrow(origin, -a_major, "red",   name=f"{target.name}_axis_major_neg")
        add_arrow(origin,  a_minor, "green", name=f"{target.name}_axis_minor")
        add_arrow(origin, -a_minor, "green", name=f"{target.name}_axis_minor_neg")
        add_arrow(origin,  pav_dir, "yellow", name=f"{target.name}_axis_pavilion")

        # optional labels
        if getattr(self, "show_axis_labels_cb", None) and self.show_axis_labels_cb.isChecked():
            label_pts = [
                origin + tnorm * (L*1.05),
                origin +  ng   * (L*1.05),
                origin -  ng   * (L*1.05),
                origin +  ref  * (L*1.05),
                origin +  a_major * (L*1.05),
                origin -  a_major * (L*1.05),
                origin +  a_minor * (L*1.05),
                origin -  a_minor * (L*1.05),
                origin +  pav_dir * (L*1.05),
            ]
            texts = ["Table (T)", "Girdle +G", "Girdle -G", "Azimuth 0°", "Major +A", "Major -A", "Minor +B", "Minor -B", "Pavilion/Culet"]
            try:
                target.axes_labels_actor = self.plotter.add_point_labels(
                    label_pts, texts, point_size=0, shape=None, font_size=11,
                    text_color='white', always_visible=True
                )
            except Exception:
                target.axes_labels_actor = None

    def _rebuild_axes_for_targets(self):
        for t in (self.target_polished, self.target_rough):
            self._clear_axes(t)
            if getattr(self, "show_axes_cb", None) and self.show_axes_cb.isChecked() and t.mesh is not None:
                self._build_diamond_axes(t)

    def toggle_axes_visibility(self, *_):
        if not getattr(self, "show_axes_cb", None):
            return
        if self.show_axes_cb.isChecked():
            self._rebuild_axes_for_targets()
        else:
            self._clear_axes(self.target_polished)
            self._clear_axes(self.target_rough)
        try: self.plotter.render()
        except Exception: pass

        # ---------------- Visualization per selected facet (Active) ----------------
    def clear_overlay(self):
        tgt = self.get_active_target()

        # Per-active-target overlays only
        if tgt.facet_poly_actor:
            try: self.plotter.remove_actor(tgt.facet_poly_actor)
            except Exception: pass
            tgt.facet_poly_actor = None

        if tgt.points_actor:
            try: self.plotter.remove_actor(tgt.points_actor)
            except Exception: pass
            tgt.points_actor = None

        if tgt.highlight_actor:
            try: self.plotter.remove_actor(tgt.highlight_actor)
            except Exception: pass
            tgt.highlight_actor = None

        # NEW: remove azimuth glyphs
        if hasattr(tgt, "az_glyph_actors") and tgt.az_glyph_actors:
            for a in tgt.az_glyph_actors:
                try: self.plotter.remove_actor(a)
                except Exception: pass
            tgt.az_glyph_actors = []

        self.clear_dimension_labels()
        self.clear_facet_labels()

    def clear_dimension_labels(self):
        tgt = self.get_active_target()
        if tgt.dim_label_actor:
            try:
                self.plotter.remove_actor(tgt.dim_label_actor)
            except Exception:
                pass
            tgt.dim_label_actor = None

        if tgt.edge_line_actors:
            for a in tgt.edge_line_actors:
                try:
                    self.plotter.remove_actor(a)
                except Exception:
                    pass
            tgt.edge_line_actors = []

    def refresh_selected_overlay(self):
        self.show_selected_facet(self.current_facet)

    def show_selected_facet(self, fid_or_vis_idx):
        if getattr(self, 'calc_locked', False):
            self.update_status('Facet calculations locked')
            return

        active = self.get_active_target()
        other = self.get_other_target()

        # Clear any previous per-selected overlays
        self.clear_overlay()
        if not active.facets:
            return

        # Decide whether we got an actual facet id or a visible index
        if isinstance(fid_or_vis_idx, int) and fid_or_vis_idx in getattr(active, "visible_facet_ids", []):
            # Treat as actual facet id
            fid = fid_or_vis_idx
            try:
                vis_idx = active.visible_facet_ids.index(fid)
                self.facet_spin.setValue(vis_idx)
            except ValueError:
                pass
        else:
            # Treat as visible index
            if not active.visible_facet_ids:
                return
            vis_idx = max(0, min(int(fid_or_vis_idx), len(active.visible_facet_ids) - 1))
            fid = active.visible_facet_ids[vis_idx]

        self.current_facet = fid

        # If this facet has no computed result yet, show minimal info and return
        if fid not in active.facet_results:
            f = active.facets[fid]
            self.info_facet.setText(f"{fid} (faces: {len(f['faces_idx'])})")
            self.info_facet_type.setText(f"Facet Type: {f['facet_type']}")
            self.update_status(f"Facet selected (fid={fid})")
            return

        f   = active.facets[fid]
        res = active.facet_results[fid]
        hull2d   = res.get('hull2d', None)
        centroid = res.get('centroid', None)
        normal   = res.get('normal', None)
        u        = res.get('u', None)
        v        = res.get('v', None)

        if centroid is None or normal is None or u is None or v is None:
            return

        # Show facet classification
        self.info_facet_type.setText(f"Facet Type: {f.get('facet_type', 'Unknown')}")

        # --- BLUE FILL — inset slightly so it sits inside the dark facet lines ---
        if isinstance(hull2d, np.ndarray) and hull2d.shape[0] >= 3:
            try:
                # scale-aware inset based on stone size (world) + local edge size (facet)
                diag = _mesh_diag(active.mesh if active.mesh is not None else active.view_mesh)
                raw_inset_world = 0.004 * diag  # ~0.4% overall
                edge_lengths_2d = np.linalg.norm(np.roll(hull2d, -1, axis=0) - hull2d, axis=1)
                if edge_lengths_2d.size > 0:
                    # cap ≈ 10% of the **shortest** edge to avoid overreach on tight corners
                    inset_cap = 0.10 * float(np.min(edge_lengths_2d))
                else:
                    inset_cap = raw_inset_world
                inset = float(max(0.0, min(raw_inset_world, inset_cap)))

                # do the inset in 2D, then lift back to 3D; raise a hair to avoid z-fighting
                hull_in = self._inset_polygon_2d(hull2d, max(inset, 0.0))
                poly_world = np.array(
                    [centroid + u * p[0] + v * p[1] + normal * 5e-4 for p in hull_in],
                    dtype=float
                )

                # triangulate fan
                faces = []
                for i in range(1, len(poly_world) - 1):
                    faces.append([3, 0, i, i + 1])
                if faces:
                    poly = pv.PolyData(poly_world, np.hstack(faces).astype(np.int64))
                    opacity = 0.20 if getattr(self, 'see_through_cb', None) and self.see_through_cb.isChecked() else 0.30
                    active.facet_poly_actor = self.plotter.add_mesh(
                        poly, color='blue', opacity=opacity, smooth_shading=False,
                        name=f'{active.name}_facet_poly_{fid}'
                    )
                if getattr(self, "show_facet_edges_cb", None) and self.show_facet_edges_cb.isChecked():
                    self._add_or_update_facet_edges(active, angle_deg=20.0, edge_color="#0b0b0b", edge_width=2)
            except Exception as e:
                print("Facet fill error:", e)

        # --- PROJECTED POINTS from the OTHER mesh (colored by depth along normal) ---
        if self.show_points_cb.isChecked():
            pidx = res.get('points_inside_idx', np.array([], dtype=int))
            if other.mesh is not None and pidx is not None and pidx.size > 0:
                try:
                    pts = np.asarray(other.mesh.points)[pidx]
                    depths = np.maximum(0.0, np.dot(pts - centroid, normal))
                    clouds = pv.PolyData(pts)
                    clouds['depth'] = depths
                    active.points_actor = self.plotter.add_mesh(
                        clouds,
                        render_points_as_spheres=True,
                        point_size=6,
                        scalars='depth',
                        cmap='viridis',
                        name=f'{active.name}_points_{fid}',
                        show_scalar_bar=False
                    )
                except Exception as e:
                    print("Points overlay error:", e)

        # --- HIGHLIGHT the ACTIVE mesh cells belonging to this facet ---
        try:
            if active.mesh is not None:
                cells_to_highlight = []
                if 0 <= fid < len(active.facets):
                    cells_to_highlight = [c for c in active.facets[fid]['faces_idx']
                                        if 0 <= c < active.mesh.n_cells]

                if active.highlight_actor is not None:
                    try:
                        self.plotter.remove_actor(active.highlight_actor)
                    except Exception:
                        pass
                    active.highlight_actor = None

                if cells_to_highlight:
                    highlight = active.mesh.extract_cells(np.array(cells_to_highlight, dtype=int))

                    # NEW: draw only the facet boundary as tubes (crisp, no color wash)
                    try:
                        edges = _extract_feature_edges(
                        highlight,
                        angle_deg=1.0,
                        feature_edges=False,
                        boundary_edges=True,
                        non_manifold_edges=False,
                        manifold_edges=False
                    )

                        if edges.n_points > 0:
                            diag = _mesh_diag(highlight)
                            r = max(1e-6, 0.002 * diag)
                            edge_geo = edges.tube(radius=r, n_sides=12)
                            active.highlight_actor = self.plotter.add_mesh(
                                edge_geo, color='lime', lighting=False, name=f'{active.name}_highlight'
                            )
                        else:
                            # fallback to wireframe
                            active.highlight_actor = None
                            
                    except Exception:
                        active.highlight_actor = self.plotter.add_mesh(
                            highlight, style='wireframe', color='lime',
                            line_width=3, lighting=False, name=f'{active.name}_highlight'
                        )
        except Exception as e:
            print(f"Could not highlight {active.name} facet:", e)

        # --- Dimension labels & edge lengths (optional) ---
        if self.show_dims_cb.isChecked() and isinstance(hull2d, np.ndarray) and hull2d.shape[0] >= 3:
            self.draw_dimension_labels(fid)

        # --- Info panel updates ---
        self.info_facet.setText(f"{fid} (faces: {len(f['faces_idx'])})")
        self.info_max_depth.setText(f"{res.get('max_depth', 0.0):.6f}")
        self.info_mean_depth.setText(f"{res.get('mean_depth', 0.0):.6f}")
        self.info_depth_p95.setText(f"{res.get('depth_p95', 0.0):.6f}")
        self.info_depth_rms.setText(f"{res.get('depth_rms', 0.0):.6f}")
        self.info_area.setText(f"{res.get('footprint_area', 0.0):.6e}")
        self.info_perimeter.setText(f"{res.get('perimeter', 0.0):.6e}")
        self.info_points_inside.setText(str(int(res.get('points_inside_idx').size
                                                if res.get('points_inside_idx') is not None else 0)))
        self.info_approx_volume.setText(f"{res.get('approx_volume', 0.0):.6e}")
        self.info_voxel_volume.setText(f"{res.get('voxel_volume', 0.0):.6e}")

        passes = res.get('passes', [])
        times  = res.get('pass_times_sec', [])
        pass_map = {p[0]: p for p in passes}
        time_map = {t[0]: t for t in times}
        names_order = ["Coarse", "Medium", "Fine"]
        parts = []
        for nm in names_order:
            if nm in pass_map:
                d = pass_map[nm][1]
                vol = pass_map[nm][2]
                sec = time_map.get(nm, (nm, 0.0, 0.0, 0.0))[3]
                parts.append(f"{nm}: d={d:.6f} vol≈{vol:.6e} time≈{sec/60.0:.1f}m")
        self.info_passes.setText("; ".join(parts))
        self.info_time.setText(f"{res.get('time_total_sec', 0.0)/60.0:.1f} min")

        az = f.get('azimuth_deg', None)
        self.info_azimuth.setText("-" if az is None else f"{az:.2f}")
        if az is not None:
            self.update_status(f"Facet displayed (fid={fid}, azimuth={az:.1f}°)")
        else:
            self.update_status(f"Facet displayed (fid={fid})")
        try:
            if (getattr(self, "show_az_glyphs_cb", None) and self.show_az_glyphs_cb.isChecked()
                and isinstance(self.current_facet, int)
                and self.current_facet in active.facet_results):
                self._draw_azimuth_reference_glyphs(active, self.current_facet, active.facet_results[self.current_facet])
        except Exception:
            pass


    def draw_dimension_labels(self, fid):
        active = self.get_active_target()
        res = active.facet_results[fid]
        hull2d = res['hull2d']
        centroid = res['centroid']
        normal = res['normal']
        u = res['u']
        v = res['v']

        # world coordinates of hull
        hull_world = np.array([centroid + u * p[0] + v * p[1] + normal * 1e-4 for p in hull2d])

        # edge lines + length labels
        edge_mid_pts = []
        edge_labels = []

        n = len(hull_world)
        for i in range(n):
            p0 = hull_world[i]
            p1 = hull_world[(i + 1) % n]
            mid = 0.5 * (p0 + p1) + normal * 1e-4
            L = np.linalg.norm(p1 - p0)
            edge_mid_pts.append(mid)
            edge_labels.append(f"{L:.3f}")
            try:
                line = pv.Line(p0, p1)
                actor = self.plotter.add_mesh(line, color='white', line_width=2)
                active.edge_line_actors.append(actor)
            except Exception:
                pass

        # area & depth labels
        area = res.get('footprint_area', 0.0)
        maxd = res.get('max_depth', 0.0)
        meand = res.get('mean_depth', 0.0)
        label_pts = edge_mid_pts + [centroid + normal * 1e-3, centroid + normal * 2e-3]
        label_texts = edge_labels + [f"Area: {area:.3f}", f"Depth (max/mean): {maxd:.3f} / {meand:.3f}"]

        try:
            active.dim_label_actor = self.plotter.add_point_labels(
                label_pts, label_texts, point_size=0, shape=None, font_size=12, text_color='white', always_visible=True
            )
        except Exception as e:
            print("Label error:", e)

    # ---------------- Facet labels (clickable) ----------------
    def clear_facet_labels(self):
        tgt = self.get_active_target()
        try:
            if getattr(tgt, "_facet_labels_actor", None) is not None:
                self.plotter.remove_actor(tgt._facet_labels_actor)
        except Exception:
            pass
        tgt._facet_labels_actor = None

        # Clear stored label anchors and mapping
        tgt._facet_label_points = None
        tgt._facet_label_fids = None
        tgt._facet_label_pick_cb = getattr(tgt, "_facet_label_pick_cb", None)

        # Remove custom picker observers if we created them
        try:
            if hasattr(tgt, "_facet_label_picker") and tgt._facet_label_picker is not None:
                rw = self.plotter.ren_win if hasattr(self.plotter, "ren_win") else None
                if rw is not None:
                    iren = rw.GetInteractor()
                    if iren is not None:
                        try:
                            if hasattr(tgt, "_facet_label_pick_tag") and tgt._facet_label_pick_tag is not None:
                                iren.RemoveObserver(tgt._facet_label_pick_tag)
                        except Exception:
                            pass
        except Exception:
            pass
        tgt._facet_label_picker = None
        tgt._facet_label_pick_tag = None

    def build_clickable_facet_labels(self, offset=1e-3, font_size=12, text_color='yellow'):
        active = self.get_active_target()
        self.clear_facet_labels()

        if not getattr(self, "show_labels_cb", None) or not self.show_labels_cb.isChecked():
            return
        if not active.facets or not getattr(active, "visible_facet_ids", None):
            self._update_visible_facet_ids()
        vis_ids = list(getattr(active, "visible_facet_ids", []))
        if not vis_ids:
            return

        # Cap labels
        if len(vis_ids) > MAX_FACET_LABELS:
            step = max(1, len(vis_ids) // MAX_FACET_LABELS)
            vis_ids = vis_ids[::step][:MAX_FACET_LABELS]

        # Build anchors
        pts, fids = [], []
        for fid in vis_ids:
            if fid in active.facet_results and active.facet_results[fid].get('centroid') is not None:
                c = active.facet_results[fid]['centroid']; n = active.facet_results[fid]['normal']
            else:
                c = active.facets[fid]['centroid']; n = active.facets[fid]['normal']
            pts.append(np.asarray(c, float) + _norm(np.asarray(n, float)) * offset)
            fids.append(fid)
        if not pts:
            return

        pts = np.asarray(pts, float); fids = np.asarray(fids, int)
        try:
            labels = [str(fid) for fid in fids.tolist()]
            active._facet_labels_actor = self.plotter.add_point_labels(
                points=pts, labels=labels, point_size=0, shape=None, font_size=font_size,
                text_color=text_color, always_visible=True
            )
        except Exception:
            active._facet_labels_actor = None
            return

        # Store for picking, set up observer
        active._facet_label_points = pts
        active._facet_label_fids = fids
        try:
            import vtk
            rw = self.plotter.ren_win
            if rw is None:
                return
            iren = rw.GetInteractor()
            if iren is None:
                return
            try:
                active._facet_label_kd = cKDTree(pts)
            except Exception:
                active._facet_label_kd = None

            def _on_left_button_press(obj, ev):
                try:
                    x, y = iren.GetEventPosition()
                    ren = self.plotter.renderer

                    # Screen-space proximity to label anchors
                    pts_world = getattr(active, "_facet_label_points", None)
                    fids_arr = getattr(active, "_facet_label_fids", None)
                    if pts_world is not None and fids_arr is not None and len(pts_world) > 0:
                        disp_xy = []
                        for P in pts_world:
                            try:
                                ren.SetWorldPoint(float(P[0]), float(P[1]), float(P[2]), 1.0)
                                ren.WorldToDisplay()
                                dx, dy, dz = ren.GetDisplayPoint()
                                disp_xy.append((dx, dy))
                            except Exception:
                                disp_xy.append((float('inf'), float('inf')))
                        import numpy as _np
                        disp_xy = _np.asarray(disp_xy, float)
                        d2 = _np.hypot(disp_xy[:, 0] - x, disp_xy[:, 1] - y)
                        idx = int(_np.argmin(d2))
                        minpix = float(d2[idx])
                        pixel_tol = 40.0
                        if _np.isfinite(minpix) and minpix <= pixel_tol:
                            sel_fid = int(fids_arr[idx])
                            self.current_facet = sel_fid
                            if sel_fid in active.visible_facet_ids:
                                vis_idx = active.visible_facet_ids.index(sel_fid)
                                self.facet_spin.setValue(vis_idx)
                            self.show_selected_facet(sel_fid)
                            return

                    # Fallback: world pick + KD with tolerance
                    import vtk, numpy as _np
                    picker = vtk.vtkPropPicker()
                    picker.Pick(x, y, 0, ren)
                    picked = _np.array(picker.GetPickPosition(), float)
                    if not _np.all(_np.isfinite(picked)) or (picked == 0).all():
                        cam = self.plotter.camera
                        if cam is None:
                            return
                        picked = _np.array(cam.focal_point)

                    if getattr(active, "_facet_label_kd", None) is not None:
                        dist, idx = active._facet_label_kd.query(picked)
                        b = None
                        if active.mesh is not None:
                            b = _np.array(active.mesh.bounds, float)
                        elif getattr(self.target_polished, "mesh", None) is not None:
                            b = _np.array(self.target_polished.mesh.bounds, float)
                        elif getattr(self.target_rough, "mesh", None) is not None:
                            b = _np.array(self.target_rough.mesh.bounds, float)
                        if b is not None and b.size == 6:
                            b = b.reshape(3,2)
                            diag = float(_np.linalg.norm(b[:,1]-b[:,0]))
                            tol = max(1e-6, 0.10 * diag)
                        else:
                            tol = 1e-2
                        if _np.isfinite(dist) and dist <= tol:
                            sel_fid = int(fids_arr[idx])
                            self.current_facet = sel_fid
                            if sel_fid in active.visible_facet_ids:
                                vis_idx = active.visible_facet_ids.index(sel_fid)
                                self.facet_spin.setValue(vis_idx)
                            self.show_selected_facet(sel_fid)
                            return

                    # Empty space: no selection
                    return
                except Exception as e:
                    print("Facet label pick error:", e)

            active._facet_label_picker = iren
            active._facet_label_pick_tag = iren.AddObserver("LeftButtonPressEvent", _on_left_button_press, 1.0)
            active._facet_label_pick_cb = _on_left_button_press
        except Exception as e:
            print("Failed to set up clickable labels:", e)
            active._facet_label_picker = None
            active._facet_label_pick_tag = None

    def prev_facet(self):
        active = self.get_active_target()
        if not active.facets or not active.visible_facet_ids:
            return
        if self.facet_spin.value() > 0:
            self.facet_spin.setValue(self.facet_spin.value() - 1)
        fid = active.visible_facet_ids[self.facet_spin.value()]
        self.current_facet = fid
        self.show_selected_facet(self.facet_spin.value())
        self.update_status("Prev facet")

    def next_facet(self):
        active = self.get_active_target()
        if not active.facets or not active.visible_facet_ids:
            return
        if self.facet_spin.value() < (len(active.visible_facet_ids) - 1):
            self.facet_spin.setValue(self.facet_spin.value() + 1)
        fid = active.visible_facet_ids[self.facet_spin.value()]
        self.current_facet = fid
        self.show_selected_facet(self.facet_spin.value())
        self.update_status("Next facet")

    # ---------------- Global pass-region clouds (Active) ----------------
    def build_pass_point_clouds(self):
        active = self.get_active_target()
        other = self.get_other_target()
        if not active.facet_results or other.mesh is None:
            return

        blue_pts, green_pts, red_pts = [], [], []

        for fid, res in active.facet_results.items():
            pidx = res.get('points_inside_idx', None)
            if pidx is None or pidx.size == 0:
                continue
            centroid = res['centroid']; normal = res['normal']
            pts = np.asarray(other.mesh.points)[pidx]
            depths = np.maximum(0.0, np.dot(pts - centroid, normal))
            maxd = res.get('max_depth', 0.0)
            if maxd <= 0:
                continue
            t_coarse = 0.6 * maxd
            t_med = 0.3 * maxd
            red_pts.append(pts[depths >= t_coarse])
            green_pts.append(pts[(depths >= t_med) & (depths < t_coarse)])
            blue_pts.append(pts[depths < t_med])

        def concat(chunks):
            chunks = [c for c in chunks if c is not None and c.size > 0]
            return np.vstack(chunks) if chunks else np.zeros((0, 3))

        def subsample(pts, k):
            if pts.shape[0] <= k: return pts
            idx = np.random.choice(pts.shape[0], k, replace=False)
            return pts[idx]

        blue_pts = subsample(concat(blue_pts), MAX_PASS_POINTS_PER_COLOR)
        green_pts = subsample(concat(green_pts), MAX_PASS_POINTS_PER_COLOR)
        red_pts = subsample(concat(red_pts), MAX_PASS_POINTS_PER_COLOR)

        # remove old
        for actor in [active.pass_blue_actor, active.pass_green_actor, active.pass_red_actor]:
            if actor is not None:
                try: self.plotter.remove_actor(actor)
                except Exception: pass
        active.pass_blue_actor = active.pass_green_actor = active.pass_red_actor = None

        # add new (lightweight)
        if blue_pts.shape[0] > 0:
            active.pass_blue_actor = self.plotter.add_mesh(
                pv.PolyData(blue_pts), color='blue', render_points_as_spheres=True, point_size=4, name=f'{active.name}_pass_blue')
        if green_pts.shape[0] > 0:
            active.pass_green_actor = self.plotter.add_mesh(
                pv.PolyData(green_pts), color='green', render_points_as_spheres=True, point_size=4, name=f'{active.name}_pass_green')
        if red_pts.shape[0] > 0:
            active.pass_red_actor = self.plotter.add_mesh(
                pv.PolyData(red_pts), color='red', render_points_as_spheres=True, point_size=4, name=f'{active.name}_pass_red')

        self.update_pass_actors_visibility()

    def update_pass_actors_visibility(self):
        active = self.get_active_target()

        if active.pass_blue_actor is not None:
            try:
                active.pass_blue_actor.SetVisibility(bool(self.show_fine_cb.isChecked()))
            except Exception:
                pass
        if active.pass_green_actor is not None:
            try:
                active.pass_green_actor.SetVisibility(bool(self.show_medium_cb.isChecked()))
            except Exception:
                pass
        if active.pass_red_actor is not None:
            try:
                active.pass_red_actor.SetVisibility(bool(self.show_coarse_cb.isChecked()))
            except Exception:
                pass
        try:
            self.plotter.render()
        except Exception:
            pass

    # ---------------- Cutting volume (global, Active) ----------------
    def build_cutting_volume(self):
        active = self.get_active_target()
        if not active.facet_results:
            QtWidgets.QMessageBox.warning(self, "No data", "Compute facets first")
            return

        # remove old actor if any
        if active.cut_volume_actor is not None:
            try:
                self.plotter.remove_actor(active.cut_volume_actor)
            except Exception:
                pass
        active.cut_volume_actor = None

        # build points & cells
        points = []
        cells = []
        celltypes = []
        pid = 0

        # safety cap
        max_cells = 1_000_000
        total_boxes = 0

        use_adaptive = bool(self.use_adaptive_cb.isChecked())

        for fid, res in active.facet_results.items():
            centroid = res.get('centroid', None)
            if centroid is None:
                continue
            u = res.get('u', None); v = res.get('v', None); n = res.get('normal', None)
            if u is None or v is None or n is None:
                continue

            if use_adaptive:
                tiles = res.get('adaptive_tiles', [])
                if not tiles:
                    continue
                for (x0,y0,x1,y1, d) in tiles:
                    if d <= 1e-12:
                        continue
                    total_boxes += 1
                    if total_boxes > max_cells:
                        print("Cutting volume capped at", max_cells, "boxes to avoid memory blowup (adaptive).")
                        break
                    cx = 0.5*(x0+x1); cy = 0.5*(y0+y1)
                    hx = 0.5*(x1-x0); hy = 0.5*(y1-y0)
                    center = centroid + u*cx + v*cy + n*(d/2.0)
                    half_u = u*hx; half_v = v*hy; half_n = n*(d/2.0)

                    p0 = center - half_u - half_v - half_n
                    p1 = center + half_u - half_v - half_n
                    p2 = center + half_u + half_v - half_n
                    p3 = center - half_u + half_v - half_n
                    p4 = center - half_u - half_v + half_n
                    p5 = center + half_u - half_v + half_n
                    p6 = center + half_u + half_v + half_n
                    p7 = center - half_u + half_v + half_n

                    points.extend([p0, p1, p2, p3, p4, p5, p6, p7])
                    cells.extend([8, pid, pid+1, pid+2, pid+3, pid+4, pid+5, pid+6, pid+7])
                    celltypes.append(VTK_HEXAHEDRON)
                    pid += 8
                if total_boxes > max_cells:
                    break
            else:
                depth_map = res.get('depth_map', None)
                xs = res.get('xs', None); ys = res.get('ys', None)
                dx = res.get('dx', None); dy = res.get('dy', None)
                if depth_map is None or xs is None or ys is None or dx is None or dy is None:
                    continue

                half_u = (dx/2.0) * u
                half_v = (dy/2.0) * v

                for iy in range(depth_map.shape[0]):
                    for ix in range(depth_map.shape[1]):
                        d = float(depth_map[iy, ix])
                        if d <= 1e-12:
                            continue

                        total_boxes += 1
                        if total_boxes > max_cells:
                            print("Cutting volume capped at", max_cells, "boxes to avoid memory blowup.")
                            break

                        cx = xs[ix]; cy = ys[iy]
                        center = centroid + u * cx + v * cy + n * (d / 2.0)
                        half_n = (d / 2.0) * n

                        p0 = center - half_u - half_v - half_n
                        p1 = center + half_u - half_v - half_n
                        p2 = center + half_u + half_v - half_n
                        p3 = center - half_u + half_v - half_n
                        p4 = center - half_u - half_v + half_n
                        p5 = center + half_u - half_v + half_n
                        p6 = center + half_u + half_v + half_n
                        p7 = center - half_u + half_v + half_n

                        points.extend([p0, p1, p2, p3, p4, p5, p6, p7])
                        cells.extend([8, pid, pid+1, pid+2, pid+3, pid+4, pid+5, pid+6, pid+7])
                        celltypes.append(VTK_HEXAHEDRON)
                        pid += 8

                    if total_boxes > max_cells:
                        break

        if len(cells) == 0:
            QtWidgets.QMessageBox.information(self, "No volume", "No nonzero voxels/tiles to build cutting volume. Enable voxelization and recompute.")
            return

        points = np.asarray(points, dtype=float)
        cells = np.asarray(cells, dtype=np.int64)
        celltypes = np.asarray(celltypes, dtype=np.uint8)

        try:
            grid = pv.UnstructuredGrid(cells, celltypes, points)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to build volume: {e}")
            return

        active.cut_volume_grid = grid
        active.cut_volume_actor = self.plotter.add_mesh(
            grid, color='magenta', opacity=0.25, show_edges=False, name=f"{active.name}_cutting_volume"
        )

        # toggle visible based on checkbox
        self.toggle_cutting_volume()
        self.update_status("Cutting volume built")

    def toggle_cutting_volume(self):
        active = self.get_active_target()
        visible = bool(self.show_volume_cb.isChecked())
        if active.cut_volume_actor is not None:
            try:
                active.cut_volume_actor.SetVisibility(visible)
            except Exception:
                pass
            try:
                self.plotter.render()
            except Exception:
                pass
        elif visible:
            self.build_cutting_volume()

    # ---------------- Trimesh cache for "other" mesh ----------------
    def _ensure_trimesh_other(self):
        """Build and cache a trimesh.Trimesh from the OTHER mesh for fast ray casting."""
        if not TRIMESH_AVAILABLE:
            return None
        other = self.get_other_target()
        if other.mesh is None:
            return None

        if self._other_trimesh_cache is not None:
            return self._other_trimesh_cache

        try:
            verts = np.asarray(other.mesh.points)
            f = np.asarray(other.mesh.faces)
            if f.size == 0:
                return None
            if f.ndim == 1:
                tri = f.reshape(-1, 4)[:, 1:4]
            else:
                tri = f[:, 1:4]
            tm = trimesh.Trimesh(vertices=verts, faces=tri, process=False)
            self._other_trimesh_cache = tm
            return tm
        except Exception as e:
            print("Failed to build trimesh for other:", e)
            return None


    def _clear_rays(self, target: 'TargetBundle'):
        """Remove any debug ray actors from the scene."""
        if getattr(target, "ray_actors", None):
            for a in target.ray_actors:
                try:
                    self.plotter.remove_actor(a)
                except Exception:
                    pass
            target.ray_actors = []

    def _ray_heights_from_plane(self, origins_world: np.ndarray, normal: np.ndarray, tm, other_target: 'TargetBundle') -> np.ndarray:
        """
        First-hit distances along +normal from each origin.
        Prefers pyembree (fast/precise), falls back to trimesh numpy, last resort KDTree step-scan.
        """
        N = origins_world.shape[0]
        if N == 0:
            return np.zeros((0,), dtype=float)

        normal = _norm(normal)
        eps = 1e-6
        origins = origins_world - normal[None, :] * eps
        dirs = np.repeat(normal[None, :], N, axis=0)

        if TRIMESH_AVAILABLE and tm is not None:
            try:
                import trimesh.ray.ray_pyembree as rpe
                rmi = rpe.RayMeshIntersector(tm)
                locs, idx_ray, _ = rmi.intersects_location(origins, dirs)
            except Exception:
                locs, idx_ray, _ = tm.ray.intersects_location(origins, dirs)

            dists = np.full((N,), 0.0, dtype=float)
            if len(locs) > 0:
                vec = locs - origins[idx_ray]
                proj = np.einsum('ij,ij->i', vec, dirs[idx_ray])  # signed distances
                for r in np.unique(idx_ray):
                    mask = (idx_ray == r) & (proj > 0)
                    if np.any(mask):
                        dists[r] = float(np.min(proj[mask]))
            return dists

        # KDTree step-scan fallback
        other_np = np.asarray(other_target.mesh.points, dtype=float)
        kd = cKDTree(other_np)
        b = np.array(other_target.mesh.bounds, float).reshape(3, 2)
        diag = float(np.linalg.norm(b[:, 1] - b[:, 0]))
        max_depth = max(diag, 1e-3)
        step = max_depth / 600.0
        thr = max(diag / 2000.0, 1e-4)

        heights = np.zeros((N,), dtype=float)
        zs = np.arange(step, max_depth + step, step)
        chunk = max(1, 200000 // max(1, len(zs)))
        for i0 in range(0, N, chunk):
            i1 = min(N, i0 + chunk)
            O = origins[i0:i1]
            M = O.shape[0]
            P = O[:, None, :] + zs[None, :, None] * normal[None, None, :]
            P_flat = P.reshape(-1, 3)
            d, _ = kd.query(P_flat, k=1, workers=-1)
            hit = (d < thr).reshape(M, -1)
            for j in range(M):
                if np.any(hit[j]):
                    k = int(np.argmax(hit[j]))
                    heights[i0 + j] = float(zs[k])
        return heights



    def _choose_outward_normal(self, centroid: np.ndarray, normal: np.ndarray, tm, other_target: 'TargetBundle') -> np.ndarray:
        """
        Decide which direction (±normal) intersects the OTHER mesh first.
        This makes extrusion symmetric:
        • Active = Polished → rays go toward the Rough.
        • Active = Rough    → rays go toward the Polished.
        We pick the side that yields a positive first‑hit distance; if both do,
        we choose the nearer (smaller) distance for a tighter shell.
        """
        normal = _norm(normal)
        d_plus  = self._ray_heights_from_plane(np.asarray([centroid], float),  normal, tm, other_target)[0]
        d_minus = self._ray_heights_from_plane(np.asarray([centroid], float), -normal, tm, other_target)[0]
        # If neither side hits, default to +normal
        if d_plus <= 0.0 and d_minus <= 0.0:
            return normal
        # Prefer the side with a positive *and closer* hit distance
        if d_plus > 0.0 and (d_minus <= 0.0 or d_plus <= d_minus):
            return normal
        else:
            return -normal

    def build_edge_rays_for_selected(self, fid: int = None, max_per_edge: int = 64):
        """
        Draw multi-color rays from each boundary edge of the selected facet.
        Rays are perpendicular to the *edge* in 3D and point outward from the stone,
        stopping at the OTHER mesh (rough↔polished) on first hit.
        """
        active = self.get_active_target()
        other  = self.get_other_target()
        if active.mesh is None or other.mesh is None:
            QtWidgets.QMessageBox.warning(self, "Error", "Load both meshes first")
            return

        # resolve facet id
        if fid is None:
            if isinstance(self.current_facet, int) and self.current_facet in getattr(active, "visible_facet_ids", []):
                fid = self.current_facet
            else:
                if not getattr(active, "visible_facet_ids", None):
                    self._update_visible_facet_ids()
                if not active.visible_facet_ids:
                    QtWidgets.QMessageBox.information(self, "No facets", "Nothing to draw rays from.")
                    return
                fid = active.visible_facet_ids[max(0, min(self.facet_spin.value(), len(active.visible_facet_ids)-1))]
                self.current_facet = fid

        # need frame
        if fid not in active.facet_results:
            self.compute_selected_facet()
        if fid not in active.facet_results:
            QtWidgets.QMessageBox.warning(self, "Error", "Facet has no computed frame.")
            return

        res = active.facet_results[fid]
        hull2d   = res.get('hull2d', None)
        centroid = res.get('centroid', None)
        n0       = res.get('normal', None)
        u        = res.get('u', None)
        v        = res.get('v', None)
        if hull2d is None or hull2d.shape[0] < 3 or centroid is None or n0 is None or u is None or v is None:
            QtWidgets.QMessageBox.information(self, "Degenerate", "Facet hull/frame not available.")
            return

        n0 = _norm(np.asarray(n0, float))

        # local->world lift
        def lw(x, y):
            return centroid + u * x + v * y

        # world boundary polygon
        polyW = np.array([lw(p[0], p[1]) for p in hull2d], dtype=float)
        m = polyW.shape[0]

        # palette (distinct per edge)
        colors = ["#ff3b30", "#ff9f0a", "#ffcc00", "#34c759", "#00c7be",
                "#007aff", "#5e5ce6", "#af52de", "#ff2d55", "#a2845e"]

        # clear previous rays
        self._clear_rays(active)

        tm = self._ensure_trimesh_other()

        # spacing: ~6% of facet span
        hull2d = np.asarray(hull2d, float)
        ext = max(float(np.ptp(hull2d[:, 0])), float(np.ptp(hull2d[:, 1])))
        spacing = max(1e-6, 0.06 * ext)

        for e in range(m):
            p0w = polyW[e]
            p1w = polyW[(e + 1) % m]
            edge_vec = p1w - p0w
            L = float(np.linalg.norm(edge_vec))
            if L <= 1e-12:
                continue
            ehat = edge_vec / L

            # edge-perpendicular component of the facet normal (two opposite possibilities)
            d0 = n0 - np.dot(n0, ehat) * ehat
            if np.linalg.norm(d0) < 1e-12:
                # pathological: pick anything ⟂ edge
                tmp = np.array([1.0, 0.0, 0.0])
                if abs(np.dot(tmp, ehat)) > 0.95: tmp = np.array([0.0, 1.0, 0.0])
                d0 = np.cross(ehat, np.cross(tmp, ehat))
            d0 = _norm(d0)

            # choose outward sign using the edge midpoint
            mid = 0.5 * (p0w + p1w)
            dists = self._ray_first_hits(
                np.vstack([mid, mid]),
                np.vstack([ d0, -d0]),
                tm, other
            )
            dout = d0 if dists[0] >= dists[1] else -d0

            # sample along edge (avoid endpoints overlap)
            k = max(2, min(max_per_edge, int(round(L / max(spacing, 1e-9)))))
            ts = (np.arange(k, dtype=float) + 0.5) / k
            bases = p0w[None, :] + ts[:, None] * edge_vec[None, :]
            dirs  = np.repeat(dout[None, :], k, axis=0)

            # first hits
            hits = self._ray_first_hits(bases, dirs, tm, other)

            # draw
            col = colors[e % len(colors)]
            for base, h in zip(bases, hits):
                if h <= 0.0:
                    continue
                tip = base + dout * float(h)
                try:
                    line = pv.Line(base, tip)
                    actor = self.plotter.add_mesh(line, color=col, line_width=3, lighting=False)
                    active.ray_actors.append(actor)
                except Exception:
                    pass

        try:
            self.plotter.render()
        except Exception:
            pass
        self.update_status(f"Edge rays (perpendicular & outward) drawn for fid={fid}")

    
    def _ray_first_hits(self, origins: np.ndarray, dirs: np.ndarray, tm, other_target: 'TargetBundle') -> np.ndarray:
        """
        First positive hit distances along 'dirs' for each origin.
        Uses pyembree if available; falls back to trimesh numpy, then KDTree stepping.
        origins: (N,3), dirs: (N,3) (assumed normalized)
        """
        N = 0 if origins is None else int(len(origins))
        if N == 0:
            return np.zeros((0,), dtype=float)

        dirs = np.asarray(dirs, float)
        norms = np.linalg.norm(dirs, axis=1, keepdims=True) + 1e-18
        dirs = dirs / norms

        # tiny back-off to avoid starting "inside" triangles
        origins = np.asarray(origins, float) - dirs * 1e-6

        if TRIMESH_AVAILABLE and tm is not None:
            try:
                import trimesh.ray.ray_pyembree as rpe
                rmi = rpe.RayMeshIntersector(tm)
                locs, idx_ray, _ = rmi.intersects_location(origins, dirs)
            except Exception:
                locs, idx_ray, _ = tm.ray.intersects_location(origins, dirs)

            dists = np.zeros((N,), dtype=float)
            if len(locs) > 0:
                vec = locs - origins[idx_ray]
                proj = np.einsum('ij,ij->i', vec, dirs[idx_ray])  # signed
                # nearest positive per ray
                for r in range(N):
                    m = (idx_ray == r) & (proj > 0)
                    if np.any(m):
                        dists[r] = float(np.min(proj[m]))
            return dists

        # ---- KDTree stepping fallback ----
        other_np = np.asarray(other_target.mesh.points, dtype=float)
        kd = cKDTree(other_np)
        b = np.array(other_target.mesh.bounds, float).reshape(3, 2)
        diag = float(np.linalg.norm(b[:, 1] - b[:, 0]))
        max_depth = max(diag, 1e-3)
        step = max_depth / 600.0
        thr = max(diag / 2000.0, 1e-4)
        zs = np.arange(step, max_depth + step, step)

        dists = np.zeros((N,), dtype=float)
        # chunk so memory doesn’t explode
        chunk = max(1, 150000 // max(1, len(zs)))
        for i0 in range(0, N, chunk):
            i1 = min(N, i0 + chunk)
            O = origins[i0:i1]
            D = dirs[i0:i1]
            P = O[:, None, :] + zs[None, :, None] * D[:, None, :]
            P_flat = P.reshape(-1, 3)
            d, _ = kd.query(P_flat, k=1, workers=-1)
            hit = (d < thr).reshape(i1 - i0, -1)
            for j in range(i1 - i0):
                if np.any(hit[j]):
                    k = int(np.argmax(hit[j]))
                    dists[i0 + j] = float(zs[k])
        return dists

    # ---------------- Extrusion (ACTIVE facet against OTHER mesh) ----------------
    def build_extruded_selected(self):
        active = self.get_active_target()
        other  = self.get_other_target()

        if active.mesh is None or other.mesh is None:
            QtWidgets.QMessageBox.warning(self, "Error", "Load both meshes first")
            return

        if not active.facets:
            active.facets = self.extract_facets(active, angle_tol_deg=0.75)
            if not active.facets:
                QtWidgets.QMessageBox.warning(self, "No facets", f"Couldn't extract facets from {active.name} mesh.")
                return

        # Visible -> actual facet id
        vis_idx = int(self.facet_spin.value())
        if vis_idx < 0 or vis_idx >= len(active.visible_facet_ids):
            QtWidgets.QMessageBox.warning(self, "Invalid facet", "Choose a valid facet index")
            return
        fid = active.visible_facet_ids[vis_idx]

        # Ensure per-facet data exists
        if fid not in active.facet_results:
            self.compute_selected_facet()
        res = active.facet_results.get(fid)
        if res is None:
            QtWidgets.QMessageBox.warning(self, "Error", "No facet data available")
            return

        hull2d   = res['hull2d']
        centroid = res['centroid']
        n        = _norm(res['normal'])
        u        = _norm(res['u'])
        v        = _norm(res['v'])
        if hull2d is None or hull2d.shape[0] < 3:
            QtWidgets.QMessageBox.warning(self, "Degenerate facet", "Facet hull has fewer than 3 vertices")
            return

        # Clear previous extrusion actors for this target
        if active.extruded_actor is not None:
            try: self.plotter.remove_actor(active.extruded_actor)
            except Exception: pass
            active.extruded_actor = None
            active.extruded_grid  = None

        if hasattr(active, "extruded_side_actors") and active.extruded_side_actors:
            for a in active.extruded_side_actors:
                try: self.plotter.remove_actor(a)
                except Exception: pass
        active.extruded_side_actors = []

        # -------------------------------- GRID OVER FACET PLANE --------------------------------
        min_x, min_y = np.min(hull2d, axis=0)
        max_x, max_y = np.max(hull2d, axis=0)
        longer = max(max_x - min_x, max_y - min_y)
        S  = int(self.extrude_samples_spin.value())
        nx = max(2, int(math.ceil((max_x - min_x) / (longer if longer > 0 else 1.0) * S)))
        ny = max(2, int(math.ceil((max_y - min_y) / (longer if longer > 0 else 1.0) * S)))

        xs = np.linspace(min_x, max_x, nx + 1)
        ys = np.linspace(min_y, max_y, ny + 1)
        XX, YY = np.meshgrid(xs, ys)

        world_nodes = (centroid[None, None, :] +
                    XX[:, :, None] * u[None, None, :] +
                    YY[:, :, None] * v[None, None, :])

        # Keep only nodes inside the facet polygon
        poly = Path(hull2d)
        nodes_2d = np.column_stack([XX.ravel(), YY.ravel()])
        inside_nodes = poly.contains_points(nodes_2d).reshape(YY.shape)
        mask_flat = inside_nodes.ravel()

        # -------------------------------- RAY / INTERSECTION SETUP --------------------------------
        eps = 1e-6
        b = np.array(other.mesh.bounds).reshape(3, 2)
        diag = float(np.linalg.norm(b[:, 1] - b[:, 0]))
        ray_len = max(diag * 2.5, 1.0)

        # Trimesh intersector for "other" mesh if available
        tm = self._ensure_trimesh_other() if TRIMESH_AVAILABLE else None
        intersector = None
        if tm is not None and hasattr(tm, "ray"):
            try:
                intersector = trimesh.ray.ray_triangle.RayMeshIntersector(tm)
            except Exception:
                intersector = None

        def cast_first_hit_dist(origins, dirs):
            """First positive hit distance to OTHER; 0 if no hit."""
            if intersector is not None:
                try:
                    loc, idx_ray, _ = intersector.intersects_location(origins, dirs, multiple_hits=True)
                    if loc.shape[0] > 0:
                        dists = np.einsum('ij,ij->i', (loc - origins[idx_ray]), dirs[idx_ray])
                        out = np.full(origins.shape[0], np.nan)
                        for i, d in zip(idx_ray, dists):
                            if d >= 0.0 and (np.isnan(out[i]) or d < out[i]):
                                out[i] = d
                        return np.nan_to_num(out, nan=0.0)
                    return np.zeros(origins.shape[0], dtype=float)
                except Exception:
                    return np.zeros(origins.shape[0], dtype=float)

            # Fallback PyVista ray tracing
            out = np.zeros(origins.shape[0], dtype=float)
            other_poly = other.mesh
            for i in range(origins.shape[0]):
                o = origins[i]; d = dirs[i]
                p2 = o + d * ray_len
                try:
                    pts, _ = other_poly.ray_trace(o, p2)
                    if pts is not None and len(pts) > 0:
                        first = np.asarray(pts)[0]
                        out[i] = max(0.0, float(np.dot(first - o, d)))
                    else:
                        out[i] = 0.0
                except Exception:
                    out[i] = 0.0
            return out

        # KD-tree for robust fallback nearest vectors (to "other" mesh)
        other_np = np.asarray(other.mesh.points)
        kd = cKDTree(other_np)

        # --------------------------- ORIENT NORMAL TOWARD POLISH (if active is ROUGH) ---------------------------
        # This ensures: when active == rough, the yellow extrusion goes FROM the rough facet surface
        # TO the polish diamond surface (i.e., normal points "toward" the other mesh).
        if self._target_is_rough(active) and other_np.size >= 3:
            _, nn = kd.query(centroid.reshape(1, -1), k=1)
            nn = int(nn[0]) if np.ndim(nn) else int(nn)
            to_other = other_np[nn] - centroid
            if np.dot(n, to_other) < 0.0:
                n = -n  # flip to face the polish

        def best_signed_along(dir_abs):
            """
            For each inside node, try +dir and -dir; pick whichever hits first (shortest > 0).
            If both miss, fall back to nearest-point vector so volume is still occupied.
            Returns (chosen_dir[Ni,3], dist[Ni]) for the inside nodes in flattened order.
            """
            node_origins = world_nodes.reshape(-1, 3)[mask_flat]

            d_plus  = np.repeat(dir_abs[None, :], node_origins.shape[0], axis=0)
            d_minus = -d_plus

            # try both directions
            h_plus  = cast_first_hit_dist(node_origins - d_plus * eps,  d_plus)
            h_minus = cast_first_hit_dist(node_origins - d_minus * eps, d_minus)

            choose_plus  = (h_plus  > 0) & ((h_minus <= 0) | (h_plus <= h_minus))
            choose_minus = (h_minus > 0) & ~choose_plus

            chosen_h   = np.zeros_like(h_plus)
            chosen_dir = np.zeros_like(d_plus)

            chosen_h[choose_plus]   = h_plus[choose_plus]
            chosen_dir[choose_plus] = d_plus[choose_plus]

            chosen_h[choose_minus]   = h_minus[choose_minus]
            chosen_dir[choose_minus] = d_minus[choose_minus]

            # Fallback where both miss: vector to nearest point on "other"
            miss = (chosen_h <= 0)
            if np.any(miss):
                miss_idx = np.where(miss)[0]
                miss_orig = node_origins[miss_idx]
                _, nn = kd.query(miss_orig)
                vecs = other_np[nn] - miss_orig
                lens = np.linalg.norm(vecs, axis=1)
                good = lens > 1e-12
                if np.any(good):
                    gidx = miss_idx[good]
                    gv   = vecs[good] / lens[good, None]
                    chosen_dir[gidx] = gv
                    chosen_h[gidx]   = lens[good]
                # if lens == 0 (exactly on surface), we leave height 0

            return chosen_dir, chosen_h

        # ------------------------ EXPORTED VOLUME (YELLOW ONLY, NORMAL-BASED) ------------------------
        dir_specs_export = [
            ("normal", n, np.array([255, 255,   0, 180], dtype=np.uint8)),  # yellow
        ]

        all_points, all_cells, all_types, all_cell_rgba = [], [], [], []
        pid = 0
        max_cells  = 1_000_000
        total_cells = 0

        for _, dabs, rgba in dir_specs_export:
            chosen_dir_flat, chosen_h_flat = best_signed_along(dabs)

            # Scatter to grids
            dir_field = np.zeros(world_nodes.shape, dtype=float)   # (ny+1, nx+1, 3)
            h_field   = np.zeros(XX.shape, dtype=float)            # (ny+1, nx+1)
            dir_field.reshape(-1, 3)[mask_flat] = chosen_dir_flat
            h_field.reshape(-1)[mask_flat] = chosen_h_flat

            pid_bottom = -np.ones_like(XX, dtype=int)
            pid_top    = -np.ones_like(XX, dtype=int)

            # Build per-node bottom/top points (bottom on rough facet surface; top on polish surface)
            for j in range(YY.shape[0]):
                for i in range(XX.shape[1]):
                    if not inside_nodes[j, i]:
                        continue
                    base_pt = world_nodes[j, i, :]
                    h   = float(h_field[j, i])
                    dvec = dir_field[j, i, :]
                    top_pt = base_pt + dvec * h

                    all_points.append(base_pt); pid_bottom[j, i] = pid; pid += 1
                    all_points.append(top_pt);  pid_top[j, i]    = pid; pid += 1

            def ok(j, i):
                return (0 <= j < YY.shape[0] and 0 <= i < XX.shape[1] and
                        inside_nodes[j, i] and pid_bottom[j, i] >= 0 and pid_top[j, i] >= 0)

            # Quad cells -> hexahedra
            for j in range(YY.shape[0] - 1):
                for i in range(XX.shape[1] - 1):
                    if not (ok(j, i) and ok(j, i + 1) and ok(j + 1, i + 1) and ok(j + 1, i)):
                        continue
                    b0 = pid_bottom[j, i];       b1 = pid_bottom[j, i + 1]
                    b2 = pid_bottom[j + 1, i + 1]; b3 = pid_bottom[j + 1, i]
                    t0 = pid_top[j, i];         t1 = pid_top[j, i + 1]
                    t2 = pid_top[j + 1, i + 1]; t3 = pid_top[j + 1, i]
                    all_cells.extend([8, b0, b1, b2, b3, t0, t1, t2, t3])
                    all_types.append(VTK_HEXAHEDRON)
                    all_cell_rgba.append(rgba)
                    total_cells += 1
                    if total_cells >= max_cells:
                        break
                if total_cells >= max_cells:
                    break
            if total_cells >= max_cells:
                print(f"Extrusion cell cap reached ({max_cells}); remaining cells skipped.")
                break

        if total_cells == 0:
            QtWidgets.QMessageBox.information(self, "No volume", "Extrusion created no interior cells (facet too small or samples too low).")
            return

        points_arr = np.asarray(all_points, dtype=float)
        cells_arr  = np.asarray(all_cells, dtype=np.int64)
        types_arr  = np.asarray(all_types, dtype=np.uint8)
        cell_rgba  = np.vstack(all_cell_rgba).astype(np.uint8)
        if cell_rgba.shape != (total_cells, 4):
            cell_rgba = cell_rgba.reshape(total_cells, 4)

        try:
            grid = pv.UnstructuredGrid(cells_arr, types_arr, points_arr)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to build extruded grid: {e}")
            return

        grid.cell_data["RGBA"] = cell_rgba
        active.extruded_grid = grid
        active.extruded_actor = self.plotter.add_mesh(
            grid, scalars="RGBA", rgb=True, opacity=0.95, show_edges=True,
            name=f"{active.name}_extruded_volume", show_scalar_bar=False
        )

        # ---------------- PREVIEW-ONLY (NOT EXPORTED): U/V EXTRUSIONS ----------------
        preview_specs = [
            ("u", u, (255,  60,  60, 160)),   # red
            ("v", v, ( 60, 130, 255, 160)),   # blue
        ]

        for label, dabs, rgba in preview_specs:
            chosen_dir_flat, chosen_h_flat = best_signed_along(dabs)

            dir_field = np.zeros(world_nodes.shape, dtype=float)
            h_field   = np.zeros(XX.shape, dtype=float)
            dir_field.reshape(-1, 3)[mask_flat] = chosen_dir_flat
            h_field.reshape(-1)[mask_flat] = chosen_h_flat

            pid_bottom = -np.ones_like(XX, dtype=int)
            pid_top    = -np.ones_like(XX, dtype=int)
            pts_p, cells_p, types_p = [], [], []
            pidp = 0
            made_any = False

            # Build nodes
            for j in range(YY.shape[0]):
                for i in range(XX.shape[1]):
                    if not inside_nodes[j, i]:
                        continue
                    base_pt = world_nodes[j, i, :]
                    h   = float(h_field[j, i])
                    dvec = dir_field[j, i, :]
                    top_pt = base_pt + dvec * h
                    pts_p.append(base_pt); pid_bottom[j, i] = pidp; pidp += 1
                    pts_p.append(top_pt);  pid_top[j, i]    = pidp; pidp += 1

            def okp(j, i):
                return (0 <= j < YY.shape[0] and 0 <= i < XX.shape[1] and
                        inside_nodes[j, i] and pid_bottom[j, i] >= 0 and pid_top[j, i] >= 0)

            for j in range(YY.shape[0] - 1):
                for i in range(XX.shape[1] - 1):
                    if not (okp(j, i) and okp(j, i + 1) and okp(j + 1, i + 1) and okp(j + 1, i)):
                        continue
                    b0 = pid_bottom[j, i];       b1 = pid_bottom[j, i + 1]
                    b2 = pid_bottom[j + 1, i + 1]; b3 = pid_bottom[j + 1, i]
                    t0 = pid_top[j, i];         t1 = pid_top[j, i + 1]
                    t2 = pid_top[j + 1, i + 1]; t3 = pid_top[j + 1, i]
                    cells_p.extend([8, b0, b1, b2, b3, t0, t1, t2, t3])
                    types_p.append(VTK_HEXAHEDRON)
                    made_any = True

            if made_any:
                try:
                    grid_p = pv.UnstructuredGrid(np.asarray(cells_p, np.int64),
                                                np.asarray(types_p, np.uint8),
                                                np.asarray(pts_p, float))
                    color_rgb = (rgba[0]/255.0, rgba[1]/255.0, rgba[2]/255.0)
                    alpha = max(0.0, min(1.0, rgba[3]/255.0))
                    act = self.plotter.add_mesh(
                        grid_p, color=color_rgb, opacity=alpha,
                        show_edges=True, name=f"{active.name}_extruded_preview_{label}",
                        show_scalar_bar=False
                    )
                    active.extruded_side_actors.append(act)
                except Exception as e:
                    print(f"Preview grid failed for {label}:", e)

        # UI
        self.show_extruded_cb.setEnabled(True)
        self.export_extruded_btn.setEnabled(True)
        self.show_extruded_cb.setChecked(True)
        self.update_status("Extruded volume built")
        try: self.plotter.render()
        except Exception: pass


    def _target_is_rough(self, target) -> bool:
        """Best-effort check to know if a target is the rough stone."""
        name = str(getattr(target, "name", "")).lower()
        if getattr(target, "is_rough", False): return True
        if getattr(target, "role", "").lower() == "rough": return True
        return "rough" in name

    
    def toggle_extruded_visibility(self, state=None):
        """Show/hide both the exported yellow grid and the preview-only u/v actors."""
        active = self.get_active_target()
        vis = bool(self.show_extruded_cb.isChecked()) if state is None else bool(state)
        if getattr(active, "extruded_actor", None) is not None:
            try: active.extruded_actor.SetVisibility(vis)
            except Exception: pass
        if hasattr(active, "extruded_side_actors") and active.extruded_side_actors:
            for a in active.extruded_side_actors:
                try: a.SetVisibility(vis)
                except Exception: pass
        try: self.plotter.render()
        except Exception: pass

    def export_extruded_stl(self):
        """Export only the yellow extruded solid (no rays/lines are included)."""
        active = self.get_active_target()
        if active.extruded_grid is None or active.extruded_grid.n_cells == 0:
            QtWidgets.QMessageBox.information(self, "Nothing to export", "No extruded geometry available. Build it first.")
            return

        # Rays are actors (not part of the mesh); clear for tidiness (optional)
        self._clear_rays(active)

        fname, _ = QFileDialog.getSaveFileName(self, "Save Extruded STL", "", "STL Files (*.stl)")
        if not fname:
            return
        try:
            active.extruded_grid.save(fname)  # STL writer chosen by extension
            QtWidgets.QMessageBox.information(self, "Saved", f"Extruded STL saved:\n{fname}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Save failed", f"Could not save STL:\n{e}")


    # ---------------- Heatmap (explainability) ----------------
    def paint_active_heatmap(self, active: TargetBundle, other: TargetBundle):
        if active.mesh is None or not active.facet_results:
            return
        try:
            tri = active.mesh.triangulate().clean()
        except Exception:
            return
        centers = tri.cell_centers().points
        scal = np.zeros(tri.n_cells, dtype=float)

        for fid, res in active.facet_results.items():
            hull2d = res.get('hull2d')
            if hull2d is None or hull2d.shape[0]<3:
                continue
            c = res['centroid']; n = res['normal']; u = res['u']; v = res['v']
            poly = Path(hull2d)
            rel = centers - c
            xy = np.column_stack([rel@u, rel@v])
            mask = poly.contains_points(xy)
            if not np.any(mask):
                continue
            # approximate depth at these centers via nearest "other" point along normal
            pts_near = np.asarray(other.mesh.points)
            kd = cKDTree(pts_near)
            idx = np.where(mask)[0]
            proj = centers[idx]
            dists, nn = kd.query(proj)
            signed = np.dot(pts_near[nn] - c, n)
            scal[idx] = np.maximum(0.0, signed)

        tri.cell_data['work'] = scal
        try:
            if getattr(active, "_heat_actor", None) is not None:
                self.plotter.remove_actor(active._heat_actor)
            active._heat_actor = self.plotter.add_mesh(
            tri, scalars='work', cmap='plasma',
            opacity=0.55, culling='back', name=f'{active.name}_heat',show_scalar_bar=False
                )
            self.update_status("Heatmap updated")
        except Exception as e:
            print("Heatmap error:", e)

    def toggle_heatmap_visibility(self):
        active = self.get_active_target()
        want = bool(self.show_heatmap_cb.isChecked())
        if getattr(active, "_heat_actor", None) is not None:
            try:
                active._heat_actor.SetVisibility(want)
                self.plotter.render()
            except Exception:
                pass
    
    def plan_sequence_oo(self, active: TargetBundle, pass_name: str, alpha_angle=0.5):
        """
        Order facets to minimize distance + alpha * angle_change between consecutive facets.
        """
        items=[]
        for fid,f in enumerate(active.facets):
            res = active.facet_results.get(fid,{})
            passes = res.get('passes', [])
            p = next((x for x in passes if x[0]==pass_name), None)
            if p and p[1]>1e-9:
                items.append((fid, res.get('centroid'), res.get('normal')))
        if len(items)<=1: 
            return [fid for fid,_,_ in items]

        remaining = set(fid for fid,_,_ in items)
        # start with facet of largest mean depth for this pass
        start = max(items, key=lambda it: active.facet_results[it[0]].get('mean_depth',0.0))[0]
        cur = start
        order=[cur]; remaining.remove(cur)
        centers = {fid: c for fid,c,_ in items}
        normals  = {fid: n for fid,_,n in items}

        while remaining:
            best=None; bestcost=1e18
            for cand in remaining:
                d = np.linalg.norm(centers[cur]-centers[cand])
                ang = 1.0 - float(np.dot(normals[cur], normals[cand]))
                cost = d + alpha_angle*ang
                if cost<bestcost:
                    bestcost=cost; best=cand
            order.append(best); remaining.remove(best); cur=best

        # 2-opt polish
        def seq_cost(seq):
            s=0.0
            for i in range(len(seq)-1):
                a,b = seq[i], seq[i+1]
                s += np.linalg.norm(centers[a]-centers[b]) + alpha_angle*(1.0-np.dot(normals[a], normals[b]))
            return s
        improved=True
        while improved:
            improved=False
            for i in range(1, len(order)-2):
                for j in range(i+1, len(order)-1):
                    new = order[:i]+order[i:j+1][::-1]+order[j+1:]
                    if seq_cost(new) < seq_cost(order)-1e-6:
                        order=new; improved=True
        return order

    def generate_sequence(self):
        active = self.get_active_target()

        if not active.facet_results or not active.facets:
            QtWidgets.QMessageBox.warning(self, "No data", "Compute facets first")
            return

        sample_passes = next(iter(active.facet_results.values())).get('passes', [])
        pass_names = [p[0] for p in sample_passes] if sample_passes else ["Coarse", "Medium", "Fine"]

        seq_text_lines = []
        self.sequence_plan = []

        for pname in pass_names:
            # Collect entries
            entries = []
            for fid, f in enumerate(active.facets):
                res = active.facet_results.get(fid, {})
                passes = res.get('passes', [])
                pass_entry = None
                for p in passes:
                    if p[0] == pname:
                        pass_entry = p
                        break
                if pass_entry is None:
                    continue
                depth = pass_entry[1]
                vol = pass_entry[2]
                if depth <= 1e-9:
                    continue
                entries.append((fid, depth, vol, res.get('footprint_area', 0.0), res.get('max_depth', 0.0), res.get('time_total_sec',0.0)))

            # Plan sequence with orientation-aware 2-opt
            order = self.plan_sequence_oo(active, pname, alpha_angle=0.5)
            id2e = {e[0]:e for e in entries}
            entries_sorted = [id2e[i] for i in order if i in id2e]

            self.sequence_plan.append((pname, entries_sorted))

            seq_text_lines.append(f"=== PASS: {pname} ({len(entries_sorted)} facets) ===")
            for i, e in enumerate(entries_sorted):
                fid, depth, vol, area, maxd, tsec = e
                seq_text_lines.append(f"{i+1:02d}. Facet {fid}: pass_depth={depth:.6f}, pass_vol≈{vol:.6e}, max_depth={maxd:.6f}, area={area:.6e}, est_time≈{tsec/60.0:.1f}m")
            seq_text_lines.append("")

        self.sequence_text.setPlainText("\n".join(seq_text_lines))
        self.export_seq_btn.setEnabled(True)
        QtWidgets.QMessageBox.information(self, "Sequence generated", f"Sequence planner created for {active.name} (see panel).")

    # ---------------- Exports (Active) ----------------
    def export_csv(self):
        active = self.get_active_target()
        if not active.facet_results:
            QtWidgets.QMessageBox.warning(self, "No data", "Compute facets first")
            return
        fname_suggest = f"{active.name}_facets.csv"
        fname, _ = QFileDialog.getSaveFileName(self, "Save facets CSV", fname_suggest, "CSV Files (*.csv)")
        if not fname:
            return
        try:
            import csv
            with open(fname, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow([
                    'facet_id', 'facet_type', 'n_faces', 'max_depth', 'mean_depth',
                    'depth_p95', 'depth_rms', 'planarity_rms',
                    'footprint_area', 'perimeter',
                    'approx_volume', 'voxel_volume',
                    'points_inside_count',
                    'passes', 'time_total_sec'
                ])
                for fid, facet in enumerate(active.facets):
                    res = active.facet_results.get(fid, {})
                    n_faces = len(facet['faces_idx'])
                    max_d = res.get('max_depth', 0.0)
                    mean_d = res.get('mean_depth', 0.0)
                    p95 = res.get('depth_p95', 0.0)
                    rms = res.get('depth_rms', 0.0)
                    planr = res.get('planarity_rms', 0.0)
                    area = res.get('footprint_area', 0.0)
                    perim = res.get('perimeter', 0.0)
                    approx_v = res.get('approx_volume', 0.0)
                    voxel_v = res.get('voxel_volume', 0.0)
                    cnt = int(res.get('points_inside_idx').size if res.get('points_inside_idx') is not None else 0)
                    passes = res.get('passes', [])
                    passes_str = ";".join([f"{n}:{d:.6f}:{v:.6e}" for (n,d,v) in passes])
                    tsec = res.get('time_total_sec', 0.0)
                    w.writerow([
                        fid, facet.get('facet_type','Unknown'), n_faces, max_d, mean_d,
                        p95, rms, planr,
                        area, perim, approx_v, voxel_v, cnt, passes_str, tsec
                    ])
            QtWidgets.QMessageBox.information(self, "Saved", f"CSV saved to {fname}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save CSV: {e}")

    def export_selected_facet_csv(self):
        active = self.get_active_target()
        other = self.get_other_target()

        if not active.facet_results:
            QtWidgets.QMessageBox.warning(self, "No data", "Compute selected facet first")
            return

        vis_idx = int(self.facet_spin.value())
        if vis_idx < 0 or vis_idx >= len(active.visible_facet_ids):
            QtWidgets.QMessageBox.warning(self, "No data", "Select a valid facet first")
            return
        fid = active.visible_facet_ids[vis_idx]
        res = active.facet_results.get(fid, None)
        if res is None:
            QtWidgets.QMessageBox.warning(self, "No data", "Compute selected facet first")
            return

        fname_suggest = f"{active.name}_facet_{fid}.csv"
        fname, _ = QFileDialog.getSaveFileName(self, "Save selected facet CSV", fname_suggest, "CSV Files (*.csv)")
        if not fname:
            return

        try:
            import csv
            with open(fname, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(['point_index', 'x', 'y', 'z', 'depth'])
                idxs = res.get('points_inside_idx', np.array([], dtype=int))
                pts = np.asarray(other.mesh.points)[idxs] if (other.mesh is not None and idxs.size > 0) else np.zeros((0, 3))
                depths = res.get('depths_array', np.array([]))
                for i, (p, d) in enumerate(zip(pts, depths)):
                    w.writerow([int(idxs[i]), float(p[0]), float(p[1]), float(p[2]), float(d)])
            QtWidgets.QMessageBox.information(self, "Saved", f"Selected facet details saved to {fname}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save CSV: {e}")

    def export_sequence_csv(self):
        if not self.sequence_plan:
            QtWidgets.QMessageBox.warning(self, "No sequence", "Generate sequence first")
            return
        active = self.get_active_target()
        fname_suggest = f"{active.name}_sequence.csv"
        fname, _ = QFileDialog.getSaveFileName(self, "Save sequence CSV", fname_suggest, "CSV Files (*.csv)")
        if not fname:
            return
        try:
            import csv
            with open(fname, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(['pass_name', 'order_idx', 'facet_id', 'pass_depth', 'pass_vol', 'footprint_area', 'facet_max_depth', 'facet_time_sec'])
                for pname, entries in self.sequence_plan:
                    for i, e in enumerate(entries):
                        fid, depth, vol, area, maxd, tsec = e
                        w.writerow([pname, i, fid, depth, vol, area, maxd, tsec])
            QtWidgets.QMessageBox.information(self, "Saved", f"Sequence saved to {fname}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save CSV: {e}")


    def update_visual_center(self, *_):
        """Optional: nudge meshes so their midpoints visually overlap a bit."""
        try:
            pol, rough = self.target_polished.mesh, self.target_rough.mesh
            if pol is None or rough is None:
                return
            def center(m): 
                b = np.array(m.bounds).reshape(3,2); return (b[:,0]+b[:,1]) * 0.5
            c_pol, c_r = center(pol), center(rough)
            c_mid = 0.5*(c_pol + c_r)
            pol.translate(c_mid - c_pol, inplace=True)
            rough.translate(c_mid - c_r, inplace=True)
            if self.target_polished.actor: self.plotter.update_coordinates(pol.points, mesh=self.target_polished.actor)
            if self.target_rough.actor:    self.plotter.update_coordinates(rough.points, mesh=self.target_rough.actor)
            self._refresh_edge_overlays()
            self.plotter.reset_camera()
        except Exception:
            pass

    def on_toggle_ortho(self, *_):
        self._set_ortho(bool(self.ortho_cb.isChecked()))

    def view_iso(self): 
        try: self.plotter.view_isometric(); self.plotter.reset_camera()
        except Exception: pass

    def _view_axis(self, vec, up=None):
        try:
            self.plotter.view_vector(vec, viewup=up)
            self.plotter.reset_camera()
        except Exception:
            pass

    def view_top(self):    self._view_axis((0, 0, 1), up=(0, 1, 0))
    def view_bottom(self): self._view_axis((0, 0,-1), up=(0,-1, 0))
    def view_front(self):  self._view_axis((0, 1, 0), up=(0, 0, 1))
    def view_back(self):   self._view_axis((0,-1, 0), up=(0, 0, 1))
    def view_left(self):   self._view_axis((1, 0, 0), up=(0, 0, 1))
    def view_right(self):  self._view_axis((-1,0, 0), up=(0, 0, 1))

    def focus_camera_on_facet(self, fid_or_vis_idx):
        try:
            active = self.get_active_target()
            if not active.facets:
                self.smooth_reset(); return

            if isinstance(fid_or_vis_idx, int) and fid_or_vis_idx in getattr(active, "visible_facet_ids", []):
                fid = fid_or_vis_idx
            else:
                fid = active.visible_facet_ids[
                    max(0, min(int(fid_or_vis_idx), len(active.visible_facet_ids) - 1))
                ]

            cells = active.facets[fid].get('faces_idx', [])
            if not cells:
                self.smooth_reset(); return

            sub = active.mesh.extract_cells(np.asarray(cells, int))
            self.fly_to_bounds(sub.bounds, duration=0.60)  # smooth transition
        except Exception:
            self.smooth_reset()


    def on_lock_calc_toggled(self, checked: bool):
        self.calc_locked = bool(checked)
        disabled = bool(checked)
        for w in [self.compute_selected_btn, self.compute_all_btn, self.facet_spin,
                self.prev_btn, self.next_btn]:
            try: w.setEnabled(not disabled)
            except Exception: pass
        self.update_status("Facet calculations locked" if disabled else "Facet calculations unlocked")

    def clear_all_calculations(self):
        # wipe per-target overlays/results/volumes/labels
        for tgt in [self.target_polished, self.target_rough]:
            tgt.facet_results = {}
            tgt.facets = getattr(tgt, 'facets', [])
            # overlays
            for a in [tgt.facet_poly_actor, tgt.points_actor, tgt.highlight_actor,
                    tgt.dim_label_actor, tgt.pass_red_actor, tgt.pass_green_actor,
                    tgt.pass_blue_actor, tgt._heat_actor, tgt.facet_edges_actor,
                    tgt._facet_labels_actor, tgt.extruded_actor, tgt.cut_volume_actor]:
                if a is not None:
                    try: self.plotter.remove_actor(a)
                    except Exception: pass
            tgt.facet_poly_actor = tgt.points_actor = tgt.highlight_actor = None
            tgt.dim_label_actor = None; tgt.edge_line_actors = []
            tgt.pass_red_actor = tgt.pass_green_actor = tgt.pass_blue_actor = None
            tgt._heat_actor = tgt.facet_edges_actor = None
            tgt._facet_labels_actor = None
            tgt.extruded_actor = None; tgt.extruded_grid = None
            tgt.cut_volume_actor = None; tgt.cut_volume_grid = None
        self.sequence_text.clear()
        try: self.plotter.render()
        except Exception: pass
        self.update_status("Cleared calculations and overlays")

    # --- Fix: avoid double-adding facet edge overlays; handle fallbacks cleanly
    def _add_or_update_facet_edges(self, target: 'TargetBundle', angle_deg=22.0,
                                edge_color="#0b0b0b", edge_width=1, tube_radius=None):
        mesh = target.mesh
        if mesh is None: return
        self._remove_edges(target)
        try:
            base  = mesh.triangulate().clean()
            edges = _extract_feature_edges(base, angle_deg=angle_deg,
                                        feature_edges=False, boundary_edges=True,
                                        non_manifold_edges=True, manifold_edges=False)
            if edges.n_points == 0: return
            diag = _mesh_diag(base)
            r = float(tube_radius) if (tube_radius and tube_radius > 0) else max(1e-6, 0.002*diag)
            try:
                edge_geo = edges.tube(radius=r, n_sides=12)
                target.facet_edges_actor = self.plotter.add_mesh(
                    edge_geo, color=edge_color, lighting=False,
                    name=f"{target.name}_facet_edges", smooth_shading=False
                )
            except Exception:
                target.facet_edges_actor = self.plotter.add_mesh(
                    edges, color=edge_color, line_width=int(edge_width),
                    lighting=False, name=f"{target.name}_facet_edges",
                    render_lines_as_tubes=False, smooth_shading=False
                )
        except Exception:
            target.facet_edges_actor = None

    # --- Optional: heuristics to tag Table/Culet then add azimuths
    def _refine_polished_labels(self, facets, cg, ng):
        ng = _norm(np.asarray(ng))
        if not facets: return
        # compute planar (girdle-plane) radius for centroids
        cent = np.array([f['centroid'] for f in facets], float)
        # project to girdle plane
        def proj_g(p): 
            v = p - cg; return v - np.dot(v, ng)*ng
        radii = np.linalg.norm(np.vstack([proj_g(c) for c in cent]), axis=1)
        r_med = float(np.median(radii)) if radii.size else 1.0
        par_tol = POLISH_CLASS_PARAMS["parallel_tol"]
        cen_tol = POLISH_CLASS_PARAMS["center_tol"] * max(r_med, 1e-9)

        # TABLE: crown facets with normal ~ +ng and near center, pick largest area
        crown = [f for f in facets if f.get('facet_type') == 'Crown']
        cand_table = []
        for f in crown:
            n = _norm(np.asarray(f['normal'], float))
            if abs(np.dot(n, ng)) >= par_tol:
                r = np.linalg.norm(proj_g(np.asarray(f['centroid'], float)))
                if r <= cen_tol:
                    cand_table.append(f)
        if cand_table:
            tbl = max(cand_table, key=lambda x: float(x.get('footprint_area', 0.0)))
            tbl['facet_type'] = 'Table'

        # CULET: pavilion facets ~ parallel and near center, pick smallest area
        pav = [f for f in facets if f.get('facet_type') == 'Pavilion']
        cand_culet = []
        for f in pav:
            n = _norm(np.asarray(f['normal'], float))
            if abs(np.dot(n, ng)) >= par_tol:
                r = np.linalg.norm(proj_g(np.asarray(f['centroid'], float)))
                if r <= cen_tol:
                    cand_culet.append(f)
        if cand_culet:
            cu = min(cand_culet, key=lambda x: float(x.get('footprint_area', 0.0)))
            cu['facet_type'] = 'Culet'

        # finally, stamp azimuths using the (possibly) tagged table
        annotate_facets_with_azimuth(facets, cg=cg, ng=ng, table_facet=_pick_table_facet(facets))

    # --- Hook azimuth after extraction (replace your extract_facets_from_active_mesh body end)
    def extract_facets_from_active_mesh(self):
        tgt = self.get_active_target()
        if tgt.mesh is None:
            QtWidgets.QMessageBox.warning(self, "Error", f"Load a {tgt.name} mesh first")
            return
        tgt.facets = self.extract_facets(tgt, angle_tol_deg=1.0)

        # Add azimuths + color if we have something
        if tgt.facets:
            ng, cg = _compute_girdle_plane_from_facets(tgt.facets)
            if getattr(tgt, "name", "").lower() == "polished":
                # try to tag table/culet then annotate
                try: self._refine_polished_labels(tgt.facets, cg, ng)
                except Exception: annotate_facets_with_azimuth(tgt.facets, cg=cg, ng=ng)
            else:
                annotate_facets_with_azimuth(tgt.facets, cg=cg, ng=ng)
            self._apply_azimuth_coloring_if_available(tgt)

        self._update_visible_facet_ids()
        if not tgt.visible_facet_ids:
            QtWidgets.QMessageBox.information(self, "No non-girdle facets",
                                            "Facets were detected, but all are 'Girdle'. The index excludes girdle facets.")
            self.update_status("No non-girdle facets")
            return

        if self.get_other_target().mesh is not None:
            self.compute_all_facets()
        else:
            self.show_selected_facet(0)

        if getattr(self, "show_labels_cb", None) and self.show_labels_cb.isChecked():
            self.build_clickable_facet_labels()
        self.update_status("Facets extracted")

    # --- Finish generate_sequence and add CSV exporters --------------------------

    def generate_sequence(self):
        active = self.get_active_target()
        if not active.facet_results or not active.facets:
            QtWidgets.QMessageBox.warning(self, "No data", "Compute facets first")
            return

        sample_passes = next(iter(active.facet_results.values())).get('passes', [])
        pass_names = [p[0] for p in sample_passes] if sample_passes else ["Coarse", "Medium", "Fine"]

        self.sequence_plan = []
        seq = []
        rates = {"Coarse": MRR_COARSE, "Medium": MRR_MEDIUM, "Fine": MRR_FINE}

        for pname in pass_names:
            # collect entries that actually need this pass
            entries = []
            for fid, f in enumerate(active.facets):
                res = active.facet_results.get(fid, {})
                p = next((x for x in res.get('passes', []) if x[0] == pname), None)
                if p is None: continue
                depth, vol = float(p[1]), float(p[2])
                if depth <= 1e-12 or vol <= 0.0: continue
                entries.append((fid, depth, vol,
                                float(res.get('footprint_area', 0.0)),
                                float(res.get('max_depth', 0.0))))

            order = self.plan_sequence_oo(active, pname, alpha_angle=0.5)
            id2e = {e[0]: e for e in entries}
            ordered = [id2e[i] for i in order if i in id2e]
            self.sequence_plan.append((pname, ordered))

            seq.append(f"=== PASS: {pname} ({len(ordered)} facets) ===")
            total_vol = 0.0
            total_sec = 0.0
            for i, (fid, depth, vol, area, maxd) in enumerate(ordered, 1):
                mrr = max(rates.get(pname, MRR_MEDIUM), 1e-9)
                tsec = vol / mrr * 60.0 + SETUP_PENALTY_SEC
                total_vol += vol; total_sec += tsec
                seq.append(f"{i:02d}. FID {fid:03d}  d≈{depth:.4f}  vol≈{vol:.6e}  "
                        f"area≈{area:.6e}  maxd≈{maxd:.4f}  time≈{tsec/60.0:.1f}m")
            seq.append(f"TOTAL for {pname}: vol≈{total_vol:.6e}  time≈{total_sec/60.0:.1f}m\n")

        self.sequence_text.setText("\n".join(seq))
        self.export_seq_btn.setEnabled(True)
        self.update_status("Sequence generated")

    def export_csv(self):
        active = self.get_active_target()
        if not active.facet_results:
            QtWidgets.QMessageBox.warning(self, "No data", "Compute facets first")
            return
        fname, _ = QFileDialog.getSaveFileName(self, "Export Facets CSV", f"{active.name}_facets.csv", "CSV (*.csv)")
        if not fname: return
        import csv
        cols = ["fid","facet_type","azimuth_deg","footprint_area","perimeter",
                "max_depth","mean_depth","depth_p95","depth_rms",
                "approx_volume","voxel_volume","time_total_sec"]
        with open(fname, "w", newline="") as f:
            w = csv.writer(f); w.writerow(cols)
            for fid, fct in enumerate(active.facets):
                r = active.facet_results.get(fid, {})
                w.writerow([
                    fid, fct.get('facet_type', ''),
                    fct.get('azimuth_deg', ''),
                    r.get('footprint_area', 0.0), r.get('perimeter', 0.0),
                    r.get('max_depth', 0.0), r.get('mean_depth', 0.0),
                    r.get('depth_p95', 0.0), r.get('depth_rms', 0.0),
                    r.get('approx_volume', 0.0), r.get('voxel_volume', 0.0),
                    r.get('time_total_sec', 0.0)
                ])
        QtWidgets.QMessageBox.information(self, "Saved", f"CSV saved to {fname}")

    def export_selected_facet_csv(self):
        active = self.get_active_target()
        if not active.facet_results or not active.visible_facet_ids:
            QtWidgets.QMessageBox.warning(self, "No data", "Compute a facet first")
            return
        vis_idx = int(self.facet_spin.value())
        fid = active.visible_facet_ids[vis_idx]
        r = active.facet_results.get(fid)
        if r is None:
            QtWidgets.QMessageBox.warning(self, "No data", "Selected facet has no results")
            return
        fname, _ = QFileDialog.getSaveFileName(self, "Export Selected Facet CSV", f"{active.name}_facet_{fid}.csv", "CSV (*.csv)")
        if not fname: return
        import csv
        with open(fname, "w", newline="") as f:
            w = csv.writer(f)
            for k in ["max_depth","mean_depth","depth_p95","depth_rms",
                    "footprint_area","perimeter","approx_volume","voxel_volume","time_total_sec"]:
                w.writerow([k, r.get(k, 0.0)])
        QtWidgets.QMessageBox.information(self, "Saved", f"CSV saved to {fname}")

    def export_sequence_csv(self):
        if not getattr(self, "sequence_plan", None):
            QtWidgets.QMessageBox.warning(self, "No data", "Generate the sequence first")
            return
        active = self.get_active_target()
        fname, _ = QFileDialog.getSaveFileName(self, "Export Sequence CSV", f"{active.name}_sequence.csv", "CSV (*.csv)")
        if not fname: return
        import csv
        with open(fname, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["pass","order","fid","depth","volume"])
            for pname, items in self.sequence_plan:
                for i,(fid, depth, vol, *_rest) in enumerate(items, 1):
                    w.writerow([pname, i, fid, depth, vol])
        QtWidgets.QMessageBox.information(self, "Saved", f"CSV saved to {fname}")

def main():
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    win = PolishPlanner()
    win.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()            
