import sys
import os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import re
import SimpleITK as sitk
import numpy as np
import pydicom
import math
import time
import scipy.ndimage
import nibabel as nib
import json
import traceback
import glob
import subprocess
import shutil

matplotlib.use('TkAgg')

from datetime import datetime
from skimage.draw import polygon
from scipy.ndimage import gaussian_filter
from pathlib import Path
from typing import Dict, Optional, Tuple, OrderedDict, Any
from matplotlib.axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QAbstractTableModel
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QColor, QIcon
from scipy.spatial import ConvexHull, Delaunay
import matplotlib.colors as mcolors
from matplotlib.widgets import Slider, Button, CheckButtons
from skimage.measure import find_contours

SMOOTH_SIGMA_MM: float = 0.75

def plot_combined_plot(CT_data, Dose_data, ROIs_data):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    plt.subplots_adjust(bottom=0.38, left=0.22)  # leave space for checkboxes

    views = ['axial', 'coronal', 'sagittal']
    get_ct = {
        'axial': lambda i: CT_data['Volume'][i, :, :],
        'coronal': lambda i: CT_data['Volume'][:, i, :],
        'sagittal': lambda i: CT_data['Volume'][:, :, i]
    }
    get_dose = {
        'axial': lambda i: Dose_data['Volume'][i, :, :],
        'coronal': lambda i: Dose_data['Volume'][:, i, :],
        'sagittal': lambda i: Dose_data['Volume'][:, :, i]
    }

    shapes = {
        'axial': CT_data['Volume'].shape[0],
        'coronal': CT_data['Volume'].shape[1],
        'sagittal': CT_data['Volume'].shape[2]
    }
    origins = {'axial': 'upper', 'coronal': 'lower', 'sagittal': 'lower'}

    imgs_ct, imgs_dose, sliders = [], [], []
    roi_patches_by_axis = [[] for _ in range(3)]
    roi_masks = [None, None, None]

    dose_global_max = float(np.max(Dose_data['Volume']))
    dose_min, dose_max = 0.0, dose_global_max

    cmap_ct = plt.cm.gray.copy()
    cmap_ct.set_bad(color='black')

    show_mode = {'mode': 'contour'}
    view_extents = {}
    selected_rois = set()

    # ROI mask colormap (still needed for mask display)
    unique_rois = list(ROIs_data.get('ROIs', {}).keys())
    color_list = [plt.cm.tab20.colors[i % len(plt.cm.tab20.colors)] for i in range(len(unique_rois))]
    cmap_roi = mcolors.ListedColormap([(0, 0, 0, 0)] + list(color_list))
    norm_roi = mcolors.BoundaryNorm(
        boundaries=np.arange(len(unique_rois) + 2) - 0.5,
        ncolors=len(unique_rois) + 1
    )

    # Precompute pixel -> mm extents
    for view in views:
        if view == 'axial':
            extent = [0, CT_data["Spacing"][2] * shapes['sagittal'],
                      0, CT_data["Spacing"][1] * shapes['coronal']]
        elif view == 'coronal':
            extent = [0, CT_data["Spacing"][2] * shapes['sagittal'],
                      0, CT_data["Spacing"][0] * shapes['axial']]
        else:
            extent = [0, CT_data["Spacing"][1] * shapes['coronal'],
                      0, CT_data["Spacing"][0] * shapes['axial']]
        view_extents[view] = extent

    def rgba_from_dose(dose_slice, min_val, max_val):
        norm_color = np.clip(dose_slice / max(dose_global_max, 1e-9), 0, 1)
        rgba = plt.cm.jet(norm_color)
        alpha = np.zeros_like(dose_slice, dtype=float)
        if max_val > min_val:
            in_range = (dose_slice >= min_val) & (dose_slice <= max_val)
            alpha[in_range] = (dose_slice[in_range] - min_val) / (max_val - min_val)
        rgba[..., 3] = alpha
        return rgba

    # Initial draw
    for i, view in enumerate(views):
        ax = axes[i]
        ct_data0 = get_ct[view](0)
        dose0 = get_dose[view](0)

        ct_img = ax.imshow(ct_data0, cmap=cmap_ct, vmin=900, vmax=1200,
                           origin=origins[view], extent=view_extents[view])
        dose_img = ax.imshow(rgba_from_dose(dose0, dose_min, dose_max),
                             origin=origins[view], extent=view_extents[view])

        ax.set_title(f"{view.capitalize()} Slice 0")
        ax.axis('off')
        imgs_ct.append(ct_img)
        imgs_dose.append(dose_img)

    # Dose colorbar
    sm = plt.cm.ScalarMappable(cmap='jet')
    sm.set_clim(0, dose_global_max)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes.ravel().tolist(), fraction=0.015, pad=0.02)
    cbar.set_label("Dose (Gy)")

    # Sliders
    slider_axes = [
        plt.axes([0.30, 0.25, 0.5, 0.02]),
        plt.axes([0.30, 0.20, 0.5, 0.02]),
        plt.axes([0.30, 0.15, 0.5, 0.02])
    ]
    dose_min_ax = plt.axes([0.30, 0.08, 0.5, 0.02])
    dose_max_ax = plt.axes([0.30, 0.03, 0.5, 0.02])
    button_ax = plt.axes([0.50, 0.30, 0.12, 0.04])

    dose_min_slider = Slider(dose_min_ax, 'Min Dose', 0.0, dose_global_max, valinit=dose_min, valstep=0.001)
    dose_max_slider = Slider(dose_max_ax, 'Max Dose', 0.0, dose_global_max, valinit=dose_max, valstep=0.001)
    toggle_button = Button(button_ax, 'Show Mask')

    # Checkbox for ROI selection
    checkbox_ax = plt.axes([0.02, 0.15, 0.15, 0.7])
    checkbox_labels = ["All"] + [ROIs_data['ROIs'][roi]['Name'] for roi in unique_rois]
    checkbox_states = [False] * len(checkbox_labels)
    checkbox = CheckButtons(checkbox_ax, labels=checkbox_labels, actives=checkbox_states)

    # Set label colors: black for "All", ROI colors for others
    checkbox.labels[0].set_color("black")
    for i, color in enumerate(color_list, start=1):
        checkbox.labels[i].set_color(color)

    def refresh_all(*_):
        min_val = dose_min_slider.val
        max_val = dose_max_slider.val

        for i, view in enumerate(views):
            idx = int(sliders[i].val)

            ct_slice = get_ct[view](idx)
            dose_slice = get_dose[view](idx)
            ct_slice = np.ma.masked_where(dose_slice <= 0, ct_slice)


            imgs_ct[i].set_data(ct_slice)
            imgs_dose[i].set_data(rgba_from_dose(dose_slice, min_val, max_val))

            for line in roi_patches_by_axis[i]:
                line.remove()
            roi_patches_by_axis[i].clear()
            if roi_masks[i] is not None:
                roi_masks[i].remove()
                roi_masks[i] = None

            if unique_rois:
                if show_mode['mode'] == 'mask':
                    combined = np.zeros_like(dose_slice, dtype=int)
                    roi_sizes = []
                    for j, roi_id in enumerate(unique_rois):
                        if j not in selected_rois:
                            continue
                        vol = ROIs_data['ROIs'][roi_id]['Volume']
                        if view == 'axial':
                            slice_mask = vol[idx, :, :]
                        elif view == 'coronal':
                            slice_mask = vol[:, idx, :]
                        else:
                            slice_mask = vol[:, :, idx]
                        roi_sizes.append((j, roi_id, np.count_nonzero(slice_mask)))

                    roi_sizes.sort(key=lambda x: x[2], reverse=True)

                    for j, roi_id, _size in roi_sizes:
                        vol = ROIs_data['ROIs'][roi_id]['Volume']
                        if view == 'axial':
                            slice_mask = vol[idx, :, :]
                        elif view == 'coronal':
                            slice_mask = vol[:, idx, :]
                        else:
                            slice_mask = vol[:, :, idx]
                        combined[slice_mask.astype(bool)] = j + 1

                    combined = np.ma.masked_where(dose_slice <= 0, combined)
                    roi_masks[i] = axes[i].imshow(
                        combined, cmap=cmap_roi, norm=norm_roi, alpha=0.5,
                        origin=origins[view], extent=view_extents[view]
                    )

                else:  # contour mode
                    if view == 'axial':
                        spacing_x = CT_data["Spacing"][2]
                        spacing_y = CT_data["Spacing"][1]
                    elif view == 'coronal':
                        spacing_x = CT_data["Spacing"][2]
                        spacing_y = CT_data["Spacing"][0]
                    else:
                        spacing_x = CT_data["Spacing"][1]
                        spacing_y = CT_data["Spacing"][0]

                    ext = view_extents[view]
                    for j, roi_id in enumerate(unique_rois):
                        if j not in selected_rois:
                            continue
                        vol = ROIs_data['ROIs'][roi_id]['Volume']
                        roi_slice = vol[idx, :, :] if view == 'axial' else \
                                    (vol[:, idx, :] if view == 'coronal' else vol[:, :, idx])

                        if not np.any(roi_slice):
                            continue

                        for contour in find_contours(roi_slice.astype(float), level=0.5):
                            y_mm = contour[:, 0] * spacing_y
                            x_mm = contour[:, 1] * spacing_x
                            if origins[view] == 'upper':
                                y_mm = ext[3] - y_mm
                            line, = axes[i].plot(x_mm, y_mm, color=color_list[j], linewidth=1.5)
                            roi_patches_by_axis[i].append(line)

            axes[i].set_title(f"{view.capitalize()} Slice {idx}")

        fig.canvas.draw_idle()

    def toggle_display(_event):
        if show_mode['mode'] == 'contour':
            show_mode['mode'] = 'mask'
            toggle_button.label.set_text('Show Contour')
        else:
            show_mode['mode'] = 'contour'
            toggle_button.label.set_text('Show Mask')
        refresh_all()

    updating_checkboxes = False
    def on_checkbox_clicked(label):
        nonlocal selected_rois, updating_checkboxes
        if updating_checkboxes:
            return

        if label == "All":
            updating_checkboxes = True
            if len(selected_rois) == len(unique_rois):
                selected_rois.clear()
                for i in range(1, len(checkbox_labels)):
                    if checkbox.get_status()[i]:
                        checkbox.set_active(i)
            else:
                selected_rois = set(range(len(unique_rois)))
                for i in range(1, len(checkbox_labels)):
                    if not checkbox.get_status()[i]:
                        checkbox.set_active(i)
            updating_checkboxes = False
        else:
            idx = checkbox_labels.index(label) - 1
            if idx in selected_rois:
                selected_rois.remove(idx)
            else:
                selected_rois.add(idx)

            updating_checkboxes = True
            all_checked = (len(selected_rois) == len(unique_rois))
            if checkbox.get_status()[0] != all_checked:
                checkbox.set_active(0)
            updating_checkboxes = False

        refresh_all()

    toggle_button.on_clicked(toggle_display)
    dose_min_slider.on_changed(refresh_all)
    dose_max_slider.on_changed(refresh_all)
    checkbox.on_clicked(on_checkbox_clicked)

    for i, view in enumerate(views):
        sld = Slider(slider_axes[i], f'{view.capitalize()} Slice', 0, shapes[view] - 1, valinit=0, valstep=1)
        sld.on_changed(lambda _val, i=i: refresh_all())
        sliders.append(sld)

    plt.show()

def load_nifti_volume(path):
    """
    Load a NIfTI file and return a dictionary with volume, spacing, and origin.
    """
    nii = nib.load(path)
    volume = nii.get_fdata().astype(np.float32)
    spacing = nii.header.get_zooms()[::-1]  # Z, Y, X
    origin = nii.affine[:3, 3][::-1]  # Z, Y, X
    return {
        "Volume": volume,
        "Spacing": np.array(spacing),
        "Position": np.array(origin)
    }

def load_preprocessed_volumes(files_path):
    """
    Load CT, Dose, and ROI volumes from .nii.gz files in the specified directory.

    Returns:
        CT_data, Dose_data, ROIs_data
    """

    # --- Load CT ---
    ct_path = os.path.join(files_path, "CT_volume.nii.gz")
    CT_data = load_nifti_volume(ct_path)

    # --- Load Dose ---
    dose_path = os.path.join(files_path, "Dose_volume.nii.gz")
    Dose_data = load_nifti_volume(dose_path)

    # --- Load ROI metadata ---
    roi_metadata_path = os.path.join(files_path, "ROIs", "roi_metadata.json")
    roi_metadata = {}
    if os.path.exists(roi_metadata_path):
        with open(roi_metadata_path, "r") as f:
            roi_metadata = json.load(f)

    # --- Load ROI volumes ---
    ROIs_data = {
        "ROIs": {},
        "Spacing": CT_data["Spacing"],
        "Position": CT_data["Position"]
    }

    roi_paths = sorted(glob.glob(os.path.join(files_path, "ROIs", "ROI_*_volume.nii.gz")))
    for path in roi_paths:
        filename = os.path.basename(path)
        parts = filename.split("_")
        if len(parts) < 3:
            continue  # Skip malformed files

        roi_number = parts[1]
        volume = load_nifti_volume(path)["Volume"]

        ROIs_data["ROIs"][roi_number] = {
            "Name": roi_metadata.get(roi_number, {}).get("Name", f"ROI_{roi_number}"),
            "Color": roi_metadata.get(roi_number, {}).get("Color", None),
            "Volume": volume.astype(bool)
        }

    return CT_data, Dose_data, ROIs_data

def save_volume_as_nifti(volume, spacing, output_path, affine_origin=(0, 0, 0)):
    """
    Save a 3D NumPy volume as a NIfTI file.

    Parameters:
    - volume (np.ndarray): The 3D volume (Z, Y, X).
    - spacing (tuple): Voxel spacing (Z, Y, X) in mm.
    - output_path (str): Where to save the .nii.gz file.
    - affine_origin (tuple): Origin of the image (Z, Y, X), defaults to (0,0,0).
    """
    affine = np.diag(list(spacing)[::-1] + [1])
    affine[:3, 3] = affine_origin[::-1]  # Put origin in correct position (X, Y, Z)

    nifti_img = nib.Nifti1Image(volume.astype(np.float32), affine)
    nib.save(nifti_img, output_path)

def save_volumes(CT_data, Dose_data, ROIs_data, output_path):
    # Save CT
    CT_output_path = os.path.join(output_path, "CT_volume.nii.gz")
    save_volume_as_nifti(volume=CT_data["Volume"], spacing=CT_data["Spacing"],
                         output_path=CT_output_path, affine_origin=CT_data["Position"])

    # Save Dose
    Dose_output_path = os.path.join(output_path, "Dose_volume.nii.gz")
    save_volume_as_nifti(volume=Dose_data["Volume"], spacing=Dose_data["Spacing"],
                         output_path=Dose_output_path, affine_origin=Dose_data["Position"])

    # Save ROIs
    ROIs_output_path = os.path.join(output_path, "ROIs/")
    os.makedirs(ROIs_output_path, exist_ok=True)

    roi_metadata = {}  # Dictionary to store ROI metadata

    for ROI_Number, ROI_entry in ROIs_data['ROIs'].items():
        # Save the volume
        ROI_volume_path = os.path.join(ROIs_output_path, f"ROI_{ROI_Number}_volume.nii.gz")
        save_volume_as_nifti(volume=ROI_entry["Volume"], spacing=ROIs_data["Spacing"],
                             output_path=ROI_volume_path, affine_origin=ROIs_data["Position"])

        # Store metadata
        roi_name = ROI_entry.get("Name")
        roi_color = ROI_entry.get("Color")

        # Convert color to standard Python list of ints
        if roi_color is not None:
            try:
                color_list = [int(c) for c in roi_color]
            except:
                color_list = None
        else:
            color_list = None

        roi_metadata[ROI_Number] = {
            "Name": str(roi_name) if roi_name is not None else f"ROI_{ROI_Number}",
            "Color": color_list
        }
    # Save ROI metadata as JSON
    metadata_path = os.path.join(ROIs_output_path, "roi_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(roi_metadata, f, indent=4)

def match_Dose_to_CT(Dose_data, CT_data, scales, offsets):
    """
    Aligns Dose images to the CT slice dimensions.

    Parameters:
    Dose_data: numpy.ndarray
        A dictionary containing the dose metadata.
    CT_data: dict
        A dictionary containing the CT metadata.
    scale_x: float
        Scaling factor along the x-axis.
    scale_y: float
        Scaling factor along the y-axis.
    offset_x: int
        Offset in pixels along the x-axis.
    offset_y: int
        Offset in pixels along the y-axis.

    Returns:
    numpy.ndarray
        A transformed 3D array of dose images aligned with the CT slice.
    """
    scale_z, scale_y, scale_x = scales
    offset_z, offset_y, offset_x = offsets

    # Build the 3D affine transformation matrix (rotation + scale)
    affine_matrix = np.array([
        [1 / scale_z, 0, 0],
        [0, 1 / scale_y, 0],
        [0, 0, 1 / scale_x]
    ])

    # Note: affine_transform maps from output space to input space
    offset = [-offset_z / scale_z, -offset_y / scale_y, -offset_x / scale_x]

    # Apply the affine transformation
    Dose_data["Volume"] = scipy.ndimage.affine_transform(
        Dose_data["Volume"],
        matrix=affine_matrix,
        offset=offset,
        output_shape=CT_data["Volume"].shape,
        order=1  # Linear interpolation
    )

def preprocess_Dose_to_CT(Dose_data, CT_data):
    """
    Transforms dose images to align with CT slices dimensions.

    Parameters:
    Dose_data: dict
        A dictionary containing dose metadata.
    CT_data: dict
        A dictionary containing CT metadata.

    Returns:
    dict
        The updated Dose_data dictionary with transformed images aligned to CT.
    """
    # Obtain Dose and CT Spacings and Positions to match between them.
    Dose_z_spacing, Dose_y_spacing, Dose_x_spacing = Dose_data["Spacing"]
    Dose_z_position, Dose_y_position, Dose_x_position = Dose_data["Position"]

    CT_z_spacing, CT_y_spacing, CT_x_spacing = CT_data["Spacing"]
    CT_z_position, CT_y_position, CT_x_position = CT_data["Position"]

    # Define scales
    scale_z = Dose_z_spacing / CT_z_spacing
    scale_y = Dose_y_spacing / CT_y_spacing
    scale_x = Dose_x_spacing / CT_x_spacing
    scales = [scale_z, scale_y, scale_x]

    # Define offsets
    offset_z = int((Dose_z_position - CT_z_position) / CT_z_spacing)
    offset_y = int((Dose_y_position - CT_y_position) / CT_y_spacing)
    offset_x = int((Dose_x_position - CT_x_position) / CT_x_spacing)
    offsets = [offset_z, offset_y, offset_x]

    # Match Dose images to CT
    match_Dose_to_CT(Dose_data, CT_data, scales, offsets)
    Dose_data["Spacing"] = CT_data["Spacing"]
    Dose_data["Position"] = CT_data["Position"]
    return Dose_data

def voxelize_convex_hull(points_voxel, volume_shape):
    hull = ConvexHull(points_voxel)
    delaunay = Delaunay(points_voxel[hull.vertices])
    zz, yy, xx = np.meshgrid(
        np.arange(volume_shape[0]),
        np.arange(volume_shape[1]),
        np.arange(volume_shape[2]),
        indexing='ij'
    )
    test_points = np.vstack([zz.ravel(), yy.ravel(), xx.ravel()]).T
    mask = delaunay.find_simplex(test_points) >= 0
    filled = np.zeros(volume_shape, dtype=bool)
    filled[zz.ravel()[mask], yy.ravel()[mask], xx.ravel()[mask]] = True
    return filled

def extract_ROIs_data(RS_data, CT_data):
    """
    Extracts ROIs and fills their 3D volume using convex hull of contour points.

    Args:
        RS_data (pydicom Dataset): RT Structure Set (RS) DICOM dataset.
        CT_data (dict): Dictionary containing CT volume and geometry.

    Returns:
        dict: ROI data with names, colors, and filled 3D binary volumes.
    """

    # Extract sequences
    ROIs_raw_data = RS_data.StructureSetROISequence
    contours_data = RS_data.ROIContourSequence

    # CT grid reference
    z_origin, y_origin, x_origin = CT_data["Position"]
    z_spacing, y_spacing, x_spacing = CT_data["Spacing"]
    volume_shape = CT_data['Volume'].shape

    # Initialize output
    ROIs_data = {'ROIs': {}}

    for ROI in ROIs_raw_data:
        ROI_Number = str(ROI.ROINumber)
        ROIs_data['ROIs'][ROI_Number] = {
            "Name": ROI.ROIName,
            "Color": None,
            "Volume": np.zeros(volume_shape, dtype=bool)
        }

    for contour in contours_data:
        ROI_Number = str(contour.ReferencedROINumber)
        ROI_entry = ROIs_data['ROIs'][ROI_Number]

        if ROI_entry["Color"] is None:
            ROI_entry["Color"] = getattr(contour, "ROIDisplayColor", None)

        voxel_coords_list = []

        if hasattr(contour, "ContourSequence") and contour.ContourSequence:
            for contour_seq in contour.ContourSequence:
                slice_uid = contour_seq.ContourImageSequence[0].ReferencedSOPInstanceUID
                z_index = CT_data['Slices'][slice_uid]['Z Index']

                points = np.array(contour_seq.ContourData).reshape(-1, 3)
                x_indices = np.round((points[:, 0] - x_origin) / x_spacing).astype(int)
                y_indices = np.round((points[:, 1] - y_origin) / y_spacing).astype(int)
                z_indices = np.full_like(x_indices, z_index)

                coords = np.stack([z_indices, y_indices, x_indices], axis=1)
                voxel_coords_list.append(coords)

            all_voxel_coords = np.vstack(voxel_coords_list)
            filled_volume = voxelize_convex_hull(all_voxel_coords, volume_shape)
            ROI_entry['Volume'][filled_volume] = True  # Set matching cells to True

    return ROIs_data

def extract_dose_data(RD_data):
    """
    Extracts relevant dose-related information from the RD (Radiotherapy Dose) dataset.

    Parameters:
    RD_data: pydicom Dataset
        The DICOM dataset containing radiotherapy dose information.

    Returns:
    dict
        A dictionary containing:
        - "Scaling Factor": The dose grid scaling factor.
        - "Position": The (x, y, z) position of the dose grid in patient coordinates.
        - "Spacing": The spacing between voxels in the dose grid (z, y, x) in mm.
        - "Volume": The 3D dose array in Gy units.
    """
    pos_x, pos_y, pos_z = RD_data.ImagePositionPatient
    spacing_x, spacing_y = RD_data.PixelSpacing

    offset_vector = RD_data.GridFrameOffsetVector
    spacing_z = offset_vector[1] - offset_vector[0] if len(offset_vector) > 1 else 0.0

    dose_volume = RD_data.pixel_array * RD_data.DoseGridScaling

    return {
        "Position": (float(pos_z), float(pos_y), float(pos_x)),
        "Spacing": (float(spacing_z), float(spacing_y), float(spacing_x)),  # matches (z, y, x) shape
        "Volume": dose_volume
    }

def read_dicom_rd_file(file_path):
    """Reads and loads a DICOM Radiation Dose (RD) file."""
    rd = pydicom.dcmread(file_path)
    if rd.Modality == 'RTDOSE':
        return rd
    else:
        raise ValueError("The provided file is not a Radiation Dose (RD) DICOM file.")

def read_dicom_rs_file(file_path):
    """Reads and loads a DICOM Radiation Therapy (RT) Structure Set (RS) file."""
    rs = pydicom.dcmread(file_path)
    if rs.Modality == 'RTSTRUCT':
        return rs
    else:
        raise ValueError("The provided file is not an RT Structure Set (RTSTRUCT) DICOM file.")


def read_dicom_rp_file(file_path):
    """Reads and loads a DICOM Radiation Therapy Plan (RP) file."""
    rp = pydicom.dcmread(file_path)
    if rp.Modality == 'RTPLAN':
        return rp
    else:
        raise ValueError("The provided file is not an RP (RTPLAN) DICOM file.")

def load_RT_data(files_path):
    """
    Load DICOM Radiation Therapy (RT) data from a given directory.

    This function loads three types of DICOM RT files:
    - RD (Radiation Dose) file: Contains radiation dose distribution data.
    - RS (Radiation Structure) file: Contains structure set data, defining target volumes and organs-at-risk.
    - RP (Radiation Plan) file: Contains treatment plan information.

    Parameters:
    ----------
    files_path : str
        The path to the directory containing the DICOM RT files.

    Returns:
    -------
    tuple
        A tuple containing three elements:
        - RD_data: Radiation dose data extracted from the RD file.
        - RS_data: Radiation structure data extracted from the RS file.
        - RP_data: Radiation plan data extracted from the RP file.

    Raises:
    ------
    FileNotFoundError:
        If any of the required files (RD, RS, RP) are not found in the directory.
    """

    # Load RD data
    RD_file_name = find_file_with_prefix(files_path, 'RD')
    if RD_file_name is None:
        raise FileNotFoundError("RD (Radiation Dose) file not found in the directory.")
    RD_data = read_dicom_rd_file(RD_file_name)  # load radiation dose information

    # Load RS data
    RS_file_name = find_file_with_prefix(files_path, 'RS')
    if RS_file_name is None:
        raise FileNotFoundError("RS (Radiation Structure) file not found in the directory.")
    RS_data = read_dicom_rs_file(RS_file_name)  # load radiation structure information

    # Load RP data
    RP_file_name = find_file_with_prefix(files_path, 'RP')
    if RP_file_name is None:
        raise FileNotFoundError("RP (Radiation Plan) file not found in the directory.")
    RP_data = read_dicom_rp_file(RP_file_name)  # load radiation plan information

    return RD_data, RS_data, RP_data

def create_CT_volume(CT_data):
    # 1. Sort CT slices
    CT_slices_data = [(slice_number, CT_data['Slices'][slice_number]["Position"][0]) for slice_number in
                      CT_data['Slices']]
    CT_slices_data.sort(key=lambda s: s[1])

    # 2. Extract CT volume shape
    z_len = len(CT_slices_data)
    y_len = list(CT_data['Slices'].values())[0]["Image"].shape[0]
    x_len = list(CT_data['Slices'].values())[0]["Image"].shape[1]

    # Insert CT slices
    CT_volume = np.zeros((z_len, y_len, x_len), dtype=np.float32)
    for i, (slice_number, _) in enumerate(CT_slices_data):
        CT_data['Slices'][slice_number]['Z Index'] = i
        CT_volume[i] = CT_data['Slices'][slice_number]['Image']

    return CT_volume

def load_CT_data(files_path):
    """
    Loads CT image data from DICOM files in a specified directory.

    Parameters:
    files_path: str
        The directory path containing CT DICOM files.

    Returns:
    dict
        A dictionary where each key is a CT slice identifier (SOPInstanceUID), and values are dictionaries containing:
        - "Position": The (x, y, z) position of the slice.
        - "Spacing": The pixel spacing values.
        - "Image": The pixel array representing the CT image.
    """

    CT_data = {}
    CT_data['Slices'] = {}

    # Extract z positions
    z_positions = []

    min_z = np.inf
    for file_name in os.listdir(files_path):
        if file_name.startswith('CT'):
            CT_slice_data = pydicom.dcmread(os.path.join(files_path, file_name))

            slice_number = CT_slice_data.SOPInstanceUID
            pos_x, pos_y, pos_z = CT_slice_data.ImagePositionPatient
            slice_position = (pos_z, pos_y, pos_x)
            spacing_x, spacing_y = CT_slice_data.PixelSpacing
            pixel_spacing = (spacing_y, spacing_x)
            pixel_array = CT_slice_data.pixel_array

            CT_data['Slices'][slice_number] = {"Position": slice_position,
                                               "Spacing": pixel_spacing,
                                               "Image": pixel_array}
            z_positions.append(float(slice_position[0]))

            # Set total CT position and spacing to be the same as the slice with lowest Z index
            if min_z > slice_position[0]:
                min_z = slice_position[0]
                CT_data['Position'] = slice_position
                CT_data['Spacing'] = pixel_spacing

    # Calculate spacing as average distance between z-values
    z_diffs = np.diff(sorted(z_positions))
    z_spacing = np.abs(np.mean(z_diffs))
    CT_data['Spacing'] = [z_spacing] + list(CT_data['Spacing'])

    # Create volume
    CT_data['Volume'] = create_CT_volume(CT_data)
    return CT_data

class PreprocessWorker(QThread):
    finished = pyqtSignal(dict)  # {ok: bool, msg: str, out_dir: str}
    log = pyqtSignal(str)

    def __init__(self, patient_data, outputs_dir, resample_type, new_size, new_spacing):
        super().__init__()
        self.patient_data = patient_data
        self.outputs_dir = outputs_dir
        self.resample_type = resample_type
        self.new_size = np.array(new_size) if new_size is not None else None
        self.new_spacing = np.array(new_spacing) if new_spacing is not None else None

    def run(self):
        try:
            t0 = time.time()

            self.log.emit("🔍 Checking if outputs already exist...")
            ready = all(os.path.exists(os.path.join(self.outputs_dir, f))
                        for f in ("CT_volume.nii.gz", "Dose_volume.nii.gz", "ROIs"))
            if ready:
                self.log.emit(f"✅ NIfTI already present in {self.outputs_dir}")
                self.finished.emit({
                    "ok": True,
                    "msg": f"NIfTI already present in {self.outputs_dir}",
                    "out_dir": self.outputs_dir
                })
                return

            # ------------------------
            # Load DICOM data
            # ------------------------
            self.log.emit("📥 Loading CT and RT data...")
            CT = load_CT_data(self.patient_data)
            RD, RS, _ = load_RT_data(self.patient_data)

            self.log.emit("💉 Extracting Dose data...")
            Dose = extract_dose_data(RD)

            self.log.emit("🧠 Extracting ROI structures...")
            ROIs = extract_ROIs_data(RS, CT)

            # ------------------------
            # Compute zoom factors
            # ------------------------
            if self.resample_type == "shape":
                zoom = self.new_size / CT["Volume"].shape
                self.log.emit(f"📏 Resampling by shape to {self.new_size.tolist()}")
            else:
                zoom = CT["Spacing"] / self.new_spacing
                self.log.emit(f"📏 Resampling by spacing to {self.new_spacing.tolist()}")

            # ------------------------
            # Resample CT
            # ------------------------
            self.log.emit("   🔄 Resampling CT volume...")
            CT["Volume"] = scipy.ndimage.zoom(CT["Volume"], zoom, order=1)
            CT["Spacing"] = CT["Spacing"] / zoom

            # ------------------------
            # Resample ROIs
            # ------------------------
            self.log.emit("   🔄 Aligning ROI structures to CT volume...")
            for r in ROIs["ROIs"].values():
                r["Volume"] = scipy.ndimage.zoom(r["Volume"], zoom, order=0)
            ROIs["Spacing"], ROIs["Position"] = CT["Spacing"], CT["Position"]

            # ------------------------
            # Resample Dose
            # ------------------------
            self.log.emit("   🔄 Aligning Dose volume to CT volume...")
            Dose = preprocess_Dose_to_CT(Dose, CT)

            # ------------------------
            # Save Outputs
            # ------------------------
            os.makedirs(self.outputs_dir, exist_ok=True)
            self.log.emit(f"💾 Saving volumes to: {self.outputs_dir}")
            save_volumes(CT, Dose, ROIs, self.outputs_dir)

            dt = time.time() - t0
            self.finished.emit({
                "ok": True,
                "msg": f"Preprocess finished in {dt / 60:.1f} min. Saved to {self.outputs_dir}",
                "out_dir": self.outputs_dir
            })
        except Exception:
            self.finished.emit({
                "ok": False,
                "msg": traceback.format_exc(),
                "out_dir": ""
            })

class PandasModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self._df = df.copy()

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, idx, role=Qt.DisplayRole):
        if role in (Qt.DisplayRole, Qt.ToolTipRole) and idx and idx.isValid():
            v = self._df.iat[idx.row(), idx.column()]
            if pd.isna(v):
                return ""
            return f"{v:.2f}" if isinstance(v, float) else str(v)

    def headerData(self, sec, ori, role=Qt.DisplayRole):
        if role != Qt.DisplayRole: return None
        return str(self._df.columns[sec]) if ori == Qt.Horizontal else str(self._df.index[sec])

def _dvh_cumsum_weighted(dose_values: np.ndarray,
                         weights: np.ndarray,
                         voxel_vol_cc: float,
                         step_gy: float = 0.1,
                         max_dose: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Weighted differential histogram (Gy) → cumulative volume (cc) DVH.
    Returns (dose_bins_left_edges, cumulative_volumes_cc).
    """
    if dose_values.size == 0:
        return np.empty(0, dtype=np.float32), np.empty(0, dtype=np.float32)

    end = max_dose if max_dose is not None else float(dose_values.max())
    last_edge = math.ceil(end / step_gy) * step_gy
    bins = np.arange(0.0, last_edge + step_gy, step_gy, dtype=np.float32)

    vol_hist, _ = np.histogram(dose_values, bins=bins,
                               weights=weights * float(voxel_vol_cc))
    cumvol = np.cumsum(vol_hist[::-1])[::-1]
    return bins[:-1], cumvol.astype(np.float32)

def dvh_table_abs(dose_values: np.ndarray,
                  weights: np.ndarray,
                  voxel_vol_cc: float,
                  step_gy: float = 0.1,
                  prescription: Optional[float] = None,
                  max_dose: Optional[float] = None) -> pd.DataFrame:
    """
    Build an absolute DVH DataFrame with columns:
      - Dose [Gy], Rel. Dose [%], Volume [cm³]
    Rel. dose is % of prescription if available; otherwise % of max curve dose.
    """
    d, v = _dvh_cumsum_weighted(dose_values, weights, voxel_vol_cc, step_gy, max_dose=max_dose)
    if d.size == 0:
        return pd.DataFrame(columns=["Dose [Gy]", "Rel. Dose [%]", "Volume [cm³]"])

    denom = float(prescription) if prescription else float(max(d[-1], 1e-12))
    rel = (100.0 * d / denom).astype(np.float32)

    return pd.DataFrame({
        "Dose [Gy]": d.astype(np.float32),
        "Rel. Dose [%]": rel,
        "Volume [cm³]": v.astype(np.float32),
    })

def compute_abs_dvhs(masks,
                     dose_arr,
                     voxel_vol_cc,
                     prescription,
                     spacing_mm,
                     log):
    """
    Compute absolute DVH tables (0.1 Gy bins) per ROI.
    """
    dvh_abs: Dict[str, pd.DataFrame] = {}
    global_max = float(dose_arr.max()) if dose_arr.size else 0.0

    for roi, mask in masks.items():
        dose_vals, weights = _sample_native_dose(mask, spacing_mm, dose_arr)
        df = dvh_table_abs(dose_vals, weights, voxel_vol_cc, 0.1, prescription, max_dose=global_max)
        dvh_abs[roi] = df
        log.emit("📈     Finished calculating DVH curve for ROI '{}'".format(roi))

    return dvh_abs

def extract_group1_metadata(RP_data, RD_data, patient_folder_path) -> Dict[str, Any]:
    """
    Return a dict with the nine “Group‑1” plan‑level metadata items:

        PatientID │ Session date │ PrescriptionDose[Gy] │ NumberofFractions
        DoseperFraction[Gy] │ PlanningSoftware │ PlanningTechnique
        DoseCalculation Algorithm │ DoseGridSize[mm]  (z,y,x)

    *The function is resilient to missing DICOM tags and non‑standard planners –
    any unavailable item is returned as None / 'Unknown…'.*
    """
    meta: Dict[str, Any] = {
        "Patient ID":               "UnknownID",
        "Session Date":             "UnknownDate",
        "Prescription Dose [Gy]":   None,
        "Number of Fractions":      None,
        "Dose per Fraction [Gy]":   None,
        "Planning Software":        None,
        "Planning Technique":       None,
        "Dose Calculation Algorithm": None,
        "Dose Grid Size [mm]":      None,
    }

    # ── 1) Patient‑ID & session date from the folder name ─────────────────
    folder = Path(patient_folder_path).name
    if folder:
        #   • Patient‑ID = everything before first “_”
        meta["Patient ID"] = folder.split("_")[0] or meta["Patient ID"]

        #   • Any 8‑digit block interpreted as date
        m = re.search(r"(\d{8})", folder)
        if m:
            raw = m.group(1)
            for fmt in ("%d%m%Y", "%Y%m%d"):
                try:
                    meta["Session Date"] = datetime.strptime(
                        raw, fmt).strftime("%d/%m/%Y")
                    break
                except ValueError:
                    continue
            else:
                meta["Session Date"] = raw          # unknown order

    # ── 2) Prescription, n‑fractions, dose/fraction from the RTPLAN ───────
    rx = _get_prescription(RP_data)                    # helper already in file :contentReference[oaicite:2]{index=2}
    if rx is not None:
        meta["Prescription Dose [Gy]"] = float(rx)

    for fg in getattr(RP_data, "FractionGroupSequence", []):
        n_frac = getattr(fg, "NumberOfFractionsPlanned", None)
        if n_frac:
            meta["Number of Fractions"] = int(n_frac)
            break

    if meta["Prescription Dose [Gy]"] and meta["Number of Fractions"]:
        meta["Dose per Fraction [Gy]"] = (
            meta["Prescription Dose [Gy]"] / meta["Number of Fractions"]
        )

    # ── 3) Planning software / technique / algorithm ──────────────────────
    sw = getattr(RP_data, "SoftwareVersions", None)
    meta["Planning Software"] = str(sw) if sw is not None else None

    beam = next(iter(getattr(RP_data, "BeamSequence", [])), None)
    if beam:
        meta["Planning Technique"] = getattr(beam, "BeamTechnique", None)
        meta["Dose Calculation Algorithm"] = getattr(
            beam, "DoseCalculationAlgorithm", None)

    # ── 4) Dose‑grid spacing from RTDOSE ───────────────────────────────────
    try:
        spacing_x, spacing_y = map(float, RD_data.PixelSpacing)
        gfv = RD_data.GridFrameOffsetVector
        spacing_z = float(gfv[1] - gfv[0]) if len(gfv) > 1 else float(
            getattr(RD_data, "SliceThickness", np.nan))
        meta["Dose Grid Size [mm]"] = (spacing_z, spacing_y, spacing_x)
    except Exception:
        pass

    return meta

def _weighted_percentile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    """Weighted percentile (linear interpolation on the CDF)."""
    sorter = np.argsort(values)
    v, w = values[sorter], weights[sorter]
    cdf = np.cumsum(w) / np.sum(w)
    return float(np.interp(q / 100.0, cdf, v))

def _weighted_mode(values: np.ndarray, weights: np.ndarray, bin_width: float = 0.1) -> float:
    """Weighted mode via histogram with guards for narrow/degenerate ranges."""
    if values.size == 0:
        return float("nan")
    if np.allclose(values.ptp(), 0):
        return float(values[0])
    v_min, v_max = float(values.min()), float(values.max())
    if v_max - v_min < bin_width:
        bins = np.array([v_min, v_max + bin_width], dtype=np.float32)
    else:
        bins = np.arange(v_min, v_max + bin_width, bin_width, dtype=np.float32)
    hist, edges = np.histogram(values, bins=bins, weights=weights)
    if hist.size == 0 or hist.max() == 0:
        return float(np.average(values, weights=weights if weights.sum() > 0 else None))
    idx = int(np.argmax(hist))
    return float((edges[idx] + edges[idx + 1]) / 2.0)

def _sample_native_dose(mask: np.ndarray,
                        spacing_mm: Tuple[float, float, float],
                        dose: np.ndarray,
                        smooth_sigma: float = SMOOTH_SIGMA_MM) -> Tuple[np.ndarray, np.ndarray]:
    """
    Return dose values and smoothed occupancy weights inside the binary `mask`.
    The smoothing produces fractional weights at edges (sub‑voxel interpolation).
    """
    if mask.shape != dose.shape:
        raise ValueError(f"Mask shape {mask.shape} must match dose shape {dose.shape}")
    if smooth_sigma > 0:
        sigma_vox = (smooth_sigma/spacing_mm[2], smooth_sigma/spacing_mm[1], smooth_sigma/spacing_mm[0])
        weight_mask = gaussian_filter(mask.astype(np.float32), sigma=sigma_vox)
    else:
        weight_mask = mask.astype(np.float32)

    inside = mask.astype(bool)
    return dose[inside], weight_mask[inside]

def compute_roi_metrics(masks: Dict[str, np.ndarray],
                        dose_arr: np.ndarray,
                        voxel_vol_cc: float,
                        prescription: Optional[float],
                        spacing_mm: Tuple[float, float, float],
                        smooth_sigma: float,
                        log) -> pd.DataFrame:
    """
    Compute per‑ROI dose/volume metrics and selected Vx (cc) for healthy brain.
    """
    rows = []
    hb_thrs = [5, 10, 12, 18, 20, 23, 24, 25, 27, 30]

    for roi, mask in masks.items():
        dose_vals, w = _sample_native_dose(mask, spacing_mm, dose_arr, smooth_sigma)
        if dose_vals.size == 0:
            continue

        vol_total = float(np.sum(w) * voxel_vol_cc)
        mean = float(np.average(dose_vals, weights=w))
        std = float(np.sqrt(np.average((dose_vals - mean) ** 2, weights=w)))
        median = _weighted_percentile(dose_vals, w, 50.0)

        d2 = _weighted_percentile(dose_vals, w, 98.0)   # high-dose tail
        d50 = median
        d98 = _weighted_percentile(dose_vals, w, 2.0)   # low-dose tail
        mode = _weighted_mode(dose_vals, w)

        hi = float(abs((d98 - d2) / prescription)) if prescription else float("nan")

        # Simple conformity index for PTVs (if name contains 'ptv')
        roi_is_ptv = ("ptv" in roi.lower())
        if prescription and roi_is_ptv:
            v_ptv_100 = float(np.sum(w[dose_vals >= prescription]) * voxel_vol_cc)
            v_ptv_80  = float(np.sum(w[dose_vals >= 0.8 * prescription]) * voxel_vol_cc)
            ci = (v_ptv_100 ** 2) / (v_ptv_80 * vol_total) if v_ptv_80 > 0 else float("nan")
        else:
            ci = float("nan")

        row = OrderedDict([
            ("ROI", roi),
            ("Volume_cc", vol_total),
            ("Min_Gy", float(dose_vals.min())),
            ("Max_Gy", float(dose_vals.max())),
            ("Mean_Gy", mean),
            ("Median_Gy", float(median)),
            ("Mode_Gy", float(mode)),
            ("Std_Gy", std),
            ("D2_Gy", float(d2)),
            ("D50_Gy", float(d50)),
            ("D98_Gy", float(d98)),
            ("HI", hi),
            ("CI", float(ci)),
        ])

        roi_clean = roi.strip().lower()
        if "brain" in roi_clean and "brainstem" not in roi_clean:
            for thr in hb_thrs:
                vx = float(np.sum(w[dose_vals >= thr]) * voxel_vol_cc)
                row[f"V{thr}_cc"] = vx

        rows.append(row)
        log.emit("📊     Finished calculating metrics for ROI '{}'".format(roi))

    return pd.DataFrame(rows)

def _get_prescription(rtplan: pydicom.dataset.FileDataset) -> Optional[float]:
    """
    Heuristically extract prescription dose (Gy) from RTPLAN.
    Returns None if not found.
    """
    # 1) DoseReferenceSequence (TARGET)
    try:
        for dr in getattr(rtplan, "DoseReferenceSequence", []):
            if str(getattr(dr, "DoseReferenceType", "")).upper() == "TARGET":
                for tag in ("TargetPrescriptionDose", "DeliveryMaximumDose",
                            "DeliveryWarningDose", "DeliveryUnit"):
                    if hasattr(dr, tag):
                        val = float(getattr(dr, tag))
                        if val > 0:
                            return round(val)
    except Exception:
        pass

    # 2) Common top-level fields
    for tag in ("DoseReferenceTreatmentMaxDose", "PrescriptionDescription"):
        try:
            val = float(getattr(rtplan, tag))
            if val > 0:
                return val
        except Exception:
            pass

    # 3) Fraction × number of fractions
    try:
        beams = getattr(rtplan, "BeamSequence", [])
        if beams:
            doses = []
            for b in beams:
                fracs = int(getattr(b, "NumberOfFractionsPlanned", 0) or 0)
                dose_per_frac = float(getattr(b, "FinalCumulativeMetersetWeight", 0.0) or 0.0)
                if fracs > 0 and dose_per_frac > 0:
                    doses.append(fracs * dose_per_frac)
            if doses:
                est = float(np.median(doses))
                if est > 0:
                    return est
    except Exception:
        pass

    return None

def build_roi_masks(rs: pydicom.dataset.FileDataset,
                    ct_img: sitk.Image,  log,
                    verbose: bool = True) -> Dict[str, np.ndarray]:
    """
    Rasterize 2D polygon contours from RTSTRUCT onto the CT grid.
    Returns dict: {roi_name -> mask[Z,Y,X] (uint8 in {0,1})}.
    Notes:
      - For each polyline we project to the nearest CT slice using the median Z‑index.
      - This ignores any cross‑slice interpolation; typical for planar slice contours.
    """
    size_x, size_y, size_z = ct_img.GetSize()     # (X, Y, Z) voxel counts
    masks: Dict[str, np.ndarray] = {}

    roi_contour_by_number = {}
    if hasattr(rs, "ROIContourSequence"):
        for rc in rs.ROIContourSequence:
            roi_contour_by_number[int(rc.ReferencedROINumber)] = rc

    for roi in getattr(rs, "StructureSetROISequence", []):
        num = int(roi.ROINumber)
        name = str(getattr(roi, "ROIName", f"ROI_{num}")).strip()

        rc = roi_contour_by_number.get(num, None)
        if rc is None or not getattr(rc, "ContourSequence", []):
            if verbose:
                print(f"⚠️  ROI '{name}' has no contours – skipped")
            continue

        m = np.zeros((size_z, size_y, size_x), np.uint8)
        for cs in rc.ContourSequence:
            pts = np.asarray(cs.ContourData, dtype=np.float64).reshape(-1, 3)
            if pts.size == 0:
                continue

            # Convert patient (x,y,z) to CT index (i,j,k) then split
            ijk = [ct_img.TransformPhysicalPointToIndex(tuple(p)) for p in pts]
            xs, ys, zs = map(np.array, zip(*ijk))

            # Round/clip XY; use median Z slice for the polygon
            xs = np.clip(np.round(xs).astype(int), 0, size_x - 1)
            ys = np.clip(np.round(ys).astype(int), 0, size_y - 1)
            z  = int(np.clip(np.round(np.median(zs)), 0, size_z - 1))

            rr, cc = polygon(ys, xs, (size_y, size_x))
            m[z, rr, cc] = 1

        if m.any():
            masks[name] = m
        elif verbose:
            print(f"⚠️  ROI '{name}' contours lay outside the CT – skipped")
        log.emit("🔬     Finished building mask for ROI '{}'".format(name))

    return masks

def find_file_with_prefix(folder_path, prefix):
    """Finds a file in the given folder with the specified prefix."""
    for file_name in os.listdir(folder_path):
        if file_name.startswith(prefix):
            return os.path.join(folder_path, file_name)
    return None

def resample_dose_to_ct(dose_ds: pydicom.dataset.FileDataset,
                        dose_arr: np.ndarray,
                        ct_img: sitk.Image) -> np.ndarray:
    """
    Wrap the raw dose array in a SimpleITK image with correct spacing/origin,
    then resample onto the CT grid with linear interpolation.
    Returns dose_on_ct as array[Z,Y,X] in Gy.
    """
    img = sitk.GetImageFromArray(dose_arr)  # [Z,Y,X]

    # DICOM PixelSpacing is [row_spacing (dy), col_spacing (dx)]
    dy, dx = map(float, dose_ds.PixelSpacing)
    # z spacing from GridFrameOffsetVector or fallback to SliceThickness
    if hasattr(dose_ds, "GridFrameOffsetVector") and len(dose_ds.GridFrameOffsetVector) > 1:
        dz = float(np.diff(dose_ds.GridFrameOffsetVector).mean())
    else:
        dz = float(getattr(dose_ds, "SliceThickness", 1.0))

    # IMPORTANT: SimpleITK expects spacing order (x, y, z)
    img.SetSpacing((dx, dy, dz))
    # Origin in patient space
    img.SetOrigin(tuple(map(float, dose_ds.ImagePositionPatient)))

    rf = sitk.ResampleImageFilter()
    rf.SetReferenceImage(ct_img)
    rf.SetInterpolator(sitk.sitkLinear)
    rf.SetDefaultPixelValue(0.0)
    out = rf.Execute(img)
    return sitk.GetArrayFromImage(out).astype(np.float32)  # [Z,Y,X]

def _find_dcm(folder: str, modality: str) -> str:
    """
    Return path to the first DICOM file in `folder` whose Modality equals `modality`.
    Scans only the immediate files in `folder` (not recursive).
    """
    for fn in os.listdir(folder):
        p = os.path.join(folder, fn)
        if not os.path.isfile(p):
            continue
        try:
            if pydicom.dcmread(p, stop_before_pixels=True).Modality == modality:
                return p
        except Exception:
            # Skip unreadable files
            pass
    raise FileNotFoundError(f"Could not find a DICOM with modality={modality!r} in {folder!r}")

def load_dose(folder: str) -> Tuple[pydicom.dataset.FileDataset, np.ndarray]:
    """
    Load RTDOSE from `folder`. Returns (pydicom_ds, dose_array[Z,Y,X] in Gy).
    """
    ds = pydicom.dcmread(_find_dcm(folder, "RTDOSE"))
    dose = ds.pixel_array * ds.DoseGridScaling
    # Some RTDOSE are 4D (time). Use first frame if so.
    if dose.ndim == 4:
        dose = dose[0]
    return ds, dose

def load_ct(folder: str) -> Tuple[sitk.Image, np.ndarray]:
    """
    Load a CT series under `folder` using SimpleITK.
    Returns (itk_image, array[Z,Y,X] in HU).
    """
    rdr = sitk.ImageSeriesReader()
    ids = rdr.GetGDCMSeriesIDs(folder) or []
    for sid in ids:
        fns = rdr.GetGDCMSeriesFileNames(folder, sid)
        if not fns:
            continue
        try:
            if pydicom.dcmread(fns[0], stop_before_pixels=True).Modality != "CT":
                continue
        except Exception:
            continue
        rdr.SetFileNames(fns)
        img = rdr.Execute()
        arr = sitk.GetArrayFromImage(img).astype(np.float32)  # [Z,Y,X]
        # Convert to HU if unsigned storage (common: 0..4095)
        if arr.min() >= 0:
            arr -= 1024.0
        return img, arr
    raise RuntimeError(f"No CT series found under {folder!r}")

class MetricsWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log = pyqtSignal(str)
    result = pyqtSignal(object)

    def __init__(self, patient_data):
        super().__init__()
        self.patient_data = patient_data

    def run(self):
        try:
            self.log.emit("📥 Starting metric extraction...")

            self.log.emit("🔄 Loading CT and Dose data...")
            ct_img, _ = load_ct(self.patient_data)
            self.log.emit("🔄   Finished Loading CT")
            ds_dose, dose_raw = load_dose(self.patient_data)
            self.log.emit("🔄   Finished Loading Dose data")

            self.log.emit("   ↳ Resampling Dose to CT grid...")
            dose_arr = resample_dose_to_ct(ds_dose, dose_raw, ct_img)

            self.log.emit("🔄 Reading RT Structure and Plan...")
            rs = pydicom.dcmread(find_file_with_prefix(self.patient_data, "RS"))
            rp = pydicom.dcmread(find_file_with_prefix(self.patient_data, "RP"))

            self.log.emit("🔬 Building ROI masks...")
            masks = build_roi_masks(rs, ct_img, self.log)

            self.log.emit("💊 Extracting prescription...")
            rx = _get_prescription(rp)

            sx, sy, sz = ct_img.GetSpacing()
            spacing = (sx, sy, sz)
            vv_cc = (sx * sy * sz) / 1000.0

            self.log.emit("📊 Computing ROI metrics...")

            roi_df = compute_roi_metrics(masks, dose_arr, vv_cc, rx, spacing, SMOOTH_SIGMA_MM, self.log).round(2)

            self.log.emit("📄 Extracting patient metadata...")
            meta_df = pd.DataFrame(
                extract_group1_metadata(rp, None, self.patient_data).items(),
                columns=["Field", "Value"]
            )

            self.log.emit("📈 Calculating DVH curves...")
            dvh_abs = compute_abs_dvhs(masks, dose_arr, vv_cc, rx, spacing_mm=spacing, log=self.log)

            result = {
                "ROI_DF": roi_df,
                "Meta_DF": meta_df,
                "DVH": dvh_abs,
                "Rx": rx
            }

            self.result.emit(result)
            self.finished.emit()
        except Exception as e:
            import traceback
            self.error.emit(traceback.format_exc())
            self.finished.emit()

class ProcessingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preprocessing in Progress")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        self.log_area = QPlainTextEdit(self)
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)

        self.close_button = QPushButton("Close", self)
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button)

    def write(self, message):
        self.log_area.appendPlainText(message.strip())

    def mark_done(self):
        self.progress_bar.setRange(0, 1)  # Set to determinate
        self.progress_bar.setValue(1)
        self.close_button.setEnabled(True)
        self.write("✅ Preprocessing complete.")

    def show_error(self, message):
        self.write(f"❌ Error: {message}")
        self.mark_done()

class NIfTISettingsDialog(QDialog):
    def __init__(self, default_output_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resample and Output Settings")
        self.setMinimumWidth(400)

        # ─── Widgets ──────────────────────────────────────────────
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Select resample type...", "shape", "spacing"])
        self.value_edit = QLineEdit()
        self.value_edit.setEnabled(False)  # Disabled initially

        self.output_edit = QLineEdit(default_output_dir)
        self.browse_btn = QPushButton("Browse...")

        # ─── Layout ────────────────────────────────────────────────
        form = QVBoxLayout()

        form.addWidget(QLabel("Resample Type:"))
        form.addWidget(self.type_combo)

        form.addWidget(QLabel("Resample Values:"))
        form.addWidget(self.value_edit)

        form.addWidget(QLabel("Output Folder:"))
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_edit)
        output_row.addWidget(self.browse_btn)
        form.addLayout(output_row)

        # ─── Buttons ──────────────────────────────────────────────
        button_row = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        button_row.addStretch()
        button_row.addWidget(self.ok_btn)
        button_row.addWidget(self.cancel_btn)
        form.addLayout(button_row)

        self.setLayout(form)

        # ─── Events ───────────────────────────────────────────────
        self.type_combo.currentTextChanged.connect(self._on_type_change)
        self.browse_btn.clicked.connect(self._browse_folder)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def _on_type_change(self, text):
        if text == "shape":
            self.value_edit.setEnabled(True)
            self.value_edit.setText("512,512,512")
        elif text == "spacing":
            self.value_edit.setEnabled(True)
            self.value_edit.setText("1.0,1.0,1.0")
        else:
            self.value_edit.setEnabled(False)
            self.value_edit.setText("")

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_edit.setText(folder)

    def get_values(self):
        return {
            "resample_type": self.type_combo.currentText(),
            "resample_value": self.value_edit.text(),
            "output_dir": self.output_edit.text()
        }

def parse_patient_metadata(name):
    """
    Parse metadata from patient folder name.
    Example format: 1575_SRS_LT occipital_02062021
    """
    pattern = r"(\d+)[ _]+([A-Z]+)(?:[ _]+([A-Z0-9]+))?(?:[ _]+([A-Za-z0-9 ]+))?[ _]+(\d{2})(\d{2})(\d{4})"
    match = re.match(pattern, name)

    if not match:
        return {"Patient ID": "Unknown", "Treatment": "Unknown", "Region": "Unknown", "Date": "Unknown"}

    pid, treatment, side, region, day, month, year = match.groups()
    date = f"{day}/{month}/{year}"
    return {
        "Patient ID": pid,
        "Treatment": treatment,
        "Region": f"{side} {region}" if side else region,
        "Date": date
    }

def plot_all_roi_dvhs(dvh_abs: Dict[str, pd.DataFrame],
                      prescription: Optional[float],
                      *,
                      x_mode: str = "dose",
                      y_mode: str = "volume",
                      ax: Optional[Axes] = None,
                      linewidth: float = 1.5) -> Axes:
    """
    Plot all DVHs with flexible axes.
      x_mode: {'dose','relative'}
      y_mode: {'volume','relative'}
    """
    if x_mode not in {"dose", "relative"}:
        raise ValueError("x_mode must be 'dose' or 'relative'")
    if y_mode not in {"volume", "relative"}:
        raise ValueError("y_mode must be 'volume' or 'relative'")
    if x_mode == "relative" and not prescription:
        raise ValueError("Relative x‑axis requires a prescription dose")

    if ax is None:
        _, ax = plt.subplots()

    for roi, df in dvh_abs.items():
        if df.empty:
            continue

        if x_mode == "dose":
            x = df["Dose [Gy]"].to_numpy()
            xlabel = "Dose [Gy]"
        else:
            x = df["Dose [Gy]"].to_numpy() / float(prescription) * 100.0
            xlabel = "Relative dose [% Rx]"

        if y_mode == "volume":
            y = df["Volume [cm³]"].to_numpy()
            ylabel = "Volume [cm³]"
        else:
            y0 = float(df["Volume [cm³]"].iloc[0]) if not df.empty else 1.0
            y = df["Volume [cm³]"].to_numpy() / max(y0, 1e-12) * 100.0
            ylabel = "Relative volume [%]"

        ax.plot(x, y, label=roi, linewidth=linewidth)

    ax.grid(True, which="both", linestyle="--", linewidth=0.4)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(loc="best", fontsize="small")
    ax.figure.tight_layout()
    return ax

class DVHPlotWidget(QWidget):
    """
    Composite widget that shows cumulative DVHs and lets the user
    choose which ROIs to overlay.  Each checklist entry now carries
    the same colour as its curve in the plot.
    """
    def __init__(self, dvh_abs: dict[str, "pd.DataFrame"] | None = None,
                 prescription: float | None = None,
                 parent=None):
        super().__init__(parent)
        self._dvh_abs = dvh_abs or {}
        self._prescription = prescription

        # colour bookkeeping ----------------------------------------------
        self._roi_colors: dict[str, str] = {}     # ROI name → "#rrggbb"
        self._mpl_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

        # ROI checklist ----------------------------------------------------
        self.roi_list = QListWidget()
        self.roi_list.setSelectionMode(QListWidget.NoSelection)
        self.roi_list.itemChanged.connect(self._redraw)

        # axis selectors ---------------------------------------------------
        self.x_selector = QComboBox();  self.x_selector.addItems(["dose", "relative"])
        self.y_selector = QComboBox();  self.y_selector.addItems(["volume", "relative"])
        self.x_selector.currentIndexChanged.connect(self._redraw)
        self.y_selector.currentIndexChanged.connect(self._redraw)

        # Matplotlib canvas ------------------------------------------------
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # layout -----------------------------------------------------------
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("X‑axis:")); ctrl.addWidget(self.x_selector)
        ctrl.addSpacing(12)
        ctrl.addWidget(QLabel("Y‑axis:")); ctrl.addWidget(self.y_selector)
        ctrl.addStretch()

        left = QVBoxLayout()
        left.addWidget(QLabel("ROIs to display:"))
        left.addWidget(self.roi_list)
        left.addLayout(ctrl)

        main = QHBoxLayout(self)
        main.addLayout(left, 0)
        main.addWidget(self.canvas, 1)

        # first fill (if data were supplied) ------------------------------
        self._populate_list()
        self._redraw()

    # =====================================================================
    def set_data(self, dvh_abs: dict[str, "pd.DataFrame"],
                 prescription: float | None):
        """Replace DVH dictionary and Rx dose, then refresh widget."""
        self._dvh_abs = dvh_abs
        self._prescription = prescription
        self._populate_list()
        self._redraw()

    def clear(self):
        self.figure.clear()
        self.canvas.draw()
        self.roi_list.clear()

    # =====================================================================
    # internals
    # =====================================================================
    def _make_color_icon(self, hex_color: str) -> QIcon:
        """Return a 12×12 pixmap filled with *hex_color*."""
        pix = QPixmap(12, 12)
        pix.fill(QColor(hex_color))
        return QIcon(pix)

    def _populate_list(self):
        """Populate ROI checklist with coloured bullets (all ticked)."""
        self.roi_list.blockSignals(True)
        self.roi_list.clear()
        self._roi_colors.clear()

        for idx, roi in enumerate(sorted(self._dvh_abs.keys())):
            # deterministic colour from the Matplotlib cycle
            color = self._mpl_cycle[idx % len(self._mpl_cycle)]
            self._roi_colors[roi] = color

            item = QListWidgetItem(self._make_color_icon(color), roi)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.roi_list.addItem(item)

        self.roi_list.blockSignals(False)

    def _selected_rois(self):
        return [
            self.roi_list.item(i).text()
            for i in range(self.roi_list.count())
            if self.roi_list.item(i).checkState() == Qt.Checked
        ]

    def _redraw(self):
        self.figure.clear()
        rois = self._selected_rois()
        if not self._dvh_abs or not rois:
            self.canvas.draw_idle()
            return

        ax = self.figure.add_subplot(111)

        # set colour cycle to match the order in *rois*
        ax.set_prop_cycle('color', [self._roi_colors[r] for r in rois])

        subset = {roi: self._dvh_abs[roi] for roi in rois}
        plot_all_roi_dvhs(
            subset,
            self._prescription,
            ax=ax,
            x_mode=self.x_selector.currentText(),
            y_mode=self.y_selector.currentText(),
        )
        self.canvas.draw_idle()


class ArnousUnifiedGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ARVOUS – Automatic Radiotherapy Visualization and Utility Output System")
        self.resize(1420, 860)

        # define output folders
        self.outputs_dir = os.path.join(os.getcwd(), "Outputs")
        os.makedirs(self.outputs_dir, exist_ok=True)

        # ── top bar
        self.btn_load = QPushButton("Load Patient Data")
        self.btn_metrics = QPushButton("Extract Metrics")
        self.btn_nifti = QPushButton("Create NIfTI Volumes")
        self.btn_vis = QPushButton("Show Visualization")
        for b in (self.btn_metrics, self.btn_nifti, self.btn_vis):
            b.setEnabled(False)

        self.btn_load.clicked.connect(self.load_patient_data)
        self.btn_metrics.clicked.connect(self.extract_metrics)
        self.btn_nifti.clicked.connect(self.create_nifti_volumes)
        self.btn_vis.clicked.connect(self.show_visualization)

        bar = QHBoxLayout()
        [bar.addWidget(w) for w in (self.btn_load, self.btn_metrics, self.btn_nifti, self.btn_vis)]
        bar.addStretch()

        # ── patient info display
        self.patient_info_label = QLabel()
        self.patient_info_label.setStyleSheet("font: 14px 'Courier New'; padding: 5px;")
        self.patient_info_label.setAlignment(Qt.AlignLeft)
        self.patient_info_label.setText("🧾 No patient selected yet.")

        # ── tables + DVH plot
        self.tbl_meta = QTableView()
        self.tbl_roi = QTableView()
        self._make_table_interactive(self.tbl_meta)
        self._make_table_interactive(self.tbl_roi)

        self.dvh_widget = DVHPlotWidget()

        split_tables = QSplitter(Qt.Horizontal)
        split_tables.addWidget(self.tbl_meta)
        split_tables.addWidget(self.tbl_roi)
        split_tables.setStretchFactor(0, 1)
        split_tables.setStretchFactor(1, 4)

        split_vert = QSplitter(Qt.Vertical)
        split_vert.addWidget(split_tables)
        split_vert.addWidget(self.dvh_widget)
        split_vert.setStretchFactor(0, 3)
        split_vert.setStretchFactor(1, 2)

        root = QVBoxLayout(self)
        root.addLayout(bar)
        root.addWidget(self.patient_info_label)
        root.addWidget(split_vert)

    # ────────────────────────── UI helpers ────────────────────────────────
    def clear_all_data(self):
        self.tbl_meta.setModel(None)
        self.tbl_roi.setModel(None)
        self.dvh_widget.clear()
        self.metric_data = None

    def _make_table_interactive(self, tbl: QTableView):
        hh = tbl.horizontalHeader()
        vh = tbl.verticalHeader()
        hh.setSectionsMovable(True)
        hh.setSectionsClickable(True)
        hh.setSectionResizeMode(QHeaderView.Interactive)
        hh.setStretchLastSection(False)
        vh.setSectionsMovable(True)
        vh.setSectionsClickable(True)
        vh.setSectionResizeMode(QHeaderView.Interactive)
        tbl.setSortingEnabled(True)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.ExtendedSelection)
        tbl.setAlternatingRowColors(True)

    # ══════════════════════════ Main actions ═════════════════════════════
    def load_patient_data(self):
        # Let user select patient data
        self.patient_data = QFileDialog.getExistingDirectory(self, "Select patient DICOM folder")
        if not self.patient_data:
            return
        self.patient_name = Path(self.patient_data).name

        # Parse and display patient metadata
        meta = parse_patient_metadata(self.patient_name)
        info_text = (
            f"📁 <b>Processing Patient Record</b><br>"
            f"   • <b>Patient ID:</b> {meta['Patient ID']}<br>"
            f"   • <b>Treatment Type:</b> {meta['Treatment']}<br>"
            f"   • <b>Targeted Region:</b> {meta['Region']}<br>"
            f"   • <b>Session Date:</b> {meta['Date']}<br>"
            f"🗂️  DICOM path: <i>{self.patient_data}</i>"
        )
        self.patient_info_label.setText(info_text)
        self.clear_all_data()
        self.btn_metrics.setEnabled(True)
        self.btn_nifti.setEnabled(True)

    def extract_metrics(self):
        # Open dialog to show extraction progress
        self.processing_dialog = ProcessingDialog(self)
        self.processing_dialog.setWindowTitle("Extracting Dosimetric and Volumetric Metrics…")
        self.processing_dialog.show()

        # Set up thread and worker
        self.metrics_thread = QThread()
        self.metrics_worker = MetricsWorker(self.patient_data)
        self.metrics_worker.moveToThread(self.metrics_thread)

        # Connect signals
        self.metrics_thread.started.connect(self.metrics_worker.run)
        self.metrics_worker.log.connect(self.processing_dialog.write)
        self.metrics_worker.error.connect(self.processing_dialog.show_error)

        def handle_result(result):
            self.metric_data = result
            self.tbl_meta.setModel(PandasModel(result["Meta_DF"]))
            self.tbl_meta.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            self.tbl_roi.setModel(PandasModel(result["ROI_DF"]))
            self.tbl_roi.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            self.dvh_widget.set_data(result["DVH"], result["Rx"])
            self.btn_metrics.setEnabled(False)

        self.metrics_worker.result.connect(handle_result)

        def cleanup():
            self.processing_dialog.mark_done()
            self.processing_dialog.close()
            self.metrics_thread.quit()
            self.metrics_thread.wait()
            self.metrics_worker.deleteLater()
            self.metrics_thread.deleteLater()

        # Start thread
        self.metrics_worker.finished.connect(cleanup)
        self.metrics_thread.start()

    def create_nifti_volumes(self):
        # Show combined dialog
        dialog = NIfTISettingsDialog(default_output_dir=self.patient_data, parent=self)
        if dialog.exec_() != QDialog.Accepted:
            return

        # Extract values
        settings = dialog.get_values()
        resample_type = settings["resample_type"]
        self.outputs_dir = os.path.join(settings["output_dir"], Path(self.patient_data).name, f"Resample by {settings['resample_type']}", settings["resample_value"])

        # Parse resample values
        try:
            if resample_type == "shape":
                new_size = tuple(map(int, settings["resample_value"].split(",")))
                new_spacing = None
            else:
                new_spacing = tuple(map(float, settings["resample_value"].split(",")))
                new_size = None
        except Exception:
            QMessageBox.critical(self, "Error", "Invalid resample values.")
            return

        # Show progress/log dialog
        self.processing_dialog = ProcessingDialog(self)
        self.processing_dialog.show()

        self.preprocess_thread = PreprocessWorker(
            patient_data=self.patient_data,
            outputs_dir=self.outputs_dir,
            resample_type=resample_type,
            new_size=new_size,
            new_spacing=new_spacing
        )
        self.preprocess_thread.log.connect(self.processing_dialog.write)

        def on_finish(res):
            self.processing_dialog.mark_done()
            self.processing_dialog.close()
            ok, msg, out_dir = res.get("ok", False), res.get("msg", ""), res.get("out_dir", "")
            if not ok:
                QMessageBox.critical(self, "Preprocess error", msg)
            else:
                self.btn_vis.setEnabled(True)

        self.preprocess_thread.finished.connect(on_finish)
        self.preprocess_thread.start()

    # ------------------------------------------------------------------
    def show_visualization(self):
        CT, Dose, ROIs = load_preprocessed_volumes(self.outputs_dir)
        plot_combined_plot(CT, Dose, ROIs)

    # ------------------------------------------------------------------
    def batch_process(self):
        # Adapted from your metrics UI unchanged logic, wrapped here
        parent_str = QFileDialog.getExistingDirectory(self, "Select a parent folder (contains patient/session folders)")
        if not parent_str:
            return
        parent = Path(parent_str)

        selected_dirs = self._choose_multiple_dirs_under_parent(parent)
        if not selected_dirs:
            return

        # Discover concrete session folders
        session_folders = []
        for p in selected_dirs:
            session_folders.extend(self._discover_session_folders(p))
        session_folders = sorted(set(session_folders), key=lambda x: (x.parent.name, x.name))
        if not session_folders:
            QMessageBox.warning(self, "Nothing to process", "No valid patient/session folders found.")
            return

        n_max = len(session_folders)
        n, ok = QInputDialog.getInt(self, "How many?",
                                    f"Found {n_max} session folders.\nHow many do you want to process (1–{n_max})?",
                                    value=n_max, min=1, max=n_max)
        if not ok:
            return
        to_process = session_folders[:n]

        # Output root: common parent → DVH_files
        try:
            common_root = Path(os.path.commonpath([str(p.parent) for p in to_process]))
        except Exception:
            common_root = parent
        dvh_out = common_root / "DVH_files"
        dvh_out.mkdir(parents=True, exist_ok=True)

        # Locate engine script
        aligned_script = (Path(__file__).parent / "aligned_metrics_full_sigmafix_calls.py").resolve()
        if not aligned_script.exists():
            QMessageBox.critical(self, "Missing script", f"Cannot find {aligned_script}")
            return

        prog = QProgressDialog("Preparing…", "Cancel", 0, len(to_process), self)
        prog.setWindowTitle("Batch Process")
        prog.setWindowModality(Qt.WindowModal)
        prog.setMinimumDuration(0)
        prog.setAutoClose(False)
        prog.setAutoReset(False)
        prog.show()

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        errors = []
        processed = 0
        for i, sess in enumerate(to_process, start=1):
            if prog.wasCanceled(): break
            prog.setLabelText(f"Processing {i}/{len(to_process)}:\n{sess}")
            prog.setValue(i - 1)
            QApplication.processEvents()

            # quick skip if no CT
            if not self._likely_has_ct(sess):
                errors.append((sess, "Skipped: no CT series detected"))
                prog.setValue(i)
                QApplication.processEvents()
                continue
            try:
                cmd = [sys.executable, str(aligned_script), str(sess)]
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False, env=env)
                stdout = proc.stdout.decode("utf-8", errors="replace") if proc.stdout else ""
                stderr = proc.stderr.decode("utf-8", errors="replace") if proc.stderr else ""
                if proc.returncode != 0:
                    errors.append((sess, f"Return code {proc.returncode}\n{stderr[-2000:]}"))
                    continue
                produced = sess / "abs_DVH_CTgrid.xlsx"
                if not produced.exists():
                    cands = list(sess.glob("*.xlsx"))
                    if cands:
                        produced = cands[0]
                    else:
                        errors.append((sess, "No Excel output found after processing"))
                        continue
                if sess.parent not in (common_root, parent):
                    out_name = f"{sess.parent.name}__{sess.name}_DVH.xlsx"
                else:
                    out_name = f"{sess.name}_DVH.xlsx"
                shutil.copyfile(str(produced), str(dvh_out / out_name))
                processed += 1
            except Exception as e:
                errors.append((sess, repr(e)))
            prog.setValue(i)
            QApplication.processEvents()
        prog.close()

        if errors:
            lines = [f"Processed: {processed}", f"Errors: {len(errors)}", "", "Details:"]
            for s, err in errors[:12]:
                lines.append(f"- {s}: {err}")
            if len(errors) > 12:
                lines.append(f"...and {len(errors) - 12} more.")
            QMessageBox.warning(self, "Batch completed with errors", "\n".join(lines))
        else:
            QMessageBox.information(self, "Batch completed", f"Processed: {processed}\nSaved in: {dvh_out}")

    # ── helpers copied from your metrics UI ─────────────────────────────
    def _choose_multiple_dirs_under_parent(self, parent: Path):
        dlg = QFileDialog(self, "Select patients/sessions (multi-select)")
        dlg.setDirectory(str(parent))
        dlg.setFileMode(QFileDialog.Directory)
        dlg.setOption(QFileDialog.DontUseNativeDialog, True)
        dlg.setOption(QFileDialog.ShowDirsOnly, True)
        for view in dlg.findChildren((QListView, QTreeView)):
            view.setSelectionMode(QAbstractItemView.MultiSelection)
        if dlg.exec_() != QFileDialog.Accepted:
            return []
        picks = [Path(p) for p in dlg.selectedFiles() if Path(p).is_dir()]
        picks = [p for p in picks if p.parent == parent]
        return picks

    def _likely_has_ct(self, folder: Path, max_files: int = 200) -> bool:
        try:
            dcm_files = [p for p in folder.rglob("*.dcm")]
            if not dcm_files:
                return False
            uid_ct = "1.2.840.10008.5.1.4.1.1.2"
            for f in dcm_files[:max_files]:
                try:
                    ds = pydicom.dcmread(str(f), stop_before_pixels=True, force=True)
                    if getattr(ds, "Modality", "").upper() == "CT":
                        return True
                    if str(getattr(ds, "SOPClassUID", "")) == uid_ct:
                        return True
                    if "ct" in str(getattr(ds, "SeriesDescription", "")).lower():
                        return True
                except Exception:
                    continue
        except Exception:
            return False
        return False

    def _discover_session_folders(self, root_path: Path):
        if self._contains_dicoms_nonrecursive(root_path):
            return [root_path]
        level1_dirs = [p for p in root_path.iterdir() if p.is_dir()]
        sessions = []
        for d in level1_dirs:
            if self._contains_dicoms_nonrecursive(d) or self._looks_like_session(d):
                sessions.append(d)
        if sessions:
            return sorted(set(sessions), key=lambda x: x.name)
        return []

    def _looks_like_session(self, folder: Path, max_checks: int = 200) -> bool:
        try:
            modalities = set()
            checked = 0
            for f in folder.rglob("*"):
                if not f.is_file():
                    continue
                checked += 1
                if f.suffix.lower() in {".dcm", ".dicom"}:
                    modalities.add("ANY")
                else:
                    try:
                        ds = pydicom.dcmread(str(f), stop_before_pixels=True, force=True)
                        mod = str(getattr(ds, "Modality", "")).upper()
                        if mod:
                            modalities.add(mod)
                        elif getattr(ds, "SOPClassUID", None):
                            modalities.add("ANY")
                    except Exception:
                        pass
                if {"CT", "RTDOSE", "RTPLAN", "RTSTRUCT"} & modalities or ("ANY" in modalities and checked >= 20):
                    return True
                if checked >= max_checks:
                    break
        except Exception:
            return False
        return False

    def _contains_dicoms_nonrecursive(self, folder: Path, max_checks: int = 200) -> bool:
        checked = 0
        for f in folder.iterdir():
            if not f.is_file():
                continue
            checked += 1
            if f.suffix.lower() in {".dcm", ".dicom"}:
                return True
            try:
                ds = pydicom.dcmread(str(f), stop_before_pixels=True, force=True)
                if getattr(ds, "SOPClassUID", None) or getattr(ds, "Modality", None):
                    return True
            except Exception:
                pass
            if checked >= max_checks:
                break
        return False



if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ArnousUnifiedGUI()
    gui.show()
    sys.exit(app.exec_())