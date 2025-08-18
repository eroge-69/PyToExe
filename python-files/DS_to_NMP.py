import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

paths = []

NMP_HEADER = """FILEVER/NEXIV,ONLINE,010204
UNITS/MM,DEG
ENCODE/NASE64
FORMAT/LENGTH,MM,5
FORMAT/ANGLE,DEG,5
SAMPLE/LOT,"00000000"
SAMPLE/NUM,1
ORIGIN/MATRIX,1,0,0,0,1,0,0,0,1,0,0,0
REPEAT/GRID,0,0,0,1,1,1
FILE/CONVERT,HORIZ
FILE/DDE,"Excel","[Book1.xls]Sheet1"
CONTROL/FAIL,IGNORE,NOSAVE
CONTROL/ERROR,STOP,NOSAVE
REPLAY/OUTPUT,CONVERT
MACHINE/NEXIV
 CAMERA/FORMAT,VGA
ENDMACH
PROGRAM/MAIN"""

NMP_FOOTER = "ENDPROG\nENDFILE"

def read_ds_file(ds_path):
	points = []
	try:
		with open(ds_path, 'r') as file:
			lines = file.readlines()[1:]
			for line in lines:
				parts = line.strip().split()
				if len(parts) >= 3:
					x, y, z = parts[0], parts[1], parts[2]
					points.append((x, y, z))
	except Exception as e:
		messagebox.showerror("Error, Failed to read DS file: {}".format(e))
	return points

def reorder_coordinates(coords, mapping):
    """
    mapping = {'X': 'Z', 'Y': 'X', 'Z': 'Y'}
    Meaning (with GUI labels): DS.X -> NMP.Z, DS.Y -> NMP.X, DS.Z -> NMP.Y
    """
    letter_to_index = {'X': 0, 'Y': 1, 'Z': 2}

    inverted = {v: k for k, v in mapping.items()}

    return (
        coords[letter_to_index[inverted['X']]],
        coords[letter_to_index[inverted['Y']]],
        coords[letter_to_index[inverted['Z']]],
    )

def generate_point_block(point_number, coords, ds_filename):
	x, y, z = coords
	block = []
	block.append(f"CODE/{point_number},CPOINT")
	block.append(F' TEXT/CODE,"{ds_filename}"')
	block.append(" WKPLANE/XY")
	block.append(f" F/POINT,CART,{float(x):.5f},{float(y):.5f},{float(z):.5f},0,0,1")
	block.append(f" T/X,{float(x):.5f},0.00000,0.00000")
	block.append(f" T/Y,{float(y):.5f},0.00000,0.00000")
	block.append(f" T/Z,{float(z):.5f},0.00000,0.00000")
	block.append(" T/POS,0.00000,0.00000,0.00000")
	block.append(" DISPLAY/FEAT")
	block.append("ENDCODE")
	return "\n".join(block)

def convert_ds_files_to_nmp(ds_paths, nmp_path, mapping):
    nmp_content = [NMP_HEADER]
    point_counter = 1

    for ds_path in ds_paths:
        base_name = os.path.splitext(os.path.basename(ds_path))[0]
        points = read_ds_file(ds_path)
        for coords in points:
            reordered = reorder_coordinates(coords, mapping)
            block = generate_point_block(point_counter, reordered, base_name)
            nmp_content.append(block)
            point_counter += 1

    nmp_content.append(NMP_FOOTER)

    try:
        with open(nmp_path, 'w') as f:
            f.write("\n".join(nmp_content))
        messagebox.showinfo("Success", f"Merged NMP file saved to {nmp_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write NMP file: {e}")


#GUI
def select_ds_files():
    global paths
    file_paths = filedialog.askopenfilenames(filetypes=[("DS files", "*.ds")])
    if file_paths:
        for f in file_paths:
            if f not in paths:
                paths.append(f)
                listbox_ds_files.insert(tk.END, os.path.basename(f))
        messagebox.showinfo("Files Selected", f"{len(file_paths)} file(s) selected.")

def deselect_ds_files():
	global paths
	paths = []
	listbox_ds_files.delete(0, tk.END)
	messagebox.showinfo("Deselection", "All .ds files have been deselected.")

def save_nmp_file():
	nmp_path = filedialog.asksaveasfilename(defaultextension=".nmp", filetypes=[("NMP files", "*.nmp")])
	if nmp_path:
		entry_nmp_path.delete(0, tk.END)
		entry_nmp_path.insert(0, nmp_path)

def run_conversion():
    if not paths:
        messagebox.showerror("Error", "Please select at least one DS file.")
        return

    nmp_path = entry_nmp_path.get()
    if not nmp_path:
        messagebox.showerror("Error", "Please select a location to save the NMP file.")
        return

    mapping = {
        'X': var_x.get(),
        'Y': var_y.get(),
        'Z': var_z.get()
    }

    convert_ds_files_to_nmp(paths, nmp_path, mapping)

# ===== GUI Setup =====
root = tk.Tk()
root.title("DS to NMP Converter")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# DS File Selection
ttk.Label(frame, text="Select DS files:").grid(row=0, column=0, sticky=tk.W)
listbox_ds_files = tk.Listbox(frame, width=50, height=8)
listbox_ds_files.grid(row=1, column=0, columnspan=2, pady=5)
ttk.Button(frame, text="Add Files", command=select_ds_files).grid(row=1, column=2, padx=5)

# NMP file save location
ttk.Label(frame, text="Save NMP file as:").grid(row=2, column=0, sticky=tk.W, pady=5)
entry_nmp_path = ttk.Entry(frame, width=50)
entry_nmp_path.grid(row=2, column=1, padx=5)
ttk.Button(frame, text="Browse", command=save_nmp_file).grid(row=2, column=2)

# X/Y/Z Mapping
ttk.Label(frame, text="X is:").grid(row=3, column=0, sticky=tk.W)
var_x = tk.StringVar(value="X")
combobox_x = ttk.Combobox(frame, textvariable=var_x, values=["X","Y","Z"], width=5, state="readonly")
combobox_x.grid(row=3, column=1, sticky=tk.W)

ttk.Label(frame, text="Y is:").grid(row=4, column=0, sticky=tk.W)
var_y = tk.StringVar(value="Y")
combobox_y = ttk.Combobox(frame, textvariable=var_y, values=["X","Y","Z"], width=5, state="readonly")
combobox_y.grid(row=4, column=1, sticky=tk.W)

ttk.Label(frame, text="Z is:").grid(row=5, column=0, sticky=tk.W)
var_z = tk.StringVar(value="Z")
combobox_z = ttk.Combobox(frame, textvariable=var_z, values=["X","Y","Z"], width=5, state="readonly")
combobox_z.grid(row=5, column=1, sticky=tk.W)

#Convert button
ttk.Button(frame, text="Convert", command=run_conversion).grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()
