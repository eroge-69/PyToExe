from panda3d.core import loadPrcFileData, WindowProperties # type: ignore
from direct.showbase.ShowBase import ShowBase # type: ignore
from mainmenu import MainMenu # type: ignore
from settings import SettingsMenu # type: ignore
import os

# Kuvakkeen konvertointi PNG → ICO (vain ensimmäisellä käynnistyksellä)
try:
    from PIL import Image # type: ignore
    png_path = r"E:\jungle adventure\game\peli scriptit\images\jungle adventure logo.png"
    ico_path = r"E:\jungle adventure\game\peli scriptit\images\jungle adventure logo.ico"
    img = Image.open(png_path).convert("RGBA")
    img.save(ico_path, format='ICO', sizes=[(32, 32), (48, 48), (64, 64)])
except Exception as e:
    print(f"Kuvakkeen konvertointi epäonnistui: {e}")

# Panda3D-ikkunan asetukset
loadPrcFileData('', 'win-size 1920 1080')
loadPrcFileData('', 'window-title JungleAdventure')

try:
    from screeninfo import get_monitors # type: ignore
except ImportError:
    get_monitors = None

class MyApp(ShowBase):
    def __init__(self):
        super().__init__()

        # Tarkistetaan, että ICO-tiedosto löytyy ennen kuin asetetaan se ikonikuvaksi
        if os.path.exists(ico_path):
            props = WindowProperties()
            props.setIconFilename(ico_path)
            self.win.requestProperties(props)
            print(f"Ikkunan kuvake asetettu tiedostosta: {ico_path}")
        else:
            print(f"Varoitus: Ikonitiedostoa ei löydy polusta: {ico_path}")

        # Alustetaan asetukset suoraan ilman config-tiedostoa
        self.current_display = 0
        self.current_width = 1920
        self.current_height = 1080

        self.settings_menu = SettingsMenu(self)
        self.main_menu = MainMenu(self)

        self.show_main_menu()
        self.apply_window_changes()

    def apply_window_changes(self):
        if get_monitors:
            try:
                monitors = get_monitors()
                display = monitors[self.current_display]
                win_x = display.x + (display.width - self.current_width) // 2
                win_y = display.y + (display.height - self.current_height) // 2

                props = WindowProperties()
                props.setSize(self.current_width, self.current_height)
                props.setOrigin(win_x, win_y)
                props.setFullscreen(False)
                self.win.requestProperties(props)
            except Exception as e:
                print(f"Virhe asetettaessa ikkunan sijaintia: {e}")
        else:
            print("screeninfo ei ole saatavilla – käytetään oletusasetuksia.")

    def set_resolution(self, width, height):
        self.current_width = width
        self.current_height = height
        self.apply_window_changes()

    def set_display(self, display_index):
        self.current_display = display_index
        self.apply_window_changes()

    def show_main_menu(self):
        self.settings_menu.hide()
        self.main_menu.show()

    def show_settings(self):
        self.main_menu.hide()
        self.settings_menu.show()

    def start_game(self):
        print("Peli käynnistyy...")
        self.main_menu.hide()
        self.settings_menu.hide()

    def exit_game(self):
        print("Poistutaan pelistä...")
        self.userExit()

app = MyApp()
app.run()
