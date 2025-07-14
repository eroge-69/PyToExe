import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

# 1. Load the shapefile and text data
shapefile_path = "/content/PeykarehBandi_fars.shp"
text_data_path = "/content/DATA.txt"  # CSV/TXT with 'Bazeh_Code' and 'PERCENT_VALUE'

# Read shapefile
gdf = gpd.read_file(shapefile_path)

# Check the current CRS
print("Current CRS:", gdf.crs)

# If the CRS is not EPSG:4326, reproject to WGS84 (EPSG:4326)
if gdf.crs.to_string() != "EPSG:4326":
    gdf = gdf.to_crs(epsg=4326)

# Read text data (modify sep=',' if needed)
df = pd.read_csv(text_data_path, sep='\t')  # Adjust delimiter if required

# 2. Merge shapefile with text data
merged_gdf = gdf.merge(
    df, 
    on="Bazeh_Code",
    how="left"  # Keeps all shapes even if no matching label
)

# 3. Plot the map with labels
fig, ax = plt.subplots(figsize=(12, 10))

# Base map with colored polygons
plot = merged_gdf.plot(
    ax=ax,
    column="PERCENT_VALUE",
    cmap="hot_r",
    edgecolor="black",
    linewidth=0.3
)

# Add combined labels (Bazeh_Code + PERCENT_VALUE)
for idx, row in merged_gdf.iterrows():
    centroid = row.geometry.centroid
    label = f"{row['Bazeh_Code']}\n{row['PERCENT_VALUE']}%"  # Two-line label
    
    ax.text(
        centroid.x,
        centroid.y,
        label,
        fontsize=8,  # Slightly smaller font for two lines
        ha='center',
        va='center',
        bbox=dict(
            facecolor='white',
            alpha=0.8,
            edgecolor='none',
            boxstyle='round,pad=0.2'
        )
    )

# 4. Add a small colorbar inside the map, slightly higher
norm = Normalize(vmin=merged_gdf['PERCENT_VALUE'].min(), vmax=merged_gdf['PERCENT_VALUE'].max())
sm = ScalarMappable(cmap='hot_r', norm=norm)
cbar = fig.colorbar(
    sm, 
    ax=ax, 
    shrink=0.3,  # Small size
    aspect=10,   # Adjust width
    location='right',
    pad=-0.09,    # Reduced padding to move it up
    fraction=0.046,  # Size relative to axes
    anchor=(0.5, 0.1)  # Centered horizontally, slightly higher vertically
)
cbar.set_label('Percent Value (%)', fontsize=10)

# 5. Customize the plot
plt.title("Percentage Values by Region with Bazeh Codes", fontsize=14)

# Set x and y axis labels to show degrees
ax.set_xlabel("Longitude (°)", fontsize=12)
ax.set_ylabel("Latitude (°)", fontsize=12)

# Set grid and customize ticks
plt.grid(linestyle='--', alpha=0.5)

# Save the plot to a file
plt.savefig("percentage_values_by_region.png", dpi=300, bbox_inches='tight')  # Save as PNG with 300 DPI