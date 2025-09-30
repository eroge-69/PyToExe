import threading, time, tkinter as tk, requests, json, os
from bs4 import BeautifulSoup
from win10toast import ToastNotifier
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw, ImageTk
from io import BytesIO

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"gameday_only": False}

TEAM_COLORS = {
    "49ers": "#aa0000", "Bears": "#0b162a", "Bengals": "#fb4f14", "Bills": "#00338d",
    "Broncos": "#fb4f14", "Browns": "#311d00", "Buccaneers": "#d50a0a", "Cardinals": "#97233f",
    "Chargers": "#0080c6", "Chiefs": "#e31837", "Colts": "#002c5f", "Commanders": "#5a1414",
    "Cowboys": "#003594", "Dolphins": "#008e97", "Eagles": "#004c54", "Falcons": "#a71930",
    "Giants": "#0b2265", "Jaguars": "#006778", "Jets": "#125740", "Lions": "#0069aa",
    "Packers": "#203731", "Panthers": "#0085ca", "Patriots": "#002244", "Raiders": "#000000",
    "Rams": "#003594", "Ravens": "#241773", "Saints": "#d3bc8d", "Seahawks": "#002244",
    "Steelers": "#ffb612", "Texans": "#03202f", "Titans": "#4b92db", "Vikings": "#4f2683"
}

TEAM_LOGOS = {
    "49ers": "https://a.espncdn.com/i/teamlogos/nfl/500/sfo.png",
    "Bears": "https://a.espncdn.com/i/teamlogos/nfl/500/chi.png",
    "Bengals": "https://a.espncdn.com/i/teamlogos/nfl/500/cin.png",
    "Bills": "https://a.espncdn.com/i/teamlogos/nfl/500/buf.png",
    "Broncos": "https://a.espncdn.com/i/teamlogos/nfl/500/den.png",
    "Browns": "https://a.espncdn.com/i/teamlogos/nfl/500/cle.png",
    "Buccaneers": "https://a.espncdn.com/i/teamlogos/nfl/500/tb.png",
    "Cardinals": "https://a.espncdn.com/i/teamlogos/nfl/500/ari.png",
    "Chargers": "https://a.espncdn.com/i/teamlogos/nfl/500/lac.png",
    "Chiefs": "https://a.espncdn.com/i/teamlogos/nfl/500/kc.png",
    "Colts": "https://a.espncdn.com/i/teamlogos/nfl/500/ind.png",
    "Commanders": "https://a.espncdn.com/i/teamlogos/nfl/500/wsh.png",
    "Cowboys": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
    "Dolphins": "https://a.espncdn.com/i/teamlogos/nfl/500/mia.png",
    "Eagles": "https://a.espncdn.com/i/teamlogos/nfl/500/phi.png",
    "Falcons": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
    "Giants": "https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png",
    "Jaguars": "https://a.espncdn.com/i/teamlogos/nfl/500/jax.png",
    "Jets": "https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png",
    "Lions": "https://a.espncdn.com/i/teamlogos/nfl/500/det.png",
    "Packers": "https://a.espncdn.com/i/teamlogos/nfl/500/gb.png",
    "Panthers": "https://a.espncdn.com/i/teamlogos/nfl/500/car.png",
    "Patriots": "https://a.espncdn.com/i/teamlogos/nfl/500/ne.png",
    "Raiders": "https://a.espncdn.com/i/teamlogos/nfl/500/lv.png",
    "Rams": "https://a.espncdn.com/i/teamlogos/nfl/500/lar.png",
    "Ravens": "https://a.espncdn.com/i/teamlogos/nfl/500/bal.png",
    "Saints": "https://a.espncdn.com/i/teamlogos/nfl/500/no.png",
    "Seahawks": "https://a.espncdn.com/i/teamlogos/nfl/500/sea.png",
    "Steelers": "https://a.espncdn.com/i/teamlogos/nfl/500/pit.png",
    "Texans": "https://a.espncdn.com/i/teamlogos/nfl/500/hou.png",
    "Titans": "https://a.espncdn.com/i/teamlogos/nfl/500/ten.png",
    "Vikings": "https://a.espncdn.com/i/teamlogos/nfl/500/min.png"
}
def get_team_records():
    try:
        url = "https://www.espn.com/nfl/standings/_/type/regular"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        records = {}
        rows = soup.select("table tbody tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 4:
                team_name = cells[0].get_text(strip=True)
                wins = cells[1].get_text(strip=True)
                losses = cells[2].get_text(strip=True)
                ties = cells[3].get_text(strip=True)
                short_name = team_name.split()[-1]
                record = f"{wins}–{losses}" if ties == "0" else f"{wins}–{losses}–{ties}"
                records[short_name] = record
        return records
    except Exception as e:
        print("Error fetching records:", e)
        return {}

def get_lions_schedule():
    past = {"team_left": "Lions", "team_right": "Browns", "score": "34 - 10", "clock": "Final", "down": "—", "quarter": "—", "active": False}
    future = {"team_left": "Lions", "team_right": "Bengals", "score": "—", "clock": "Sun Oct 5 @ 4:25 PM", "down": "—", "quarter": "—", "active": False}
    return past, future

def get_lions_game():
    try:
        url = "https://www.nfl.com/scores/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        games = soup.find_all("div", class_="nfl-c-matchup-strip")
        for game in games:
            teams = game.find_all("span", class_="nfl-c-matchup-strip__team-fullname")
            scores = game.find_all("span", class_="nfl-c-matchup-strip__team-score")
            status = game.find("span", class_="nfl-c-matchup-strip__status")
            down_dist = game.find("span", class_="nfl-c-matchup-strip__down-distance")
            if not teams or len(teams) < 2:
                continue
            names = [t.get_text(strip=True) for t in teams]
            if "Lions" in names:
                score_text = f"{scores[0].text} - {scores[1].text}" if scores else "0 - 0"
                clock = status.text.strip() if status else "00:00"
                down = down_dist.text.strip() if down_dist else "1st & 10"
                quarter = "1st" if "1st" in clock else "Q?"
                return {
                    "team_left": names[0], "team_right": names[1],
                    "score": score_text, "clock": clock,
                    "down": down, "quarter": quarter, "active": True
                }
        return None
    except Exception as e:
        print("Error in get_lions_game:", e)
        return None

def download_logo(team_name):
    try:
        url = TEAM_LOGOS.get(team_name)
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        img = Image.open(BytesIO(response.content)).resize((60, 60))
        return img
    except:
        return Image.new("RGB", (60, 60), color="black")

def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except:
        pass
class TickerBar:
    def __init__(self, root, get_game_func, settings, team_records):
        self.root = root
        self.get_game = get_game_func
        self.settings = settings
        self.team_records = team_records
        self.offset_x = 0
        self.offset_y = 0
        self.alt_mode = False
        self.last_swap_time = time.time()

        self.canvas = tk.Canvas(root, height=60, width=800, bg="gray", highlightthickness=0)
        self.canvas.pack()
        self.root.overrideredirect(True)
        self.root.geometry("800x60+100+100")
        self.root.attributes("-topmost", True)
        self.root.update_idletasks()

        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.do_move)

        self.update()

    def start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):
        x = event.x_root - self.offset_x
        y = event.y_root - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def update(self):
        game = self.get_game()
        if not game or "team_left" not in game:
            if time.time() - self.last_swap_time > 30:
                self.alt_mode = not self.alt_mode
                self.last_swap_time = time.time()
            past, future = get_lions_schedule()
            game = past if self.alt_mode else future

        if not game:
            game = {
                "team_left": "Lions", "team_right": "Unknown",
                "score": "—", "clock": "Error",
                "down": "—", "quarter": "—", "active": False
            }

        if self.settings.get("gameday_only") and not game["active"]:
            self.root.withdraw()
        else:
            self.root.deiconify()

        self.canvas.delete("all")

        left_color = TEAM_COLORS.get(game["team_left"].split()[-1], "#333")
        right_color = TEAM_COLORS.get(game["team_right"].split()[-1], "#333")

        self.canvas.create_rectangle(0, 0, 150, 60, fill=left_color, outline="")
        self.canvas.create_rectangle(650, 0, 800, 60, fill=right_color, outline="")
        self.canvas.create_rectangle(250, 0, 550, 60, fill="#222", outline="")

        left_logo = download_logo(game["team_left"].split()[-1])
        right_logo = download_logo(game["team_right"].split()[-1])
        self.left_logo = ImageTk.PhotoImage(left_logo)
        self.right_logo = ImageTk.PhotoImage(right_logo)

        self.canvas.create_image(75, 30, image=self.left_logo)
        self.canvas.create_image(725, 30, image=self.right_logo)

        score_left, score_right = game["score"].split(" - ") if " - " in game["score"] else ("—", "—")
        self.canvas.create_text(200, 30, text=score_left, fill="white", font=("Segoe UI", 25, "bold"))
        self.canvas.create_text(600, 30, text=score_right, fill="white", font=("Segoe UI", 25, "bold"))

        def normalize_team_name(name):
            name = name.strip().lower()
            for key in self.team_records:
                if key.lower() in name:
                    return key
            return name.title()

        left_key = normalize_team_name(game["team_left"])
        right_key = normalize_team_name(game["team_right"])
        record_left = self.team_records.get(left_key, "—")
        record_right = self.team_records.get(right_key, "—")

        #self.canvas.create_text(160, 30, text=record_left, fill="white", font=("Segoe UI", 10))
        #self.canvas.create_text(640, 30, text=record_right, fill="white", font=("Segoe UI", 10))

        self.canvas.create_text(400, 15, text=game["clock"], fill="white", font=("Segoe UI", 14, "bold"))
        info_text = f"{game['down']} | {game['quarter']}" if game["clock"].lower() != "final" else ""
        self.canvas.create_text(400, 35, text=info_text, fill="white", font=("Segoe UI", 10))

        self.root.after(60000, self.update)
def create_image():
    image = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(image)
    draw.text((10, 20), "L", fill='white')
    return image

def poll_scores(icon):
    last_score = None
    notifier = ToastNotifier()
    while icon.visible:
        game = get_lions_game()
        if game and game["score"] != last_score and "Error" not in game["score"]:
            notifier.show_toast("Detroit Lions Update", game["score"], duration=10)
            last_score = game["score"]
        time.sleep(60)

def start_polling(icon):
    thread = threading.Thread(target=poll_scores, args=(icon,), daemon=True)
    thread.start()

def open_settings():
    def save_and_close():
        settings["gameday_only"] = gameday_var.get()
        save_settings(settings)
        win.destroy()

    win = tk.Toplevel()
    win.title("Ticker Settings")
    win.geometry("300x100")
    win.resizable(False, False)

    gameday_var = tk.BooleanVar(value=settings.get("gameday_only", False))
    tk.Checkbutton(win, text="Show only during active Lions games", variable=gameday_var).pack(pady=10)
    tk.Button(win, text="Save", command=save_and_close).pack(pady=5)

def quit_app(icon, item):
    icon.stop()
    root.destroy()

# Load settings and team records
settings = load_settings()
TEAM_RECORDS = get_team_records()

# Launch app
root = tk.Tk()
ticker = TickerBar(root, get_lions_game, settings, TEAM_RECORDS)

# Tray icon setup
icon = Icon("LionsScore", create_image(), menu=Menu(
    MenuItem("Settings", lambda icon, item: open_settings()),
    MenuItem("Quit", quit_app)
))

start_polling(icon)
threading.Thread(target=icon.run, daemon=True).start()
root.mainloop()