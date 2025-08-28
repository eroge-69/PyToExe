import tkinter as tk
import time
from datetime import datetime, timedelta
from tkinter import simpledialog, messagebox, filedialog, ttk, Toplevel, Listbox, Scrollbar
from PIL import Image, ImageTk
import csv, os
import tempfile
import platform
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
import webbrowser
import tempfile
import glob

#-------------------------------------#
#-------Diretórios e Constantes-------#
#-------------------------------------#

# Pasta principal
DADOS_DIR = "Arquivo de Avisos"
os.makedirs(DADOS_DIR, exist_ok=True)

# Subpasta do ano atual
ano = time.strftime("%Y", time.localtime()) # Quando mudar de ano, cria automaticamente os ficheiros novos, com reset na numeração, e respetiva subpasta do ano.
ANO_DIR = os.path.join(DADOS_DIR, ano)
os.makedirs(ANO_DIR, exist_ok=True)

# Aviso de Bandeira e de Tempo Gravoso gravam no mesmo ficheiro .csv. Definir ficheiros dentro da subpasta do ano
FICHEIROS_TIPOS = {
    "Aviso de Bandeira": os.path.join(ANO_DIR, f"avisos_{ano}.csv"),
    "Aviso de Tempo Gravoso": os.path.join(ANO_DIR, f"avisos_{ano}.csv"),
    "Aviso de Corrente de Jato": os.path.join(ANO_DIR, f"jetstream_{ano}.csv")
}

TIPOS_AVISO = ["Aviso de Bandeira", "Aviso de Tempo Gravoso", "Aviso de Corrente de Jato"]

CAMPOS_BANDEIRA = ["Data do Aviso","Hora do Aviso", "Região", "Unidades informadas", "Data & Hora de início da validade", "Data & Hora de fim da validade", "Descritivo", "Iniciais"]
CAMPOS_GRAVOSO = ["Data do Aviso", "Hora do Aviso", "Região", "Unidades informadas", "Data & Hora de início da validade", "Data & Hora de fim da validade", "Descritivo", "Iniciais"]
CAMPOS_JATO = ["Iniciais","Data do Aviso", "Hora do Aviso", "Direção", "FL Base", "FL Topo", "Int.Máx (KT)", "FL Intensidade Máxima", "Zona (N / C / S)","Data & Hora de início da validade", "Data & Hora de fim da validade", "Cancelamento", "Entidade contactada"]

#---------------------------------------#
#-----Regiões e respetivas Unidades-----#
#---------------------------------------#
unidades_por_regiao = {
    "Continente": ["ER2", "BA8", "BA5", "BA1", "MUSAR", "AFA", "UAL", "CA", "AT1", "ER3", "CFMTFA", "DGMFA",
                   "CT", "BA6", "CTSFA", "BA11", "ER1"],
    "Açores": ["BA4", "CZAA"],
    "Madeira": ["ER4", "AM3"]
}
regioes = ["Continente", "Açores", "Madeira"]
reset_regiao = "-- Escolha a Região --"
reset_tipo_aviso = "-- Escolha um tipo de aviso --"

#------------------------------------#
#-----Inicialização da Interface-----#
#------------------------------------#

root = tk.Tk()
root.title("Gestor de Avisos")
root.geometry("1000x975")# Dimensões da interface.
root.configure(bg="#f0f0f0")# Cor do fundo.
root.resizable(False, False) # Faz com que a interface tenha uma dimensão fixa.

campos_vars = {}

container_inicial = tk.Frame(root, bg="#f0f0f0")
container_inicial.place(relx=0.5, rely=0.5, anchor="center")
form_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)

#Input do logotipo do CIMFA.
top_frame = tk.Frame(container_inicial, bg="#f0f0f0")
top_frame.pack(pady=(0, 20))  # Espaçamento abaixo do logotipo

try:
    logo_img = ImageTk.PhotoImage(Image.open("Suporte/CIMFA.png").resize((300, 300)))
    tk.Label(top_frame, image=logo_img, bg="#f0f0f0").pack()
except Exception as e:
    print("Erro ao carregar logotipo:", e)
    pass

#Inserir direitos no fundo da interface#
label_direitos = tk.Text(root, height=1, borderwidth=0, font=("Arial", 9), fg="gray", bg=root["bg"])
label_direitos.insert("1.0", "© 2025 CIMFA - SDP. Todos os direitos reservados.")

# Alinhamento ao centro
label_direitos.tag_configure("center", justify="center")
label_direitos.tag_add("center", "1.0", "end")

# Tornar o texto não editável
label_direitos.config(state="disabled")

# Expande e centraliza horizontalmente
label_direitos.pack(side="bottom", fill="x", pady=5)


# ------------------------------- #
# ----- Funções Utilitárias ----- #
# ------------------------------- #

#Função que permite abrir a tabela de conversão de unidades.#
def mostrar_tabela_vento():
    caminho_imagem = "Suporte/Tabela_Vento.png"  # Caminho da imagem
    if not os.path.exists(caminho_imagem):
        messagebox.showerror("Erro", "Imagem não encontrada.")
        return

    # Obter posição e dimensões da janela principal
    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()

    # Criação da nova janela
    img_tabela = tk.Toplevel()
    img_tabela.title("Tabela de conversão de kt para km/h.")

    # Define posição à direita da janela principal
    offset_x = root_x + root_width + 40  # 40px de espaçamento
    offset_y = root_y
    img_tabela.geometry(f"+{offset_x}+{offset_y}")

    try:
        img = Image.open(caminho_imagem)
        img_tk = ImageTk.PhotoImage(img)

        label_img = tk.Label(img_tabela, image=img_tk)
        label_img.image = img_tk  # evitar que a imagem seja apagada da memória
        label_img.pack(padx=10, pady=10)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir imagem: {e}")
        img_tabela.destroy()


#Função que cria o botão de ajuda, para aparecer o popup de ajuda ao preenchimento do aviso.#
def mostrar_popup_ajuda_bandeira(texto):
    popup = tk.Toplevel()
    popup.title("Exemplos de avisos")
    popup.geometry("570x200")
    label = tk.Label(popup, text=texto, wraplength=550, justify="left")
    label.pack(padx=10, pady=10)
    btn_fechar = tk.Button(popup, text="Fechar", command=popup.destroy)
    btn_fechar.pack(pady=10)

#Função que cria o botão de ajuda, para aparecer o popup de ajuda ao preenchimento do aviso.#
def mostrar_popup_ajuda_gravoso(texto):
    popup = tk.Toplevel()
    popup.title("Exemplos de avisos")
    popup.geometry("570x450")
    label = tk.Label(popup, text=texto, wraplength=550, justify="left")
    label.pack(padx=10, pady=10)
    btn_fechar = tk.Button(popup, text="Fechar", command=popup.destroy)
    btn_fechar.pack(pady=10)

#Popup de ajuda ao preenchimento do aviso.#
def mostrar_popup_instrucoes():
    popup = tk.Toplevel()
    popup.title("Instruções de preenchimento.")
    popup.geometry("600x200")
    label = tk.Label(popup, text=TEXTO_AJUDA_PREENCHIMENTO, wraplength=550, justify="center", anchor="center")
    label.pack(expand=True, fill='both', padx=10, pady=10)

#Função que limpa o formulário.#
def limpar_formulario():
    for w in form_frame.winfo_children():
        w.destroy()
    campos_vars.clear()

def criar_menu_inicial():
    # Limpa tudo dentro do container_inicial
    for widget in container_inicial.winfo_children():
        widget.destroy()

    logo_frame = tk.Frame(container_inicial, bg="#f0f0f0")
    logo_frame.pack()

    try:
        logo_img = ImageTk.PhotoImage(Image.open("Suporte/CIMFA.png").resize((300, 300)))
        logo_label = tk.Label(logo_frame, image=logo_img, bg="#f0f0f0")
        logo_label.image = logo_img 
        logo_label.pack()
    except Exception as e:
        print("Erro ao carregar logotipo:", e)

    menu_frame = tk.Frame(container_inicial, bg="#f0f0f0")
    menu_frame.pack()
    
    btns = [
    ("Aviso de Bandeira", criar_formulario_aviso_bandeira, "#acacac"),
    ("Aviso de Tempo Gravoso", criar_formulario_gravoso, "#acacac"),
    ("Aviso de Corrente de Jato", criar_formulario_aviso_corrente_jato, "#acacac"),
    ("Arquivo de Avisos", mostrar_avisos_por_data_com_menu,"#acacac"),
    ("Instruções de preenchimento", mostrar_popup_instrucoes,"#acacac")
    ]

    tk.Label(menu_frame, text="Escolha o tipo de aviso:", font=("Arial", 13), bg="#f0f0f0").pack(pady=10)
    for texto, comando, cor in btns:
        tk.Button(menu_frame, text=texto, command=comando, font=("Verdana", 11, "bold"), bg=cor, fg="black", width=25).pack(pady=5)

    #Inserir direitos no fundo da interface#
    label_direitos = tk.Text(root, height=1, borderwidth=0, font=("Arial", 9), fg="gray", bg=root["bg"])
    label_direitos.insert("1.0", "© 2025 CIMFA - SDP. Todos os direitos reservados.")

    # Alinhamento ao centro
    label_direitos.tag_configure("center", justify="center")
    label_direitos.tag_add("center", "1.0", "end")

    # Expande e centraliza horizontalmente
    label_direitos.pack(side="bottom", fill="x", pady=5)

def voltar_menu():
    # Remove todo o conteúdo do root
    for widget in root.winfo_children():
        widget.destroy()

    # Recria container_inicial e form_frame
    global container_inicial, form_frame
    container_inicial = tk.Frame(root, bg="#f0f0f0")
    container_inicial.place(relx=0.5, rely=0.5, anchor="center")
    form_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
    criar_menu_inicial()


#Função que criar as checkboxes das unidades.#
def atualizar_unidades(regiao):
    u_frame = campos_vars.get("unidades_Frame")
    if not u_frame:
        return

    for w in u_frame.winfo_children():
        w.destroy()

    if regiao == reset_regiao:
        return

    tk.Label(u_frame, text="Unidades informadas:", bg="#f0f0f0",
             font=("Arial", 11), anchor="center").pack(pady=(0, 5))

    # Frame intermediário centralizado
    center_frame = tk.Frame(u_frame, bg="#f0f0f0")
    center_frame.pack(anchor="center")

    check_vars = []
    unidades = unidades_por_regiao.get(regiao, [])
    for idx, ub in enumerate(unidades):
        v = tk.IntVar()
        cb = tk.Checkbutton(center_frame, text=ub, variable=v, bg="#f0f0f0",font=("Arial", 10), anchor="w",width=8)
        row = idx // 9
        col = idx % 9
        cb.grid(row=row, column=col, padx=10, pady=4)
        check_vars.append((ub, v))

    campos_vars["Unidades informadas"] = check_vars

#Função que lê o ficheiro csv dos avisos e devolve o número do aviso a enviar.#
def obter_numero_aviso(ficheiro_csv):
    caminho = ficheiro_csv
    if not os.path.exists(caminho):
        return "1"
    with open(caminho, "r", encoding="utf-8") as f:
        linhas = list(csv.reader(f))
    return str(len(linhas) if linhas else 1)

#Função que permite acrescentar ao número do aviso a letra referente à região.
def atualizar_numero_aviso_com_regiao(regiao):
    if regiao == reset_regiao:
        campos_vars["Número"].set("")
        return

    letra = regiao[0].upper()  # primeira letra: C, A ou M
    numero_base = obter_numero_aviso(FICHEIROS_TIPOS["Aviso de Tempo Gravoso"])
    campos_vars["Número"].set(f"{numero_base}{letra}")


#Texto a aparecer nos menus Ajuda#
TEXTO_AJUDA_BANDEIRA = (
    "CA-CIMFA 13JUN2025, AVISO DE TEMPO GRAVOSO Nº 128/2025 Bandeira \n\n"
    "Válido das 12Z às 20Z de dia 14JUN \n"
    "UAL e CA:\n"
    "- Vento de norte, moderado, com rajadas superiores a 25 nós.\n"
)

TEXTO_AJUDA_GRAVOSO = (
    "CA-CIMFA 09JUN2025, AVISO DE TEMPO GRAVOSO Nº 126/2025 C \n\n"
    "Válido das 18Z às 21Z de 10JUN25\n"
    "BA8, BA5 ER2,ER3, CFMTFA:\n"
    "-Vento do quadrante sul, moderado, com rajadas que poderão atingir os 35 nós (65km/h).\n\n"

    "CA-CIMFA 07MAR24, AVISO DE TEMPO GRAVOSO Nº 55/2024 C\n"
    "Válido das 14Z às 20Z de 08MAR2024\n"
    "Todas as unidades do Continente:\n"
    "- Precipitação por vezes forte, com condições favoráveis à ocorrência de trovoada.\n"
    "- Vento do quadrante oeste, moderado a forte e com rajadas que podem atingir os 40 nós (74 km/h).\n\n"

    "CA-CIMFA 19ABR2025, AVISO DE TEMPO GRAVOSO Nº 106/2025 C\n"
    "Válido das 07Z às 22Z de dia 19ABR25\n"
    "ER2, BA8 e BA5:\n"
    "- Ocorrência de aguaceiros de chuva, que poderão ser pontualmente fortes, de granizo e acompanhados de trovoada até às 12Z;\n"
    "BA8:\n"
    "- Vento de noroeste, moderado a forte, com rajadas na ordem dos 40 nós.\n"
)

TEXTO_AJUDA_PREENCHIMENTO = (
    "\n Campo Data - DDMMMAA\n"
    "Campo Hora - HHMMZ\n"
    "Campos Data & Hora - DDMMMAA HHMMZ \n\n\n"

    "Abreviaturas dos meses (EM INGLÊS!) \n\n"
    "JAN / FEB / MAR / APR / MAY / JUN / JUL / AUG / SEP / OCT / NOV / DEC \n"
)
# -------------------------------- # 
# ----- Funções de Submissão ----- #
# -------------------------------- #

#Função que valida se o campo Data do Aviso se encontra preenchido no formato correto.#
def validar_data_aviso(texto):
    try:
        return datetime.strptime(texto, "%d%b%y")
    except ValueError:
        return None

#Função que valida se os campo Data & Hora das validades se encontram preenchidos no formato correto.#
def validar_datetime(texto):
    if len(texto) != 13 or not texto.endswith("Z"):
        return None
    try:
        return datetime.strptime(texto[:12], "%d%b%y %H%M")
    except ValueError:
        return None

#Função que valida se os campos apenas com Hora se encontram preenchidos no formato correto (HHMMZ).#
def validar_hora(texto):
    # Tem de ter exatamente 5 caracteres (HHMMZ)
    if len(texto) != 5 or not texto.endswith("Z"):
        return None
    try:
        # Só validar os primeiros 4 dígitos como hora/minuto
        return datetime.strptime(texto[:4], "%H%M")
    except ValueError:
        return None

#Função que força a que todos os campos sejam preenchidos em maiúsculas#
def forcar_maiusculas(event):
    valor = event.widget.get()
    event.widget.delete(0, tk.END)
    event.widget.insert(0, valor.upper())

#Função que permite acrescentar "FL" automaticamente#
def preencher_prefixo(event, prefixo):
    valor = event.widget.get()
    if valor and not valor.startswith(prefixo):
        event.widget.delete(0, tk.END)
        event.widget.insert(0, f"{prefixo}{valor}")

#Função que permite acrescentar "KT ou Z" automaticamente#
def preencher_sufixo(event, sufixo):
    valor = event.widget.get()
    if valor and not valor.endswith(sufixo):
        event.widget.delete(0, tk.END)
        event.widget.insert(0, f"{valor}{sufixo}")

#Função que permite selecionar 
def perguntar_tipo_aviso(parent):
    #Abre uma janela para escolher entre Novo ou Alteração
    win = tk.Toplevel(parent)
    win.title("Tipo de Aviso")
    win.grab_set()  # bloqueia interação com a janela principal

    tk.Label(win, text="Este aviso é novo ou estás a fazer uma alteração?", font=("Arial", 11)).pack(padx=20, pady=10)

    resposta = {"valor": None}

    def escolher(valor):
        resposta["valor"] = valor
        win.destroy()

    tk.Button(win, text="NOVO", width=15, command=lambda: escolher("Novo")).pack(pady=5)
    tk.Button(win, text="ALTERAÇÃO", width=15, command=lambda: escolher("Alteração")).pack(pady=5)

    win.wait_window()  # espera até a janela ser fechada
    return resposta["valor"]

#Função que permite guardar a informação no ficheiro .csv.#
def guardar_dados(campos, tipo, ficheiro):
    valores = []
    numero_aviso = campos_vars.get("Número").get()
    texto_preview = f"Número: {numero_aviso}\nTipo: {tipo}\n\n"

    for campo in campos:
        widget = campos_vars.get(campo)
        if campo == "Unidades informadas":
            sel = [ub for ub, var in widget if var.get() == 1]
            valor = " ".join(sel)
        elif isinstance(widget, tk.Text):
            valor = widget.get("1.0", tk.END).strip()
        else:
            valor = widget.get().strip()

        if campo == "Região" and valor == reset_regiao:
            valor = ""

        if not valor:
            messagebox.showwarning("Campos em branco", f"Por favor, preencha o campo '{campo}'.")
            return

        if campo in ["Data do Aviso"]:
            if not validar_data_aviso(valor):
                messagebox.showerror("Formato Inválido", f"O campo '{campo}' deve estar no formato DDMMMAA.\nExemplo: 16JUN25")
                return

        if campo in ["Hora do Aviso"]:
            if not validar_hora(valor):
                messagebox.showerror("Formato Inválido", f"O campo '{campo}' deve estar no formato HHMMZ.\nExemplo: 1200Z")
                return

        if campo in ["Data & Hora de início da validade", "Data & Hora de fim da validade"]:
            if not validar_datetime(valor):
                messagebox.showerror("Formato Inválido", f"O campo '{campo}' deve estar no formato DDMMMAA HHMMZ.\nExemplo: 16JUN25 1430Z")
                return

        valores.append(valor)
        texto_preview += f"{campo}: {valor}\n"

    confirmar = messagebox.askyesno("Confirmar Submissão", f"Pré-visualização do aviso:\n\n{texto_preview}\nDeseja confirmar?")
    
    if not confirmar:
        return

    tipo_submissao = perguntar_tipo_aviso(root)
    if not tipo_submissao:
        return  # utilizador fechou a janela sem escolher

    # Caminho para ficheiro das alterações
    pasta = os.path.dirname(ficheiro)

    if tipo == "Aviso de Bandeira":
        ficheiro_alteracoes = os.path.join(pasta, 'Alterações aos avisos_'+ano+'.csv')
        cabecalho = ["Número", "Tipo"] + campos
    else:
        ficheiro_alteracoes = os.path.join(pasta, 'Alterações aos avisos de corrente de jato_'+ano+'.csv')
        cabecalho = ["Número", "Tipo"] + campos


    #Se for alteração vai gravar versão antiga no ficheiro Alterações, antes de fazer overwrite no fiheiro de arquivo
    if tipo_submissao == "Alteração" and os.path.exists(ficheiro):
        with open(ficheiro, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter='*')
            linhas_existentes = list(reader)

        for linha in linhas_existentes[1:]:
            if linha[0] == numero_aviso:  # encontrou aviso original
                # Guardar no ficheiro Alterações
                existe = os.path.exists(ficheiro_alteracoes)
                with open(ficheiro_alteracoes, "a", newline="", encoding="utf-8") as f_alt:
                    writer = csv.writer(f_alt, delimiter='*')
                    if not existe:
                        writer.writerow(cabecalho)
                    writer.writerow(linha)  #grava os dados antigos
                break

    #caminho = os.path.join(DADOS_DIR, ficheiro)
    caminho=ficheiro
    linhas = []
    cabecalho = ["Número", "Tipo"] + campos
    aviso_existente = False

    # Lê o ficheiro (se existir) e atualiza a linha correspondente
    if os.path.exists(caminho):
        with open(caminho, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter='*')
            linhas = list(reader)

        for i, linha in enumerate(linhas[1:], start=1):
            if linha[0] == numero_aviso:
                linhas[i] = [numero_aviso, tipo] + valores
                aviso_existente = True
                break

    if not aviso_existente:
        linhas.append([numero_aviso, tipo] + valores)
        if not linhas or linhas[0] != cabecalho:
            linhas.insert(0, cabecalho)

    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter='*')
        writer.writerows(linhas)

    if tipo == "Aviso de Bandeira":# Atualiza Avisos a Enviar (.txt)
        caminho_txt = os.path.join("/home/cimfa/rfnunes/Teste_Avisos", "Avisos a enviar.txt")
        colunas_para_apresentar=["Data & Hora do Aviso", "Região", "Unidades informadas", "Data & Hora de início da validade", "Data & Hora de fim da validade", "Descritivo", "Iniciais"]

        with open(caminho_txt, "a", encoding="utf-8") as txt:
            txt.write("="*40 + "\n")
            txt.write(f"Aviso N.º: {numero_aviso} - CA/CIMFA\nTipo: {tipo}\n")
            for campo, valor in zip(campos, valores):
                if campo in colunas_para_apresentar:
                    txt.write(f"{campo}: {valor}\n")
            txt.write("\n")

    messagebox.showinfo("Sucesso", f"{tipo} guardado com êxito.")
    voltar_menu()

  
def guardar_dados_gravoso(campos, tipo, ficheiro):
    valores = []
    numero_aviso = campos_vars.get("Número").get()
    texto_preview = f"Número: {numero_aviso}\nTipo: {tipo}\n\n"

    for campo in campos:
        widget = campos_vars.get(campo)
        if campo == "Unidades informadas":
            sel = [ub for ub, var in widget if var.get() == 1]
            valor = " ".join(sel)
        elif isinstance(widget, tk.Text):
            valor = widget.get("1.0", tk.END).strip()
        else:
            valor = widget.get().strip()

        if campo == "Região" and valor == reset_regiao:
            valor = ""

        if not valor:
            messagebox.showwarning("Campos em branco", f"Por favor, preencha o campo '{campo}'.")
            return

        if campo in ["Data do Aviso"]:
            if not validar_data_aviso(valor):
                messagebox.showerror("Formato Inválido", f"O campo '{campo}' deve estar no formato DDMMMAA.\nExemplo: 16JUN25")
                return

        if campo in ["Hora do Aviso"]:
            if not validar_hora(valor):
                messagebox.showerror("Formato Inválido", f"O campo '{campo}' deve estar no formato HHMMZ.\nExemplo: 1200Z")
                return

        if campo in ["Data & Hora de início da validade", "Data & Hora de fim da validade"]:
            if not validar_datetime(valor):
                messagebox.showerror("Formato Inválido", f"O campo '{campo}' deve estar no formato DDMMMAA HHMMZ.\nExemplo: 16JUN25 1430Z")
                return

        valores.append(valor)
        texto_preview += f"{campo}: {valor}\n"

    confirmar = messagebox.askyesno("Confirmar Submissão", f"Pré-visualização do aviso:\n\n{texto_preview}\nDeseja confirmar?")
    if not confirmar:
        return

    tipo_submissao = perguntar_tipo_aviso(root)
    if not tipo_submissao:
        return  # utilizador fechou a janela sem escolher

    # Caminho para ficheiro das alterações
    pasta = os.path.dirname(ficheiro)

    ficheiro_alteracoes = os.path.join(pasta, 'Alterações aos avisos_'+ano+'.csv')
    cabecalho = ["Número", "Tipo"] + campos


    #Se for alteração vai gravar versão antiga no ficheiro Alterações, antes de fazer overwrite no fiheiro de arquivo
    if tipo_submissao == "Alteração" and os.path.exists(ficheiro):
        with open(ficheiro, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter='*')
            linhas_existentes = list(reader)

        for linha in linhas_existentes[1:]:
            if linha[0] == numero_aviso:  # encontrou aviso original
                # Guardar no ficheiro Alterações
                existe = os.path.exists(ficheiro_alteracoes)
                with open(ficheiro_alteracoes, "a", newline="", encoding="utf-8") as f_alt:
                    writer = csv.writer(f_alt, delimiter='*')
                    if not existe:
                        writer.writerow(cabecalho)
                    writer.writerow(linha)  # grava os dados antigos
                break

    caminho_principal=ficheiro    
    caminhos_csv = [caminho_principal, os.path.join("/home/cimfa/rfnunes/Teste_Avisos", "Avisos Em Vigor.csv")]
    cabecalho = ["Número", "Tipo"] + campos

    for caminho in caminhos_csv:
        linhas = []
        aviso_existente = False

        if os.path.exists(caminho):
            with open(caminho, newline="", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter='*')
                linhas = list(reader)

            for i, linha in enumerate(linhas[1:], start=1):
                if linha[0] == numero_aviso:
                    linhas[i] = [numero_aviso, tipo] + valores
                    aviso_existente = True
                    break

        if not aviso_existente:
            linhas.append([numero_aviso, tipo] + valores)
            if not linhas or linhas[0] != cabecalho:
                linhas.insert(0, cabecalho)

        with open(caminho, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter='*')
            writer.writerows(linhas)

    # Gravação adicional .txt
    caminho_txt = os.path.join("/home/cimfa/rfnunes/Teste_Avisos", "Avisos a enviar.txt")
    colunas_para_apresentar = ["Data & Hora do Aviso", "Região", "Unidades informadas", "Data & Hora de início da validade", "Data & Hora de fim da validade", "Descritivo"]

    with open(caminho_txt, "a", encoding="utf-8") as txt:
        txt.write("="*40 + "\n")
        txt.write(f"Aviso N.º: {numero_aviso} - CA/CIMFA\nTipo: {tipo}\n")
        for campo, valor in zip(campos, valores):
            if campo in colunas_para_apresentar:
                txt.write(f"{campo}: {valor}\n")
        txt.write("\n")

    messagebox.showinfo("Sucesso", f"{tipo} guardado com êxito.")
    voltar_menu()


def criar_selector_avisos(ficheiro, tipo_formulario):
    if not os.path.exists(ficheiro):
        messagebox.showerror("Erro", "O ficheiro não foi encontrado.")
        return

    # Lê os avisos
    with open(ficheiro, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter='*')
        # Filtra apenas avisos do tipo correto
        avisos = [row for row in reader if row.get("Tipo", "").strip() == tipo_formulario]

    if not avisos:
        messagebox.showinfo("Avisos", f"Não existem avisos arquivados do tipo '{tipo_formulario}'.")
        return

    # Janela para selecionar
    selector = Toplevel()
    selector.title("Selecionar Aviso")

    scrollbar = Scrollbar(selector)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = Listbox(selector, width=100, yscrollcommand=scrollbar.set)
    for aviso in avisos:
        num = aviso.get("Número", "Sem número")
        tipo = aviso.get("Tipo", "Sem tipo")
        
        if tipo_formulario == "Aviso de Corrente de Jato":
            regiao = "Continente"
        else:
            regiao = aviso.get("Região", "")
        data = aviso.get("Data do Aviso", "")
        listbox.insert(tk.END, f"{num} | {tipo} | {regiao} | {data}")
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    scrollbar.config(command=listbox.yview)

    def ao_selecionar():
        selecionado = listbox.curselection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Por favor, selecione um aviso.")
            return
        aviso_escolhido = avisos[selecionado[0]]
        carregar_dados_aviso(aviso_escolhido)
        selector.destroy()

    tk.Button(selector, text="Carregar Aviso", command=ao_selecionar).pack(pady=5)

def carregar_dados_aviso(aviso_dict):
    # 1. Primeiro definimos a região (isso chama atualizar_unidades e cria checkboxes)
    regiao = aviso_dict.get("Região", "").strip()
    if "Região" in campos_vars:
        campos_vars["Região"].set(regiao)
        atualizar_unidades(regiao)  # Garante que as checkboxes sejam criadas

    # 2. Agora carregamos os restantes campos
    for campo, widget in list(campos_vars.items()):
        if campo == "Região":
            continue

        valor = aviso_dict.get(campo, "").strip()

        if campo == "Unidades informadas":
            unidades = valor.split()
            if isinstance(widget, list):
                for ub, var in widget:
                    if ub in unidades:
                        var.set(1)
        elif isinstance(widget, tk.StringVar):
            widget.set(valor)
        elif isinstance(widget, tk.Text):
            widget.delete("1.0", tk.END)
            widget.insert("1.0", valor)

#-----------------------------------#
# ----- Funções de Formulário ----- #
#-----------------------------------#

#Função que cria o formulário para o aviso de bandeira.#
def criar_formulario_aviso_bandeira():
    limpar_formulario()
    container_inicial.pack_forget()
    form_frame.pack(fill="both", expand=True)

    tipo = "Aviso de Bandeira"
    ficheiro_csv = FICHEIROS_TIPOS[tipo]
    numero_aviso = obter_numero_aviso(ficheiro_csv)

    #Número do Aviso (read-only)
    num_frame = tk.Frame(form_frame, bg="#f0f0f0")
    num_frame.pack(pady=10)

    tk.Label(num_frame, text="Aviso de Bandeira", bg="#f0f0f0", font=("Arial", 13, "bold")).pack()
    tk.Label(num_frame, text="Número:", bg="#f0f0f0", font=("Arial", 12, "bold")).pack()
    num_aviso_var = tk.StringVar(value=numero_aviso)
    entry_num = tk.Entry(num_frame, textvariable=num_aviso_var, font=("Courier New", 11), state='readonly', justify='center')
    entry_num.pack(pady=5, ipadx=30)  
    campos_vars["Número"] = num_aviso_var

    for campo in CAMPOS_BANDEIRA:
        if "Data" in campo or "Hora" in campo or "Iniciais" in campo:
            tk.Label(form_frame, text=campo + ":", bg="#f0f0f0", font=("Arial", 11)).pack(fill="x", pady=2)
            var = tk.StringVar()
            entry = tk.Entry(form_frame, textvariable=var, font=("Courier New", 11))
            entry.pack(fill="x", pady=2)
            entry.bind("<FocusOut>", forcar_maiusculas)
            campos_vars[campo] = var
        else:
            if campo == "Descritivo":
                tk.Label(form_frame, text=campo + ":", bg="#f0f0f0", font=("Arial", 11)).pack(fill="x", pady=2)
                t = tk.Text(form_frame, height=7, font=("Courier New", 11))
                t.pack(fill="x", pady=2)
                campos_vars[campo] = t
            elif campo == "Região":
                tk.Label(form_frame, text=campo + ":", bg="#f0f0f0", font=("Arial", 11)).pack(fill="x", pady=2)
                var = tk.StringVar(value=reset_regiao)
                drop = tk.OptionMenu(form_frame, var, reset_regiao, *regioes, command=atualizar_unidades)
                drop.config(font=("Courier New", 11), bg="white")
                drop.pack(fill="x", pady=2)
                campos_vars[campo] = var

            elif campo == "Unidades informadas":
                unidades_frame = tk.Frame(form_frame, bg="#f0f0f0")
                unidades_frame.pack(fill="x", pady=2)
                campos_vars["unidades_Frame"] = unidades_frame
                atualizar_unidades(campos_vars["Região"].get())  # Inicializa com a região atual

            else:
                tk.Label(form_frame, text=campo + ":", bg="#f0f0f0", font=("Arial", 11)).pack(fill="x", pady=2)
                var = tk.StringVar()
                tk.Entry(form_frame, textvariable=var, font=("Courier New", 11)).pack(fill="x", pady=2)
                campos_vars[campo] = var

    tk.Button(form_frame, text="Submeter", command=lambda: guardar_dados(CAMPOS_BANDEIRA, "Aviso de Bandeira", FICHEIROS_TIPOS["Aviso de Bandeira"]), font=("Verdana", 10, "bold"), bg="#4CAF50", fg="white", width=20).pack(pady=(20, 5))
    tk.Button(form_frame, text="Voltar ao Menu", command=voltar_menu, font=("Verdana", 10, "bold"), bg="#cccccc", width=20).pack(pady=5)
    tk.Button(form_frame, text="Tabela - Nós para km/h", command=mostrar_tabela_vento, font=("Verdana", 10,"bold"), bg="#1976D2", fg="white",width=20).pack(pady=5)
    tk.Button(form_frame, text="Ajuda", command=lambda: mostrar_popup_ajuda_bandeira(TEXTO_AJUDA_BANDEIRA),font=("Verdana", 10,"bold"), width=20).pack(pady=5)
    tk.Button(form_frame, text="Carregar Aviso", command=lambda: criar_selector_avisos(ficheiro_csv, tipo), font=("Verdana", 10, "bold"), bg="#FFA000", fg="black", width=20).pack(pady=5)

#Função que cria o formulário para o aviso de tempo gravoso.#
def criar_formulario_gravoso():
    limpar_formulario()
    container_inicial.pack_forget()
    form_frame.pack(fill="both", expand=True)

    tipo = "Aviso de Tempo Gravoso"
    ficheiro_csv = FICHEIROS_TIPOS[tipo]
    numero_aviso = obter_numero_aviso(ficheiro_csv)

    num_frame = tk.Frame(form_frame, bg="#f0f0f0")
    num_frame.pack(pady=10)
    
    tk.Label(num_frame, text="Aviso de Tempo Gravoso", bg="#f0f0f0", font=("Arial", 13, "bold")).pack()
    tk.Label(num_frame, text="Número:", bg="#f0f0f0", font=("Arial", 12, "bold")).pack()
    num_aviso_var = tk.StringVar(value=numero_aviso)
    entry_num = tk.Entry(num_frame, textvariable=num_aviso_var, font=("Courier New", 11), state='readonly', justify='center')
    entry_num.pack(pady=5, ipadx=30)  # ipadx aumenta a largura interna
    campos_vars["Número"] = num_aviso_var

   
    for campo in CAMPOS_GRAVOSO:
        if "Data" in campo or "Hora" in campo or "Iniciais" in campo:
            tk.Label(form_frame, text=campo + ":", bg="#f0f0f0", font=("Arial", 11)).pack(fill="x", pady=2)
            var = tk.StringVar()
            entry = tk.Entry(form_frame, textvariable=var, font=("Courier New", 11))
            entry.pack(fill="x", pady=2)
            entry.bind("<FocusOut>", forcar_maiusculas)
            campos_vars[campo] = var
        else:
        
            if campo == "Descritivo":
                tk.Label(form_frame, text=campo + ":", bg="#f0f0f0", font=("Arial", 11)).pack(fill="x", pady=2)
                t = tk.Text(form_frame, height=7, font=("Courier New", 11))
                t.pack(fill="x", pady=2)
                campos_vars[campo] = t
            elif campo == "Região":
                tk.Label(form_frame, text=campo + ":", bg="#f0f0f0", font=("Arial", 11)).pack(fill="x", pady=2)
                var = tk.StringVar(value=reset_regiao)

                def on_regiao_selected(regiao):
                    atualizar_unidades(regiao)
                    #Vai identificar a região e dá input à função para adicionar a letra da região ao número do aviso.#
                    atualizar_numero_aviso_com_regiao(regiao)

                drop = tk.OptionMenu(form_frame, var, reset_regiao, *regioes, command=on_regiao_selected)
                drop.config(font=("Courier New", 11), bg="white", justify="center")
                drop.pack(fill="x", pady=2)
                campos_vars[campo] = var

            elif campo == "Unidades informadas":
                unidades_frame = tk.Frame(form_frame, bg="#f0f0f0")
                unidades_frame.pack(fill="x", pady=2)
                campos_vars["unidades_Frame"] = unidades_frame
            else:
                tk.Label(form_frame, text=campo + ":", bg="#f0f0f0", font=("Arial", 11)).pack(fill="x", pady=2)
                var = tk.StringVar()
                tk.Entry(form_frame, textvariable=var, font=("Courier New", 11)).pack(fill="x", pady=2)
                campos_vars[campo] = var

    tk.Button(form_frame, text="Submeter", command=lambda: guardar_dados_gravoso(CAMPOS_GRAVOSO, "Aviso de Tempo Gravoso", FICHEIROS_TIPOS["Aviso de Tempo Gravoso"]), font=("Verdana", 10, "bold"), bg="#4CAF50", fg="white", width=20).pack(pady=(20, 5))
    tk.Button(form_frame, text="Voltar ao Menu", command=voltar_menu, font=("Verdana", 10, "bold"), bg="#cccccc", width=20).pack(pady=5)
    tk.Button(form_frame, text="Tabela - Nós para km/h", command=mostrar_tabela_vento, font=("Verdana", 10, "bold"), bg="#1976D2", fg="white",width=20).pack(pady=5)
    tk.Button(form_frame, text="Ajuda", command=lambda: mostrar_popup_ajuda_gravoso(TEXTO_AJUDA_GRAVOSO), font=("Verdana", 10, "bold"), bg="#cccccc", width=20).pack(pady=5)
    tk.Button(form_frame, text="Carregar Aviso", command=lambda: criar_selector_avisos(ficheiro_csv, tipo), font=("Verdana", 10, "bold"), bg="#FFA000", fg="black",width=20).pack(pady=5)

#Função que cria o formulário para o aviso de corrente de jato.#
def criar_formulario_aviso_corrente_jato():
    global container_externo
    limpar_formulario()
    
    tipo = "Aviso de Corrente de Jato"
    ficheiro_csv = FICHEIROS_TIPOS[tipo]
    numero_aviso = obter_numero_aviso(ficheiro_csv)
    
    for widget in root.winfo_children():
        widget.pack_forget()
        widget.grid_forget()

    container_externo = tk.Frame(root, bg="#f0f0f0", width=800, height=600)
    container_externo.pack(fill="both", expand=True)
    container_externo.pack_propagate(False)

    form_frame = tk.Frame(container_externo, bg="#f0f0f0", padx=20, pady=20)
    form_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(form_frame, text="Aviso de Corrente de Jato", font=("Arial", 13, "bold"), bg="#f0f0f0").grid(row=0, column=0, columnspan=2, pady=(10, 5))

    # Número do aviso
    tk.Label(form_frame, text="Número:", bg="#f0f0f0", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    num_aviso_var = tk.StringVar(value=numero_aviso)

    entry_num = tk.Entry(form_frame, textvariable=num_aviso_var, font=("Courier New", 11), state='readonly', justify='center', width=30)
    entry_num.grid(row=1, column=1, sticky="w", padx=5, pady=5)
    campos_vars["Número"] = num_aviso_var

    
    # Campos
    row = 2
    for campo in CAMPOS_JATO:
        tk.Label(form_frame, text=campo + ":", bg="#f0f0f0", font=("Arial", 11)).grid(row=row, column=0, sticky="e", padx=5, pady=5)

        var = tk.StringVar()
        entry = tk.Entry(form_frame, textvariable=var, font=("Courier New", 11), width=30)
        entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)

        if any(x in campo.lower() for x in ["iniciais","direção","zona","data", "hora","entidade"]):
            entry.bind("<FocusOut>", forcar_maiusculas)

        if any(x in campo for x in ["hora"]):
            entry.bind("<FocusOut>", forcar_maiusculas)
              
        if "FL" in campo:
            entry.bind("<FocusOut>", lambda e, p="FL": preencher_prefixo(e, p))
        elif "Int.Máx (KT)" in campo:
            entry.bind("<FocusOut>", lambda e, s="KT": preencher_sufixo(e, s))

        entry.bind("<FocusIn>", lambda e: e.widget.icursor(tk.END))

        campos_vars[campo] = var
        row += 1

   # Botões
    tk.Button(form_frame, text="Submeter", command=lambda: guardar_dados(CAMPOS_JATO, tipo, ficheiro_csv), font=("Verdana", 10, "bold"), bg="#4CAF50", fg="white", width=20).grid(row=row, column=0, columnspan=2, pady=(20, 5))
    tk.Button(form_frame, text="Voltar ao Menu", command=voltar_menu, font=("Verdana", 10,"bold"), bg="#cccccc",width=20).grid(row=row+1, column=0, columnspan=2, pady=5)
    tk.Button(form_frame, text="Carregar Aviso", command=lambda: criar_selector_avisos(ficheiro_csv, tipo), font=("Verdana", 10,"bold"), bg="#FFA000", fg="black",width=20).grid(row=row+2, column=0, columnspan=2, pady=5)
  

#-------------------------------#
# ----- Arquivo de Avisos ----- #
#-------------------------------#

# Função que permite consultar o arquivo de avisos, através do input de datas pelo utilizador.
def mostrar_avisos_por_data_com_menu(coluna_data="Data do Aviso", formato_data="%d%b%y"):
    janela_tipo = tk.Toplevel(root)
    janela_tipo.title("Selecionar Tipo de Aviso")
    janela_tipo.geometry("300x150")
    janela_tipo.resizable(False, False)

    tk.Label(janela_tipo, text="Seleciona o tipo de aviso:", font=("Arial", 11)).pack(pady=10)

    tipo_var = tk.StringVar()
    tipo_var.set(reset_tipo_aviso)  # Seleção por defeito

    menu_tipos = tk.OptionMenu(janela_tipo, tipo_var, *TIPOS_AVISO)
    menu_tipos.pack(pady=5)

    def confirmar_tipo():
        tipo_escolhido = tipo_var.get()
        janela_tipo.destroy()
        selecionar_ano(tipo_escolhido)

    tk.Button(janela_tipo, text="Confirmar", command=confirmar_tipo).pack(pady=10)


    def selecionar_ano(tipo_escolhido):
        janela_ano = tk.Toplevel(root)
        janela_ano.title("Selecionar Ano do Aviso")
        janela_ano.geometry("300x150")
        janela_ano.resizable(False, False)

        tk.Label(janela_ano, text=f"Seleciona o ano:", font=("Arial", 11)).pack(pady=10)

        anos_disponiveis = []

        for pasta in os.listdir(DADOS_DIR):
            subpasta = os.path.join(DADOS_DIR, pasta)
            if os.path.isdir(subpasta) and pasta.isdigit():

                if tipo_escolhido in ["Aviso de Bandeira", "Aviso de Tempo Gravoso"]:
                    ficheiros_csv = glob.glob(os.path.join(subpasta, "avisos_*.csv"))

                elif tipo_escolhido == "Aviso de Corrente de Jato":
                    ficheiros_csv = glob.glob(os.path.join(subpasta, "jetstream*.csv"))

                else:
                    ficheiros_csv = []

                if ficheiros_csv:
                    anos_disponiveis.append(pasta)

        anos_disponiveis = sorted(anos_disponiveis)

        if not anos_disponiveis:
            tk.Label(janela_ano, text="Nenhum ano disponível.", font=("Arial", 10, "italic")).pack(pady=20)
            return

        ano_var = tk.StringVar()
        ano_var.set(anos_disponiveis[-1])  # Presente ano aparece selecionado por defeito.

        menu_anos = tk.OptionMenu(janela_ano, ano_var, *anos_disponiveis)
        menu_anos.pack(pady=5)

        def confirmar_ano():
            ano_escolhido = ano_var.get()
            janela_ano.destroy()
            mostrar_avisos_por_data(ano_escolhido, tipo_escolhido, coluna_data, formato_data)

        tk.Button(janela_ano, text="Confirmar", command=confirmar_ano).pack(pady=10)

    def mostrar_avisos_por_data(ano, tipo_escolhido, coluna_data="Data do Aviso", formato_data="%d%b%y"):
        subpasta_ano = os.path.join(DADOS_DIR, ano)

        # --- Funções auxiliares ---
        def forcar_maiusculas(event):
            valor = event.widget.get()
            event.widget.delete(0, tk.END)
            event.widget.insert(0, valor.upper())

        def pedir_data_personalizada(prompt, root, formato_data="%d%b%y"):
            resultado = tk.StringVar()
            concluido = tk.BooleanVar(value=False)

            janela = tk.Toplevel(root)
            janela.title("Introduzir Data")
            janela.geometry("+{}+{}".format(root.winfo_rootx() + root.winfo_width() // 2 - 100, root.winfo_rooty() + 50))
            janela.resizable(False, False)

            tk.Label(janela, text=prompt + f" (DDMMMAA)", font=("Arial", 10)).pack(padx=10, pady=10)
            entry = tk.Entry(janela, textvariable=resultado, font=("Courier New", 11), width=20)
            entry.pack(pady=5)
            entry.focus()

            entry.bind("<KeyRelease>", forcar_maiusculas)

            def confirmar():
                concluido.set(True)
                janela.destroy()

            tk.Button(janela, text="OK", command=confirmar).pack(pady=(5, 10))
            janela.grab_set()
            janela.wait_variable(concluido)

            valor = resultado.get().strip().upper()
            if not valor:
                return None
            try:
                return datetime.strptime(valor, formato_data)
            except ValueError:
                messagebox.showerror("Erro", f"Formato inválido. Use DDMMMAA")
                return pedir_data_personalizada(prompt, root, formato_data)

        
        if tipo_escolhido in ["Aviso de Bandeira", "Aviso de Tempo Gravoso"]:
            ficheiros_csv = glob.glob(os.path.join(subpasta_ano, "avisos_*.csv"))

            
            # --- Input datas ---
            data_inicio = pedir_data_personalizada("Introduz a data inicial", root)
            if data_inicio is None:
                return

            data_fim = pedir_data_personalizada("Introduz a data final", root)
            if data_fim is None:
                return

            if data_fim == data_inicio:
                data_fim = data_fim + timedelta(days=1)

            if data_fim < data_inicio:
                messagebox.showerror("Erro", "A data final deve ser posterior ou igual à data inicial.")
                return

            # --- Ler e filtrar avisos ---
            avisos_filtrados = []
            for ficheiro_csv in ficheiros_csv:
                with open(ficheiro_csv, newline='', encoding='utf-8') as f:
                    leitor = csv.DictReader(f, delimiter='*')
                    for linha in leitor:
                        # Primeiro filtra pelo tipo escolhido
                        if linha.get("Tipo", "").strip() != tipo_escolhido:
                            continue
                         # Depois valida a data
                        data_aviso_str = linha.get(coluna_data, "").strip()
                        if not data_aviso_str:
                            continue
                        try:
                            data_aviso = datetime.strptime(data_aviso_str, formato_data)
                        except ValueError:
                            continue

                        if data_inicio <= data_aviso <= data_fim:
                            avisos_filtrados.append(linha)

            # --- Janela resultados ---
            janela_resultados = tk.Toplevel()
            janela_resultados.title(f"Avisos de {data_inicio.strftime(formato_data).upper()} a {data_fim.strftime(formato_data).upper()}")
            janela_resultados.geometry("1300x400")
            janela_resultados.resizable(True, True)

            frame_topo = tk.Frame(janela_resultados)
            frame_topo.pack(fill="x", pady=(5, 0))

            btn_imprimir = tk.Button(frame_topo, text="Gerar PDF", command=lambda: imprimir_resultado())
            btn_imprimir.pack(side="left", padx=10)

            if not avisos_filtrados:
                tk.Label(janela_resultados, text="Nenhum aviso encontrado nesse intervalo de datas.", font=("Arial", 11)).pack(pady=10)
                return

            #-----------------------#
            # Criar tabela Treeview #
            #-----------------------#

            # Define colunas a mostrar
            colunas_para_mostrar = [
                "Número",
                "Tipo",
                "Data do Aviso",
                "Hora do Aviso",
                "Região",
                "Unidades informadas",
                "Iniciais"
            ]
            # Cria a tabela apenas com essas colunas
            tabela = ttk.Treeview(janela_resultados, columns=colunas_para_mostrar, show="headings")

            # Largura personalizada para cada coluna
            larguras_colunas = {
                "Número": 15,
                "Tipo": 100,
                "Data do Aviso": 40,
                "Hora do Aviso": 40,
                "Região": 50,
                "Unidades informadas": 500,
                "Iniciais": 15
            }

            # Define cabeçalhos e larguras
            for col in colunas_para_mostrar:
                tabela.heading(col, text=col)
                largura = larguras_colunas.get(col, 100)
                tabela.column(col, anchor="center", width=largura)

            # Insere linhas
            for aviso in avisos_filtrados:
                valores = [aviso.get(col, "") for col in colunas_para_mostrar]  # <-- usa .get()
                tabela.insert("", "end", values=valores)

            # Scroll vertical
            scroll_y = ttk.Scrollbar(janela_resultados, orient="vertical", command=tabela.yview)
            tabela.configure(yscrollcommand=scroll_y.set)

            # Posicionamento
            tabela.pack(fill="both", expand=True, side="left")
            scroll_y.pack(fill="y", side="right")

        # Função para gerar e abrir uma pré-visualização (PDF) dos dados a mostrar em landscape. (Permite depois imprimir, fazer Save As,...).
            def imprimir_resultado():
                try:
                    # Obter colunas e dados da tabela.
                    colunas = tabela["columns"]
                    cabecalhos = [tabela.heading(col)["text"] for col in colunas]
                    dados = [tabela.item(item)["values"] for item in tabela.get_children()]

                    # Criar ficheiro PDF temporário
                    pdf_path = os.path.join(tempfile.gettempdir(), "Listagem de Avisos Emitidos.pdf")
                    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
                    largura_pagina, altura_pagina = landscape(A4)

                    # Inserir logotipo no canto superior esquerdo do pdf.
                    try:
                        imagem_path = "Suporte/CIMFA_sem_transparencia.png" # ReportLab (biblioteca usada para gerar PDFs) não lida nativamente com transparência (canal alpha) em imagens PNG.
                        logo = ImageReader(imagem_path)                     
                        c.drawImage(logo, x=1*cm, y=altura_pagina - 4*cm, width=3*cm, height=3*cm)
                    except Exception as e:
                        print(f"Erro ao carregar logotipo: {e}")

                    # Título
                    titulo = f"Avisos de {data_inicio.strftime('%d%b%Y').upper()} a {data_fim.strftime('%d%b%Y').upper()}"
                    y_titulo = altura_pagina - 3 * cm
                    c.setFont("Helvetica-Bold", 14)
                    c.drawCentredString(largura_pagina / 2, y_titulo, titulo)

                    # Layout
                    topo = altura_pagina - 5 * cm
                    margem_esquerda = 0.2 * cm
                    margem_direita = 0.2 * cm
                    linha_altura = 1 * cm

                    # Calcular larguras proporcionais
                    largura_total = largura_pagina - margem_esquerda - margem_direita
                    pesos = []
                   
                    # Dicionário de ponderações por cabeçalho. Para que as colunas não tenham todas a mesma largura.
                    ponderacoes = {
                        "Número": 0.5,
                        "Tipo": 1,
                        "Data do Aviso": 0.9,
                        "Hora do Aviso": 0.9,
                        "Região": 0.7,
                        "Unidades informadas": 3.5,
                        "Iniciais":0.4,
                    }

                    # Calcular os pesos com base nos cabeçalhos
                    pesos = []
                    for cab in cabecalhos:
                        peso = ponderacoes.get(cab.strip(), 0.7)  # valor padrão para colunas não listadas
                        pesos.append(peso)

                                 
                    soma_pesos = sum(pesos)
                    largura_base = largura_total / soma_pesos
                    larguras = [largura_base * peso for peso in pesos]

                    # Cabeçalhos
                    y = topo
                    c.setFont("Helvetica-Bold", 12)
                    x = margem_esquerda
                    for i, cab in enumerate(cabecalhos):
                        largura = larguras[i]
                        c.drawCentredString(x + largura / 2, y, str(cab))
                        x += largura

                    # Dados
                    y -= 1.2 * cm
                    c.setFont("Helvetica", 10)
                    for linha in dados:
                        x = margem_esquerda
                        for i, valor in enumerate(linha):
                            largura = larguras[i]
                            c.drawCentredString(x + largura / 2, y, str(valor))
                            x += largura
                        y -= linha_altura
                        if y < 2 * cm:
                            c.showPage()
                            y = altura_pagina - 3 * cm

                            # Redesenhar título e cabeçalhos
                            c.setFont("Helvetica-Bold", 14)
                            c.drawCentredString(largura_pagina / 2, altura_pagina - 1.5 * cm, titulo)
                            c.setFont("Helvetica-Bold", 10)
                            y = altura_pagina - 3 * cm
                            x = margem_esquerda
                            for i, cab in enumerate(cabecalhos):
                                largura = larguras[i]
                                c.drawCentredString(x + largura / 2, y, str(cab))
                                x += largura
                            y -= 1.2 * cm
                            c.setFont("Helvetica", 9)

                    c.save()
                    webbrowser.open(f"file://{os.path.abspath(pdf_path)}")

                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao imprimir resultado:\n{e}")

        elif tipo_escolhido == "Aviso de Corrente de Jato":
            ficheiros_csv = glob.glob(os.path.join(subpasta_ano, "jetstream_*.csv"))

            # --- Input datas ---
            data_inicio = pedir_data_personalizada("Introduz a data inicial", root)
            if data_inicio is None:
                return

            data_fim = pedir_data_personalizada("Introduz a data final", root)
            if data_fim is None:
                return

            if data_fim == data_inicio:
                data_fim = data_fim + timedelta(days=1)

            if data_fim < data_inicio:
                messagebox.showerror("Erro", "A data final deve ser posterior ou igual à data inicial.")
                return

            # --- Ler e filtrar avisos ---
            avisos_filtrados = []
            for ficheiro_csv in ficheiros_csv:
                with open(ficheiro_csv, newline='', encoding='utf-8') as f:
                    leitor = csv.DictReader(f, delimiter='*')
                    for linha in leitor:
                        data_aviso_str = linha.get(coluna_data, "").strip()
                        if not data_aviso_str:
                            continue
                        try:
                            data_aviso = datetime.strptime(data_aviso_str, formato_data)
                        except ValueError:
                            continue
                        if data_inicio <= data_aviso <= data_fim:
                            avisos_filtrados.append(linha)

            # --- Janela resultados ---
            janela_resultados = tk.Toplevel()
            janela_resultados.title(f"Avisos de {data_inicio.strftime(formato_data).upper()} a {data_fim.strftime(formato_data).upper()}")
            janela_resultados.geometry("1700x400")
            janela_resultados.resizable(False, False)

            frame_topo = tk.Frame(janela_resultados)
            frame_topo.pack(fill="x", pady=(5, 0))

            btn_imprimir = tk.Button(frame_topo, text="Gerar PDF", command=lambda: imprimir_resultado())
            btn_imprimir.pack(side="left", padx=10)

            if not avisos_filtrados:
                tk.Label(janela_resultados, text="Nenhum aviso encontrado nesse intervalo de datas.", font=("Arial", 11)).pack(pady=10)
                return

            #-----------------------#
            # Criar tabela Treeview #
            #-----------------------#

            # Define colunas a mostrar
            colunas_para_mostrar = [
                "Número",
                "Tipo",
                "Data do Aviso",
                "Hora do Aviso",
                "Data & Hora de início da validade",
                "Direção",
                "FL Base",
                "FL Topo",
                "Iniciais"
            ]
            # Cria a tabela apenas com essas colunas
            tabela = ttk.Treeview(janela_resultados, columns=colunas_para_mostrar, show="headings")

            # Largura personalizada para cada coluna
            larguras_colunas = {
                "Número": 5,
                "Tipo": 15,
                "Data do Aviso": 5,
                "Hora do Aviso": 5,
                "Data & Hora de início da validade":15,
                "Direção": 5,
                "FL Base": 5,
                "FL Topo": 5,
                "Iniciais": 5
            }

            # Define cabeçalhos e larguras
            for col in colunas_para_mostrar:
                tabela.heading(col, text=col)
                largura = larguras_colunas.get(col, 100)
                tabela.column(col, anchor="center", width=largura)

            # Insere linhas
            for aviso in avisos_filtrados:
                valores = [aviso.get(col, "") for col in colunas_para_mostrar]
                tabela.insert("", "end", values=valores)

            # Scroll vertical
            scroll_y = ttk.Scrollbar(janela_resultados, orient="vertical", command=tabela.yview)
            tabela.configure(yscrollcommand=scroll_y.set)

            # Posicionamento
            tabela.pack(fill="both", expand=True, side="left")
            scroll_y.pack(fill="y", side="right")

        # Função para gerar e abrir uma pré-visualização (PDF) dos dados a mostrar em landscape. (Permite depois imprimir, fazer Save As,...).
            def imprimir_resultado():
                try:
                    # Obter colunas e dados da tabela.
                    colunas = tabela["columns"]
                    cabecalhos = [tabela.heading(col)["text"] for col in colunas]
                    dados = [tabela.item(item)["values"] for item in tabela.get_children()]

                    # Criar ficheiro PDF temporário
                    pdf_path = os.path.join(tempfile.gettempdir(), "Listagem de Avisos Emitidos.pdf")
                    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
                    largura_pagina, altura_pagina = landscape(A4)

                    # Inserir logotipo no canto superior esquerdo do pdf.
                    try:
                        imagem_path = "Suporte/CIMFA_sem_transparencia.png" # ReportLab (biblioteca usada para gerar PDFs) não lida nativamente com transparência (canal alpha) em imagens PNG.
                        logo = ImageReader(imagem_path)                     
                        c.drawImage(logo, x=1*cm, y=altura_pagina - 4*cm, width=3*cm, height=3*cm)
                    except Exception as e:
                        print(f"Erro ao carregar logotipo: {e}")

                    # Título
                    titulo = f"Avisos de {data_inicio.strftime('%d%b%Y').upper()} a {data_fim.strftime('%d%b%Y').upper()}"
                    y_titulo = altura_pagina - 3 * cm
                    c.setFont("Helvetica-Bold", 14)
                    c.drawCentredString(largura_pagina / 2, y_titulo, titulo)

                    # Layout
                    topo = altura_pagina - 5 * cm
                    margem_esquerda = 0.2 * cm
                    margem_direita = 0.2 * cm
                    linha_altura = 1 * cm

                    # Calcular larguras proporcionais
                    largura_total = largura_pagina - margem_esquerda - margem_direita
                    pesos = []
                   
                    # Dicionário de ponderações por cabeçalho. Para que as colunas não tenham todas a mesma largura.
                    ponderacoes = {
                        "Número": 0.2,
                        "Tipo": 0.5,
                        "Data do Aviso": 0.3,
                        "Hora do Aviso": 0.3,
                        "Data & Hora de início da validade": 0.7,
                        "Direção": 0.2,
                        "FL Base": 0.2,
                        "FL Topo": 0.2,
                        "Iniciais": 0.2
                    }

                    # Calcular os pesos com base nos cabeçalhos
                    pesos = []
                    for cab in cabecalhos:
                        peso = ponderacoes.get(cab.strip(), 0.7)  # valor padrão para colunas não listadas
                        pesos.append(peso)

                                 
                    soma_pesos = sum(pesos)
                    largura_base = largura_total / soma_pesos
                    larguras = [largura_base * peso for peso in pesos]

                    # Cabeçalhos
                    y = topo
                    c.setFont("Helvetica-Bold", 12)
                    x = margem_esquerda
                    for i, cab in enumerate(cabecalhos):
                        largura = larguras[i]
                        c.drawCentredString(x + largura / 2, y, str(cab))
                        x += largura

                    # Dados
                    y -= 1.2 * cm
                    c.setFont("Helvetica", 10)
                    for linha in dados:
                        x = margem_esquerda
                        for i, valor in enumerate(linha):
                            largura = larguras[i]
                            c.drawCentredString(x + largura / 2, y, str(valor))
                            x += largura
                        y -= linha_altura
                        if y < 2 * cm:
                            c.showPage()
                            y = altura_pagina - 3 * cm

                            # Redesenhar título e cabeçalhos
                            c.setFont("Helvetica-Bold", 14)
                            c.drawCentredString(largura_pagina / 2, altura_pagina - 1.5 * cm, titulo)
                            c.setFont("Helvetica-Bold", 10)
                            y = altura_pagina - 3 * cm
                            x = margem_esquerda
                            for i, cab in enumerate(cabecalhos):
                                largura = larguras[i]
                                c.drawCentredString(x + largura / 2, y, str(cab))
                                x += largura
                            y -= 1.2 * cm
                            c.setFont("Helvetica", 9)

                    c.save()
                    webbrowser.open(f"file://{os.path.abspath(pdf_path)}")

                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao imprimir resultado:\n{e}")

#-------------------------------------#
# ----- Menu Inicial com Botões ----- #
#-------------------------------------#

menu_frame = tk.Frame(container_inicial, bg="#f0f0f0")
menu_frame.pack()
btns = [
    ("Aviso de Bandeira", criar_formulario_aviso_bandeira, "#acacac"),
    ("Aviso de Tempo Gravoso", criar_formulario_gravoso, "#acacac"),
    ("Aviso de Corrente de Jato", criar_formulario_aviso_corrente_jato, "#acacac"),
    ("Arquivo de Avisos", mostrar_avisos_por_data_com_menu,"#acacac"),
    ("Instruções de preenchimento", mostrar_popup_instrucoes,"#acacac")
    ]

tk.Label(menu_frame, text="Escolha o tipo de aviso:", font=("Arial", 13), bg="#f0f0f0").pack(pady=10)
for texto, comando, cor in btns:
    tk.Button(menu_frame, text=texto, command=comando, font=("Verdana", 11, "bold"), bg=cor, fg="black", width=25).pack(pady=5)

root.mainloop()
