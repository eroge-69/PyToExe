import PySimpleGUI as sg
import os
import subprocess
import configparser

# =============================
# Arquivo de configuração
# =============================
CONFIG_FILE = 'config.ini'
config = configparser.ConfigParser()

# Carrega configurações se existir
if os.path.exists(CONFIG_FILE):
    config.read(CONFIG_FILE)
    MAME_PATH = config.get('Paths', 'mame', fallback='')
    ROMS_PATH = config.get('Paths', 'roms', fallback='')
    SNAPS_PATH = config.get('Paths', 'snaps', fallback='')
else:
    MAME_PATH = ''
    ROMS_PATH = ''
    SNAPS_PATH = ''

# =============================
# Função para atualizar lista de jogos
# =============================
def update_games_list(path):
    games = []
    if os.path.isdir(path):
        for file in os.listdir(path):
            if file.lower().endswith('.zip'):
                games.append(file[:-4])
    return sorted(games)

# =============================
# Layout da janela
# =============================
layout = [
    [sg.Text('Executável do MAME:'), sg.Input(MAME_PATH, key='mame_path'), sg.FileBrowse(file_types=(("Executáveis", "*.exe"),))],
    [sg.Text('Pasta das ROMs:'), sg.Input(ROMS_PATH, key='roms_path'), sg.FolderBrowse()],
    [sg.Text('Pasta das Snaps:'), sg.Input(SNAPS_PATH, key='snaps_path'), sg.FolderBrowse()],
    [sg.HorizontalSeparator()],
    [sg.Listbox(values=update_games_list(ROMS_PATH), size=(30,20), key='games_list', enable_events=True), 
     sg.Image(key='snap_preview', size=(320,240))],
    [sg.Button('Rodar Jogo'), sg.Button('Sair')]
]

window = sg.Window('Front-End MAME Leve', layout, finalize=True)

# =============================
# Loop principal
# =============================
while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, 'Sair'):
        break

    # Atualiza lista de jogos ao mudar a pasta de ROMs
    if event == 'roms_path':
        games = update_games_list(values['roms_path'])
        window['games_list'].update(games)

    # Atualiza snap ao selecionar jogo
    if event == 'games_list' and values['games_list']:
        selected = values['games_list'][0]
        snap_folder = values['snaps_path']
        snap_path_png = os.path.join(snap_folder, selected + '.png')
        snap_path_jpg = os.path.join(snap_folder, selected + '.jpg')
        if os.path.exists(snap_path_png):
            window['snap_preview'].update(filename=snap_path_png)
        elif os.path.exists(snap_path_jpg):
            window['snap_preview'].update(filename=snap_path_jpg)
        else:
            window['snap_preview'].update(filename='')

    # Executa o jogo
    if event == 'Rodar Jogo' and values['games_list'] and values['mame_path']:
        selected_game = values['games_list'][0]
        mame_exe = values['mame_path']
        rom_folder = values['roms_path']
        subprocess.Popen([mame_exe, '-rompath', rom_folder, selected_game])

    # Salva configurações sempre que forem alteradas
    if event in ['mame_path','roms_path','snaps_path']:
        if not config.has_section('Paths'):
            config.add_section('Paths')
        config.set('Paths', 'mame', values['mame_path'])
        config.set('Paths', 'roms', values['roms_path'])
        config.set('Paths', 'snaps', values['snaps_path'])
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

window.close()

