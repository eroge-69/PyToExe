import tkinter as tk
from tkinter import messagebox, simpledialog
import pyperclip
import base64

# Hidden Watermark
__unique_id__ = "WM_Tomas_Alexandre_2025_Escavamos"
encoded_watermark = base64.b64encode(__unique_id__.encode()).decode()

def parse_postcode_range(postcode_range):
    try:
        start, end = postcode_range.split('-')
        return [str(i) for i in range(int(start.strip()), int(end.strip()) + 1)]
    except:
        messagebox.showerror("Error", "Invalid postcode range format. Use 'start - end'.")
        return []

def generate_output():
    origin_country = simpledialog.askstring("Origin Country", "Enter 2-digit origin country:").upper()
    delivery_country = simpledialog.askstring("Delivery Country", "Enter 2-digit delivery country:").upper()
    
    origin_zones = []
    count = int(simpledialog.askstring("Origin Zones", f"How many origin zones for {origin_country}?"))
    for i in range(count):
        zone_name = f"{origin_country}{i+1:02d}"
        raw_input = simpledialog.askstring("Origin Postcodes", f"Postcodes for {zone_name} (comma separated, ranges allowed):")
        postcodes = []
        for p in raw_input.split(','):
            if ' - ' in p:
                postcodes.extend(parse_postcode_range(p))
            else:
                postcodes.append(p.strip())
        origin_zones.append((zone_name, postcodes))

    delivery_zones = []
    count = int(simpledialog.askstring("Delivery Zones", f"How many delivery zones for {delivery_country}?"))
    for i in range(count):
        zone_name = f"{delivery_country}{i+1:02d}"
        raw_input = simpledialog.askstring("Delivery Postcodes", f"Postcodes for {zone_name} (comma separated, ranges allowed):")
        postcodes = []
        for p in raw_input.split(','):
            if ' - ' in p:
                postcodes.extend(parse_postcode_range(p))
            else:
                postcodes.append(p.strip())
        delivery_zones.append((zone_name, postcodes))

    repeat_count = int(simpledialog.askstring("Repeat Count", "How many times to repeat each value?"))
    
    output_data = []
    for o_zone, o_postcodes in origin_zones:
        for o_pc in o_postcodes:
            for d_zone, d_postcodes in delivery_zones:
                for d_pc in d_postcodes:
                    result = f"{origin_country}_{o_pc}_{delivery_country}_{d_pc} \t {d_zone}"
                    output_data.extend([result] * repeat_count)

    with open("output.txt", "w") as f:
        f.write("\n".join(output_data))
        f.write(f"\n# Watermark (Encoded): {encoded_watermark}")

    pyperclip.copy("\n".join(output_data))
    messagebox.showinfo("Done", "✅ Output saved to output.txt and copied to clipboard!")

root = tk.Tk()
root.withdraw()
generate_output()
