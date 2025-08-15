import tkinter as tk
from tkinter import messagebox
import os

# Original KML generation function
def generate_kml(lat, lon, start_level=10, num_levels=11, start_alt=36.23, alt_increment=3.2, heading=330, tilt=90, range_val=1):
    kml_header = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\" xmlns:kml=\"http://www.opengis.net/kml/2.2\" xmlns:atom=\"http://www.w3.org/2005/Atom\">
<Document>
    <name>Levels</name>
    <open>1</open>
"""
    kml_body = ""
    for i in range(num_levels):
        level_num = start_level + i
        altitude = start_alt + i * alt_increment
        placemark = f"""
    <!-- Placemark {i+1} -->
    <Placemark>
        <name>Level {level_num}</name>
        <LookAt>
            <longitude>{lon}</longitude>
            <latitude>{lat}</latitude>
            <altitude>{altitude:.6f}</altitude>
            <heading>{heading}</heading>
            <tilt>{tilt}</tilt>
            <range>{range_val}</range>
            <gx:altitudeMode>absolute</gx:altitudeMode>
        </LookAt>
        <Point>
            <coordinates>{lon},{lat},{altitude:.6f}</coordinates>
        </Point>
    </Placemark>
"""
        kml_body += placemark

    kml_footer = "\n</Document>\n</kml>"
    return kml_header + kml_body + kml_footer

# GUI application
def create_gui():
    def generate_file():
        try:
            lat = float(entry_lat.get())
            lon = float(entry_lon.get())
            start_level = int(entry_start_level.get())
            num_levels = int(entry_num_levels.get())
            start_alt = float(entry_start_alt.get())
            alt_increment = float(entry_alt_increment.get())
            heading = float(entry_heading.get())
            tilt = float(entry_tilt.get())
            range_val = float(entry_range.get())
            save_dir = entry_output_dir.get() or "output"

            kml_content = generate_kml(lat, lon, start_level, num_levels, start_alt, alt_increment, heading, tilt, range_val)
            os.makedirs(save_dir, exist_ok=True)
            filename = os.path.join(save_dir, "Levels.kml")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(kml_content)

            messagebox.showinfo("Success", f"KML file saved successfully at: {filename}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("KML Generator")

    labels = [
        ("Latitude:", "0.0"),
        ("Longitude:", "0.0"),
        ("Starting Level:", "1"),
        ("Number of Levels:", "20"),
        ("Starting Altitude (m):", "0"),
        ("Altitude Increment:", "3.2"),
        ("Heading:", "0"),
        ("Tilt:", "90"),
        ("Range:", "1"),
        ("Output Folder:", "output")
    ]

    entries = []
    for i, (label_text, default) in enumerate(labels):
        tk.Label(root, text=label_text).grid(row=i, column=0, sticky="e")
        entry = tk.Entry(root)
        entry.insert(0, default)
        entry.grid(row=i, column=1)
        entries.append(entry)

    (entry_lat, entry_lon, entry_start_level, entry_num_levels, entry_start_alt,
     entry_alt_increment, entry_heading, entry_tilt, entry_range, entry_output_dir) = entries

    tk.Button(root, text="Generate KML", command=generate_file).grid(row=len(labels), columnspan=2, pady=10)

    root.mainloop()

# Run the GUI
create_gui()
