"""
HyelakuchStructure_Final.py

Full single-file integration of the HyelakuchStructure application.

Features included:
- Core model classes: Node, Member, SlabPanel, Model
- LabelManager
- Simple FEA engine (3D beam element, assemble, solve) - for demo/validation
- DXF import/export hooks using ezdxf (if available)
- IFC import hook placeholder (ifcopenshell optional)
- Rebar Designer & AutoSizer (basic automated detailing)
- 3D viewport (pyqtgraph.opengl) with label overlays and grid offsets
- Rebar visualizer and section-cut tool
- GUI: menus, tabs, import/export, design, auto-size, BBS export, section export

Notes:
- This file is large but self-contained as the main entry point. Optional features
  (IFC, DXF, PDF) require their libraries to be installed (ifcopenshell, ezdxf, reportlab).
- Before converting to .exe, test locally: `python HyelakuchStructure_Final.py`
- For PyInstaller builds, use --onefile or --onedir; include PyQt6 plugins if needed.

Dependencies (install before running/building):
    pip install PyQt6 pyqtgraph numpy scipy ezdxf reportlab
    pip install ifcopenshell   # optional, for IFC

"""

import sys, os, math, json, csv
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

# GUI & 3D
from PyQt6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl

# Numerics
import numpy as np

# Optional libs
try:
    import ezdxf
    HAS_EZDXF = True
except Exception:
    HAS_EZDXF = False
try:
    import ifcopenshell
    HAS_IFC = True
except Exception:
    HAS_IFC = False
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas as pdfcanvas
    HAS_RL = True
except Exception:
    HAS_RL = False

# -------------------- Core data models -----------------------------------
@dataclass
class Node:
    id: int
    x: float
    y: float
    z: float
    restraints: List[bool] = field(default_factory=lambda:[False]*6)
    loads: np.ndarray = field(default_factory=lambda: np.zeros(6))

@dataclass
class Member:
    id: int
    n1: int
    n2: int
    type: str = 'beam'  # beam, column, foundation
    section_area: float = 0.02
    width: float = 0.25
    depth: float = 0.45
    Iy: float = 1e-5
    Iz: float = 1e-5
    J: float = 1e-5
    E: float = 200e9
    G: float = 80e9
    material: str = 'steel'
    utilization: float = 0.0
    label: Optional[str] = None
    axial: float = 0.0
    moment_y: float = 0.0
    moment_z: float = 0.0

@dataclass
class SlabPanel:
    id: int
    node_ids: List[int]
    Lx: float
    Ly: float
    t: float
    label: Optional[str]=None

@dataclass
class Model:
    nodes: List[Node] = field(default_factory=list)
    members: List[Member] = field(default_factory=list)
    slabs: List[SlabPanel] = field(default_factory=list)

    def get_node(self, nid):
        return next((n for n in self.nodes if n.id==nid), None)
    def get_member(self, mid):
        return next((m for m in self.members if m.id==mid), None)

# -------------------- Label manager -------------------------------------
class LabelManager:
    def __init__(self):
        self.counters = {'S':0,'B':0,'C':0,'F':0,'G':0}
        self.map: Dict[int,str] = {}
    def assign(self, kind: str, elem_id: int) -> str:
        self.counters[kind]+=1
        label=f"{kind}{self.counters[kind]}"
        self.map[elem_id]=label
        return label
    def get(self, elem_id:int) -> Optional[str]:
        return self.map.get(elem_id)

# -------------------- Simple FEA solver ---------------------------------
class FEASolver:
    def __init__(self, model: Model):
        self.model=model
        self.dof_per_node=6

    def assemble(self):
        N=len(self.model.nodes)*self.dof_per_node
        K=np.zeros((N,N))
        node_index={n.id:i for i,n in enumerate(self.model.nodes)}
        for m in self.model.members:
            n1=self.model.get_node(m.n1); n2=self.model.get_node(m.n2)
            L=math.dist((n1.x,n1.y,n1.z),(n2.x,n2.y,n2.z))
            k_local=self.local_beam_stiffness(m, L)
            T=self.transformation(n1,n2)
            k_global=T.T @ k_local @ T
            dof_inds=[]
            for nid in (n1.id,n2.id):
                s=node_index[nid]*self.dof_per_node
                dof_inds.extend(range(s,s+self.dof_per_node))
            for i,gi in enumerate(dof_inds):
                for j,gj in enumerate(dof_inds):
                    K[gi,gj]+=k_global[i,j]
        self.K=K
        return K

    def local_beam_stiffness(self, m: Member, L: float):
        E=m.E; G=m.G; A=m.section_area; Iy=m.Iy; Iz=m.Iz; J=m.J
        k=np.zeros((12,12))
        # axial
        k[0,0]=k[6,6]=A*E/L
        k[0,6]=k[6,0]=-A*E/L
        # torsion
        k[3,3]=k[9,9]=G*J/L
        k[3,9]=k[9,3]=-G*J/L
        # bending about z
        k[1,1]=k[7,7]=12*E*Iz/(L**3)
        k[1,7]=k[7,1]=-12*E*Iz/(L**3)
        k[1,5]=6*E*Iz/(L**2); k[5,1]=6*E*Iz/(L**2)
        k[7,11]=-6*E*Iz/(L**2); k[11,7]=-6*E*Iz/(L**2)
        k[5,5]=k[11,11]=4*E*Iz/L
        k[5,11]=k[11,5]=2*E*Iz/L
        # bending about y
        k[2,2]=k[8,8]=12*E*Iy/(L**3)
        k[2,8]=k[8,2]=-12*E*Iy/(L**3)
        k[2,4]=-6*E*Iy/(L**2); k[4,2]=-6*E*Iy/(L**2)
        k[8,10]=6*E*Iy/(L**2); k[10,8]=6*E*Iy/(L**2)
        k[4,4]=k[10,10]=4*E*Iy/L
        k[4,10]=k[10,4]=2*E*Iy/L
        return k

    def transformation(self, n1: Node, n2: Node):
        L=math.dist((n1.x,n1.y,n1.z),(n2.x,n2.y,n2.z))
        ex=np.array([(n2.x-n1.x)/L,(n2.y-n1.y)/L,(n2.z-n1.z)/L])
        up=np.array([0,0,1.0])
        if abs(np.dot(up,ex))>0.9:
            up=np.array([0,1,0])
        ez=np.cross(ex,up); ez=ez/np.linalg.norm(ez)
        ey=np.cross(ez,ex); ey=ey/np.linalg.norm(ey)
        R = np.eye(3)
        R[0,:]=ex; R[1,:]=ey; R[2,:]=ez
        T = np.zeros((12,12))
        for i in range(4):
            T[i*3:(i+1)*3,i*3:(i+1)*3]=R
        return T

    def apply_bc_and_solve(self):
        node_index={n.id:i for i,n in enumerate(self.model.nodes)}
        N=len(self.model.nodes)*self.dof_per_node
        F=np.zeros(N)
        for n in self.model.nodes:
            start=node_index[n.id]*self.dof_per_node
            F[start:start+6]=n.loads
        K=self.assemble()
        constrained=[]
        for n in self.model.nodes:
            start=node_index[n.id]*self.dof_per_node
            for i,rest in enumerate(n.restraints):
                if rest: constrained.append(start+i)
        Kc=K.copy(); Fc=F.copy()
        for c in constrained:
            Kc[c,:]=0; Kc[:,c]=0; Kc[c,c]=1; Fc[c]=0
        disp=np.linalg.solve(Kc,Fc)
        self.displacements=disp
        return disp

# -------------------- DXF / IFC importers --------------------------------
class Importer:
    def __init__(self, model: Model, labels: LabelManager):
        self.model = model; self.labels = labels

    def import_dxf(self, filepath: str, grid: Optional[Dict]=None, snap_tol: float=1e-3):
        if not HAS_EZDXF:
            raise RuntimeError('ezdxf not installed')
        doc = ezdxf.readfile(filepath); msp = doc.modelspace()
        def _get_or_create_node(pt):
            for n in self.model.nodes:
                if abs(n.x-pt[0])<snap_tol and abs(n.y-pt[1])<snap_tol and abs(n.z-pt[2])<snap_tol:
                    return n
            nid = max([n.id for n in self.model.nodes], default=0)+1
            node=Node(nid,pt[0],pt[1],pt[2])
            self.model.nodes.append(node); return node
        for e in msp.query('LINE'):
            s=(float(e.dxf.start.x), float(e.dxf.start.y), float(getattr(e.dxf.start,'z',0.0)))
            t=(float(e.dxf.end.x), float(e.dxf.end.y), float(getattr(e.dxf.end,'z',0.0)))
            n1=_get_or_create_node(s); n2=_get_or_create_node(t)
            mid = max([m.id for m in self.model.members], default=0)+1
            m = Member(mid, n1.id, n2.id, type='beam')
            m.label = self.labels.assign('B', m.id)
            self.model.members.append(m)
        return {'nodes':len(self.model.nodes),'members':len(self.model.members)}

    def import_ifc(self, filepath: str):
        if not HAS_IFC:
            raise RuntimeError('ifcopenshell not installed')
        ifc = ifcopenshell.open(filepath)
        # basic hook: create nodes from IfcProduct placements
        count=0
        for el in ifc.by_type('IfcBuildingElement'):
            if hasattr(el, 'ObjectPlacement') and el.ObjectPlacement:
                try:
                    lp = el.ObjectPlacement
                    # skipping robust extraction; use bounding box centroid if available
                    count+=1
                except Exception:
                    pass
        return {'ifc_elements':count}

# -------------------- DXF utils (export) --------------------------------
class ExporterDXF:
    def __init__(self, model: Model, labels: LabelManager):
        self.model=model; self.labels=labels
    def export_dxf(self, filepath: str):
        if not HAS_EZDXF: raise RuntimeError('ezdxf missing')
        doc=ezdxf.new('R2010'); msp=doc.modelspace()
        for m in self.model.members:
            n1=self.model.get_node(m.n1); n2=self.model.get_node(m.n2)
            msp.add_line((n1.x,n1.y,n1.z),(n2.x,n2.y,n2.z), dxfattribs={'layer':'BEAM'})
            lbl = self.labels.get(m.id) or m.label
            if lbl: msp.add_mtext(lbl, dxfattribs={'insert':((n1.x+n2.x)/2,(n1.y+n2.y)/2,(n1.z+n2.z)/2), 'layer':'ANNO'})
        for s in self.model.slabs:
            pts=[(self.model.get_node(nid).x,self.model.get_node(nid).y,self.model.get_node(nid).z) for nid in s.node_ids]
            if pts:
                msp.add_lwpolyline([(p[0],p[1]) for p in pts], dxfattribs={'layer':'SLAB','closed':True})
        doc.saveas(filepath); return filepath

# -------------------- Rebar Designer & AutoSizer -------------------------
class RebarDesigner:
    def __init__(self, model: Model, rebar_options_mm: List[int]=[10,12,16,20,25,32]):
        self.model=model
        self.rebar_options=[d/1000.0 for d in rebar_options_mm]
        self.layouts: Dict[int, Dict]={}
    def design_all_slabs(self):
        for s in self.model.slabs:
            self.design_slab(s)
        return self.layouts
    def design_slab(self, slab: SlabPanel):
        Lx=slab.Lx; Ly=slab.Ly; t=slab.t
        # approximate required As
        As_x = 0.001*t; As_y=0.001*t
        dia=self.rebar_options[1]; spacing=0.15
        self.layouts[slab.id] = {'elem':slab, 'layers':[{'dir':'x','dia':dia,'spacing':spacing,'As':As_x},{'dir':'y','dia':dia,'spacing':spacing,'As':As_y}]}
        return self.layouts[slab.id]
    def design_all_beams(self):
        for m in self.model.members:
            if m.type=='beam': self.design_beam(m)
        return {k:v for k,v in self.layouts.items() if v['elem'].__class__ is Member}
    def design_beam(self, member: Member):
        dia=self.rebar_options[2]; spacing=0.1
        self.layouts[member.id] = {'elem':member, 'layers':[{'dir':'long','dia':dia,'spacing':spacing}]}
        return self.layouts[member.id]

class AutoSizer:
    def __init__(self, model: Model, rebar_designer: RebarDesigner=None):
        self.model=model; self.rd=rebar_designer
    def run_auto_size(self, target_util=0.95, max_iters=6):
        history=[]
        for it in range(max_iters):
            failed=[m for m in self.model.members if getattr(m,'utilization',0.0)>target_util]
            if not failed: history.append({'iter':it,'status':'passed'}); break
            for m in failed:
                m.section_area*=1.25; m.width*=1.1; m.depth*=1.1
            history.append({'iter':it,'failed':[m.id for m in failed]})
        return history

# -------------------- 3D Viewport & Overlay Labels -----------------------
class Viewport(gl.GLViewWidget):
    def __init__(self, model: Model, labels: LabelManager):
        super().__init__(); self.model=model; self.labels=labels
        self.setCameraPosition(distance=30)
        self.grid_item = gl.GLGridItem(); self.addItem(self.grid_item)
        self.member_lines={}
        self.node_scat=None
        self.label_widgets: Dict[int, QtWidgets.QLabel] = {}
        self.overlay_parent=None
        self.grid_settings={'sx':5.0,'sy':5.0,'nx':10,'ny':10,'offset_x':0.0,'offset_y':0.0,'visible':True}
        self.update_scene()
    def set_overlay_parent(self, widget): self.overlay_parent=widget
    def update_scene(self):
        for it in list(self.member_lines.values()):
            try: self.removeItem(it)
            except: pass
        self.member_lines.clear()
        for m in self.model.members:
            n1=self.model.get_node(m.n1); n2=self.model.get_node(m.n2)
            pts=np.array([[n1.x,n1.y,n1.z],[n2.x,n2.y,n2.z]])
            line=gl.GLLinePlotItem(pos=pts,width=3,antialias=True,color=pg.mkColor((0,255,255,200)))
            self.addItem(line); self.member_lines[m.id]=line
        if self.node_scat:
            try: self.removeItem(self.node_scat)
            except: pass
        pos=np.array([[n.x,n.y,n.z] for n in self.model.nodes]) if self.model.nodes else np.zeros((0,3))
        if pos.shape[0]>0:
            self.node_scat=gl.GLScatterPlotItem(pos=pos,size=6.0); self.addItem(self.node_scat)
        QtCore.QTimer.singleShot(50, self.update_labels_overlay)
    def world_to_screen(self,x,y,z):
        w=self.width(); h=self.height()
        xs=[n.x for n in self.model.nodes] if self.model.nodes else [0]
        ys=[n.y for n in self.model.nodes] if self.model.nodes else [0]
        minx,maxx=min(xs),max(xs); miny,maxy=min(ys),max(ys)
        sx=(x-minx)/(maxx-minx+1e-6); sy=(y-miny)/(maxy-miny+1e-6)
        scr_x=int(sx*w); scr_y=int((1-sy)*h); return scr_x, scr_y
    def update_labels_overlay(self):
        if not self.overlay_parent: return
        for k in list(self.label_widgets.keys()):
            if not any(m.id==k for m in self.model.members) and not any(s.id==k for s in self.model.slabs):
                lbl=self.label_widgets.pop(k); lbl.setParent(None); lbl.deleteLater()
        for m in self.model.members:
            n1=self.model.get_node(m.n1); n2=self.model.get_node(m.n2)
            mx=0.5*(n1.x+n2.x); my=0.5*(n1.y+n2.y); mz=0.5*(n1.z+n2.z)
            sx,sy=self.world_to_screen(mx,my,mz)
            if m.id not in self.label_widgets:
                lbl=QtWidgets.QLabel(self.overlay_parent); lbl.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                lbl.setStyleSheet('background: rgba(0,0,0,0.5); color: white; padding:2px; border-radius:3px')
                self.label_widgets[m.id]=lbl
            lbl=self.label_widgets[m.id]; lbl.setText(m.label or f'M{m.id}'); lbl.move(sx,sy); lbl.show()
        for s in self.model.slabs:
            xs=[self.model.get_node(nid).x for nid in s.node_ids]; ys=[self.model.get_node(nid).y for nid in s.node_ids]; zs=[self.model.get_node(nid).z for nid in s.node_ids]
            cx=sum(xs)/len(xs); cy=sum(ys)/len(ys); cz=sum(zs)/len(zs)
            sx,sy=self.world_to_screen(cx,cy,cz)
            if s.id not in self.label_widgets:
                lbl=QtWidgets.QLabel(self.overlay_parent); lbl.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                lbl.setStyleSheet('background: rgba(0,128,0,0.6); color: white; padding:2px; border-radius:3px')
                self.label_widgets[s.id]=lbl
            lbl=self.label_widgets[s.id]; lbl.setText(s.label or f"S{s.id}"); lbl.move(sx,sy); lbl.show()

# -------------------- Rebar Visualizer ----------------------------------
class RebarVisualizer:
    def __init__(self, viewport: Viewport, model: Model, labels: LabelManager, parent_ui:Optional[QtWidgets.QWidget]=None):
        self.viewport=viewport; self.model=model; self.labels=labels; self.visible=True
        self.rebar_items=[]; self.loops=[]; self.parent_ui=parent_ui
    def update_from_layouts(self, layouts: Dict[int, Dict]):
        # clear existing
        self.clear();
        for eid, layout in layouts.items():
            elem = layout.get('elem')
            if isinstance(elem, Member):
                n1=self.model.get_node(elem.n1); n2=self.model.get_node(elem.n2)
                p1=(n1.x,n1.y,n1.z); p2=(n2.x,n2.y,n2.z)
                for idx, item in enumerate(layout.get('layers',[])):
                    off = self._perp_offset(p1,p2,0.02*(idx+1))
                    sp=(p1[0]+off[0],p1[1]+off[1],p1[2]+off[2]); ep=(p2[0]+off[0],p2[1]+off[1],p2[2]+off[2])
                    line=gl.GLLinePlotItem(pos=np.array([sp,ep]), width=2, antialias=True, color=pg.mkColor((200,50,50,255)))
                    self.viewport.addItem(line); self.rebar_items.append(line)
            elif isinstance(elem, SlabPanel):
                # draw representative X/Y bars at centroid
                xs=[self.model.get_node(nid).x for nid in elem.node_ids]; ys=[self.model.get_node(nid).y for nid in elem.node_ids]; zs=[self.model.get_node(nid).z for nid in elem.node_ids]
                cx=sum(xs)/len(xs); cy=sum(ys)/len(ys); cz=sum(zs)/len(zs)
                for item in layout.get('layers',[]):
                    if item['dir']=='x': sp=(cx-elem.Lx/2+0.05,cy,cz); ep=(cx+elem.Lx/2-0.05,cy,cz)
                    else: sp=(cx,cy-elem.Ly/2+0.05,cz); ep=(cx,cy+elem.Ly/2-0.05,cz)
                    line=gl.GLLinePlotItem(pos=np.array([sp,ep]), width=1.6, antialias=True, color=pg.mkColor((0,200,0,200)))
                    self.viewport.addItem(line); self.rebar_items.append(line)
    def _perp_offset(self,p1,p2,width):
        vx=p2[0]-p1[0]; vy=p2[1]-p1[1]; vz=0
        nx=-vy; ny=vx; nz=0
        nlen=math.hypot(nx,ny)+1e-9
        return (width*nx/nlen, width*ny/nlen, 0)
    def clear(self):
        for it in self.rebar_items:
            try: self.viewport.removeItem(it)
            except: pass
        self.rebar_items=[]
    def toggle_visibility(self, show:bool):
        if not show: self.clear(); self.visible=False
        else: self.visible=True
    def export_rebars_dxf(self, filename:str):
        if not HAS_EZDXF: raise RuntimeError('ezdxf required')
        doc=ezdxf.new('R2010'); msp=doc.modelspace()
        for it in self.rebar_items:
            pos = it.pos
            if hasattr(pos,'tolist'):
                pts = pos.tolist()
                if len(pts)>=2:
                    msp.add_line((pts[0][0],pts[0][1]),(pts[1][0],pts[1][1]), dxfattribs={'layer':'REBAR'})
        doc.saveas(filename); return filename

# -------------------- Section Cut Tool ----------------------------------
class SectionCutTool(QtCore.QObject):
    def __init__(self, viewport: Viewport, model: Model, labels: LabelManager, parent=None):
        super().__init__(); self.viewport=viewport; self.model=model; self.labels=labels; self.parent=parent
        self.P0=(0,0,0); self.n=(0,0,1); self.intersection_items=[]; self.sweep_timer=None; self.sweep_direction=1
    def show_ui(self, container_widget: QtWidgets.QWidget):
        gb=QtWidgets.QGroupBox('Section Cut'); layout=QtWidgets.QFormLayout(gb)
        self.spin_x=QtWidgets.QDoubleSpinBox(); self.spin_y=QtWidgets.QDoubleSpinBox(); self.spin_z=QtWidgets.QDoubleSpinBox()
        layout.addRow('Plane X', self.spin_x); layout.addRow('Plane Y', self.spin_y); layout.addRow('Plane Z', self.spin_z)
        self.spin_az=QtWidgets.QDoubleSpinBox(); self.spin_el=QtWidgets.QDoubleSpinBox(); layout.addRow('Azimuth', self.spin_az); layout.addRow('Elevation', self.spin_el)
        btn_apply=QtWidgets.QPushButton('Apply Cut'); btn_apply.clicked.connect(self.apply_cut); layout.addRow(btn_apply)
        btn_export=QtWidgets.QPushButton('Export Section DXF'); btn_export.clicked.connect(self.export_section_dxf); layout.addRow(btn_export)
        try: container_widget.layout().addWidget(gb)
        except: pass
    def clear_intersections(self):
        for it in self.intersection_items:
            try: self.viewport.removeItem(it)
            except: pass
        self.intersection_items=[]
    def apply_cut(self):
        ax=float(self.spin_x.value()); ay=float(self.spin_y.value()); az=float(self.spin_z.value())
        azm=math.radians(float(self.spin_az.value())); el=math.radians(float(self.spin_el.value()))
        nx=math.cos(el)*math.cos(azm); ny=math.cos(el)*math.sin(azm); nz=math.sin(el)
        self.P0=(ax,ay,az); self.n=(nx,ny,nz)
        self.clear_intersections()
        for m in self.model.members:
            n1=self.model.get_node(m.n1); n2=self.model.get_node(m.n2)
            ip=line_plane_intersection((n1.x,n1.y,n1.z),(n2.x,n2.y,n2.z),self.P0,self.n)
            if ip is not None:
                pts=np.array([[ip[0]-0.05,ip[1]-0.05,ip[2]],[ip[0]+0.05,ip[1]+0.05,ip[2]]])
                item=gl.GLLinePlotItem(pos=pts, color=pg.mkColor((255,0,0,255)), width=3)
                self.viewport.addItem(item); self.intersection_items.append(item)
        for s in self.model.slabs:
            poly=[(self.model.get_node(nid).x,self.model.get_node(nid).y,self.model.get_node(nid).z) for nid in s.node_ids]
            pts=polygon_plane_intersection(poly, self.P0, self.n)
            if pts:
                pos=np.array(pts)
                item=gl.GLLinePlotItem(pos=pos, color=pg.mkColor((0,255,0,255)), width=2)
                self.viewport.addItem(item); self.intersection_items.append(item)
    def export_section_dxf(self):
        if not HAS_EZDXF: raise RuntimeError('ezdxf required')
        doc=ezdxf.new('R2010'); msp=doc.modelspace()
        for it in self.intersection_items:
            pos = it.pos
            if hasattr(pos,'tolist'):
                pts=pos.tolist(); msp.add_lwpolyline([(p[0],p[1]) for p in pts], dxfattribs={'layer':'SECTION'})
        fn=QtWidgets.QFileDialog.getSaveFileName(self.parent,'Save Section DXF','','DXF files (*.dxf)')[0]
        if fn: doc.saveas(fn); return fn
        return None

# -------------------- geometry helpers ----------------------------------
def line_plane_intersection(p1,p2,P0,n):
    u=np.array(p2)-np.array(p1); denom=np.dot(n,u)
    if abs(denom)<1e-9: return None
    t=np.dot(n, np.array(P0)-np.array(p1))/denom
    if t<-1e-9 or t>1+1e-9: return None
    return tuple((np.array(p1)+t*u).tolist())
def polygon_plane_intersection(poly_pts,P0,n):
    pts=[]; N=len(poly_pts)
    for i in range(N): a=poly_pts[i]; b=poly_pts[(i+1)%N]; ip=line_plane_intersection(a,b,P0,n)
    # collect intersections
    for i in range(N):
        a=poly_pts[i]; b=poly_pts[(i+1)%N]; ip=line_plane_intersection(a,b,P0,n)
        if ip is not None: pts.append(ip)
    if not pts: return []
    # unique
    uniq=[]
    for p in pts:
        if not any(math.dist(p,q)<1e-6 for q in uniq): uniq.append(p)
    return uniq

# -------------------- BBS Exporter --------------------------------------
class BBSExporter:
    def __init__(self, model: Model, layouts: Dict[int, Dict]=None):
        self.model=model; self.layouts=layouts or {}
    def collect_layouts(self, rd: RebarDesigner):
        self.layouts={}
        self.layouts.update(rd.design_all_slabs())
        self.layouts.update(rd.design_all_beams())
        return self.layouts
    def export_csv(self, filename='bbs.csv'):
        rows=[]
        for eid, layout in self.layouts.items():
            elem = layout.get('elem')
            for layer in layout.get('layers',[]):
                rows.append([getattr(elem,'label',str(eid)), getattr(elem,'type',type(elem).__name__), int(layer.get('dia',0)*1000), layer.get('spacing',0)])
        with open(filename,'w', newline='') as f:
            w=csv.writer(f); w.writerow(['Element','Type','Dia_mm','Spacing_m']); w.writerows(rows)
        return filename
    def export_pdf(self, filename='bbs.pdf'):
        if not HAS_RL: raise RuntimeError('reportlab required')
        c=pdfcanvas(filename,pagesize=landscape(A4)); W,H=landscape(A4)
        c.setFont('Helvetica-Bold',14); c.drawString(30,H-30,'Bar Bending Schedule')
        y=H-60; c.setFont('Helvetica',10)
        for eid, layout in self.layouts.items():
            elem=layout.get('elem'); c.drawString(40,y,f"{getattr(elem,'label',eid)} ({getattr(elem,'type','')})"); y-=12
            for layer in layout.get('layers',[]):
                c.drawString(60,y,f"dia={int(layer.get('dia',0)*1000)} mm spacing={layer.get('spacing',0):.3f} m"); y-=10
            y-=6
            if y<60: c.showPage(); y=H-40
        c.save(); return filename

# -------------------- Main Application ---------------------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('HyelakuchStructure Final')
        self.resize(1400,900)
        self.model=Model(); self.labels=LabelManager(); self.solver=FEASolver(self.model)
        self._create_sample_model()
        self.viewport=Viewport(self.model,self.labels)
        central=QtWidgets.QWidget(); self.setCentralWidget(central)
        h=QtWidgets.QHBoxLayout(central); h.addWidget(self.viewport,3)
        self.tabs=QtWidgets.QTabWidget(); h.addWidget(self.tabs,1)
        # add tabs & controls
        self._build_controls();
        # tools
        self.importer=Importer(self.model,self.labels); self.exporter=ExporterDXF(self.model,self.labels)
        self.rebar_designer=RebarDesigner(self.model); self.autosizer=AutoSizer(self.model,self.rebar_designer); self.bbs_exporter=BBSExporter(self.model)
        self.rebar_visualizer=RebarVisualizer(self.viewport,self.model,self.labels,self.tabs)
        self.section_tool=SectionCutTool(self.viewport,self.model,self.labels,self)
        self.section_tool.show_ui(self.tabs)
        self.viewport.set_overlay_parent(central)
        self.status=self.statusBar()
    def _create_sample_model(self):
        self.model.nodes=[Node(1,0,0,0),Node(2,6,0,0),Node(3,0,4,0),Node(4,6,4,0)]
        self.model.members=[Member(1,1,3,'column',section_area=0.02,material='concrete'),Member(2,2,4,'column',section_area=0.02,material='concrete'),Member(3,3,4,'beam',section_area=0.025,material='steel'),Member(4,1,2,'beam',section_area=0.02,material='steel')]
        self.model.slabs=[SlabPanel(1,[1,2,4,3],6.0,4.0,0.15)]
        for m in self.model.members:
            m.label=self.labels.assign('B' if m.type=='beam' else 'C', m.id)
        for s in self.model.slabs:
            s.label=self.labels.assign('S', s.id)
    def _build_controls(self):
        t1=QtWidgets.QWidget(); v=QtWidgets.QVBoxLayout(t1)
        btn_import=QtWidgets.QPushButton('Import DXF'); btn_import.clicked.connect(self.import_dxf); v.addWidget(btn_import)
        btn_export=QtWidgets.QPushButton('Export DXF'); btn_export.clicked.connect(self.export_dxf); v.addWidget(btn_export)
        btn_design=QtWidgets.QPushButton('Design Reinforcement'); btn_design.clicked.connect(self.design_rebar); v.addWidget(btn_design)
        btn_auto=QtWidgets.QPushButton('Auto-Size Members'); btn_auto.clicked.connect(self.auto_size); v.addWidget(btn_auto)
        btn_bbs=QtWidgets.QPushButton('Export BBS'); btn_bbs.clicked.connect(self.export_bbs); v.addWidget(btn_bbs)
        chk_rebar=QtWidgets.QCheckBox('Show Rebars'); chk_rebar.setChecked(True); chk_rebar.stateChanged.connect(lambda s: self.rebar_visualizer.toggle_visibility(s==2)); v.addWidget(chk_rebar)
        btn_export_rebar=QtWidgets.QPushButton('Export Rebar DXF'); btn_export_rebar.clicked.connect(self.export_rebar_dxf); v.addWidget(btn_export_rebar)
        v.addStretch(); self.tabs.addTab(t1,'Design & Export')
    def import_dxf(self):
        fn=QtWidgets.QFileDialog.getOpenFileName(self,'Import DXF','','DXF files (*.dxf)')[0]
        if not fn: return
        try:
            summary=self.importer.import_dxf(fn, grid=self.viewport.grid_settings)
            self.viewport.update_scene(); self.status.showMessage(f'Imported DXF: {summary}',5000)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self,'DXF Import',str(e))
    def export_dxf(self):
        fn=QtWidgets.QFileDialog.getSaveFileName(self,'Export DXF','','DXF files (*.dxf)')[0]
        if not fn: return
        try:
            self.exporter.export_dxf(fn); self.status.showMessage(f'Exported DXF: {fn}',5000)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self,'DXF Export',str(e))
    def design_rebar(self):
        layouts={}; layouts.update(self.rebar_designer.design_all_slabs()); layouts.update(self.rebar_designer.design_all_beams())
        self.bbs_exporter.layouts=layouts
        self.rebar_visualizer.update_from_layouts(layouts)
        self.status.showMessage('Reinforcement designed',5000)
    def auto_size(self):
        history=self.autosizer.run_auto_size(); QtWidgets.QMessageBox.information(self,'Auto-Size',str(history)); self.viewport.update_scene()
    def export_bbs(self):
        fn=QtWidgets.QFileDialog.getSaveFileName(self,'Save BBS CSV','','CSV files (*.csv)')[0]
        if fn:
            self.bbs_exporter.export_csv(fn); self.status.showMessage(f'BBS exported: {fn}',5000)
            try:
                pdfn=fn.replace('.csv','.pdf'); self.bbs_exporter.export_pdf(pdfn)
            except Exception:
                pass
    def export_rebar_dxf(self):
        fn=QtWidgets.QFileDialog.getSaveFileName(self,'Export Rebar DXF','','DXF files (*.dxf)')[0]
        if fn:
            try: self.rebar_visualizer.export_rebars_dxf(fn); self.status.showMessage(f'Rebar DXF: {fn}',5000)
            except Exception as e: QtWidgets.QMessageBox.critical(self,'Rebar DXF',str(e))

# -------------------- Run ------------------------------------------------
def main():
    app=QtWidgets.QApplication(sys.argv)
    w=MainWindow(); w.show()
    sys.exit(app.exec())

if __name__=='__main__':
    main()
