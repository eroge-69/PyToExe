import os
import csv
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict

# GUI wrapper for PyInstaller
# > pip install auto-py-to-exe
# > auto-py-to-exe

def select_folder_and_ask_indices():
    # Hide the main tkinter window (only show dialog)
    root = tk.Tk()
    root.withdraw()

    # Folder selection dialog
    print("📂 Please select the folder with the *.csv files")
    folder_selected = filedialog.askdirectory(title="📂 Please select the folder with the *.csv files")
    if not folder_selected:
        print("  ❌ No folder selected. Exiting program.")
        exit(1)

    print(f"  ✅ Selected folder: {folder_selected}")

    # Ask for start and end indices via console input
    while True:
        try:
            start_index = int(input("➡️  Enter start index (e.g., 30): "))
            end_index = int(input("➡️  Enter  end  index (e.g., 32): "))
            if start_index > end_index:
                print("⚠️  Start index cannot be greater than end index. Please try again.")
                continue
            break
        except ValueError:
            print("⚠️  Please enter valid integer numbers.")

    print("")

    return folder_selected, start_index, end_index

def process_n2kdecoded(input_file, output_file):
    """
    Process CSV:
    - Make headers unique
    - Filter allowed columns only
    - Filter rows by allowed PGNs
    """
    allowed_pgns = {"127488", "127489", "127493", "127496", "127501", "127505",
                    "127506", "127508", "127751", "128275", "129026", "129029",
                    "130310", "130316"}

    allowed_columns = {
        "Time", "Type", "PGN", "Name", "Src", "Dest", "Pri", "Size",             # default
        "Engine Speed",                                                          # PGN 127488 Engine Parameters, Rapid Update
        "Engine temp.", "Total engine hours", "Percent Engine Torque",           # PGN 127489 Engine Parameters, Dynamic
        "Transmission Gear",                                                     # PGN 127493 Transmission Parameters, Dynamic
        "Distance to Empty /Fuel Range",                                         # PGN 127496 Trip Fuel Consumption, Vessel
        "Binary Device Bank Instance", *["Status "+str(i) for i in range(1,29)], # PGN 127501 Binary Status Report
        "Fluid Level",                                                           # PGN 127505 Fluid Level
        "State of Charge",                                                       # PGN 127506 DC Detailed Status
        "Battery Voltage", "Battery Current", "Battery Case Temperature",        # PGN 127508 Battery Status
        "DC Voltage", "DC Current",                                              # PGN 127751 DC Voltage / Current
        "Total Cumulative Distance", "Distance Since Last Reset",                # PGN 128275 Distance Log
        "Course Over Ground", "Speed Over Ground",                               # PGN 129026 COG & SOG, Rapid Update
        "Position date", "Position time", "Latitude", "Longitude",               # PGN 129029 GNSS Position Data
        "Water Temp",                                                            # PGN 130310 Environmental Parameters - DEPRECATED
        "Temperature Instance", "Actual Temperature"                             # PGN 130316 Temperature, Extended Range
    }

    if not os.path.isfile(input_file):
        print(f"❌ Input file '{input_file}' does not exist.")
        return

    print(f"    📥 Reading '{input_file}' and processing...")

    try:
        with open(input_file, mode='r', newline='') as infile:
            reader = csv.reader(infile)
            try:
                original_headers = next(reader)
            except StopIteration:
                print("❌ Input file is empty.")
                return

            # Make headers unique
            seen = defaultdict(int)
            headers_unique = []
            header_map = {}
            for idx, header in enumerate(original_headers):
                clean_header = header.strip()
                count = seen[clean_header]
                new_header = clean_header if count == 0 else f"{clean_header} {count}"
                seen[clean_header] += 1
                headers_unique.append(new_header)
                header_map[new_header] = idx

            # Filter headers to allowed columns only
            filtered_headers = [h for h in headers_unique if h in allowed_columns]

            if "PGN" not in filtered_headers:
                print("❌ Required column 'PGN' missing after filtering.")
                return

            keep_indices = [header_map[h] for h in filtered_headers]
            pgn_idx = filtered_headers.index("PGN")

            with open(output_file, mode='w', newline='') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(filtered_headers)
                count_in = 0
                count_out = 0

                for line_num, row in enumerate(reader, start=2):
                    count_in += 1
                    row += [""] * (len(headers_unique) - len(row))
                    filtered_row = [row[i] for i in keep_indices]
                    pgn_value = filtered_row[pgn_idx].strip()
                    if pgn_value not in allowed_pgns:
                        continue
                    writer.writerow(filtered_row)
                    count_out += 1

        print(f"      ✅ Processed {count_in} rows, kept {count_out} rows. Output: '{output_file}'")

    except Exception as e:
        print(f"❌ Error processing file: {e}")

def process_n2k(input_file, output_file):
    """
    Process input CSV by:
    - Expanding 'Data' column into Data0..Data7
    - Calculate HV_DC_V and HV_DC_C from data bytes
    - Remove Data0..Data7, add HV_DC_V and HV_DC_C
    """

    if not os.path.isfile(input_file):
        print(f"❌ Input file '{input_file}' does not exist.")
        return

    print(f"    📥 Reading '{input_file}' and processing data bytes...")

    try:
        with open(input_file, mode='r', newline='') as infile, \
             open(output_file, mode='w', newline='') as outfile:

            reader = csv.reader(infile)
            try:
                header = next(reader)
            except StopIteration:
                print("❌ Input file is empty.")
                return

            if 'Data' in header:
                data_idx = header.index('Data')
                header = header[:data_idx] + [f'Data{i}' for i in range(8)] + header[data_idx+1:]

            # Prepare output headers: remove Data0..Data7, add HV_DC_V and HV_DC_C
            fieldnames_out = [h for h in header if not h.startswith('Data')]
            fieldnames_out += ['HV_DC_V', 'HV_DC_C']

            writer = csv.DictWriter(outfile, fieldnames=fieldnames_out)
            writer.writeheader()

            count_rows = 0
            for line_num, row in enumerate(reader, start=2):
                count_rows += 1
                if len(row) < len(header):
                    row += [''] * (len(header) - len(row))
                elif len(row) > len(header):
                    row = row[:len(header)]

                row_dict = dict(zip(header, row))

                data_bytes = []
                for i in range(8):
                    val = row_dict.get(f'Data{i}', '0')
                    try:
                        data_bytes.append(int(val))
                    except ValueError:
                        data_bytes.append(0)

                voltage_raw = (data_bytes[3] << 8) | data_bytes[2]
                current_raw = (data_bytes[6] << 16) | (data_bytes[5] << 8) | data_bytes[4]
                if current_raw & 0x800000:
                    current_raw -= 0x1000000

                row_dict['HV_DC_V'] = round(voltage_raw / 10, 2)
                row_dict['HV_DC_C'] = round(current_raw / 100, 2)

                for i in range(8):
                    row_dict.pop(f'Data{i}', None)

                filtered_row = {k: row_dict.get(k, '') for k in fieldnames_out}
                writer.writerow(filtered_row)

        print(f"      ✅ Processed {count_rows} rows. Output: '{output_file}'")

    except Exception as e:
        print(f"❌ Error processing file: {e}")

def update_dc_current(file_n2kdecoded, file_n2k, output_file):
    """
    Update 'DC Current' in n2kdecoded data based on matching rows from n2k file.
    """
    key_fields = ["Time", "Type", "PGN", "Name", "Src", "Dest", "Pri", "Size"]

    if not os.path.isfile(file_n2kdecoded) or not os.path.isfile(file_n2k):
        print(f"❌ One or both input files do not exist: '{file_n2kdecoded}', '{file_n2k}'")
        return

    print(f"    🔄 Updating DC Current using '{file_n2kdecoded}' and '{file_n2k}'...")

    with open(file_n2kdecoded, newline='') as fa:
        reader_a = csv.DictReader(fa)
        data_a = list(reader_a)
        headers_a = reader_a.fieldnames

    with open(file_n2k, newline='') as fb:
        reader_b = csv.DictReader(fb)
        data_b = list(reader_b)

    b_lookup = defaultdict(list)
    for row in data_b:
        key = tuple(row.get(k, '').strip() for k in key_fields)
        b_lookup[key].append(row)

    updated_count = 0
    for row_a in data_a:
        key = tuple(row_a.get(k, '').strip() for k in key_fields)
        matches = b_lookup.get(key, [])

        dc_voltage_a = row_a.get("DC Voltage", "").strip()

        for b_row in matches:
            hv_voltage = b_row.get("HV_DC_V", "").strip()
            if dc_voltage_a == hv_voltage:
                row_a["DC Current"] = b_row.get("HV_DC_C", "")
                updated_count += 1
                break

    with open(output_file, mode='w', newline='') as fo:
        writer = csv.DictWriter(fo, fieldnames=headers_a)
        writer.writeheader()
        writer.writerows(data_a)

    print(f"      ✅ Updated DC Current in {updated_count} rows. Output: '{output_file}'")

def merge_all_combined_outputs(folder, output_file):
    """
    Merge all 'combined_output_*.csv' files:
    - Add missing columns with empty values
    - Remove unwanted columns
    - Keep consistent column order
    """

    wanted_columns = [
        "Time","Type","PGN","Name","Src","Dest","Pri","Size","Engine Speed","Transmission Gear",
        "Engine temp.","Total engine hours","Percent Engine Torque","Course Over Ground","Speed Over Ground",
        "Total Cumulative Distance","Distance Since Last Reset","Water Temp","Binary Device Bank Instance",
        *["Status "+str(i) for i in range(1,29)],
        "Position date","Position time","Latitude","Longitude","Temperature Instance","Actual Temperature",
        "Distance to Empty /Fuel Range","Battery Voltage","Battery Current","Battery Case Temperature","Fluid Level",
        "State of Charge","DC Voltage","DC Current"
    ]

    print(f"  📂 Merging all 'combined_output_*.csv' files from '{folder}'...")

    merged_data = []

    for filename in sorted(os.listdir(folder)):
        if filename.startswith("combined_output_") and filename.endswith(".csv"):
            filepath = os.path.join(folder, filename)
            with open(filepath, newline='') as f:
                reader = csv.DictReader(f)
                rows_count = 0
                for row in reader:
                    filtered_row = {col: row.get(col, '') for col in wanted_columns}
                    merged_data.append(filtered_row)
                    rows_count += 1
                print(f"    🔹 Loaded {rows_count} rows from '{filename}'")

    if merged_data:
        with open(output_file, mode='w', newline='') as fo:
            writer = csv.DictWriter(fo, fieldnames=wanted_columns)
            writer.writeheader()
            writer.writerows(merged_data)
        print(f"    ✅ Merged total {len(merged_data)} rows into '{output_file}'")
    else:
        print("⚠️  No 'combined_output_*.csv' files found to merge.")

def batch_process_and_merge(start_index, end_index, folder='.'):
    """
    Batch process files from start_index to end_index:
    - Process n2kdecoded and n2k files
    - Update DC current
    - Merge all combined output files into final CSV
    """
    print(f"🚀 Starting batch processing from {start_index} to {end_index} in '{folder}'")

    for i in range(start_index, end_index + 1):
        suffix = f"{i:03}"
        base_name = f"000000_{suffix}"
        n2kdecoded_file = os.path.join(folder, f"{base_name}.n2kdecoded.csv")
        n2k_file = os.path.join(folder, f"{base_name}.n2k.csv")

        out_decoded = os.path.join(folder, f"output_{suffix}.n2kdecoded.csv")
        out_n2k = os.path.join(folder, f"output_{suffix}.n2k.csv")
        combined_output = os.path.join(folder, f"combined_output_{suffix}.csv")

        if os.path.exists(n2kdecoded_file):
            print(f"  📁 Processing file pair {base_name}")
            process_n2kdecoded(n2kdecoded_file, out_decoded)

            if os.path.exists(n2k_file):
                process_n2k(n2k_file, out_n2k)
                update_dc_current(out_decoded, out_n2k, combined_output)
            else:
                print(f"    ⚠️  File '{n2k_file}' not found, skipping n2k processing and DC Current update.")
        else:
            print(f"  ⚠️  Missing files for {base_name}, skipping.")

    final_output = os.path.join(folder, "final_merged_output.csv")
    merge_all_combined_outputs(folder, final_output)

    print("🏁 Batch processing completed.")

if __name__ == '__main__':
    folder, start_idx, end_idx = select_folder_and_ask_indices()
    batch_process_and_merge(start_index=start_idx, end_index=end_idx, folder=folder)

    #process_n2kdecoded('000000_022.n2kdecoded.csv', 'output.n2kdecoded.csv')
    #process_n2k('000000_022.n2k.csv', 'output.n2k.csv')
    #update_dc_current("output.n2kdecoded.csv", "output.n2k.csv", "combined_output.csv")