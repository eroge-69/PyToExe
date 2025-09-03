import speech_recognition as sr
import os
import webbrowser
from win32 import win32api
from win32 import win32process
from win32 import win32gui
from tkinter import *
import ctypes
import winsound

MessageBox = ctypes.windll.user32.MessageBoxW

pckapat = 0

discord_startup = 'C://Users//%USERNAME%//AppData//Local//Discord//Update.exe --processStart Discord.exe'

r = sr.Recognizer()
m = sr.Microphone()

try:
    with m as source: r.adjust_for_ambient_noise(source)
    while True:
        print("Dinliyorum!")
        with m as source: audio = r.listen(source)
        print("Analiz ediyorum...")
        try:
            # Google'ın konuşma analizini türkçe olarak value değerine tanımlama
            value = r.recognize_google(audio, language='tr-TR')
            
            if 'araştırma yapmak istiyorum' in value:
                root=Tk()
                def araştırma():
                    inputValue=textBox.get("1.0","end-1c")
                    print('"' + inputValue + '" ' + "ile ilgili sonuçlar araştırılıyor..")
                    webbrowser.open_new_tab("https://www.google.com/search?q=" + inputValue)
                    inputValue = ""
                    root.destroy()
                textBox=Text(root, height=4, width=25)
                textBox.pack()
                buttonCommit=Button(root, height=1, width=20, text="Google'da araştır", command=araştırma)
                root.attributes('-topmost', True)
                root.geometry("+500+100")
                root.overrideredirect(True)
                buttonCommit.pack()
                mainloop()
            
            if 'kapat Bilgisayarı' in value:
                pckapat = 1
                MessageBox(None, 'Emin misin?', 'Sistem',0x30)
                
            if 'Evet' in value:
                if pckapat == 1:
                    os.system("shutdown /s /t 1")
                    
            if 'vazgeçtim' in value:
                if pckapat == 1:
                    pckapat = 0
                    print("İşlem iptal edildi!")
            
            if 'ders kurulumuna geç' in value:
                os.startfile('C://Users//Guldur//AppData//Roaming//Zoom//bin//Zoom.exe')
                webbrowser.open_new_tab("https://web.whatsapp.com")
                webbrowser.open_new_tab("http://www.youtube.com")
                          
            if 'başlangıç' in value:
                os.startfile('C://Users//Guldur//Desktop//Discord.lnk')
                os.startfile("C://Users//Guldur//AppData//Roaming//Spotify//Spotify.exe")
                webbrowser.open_new_tab("http://www.youtube.com")
                os.startfile('C://Users//Guldur//Documents//SonOyuncu Minecraft Client.exe')
                
            if 'projeyi kapat' in value:
                print('Uygulama kapatılıyor...')
                exit()
            
            if 'proje kapat' in value:
                print('Uygulama kapatılıyor...')
                exit()
            
            if 'proje bitir' in value:
                print('Uygulama kapatılıyor...')
                exit()

            if 'projeyi bitir' in value:
                print('Uygulama kapatılıyor...')
                exit()

            if "Spotify aç" in value:
                os.system("C://Users//%USERNAME%//AppData//Roaming//Spotify//Spotify.exe")

            if "Spotify kapat" in value:
                os.system("TASKKILL /F /IM spotify.exe")
                
            if "Spotify kapa" in value:
                os.system("TASKKILL /F /IM spotify.exe")
            
            if "Spotify kapağı" in value:
                os.system("TASKKILL /F /IM spotify.exe")

            if "discord'u aç" in value:
                os.system(discord_startup)
                
            if "discord aç" in value:
                os.system(discord_startup)
                
            if "discord gir" in value:
                os.system(discord_startup)
                
            if "discord'a gir" in value:
                os.system(discord_startup)
                
            if "discordu kapat" in value:
                os.system("TASKKILL /F /IM discord.exe")
                
            if "discord'u kapat" in value:
                os.system("TASKKILL /F /IM discord.exe")
                
            if "discord kapat" in value:
                os.system("TASKKILL /F /IM discord.exe")
                
            if "Google'ı aç" in value:
                os.startfile("brave.exe")
            
            if "Google aç" in value:
                os.startfile("brave.exe")
                
            if "Chrome aç" in value:
                os.startfile("brave.exe")
                
            if "Chrome'u aç" in value:
                os.startfile("brave.exe")
                
            if "Google'ı kapat" in value:
                os.system("TASKKILL /F /IM brave.exe")
            
            if "Google kapat" in value:
                os.system("TASKKILL /F /IM brave.exe")
                     
            if "YouTube aç" in value:
                webbrowser.open_new_tab("http://www.youtube.com")
                
            if "YouTube'a aç" in value:
                webbrowser.open_new_tab("http://www.youtube.com")
                
            if "YouTube'u aç" in value:
                webbrowser.open_new_tab("http://www.youtube.com")
                
            if "YouTube'a gir" in value:
                webbrowser.open_new_tab("http://www.youtube.com")
                
            if "YouTube'u çalıştır" in value:
                webbrowser.open_new_tab("http://www.youtube.com")
            
            if "YouTube'a çalıştır" in value:
                webbrowser.open_new_tab("http://www.youtube.com")
                
            if 'Tarayıcıyı kapat' in value:
                os.system("TASKKILL /F /IM brave.exe")
                
            if "YouTube'da bul" in value:
                valuee = value.replace("YouTube'da bul", "")
                webbrowser.open_new_tab("https://www.youtube.com/results?search_query=" + valuee)
            
            if 'Merhaba' in value:
                winsound.PlaySound('kayit.wav', winsound.SND_FILENAME)
            
            if str is bytes:
                print("- {}".format(value).encode("utf-8"))
            else:
                print("- {}".format(value))
        except sr.UnknownValueError:
            print("Olamaz! Anlayamadım, tekrarlar mısın?")
        except sr.RequestError as e:
            print("Olamaz! Google Speech servislerine ulaşılamıyor...; {0}".format(e))
except KeyboardInterrupt:
    pass
