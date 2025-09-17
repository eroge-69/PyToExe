import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import struct
import threading
import sys

# -----------------------
# قائمة بادئات سيريالات HP المحدثة بالكامل
hp_serial_prefixes = [
    "5CD", "5CG", "5CB", "5CE", "5CF", "5CH", "5CK", "5CM", "5CS", "5CT", "5CU",
    "5CX", "5CY", "5CZ", "5D0", "5D1", "5D2", "5D3", "5D4", "5D5", "5D6", "5D7",
    "5D8", "5D9", "5DA", "5DB", "5DC", "5DD", "5DE", "5DF", "5DG", "5DH", "5DJ",
    "5DK", "5DL", "5DM", "5DN", "5DP", "5DQ", "5DR", "5DS", "5DT", "5DU", "5DV",
    "5DW", "5DX", "5DY", "5DZ", "5E0", "5E1", "5E2", "5E3", "5E4", "5E5", "5E6",
    "5E7", "5E8", "5E9", "5EA", "5EB", "5EC", "5ED", "5EE", "5EF", "5EG", "5EH",
    "5EJ", "5EK", "5EL", "5EM", "5EN", "5EP", "5EQ", "5ER", "5ES", "5ET", "5EU",
    "5EV", "5EW", "5EX", "5EY", "5EZ",
    "2CE", "2CG", "2CH", "2CB", "2CC", "2CD", "2CF", "2CJ", "2CK", "2CL", "2CM",
    "2CP", "2CR", "2CS", "2CT", "2CU", "2CV", "2CW", "2CX", "2CY", "2CZ", "2D0",
    "2D1", "2D2", "2D3", "2D4", "2D5", "2D6", "2D7", "2D8", "2D9", "2DA", "2DB",
    "2DC", "2DD", "2DE", "2DF", "2DG", "2DH", "2DJ", "2DK", "2DL", "2DM", "2DN",
    "2DP", "2DQ", "2DR", "2DS", "2DT", "2DU", "2DV", "2DW", "2DX", "2DY", "2DZ",
    "CNC", "CNF", "CNU", "CND", "CNP", "CNW", "CNB", "CNA", "CNJ", "CNK", "CNL",
    "CNM", "CNN", "CNQ", "CNR", "CNS", "CNT", "CNV", "CNX", "CNY", "CNZ",
    "CZJ", "CZK", "CZL", "CZM", "CZN", "CZP", "CZQ", "CZR", "CZS", "CZT", "CZU",
    "CZV", "CZW", "CZX", "CZY", "CZZ", "CZC",
    "MXL", "MXJ", "MXG", "MXQ", "MXK",
    "MYK", "MYJ", "MYD", "MYQ", "MYR",
    "SGD", "SGH", "SGL", "SGM", "SGP", "SGW", "SGX", "SGY", "SGZ", "SGC",
    "JPP", "JPN", "JPM", "JPL", "JPK", "AUD",
    "JKB", "JKC", "JKD", "JKH", "JKS",
    "JPB", "JPC", "JPD", "JPH", "JPS",
    "3CR", "3CT", "3CU", "3CV", "3CW",
    "4CC", "4CD", "4CF", "4CG", "4CH",
    "8CC", "8CD", "8CF", "8CG", "8CH",
    "C0G", "C0H", "C0J", "C0K", "C0L",
    "JPR", "1TJ",
    "VND", "VNG", "VNH", "VNK", "VNP",
    "VNW", "VNX", "VNY", "VNZ"
]

# الكلمات التي يجب استبعادها لتقليل النتائج الخاطئة
BLACKLISTED_WORDS = {"SECURITY", "VERSION", "BUILD", "DATE", "NUMBER", "MODEL", "BIOS", "UEFI", "PRODUCT", "SYSTEM", "N.A", "N/A"}

# -----------------------
# Helper: find UTF-16LE/BE printable runs
def find_utf16le_runs(data: bytes, min_chars=4):
    """Return list of (offset, decoded_str) for UTF-16LE printable runs."""
    pat = re.compile(rb'(?:[\x20-\x7E]\x00){%d,}' % min_chars)
    out = []
    for m in pat.finditer(data):
        raw = m.group()
        try:
            s = raw.decode('utf-16le', errors='ignore')
            out.append((m.start(), s))
        except Exception:
            continue
    return out

def find_utf16be_runs(data: bytes, min_chars=4):
    """Return list of (offset, decoded_str) for UTF-16BE printable runs."""
    pat = re.compile(rb'(?:\x00[\x20-\x7E]){%d,}' % min_chars)
    out = []
    for m in pat.finditer(data):
        raw = m.group()
        try:
            s = raw.decode('utf-16be', errors='ignore')
            out.append((m.start(), s))
        except Exception:
            continue
    return out

# -----------------------
# SMBIOS parsing (Type 1)
def parse_smbios(data: bytes):
    serials = []
    for i in range(len(data) - 4):
        if data[i:i+4] == b'_SM_':
            try:
                struct_table_length = struct.unpack_from("<H", data, i + 22)[0]
                struct_table_offset = struct.unpack_from("<I", data, i + 24)[0]
                if 0 <= struct_table_offset < len(data):
                    struct_table = data[struct_table_offset:struct_table_offset + struct_table_length]
                    j = 0
                    while j < len(struct_table):
                        if j + 4 > len(struct_table):
                            break
                        type_id = struct_table[j]
                        length = struct_table[j + 1]
                        if length == 0:
                            break
                        if type_id == 1 and length > 0x08:
                            try:
                                serial_index = struct_table[j + 7]
                            except IndexError:
                                serial_index = 0
                            strings_start = j + length
                            strings = struct_table[strings_start:].split(b"\x00")
                            if 0 < serial_index <= len(strings):
                                try:
                                    serial = strings[serial_index - 1].decode(errors="ignore").strip()
                                except:
                                    serial = strings[serial_index - 1].decode('latin-1', errors='ignore').strip()
                                if serial:
                                    serials.append(serial)
                        j += length
                        while j < len(struct_table) - 1 and struct_table[j:j + 2] != b"\x00\x00":
                            j += 1
                        j += 2
            except Exception:
                continue
    return serials

# Core: extract & score candidates
def extract_and_score_candidates(data: bytes, deep=False):
    candidates = []
    
    # Define a new, highly strict scoring function
    def score_candidate(val: str, offset: int, encoding: str, source: str, bonus=0):
        key = val.strip()
        uc = key.upper()
        
        # Mandatory check: must start with a known HP prefix
        if not any(uc.startswith(pref) for pref in hp_serial_prefixes):
            return None # Reject invalid candidates immediately
        
        # Filter out blacklisted words
        if uc in BLACKLISTED_WORDS:
            return None
        
        # Strict length check for HP serials
        if not (9 <= len(uc) <= 12):
            return None
            
        score = 0
        letters = sum(1 for c in uc if c.isalpha())
        digits = sum(1 for c in uc if c.isdigit())
        
        # Check for a good mix of letters and digits
        if letters >= 2 and digits >= 2:
            score += 100
        else:
            return None # Reject if not mixed
        
        # High bonus for context keywords
        score += bonus
        
        if encoding.startswith('UTF-16'):
            score += 200 # New: Very high bonus for Unicode
            
        return {'value': key, 'score': score, 'occurrences': [(offset, encoding, source)]}

    max_len = 60 if deep else 40
    pattern = re.compile(rb'[A-Za-z0-9][A-Za-z0-9\-./]{6,' + str(max_len - 1).encode() + rb'}', re.IGNORECASE)
    keywords = [b"serial", b"service tag", b"s/n", b"ct number", b"product"]
    
    # Improved loop for finding candidates
    for m in pattern.finditer(data):
        try:
            s = m.group(0).decode('ascii', errors='ignore').strip()
        except:
            s = m.group(0).decode('latin-1', errors='ignore').strip()
        off = m.start()
        ctx = data[max(0, off - (512 if deep else 128)): off + (512 if deep else 128)].lower()
        bonus = 100 if any(kw in ctx for kw in keywords) else 0
        candidate = score_candidate(s, off, 'ASCII', 'Regex', bonus=bonus)
        if candidate:
            candidates.append(candidate)

    # Unicode (UTF-16LE/BE) extraction
    for off, s in find_utf16le_runs(data, min_chars=4):
        for t in re.split(r'[\s\x00:;,/\\|]+', s):
            t = t.strip()
            if 4 <= len(t) <= 60:
                ctx = data[max(0, off - 256): off + 256].lower()
                bonus = 100 if any(kw in ctx for kw in keywords) else 0
                candidate = score_candidate(t, off, 'UTF-16LE', 'Unicode', bonus=bonus)
                if candidate:
                    candidates.append(candidate)

    for off, s in find_utf16be_runs(data, min_chars=4):
        for t in re.split(r'[\s\x00:;,/\\|]+', s):
            t = t.strip()
            if 4 <= len(t) <= 60:
                ctx = data[max(0, off - 256): off + 256].lower()
                bonus = 100 if any(kw in ctx for kw in keywords) else 0
                candidate = score_candidate(t, off, 'UTF-16BE', 'Unicode', bonus=bonus)
                if candidate:
                    candidates.append(candidate)
    
    # Merge and sort unique candidates
    unique_candidates = {}
    for c in candidates:
        key = c['value']
        if key not in unique_candidates:
            unique_candidates[key] = c
        else:
            unique_candidates[key]['score'] += c['score']
            unique_candidates[key]['occurrences'].extend(c['occurrences'])
            
    final_results = list(unique_candidates.values())
    final_results.sort(key=lambda x: x['score'], reverse=True)
    return final_results

# -----------------------
# GUI helpers
def analyze_file_thread(filepath, deep=False):
    threading.Thread(target=analyze_file_logic, args=(filepath, deep), daemon=True).start()

def browse_file():
    filepath = filedialog.askopenfilename(
        title="Select BIOS file",
        filetypes=[("BIOS files", "*.bin *.rom *.fd *.cap"), ("All files", "*.*")]
    )
    if filepath:
        analyze_file_thread(filepath)

def analyze_file_logic(filepath, deep=False):
    try:
        with open(filepath, "rb") as f:
            data = f.read()

        root.after(0, log_box.delete, "1.0", tk.END)
        root.after(0, log_box.insert, tk.END, f"[+] File: {os.path.basename(filepath)}\n\n")

        # Prioritize SMBIOS first
        smbios = parse_smbios(data)
        if smbios:
            root.after(0, result_var.set, f"Best Candidate (SMBIOS): {smbios[0]}")
            root.after(0, log_box.insert, tk.END, "[SMBIOS Results - High Confidence]\n")
            for s in smbios:
                root.after(0, log_box.insert, tk.END, f" → {s}\n")
            return

        # Fallback to general search if SMBIOS fails
        results = extract_and_score_candidates(data, deep=deep)
        if results:
            best = results[0]
            root.after(0, result_var.set, f"Best Candidate: {best['value']}")
            root.after(0, log_box.insert, tk.END, f"[+] Found {len(results)} candidates (ranked).\n\n")
            root.after(0, log_box.insert, tk.END, "--- Top Candidates ---\n")
            for i, r in enumerate(results[:15], 1):
                root.after(0, log_box.insert, tk.END, f"{i}. {r['value']} (score={r['score']})\n")
                occs = r.get('occurrences', [])[:4]
                for off, enc, src in occs:
                    root.after(0, log_box.insert, tk.END, f"    - {src} @ 0x{off:X} ({enc})\n" if isinstance(off, int) else f"    - {src} @ {off} ({enc})\n")
                root.after(0, log_box.insert, tk.END, "\n")
        else:
            root.after(0, result_var.set, "Serial Number not found.")
            root.after(0, log_box.insert, tk.END, "[-] Serial Number not found.\n")
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
        root.after(0, log_box.insert, tk.END, f"[!] Critical Error: {e}\n")

def save_result():
    result = result_var.get()
    if not result or "not found" in result:
        messagebox.showwarning("Warning", "No result to save.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".txt")
    if filepath:
        try:
            val = result.split(":", 1)[1].strip()
            with open(filepath, "w", encoding="utf8") as f:
                f.write(val + "\n")
            messagebox.showinfo("Saved", f"Saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")

def copy_result():
    result = result_var.get()
    if result and "not found" not in result:
        try:
            val = result.split(":", 1)[1].strip()
            root.clipboard_clear()
            root.clipboard_append(val)
            messagebox.showinfo("Copied", "Serial copied to clipboard.")
        except Exception as e:
            messagebox.showerror("Error", f"Copy failed: {e}")
    else:
        messagebox.showwarning("Warning", "No result to copy.")

def deep_scan():
    filepath = filedialog.askopenfilename(
        title="Select BIOS file for Deep Scan",
        filetypes=[("BIOS files", "*.bin *.rom *.fd *.cap"), ("All files", "*.*")]
    )
    if filepath:
        analyze_file_thread(filepath, deep=True)

# -----------------------
# GUI
if __name__ == "__main__":
    root = tk.Tk()
    root.title("HP BIOS Serial Extractor (Unicode + Full Prefixes)")
    root.geometry("820x640")

    result_var = tk.StringVar(value="Select a BIOS file to analyze.")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Button(frame, text="Browse BIOS File", command=browse_file).pack(side=tk.LEFT, padx=6)
    tk.Button(frame, text="Deep Scan", command=deep_scan, fg="red").pack(side=tk.LEFT, padx=6)
    tk.Button(frame, text="Save Result", command=save_result).pack(side=tk.LEFT, padx=6)
    tk.Button(frame, text="Copy Result", command=copy_result).pack(side=tk.LEFT, padx=6)

    tk.Label(root, textvariable=result_var, font=("Arial", 13, "bold"), fg="blue", wraplength=780, justify="center").pack(pady=10)

    log_box = scrolledtext.ScrolledText(root, width=100, height=30)
    log_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    contact_info = tk.Label(root, text="Developed by Mohamed Nasser\n+201068111576", font=("Arial", 12, "bold"), fg="#008000")
    contact_info.pack(pady=5)
    
    class TextRedirector(object):
        def __init__(self, widget, tag="stdout"):
            self.widget = widget
            self.tag = tag
        def write(self, str):
            self.widget.insert(tk.END, str, (self.tag,))
            self.widget.see(tk.END)
        def flush(self):
            pass

    sys.stdout = TextRedirector(log_box, "stdout")
    sys.stderr = TextRedirector(log_box, "stderr")

    root.mainloop()