import re
import tkinter as tk
from tkinter import filedialog, simpledialog

def extract_third_real_number(trigger_string):
    pattern = re.compile(r'[-+]?\d*\.\d+|[-+]?\d+')
    extracting = False
    line_number = -1
    step = None
    minp = None
    maxp = None

    # GUI setup
    root = tk.Tk()
    root.withdraw()

    # Select input file
    input_path = filedialog.askopenfilename(title="Select Input File", filetypes=[("Text Files", "*.REN")])
    if not input_path:
        print("No input file selected.")
        return

    # Select output file
    output_path = filedialog.asksaveasfilename(title="Save Output File As", defaultextension=".ini",
                                                filetypes=[("Text Files", "*.ini")])
    if not output_path:
        print("No output file selected.")
        return

    # Ask for axis name
    axis_name = simpledialog.askstring("Axis Name", "Enter axis name (1–2 letters):")
    if not axis_name or not axis_name.isalpha() or len(axis_name) > 2:
        print("Invalid axis name.")
        return

    # First pass: extract step, minp, maxp
    with open(input_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            if "Compensation spacing" in line:
                match = pattern.search(line)
                if match:
                    step = match.group()

            elif "Compensation start" in line:
                match = pattern.search(line)
                if match:
                    minp = match.group()

            elif "Compensation end" in line:
                match = pattern.search(line)
                if match:
                    maxp = match.group()

    # Check if all values were found
    if step is None or minp is None or maxp is None:
        print("Missing one or more compensation values in the file.")
        return

    # Second pass: extract data after trigger and write output
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:

        outfile.write("CHANDATA(1)\n")

        for line in infile:
            if not extracting:
                if trigger_string in line:
                    extracting = True
                continue

            numbers = pattern.findall(line)
            if len(numbers) >= 3:
                line_number += 1
                third_number = numbers[2]
                outfile.write(f"$AA_ENC_COMP[1,{line_number},{axis_name.upper()}]  {third_number}\n")

        # Write footer using the values extracted above
        outfile.write(f"$AA_ENC_COMP_STEP[1,{axis_name.upper()}]  {step}\n")
        outfile.write(f"$AA_ENC_COMP_MIN[1,{axis_name.upper()}]  {minp}\n")
        outfile.write(f"$AA_ENC_COMP_MAX[1,{axis_name.upper()}]  {maxp}\n")
        outfile.write(f"$AA_ENC_COMP_IS_MODULO[1,{axis_name.upper()}]  0\n")
        outfile.write("m0\n")
        outfile.write("m30\n")
        outfile.write("M17\n")

    print(f"Extraction complete. Output saved to: {output_path}")

# Run the extractor
extract_third_real_number(trigger_string='No.     Axis position        Combined')
