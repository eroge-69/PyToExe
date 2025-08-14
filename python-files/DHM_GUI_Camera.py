import os
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg' if you have PyQt installed
import matplotlib.pyplot as plt
from skimage.draw import disk, rectangle
from tkinter import Tk, filedialog, Label, Entry, Button, StringVar, OptionMenu
from PIL import Image
import tkinter as tk
from matplotlib.widgets import RectangleSelector
from skimage.draw import line
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pypylon import pylon
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector

#fixed problem with functionss & variables assigment / now able to use run all many times without problems
#did some refactoring
#fixed roi selection by making all windows top level

#global variables initialization
root = tk.Tk()

#users imported images
images_dict = {}
reference = None

#variables to hold images for functions
spectrum_image = unwrapped_psi_image = roi_image = cleaned_roi_image = thickness_2d_image = thickness_3d_image = thickness_1d_image = None

vmin = vmax = None

#Ui buttons
check_spectrum_button = run_phase_button = select_roi_button = noise_reduction_button = thickness_2d_button = thickness_3d_button = thickness_1d_button = run_all_button = None
zoom_in_button = zoom_out_button = None
dropdown_var = reference_label_var = image_label_var = entry_var = None

dropdown_widget = None

#System parameters
pixel_size_var = magnification_var = delta_ri_var = dc_remove_var = filter_type_var = filter_size_var = type_var = None


#for roi selection
roi_coords = None
roi_selected_flag = False


list_of_windows = []

######################################################################################################################
#function for UI/UX
def show_figure_in_new_window(fig, title="Figure"):
    win = tk.Toplevel()
    win.title(title)
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


#function used to ensure order of operations by user / enabling program features only after images are loaded
def enable_phase_computation():
    global check_spectrum_button
    global run_phase_button
    global run_all_button


    if (len(images_dict.keys()) > 0) and reference is not None:

        check_spectrum_button.config(state='normal')
        run_phase_button.config(state='normal')
        run_all_button.config(state='normal')

#function used to ensure order of operations by user / enabling other program features only after phases is computed
def enable_rest():
    select_roi_button.config(state='normal')
    noise_reduction_button.config(state='normal')
    thickness_2d_button.config(state='normal')
    thickness_3d_button.config(state='normal')
    thickness_1d_button.config(state='normal')

######################################################################################################################
#Back-End

def load_image(dest, dropdown_var=None, dropdown_widget=None):
    file_paths = filedialog.askopenfilenames(
        title="Select Image(s)",
        filetypes=[
            ("Bitmap files", "*.bmp"),
            ("TIFF files", "*.tif"),
            ("All files", "*.*")
        ]
    )

    if not file_paths:
        print("No file(s) selected.")
        return

    try:
        if isinstance(dest, dict):
            # Handle multiple image loading into dictionary
            for file_path in file_paths:
                img = Image.open(file_path).convert("L")
                title = os.path.basename(file_path)
                dest[title] = np.array(img)

            # Update dropdown menu
            if dropdown_var and dropdown_widget:
                menu = dropdown_widget["menu"]
                menu.delete(0, "end")
                for item in dest:
                    menu.add_command(label=item, command=tk._setit(dropdown_var, item))
                dropdown_var.set(list(dest.keys())[0])  # Set first loaded image as selected
        else:
            # Handle single reference image
            img = Image.open(file_paths[0]).convert("L")
            title = os.path.basename(file_paths[0])
            img_array = np.array(img)

            global reference
            global reference_label_var
            reference = img_array
            reference_label_var.set(title)

        enable_phase_computation()

        global image_label_var
        print(image_label_var.get())
    except Exception as e:
        print("Image loading failed:", e)



def create_mask(shape, center, size, kind='square'):
    mask = np.zeros(shape, dtype=bool)
    if kind == 'square':
        top_left = (center[0] - size // 2, center[1] - size // 2)
        rr, cc = rectangle(start=top_left, extent=(size, size), shape=shape)
    elif kind == 'circle':
        rr, cc = disk(center, radius=size // 2, shape=shape)
    mask[rr, cc] = True
    return mask

def Fast_Unwrap(Fx, Fy, phase1):
    X, Y = np.meshgrid(Fx, Fy)
    K = X**2 + Y**2 + np.finfo(float).eps
    K = np.fft.fftshift(K)
    estimated_psi = np.fft.ifftn(
        np.fft.fftn(
            (np.cos(phase1) * np.fft.ifftn(K * np.fft.fftn(np.sin(phase1)))) -
            (np.sin(phase1) * np.fft.ifftn(K * np.fft.fftn(np.cos(phase1))))
        ) / K
    )
    Q = np.round((np.real(estimated_psi) - phase1) / (2 * np.pi))
    return phase1 + 2 * np.pi * Q

def FFT_calc(A):
    A = A.astype(float)
    return np.fft.fftshift(np.fft.fft2(A))

def check_spectrum(calledFromFunction=False):
    global mask_bool, shift_y, shift_x, obj_image, image_label_var, dc_remove_var, filter_type_var, filter_size_var
    global images_dict

    A1 = images_dict.get(image_label_var.get())

    #added error handling
    if type(A1) == np.ndarray:
        Ny, Nx = A1.shape
        A1_shiftft = FFT_calc(A1)

        center_y, center_x = Ny // 2, Nx // 2
        temp = np.abs(A1_shiftft.copy())
        dc_out = int(dc_remove_var.get())
        filter_type = filter_type_var.get()
        filter_size = int(filter_size_var.get())

        temp[center_y-dc_out:center_y+dc_out, center_x-dc_out:center_x+dc_out] = 0
        max_y, max_x = np.unravel_index(np.argmax(temp), temp.shape)
        mask_bool = create_mask((Ny, Nx), (max_y, max_x), filter_size, kind=filter_type)
        spectrum_global = np.log(1 + np.abs(A1_shiftft))
        if not calledFromFunction:
            fig, ax = plt.subplots()
            ax.imshow(np.log(1 + np.abs(A1_shiftft)), cmap='gray')
            ax.contour(mask_bool, colors='red', linewidths=1)
            ax.set_title('Filter and Position')
            ax.axis('off')
            fig.tight_layout()

            show_figure_in_new_window(fig, title="Filter and Position")

            filt_spec = A1_shiftft * mask_bool
            cy, cx = np.array(mask_bool.shape) // 2
            shift_y = cy - max_y
            shift_x = cx - max_x
            filt_spec = np.roll(np.roll(filt_spec, shift_y, axis=0), shift_x, axis=1)
            obj_image = np.fft.ifft2(filt_spec)
        else:

            return(A1_shiftft, mask_bool, max_y, max_x)



def run_phase_difference(calledFromFunction=False):
    global unwrapped_psi_image, wavelength_var, pixel_size_var, magnification_var, delta_ri_var, dc_remove_var, filter_type_var, filter_size_var, image_label_var
    global images_dict, reference
    global vmin, vmax

    lambda_ = float(wavelength_var.get())
    cam_pix_size = float(pixel_size_var.get())
    magnification = float(magnification_var.get())
    delta_RI = float(delta_ri_var.get())
    dc_out = int(dc_remove_var.get())
    filter_type = filter_type_var.get()
    filter_size = int(filter_size_var.get())

    A1 = images_dict.get(image_label_var.get())
    print(np.mean(A1))

    Ny, Nx = A1.shape
    A1_shiftft = FFT_calc(A1)

    center_y, center_x = Ny // 2, Nx // 2
    temp = np.abs(A1_shiftft.copy())
    temp[center_y - dc_out:center_y + dc_out, center_x - dc_out:center_x + dc_out] = 0
    max_y, max_x = np.unravel_index(np.argmax(temp), temp.shape)
    mask_bool = create_mask((Ny, Nx), (max_y, max_x), filter_size, kind=filter_type)

    filt_spec = A1_shiftft * mask_bool
    cy, cx = np.array(mask_bool.shape) // 2
    shift_y = cy - max_y
    shift_x = cx - max_x
    filt_spec = np.roll(np.roll(filt_spec, shift_y, axis=0), shift_x, axis=1)
    obj_image = np.fft.ifft2(filt_spec)

    A2 = reference
    print(np.mean(A2))
    A2_shiftft = FFT_calc(A2)
    ref_filt_spec = A2_shiftft * mask_bool
    ref_filt_spec = np.roll(np.roll(ref_filt_spec, shift_y, axis=0), shift_x, axis=1)
    ref_image = np.fft.ifft2(ref_filt_spec)

    o1 = obj_image / ref_image
    phase1 = np.angle(o1)
    phase1[phase1 < 0] += 2 * np.pi

    obj_img = np.fft.fft2(np.fft.fftshift(filt_spec))
    int_obj = np.abs(obj_img) ** 2
    int_obj = (int_obj - np.min(int_obj)) / np.max(int_obj)

    Fs_x = 1 / cam_pix_size
    Fs_y = 1 / cam_pix_size
    dFx = Fs_x / Nx
    dFy = Fs_y / Ny
    Fx = np.linspace(-Fs_x / 2, Fs_x / 2 - dFx, Nx)
    Fy = np.linspace(-Fs_y / 2, Fs_y / 2 - dFy, Ny)

    unwrapped_psi = Fast_Unwrap(Fx, Fy, phase1)
    unwrapped_psi -= np.min(unwrapped_psi)

    mean = np.mean(unwrapped_psi)

    psi_inverted = 2 * mean - unwrapped_psi

    clean_psi = np.copy(unwrapped_psi)
    clean_psi[unwrapped_psi < mean] = mean

    clean_psi_inverted = np.copy(psi_inverted)
    clean_psi_inverted[psi_inverted < mean] = mean

    combined_clean = np.maximum(clean_psi, clean_psi_inverted)

    vmin = min(np.min(unwrapped_psi), np.min(psi_inverted), np.min(combined_clean))
    vmax = max(np.max(unwrapped_psi), np.max(psi_inverted), np.max(combined_clean))

    if not calledFromFunction:
        vmin, vmax = np.min(unwrapped_psi), np.max(unwrapped_psi)

        fig, ax = plt.subplots(figsize=(8, 6))

        if type_var.get() == "1 Beam":
            im = ax.imshow(combined_clean, cmap='jet', vmin=vmin, vmax=vmax)
            ax.set_title('Combined Unwrapped Phase')
            ax.axis('off')
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            unwrapped_psi = combined_clean
        else:
            im = ax.imshow(unwrapped_psi, cmap='jet')
            ax.set_title('Unwrapped Phase')
            ax.axis('off')
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

        unwrapped_psi_image = unwrapped_psi
        fig.tight_layout()

        show_figure_in_new_window(fig, title="Phase Visualization")
        enable_rest()

    else:
        if type_var.get() == "1 Beam":
            unwrapped_psi = combined_clean
        unwrapped_psi_image = unwrapped_psi
        return unwrapped_psi




def onselect(eclick, erelease):
    global roi_coords, roi_selected_flag
    x1, y1 = int(eclick.xdata), int(eclick.ydata)
    x2, y2 = int(erelease.xdata), int(erelease.ydata)
    roi_coords = (min(y1, y2), max(y1, y2), min(x1, x2), max(x1, x2))
    roi_selected_flag = True
    plt.close()

def select_roi(calledFromFunction=False):
    global roi_coords, roi_selected_flag, roi, unwrapped_psi_image

    roi_coords = None
    roi_selected_flag = False
    plt.close('all')

    fig, ax = plt.subplots()
    ax.imshow(unwrapped_psi_image, cmap='jet')
    ax.set_title("Draw ROI: Click-drag-release")

    selector = RectangleSelector(
        ax, onselect,
        useblit=True,
        interactive=True,
        button=[1],
        minspanx=5,
        minspany=5,
        props=dict(facecolor='none', edgecolor='red', linestyle='--', linewidth=2)
    )

    plt.show(block=True)

    if not roi_selected_flag or roi_coords is None:
        print("ROI selection not done.")
        return

    r1, r2, c1, c2 = roi_coords
    roi = unwrapped_psi_image[r1:r2, c1:c2]
    roi_global = roi
    if not calledFromFunction:
        fig, ax = plt.subplots()
        im = ax.imshow(roi, cmap='jet')
        ax.set_title("Selected ROI")
        ax.axis('off')
        fig.colorbar(im, ax=ax)
        fig.tight_layout()

        show_figure_in_new_window(fig, title="Selected ROI")

    else:
        return roi




reduce_noise_flag = False
def reduce_noise(calledFromFunction=False):
    global noise_red_phase, reduce_noise_flag
    reduce_noise_flag = True
    th = float(noise_th.get())

    if roi_selected_flag:
        in_phase = roi.copy()
    else:
        in_phase = unwrapped_psi_image.copy()
    noise_red_phase = in_phase.copy()
    noise_red_phase[noise_red_phase<th*np.mean(noise_red_phase)] = th*np.mean(noise_red_phase)

    cam_pix_size = float(pixel_size_var.get())
    magnification = float(magnification_var.get())

    rows2, cols2 = noise_red_phase.shape
    delta_x = np.arange(1, cols2 + 1) * cam_pix_size / magnification
    delta_y = np.arange(1, rows2 + 1) * cam_pix_size / magnification


    if(calledFromFunction is False):

        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(noise_red_phase, extent=(delta_x.min(), delta_x.max(), delta_y.min(), delta_y.max()), cmap='jet')
        ax.set_title('noise reduced phase', fontsize=16, fontname='Times New Roman')
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('(μm)', fontsize=20)
        ax.axis('image')
        ax.tick_params(labelsize=20)
        ax.set_xlabel('x (μm)', fontsize=20, fontname='Times New Roman')
        ax.set_ylabel('y (μm)', fontsize=20, fontname='Times New Roman')

        show_figure_in_new_window(fig, title="Noise Reduced Phase")
    else:
        return noise_red_phase, delta_x, delta_y


def compute_2d_thickness(calledFromFunction=False):
    if roi_selected_flag and (not reduce_noise_flag):
        in_phase = roi.copy()
    elif (not roi_selected_flag) and (not reduce_noise_flag):
        in_phase = unwrapped_psi_image.copy()
    else:
        in_phase = noise_red_phase

    lambda_ = float(wavelength_var.get())
    cam_pix_size = float(pixel_size_var.get())
    magnification = float(magnification_var.get())
    delta_RI = float(delta_ri_var.get())

    rows2, cols2 = in_phase.shape
    delta_x = np.arange(1, cols2 + 1) * cam_pix_size / magnification
    delta_y = np.arange(1, rows2 + 1) * cam_pix_size / magnification

    thickness = in_phase * lambda_ / (2 * np.pi * delta_RI)
    thickness -= np.min(thickness)

    if(calledFromFunction):
        return thickness
    else:
        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(thickness, extent=(delta_x.min(), delta_x.max(), delta_y.min(), delta_y.max()), cmap='jet')
        ax.set_title('Thickness 2D Profile', fontsize=16, fontname='Times New Roman')
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('(μm)', fontsize=20)
        ax.axis('image')
        ax.tick_params(labelsize=20)
        ax.set_xlabel('x (μm)', fontsize=20, fontname='Times New Roman')
        ax.set_ylabel('y (μm)', fontsize=20, fontname='Times New Roman')

        # Assuming you have a function like this to show in a new window
        show_figure_in_new_window(fig, title="Thickness 2D Profile")

        thickness_2d = thickness
    return thickness


def compute_3d_thickness(calledFromFunction=False):

    thickness_3d = compute_2d_thickness(True)
    thickness_3d -= np.min(thickness_3d)

    cam_pix_size = float(pixel_size_var.get())
    magnification = float(magnification_var.get())
    pixel_size_micron = cam_pix_size / magnification

    rows2, cols2 = thickness_3d.shape
    delta_x = np.arange(0, cols2) * cam_pix_size / magnification
    delta_y = np.arange(0, rows2) * cam_pix_size / magnification
    X, Y = np.meshgrid(delta_x, delta_y)

    if(calledFromFunction is False):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(
            X, Y, thickness_3d,
            cmap='jet',
            linewidth=0,
            antialiased=True,
            shade=True
        )

        ax.set_title('Thickness (3D rendering)', fontsize=16, fontname='Times New Roman')
        ax.set_xlabel('x (μm)', fontsize=14, fontname='Times New Roman')
        ax.set_ylabel('y (μm)', fontsize=14, fontname='Times New Roman')
        ax.set_zlabel('Thickness (μm)', fontsize=14, fontname='Times New Roman')

        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='(μm)')

        # Use your custom function to open figure in new window
        show_figure_in_new_window(fig, title="Thickness 3D Profile")
    else:
        return (X,Y,thickness_3d)


def compute_1d_thickness(calledFromFunction=False):

    thickness_1d = compute_2d_thickness(True)
    thickness_1d = thickness_1d - thickness_1d.min()

    cam_pix_size = float(pixel_size_var.get())
    magnification = float(magnification_var.get())
    pixel_size_micron = cam_pix_size / magnification

    fig, ax = plt.subplots()
    ax.imshow(thickness_1d, cmap='jet')
    ax.set_title("Click two points to extract 1D profile", fontsize=14)
    pts = plt.ginput(2)

    if len(pts) != 2:
        plt.close(fig)
        messagebox.showerror("Error", "Please select exactly two points.")
        return

    (x1, y1), (x2, y2) = pts
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    rr, cc = line(y1, x1, y2, x2)

    rr = np.clip(rr, 0, thickness_1d.shape[0] - 1)
    cc = np.clip(cc, 0, thickness_1d.shape[1] - 1)

    ax.plot([x1, x2], [y1, y2], 'w-', linewidth=2)
    ax.set_title("Selected Line for 1D Profile", fontsize=14)
    plt.close( )
    thickness_values = thickness_1d[rr, cc]

    distances = np.linspace(0, len(thickness_values) * pixel_size_micron, len(thickness_values))

    if not calledFromFunction:
        fig, ax = plt.subplots()
        ax.plot(distances, thickness_values, 'b-', linewidth=2)
        ax.set_xlabel("Position (μm)", fontsize=16, fontname='Times New Roman')
        ax.set_ylabel("Thickness (μm)", fontsize=16, fontname='Times New Roman')
        ax.set_title("1D Thickness Profile", fontsize=16, fontname='Times New Roman')
        ax.grid(True)
        ax.tick_params(labelsize=14)
        fig.tight_layout()

        show_figure_in_new_window(fig, title="1D Thickness Profile")
    else:
        return (distances, thickness_values)
def run_all():
    # Add FFT
    # Fix 1D problem


    # Data computations
    image = images_dict.get(image_label_var.get())
    A1_shiftft, mask_bool, max_y, max_x = check_spectrum(True)
    unwrapped_psi_image = run_phase_difference(True)
    roi = select_roi(True)
    noise_red_phase, delta_x, delta_y = reduce_noise(True)
    X, Y, thickness_3d = compute_3d_thickness(True)
    distances, thickness_values = compute_1d_thickness(True)

    # Prepare filtered spectrum image
    filt_spec = A1_shiftft * mask_bool
    cy, cx = np.array(mask_bool.shape) // 2
    shift_y = cy - max_y
    shift_x = cx - max_x
    filt_spec = np.roll(np.roll(filt_spec, shift_y, axis=0), shift_x, axis=1)
    obj_image = np.fft.ifft2(filt_spec)
    spectrum_display = np.log(1 + np.abs(A1_shiftft))  # For FFT visualization

    # Set up figure
    fig, axs = plt.subplots(3, 2, figsize=(16, 18))
    fig.suptitle("DHM Output Overview", fontsize=22)
    axs = axs.ravel()  # Flatten the 2D array of axes for easier indexing

    # 1. Original Image
    im0 = axs[0].imshow(image, cmap='gray')
    axs[0].set_title('Original Image')
    axs[0].axis('off')
    axs[0].set_aspect('equal')
    fig.colorbar(im0, ax=axs[0], fraction=0.046)

    # 2. FFT Spectrum + Mask
    im1 = axs[1].imshow(spectrum_display, cmap='gray')
    axs[1].contour(mask_bool, colors='red', linewidths=1)
    axs[1].set_title('Filter and Position')
    axs[1].axis('off')
    axs[1].set_aspect('equal')
    fig.colorbar(im1, ax=axs[1], fraction=0.046)

    # 3. Unwrapped Phase
    im2 = axs[2].imshow(unwrapped_psi_image, cmap='jet')
    axs[2].set_title('Unwrapped Phase')
    axs[2].axis('off')
    axs[2].set_aspect('equal')
    fig.colorbar(im2, ax=axs[2], fraction=0.046)

    # 4. ROI
    im3 = axs[3].imshow(roi, cmap='jet')
    axs[3].set_title("Selected ROI")
    axs[3].axis('off')
    axs[3].set_aspect('equal')
    fig.colorbar(im3, ax=axs[3], fraction=0.046)

    # 5. 1D Thickness Profile
    axs[4].plot(distances, thickness_values, 'b-', linewidth=2)
    axs[4].set_title("1D Thickness Profile")
    axs[4].set_xlabel("Position (μm)")
    axs[4].set_ylabel("Thickness (μm)")
    axs[4].grid(True)
    axs[4].set_aspect('auto')

    # 6. Noise-Reduced Phase
    im5 = axs[5].imshow(noise_red_phase, extent=(delta_x.min(), delta_x.max(), delta_y.min(), delta_y.max()), cmap='jet')
    axs[5].set_title('Noise Reduced Phase', fontsize=16, fontname='Times New Roman')
    axs[5].set_xlabel('x (μm)', fontsize=16, fontname='Times New Roman')
    axs[5].set_ylabel('y (μm)', fontsize=16, fontname='Times New Roman')
    axs[5].tick_params(labelsize=12)
    axs[5].set_aspect('equal')
    fig.colorbar(im5, ax=axs[5], fraction=0.046).set_label('(μm)', fontsize=16)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    enable_phase_computation()
    enable_rest()
    plt.show()


def open_camera_window():
    new_win = tk.Toplevel(root)
    new_win.title("Camera View")
    new_win.geometry("960x600")

    top_bar = tk.Frame(new_win, padx=10, pady=5)
    top_bar.pack(fill='x')

    capture_btn = tk.Button(top_bar, text="Capture", state='disabled')
    capture_btn.pack(side='left', padx=5)

    set_reference_btn = tk.Button(top_bar, text="Set as Reference", state='disabled')
    set_reference_btn.pack(side='left', padx=5)

    add_image_btn = tk.Button(top_bar, text="Add as Image", state='disabled')
    add_image_btn.pack(side='left', padx=5)

    tk.Label(top_bar, text="Exposure (µs):").pack(side='left')
    exposure_var = tk.StringVar(value="150")
    exposure_entry = tk.Entry(top_bar, textvariable=exposure_var, width=10)
    exposure_entry.pack(side='left', padx=5)

    canvas = tk.Canvas(new_win, width=960, height=540)
    canvas.pack()

    upButton = tk.Button(top_bar, text="↑ Up", width=10, command=None)
    upButton.pack(side='left', padx=5)

    leftButton = tk.Button(top_bar, text="← Left", width=10, command=lambda: move_motor("left"))
    leftButton.pack(side='left', padx=5)

    rightButton = tk.Button(top_bar, text="→ Right", width=10, command=lambda: move_motor("right"))
    rightButton.pack(side='left', padx=5)

    downButton = tk.Button(top_bar, text="↓ Down", width=10, command=lambda: move_motor("down"))
    downButton.pack(side='left', padx=5)

    def move_motor(direction):
        print(f"Moving motor: {direction}")
        # TODO: Replace with motor control code

    # Create a separate frame for motor buttons
    motor_bar = tk.Frame(new_win, padx=10, pady=5)
    motor_bar.pack(fill='x')





    

    try:
        camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        camera.Open()
        camera.ExposureAuto.SetValue('Off')  # Disable auto exposure
        camera.ExposureTime.SetValue(150.0)  # Default exposure
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    except Exception as e:
        tk.messagebox.showerror("Camera Error", f"Failed to open Basler camera.\n{e}")
        new_win.destroy()
        return

    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_Mono8
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    current_img = [None]
    tk_img = [None]

    def update_frame():
        if camera.IsGrabbing():
            grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grab_result.GrabSucceeded():
                image = converter.Convert(grab_result)
                frame = image.GetArray()

                img = Image.fromarray(frame)
                img = img.resize((960, 540), Image.Resampling.LANCZOS)
                current_img[0] = frame
                tk_img[0] = ImageTk.PhotoImage(img)
                canvas.create_image(0, 0, anchor='nw', image=tk_img[0])

                capture_btn.config(state='normal')
            grab_result.Release()
        if camera.IsGrabbing():
            new_win.after(30, update_frame)

    def capture_image():
        capture_btn.config(state='disabled')
        set_reference_btn.config(state='normal')
        add_image_btn.config(state='normal')

    def set_as_reference():
        global reference, reference_label_var
        reference = current_img[0]
        reference_label_var.set("Captured Reference")
        set_reference_btn.config(state='disabled')
        add_image_btn.config(state='disabled')
        enable_phase_computation()

    def add_as_image():
        global images_dict, image_label_var, image_dropdown
        index = 1
        while f"Captured_Image_{index}" in images_dict:
            index += 1
        key = f"Captured_Image_{index}"
        images_dict[key] = current_img[0]

        menu = image_dropdown["menu"]
        menu.delete(0, "end")
        for item in images_dict:
            menu.add_command(label=item, command=tk._setit(image_label_var, item))
        image_label_var.set(key)

        set_reference_btn.config(state='disabled')
        add_image_btn.config(state='disabled')
        enable_phase_computation()

    def on_exposure_change(*args):
        try:
            val = float(exposure_var.get())
            if camera.IsOpen():
                camera.ExposureTime.SetValue(val)
        except Exception as e:
            print(f"Exposure update failed: {e}")

    exposure_var.trace_add("write", on_exposure_change)

    def on_close():
        try:
            if camera.IsGrabbing():
                camera.StopGrabbing()
            camera.Close()
        except Exception as e:
            print(f"Camera close failed: {e}")
        new_win.destroy()

    new_win.protocol("WM_DELETE_WINDOW", on_close)

    capture_btn.config(command=capture_image)
    set_reference_btn.config(command=set_as_reference)
    add_image_btn.config(command=add_as_image)

    update_frame()






root.title("Image Plane DHM")
root.geometry("480x850")
root.resizable(False, False)

param_panel = tk.LabelFrame(root, text="Parameters", padx=10, pady=10, font=('Arial', 10, 'bold'))
param_panel.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

Label(param_panel, text="Wavelength (μm)").grid(row=0, column=0, sticky='e')
wavelength_var = Entry(param_panel, width=10)
wavelength_var.insert(0, "0.650")
wavelength_var.grid(row=0, column=1)

Label(param_panel, text="Camera Pixel Size (μm)").grid(row=0, column=2, sticky='e')
pixel_size_var = Entry(param_panel, width=10)
pixel_size_var.insert(0, "1.0")
pixel_size_var.grid(row=0, column=3)

Label(param_panel, text="Magnification").grid(row=1, column=0, sticky='e')
magnification_var = Entry(param_panel, width=10)
magnification_var.insert(0, "10")
magnification_var.grid(row=1, column=1)

Label(param_panel, text="RI Difference").grid(row=1, column=2, sticky='e')
delta_ri_var = Entry(param_panel, width=10)
delta_ri_var.insert(0, "1")
delta_ri_var.grid(row=1, column=3)

Label(param_panel, text="Pixels not be used in scanning").grid(row=2, column=0, sticky='e')
dc_remove_var = Entry(param_panel, width=10)
dc_remove_var.insert(0, "20")
dc_remove_var.grid(row=2, column=1)

Label(param_panel, text="Filter Size (pixels)").grid(row=2, column=2, sticky='e')
filter_size_var = Entry(param_panel, width=10)
filter_size_var.insert(0, "101")
filter_size_var.grid(row=2, column=3)

Label(param_panel, text="Filter Type").grid(row=3, column=0, sticky='e')
filter_type_var = StringVar(root)
filter_type_var.set("circle")
OptionMenu(param_panel, filter_type_var, "circle", "square").grid(row=3, column=1)

Label(param_panel, text="Number of beams").grid(row=3, column=2, sticky='e')
type_var = StringVar(root)
type_var.set("1 Beam")
OptionMenu(param_panel, type_var, "2 Beams", "1 Beam").grid(row=3, column=3)


button_panel = tk.LabelFrame(root, text="Phase computation", padx=10, pady=10, font=('Arial', 10, 'bold'))
button_panel.grid(row=4, column=0, columnspan=4, pady=20)

reference_label_var = tk.StringVar(value="No Reference Selected")

images_panel = tk.LabelFrame(root, text="Images", padx=10, pady=10, font=('Arial', 10, 'bold'))
images_panel.grid(row=3, column=0, columnspan=4, pady=10)


camera_panel = tk.LabelFrame(root, text="Camera", padx=10, pady=10, font=('Arial', 10, 'bold'))
camera_panel.grid(row=2, column=0, columnspan=4, pady=10)
Button(camera_panel, text="Open Camera", command=open_camera_window, width=15).grid(row=3, column=1, padx=10, pady=5)



Button(images_panel, text="Load Image", command=lambda: load_image(images_dict, image_label_var, image_dropdown), width=15).grid(row=3, column=1, padx=10, pady=5)
Button(images_panel, text="Load Reference", command=lambda: load_image(reference), width=15).grid(row=3, column=2, padx=10, pady=5)

image_label_var = tk.StringVar()
image_label_var.set("None Selected")
image_dropdown = tk.OptionMenu(images_panel, image_label_var, "None Available")
image_dropdown.grid(row=4, column=1, pady=(0, 2))

Label(images_panel, textvariable=image_label_var).grid(row=4, column=1, pady=(0, 2))
Label(images_panel, textvariable=reference_label_var).grid(row=4, column=2, pady=(0, 5))

check_spectrum_button = Button(button_panel, state='disabled', text="Check Spectrum", command=check_spectrum, width=15)
check_spectrum_button.grid(row=0, column=0, padx=10, pady=5)

run_phase_button  = Button(button_panel, state='disabled', text="Phase Difference", command=run_phase_difference, width=15)
run_phase_button.grid(row=0, column=1, padx=10, pady=5)

button_panel2 = tk.LabelFrame(root, text="ROI and backgroundnd noise reduction", padx=10, pady=10, font=('Arial', 10, 'bold'))
button_panel2.grid(row=5, column=0, columnspan=4, pady=20)

select_roi_button = Button(button_panel2, text="Select ROI", state='disabled', command=select_roi, width=15)
select_roi_button.grid(row=0, column=0, padx=10)

Label(button_panel2, text="Threshold strengh").grid(row=0, column=1, sticky='e')

noise_th = Entry(button_panel2, width=10)
noise_th.insert(0, "1")
noise_th.grid(row=0, column=3)

noise_reduction_button = Button(button_panel2, text="Noise Reduction", state='disabled', command=reduce_noise, width=15)
noise_reduction_button.grid(row=0, column=4, padx=10)

button_panel3 = tk.LabelFrame(root, text="Thickness distribution", padx=10, pady=10, font=('Arial', 10, 'bold'))
button_panel3.grid(row=6, column=0, columnspan=4, pady=20)

thickness_2d_button = Button(button_panel3, text="2D profile", state='disabled', command=compute_2d_thickness, width=15)
thickness_2d_button.grid(row=0, column=0, padx=10)

thickness_3d_button = Button(button_panel3, text="3D profile", state='disabled', command=compute_3d_thickness, width=15)
thickness_3d_button.grid(row=0, column=1, padx=10)

thickness_1d_button = Button(button_panel3, text="1D profile", state='disabled', command=compute_1d_thickness, width=15)
thickness_1d_button.grid(row=0, column=3, padx=10)

button_panel4 = tk.LabelFrame(root, text="Other", padx=10, pady=10, font=('Arial', 10, 'bold'))
button_panel4.grid(row=7, column=0, columnspan=4, pady=20)
run_all_button = Button(button_panel4, text="Run All", state='disabled', command=run_all, width=15)
run_all_button.grid(row=0, column=1, padx=10)

root.protocol("WM_DELETE_WINDOW", root.destroy)

root.mainloop()


