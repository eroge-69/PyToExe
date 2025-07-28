# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 17:19:56 2023

@author: hp
"""

import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import pandas as pd


# Define paths
csv_file_path = "C:/Users/HP/OneDrive/Desktop/eFile Report/eOffice30Mar-4Apr.csv"
output_shapefile_path = "C:/Users/HP/OneDrive/Desktop/eFile Report/States&Districts/States&Districts/New folder/eoffice_lbl.shp"

# Read CSV file using pandas
data = pd.read_csv(csv_file_path)

# Create a GeoDataFrame
geometry = [Point(xy) for xy in zip(data.Lon_dec, data.Lat_dec)]
geo_df = gpd.GeoDataFrame(data, geometry=geometry)

# Save the GeoDataFrame as a shapefile
output_folder = Path(output_shapefile_path).parent
output_folder.mkdir(parents=True, exist_ok=True)

#shapefile_name = 'eoffice_lbl.shp'
geo_df.to_file(output_shapefile_path, driver='ESRI Shapefile', crs="EPSG:4326")

