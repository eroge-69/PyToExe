```python
#!/usr/bin/env python3
"""
FiveM Timecycle Editor (Python)
A general-purpose editor to open, inspect, and edit Timecycle-like files commonly used with FiveM/GTA V mods.
This script does NOT decompile an .exe. Instead it provides a working Python-based editor that:
 - Opens XML, JSON, INI (ConfigParser), or plain text files
 - Displays a navigable tree for XML/JSON and editable key/value pairs
 - Provides a raw text editor for unsupported/binary formats
 - Allows search, replace, and save-as
 - Exports JSON <-> XML conversions (best-effort)
 - Lightweight Tkinter GUI (no external dependencies)

Usage:
    python timecycle_editor.py

Note:
 - This is a best-effort editor for mod configuration/timecycle data. If your binary/exe embeds resources,
   you'd still need reverse-engineering tools to extract original source/code.
"""
import sys
import os
import json
import traceback
import configparser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
from io import StringIO

# ---------- Utilities ----------

def detect_format(path, data=None):
    """Guess file format from extension/content. returns 'json','xml','ini','text'."""
    _, ext = os.path.splitext(path or "")
    ext = ext.lower()
    if ext in ('.json',):
        return 'json'
    if ext in ('.xml', '.ymt'):
        return 'xml'
    if ext in ('.ini', '.cfg', '.conf'):
        return 'ini'
    # try sniffing content
    sample = data if data is not None else ''
    if isinstance(sample, bytes):
        try:
            sample = sample.decode('utf-8', errors='ignore')
        except:
            return 'text'
    s = (sample or '')[:2048].lstrip()
    if not s:
        return 'text'
    if s.startswith('{') or s.startswith('['):
        return 'json'
    if s.startswith('<'):
        return 'xml'
    if '=' in s or '\n[' in s:
        # heuristics for ini
        return 'ini'
    return 'text'

def xml_to_dict(elem):
    """Convert xml.etree.ElementTree.Element to nested dict (simple)."""
    d = {}
    # attributes
    if elem.attrib:
        d['@attrs'] = dict(elem.attrib)
    # text
    text = (elem.text or '').strip()
    if text:
        d['#text'] = text
    # children
    for child in elem:
        tag = child.tag
        child_dict = xml_to_dict(child)
        if tag in d:
            # convert to list
            if not isinstance(d[tag], list):
                d[tag] = [d[tag]]
            d[tag].append(child_dict)
        else:
            d[tag] = child_dict
    return d

def dict_to_xml(d, tag='root'):
    """Convert a simple dict to an xml Element."""
    elem = ET.Element(tag)
    if not isinstance(d, dict):
        elem.text = str(d)
        return elem
    # attributes
    attrs = d.get('@attrs', {})
    for k,v in attrs.items():
        elem.set(k, str(v))
    # text
    if '#text' in d:
        elem.text = str(d['#text'])
    for k,v in d.items():
        if k in ('@attrs', '#text'):
            continue
        if isinstance(v, list):
            for item in v:
                elem.append(dict_to_xml(item, k))
        else:
            elem.append(dict_to_xml(v, k))
    return elem

# ---------- Parsers ----------

def parse_json(text):
    return json.loads(text)

def dump_json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)

def parse_xml(text):
    root = ET.fromstring(text)
    return root

def dump_xml(elem):
    # pretty print
    def indent(e, level=0):
        i = "\n" + level*"  "
        if len(e):
            if not e.text or not e.text.strip():
                e.text = i + "  "
            for child in e:
                indent(child, level+1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        if level and (not e.tail or not e.tail.strip()):
            e.tail = i
    indent(elem)
    return ET.tostring(elem, encoding='unicode')

# ---------- Main Application ----------

class TimecycleEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FiveM Timecycle Editor")
        self.geometry("800x600")

        self.filepath = None
        self.fileformat = None
        self.data = None

        self.create_widgets()

    def create_widgets(self):
        # Menu
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Save As", command=self.save_file_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

        # Paned window
        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Treeview for JSON/XML/INI
        self.tree = ttk.Treeview(paned)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        paned.add(self.tree, weight=1)

        # Text editor for raw text or editing values
        self.text = tk.Text(paned, wrap=tk.NONE)
        paned.add(self.text, weight=3)

        # Status bar
        self.status = tk.Label(self, text="Ready", anchor=tk.W)
        self.status.pack(fill=tk.X)

    def open_file(self):
        path = filedialog.askopenfilename(title="Open File", filetypes=[
            ("All files", "*.*"),
            ("JSON files", "*.json"),
            ("XML files", "*.xml;*.ymt"),
            ("INI files", "*.ini;*.cfg;*.conf"),
            ("Text files", "*.txt"),
        ])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            fmt = detect_format(path, content)
            self.filepath = path
            self.fileformat = fmt
            self.load_content(content, fmt)
            self.status.config(text=f"Opened {os.path.basename(path)} as {fmt.upper()}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")
            self.status.config(text="Error opening file")

    def load_content(self, content, fmt):
        self.tree.delete(*self.tree.get_children())
        self.text.delete('1.0', tk.END)
        self.data = None
        if fmt == 'json':
            try:
                obj = parse_json(content)
                self.data = obj
                self.build_tree_json(obj)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to parse JSON:\n{e}")
                self.text.insert('1.0', content)
        elif fmt == 'xml':
            try:
                root = parse_xml(content)
                self.data = root
                self.build_tree_xml(root)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to parse XML:\n{e}")
                self.text.insert('1.0', content)
        elif fmt == 'ini':
            try:
                config = configparser.ConfigParser()
                config.read_string(content)
                self.data = config
                self.build_tree_ini(config)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to parse INI:\n{e}")
                self.text.insert('1.0', content)
        else:
            self.text.insert('1.0', content)

    def build_tree_json(self, obj, parent=''):
        if isinstance(obj, dict):
            for k, v in obj.items():
                node = self.tree.insert(parent, 'end', text=str(k), open=True)
                self.build_tree_json(v, node)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                node = self.tree.insert(parent, 'end', text=f"[{i}]", open=True)
                self.build_tree_json(item, node)
        else:
            self.tree.insert(parent, 'end', text=str(obj))

    def build_tree_xml(self, elem, parent=''):
        text = elem.tag
        if elem.attrib:
            text += " " + " ".join(f'{k}="{v}"' for k,v in elem.attrib.items())
        node = self.tree.insert(parent, 'end', text=text, open=True)
        if elem.text and elem.text.strip():
            self.tree.insert(node, 'end', text=elem.text.strip())
        for child in elem:
            self.build_tree_xml(child, node)

    def build_tree_ini(self, config):
        for section in config.sections():
            node = self.tree.insert('', 'end', text=section, open=True)
            for key, val in config.items(section):
