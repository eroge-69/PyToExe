import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import re


def extract_patch_numbers(element):
    patch_numbers = set()
    for e in element.iter():
        if e.text:
            # Look for 'Patch_XXX' in paths
            matches = re.findall(r'Patch_(\d{1,4})', e.text)
            patch_numbers.update(matches)
    return sorted(patch_numbers, key=lambda x: int(x))

#def extract_patch_numbers(element):
 #   patch_numbers = set()
  #  for e in element.iter():
   #     if e.text:
    #        matches = re.findall(r'\b\d{1,4}\b', e.text)
     #       patch_numbers.update(matches)
    #return sorted(patch_numbers, key=lambda x: int(x))

def find_install_path(element):
    for e in element.iter():
        if e.tag.lower() == 'installpath' and e.text:
            return e.text.strip()
        if e.text and 'Postilion' in e.text:
            return e.text.strip()
    return '—'

def parse_applications(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError:
        raise ValueError("The selected file is not a valid XML file.")

    apps = []

    for app in root.iter():
        name = app.findtext('name')
        version = app.findtext('version')

        if name and version:
            patches = extract_patch_numbers(app)
            path = find_install_path(app)
            apps.append({
                'name': name.strip(),
                'version': version.strip(),
                'path': path,
                'patches': ', '.join(patches) if patches else '—'
            })

    return apps

def generate_html(apps, output_file='application_summary.html'):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n<html lang="en">\n<head><meta charset="UTF-8"><title>Application Summary</title></head>\n<body>\n')
        f.write('<h2>Application Summary</h2>\n<table border="1" cellspacing="0" cellpadding="5">\n')
        f.write('<tr><th>Application Name</th><th>Version(s)</th><th>Patch Numbers</th><th>Install Path</th></tr>\n')

        for app in apps:
            f.write(f"<tr><td>{app['name']}</td><td>{app['version']}</td><td>{app['patches']}</td><td>{app['path']}</td></tr>\n")

        f.write('</table>\n</body></html>')

def run_app():
    file_path = filedialog.askopenfilename(title="Select an XML file")
    if not file_path:
        return
    try:
        apps = parse_applications(file_path)
        generate_html(apps)
        messagebox.showinfo("Success", "HTML summary generated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate summary: {e}")

# GUI setup
root = tk.Tk()
root.title("Application Summary Generator")
root.geometry("300x150")

label = tk.Label(root, text="Select an XML file to generate application summary")
label.pack(pady=10)

button = tk.Button(root, text="Browse and Generate", command=run_app)
button.pack(pady=20)

root.mainloop()