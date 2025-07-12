import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

class GATTEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 BLE GATT Configurator")
        self.root.configure(bg="#f0f2f5")

        self.services = {}

        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("TFrame", background="#f0f2f5")
        style.configure("TLabel", background="#f0f2f5", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=5)
        style.configure("TEntry", padding=4)
        style.configure("Treeview", rowheight=24, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe", background="#f0f2f5", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", background="#f0f2f5")
        style.map("TButton", background=[("active", "#dbeafe")])

        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        self.tree_frame = ttk.Frame(self.main_pane)
        self.tree = ttk.Treeview(self.tree_frame, show="tree")
        self.tree.tag_configure('service', foreground="#1d4ed8")
        self.tree.tag_configure('char', foreground="#047857")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.main_pane.add(self.tree_frame, weight=1)

        self.detail_frame = ttk.LabelFrame(self.main_pane, text="Details")
        self.build_detail_panel()
        self.main_pane.add(self.detail_frame, weight=2)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="Add Service", command=self.add_service).pack(side=tk.LEFT, padx=5, pady=8)
        ttk.Button(button_frame, text="Add Characteristic", command=self.add_characteristic).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove", command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Code", command=self.generate_code).pack(side=tk.RIGHT, padx=5)

        self.set_details_state('disabled')
        self.main_pane.forget(self.detail_frame)

    def build_detail_panel(self):
        self.selected_id = None

        self.name_var = tk.StringVar()
        self.uuid_var = tk.StringVar()
        self.value_var = tk.StringVar()
        self.sig_type = tk.StringVar()
        self.is_primary_service = tk.BooleanVar()

        self.read_var = tk.BooleanVar()
        self.write_var = tk.BooleanVar()
        self.notify_var = tk.BooleanVar()
        self.auth_var = tk.BooleanVar()
        self.bond_var = tk.BooleanVar()
        self.encrypt_var = tk.BooleanVar()

        ttk.Label(self.detail_frame, text="Name").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.name_entry = ttk.Entry(self.detail_frame, textvariable=self.name_var)
        self.name_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(self.detail_frame, text="UUID").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.uuid_entry = ttk.Entry(self.detail_frame, textvariable=self.uuid_var)
        self.uuid_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(self.detail_frame, text="Initial Value").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.value_entry = ttk.Entry(self.detail_frame, textvariable=self.value_var)
        self.value_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(self.detail_frame, text="SIG Type (optional)").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.sig_entry = ttk.Entry(self.detail_frame, textvariable=self.sig_type)
        self.sig_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=2)

        self.primary_cb = ttk.Checkbutton(self.detail_frame, text="Primary Service", variable=self.is_primary_service)
        self.primary_cb.grid(row=4, column=0, columnspan=2, sticky='w', padx=5, pady=5)

        self.props_frame = ttk.LabelFrame(self.detail_frame, text="Characteristic Properties")
        self.props_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky="ew", padx=5)
        ttk.Checkbutton(self.props_frame, text="Read", variable=self.read_var).grid(row=0, column=0, sticky='w', padx=5)
        ttk.Checkbutton(self.props_frame, text="Write", variable=self.write_var).grid(row=0, column=1, sticky='w', padx=5)
        ttk.Checkbutton(self.props_frame, text="Notify", variable=self.notify_var).grid(row=0, column=2, sticky='w', padx=5)

        self.access_frame = ttk.LabelFrame(self.detail_frame, text="Access Control")
        self.access_frame.grid(row=6, column=0, columnspan=2, pady=5, sticky="ew", padx=5)
        ttk.Checkbutton(self.access_frame, text="Authenticated", variable=self.auth_var).grid(row=0, column=0, sticky='w', padx=5)
        ttk.Checkbutton(self.access_frame, text="Bonded", variable=self.bond_var).grid(row=0, column=1, sticky='w', padx=5)
        ttk.Checkbutton(self.access_frame, text="Encrypted", variable=self.encrypt_var).grid(row=0, column=2, sticky='w', padx=5)

        self.save_btn = ttk.Button(self.detail_frame, text="💾 Save", command=self.save_details)
        self.save_btn.grid(row=7, column=0, columnspan=2, pady=10)

        for i in range(2):
            self.detail_frame.columnconfigure(i, weight=1)

    def set_details_state(self, state):
        widgets = [
            self.name_entry, self.uuid_entry, self.sig_entry, self.value_entry,
            self.primary_cb, self.save_btn,
            *self.props_frame.winfo_children(),
            *self.access_frame.winfo_children()
        ]
        for widget in widgets:
            try:
                widget.configure(state=state)
            except:
                pass

    def add_service(self):
        svc_name = simpledialog.askstring("Add Service", "Enter service name:")
        if svc_name:
            svc_id = f"svc_{len(self.services)}"
            self.services[svc_id] = {
                "name": svc_name,
                "uuid": "",
                "sig_type": "",
                "primary": True,
                "characteristics": {}
            }
            self.tree.insert('', 'end', iid=svc_id, text=f"🧱 {svc_name}", tags=('service',))
            self.tree.selection_set(svc_id)

    def add_characteristic(self):
        selected = self.tree.selection()
        if not selected or not selected[0].startswith("svc_"):
            messagebox.showwarning("Select Service", "Please select a service to add characteristic.")
            return
        svc_id = selected[0]
        svc = self.services[svc_id]
        char_name = simpledialog.askstring("Add Characteristic", "Enter characteristic name:")
        if char_name:
            char_id = f"{svc_id}_char_{len(svc['characteristics'])}"
            svc["characteristics"][char_id] = {
                "name": char_name,
                "uuid": "",
                "value": "",
                "read": False,
                "write": False,
                "notify": False,
                "auth": False,
                "bond": False,
                "encrypt": False
            }
            self.tree.insert(svc_id, 'end', iid=char_id, text=f"🔹 {char_name}", tags=('char',))
            self.tree.selection_set(char_id)

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            self.main_pane.forget(self.detail_frame)
            return

        if not self.detail_frame.winfo_ismapped():
            self.main_pane.add(self.detail_frame, weight=2)

        sel_id = sel[0]
        self.selected_id = sel_id
        self.set_details_state('normal')

        if "_char_" in sel_id:
            svc_id = sel_id.split("_char_")[0]
            char = self.services[svc_id]["characteristics"][sel_id]
            self.name_var.set(char["name"])
            self.uuid_var.set(char["uuid"])
            self.value_var.set(char.get("value", ""))
            self.sig_type.set("")
            self.is_primary_service.set(False)

            self.read_var.set(char["read"])
            self.write_var.set(char["write"])
            self.notify_var.set(char["notify"])
            self.auth_var.set(char["auth"])
            self.bond_var.set(char["bond"])
            self.encrypt_var.set(char["encrypt"])

            self.value_entry.grid()
            self.props_frame.grid()
            self.access_frame.grid()
            self.primary_cb.grid_remove()
            self.sig_entry.grid_remove()

        else:
            svc = self.services[sel_id]
            self.name_var.set(svc["name"])
            self.uuid_var.set(svc["uuid"])
            self.sig_type.set(svc["sig_type"])
            self.is_primary_service.set(svc["primary"])

            self.read_var.set(False)
            self.write_var.set(False)
            self.notify_var.set(False)
            self.auth_var.set(False)
            self.bond_var.set(False)
            self.encrypt_var.set(False)

            self.value_var.set("")
            self.value_entry.grid_remove()
            self.props_frame.grid_remove()
            self.access_frame.grid_remove()
            self.primary_cb.grid()
            self.sig_entry.grid()

    def save_details(self):
        if not self.selected_id:
            return
        if "_char_" in self.selected_id:
            svc_id = self.selected_id.split("_char_")[0]
            char = self.services[svc_id]["characteristics"][self.selected_id]
            char["name"] = self.name_var.get()
            char["uuid"] = self.uuid_var.get()
            char["value"] = self.value_var.get()
            char["read"] = self.read_var.get()
            char["write"] = self.write_var.get()
            char["notify"] = self.notify_var.get()
            char["auth"] = self.auth_var.get()
            char["bond"] = self.bond_var.get()
            char["encrypt"] = self.encrypt_var.get()
            self.tree.item(self.selected_id, text=f"🔹 {char['name']}")
        else:
            svc = self.services[self.selected_id]
            svc["name"] = self.name_var.get()
            svc["uuid"] = self.uuid_var.get()
            svc["sig_type"] = self.sig_type.get()
            svc["primary"] = self.is_primary_service.get()
            self.tree.item(self.selected_id, text=f"🧱 {svc['name']}")

    def remove_selected(self):
        sel = self.tree.selection()
        for sel_id in sel:
            if "_char_" in sel_id:
                svc_id = sel_id.split("_char_")[0]
                del self.services[svc_id]["characteristics"][sel_id]
            else:
                del self.services[sel_id]
            self.tree.delete(sel_id)

        if not self.tree.get_children():
            self.set_details_state('disabled')
            self.main_pane.forget(self.detail_frame)

    def generate_code(self):
        def format_macro(name):
            return name.upper().replace(" ", "_")

        def format_var(name):
            return "p" + name.replace(" ", "_").capitalize()

        def format_service_var(name):
            return "p" + name.replace(" ", "_").capitalize() + "Service"

        code = '#include <BLEDevice.h>\n#include <BLEServer.h>\n#include <BLEUtils.h>\n#include <BLE2902.h>\n\n'

        code += '// UUID definitions\n'
        for svc in self.services.values():
            code += f'#define {format_macro(svc["name"])}_UUID "{svc["uuid"]}"\n'
            for char in svc["characteristics"].values():
                code += f'#define {format_macro(char["name"])}_UUID "{char["uuid"]}"\n'

        code += '\nBLEServer* pServer = nullptr;\nbool deviceConnected = false;\n'

        for svc in self.services.values():
            for char in svc["characteristics"].values():
                code += f'BLECharacteristic* {format_var(char["name"])} = nullptr;\n'

        code += '\nclass MyServerCallbacks : public BLEServerCallbacks {\n'
        code += '  void onConnect(BLEServer* pServer) {\n    deviceConnected = true;\n    Serial.println("Device connected");\n  }\n'
        code += '  void onDisconnect(BLEServer* pServer) {\n    deviceConnected = false;\n    Serial.println("Device disconnected");\n  }\n};\n\n'

        code += 'void setup() {\n  Serial.begin(115200);\n  BLEDevice::init("ESP32-BLE-Device");\n'
        code += '  pServer = BLEDevice::createServer();\n  pServer->setCallbacks(new MyServerCallbacks());\n\n'

        for svc in self.services.values():
            svc_var = format_service_var(svc["name"])
            code += f'  BLEService* {svc_var} = pServer->createService({format_macro(svc["name"])}_UUID);\n'
            for char in svc["characteristics"].values():
                char_var = format_var(char["name"])
                props = []
                if char["read"]: props.append("BLECharacteristic::PROPERTY_READ")
                if char["write"]: props.append("BLECharacteristic::PROPERTY_WRITE")
                if char["notify"]: props.append("BLECharacteristic::PROPERTY_NOTIFY")
                props_combined = " | ".join(props) if props else "0"
                value = char.get("value", "").replace('"', '\\"')

                code += f'  {char_var} = {svc_var}->createCharacteristic({format_macro(char["name"])}_UUID, {props_combined});\n'
                code += f'  {char_var}->addDescriptor(new BLE2902());\n'
                code += f'  {char_var}->setValue("{value}");\n\n'

            code += f'  {svc_var}->start();\n\n'

        code += '  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();\n'
        for svc in self.services.values():
            code += f'  pAdvertising->addServiceUUID({format_macro(svc["name"])}_UUID);\n'
        code += '  pAdvertising->setScanResponse(false);\n'
        code += '  pAdvertising->setMinPreferred(0x06);\n'
        code += '  pAdvertising->setMinPreferred(0x12);\n'
        code += '  BLEDevice::startAdvertising();\n  Serial.println("BLE device is now advertising");\n}\n\n'

        code += 'void loop() {\n'
        notifiable = any(char["notify"] for svc in self.services.values() for char in svc["characteristics"].values())
        if notifiable:
            code += '  if (deviceConnected) {\n'
            for svc in self.services.values():
                for char in svc["characteristics"].values():
                    if char["notify"]:
                        code += f'    {format_var(char["name"])}->setValue("Updated Data");\n'
                        code += f'    {format_var(char["name"])}->notify();\n'
            code += '    delay(2000);\n  }\n'
        else:
            code += '  delay(1000);\n'
        code += '}\n'

        code_window = tk.Toplevel(self.root)
        code_window.title("Generated Arduino Code")
        code_window.geometry("800x600")
        code_window.configure(bg="#ffffff")
        text = tk.Text(code_window, wrap=tk.WORD, bg="#f9fafb", fg="#111827",
                       font=("Consolas", 10), insertbackground="black")
        text.insert(tk.END, code)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = GATTEditor(root)
    root.mainloop()
