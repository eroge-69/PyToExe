# Author: Akshay Gajare (enhanced)
import os
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

# ------------------------
# Config toggles
# ------------------------
RECURSIVE_SEARCH = True
FILE_EXTENSIONS = {".cid", ".scd", ".icd", ".iid"}  # add/remove as needed
INCLUDE_IPV6 = True  # set False if you don't need IPv6 columns

# ------------------------
# Helpers
# ------------------------
def detect_ns(xml_root):
    """Return nsmap {'scl': uri} if namespaced, else {}."""
    if "}" in xml_root.tag:
        uri = xml_root.tag.split("}")[0].strip("{")
        return {"scl": uri}
    return {}

def findall(elem, path_ns, path_non_ns, nsmap):
    """Try namespaced path first; if nothing found, try non-namespaced."""
    res = elem.findall(path_ns, nsmap) if nsmap else []
    if not res:
        res = elem.findall(path_non_ns)
    return res

def norm_key(s: str) -> str:
    """Normalize P[@type] to tolerate vendor variations (case, hyphens, etc.)."""
    return "".join(ch.lower() for ch in s if ch.isalnum() or ch in ("-", "_"))

def collect_files(folder, exts, recursive=True):
    files = []
    if recursive:
        for root, _, names in os.walk(folder):
            for nm in names:
                if os.path.splitext(nm)[1].lower() in exts:
                    files.append(os.path.join(root, nm))
    else:
        for nm in os.listdir(folder):
            if os.path.splitext(nm)[1].lower() in exts:
                files.append(os.path.join(folder, nm))
    return files

def parse_file(file_path):
    """
    Return (rows, errors) for one SCL file.
    Each row matches the CSV header defined below.
    """
    rows = []
    errs = []

    try:
        tree = ET.parse(file_path)
        xml_root = tree.getroot()
    except ET.ParseError as e:
        errs.append(f"{os.path.basename(file_path)}: XML ParseError - {e}")
        return rows, errs
    except Exception as e:
        errs.append(f"{os.path.basename(file_path)}: Unexpected parse error - {e}")
        return rows, errs

    nsmap = detect_ns(xml_root)

    # Find all SubNetworks; if none, still attempt to find ConnectedAP globally
    subnets = findall(xml_root,
                      ".//scl:SubNetwork",
                      ".//SubNetwork",
                      nsmap)

    def extract_cap_rows(cap_elem, subnetwork_name):
        # ConnectedAP attributes
        ied_name = cap_elem.attrib.get("iedName", "")
        ap_name = cap_elem.attrib.get("apName", "")

        # Defaults
        ip = ip_subnet = ip_gateway = ip_port = ""
        mac = appid = vlan_id = vlan_prio = ""
        ipv6 = ipv6_prefix = ipv6_gateway = ""

        # Get Address under ConnectedAP
        addr_elems = findall(cap_elem,
                             "scl:Address",
                             "Address",
                             nsmap)
        # Map known P types (vendor deviations normalized)
        KEYMAP = {
            "ip": "ip",
            "ip-subnet": "ip_subnet",
            "subnet": "ip_subnet",
            "netmask": "ip_subnet",
            "ip-gateway": "ip_gateway",
            "gateway": "ip_gateway",
            "ip-port": "ip_port",
            "port": "ip_port",
            "mac-address": "mac",
            "mac": "mac",
            "appid": "appid",
            "vlan-id": "vlan_id",
            "vlanpriority": "vlan_prio",
            "vlan-priority": "vlan_prio",
            # IPv6 variations
        }

        if INCLUDE_IPV6:
            KEYMAP.update({
                "ipv6": "ipv6",
                "ip-v6": "ipv6",
                "ipv6address": "ipv6",
                "ipv6-address": "ipv6",
                "ipv6prefix": "ipv6_prefix",
                "ipv6-prefix": "ipv6_prefix",
                "ipv6prefixlength": "ipv6_prefix",
                "ipv6-prefix-length": "ipv6_prefix",
                "ip-v6-subnet": "ipv6_prefix",
                "ipv6gateway": "ipv6_gateway",
                "ipv6-gateway": "ipv6_gateway",
                "ip-v6-gateway": "ipv6_gateway",
            })

        # Read params
        for addr in addr_elems:
            p_list = findall(addr, "scl:P", "P", nsmap)
            for p in p_list:
                p_type = p.attrib.get("type", "")
                key = KEYMAP.get(norm_key(p_type))
                if not key:
                    continue
                val = (p.text or "").strip()
                if not val:
                    continue
                if key == "ip":
                    ip = val
                elif key == "ip_subnet":
                    ip_subnet = val
                elif key == "ip_gateway":
                    ip_gateway = val
                elif key == "ip_port":
                    ip_port = val
                elif key == "mac":
                    mac = val
                elif key == "appid":
                    appid = val
                elif key == "vlan_id":
                    vlan_id = val
                elif key == "vlan_prio":
                    vlan_prio = val
                elif INCLUDE_IPV6 and key == "ipv6":
                    ipv6 = val
                elif INCLUDE_IPV6 and key == "ipv6_prefix":
                    ipv6_prefix = val
                elif INCLUDE_IPV6 and key == "ipv6_gateway":
                    ipv6_gateway = val

        row = [
            os.path.basename(file_path),
            subnetwork_name,
            ap_name,
            ied_name,
            ip,
            ip_subnet,
            ip_gateway,
            ip_port,
            mac,
            appid,
            vlan_id,
            vlan_prio,
        ]

        if INCLUDE_IPV6:
            row.extend([ipv6, ipv6_prefix, ipv6_gateway])

        rows.append(row)

    if subnets:
        for sn in subnets:
            sn_name = sn.attrib.get("name", "")
            caps = findall(sn,
                           "scl:ConnectedAP",
                           "ConnectedAP",
                           nsmap)
            for cap in caps:
                extract_cap_rows(cap, sn_name)
    else:
        # Fallback: global search for ConnectedAP
        caps = findall(xml_root,
                       ".//scl:ConnectedAP",
                       ".//ConnectedAP",
                       nsmap)
        for cap in caps:
            extract_cap_rows(cap, "")

    return rows, errs

# ------------------------
# GUI and main flow
# ------------------------
def main():
    tk_root = tk.Tk()
    tk_root.withdraw()  # Hide the main window

    folder_path = filedialog.askdirectory(title="Select Folder Containing SCL Files (.cid/.scd/.icd/.iid)")
    if not folder_path:
        messagebox.showinfo("Operation Cancelled", "You cancelled the folder selection. Exiting now.")
        tk_root.destroy()
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = os.path.join(folder_path, f"scl_extracted_data_{timestamp}.csv")
    error_csv = os.path.join(folder_path, f"scl_extraction_errors_{timestamp}.csv")

    # Build header
    header = [
        "File Name", "SubNetwork", "IED Name", "AP Name",
        "IP", "IP-SUBNET", "IP-GATEWAY", "IP-PORT",
        "MAC-Address", "APPID", "VLAN-ID", "VLAN-PRIORITY",
    ]
    if INCLUDE_IPV6:
        header.extend(["IPv6", "IPv6-PREFIX", "IPv6-GATEWAY"])

    files = collect_files(folder_path, FILE_EXTENSIONS, RECURSIVE_SEARCH)
    if not files:
        messagebox.showwarning("No Files Found",
                               f"No files with {', '.join(sorted(FILE_EXTENSIONS))} found.")
        tk_root.destroy()
        return

    all_rows = [header]
    error_rows = [["File Name", "Error"]]

    for fp in files:
        rows, errs = parse_file(fp)
        all_rows.extend(rows)
        for e in errs:
            error_rows.append([os.path.basename(fp), e])

    # Write main CSV
    try:
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(all_rows)
    except Exception as e:
        messagebox.showerror("CSV Write Error", f"Failed to write CSV file:\n{e}")
        tk_root.destroy()
        return

    # Write errors CSV if any
    err_msg = ""
    if len(error_rows) > 1:
        try:
            with open(error_csv, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(error_rows)
            err_msg = f"\n⚠️ Errors logged to:\n{error_csv}"
        except Exception as e:
            err_msg = f"\n⚠️ Some errors occurred but could not be written to error log:\n{e}"

    messagebox.showinfo(
        "Extraction Complete",
        f"✅ Extraction complete.\n\n"
        f"Files scanned: {len(files)}\n"
        f"Rows (excluding header): {len(all_rows)-1}\n\n"
        f"Data saved to:\n{output_csv}"
        f"{err_msg}"
    )

    tk_root.destroy()

if __name__ == "__main__":
    main()
