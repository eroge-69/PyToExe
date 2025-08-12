#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import threading
import traceback
from tkinter import Tk, StringVar, IntVar, BooleanVar, filedialog, messagebox
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, UnidentifiedImageError, ImageSequence
import subprocess

# Optional drag & drop — tkinterdnd2 (instalar opcionalmente)
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False

# Optional imageio for animated webp
try:
    import imageio.v3 as iio
    IMAGEIO_AVAILABLE = True
except Exception:
    IMAGEIO_AVAILABLE = False

SUPPORTED = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp')

def is_animated_gif(path):
    try:
        with Image.open(path) as im:
            return getattr(im, "is_animated", False)
    except Exception:
        return False

def convert_single(input_path, out_folder, quality, keep_exif, overwrite, convert_animated_with_ffmpeg):
    name = os.path.splitext(os.path.basename(input_path))[0]
    ext = os.path.splitext(input_path)[1].lower()
    out_path = os.path.join(out_folder, f"{name}.webp")

    if not overwrite and os.path.exists(out_path):
        return f"skip: {input_path} -> existe {out_path}"

    # Animated GIF handling
    if ext == ".gif" and is_animated_gif(input_path):
        # Prefer imageio (pure-python) if available and ffmpeg not forced
        if IMAGEIO_AVAILABLE and not convert_animated_with_ffmpeg:
            try:
                seq = iio.imread(input_path, index=None)  # list of frames
                # imageio v3 will infer webp animated if extension .webp and params
                iio.imwrite(out_path, seq, extension=".webp", quality=quality)
                return f"ok: {input_path}"
            except Exception as e:
                # fallback to ffmpeg approach
                pass

        # Use ffmpeg if available
        try:
            # ffmpeg -i in.gif -lossless 0 -q:v (quality) out.webp
            cmd = ["ffmpeg", "-y", "-i", input_path, "-vcodec", "libwebp", "-filter:v", "fps=fps=15", "-lossless", "0", "-qscale", str(max(0, min(100, quality))), out_path]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode == 0 and os.path.exists(out_path):
                return f"ok: {input_path}"
            else:
                return f"error(ffmpeg): {input_path} -> {proc.stderr.decode('utf-8', errors='ignore')[:200]}"
        except FileNotFoundError:
            return f"error: ffmpeg no encontrado para animación -> {input_path}"
        except Exception as e:
            return f"error(ffmpeg): {input_path} -> {e}"

    # Non-animated conversion via Pillow
    try:
        img = Image.open(input_path)
        save_params = {"format": "WEBP", "quality": int(quality)}
        if keep_exif and "exif" in img.info:
            save_params["exif"] = img.info["exif"]

        # Manage transparency
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGBA")
            # Pillow will save RGBA webp with alpha
        else:
            img = img.convert("RGB")

        img.save(out_path, **save_params)
        return f"ok: {input_path}"
    except UnidentifiedImageError:
        return f"error: no es imagen válida -> {input_path}"
    except Exception as e:
        return f"error: {input_path} -> {str(e)[:200]}"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Convertidor Pro a WebP")
        self.root.geometry("720x520")
        # If DND available, root could be TkinterDnD.Tk()
        self.files = []
        self.setup_vars()
        self.build_ui()

    def setup_vars(self):
        self.quality_var = IntVar(value=85)
        self.exif_var = BooleanVar(value=True)
        self.overwrite_var = BooleanVar(value=False)
        self.threads_var = IntVar(value=4)
        self.outfolder_var = StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "webp_converted"))
        self.ffmpeg_anim_var = BooleanVar(value=True)  # use ffmpeg for animated gifs if available

    def build_ui(self):
        frm = ttk.Frame(self.root, padding=12)
        frm.pack(fill="both", expand=True)

        # Top controls
        ctrl = ttk.Frame(frm)
        ctrl.pack(fill="x", pady=6)

        btn_add_files = ttk.Button(ctrl, text="Añadir archivos", command=self.add_files)
        btn_add_files.pack(side="left")
        btn_add_folder = ttk.Button(ctrl, text="Añadir carpeta (recursiva)", command=self.add_folder)
        btn_add_folder.pack(side="left", padx=6)
        btn_clear = ttk.Button(ctrl, text="Limpiar lista", command=self.clear_list)
        btn_clear.pack(side="left", padx=6)

        # Drag & drop hint
        if DND_AVAILABLE:
            lbl_dnd = ttk.Label(ctrl, text="(Arrastra archivos o carpetas aquí)")
            lbl_dnd.pack(side="left", padx=12)

        # Listbox / treeview for files
        self.tree = ttk.Treeview(frm, columns=("size", "path"), show="headings", height=12)
        self.tree.heading("size", text="Tamaño")
        self.tree.heading("path", text="Ruta")
        self.tree.column("size", width=100, anchor="center")
        self.tree.column("path", width=520)
        self.tree.pack(fill="both", expand=True, pady=8)

        # Options
        opts = ttk.Frame(frm)
        opts.pack(fill="x", pady=6)

        ttk.Label(opts, text="Carpeta de salida:").grid(row=0, column=0, sticky="w")
        ttk.Entry(opts, textvariable=self.outfolder_var, width=60).grid(row=0, column=1, sticky="w", padx=6)
        ttk.Button(opts, text="Seleccionar...", command=self.select_outfolder).grid(row=0, column=2, padx=6)

        ttk.Label(opts, text="Calidad (0-100):").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(opts, textvariable=self.quality_var, width=6).grid(row=1, column=1, sticky="w")

        ttk.Checkbutton(opts, text="Conservar EXIF", variable=self.exif_var).grid(row=1, column=2, sticky="w")
        ttk.Checkbutton(opts, text="Sobrescribir existentes", variable=self.overwrite_var).grid(row=1, column=3, sticky="w", padx=6)

        ttk.Label(opts, text="Threads:").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(opts, textvariable=self.threads_var, width=6).grid(row=2, column=1, sticky="w")

        ttk.Checkbutton(opts, text="Usar ffmpeg para GIF animados (recomendado)", variable=self.ffmpeg_anim_var).grid(row=2, column=2, columnspan=2, sticky="w")

        # Progress and actions
        actions = ttk.Frame(frm)
        actions.pack(fill="x", pady=8)

        self.progress = ttk.Progressbar(actions, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", side="left", expand=True, padx=6)

        self.lbl_status = ttk.Label(actions, text="Listo")
        self.lbl_status.pack(side="left", padx=6)

        btn_convert = ttk.Button(actions, text="Convertir", command=self.start_conversion)
        btn_convert.pack(side="right", padx=6)

        # Log
        ttk.Label(frm, text="Log:").pack(anchor="w")
        self.logbox = ttk.Treeview(frm, columns=("msg",), show="headings", height=6)
        self.logbox.heading("msg", text="Mensajes")
        self.logbox.column("msg", width=700)
        self.logbox.pack(fill="both", expand=False, pady=(6,0))

        # Drag & drop binder
        if DND_AVAILABLE:
            # If DND available, make the main window accept drops
            try:
                self.root.drop_target_register(DND_FILES)
                self.root.dnd_bind('<<Drop>>', self.drop_event)
            except Exception:
                pass

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Seleccionar imágenes", filetypes=[("Imágenes", "*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff;*.tif;*.webp")])
        if paths:
            self.add_paths(paths)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder:
            files = []
            for root, _, files_in in os.walk(folder):
                for f in files_in:
                    if f.lower().endswith(SUPPORTED):
                        files.append(os.path.join(root, f))
            self.add_paths(files)

    def add_paths(self, paths):
        added = 0
        for p in paths:
            p = p.strip().strip('"')
            if p and os.path.exists(p):
                # if it's a folder, add files inside
                if os.path.isdir(p):
                    for root, _, files_in in os.walk(p):
                        for f in files_in:
                            if f.lower().endswith(SUPPORTED):
                                full = os.path.join(root, f)
                                if full not in self.files:
                                    self.files.append(full); added += 1
                                    self.tree.insert("", "end", values=(self.human_size(full), full))
                else:
                    if p.lower().endswith(SUPPORTED) and p not in self.files:
                        self.files.append(p); added += 1
                        self.tree.insert("", "end", values=(self.human_size(p), p))
        self.lbl_status.config(text=f"{len(self.files)} archivos en la lista")

    def human_size(self, path):
        try:
            s = os.path.getsize(path)
            for unit in ['B','KB','MB','GB']:
                if s < 1024:
                    return f"{s:.0f}{unit}"
                s /= 1024
            return f"{s:.1f}TB"
        except Exception:
            return "N/A"

    def clear_list(self):
        self.files = []
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.lbl_status.config(text="Lista limpiada")

    def select_outfolder(self):
        out = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if out:
            self.outfolder_var.set(out)

    def drop_event(self, event):
        # event.data may be a string with space separated paths
        data = event.data
        paths = self.root.tk.splitlist(data)
        self.add_paths(paths)

    def start_conversion(self):
        if not self.files:
            messagebox.showwarning("Aviso", "No hay archivos en la lista.")
            return
        out = self.outfolder_var.get()
        if not out:
            messagebox.showwarning("Aviso", "Selecciona una carpeta de salida.")
            return
        os.makedirs(out, exist_ok=True)

        # disable UI while running
        self.root.config(cursor="wait")
        self.progress["value"] = 0
        total = len(self.files)
        self.progress["maximum"] = total
        self.logbox.delete(*self.logbox.get_children())

        # run in thread to avoid blocking UI
        t = threading.Thread(target=self._run_convert, args=(list(self.files), out))
        t.daemon = True
        t.start()

    def _run_convert(self, files, out):
        quality = self.quality_var.get()
        keep_exif = self.exif_var.get()
        overwrite = self.overwrite_var.get()
        threads = max(1, int(self.threads_var.get()))
        use_ffmpeg = self.ffmpeg_anim_var.get()

        results = []
        count = 0
        self._log(f"Inicio conversión: {len(files)} archivos • threads={threads} • calidad={quality}")
        with ThreadPoolExecutor(max_workers=threads) as ex:
            future_to_path = {ex.submit(convert_single, p, out, quality, keep_exif, overwrite, use_ffmpeg): p for p in files}
            for future in as_completed(future_to_path):
                res = None
                try:
                    res = future.result()
                except Exception as e:
                    res = f"error interno: {future_to_path[future]} -> {str(e)}"
                results.append(res)
                count += 1
                # update UI
                self.root.after(0, self._update_progress, count, res)

        # finished
        ok = sum(1 for r in results if r.startswith("ok:"))
        skipped = sum(1 for r in results if r.startswith("skip:"))
        errors = [r for r in results if r.startswith("error") or "error" in r and not r.startswith("ok")]
        self.root.after(0, self._done, ok, skipped, len(errors), results)

    def _update_progress(self, done, message):
        self.progress["value"] = done
        self.lbl_status.config(text=f"{done}/{int(self.progress['maximum'])}")
        self._log(message)

    def _log(self, message):
        self.logbox.insert("", "end", values=(message,))

    def _done(self, ok, skipped, errors_count, results):
        self.root.config(cursor="")
        self._log(f"Finalizado. OK: {ok} • Skipped: {skipped} • Errors: {errors_count}")
        messagebox.showinfo("Convertidor", f"Conversión completada.\nOK: {ok}\nOmitidos: {skipped}\nErrores: {errors_count}")

def main():
    # If TkinterDnD available, use it for drag & drop root
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
