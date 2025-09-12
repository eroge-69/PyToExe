#!/usr/bin/env python3
# in_project_estoque_final.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
import hashlib, binascii, os

DB_PATH = "estoque.db"

# ---------------------------
# Banco de dados
# ---------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        maximo INTEGER NOT NULL,
        atual INTEGER NOT NULL DEFAULT 0
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        tipo TEXT,
        categoria TEXT,
        quantidade INTEGER,
        timestamp TEXT
    )""")
    conn.commit()
    conn.close()

# ---------------------------
# Senhas
# ---------------------------
def hash_password(password):
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 150000)
    return binascii.hexlify(salt).decode() + '$' + binascii.hexlify(dk).decode()

def verify_password(stored, password):
    try:
        salt_hex, dk_hex = stored.split('$')
        salt = binascii.unhexlify(salt_hex)
        dk = binascii.unhexlify(dk_hex)
        new = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 150000)
        return new == dk
    except: return False

# ---------------------------
# DB helpers
# ---------------------------
def criar_usuario_db(username,password):
    conn=get_db(); cur=conn.cursor()
    try:
        cur.execute("INSERT INTO usuarios(username,password_hash) VALUES (?,?)",
                    (username,hash_password(password)))
        conn.commit(); conn.close()
        registrar_historico(username,"cadastro_usuario",None,None)
        return True,None
    except sqlite3.IntegrityError:
        conn.close()
        return False,"Nome de usuário já existe."

def validar_login_db(username,password):
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT password_hash FROM usuarios WHERE username=?",(username,))
    row=cur.fetchone(); conn.close()
    if not row: return False
    return verify_password(row["password_hash"],password)

def listar_categorias_db():
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT nome,atual,maximo FROM categorias ORDER BY nome")
    rows=cur.fetchall(); conn.close()
    return [dict(r) for r in rows]

def adicionar_categoria_db(nome,maximo,usuario):
    conn=get_db(); cur=conn.cursor()
    try:
        cur.execute("INSERT INTO categorias(nome,maximo,atual) VALUES (?,?,0)",(nome,maximo))
        conn.commit(); conn.close()
        registrar_historico(usuario,"criar_categoria",nome,None)
        return True,None
    except sqlite3.IntegrityError:
        conn.close()
        return False,"Categoria já existe."

def remover_categoria_db(nome,usuario):
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT id FROM categorias WHERE nome=?",(nome,))
    if not cur.fetchone(): conn.close(); return False,"Categoria não encontrada."
    cur.execute("DELETE FROM categorias WHERE nome=?",(nome,))
    conn.commit(); conn.close()
    registrar_historico(usuario,"remover_categoria",nome,None)
    return True,None

def alterar_quantidade_db(nome,delta,usuario):
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT atual,maximo FROM categorias WHERE nome=?",(nome,))
    row=cur.fetchone()
    if not row: conn.close(); return False,"Categoria não encontrada."
    atual,maximo=row["atual"],row["maximo"]
    novo=atual+delta
    if novo<0: novo=0; efetivo=-atual
    elif novo>maximo: efetivo=(maximo-atual) if delta>0 else delta
    else: efetivo=delta
    cur.execute("UPDATE categorias SET atual=? WHERE nome=?",(novo,nome))
    conn.commit(); conn.close()
    tipo="entrada" if delta>0 else "saida"
    registrar_historico(usuario,tipo,nome,abs(delta if efetivo is None else efetivo))
    return True,None

def registrar_historico(usuario,tipo,categoria,quantidade):
    conn=get_db(); cur=conn.cursor()
    ts=datetime.now().isoformat()
    cur.execute("INSERT INTO historico(usuario,tipo,categoria,quantidade,timestamp) VALUES (?,?,?,?,?)",
                (usuario,tipo,categoria,quantidade,ts))
    conn.commit(); conn.close()

def carregar_historico_db(limit=None,days=None):
    conn=get_db(); cur=conn.cursor()
    query="SELECT usuario,tipo,categoria,quantidade,timestamp FROM historico"
    params=[]; conds=[]
    if days is not None:
        dt=(datetime.now()-timedelta(days=days)).isoformat()
        conds.append("timestamp >= ?"); params.append(dt)
    if conds: query+=" WHERE "+" AND ".join(conds)
    query+=" ORDER BY id DESC"
    if limit: query+=f" LIMIT {int(limit)}"
    cur.execute(query,params)
    rows=cur.fetchall(); conn.close()
    seen=set(); unique=[]
    for r in rows:
        key=(r["usuario"],r["tipo"],r["categoria"],r["quantidade"],r["timestamp"])
        if key not in seen: seen.add(key); unique.append(dict(r))
    return unique

def calcular_totais_entradas_saidas():
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT COALESCE(SUM(quantidade),0) as soma FROM historico WHERE tipo='entrada'")
    entr=cur.fetchone()["soma"]
    cur.execute("SELECT COALESCE(SUM(quantidade),0) as soma FROM historico WHERE tipo='saida'")
    sai=cur.fetchone()["soma"]; conn.close()
    return int(entr),int(sai)

# ---------------------------
# UI
# ---------------------------
ROOT=tk.Tk(); ROOT.withdraw(); ROOT.title("In Project - Estoque")
current_user=None

STYLE_BG="#f4f4f9"
STYLE_TEXT="#222"
STYLE_BTN_PRIMARY="#4e8cff"
STYLE_BTN_SECONDARY="#aaa"
STYLE_BTN_DANGER="#e74c3c"
STYLE_FONT=("Helvetica",11)

def center(win,w=600,h=400):
    win.update_idletasks()
    sw=win.winfo_screenwidth(); sh=win.winfo_screenheight()
    x=(sw//2)-(w//2); y=(sh//2)-(h//2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def styled_button(parent,text,cmd,bg=STYLE_BTN_PRIMARY,width=16,height=2):
    b=tk.Button(parent,text=text,command=cmd,bg=bg,fg="white",font=STYLE_FONT,width=width,height=height,relief="raised")
    return b

# ---------------------------
# Registro
# ---------------------------
def open_register(required=False):
    reg=tk.Toplevel(); reg.title("Registrar usuário")
    center(reg,420,240); reg.grab_set(); reg.configure(bg=STYLE_BG)
    tk.Label(reg,text="Criar novo usuário",font=("Helvetica",12,"bold"),bg=STYLE_BG,fg=STYLE_TEXT).pack(pady=8)
    frm=tk.Frame(reg,bg=STYLE_BG); frm.pack(padx=12,pady=6)
    tk.Label(frm,text="Usuário:",bg=STYLE_BG,fg=STYLE_TEXT).grid(row=0,column=0,sticky="w")
    entry_user=tk.Entry(frm,width=30); entry_user.grid(row=0,column=1,pady=4)
    tk.Label(frm,text="Senha:",bg=STYLE_BG,fg=STYLE_TEXT).grid(row=1,column=0,sticky="w")
    entry_pass=tk.Entry(frm,show="*",width=30); entry_pass.grid(row=1,column=1,pady=4)
    tk.Label(frm,text="Confirmar senha:",bg=STYLE_BG,fg=STYLE_TEXT).grid(row=2,column=0,sticky="w")
    entry_pass2=tk.Entry(frm,show="*",width=30); entry_pass2.grid(row=2,column=1,pady=4)

    def on_create():
        u=entry_user.get().strip(); p=entry_pass.get(); p2=entry_pass2.get()
        if not u or not p: messagebox.showerror("Erro","Usuário e senha obrigatórios"); return
        if p!=p2: messagebox.showerror("Erro","Senhas não conferem"); return
        ok,err=criar_usuario_db(u,p)
        if not ok: messagebox.showerror("Erro",err); return
        messagebox.showinfo("OK","Usuário criado com sucesso"); reg.destroy(); login_success(u)

    btn_frame=tk.Frame(reg,bg=STYLE_BG); btn_frame.pack(pady=10)
    styled_button(btn_frame,"Criar usuário",on_create).pack(side="left",padx=6)
    if not required: styled_button(btn_frame,"Cancelar",reg.destroy,bg=STYLE_BTN_SECONDARY).pack(side="left",padx=6)
    else:
        def on_close(): 
            if messagebox.askokcancel("Sair","Deseja sair do aplicativo?"): ROOT.quit()
        reg.protocol("WM_DELETE_WINDOW",on_close)

# ---------------------------
# Login
# ---------------------------
def open_login():
    login=tk.Toplevel(); login.title("Login"); center(login,420,200); login.grab_set(); login.configure(bg=STYLE_BG)
    tk.Label(login,text="Login",font=("Helvetica",14,"bold"),bg=STYLE_BG,fg=STYLE_TEXT).pack(pady=8)
    frm=tk.Frame(login,bg=STYLE_BG); frm.pack(padx=12,pady=6)
    tk.Label(frm,text="Usuário:",bg=STYLE_BG,fg=STYLE_TEXT).grid(row=0,column=0,sticky="w")
    entry_user=tk.Entry(frm,width=30); entry_user.grid(row=0,column=1,pady=4)
    tk.Label(frm,text="Senha:",bg=STYLE_BG,fg=STYLE_TEXT).grid(row=1,column=0,sticky="w")
    entry_pass=tk.Entry(frm,show="*",width=30); entry_pass.grid(row=1,column=1,pady=4)
    entry_user.focus_set()
    btns=tk.Frame(login,bg=STYLE_BG); btns.pack(pady=8)
    styled_button(btns,"Entrar",lambda: login_action(entry_user.get(),entry_pass.get())).pack(side="left",padx=6)
    styled_button(btns,"Registrar novo",open_register,bg=STYLE_BTN_SECONDARY).pack(side="left",padx=6)
    styled_button(btns,"Sair",ROOT.quit,bg=STYLE_BTN_DANGER).pack(side="left",padx=6)

def login_action(u,p):
    u=u.strip()
    if not u or not p: messagebox.showerror("Erro","Preencha usuário e senha"); return
    if validar_login_db(u,p): registrar_historico(u,"login",None,None); login_success(u)
    else: messagebox.showerror("Erro","Usuário ou senha incorretos")

# ---------------------------
# Tela principal
# ---------------------------
def login_success(username):
    global current_user
    current_user=username; ROOT.deiconify(); ROOT.geometry("600x500"); center(ROOT,600,500)
    for w in ROOT.winfo_children(): w.destroy()
    ROOT.configure(bg=STYLE_BG)
    tk.Label(ROOT,text="In Project",font=("Helvetica",18,"bold"),bg=STYLE_BG,fg=STYLE_TEXT).pack(pady=12)
    tk.Label(ROOT,text=f"Bem-vindo, {current_user}",font=("Helvetica",11),bg=STYLE_BG,fg=STYLE_TEXT).pack()
    btn_frame=tk.Frame(ROOT,bg=STYLE_BG); btn_frame.pack(pady=20)
    styled_button(btn_frame,"Estoque",open_estoque).pack(pady=6)
    styled_button(btn_frame,"Sobre",open_sobre,bg=STYLE_BTN_SECONDARY).pack(pady=6)
    styled_button(btn_frame,"Sair",logout,bg=STYLE_BTN_DANGER).pack(pady=6)

def logout():
    global current_user
    if messagebox.askyesno("Sair","Deseja fazer logout?"):
        registrar_historico(current_user,"logout",None,None)
        current_user=None; ROOT.withdraw(); open_login()

# ---------------------------
# Sobre
# ---------------------------
def open_sobre():
    s=tk.Toplevel(); s.title("Sobre"); center
    def open_sobre():s = tk.Toplevel()
    s.title("Sobre — In Project")
    center(s, 380, 240)
    s.grab_set()
    s.configure(bg=STYLE_BG)
    tk.Label(s, text="Projetado por Matunas em 2025", font=("Helvetica",12), bg=STYLE_BG, fg=STYLE_TEXT).pack(pady=6)
    tk.Label(s, text="In Project", font=("Helvetica",12,"bold"), bg=STYLE_BG, fg=STYLE_TEXT).pack(pady=2)
    tk.Label(s, text="Luis Henrique", font=("Helvetica",11), bg=STYLE_BG, fg=STYLE_TEXT).pack(pady=2)
    tk.Label(s, text="Contato: lh5465214@gmail.com", font=("Helvetica",11), bg=STYLE_BG, fg=STYLE_TEXT).pack(pady=6)
    styled_button(s, "Fechar", s.destroy).pack(pady=6)

# ---------------------------
# Estoque
# ---------------------------
def open_estoque():
    est = tk.Toplevel()
    est.title("Estoque — In Project")
    center(est, 800, 550)
    est.grab_set()
    est.configure(bg=STYLE_BG)

    # topo
    topo = tk.Frame(est, bg=STYLE_BG)
    topo.pack(fill="x", padx=8, pady=6)
    tk.Label(topo, text=f"Usuário logado: {current_user}", font=("Helvetica",11,"bold"), bg=STYLE_BG, fg=STYLE_TEXT).pack(side="left")
    tk.Button(topo, text="Relatório Geral", command=mostrar_relatorio_geral, bg=STYLE_BTN_SECONDARY, fg="white").pack(side="right")

    # mini histórico
    hist_frame = tk.LabelFrame(est, text="Mini histórico (últimos 7 dias)", padx=8, pady=6, bg=STYLE_BG, fg=STYLE_TEXT)
    hist_frame.pack(fill="x", padx=8, pady=6)
    recent = carregar_historico_db(limit=5, days=7)
    if not recent:
        tk.Label(hist_frame, text="Sem movimentações recentes.", fg="gray", bg=STYLE_BG).pack(anchor="w")
    else:
        for rec in recent:
            ts = datetime.fromisoformat(rec["timestamp"]).strftime("%d/%m %H:%M")
            txt = f"{ts} — {rec['usuario']}: {rec['tipo']}"
            if rec["categoria"]:
                txt += f" — {rec['categoria']}"
            if rec["quantidade"] is not None:
                txt += f" ({rec['quantidade']})"
            tk.Label(hist_frame, text=txt, font=("Helvetica",10), fg="gray", bg=STYLE_BG).pack(anchor="w")

    # lista com scroll
    cont = tk.Frame(est, bg=STYLE_BG)
    cont.pack(fill="both", expand=True, padx=8, pady=6)
    canvas = tk.Canvas(cont, highlightthickness=0, bg=STYLE_BG)
    vsb = tk.Scrollbar(cont, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    frame_list = tk.Frame(canvas, bg=STYLE_BG)
    canvas.create_window((0,0), window=frame_list, anchor="nw")
    def on_config(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame_list.bind("<Configure>", on_config)

    def refresh_list():
        for w in frame_list.winfo_children():
            w.destroy()
        cats = listar_categorias_db()
        if not cats:
            tk.Label(frame_list, text="Nenhuma categoria cadastrada.", fg="gray", bg=STYLE_BG).pack(pady=8)
            return
        for c in cats:
            nome = c["nome"]
            atual = c["atual"]
            maximo = c["maximo"]
            percentual = (atual / maximo) * 100 if maximo>0 else 0
            cor = "green" if percentual>=60 else "red"

            item = tk.Frame(frame_list, pady=6, bg=STYLE_BG)
            item.pack(fill="x", padx=6)

            lbl = tk.Label(item, text=f"{nome} — {atual}/{maximo}", font=("Helvetica",11), bg=STYLE_BG, fg=STYLE_TEXT)
            lbl.pack(side="left")

            luz = tk.Label(item, text="⬤", fg=cor, font=("Helvetica",14), bg=STYLE_BG)
            luz.pack(side="right", padx=6)

            pb = ttk.Progressbar(item, orient="horizontal", length=160, mode="determinate")
            pb["value"] = percentual
            pb.pack(side="right", padx=6)

            btns = tk.Frame(item, bg=STYLE_BG)
            btns.pack(side="right", padx=6)
            styled_button(btns, "+", lambda n=nome: on_change(n, True, refresh_list), width=3, height=1).pack(side="left", padx=2)
            styled_button(btns, "-", lambda n=nome: on_change(n, False, refresh_list), width=3, height=1, bg=STYLE_BTN_DANGER).pack(side="left", padx=2)

    refresh_list()

    # botoes inferiores
    footer = tk.Frame(est, bg=STYLE_BG)
    footer.pack(fill="x", pady=8)
    styled_button(footer, "Adicionar Categoria", lambda: on_add_category(refresh_list)).pack(side="left", padx=6)
    styled_button(footer, "Remover Categoria", lambda: on_remove_category(refresh_list), bg=STYLE_BTN_DANGER).pack(side="left", padx=6)
    styled_button(footer, "Ver histórico completo", open_historico, bg=STYLE_BTN_SECONDARY).pack(side="left", padx=6)
    styled_button(footer, "Fechar", est.destroy, bg=STYLE_BTN_SECONDARY).pack(side="right", padx=6)


# ---------------------------
# ações
# ---------------------------
def on_change(nome, is_add, refresh_callback):
    prompt = "Quantidade a adicionar:" if is_add else "Quantidade a remover:"
    qtd = simpledialog.askinteger("Quantidade", prompt, minvalue=1)
    if qtd is None:
        return
    delta = qtd if is_add else -qtd
    ok, err = alterar_quantidade_db(nome, delta, current_user)
    if not ok:
        messagebox.showerror("Erro", err)
        return
    # Atualiza a tela imediatamente
    refresh_callback()

def on_add_category(refresh_callback):
    nome = simpledialog.askstring("Nova categoria","Nome da categoria:")
    if not nome: return
    maximo = simpledialog.askinteger("Capacidade máxima",f"Quantidade máxima de {nome}:",minvalue=1)
    if maximo is None: return
    ok, err = adicionar_categoria_db(nome,maximo,current_user)
    if not ok: messagebox.showerror("Erro",err)
    else: refresh_callback(); messagebox.showinfo("OK",f"Categoria '{nome}' criada.")

def on_remove_category(refresh_callback):
    nome = simpledialog.askstring("Remover categoria","Nome da categoria a remover:")
    if not nome: return
    if messagebox.askyesno("Confirmar",f"Remover a categoria '{nome}'?"):
        ok, err = remover_categoria_db(nome,current_user)
        if not ok: messagebox.showerror("Erro",err)
        else: refresh_callback(); messagebox.showinfo("OK","Categoria removida.")

# ---------------------------
# Histórico completo
# ---------------------------
def open_historico():
    hwin = tk.Toplevel(); hwin.title("Histórico completo"); center(hwin,720,480); hwin.grab_set(); hwin.configure(bg=STYLE_BG)
    tk.Label(hwin,text="Histórico de movimentações",font=("Helvetica",12,"bold"),bg=STYLE_BG,fg=STYLE_TEXT).pack(pady=8)
    cont=tk.Frame(hwin,bg=STYLE_BG); cont.pack(fill="both",expand=True,padx=8,pady=6)
    cols=("timestamp","usuario","tipo","categoria","quantidade")
    tree=ttk.Treeview(cont,columns=cols,show="headings")
    for c in cols: tree.heading(c,text=c.capitalize()); tree.column(c,anchor="w")
    vsb=ttk.Scrollbar(cont,orient="vertical",command=tree.yview)
    tree.configure(yscrollcommand=vsb.set); vsb.pack(side="right",fill="y"); tree.pack(side="left",fill="both",expand=True)
    rows = carregar_historico_db(limit=1000)
    for r in rows:
        ts=datetime.fromisoformat(r["timestamp"]).strftime("%d/%m %H:%M")
        tree.insert("","end",values=(ts,r["usuario"],r["tipo"],r["categoria"] or "",r["quantidade"] or ""))

    # exportar CSV
    def export_csv():
        path = simpledialog.askstring("Exportar CSV","Digite o nome do arquivo (ex: historico.csv):")
        if not path: return
        try:
            import csv
            with open(path,"w",newline='',encoding='utf-8') as f:
                writer=csv.writer(f); writer.writerow(cols)
                for r in rows: writer.writerow([r["timestamp"],r["usuario"],r["tipo"],r["categoria"],r["quantidade"]])
            messagebox.showinfo("OK",f"Exportado para {path}")
        except Exception as e:
            messagebox.showerror("Erro",f"Falha ao exportar: {e}")
    frm = tk.Frame(hwin,bg=STYLE_BG); frm.pack(pady=8)
    styled_button(frm,"Exportar CSV",export_csv,bg=STYLE_BTN_PRIMARY).pack(side="left",padx=6)
    styled_button(frm,"Fechar",hwin.destroy,bg=STYLE_BTN_SECONDARY).pack(side="left",padx=6)

# ---------------------------
# Relatório geral
# ---------------------------
def mostrar_relatorio_geral():
    entradas, saidas = calcular_totais_entradas_saidas()
    cats = listar_categorias_db()
    total_atual = sum(c["atual"] for c in cats)
    total_max = sum(c["maximo"] for c in cats)
    messagebox.showinfo("Relatório Geral",
                        f"Entradas totais: {entradas}\n"
                        f"Saídas totais: {saidas}\n\n"
                        f"Total atual (itens): {total_atual}\n"
                        f"Capacidade máxima (itens): {total_max}")

# ---------------------------
# Inicialização
# ---------------------------
def start_app():
    init_db()
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT COUNT(*) FROM usuarios"); total=cur.fetchone()[0]; conn.close()
    if total==0: open_register(required=True)
    else: open_login()
    ROOT.mainloop()

if __name__=="__main__":
    start_app()

