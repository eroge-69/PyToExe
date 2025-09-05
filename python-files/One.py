
import pyttsx3
import speech_recognition as sr
import pickle
import os

# Inicializar voz
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def falar(texto):
    engine.say(texto)
    engine.runAndWait()

reconhecedor = sr.Recognizer()

def ouvir():
    with sr.Microphone() as source:
        print("Ouvindo...")
        audio = reconhecedor.listen(source)
        try:
            comando = reconhecedor.recognize_google(audio, language="pt-BR")
            print(f"Você disse: {comando}")
            return comando.lower()
        except:
            falar("Não entendi, repita por favor.")
            return ""

memoria_file = "memoria.pkl"
if os.path.exists(memoria_file):
    with open(memoria_file, "rb") as f:
        memoria = pickle.load(f)
else:
    memoria = {}

def aprender(pergunta, resposta):
    memoria[pergunta] = resposta
    with open(memoria_file, "wb") as f:
        pickle.dump(memoria, f)

falar("Olá, eu sou a IA One. Como posso te ajudar hoje?")
while True:
    comando = ouvir()
    if comando in ["sair", "fechar", "encerre"]:
        falar("Até mais!")
        break
    elif comando in memoria:
        falar(memoria[comando])
    else:
        falar("Não sei responder isso ainda. Qual seria a resposta certa?")
        resposta = ouvir()
        aprender(comando, resposta)
        falar("Aprendido!")
