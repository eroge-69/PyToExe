# -*- coding: utf-8 -*-
"""
tinder_scans.py
---------------
UI Tkinter pour trier/valider des pages (images et/ou PDF) et fabriquer un ou plusieurs gros PDF.

Modifs (cette version) :
- En fin de sélection (plus d'éléments) :
  1) proposer d’enregistrer le lot courant s’il n’est pas vide (AskString ; Cancel = pas d’enregistrement, sélection conservée)
  2) proposer ensuite de supprimer les dossiers parcourus (selon les mêmes règles)
     -> si l’utilisateur clique sur NON, le programme NE se ferme PAS (il reste ouvert).
- Le comportement sur fermeture (croix rouge / Échap) reste inchangé : on propose de vider, puis on ferme.
"""

import os
import sys
import argparse
import logging
import shutil
from dataclasses import dataclass
from typing import List, Optional, Tuple, Set, Dict

from PIL import Image, ImageTk, ImageOps
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from natsort import natsorted

# IMPORTANT: tkfilebrowser apporte des boîtes de dialogue avancées (multi-dossiers)
try:
    from tkfilebrowser import askopendirnames, askopendirname
except Exception as e:
    raise SystemExit("tkfilebrowser n'est pas installé. Faites : pip install tkfilebrowser") from e

LOG_FILE = "tinder_scans.log"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".gif"}
WINDOW_W, WINDOW_H = 1100, 800


@dataclass
class PageItem:
    source_type: str           # "image" ou "pdf"
    file_path: str             # chemin image ou PDF
    page_index: Optional[int]  # index pour PDF, sinon None
    folder: str                # dossier source (sélectionné)
    rotation_quarter: int = 0
    note: str = ""


def is_image_file(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in IMAGE_EXTS

def natural_listdir(path: str) -> List[str]:
    try:
        return natsorted(os.listdir(path))
    except FileNotFoundError:
        return []

def next_available_name(out_dir: str, prefix: str = "merged_", ext: str = ".pdf") -> str:
    i = 1
    while True:
        name = f"{prefix}{i:03d}{ext}"
        path = os.path.join(out_dir, name)
        if not os.path.exists(path):
            return path
        i += 1

def render_pdf_page_to_pil(pdf_path: str, page_index: int, dpi: int = 150) -> Image.Image:
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    with fitz.open(pdf_path) as doc:
        page = doc.load_page(page_index)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

def open_image_as_rgb(path: str) -> Image.Image:
    with Image.open(path) as im:
        return im.convert("RGB")

def apply_rotation_quarter(im: Image.Image, rotation_quarter: int) -> Image.Image:
    q = rotation_quarter % 4
    if q == 0:
        return im
    return im.rotate(-90 * q, expand=True)

def fit_in_box(im: Image.Image, box_w: int, box_h: int) -> Image.Image:
    return ImageOps.contain(im, (box_w, box_h))

def mtime(path: str) -> float:
    try:
        return os.path.getmtime(path)  # date de MODIFICATION
    except Exception:
        return float("inf")


def ask_sources_and_output() -> Tuple[List[str], str]:
    """1) multi-dossiers sources, 2) dossier de sortie."""
    root = tk.Tk()
    root.withdraw()

    sources_tuple = askopendirnames(
        title="Choisissez les dossiers SOURCES (multi-sélection)",
        initialdir=os.getcwd()
    )
    if not sources_tuple or len(sources_tuple) == 0:
        messagebox.showinfo("Aucun dossier", "Aucun dossier source sélectionné. Arrêt.")
        root.destroy(); sys.exit(0)

    sources = [p for p in sources_tuple if p and os.path.isdir(p)]
    if not sources:
        messagebox.showinfo("Aucun dossier", "Sélection invalide. Arrêt.")
        root.destroy(); sys.exit(0)

    output_dir = filedialog.askdirectory(
        title="Choisir le dossier de SORTIE des PDF",
        initialdir=os.path.dirname(sources[0]) if sources else os.getcwd()
    )
    if not output_dir or not os.path.isdir(output_dir):
        messagebox.showinfo("Annulé", "Aucun dossier de sortie sélectionné. Arrêt.")
        root.destroy(); sys.exit(0)

    root.destroy()
    return sources, output_dir


def folder_key_oldest_eligible(folder: str) -> Tuple[float, str]:
    entries = natural_listdir(folder)
    pdfs = [os.path.join(folder, f) for f in entries if f.lower().endswith(".pdf")]
    imgs = [os.path.join(folder, f) for f in entries if is_image_file(f)]
    if pdfs:
        t = min((mtime(p) for p in pdfs), default=float("inf"))
    elif imgs:
        t = min((mtime(i) for i in imgs), default=float("inf"))
    else:
        t = float("inf")
    return (t, os.path.basename(folder).lower())

def collect_page_items_from_sources(source_dirs: List[str]) -> List[PageItem]:
    items: List[PageItem] = []
    folders = sorted({d for d in source_dirs if os.path.isdir(d)}, key=folder_key_oldest_eligible)

    for folder in folders:
        entries = natural_listdir(folder)
        if not entries:
            continue

        pdfs = [os.path.join(folder, f) for f in entries if f.lower().endswith(".pdf")]
        images = [os.path.join(folder, f) for f in entries if is_image_file(f)]

        if pdfs:
            pdfs.sort(key=mtime)
            for pdf in pdfs:
                try:
                    with fitz.open(pdf) as doc:
                        n_pages = doc.page_count
                    for p in range(n_pages):
                        items.append(PageItem("pdf", pdf, p, folder))
                except Exception as e:
                    logging.exception(f"PDF illisible, ignoré: {pdf} ({e})")
        elif images:
            images.sort(key=mtime)
            for img in images:
                items.append(PageItem("image", img, None, folder))

    return items


class LotManager:
    def __init__(self):
        self.accepted_indices: List[int] = []

    def accept(self, idx: int):
        self.accepted_indices.append(idx)

    def remove_if_present(self, idx: int):
        if idx in self.accepted_indices:
            for i in range(len(self.accepted_indices) - 1, -1, -1):
                if self.accepted_indices[i] == idx:
                    self.accepted_indices.pop(i)
                    break

    def clear(self):
        self.accepted_indices.clear()

    def is_empty(self) -> bool:
        return len(self.accepted_indices) == 0

    def __len__(self):
        return len(self.accepted_indices)


class TinderUI:
    def __init__(self, source_dirs: List[str], output_dir: str, dpi: int = 300):
        self.source_dirs = source_dirs
        self.output_dir = output_dir
        self.dpi = dpi

        self.items: List[PageItem] = collect_page_items_from_sources(self.source_dirs)
        self.n_items = len(self.items)
        self.index = 0

        self.lot_manager = LotManager()
        self.folders_seen: Set[str] = set()
        self.pdf_pages_seen: Set[Tuple[str, int]] = set()
        self.pdf_total_pages: Dict[str, int] = {}

        self.end_reached = False  # évite de re-proposer en boucle la séquence de fin

        self.win = tk.Tk()
        self.win.title("Tinder de pages (images + PDF)")
        self.win.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.win.protocol("WM_DELETE_WINDOW", self.on_close_request)

        self.canvas = tk.Canvas(self.win, bg="black", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10, fill="both", expand=True)

        self.info_var = tk.StringVar()
        self.info_label = tk.Label(self.win, textvariable=self.info_var, anchor="w", justify="left")
        self.info_label.pack(fill="x", padx=10, pady=(0, 8))

        self.win.bind("<Key-a>", self.on_accept)
        self.win.bind("<Key-z>", self.on_reject)
        self.win.bind("<Key-t>", self.on_rotate)
        self.win.bind("<Key-r>", self.on_back)
        self.win.bind("<Key-s>", self.on_save_lot)
        self.win.bind("<Key-q>", self.on_quick_add)
        self.win.bind("<Escape>", self.on_close_request)

        self.win.bind("<Configure>", lambda e: self.refresh_ui())

        self.tk_img_current = None
        self.tk_img_preview = None

        if self.n_items == 0:
            messagebox.showinfo("Aucune page", "Aucun PDF ou image éligible trouvé dans les dossiers sélectionnés.")
        else:
            self.refresh_ui()

        self.win.mainloop()

    # ---- suivi vu ----
    def _mark_seen(self, item: PageItem):
        self.folders_seen.add(item.folder)
        if item.source_type == "pdf":
            self.pdf_pages_seen.add((item.file_path, item.page_index))
            if item.file_path not in self.pdf_total_pages:
                try:
                    with fitz.open(item.file_path) as doc:
                        self.pdf_total_pages[item.file_path] = doc.page_count
                except Exception:
                    self.pdf_total_pages[item.file_path] = 0

    # ---- rendu ----
    def load_page_image(self, item: PageItem, max_w: int, max_h: int, dpi_hint: int) -> Image.Image:
        try:
            if item.source_type == "pdf":
                im = render_pdf_page_to_pil(item.file_path, item.page_index, dpi=dpi_hint)
            else:
                im = open_image_as_rgb(item.file_path)
        except Exception as e:
            logging.exception(f"Erreur de rendu: {item} -> {e}")
            im = Image.new("RGB", (640, 480), color=(80, 80, 80))
        im = apply_rotation_quarter(im, item.rotation_quarter)
        return fit_in_box(im, max_w, max_h)

    def refresh_ui(self):
        if self.n_items == 0 or not self.win.winfo_exists():
            return
        self.index = max(0, min(self.index, self.n_items - 1))
        cur = self.items[self.index]
        nxt = self.items[self.index + 1] if (self.index + 1) < self.n_items else None

        self._mark_seen(cur)

        self.win.update_idletasks()
        cw, ch = max(200, self.canvas.winfo_width()), max(200, self.canvas.winfo_height())
        main_w, main_h = int(cw * 0.86), int(ch * 0.82)
        prev_w, prev_h = max(220, min(int(cw * 0.28), 520)), max(150, min(int(ch * 0.28), 360))

        img_cur = self.load_page_image(cur, main_w, main_h, dpi_hint=180)
        self.tk_img_current = ImageTk.PhotoImage(img_cur)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, image=self.tk_img_current, anchor="center")

        if nxt is not None:
            img_prev = self.load_page_image(nxt, prev_w, prev_h, dpi_hint=120)
            self.tk_img_preview = ImageTk.PhotoImage(img_prev)
            x, y = cw - (prev_w // 2) - 12, (prev_h // 2) + 12
            self.canvas.create_rectangle(x - prev_w // 2 - 4, y - prev_h // 2 - 4,
                                         x + prev_w // 2 + 4, y + prev_h // 2 + 4,
                                         fill="#222222", outline="#555555")
            self.canvas.create_image(x, y, image=self.tk_img_preview, anchor="center")
            self.canvas.create_text(x, y - prev_h // 2 - 10, text="(aperçu suivante)", fill="white", anchor="s")

        suffix = " | FIN atteinte" if self.end_reached else ""
        self.info_var.set(self.make_info_text(cur) + suffix)

    def make_info_text(self, item: PageItem) -> str:
        src = "PDF" if item.source_type == "pdf" else "IMG"
        page_info = f"p.{item.page_index + 1}" if item.source_type == "pdf" else ""
        rotation = 90 * (item.rotation_quarter % 4)
        return (f"Élément {self.index + 1}/{self.n_items} | Lot: {len(self.lot_manager)} page(s) "
                f"| Type: {src} {page_info} | Rotation: {rotation}°\n"
                f"Dossier: {item.folder}\nSource: {item.file_path}")

    # ---- actions ----
    def on_accept(self, e=None):
        self.lot_manager.accept(self.index)
        self.goto_next()

    def on_reject(self, e=None):
        self.lot_manager.remove_if_present(self.index)
        self.goto_next()

    def on_rotate(self, e=None):
        self.items[self.index].rotation_quarter = (self.items[self.index].rotation_quarter + 1) % 4
        self.refresh_ui()

    def on_back(self, e=None):
        if self.index > 0:
            prev_idx = self.index - 1
            self.lot_manager.remove_if_present(prev_idx)
            self.index = prev_idx
            self.refresh_ui()

    def on_save_lot(self, e=None):
        if len(self.lot_manager) == 0:
            messagebox.showinfo("Lot vide", "Aucune page acceptée.")
            return
        self._save_lot_with_prompt()

    def on_quick_add(self, e=None):
        item = self.items[self.index]
        item.rotation_quarter = (item.rotation_quarter + 2) % 4
        self.lot_manager.accept(self.index)
        self.goto_next()

    # ---- fin / fermeture ----
    def on_close_request(self, e=None):
        """Fermeture par croix rouge / Échap -> on propose de vider puis on ferme (comportement inchangé)."""
        if messagebox.askyesno(
            "Vider les dossiers parcourus ?",
            "Supprimer les dossiers sources parcourus ?\n"
            "(Images seules -> supprimés ; Dossiers avec PDF -> supprimés si tous les PDF ont été entièrement parcourus ; Dossiers vides -> supprimés)"
        ):
            self._cleanup_sources_parcourus()
        self.win.destroy()

    def goto_next(self):
        if self.index < self.n_items - 1:
            self.index += 1
            self.refresh_ui()
        else:
            self._on_end_reached()

    # ---- logique fin de sélection ----
    def _on_end_reached(self):
        """Plus d’éléments : proposer d’abord l’enregistrement, puis (optionnel) la suppression.
           Ne pas fermer si l’utilisateur refuse la suppression."""
        if self.end_reached:
            # déjà traité ; ne pas boucler
            return
        self.end_reached = True

        # 1) proposer d’enregistrer le lot courant (s’il y en a un)
        if len(self.lot_manager) > 0:
            if messagebox.askyesno("Fin de sélection", "Voulez-vous enregistrer le lot courant en PDF ?"):
                self._save_lot_with_prompt()
            # si Non : on ne sauvegarde pas (sélection conservée)

        # 2) proposer de supprimer les dossiers parcourus
        if messagebox.askyesno(
            "Supprimer les dossiers parcourus ?",
            "Supprimer les dossiers sources parcourus ?\n"
            "(Images seules -> supprimés ; Dossiers avec PDF -> supprimés si tous les PDF ont été entièrement parcourus ; Dossiers vides -> supprimés)"
        ):
            self._cleanup_sources_parcourus()
            messagebox.showinfo("Terminé", "Nettoyage effectué. L’application reste ouverte.")
        else:
            # NE PAS fermer : rester sur la dernière page, avec un suffixe 'FIN atteinte'
            messagebox.showinfo("Fin", "Fin de la sélection. L’application reste ouverte.")

        # Rester affiché sur le dernier élément
        self.refresh_ui()

    def _save_lot_with_prompt(self):
        """Boîte de nommage + export ; Cancel -> on n’enregistre pas, on conserve la sélection."""
        name = simpledialog.askstring("Nom du PDF", "Entrez le nom du fichier (sans .pdf) :")
        if name is None:
            # Cancel
            messagebox.showinfo("Annulé", "Enregistrement annulé. La sélection est conservée.")
            return
        name = name.strip()
        out_path = (os.path.join(self.output_dir, name + ".pdf")
                    if name else next_available_name(self.output_dir, prefix="merged_", ext=".pdf"))
        try:
            self.export_current_lot(out_path)
            messagebox.showinfo("PDF enregistré", f"Fichier créé :\n{out_path}")
            self.lot_manager.clear()
            self.refresh_ui()
        except Exception as e:
            logging.exception(f"Échec export: {e}")
            messagebox.showerror("Erreur", f"Échec export:\n{e}")

    # ---- export PDF ----
    def export_current_lot(self, out_path: str):
        pil_pages: List[Image.Image] = []
        for idx in self.lot_manager.accepted_indices:
            item = self.items[idx]
            im = (render_pdf_page_to_pil(item.file_path, item.page_index, dpi=self.dpi)
                  if item.source_type == "pdf" else open_image_as_rgb(item.file_path))
            im = apply_rotation_quarter(im, item.rotation_quarter)
            pil_pages.append(im)
        first, rest = pil_pages[0], pil_pages[1:]
        first.save(out_path, "PDF", save_all=True, append_images=rest)

    # ---- nettoyage ----
    def _cleanup_sources_parcourus(self):
        deleted = 0
        for folder in sorted(self.folders_seen):
            try:
                if not os.path.isdir(folder):
                    continue
                entries = natural_listdir(folder)
                if not entries:
                    shutil.rmtree(folder, ignore_errors=True)
                    deleted += 1
                    continue

                pdfs = [os.path.join(folder, f) for f in entries if f.lower().endswith(".pdf")]

                if pdfs:
                    all_pdfs_complete = True
                    for pdf in pdfs:
                        total = self.pdf_total_pages.get(pdf)
                        if total is None:
                            all_pdfs_complete = False
                            break
                        seen_count = sum(1 for (ppath, _) in self.pdf_pages_seen if ppath == pdf)
                        if seen_count < total:
                            all_pdfs_complete = False
                            break
                    if all_pdfs_complete:
                        shutil.rmtree(folder, ignore_errors=True)
                        deleted += 1
                else:
                    shutil.rmtree(folder, ignore_errors=True)
                    deleted += 1
            except Exception as ex:
                logging.exception(f"Suppression échouée: {folder} ({ex})")

        messagebox.showinfo("Nettoyage", f"{deleted} dossier(s) supprimé(s).")


def main():
    parser = argparse.ArgumentParser(description="Tinder de pages (images + PDF) -> gros PDF(s)")
    parser.add_argument("--dpi", type=int, default=300, help="DPI d'export des pages PDF.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"),
                                  logging.StreamHandler(sys.stdout)])

    source_dirs, output_dir = ask_sources_and_output()
    TinderUI(source_dirs=source_dirs, output_dir=output_dir, dpi=args.dpi)

if __name__ == "__main__":
    main()
