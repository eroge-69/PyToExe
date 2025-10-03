import os
import time
import threading
from dotenv import load_dotenv
from openai import OpenAI
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import speech_recognition as sr
import pyttsx3
import pyautogui
import subprocess

# -------------------------
# Config
# -------------------------
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY não encontrada no .env")

client = OpenAI(api_key=API_KEY)

pause_flag = threading.Event()
stop_flag = threading.Event()

# -------------------------
# Histórico de Conversa (MEMÓRIA)
# -------------------------
CHAT_HISTORY = [
    {
        "role": "system", 
        "content": (
            "Você é Jarvis, assistente virtual inspirado no Homem de Ferro. "
            "Personalidade formal, elegante, com sarcasmo sutil. "
            "Sempre se apresenta como Jarvis. Especialista em programação, gera código limpo e explicativo. "
            "Se gerar código, explique linha por linha. "
            "Sempre se refira ao usuário como 'senhor Pedro'."
        )
    }
]

# -------------------------
# TTS / Voz
# -------------------------
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Força usar Daniel (UK) se existir
selected_voice = None
for v in voices:
    if "daniel" in v.name.lower() or "uk" in v.id.lower():
        selected_voice = v
        break

# Se não achar Daniel UK, usa David
if not selected_voice:
    for v in voices:
        if "david" in v.name.lower():
            selected_voice = v
            break

if selected_voice:
    engine.setProperty('voice', selected_voice.id)

engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

ultima_resposta = ""  # para armazenar a última resposta do Jarvis

def falar(texto):
    def run_tts():
        engine.say(texto)
        engine.runAndWait()
    threading.Thread(target=run_tts, daemon=True).start()

def ouvir():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        append_chat("🎤 Jarvis ouvindo...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        texto = r.recognize_google(audio, language="pt-BR")
        append_chat(f"Você (voz): {texto}")
        return texto
    except sr.UnknownValueError:
        append_chat("❌ Não entendi, senhor Pedro. Pode repetir?")
        return ""
    except sr.RequestError as e:
        append_chat(f"❌ Erro no reconhecimento de voz: {e}")
        return ""

# -------------------------
# Função para abrir Chrome e pesquisar
# -------------------------
def abrir_chrome_e_pesquisar(query):
    subprocess.Popen("start chrome", shell=True)
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'l')
    pyautogui.write(f'{query}')
    pyautogui.press('enter')
    append_chat(f"🔍 Pesquisando no Google por: {query}")

# -------------------------
# Interface
# -------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Jarvis v2.0 🤖💻")
app.geometry("900x700")

# Topo
top_frame = ctk.CTkFrame(app)
top_frame.pack(fill="x", padx=12, pady=(12,6))

status_label = ctk.CTkLabel(top_frame, text="", anchor="w")
status_label.pack(side="left", padx=8)

btn_frame = ctk.CTkFrame(top_frame)
btn_frame.pack(side="right", padx=6)
pause_button = ctk.CTkButton(btn_frame, text="⏸ Pause", width=100)
stop_button = ctk.CTkButton(btn_frame, text="❌ Parar", width=100)
pause_button.pack(side="left", padx=6, pady=6)
stop_button.pack(side="left", padx=6, pady=6)

# Chat
chat_box = ctk.CTkTextbox(app, width=860, height=400, wrap="word", state="disabled", font=("Roboto", 12))
chat_box.pack(padx=12, pady=(6, 12))

# Área imagens
image_frame = ctk.CTkFrame(app, width=860, height=200)
image_frame.pack(padx=12, pady=(6,12))
image_label = ctk.CTkLabel(image_frame, text="(Imagens aparecerão aqui)")
image_label.pack()

# Entrada + enviar + voz + ler
bottom_frame = ctk.CTkFrame(app)
bottom_frame.pack(fill="x", padx=12, pady=(6,12))
entry = ctk.CTkEntry(bottom_frame, width=400, placeholder_text="Digite sua mensagem...")
entry.pack(side="left", padx=8, pady=8)
send_button = ctk.CTkButton(bottom_frame, text="Enviar", width=100)
send_button.pack(side="left", padx=(6,12), pady=8)
voice_button = ctk.CTkButton(bottom_frame, text="🎤 Falar", width=100)
voice_button.pack(side="left", padx=(6,12), pady=8)
read_button = ctk.CTkButton(bottom_frame, text="🔊 Ler Resposta", width=130)
read_button.pack(side="left", padx=(6,12), pady=8)

# -------------------------
# Funções utilitárias
# -------------------------
def append_chat(text):
    chat_box.configure(state="normal")
    chat_box.insert("end", text + "\n")
    chat_box.see("end")
    chat_box.configure(state="disabled")

def cursor_blinking(event_done):
    while not event_done.is_set():
        for i in range(4):
            if event_done.is_set(): break
            status_label.configure(text="Jarvis está digitando" + "."*i)
            time.sleep(0.5)
    status_label.configure(text="")

def type_with_animation(texto):
    global ultima_resposta
    ultima_resposta = texto
    append_chat("Jarvis: ")
    for letra in texto:
        if stop_flag.is_set():
            append_chat("\n--- resposta cancelada ---\n")
            return
        while pause_flag.is_set():
            time.sleep(0.1)
        chat_box.configure(state="normal")
        chat_box.insert("end", letra)
        chat_box.see("end")
        chat_box.configure(state="disabled")
        time.sleep(0.02)
    append_chat("\n")

# -------------------------
# IA - texto / códigos
# -------------------------
def ask_model(user_text):
    global CHAT_HISTORY 
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=CHAT_HISTORY, 
            max_tokens=800
        )
        assistant_response = resp.choices[0].message.content
        CHAT_HISTORY.append({"role": "assistant", "content": assistant_response})
        return assistant_response
    except Exception as e:
        return f"Erro: {e}"

# -------------------------
# IA - imagens
# -------------------------
def gerar_imagem(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3", 
            prompt=prompt,
            size="1024x1024"
        )
        url = response.data[0].url
        resp = requests.get(url)
        img = Image.open(BytesIO(resp.content))
        return img
    except Exception as e:
        append_chat(f"Erro ao gerar imagem: {e}")
        return None

# -------------------------
# Funções principais
# -------------------------
def enviar_handler(event=None):
    text = entry.get().strip()
    if not text: return
    entry.delete(0, "end")
    append_chat(f"Você: {text}")

    done_event = threading.Event()
    cursor_thread = threading.Thread(target=cursor_blinking, args=(done_event,), daemon=True)
    cursor_thread.start()

    def run():
        stop_flag.clear()
        global CHAT_HISTORY 
        
        should_ask_model = True

        if any(p in text.lower() for p in ["seu nome", "qual é o seu nome", "quem é você", "como você se chama"]):
            done_event.set()
            type_with_animation("Sou Jarvis, assistente pessoal do senhor Pedro. 🤖")
            should_ask_model = False 
        
        elif "pesquisar" in text.lower():
            termo = text.lower().split("pesquisar", 1)[1].strip()
            if termo:
                abrir_chrome_e_pesquisar(termo)
            else:
                append_chat("❌ Por favor, diga o que deseja pesquisar após 'pesquisar'.")
            done_event.set()
            should_ask_model = False 

        elif text.lower().startswith("gerar imagem"):
            prompt = text.replace("gerar imagem", "").strip()
            done_event.set()
            if not prompt:
                 append_chat("❌ Por favor, forneça um prompt após 'gerar imagem'.")
                 should_ask_model = False
            else:
                append_chat(f"🎨 Gerando imagem para: '{prompt}'...")
                img = gerar_imagem(prompt)
                if img:
                    img_tk = ImageTk.PhotoImage(img)
                    image_label.configure(image=img_tk, text="")
                    image_label.image = img_tk
                    append_chat("✅ Imagem gerada com sucesso!")
                should_ask_model = False 

        if should_ask_model:
            CHAT_HISTORY.append({"role": "user", "content": text})
            if len(CHAT_HISTORY) > 11: 
                 CHAT_HISTORY = [CHAT_HISTORY[0]] + CHAT_HISTORY[-10:] 
            answer = ask_model(text)
            done_event.set()
            type_with_animation(answer)

    threading.Thread(target=run, daemon=True).start()

def voz_handler():
    texto = ouvir()
    if texto:
        entry.delete(0, "end")
        entry.insert(0, texto)
        enviar_handler()

def ler_resposta_handler():
    global ultima_resposta
    if ultima_resposta:
        falar(ultima_resposta)
    else:
        append_chat("⚠ Nenhuma resposta disponível para ler.")

def pause_handler():
    if not pause_flag.is_set():
        pause_flag.set()
        pause_button.configure(text="▶ Continuar")
    else:
        pause_flag.clear()
        pause_button.configure(text="⏸ Pause")

def stop_handler():
    stop_flag.set()
    pause_flag.clear()
    pause_button.configure(text="⏸ Pause")
    status_label.configure(text="Resposta cancelada.")

# -------------------------
# Bindings
# -------------------------
send_button.configure(command=enviar_handler)
voice_button.configure(command=voz_handler)
read_button.configure(command=ler_resposta_handler)
pause_button.configure(command=pause_handler)
stop_button.configure(command=stop_handler)
app.bind("<Return>", enviar_handler)

# -------------------------
# Start
# -------------------------
append_chat("🤖 Jarvis v2.0 iniciado! Agora com voz Daniel UK (ou David).")
append_chat("💡 Dica: Use '🔊 Ler Resposta' para ouvir a resposta com voz britânica.")
app.mainloop()
