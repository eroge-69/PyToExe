import os
import math
import csv
import pandas as pd
import easygui

# input from user
offset_ft = easygui.enterbox("Enter Offset in Feet from Center", 
                             "Offset",
                             6)

#convert input to double/float
offset_ft = float(offset_ft)

input_path = easygui.fileopenbox(title="Select the Center TSM Beam Point")

# load csv
print("Loading CSV file...")
try:
    data = pd.read_csv(input_path)
    print("File loaded successfully.")
except:
    print("Could not load the file. Please check the file path.")

# convert rot angfrom degrees to radians
print("Converting rotation angles to radians...")
data["rad"] = data["Rotation"].apply(lambda x: math.radians(x))

# calc direction vectors (up/north and right/east)
print("Calculating heading vectors...")
data["v_x"] = data["rad"].apply(lambda x: math.sin(x))  # e
data["v_y"] = data["rad"].apply(lambda x: math.cos(x))  # n

# def directions and their offset cals
print("Defining direction offsets...")
direction_list = ["NORTH", "SOUTH", "EAST", "WEST"]
suffix_dict = {
    "NORTH": "_N",
    "SOUTH": "_S",
    "EAST": "_E",
    "WEST": "_W"
}

# Create output directory info
output_folder = os.path.dirname(input_path)
file_name = os.path.basename(input_path)
file_base = os.path.splitext(file_name)[0]

# Go through each direction
for direction in direction_list:
    print("Processing direction:", direction)

    # Make a copy of the data
    copy_data = data.copy()

    dx_values = []
    dy_values = []

    # Loop through each row to calculate offset
    for index, row in copy_data.iterrows():
        if direction == "NORTH":
            dx = row["v_x"] * offset_ft
            dy = row["v_y"] * offset_ft
        elif direction == "SOUTH":
            dx = -row["v_x"] * offset_ft
            dy = -row["v_y"] * offset_ft
        elif direction == "EAST":
            dx = row["v_y"] * offset_ft
            dy = -row["v_x"] * offset_ft
        elif direction == "WEST":
            dx = -row["v_y"] * offset_ft
            dy = row["v_x"] * offset_ft

        dx_values.append(dx)
        dy_values.append(dy)

    # Add dx, dy to the dataframe
    copy_data["dx"] = dx_values
    copy_data["dy"] = dy_values

    # Update positions
    copy_data["Position X"] = copy_data["Position X"] + copy_data["dx"]
    copy_data["Position Y"] = copy_data["Position Y"] + copy_data["dy"]

    # Add output columns
    copy_data["Column / Cell ID"] = copy_data["PTNO"].astype(
        str) + suffix_dict[direction]
    copy_data["Easting / X"] = copy_data["Position X"]
    copy_data["Northing / Y"] = copy_data["Position Y"]
    # Set elevation to zero so the daqin can work
    copy_data["Elevation / Z"] = 0.0

    # Select final output columns
    result = copy_data[[
        "Column / Cell ID",
        "Easting / X",
        "Northing / Y",
        "Elevation / Z",
        "Rotation"
    ]]

    # Save to CSV
    output_file = os.path.join(
        output_folder, file_base + "_" + direction + ".csv")
    result.to_csv(
        output_file,
        index=False,
        header=True,
        encoding="utf-8-sig",
        quoting=csv.QUOTE_MINIMAL,
        float_format="%.6f"
    )

    print("Saved:", output_file)

print("Done.")
