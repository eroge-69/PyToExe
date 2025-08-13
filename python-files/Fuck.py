import dnfile
import base64
import re
import sys
import os
from tqdm import tqdm
from tkinter import Tk, filedialog

# ----------------------------
# Heuristics for filtering junk
# ----------------------------

def is_printable_string(s: str, min_len=6) -> bool:
    if len(s) < min_len:
        return False
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,;:_-+=()[]{}<>@#$/\\|!?\"'")
    non_printable = sum(c not in allowed_chars for c in s)
    return (non_printable / len(s)) <= 0.1

def looks_like_identifier(s: str) -> bool:
    """Check if it looks like a namespace/class/method name"""
    return re.fullmatch(r'[A-Za-z0-9_.`$]+', s) is not None

def looks_like_base64(s: str) -> bool:
    s = s.strip().replace("\n", "")
    if len(s) < 8:
        return False
    return re.fullmatch(r'[A-Za-z0-9+/=]+', s) is not None

def try_multi_base64(s: str) -> str:
    """Try decoding multiple layers of Base64 until it fails"""
    data = s.strip()
    for _ in range(5):
        try:
            decoded_bytes = base64.b64decode(data + "=" * (-len(data) % 4))
            decoded = decoded_bytes.decode("utf-8")
            if looks_like_base64(decoded):
                data = decoded
            else:
                return decoded
        except Exception:
            return data
    return data

def is_probably_junk(s: str) -> bool:
    if len(s) < 6:
        return True
    if len(s) > 512:
        return True
    if not is_printable_string(s, min_len=6):
        return True
    # Reject hex or digit only strings
    if re.fullmatch(r"[0-9a-fA-F]+", s):
        return True
    if re.fullmatch(r"[0-9]+", s):
        return True
    # Reject very repetitive strings (2 or fewer unique chars, long enough)
    if len(set(s)) <= 2 and len(s) > 8:
        return True
    # Reject namespace/class/method style names (usually identifiers)
    if looks_like_identifier(s) and len(s) < 64:
        return True
    return False

def is_compiler_artifact(s: str) -> bool:
    patterns = [
        r"^<.*>$",                    # Anything enclosed in <>
        r"^<.*>b__\d+_\d+$",         # anonymous lambda method names like <Start>b__10_100
        r"^<>.*$",                   # names starting with <>
        r"^\[\w+\]$",                # attributes like [Serializable]
        r"^__.*$",                   # compiler temp vars
        r"^\d+$",                    # pure digits
    ]
    for p in patterns:
        if re.match(p, s):
            return True
    return False

# ----------------------------
# Extraction Functions (in discovery order)
# ----------------------------

def extract_from_user_strings(pe, progress_bar, counter, seen, ordered_strings):
    try:
        heap = pe.net.user_string_heap
        for _, val in heap.items():
            if isinstance(val, str) and val.strip() and val not in seen:
                seen.add(val)
                ordered_strings.append(val.strip())
                counter[0] += 1
                progress_bar.set_postfix(strings_found=counter[0])
    except Exception:
        pass
    progress_bar.update(1)

def extract_from_metadata(pe, progress_bar, counter, seen, ordered_strings):
    if hasattr(pe.net, "mdtables"):
        for name, table in pe.net.mdtables.__dict__.items():
            if hasattr(table, "rows"):
                for row in table.rows:
                    for val in row.__dict__.values():
                        if isinstance(val, str) and val.strip() and val not in seen:
                            seen.add(val.strip())
                            ordered_strings.append(val.strip())
                            counter[0] += 1
                            progress_bar.set_postfix(strings_found=counter[0])
    progress_bar.update(1)

def extract_from_method_il(pe, progress_bar, counter, seen, ordered_strings):
    if hasattr(pe.net, "mdtables") and hasattr(pe.net.mdtables, "MethodDef"):
        methods = pe.net.mdtables.MethodDef.rows
        for method in methods:
            if getattr(method, "ImplFlags", None) is not None and getattr(method, "Rva", 0) != 0:
                try:
                    body = pe.get_data(method.Rva, method.CodeSize)
                    for match in re.findall(rb"[\x20-\x7E]{4,}", body):
                        try:
                            s = match.decode("utf-8").strip()
                            if s and s not in seen:
                                seen.add(s)
                                ordered_strings.append(s)
                                counter[0] += 1
                                progress_bar.set_postfix(strings_found=counter[0])
                        except:
                            pass
                except:
                    continue
    progress_bar.update(1)

def extract_from_raw_sections(pe, progress_bar, counter, seen, ordered_strings):
    for section in pe.sections:
        try:
            data = pe.get_data(section.VirtualAddress, section.SizeOfRawData)
        except Exception:
            continue

        # ASCII strings
        for match in re.findall(rb"[\x20-\x7E]{4,}", data):
            try:
                s = match.decode("utf-8").strip()
                if s and s not in seen:
                    seen.add(s)
                    ordered_strings.append(s)
                    counter[0] += 1
                    progress_bar.set_postfix(strings_found=counter[0])
            except:
                pass

        # UTF-16 LE strings
        for match in re.findall(rb"(?:[\x20-\x7E]\x00){4,}", data):
            try:
                s = match.decode("utf-16le").strip()
                if s and s not in seen:
                    seen.add(s)
                    ordered_strings.append(s)
                    counter[0] += 1
                    progress_bar.set_postfix(strings_found=counter[0])
            except:
                pass

    progress_bar.update(1)

def extract_all_strings(file_path):
    pe = dnfile.dnPE(file_path)
    ordered_strings = []
    seen = set()
    counter = [0]

    phases = [
        extract_from_user_strings,
        extract_from_metadata,
        extract_from_method_il,
        extract_from_raw_sections,
    ]

    with tqdm(total=len(phases), desc="Scanning Phases") as progress_bar:
        for phase_func in phases:
            phase_func(pe, progress_bar, counter, seen, ordered_strings)

    print(f"[+] Total unique strings found: {counter[0]}")
    return ordered_strings

# ----------------------------
# Main processing
# ----------------------------

def process_assembly(file_path):
    all_strings = extract_all_strings(file_path)
    filtered_results = []

    for s in tqdm(all_strings, desc="Filtering Strings"):
        if is_probably_junk(s) or is_compiler_artifact(s):
            continue

        if looks_like_base64(s):
            decoded = try_multi_base64(s)
            if is_probably_junk(decoded) or is_compiler_artifact(decoded):
                continue
            filtered_results.append((s, decoded))
        else:
            filtered_results.append((s, s))

    return filtered_results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        dll_path = sys.argv[1]
    else:
        root = Tk()
        root.withdraw()
        dll_path = filedialog.askopenfilename(
            title="Select a .NET DLL/EXE",
            filetypes=[("Assemblies", "*.dll *.exe"), ("All files", "*.*")]
        )
        root.update()

    if not dll_path:
        print("No file selected.")
        sys.exit(0)

    print(f"[*] Extracting filtered strings from: {dll_path}")
    filtered_results = process_assembly(dll_path)

    base_name = os.path.splitext(os.path.basename(dll_path))[0]

    out_file_all = base_name + "_filtered_strings.txt"
    with open(out_file_all, "w", encoding="utf-8") as f:
        for orig, dec in filtered_results:
            if orig != dec:
                f.write(f"[ENCODED] {orig} -> [DECODED] {dec}\n")
            else:
                f.write(f"{orig}\n")

    print(f"[+] Done! Extracted {len(filtered_results)} filtered strings → saved to {out_file_all}")
