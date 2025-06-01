import tkinter as tk
from tkinter import messagebox

def convert_coordinates():
    try:
        # Get input values
        given_n = float(entry_given_n.get())
        given_e = float(entry_given_e.get())
        ref_n = float(entry_ref_n.get())
        ref_e = float(entry_ref_e.get())
        ref_lat_dd = float(entry_ref_lat_dd.get())
        ref_lat_mm = float(entry_ref_lat_mm.get())
        ref_lat_ss = float(entry_ref_lat_ss.get())
        ref_long_dd = float(entry_ref_long_dd.get())
        ref_long_mm = float(entry_ref_long_mm.get())
        ref_long_ss = float(entry_ref_long_ss.get())
        lat_meter_per_sec = float(entry_lat_sec.get())
        long_meter_per_sec = float(entry_long_sec.get())

        # Convert reference lat/long to decimal degrees
        ref_lat_dec = ref_lat_dd + (ref_lat_mm / 60) + (ref_lat_ss / 3600)
        ref_long_dec = ref_long_dd + (ref_long_mm / 60) + (ref_long_ss / 3600)

        # Compute differences
        diff_n = given_n - ref_n
        diff_e = given_e - ref_e

        # Convert to seconds
        sec_lat = diff_n / lat_meter_per_sec
        sec_long = diff_e / long_meter_per_sec

        # Compute new coordinates
        new_lat = ref_lat_dec + (sec_lat / 3600)
        new_long = ref_long_dec + (sec_long / 3600)

        # Convert back to DD-MM-SS format
        new_lat_dd = int(new_lat)
        new_lat_mm = int((new_lat - new_lat_dd) * 60)
        new_lat_ss = ((new_lat - new_lat_dd) * 60 - new_lat_mm) * 60
        
        new_long_dd = int(new_long)
        new_long_mm = int((new_long - new_long_dd) * 60)
        new_long_ss = ((new_long - new_long_dd) * 60 - new_long_mm) * 60
        
        formatted_lat = f"{new_lat_dd}°{new_lat_mm}'{new_lat_ss:.3f}\""
        formatted_long = f"{new_long_dd}°{new_long_mm}'{new_long_ss:.3f}\""


        # Show result
        messagebox.showinfo("Computed Coordinates", f"Latitude: {formatted_lat}\nLongitude: {formatted_long}\n\nEngr. Neil Bryan Tabanao")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

# Create GUI window
root = tk.Tk()
root.title("Geographic Position Calculator")

# Create frames for layout
frame1 = tk.Frame(root)
frame2 = tk.Frame(root)
frame3 = tk.Frame(root)
frame4 = tk.Frame(root)
frame1.pack(pady=5)
frame2.pack(pady=5)
frame3.pack(pady=5)
frame4.pack(pady=5)

# Given Coordinates
tk.Label(frame1, text="Observed Station").grid(row=0, column=1)
tk.Label(frame1, text="Northing:").grid(row=1, column=0)
tk.Label(frame1, text="Easting:").grid(row=2, column=0)
entry_given_n = tk.Entry(frame1)
entry_given_e = tk.Entry(frame1)
entry_given_n.grid(row=1, column=1)
entry_given_e.grid(row=2, column=1)

# Reference Coordinates
tk.Label(frame2, text="Reference Station").grid(row=0, column=1)
tk.Label(frame2, text="Northing:").grid(row=1, column=0)
tk.Label(frame2, text="Easting:").grid(row=2, column=0)
entry_ref_n = tk.Entry(frame2)
entry_ref_e = tk.Entry(frame2)
entry_ref_n.grid(row=1, column=1)
entry_ref_e.grid(row=2, column=1)

# Reference Latitude
tk.Label(frame3, text="Reference Latitude").grid(row=0, column=1)
lat_frame = tk.Frame(frame3)
lat_frame.grid(row=1, column=0, columnspan=3)
tk.Label(lat_frame, text="Degree:").grid(row=0, column=0)
tk.Label(lat_frame, text="Minute:").grid(row=0, column=1)
tk.Label(lat_frame, text="Seconds:").grid(row=0, column=2)
entry_ref_lat_dd = tk.Entry(lat_frame, width=5)
entry_ref_lat_mm = tk.Entry(lat_frame, width=5)
entry_ref_lat_ss = tk.Entry(lat_frame, width=5)
entry_ref_lat_dd.grid(row=1, column=0)
entry_ref_lat_mm.grid(row=1, column=1)
entry_ref_lat_ss.grid(row=1, column=2)

# Reference Longitude
tk.Label(frame4, text="Reference Longitude").grid(row=0, column=1)
long_frame = tk.Frame(frame4)
long_frame.grid(row=1, column=0, columnspan=3)
tk.Label(long_frame, text="Degree:").grid(row=0, column=0)
tk.Label(long_frame, text="Minute:").grid(row=0, column=1)
tk.Label(long_frame, text="Seconds:").grid(row=0, column=2)
entry_ref_long_dd = tk.Entry(long_frame, width=5)
entry_ref_long_mm = tk.Entry(long_frame, width=5)
entry_ref_long_ss = tk.Entry(long_frame, width=5)
entry_ref_long_dd.grid(row=1, column=0)
entry_ref_long_mm.grid(row=1, column=1)
entry_ref_long_ss.grid(row=1, column=2)

# Length per Second
tk.Label(frame4, text="Length per Second").grid(row=2, column=1)
tk.Label(frame4, text="Latitude (m/s):").grid(row=3, column=0)
tk.Label(frame4, text="Longitude (m/s):").grid(row=4, column=0)
entry_lat_sec = tk.Entry(frame4)
entry_long_sec = tk.Entry(frame4)
entry_lat_sec.grid(row=3, column=1)
entry_long_sec.grid(row=4, column=1)

# Compute Button
tk.Button(frame4, text="Compute", command=convert_coordinates).grid(row=5, column=1)

# Run GUI
root.mainloop()
