import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pygame
import os, random, io
from PIL import Image, ImageTk, ImageDraw, ImageOps
try:
    from mutagen.id3 import ID3, APIC
except ImportError:
    print("Mutagen not installed. MP3 cover art will not work.")

# ----------------------------- Setup -----------------------------
pygame.mixer.init()
tracks = []
track_names = []
images = []
decorations = []

track_positions = {}  # last positions

current_song_pos = 0
current_track_length = 1
progress_running = False
progress_dragging = False

THEME = {"bg": "#1e1e1e", "fg": "#f5f5f5", "accent": "#bb86fc", "deco": "★"}
DEFAULT_VOLUME = 0.5
FONT_OPTION = ("Comic Sans MS", 12, "bold")

root = tk.Tk()
root.title("Music Player ✨")
root.geometry("1280x720")
root.configure(bg=THEME["bg"])
root.resizable(True, True)

canvas = tk.Canvas(root, highlightthickness=0, bd=0, bg=THEME["bg"])
canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

# ----------------------------- Spinning Disk -----------------------------
def create_disk_image(size=120):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0,0,size,size), fill=(60,60,60,255))
    draw.ellipse((size*0.1,size*0.1,size*0.9,size*0.9), fill=(120,120,120,255))
    draw.ellipse((size*0.45,size*0.45,size*0.55,size*0.55), fill=(255,255,255,255))
    return img

disk_img_orig = create_disk_image()
disk_img = ImageTk.PhotoImage(disk_img_orig)
disk_angle = 0

def rotate_disk():
    global disk_img, disk_angle
    if pygame.mixer.music.get_busy():
        disk_angle = (disk_angle + 5) % 360
        rotated = disk_img_orig.rotate(disk_angle)
        disk_img = ImageTk.PhotoImage(rotated)
        disk_label.configure(image=disk_img)
    root.after(50, rotate_disk)

# ----------------------------- Central UI Frame -----------------------------
ui_frame = tk.Frame(root, bg=THEME["bg"])
ui_frame.place(relx=0.5, rely=0.5, anchor="center")

disk_frame = tk.Frame(ui_frame, bg=THEME["bg"], width=120, height=120)
disk_frame.grid(row=0, column=0, padx=(0,5))
disk_frame.grid_propagate(False)
disk_label = tk.Label(disk_frame, image=disk_img, bg=THEME["bg"])
disk_label.place(relx=0.5, rely=0.5, anchor="center")

player_frame = tk.Frame(ui_frame, bg=THEME["bg"], width=500, height=400)
player_frame.grid(row=0, column=1, padx=0)
player_frame.grid_propagate(False)

title = tk.Label(player_frame, text="🎶 Music Player 🎶", font=("Comic Sans MS", 20, "bold"),
                 bg=THEME["bg"], fg=THEME["accent"])
title.pack(pady=5)

currently_playing = tk.Label(player_frame, text="Currently Playing: None", font=("Arial", 12),
                             bg=THEME["bg"], fg=THEME["fg"])
currently_playing.pack(pady=2)

playlist_box = tk.Listbox(player_frame, height=12, width=35, selectmode="multiple",
                          font=("Arial", 12), bg="#2e2e2e", fg="white",
                          selectbackground=THEME["accent"], selectforeground=THEME["bg"])
playlist_box.pack(padx=5, pady=5, fill="both", expand=False)

controls = tk.Frame(player_frame, bg=THEME["bg"])
controls.pack(pady=5)

resolutions = ["900x600","1024x768","1280x720","1920x1080"]
res_menu = ttk.Combobox(controls, values=resolutions, font=("Comic Sans MS",11), state="readonly")
res_menu.set("1280x720")

add_btn = tk.Button(controls, text="➕ Add Songs", font=FONT_OPTION)
play_btn = tk.Button(controls, text="▶ Play", font=FONT_OPTION)
stop_btn = tk.Button(controls, text="⏹ Stop All", font=FONT_OPTION)
upload_btn = tk.Button(controls, text="🖼 Upload GIF/Image", font=FONT_OPTION)

add_btn.grid(row=0,column=0,padx=5,pady=5)
play_btn.grid(row=0,column=1,padx=5,pady=5)
stop_btn.grid(row=0,column=2,padx=5,pady=5)
upload_btn.grid(row=0,column=3,padx=5,pady=5)
res_menu.grid(row=0,column=4,padx=5,pady=5)

preset_frame = tk.Frame(player_frame, bg=THEME["bg"])
preset_frame.pack(pady=5)
save_btn = tk.Button(preset_frame, text="💾 Save Preset", font=FONT_OPTION)
load_btn = tk.Button(preset_frame, text="📂 Load Preset", font=FONT_OPTION)
save_btn.pack(side="left", padx=5)
load_btn.pack(side="left", padx=5)

cover_frame = tk.Frame(ui_frame, bg=THEME["bg"], width=180, height=180)
cover_frame.grid(row=0, column=2, padx=(10,0))
cover_frame.grid_propagate(False)
cover_label = tk.Label(cover_frame, bg=THEME["bg"])
cover_label.place(relx=0.5, rely=0.5, anchor="center")

volume_frame = tk.Frame(root, bg=THEME["bg"])
volume_frame.place(relx=0.97, rely=0.5, anchor="center")
volume_label = tk.Label(volume_frame, text="Volume", bg=THEME["bg"], fg=THEME["fg"], font=FONT_OPTION)
volume_label.pack()
volume_slider = tk.Scale(volume_frame, from_=1, to=0, resolution=0.01, orient="vertical",
                         bg=THEME["bg"], fg=THEME["fg"], length=200, font=FONT_OPTION)
volume_slider.set(DEFAULT_VOLUME)
volume_slider.pack()

# ----------------------------- Song Progress (draggable) -----------------------------
song_progress_frame = tk.Frame(player_frame, bg=THEME["bg"])
song_progress_frame.pack(pady=5, fill="x", padx=10)
song_progress = ttk.Scale(song_progress_frame, from_=0, to=100, orient="horizontal")
song_progress.pack(fill="x")

def start_drag(event):
    global progress_dragging
    progress_dragging = True

def stop_drag(event):
    global progress_dragging, current_song_pos
    progress_dragging = False
    idx = playlist_box.curselection()[0] if playlist_box.curselection() else None
    if idx is not None:
        new_time = song_progress.get()
        track_positions[idx] = new_time
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=new_time)

song_progress.bind("<Button-1>", start_drag)
song_progress.bind("<ButtonRelease-1>", stop_drag)

def update_progress():
    global current_song_pos
    if progress_running and playlist_box.curselection() and not progress_dragging:
        idx = playlist_box.curselection()[0]
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms >= 0:
            current_song_pos = pos_ms / 1000.0 + track_positions.get(idx, 0)
            if current_song_pos > current_track_length:
                current_song_pos = current_track_length
        song_progress.set(current_song_pos)
    root.after(16, update_progress)  # 60 FPS

# ----------------------------- Functions -----------------------------
def add_songs():
    files = filedialog.askopenfilenames(filetypes=[("Audio Files","*.mp3 *.wav")])
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        playlist_box.insert("end", name)
        tracks.append(f)
        track_names.append(name)

def update_cover(file_path):
    try:
        cover_img = None
        if file_path.lower().endswith(".mp3"):
            try:
                tags = ID3(file_path)
                for tag in tags.values():
                    if isinstance(tag, APIC):
                        cover_img = Image.open(io.BytesIO(tag.data))
                        break
            except:
                cover_img = None
        if cover_img is None:
            cover_img = Image.new("RGBA", (180,180), (100,100,100,255))
        cover_img = ImageOps.fit(cover_img, (180,180), Image.LANCZOS)
        cover_img_tk = ImageTk.PhotoImage(cover_img)
        cover_label.config(image=cover_img_tk)
        cover_label.image = cover_img_tk
    except:
        cover_label.config(image='')

def play_selected():
    global current_song_pos, current_track_length, progress_running
    selections = playlist_box.curselection()
    if not selections: return
    stop_all()
    idx = selections[0]
    track = tracks[idx]

    pygame.mixer.music.load(track)
    start_pos = track_positions.get(idx, 0)
    pygame.mixer.music.play(start=start_pos)
    pygame.mixer.music.set_volume(volume_slider.get())

    currently_playing.config(text=f"Currently Playing: {track_names[idx]}")
    update_cover(track)

    current_song_pos = start_pos
    current_track_length = pygame.mixer.Sound(track).get_length()
    song_progress.config(to=current_track_length)
    progress_running = True

def stop_all():
    global progress_running
    if pygame.mixer.music.get_busy() and playlist_box.curselection():
        idx = playlist_box.curselection()[0]
        track_positions[idx] = current_song_pos
        pygame.mixer.music.stop()
    currently_playing.config(text="Currently Playing: None")
    cover_label.config(image='')
    progress_running = False

# ----------------------------- Drag & Delete GIF/Image -----------------------------
def upload_image():
    file = filedialog.askopenfilename(filetypes=[("Images","*.png;*.jpg;*.jpeg;*.gif")])
    if not file: return
    img = Image.open(file)
    frames = [ImageTk.PhotoImage(img.resize((150,150), Image.LANCZOS))]
    label = tk.Label(root, image=frames[0], bg=root["bg"])
    label.image_frames = frames
    label.place(x=300, y=400, anchor="center")
    images.append(label)

    def start_drag(e, lbl=label):
        lbl.startX, lbl.startY = e.x, e.y
    def do_drag(e, lbl=label):
        x = lbl.winfo_x() + (e.x - lbl.startX)
        y = lbl.winfo_y() + (e.y - lbl.startY)
        lbl.place(x=x, y=y)
    def delete_image(e, lbl=label):
        lbl.destroy()
        if lbl in images:
            images.remove(lbl)

    label.bind("<Button-1>", start_drag)
    label.bind("<B1-Motion>", do_drag)
    label.bind("<Button-3>", delete_image)

# ----------------------------- Decorations -----------------------------
def make_decorations():
    deco = THEME["deco"]
    canvas.delete("all")
    objs = []
    width, height = root.winfo_width(), root.winfo_height()
    for _ in range(20):
        x = random.randint(int(width*0.1), int(width*0.9))
        y = random.randint(int(height*0.1), int(height*0.9))
        speed = random.uniform(0.2, 1.2)
        obj = {"id": canvas.create_text(x, y, text=deco, fill=THEME["accent"],
                                        font=("Arial", 14, "bold"))}
        obj["dx"] = random.choice([-1,1])*speed
        obj["dy"] = random.choice([-1,1])*speed
        objs.append(obj)
    return objs

def animate_decorations():
    for obj in decorations:
        canvas.move(obj["id"], obj["dx"], obj["dy"])
        x, y = canvas.coords(obj["id"])
        if x<0 or x>root.winfo_width(): obj["dx"]*=-1
        if y<0 or y>root.winfo_height(): obj["dy"]*=-1
        for lbl in images:
            lx, ly = lbl.winfo_x(), lbl.winfo_y()
            lw, lh = lbl.winfo_width(), lbl.winfo_height()
            if lx < x < lx+lw and ly < y < ly+lh:
                obj["dx"]*=-1
                obj["dy"]*=-1
    root.after(50, animate_decorations)

decorations = make_decorations()
animate_decorations()
rotate_disk()

# ----------------------------- Responsive resolution -----------------------------
def change_resolution(res):
    width, height = map(int, res.split("x"))
    root.geometry(res)
    player_frame.config(width=int(width*0.4), height=int(height*0.45))
    playlist_box.config(width=int((width*0.4)/8), height=int((height*0.45)/20))
    disk_frame.grid(row=0,column=0,padx=(0,5))
    cover_frame.grid(row=0,column=2,padx=(10,0))

res_menu.bind("<<ComboboxSelected>>", lambda e: change_resolution(res_menu.get()))
volume_slider.config(command=lambda e: pygame.mixer.music.set_volume(volume_slider.get()))

# ----------------------------- Bind Buttons -----------------------------
add_btn.config(command=add_songs)
play_btn.config(command=play_selected)
stop_btn.config(command=stop_all)
upload_btn.config(command=upload_image)

# ----------------------------- Start progress bar update -----------------------------
update_progress()

root.mainloop()
