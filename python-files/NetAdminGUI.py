
import json
import os
import csv
import datetime
import threading
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

CONFIG_PATH = "netadmin_config.json"


# ---------- Data Models ----------

@dataclass
class Device:
    hostname: str
    ip: str
    mac: str
    online: bool = True
    rx_bytes: int = 0
    tx_bytes: int = 0
    last_seen: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    policy: str = "Default"  # e.g., Allowed, Blocked, Limited


@dataclass
class Schedule:
    mac: str
    start_time: Optional[str] = None  # "08:00"
    end_time: Optional[str] = None    # "18:30"
    days: List[str] = field(default_factory=lambda: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])


@dataclass
class PolicyStore:
    mac_allowlist: List[str] = field(default_factory=list)
    mac_blocklist: List[str] = field(default_factory=list)
    url_blocklist: List[str] = field(default_factory=list)  # domains
    app_blocklist: List[str] = field(default_factory=list)  # app/protocol labels
    schedules: List[Schedule] = field(default_factory=list)
    quotas_mb: Dict[str, int] = field(default_factory=dict)  # mac -> monthly quota in MB


# ---------- Adapter Interface ----------

class RouterAdapter:
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password

    def connect(self) -> bool:
        raise NotImplementedError

    def disconnect(self):
        pass

    def list_devices(self) -> List[Device]:
        raise NotImplementedError

    def get_usage_bytes(self, mac: str) -> Optional[Dict[str, int]]:
        return None

    def block_mac(self, mac: str) -> bool:
        raise NotImplementedError

    def allow_mac(self, mac: str) -> bool:
        raise NotImplementedError

    def set_url_blocklist(self, domains: List[str]) -> bool:
        return True

    def set_app_blocklist(self, apps: List[str]) -> bool:
        return True

    def set_schedule(self, schedule: Schedule) -> bool:
        return True

    def remove_schedule(self, mac: str) -> bool:
        return True

    def apply_quota_mb(self, mac: str, quota_mb: int) -> bool:
        return True


# ---------- Mock Adapter ----------

class MockRouterAdapter(RouterAdapter):
    def __init__(self, host: str, username: str, password: str):
        super().__init__(host, username, password)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._devices = [
            Device("Nitesh-PC", "192.168.1.10", "AA:BB:CC:DD:EE:01", True, 1234567, 3210000, now, "Allowed"),
            Device("ShopFloor-PLC", "192.168.1.20", "AA:BB:CC:DD:EE:02", True, 234567, 110000, now, "Allowed"),
            Device("QC-Tablet", "192.168.1.30", "AA:BB:CC:DD:EE:03", True, 56789, 44000, now, "Limited"),
            Device("Visitor-Phone", "192.168.1.40", "AA:BB:CC:DD:EE:04", False, 0, 0, now, "Blocked"),
        ]
        self.policies = PolicyStore(
            mac_allowlist=["AA:BB:CC:DD:EE:01"],
            mac_blocklist=["AA:BB:CC:DD:EE:04"],
            url_blocklist=["social.example.com", "video.example.com"],
            app_blocklist=["BitTorrent", "Steam"],
            schedules=[Schedule(mac="AA:BB:CC:DD:EE:03", start_time="08:00", end_time="17:30", days=["Mon","Tue","Wed","Thu","Fri"])],
            quotas_mb={"AA:BB:CC:DD:EE:03": 1024}
        )
        self.connected = False

    def connect(self) -> bool:
        time.sleep(0.2)
        self.connected = True
        return True

    def list_devices(self) -> List[Device]:
        for d in self._devices:
            if d.online:
                d.rx_bytes += 1024 * 5
                d.tx_bytes += 1024 * 3
                d.last_seen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return list(self._devices)

    def get_usage_bytes(self, mac: str) -> Optional[Dict[str, int]]:
        for d in self._devices:
            if d.mac == mac:
                return {"rx": d.rx_bytes, "tx": d.tx_bytes}
        return None

    def block_mac(self, mac: str) -> bool:
        if mac not in self.policies.mac_blocklist:
            self.policies.mac_blocklist.append(mac)
        self.policies.mac_allowlist = [m for m in self.policies.mac_allowlist if m != mac]
        for d in self._devices:
            if d.mac == mac:
                d.policy = "Blocked"
                d.online = False
        return True

    def allow_mac(self, mac: str) -> bool:
        if mac not in self.policies.mac_allowlist:
            self.policies.mac_allowlist.append(mac)
        self.policies.mac_blocklist = [m for m in self.policies.mac_blocklist if m != mac]
        for d in self._devices:
            if d.mac == mac:
                d.policy = "Allowed"
                d.online = True
        return True

    def set_url_blocklist(self, domains: List[str]) -> bool:
        self.policies.url_blocklist = domains
        return True

    def set_app_blocklist(self, apps: List[str]) -> bool:
        self.policies.app_blocklist = apps
        return True

    def set_schedule(self, schedule: Schedule) -> bool:
        self.policies.schedules = [s for s in self.policies.schedules if s.mac != schedule.mac]
        self.policies.schedules.append(schedule)
        return True

    def remove_schedule(self, mac: str) -> bool:
        self.policies.schedules = [s for s in self.policies.schedules if s.mac != mac]
        return True

    def apply_quota_mb(self, mac: str, quota_mb: int) -> bool:
        self.policies.quotas_mb[mac] = quota_mb
        return True


# ---------- GUI ----------

class NetAdminApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NetAdmin GUI (Admin Use Only)")
        self.geometry("1080x720")

        self.adapter: Optional[RouterAdapter] = None
        self.devices: List[Device] = []
        self.policy_store = PolicyStore()

        self.cfg = self.load_config()
        self._build_ui()

        if self.cfg.get("host"):
            self.host_var.set(self.cfg.get("host", ""))
            self.user_var.set(self.cfg.get("username", ""))
            self.pass_var.set(self.cfg.get("password", ""))
            self.adapter_type_var.set(self.cfg.get("adapter_type", "Mock"))
            self._connect_adapter()

        self._stop_refresh = False
        self._start_auto_refresh()

    def on_close(self):
        self._stop_refresh = True
        if self.adapter:
            self.adapter.disconnect()
        self.destroy()

    def load_config(self) -> Dict:
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_config(self, cfg: Dict):
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=2)

    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        self.tab_devices = ttk.Frame(nb)
        self.tab_policies = ttk.Frame(nb)
        self.tab_schedules = ttk.Frame(nb)
        self.tab_settings = ttk.Frame(nb)

        nb.add(self.tab_devices, text="Devices & Usage")
        nb.add(self.tab_policies, text="Policies (MAC/URLs/Apps)")
        nb.add(self.tab_schedules, text="Schedules & Quotas")
        nb.add(self.tab_settings, text="Settings")

        self._build_devices_tab()
        self._build_policies_tab()
        self._build_schedules_tab()
        self._build_settings_tab()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ----- Settings Tab -----
    def _build_settings_tab(self):
        frm = ttk.Frame(self.tab_settings, padding=16)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Adapter Type").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.adapter_type_var = tk.StringVar(value="Mock")
        adapter_combo = ttk.Combobox(frm, textvariable=self.adapter_type_var, values=["Mock"], state="readonly")
        adapter_combo.grid(row=0, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(frm, text="Router IP/Host").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.host_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.host_var, width=30).grid(row=1, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(frm, text="Username").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        self.user_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.user_var, width=30).grid(row=2, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(frm, text="Password").grid(row=3, column=0, sticky="w", padx=4, pady=4)
        self.pass_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.pass_var, width=30, show="*").grid(row=3, column=1, sticky="w", padx=4, pady=4)

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, sticky="w", pady=12)
        ttk.Button(btns, text="Connect", command=self._connect_adapter).pack(side="left", padx=4)
        ttk.Button(btns, text="Save Settings", command=self._save_settings).pack(side="left", padx=4)

        info = ttk.Label(frm, text="This app enforces policies only on routers you control. Replace the Mock adapter with a router-specific adapter (e.g., MikroTik, OpenWrt) to apply changes on your network.", wraplength=800, foreground="#444")
        info.grid(row=5, column=0, columnspan=2, sticky="w", padx=4, pady=16)

    def _save_settings(self):
        self.cfg["host"] = self.host_var.get()
        self.cfg["username"] = self.user_var.get()
        self.cfg["password"] = self.pass_var.get()
        self.cfg["adapter_type"] = self.adapter_type_var.get()
        self.save_config(self.cfg)
        messagebox.showinfo("Saved", "Settings saved.")

    def _connect_adapter(self):
        adapter_type = self.adapter_type_var.get()
        host = self.host_var.get() or "192.168.1.1"
        user = self.user_var.get() or "admin"
        pwd = self.pass_var.get() or "admin"

        if adapter_type == "Mock":
            self.adapter = MockRouterAdapter(host, user, pwd)
        else:
            messagebox.showerror("Adapter", f"Unsupported adapter type: {adapter_type}")
            return

        ok = self.adapter.connect()
        if ok:
            messagebox.showinfo("Connected", f"Connected to {host} using {adapter_type} adapter.")
            if isinstance(self.adapter, MockRouterAdapter):
                self.policy_store = self.adapter.policies
            self.refresh_devices()
        else:
            messagebox.showerror("Connection Failed", "Could not connect to router.")

    # ----- Devices Tab -----
    def _build_devices_tab(self):
        top = ttk.Frame(self.tab_devices, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="Connected Devices (live)").pack(side="left")

        btn_frame = ttk.Frame(self.tab_devices, padding=8)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_devices).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Block Selected", command=self.block_selected).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Allow Selected", command=self.allow_selected).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Export CSV", command=self.export_csv).pack(side="left", padx=4)

        cols = ("hostname", "ip", "mac", "status", "rx", "tx", "last_seen", "policy")
        self.tree = ttk.Treeview(self.tab_devices, columns=cols, show="headings", height=18)
        for c, w in zip(cols, (160,120,160,80,120,120,160,100)):
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=w, stretch=False)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        self.status_var = tk.StringVar(value="Disconnected")
        ttk.Label(self.tab_devices, textvariable=self.status_var, anchor="w").pack(fill="x", padx=8, pady=(0,8))

    def refresh_devices(self):
        if not self.adapter:
            messagebox.showwarning("Not connected", "Connect to a router in Settings.")
            return
        try:
            self.devices = self.adapter.list_devices()
            for row in self.tree.get_children():
                self.tree.delete(row)
            for d in self.devices:
                self.tree.insert("", "end", values=(
                    d.hostname, d.ip, d.mac, "Online" if d.online else "Offline",
                    self._fmt_bytes(d.rx_bytes), self._fmt_bytes(d.tx_bytes),
                    d.last_seen, d.policy
                ))
            self.status_var.set(f"Devices: {len(self.devices)} • Last refresh: {datetime.datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def block_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        for item in sel:
            vals = self.tree.item(item, "values")
            mac = vals[2]
            self.adapter.block_mac(mac)
        self.refresh_devices()
        self._sync_policy_lists()

    def allow_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        for item in sel:
            vals = self.tree.item(item, "values")
            mac = vals[2]
            self.adapter.allow_mac(mac)
        self.refresh_devices()
        self._sync_policy_lists()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Hostname","IP","MAC","Status","RX Bytes","TX Bytes","Last Seen","Policy"])
            for d in self.devices:
                writer.writerow([d.hostname, d.ip, d.mac, "Online" if d.online else "Offline", d.rx_bytes, d.tx_bytes, d.last_seen, d.policy])
        messagebox.showinfo("Exported", f"Saved to {path}")

    # ----- Policies Tab -----
    def _build_policies_tab(self):
        container = ttk.Frame(self.tab_policies, padding=12)
        container.pack(fill="both", expand=True)

        mac_frame = ttk.LabelFrame(container, text="MAC Filters")
        mac_frame.pack(fill="x", pady=8)
        self.allow_var = tk.StringVar()
        self.block_var = tk.StringVar()

        ttk.Label(mac_frame, text="Allowlist (one MAC per line)").grid(row=0, column=0, sticky="w")
        ttk.Label(mac_frame, text="Blocklist (one MAC per line)").grid(row=0, column=1, sticky="w")
        self.allow_txt = tk.Text(mac_frame, width=50, height=10)
        self.block_txt = tk.Text(mac_frame, width=50, height=10)
        self.allow_txt.grid(row=1, column=0, padx=6, pady=6)
        self.block_txt.grid(row=1, column=1, padx=6, pady=6)

        ttk.Button(mac_frame, text="Apply MAC Filters", command=self.apply_mac_filters).grid(row=2, column=0, padx=6, pady=6, sticky="w")

        url_frame = ttk.LabelFrame(container, text="URL/DNS Blocklist (domains)")
        url_frame.pack(fill="x", pady=8)
        self.url_txt = tk.Text(url_frame, height=6)
        self.url_txt.pack(fill="x", padx=6, pady=6)
        ttk.Button(url_frame, text="Apply URL Blocklist", command=self.apply_url_filters).pack(padx=6, pady=6, anchor="w")

        app_frame = ttk.LabelFrame(container, text="App/Protocol Blocklist (labels)")
        app_frame.pack(fill="x", pady=8)
        self.app_txt = tk.Text(app_frame, height=6)
        self.app_txt.pack(fill="x", padx=6, pady=6)
        ttk.Button(app_frame, text="Apply App Blocklist", command=self.apply_app_filters).pack(padx=6, pady=6, anchor="w")

    def _sync_policy_lists(self):
        self.allow_txt.delete("1.0", tk.END)
        self.block_txt.delete("1.0", tk.END)
        self.allow_txt.insert(tk.END, "\n".join(self.policy_store.mac_allowlist))
        self.block_txt.insert(tk.END, "\n".join(self.policy_store.mac_blocklist))

    def apply_mac_filters(self):
        allows = [l.strip() for l in self.allow_txt.get("1.0", tk.END).splitlines() if l.strip()]
        blocks = [l.strip() for l in self.block_txt.get("1.0", tk.END).splitlines() if l.strip()]
        self.policy_store.mac_allowlist = allows
        self.policy_store.mac_blocklist = blocks
        for mac in set(blocks):
            self.adapter.block_mac(mac)
        for mac in set(allows):
            self.adapter.allow_mac(mac)
        messagebox.showinfo("Applied", "MAC filters applied.")
        self.refresh_devices()

    def apply_url_filters(self):
        urls = [l.strip() for l in self.url_txt.get("1.0", tk.END).splitlines() if l.strip()]
        self.policy_store.url_blocklist = urls
        if self.adapter:
            ok = self.adapter.set_url_blocklist(urls)
            if ok:
                messagebox.showinfo("Applied", "URL/DNS blocklist applied.")
        else:
            messagebox.showwarning("Not connected", "Connect to a router in Settings.")

    def apply_app_filters(self):
        apps = [l.strip() for l in self.app_txt.get("1.0", tk.END).splitlines() if l.strip()]
        self.policy_store.app_blocklist = apps
        if self.adapter:
            ok = self.adapter.set_app_blocklist(apps)
            if ok:
                messagebox.showinfo("Applied", "App/protocol blocklist applied.")
        else:
            messagebox.showwarning("Not connected", "Connect to a router in Settings.")

    # ----- Schedules Tab -----
    def _build_schedules_tab(self):
        container = ttk.Frame(self.tab_schedules, padding=12)
        container.pack(fill="both", expand=True)

        editor = ttk.LabelFrame(container, text="Access Window (Daily)")
        editor.pack(fill="x", pady=8)

        ttk.Label(editor, text="Device MAC").grid(row=0, column=0, sticky="w")
        self.s_mac = tk.StringVar()
        ttk.Entry(editor, textvariable=self.s_mac, width=24).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(editor, text="Start Time (HH:MM 24h)").grid(row=1, column=0, sticky="w")
        ttk.Label(editor, text="End Time (HH:MM 24h)").grid(row=2, column=0, sticky="w")
        self.s_start = tk.StringVar()
        self.s_end = tk.StringVar()
        ttk.Entry(editor, textvariable=self.s_start, width=12).grid(row=1, column=1, sticky="w", padx=6, pady=4)
        ttk.Entry(editor, textvariable=self.s_end, width=12).grid(row=2, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(editor, text="Days (comma-separated, e.g., Mon,Tue,Wed)").grid(row=3, column=0, sticky="w")
        self.s_days = tk.StringVar(value="Mon,Tue,Wed,Thu,Fri,Sat,Sun")
        ttk.Entry(editor, textvariable=self.s_days, width=40).grid(row=3, column=1, sticky="w", padx=6, pady=4)

        btns = ttk.Frame(editor)
        btns.grid(row=4, column=0, columnspan=2, sticky="w", pady=8)
        ttk.Button(btns, text="Save/Update Schedule", command=self.save_schedule).pack(side="left", padx=4)
        ttk.Button(btns, text="Remove Schedule", command=self.remove_schedule).pack(side="left", padx=4)

        quotas = ttk.LabelFrame(container, text="Monthly Data Quotas (MB)")
        quotas.pack(fill="x", pady=8)
        self.quota_mac = tk.StringVar()
        self.quota_mb = tk.IntVar(value=1024)
        ttk.Label(quotas, text="Device MAC").grid(row=0, column=0, sticky="w")
        ttk.Entry(quotas, textvariable=self.quota_mac, width=24).grid(row=0, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(quotas, text="Quota (MB)").grid(row=1, column=0, sticky="w")
        ttk.Entry(quotas, textvariable=self.quota_mb, width=12).grid(row=1, column=1, sticky="w", padx=6, pady=4)
        ttk.Button(quotas, text="Apply Quota", command=self.apply_quota).grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=6)

        list_frame = ttk.LabelFrame(container, text="Existing Schedules")
        list_frame.pack(fill="both", expand=True, pady=8)
        cols = ("mac", "start", "end", "days")
        self.sch_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        for c, w in zip(cols, (180,120,120,400)):
            self.sch_tree.heading(c, text=c.title())
            self.sch_tree.column(c, width=w, stretch=False)
        self.sch_tree.pack(fill="both", expand=True, padx=6, pady=6)

    def save_schedule(self):
        mac = self.s_mac.get().strip()
        start = self.s_start.get().strip() or None
        end = self.s_end.get().strip() or None
        days = [d.strip() for d in self.s_days.get().split(",") if d.strip()]
        if not mac:
            messagebox.showwarning("Missing", "MAC is required.")
            return
        sch = Schedule(mac=mac, start_time=start, end_time=end, days=days)
        if self.adapter and self.adapter.set_schedule(sch):
            self.policy_store.schedules = [s for s in self.policy_store.schedules if s.mac != mac]
            self.policy_store.schedules.append(sch)
            messagebox.showinfo("Saved", "Schedule saved.")
            self._refresh_schedule_list()

    def remove_schedule(self):
        mac = self.s_mac.get().strip()
        if not mac:
            messagebox.showwarning("Missing", "MAC is required.")
            return
        if self.adapter and self.adapter.remove_schedule(mac):
            self.policy_store.schedules = [s for s in self.policy_store.schedules if s.mac != mac]
            self._refresh_schedule_list()
            messagebox.showinfo("Removed", "Schedule removed.")

    def apply_quota(self):
        mac = self.quota_mac.get().strip()
        quota = self.quota_mb.get()
        if not mac:
            messagebox.showwarning("Missing", "MAC is required.")
            return
        if self.adapter and self.adapter.apply_quota_mb(mac, quota):
            self.policy_store.quotas_mb[mac] = quota
            messagebox.showinfo("Applied", f"Quota {quota} MB applied for {mac}.")

    def _refresh_schedule_list(self):
        for row in self.sch_tree.get_children():
            self.sch_tree.delete(row)
        for s in self.policy_store.schedules:
            self.sch_tree.insert("", "end", values=(s.mac, s.start_time or "", s.end_time or "", ",".join(s.days)))

    def _fmt_bytes(self, n: int) -> str:
        step = 1024.0
        units = ["B","KB","MB","GB","TB"]
        idx = 0
        val = float(n)
        while val >= step and idx < len(units)-1:
            val /= step
            idx += 1
        return f"{val:.2f} {units[idx]}"

    def _start_auto_refresh(self):
        def loop():
            while not self._stop_refresh:
                try:
                    if self.adapter:
                        self.devices = self.adapter.list_devices()
                        self._update_tree_quiet()
                        self.status_var.set(f"Devices: {len(self.devices)} • Auto refresh: {datetime.datetime.now().strftime('%H:%M:%S')}")
                        self._refresh_schedule_list()
                        self._sync_policy_lists()
                        self.url_txt.delete("1.0", tk.END)
                        self.url_txt.insert(tk.END, "\n".join(self.policy_store.url_blocklist))
                        self.app_txt.delete("1.0", tk.END)
                        self.app_txt.insert(tk.END, "\n".join(self.policy_store.app_blocklist))
                    time.sleep(5)
                except Exception:
                    time.sleep(5)
        threading.Thread(target=loop, daemon=True).start()

    def _update_tree_quiet(self):
        sel_macs = set()
        for item in self.tree.selection():
            vals = self.tree.item(item, "values")
            if vals:
                sel_macs.add(vals[2])

        for row in self.tree.get_children():
            self.tree.delete(row)
        for d in self.devices:
            iid = self.tree.insert("", "end", values=(
                d.hostname, d.ip, d.mac, "Online" if d.online else "Offline",
                self._fmt_bytes(d.rx_bytes), self._fmt_bytes(d.tx_bytes),
                d.last_seen, d.policy
            ))
            if d.mac in sel_macs:
                self.tree.selection_add(iid)

    # ----- Devices Tab helpers -----
    def _build_devices_tab(self):
        top = ttk.Frame(self.tab_devices, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="Connected Devices (live)").pack(side="left")

        btn_frame = ttk.Frame(self.tab_devices, padding=8)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_devices).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Block Selected", command=self.block_selected).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Allow Selected", command=self.allow_selected).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Export CSV", command=self.export_csv).pack(side="left", padx=4)

        cols = ("hostname", "ip", "mac", "status", "rx", "tx", "last_seen", "policy")
        self.tree = ttk.Treeview(self.tab_devices, columns=cols, show="headings", height=18)
        for c, w in zip(cols, (160,120,160,80,120,120,160,100)):
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=w, stretch=False)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        self.status_var = tk.StringVar(value="Disconnected")
        ttk.Label(self.tab_devices, textvariable=self.status_var, anchor="w").pack(fill="x", padx=8, pady=(0,8))

if __name__ == "__main__":
    app = NetAdminApp()
    app.mainloop()
