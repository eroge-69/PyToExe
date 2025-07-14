import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
import json
import colorsys
import time
import threading

# --- Utils ---
def rgb_to_hex(rgb):
    """Converte uma tupla RGB (0-255, 0-255, 0-255) para uma string HEX."""
    return "#{:02X}{:02X}{:02X}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def hex_to_rgb(hexstr):
    """Converte uma string HEX (e.g., '#RRGGBB') para uma tupla RGB."""
    hexstr = hexstr.lstrip("#")
    return tuple(int(hexstr[i:i+2], 16) for i in (0, 2, 4))

def interpolate_colors(c1, c2, steps):
    """Interpola linearmente entre duas cores HEX para criar um gradiente."""
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    gradient = []
    for i in range(steps):
        # Evita divisão por zero se steps é 1
        factor = i / (steps - 1) if steps > 1 else 0
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        gradient.append(rgb_to_hex((r, g, b)))
    return gradient

# --- Tela de Loading com barra animada ---
class LoadingScreen(tk.Toplevel):
    def __init__(self, parent, duration=2.5):
        super().__init__(parent)
        self.duration = duration
        self.overrideredirect(True) # Remove bordas e barra de título
        self.geometry("400x130+{}+{}".format(
            int(parent.winfo_screenwidth()/2 - 200),
            int(parent.winfo_screenheight()/2 - 65)
        ))
        self.configure(bg="#222222")
        self.grab_set() # Torna a tela de loading modal

        self.label = tk.Label(self, text="Carregando ColorMaster AI...",
                              fg="#eee", bg="#222222", font=("Segoe UI", 18, "bold"))
        self.label.pack(pady=(25, 15))

        self.progress_frame = tk.Frame(self, bg="#444444")
        self.progress_frame.pack(fill="x", padx=30, pady=10, ipady=8)

        self.progress = tk.Frame(self.progress_frame, bg="#0078d7", width=0)
        self.progress.pack(side="left", fill="y")

        self.after(100, self.animate)

    def animate(self):
        steps = 120
        delay = self.duration / steps
        for i in range(steps + 1):
            if not self.winfo_exists():
                break
            self.progress.config(width=int(3 * i))
            self.update_idletasks()
            time.sleep(delay)
        if self.winfo_exists():
            self.destroy()

# --- Diálogo de Novo/Abrir Projeto ---
class StartupDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.overrideredirect(True)
        self.geometry("350x200+{}+{}".format(
            int(parent.winfo_screenwidth()/2 - 175),
            int(parent.winfo_screenheight()/2 - 100)
        ))
        self.configure(bg="#222222", bd=2, relief="ridge")
        self.grab_set() # Torna o diálogo modal

        tk.Label(self, text="Bem-vindo ao ColorMaster!",
                 font=("Segoe UI", 16, "bold"), fg="#eee", bg="#222222").pack(pady=20)

        btn_new = tk.Button(self, text="Novo Projeto",
                            font=("Segoe UI", 12), bg="#0078d7", fg="white",
                            command=self.new_project_action, relief="flat", cursor="hand2")
        btn_new.pack(pady=10, padx=50, fill="x")

        btn_open = tk.Button(self, text="Abrir Projeto Existente",
                             font=("Segoe UI", 12), bg="#009933", fg="white",
                             command=self.open_project_action, relief="flat", cursor="hand2")
        btn_open.pack(pady=5, padx=50, fill="x")

        self.choice = None # 'new' or 'open'

    def new_project_action(self):
        self.choice = 'new'
        self.destroy()

    def open_project_action(self):
        self.choice = 'open'
        self.destroy()


# --- Aplicativo principal ---
class ColorMasterApp(tk.Tk):
    PREDEFINED_COLORS = {
        "Azul Escuro": "#003366",
        "Azul": "#0078d7",
        "Verde": "#008000",
        "Vermelho": "#cc3300",
        "Laranja": "#ff6600",
        "Roxo": "#663399",
        "Cinza Escuro": "#444444",
        "Cinza Claro": "#bbbbbb",
        "Preto": "#000000",
        "Branco": "#ffffff"
    }

    def __init__(self):
        super().__init__()
        self.title("ColorMaster - Gerenciador de Paletas")
        self.geometry("1100x700")
        self.minsize(1000, 600)
        self.configure(bg="#1e1e1e")

        self.colors = {
            "bg": "#1e1e1e",
            "fg": "#eeeeee",
            "accent": "#0078d7",
            "button_bg": "#2a2a2a",
            "button_fg": "#eeeeee",
            "frame_bg": "#252525",
            "entry_bg": "#333333",
            "entry_fg": "#eeeeee",
            "border": "#3a3a3a"
        }

        self.palette_size = 7
        self.current_palette = ["#FFFFFF" for _ in range(self.palette_size)]
        self.history = []
        self.history_index = -1

        self.selected_index = 0

        self._status_timer = None

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_loading_screen()

    def create_loading_screen(self):
        self.withdraw()
        self.loading = LoadingScreen(self)
        self.after(int(self.loading.duration * 1000 + 50), self.show_startup_dialog)

    def show_startup_dialog(self):
        self.loading.destroy()
        self.startup_dialog = StartupDialog(self)
        # Espera o diálogo ser fechado para continuar
        self.wait_window(self.startup_dialog)
        self.deiconify() # Mostra a janela principal

        if self.startup_dialog.choice == 'new':
            self.setup_ui()
            self.new_palette(confirm=False) # Cria uma nova paleta sem perguntar novamente
        elif self.startup_dialog.choice == 'open':
            self.setup_ui()
            self.load_palette() # Tenta carregar uma paleta
        else: # Se o diálogo foi fechado sem escolha
            self.destroy() # Sai do aplicativo

    def setup_ui(self):
        self.create_menu()
        self.create_sidebar()
        self.create_palette_area()
        self.create_history_area()
        self.create_statusbar()

        # Inicializa a paleta e o estado da UI
        # Não gera paleta aleatória aqui, pois o diálogo de início já lida com isso
        self.update_palette_display()
        self.update_selected_color(0)
        self.update_history_box()
        self.update_undo_redo_buttons()
        self.status("ColorMaster pronto para uso!")

    # --- MENU BAR ---
    def create_menu(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0, bg=self.colors["frame_bg"], fg=self.colors["fg"])
        filemenu.add_command(label="Novo", command=lambda: self.new_palette(confirm=True)) # Adiciona confirmação
        filemenu.add_command(label="Carregar...", command=self.load_palette)
        filemenu.add_command(label="Salvar...", command=self.save_palette)
        filemenu.add_separator()
        filemenu.add_command(label="Sair", command=self.on_close)
        menubar.add_cascade(label="Arquivo", menu=filemenu)

        editmenu = tk.Menu(menubar, tearoff=0, bg=self.colors["frame_bg"], fg=self.colors["fg"])
        editmenu.add_command(label="Gerar Gradiente", command=self.generate_gradient)
        editmenu.add_command(label="Gerar Paleta Aleatória", command=self.generate_random_palette)
        menubar.add_cascade(label="Editar", menu=editmenu)

        self.config(menu=menubar)

    # --- SIDEBAR (Controles e Edição de Cores) ---
    def create_sidebar(self):
        self.sidebar = tk.Frame(self, bg=self.colors["frame_bg"], width=320, bd=0, relief="solid")
        self.sidebar.pack(side="left", fill="y", padx=(0,0), pady=(0,0))
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="Controles da Paleta", font=("Segoe UI", 14, "bold"),
                 fg=self.colors["fg"], bg=self.colors["frame_bg"]).pack(pady=(15, 10), padx=10, anchor="w")

        lbl_size = tk.Label(self.sidebar, text="Nº de cores na paleta:", font=("Segoe UI", 11),
                            fg=self.colors["fg"], bg=self.colors["frame_bg"])
        lbl_size.pack(pady=(5,2), padx=10, anchor="w")

        self.scale_size = tk.Scale(self.sidebar, from_=2, to=12, orient="horizontal", bg=self.colors["frame_bg"],
                                   fg=self.colors["fg"], troughcolor=self.colors["button_bg"], highlightthickness=0,
                                   length=280, command=self.on_palette_size_change, showvalue=True,
                                   relief="flat", bd=0)
        self.scale_size.set(self.palette_size)
        self.scale_size.pack(padx=10, pady=(0,20))

        lbl_static = tk.Label(self.sidebar, text="Gerar de Paleta Base:", font=("Segoe UI", 11),
                              fg=self.colors["fg"], bg=self.colors["frame_bg"])
        lbl_static.pack(pady=(0, 2), padx=10, anchor="w")

        options = ["Nenhuma"] + list(self.PREDEFINED_COLORS.keys())
        self.static_color_var = tk.StringVar(value="Nenhuma")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground=self.colors["entry_bg"], background=self.colors["button_bg"],
                        foreground=self.colors["entry_fg"], selectbackground=self.colors["accent"],
                        selectforeground="white", bordercolor=self.colors["border"], arrowcolor=self.colors["fg"])
        style.map("TCombobox", background=[('readonly', self.colors["button_bg"])])

        static_select_frame = tk.Frame(self.sidebar, bg=self.colors["frame_bg"])
        static_select_frame.pack(padx=10, pady=(0, 20), fill="x")

        self.dropdown_static = ttk.Combobox(static_select_frame, values=options, state="readonly",
                                            textvariable=self.static_color_var, font=("Segoe UI", 10))
        self.dropdown_static.pack(side="left", fill="x", expand=True)
        # self.dropdown_static.bind("<<ComboboxSelected>>", self.on_static_color_select) # Agora com botão

        btn_apply_base = tk.Button(static_select_frame, text="Aplicar Base", command=self.on_static_color_select,
                                  bg=self.colors["button_bg"], fg=self.colors["button_fg"], cursor="hand2", relief="flat")
        btn_apply_base.pack(side="right", padx=(5,0))

        self.edit_label = tk.Label(self.sidebar, text="Editar Cor Selecionada:", font=("Segoe UI", 13, "bold"),
                                   fg=self.colors["accent"], bg=self.colors["frame_bg"])
        self.edit_label.pack(pady=(10, 10), padx=10, anchor="w")

        self.color_preview = tk.Canvas(self.sidebar, width=100, height=100, bg="#000", bd=2, relief="sunken",
                                        highlightbackground=self.colors["border"], highlightthickness=1)
        self.color_preview.pack(padx=10, pady=(0, 10))
        self.color_preview.bind("<Button-1>", lambda e: self.open_color_picker())

        # Entrada HEX
        frame_hex = tk.Frame(self.sidebar, bg=self.colors["frame_bg"])
        frame_hex.pack(padx=10, pady=(0,5), fill="x", anchor="w")
        tk.Label(frame_hex, text="HEX:", fg=self.colors["fg"], bg=self.colors["frame_bg"], font=("Segoe UI", 9)).pack(side="left", padx=(0,5))
        self.entry_hex = tk.Entry(frame_hex, bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
                                  insertbackground=self.colors["fg"], bd=1, relief="solid",
                                  highlightbackground=self.colors["border"], highlightthickness=1)
        self.entry_hex.pack(side="left", fill="x", expand=True)
        self.entry_hex.bind("<Return>", lambda e: self.update_color_from_hex())
        btn_copy_hex = tk.Button(frame_hex, text="Copiar", command=self.copy_hex_to_clipboard,
                                 bg=self.colors["button_bg"], fg=self.colors["button_fg"], cursor="hand2", relief="flat")
        btn_copy_hex.pack(side="right", padx=(5,0))

        # Entradas RGB
        frame_rgb = tk.Frame(self.sidebar, bg=self.colors["frame_bg"])
        frame_rgb.pack(padx=10, pady=(5,10), fill="x")
        self.entry_r = self.create_labeled_entry(frame_rgb, "R")
        self.entry_g = self.create_labeled_entry(frame_rgb, "G")
        self.entry_b = self.create_labeled_entry(frame_rgb, "B")
        for e in (self.entry_r, self.entry_g, self.entry_b):
            e.bind("<Return>", lambda e: self.update_color_from_rgb())

        # Entradas HSL
        frame_hsl = tk.Frame(self.sidebar, bg=self.colors["frame_bg"])
        frame_hsl.pack(padx=10, pady=(0,10), fill="x")
        self.entry_h = self.create_labeled_entry(frame_hsl, "H")
        self.entry_s = self.create_labeled_entry(frame_hsl, "S (%)")
        self.entry_l = self.create_labeled_entry(frame_hsl, "L (%)")
        for e in (self.entry_h, self.entry_s, self.entry_l):
            e.bind("<Return>", lambda e: self.update_color_from_hsl())

        lbl_hsv = tk.Label(self.sidebar, text="HSV (arraste para alterar):", font=("Segoe UI", 11),
                           fg=self.colors["fg"], bg=self.colors["frame_bg"])
        lbl_hsv.pack(pady=(15, 5), padx=10, anchor="w")

        self.scale_h = self._create_hsv_slider(0, 360, self.on_hsv_sliders_changed)
        self.scale_h.pack(padx=10, fill="x")
        self.scale_s = self._create_hsv_slider(0, 100, self.on_hsv_sliders_changed)
        self.scale_s.pack(padx=10, fill="x")
        self.scale_v = self._create_hsv_slider(0, 100, self.on_hsv_sliders_changed)
        self.scale_v.pack(padx=10, fill="x")

        self.btn_apply = tk.Button(self.sidebar, text="Aplicar Cor", bg=self.colors["accent"], fg="#fff",
                                   font=("Segoe UI", 12, "bold"), command=self.apply_color_to_selected,
                                   cursor="hand2", relief="flat")
        self.btn_apply.pack(pady=20, padx=10, fill="x")

        self.btn_add = tk.Button(self.sidebar, text="Adicionar Nova Cor", bg="#0078d7", fg="#fff",
                                 font=("Segoe UI", 10, "bold"), command=self.add_new_color,
                                 cursor="hand2", relief="flat")
        self.btn_add.pack(pady=(0, 10), padx=10, fill="x")

        self.btn_delete = tk.Button(self.sidebar, text="Remover Cor Selecionada", bg="#aa0000", fg="#fff",
                                    font=("Segoe UI", 10, "bold"), command=self.remove_selected_color,
                                    cursor="hand2", relief="flat")
        self.btn_delete.pack(pady=(0, 20), padx=10, fill="x")

        self.btn_generate_gradient = tk.Button(self.sidebar, text="Gerar Gradiente (2 Pontos)", bg="#009933", fg="#fff",
                                               font=("Segoe UI", 10, "bold"), command=self.generate_gradient,
                                               cursor="hand2", relief="flat")
        self.btn_generate_gradient.pack(pady=(0, 20), padx=10, fill="x")

    def create_labeled_entry(self, parent, label):
        frame = tk.Frame(parent, bg=self.colors["frame_bg"])
        frame.pack(side="left", padx=5, fill="x", expand=True) # Usar expand=True para preencher espaço
        lbl = tk.Label(frame, text=label, fg=self.colors["fg"], bg=self.colors["frame_bg"], font=("Segoe UI", 9))
        lbl.pack(anchor="w")
        ent = tk.Entry(frame, width=5, bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
                       insertbackground=self.colors["fg"], bd=1, relief="solid",
                       highlightbackground=self.colors["border"], highlightthickness=1)
        ent.pack(fill="x", expand=True)
        return ent

    def _create_hsv_slider(self, _from, to, command):
        return tk.Scale(self.sidebar, from_=_from, to=to, orient="horizontal", bg=self.colors["frame_bg"],
                        fg=self.colors["fg"], troughcolor=self.colors["button_bg"], highlightthickness=0,
                        length=280, command=command, showvalue=True, bd=0, relief="flat")

    # --- ÁREA DA PALETA (Display principal) ---
    def create_palette_area(self):
        self.palette_area = tk.Frame(self, bg=self.colors["bg"])
        self.palette_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.palette_label = tk.Label(self.palette_area, text="Paleta Atual", fg=self.colors["fg"],
                                      bg=self.colors["bg"], font=("Segoe UI", 22, "bold"))
        self.palette_label.pack(anchor="nw", pady=(0,15))

        self.palette_frame = tk.Frame(self.palette_area, bg=self.colors["bg"])
        self.palette_frame.pack(fill="x")

    # --- BARRA DE STATUS ---
    def create_statusbar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Bem-vindo ao ColorMaster Photoshop!")

        statusbar = tk.Label(self, textvariable=self.status_var, bd=1, relief="sunken",
                             anchor="w", bg=self.colors["frame_bg"], fg=self.colors["fg"],
                             font=("Segoe UI", 10), padx=5)
        statusbar.pack(side="bottom", fill="x")

    def status(self, msg, duration=3000):
        self.status_var.set(msg)
        if self._status_timer:
            self.after_cancel(self._status_timer)
        self._status_timer = self.after(duration, self._clear_status)

    def _clear_status(self):
        self.status_var.set("Pronto.")
        self._status_timer = None

    # --- HISTÓRICO DE PALETAS ---
    def create_history_area(self):
        history_frame = tk.Frame(self.palette_area, bg=self.colors["bg"])
        history_frame.pack(fill="both", expand=True, pady=(20,0))

        lbl_hist = tk.Label(history_frame, text="Histórico de Paletas (até 15)", fg=self.colors["fg"],
                            bg=self.colors["bg"], font=("Segoe UI", 12, "bold"))
        lbl_hist.pack(anchor="nw", pady=(0,10))

        listbox_frame = tk.Frame(history_frame, bg=self.colors["entry_bg"], relief="solid", bd=1,
                                 highlightbackground=self.colors["border"], highlightthickness=1)
        listbox_frame.pack(fill="both", expand=True)

        self.history_listbox = tk.Listbox(listbox_frame, height=8, bg=self.colors["entry_bg"],
                                          fg=self.colors["entry_fg"], font=("Consolas", 10),
                                          selectbackground=self.colors["accent"], activestyle="none",
                                          bd=0, highlightthickness=0)
        self.history_listbox.pack(side="left", fill="both", expand=True)
        self.history_listbox.bind("<<ListboxSelect>>", self.on_history_select)

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.history_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(history_frame, bg=self.colors["bg"])
        btn_frame.pack(pady=10, anchor="e")

        self.btn_undo = tk.Button(btn_frame, text="Desfazer", command=self.undo, state="disabled",
                                  bg=self.colors["button_bg"], fg=self.colors["fg"], cursor="hand2", relief="flat")
        self.btn_undo.pack(side="left", padx=5)
        self.btn_redo = tk.Button(btn_frame, text="Refazer", command=self.redo, state="disabled",
                                  bg=self.colors["button_bg"], fg=self.colors["fg"], cursor="hand2", relief="flat")
        self.btn_redo.pack(side="left", padx=5)

    # --- FUNÇÕES PRINCIPAIS DE GESTÃO DE PALETA ---
    def generate_random_palette(self):
        import random
        self.current_palette = [rgb_to_hex((random.randint(0,255), random.randint(0,255), random.randint(0,255)))
                                for _ in range(self.palette_size)]
        self.push_history()
        self.update_palette_display()
        self.update_selected_color(0)
        self.status("Paleta aleatória gerada.")

    def update_palette_display(self):
        for w in self.palette_frame.winfo_children():
            w.destroy()

        w_size = 70
        pad_x = 8
        for i, c in enumerate(self.current_palette):
            frame = tk.Frame(self.palette_frame, bg=c, width=w_size, height=w_size, cursor="hand2",
                             relief="raised", bd=2, highlightbackground=self.colors["border"], highlightthickness=1)
            frame.pack(side="left", padx=pad_x, pady=5)
            frame.pack_propagate(False)

            lbl_hex = tk.Label(frame, text=c.upper(), bg=c, fg=self.get_contrast_color(c),
                               font=("Segoe UI", 8, "bold"))
            lbl_hex.pack(side="bottom", fill="x", pady=2)
            lbl_hex.bind("<Button-1>", lambda e, idx=i: self.update_selected_color(idx))

            frame.bind("<Button-1>", lambda e, idx=i: self.update_selected_color(idx))

            if i == self.selected_index:
                frame.config(relief="sunken", bd=4, highlightbackground=self.colors["accent"], highlightthickness=2)
                lbl_hex.config(font=("Segoe UI", 9, "bold"))

    def update_selected_color(self, index):
        if not self.current_palette:
            self.selected_index = -1
            self.status("Nenhuma cor para selecionar.")
            return

        if index < 0:
            self.selected_index = 0
        elif index >= len(self.current_palette):
            self.selected_index = len(self.current_palette) - 1
        else:
            self.selected_index = index

        if self.selected_index == -1: return

        color = self.current_palette[self.selected_index]
        self.update_color_fields(color)
        self.update_palette_display()
        self.status(f"Cor #{self.selected_index+1} selecionada: {color.upper()}")

    def update_color_fields(self, hexcolor):
        self.entry_hex.delete(0, tk.END)
        self.entry_hex.insert(0, hexcolor.upper())

        r, g, b = hex_to_rgb(hexcolor)
        self.entry_r.delete(0, tk.END)
        self.entry_r.insert(0, str(r))
        self.entry_g.delete(0, tk.END)
        self.entry_g.insert(0, str(g))
        self.entry_b.delete(0, tk.END)
        self.entry_b.insert(0, str(b))

        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        self.entry_h.delete(0, tk.END)
        self.entry_h.insert(0, f"{int(h*360):.0f}")
        self.entry_s.delete(0, tk.END)
        self.entry_s.insert(0, f"{int(s*100):.0f}")
        self.entry_l.delete(0, tk.END)
        self.entry_l.insert(0, f"{int(l*100):.0f}")

        self.scale_h.config(command=None)
        self.scale_s.config(command=None)
        self.scale_v.config(command=None)

        h2, s2, v2 = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        self.scale_h.set(int(h2*360))
        self.scale_s.set(int(s2*100))
        self.scale_v.set(int(v2*100))

        self.scale_h.config(command=lambda e: self.on_hsv_sliders_changed())
        self.scale_s.config(command=lambda e: self.on_hsv_sliders_changed())
        self.scale_v.config(command=lambda e: self.on_hsv_sliders_changed())

        self.color_preview.configure(bg=hexcolor)

    def open_color_picker(self):
        if not self.current_palette or self.selected_index == -1:
            self.status("Selecione uma cor antes de usar o seletor.")
            messagebox.showinfo("Aviso", "Não há cores na paleta para editar ou nenhuma está selecionada.")
            return

        current_color = self.current_palette[self.selected_index]
        chosen = colorchooser.askcolor(color=current_color, title="Escolha uma cor")
        if chosen and chosen[1]:
            self.current_palette[self.selected_index] = chosen[1].upper()
            self.push_history()
            self.update_selected_color(self.selected_index)
            self.status(f"Cor #{self.selected_index+1} alterada para {chosen[1].upper()}")
        else:
            self.status("Seleção de cor cancelada.")

    def update_color_from_hex(self):
        hexcolor = self.entry_hex.get().strip().upper()
        if not hexcolor.startswith("#"):
            hexcolor = "#" + hexcolor

        import re
        if not re.match(r"^#[0-9A-F]{6}$", hexcolor):
            self.status("HEX inválido. Use #RRGGBB.", duration=5000)
            messagebox.showerror("Erro de HEX", "Formato HEX inválido. Use #RRGGBB (ex: #AABBCC).")
            self.update_color_fields(self.current_palette[self.selected_index])
            return

        try:
            hex_to_rgb(hexcolor)
            if hexcolor != self.current_palette[self.selected_index]:
                self.current_palette[self.selected_index] = hexcolor
                self.push_history()
                self.update_selected_color(self.selected_index)
                self.status(f"Cor atualizada para {hexcolor}.")
            else:
                self.status("Cor HEX não alterada.")
        except Exception as e:
            self.status(f"Erro ao aplicar HEX: {e}", duration=5000)
            messagebox.showerror("Erro de HEX", f"Não foi possível converter o HEX '{hexcolor}'. Verifique.")
            self.update_color_fields(self.current_palette[self.selected_index])

    def update_color_from_rgb(self):
        try:
            r = int(self.entry_r.get())
            g = int(self.entry_g.get())
            b = int(self.entry_b.get())
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                raise ValueError("Valores RGB devem estar entre 0 e 255.")
        except ValueError as e:
            self.status(f"Erro de RGB: {e}", duration=5000)
            messagebox.showerror("Erro de RGB", f"RGB inválido: {e}. Use valores inteiros entre 0 e 255.")
            self.update_color_fields(self.current_palette[self.selected_index])
            return

        hexcolor = rgb_to_hex((r,g,b))
        if hexcolor != self.current_palette[self.selected_index]:
            self.current_palette[self.selected_index] = hexcolor
            self.push_history()
            self.update_selected_color(self.selected_index)
            self.status(f"Cor atualizada para RGB({r},{g},{b}).")
        else:
            self.status("Cor RGB não alterada.")


    def update_color_from_hsl(self):
        try:
            h = float(self.entry_h.get())
            s = float(self.entry_s.get())
            l = float(self.entry_l.get())

            if not (0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100):
                raise ValueError("H (0-360), S (0-100%), L (0-100%).")

            r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
            r, g, b = int(r*255), int(g*255), int(b*255)

        except ValueError as e:
            self.status(f"Erro de HSL: {e}", duration=5000)
            messagebox.showerror("Erro de HSL", f"HSL inválido: {e}. Verifique os intervalos.")
            self.update_color_fields(self.current_palette[self.selected_index])
            return

        hexcolor = rgb_to_hex((r,g,b))
        if hexcolor != self.current_palette[self.selected_index]:
            self.current_palette[self.selected_index] = hexcolor
            self.push_history()
            self.update_selected_color(self.selected_index)
            self.status(f"Cor atualizada para HSL({int(h)},{int(s)}%,{int(l)}%).")
        else:
            self.status("Cor HSL não alterada.")

    def on_hsv_sliders_changed(self):
        try:
            h = self.scale_h.get() / 360
            s = self.scale_s.get() / 100
            v = self.scale_v.get() / 100

            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            r, g, b = int(r*255), int(g*255), int(b*255)
            hexcolor = rgb_to_hex((r,g,b))
        except Exception:
            return
        
        if hexcolor != self.current_palette[self.selected_index]:
            self.current_palette[self.selected_index] = hexcolor
            self.push_history()
            self.update_selected_color(self.selected_index)
            self.status("Cor atualizada via HSV sliders.")

    def apply_color_to_selected(self):
        self.update_color_from_hex() # Força a atualização do campo HEX para pegar o valor final
        self.status(f"Cor #{self.selected_index+1} aplicada com sucesso.")

    def add_new_color(self):
        if len(self.current_palette) >= 12:
            messagebox.showinfo("Limite de Cores", "O número máximo de cores por paleta é 12.")
            self.status("Não foi possível adicionar nova cor: limite atingido.", duration=3000)
            return
        self.current_palette.append("#FFFFFF")
        self.palette_size = len(self.current_palette)
        self.scale_size.set(self.palette_size)
        self.push_history()
        self.update_palette_display()
        self.update_selected_color(len(self.current_palette)-1)
        self.status("Nova cor (branco) adicionada à paleta.")

    def remove_selected_color(self):
        if len(self.current_palette) <= 2:
            messagebox.showinfo("Limite de Cores", "Uma paleta deve ter ao menos 2 cores.")
            self.status("Não foi possível remover cor: mínimo de 2 cores.", duration=3000)
            return
        if self.selected_index != -1 and self.selected_index < len(self.current_palette):
            removed_color = self.current_palette[self.selected_index]
            del self.current_palette[self.selected_index]
            self.palette_size = len(self.current_palette)
            self.scale_size.set(self.palette_size)
            self.push_history()
            self.selected_index = min(self.selected_index, len(self.current_palette) - 1)
            if not self.current_palette: self.selected_index = -1
            self.update_palette_display()
            self.update_selected_color(self.selected_index if self.current_palette else -1)
            self.status(f"Cor {removed_color.upper()} removida da paleta.")
        else:
            self.status("Nenhuma cor selecionada para remover.", duration=3000)

    def on_palette_size_change(self, val):
        new_size = int(val)
        if new_size == self.palette_size:
            return

        if new_size > self.palette_size:
            for _ in range(new_size - self.palette_size):
                self.current_palette.append("#FFFFFF")
        else:
            self.current_palette = self.current_palette[:new_size]

        self.palette_size = new_size
        self.push_history()
        self.update_palette_display()
        if self.selected_index >= new_size:
            self.update_selected_color(new_size - 1)
        else:
             self.update_selected_color(self.selected_index)
        self.status(f"Tamanho da paleta alterado para {new_size} cores.")

    def on_static_color_select(self):
        sel = self.static_color_var.get()
        if sel == "Nenhuma":
            self.status("Nenhuma paleta base selecionada. Gerando paleta padrão (brancos).", duration=3000)
            self.new_palette(confirm=False) # Volta para paleta padrão se "Nenhuma" for selecionada
            return

        base_color = self.PREDEFINED_COLORS.get(sel)
        if base_color:
            self.current_palette = self.generate_palette_from_base(base_color)
            self.palette_size = len(self.current_palette)
            self.scale_size.set(self.palette_size)
            self.push_history()
            self.update_palette_display()
            self.update_selected_color(0)
            self.status(f"Paleta base '{sel}' aplicada.")

    def generate_palette_from_base(self, base_color):
        size = self.palette_size
        r, g, b = hex_to_rgb(base_color)
        
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        
        palette = []
        # Cria um gradiente variando a lightness e mantendo o hue e a saturação
        # Ajuste para garantir variação perceptível, mas dentro de limites razoáveis
        start_l = max(0.1, l - 0.35) # Começa um pouco mais escuro que a base
        end_l = min(0.9, l + 0.35)   # Termina um pouco mais claro que a base

        for i in range(size):
            factor = i / (size - 1) if size > 1 else 0
            
            new_l = start_l + (end_l - start_l) * factor
            
            nr, ng, nb = colorsys.hls_to_rgb(h, new_l, s)
            # Garante que os valores RGB estejam dentro de 0-255 antes de converter para HEX
            nr = max(0, min(255, int(nr*255)))
            ng = max(0, min(255, int(ng*255)))
            nb = max(0, min(255, int(nb*255)))
            palette.append(rgb_to_hex((nr, ng, nb)))
        return palette

    def generate_gradient(self):
        if self.palette_size < 2:
            messagebox.showinfo("Aviso", "A paleta deve ter ao menos 2 cores para gerar um gradiente.")
            self.status("Não é possível gerar gradiente com menos de 2 cores.", duration=3000)
            return

        c1_chosen = colorchooser.askcolor(title="Escolha a COR INICIAL do gradiente", initialcolor=self.current_palette[0])
        if c1_chosen[1] is None:
            self.status("Geração de gradiente cancelada.", duration=2000)
            return

        c2_chosen = colorchooser.askcolor(title="Escolha a COR FINAL do gradiente", initialcolor=self.current_palette[-1])
        if c2_chosen[1] is None:
            self.status("Geração de gradiente cancelada.", duration=2000)
            return

        self.current_palette = interpolate_colors(c1_chosen[1], c2_chosen[1], self.palette_size)
        self.push_history()
        self.update_palette_display()
        self.update_selected_color(0)
        self.status("Gradiente gerado com sucesso.")

    def copy_hex_to_clipboard(self):
        if self.selected_index != -1 and self.current_palette:
            hex_value = self.current_palette[self.selected_index].upper()
            self.clipboard_clear()
            self.clipboard_append(hex_value)
            self.update()
            self.status(f"HEX '{hex_value}' copiado para a área de transferência.")
        else:
            self.status("Nenhuma cor selecionada para copiar.", duration=3000)

    # --- FUNÇÕES DE HISTÓRICO (Undo/Redo) ---
    def push_history(self):
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]

        self.history.append(self.current_palette.copy())
        self.history_index += 1

        if len(self.history) > 15:
            self.history.pop(0)
            self.history_index -= 1

        self.update_history_box()
        self.update_undo_redo_buttons()

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_palette = self.history[self.history_index].copy()
            self.palette_size = len(self.current_palette)
            self.scale_size.set(self.palette_size)
            self.update_palette_display()
            self.update_selected_color(self.selected_index)
            self.update_history_box()
            self.update_undo_redo_buttons()
            self.status("Desfeito.")
        else:
            self.status("Não há mais ações para desfazer.", duration=2000)

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_palette = self.history[self.history_index].copy()
            self.palette_size = len(self.current_palette)
            self.scale_size.set(self.palette_size)
            self.update_palette_display()
            self.update_selected_color(self.selected_index)
            self.update_history_box()
            self.update_undo_redo_buttons()
            self.status("Refeito.")
        else:
            self.status("Não há mais ações para refazer.", duration=2000)

    def update_undo_redo_buttons(self):
        self.btn_undo.config(state="normal" if self.history_index > 0 else "disabled")
        self.btn_redo.config(state="normal" if self.history_index < len(self.history) - 1 else "disabled")

    def update_history_box(self):
        self.history_listbox.delete(0, tk.END)
        for idx, pal in enumerate(self.history):
            display_colors = ", ".join(pal)
            if len(display_colors) > 60:
                display_colors = display_colors[:57] + "..."
            prefix = ">> " if idx == self.history_index else "    "
            self.history_listbox.insert(tk.END, prefix + display_colors)
        self.history_listbox.see(self.history_index)
        self.history_listbox.selection_clear(0, tk.END)
        self.history_listbox.selection_set(self.history_index)

    def on_history_select(self, event):
        sel_indices = self.history_listbox.curselection()
        if sel_indices:
            index = sel_indices[0]
            if index != self.history_index:
                self.history_index = index
                self.current_palette = self.history[index].copy()
                self.palette_size = len(self.current_palette)
                self.scale_size.set(self.palette_size)
                self.update_palette_display()
                self.update_selected_color(0)
                self.update_undo_redo_buttons()
                self.status("Paleta do histórico carregada.")
        else:
            self.status("Nenhuma entrada do histórico selecionada.", duration=2000)

    # --- SALVAR / CARREGAR PALETAS (JSON) ---
    def save_palette(self):
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                            title="Salvar Paleta")
        if not path:
            self.status("Operação de salvar cancelada.", duration=2000)
            return
        try:
            data = {
                "palette_size": self.palette_size,
                "colors": self.current_palette
            }
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            self.status(f"Paleta salva em: {path}")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Falha ao salvar arquivo: {e}")
            self.status(f"Erro ao salvar: {e}", duration=5000)

    def load_palette(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                          title="Carregar Paleta")
        if not path:
            self.status("Operação de carregar cancelada.", duration=2000)
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            colors = data.get("colors", [])
            if not colors or not isinstance(colors, list) or not all(isinstance(c, str) and c.startswith("#") and len(c) == 7 for c in colors):
                raise ValueError("Formato de paleta inválido no arquivo.")

            self.current_palette = colors[:]
            self.palette_size = len(colors)
            self.scale_size.set(self.palette_size)
            self.history.clear()
            self.history_index = -1
            self.push_history()
            self.update_palette_display()
            self.update_selected_color(0)
            self.status(f"Paleta carregada de: {path}")
        except json.JSONDecodeError:
            messagebox.showerror("Erro ao Carregar", "Arquivo JSON inválido ou corrompido.")
            self.status("Erro: Arquivo JSON inválido.", duration=5000)
        except ValueError as ve:
            messagebox.showerror("Erro ao Carregar", f"Conteúdo da paleta inválido: {ve}")
            self.status(f"Erro: Conteúdo inválido no arquivo: {ve}", duration=5000)
        except Exception as e:
            messagebox.showerror("Erro ao Carregar", f"Falha ao carregar arquivo: {e}")
            self.status(f"Erro ao carregar: {e}", duration=5000)

    # --- OUTROS COMANDOS GERAIS ---
    def new_palette(self, confirm=True):
        if confirm and not messagebox.askyesno("Nova Paleta", "Deseja criar uma nova paleta? Todas as alterações atuais e o histórico serão perdidos."):
            self.status("Criação de nova paleta cancelada.", duration=2000)
            return
        
        self.current_palette = ["#FFFFFF" for _ in range(7)]
        self.palette_size = 7
        self.scale_size.set(self.palette_size)
        self.history.clear()
        self.history_index = -1
        self.push_history()
        self.update_palette_display()
        self.update_selected_color(0)
        self.status("Nova paleta criada.")

    def get_contrast_color(self, hexcolor):
        r, g, b = hex_to_rgb(hexcolor)
        def sRGB_to_Linear(C):
            C = C / 255.0
            if C <= 0.03928:
                return C / 12.92
            else:
                return ((C + 0.055) / 1.055) ** 2.4

        L = 0.2126 * sRGB_to_Linear(r) + 0.7152 * sRGB_to_Linear(g) + 0.0722 * sRGB_to_Linear(b)
        return "#000000" if L > 0.179 else "#FFFFFF"

    def on_close(self):
        if messagebox.askokcancel("Sair do ColorMaster", "Deseja realmente sair?"):
            self.destroy()

if __name__ == "__main__":
    app = ColorMasterApp()
    app.mainloop()