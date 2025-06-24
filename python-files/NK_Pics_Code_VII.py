import os
import threading
import time
import requests
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
import customtkinter as ctk
import tkinter.messagebox
import pandas as pd

REMOVE_BG_API_KEY = "k5oiytj1cGWyoES6mYJFT9B2"

# Carregar CSV no seu computador
df_carros = pd.read_csv(r"C:\Users\Cliente\Downloads\carapi-opendatafeed-sample\carapi-opendatafeed-sample.csv")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("NK Pics")
app.geometry("1000x700")


def buscar_imagens(query, quantidade=1):
    imagens = []
    url = f"https://www.google.com/search?q={query}&tbm=isch"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        resultados = soup.find_all("img")
        for img in resultados[1:quantidade + 1]:
            img_url = img.get("src")
            if img_url:
                imagens.append(img_url)
    except Exception as e:
        print(f"[ERRO] Falha na busca: {e}")
    return imagens


def baixar_imagem(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        print(f"[ERRO] Falha ao baixar imagem: {e}")
        return None


def remover_fundo(imagem):
    try:
        buffered = BytesIO()
        imagem.save(buffered, format="PNG")
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": buffered.getvalue()},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVE_BG_API_KEY},
            timeout=10
        )
        if response.status_code == requests.codes.ok:
            return Image.open(BytesIO(response.content)).convert("RGBA")
        else:
            print(f"[ERRO] remove.bg: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[ERRO] remove.bg falhou: {e}")
    return imagem


def redimensionar_com_transparencia(imagem, tamanho):
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.ANTIALIAS
    return imagem.resize(tamanho, resample)


def cortar_borda_transparente(imagem):
    bbox = imagem.getbbox()
    return imagem.crop(bbox) if bbox else imagem


def criar_arte(marca, modelo, ano, lado, tipo, categorias):
    pasta = f"ImagensGeradas/{marca}{modelo}{ano}_{int(time.time())}"
    os.makedirs(pasta, exist_ok=True)

    lado_texto = "frente" if lado == "Dianteiro" else "traseira"
    carro_urls = buscar_imagens(f"{modelo} {ano} {lado_texto}", 1)
    carro = baixar_imagem(carro_urls[0]) if carro_urls else None
    if carro:
        carro = remover_fundo(carro)
        carro = cortar_borda_transparente(carro)

    if tipo == "Rufato" and carro:
        largura, altura = carro.size
        carro = carro.crop((largura // 2, 0, largura, altura))

    pecas = []
    for cat in categorias:
        urls = buscar_imagens(f"{cat} {marca} {modelo} {ano}", 1)
        img = baixar_imagem(urls[0]) if urls else None
        if img:
            img = remover_fundo(img)
            img = cortar_borda_transparente(img)
            pecas.append(img)

    fundo = Image.new("RGBA", (1080, 1080), (255, 255, 255, 255))

    for idx, peca in enumerate(pecas, start=1):
        img_final = fundo.copy()

        if carro:
            carro_resized = redimensionar_com_transparencia(carro, (900, 400))
            pos_x = (1080 - carro_resized.width) // 2
            img_final.paste(carro_resized, (pos_x, 50), carro_resized)

        peca_resized = redimensionar_com_transparencia(peca, (700, 300))
        pos_x = (1080 - peca_resized.width) // 2
        img_final.paste(peca_resized, (pos_x, 600), peca_resized)

        img_final.save(f"{pasta}/{idx}_carro_peca_{marca}_{modelo}_{idx}.png")

    return pasta


def gerar():
    try:
        btn_gerar.configure(state="disabled")
        marca = marca_var.get()
        modelo = modelo_var.get()
        ano = ano_var.get()
        lado = lado_var.get()
        tipo = tipo_var.get()
        qtd = int(qtd_var.get())
        categorias = [campo.get() for campo in campos_pecas if campo.get().strip()]

        if len(categorias) != qtd:
            tkinter.messagebox.showerror("Erro", "Quantidade de peças não bate com os campos preenchidos.")
            return

        pasta = criar_arte(marca, modelo, ano, lado, tipo, categorias)
        tkinter.messagebox.showinfo("Sucesso", f"Imagens geradas em: {pasta}")
    except Exception as e:
        print(f"[ERRO] Falha: {e}")
        tkinter.messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
    finally:
        btn_gerar.configure(state="normal")


def gerar_thread():
    threading.Thread(target=gerar, daemon=True).start()


# Interface
frame = ctk.CTkFrame(app)
frame.pack(padx=20, pady=20, fill="both", expand=True)

marcas_unicas = sorted(df_carros['Make Name'].dropna().unique().tolist())
marca_var = ctk.StringVar()
modelo_var = ctk.StringVar()
ano_var = ctk.StringVar()

def atualizar_modelos(*args):
    marca = marca_var.get()
    modelos = df_carros[df_carros['Make Name'] == marca]['Model Name'].dropna().unique()
    modelos = sorted(modelos.tolist())
    if modelos:
        modelo_menu.configure(values=modelos)
        modelo_var.set(modelos[0])
    else:
        modelo_menu.configure(values=[])
        modelo_var.set("")
    atualizar_anos()

def atualizar_anos(*args):
    marca = marca_var.get()
    modelo = modelo_var.get()
    anos = df_carros[
        (df_carros['Make Name'] == marca) &
        (df_carros['Model Name'] == modelo)
    ]['Trim Year'].dropna().unique()
    anos = sorted(anos.tolist(), reverse=True)
    if anos:
        ano_menu.configure(values=[str(a) for a in anos])
        ano_var.set(str(anos[0]))
    else:
        ano_menu.configure(values=[])
        ano_var.set("")

marca_menu = ctk.CTkOptionMenu(frame, variable=marca_var, values=marcas_unicas, command=lambda _: atualizar_modelos())
marca_menu.pack(pady=5)

modelo_menu = ctk.CTkOptionMenu(frame, variable=modelo_var, values=[], command=lambda _: atualizar_anos())
modelo_menu.pack(pady=5)

ano_menu = ctk.CTkOptionMenu(frame, variable=ano_var, values=[])
ano_menu.pack(pady=5)

if marcas_unicas:
    marca_var.set(marcas_unicas[0])
    atualizar_modelos()

lado_var = ctk.StringVar(value="Dianteiro")
ctk.CTkOptionMenu(frame, variable=lado_var, values=["Dianteiro", "Traseiro"]).pack(pady=5)

qtd_var = ctk.StringVar(value="1")
ctk.CTkEntry(frame, textvariable=qtd_var, placeholder_text="Quantidade de Peças").pack(pady=5)

scroll_frame = ctk.CTkScrollableFrame(frame)
scroll_frame.pack(fill="both", expand=True, pady=5)
campos_pecas = []

def atualizar_campos(*args):
    for campo in campos_pecas:
        campo.destroy()
    campos_pecas.clear()
    try:
        quantidade = int(qtd_var.get())
        for _ in range(quantidade):
            campo = ctk.CTkEntry(scroll_frame, placeholder_text="Categoria da Peça")
            campo.pack(pady=2)
            campos_pecas.append(campo)
    except ValueError:
        pass

qtd_var.trace_add("write", atualizar_campos)

tipo_var = ctk.StringVar(value="Estoque")
ctk.CTkOptionMenu(frame, variable=tipo_var, values=["Estoque", "Rufato"]).pack(pady=5)

btn_gerar = ctk.CTkButton(frame, text="Gerar Imagens", command=gerar_thread)
btn_gerar.pack(pady=20)

ctk.CTkLabel(frame, text="Desenvolvido por Lucas Henrick").pack(side="bottom", pady=10)

app.mainloop()
