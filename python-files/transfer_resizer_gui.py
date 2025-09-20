# -*- coding: utf-8 -*-
"""
Transfer Resizer GUI

Aplicación de escritorio (Tkinter + Pillow) para convertir imágenes a PNG con
un tamaño final fijo en centímetros (por defecto 58 x 100 cm) y resolución
de impresión. Pensada para dejar los archivos listos para imprimir en papel
transfer.

Características:
- Selección de múltiples archivos (JPG, PNG, TIFF, WebP, etc.)
- Conversión a PNG con DPI incrustado (300 ppp por defecto)
- Redimensionado exacto a tamaño físico (cm → píxeles según DPI)
- Dos modos de ajuste:
  * "Ajustar con relleno" (no recorta; añade fondo blanco o transparente)
  * "Rellenar y recortar" (cubre todo el lienzo y recorta el exceso)
- Opción de espejo horizontal (recomendado para algunas láminas transfer)
- Opción de fondo: blanco o transparente (para PNG)
- Informe por archivo (aviso si la imagen original tiene resolución insuficiente)

Requisitos:
    pip install pillow

Ejecución:
    python transfer_resizer_gui.py

Autor: ChatGPT
Licencia: MIT
"""

from __future__ import annotations
import os
import sys
import math
import traceback
from typing import List, Tuple

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except Exception:
    print("Tkinter no disponible en este entorno.")
    sys.exit(1)

from PIL import Image, ImageOps

# Intentar usar gestión de color si está disponible (opcional)
try:
    from PIL import ImageCms  # type: ignore
    HAS_IMAGECMS = True
except Exception:
    HAS_IMAGECMS = False

APP_TITLE = "Transfer Resizer GUI"
SUPPORTED_EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp", ".heic", ".heif")


def cm_to_px(cm: float, dpi: int) -> int:
    return int(round(cm * dpi / 2.54))


def safe_open_image(path: str) -> Image.Image:
    """Abre una imagen corrigiendo orientación EXIF y normalizando modos comunes."""
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    return im


def ensure_srgb(im: Image.Image) -> Image.Image:
    """Convierte la imagen a sRGB si es posible. Devuelve una copia en RGB/RGBA."""
    try:
        # Si la imagen ya es RGB/RGBA sin perfil, solo asegurar modo correcto
        if not HAS_IMAGECMS:
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA" if im.mode in ("LA", "P", "PA") else "RGB")
            return im

        icc = im.info.get("icc_profile")
        if icc:
            src_profile = ImageCms.ImageCmsProfile(bytes(icc))
            dst_profile = ImageCms.createProfile("sRGB")
            intent = ImageCms.INTENT_PERCEPTUAL
            # Elegir modo de salida según necesidad de alfa más adelante
            out_mode = "RGBA" if im.mode in ("RGBA", "LA") else "RGB"
            im = ImageCms.profileToProfile(im, src_profile, dst_profile, renderingIntent=intent, outputMode=out_mode)
        else:
            # Sin perfil incrustado: asegurar modo RGB/RGBA
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA" if im.mode in ("LA", "P", "PA") else "RGB")
        return im
    except Exception:
        # Si algo falla, continuar con conversión básica
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if im.mode in ("LA", "P", "PA") else "RGB")
        return im


def resize_with_letterbox(im: Image.Image, target_size: Tuple[int, int], transparent_bg: bool) -> Image.Image:
    """Ajusta la imagen dentro del lienzo objetivo añadiendo relleno (no recorta)."""
    target_w, target_h = target_size
    # Elegir modo final segun transparencia
    canvas_mode = "RGBA" if transparent_bg else "RGB"
    bg = (0, 0, 0, 0) if transparent_bg else (255, 255, 255)

    # Copia en sRGB y en modo con/ sin alfa acorde
    base = ensure_srgb(im)
    if transparent_bg and base.mode != "RGBA":
        base = base.convert("RGBA")
    if not transparent_bg and base.mode != "RGB":
        base = base.convert("RGB")

    # Redimensionar manteniendo proporciones
    base_copy = base.copy()
    base_copy.thumbnail((target_w, target_h), Image.LANCZOS)

    canvas = Image.new(canvas_mode, (target_w, target_h), bg)
    # Centrar
    x = (target_w - base_copy.width) // 2
    y = (target_h - base_copy.height) // 2
    canvas.paste(base_copy, (x, y), base_copy if base_copy.mode == "RGBA" else None)
    return canvas


def resize_with_cover_crop(im: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    """Cubre todo el lienzo y recorta el exceso manteniendo proporciones (como ImageOps.fit)."""
    target_w, target_h = target_size
    base = ensure_srgb(im)
    out_mode = "RGBA" if base.mode == "RGBA" else "RGB"
    result = ImageOps.fit(base.convert(out_mode), (target_w, target_h), method=Image.LANCZOS, centering=(0.5, 0.5))
    return result


def estimate_input_effective_dpi(im: Image.Image, target_cm: Tuple[float, float]) -> float:
    """Estima el DPI efectivo del archivo de entrada al imprimirlo a las dimensiones objetivo.
    (útil para advertencias de calidad)"""
    w_cm, h_cm = target_cm
    # DPI efectivo mínimo de la dimensión limitante
    # Relación píxeles / cm en cada eje
    px_per_cm_x = im.width / w_cm if w_cm > 0 else 0
    px_per_cm_y = im.height / h_cm if h_cm > 0 else 0
    # Convertir a ppp equivalentes (1 in = 2.54 cm)
    dpi_x = px_per_cm_x * 2.54
    dpi_y = px_per_cm_y * 2.54
    return min(dpi_x, dpi_y)


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("880x640")
        self.minsize(820, 560)

        # Variables de control
        self.width_cm_var = tk.DoubleVar(value=58.0)
        self.height_cm_var = tk.DoubleVar(value=100.0)
        self.dpi_var = tk.IntVar(value=300)
        self.mode_var = tk.StringVar(value="letterbox")  # letterbox | cover
        self.bg_var = tk.StringVar(value="white")        # white | transparent
        self.mirror_var = tk.BooleanVar(value=False)
        self.outdir_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}

        # Marco de opciones
        options = ttk.LabelFrame(self, text="Parámetros de salida")
        options.pack(fill="x", **pad)

        row = 0
        ttk.Label(options, text="Ancho (cm):").grid(row=row, column=0, sticky="w")
        ttk.Entry(options, textvariable=self.width_cm_var, width=8).grid(row=row, column=1, sticky="w")
        ttk.Label(options, text="Alto (cm):").grid(row=row, column=2, sticky="w", padx=(16, 2))
        ttk.Entry(options, textvariable=self.height_cm_var, width=8).grid(row=row, column=3, sticky="w")
        ttk.Label(options, text="DPI:").grid(row=row, column=4, sticky="w", padx=(16, 2))
        ttk.Spinbox(options, from_=72, to=1200, textvariable=self.dpi_var, width=6).grid(row=row, column=5, sticky="w")

        row += 1
        ttk.Label(options, text="Modo de ajuste:").grid(row=row, column=0, sticky="w")
        ttk.Radiobutton(options, text="Ajustar con relleno", value="letterbox", variable=self.mode_var).grid(row=row, column=1, columnspan=2, sticky="w")
        ttk.Radiobutton(options, text="Rellenar y recortar", value="cover", variable=self.mode_var).grid(row=row, column=3, columnspan=2, sticky="w")

        row += 1
        ttk.Label(options, text="Fondo:").grid(row=row, column=0, sticky="w")
        ttk.Radiobutton(options, text="Blanco", value="white", variable=self.bg_var).grid(row=row, column=1, sticky="w")
        ttk.Radiobutton(options, text="Transparente (PNG)", value="transparent", variable=self.bg_var).grid(row=row, column=2, columnspan=2, sticky="w")
        ttk.Checkbutton(options, text="Espejo horizontal (transfer)", variable=self.mirror_var).grid(row=row, column=4, columnspan=2, sticky="w")

        # Directorio de salida
        row += 1
        ttk.Label(options, text="Carpeta de salida:").grid(row=row, column=0, sticky="w")
        outdir_entry = ttk.Entry(options, textvariable=self.outdir_var, width=60)
        outdir_entry.grid(row=row, column=1, columnspan=4, sticky="we")
        ttk.Button(options, text="Elegir…", command=self.choose_outdir).grid(row=row, column=5, sticky="w")
        for i in range(6):
            options.columnconfigure(i, weight=1)

        # Lista de archivos
        files_frame = ttk.LabelFrame(self, text="Archivos a convertir")
        files_frame.pack(fill="both", expand=True, **pad)

        self.files_list = tk.Listbox(files_frame, selectmode=tk.EXTENDED)
        self.files_list.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=8)

        sb = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_list.yview)
        sb.pack(side="left", fill="y", pady=8)
        self.files_list.config(yscrollcommand=sb.set)

        btns = ttk.Frame(files_frame)
        btns.pack(side="right", fill="y", padx=10, pady=8)
        ttk.Button(btns, text="Añadir archivos…", command=self.add_files).pack(fill="x", pady=4)
        ttk.Button(btns, text="Quitar seleccionados", command=self.remove_selected).pack(fill="x", pady=4)
        ttk.Button(btns, text="Vaciar lista", command=self.clear_list).pack(fill="x", pady=4)

        # Progreso y acciones
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", **pad)

        self.progress = ttk.Progressbar(bottom, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", side="left", expand=True, padx=(0, 8))
        ttk.Button(bottom, text="Convertir", command=self.convert_all).pack(side="right")

        # Consola/log
        log_frame = ttk.LabelFrame(self, text="Registro")
        log_frame.pack(fill="both", expand=False, **pad)
        self.log_text = tk.Text(log_frame, height=8, wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=8, pady=8)

    # --- Callbacks de UI ---
    def add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Seleccionar imágenes",
            filetypes=[
                ("Imágenes", "*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.webp;*.bmp;*.heic;*.heif"),
                ("Todos los archivos", "*.*"),
            ],
        )
        for p in paths:
            if p and os.path.splitext(p)[1].lower() in SUPPORTED_EXTS:
                self.files_list.insert(tk.END, p)
        self.log(f"Añadidos {len(paths)} archivo(s).")

    def remove_selected(self) -> None:
        sel = list(self.files_list.curselection())
        sel.reverse()
        for idx in sel:
            self.files_list.delete(idx)
        self.log("Elementos seleccionados eliminados.")

    def clear_list(self) -> None:
        self.files_list.delete(0, tk.END)
        self.log("Lista vaciada.")

    def choose_outdir(self) -> None:
        d = filedialog.askdirectory(title="Elegir carpeta de salida")
        if d:
            self.outdir_var.set(d)

    def log(self, msg: str) -> None:
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.update_idletasks()

    # --- Núcleo de conversión ---
    def convert_all(self) -> None:
        try:
            files = list(self.files_list.get(0, tk.END))
            if not files:
                messagebox.showwarning(APP_TITLE, "Añade al menos un archivo.")
                return

            outdir = self.outdir_var.get().strip() or os.path.join(os.path.dirname(files[0]), "export_png")
            os.makedirs(outdir, exist_ok=True)

            width_cm = max(0.1, float(self.width_cm_var.get()))
            height_cm = max(0.1, float(self.height_cm_var.get()))
            dpi = max(72, int(self.dpi_var.get()))

            target_w = cm_to_px(width_cm, dpi)
            target_h = cm_to_px(height_cm, dpi)
            target_size = (target_w, target_h)

            mode = self.mode_var.get()
            transparent = self.bg_var.get() == "transparent"
            mirror = bool(self.mirror_var.get())

            self.progress.config(maximum=len(files), value=0)
            self.log(
                f"\nSalida: {width_cm:.2f} x {height_cm:.2f} cm  |  {dpi} DPI  →  {target_w}x{target_h} px  |  modo={mode}, fondo={'transparente' if transparent else 'blanco'}, espejo={mirror}."
            )

            for i, path in enumerate(files, 1):
                try:
                    img = safe_open_image(path)

                    # Aviso de calidad (DPI efectivo de la imagen fuente a tamaño final)
                    eff_dpi = estimate_input_effective_dpi(img, (width_cm, height_cm))
                    if eff_dpi < dpi:
                        self.log(f"⚠️ {os.path.basename(path)}: la resolución original rinde ~{eff_dpi:.0f} DPI al tamaño final (por debajo de {dpi} DPI).")

                    if mode == "letterbox":
                        out = resize_with_letterbox(img, target_size, transparent_bg=transparent)
                    else:
                        out = resize_with_cover_crop(img, target_size)
                        if not transparent and out.mode == "RGBA":
                            # Si se elige fondo blanco pero la imagen trae alfa, aplanar
                            bg = Image.new("RGB", out.size, (255, 255, 255))
                            bg.paste(out, mask=out.split()[-1])
                            out = bg

                    if mirror:
                        out = ImageOps.mirror(out)

                    # Asegurar modo final según fondo elegido
                    if transparent and out.mode != "RGBA":
                        out = out.convert("RGBA")
                    if not transparent and out.mode != "RGB":
                        out = out.convert("RGB")

                    base_name = os.path.splitext(os.path.basename(path))[0]
                    suffix = f"_{int(self.width_cm_var.get())}x{int(self.height_cm_var.get())}cm_{dpi}dpi"
                    if mirror:
                        suffix += "_mirror"
                    out_name = f"{base_name}{suffix}.png"
                    out_path = os.path.join(outdir, out_name)

                    # Guardar con metadatos de DPI
                    out.save(out_path, format="PNG", dpi=(dpi, dpi))
                    self.log(f"✅ Exportado: {out_name}")
                except Exception as e:
                    self.log(f"❌ Error con {os.path.basename(path)}: {e}")
                    traceback.print_exc()
                finally:
                    self.progress.step(1)
                    self.update_idletasks()

            self.log("\nProceso completado.")
            messagebox.showinfo(APP_TITLE, "Conversión finalizada.")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Error inesperado: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    app = App()
    app.mainloop()
