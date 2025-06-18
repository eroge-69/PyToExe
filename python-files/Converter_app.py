# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 11:22:48 2025

@author: 5maxc

Full Converter app
"""
#import Libraries
from tkinter import *
import os
import tifffile
from ome_types.model import OME, Pixels, Channel
from ome_types.model import Image as omed
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
#from PIL import Image
#from PIL import ImageTk
import napari
from imctools.converters.mcdfolder2imcfolder import mcdfolder_to_imcfolder
from aicsimageio import AICSImage
#import sys
#from pathlib import Path


# def resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and PyInstaller """
#     try:
#         # PyInstaller stores temp path in _MEIPASS
#         base_path = Path(sys._MEIPASS)
#     except AttributeError:
#         base_path = Path(__file__).parent
#     return base_path / relative_path


def convert_mcd_window(): #opens drop box for mcd converter and runs function
    def on_drop(event):
        path = event.data.strip('{}')
        file_path_var.set(path)
        listb.insert("end", event.data)
        listb.destroy()
        instructions.destroy()
        # Run the conversion
        mcdfolder_to_imcfolder( input=path, output_folder=path, create_zip=False, parse_txt=True)

 
    instructions=Label(overview,text="Drop the ENTIRE folder containing your MCD file")
    instructions.grid(row=2, column=1, sticky=EW, padx=10)
    listb=Listbox(overview, selectmode=SINGLE, background="#b3b3cc", width=55, height=8)
    listb.grid(row=1, column=1, padx=10)
    listb.drop_target_register(DND_FILES)
    listb.dnd_bind("<<Drop>>", on_drop )
    
  


def convert_cosmx_window():#opens drop box for cosmx converter and runs function
    def on_drop(event):
        path = event.data.strip('{}')
        file_path_var.set(path)
        listb.insert("end", event.data)
        #print(f"Dropped file: {path}")
        listb.destroy()
        instructions.destroy()
        
        #actual Function to convert tif to ome-tiff
        # === Creates input and output based on drag and drop ===
        newfilepath=path.replace(".TIF",".ome-tiff" )
        input_path = path
        output_path = newfilepath
        # === Load image data ===
        image_data = tifffile.imread(input_path)
        print(f"Original image shape: {image_data.shape}")
        # --- Understand the shape ---
        # For multichannel fluorescence, expected shape could be (T, C, Y, X) or (C, Y, X)
        # Let's handle both cases:
        if len(image_data.shape) == 4:
            # Assume (T, C, Y, X)
            T, C, Y, X = image_data.shape
            if T != 1:
                print(f"Warning: Image has {T} timepoints, but should be 1. Fixing metadata accordingly.")
        elif len(image_data.shape) == 3:
            # Assume (C, Y, X)
            C, Y, X = image_data.shape
            T = 1
        else:
            raise ValueError(f"Unexpected image shape: {image_data.shape}")
        # --- Confirm channel count matches your info ---
        assert C == 5, f"Expected 5 channels but got {C}"
        # === Build OME metadata ===
        pixels = Pixels(
            dimension_order="XYCZT",  # XY, then Channels, Z=1, T=1
            size_x=X,
            size_y=Y,
            size_c=C,
            size_z=1,
            size_t=T,
            type=str(image_data.dtype),
            channel=[Channel(id=f"Channel:0:{i}", name=f"Channel {i+1}") for i in range(C)]
        )
        ome_image = omed(id="Image:0", name=os.path.basename(input_path), pixels=pixels)
        ome = OME(image=[ome_image])
        # === Save as OME-TIFF ===
        # tifffile expects the axes order in data to match the metadata; here we give data as (T, C, Y, X) or (C, Y, X)
        # If shape is (C, Y, X), we add a time dimension for saving
        if len(image_data.shape) == 3:
            # Add time axis (T=1)
            image_data = image_data[None, :, :, :]  # shape becomes (1, C, Y, X)
        tifffile.imwrite(
            output_path,
            image_data,
            metadata={'axes': 'TCYX'},
            ome=True,
            description=ome.to_xml()
        )
        print(f"OME-TIFF file saved successfully at:\n{output_path}")
    #the rest of window popup with drag and drop feature
    listb=Listbox(overview, selectmode=SINGLE, background="#b3b3cc", width=55, height=8)
    listb.grid(row=1, column=1, padx=10)
    listb.drop_target_register(DND_FILES)
    listb.dnd_bind("<<Drop>>", on_drop )
    instructions=Label(overview,text="Drop Your Single TIF File Above")
    instructions.grid(row=2, column=1, sticky=EW, padx=10)




def extract_channel_names(ome_tiff_path):
    """
    Extracts channel names from an OME-TIFF file.

    Args:
        ome_tiff_path (str): Path to the OME-TIFF file.

    Returns:
        list: A list of channel names (strings) or None if no channels are found.
    """
    try:
        # Load the OME-TIFF image
        img = AICSImage(ome_tiff_path)

        # Extract channel names
        channel_names = img.channel_names

        if channel_names:
            return channel_names
        else:
            return None

    except FileNotFoundError:
        print(f"Error: File not found at {ome_tiff_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def split_ome_tiff(input_file, output_dir, channel_listy):

    try:
        os.makedirs(output_dir, exist_ok=True)

        with tifffile.TiffFile(input_file) as tif:
            for i, page in enumerate(tif.pages):
                output_path = os.path.join(output_dir, f"{input_file}_{channel_listy[i]}.tif")
                tifffile.imwrite(output_path, page.asarray())

        print("OME-TIFF file split successfully.")

    except Exception as e:
        print(f"Error splitting OME-TIFF file: {e}")
        

    
    
def ome_to_tif_window():
    def on_drop(event):
        path = event.data.strip('{}')
        file_path_var.set(path)
        channel_list = extract_channel_names(path)
        directory = os.path.dirname(path)
        split_ome_tiff(path, directory, channel_list)
        listb.destroy()
        instructions.destroy()
    listb=Listbox(overview, selectmode=SINGLE, background="#b3b3cc", width=55, height=8)
    listb.grid(row=1, column=1, padx=10)
    listb.drop_target_register(DND_FILES)
    listb.dnd_bind("<<Drop>>", on_drop )   
    instructions=Label(overview,text="Convert OME-TIFF to Multiple TIFs by Channel")
    instructions.grid(row=2, column=1,sticky=EW, padx=10)
 




def base_napari(): #opens base napari
    viewer = napari.view_image()
    napari.run()
    
    
def open_napari_window(): #opens drag and drop window for napari image selection. Then opens napari
    def on_drop(event):
        path = event.data.strip('{}')
        file_path_var.set(path)
        image = tifffile.imread(path)
        listb.destroy()
        instructions.destroy()
        # Launch napari 
        viewer = napari.view_image(image)
        napari.run()
    #Drag and drop window
    listb=Listbox(overview, selectmode=SINGLE, background="#b3b3cc", width=55, height=8)
    listb.grid(row=1, column=1, padx=10)
    listb.drop_target_register(DND_FILES)
    listb.dnd_bind("<<Drop>>", on_drop )
    instructions=Label(overview,text="Drop Your Single TIF File Above To Open in Napari")
    instructions.grid(row=2, column=1, sticky=EW, padx=10)

    
###################################################################### 
root=TkinterDnD.Tk()
root.title("Multiple Format Converter")
root.config(bg="#0c294d")
root.geometry('1000x600')
label = Label(root, text="Welcome to the Multiple Format Converter", font=('Arial', 20))
label.pack(fill=X)
file_path_var = StringVar() #Important for 2nd button

#main structure. frame with 2 parts
overview= Frame(root, bg="#0c294d")
overview.pack(fill=X, pady=5)

button_frame = Frame(overview, bg="#0c294d")
button_frame.grid(row=1, column=0, padx=10)



###### 5 buttons top right
#add pictures
#ometif_path=resource_path("assets/ome-tiff-pic.png")
#napari_path=resource_path("assets/napari-logo-3.png")
#ometiff_pic = PhotoImage(file = ometif_path).subsample(2, 2)
#napari_pic= PhotoImage(file=napari_path).subsample(18,18)
#style button formats
s=ttk.Style()
s.configure("Ome.TButton",   bg= "#fdfdfd",  font=('Rockwell', 18))
s.configure("Napari.TButton", bg= "#fdfdfd",  font=('Rockwell', 18))
s.configure("Tif.TButton",  font=('Rockwell',18))

#add buttons
btn1=ttk.Button(button_frame, text="MCD to OME-TIFF", command=convert_mcd_window, style="Ome.TButton")
btn1.grid(row=1, column=0, padx=10, pady=5)

btn2=ttk.Button(button_frame, text="COSMX to OME-TIFF", command=convert_cosmx_window, style="Ome.TButton")
btn2.grid(row=2, column=0, padx=10, pady=5)

btn3=ttk.Button(button_frame, text="OME-TIFF to TIF Folder", command=ome_to_tif_window, style="Tif.TButton")
btn3.grid(row=3, column=0, padx=10, pady=5)

btn4=ttk.Button(button_frame, text="Open base napari", command=base_napari, style="Napari.TButton")
btn4.grid(row=4, column=0, padx=10, pady=5)

btn5=ttk.Button(button_frame, text="Open TIF image with Napari", command=open_napari_window, style="Napari.TButton")
btn5.grid(row=5, column=0, padx=10, pady=5)



#runs tkinter GUI
root.mainloop()


