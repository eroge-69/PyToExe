import os
import subprocess
import xml.etree.ElementTree as ET
from tkinter import *
from tkinter import ttk, messagebox, simpledialog, filedialog
import socket
import datetime
import platform
import threading

ADDRESSBOOK_PATH = r"C:\LIMSY\VNCremote\addressbook.xml"
SETTINGS_PATH = r"C:\LIMSY\VNCremote\SetPath.xml"
DEFAULT_PORT = 5900
DEFAULT_VNC_PATH = r"C:\Program Files\TightVNC\tvnviewer.exe"

OFFICE_365_THEMES = [
    "Colorful", "Dark Gray", "Black", "White", "Blue-Gray", "Light Blue",
    "Orange", "Green", "Red", "Purple"
]

class ThemeDialog(simpledialog.Dialog):
    def body(self, master):
        Label(master, text="Select Theme:").pack(pady=5)
        self.theme_var = StringVar(value=OFFICE_365_THEMES[0])
        self.dropdown = ttk.Combobox(master, textvariable=self.theme_var, values=OFFICE_365_THEMES, state="readonly")
        self.dropdown.pack(pady=5)
        return self.dropdown

    def apply(self):
        self.result = self.theme_var.get()

class HostStatusDialog(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Check Host Status")
        self.geometry("500x300")
        self.resizable(False, False)

        self.host_var = StringVar()
        Label(self, text="Enter IP or Hostname:").pack(pady=5)
        Entry(self, textvariable=self.host_var).pack(fill=X, padx=10)
        btn_frame = Frame(self)
        btn_frame.pack(pady=5)
        Button(btn_frame, text="Check", command=self.run_checks).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Close", command=self.destroy).pack(side=LEFT, padx=5)

        self.log_area = Text(self, height=10, wrap=WORD)
        self.log_area.pack(fill=BOTH, padx=10, pady=5, expand=True)

    def log(self, msg):
        self.log_area.insert(END, msg + "\n")
        self.log_area.see(END)

    def run_checks(self):
        host = self.host_var.get().strip()
        if not host:
            self.log("Host/IP is required.")
            return
        self.log(f"Checking status for {host}...")
        threading.Thread(target=self._run_checks, args=(host,), daemon=True).start()

    def _run_checks(self, host):
        try:
            self.log("Pinging...")
            count_flag = "-n" if platform.system() == "Windows" else "-c"
            ping = subprocess.run(["ping", count_flag, "1", host], capture_output=True, text=True)
            self.log(ping.stdout.strip())

            self.log("Running nslookup...")
            ns = subprocess.run(["nslookup", host], capture_output=True, text=True)
            self.log(ns.stdout.strip())

            self.log("Scanning ports (22, 80, 443, 3389)...")
            for port in [22, 80, 443, 3389]:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex((host, port))
                    status = "Open" if result == 0 else "Closed"
                    self.log(f"Port {port}: {status}")

            self.log("Checking AD last logon (mocked)...")
            self.log(f"Last AD logon time for {host}: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Mock)")

        except Exception as e:
            self.log(f"Error: {e}")

def export_addressbook():
    dest_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML Files", "*.xml")])
    if dest_path:
        try:
            if os.path.exists(ADDRESSBOOK_PATH):
                with open(ADDRESSBOOK_PATH, "rb") as src, open(dest_path, "wb") as dst:
                    dst.write(src.read())
                messagebox.showinfo("Export", "Address book exported successfully.")
            else:
                messagebox.showerror("Error", "No address book file found to export.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

def import_addressbook(app):
    src_path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
    if src_path:
        try:
            with open(src_path, "rb") as src, open(ADDRESSBOOK_PATH, "wb") as dst:
                dst.write(src.read())
            app.load_addressbook()
            messagebox.showinfo("Import", "Address book imported successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import: {e}")

def open_log_history():
    folder = os.path.dirname(ADDRESSBOOK_PATH)
    log_file = os.path.join(folder, "log.txt")
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("Log History\n")
    try:
        os.startfile(log_file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open log file: {e}")

def relocate_addressbook():
    global ADDRESSBOOK_PATH
    new_folder = filedialog.askdirectory(title="Select Address Book Folder")
    if new_folder:
        ADDRESSBOOK_PATH = os.path.join(new_folder, "addressbook.xml")
        messagebox.showinfo("Relocated", f"Address book path updated to:\n{ADDRESSBOOK_PATH}")

class AddComputerDialog(simpledialog.Dialog):
    def __init__(self, parent, group_name):
        self.group_name = group_name
        super().__init__(parent, f"Add Computer to '{group_name}'")

    def body(self, master):
        Label(master, text="Computer Name:").grid(row=0, column=0, sticky=E)
        Label(master, text="IP / Hostname:").grid(row=1, column=0, sticky=E)
        Label(master, text="Port:").grid(row=2, column=0, sticky=E)

        self.name_var = StringVar()
        self.host_var = StringVar()
        self.port_var = StringVar(value=str(DEFAULT_PORT))

        Entry(master, textvariable=self.name_var).grid(row=0, column=1)
        Entry(master, textvariable=self.host_var).grid(row=1, column=1)
        Entry(master, textvariable=self.port_var).grid(row=2, column=1)

        return master

    def validate(self):
        if not self.name_var.get().strip():
            messagebox.showerror("Input Error", "Computer name is required.")
            return False
        if not self.host_var.get().strip():
            messagebox.showerror("Input Error", "IP/Hostname is required.")
            return False
        if not self.port_var.get().isdigit() or not (1 <= int(self.port_var.get()) <= 65535):
            messagebox.showerror("Input Error", "Port must be a number between 1 and 65535.")
            return False
        return True

    def apply(self):
        self.result = {
            "name": self.name_var.get().strip(),
            "host": self.host_var.get().strip(),
            "port": int(self.port_var.get())
        }

class VNCAddressBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VNC Address Book")
        self.vnc_path = DEFAULT_VNC_PATH

        self.create_menu()
        self.create_widgets()
        self.addressbook = {"groups": {}}
        self.load_addressbook()
        self.load_vnc_path()

    def create_menu(self):
        menubar = Menu(self.root)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export Addressbook", command=export_addressbook)
        file_menu.add_command(label="Import Addressbook", command=lambda: import_addressbook(self))
        file_menu.add_command(label="Re-locate Addressbook Folder", command=relocate_addressbook)
        file_menu.add_command(label="Change Theme", command=self.change_theme)
        file_menu.add_command(label="Log History", command=open_log_history)
        file_menu.add_command(label="Check Host Status", command=lambda: HostStatusDialog(self.root))
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def change_theme(self):
        dlg = ThemeDialog(self.root)
        if dlg.result:
            messagebox.showinfo("Theme Selected", f"You selected: {dlg.result}")
            # TODO: Apply the selected theme to your app here

    def create_widgets(self):
        paned = ttk.Panedwindow(self.root, orient=HORIZONTAL)
        paned.pack(fill=BOTH, expand=True)

        self.left_frame = ttk.Frame(paned, width=250)
        paned.add(self.left_frame, weight=1)

        self.right_frame = ttk.Frame(paned)
        paned.add(self.right_frame, weight=3)

        self.tree = ttk.Treeview(self.left_frame)
        self.tree.pack(fill=BOTH, expand=True, side=TOP)
        self.tree.heading("#0", text="Groups / Sub-Groups", anchor=W)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill=X)
        ttk.Button(btn_frame, text="Add Group", command=self.add_group).pack(side=LEFT, padx=5, pady=3)
        ttk.Button(btn_frame, text="Add Sub-Group", command=self.add_subgroup).pack(side=LEFT, padx=5, pady=3)
        ttk.Button(btn_frame, text="Remove Group", command=self.remove_group).pack(side=LEFT, padx=5, pady=3)
        ttk.Button(btn_frame, text="Edit Group", command=self.edit_group).pack(side=LEFT, padx=5, pady=3)

        self.selected_label = ttk.Label(self.right_frame, text="Select a group or sub-group")
        self.selected_label.pack(anchor=W, padx=5, pady=5)

        columns = ("Name", "Host", "Port")
        self.computer_list = ttk.Treeview(self.right_frame, columns=columns, show="headings")
        for col in columns:
            self.computer_list.heading(col, text=col)
            self.computer_list.column(col, width=150)
        self.computer_list.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.computer_list.bind("<Double-1>", self.on_computer_double_click)

        bottom_btn_frame = ttk.Frame(self.right_frame)
        bottom_btn_frame.pack(pady=5)

        self.add_computer_btn = ttk.Button(bottom_btn_frame, text="Add Computer", command=self.add_computer)
        self.add_computer_btn.pack(side=LEFT, padx=5)
        self.add_computer_btn.config(state=DISABLED)

        self.edit_computer_btn = ttk.Button(bottom_btn_frame, text="Edit Computer", command=self.edit_computer)
        self.edit_computer_btn.pack(side=LEFT, padx=5)
        self.edit_computer_btn.config(state=DISABLED)

        self.remove_computer_btn = ttk.Button(bottom_btn_frame, text="Remove Computer", command=self.remove_computer)
        self.remove_computer_btn.pack(side=LEFT, padx=5)
        self.remove_computer_btn.config(state=DISABLED)

        self.quick_connect_btn = ttk.Button(bottom_btn_frame, text="Quick Connect", command=self.quick_connect)
        self.quick_connect_btn.pack(side=LEFT, padx=5)

    def add_group(self):
        name = simpledialog.askstring("Add Group", "Enter new group name:")
        if name:
            name = name.strip()
            if name and name not in self.addressbook["groups"]:
                self.addressbook["groups"][name] = {}
                self.tree.insert("", "end", iid=name, text=name, open=True)
                self.save_addressbook()
            else:
                messagebox.showerror("Error", "Group name already exists or invalid.")

    def edit_group(self):
        selected = self.tree.selection()
        if selected:
            node_id = selected[0]
            if "/" in node_id:
                messagebox.showerror("Error", "Select a group, not a sub-group.")
                return
            new_name = simpledialog.askstring("Edit Group", "Enter new group name:", initialvalue=node_id)
            if new_name and new_name != node_id:
                new_name = new_name.strip()
                if new_name in self.addressbook["groups"]:
                    messagebox.showerror("Error", "Group name already exists.")
                    return
                self.addressbook["groups"][new_name] = self.addressbook["groups"].pop(node_id)
                self.tree.delete(node_id)
                self.tree.insert("", "end", iid=new_name, text=new_name, open=True)
                for subgroup in self.addressbook["groups"][new_name]:
                    self.tree.insert(new_name, "end", iid=f"{new_name}/{subgroup}", text=subgroup, open=True)
                self.save_addressbook()

    def add_subgroup(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a group first.")
            return
        parent_id = selected[0]
        if parent_id in self.addressbook["groups"]:
            name = simpledialog.askstring("Add Sub-Group", "Enter new sub-group name:")
            if name:
                name = name.strip()
                if name and name not in self.addressbook["groups"][parent_id]:
                    self.addressbook["groups"][parent_id][name] = []
                    self.tree.insert(parent_id, "end", iid=f"{parent_id}/{name}", text=name, open=True)
                    self.save_addressbook()
                else:
                    messagebox.showerror("Error", "Sub-group name already exists or invalid.")
        else:
            messagebox.showerror("Error", "You must select a group to add sub-group.")

    def remove_group(self):
        selected = self.tree.selection()
        if selected:
            node_id = selected[0]
            if node_id in self.addressbook["groups"]:
                if messagebox.askyesno("Remove Group", f"Are you sure you want to delete the group '{node_id}'?"):
                    self.tree.delete(node_id)
                    del self.addressbook["groups"][node_id]
                    self.save_addressbook()
                    self.computer_list.delete(*self.computer_list.get_children())
                    self.selected_label.config(text="Select a group or sub-group")

    def add_computer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a sub-group first.")
            return
        node_id = selected[0]
        if "/" not in node_id:
            messagebox.showerror("Error", "Select a sub-group to add computer.")
            return
        group, subgroup = node_id.split("/", 1)
        dlg = AddComputerDialog(self.root, f"{group}/{subgroup}")
        if dlg.result:
            comp = dlg.result
            comps = self.addressbook["groups"][group][subgroup]
            if any(c["name"] == comp["name"] or c["host"] == comp["host"] for c in comps):
                messagebox.showerror("Error", "Computer with same name or host already exists.")
                return
            comps.append(comp)
            self.save_addressbook()
            self.on_tree_select(None)

    def edit_computer(self):
        selected_item = self.computer_list.focus()
        if not selected_item:
            return
        comp_data = self.computer_list.item(selected_item)["values"]
        selected_node = self.tree.selection()
        if not selected_node:
            return
        node_id = selected_node[0]
        if "/" not in node_id:
            return
        group, subgroup = node_id.split("/", 1)
        comps = self.addressbook["groups"][group][subgroup]
        old_comp = next((c for c in comps if c["name"] == comp_data[0] and c["host"] == comp_data[1]), None)
        if not old_comp:
            return
        dlg = AddComputerDialog(self.root, f"{group}/{subgroup}")
        dlg.name_var.set(old_comp["name"])
        dlg.host_var.set(old_comp["host"])
        dlg.port_var.set(str(old_comp["port"]))
        # Manually force the dialog result after setting fields:
        if dlg.result is None:  # dialog not yet applied
            dlg.wait_window()
        if dlg.result:
            new_comp = dlg.result
            comps[comps.index(old_comp)] = new_comp
            self.save_addressbook()
            self.on_tree_select(None)

    def remove_computer(self):
        selected_item = self.computer_list.focus()
        if not selected_item:
            return
        selected_node = self.tree.selection()
        if selected_node:
            node_id = selected_node[0]
            if "/" in node_id:
                group, subgroup = node_id.split("/", 1)
                comps = self.addressbook["groups"][group][subgroup]
                comp_data = self.computer_list.item(selected_item)["values"]
                comps = [c for c in comps if not (c["name"] == comp_data[0] and c["host"] == comp_data[1])]
                self.addressbook["groups"][group][subgroup] = comps
                self.save_addressbook()
                self.on_tree_select(None)

    def quick_connect(self):
        host = simpledialog.askstring("Quick Connect", "Enter IP or Hostname:")
        if host:
            self.connect_to_vnc("QuickConnect", host.strip(), DEFAULT_PORT)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        self.remove_computer_btn.config(state=DISABLED)
        self.edit_computer_btn.config(state=DISABLED)
        if not selected:
            self.add_computer_btn.config(state=DISABLED)
            self.selected_label.config(text="Select a group or sub-group")
            self.computer_list.delete(*self.computer_list.get_children())
            return
        node_id = selected[0]
        if node_id in self.addressbook["groups"]:
            self.selected_label.config(text=f"Group: {node_id}")
            self.add_computer_btn.config(state=DISABLED)
            self.computer_list.delete(*self.computer_list.get_children())
        else:
            if "/" not in node_id:
                self.computer_list.delete(*self.computer_list.get_children())
                self.selected_label.config(text="Select a group or sub-group")
                self.add_computer_btn.config(state=DISABLED)
                return
            group, subgroup = node_id.split("/", 1)
            self.selected_label.config(text=f"Sub-Group: {subgroup} (Group: {group})")
            self.add_computer_btn.config(state=NORMAL)
            self.remove_computer_btn.config(state=NORMAL)
            self.edit_computer_btn.config(state=NORMAL)
            self.computer_list.delete(*self.computer_list.get_children())
            comps = self.addressbook["groups"].get(group, {}).get(subgroup, [])
            for comp in comps:
                self.computer_list.insert("", "end", values=(comp["name"], comp["host"], comp["port"]))

    def on_computer_double_click(self, event):
        item = self.computer_list.focus()
        if not item:
            return
        comp_data = self.computer_list.item(item)["values"]
        if comp_data:
            name, host, port = comp_data[:3]
            self.connect_to_vnc(name, host, port)

    def connect_to_vnc(self, name, host, port):
        try:
            subprocess.Popen(
                [self.vnc_path, f"{host}::{port}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to start VNC viewer: {e}")

    def set_vnc_path(self):
        path = filedialog.askopenfilename(title="Select VNC Viewer Executable", filetypes=[("Executable files", "*.exe")])
        if path:
            self.vnc_path = path
            os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
            root = ET.Element("settings")
            ET.SubElement(root, "vnc_path", path=path)
            tree = ET.ElementTree(root)
            tree.write(SETTINGS_PATH)
            messagebox.showinfo("Success", "VNC path saved successfully.")

    def load_vnc_path(self):
        if os.path.isfile(SETTINGS_PATH):
            try:
                tree = ET.parse(SETTINGS_PATH)
                root = tree.getroot()
                self.vnc_path = root.find("vnc_path").get("path", DEFAULT_VNC_PATH)
            except:
                self.vnc_path = DEFAULT_VNC_PATH

    def load_addressbook(self):
        os.makedirs(os.path.dirname(ADDRESSBOOK_PATH), exist_ok=True)
        if not os.path.isfile(ADDRESSBOOK_PATH):
            tree = ET.ElementTree(ET.Element("addressbook"))
            tree.write(ADDRESSBOOK_PATH)
        try:
            tree = ET.parse(ADDRESSBOOK_PATH)
            root = tree.getroot()
            self.addressbook = {"groups": {}}
            self.tree.delete(*self.tree.get_children())  # Clear treeview before loading
            for group_elem in root.findall("group"):
                group_name = group_elem.get("name")
                self.addressbook["groups"][group_name] = {}
                self.tree.insert("", "end", iid=group_name, text=group_name, open=True)
                for subgroup_elem in group_elem.findall("subgroup"):
                    subgroup_name = subgroup_elem.get("name")
                    self.addressbook["groups"][group_name][subgroup_name] = []
                    subgroup_id = f"{group_name}/{subgroup_name}"
                    self.tree.insert(group_name, "end", iid=subgroup_id, text=subgroup_name, open=True)
                    for comp_elem in subgroup_elem.findall("computer"):
                        comp = {
                            "name": comp_elem.get("name"),
                            "host": comp_elem.get("host"),
                            "port": int(comp_elem.get("port"))
                        }
                        self.addressbook["groups"][group_name][subgroup_name].append(comp)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load addressbook: {e}")

    def save_addressbook(self):
        root = ET.Element("addressbook")
        for group_name, subgroups in self.addressbook["groups"].items():
            group_elem = ET.SubElement(root, "group", name=group_name)
            for subgroup_name, comps in subgroups.items():
                subgroup_elem = ET.SubElement(group_elem, "subgroup", name=subgroup_name)
                for comp in comps:
                    ET.SubElement(subgroup_elem, "computer",
                                  name=comp["name"],
                                  host=comp["host"],
                                  port=str(comp["port"]))
        tree = ET.ElementTree(root)
        try:
            tree.write(ADDRESSBOOK_PATH, encoding="utf-8", xml_declaration=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save addressbook: {e}")

if __name__ == "__main__":
    root = Tk()
    root.geometry("800x500")
    app = VNCAddressBookApp(root)
    root.mainloop()
