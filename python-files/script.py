import tkinter as tk
from tkinter import simpledialog
import subprocess
import math
import os

def create_kml_file(lat, lon, azimuths):
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Starting Point</name>
      <Point>
        <coordinates>{lon},{lat}</coordinates>
      </Point>
    </Placemark>
"""

    for i, azimuth in enumerate(azimuths):
        distance = 1  # distance in kilometers
        # Calculate the new point based on azimuth
        new_lat = lat + (distance * math.cos(math.radians(azimuth)) / 111.32)  # 1 km latitude ≈ 1/111.32 degrees
        new_lon = lon + (distance * math.sin(math.radians(azimuth)) / (111.32 * math.cos(math.radians(lat))))  # 1 km longitude
        kml_content += f"""
    <Placemark>
      <name>Line to {azimuth}°</name>
      <LineString>
        <altitudeMode>clampToGround</altitudeMode>
        <coordinates>
          {lon},{lat} {new_lon},{new_lat}
        </coordinates>
      </LineString>
    </Placemark>
"""

    kml_content += """
  </Document>
</kml>
"""
    
    # Save KML content to a file
    with open("lines.kml", "w") as f:
        f.write(kml_content)
    
    return "lines.kml"

def open_google_earth(kml_file):
    # Replace 'C:\\Path\\To\\Google Earth Pro\\client\\client.exe' with the actual path to your Google Earth executable
    google_earth_path = r'C:\Program Files\Google\Earth Pro\client\client.exe'
    subprocess.Popen([google_earth_path, kml_file])

def main():
    # Create a simple dialog to ask for coordinates and azimuths
    ROOT = tk.Tk()
    ROOT.withdraw()  # Hide the main window

    lat = simpledialog.askfloat("Input", "Enter latitude:", minvalue=-90, maxvalue=90)
    lon = simpledialog.askfloat("Input", "Enter longitude:", minvalue=-180, maxvalue=180)
    
    azimuths = []
    for i in range(3):
        azimuth = simpledialog.askfloat("Input", f"Enter azimuth {i+1} (degrees):", minvalue=0, maxvalue=360)
        azimuths.append(azimuth)

    # Create KML file
    kml_file = create_kml_file(lat, lon, azimuths)

    # Open Google Earth with the KML file
    open_google_earth(kml_file)

if __name__ == "__main__":
    main()