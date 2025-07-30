import os.path
import kml2geojsonFTTH as k2g
import json
import geojson
from tkinter import *
from tkinter import filedialog
import xml.etree.ElementTree as ET
from fastkml import kml
from shapely.geometry import shape, Polygon, mapping, Point
from shapely.validation import make_valid

# DefualtPath = 'D:\\mygeodata\\kml'
# FileName = 'teh.tehn.s.602'

global FilePath
FilePath = ''
class KMLFile:
    def __init__(self):
        self.KMLFileName = ''

    def conversion(self):
        FileName = self.KMLFileName
        OriginalFileName = os.path.split(FileName)[1].replace('.kml', '')
        print(FilePath)

        JsonData = k2g.main.convert(self.KMLFileName, '')
        print(JsonData)
        with open(OriginalFileName + ".json", 'w') as JsonFile:
            json.dump(JsonData[0], JsonFile)

# Function to rename polygons based on the names of points with specific substrings
def rename_polygons_based_on_points(geojson_data, substrings):
    # Collect names of points with specified substrings
    point_names = []
    for feature in geojson_data['features']:
        if feature['geometry']['type'] == 'Point':
            point_name = feature['properties'].get('name', '')
            if any(sub in point_name for sub in substrings):
                point_names.append(point_name)

    # Rename polygons using the collected point names
    for feature in geojson_data['features']:
        if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']:
            if point_names:
                feature['properties']['name'] = point_names[0]  # Assign the first matching point name
                point_names.pop(0)  # Remove the used name to prevent reusing

def browseFiles():
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a KML File",
                                          filetypes=(("KML files", "*.kml*"),
                                                     ("all files", "*.*")))

    print(IsRemove.get())

    # Change label contents
    if IsRemove.get() == 0:
        label_file_explorer.configure(text="File Opened: " + filename)
        MyKML = KMLFile()
        MyKML.KMLFileName = filename
        MyKML.conversion()
        label_file_explorer.configure(text="File Opened: " + filename + ', Conversion Done!')
    if IsRemove.get() == 1:
        label_file_explorer.configure(text="File Opened: " + filename)
        MyKML = KMLFile()
        MyKML.KMLFileName = filename

        # Load the KML file
        tree = ET.parse(filename)
        root = tree.getroot()

        # Define the KML namespace
        namespace = {'kml': 'http://www.opengis.net/kml/2.2'}

        # Iterate over placemarks and remove those that have "ft" or "br" in their name
        for parent in root.findall('.//kml:Document', namespaces=namespace) + root.findall('.//kml:Folder', namespaces=namespace):
            for placemark in parent.findall('kml:Placemark', namespaces=namespace):
                name = placemark.find('kml:name', namespaces=namespace)
                if name is not None and ('ft.' in name.text or 'br.' in name.text):
                    parent.remove(placemark)  # Remove placemark from its parent

        # Save the modified KML file
        OriginalFileName = os.path.split(filename)[1]
        tree.write(OriginalFileName, encoding='utf-8')

        # Read and parse the modified KML file
        with open(OriginalFileName, 'rt', encoding='utf-8') as file:
            kml_data = file.read()

        k = kml.KML()
        k.from_string(kml_data)

        features = []
        # Iterate through the KML structure and collect only Placemark elements
        for document in k.features():  # Top-level features (e.g., Document)
            for feature in document.features():  # Nested features (e.g., Folder or Placemark)
                if hasattr(feature, 'features'):  # Check if the feature can contain other features (like a Folder)
                    for placemark in feature.features():  # Iterate over the placemarks inside folders
                        if hasattr(placemark, 'geometry') and placemark.geometry:
                            # Create a GeoJSON feature
                            geom = geojson.Feature(
                                geometry=placemark.geometry.__geo_interface__,
                                properties={"name": placemark.name}
                            )
                            features.append(geom)
                elif hasattr(feature, 'geometry') and feature.geometry:  # If the feature is a Placemark directly
                    geom = geojson.Feature(
                        geometry=feature.geometry.__geo_interface__,
                        properties={"name": feature.name}
                    )
                    features.append(geom)

        feature_collection = geojson.FeatureCollection(features)

        # Save to GeoJSON
        GeojsonFilename = OriginalFileName.replace("kml", "geojson")
        with open(GeojsonFilename, 'w', encoding='utf-8') as f:
            geojson.dump(feature_collection, f)

        print("Conversion to GeoJSON complete!")
        label_file_explorer.configure(text="File Opened: " + filename + ', Conversion Done!')

        with open(GeojsonFilename, 'r') as f:
            geojson_data = json.load(f)

        # Rename polygons based on point names with specific substrings
        if IsRename.get() == 1:
            rename_polygons_based_on_points(geojson_data, ['.s.', '.m', '.p', '.b'])

        # Validate and fix geometries
        for feature in geojson_data['features']:
            geom = shape(feature['geometry'])

            # Check if the geometry is a Polygon or MultiPolygon
            if isinstance(geom, Polygon) or geom.geom_type == 'MultiPolygon':
                if not geom.is_valid:
                    print(f"Invalid polygon found with ID: {feature.get('id', 'N/A')}")
                    fixed_geom = make_valid(geom)

                    if fixed_geom.is_valid:
                        print("Polygon fixed successfully.")
                        feature['geometry'] = mapping(fixed_geom)
                    else:
                        print("Polygon could not be fixed automatically.")
                else:
                    print("Polygon is valid.")

        # Save the modified GeoJSON back to a file
        with open('valid_' + GeojsonFilename, 'w') as f:
            json.dump(geojson_data, f, indent=2)

        print("Validation and fixing process complete!")

window = Tk()

window.title('File Explorer')
window.geometry("700x150")
window.config(background="gray")

label_file_explorer = Label(window,
                            text="KML Converter",
                            width=100, height=4,
                            fg="blue")

IsRemove = IntVar()
IsRename = IntVar()

checkbox = Checkbutton(window, text="Remove FAT points and polygon validation", variable=IsRemove)
checkbox2 = Checkbutton(window, text="Rename polygon to point", variable=IsRename)


button_explore = Button(window,
                        text="Browse Files",
                        command=browseFiles)

# Pack the checkbox to make it visible
checkbox.grid(column=1, row=2)
checkbox2.grid(column=1, row=3)


label_file_explorer.grid(column=1, row=1)

button_explore.grid(column=1, row=4)

window.mainloop()