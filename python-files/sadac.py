import customtkinter as ctk
from pygame import mixer
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import pygame

ctk.set_appearance_mode('dark')
mixer.init()
pygame.init()

def fechar():
    arboreio.destroy()

def mapasadc():
    arboreio.withdraw()
    mapa_sadac = ctk.CTkToplevel()
    mapa_sadac.title('Mapa Sadac')
    mapa_sadac.geometry('450x650')
    
    # Criar um frame principal para organizar melhor
    principal = ctk.CTkFrame(mapa_sadac)
    principal.pack(fill="both", expand=True, padx=10, pady=10)

    # Carrega a imagem de fundo usando Pillow
    ar1 = Image.open(r"./alex/ar 2.png")
    ar1 = ar1.resize((550, 750), Image.Resampling.LANCZOS)
    # Tenta escurecer um pouco a imagem para o texto e botões se destacarem
    # enhancer = ImageEnhance.Brightness(ar1)
    # ar1 = enhancer.enhance(0.8) 
    background_image = ImageTk.PhotoImage(ar1)

    # Cria um CTkLabel para exibir a imagem de fundo
    background_label = ctk.CTkLabel(master=principal, image=background_image, text="")
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Armazenar a referência à imagem globalmente
    mapa_sadac.imagem_ref = None

    # Carregar a imagem MapaArboreio.jpeg
    caminho_imagem = r"./MapaArboreio.jpeg"
    
    # Frame para a imagem do mapa para melhor organização e fundo transparente
    frame_mapa = ctk.CTkFrame(master=principal, fg_color='transparent')
    frame_mapa.pack(pady=30)
    
    if os.path.exists(caminho_imagem):
        try:
            # Carregar a imagem com CTkImage
            mapa_sadac.imagem_ref = ctk.CTkImage(light_image=Image.open(caminho_imagem), dark_image=Image.open(caminho_imagem), size=(400, 282))
            
            # Criar um label com a imagem
            label_imagem = ctk.CTkLabel(master=frame_mapa, image=mapa_sadac.imagem_ref, text="")
            label_imagem.pack()
            
        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")
            erro_label = ctk.CTkLabel(master=frame_mapa, text=f"Erro ao carregar imagem\n{e}", font=('Times New Roman', 14))
            erro_label.pack(pady=10)
    else:
        print(f"Arquivo {caminho_imagem} não encontrado.")
        erro_label = ctk.CTkLabel(master=frame_mapa, text=f"Arquivo não encontrado: {caminho_imagem}", font=('Times New Roman', 14))
        erro_label.pack(pady=10)

    def voltar():
        if mixer.music.get_busy():
            mixer.music.stop() # Para a música ao voltar
        arboreio.deiconify() # exibe janela
        mapa_sadac.destroy()

    # Função genérica para tocar música
    def tocar_musica(numero_arvore, nome_arquivo):
        try:
            caminho_audio = os.path.join("alex", "audio", nome_arquivo)
            if not os.path.exists(caminho_audio):
                print(f"Arquivo de áudio não encontrado: {caminho_audio}")
                return
                
            if mixer.music.get_busy():
                mixer.music.stop()
                print(f"parando: {nome_arquivo}")

            else:
                mixer.music.load(caminho_audio)
                mixer.music.play()
                print(f"Tocando: {nome_arquivo}")
        except Exception as e:
            print(f"Erro ao reproduzir música {numero_arvore}: {e}")

    # Dicionário com as músicas
    musicas = {
        1: "1 - Pau-brasil.mp3",
        2: "2 - Jenipapo.mp3", 
        3: "3 - Abiu-roxo.mp3",
        4: "4 - Ingá-branco.mp3",
        5: "5 - Jamelão.mp3",
        6: "6 - Palmeira-imperial.mp3",
        7: "7 - Pau-ferro.mp3",
        8: "8 - Aldrago.mp3",
        9: "9 - Tataré.mp3",
        10: "10 - Munguba.mp3",
        11: "11 - Amoreira-negra.mp3",
        12: "12 - Mogno-africano.mp3",
        13: "13 - Jatobá.mp3",
        14: "14- Ipê-rosa.mp3",
        15: "15 - Mogno-brasileiro.mp3"
    }

    # Frame para os botões das árvores
    # Corrigido: Fundo transparente para o frame de botões
    frame_botoes = ctk.CTkFrame(principal, fg_color='transparent') 
    frame_botoes.pack(pady=10)

    # Criar botões dinamicamente
    botoes = []
    for i in range(1, 16):
        # Usar lambda com argumento padrão para capturar o valor correto
        comando = lambda num=i: tocar_musica(num, musicas[num])
        
        # Corrigido: Estilo e cor para os botões numerados
        botao = ctk.CTkButton(master=frame_botoes, text=str(i), width=30, height=30, 
                              font=('Times New Roman', 12, 'bold'), command=comando,
                              fg_color="#38761D", hover_color="#6AA84F", text_color="white") 
        botoes.append(botao)

    # Organizar botões em grid
    for i, botao in enumerate(botoes):
        linha = i // 5  # 5 botões por linha
        coluna = i % 5
        botao.grid(row=linha, column=coluna, padx=2, pady=2)

    # Botão de voltar
    # Corrigido: Estilo e cor para o botão de voltar
    retroceder = ctk.CTkButton(principal, text='← Voltar',  width=80, height=30, 
                               font=('Times New Roman', 16, 'bold'), command=voltar, 
                               fg_color="#38761D", hover_color="#6AA84F")
    retroceder.place(relx=0.5, rely=0.9, anchor="center")

    mapa_sadac.mainloop()

# --- Tela inicial responsiva ---

bg_path = r"./alex/ar 1.png"
if not os.path.exists(bg_path):
    raise FileNotFoundError(f"Imagem de fundo não encontrada: {bg_path}")

# Tamanho inicial fixo
initial_width = 450
initial_height = 650

bg_img_original = Image.open(bg_path)
bg_img = bg_img_original.resize((initial_width, initial_height), Image.LANCZOS)
bg_width, bg_height = bg_img.size

# --- DESENHA O TEXTO E BOTÕES NA IMAGEM ---
draw = ImageDraw.Draw(bg_img)
try:
    font_title = ImageFont.truetype("arialbd.ttf", int(bg_height*0.06))
    font_sub = ImageFont.truetype("arial.ttf", int(bg_height*0.03))
    font_btn = ImageFont.truetype("arialbd.ttf", int(bg_height*0.04))
except:
    font_title = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_btn = ImageFont.load_default()

title = "Bem vindo ao SADAC"
sub = "Sistema de AudioDescrição das Ârvores Ceturianas"

bbox_title = draw.textbbox((0, 0), title, font=font_title)
w_title = bbox_title[2] - bbox_title[0]
h_title = bbox_title[3] - bbox_title[1]

bbox_sub = draw.textbbox((0, 0), sub, font=font_sub)
w_sub = bbox_sub[2] - bbox_sub[0]
h_sub = bbox_sub[3] - bbox_sub[1]

x_title = (bg_width - w_title) // 2
x_sub = (bg_width - w_sub) // 2

draw.text((x_title+2, int(bg_height*0.05)+2), title, font=font_title, fill="black")
draw.text((x_title, int(bg_height*0.05)), title, font=font_title, fill="white")
draw.text((x_sub+1, int(bg_height*0.15)+1), sub, font=font_sub, fill="black")
draw.text((x_sub, int(bg_height*0.15)), sub, font=font_sub, fill="white")

# --- Desenha os botões na imagem ---
btn_mapa_text = "Mapa"
bbox_btn_mapa = draw.textbbox((0, 0), btn_mapa_text, font=font_btn)
btn_mapa_w = bbox_btn_mapa[2] - bbox_btn_mapa[0] + int(bg_width*0.05)
btn_mapa_h = bbox_btn_mapa[3] - bbox_btn_mapa[1] + int(bg_height*0.03)
btn_mapa_x = (bg_width - btn_mapa_w) // 2
btn_mapa_y = int(bg_height*0.25)

draw.rounded_rectangle(
    [btn_mapa_x, btn_mapa_y, btn_mapa_x + btn_mapa_w, btn_mapa_y + btn_mapa_h],
    radius=int(min(btn_mapa_w, btn_mapa_h)*0.3), fill="#38761D"
)
draw.text(
    (btn_mapa_x + (btn_mapa_w - (bbox_btn_mapa[2] - bbox_btn_mapa[0])) // 2,
     btn_mapa_y + (btn_mapa_h - (bbox_btn_mapa[3] - bbox_btn_mapa[1])) // 2),
    btn_mapa_text, font=font_btn, fill="white"
)

btn_sair_text = "Sair"
bbox_btn_sair = draw.textbbox((0, 0), btn_sair_text, font=font_btn)
btn_sair_w = bbox_btn_sair[2] - bbox_btn_sair[0] + int(bg_width*0.05)
btn_sair_h = bbox_btn_sair[3] - bbox_btn_sair[1] + int(bg_height*0.03)
btn_sair_x = (bg_width - btn_sair_w) // 2
btn_sair_y = int(bg_height * 0.85)

draw.rounded_rectangle(
    [btn_sair_x, btn_sair_y, btn_sair_x + btn_sair_w, btn_sair_y + btn_sair_h],
    radius=int(min(btn_sair_w, btn_sair_h)*0.3), fill="#38761D"
)
draw.text(
    (btn_sair_x + (btn_sair_w - (bbox_btn_sair[2] - bbox_btn_sair[0])) // 2,
     btn_sair_y + (btn_sair_h - (bbox_btn_sair[3] - bbox_btn_sair[1])) // 2),
    btn_sair_text, font=font_btn, fill="white"
)

btn_areas = {
    "mapa": (btn_mapa_x, btn_mapa_y, btn_mapa_x + btn_mapa_w, btn_mapa_y + btn_mapa_h),
    "sair": (btn_sair_x, btn_sair_y, btn_sair_x + btn_sair_w, btn_sair_y + btn_sair_h)
}

arboreio = ctk.CTk()
arboreio.title('Arboreio')
arboreio.geometry(f"{initial_width}x{initial_height}")  # Tamanho inicial fixo
arboreio.resizable(True, True)

frame_inicial = ctk.CTkFrame(arboreio, fg_color="transparent")
frame_inicial.pack(fill="both", expand=True)
frame_inicial.pack_propagate(False)

bg_img_tk = ImageTk.PhotoImage(bg_img)
background_label = ctk.CTkLabel(master=frame_inicial, image=bg_img_tk, text="", fg_color="transparent")
background_label.place(x=0, y=0, relwidth=1, relheight=1)

def on_click(event):
    x, y = event.x, event.y
    if btn_areas["mapa"][0] <= x <= btn_areas["mapa"][2] and btn_areas["mapa"][1] <= y <= btn_areas["mapa"][3]:
        mapasadc()
    elif btn_areas["sair"][0] <= x <= btn_areas["sair"][2] and btn_areas["sair"][1] <= y <= btn_areas["sair"][3]:
        fechar()

background_label.bind("<Button-1>", on_click)

def on_resize(event):
    # Usa o tamanho real da janela
    new_w = arboreio.winfo_width()
    new_h = arboreio.winfo_height()
    if new_w < 300 or new_h < 300:
        return
    img = bg_img_original.resize((new_w, new_h), Image.LANCZOS)
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arialbd.ttf", int(new_h*0.06))
        font_sub = ImageFont.truetype("arial.ttf", int(new_h*0.03))
        font_btn = ImageFont.truetype("arialbd.ttf", int(new_h*0.04))
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_btn = ImageFont.load_default()

    title = "Bem vindo ao SADAC"
    sub = "Sistema de AudioDescrição das Ârvores Ceturianas"

    bbox_title = draw.textbbox((0, 0), title, font=font_title)
    w_title = bbox_title[2] - bbox_title[0]
    h_title = bbox_title[3] - bbox_title[1]

    bbox_sub = draw.textbbox((0, 0), sub, font=font_sub)
    w_sub = bbox_sub[2] - bbox_sub[0]
    h_sub = bbox_sub[3] - bbox_sub[1]

    x_title = (new_w - w_title) // 2
    x_sub = (new_w - w_sub) // 2

    draw.text((x_title+2, int(new_h*0.05)+2), title, font=font_title, fill="black")
    draw.text((x_title, int(new_h*0.05)), title, font=font_title, fill="white")
    draw.text((x_sub+1, int(new_h*0.15)+1), sub, font=font_sub, fill="black")
    draw.text((x_sub, int(new_h*0.15)), sub, font=font_sub, fill="white")

    # Botão Mapa
    btn_mapa_text = "Mapa"
    bbox_btn_mapa = draw.textbbox((0, 0), btn_mapa_text, font=font_btn)
    btn_mapa_w = bbox_btn_mapa[2] - bbox_btn_mapa[0] + int(new_w*0.05)
    btn_mapa_h = bbox_btn_mapa[3] - bbox_btn_mapa[1] + int(new_h*0.03)
    btn_mapa_x = (new_w - btn_mapa_w) // 2
    btn_mapa_y = int(new_h*0.25)

    draw.rounded_rectangle(
        [btn_mapa_x, btn_mapa_y, btn_mapa_x + btn_mapa_w, btn_mapa_y + btn_mapa_h],
        radius=int(min(btn_mapa_w, btn_mapa_h)*0.3), fill="#38761D"
    )
    draw.text(
        (btn_mapa_x + (btn_mapa_w - (bbox_btn_mapa[2] - bbox_btn_mapa[0])) // 2,
         btn_mapa_y + (btn_mapa_h - (bbox_btn_mapa[3] - bbox_btn_mapa[1])) // 2),
        btn_mapa_text, font=font_btn, fill="white"
    )

    # Botão Sair
    btn_sair_text = "Sair"
    bbox_btn_sair = draw.textbbox((0, 0), btn_sair_text, font=font_btn)
    btn_sair_w = bbox_btn_sair[2] - bbox_btn_sair[0] + int(new_w*0.05)
    btn_sair_h = bbox_btn_sair[3] - bbox_btn_sair[1] + int(new_h*0.03)
    btn_sair_x = (new_w - btn_sair_w) // 2
    btn_sair_y = int(new_h * 0.85)

    draw.rounded_rectangle(
        [btn_sair_x, btn_sair_y, btn_sair_x + btn_sair_w, btn_sair_y + btn_sair_h],
        radius=int(min(btn_sair_w, btn_sair_h)*0.3), fill="#38761D"
    )
    draw.text(
        (btn_sair_x + (btn_sair_w - (bbox_btn_sair[2] - bbox_btn_sair[0])) // 2,
         btn_sair_y + (btn_sair_h - (bbox_btn_sair[3] - bbox_btn_sair[1])) // 2),
        btn_sair_text, font=font_btn, fill="white"
    )

    # Atualiza áreas dos botões
    btn_areas["mapa"] = (btn_mapa_x, btn_mapa_y, btn_mapa_x + btn_mapa_w, btn_mapa_y + btn_mapa_h)
    btn_areas["sair"] = (btn_sair_x, btn_sair_y, btn_sair_x + btn_sair_w, btn_sair_y + btn_sair_h)

    new_img_tk = ImageTk.PhotoImage(img)
    background_label.configure(image=new_img_tk)
    background_label.image = new_img_tk

    # Atualiza tamanho do frame e do label
    frame_inicial.configure(width=new_w, height=new_h)
    background_label.place(x=0, y=0, width=new_w, height=new_h)

arboreio.bind("<Configure>", on_resize)

arboreio._bg_img_ref = bg_img_tk

arboreio.mainloop()
