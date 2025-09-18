# file: ax_pdf_uploader.py
"""
AX PDF Uploader Bot (coordinate-based RPA using pyautogui).
Workflow:
1. User opens AX manually.
2. Bot clicks "Project Design Family Tree".
3. Waits 10s for AX to load.
4. Shows popup to enter Project Name, types it in the project search field.
5. Finds all PDFs in chosen folder (recursive).
6. For each PDF:
   - Enters the filename into filename search field.
   - Runs: Drawing Review → Create New Review → Attach File → Submit for Approval.
Calibration is done once, positions saved to config file.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, Tuple, List

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog
except Exception:
    tk = None

import pyautogui
import pyperclip

# Config & constants
CONFIG_FILE = Path(__file__).with_suffix(".config.json")
LOG_FILE = Path(__file__).with_suffix(".log")
pyautogui.FAILSAFE = True
DEFAULT_DELAY = 1.0  # base delay between UI actions (seconds)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console = logging.getLogger()
console.addHandler(logging.StreamHandler(sys.stdout))


def choose_folder_gui() -> str:
    if tk:
        root = tk.Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title="Select folder containing PDFs")
        root.update()
        root.destroy()
        if folder:
            return folder
    folder = input("Enter the folder path containing PDFs: ").strip('"').strip()
    return folder


def find_pdfs(root_folder: str) -> List[str]:
    pdfs = []
    for dirpath, _, filenames in os.walk(root_folder):
        for f in filenames:
            if f.lower().endswith(".pdf"):
                pdfs.append(os.path.join(dirpath, f))
    pdfs.sort()
    return pdfs


def save_config(cfg: Dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def load_config() -> Dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def prompt(msg: str):
    try:
        if tk:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("AX Uploader", msg)
            root.destroy()
        else:
            print(msg)
    except Exception:
        print(msg)


def prompt_input(msg: str) -> str:
    """Show popup to get text input from user"""
    if tk:
        root = tk.Tk()
        root.withdraw()
        value = simpledialog.askstring("AX Uploader", msg, parent=root)
        root.destroy()
        return value or ""
    else:
        return input(msg + ": ").strip()


def calibrate_positions() -> Dict[str, Tuple[int, int]]:
    needed = [
        ("family_tree", "Hover over the 'Project Design Family Tree' button and press Enter"),
        ("project_search", "Hover over the field where Project Name should be entered and press Enter"),
        ("filename_search", "Hover over the field where PDF filename should be entered and press Enter"),
        ("drawing_review", "Hover over the 'Drawing Review Detail' button and press Enter"),
        ("create_review", "Hover over the 'Create New Review' button and press Enter"),
        ("attach_file", "Hover over the 'Attach File' button (opens file dialog) and press Enter"),
        ("submit", "Hover over the 'Submit for Approval' button and press Enter"),
    ]
    positions = {}
    print("\n--- Calibration ---")
    print("For each prompt: hover over the AX UI element, then press Enter here.")
    time.sleep(1.0)
    for key, instruction in needed:
        input(f"{instruction}\nPress Enter when ready...")
        pos = pyautogui.position()
        positions[key] = {"x": pos.x, "y": pos.y}
        print(f"Captured {key} -> {pos}\n")
        time.sleep(0.4)
    while True:
        try:
            d = input(f"Enter base delay between clicks in seconds (float, default {DEFAULT_DELAY}): ").strip()
            base_delay = float(d) if d else DEFAULT_DELAY
            break
        except Exception:
            print("Invalid number, try again.")
    cfg = {"positions": positions, "delays": {"base_delay": base_delay}}
    save_config(cfg)
    print(f"Calibration saved to {CONFIG_FILE}")
    return cfg


def ensure_ax_ready():
    prompt("Please open AX, navigate to the start screen, keep it visible.\nPress Enter when ready.")
    input("Press Enter here when AX is ready and focused...")


def click_point(pt: Dict[str, int], description: str = "", clicks: int = 1, wait: float = 0.2):
    x, y = int(pt["x"]), int(pt["y"])
    logging.info(f"Clicking {description} at ({x},{y})")
    pyautogui.click(x=x, y=y, clicks=clicks, interval=0.12)
    time.sleep(wait)


def paste_and_enter(text: str):
    pyperclip.copy(text)
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")


def navigate_to_project(cfg: dict) -> str:
    pos = cfg["positions"]
    # 1. Click Family Tree
    click_point(pos["family_tree"], "Project Design Family Tree", wait=5)
    time.sleep(10)  # wait for AX to load family tree
    # 2. Ask user for Project Name via popup
    project_name = prompt_input("Enter Project Name to upload into")
    if not project_name:
        raise ValueError("No project name entered.")
    # 3. Enter Project Name
    click_point(pos["project_search"], "Project Search field", wait=1)
    paste_and_enter(project_name)
    time.sleep(3)
    return project_name


def upload_single_pdf(pdf_path: str, cfg: Dict, retry: int = 1) -> Tuple[bool, str]:
    pos = cfg["positions"]
    base_delay = cfg.get("delays", {}).get("base_delay", DEFAULT_DELAY)
    try:
        # 1. Enter filename in filename_search field
        filename = os.path.splitext(os.path.basename(pdf_path))[0]  # removes .pdf extension
        click_point(pos["filename_search"], "Filename Search field", wait=0.5)
        paste_and_enter(filename)
        time.sleep(base_delay + 1)

        # 2. Click Drawing Review Detail
        click_point(pos["drawing_review"], "Drawing Review Detail", wait=base_delay + 0.2)
        time.sleep(base_delay)

        # 3. Click Create New Review
        click_point(pos["create_review"], "Create New Review", wait=base_delay + 0.2)
        time.sleep(base_delay)

        # 4. Click Attach File
        click_point(pos["attach_file"], "Attach File", wait=base_delay + 0.2)
        time.sleep(base_delay + 0.5)

        # 5. File dialog: paste path + Enter
        paste_and_enter(pdf_path)
        time.sleep(base_delay + 1.0)

        # 6. Click Submit for Approval
        click_point(pos["submit"], "Submit for Approval", wait=base_delay + 0.5)
        time.sleep(base_delay + 0.8)

        logging.info(f"Uploaded: {pdf_path}")
        return True, "ok"

    except Exception as e:
        logging.exception("Upload error")
        if retry > 0:
            logging.info(f"Retrying {pdf_path} (retries left {retry})")
            time.sleep(1.0)
            return upload_single_pdf(pdf_path, cfg, retry=retry - 1)
        return False, str(e)


def main():
    print("\nAX PDF Uploader (with Project + Filename Search)\n")
    cfg = load_config()
    if not cfg:
        cfg = calibrate_positions()

    folder = choose_folder_gui()
    if not folder or not os.path.isdir(folder):
        print("No valid folder chosen. Exiting.")
        return
    pdfs = find_pdfs(folder)
    if not pdfs:
        print("No PDF files found in folder. Exiting.")
        return

    ensure_ax_ready()
    project_name = navigate_to_project(cfg)

    for idx, pdf in enumerate(pdfs, start=1):
        print(f"[{idx}/{len(pdfs)}] Processing: {pdf}")
        ok, msg = upload_single_pdf(pdf, cfg, retry=1)
        if not ok:
            print(f"Failed for {pdf}: {msg}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user.")
    except Exception:
        logging.exception("Fatal error")
        print("Fatal error occurred. See log file:", LOG_FILE)
