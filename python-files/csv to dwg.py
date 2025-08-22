import csv
import ezdxf
import tkinter as tk
from tkinter import filedialog, messagebox
from ezdxf.enums import TextEntityAlignment

def choose_csv_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

def choose_dxf_save_location():
    root = tk.Tk()
    root.withdraw()
    return filedialog.asksaveasfilename(
        title="Save DXF File As",
        defaultextension=".dxf",
        filetypes=[("DXF files", "*.dxf"), ("All files", "*.*")]
    )

def get_coordinate_order():
    """Ask user for coordinate order"""
    root = tk.Tk()
    root.withdraw()
    
    choice = messagebox.askquestion(
        "Coordinate Order",
        "What is the coordinate order in your CSV?\n\n"
        "Yes: PointName, X, Y, Z, Height (Standard)\n"
        "No: PointName, Y, X, Z, Height (Your file)"
    )
    
    return choice == 'yes'  # True for X,Y order, False for Y,X order

def csv_to_dxf_with_layers(csv_file, dxf_file, xy_order=True):
    """Convert CSV to DXF with configurable coordinate order"""
    try:
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Create layers
        doc.layers.new(name='POINTS', dxfattribs={'color': 2})
        doc.layers.new(name='POINT_NAMES', dxfattribs={'color': 5})
        doc.layers.new(name='POINT_HEIGHTS', dxfattribs={'color': 1})
        
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            points_count = 0
            
            for row in reader:
                if len(row) >= 5:
                    try:
                        point_name = row[0]
                        
                        if xy_order:
                            # Standard order: X, Y, Z, Height
                            x = float(row[1])
                            y = float(row[2])
                        else:
                            # Your order: Y, X, Z, Height
                            y = float(row[1])
                            x = float(row[2])
                            
                        z = float(row[3])
                        height = row[4]
                        
                        # Add point
                        msp.add_point((x, y), dxfattribs={'layer': 'POINTS'})
                        
                        # Add point name text
                        text_name = msp.add_text(
                            point_name,
                            dxfattribs={
                                'layer': 'POINT_NAMES',
                                'height': 1,
                            }
                        )
                        text_name.set_placement((x+1, y), align=TextEntityAlignment.BOTTOM_LEFT)
                        
                        # Add height text
                        text_height = msp.add_text(
                            height,
                            dxfattribs={
                                'layer': 'POINT_HEIGHTS',
                                'height': 1,
                            }
                        )
                        text_height.set_placement((x+1, y), align=TextEntityAlignment.TOP_LEFT)
                        
                        points_count += 1
                        
                    except ValueError:
                        continue
        
        doc.saveas(dxf_file)
        
        order = "X,Y order" if xy_order else "Y,X order (corrected)"
        messagebox.showinfo(
            "Success",
            f"Converted {points_count} points!\n"
            f"Coordinate order: {order}\n"
            f"Saved to:\n{dxf_file}"
        )
        
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"Conversion failed:\n{str(e)}")
        return False

def main():
    csv_file = choose_csv_file()
    if not csv_file:
        return
    
    dxf_file = choose_dxf_save_location()
    if not dxf_file:
        return
    
    # Ask for coordinate order
    xy_order = get_coordinate_order()
    
    csv_to_dxf_with_layers(csv_file, dxf_file, xy_order)

if __name__ == "__main__":
    main()
