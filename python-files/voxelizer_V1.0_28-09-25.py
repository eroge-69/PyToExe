#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced voxelizer GUI per technical specification.
- Regular grid (uniform spacing by roughness_nm) inside STL mesh in nm units.
- Shift mesh to positive octant, origin at lower min-corner.
- GUI control + visualization on one page (left panel scrollable controls, right panel with tabs).
- Coarse filling places internal voxels only if ellipsoid fully inside model (subset of internal nodes).
  Fallback: try half hatching/slicing offsets for a candidate when not fitting.
- Smoothing adds boundary voxels by normal-shift heuristic.
- Trajectory supports multiple modes per spec (zigzag/stripes/circle for internal; shell spiral for boundary; order selectable).
- Visualization optimized: draw voxel centers; for up to Nlimit voxels draw 3 circles (equator + 2 meridians).
- Status pane with log + export; statistics include percent of nodes covered by voxels.
- Layer tab with slider to display per-layer nodes and voxels.
- Multithreaded workers with cancel event; robust error logging.

Note: This is a reference implementation aimed to meet functional requirements and run on moderate meshes.
Heavy models may require tuning parameters (coarser roughness, fewer preview circles).
"""

import os
import sys
import math
import time
import queue
import json
import threading
from dataclasses import dataclass
from typing import List, Tuple, Optional

import numpy as np
from scipy.spatial import cKDTree

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Visualization
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Line3DCollection

# Geometry
import trimesh
from trimesh.proximity import closest_point
from scipy.spatial import cKDTree

# Добавляем импорт модуля re для регулярных выражений
import re


@dataclass
class Voxel:
    center: Tuple[float, float, float]  # in nm
    size_id: int                       # 1..N
    a_nm: float                        # horizontal semi-axis (radius)
    c_nm: float                        # vertical semi-axis (radius)
    is_boundary: bool                  # True for shell voxel


class VoxelizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voxelizer")
        self.geometry("1400x900")

        # State
        self.tri_mesh = None          # original units
        self.tri_mesh_nm = None       # scaled and shifted to nm and positive
        self.mesh_bounds_nm = None
        self.units_var = tk.StringVar(value='nm')
        self.scale_var = tk.DoubleVar(value=100.0)
        self.roughness_nm_var = tk.DoubleVar(value=200.0)
        self.min_width_nm_var = tk.DoubleVar(value=200.0)
        self.max_width_nm_var = tk.DoubleVar(value=500.0)
        self.min_height_nm_var = tk.DoubleVar(value=500.0)
        self.max_height_nm_var = tk.DoubleVar(value=1000.0)
        self.num_sizes_var = tk.IntVar(value=5)
        self.hatching_nm_var = tk.DoubleVar(value=300.0)
        self.slicing_nm_var = tk.DoubleVar(value=400.0)

            # GWL параметры
        self.min_laser_power_var = tk.DoubleVar(value=10.0)
        self.max_laser_power_var = tk.DoubleVar(value=40.0)
        self.scan_speed_var = tk.DoubleVar(value=100.0)

        self.fill_order_var = tk.StringVar(value='inner_then_shell')
        self.inner_pattern_var = tk.StringVar(value='zigzag')  # zigzag, stripes, circle

        self.show_stl_var = tk.BooleanVar(value=True)
        self.show_grid_var = tk.BooleanVar(value=False)
        self.show_nodes_var = tk.BooleanVar(value=False)
        self.show_internal_voxels_var = tk.BooleanVar(value=False)
        self.show_boundary_voxels_var = tk.BooleanVar(value=False)
        self.show_trajectory_var = tk.BooleanVar(value=False)

        # Добавляем переменную для отображения границ
        self.show_voxel_outlines_var = tk.BooleanVar(value=False)

        # Computed data
        self.grid_origin_nm = None
        self.grid_shape = None
        self.grid_spacing_nm = None
        self.grid_nodes_nm = None  # (N,3)
        self.is_inside_mask = None  # (N,)
        self.is_boundary_node = None  # (N,)
        self.internal_nodes_idx = None  # indices of internal nodes
        self.boundary_nodes_idx = None
        self.kdtree_nodes = None

        self.voxels: List[Voxel] = []
        self.internal_voxel_indices: List[int] = []
        self.boundary_voxel_indices: List[int] = []
        self.trajectory: List[int] = []  # indices into self.voxels

        self.filled_mask = None  # per-node filled flag

        self.cancel_event = threading.Event()
        self.worker_thread = None
        self.current_worker = None  # Track current worker function

        # UI
        self._build_ui()
        self._reset_status()

    # ----------------------- UI -----------------------
    def _build_ui(self):
        # Root: two columns: left controls (scrollable), right notebook for views
        root = ttk.Frame(self)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        # Left scrollable controls
        left_container = ttk.Frame(root)
        left_container.grid(row=0, column=0, sticky='ns')

        canvas = tk.Canvas(left_container, width=580)
        scrollbar = ttk.Scrollbar(left_container, orient='vertical', command=canvas.yview)
        self.ctrl_frame = ttk.Frame(canvas)
        self.ctrl_frame.bind(
            '<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.ctrl_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='y')
        scrollbar.pack(side='right', fill='y')

        # Right notebook
        right = ttk.Notebook(root)
        right.grid(row=0, column=1, sticky='nsew')

        # 3D View tab
        self.view_tab = ttk.Frame(right)
        right.add(self.view_tab, text='3D View')
        self._build_3d_view(self.view_tab)

        # Layers tab
        self.layers_tab = ttk.Frame(right)
        right.add(self.layers_tab, text='Layers')
        self._build_layers_view(self.layers_tab)

        # Statistics tab
        self.stats_tab = ttk.Frame(right)
        right.add(self.stats_tab, text='Statistics')
        self._build_stats_view(self.stats_tab)

        # Добавляем вкладку GWL Code в правый блок
        self.gwl_tab = ttk.Frame(right)
        right.add(self.gwl_tab, text='GWL Code')
        self._build_gwl_view(self.gwl_tab)

        # Controls content
        self._build_controls(self.ctrl_frame)

    def _build_stats_view(self, parent):
        # Create text widget for statistics
        self.stats_text = tk.Text(parent, height=20, width=80)
        self.stats_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.stats_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.stats_text.configure(yscrollcommand=scrollbar.set)

    def update_stats(self):
        """Update statistics display"""
        if not self.stats_text:
            return

        self.stats_text.delete(1.0, tk.END)

        stats = "Voxelization Statistics\n"
        stats += "=====================\n\n"

        if self.mesh_bounds_nm is not None:
            stats += f"Model Bounds (nm):\n"
            stats += f"  Min: {self.mesh_bounds_nm[0]}\n"
            stats += f"  Max: {self.mesh_bounds_nm[1]}\n\n"

        if self.grid_shape is not None:
            stats += f"Grid Shape: {self.grid_shape}\n"
            stats += f"Grid Spacing: {self.grid_spacing_nm} nm\n\n"

        if self.is_inside_mask is not None:
            total_nodes = int(self.is_inside_mask.sum())
            stats += f"Total Inside Nodes: {total_nodes}\n"

        if self.is_boundary_node is not None:
            boundary_nodes = int(self.is_boundary_node.sum())
            stats += f"Boundary Nodes: {boundary_nodes}\n"

        if self.internal_nodes_idx is not None:
            internal_nodes = len(self.internal_nodes_idx)
            stats += f"Internal Nodes: {internal_nodes}\n\n"

        stats += f"Total Voxels: {len(self.voxels)}\n"
        stats += f"Internal Voxels: {len(self.internal_voxel_indices)}\n"
        stats += f"Boundary Voxels: {len(self.boundary_voxel_indices)}\n\n"

        if self.trajectory:
            trajectory_length = self._trajectory_length(self.trajectory)
            stats += f"Trajectory Length: {trajectory_length:.2f} nm\n"
            stats += f"Trajectory Points: {len(self.trajectory)}\n\n"

        if self.is_inside_mask is not None and self.filled_mask is not None:
            total_inside = int(self.is_inside_mask.sum())
            filled = int(self.filled_mask.sum())
            coverage = (filled / total_inside * 100.0) if total_inside > 0 else 0
            stats += f"Coverage: {filled}/{total_inside} ({coverage:.2f}%)\n"

        self.stats_text.insert(tk.END, stats)

    def _build_controls(self, f):
        r = 0
        # File
        ttk.Label(f, text='File').grid(row=r, column=0, sticky='w'); r+=1
        file_frame = ttk.Frame(f); file_frame.grid(row=r, column=0, sticky='we'); r+=1
        ttk.Button(file_frame, text='Load STL', command=self._on_load_stl).pack(side='left', expand=True, fill='x')
        ttk.Button(file_frame, text='Update Model', command=self._update_model).pack(side='left', expand=True, fill='x')

        # Units & scale
        ttk.Label(f, text='Units').grid(row=r, column=0, sticky='w'); r+=1
        u = ttk.Frame(f); u.grid(row=r, column=0, sticky='we'); r+=1
        ttk.Label(u, text='Units:').pack(side='left')
        ttk.OptionMenu(u, self.units_var, self.units_var.get(), 'mm', 'um', 'nm').pack(side='left')
        ttk.Label(u, text='Scale:').pack(side='left')
        ttk.Entry(u, textvariable=self.scale_var, width=8).pack(side='left')

        # Grid params
        ttk.Label(f, text='Grid / Roughness (nm)').grid(row=r, column=0, sticky='w'); r+=1
        g = ttk.Frame(f); g.grid(row=r, column=0, sticky='we'); r+=1
        ttk.Label(g, text='Roughness nm:').pack(side='left')
        ttk.Entry(g, textvariable=self.roughness_nm_var, width=8).pack(side='left')

        # Voxel params
        ttk.Label(f, text='Voxel sizes (nm)').grid(row=r, column=0, sticky='w'); r+=1
        v = ttk.Frame(f); v.grid(row=r, column=0, sticky='we'); r+=1
        ttk.Label(v, text='min width:').pack(side='left')
        ttk.Entry(v, textvariable=self.min_width_nm_var, width=8).pack(side='left')
        ttk.Label(v, text='max width:').pack(side='left')
        ttk.Entry(v, textvariable=self.max_width_nm_var, width=8).pack(side='left')
        ttk.Label(v, text='min height:').pack(side='left')
        ttk.Entry(v, textvariable=self.min_height_nm_var, width=8).pack(side='left')
        ttk.Label(v, text='max height:').pack(side='left')
        ttk.Entry(v, textvariable=self.max_height_nm_var, width=8).pack(side='left')
        ttk.Label(v, text='types:').pack(side='left')
        ttk.Entry(v, textvariable=self.num_sizes_var, width=6).pack(side='left')

        # Spacings
        ttk.Label(f, text='Distances (nm)').grid(row=r, column=0, sticky='w'); r+=1
        d = ttk.Frame(f); d.grid(row=r, column=0, sticky='we'); r+=1
        ttk.Label(d, text='hatching:').pack(side='left')
        ttk.Entry(d, textvariable=self.hatching_nm_var, width=8).pack(side='left')
        ttk.Label(d, text='slicing:').pack(side='left')
        ttk.Entry(d, textvariable=self.slicing_nm_var, width=8).pack(side='left')

        # Trajectory options
        ttk.Label(f, text='Trajectory').grid(row=r, column=0, sticky='w'); r+=1
        t = ttk.Frame(f); t.grid(row=r, column=0, sticky='we'); r+=1
        ttk.OptionMenu(t, self.fill_order_var, self.fill_order_var.get(), 'inner_then_shell', 'shell_then_inner').pack(side='left')
        ttk.OptionMenu(t, self.inner_pattern_var, self.inner_pattern_var.get(), 'zigzag', 'stripes', 'circle').pack(side='left')

        # Run buttons
        ttk.Label(f, text='Run').grid(row=r, column=0, sticky='w'); r+=1
        rb = ttk.Frame(f); rb.grid(row=r, column=0, sticky='we'); r+=1
        ttk.Button(rb, text='Calc grid', command=self._run_calc_grid).pack(side='left', expand=True, fill='x')
        ttk.Button(rb, text='Coarse fill', command=self._run_coarse_fill).pack(side='left', expand=True, fill='x')
        ttk.Button(rb, text='Smoothing', command=self._run_smoothing).pack(side='left', expand=True, fill='x')
        ttk.Button(rb, text='Trajectory', command=self._run_trajectory).pack(side='left', expand=True, fill='x')
        ttk.Button(rb, text='Cancel', command=self._cancel).pack(side='left', expand=True, fill='x')

        # Show checkboxes
        ttk.Label(f, text='Show').grid(row=r, column=0, sticky='w'); r+=1
        sc = ttk.Frame(f); sc.grid(row=r, column=0, sticky='we'); r+=1
        ttk.Checkbutton(sc, text='STL', variable=self.show_stl_var, command=self._update_view).pack(anchor='w')
        ttk.Checkbutton(sc, text='Grid', variable=self.show_grid_var, command=self._update_view).pack(anchor='w')
        ttk.Checkbutton(sc, text='Nodes', variable=self.show_nodes_var, command=self._update_view).pack(anchor='w')
        ttk.Checkbutton(sc, text='Internal voxels', variable=self.show_internal_voxels_var, command=self._update_view).pack(anchor='w')
        ttk.Checkbutton(sc, text='Boundary voxels', variable=self.show_boundary_voxels_var, command=self._update_view).pack(anchor='w')
        ttk.Checkbutton(sc, text='Trajectory', variable=self.show_trajectory_var, command=self._update_view).pack(anchor='w')
        # Добавляем чекбокс в UI
        ttk.Checkbutton(sc, text='Voxel outlines',
                        variable=self.show_voxel_outlines_var,
                        command=self._update_view).pack(anchor='w')

        # Export & Status
        ttk.Label(f, text='Export').grid(row=r, column=0, sticky='w'); r+=1
        eb = ttk.Frame(f); eb.grid(row=r, column=0, sticky='we'); r+=1
        ttk.Button(eb, text='Export coords', command=self._export_coords).pack(side='left', expand=True, fill='x')
        ttk.Button(eb, text='Export stats/log', command=self._export_stats).pack(side='left', expand=True, fill='x')

        ttk.Label(f, text='Status').grid(row=r, column=0, sticky='w'); r+=1
        self.status_text = tk.Text(f, width=45, height=18)
        self.status_text.grid(row=r, column=0, sticky='we'); r+=1
        self.progress = ttk.Progressbar(f, mode='determinate', maximum=100)
        self.progress.grid(row=r, column=0, sticky='we'); r+=1

        for i in range(r):
            f.grid_rowconfigure(i, pad=2)

    def _build_3d_view(self, parent):
        fig = Figure(figsize=(7, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel('x (nm)')
        ax.set_ylabel('y (nm)')
        ax.set_zlabel('z (nm)')
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.fig3d = fig
        self.ax3d = ax
        self.canvas3d = canvas

        # Добавляем кнопки для управления видом
        view_buttons = ttk.Frame(parent)
        view_buttons.pack(fill=tk.X, pady=5)

        ttk.Button(view_buttons, text="Вид спереди",
                   command=lambda: self._set_view(0, 0)).pack(side=tk.LEFT, padx=5)
        ttk.Button(view_buttons, text="Вид сверху",
                   command=lambda: self._set_view(90, 0)).pack(side=tk.LEFT, padx=5)
        ttk.Button(view_buttons, text="Вид сбоку",
                   command=lambda: self._set_view(0, 90)).pack(side=tk.LEFT, padx=5)
        ttk.Button(view_buttons, text="Вид изометрический",
                   command=lambda: self._set_view(30, 45)).pack(side=tk.LEFT, padx=5)

    def _set_view(self, elev, azim):
        self.ax3d.view_init(elev=elev, azim=azim)
        self.canvas3d.draw()

    def _build_layers_view(self, parent):
        top = ttk.Frame(parent)
        top.pack(fill=tk.BOTH, expand=True)
        fig = Figure(figsize=(7, 6))
        ax = fig.add_subplot(111)
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel('x (nm)')
        ax.set_ylabel('y (nm)')
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        bottom = ttk.Frame(parent)
        bottom.pack(fill=tk.X)
        ttk.Label(bottom, text='Layer Z (index)').pack(side='left')
        self.layer_slider = ttk.Scale(bottom, from_=0, to=0, orient='horizontal', command=self._on_layer_change)
        self.layer_slider.pack(side='left', fill='x', expand=True, padx=5)
        self.layer_label = ttk.Label(bottom, text='0')
        self.layer_label.pack(side='left')

        self.fig_layer = fig
        self.ax_layer = ax
        self.canvas_layer = canvas

    # В классе VoxelizerApp добавляем метод для подсветки синтаксиса
    def highlight_gwl_syntax(self):
        """Подсветка синтаксиса GWL кода с использованием re.finditer"""
        if not hasattr(self, 'gwl_text') or not self.gwl_text:
            return

        try:
            # Очищаем предыдущие теги
            for tag in ["command", "comment", "number", "string"]:
                self.gwl_text.tag_remove(tag, "1.0", "end")

            # Получаем весь текст
            text = self.gwl_text.get("1.0", "end-1c")
            if not text.strip():
                return

            # Определяем шаблоны для подсветки
            patterns = [
                # Комментарии (серый) - должны быть первыми
                (r'%.*$', "comment"),

                # Строки в кавычках (темно-красный)
                (r'\"[^\"]*\"', "string"),

                # Команды GWL (синий)
                (r'(PiezoScanMode|ContinuousMode|ConnectPointsOn|PerfectShapeIntermediate|'
                 r'InvertZAxis|PowerScaling|LaserPower|ScanSpeed|PointDistance|UpdateRate|'
                 r'Write|GotoX|GotoY|GotoZ|MessageOut|PerfectShapeOff|PerfectShapeQuality|'
                 r'PerfectShapeFast|psLoadPowerProfiles|psPowerProfile|psPowerSlope|'
                 r'include|repeat|var|local|set|if|elif|else|end|for|while|continue|break|'
                 r'Add|Mult|WriteText|TextPositionX|TextPositionY|TextPositionZ|'
                 r'LineSpacingX|LineSpacingY|LineSpacingZ|TextLaserPower|TextPointDistance|'
                 r'TextScanSpeed|TextFontSize|DefocusFactor|MeasureTilt|TiltCorrectionOn|'
                 r'TiltCorrectionOff|ManualTiltX|ManualTiltY|AccelerationTime|'
                 r'DecelerationTime|Acceleration|Deceleration|FindInterfaceAt|InterfaceMax|'
                 r'InterfaceMin|ResetInterface|InterfacePosition|SamplePosition|'
                 r'ChooseObjective|CapturePhoto|TimeStampOn|TimeStampOff|DebugModeOn|'
                 r'DebugModeOff|ShowParameter|ShowVar|SaveMessages|Pause|ZDrivePosition|'
                 r'NewStructure|ManualControl|ReloadIni|Recalibrate)', "command"),

                # Числа (зеленый)
                (r'\b\d+\.?\d*\b', "number"),
            ]

            # Применяем подсветку для каждого паттерна
            for pattern, tag_name in patterns:
                start_index = "1.0"
                while True:
                    # Ищем совпадение
                    match_start = self.gwl_text.search(pattern, start_index, stopindex="end", regexp=True, nocase=1)
                    if not match_start:
                        break

                    # Вычисляем конец совпадения
                    match_end = self.gwl_text.index(f"{match_start} + {len(self.gwl_text.get(match_start, match_start + ' lineend'))}c")

                    # Применяем тег
                    self.gwl_text.tag_add(tag_name, match_start, match_end)

                    # Переходим к следующему поиску
                    start_index = match_end

            # Настраиваем цвета тегов
            self.gwl_text.tag_config("command", foreground="blue", font=('Courier', 10, 'bold'))
            self.gwl_text.tag_config("comment", foreground="gray", font=('Courier', 10))
            self.gwl_text.tag_config("number", foreground="green", font=('Courier', 10))
            self.gwl_text.tag_config("string", foreground="darkred", font=('Courier', 10))

        except Exception as e:
            print(f"Error in syntax highlighting: {e}")

    def _generate_gwl_code(self):
        """Генерирует GWL код из траектории вокселей"""
        if not self.trajectory:
            messagebox.showinfo('Info', 'No trajectory computed yet')
            return

        try:
            gwl_code = self._create_gwl_script()
            self.gwl_text.delete(1.0, tk.END)
            self.gwl_text.insert(1.0, gwl_code)

            # Даем время на обновление виджета перед подсветкой
            self.after(100, self.highlight_gwl_syntax)

            self._log("GWL code generated successfully")
        except Exception as e:
            messagebox.showerror('Error', f'Failed to generate GWL code: {e}')
            self._log(f"Error generating GWL code: {e}")



    def _build_gwl_view(self, parent):
        """Создает интерфейс для работы с GWL кодом"""
        # Верхняя панель с параметрами GWL
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        # Параметры мощности лазера
        ttk.Label(top_frame, text='Min Laser Power (%):').grid(row=0, column=0, sticky='w')
        self.min_laser_power_var = tk.DoubleVar(value=10.0)
        ttk.Entry(top_frame, textvariable=self.min_laser_power_var, width=8).grid(row=0, column=1, padx=5)

        ttk.Label(top_frame, text='Max Laser Power (%):').grid(row=0, column=2, sticky='w', padx=(10,0))
        self.max_laser_power_var = tk.DoubleVar(value=60.0)
        ttk.Entry(top_frame, textvariable=self.max_laser_power_var, width=8).grid(row=0, column=3, padx=5)

        ttk.Label(top_frame, text='Scan Speed (µm/s):').grid(row=0, column=4, sticky='w', padx=(10,0))
        self.scan_speed_var = tk.DoubleVar(value=100.0)
        ttk.Entry(top_frame, textvariable=self.scan_speed_var, width=8).grid(row=0, column=5, padx=5)

        # Кнопки управления
        button_frame = ttk.Frame(top_frame)
        button_frame.grid(row=0, column=6, sticky='e', padx=(20,0))

        ttk.Button(button_frame, text='Generate GWL',
                   command=self._generate_gwl_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Load GWL',
                   command=self._load_gwl_file).pack(side=tk.LEFT, padx=5)  # Новая кнопка
        ttk.Button(button_frame, text='Export GWL',
                   command=self._export_gwl_file).pack(side=tk.LEFT, padx=5)

        # Основное текстовое поле для GWL кода
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Добавляем вертикальный скроллбар
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.gwl_text = tk.Text(text_frame, yscrollcommand=scrollbar.set,
                               wrap=tk.WORD, font=('Courier', 10))
        self.gwl_text.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.gwl_text.yview)

        # Добавляем контекстное меню для текстового поля
        self._create_gwl_context_menu()

    def _create_gwl_context_menu(self):
        """Создает контекстное меню для текстового поля GWL"""
        context_menu = tk.Menu(self.gwl_text, tearoff=0)
        context_menu.add_command(label="Копировать", command=self._copy_gwl_text)
        context_menu.add_command(label="Вставить", command=self._paste_gwl_text)
        context_menu.add_command(label="Выделить все", command=self._select_all_gwl_text)
        context_menu.add_separator()
        context_menu.add_command(label="Обновить подсветку", command=self.highlight_gwl_syntax)

        # Привязываем контекстное меню к правой кнопке мыши
        self.gwl_text.bind("<Button-3>", lambda event: context_menu.tk_popup(event.x_root, event.y_root))

    def _copy_gwl_text(self):
        """Копирует выделенный текст из GWL редактора"""
        try:
            selected_text = self.gwl_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            # Если ничего не выделено
            pass

    def _paste_gwl_text(self):
        """Вставляет текст в GWL редактор"""
        try:
            clipboard_text = self.clipboard_get()
            self.gwl_text.insert(tk.INSERT, clipboard_text)
            # Обновляем подсветку после вставки
            self.highlight_gwl_syntax()
        except tk.TclError:
            pass

    def _select_all_gwl_text(self):
        """Выделяет весь текст в GWL редакторе"""
        self.gwl_text.tag_add(tk.SEL, "1.0", tk.END)
        self.gwl_text.mark_set(tk.INSERT, "1.0")
        self.gwl_text.see(tk.INSERT)


#------------------------------------------------------------------------------
    def _generate_gwl_code(self):
        """Генерирует GWL код из траектории вокселей"""
        if not self.trajectory:
            messagebox.showinfo('Info', 'No trajectory computed yet')
            return

        try:
            gwl_code = self._create_gwl_script()
            self.gwl_text.delete(1.0, tk.END)
            self.gwl_text.insert(1.0, gwl_code)

            # Применяем подсветку синтаксиса
            self.highlight_gwl_syntax()

            self._log("GWL code generated successfully")
        except Exception as e:
            messagebox.showerror('Error', f'Failed to generate GWL code: {e}')
            self._log(f"Error generating GWL code: {e}")

    def _load_gwl_file(self):
        """Загружает GWL код из файла с подсветкой синтаксиса"""
        path = filedialog.askopenfilename(
            defaultextension='.gwl',
            filetypes=[('Text files', '*.txt'), ('All files', '*.*')]
        )

        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                gwl_code = f.read()

            self.gwl_text.delete(1.0, tk.END)
            self.gwl_text.insert(1.0, gwl_code)

            # Применяем подсветку синтаксиса
            self.highlight_gwl_syntax()

            self._log(f"GWL code loaded from: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load GWL file: {e}')
            self._log(f"Error loading GWL file: {e}")


    def _create_gwl_script(self):
        """Создает GWL скрипт согласно спецификации Nanoscribe"""
        # Стандартный заголовок для PiezoScanMode
        header = """% GWL script generated by Voxelizer
% Mode: PiezoScanMode with PerfectShape

PiezoScanMode
ContinuousMode
ConnectPointsOn
PerfectShapeIntermediate

% System Initialization
InvertZAxis 0
PowerScaling 1.0

% Printing parameters
ScanSpeed {scan_speed}
PointDistance 100
UpdateRate 1000

% Start position
GotoX 0
GotoY 0
GotoZ 0

% Begin writing
"""

        # Получаем параметры
        min_power = float(self.min_laser_power_var.get())
        max_power = float(self.max_laser_power_var.get())
        scan_speed = float(self.scan_speed_var.get())

        # Определяем диапазон размеров вокселей для нормализации мощности
        voxel_sizes = self._voxel_sizes()
        if not voxel_sizes:
            raise ValueError("No voxel sizes defined")

        min_size = min(a for a, c in voxel_sizes)
        max_size = max(a for a, c in voxel_sizes)
        size_range = max_size - min_size

        # Создаем карту размера вокселя -> мощность лазера
        size_to_power = {}
        for i, (a, c) in enumerate(voxel_sizes):
            if size_range > 0:
                # Линейная интерполяция между min_power и max_power
                power = min_power + (a - min_size) / size_range * (max_power - min_power)
            else:
                power = (min_power + max_power) / 2

            size_to_power[i+1] = max(min_power, min(max_power, power))

        # Генерируем команды перемещения
        commands = []

        if self.trajectory:
            # Начальная позиция - первая точка траектории
            first_voxel = self.voxels[self.trajectory[0]]
            x, y, z = first_voxel.center
            commands.append(f"% Start at first voxel")
            commands.append(f"{x/1000:.3f} {y/1000:.3f} {z/1000:.3f} 0")
            commands.append("write")

            # Основная траектория
            commands.append(f"% Main trajectory - {len(self.trajectory)} voxels")

            prev_voxel = first_voxel
            for i, voxel_idx in enumerate(self.trajectory):
                voxel = self.voxels[voxel_idx]
                x, y, z = voxel.center

                # Определяем мощность для текущего вокселя
                laser_power = size_to_power.get(voxel.size_id, min_power)

                # Проверяем, является ли перемещение холостым
                is_idle = self._is_idle_move(prev_voxel, voxel)

                if is_idle:
                    # Холостое перемещение - минимальная мощность
                    commands.append(f"% Idle move to voxel {i+1}")
                    commands.append(f"{x/1000:.3f} {y/1000:.3f} {z/1000:.3f} {min_power:.1f}")
                else:
                    # Рабочее перемещение - мощность согласно размеру вокселя
                    commands.append(f"% Voxel {i+1} (size_id: {voxel.size_id})")
                    commands.append(f"{x/1000:.3f} {y/1000:.3f} {z/1000:.3f} {laser_power:.1f}")

                prev_voxel = voxel

            commands.append("write")

        # Футер
        footer = """
% End of writing
% Return to origin
GotoX 0
GotoY 0
GotoZ 0

% System shutdown
MessageOut "Printing completed"
"""

        # Собираем полный скрипт
        full_script = header.format(scan_speed=scan_speed) + "\n".join(commands) + footer
        return full_script

    def _is_idle_move(self, prev_voxel, current_voxel):
        """Определяет, является ли перемещение холостым"""
        if self.mesh_bounds_nm is None:
            return False

        # Координаты в нанометрах
        x1, y1, z1 = prev_voxel.center
        x2, y2, z2 = current_voxel.center

        # Расстояние между точками
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

        # Размеры модели для определения порога
        model_size_x = self.mesh_bounds_nm[1][0] - self.mesh_bounds_nm[0][0]
        model_size_y = self.mesh_bounds_nm[1][1] - self.mesh_bounds_nm[0][1]

        # Порог для холостого хода - половина меньшего размера модели
        idle_threshold = min(model_size_x, model_size_y) / 2

        # Перемещение между слоями считается холостым
        layer_thickness = float(self.slicing_nm_var.get())
        is_layer_change = abs(z2 - z1) > layer_thickness * 1.5

        # Перемещение за пределами модели считается холостым
        # Явно создаем точку как массив из 3 элементов
        point = np.array([x2, y2, z2])
        is_outside_model = not self._is_point_near_model(point)

        return distance > idle_threshold or is_layer_change or is_outside_model


    def _is_point_near_model(self, point, tolerance_ratio=0.1):
        """Проверяет, находится ли точка близко к модели"""
        if self.mesh_bounds_nm is None:
            return False

        try:
            # Преобразуем точку в numpy array и убедимся, что это 1D массив
            point = np.array(point).flatten()

            # Если передано несколько точек, берем только первую
            if point.size > 3:
                point = point[:3]

            # Проверяем, что точка имеет правильную размерность
            if point.size != 3:
                return False

            # Определяем допуск на основе размера модели
            model_size = max(
                self.mesh_bounds_nm[1][0] - self.mesh_bounds_nm[0][0],
                self.mesh_bounds_nm[1][1] - self.mesh_bounds_nm[0][1]
            )
            tolerance = model_size * tolerance_ratio

            # Проверяем, находится ли точка в пределах bounding box с допуском
            min_bound = self.mesh_bounds_nm[0] - tolerance
            max_bound = self.mesh_bounds_nm[1] + tolerance

            # Проверяем каждую координату отдельно
            condition_x = (min_bound[0] <= point[0]) and (point[0] <= max_bound[0])
            condition_y = (min_bound[1] <= point[1]) and (point[1] <= max_bound[1])
            condition_z = (min_bound[2] <= point[2]) and (point[2] <= max_bound[2])

            # Объединяем условия
            return condition_x and condition_y and condition_z

        except Exception as e:
            # Логируем ошибку для отладки
            print(f"Error in _is_point_near_model: {e}")
            print(f"Point: {point}, type: {type(point)}")
            return False

    def _export_gwl_file(self):
        """Экспортирует GWL код в файл"""
        gwl_code = self.gwl_text.get(1.0, tk.END).strip()
        if not gwl_code:
            messagebox.showinfo('Info', 'No GWL code to export')
            return

        path = filedialog.asksaveasfilename(
            defaultextension='.gwl',
            filetypes=[('GWL files', '*.txt'), ('All files', '*.*')]
        )

        if not path:
            return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(gwl_code)
            self._log(f"GWL code exported to: {os.path.basename(path)}")
            messagebox.showinfo('Success', f'GWL code exported successfully to:\n{path}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to export GWL code: {e}')
            self._log(f"Error exporting GWL code: {e}")

    # --------------------- Status/log ---------------------
    def _reset_status(self):
        self._log_lines = []
        self._log('Ready.')

    def _log(self, msg):
        ts = time.strftime('%H:%M:%S')
        line = f"[{ts}] {msg}"
        self._log_lines.append(line)
        self.status_text.insert('end', line + '\n')
        self.status_text.see('end')
        self.update_idletasks()

    def _set_progress(self, val):
        self.progress['value'] = max(0, min(100, val))
        self.update_idletasks()

    # --------------------- File I/O ---------------------
    def _on_load_stl(self):
        path = filedialog.askopenfilename(filetypes=[('STL files','*.stl'), ('All files','*.*')])
        if not path:
            return
        try:
            self._load_stl(path)
            self._log(f"Loaded STL: {os.path.basename(path)}")
            self._update_view()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load STL: {e}')
            self._log(f"Error loading STL: {e}")

    def _update_model(self):
        """Update model with new scale and units"""
        if self.tri_mesh is None:
            messagebox.showinfo('Info', 'No STL model loaded.')
            return

        try:
            # Reapply scaling and units to the original mesh
            mesh = self.tri_mesh.copy()

            # Shift to positive octant: move min bounds to origin
            min_corner = mesh.bounds[0].copy()
            mesh.apply_translation(-min_corner)

            # Scale to nm
            factor = self._units_to_nm(self.units_var.get()) * float(self.scale_var.get())
            mesh.apply_scale(factor)

            self.tri_mesh_nm = mesh
            self.mesh_bounds_nm = mesh.bounds.copy()

            self._log(f"Model updated with new scale/units")
            self._log(f"STL in nm: verts={len(mesh.vertices)}, faces={len(mesh.faces)}, bbox(min)={self.mesh_bounds_nm[0]}, (max)={self.mesh_bounds_nm[1]}")

            # Reset computed data
            self.grid_origin_nm = None
            self.grid_shape = None
            self.grid_spacing_nm = None
            self.grid_nodes_nm = None
            self.is_inside_mask = None
            self.is_boundary_node = None
            self.internal_nodes_idx = None
            self.boundary_nodes_idx = None
            self.kdtree_nodes = None
            self.voxels.clear()
            self.internal_voxel_indices.clear()
            self.boundary_voxel_indices.clear()
            self.trajectory.clear()
            self.filled_mask = None
            self._set_progress(0)

            self._update_view()

        except Exception as e:
            messagebox.showerror('Error', f'Failed to update model: {e}')
            self._log(f"Error updating model: {e}")

    def _units_to_nm(self, units):
        return {'mm': 1e6, 'um': 1e3, 'nm': 1.0}.get(units, 1.0)

    def _load_stl(self, path):
        mesh = trimesh.load(path, force='mesh')
        if mesh.is_empty:
            raise ValueError('STL mesh is empty')

        # Store original mesh
        self.tri_mesh = mesh.copy()

        # Shift to positive octant: move min bounds to origin
        min_corner = mesh.bounds[0].copy()
        mesh.apply_translation(-min_corner)

        # Scale to nm
        factor = self._units_to_nm(self.units_var.get()) * float(self.scale_var.get())
        mesh.apply_scale(factor)

        self.tri_mesh_nm = mesh
        self.mesh_bounds_nm = mesh.bounds.copy()

        self._log(f"STL in nm: verts={len(mesh.vertices)}, faces={len(mesh.faces)}, bbox(min)={self.mesh_bounds_nm[0]}, (max)={self.mesh_bounds_nm[1]}")

        # Reset computed data
        self.grid_origin_nm = None
        self.grid_shape = None
        self.grid_spacing_nm = None
        self.grid_nodes_nm = None
        self.is_inside_mask = None
        self.is_boundary_node = None
        self.internal_nodes_idx = None
        self.boundary_nodes_idx = None
        self.kdtree_nodes = None
        self.voxels.clear()
        self.internal_voxel_indices.clear()
        self.boundary_voxel_indices.clear()
        self.trajectory.clear()
        self.filled_mask = None
        self._set_progress(0)

    # --------------------- Workers ---------------------
    def _cancel(self):
        self.cancel_event.set()
        if self.current_worker:
            self._log(f'Cancelling {self.current_worker}...')
        else:
            self._log('Cancel requested...')

    def _run_worker(self, target, title):
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo('Busy', 'A task is already running.')
            return
        self.cancel_event.clear()
        self.current_worker = title
        self._set_progress(0)
        self._log(f"Started: {title}")
        t = threading.Thread(target=self._worker_wrapper, args=(target, title), daemon=True)
        self.worker_thread = t
        t.start()

    def _worker_wrapper(self, target, title):
        try:
            target()
            self._log(f"Finished: {title}")
        except Exception as e:
            self._log(f"Error in {title}: {e}")
            messagebox.showerror('Error', f'{title} failed: {e}')
        finally:
            self.current_worker = None
            self.after(0, lambda: self._set_progress(0))
            self._update_view()

    def _run_calc_grid(self):
        self._run_worker(self._calculate_grid_worker, 'Calc grid')

    def _run_coarse_fill(self):
        self._run_worker(self._coarse_fill_worker, 'Coarse fill')

    def _run_smoothing(self):
        self._run_worker(self._smoothing_worker, 'Smoothing')

    def _run_trajectory(self):
        self._run_worker(self._trajectory_worker, 'Trajectory')

    def _calculate_grid_worker(self):
        if self.tri_mesh_nm is None:
            raise RuntimeError('Load STL first')
        t0 = time.time()
        rough = float(self.roughness_nm_var.get())
        if rough <= 0:
            raise ValueError('Roughness must be > 0')

        # Сбрасываем все параметры сетки перед расчетом
        self.grid_origin_nm = None
        self.grid_shape = None
        self.grid_spacing_nm = None
        self.grid_nodes_nm = None
        self.is_inside_mask = None
        self.is_boundary_node = None
        self.internal_nodes_idx = None
        self.boundary_nodes_idx = None
        self.kdtree_nodes = None
        self.filled_mask = None

        bounds = self.tri_mesh_nm.bounds
        minb, maxb = bounds[0], bounds[1]

        # Расширяем bounding box на roughness во всех направлениях
        # чтобы включить узлы вне модели, но близкие к границе
        minb_expanded = minb - rough
        maxb_expanded = maxb + rough

        # Обновляем прогресс - создание сетки
        self.after(0, lambda: self._set_progress(10))
        if self.cancel_event.is_set():
            self._log('Grid calculation cancelled')
            return

        # Создаем регулярную сетку точек с шагом rough в расширенном bounding box
        x = np.arange(minb_expanded[0], maxb_expanded[0] + rough, rough)
        y = np.arange(minb_expanded[1], maxb_expanded[1] + rough, rough)
        z = np.arange(minb_expanded[2], maxb_expanded[2] + rough, rough)

        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        grid_points = np.vstack((X.ravel(), Y.ravel(), Z.ravel())).T

        # Обновляем прогресс - проверка содержания точек
        self.after(0, lambda: self._set_progress(30))
        if self.cancel_event.is_set():
            self._log('Grid calculation cancelled')
            return

        # Определяем, какие точки находятся внутри модели
        inside = self.tri_mesh_nm.contains(grid_points)

        # Вычисляем расстояния до поверхности для всех точек
        try:
            # Более точный метод для определения расстояния до поверхности
            closest_points, distances, triangle_ids = self.tri_mesh_nm.nearest.on_surface(grid_points)

            # Точки на границе или близкие к границе (в пределах roughness)
            boundary_or_near = distances <= 0.5 * rough

            # Включаем точки:
            # 1. Внутри модели
            # 2. На границе или близкие к границе (вне модели, но в пределах roughness)
            include_mask = inside | boundary_or_near

        except Exception as e:
            self._log(f"Using fallback distance calculation: {e}")
            # Fallback: используем signed_distance
            distance = self.tri_mesh_nm.nearest.signed_distance(grid_points)
            boundary_or_near = np.abs(distance) <= 0.5 * rough
            include_mask = inside | boundary_or_near

        # Фильтруем точки - оставляем только те, которые нужно включить в сетку
        included_points = grid_points[include_mask]
        included_inside = inside[include_mask]
        included_distances = distances[include_mask] if 'distances' in locals() else np.abs(distance[include_mask])

        # Обновляем прогресс - определение граничных точек
        self.after(0, lambda: self._set_progress(60))
        if self.cancel_event.is_set():
            self._log('Grid calculation cancelled')
            return

        # Определяем граничные точки среди включенных точек
        try:
            # Точка считается граничной, если она близка к поверхности
            boundary_mask = included_distances <= 0.5 * rough

            # ИСКЛЮЧЕНИЕ: точки около z=0 не считаем граничными, только если они на НИЖНЕЙ границе
            z_near_zero = included_points[:, 2] < 0.5 * rough

            # Создаем KDTree для быстрого поиска соседей
            kdtree_all = cKDTree(included_points)

            # Для точек около z=0 проверяем наличие соседних граничных узлов сверху
            for i in range(len(included_points)):
                if z_near_zero[i] and boundary_mask[i]:
                    point = included_points[i]

                    # Ищем соседние точки в радиусе 1.5*rough
                    neighbors_indices = kdtree_all.query_ball_point(point, 1.5 * rough)

                    has_boundary_neighbors_above = False

                    for neighbor_idx in neighbors_indices:
                        if neighbor_idx == i:  # Пропускаем саму точку
                            continue

                        neighbor_point = included_points[neighbor_idx]
                        neighbor_z = neighbor_point[2]

                        # Проверяем, что соседняя точка выше и является граничной
                        if (neighbor_z > point[2] + 0.1 * rough and  # немного выше
                            boundary_mask[neighbor_idx] and  # граничная
                            included_distances[neighbor_idx] <= 0.5 * rough):  # близка к поверхности

                            has_boundary_neighbors_above = True
                            break

                    # Если нет граничных соседей сверху - исключаем узел из граничных
                    if not has_boundary_neighbors_above:
                        boundary_mask[i] = False

            # Дополнительная проверка для точек внутри модели:
            # Если точка внутри модели, но близка к поверхности, она граничная
            # Если точка вне модели, но близка к поверхности, она также граничная
            for i in range(len(included_points)):
                if included_inside[i] and boundary_mask[i]:
                    # Точка внутри модели и близка к поверхности - граничная
                    pass
                elif not included_inside[i] and boundary_mask[i]:
                    # Точка вне модели, но близка к поверхности - граничная
                    pass
                else:
                    # Сбрасываем флаг граничной точки
                    boundary_mask[i] = False

        except Exception as e:
            self._log(f"Error in boundary detection: {e}")
            # Fallback: все точки, близкие к поверхности, считаем граничными
            boundary_mask = included_distances <= 0.5 * rough
            z_near_zero = included_points[:, 2] < 0.5 * rough
            boundary_mask[z_near_zero] = False


        # Сохраняем параметры сетки для вкладки Layers
        self.grid_origin_nm = minb_expanded.copy()
        self.grid_spacing_nm = np.array([rough, rough, rough])
        self.grid_shape = (len(x), len(y), len(z))

        # Сохраняем узлы и граничную маску
        self.grid_nodes_nm = included_points
        self.is_inside_mask = included_inside  # Маска для точек внутри модели
        self.is_boundary_node = boundary_mask  # Маска для граничных точек

        # Внутренние узлы - внутри модели и не граничные
        internal_mask = included_inside & ~boundary_mask
        self.internal_nodes_idx = np.where(internal_mask)[0]
        self.boundary_nodes_idx = np.where(boundary_mask)[0]

        # KDTree для быстрого поиска
        self.kdtree_nodes = cKDTree(included_points)

        # Initialize fill mask
        self.filled_mask = np.zeros(len(included_points), dtype=bool)

        # Обновляем прогресс - завершение
        self.after(0, lambda: self._set_progress(100))

        t1 = time.time()

        # Статистика
        total_points = len(included_points)
        inside_points = np.sum(included_inside)
        boundary_points = np.sum(boundary_mask)
        internal_points = np.sum(internal_mask)
        outside_near_points = total_points - inside_points  # Точки вне модели, но близкие к границе

        self._log(f"Grid statistics:")
        self._log(f"  Total nodes: {total_points}")
        self._log(f"  Inside model: {inside_points}")
        self._log(f"  Outside but near surface: {outside_near_points}")
        self._log(f"  Boundary nodes: {boundary_points}")
        self._log(f"  Internal nodes: {internal_points}")
        self._log(f"Grid calc time: {t1-t0:.2f}s")

        # Update statistics
        self.update_stats()

        # Update layer slider
        self._update_layer_slider()

    # Обновляем функцию _can_place_internal_voxel для учета нижней границы
    """
    def _can_place_internal_voxel(self, center, a, c) -> bool:
        if self.is_boundary_node is None:
            return False
        idx = self._nodes_in_ellipsoid(center, a, c)
        if len(idx) == 0:
            return False
        # All nodes must be inside and not boundary
        return np.all(~self.is_boundary_node[idx])  ###


    """
    def _can_place_internal_voxel(self, center, a, c) -> bool:
        """Проверяет возможность размещения внутреннего вокселя по ТЗ"""
        if self.is_boundary_node is None:
            return False

        idx = self._nodes_in_ellipsoid(center, a, c)
        if len(idx) == 0:
            return False

        # Главное условие по ТЗ: воксель не должен содержать граничных узлов
        return not np.any(self.is_boundary_node[idx])


    def _is_voxel_mostly_inside_internal(self, center, a, c):
        """Проверяет, что внутренний воксель в основном находится внутри модели"""
        rough = float(self.roughness_nm_var.get())

        # Проверяем ключевые точки вокселя
        test_points = []

        # Основные точки на осях
        test_points.append([center[0] + a, center[1], center[2]])  # +X
        test_points.append([center[0] - a, center[1], center[2]])  # -X
        test_points.append([center[0], center[1] + a, center[2]])  # +Y
        test_points.append([center[0], center[1] - a, center[2]])  # -Y
        test_points.append([center[0], center[1], center[2] + c])  # +Z

        # Для нижней точки применяем особые условия
        if center[2] - c >= -2 * rough:  # Не слишком низко
            test_points.append([center[0], center[1], center[2] - c])  # -Z

        # Дополнительные точки для лучшего покрытия
        for factor in [0.5, 0.7]:
            test_points.append([center[0] + a * factor, center[1], center[2]])
            test_points.append([center[0] - a * factor, center[1], center[2]])
            test_points.append([center[0], center[1] + a * factor, center[2]])
            test_points.append([center[0], center[1] - a * factor, center[2]])
            test_points.append([center[0], center[1], center[2] + c * factor])
            if center[2] - c * factor >= -rough:
                test_points.append([center[0], center[1], center[2] - c * factor])

        # Проверяем какие точки внутри модели
        inside_mask = self.tri_mesh_nm.contains(test_points)

        # Разделяем точки по высоте
        points_above_z0 = []
        points_below_z0 = []

        for i, point in enumerate(test_points):
            if point[2] >= 0:
                points_above_z0.append(inside_mask[i])
            else:
                points_below_z0.append(inside_mask[i])

        # Требования для внутренних вокселей:
        # 1. Все точки выше z=0 должны быть внутри модели
        if points_above_z0 and not all(points_above_z0):
            return False

        # 2. Точки ниже z=0 могут быть частично снаружи, но не все
        if points_below_z0 and sum(points_below_z0) < len(points_below_z0) * 0.7:
            return False

        # 3. Центр вокселя должен быть внутри модели
        center_inside = self.tri_mesh_nm.contains([center])[0]
        if not center_inside:
            # Для центров ниже z=0 допускается небольшое отклонение
            if center[2] >= 0 or abs(center[2]) > 2 * rough:
                return False

        return True
    # --------------------- Helpers ---------------------
    def _voxel_sizes(self) -> List[Tuple[float,float]]:
        a_min = float(self.min_width_nm_var.get())/2.0
        a_max = float(self.max_width_nm_var.get())/2.0
        c_min = float(self.min_height_nm_var.get())/2.0
        c_max = float(self.max_height_nm_var.get())/2.0
        n = max(1, int(self.num_sizes_var.get()))
        a_vals = np.linspace(a_min, a_max, n)
        c_vals = np.linspace(c_min, c_max, n)
        sizes = [(float(a_vals[i]), float(c_vals[i])) for i in range(n)]
        # sort by volume descending
        sizes.sort(key=lambda ac: (ac[0]**2*ac[1]), reverse=True)
        return sizes

    def _nodes_in_ellipsoid(self, center, a, c) -> np.ndarray:
        # Axis-aligned filter
        minb = np.array(center) - np.array([a, a, c])
        maxb = np.array(center) + np.array([a, a, c])
        pts = self.grid_nodes_nm
        mask_box = (
            (pts[:,0] >= minb[0]) & (pts[:,0] <= maxb[0]) &
            (pts[:,1] >= minb[1]) & (pts[:,1] <= maxb[1]) &
            (pts[:,2] >= minb[2]) & (pts[:,2] <= maxb[2])
        )
        idx = np.where(mask_box)[0]
        if len(idx)==0:
            return idx
        sel = pts[idx]
        rel = sel - np.array(center)
        val = (rel[:,0]/a)**2 + (rel[:,1]/a)**2 + (rel[:,2]/c)**2
        inside = val <= 1.0
        return idx[inside]

    def _get_inward_normal(self, point):
        """Calculate inward-pointing normal at a point near the surface"""
        try:
            # Get closest point on surface and its normal
            closest_point, distance, triangle_id = self.tri_mesh_nm.nearest.on_surface([point])
            face_normal = self.tri_mesh_nm.face_normals[triangle_id[0]]

            # Invert normal to point inward
            inward_normal = -face_normal

            # Normalize
            norm = np.linalg.norm(inward_normal)
            if norm == 0:
                return None
            inward_normal = inward_normal / norm
            return inward_normal
        except Exception as e:
            self._log(f"Error computing normal at {point}: {e}")
            return None

    def _is_voxel_mostly_inside(self, center, a, c):
        """Упрощенная проверка - воксель должен быть в основном внутри модели"""
        # Проверяем несколько точек
        test_points = [
            center,
            [center[0] + a*0.5, center[1], center[2]],
            [center[0] - a*0.5, center[1], center[2]],
            [center[0], center[1] + a*0.5, center[2]],
            [center[0], center[1] - a*0.5, center[2]],
            [center[0], center[1], center[2] + c*0.5],
        ]

        # Для точек ниже z=0 - менее строгая проверка
        if center[2] - c*0.5 >= 0:
            test_points.append([center[0], center[1], center[2] - c*0.5])

        inside_count = np.sum(self.tri_mesh_nm.contains(test_points))
        return inside_count >= len(test_points) * 0.7  # 70% точек должны быть внутри



    # --------------------- Core: Coarse fill ---------------------
# --------------------- Core: Coarse fill ---------------------
    def _coarse_fill_worker(self):
        """Исправленный модуль грубого заполнения с правильным порядком попыток размещения"""
        if self.grid_nodes_nm is None:
            raise RuntimeError('Calculate grid first')
        t0 = time.time()
        rough = float(self.roughness_nm_var.get())
        hatch = float(self.hatching_nm_var.get())
        slice_d = float(self.slicing_nm_var.get())
        sizes = self._voxel_sizes()

        self._log(f"Voxel sizes (a,c) nm: {sizes}")

        # Prepare layer indices - use only inside nodes
        z_vals = self.grid_nodes_nm[:,2]
        zmin, zmax = z_vals.min(), z_vals.max()

        # Calculate strides based on hatching and slicing distances
        stride_xy = max(1, int(round(hatch / rough)))
        stride_z = max(1, int(round(slice_d / rough)))
        self._log(f"Coarse fill strides: xy={stride_xy}, z={stride_z}")

        nodes = self.grid_nodes_nm
        filled_count_before = self.filled_mask.sum()

        # Iterate layers by z value with slicing distance
        z_layers = np.arange(zmin, zmax + 1e-9, slice_d)
        total_layers = len(z_layers)

        for layer_idx, z in enumerate(z_layers):
            if self.cancel_event.is_set():
                self._log('Coarse fill cancelled')
                return

            # Update progress
            progress = 10 + 80 * layer_idx / total_layers
            self.after(0, lambda: self._set_progress(progress))

            # Candidate indices in this layer (any i,j)
            layer_mask = (np.abs(nodes[:,2] - z) < 0.5*rough)
            if z < 2 * rough:  # Для нижних слоев
                cand_idx = np.where(layer_mask & (~self.filled_mask))[0]
            else:
                cand_idx = np.where(layer_mask & (~self.filled_mask) & (~self.is_boundary_node))[0]

            if len(cand_idx) == 0:
                continue

            # Sort candidates by x and y for consistent ordering
            cand_points = nodes[cand_idx]

            # Create ordered list of candidates following the traversal direction
            cand_idx_ordered = []
            x_min, x_max = cand_points[:, 0].min(), cand_points[:, 0].max()
            y_min, y_max = cand_points[:, 1].min(), cand_points[:, 1].max()

            # Разбиваем на полосы по X с шагом hatch
            x_bands = np.arange(x_min, x_max + hatch, hatch)

            for i in range(len(x_bands) - 1):
                x_band_mask = (cand_points[:, 0] >= x_bands[i]) & (cand_points[:, 0] < x_bands[i+1])
                x_band_indices = cand_idx[x_band_mask]

                if len(x_band_indices) == 0:
                    continue

                # В каждой полосе по X сортируем по Y
                x_band_points = nodes[x_band_indices]
                y_sorted_idx = np.argsort(x_band_points[:, 1])
                x_band_indices_sorted = x_band_indices[y_sorted_idx]

                # Берем каждый stride_xy-й элемент для соблюдения hatching distance
                cand_idx_ordered.extend(x_band_indices_sorted[::stride_xy])

            if not cand_idx_ordered:
                cand_idx_ordered = cand_idx[::stride_xy]

            # Try placing voxels with new priority order
            placed_count = 0
            for k in cand_idx_ordered:
                if self.cancel_event.is_set():
                    return

                cx, cy, cz = nodes[k]
                placed = False

                # НОВЫЙ ПОРЯДОК ПОПЫТОК РАЗМЕЩЕНИЯ:

                # Шаг 1: Самый большой размер в исходной точке
                if sizes:  # Проверяем, что есть доступные размеры
                    a, c = sizes[0]  # Самый большой размер
                    if self._can_place_internal_voxel((cx, cy, cz), a, c):
                        vi = len(self.voxels)
                        self.voxels.append(Voxel((cx, cy, cz), 1, a, c, False))  # size_id=1 для самого большого
                        self.internal_voxel_indices.append(vi)
                        idx_in = self._nodes_in_ellipsoid((cx, cy, cz), a, c)
                        self.filled_mask[idx_in] = True
                        placed = True
                        placed_count += 1

                if placed:
                    continue

                # Шаг 2: Уменьшаем шаг по оси X с самым большим размером
                if sizes:
                    a, c = sizes[0]  # Все еще самый большой размер
                    step_reductions = [0.75, 0.5]  # Только уменьшенные шаги

                    for step_factor in step_reductions:
                        if placed:
                            break

                        current_hatch = hatch * step_factor

                        # Сдвигаем только по оси X (направление движения в этом слое)
                        x_offset_points = [
                            (cx + current_hatch, cy, cz),
                            (cx - current_hatch, cy, cz)
                        ]

                        for point in x_offset_points:
                            if placed:
                                break

                            px, py, pz = point

                            if self._can_place_internal_voxel((px, py, pz), a, c):
                                vi = len(self.voxels)
                                self.voxels.append(Voxel((px, py, pz), 1, a, c, False))
                                self.internal_voxel_indices.append(vi)
                                idx_in = self._nodes_in_ellipsoid((px, py, pz), a, c)
                                self.filled_mask[idx_in] = True
                                placed = True
                                placed_count += 1
                                break

                if placed:
                    continue

                # Шаг 4: Пробуем меньшие размеры в точках с уменьшенным шагом по X
                if not placed and len(sizes) > 1:
                    for step_factor in [0.75, 0.5]:
                        if placed:
                            break

                        current_hatch = hatch * step_factor
                        x_offset_points = [
                            (cx + current_hatch, cy, cz),
                            (cx - current_hatch, cy, cz)
                        ]

                        for point in x_offset_points:
                            if placed:
                                break

                            px, py, pz = point

                            # Пробуем все меньшие размеры
                            for s_id in range(1, len(sizes)):
                                if placed:
                                    break

                                a, c = sizes[s_id]
                                if self._can_place_internal_voxel((px, py, pz), a, c):
                                    vi = len(self.voxels)
                                    self.voxels.append(Voxel((px, py, pz), s_id + 1, a, c, False))
                                    self.internal_voxel_indices.append(vi)
                                    idx_in = self._nodes_in_ellipsoid((px, py, pz), a, c)
                                    self.filled_mask[idx_in] = True
                                    placed = True
                                    placed_count += 1
                                    break

                if placed:
                    continue

                # Шаг 3: Сдвиг вдоль нормали с самым большим размером
                if sizes and cz >= 0:  # Только для точек выше z=0
                    a, c = sizes[0]  # Самый большой размер
                    normal = self._get_inward_normal((cx, cy, cz))
                    if normal is not None:
                        for distance_factor in [0.3, 0.5, 0.7, 1.0]:
                            if placed:
                                break

                            shift_distance = distance_factor * rough
                            new_center = (
                                cx + normal[0] * shift_distance,
                                cy + normal[1] * shift_distance,
                                cz + normal[2] * shift_distance
                            )

                            if self._can_place_internal_voxel(new_center, a, c):
                                vi = len(self.voxels)
                                self.voxels.append(Voxel(new_center, 1, a, c, False))
                                self.internal_voxel_indices.append(vi)
                                idx_in = self._nodes_in_ellipsoid(new_center, a, c)
                                self.filled_mask[idx_in] = True
                                placed = True
                                placed_count += 1
                                break

                if placed:
                    continue

                # Шаг 5: Меньшие размеры при сдвиге вдоль нормали
                if not placed and len(sizes) > 1 and cz >= 0:
                    normal = self._get_inward_normal((cx, cy, cz))
                    if normal is not None:
                        for distance_factor in [0.3, 0.5, 0.7, 1.0]:
                            if placed:
                                break

                            shift_distance = distance_factor * rough
                            new_center = (
                                cx + normal[0] * shift_distance,
                                cy + normal[1] * shift_distance,
                                cz + normal[2] * shift_distance
                            )

                            # Пробуем все меньшие размеры
                            for s_id in range(1, len(sizes)):
                                if placed:
                                    break

                                a, c = sizes[s_id]
                                if self._can_place_internal_voxel(new_center, a, c):
                                    vi = len(self.voxels)
                                    self.voxels.append(Voxel(new_center, s_id + 1, a, c, False))
                                    self.internal_voxel_indices.append(vi)
                                    idx_in = self._nodes_in_ellipsoid(new_center, a, c)
                                    self.filled_mask[idx_in] = True
                                    placed = True
                                    placed_count += 1
                                    break

                if placed:
                    continue

                # Шаг 6: Меньшие размеры в исходной точке
                if not placed and len(sizes) > 1:
                    for s_id in range(1, len(sizes)):  # Начинаем со второго размера (первый уже пробовали)
                        if placed:
                            break

                        a, c = sizes[s_id]
                        if self._can_place_internal_voxel((cx, cy, cz), a, c):
                            vi = len(self.voxels)
                            self.voxels.append(Voxel((cx, cy, cz), s_id + 1, a, c, False))
                            self.internal_voxel_indices.append(vi)
                            idx_in = self._nodes_in_ellipsoid((cx, cy, cz), a, c)
                            self.filled_mask[idx_in] = True
                            placed = True
                            placed_count += 1
                            break

                # Логируем успешное размещение
                if placed and placed_count % 10 == 0:
                    self._log(f"Layer {layer_idx+1}: placed {placed_count} voxels")

            self._log(f"Layer {layer_idx+1}/{total_layers}: placed {placed_count} voxels")

        filled_after = self.filled_mask.sum()
        self._log(f"Coarse fill: added {len(self.internal_voxel_indices)} internal voxels; nodes filled +{filled_after-filled_count_before}")

        # Добавляем расчет покрытия
        if self.is_inside_mask is not None and self.filled_mask is not None:
            total_inside = int(self.is_inside_mask.sum())
            coverage = (filled_after / total_inside * 100.0) if total_inside > 0 else 0
            self._log(f"Coverage after coarse fill: {filled_after}/{total_inside} ({coverage:.2f}%)")

        # Update statistics and layer slider
        self.update_stats()
        self._update_layer_slider()


    # --------------------- Core: Smoothing ---------------------
    def _smoothing_worker(self):
        """Исправленный модуль разглаживания согласно ТЗ с дополнительной оптимизацией"""
        if (self.grid_nodes_nm is None or self.is_boundary_node is None or
            self.filled_mask is None):
            self._log('Smoothing: grid not calculated or incomplete')
            return

        if len(self.internal_voxel_indices) == 0:
            self._log('Smoothing: no internal voxels yet')

        rough = float(self.roughness_nm_var.get())
        sizes = self._voxel_sizes()

        self._log(f"Starting smoothing with {len(sizes)} voxel sizes")

        # Получаем ВСЕ граничные узлы
        boundary_indices = np.where(self.is_boundary_node)[0]

        if len(boundary_indices) == 0:
            self._log('No boundary nodes found')
            return

        self._log(f"Found {len(boundary_indices)} boundary nodes")

        # Этап 1: Размещение граничных вокселей
        added_boundary_voxels = 0
        processed_count = 0

        for bi in boundary_indices:
            if self.cancel_event.is_set():
                self._log('Smoothing cancelled')
                return

            processed_count += 1
            if processed_count % 100 == 0:
                progress = 10 + 40 * processed_count / len(boundary_indices)
                self.after(0, lambda: self._set_progress(progress))
                self._log(f"Processed {processed_count}/{len(boundary_indices)} boundary nodes")

            node_pos = self.grid_nodes_nm[bi]

            # Пропускаем узлы слишком близко к низу (z=0)
            if node_pos[2] < rough:
                continue

            # Вычисляем нормаль к поверхности
            normal = self._get_inward_normal(node_pos)
            if normal is None:
                continue

            # Пробуем разместить воксель от большего размера к меньшему
            voxel_placed = False

            for size_idx, (a, c) in enumerate(sizes):
                if voxel_placed:
                    break

                # Пробуем разные расстояния сдвига вдоль нормали
                for distance_factor in [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]:
                    if voxel_placed:
                        break

                    # Вычисляем центр кандидата
                    shift_distance = distance_factor * rough
                    candidate_center = node_pos + normal * shift_distance

                    # НОВОЕ УСЛОВИЕ: воксель не должен содержать граничных узлов
                    nodes_in_voxel = self._nodes_in_ellipsoid(candidate_center, a, c)
                    if len(nodes_in_voxel) == 0:
                        continue

                    # Проверяем, что воксель не содержит граничных узлов
                    boundary_nodes_in_voxel = np.any(self.is_boundary_node[nodes_in_voxel])
                    if boundary_nodes_in_voxel:
                        continue  # Пропускаем этот вариант, пробуем следующий

                    # Проверяем, что воксель в основном внутри модели (кроме нижней части)
                    #if not self._is_voxel_valid_for_boundary(candidate_center, a, c):
                    #    continue

                    # Проверяем покрытие незаполненных узлов (только внутренних)
                    internal_nodes_in_voxel = [idx for idx in nodes_in_voxel
                                             if not self.is_boundary_node[idx] and self.is_inside_mask[idx]]

                    if len(internal_nodes_in_voxel) == 0:
                        continue

                    unfilled_count = np.sum(~self.filled_mask[internal_nodes_in_voxel])
                    coverage_ratio = unfilled_count / len(internal_nodes_in_voxel)

                    # Условие из ТЗ: покрытие должно быть >15%
                    if coverage_ratio >= 0.10:
                        # Добавляем граничный воксель
                        vi = len(self.voxels)
                        new_voxel = Voxel(
                            center=tuple(candidate_center),
                            size_id=size_idx + 1,
                            a_nm=a,
                            c_nm=c,
                            is_boundary=True
                        )
                        self.voxels.append(new_voxel)
                        self.boundary_voxel_indices.append(vi)
                        self.filled_mask[nodes_in_voxel] = True
                        added_boundary_voxels += 1
                        voxel_placed = True

                        if added_boundary_voxels % 10 == 0:
                            self._log(f"Added {added_boundary_voxels} boundary voxels")
                        break

        self._log(f"Stage 1 complete: added {added_boundary_voxels} boundary voxels")

        # Этап 2: Оптимизация перекрытий
        if added_boundary_voxels > 0 and len(self.internal_voxel_indices) > 0:
            self._log("Starting overlap optimization...")
            optimized_count = self._optimize_voxel_overlaps()
            self._log(f"Stage 2 complete: optimized {optimized_count} voxels")

        # ЭТАП 3: ДОПОЛНИТЕЛЬНАЯ ОПТИМИЗАЦИЯ - ДОЗАПОЛНЕНИЕ НЕЗАПОЛНЕННЫХ УЗЛОВ
        self._log("Starting stage 3: additional optimization for unoccupied nodes...")
        stage3_added = self._additional_optimization_worker()
        self._log(f"Stage 3 complete: added {stage3_added} additional boundary voxels")

        # Расчет итогового покрытия
        if self.is_inside_mask is not None and self.filled_mask is not None:
            total_inside = int(self.is_inside_mask.sum())
            filled = int(self.filled_mask.sum())
            coverage = (filled / total_inside * 100.0) if total_inside > 0 else 0
            self._log(f"Final coverage: {filled}/{total_inside} ({coverage:.2f}%)")

        self.after(0, lambda: self._set_progress(100))
        self.update_stats()
        self._update_layer_slider()
        self._update_view()

    def _additional_optimization_worker(self):
        """Дополнительная оптимизация - дозаполнение незаполненных узлов граничными вокселями"""
        if self.grid_nodes_nm is None or self.filled_mask is None:
            return 0

        rough = float(self.roughness_nm_var.get())
        sizes = self._voxel_sizes()

        if not sizes:
            return 0

        # Находим незаполненные узлы внутри модели
        unoccupied_nodes = np.where(
            self.is_inside_mask &
            ~self.is_boundary_node &
            ~self.filled_mask
        )[0]

        if len(unoccupied_nodes) == 0:
            self._log("No unoccupied nodes found for additional optimization")
            return 0

        self._log(f"Found {len(unoccupied_nodes)} unoccupied nodes for optimization")

        added_voxels = 0
        processed_count = 0

        # Сортируем узлы по высоте для последовательной обработки
        z_coords = self.grid_nodes_nm[unoccupied_nodes, 2]
        sorted_indices = np.argsort(z_coords)
        unoccupied_nodes_sorted = unoccupied_nodes[sorted_indices]

        for node_idx in unoccupied_nodes_sorted:
            if self.cancel_event.is_set():
                self._log('Additional optimization cancelled')
                return added_voxels

            processed_count += 1
            if processed_count % 100 == 0:
                progress = 80 + 15 * processed_count / len(unoccupied_nodes_sorted)
                self.after(0, lambda: self._set_progress(progress))
                self._log(f"Processed {processed_count}/{len(unoccupied_nodes_sorted)} unoccupied nodes")

            node_pos = self.grid_nodes_nm[node_idx]

            # Пропускаем узлы слишком близко к низу
            if node_pos[2] < rough:
                continue

            # Пробуем разместить воксель от большего размера к меньшему
            voxel_placed = False

            for size_idx, (a, c) in enumerate(sizes):
                if voxel_placed:
                    break

                # Проверяем, может ли воксель быть полностью внутри модели
                if not self._can_place_internal_voxel(node_pos, a, c):
                    continue  # Пробуем следующий размер

                # Находим узлы в потенциальном вокселе
                nodes_in_voxel = self._nodes_in_ellipsoid(node_pos, a, c)
                if len(nodes_in_voxel) == 0:
                    continue

                # Проверяем, что воксель не содержит граничных узлов
                if np.any(self.is_boundary_node[nodes_in_voxel]):
                    continue

                # Проверяем, что воксель в основном внутри модели
                #if not self._is_voxel_valid_for_boundary(node_pos, a, c):
                #    continue

                # Подсчитываем незаполненные узлы в этом вокселе
                unoccupied_in_voxel = np.sum(~self.filled_mask[nodes_in_voxel])
                total_nodes_in_voxel = len(nodes_in_voxel)

                # Проверяем процент незаполненных узлов (должен быть >10%)
                if total_nodes_in_voxel > 0:
                    unoccupied_ratio = unoccupied_in_voxel / total_nodes_in_voxel
                else:
                    unoccupied_ratio = 0

                if unoccupied_ratio > 0.02:  # Более 10% незаполненных узлов
                    # Добавляем граничный воксель
                    vi = len(self.voxels)
                    new_voxel = Voxel(
                        center=tuple(node_pos),
                        size_id=size_idx + 1,
                        a_nm=a,
                        c_nm=c,
                        is_boundary=True
                    )
                    self.voxels.append(new_voxel)
                    self.boundary_voxel_indices.append(vi)
                    self.filled_mask[nodes_in_voxel] = True
                    added_voxels += 1
                    voxel_placed = True

                    if added_voxels % 10 == 0:
                        self._log(f"Additional optimization: added {added_voxels} voxels")
                    break

        return added_voxels

    def _optimize_voxel_overlaps(self):
        """Оптимизация перекрытий между граничными и внутренними вокселями"""
        if not self.boundary_voxel_indices or not self.internal_voxel_indices:
            return 0

        optimized_count = 0
        sizes = self._voxel_sizes()

        # Создаем копии списков индексов для безопасной итерации
        boundary_indices_copy = self.boundary_voxel_indices.copy()
        internal_indices_copy = self.internal_voxel_indices.copy()

        # Список индексов для удаления
        indices_to_remove = set()

        # Проверяем перекрытия граничных вокселей с внутренними
        for boundary_idx in boundary_indices_copy:
            if self.cancel_event.is_set():
                return optimized_count

            # Проверяем, что воксель все еще существует
            if boundary_idx >= len(self.voxels) or self.voxels[boundary_idx] is None:
                continue

            boundary_voxel = self.voxels[boundary_idx]

            for internal_idx in internal_indices_copy:
                if self.cancel_event.is_set():
                    return optimized_count

                # Проверяем, что воксель все еще существует и не помечен для удаления
                if (internal_idx >= len(self.voxels) or
                    self.voxels[internal_idx] is None or
                    internal_idx in indices_to_remove):
                    continue

                internal_voxel = self.voxels[internal_idx]

                # Проверяем расстояние между центрами
                distance = np.linalg.norm(
                    np.array(boundary_voxel.center) - np.array(internal_voxel.center)
                )

                # Если воксели пересекаются
                max_distance = boundary_voxel.a_nm + internal_voxel.a_nm
                if distance < max_distance * 0.8:  # Перекрытие > 50%
                    # Находим узлы внутреннего вокселя
                    internal_nodes = self._nodes_in_ellipsoid(
                        internal_voxel.center, internal_voxel.a_nm, internal_voxel.c_nm)

                    # Находим узлы граничного вокселя
                    boundary_nodes = self._nodes_in_ellipsoid(
                        boundary_voxel.center, boundary_voxel.a_nm, boundary_voxel.c_nm)

                    # Вычисляем процент перекрытия
                    overlap_nodes = set(internal_nodes) & set(boundary_nodes)
                    overlap_ratio = len(overlap_nodes) / len(internal_nodes) if len(internal_nodes) > 0 else 0

                    if overlap_ratio > 0.4:  # Перекрытие больше 50%
                        # Пробуем уменьшить внутренний воксель
                        current_size = (internal_voxel.a_nm, internal_voxel.c_nm)

                        # Находим текущий индекс размера
                        try:
                            current_idx = next(i for i, (a, c) in enumerate(sizes)
                                          if abs(a - current_size[0]) < 1e-6 and abs(c - current_size[1]) < 1e-6)
                        except StopIteration:
                            continue

                        # Пробуем меньшие размеры
                        smaller_found = False
                        for new_idx in range(current_idx + 1, len(sizes)):
                            new_a, new_c = sizes[new_idx]

                            # Проверяем возможность размещения меньшего вокселя
                            if self._can_place_internal_voxel(internal_voxel.center, new_a, new_c):
                                # Освобождаем узлы старого вокселя
                                self.filled_mask[internal_nodes] = False

                                # Заменяем воксель на меньший
                                new_voxel = Voxel(
                                    center=internal_voxel.center,
                                    size_id=new_idx + 1,
                                    a_nm=new_a,
                                    c_nm=new_c,
                                    is_boundary=False
                                )

                                # Обновляем воксель в списке
                                self.voxels[internal_idx] = new_voxel

                                # Занимаем узлы нового вокселя
                                new_nodes = self._nodes_in_ellipsoid(internal_voxel.center, new_a, new_c)
                                self.filled_mask[new_nodes] = True

                                optimized_count += 1
                                smaller_found = True
                                break

                        # Если не нашли подходящий меньший размер, помечаем для удаления
                        if not smaller_found:
                            # Освобождаем узлы
                            self.filled_mask[internal_nodes] = False
                            indices_to_remove.add(internal_idx)
                            optimized_count += 1

        # Удаляем помеченные воксели
        if indices_to_remove:
            # Сортируем индексы в обратном порядке для безопасного удаления
            sorted_indices_to_remove = sorted(indices_to_remove, reverse=True)

            for idx in sorted_indices_to_remove:
                if idx < len(self.voxels):
                    # Устанавливаем воксель в None вместо удаления, чтобы сохранить индексы
                    self.voxels[idx] = None

            # Теперь фильтруем список, удаляя None
            self.voxels = [v for v in self.voxels if v is not None]

            # Пересчитываем индексы внутренних и граничных вокселей
            self.internal_voxel_indices = [i for i, v in enumerate(self.voxels)
                                         if not v.is_boundary]
            self.boundary_voxel_indices = [i for i, v in enumerate(self.voxels)
                                         if v.is_boundary]

        return optimized_count




    def _is_voxel_mostly_inside_boundary(self, center, a, c):
        """Усиленная проверка для граничных вокселей - они должны быть в основном внутри модели"""
        # Проверяем больше точек на поверхности эллипсоида
        test_points = []
        rough = float(self.roughness_nm_var.get())

        # Точки вдоль основных осей
        test_points.append([center[0] + a, center[1], center[2]])
        test_points.append([center[0] - a, center[1], center[2]])
        test_points.append([center[0], center[1] + a, center[2]])
        test_points.append([center[0], center[1] - a, center[2]])
        test_points.append([center[0], center[1], center[2] + c])

        # Для нижней точки применяем ослабленные требования
        if center[2] - c >= -2*rough:  # Только если не слишком низко
            test_points.append([center[0], center[1], center[2] - c])

        # Дополнительные точки на поверхности
        sqrt2 = math.sqrt(2)
        sqrt3 = math.sqrt(3)

        # Промежуточные точки
        for factor in [0.5, 0.7]:
            test_points.append([center[0] + a*factor, center[1], center[2]])
            test_points.append([center[0] - a*factor, center[1], center[2]])
            test_points.append([center[0], center[1] + a*factor, center[2]])
            test_points.append([center[0], center[1] - a*factor, center[2]])
            test_points.append([center[0], center[1], center[2] + c*factor])
            if center[2] - c*factor >= -rough:
                test_points.append([center[0], center[1], center[2] - c*factor])

        # Проверяем все точки
        inside_points = self.tri_mesh_nm.contains(test_points)

        # Разделяем точки на те, что выше z=0 и near z=0
        points_above_zero = [p for p in test_points if p[2] >= 0]
        points_near_zero = [p for p in test_points if -rough <= p[2] < 0]

        inside_above_zero = [inside_points[i] for i, p in enumerate(test_points) if p[2] >= 0]
        inside_near_zero = [inside_points[i] for i, p in enumerate(test_points) if -rough <= p[2] < 0]

        # Точки выше z=0 должны быть в основном внутри
        if points_above_zero and np.sum(inside_above_zero) < len(inside_above_zero) * 0.98:
            return False

        # Точки near z=0 могут быть частично outside, но не полностью
        if points_near_zero and np.sum(inside_near_zero) < len(inside_near_zero) * 0.8:
            return False

        return True

    def _is_voxel_completely_inside(self, center, a, c):
        """Проверяет, что весь воксель находится внутри модели"""
        # Проверяем центр
        if not self.tri_mesh_nm.contains([center])[0]:
            return False

        # Проверяем ключевые точки на поверхности эллипсоида
        test_points = []

        # Точки вдоль осей
        test_points.append([center[0] + a, center[1], center[2]])  # +X
        test_points.append([center[0] - a, center[1], center[2]])  # -X
        test_points.append([center[0], center[1] + a, center[2]])  # +Y
        test_points.append([center[0], center[1] - a, center[2]])  # -Y
        test_points.append([center[0], center[1], center[2] + c])  # +Z
        test_points.append([center[0], center[1], center[2] - c])  # -Z

        # Диагональные точки
        sqrt2 = math.sqrt(2)
        test_points.append([center[0] + a/sqrt2, center[1] + a/sqrt2, center[2]])
        test_points.append([center[0] + a/sqrt2, center[1] - a/sqrt2, center[2]])
        test_points.append([center[0] - a/sqrt2, center[1] + a/sqrt2, center[2]])
        test_points.append([center[0] - a/sqrt2, center[1] - a/sqrt2, center[2]])

        # Проверяем все точки
        inside_points = self.tri_mesh_nm.contains(test_points)

        # Требуем, чтобы все точки были внутри модели
        return np.all(inside_points)


    def _is_voxel_completely_inside_strict(self, center, a, c):
        """Strict check if the entire voxel (ellipsoid) is completely inside the model"""
        # Check center point
        if not self.tri_mesh_nm.contains([center])[0]:
            return False

        # Check key points on the ellipsoid surface
        test_points = []

        # Points along principal axes
        test_points.append([center[0] + a, center[1], center[2]])  # +X
        test_points.append([center[0] - a, center[1], center[2]])  # -X
        test_points.append([center[0], center[1] + a, center[2]])  # +Y
        test_points.append([center[0], center[1] - a, center[2]])  # -Y
        test_points.append([center[0], center[1], center[2] + c])  # +Z
        test_points.append([center[0], center[1], center[2] - c])  # -Z

        # Additional points for better coverage
        sqrt2 = math.sqrt(2)
        test_points.append([center[0] + a/sqrt2, center[1] + a/sqrt2, center[2]])
        test_points.append([center[0] + a/sqrt2, center[1] - a/sqrt2, center[2]])
        test_points.append([center[0] - a/sqrt2, center[1] + a/sqrt2, center[2]])
        test_points.append([center[0] - a/sqrt2, center[1] - a/sqrt2, center[2]])

        # Check all test points
        if not np.all(self.tri_mesh_nm.contains(test_points)):
            return False

        return True


        # Update statistics
        self.update_stats()
        self._update_layer_slider()

    # --------------------- Core: Trajectory ---------------------
    def _trajectory_worker(self):
        if len(self.voxels) == 0:
            self._log('Trajectory: no voxels')
            return
        t0 = time.time()

        # Split voxels
        inner = [i for i in self.internal_voxel_indices]
        shell = [i for i in self.boundary_voxel_indices]

        # Строим траекторию в зависимости от выбранного порядка
        if self.fill_order_var.get() == 'inner_then_shell':
            # Внутренность -> оболочка (начинаем с внутренних, заканчиваем оболочкой)
            inner_traj = self._trajectory_internal(inner)
            shell_traj = self._trajectory_shell(shell)

            # Начальная точка - самая нижняя из внутренних
            start_point = self._find_lowest_point(inner_traj)
            # Конечная точка - самая верхняя из оболочных
            end_point = self._find_highest_point(shell_traj)

            # Перестраиваем траекторию чтобы начать с самой нижней и закончить самой верхней
            inner_traj = self._reorder_trajectory_from_point(inner_traj, start_point)
            shell_traj = self._reorder_trajectory_to_point(shell_traj, end_point)

            order = inner_traj + shell_traj
        else:
            # Оболочка -> внутренность (начинаем с оболочки, заканчиваем внутренними)
            shell_traj = self._trajectory_shell(shell)
            inner_traj = self._trajectory_internal(inner)

            # Начальная точка - самая нижняя из оболочных
            start_point = self._find_lowest_point(shell_traj)
            # Конечная точка - самая верхняя из внутренних
            end_point = self._find_highest_point(inner_traj)

            # Перестраиваем траекторию чтобы начать с самой нижней и закончить самой верхней
            shell_traj = self._reorder_trajectory_from_point(shell_traj, start_point)
            inner_traj = self._reorder_trajectory_to_point(inner_traj, end_point)

            order = shell_traj + inner_traj

        self.trajectory = order
        length = self._trajectory_length(order)

        # Логируем информацию о начале и конце
        start_voxel = self.voxels[order[0]]
        end_voxel = self.voxels[order[-1]]
        self._log(f"Trajectory: {len(order)} points, length={length:.1f} nm")
        self._log(f"Start: layer z={start_voxel.center[2]:.1f} nm ({'shell' if start_voxel.is_boundary else 'inner'})")
        self._log(f"End: layer z={end_voxel.center[2]:.1f} nm ({'shell' if end_voxel.is_boundary else 'inner'})")
        self._log(f"Pattern: {self.inner_pattern_var.get()}, Order: {self.fill_order_var.get()}")

        # Update statistics
        self.update_stats()

    def _find_lowest_point(self, trajectory):
        """Находит самую нижнюю точку в траектории"""
        if not trajectory:
            return None
        min_z = float('inf')
        lowest_point = trajectory[0]
        for voxel_idx in trajectory:
            voxel = self.voxels[voxel_idx]
            if voxel.center[2] < min_z:
                min_z = voxel.center[2]
                lowest_point = voxel_idx
        return lowest_point

    def _find_highest_point(self, trajectory):
        """Находит самую верхнюю точку в траектории"""
        if not trajectory:
            return None
        max_z = -float('inf')
        highest_point = trajectory[0]
        for voxel_idx in trajectory:
            voxel = self.voxels[voxel_idx]
            if voxel.center[2] > max_z:
                max_z = voxel.center[2]
                highest_point = voxel_idx
        return highest_point

    def _reorder_trajectory_from_point(self, trajectory, start_point):
        """Перестраивает траекторию чтобы начать с указанной точки"""
        if not trajectory or start_point not in trajectory:
            return trajectory

        if trajectory[0] == start_point:
            return trajectory

        # Находим индекс стартовой точки и перестраиваем
        start_index = trajectory.index(start_point)
        return trajectory[start_index:] + trajectory[:start_index]

    def _reorder_trajectory_to_point(self, trajectory, end_point):
        """Перестраивает траекторию чтобы закончить указанной точкой"""
        if not trajectory or end_point not in trajectory:
            return trajectory

        if trajectory[-1] == end_point:
            return trajectory

        # Находим индекс конечной точки и перестраиваем
        end_index = trajectory.index(end_point)
        # Создаем новую траекторию где конечная точка в конце
        new_trajectory = [v for v in trajectory if v != end_point]
        new_trajectory.append(end_point)
        return new_trajectory

    def _trajectory_internal(self, indices: List[int]) -> List[int]:
        """Траектория для внутренних вокселей с учетом выбранного паттерна"""
        if not indices:
            return []

        pattern = self.inner_pattern_var.get()

        # Группируем по слоям
        slice_d = float(self.slicing_nm_var.get())
        centers = np.array([self.voxels[i].center for i in indices])

        if len(centers) == 0:
            return []

        z0 = centers[:, 2].min()
        layer_ids = np.floor((centers[:, 2] - z0) / max(1.0, slice_d) + 1e-6).astype(int)

        result = []

        # Сортируем слои по возрастанию Z (снизу вверх)
        unique_layers = np.unique(layer_ids)
        sorted_layers = sorted(unique_layers)

        for layer in sorted_layers:
            layer_idx = [indices[j] for j in np.where(layer_ids == layer)[0]]

            if pattern == 'zigzag':
                result += self._zigzag_pattern(layer_idx)
            elif pattern == 'stripes':
                result += self._stripes_pattern(layer_idx)
            elif pattern == 'circle':
                result += self._circle_pattern(layer_idx)
            else:
                # Простая сортировка по X, затем по Y
                layer_idx.sort(key=lambda i: (self.voxels[i].center[0], self.voxels[i].center[1]))
                result += layer_idx

        return result

    def _zigzag_pattern(self, layer_indices):
        """Зигзагообразный паттерн без самопересечений"""
        if not layer_indices:
            return []

        # Группируем по строкам (Y)
        rows = {}
        for idx in layer_indices:
            voxel = self.voxels[idx]
            y = voxel.center[1]
            # Квантуем Y для группировки в строки
            rough = float(self.roughness_nm_var.get())
            row_key = round(y / rough)

            if row_key not in rows:
                rows[row_key] = []
            rows[row_key].append(idx)

        # Сортируем строки по Y
        sorted_rows = sorted(rows.items(), key=lambda x: x[0])

        result = []
        for i, (row_key, row_voxels) in enumerate(sorted_rows):
            # Сортируем воксели в строке по X
            row_voxels.sort(key=lambda idx: self.voxels[idx].center[0])

            # Чередуем направление для зигзага
            if i % 2 == 1:
                row_voxels.reverse()

            result.extend(row_voxels)

        return result

    def _stripes_pattern(self, layer_indices):
        """Полосовой паттерн (все строки в одном направлении)"""
        if not layer_indices:
            return []

        # Группируем по строкам (Y)
        rows = {}
        for idx in layer_indices:
            voxel = self.voxels[idx]
            y = voxel.center[1]
            # Квантуем Y для группировки в строки
            rough = float(self.roughness_nm_var.get())
            row_key = round(y / rough)

            if row_key not in rows:
                rows[row_key] = []
            rows[row_key].append(idx)

        # Сортируем строки по Y
        sorted_rows = sorted(rows.items(), key=lambda x: x[0])

        result = []
        for row_key, row_voxels in sorted_rows:
            # Сортируем воксели в строке по X (всегда слева направо)
            row_voxels.sort(key=lambda idx: self.voxels[idx].center[0])
            result.extend(row_voxels)

        return result

    def _circle_pattern(self, layer_indices):
        """Круговой паттерн без самопересечений"""
        if not layer_indices:
            return []

        # Находим центр слоя
        centers = np.array([self.voxels[i].center for i in layer_indices])
        center = np.mean(centers, axis=0)

        # Сортируем по углу
        angles = []
        for idx in layer_indices:
            voxel = self.voxels[idx]
            dx = voxel.center[0] - center[0]
            dy = voxel.center[1] - center[1]
            angle = math.atan2(dy, dx)
            angles.append(angle)

        # Сортируем по углу
        sorted_indices = [idx for _, idx in sorted(zip(angles, layer_indices))]
        return sorted_indices

    def _trajectory_shell(self, indices: List[int]) -> List[int]:
        """Траектория для оболочки - спираль снизу вверх без самопересечений"""
        if not indices:
            return []

        # Группируем по слоям
        slice_d = max(1.0, float(self.slicing_nm_var.get()))
        centers = np.array([self.voxels[i].center for i in indices])

        if len(centers) == 0:
            return []

        z0 = centers[:, 2].min()

        # Создаем слои
        layers = {}
        for i, center in zip(indices, centers):
            layer_idx = int((center[2] - z0) / slice_d)
            if layer_idx not in layers:
                layers[layer_idx] = []
            layers[layer_idx].append(i)

        # Сортируем слои по возрастанию Z (снизу вверх)
        sorted_layers = sorted(layers.items(), key=lambda x: x[0])

        result = []
        for layer_idx, layer_voxels in sorted_layers:
            # Для каждого слоя используем круговой паттерн
            layer_trajectory = self._circle_pattern(layer_voxels)
            result.extend(layer_trajectory)

        return result

    def _trajectory_length(self, order: List[int]) -> float:
        if len(order) < 2:
            return 0.0
        pts = np.array([self.voxels[i].center for i in order])
        dif = np.diff(pts, axis=0)
        return float(np.sum(np.linalg.norm(dif, axis=1)))
#------------------------GWL----------------------------------------------#

    # --------------------- Export ---------------------
    def _export_coords(self):
        if not self.trajectory:
            messagebox.showinfo('Export', 'No trajectory computed yet')
            return
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text','*.txt'),('CSV','*.csv')])
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            f.write('order,x_nm,y_nm,z_nm,size_id,is_boundary\n')
            for order_id, vi in enumerate(self.trajectory, start=1):
                v = self.voxels[vi]
                f.write(f"{order_id},{v.center[0]:.3f},{v.center[1]:.3f},{v.center[2]:.3f},{v.size_id},{int(v.is_boundary)}\n")
        self._log(f"Exported coords: {os.path.basename(path)}")

    def _export_stats(self):
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text','*.txt')])
        if not path:
            return
        total_nodes = int(self.is_inside_mask.sum()) if self.is_inside_mask is not None else 0
        filled_nodes = int(self.filled_mask.sum()) if self.filled_mask is not None else 0
        coverage = (filled_nodes/total_nodes*100.0) if total_nodes>0 else 0.0
        stats = {
            'bbox_nm': self.mesh_bounds_nm.tolist() if self.mesh_bounds_nm is not None else None,
            'grid_shape': tuple(int(x) for x in self.grid_shape) if self.grid_shape else None,
            'nodes_total_inside': total_nodes,
            'nodes_boundary': int(self.is_boundary_node.sum()) if self.is_boundary_node is not None else 0,
            'nodes_internal': int(self.is_inside_mask.sum()-self.is_boundary_node.sum()) if self.is_inside_mask is not None and self.is_boundary_node is not None else 0,
            'voxels_total': len(self.voxels),
            'voxels_internal': len(self.internal_voxel_indices),
            'voxels_boundary': len(self.boundary_voxel_indices),
            'trajectory_length_nm': self._trajectory_length(self.trajectory) if self.trajectory else 0.0,
            'coverage_percent': coverage,
            'log': self._log_lines,
        }
        with open(path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(stats, ensure_ascii=False, indent=2))
        self._log(f"Exported stats/log: {os.path.basename(path)}")

    # --------------------- Visualization ---------------------

    def _draw_voxel_outline(self, v: Voxel):
        """Draw outline for a single voxel"""
        cx, cy, cz = v.center
        a, c = v.a_nm, v.c_nm
        t = np.linspace(0, 2 * np.pi, 20)

        # Draw equator (xy plane)
        x = cx + a * np.cos(t)
        y = cy + a * np.sin(t)
        z = np.full_like(x, cz)
        self.ax3d.plot(x, y, z, 'k-', linewidth=0.5, alpha=0.6)

        # Draw two meridians
        for angle in [0, np.pi/2]:
            x = cx + a * np.cos(t) * np.cos(angle)
            y = cy + a * np.cos(t) * np.sin(angle)
            z = cz + c * np.sin(t)
            self.ax3d.plot(x, y, z, 'k-', linewidth=0.5, alpha=0.6)

    def _update_view(self):
        ax = self.ax3d
        ax.cla()
        ax.set_xlabel('x (nm)')
        ax.set_ylabel('y (nm)')
        ax.set_zlabel('z (nm)')
        # STL
        if self.show_stl_var.get() and self.tri_mesh_nm is not None:
            try:
                ax.plot_trisurf(self.tri_mesh_nm.vertices[:,0], self.tri_mesh_nm.vertices[:,1], self.tri_mesh_nm.faces, self.tri_mesh_nm.vertices[:,2], color=(0.7,0.7,0.8,0.4), linewidth=0.2, edgecolor='k')
            except Exception:
                pass
        # Grid
        if self.show_grid_var.get() and self.mesh_bounds_nm is not None:
            minb,maxb = self.mesh_bounds_nm
            # draw bbox grid lines (coarse)
            xs = [minb[0], maxb[0]]; ys = [minb[1], maxb[1]]; zs = [minb[2], maxb[2]]
            for x in xs:
                ax.plot([x,x],[ys[0],ys[1]],[zs[0],zs[0]], c='gray', alpha=0.2)
                ax.plot([x,x],[ys[0],ys[1]],[zs[1],zs[1]], c='gray', alpha=0.2)
            for y in ys:
                ax.plot([xs[0],xs[1]],[y,y],[zs[0],zs[0]], c='gray', alpha=0.2)
                ax.plot([xs[0],xs[1]],[y,y],[zs[1],zs[1]], c='gray', alpha=0.2)
            for z in zs:
                ax.plot([xs[0],xs[0]],[ys[0],ys[0]],[z,z], c='gray', alpha=0.2)
                ax.plot([xs[1],xs[1]],[ys[1],ys[1]],[z,z], c='gray', alpha=0.2)

        # Nodes
        if self.show_nodes_var.get() and self.grid_nodes_nm is not None:
            pts = self.grid_nodes_nm
            # Subsample to avoid overload
            step = max(1, int(len(pts)//10000))
            sel = pts[::step]
            ax.scatter(sel[:,0], sel[:,1], sel[:,2], s=1, c='blue', alpha=0.2)
            # boundary nodes in red
            if self.is_boundary_node is not None:
                bidx = np.where(self.is_boundary_node)[0]
                bsel = bidx[::max(1,len(bidx)//5000)]
                if len(bsel)>0:
                    bp = pts[bsel]
                    ax.scatter(bp[:,0], bp[:,1], bp[:,2], s=2, c='red', alpha=0.6)

        # Voxels centers
        if self.show_internal_voxels_var.get() and self.internal_voxel_indices:
            pts = np.array([self.voxels[i].center for i in self.internal_voxel_indices])
            ax.scatter(pts[:,0], pts[:,1], pts[:,2], s=6, c='dodgerblue', alpha=0.7)
        if self.show_boundary_voxels_var.get() and self.boundary_voxel_indices:
            pts = np.array([self.voxels[i].center for i in self.boundary_voxel_indices])
            ax.scatter(pts[:,0], pts[:,1], pts[:,2], s=12, c='crimson', alpha=0.8)

        # Draw voxel outlines
        if self.show_voxel_outlines_var.get():
            # Draw outlines for all voxels
            for v in self.voxels:
                self._draw_voxel_outline(v)
        else:
            # Draw circles for a subset of voxels to visualize shape (equator + 2 meridians)
            max_circles = 0
            lines = []
            colors = []
            def add_voxel_circles(v: Voxel, color):
                cx,cy,cz = v.center
                a,c = v.a_nm, v.c_nm
                t = np.linspace(0, 2*np.pi, 40)
                # equator (xy plane at z)
                ex = cx + a*np.cos(t)
                ey = cy + a*np.sin(t)
                ez = np.full_like(ex, cz)
                for i in range(len(t)-1):
                    lines.append([(ex[i],ey[i],ez[i]), (ex[i+1],ey[i+1],ez[i+1])])
                    colors.append(color)
                # meridian xz (y fixed)
                mx = cx + a*np.cos(t)
                my = np.full_like(mx, cy)
                mz = cz + c*np.sin(t)
                for i in range(len(t)-1):
                    lines.append([(mx[i],my[i],mz[i]), (mx[i+1],my[i+1],mz[i+1])])
                    colors.append(color)
                # meridian yz (x fixed)
                mx = np.full_like(t, cx)
                my = cy + a*np.cos(t)
                mz = cz + c*np.sin(t)
                for i in range(len(t)-1):
                    lines.append([(mx[i],my[i],mz[i]), (mx[i+1],my[i+1],mz[i+1])])
                    colors.append(color)

            # choose subset
            all_indices = []
            if self.show_internal_voxels_var.get():
                all_indices += self.internal_voxel_indices
            if self.show_boundary_voxels_var.get():
                all_indices += self.boundary_voxel_indices
            sub = all_indices[:max_circles]
            for i in sub:
                v = self.voxels[i]
                add_voxel_circles(v, 'k')
            if lines:
                lc = Line3DCollection(lines, colors=colors, linewidths=0.6, alpha=0.6)
                ax.add_collection3d(lc)

        # Trajectory
        if self.show_trajectory_var.get() and self.trajectory:
            pts = np.array([self.voxels[i].center for i in self.trajectory])
            ax.plot(pts[:,0], pts[:,1], pts[:,2], c='green', lw=1.2, alpha=0.9)
            # start/end markers
            ax.scatter([pts[0,0]],[pts[0,1]],[pts[0,2]], c='lime', s=40)
            ax.scatter([pts[-1,0]],[pts[-1,1]],[pts[-1,2]], c='magenta', s=40)

        # Ax limits
        if self.mesh_bounds_nm is not None:
            minb,maxb = self.mesh_bounds_nm
            ax.set_xlim(minb[0], maxb[0])
            ax.set_ylim(minb[1], maxb[1])
            ax.set_zlim(minb[2], maxb[2])
        self.canvas3d.draw_idle()

        # Update coverage in status
        if self.is_inside_mask is not None and self.filled_mask is not None:
            total_nodes = int(self.is_inside_mask.sum())
            filled_nodes = int(self.filled_mask.sum())
            if total_nodes>0:
                cov = filled_nodes/total_nodes*100.0
                self._log(f"Coverage: {filled_nodes}/{total_nodes} nodes = {cov:.2f}%")

        # Voxels centers - добавляем проверку на None
        if self.show_internal_voxels_var.get() and self.internal_voxel_indices:
            valid_indices = [i for i in self.internal_voxel_indices
                            if i < len(self.voxels) and self.voxels[i] is not None]
            if valid_indices:
                pts = np.array([self.voxels[i].center for i in valid_indices])
                ax.scatter(pts[:,0], pts[:,1], pts[:,2], s=6, c='dodgerblue', alpha=0.7)

        if self.show_boundary_voxels_var.get() and self.boundary_voxel_indices:
            valid_indices = [i for i in self.boundary_voxel_indices
                            if i < len(self.voxels) and self.voxels[i] is not None]
            if valid_indices:
                pts = np.array([self.voxels[i].center for i in valid_indices])
                ax.scatter(pts[:,0], pts[:,1], pts[:,2], s=12, c='crimson', alpha=0.8)

        # Update layers view drawing
        self._update_layers_plot()

        # Update statistics display
        self.update_stats()

    def _update_layer_slider(self):
        if self.grid_shape is None:
            self.layer_slider.configure(from_=0, to=0)
            self.layer_label.configure(text='0')
            return
        self.layer_slider.configure(from_=0, to=self.grid_shape[2]-1)
        self.layer_label.configure(text='0')

    def _on_layer_change(self, val):
        if self.grid_shape is None:
            return
        idx = int(float(val))
        self.layer_label.configure(text=str(idx))
        self._update_layers_plot()

    def _update_layers_plot(self):
        ax = self.ax_layer
        ax.cla()
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel('x (nm)')
        ax.set_ylabel('y (nm)')

        # Добавляем проверку на наличие всех необходимых параметров
        if (self.grid_nodes_nm is None or self.grid_origin_nm is None or
            self.grid_spacing_nm is None or self.grid_shape is None):
            self.canvas_layer.draw_idle()
            return

        try:
            rough = self.grid_spacing_nm[2]
            # Проверяем, что grid_shape имеет достаточно элементов
            if len(self.grid_shape) < 3:
                self.canvas_layer.draw_idle()
                return

            idx = int(float(self.layer_slider.get()))
            z_val = self.grid_origin_nm[2] + idx * rough

            # nodes in current layer (tolerance 0.5*rough)
            pts = self.grid_nodes_nm
            m = np.abs(pts[:,2]-z_val) <= 0.5*rough
            if np.any(m):
                sel = pts[m]
                ax.scatter(sel[:,0], sel[:,1], s=2, c='lightgray', label='nodes')
            # internal voxels in layer
            if self.internal_voxel_indices:
                p = np.array([self.voxels[i].center for i in self.internal_voxel_indices])
                mask = np.abs(p[:,2]-z_val) <= 0.5*rough
                if np.any(mask):
                    ax.scatter(p[mask,0], p[mask,1], s=10, c='dodgerblue', label='internal voxels')
            # boundary voxels in layer
            if self.boundary_voxel_indices:
                p = np.array([self.voxels[i].center for i in self.boundary_voxel_indices])
                mask = np.abs(p[:,2]-z_val) <= 0.5*rough
                if np.any(mask):
                    ax.scatter(p[mask,0], p[mask,1], s=14, c='crimson', label='boundary voxels')

            # Добавляем отображение траектории
            if self.trajectory and self.show_trajectory_var.get():
                # Получаем точки траектории в текущем слое
                layer_trajectory = []
                for i in self.trajectory:
                    v = self.voxels[i]
                    if abs(v.center[2] - z_val) <= 0.5 * rough:
                        layer_trajectory.append(v.center[:2])

                if layer_trajectory:
                    layer_trajectory = np.array(layer_trajectory)
                    # Рисуем линии траектории
                    for i in range(len(layer_trajectory) - 1):
                        ax.plot([layer_trajectory[i, 0], layer_trajectory[i+1, 0]],
                                [layer_trajectory[i, 1], layer_trajectory[i+1, 1]],
                                'g-', linewidth=1, alpha=0.7)

                    # Рисуем точки траектории
                    ax.scatter(layer_trajectory[:, 0], layer_trajectory[:, 1],
                              s=20, c='green', alpha=0.8, label='trajectory')

                handles, labels = ax.get_legend_handles_labels()
                if handles:
                    ax.legend(handles, labels, loc='upper right', fontsize=8)
        except Exception as e:
            print(f"Error in _update_layers_plot: {e}")
        finally:
            self.canvas_layer.draw_idle()


if __name__ == '__main__':
    app = VoxelizerApp()
    app.mainloop()
