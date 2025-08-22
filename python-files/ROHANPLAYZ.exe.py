import os
import sys
import subprocess
import threading
import shutil
from pathlib import Path

try:
    # Optional dependency for drag & drop on Windows
    from tkinterdnd2 import DND_FILES, TkinterDnD
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    DND_AVAILABLE = True
except Exception:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    DND_AVAILABLE = False

APP_TITLE = "TikTok Converter - By Rohan Playz"
BG_GREY = "#3a3a3a"
BTN_DARK = "#2b2b2b"
TXT_WHITE = "#ffffff"
ACCENT = "#5e5e5e"

DEFAULT_FPS = 60

FFMPEG_EXE = "ffmpeg"


def which_ffmpeg():
    # Try to find ffmpeg in PATH or in the same folder as the exe/script
    local = Path(getattr(sys, '_MEIPASS', Path.cwd()))
    candidates = [
        shutil.which(FFMPEG_EXE),
        str((Path(sys.executable).parent / 'ffmpeg.exe')) if sys.platform.startswith('win') else None,
        str((local / 'ffmpeg.exe')) if sys.platform.startswith('win') else None,
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c
    return None


def run_ffmpeg(cmd, on_log):
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, universal_newlines=True)
        for line in proc.stdout:
            on_log(line.rstrip())
        proc.wait()
        return proc.returncode
    except Exception as e:
        on_log(f"Error: {e}")
        return 1


class App:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.geometry("720x520")
        root.configure(bg=BG_GREY)
        root.minsize(680, 480)

        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=BG_GREY)
        style.configure('TLabel', background=BG_GREY, foreground=TXT_WHITE)
        style.configure('TButton', background=BTN_DARK, foreground=TXT_WHITE)
        style.map('TButton', background=[('active', ACCENT)])
        
        # Top header
        header = ttk.Frame(root)
        header.pack(fill='x', pady=(12, 6), padx=12)
        ttk.Label(header, text='TikTok Friendly Converter', font=('Segoe UI', 18, 'bold')).pack(side='left')
        ttk.Label(header, text='By Rohan Playz', font=('Segoe UI', 11)).pack(side='right')

        # Mode row
        controls = ttk.Frame(root)
        controls.pack(fill='x', padx=12, pady=6)

        ttk.Label(controls, text='Mode:').grid(row=0, column=0, sticky='w')
        self.mode = tk.StringVar(value='interpolate')
        mode_combo = ttk.Combobox(controls, textvariable=self.mode, state='readonly', values=[
            'interpolate',  # Real 60 FPS via minterpolate
            'magic_itsscale',  # Timebase trick: itsscale 2 (slow on PC, smooth on TikTok)
        ])
        mode_combo.grid(row=0, column=1, sticky='w', padx=8)

        ttk.Label(controls, text='Target FPS:').grid(row=0, column=2, sticky='w', padx=(16, 0))
        self.target_fps = tk.IntVar(value=DEFAULT_FPS)
        fps_entry = ttk.Entry(controls, textvariable=self.target_fps, width=6)
        fps_entry.grid(row=0, column=3, sticky='w', padx=8)

        self.chk_vertical = tk.BooleanVar(value=False)
        chk = ttk.Checkbutton(controls, text='Make vertical 1080x1920 (TikTok)', variable=self.chk_vertical)
        chk.grid(row=0, column=4, sticky='w', padx=(16,0))

        # Drop zone / button
        drop_frame = ttk.Frame(root)
        drop_frame.pack(fill='x', padx=12, pady=10)

        self.drop_btn = tk.Label(drop_frame, text='DRAG FILE TO CONVERT TO 60 FPS',
                                 fg=TXT_WHITE, bg=BTN_DARK, font=('Segoe UI', 16, 'bold'),
                                 bd=0, padx=18, pady=22, cursor='hand2')
        self.drop_btn.pack(fill='x')
        self.drop_btn.bind('<Button-1>', self.pick_file)

        if DND_AVAILABLE and isinstance(root, TkinterDnD.Tk):
            self.drop_btn.drop_target_register(DND_FILES)
            self.drop_btn.dnd_bind('<<Drop>>', self.on_drop)

        # Output label
        out_row = ttk.Frame(root)
        out_row.pack(fill='x', padx=12, pady=(6, 4))
        ttk.Label(out_row, text='Output folder:').pack(side='left')
        self.output_dir = tk.StringVar(value=str(Path.home() / 'Videos'))
        self.out_entry = ttk.Entry(out_row, textvariable=self.output_dir)
        self.out_entry.pack(side='left', fill='x', expand=True, padx=8)
        ttk.Button(out_row, text='Browse', command=self.pick_output_dir).pack(side='left')

        # Log box
        log_frame = ttk.Frame(root)
        log_frame.pack(fill='both', expand=True, padx=12, pady=(6, 12))
        self.log = tk.Text(log_frame, height=12, bg='#2f2f2f', fg=TXT_WHITE, insertbackground=TXT_WHITE, relief='flat')
        self.log.pack(fill='both', expand=True)

        # Footer
        self.status = ttk.Label(root, text='Ready', anchor='w')
        self.status.pack(fill='x', side='bottom', padx=12, pady=(0, 8))

        # Ensure ffmpeg exists
        self.ffmpeg_path = which_ffmpeg()
        if not self.ffmpeg_path:
            self.log_write("FFmpeg not found. Please install FFmpeg and add to PATH, or place ffmpeg.exe next to this app.")

    def pick_output_dir(self):
        p = filedialog.askdirectory()
        if p:
            self.output_dir.set(p)

    def pick_file(self, *_):
        f = filedialog.askopenfilename(title='Select a video', filetypes=[('Video files', '*.mp4;*.mov;*.mkv;*.avi;*.m4v'), ('All files', '*.*')])
        if f:
            self.convert(Path(f))

    def on_drop(self, event):
        # Accept the first path from drag list
        paths = event.data
        if paths:
            first = paths
            # On Windows, multiple files are enclosed in braces; take first token
            if first.startswith('{') and first.endswith('}'):
                parts = first[1:-1].split('} {')
                first = parts[0]
            self.convert(Path(first))

    def log_write(self, text):
        self.log.insert('end', text + "\n")
        self.log.see('end')

    def convert(self, in_path: Path):
        if not self.ffmpeg_path:
            messagebox.showerror('FFmpeg missing', 'FFmpeg not found. Install it and try again.')
            return
        if not in_path.exists():
            messagebox.showerror('File missing', f'Input file not found: {in_path}')
            return

        out_dir = Path(self.output_dir.get()).expanduser()
        out_dir.mkdir(parents=True, exist_ok=True)

        stem = in_path.stem
        ext = in_path.suffix.lower() or '.mp4'

        mode = self.mode.get()
        fps = max(1, int(self.target_fps.get() or DEFAULT_FPS))

        if mode == 'magic_itsscale':
            out_file = out_dir / f"{stem}_magic{ext}"
            cmd = [self.ffmpeg_path, '-y', '-itsscale', '2', '-i', str(in_path), '-c:v', 'copy', '-c:a', 'copy', str(out_file)]
            self.log_write('Mode: Magic (itsscale 2x slow on PC, smooth on TikTok)')
        else:
            # Interpolate to target FPS; optional vertical formatting
            out_file = out_dir / f"{stem}_{fps}fps{ext}"
            vf_chain = [f"minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"]
            if self.chk_vertical.get():
                vf_chain.append('scale=1080:1920:force_original_aspect_ratio=decrease')
                vf_chain.append('pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black')
            vf = ','.join(vf_chain)
            cmd = [self.ffmpeg_path, '-y', '-i', str(in_path), '-vf', vf, '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(fps), str(out_file)]
            self.log_write(f'Mode: Interpolate to {fps} FPS')

        if self.chk_vertical.get():
            self.log_write('TikTok vertical: 1080x1920 enabled')

        self.status.config(text='Converting...')
        self.log_write('Running FFmpeg...')

        def work():
            code = run_ffmpeg(cmd, self.log_write)
            if code == 0:
                self.status.config(text=f'Done: {out_file}')
                self.log_write(f'✅ Finished: {out_file}')
                try:
                    # Reveal in folder (Windows)
                    if sys.platform.startswith('win'):
                        subprocess.Popen(['explorer', '/select,', str(out_file)])
                except Exception:
                    pass
            else:
                self.status.config(text='Failed')
                self.log_write('❌ Conversion failed.')

        threading.Thread(target=work, daemon=True).start()


def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
