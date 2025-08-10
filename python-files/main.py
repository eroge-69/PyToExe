import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ----------------------------
# Configurações
# ----------------------------
FILMES = ["Matrix", "Avatar", "Interestelar", "Oppenheimer"]
SESSOES = ["10:00", "13:00", "16:00", "19:00"]
LUGARES_POR_SESSAO = 100
ARQUIVO_ESTADO = "cinema.json"

# Paleta “Cinema”
COL_BG      = "#0f1117"  # fundo geral
COL_PANEL   = "#151a23"  # painel/card
COL_EDGE    = "#1f2430"  # borda/card
COL_TEXT    = "#e5e7eb"  # texto claro
COL_MUTED   = "#9ca3af"  # texto secundário
COL_ACCENT  = "#e50914"  # vermelho destaque
COL_OK      = "#22c55e"  # verde (disponível)
COL_BAD     = "#ef4444"  # vermelho (ocupado)
COL_WARN    = "#f59e0b"  # dourado

FONT_BASE = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI Semibold", 12)
FONT_HEAD = ("Segoe UI Semibold", 10)

class CinemaApp:
    def __init__(self):
        self.cinema = self._estado_inicial()
        self.root_main = None
        self.tree = None
        self.btn_mapa = None
        self.carregar_estado()

    # ----------------------------
    # Persistência
    # ----------------------------
    def _estado_inicial(self):
        return {f: {s: [None] * LUGARES_POR_SESSAO for s in SESSOES} for f in FILMES}

    def carregar_estado(self):
        if not os.path.exists(ARQUIVO_ESTADO):
            return
        try:
            with open(ARQUIVO_ESTADO, "r", encoding="utf-8") as f:
                data = json.load(f)
            ok = True
            for f in FILMES:
                if f not in data:
                    ok = False
                    break
                for s in SESSOES:
                    if s not in data[f] or not isinstance(data[f][s], list) or len(data[f][s]) != LUGARES_POR_SESSAO:
                        ok = False
                        break
            if ok:
                self.cinema = data
        except Exception as e:
            print("Aviso: falha ao carregar estado:", e)

    def salvar_estado(self):
        try:
            with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as f:
                json.dump(self.cinema, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar estado: {e}")

    # ----------------------------
    # Estilo/tema
    # ----------------------------
    def _aplicar_tema(self, root: tk.Tk):
        root.configure(bg=COL_BG)
        style = ttk.Style(root)
        # usar um tema que permita customização
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=COL_BG, foreground=COL_TEXT, font=FONT_BASE)

        # Frames “cards”
        style.configure("Card.TFrame", background=COL_PANEL, relief="solid", bordercolor=COL_EDGE, borderwidth=1)
        style.map("Card.TFrame", background=[("active", COL_PANEL)])

        # Labels
        style.configure("TLabel", background=COL_BG, foreground=COL_TEXT)
        style.configure("Muted.TLabel", background=COL_BG, foreground=COL_MUTED)
        style.configure("Card.TLabel", background=COL_PANEL, foreground=COL_TEXT)

        # Botões
        style.configure("TButton", background=COL_EDGE, foreground=COL_TEXT, borderwidth=0, padding=(10, 6))
        style.map("TButton",
                  background=[("active", "#2a3140"), ("pressed", "#2a3140")],
                  relief=[("pressed", "sunken")])

        style.configure("Accent.TButton", background=COL_ACCENT, foreground="white", padding=(12, 6))
        style.map("Accent.TButton",
                  background=[("active", "#bf0811"), ("pressed", "#bf0811")])

        # Treeview
        style.configure("Treeview",
                        background=COL_PANEL, fieldbackground=COL_PANEL,
                        foreground=COL_TEXT, bordercolor=COL_EDGE, borderwidth=1, rowheight=22)
        style.configure("Treeview.Heading",
                        background="#202633", foreground=COL_TEXT, font=FONT_HEAD, bordercolor=COL_EDGE, borderwidth=1)
        style.map("Treeview",
                  background=[("selected", "#2b3344")],
                  foreground=[("selected", COL_TEXT)])

        # Scrollbar discreta
        style.configure("Vertical.TScrollbar", background=COL_PANEL, troughcolor=COL_EDGE, bordercolor=COL_EDGE)

    # ----------------------------
    # Cabeçalho com “gradiente”
    # ----------------------------
    def _header(self, parent):
        header = tk.Canvas(parent, height=54, highlightthickness=0, bd=0, bg=COL_BG)
        header.pack(fill="x")

        # gradiente simples (linhas horizontais)
        w = parent.winfo_width() or parent.winfo_screenwidth()
        for i in range(54):
            # mistura entre tons
            r1, g1, b1 = (229, 9, 20)    # COL_ACCENT
            r2, g2, b2 = (31, 36, 48)    # COL_EDGE
            t = i / 54
            r = int(r1*(1-t) + r2*t)
            g = int(g1*(1-t) + g2*t)
            b = int(b1*(1-t) + b2*t)
            header.create_line(0, i, w, i, fill=f"#{r:02x}{g:02x}{b:02x}")

        # Título
        header.create_text(16, 28, text="🎬 Cinema – Reservas", anchor="w",
                           fill="white", font=("Segoe UI Semibold", 14))
        header.create_text(w-16, 28, text="🍿 Bem-vindo(a)", anchor="e",
                           fill="#f3f4f6", font=("Segoe UI", 10))
        return header

    # ----------------------------
    # Janela principal (450x300 centralizada)
    # ----------------------------
    def abrir_interface_principal(self):
        self.root_main = tk.Tk()
        self.root_main.title("🎬 Sistema de Reservas de Cinema")

        # Tema
        self._aplicar_tema(self.root_main)

        # Dimensões
        largura, altura = 450, 300
        largura_tela = self.root_main.winfo_screenwidth()
        altura_tela = self.root_main.winfo_screenheight()
        x = (largura_tela - largura) // 2
        y = (altura_tela - altura) // 2
        self.root_main.geometry(f"{largura}x{altura}+{x}+{y}")

        # Cabeçalho bonito
        self._header(self.root_main)

        # Área principal “card”
        outer = ttk.Frame(self.root_main, style="Card.TFrame", padding=8)
        outer.pack(fill="both", expand=True, padx=8, pady=(6, 8))

        # Topo do card: subtítulo + dica
        topbar = ttk.Frame(outer, style="Card.TFrame", padding=(8, 6))
        topbar.pack(fill="x")
        ttk.Label(topbar, text="Selecione um filme para ver os lugares",
                  style="Card.TLabel", font=FONT_TITLE).pack(side="left")
        ttk.Label(topbar, text="Dica: duplo clique abre o mapa de lugares",
                  style="Card.TLabel", foreground=COL_MUTED, font=("Segoe UI", 9)).pack(side="right")

        # Tabela + scrollbar em card
        table_card = ttk.Frame(outer, style="Card.TFrame", padding=6)
        table_card.pack(fill="both", expand=True, pady=(6, 6))

        tree_frame = ttk.Frame(table_card, style="Card.TFrame")
        tree_frame.pack(fill="both", expand=True)

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        cols = ["Filme"] + SESSOES
        self.tree = ttk.Treeview(
            tree_frame,
            columns=cols,
            show="headings",
            yscrollcommand=scroll_y.set,
            selectmode="browse",
        )
        scroll_y.config(command=self.tree.yview)

        for col in cols:
            self.tree.heading(col, text=col, anchor="center")
            width = 140 if col == "Filme" else 70
            self.tree.column(col, anchor="center", width=width, stretch=False)
        self.tree.pack(fill="both", expand=True)

        # ações
        actions = ttk.Frame(outer, style="Card.TFrame", padding=(8, 6))
        actions.pack(fill="x")

        ttk.Button(actions, text="🔄 Atualizar", command=self.atualizar_lista).pack(side="left", padx=4)
        self.btn_mapa = ttk.Button(actions, text="🗺️ Mapa de lugares", command=self.reservar_por_mapa, state="disabled",
                                   style="Accent.TButton")
        self.btn_mapa.pack(side="left", padx=4)
        ttk.Button(actions, text="💾 Guardar", command=self.salvar_estado).pack(side="right", padx=4)
        ttk.Button(actions, text="⏻ Sair", command=self.root_main.destroy).pack(side="right", padx=4)

        def on_select(_):
            self.btn_mapa.config(state=("normal" if self.tree.selection() else "disabled"))
        self.tree.bind("<<TreeviewSelect>>", on_select)

        # Duplo clique para abrir diretamente
        self.tree.bind("<Double-1>", lambda e: self.reservar_por_mapa())

        self.atualizar_lista()
        self.root_main.mainloop()

    def atualizar_lista(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for filme in FILMES:
            linha = [filme]
            for sessao in SESSOES:
                disponiveis = self.cinema[filme][sessao].count(None)
                linha.append(disponiveis)
            self.tree.insert('', tk.END, values=linha)

    # ----------------------------
    # Mapa de lugares (A1..J10 + corredor visual) com hover
    # ----------------------------
    def reservar_por_mapa(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um filme na tabela.")
            return
        filme = self.tree.item(item[0])['values'][0]

        # Escolha de sessão
        seletor = tk.Toplevel(self.root_main, bg=COL_BG)
        seletor.title("Escolha a sessão")
        seletor.transient(self.root_main)
        seletor.grab_set()

        self._aplicar_tema(seletor)  # aplicar tema também

        frm = ttk.Frame(seletor, style="Card.TFrame", padding=12)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frm, text=f"Sessão para '{filme}':", style="Card.TLabel").pack(padx=10, pady=(0, 6))
        sessao_var = tk.StringVar(value=SESSOES[0])
        combo = ttk.Combobox(frm, textvariable=sessao_var, values=SESSOES, state="readonly")
        combo.pack(fill="x", padx=10)

        def continuar():
            sessao = sessao_var.get()
            seletor.destroy()
            self.abrir_mapa_de_lugares(filme, sessao)

        ttk.Button(frm, text="Continuar", command=continuar, style="Accent.TButton").pack(pady=10)
        combo.focus_set()

    def abrir_mapa_de_lugares(self, filme, sessao):
        # Layout 10x10 com corredor após a coluna 5
        ROWS, COLS = 10, 10
        ROW_LABELS = [chr(ord('A') + r) for r in range(ROWS)]  # A..J
        COL_LABELS = [str(c + 1) for c in range(COLS)]         # 1..10
        AISLE_AFTER = 5  # corredor entre colunas 5 e 6

        mapa = tk.Toplevel(self.root_main, bg=COL_BG)
        mapa.title(f"Mapa de Lugares - {filme} {sessao}")
        mapa.geometry("760x620")
        mapa.transient(self.root_main)
        mapa.grab_set()

        self._aplicar_tema(mapa)

        # Cabeçalho simples no mapa
        self._header(mapa)

        container = ttk.Frame(mapa, style="Card.TFrame", padding=10)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        grid = ttk.Frame(container, style="Card.TFrame", padding=6)
        grid.pack(padx=6, pady=6)

        # Legenda
        legend = ttk.Frame(container, style="Card.TFrame", padding=(8, 6))
        legend.pack(fill="x", pady=(6, 0))
        tk.Label(legend, text="Disponível", bg=COL_PANEL, fg=COL_TEXT, font=("Segoe UI", 9)).pack(side="left")
        tk.Label(legend, width=2, bg=COL_OK).pack(side="left", padx=(4, 10))
        tk.Label(legend, text="Reservado", bg=COL_PANEL, fg=COL_TEXT, font=("Segoe UI", 9)).pack(side="left")
        tk.Label(legend, width=2, bg=COL_BAD).pack(side="left", padx=(4, 10))

        btns = [None] * (ROWS * COLS)
        aisle_grid_col = 1 + AISLE_AFTER

        # Cabeçalho
        ttk.Label(grid, text="", style="Card.TLabel").grid(row=0, column=0, padx=2, pady=2)  # canto vazio
        for c in range(COLS):
            grid_col = 1 + c + (1 if c >= AISLE_AFTER else 0)
            ttk.Label(grid, text=COL_LABELS[c], style="Card.TLabel", anchor="center", width=4)\
                .grid(row=0, column=grid_col, padx=2, pady=2)
        ttk.Label(grid, text="", width=2, style="Card.TLabel").grid(row=0, column=aisle_grid_col, padx=6)  # espaço corredor

        def index_of(r, c): return r * COLS + c

        def pintar(i):
            ocupado = self.cinema[filme][sessao][i] is not None
            btns[i].config(bg=(COL_BAD if ocupado else COL_OK), fg="white",
                           activebackground=(COL_BAD if ocupado else COL_OK),
                           activeforeground="white",
                           relief="flat", bd=0)

        def on_click(r, c):
            i = index_of(r, c)
            ocupado = self.cinema[filme][sessao][i] is not None
            seat_label = f"{ROW_LABELS[r]}{COL_LABELS[c]}"
            if not ocupado:
                nome = simpledialog.askstring("Nome do cliente", f"Reservar o lugar {seat_label} para:")
                if nome:
                    nome_limpo = nome.strip()
                    if not nome_limpo:
                        return
                    self.cinema[filme][sessao][i] = nome_limpo
                    messagebox.showinfo("Reservado", f"{nome_limpo} → {filme}, {sessao}, Lugar {seat_label}")
                    pintar(i)
                    self.atualizar_lista()
                    self.salvar_estado()
            else:
                atual = self.cinema[filme][sessao][i]
                messagebox.showwarning("Reservado", f"Este lugar já está reservado por '{atual}'.")

        # Hover/realce
        def on_enter(i):
            btn = btns[i]
            # só dar brilho em disponível
            disponivel = self.cinema[filme][sessao][i] is None
            if disponivel:
                btn.config(highlightthickness=2, highlightbackground=COL_WARN)

        def on_leave(i):
            btn = btns[i]
            btn.config(highlightthickness=0)

        # Linhas de assentos
        for r in range(ROWS):
            ttk.Label(grid, text=ROW_LABELS[r], style="Card.TLabel", anchor="center", width=2)\
                .grid(row=1 + r, column=0, padx=2, pady=2)
            for c in range(COLS):
                grid_col = 1 + c + (1 if c >= AISLE_AFTER else 0)
                i = index_of(r, c)
                btn = tk.Button(
                    grid,
                    text=f"{ROW_LABELS[r]}{COL_LABELS[c]}",
                    width=4, height=2,
                    cursor="hand2",
                    command=lambda r=r, c=c: on_click(r, c),
                )
                btn.grid(row=1 + r, column=grid_col, padx=3, pady=3)
                btns[i] = btn
                pintar(i)
                # binds de hover
                btn.bind("<Enter>", lambda e, i=i: on_enter(i))
                btn.bind("<Leave>", lambda e, i=i: on_leave(i))

            ttk.Label(grid, text="", width=1, style="Card.TLabel").grid(row=1 + r, column=aisle_grid_col, padx=10)  # corredor

        footer = ttk.Frame(container, style="Card.TFrame")
        footer.pack(fill="x", pady=(8, 0))
        ttk.Button(footer, text="Fechar", command=mapa.destroy).pack(side="right")

if __name__ == "__main__":
    app = CinemaApp()
    app.abrir_interface_principal()