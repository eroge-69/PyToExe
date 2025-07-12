#!/usr/bin/env python
import subprocess
import time
import re

print(r"""
                                                                                                                                                
                    ________  ________  ________   ________  ________  ________  _____ ______   ________                                            
                   |\   __  \|\   __  \|\   ___  \|\   ___ \|\   ____\|\   __  \|\   _ \  _   \|\   __  \                                           
 ____________      \ \  \|\ /\ \  \|\  \ \  \\ \  \ \  \_|\ \ \  \___|\ \  \|\  \ \  \\\__\ \  \ \  \|\  \      ____________                        
|\____________\     \ \   __  \ \   __  \ \  \\ \  \ \  \ \\ \ \  \    \ \   __  \ \  \\|__| \  \ \   ____\    |\____________\                      
\|____________|      \ \  \|\  \ \  \ \  \ \  \\ \  \ \  \_\\ \ \  \____\ \  \ \  \ \  \    \ \  \ \  \___|    \|____________|                      
                      \ \_______\ \__\ \__\ \__\\ \__\ \_______\ \_______\ \__\ \__\ \__\    \ \__\ \__\                                            
                       \|_______|\|__|\|__|\|__| \|__|\|_______|\|_______|\|__|\|__|\|__|     \|__|\|__|                                            
                                                                                                                                                    
                                                                                                                                                    
                                                                                                                                                    
                    ________  ________  ___       __   ________   ___       ________  ________  ________  _______   ________                        
                   |\   ___ \|\   __  \|\  \     |\  \|\   ___  \|\  \     |\   __  \|\   __  \|\   ___ \|\  ___ \ |\   __  \                       
 ____________      \ \  \_|\ \ \  \|\  \ \  \    \ \  \ \  \\ \  \ \  \    \ \  \|\  \ \  \|\  \ \  \_|\ \ \   __/|\ \  \|\  \        ____________  
|\____________\     \ \  \ \\ \ \  \\\  \ \  \  __\ \  \ \  \\ \  \ \  \    \ \  \\\  \ \   __  \ \  \ \\ \ \  \_|/_\ \   _  _\      |\____________\
\|____________|      \ \  \_\\ \ \  \\\  \ \  \|\__\_\  \ \  \\ \  \ \  \____\ \  \\\  \ \  \ \  \ \  \_\\ \ \  \_|\ \ \  \\  \|     \|____________|
                      \ \_______\ \_______\ \____________\ \__\\ \__\ \_______\ \_______\ \__\ \__\ \_______\ \_______\ \__\\ _\                    
                       \|_______|\|_______|\|____________|\|__| \|__|\|_______|\|_______|\|__|\|__|\|_______|\|_______|\|__|\|__|                   
                                                                                                                 by Th3-H4ck-M4ck                                               
""")
intro = input('Willkommen beim Bandcamp-Downloader!\nBist du bereit, die absolute Dopeness in deinen virtuellen Händen zu halten? (j = Ja, n = Nein):')

save_path = 'C:\Users\Anwender\OneDrive\Desktop\ZenMaster3000Shit\BandcampDownloader\Bandcamp_Downloader\Downloads'

if intro == 'j':
    url = input("Enter the URL: ")
    while not re.match(r'(?P<url>https?://[^\s]+)', url):  ####funktioniert wunderbar
        print('Bitte Bandcamp_URL eingeben, du Dödel!')
        url = input("Enter the URL: ")
elif intro == 'n':
    print('Schade, dann bist du wohl ein Wack_Mc!')
    quit()

if intro == 'j' and re.match(r'(?P<url>https?://[^\s]+)', url):
    print('Dopeness wird Initialisiert...')
    time.sleep(1)
    print('Lade Dopeness herunter...')
    print('...')
    print('Zuviel Dopeness für meine Rechnerleistung...')
    time.sleep(1)
    print('...')
    time.sleep(1)

    bc_opts = [
        'bandcamp-dl',
        '--template', '%{artist}/%{album}/%{track} - %{title}',
        '--base-dir', save_path,
        url
    ]
    subprocess.run(bc_opts)

more_tracks = input('Möchtest du noch mehr Tracks herunterladen? (j = Ja, n = Nein): ')
if more_tracks == 'j':
    while True:
        url = input("Enter the URL: ")
        if re.match(r'(?P<url>https?://[^\s]+)', url):
            print('Lade Dopeness herunter...')
            bc_opts = [
                'bandcamp-dl',
                '--template', '%{artist}/%{album}/%{track} - %{title}',
                '--base-dir', save_path,
                url
            ]
            subprocess.run(bc_opts)
        else:
            print('Bitte Bandcamp_URL eingeben, du Dödel!')
        

