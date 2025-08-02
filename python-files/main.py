from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFlatButton
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.behaviors import HoverBehavior
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from pathlib import Path
import threading
import time
import webbrowser

try:
    import downloader
    DOWNLOADER_AVAILABLE = True
except ImportError:
    DOWNLOADER_AVAILABLE = False
    print("Warning: downloader.py not found. Some features will be disabled.")

CREDENTIALS_FILE = Path.home() / ".s1lly_downloader_credentials.txt"

def save_credentials(username, password):
    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            f.write(f"username={username}\n")
            f.write(f"password={password}\n")
        return True
    except Exception as e:
        print(f"Error saving credentials: {e}")
        return False

def load_credentials():
    try:
        if CREDENTIALS_FILE.exists():
            with open(CREDENTIALS_FILE, 'r') as f:
                lines = f.readlines()
                username = ""
                password = ""
                for line in lines:
                    if line.startswith("username="):
                        username = line.split("=", 1)[1].strip()
                    elif line.startswith("password="):
                        password = line.split("=", 1)[1].strip()
                return username, password
    except Exception as e:
        print(f"Error loading credentials: {e}")
    return "", ""

def get_installed_games(downloads_dir):
    installed_games = []
    try:
        if not downloads_dir.exists():
            return installed_games
        
        for folder in downloads_dir.iterdir():
            if folder.is_dir():
                exe_file = folder / "RainbowSix.exe"
                if exe_file.exists():
                    season_name = folder.name
                    if DOWNLOADER_AVAILABLE and hasattr(downloader, 'SEASONS'):
                        for season_key, (folder_name, _) in downloader.SEASONS.items():
                            if folder_name == folder.name:
                                season_name = season_key
                                break
                    
                    installed_games.append({
                        "title": season_name,
                        "folder": folder,
                        "path": str(folder),
                        "exe": str(exe_file)
                    })
    except Exception as e:
        print(f"Error scanning for installed games: {e}")
    
    return installed_games

def change_username_in_files(game_folder, new_username):
    success_count = 0
    config_files = ["CODEX.ini", "CPlay.ini"]
    
    for config_file in config_files:
        file_path = game_folder / config_file
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('Username =') or line.strip().startswith('Username='):
                        lines[i] = f'Username = {new_username}'
                        break
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                success_count += 1
            except Exception as e:
                print(f"Error updating {config_file}: {e}")
    
    return success_count

class FilterChip(MDRaisedButton):
    def __init__(self, text, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.size_hint = (None, None)
        self.height = dp(36)
        self.md_bg_color = "#343a40"
        self.theme_text_color = "Custom"
        self.text_color = "#adb5bd"
        self.callback = callback
        self.selected = False
        self.elevation = 2
        
        self.bind(on_release=self.toggle_selection)
    
    def toggle_selection(self, *args):
        self.selected = not self.selected
        if self.selected:
            self.md_bg_color = "#7c3aed"
            self.text_color = "#ffffff"
        else:
            self.md_bg_color = "#343a40"
            self.text_color = "#adb5bd"
        
        if self.callback:
            self.callback(self.text, self.selected)

class Tab(MDFloatLayout, MDTabsBase):
    pass

class GameCard(MDCard, HoverBehavior):
    def __init__(self, game_data, **kwargs):
        super().__init__(**kwargs)
        self.game_data = game_data
        self.md_bg_color = "#1e1e2e"
        self.radius = [15]
        self.elevation = 8
        self.size_hint_y = None
        self.height = dp(200)
        self.padding = dp(16)
        
        main_layout = MDBoxLayout(orientation="vertical", spacing=dp(8))
        
        header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        
        title_label = MDLabel(
            text=game_data["title"],
            theme_text_color="Custom",
            text_color="#e9ecef",
            font_style="H6",
            bold=True
        )
        
        year_label = MDLabel(
            text=game_data["year"],
            theme_text_color="Custom",
            text_color="#7c3aed",
            font_style="Subtitle2",
            size_hint_x=None,
            width=dp(60),
            halign="right"
        )
        
        header.add_widget(title_label)
        header.add_widget(year_label)
        
        info_layout = MDBoxLayout(orientation="horizontal", spacing=dp(16), size_hint_y=None, height=dp(30))
        
        size_label = MDLabel(
            text=f"Size: {game_data['size']}",
            theme_text_color="Custom",
            text_color="#adb5bd",
            font_style="Caption"
        )
        
        category_label = MDLabel(
            text=f"Season: {game_data['season']}",
            theme_text_color="Custom",
            text_color="#adb5bd",
            font_style="Caption"
        )
        
        info_layout.add_widget(size_label)
        info_layout.add_widget(category_label)
        
        desc_label = MDLabel(
            text=game_data["description"],
            theme_text_color="Custom",
            text_color="#ced4da",
            font_style="Body2",
            size_hint_y=None,
            height=dp(40)
        )
        
        self.progress_bar = MDProgressBar(
            size_hint_y=None,
            height=dp(6),
            color="#7c3aed",
            back_color="#343a40",
            opacity=0
        )
        
        self.download_btn = MDRaisedButton(
            text="DOWNLOAD",
            md_bg_color="#7c3aed",
            theme_text_color="Custom",
            text_color="#ffffff",
            size_hint=(None, None),
            height=dp(40),
            width=dp(120),
            pos_hint={"center_x": 0.5},
            on_release=self.start_download
        )
        
        main_layout.add_widget(header)
        main_layout.add_widget(info_layout)
        main_layout.add_widget(desc_label)
        main_layout.add_widget(self.progress_bar)
        main_layout.add_widget(self.download_btn)
        
        self.add_widget(main_layout)
    
    def start_download(self, *args):
        if not DOWNLOADER_AVAILABLE:
            self.show_error("Downloader not available - please ensure downloader.py is in the same folder")
            return
        
        app = MDApp.get_running_app()
        if not app.steam_username.strip():
            self.show_error("Please set your Steam username in Settings tab")
            return
        
        self.download_btn.text = "VALIDATING..."
        self.download_btn.disabled = True
        
        threading.Thread(target=self.download_season, daemon=True).start()
    
    def download_season(self):
        try:
            app = MDApp.get_running_app()
            username = app.steam_username.strip()
            password = app.steam_password.strip() if app.steam_password.strip() else None
            
            season_key = self.game_data["season_key"]
            
            if not hasattr(downloader, 'SEASONS') or season_key not in downloader.SEASONS:
                Clock.schedule_once(lambda dt: self.show_error(f"Season '{season_key}' not found in downloader"))
                return
            
            folder_name, depots = downloader.SEASONS[season_key]
            target = downloader.DOWNLOADS_DIR / folder_name
            
            Clock.schedule_once(lambda dt: self.start_progress())
            
            success = downloader.depot_download('359550', target, depots, username, password)
            
            if success:
                cracks_sub = self.get_cracks_folder(folder_name)
                downloader.copy_common_files(target, cracks_sub)
                Clock.schedule_once(self.download_complete)
            else:
                Clock.schedule_once(lambda dt: self.show_steam_auth_error())
                
        except Exception as e:
            error_msg = str(e).lower()
            if "invalidpassword" in error_msg or "authentication failed" in error_msg:
                Clock.schedule_once(lambda dt: self.show_steam_auth_error())
            else:
                Clock.schedule_once(lambda dt: self.show_error(f"Download error: {str(e)}"))
    
    def get_cracks_folder(self, folder_name):
        old_seasons = ['Y1S0_Vanilla', 'Y1S1_BlackIce', 'Y1S2_DustLine', 'Y1S3_SkullRain', 'Y1S4_RedCrow', 'Y2S1_VelvetShell']
        return 'Y1SX-Y6S2' if folder_name in old_seasons else 'Y6S4-Y8SX'
    
    def start_progress(self):
        self.download_btn.text = "DOWNLOADING..."
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self.progress_bar)
        
        threading.Thread(target=self.simulate_progress, daemon=True).start()
    
    def simulate_progress(self):
        for i in range(0, 15, 2):
            time.sleep(0.2)
            Clock.schedule_once(lambda dt, progress=i: self.update_progress(progress))
        
        for i in range(15, 90, 1):
            time.sleep(0.3)
            Clock.schedule_once(lambda dt, progress=i: self.update_progress(progress))
        
        for i in range(90, 101, 2):
            time.sleep(0.1)
            Clock.schedule_once(lambda dt, progress=i: self.update_progress(progress))
    
    def update_progress(self, progress):
        self.progress_bar.value = progress
    
    def download_complete(self, *args):
        self.download_btn.text = "VALIDATE"
        self.download_btn.md_bg_color = "#28a745"
        self.download_btn.disabled = False
        
        dialog = MDDialog(
            title="Download Complete!",
            text=f"Successfully downloaded {self.game_data['title']}!\n\nClick VALIDATE to verify the installation.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#28a745",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_steam_auth_error(self):
        self.download_btn.text = "AUTH FAILED"
        self.download_btn.md_bg_color = "#dc3545"
        self.download_btn.disabled = False
        self.progress_bar.opacity = 0
        self.progress_bar.value = 0
        
        dialog = MDDialog(
            title="Steam Authentication Failed",
            text="Steam login failed. Common solutions:\n\n• Use your Steam LOGIN NAME (not display name)\n• Try leaving password empty\n• Check if Steam is running and logged in\n• Verify account has Rainbow Six Siege access",
            buttons=[
                MDFlatButton(
                    text="RETRY",
                    theme_text_color="Custom",
                    text_color="#dc3545",
                    on_release=lambda x: self.retry_download() or dialog.dismiss()
                ),
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#dc3545",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def retry_download(self):
        self.download_btn.text = "DOWNLOAD"
        self.download_btn.md_bg_color = "#7c3aed"
        self.download_btn.disabled = False
        self.progress_bar.opacity = 0
        self.progress_bar.value = 0
    
    def show_error(self, message):
        self.download_btn.text = "DOWNLOAD"
        self.download_btn.disabled = False
        self.progress_bar.opacity = 0
        self.progress_bar.value = 0
        
        dialog = MDDialog(
            title="Download Error",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#7c3aed",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def on_enter(self, *args):
        anim = Animation(elevation=12, duration=0.2)
        anim.start(self)
    
    def on_leave(self, *args):
        anim = Animation(elevation=8, duration=0.2)
        anim.start(self)

class InstalledGameCard(MDCard, HoverBehavior):
    def __init__(self, game_data, **kwargs):
        super().__init__(**kwargs)
        self.game_data = game_data
        self.md_bg_color = "#1e1e2e"
        self.radius = [15]
        self.elevation = 8
        self.size_hint_y = None
        self.height = dp(180)
        self.padding = dp(16)
        
        main_layout = MDBoxLayout(orientation="vertical", spacing=dp(8))
        
        header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        
        title_label = MDLabel(
            text=game_data["title"],
            theme_text_color="Custom",
            text_color="#e9ecef",
            font_style="H6",
            bold=True
        )
        
        status_label = MDLabel(
            text="INSTALLED ✓",
            theme_text_color="Custom",
            text_color="#28a745",
            font_style="Subtitle2",
            size_hint_x=None,
            width=dp(100),
            halign="right"
        )
        
        header.add_widget(title_label)
        header.add_widget(status_label)
        
        path_label = MDLabel(
            text=f"Path: {game_data['path']}",
            theme_text_color="Custom",
            text_color="#adb5bd",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20)
        )
        
        button_layout = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(40))
        
        play_btn = MDRaisedButton(
            text="PLAY",
            md_bg_color="#28a745",
            theme_text_color="Custom",
            text_color="#ffffff",
            size_hint=(None, None),
            height=dp(36),
            width=dp(80),
            on_release=self.launch_game
        )
        
        name_btn = MDRaisedButton(
            text="CHANGE NAME",
            md_bg_color="#7c3aed",
            theme_text_color="Custom",
            text_color="#ffffff",
            size_hint=(None, None),
            height=dp(36),
            width=dp(120),
            on_release=self.show_name_changer
        )
        
        validate_btn = MDRaisedButton(
            text="VALIDATE",
            md_bg_color="#ffc107",
            theme_text_color="Custom",
            text_color="#000000",
            size_hint=(None, None),
            height=dp(36),
            width=dp(90),
            on_release=self.validate_installation
        )
        
        button_layout.add_widget(play_btn)
        button_layout.add_widget(name_btn)
        button_layout.add_widget(validate_btn)
        
        main_layout.add_widget(header)
        main_layout.add_widget(path_label)
        main_layout.add_widget(button_layout)
        
        self.add_widget(main_layout)
    
    def launch_game(self, *args):
        try:
            import subprocess
            exe_path = Path(self.game_data["exe"])
            if exe_path.exists():
                subprocess.Popen([str(exe_path)], cwd=str(exe_path.parent))
                
                dialog = MDDialog(
                    title="Game Launched",
                    text=f"Successfully launched {self.game_data['title']}!",
                    buttons=[
                        MDFlatButton(
                            text="OK",
                            theme_text_color="Custom",
                            text_color="#28a745",
                            on_release=lambda x: dialog.dismiss()
                        )
                    ]
                )
                dialog.open()
            else:
                self.show_error("Game executable not found")
        except Exception as e:
            self.show_error(f"Failed to launch game: {str(e)}")
    
    def show_name_changer(self, *args):
        self.name_field = MDTextField(
            hint_text="Enter new username",
            text="ThrowbackUser",
            mode="rectangle",
            size_hint_y=None,
            height=dp(48)
        )
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(self.name_field)
        
        dialog = MDDialog(
            title="Change In-Game Username",
            type="custom",
            content_cls=content,
            text="This will update the username in CODEX.ini and CPlay.ini files:",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color="#6c757d",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="CHANGE NAME",
                    theme_text_color="Custom",
                    text_color="#7c3aed",
                    on_release=lambda x: self.change_username(dialog)
                )
            ]
        )
        dialog.open()
    
    def change_username(self, dialog):
        new_username = self.name_field.text.strip()
        if not new_username:
            self.show_error("Username cannot be empty")
            return
        
        dialog.dismiss()
        
        game_folder = Path(self.game_data["folder"])
        success_count = change_username_in_files(game_folder, new_username)
        
        if success_count > 0:
            success_dialog = MDDialog(
                title="Username Changed",
                text=f"Successfully updated username to '{new_username}' in {success_count} file(s)!\n\nThe change will take effect next time you launch the game.",
                buttons=[
                    MDFlatButton(
                        text="GREAT!",
                        theme_text_color="Custom",
                        text_color="#28a745",
                        on_release=lambda x: success_dialog.dismiss()
                    )
                ]
            )
            success_dialog.open()
        else:
            self.show_error("No configuration files found to update.\nMake sure CODEX.ini or CPlay.ini exist in the game folder.")
    
    def validate_installation(self, *args):
        game_folder = Path(self.game_data["folder"])
        
        required_files = ["RainbowSix.exe", "localization.lang"]
        config_files = ["CODEX.ini", "CPlay.ini"]
        
        missing_files = []
        found_configs = []
        
        for file in required_files:
            if not (game_folder / file).exists():
                missing_files.append(file)
        
        for config in config_files:
            if (game_folder / config).exists():
                found_configs.append(config)
        
        if missing_files:
            self.show_error(f"Validation failed!\nMissing files: {', '.join(missing_files)}")
        else:
            config_info = f"\nFound config files: {', '.join(found_configs)}" if found_configs else "\nNo config files found"
            
            dialog = MDDialog(
                title="Validation Successful",
                text=f"✓ {self.game_data['title']} installation is valid!{config_info}\n\nGame is ready to play.",
                buttons=[
                    MDFlatButton(
                        text="PLAY NOW",
                        theme_text_color="Custom",
                        text_color="#28a745",
                        on_release=lambda x: self.launch_game() or dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color="#28a745",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
    
    def show_error(self, message):
        dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#dc3545",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def on_enter(self, *args):
        anim = Animation(elevation=12, duration=0.2)
        anim.start(self)
    
    def on_leave(self, *args):
        anim = Animation(elevation=8, duration=0.2)
        anim.start(self)

class SeasonsTab(Tab):
    def __init__(self, **kwargs):
        self.title = "Seasons"
        super().__init__(**kwargs)
        self.build_seasons_tab()
    
    def build_seasons_tab(self):
        self.seasons_data = []
        if DOWNLOADER_AVAILABLE and hasattr(downloader, 'SEASONS'):
            for season_name, (folder_name, depots) in downloader.SEASONS.items():
                estimated_size = f"{len(depots) * 15}GB"
                
                year_match = folder_name.split('_')[0] if '_' in folder_name else "Y1S0"
                year = year_match.replace('Y', 'Year ').replace('S', ' Season ')
                
                self.seasons_data.append({
                    "title": season_name,
                    "year": year,
                    "size": estimated_size,
                    "season": "R6 Siege",
                    "season_key": season_name,
                    "description": f"Download Rainbow Six Siege {season_name} season with all content and operators."
                })
        else:
            self.seasons_data = [
                {"title": "Vanilla", "year": "Y1S0", "size": "45GB", "season": "R6 Siege", "season_key": "Vanilla", "description": "Original Rainbow Six Siege launch version with classic gameplay."},
                {"title": "Black Ice", "year": "Y1S1", "size": "45GB", "season": "R6 Siege", "season_key": "BlackIce", "description": "First major content update featuring Canadian operators and winter maps."},
                {"title": "Dust Line", "year": "Y1S2", "size": "45GB", "season": "R6 Siege", "season_key": "DustLine", "description": "Navy SEALs operators and Border map addition to the tactical shooter."},
            ]
        
        self.filtered_seasons = self.seasons_data.copy()
        
        main_layout = MDBoxLayout(orientation="vertical")
        
        scroll = MDScrollView()
        self.seasons_layout = MDGridLayout(
            cols=1,
            spacing=dp(16),
            padding=dp(16),
            size_hint_y=None,
            md_bg_color="#0d1117"
        )
        self.seasons_layout.bind(minimum_height=self.seasons_layout.setter('height'))
        
        scroll.add_widget(self.seasons_layout)
        
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        
        self.populate_seasons()
    
    def populate_seasons(self):
        self.seasons_layout.clear_widgets()
        
        cards = []
        for season in self.filtered_seasons:
            card = GameCard(season)
            cards.append(card)
            self.seasons_layout.add_widget(card)
        
        if len(cards) <= 10:
            for i, card in enumerate(cards):
                card.opacity = 0
                anim = Animation(opacity=1, duration=0.2)
                Clock.schedule_once(lambda dt, c=card, a=anim: a.start(c), i * 0.05)

class InstalledTab(Tab):
    def __init__(self, **kwargs):
        self.title = "Installed"
        super().__init__(**kwargs)
        self.build_installed_tab()
    
    def build_installed_tab(self):
        main_layout = MDBoxLayout(orientation="vertical")
        
        header_layout = MDBoxLayout(
            orientation="horizontal",
            padding=[dp(16), dp(8)],
            spacing=dp(12),
            size_hint_y=None,
            height=dp(60),
            md_bg_color="#181825"
        )
        
        title_label = MDLabel(
            text="Installed Games",
            theme_text_color="Custom",
            text_color="#e9ecef",
            font_style="H5",
            bold=True
        )
        
        refresh_btn = MDIconButton(
            icon="refresh",
            theme_icon_color="Custom",
            icon_color="#7c3aed",
            on_release=self.refresh_installed_games
        )
        
        header_layout.add_widget(title_label)
        header_layout.add_widget(refresh_btn)
        
        scroll = MDScrollView()
        self.installed_layout = MDGridLayout(
            cols=1,
            spacing=dp(16),
            padding=dp(16),
            size_hint_y=None,
            md_bg_color="#0d1117"
        )
        self.installed_layout.bind(minimum_height=self.installed_layout.setter('height'))
        
        scroll.add_widget(self.installed_layout)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        
        self.refresh_installed_games()
    
    def refresh_installed_games(self, *args):
        self.installed_layout.clear_widgets()
        
        if DOWNLOADER_AVAILABLE and hasattr(downloader, 'DOWNLOADS_DIR'):
            downloads_dir = downloader.DOWNLOADS_DIR
        else:
            downloads_dir = Path("./Downloads")
        
        installed_games = get_installed_games(downloads_dir)
        
        if not installed_games:
            no_games_label = MDLabel(
                text="No installed games found.\n\nDownload some games from the Seasons tab!",
                theme_text_color="Custom",
                text_color="#6c757d",
                font_style="H6",
                halign="center",
                size_hint_y=None,
                height=dp(100)
            )
            self.installed_layout.add_widget(no_games_label)
        else:
            for i, game in enumerate(installed_games):
                card = InstalledGameCard(game)
                self.installed_layout.add_widget(card)
                
                card.opacity = 0
                anim = Animation(opacity=1, duration=0.3)
                Clock.schedule_once(lambda dt, c=card, a=anim: a.start(c), i * 0.05)

class ToolsTab(Tab):
    def __init__(self, **kwargs):
        self.title = "Tools"
        super().__init__(**kwargs)
        self.build_tools_tab()
    
    def build_tools_tab(self):
        main_layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(16),
            md_bg_color="#0d1117"
        )
        
        title = MDLabel(
            text="Modding & Extra Tools",
            theme_text_color="Custom",
            text_color="#e9ecef",
            font_style="H4",
            size_hint_y=None,
            height=dp(50)
        )
        
        tools = [
            {"name": "R6 Liberator", "description": "Tool for Y1S0 – Y4S4 season modification", "action": self.download_liberator},
            {"name": "Heated Metal", "description": "Shadow Legacy (Y5S3) modding tool", "action": self.download_heated_metal},
            {"name": "DXVK Vulkan", "description": "Vulkan renderer for better performance", "action": self.download_dxvk},
            {"name": "Shadow Legacy Liberator", "description": "R6 Liberator2 for Shadow Legacy modding", "action": self.download_shadow_liberator},
            {"name": "R6S Global Tool", "description": "Shadow Legacy global modding tool", "action": self.download_r6s_global},
            {"name": "Void Edge Tool", "description": "Void Edge season modding tool", "action": self.download_void_edge_tool},
            {"name": "Shears", "description": "Game size reducer and optimization tool", "action": self.download_shears},
        ]
        
        scroll = MDScrollView()
        tools_layout = MDBoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
        tools_layout.bind(minimum_height=tools_layout.setter('height'))
        
        for tool in tools:
            card = MDCard(
                md_bg_color="#1e1e2e",
                radius=[10],
                elevation=4,
                size_hint_y=None,
                height=dp(80),
                padding=dp(16)
            )
            
            content = MDBoxLayout(orientation="horizontal", spacing=dp(16))
            
            info_layout = MDBoxLayout(orientation="vertical")
            
            name_label = MDLabel(
                text=tool["name"],
                theme_text_color="Custom",
                text_color="#e9ecef",
                font_style="Subtitle1",
                bold=True,
                size_hint_y=None,
                height=dp(30)
            )
            
            desc_label = MDLabel(
                text=tool["description"],
                theme_text_color="Custom",
                text_color="#adb5bd",
                font_style="Caption",
                size_hint_y=None,
                height=dp(20)
            )
            
            info_layout.add_widget(name_label)
            info_layout.add_widget(desc_label)
            
            download_btn = MDRaisedButton(
                text="GET",
                md_bg_color="#7c3aed",
                size_hint=(None, None),
                height=dp(40),
                width=dp(80),
                pos_hint={"center_y": 0.5},
                on_release=tool["action"]
            )
            
            content.add_widget(info_layout)
            content.add_widget(download_btn)
            card.add_widget(content)
            tools_layout.add_widget(card)
        
        scroll.add_widget(tools_layout)
        main_layout.add_widget(title)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def download_liberator(self, *args):
        webbrowser.open('https://github.com/SlejmUr/Manifest_Tool_TB/releases')
        dialog = MDDialog(
            title="Opening GitHub",
            text="Opening R6 Liberator releases page in your browser...",
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#7c3aed",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def download_heated_metal(self, *args):
        if DOWNLOADER_AVAILABLE and hasattr(downloader, 'DOWNLOADS_DIR'):
            downloads_dir = downloader.DOWNLOADS_DIR
        else:
            downloads_dir = Path("./Downloads")
        
        target_folder = downloads_dir / "Y5S4_NeonDawnHM"
        
        if not target_folder.exists():
            dialog = MDDialog(
                title="Installation Error",
                text=f"Y5S4_NeonDawnHM folder not found!\n\nHeated Metal requires the Neon Dawn Heated Metal season to be installed first.\n\nExpected location:\n{target_folder}",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color="#dc3545",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
            return
        
        if not DOWNLOADER_AVAILABLE:
            self.show_tool_error("Downloader not available")
            return
        
        dialog = MDDialog(
            title="Download Started",
            text=f"Downloading Heated Metal...\n\nInstalling to: {target_folder}\n\nThis may take a few moments.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#7c3aed",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
        
        def download_task():
            try:
                if hasattr(downloader, 'curl') and hasattr(downloader, 'seven_zip_extract'):
                    heated_metal_url = "https://github.com/DataCluster0/HeatedMetal/releases/download/0.2.3/HeatedMetal.7z"
                    tmp_file = downloader.THIS_DIR / 'HeatedMetal.7z'
                    
                    downloader.curl(heated_metal_url, tmp_file)
                    
                    downloader.seven_zip_extract(tmp_file, target_folder)
                    
                    Clock.schedule_once(lambda dt: self.show_heated_metal_success(str(target_folder)))
                else:
                    Clock.schedule_once(lambda dt: self.show_tool_error("Download function not available"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_tool_error(f"Download failed: {str(e)}"))
        
        threading.Thread(target=download_task, daemon=True).start()
    
    def download_dxvk(self, *args):
        webbrowser.open('https://github.com/doitsujin/dxvk/releases')
        dialog = MDDialog(
            title="Opening GitHub",
            text="Opening DXVK releases page in your browser...",
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#7c3aed",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def download_shadow_liberator(self, *args):
        if not DOWNLOADER_AVAILABLE:
            self.show_tool_error("Downloader not available")
            return
            
        dialog = MDDialog(
            title="Download Started",
            text="Downloading Shadow Legacy Liberator...\nThis tool is for Shadow Legacy season modding.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#7c3aed",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
        
        def download_task():
            try:
                if hasattr(downloader, 'curl') and hasattr(downloader, 'TOOLS_DIR'):
                    shadow_lib_url = "https://github.com/JOJOVAV/r6-tools/raw/main/R6Liberator2.exe"
                    target_path = downloader.TOOLS_DIR / 'R6Liberator2.exe'
                    downloader.curl(shadow_lib_url, target_path)
                    Clock.schedule_once(lambda dt: self.show_tool_success("Shadow Legacy Liberator downloaded successfully!"))
                else:
                    Clock.schedule_once(lambda dt: self.show_tool_error("Download function not available"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_tool_error(f"Download failed: {str(e)}"))
        
        threading.Thread(target=download_task, daemon=True).start()
    
    def download_r6s_global(self, *args):
        if DOWNLOADER_AVAILABLE and hasattr(downloader, 'DOWNLOADS_DIR'):
            downloads_dir = downloader.DOWNLOADS_DIR
        else:
            downloads_dir = Path("./Downloads")
        
        target_folder = downloads_dir / "Y5S3_ShadowLegacy"
        
        if not target_folder.exists():
            dialog = MDDialog(
                title="Installation Error",
                text=f"Y5S3_ShadowLegacy folder not found!\n\nR6S Global Tool requires Shadow Legacy season to be installed first.\n\nExpected location:\n{target_folder}",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color="#dc3545",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
            return
        
        if not DOWNLOADER_AVAILABLE:
            self.show_tool_error("Downloader not available")
            return
        
        dialog = MDDialog(
            title="Download Started",
            text=f"Downloading R6S Global Tool...\n\nInstalling to: {target_folder}\n\nThis tool is for Shadow Legacy global modding.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#7c3aed",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
        
        def download_task():
            try:
                if hasattr(downloader, 'curl'):
                    r6s_global_url = "https://github.com/JOJOVAV/r6-tools/raw/main/R6SGlobal_shadowlegacy.exe"
                    target_path = target_folder / 'R6SGlobal_shadowlegacy.exe'
                    downloader.curl(r6s_global_url, target_path)
                    Clock.schedule_once(lambda dt: self.show_r6s_global_success(str(target_folder)))
                else:
                    Clock.schedule_once(lambda dt: self.show_tool_error("Download function not available"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_tool_error(f"Download failed: {str(e)}"))
        
        threading.Thread(target=download_task, daemon=True).start()
    
    def download_void_edge_tool(self, *args):
        if not DOWNLOADER_AVAILABLE:
            self.show_tool_error("Downloader not available")
            return
            
        dialog = MDDialog(
            title="Download Started",
            text="Downloading Void Edge Tool...\nThis tool is for Void Edge season modding.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#7c3aed",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
        
        def download_task():
            try:
                if hasattr(downloader, 'curl') and hasattr(downloader, 'TOOLS_DIR'):
                    void_edge_url = "https://github.com/JOJOVAV/r6-tools/raw/main/R6S_VoidEdge.exe"
                    target_path = downloader.TOOLS_DIR / 'R6S_VoidEdge.exe'
                    downloader.curl(void_edge_url, target_path)
                    Clock.schedule_once(lambda dt: self.show_tool_success("Void Edge Tool downloaded successfully!"))
                else:
                    Clock.schedule_once(lambda dt: self.show_tool_error("Download function not available"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_tool_error(f"Download failed: {str(e)}"))
        
        threading.Thread(target=download_task, daemon=True).start()
    
    def download_shears(self, *args):
        if not DOWNLOADER_AVAILABLE:
            self.show_tool_error("Downloader not available")
            return
            
        dialog = MDDialog(
            title="Download Started",
            text="Downloading Shears...\nThis tool reduces game size and optimizes performance.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#7c3aed",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
        
        def download_task():
            try:
                if hasattr(downloader, 'curl') and hasattr(downloader, 'seven_zip_extract') and hasattr(downloader, 'TOOLS_DIR'):
                    shears_url = "https://github.com/JOJOVAV/r6-tools/raw/main/shears.zip"
                    tmp_file = downloader.THIS_DIR / 'shears.zip'
                    
                    downloader.curl(shears_url, tmp_file)
                    
                    shears_folder = downloader.TOOLS_DIR / 'Shears'
                    downloader.seven_zip_extract(tmp_file, shears_folder)
                    
                    Clock.schedule_once(lambda dt: self.show_shears_success(str(shears_folder)))
                else:
                    Clock.schedule_once(lambda dt: self.show_tool_error("Download function not available"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_tool_error(f"Download failed: {str(e)}"))
        
        threading.Thread(target=download_task, daemon=True).start()
    
    def show_heated_metal_success(self, install_path):
        dialog = MDDialog(
            title="Heated Metal Installed!",
            text=f"Successfully downloaded and installed Heated Metal!\n\nInstalled to:\n{install_path}\n\nHeated Metal is now ready to use with your Neon Dawn Heated Metal installation.",
            buttons=[
                MDFlatButton(
                    text="OPEN FOLDER",
                    theme_text_color="Custom",
                    text_color="#28a745",
                    on_release=lambda x: self.open_game_folder(install_path) or dialog.dismiss()
                ),
                MDFlatButton(
                    text="GREAT!",
                    theme_text_color="Custom",
                    text_color="#28a745",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_tool_success(self, message):
        dialog = MDDialog(
            title="Download Complete!",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#28a745",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_tool_error(self, message):
        dialog = MDDialog(
            title="Download Error",
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color="#dc3545",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_r6s_global_success(self, install_path):
        dialog = MDDialog(
            title="R6S Global Tool Installed!",
            text=f"Successfully downloaded R6S Global Tool!\n\nInstalled to:\n{install_path}\n\nThis tool is ready to use with your Shadow Legacy installation.",
            buttons=[
                MDFlatButton(
                    text="OPEN FOLDER",
                    theme_text_color="Custom",
                    text_color="#28a745",
                    on_release=lambda x: self.open_game_folder(install_path) or dialog.dismiss()
                ),
                MDFlatButton(
                    text="GREAT!",
                    theme_text_color="Custom",
                    text_color="#28a745",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_shears_success(self, install_path):
        dialog = MDDialog(
            title="Shears Installed!",
            text=f"Successfully downloaded and extracted Shears!\n\nInstalled to:\n{install_path}\n\nShears is ready to help reduce your game sizes and optimize performance.",
            buttons=[
                MDFlatButton(
                    text="OPEN FOLDER",
                    theme_text_color="Custom",
                    text_color="#28a745",
                    on_release=lambda x: self.open_game_folder(install_path) or dialog.dismiss()
                ),
                MDFlatButton(
                    text="AWESOME!",
                    theme_text_color="Custom",
                    text_color="#28a745",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def open_game_folder(self, folder_path):
        try:
            import os
            if os.name == 'nt':
                os.startfile(folder_path)
            else:
                os.system(f'xdg-open "{folder_path}"')
        except Exception as e:
            print(f"Could not open folder: {e}")

class SettingsTab(Tab):
    def __init__(self, **kwargs):
        self.title = "Settings"
        super().__init__(**kwargs)
        self.build_settings_tab()
    
    def build_settings_tab(self):
        main_layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(16),
            md_bg_color="#0d1117"
        )
        
        title = MDLabel(
            text="Settings",
            theme_text_color="Custom",
            text_color="#e9ecef",
            font_style="H4",
            size_hint_y=None,
            height=dp(50)
        )
        
        scroll = MDScrollView()
        settings_layout = MDBoxLayout(orientation="vertical", spacing=dp(16), size_hint_y=None)
        settings_layout.bind(minimum_height=settings_layout.setter('height'))
        
        steam_card = MDCard(
            md_bg_color="#1e1e2e",
            radius=[10],
            elevation=4,
            size_hint_y=None,
            height=dp(200),
            padding=dp(16)
        )
        
        steam_layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        steam_title = MDLabel(
            text="Steam Account Settings",
            theme_text_color="Custom",
            text_color="#e9ecef",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        
        self.username_field = MDTextField(
            hint_text="Steam Username",
            mode="rectangle",
            size_hint_y=None,
            height=dp(48),
            text_color_normal="#e9ecef",
            line_color_focus="#7c3aed",
            fill_color_normal="#2d2d3a"
        )
        
        self.password_field = MDTextField(
            hint_text="Steam Password (optional)",
            mode="rectangle",
            password=True,
            size_hint_y=None,
            height=dp(48),
            text_color_normal="#e9ecef",
            line_color_focus="#7c3aed",
            fill_color_normal="#2d2d3a"
        )
        
        save_btn = MDRaisedButton(
            text="SAVE CREDENTIALS",
            md_bg_color="#7c3aed",
            size_hint_y=None,
            height=dp(40),
            on_release=self.save_credentials
        )
        
        steam_layout.add_widget(steam_title)
        steam_layout.add_widget(self.username_field)
        steam_layout.add_widget(self.password_field)
        steam_layout.add_widget(save_btn)
        steam_card.add_widget(steam_layout)
        
        download_card = MDCard(
            md_bg_color="#1e1e2e",
            radius=[10],
            elevation=4,
            size_hint_y=None,
            height=dp(150),
            padding=dp(16)
        )
        
        download_layout = MDBoxLayout(orientation="vertical", spacing=dp(12))
        
        download_title = MDLabel(
            text="Download Settings",
            theme_text_color="Custom",
            text_color="#e9ecef",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        
        self.download_path_field = MDTextField(
            hint_text="Download Location",
            text=str(downloader.DOWNLOADS_DIR) if (DOWNLOADER_AVAILABLE and hasattr(downloader, 'DOWNLOADS_DIR')) else "./Downloads",
            mode="rectangle",
            size_hint_y=None,
            height=dp(48),
            text_color_normal="#e9ecef",
            line_color_focus="#7c3aed",
            fill_color_normal="#2d2d3a"
        )
        
        speed_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        speed_label = MDLabel(
            text="Fast Downloads (50 connections)",
            theme_text_color="Custom",
            text_color="#e9ecef"
        )
        
        self.fast_download_switch = MDSwitch(
            thumb_color_active="#7c3aed",
            pos_hint={"center_y": 0.5}
        )
        
        speed_layout.add_widget(speed_label)
        speed_layout.add_widget(self.fast_download_switch)
        
        download_layout.add_widget(download_title)
        download_layout.add_widget(self.download_path_field)
        download_layout.add_widget(speed_layout)
        download_card.add_widget(download_layout)
        
        settings_layout.add_widget(steam_card)
        settings_layout.add_widget(download_card)
        
        scroll.add_widget(settings_layout)
        main_layout.add_widget(title)
        main_layout.add_widget(scroll)
        
        username, password = load_credentials()
        self.username_field.text = username
        if password:
            self.password_field.text = password
        
        self.add_widget(main_layout)
    
    def save_credentials(self, *args):
        username = self.username_field.text.strip()
        password = self.password_field.text.strip()
        
        if not username:
            dialog = MDDialog(
                title="Invalid Credentials",
                text="Steam username cannot be empty",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color="#7c3aed",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
            return
        
        app = MDApp.get_running_app()
        app.steam_username = username
        app.steam_password = password
        
        if save_credentials(username, password):
            dialog = MDDialog(
                title="Success",
                text="Steam credentials saved successfully to file!\n\nYour credentials are stored securely and will be remembered next time.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color="#28a745",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
        else:
            dialog = MDDialog(
                title="Save Error",
                text="Failed to save credentials to file.\nCredentials are saved for this session only.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color="#ffc107",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()

class GameDownloaderScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        main_layout = MDBoxLayout(orientation="vertical")
        
        toolbar = MDTopAppBar(
            title="S1lly's Downloader",
            md_bg_color="#11111b",
            specific_text_color="#e9ecef",
            elevation=4
        )
        
        tabs = MDTabs(
            tab_bar_height=dp(48),
            tab_indicator_anim=True,
            tab_indicator_height=dp(2),
            indicator_color="#7c3aed"
        )
        
        tabs.add_widget(SeasonsTab())
        tabs.add_widget(InstalledTab())
        tabs.add_widget(ToolsTab())
        tabs.add_widget(SettingsTab())
        
        main_layout.add_widget(toolbar)
        main_layout.add_widget(tabs)
        
        self.add_widget(main_layout)

class S1llyDownloaderApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.steam_username = ""
        self.steam_password = ""
    
    def build(self):
        from kivy.core.window import Window
        Window.size = (1400, 900)
        Window.minimum_width = 1200
        Window.minimum_height = 800
        
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Purple"
        
        username, password = load_credentials()
        self.steam_username = username
        self.steam_password = password
        
        if DOWNLOADER_AVAILABLE:
            try:
                downloader.ensure_resources()
                self.show_setup_dialog()
            except Exception as e:
                self.show_setup_error(f"Error setting up resources: {e}")
        else:
            self.show_downloader_missing_dialog()
        
        screen_manager = MDScreenManager()
        screen_manager.add_widget(GameDownloaderScreen(name="main"))
        
        return screen_manager
    
    def show_setup_dialog(self):
        dialog = MDDialog(
            title="Setting Up S1lly's Downloader",
            text="Downloading required tools and resources...\nThis only happens once.",
            auto_dismiss=False
        )
        dialog.open()
        
        Clock.schedule_once(lambda dt: dialog.dismiss(), 3)
    
    def show_setup_error(self, message):
        dialog = MDDialog(
            title="Setup Error",
            text=f"Failed to setup downloader resources:\n{message}\n\nSome features may not work properly.",
            buttons=[
                MDFlatButton(
                    text="CONTINUE ANYWAY",
                    theme_text_color="Custom",
                    text_color="#ffc107",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_downloader_missing_dialog(self):
        dialog = MDDialog(
            title="Downloader Missing",
            text="downloader.py not found in the same folder.\n\nPlease ensure downloader.py is in the same directory as this GUI for full functionality.",
            buttons=[
                MDFlatButton(
                    text="CONTINUE IN DEMO MODE",
                    theme_text_color="Custom",
                    text_color="#ffc107",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

if __name__ == "__main__":
    S1llyDownloaderApp().run()