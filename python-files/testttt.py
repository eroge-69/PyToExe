import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pygame
import os, random, io, json
from PIL import Image, ImageTk, ImageDraw, ImageOps
from mutagen.id3 import ID3, APIC

# ----------------------------- Setup -----------------------------
pygame.mixer.init()
tracks = []
track_names = []
channels = []
images = []
decorations = []

THEME = {"bg": "#1e1e1e", "fg": "#f5f5f5", "accent": "#bb86fc", "deco": "★"}
DEFAULT_VOLUME = 0.5
FONT_OPTION = ("Comic Sans MS", 12, "bold")

# ----------------------------- Root -----------------------------
root = tk.Tk()
root.title("Music Player ✨")
root.geometry("900x600")
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
    if channels and channels[0].get_busy():
        disk_angle = (disk_angle + 5) % 360
        rotated = disk_img_orig.rotate(disk_angle)
        disk_img = ImageTk.PhotoImage(rotated)
        disk_label.configure(image=disk_img)
    root.after(50, rotate_disk)

# ----------------------------- Frames -----------------------------
ui_frame = tk.Frame(root, bg=THEME["bg"])
ui_frame.place(relx=0.5, rely=0.5, anchor="center")

# Disk frame
disk_frame = tk.Frame(ui_frame, bg=THEME["bg"], width=150, height=150)
disk_frame.grid(row=0, column=0, padx=10)
disk_frame.grid_propagate(False)
disk_label = tk.Label(disk_frame, image=disk_img, bg=THEME["bg"])
disk_label.place(relx=0.5, rely=0.5, anchor="center")

# Music player panel
player_frame = tk.Frame(ui_frame, bg=THEME["bg"])
player_frame.grid(row=0, column=1, padx=10)

# Cover art frame
cover_frame = tk.Frame(ui_frame, bg=THEME["bg"], width=160, height=160)
cover_frame.grid(row=0, column=2, padx=10)
cover_frame.grid_propagate(False)
cover_label = tk.Label(cover_frame, bg=THEME["bg"])
cover_label.place(relx=0.5, rely=0.5, anchor="center")

# ----------------------------- Playlist & Labels -----------------------------
title = tk.Label(player_frame, text="🎶 Music Player 🎶", font=("Comic Sans MS", 20, "bold"),
                 bg=THEME["bg"], fg=THEME["accent"])
title.pack(pady=5)

currently_playing = tk.Label(player_frame, text="Currently Playing: None", font=("Arial", 12),
                             bg=THEME["bg"], fg=THEME["fg"])
currently_playing.pack(pady=2)

playlist_box = tk.Listbox(player_frame, height=12, width=35, selectmode="multiple",
                          font=("Arial", 12), bg="#2e2e2e", fg="white",
                          selectbackground=THEME["accent"], selectforeground=THEME["bg"])
playlist_box.pack(padx=5, pady=5)

# ----------------------------- Functions -----------------------------
def add_songs():
    files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav")])
    for f in files:
        display_name = os.path.splitext(os.path.basename(f))[0]
        playlist_box.insert("end", display_name)
        tracks.append(f)
        track_names.append(display_name)

def play_selected():
    selections = playlist_box.curselection()
    if not selections: return
    stop_all()
    idx = selections[0]
    sound = pygame.mixer.Sound(tracks[idx])
    channel = sound.play()
    channel.set_volume(volume_slider.get())
    channels.append(channel)
    currently_playing.config(text=f"Currently Playing: {track_names[idx]}")
    update_cover(tracks[idx])

def stop_all():
    for c in channels:
        if c.get_busy():
            c.stop()
    channels.clear()
    currently_playing.config(text="Currently Playing: None")
    cover_label.config(image='')

def update_cover(file_path):
    try:
        cover_img = None
        if file_path.lower().endswith(".mp3"):
            tags = ID3(file_path)
            for tag in tags.values():
                if isinstance(tag, APIC):
                    cover_img = Image.open(io.BytesIO(tag.data))
                    break
        if cover_img is None:
            cover_img = Image.new("RGBA", (150,150), (100,100,100,255))
        cover_img = ImageOps.fit(cover_img, (150,150), Image.LANCZOS)
        cover_img_tk = ImageTk.PhotoImage(cover_img)
        cover_label.config(image=cover_img_tk)
        cover_label.image = cover_img_tk
    except: cover_label.config(image='')

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
        for img_data in images:
            lx, ly = img_data["label"].winfo_x(), img_data["label"].winfo_y()
            lw, lh = img_data["label"].winfo_width(), img_data["label"].winfo_height()
            if lx < x < lx+lw and ly < y < ly+lh:
                obj["dx"]*=-1
                obj["dy"]*=-1
    root.after(50, animate_decorations)

# ----------------------------- Image/GIF Functions -----------------------------
def upload_image():
    file = filedialog.askopenfilename(filetypes=[("Images/GIFs","*.png *.jpg *.jpeg *.gif")])
    if not file: return
    img = Image.open(file)
    frames = []
    if file.lower().endswith(".gif"):
        try:
            while True:
                frame = img.copy().resize((150,150), Image.LANCZOS)
                frames.append(ImageTk.PhotoImage(frame))
                img.seek(len(frames))
        except EOFError: pass
    else:
        frame = img.resize((150,150), Image.LANCZOS)
        frames = [ImageTk.PhotoImage(frame)]
    
    label = tk.Label(root, bg=THEME["bg"])
    label.place(x=450, y=500, anchor="center")
    label.configure(image=frames[0])
    img_data = {"frames": frames, "label": label, "scale": 1.0, "path": file}
    images.append(img_data)

    label.bind("<Button-1>", lambda e, d=img_data: start_drag(e, d))
    label.bind("<B1-Motion>", lambda e, d=img_data: do_drag(e, d))
    label.bind("<Button-3>", lambda e, d=img_data: delete_image(d))

    if len(frames) > 1:
        animate_gif(img_data, 0)

def start_drag(event, img_data):
    img_data["label"].startX = event.x
    img_data["label"].startY = event.y

def do_drag(event, img_data):
    dx = event.x - img_data["label"].startX
    dy = event.y - img_data["label"].startY
    x = img_data["label"].winfo_x() + dx
    y = img_data["label"].winfo_y() + dy
    img_data["label"].place(x=x, y=y)

def delete_image(img_data):
    img_data["label"].destroy()
    images.remove(img_data)

def animate_gif(img_data, idx):
    frames = img_data["frames"]
    if frames:
        img_data["label"].configure(image=frames[idx])
        root.after(100, animate_gif, img_data, (idx+1)%len(frames))

# ----------------------------- Controls -----------------------------
controls = tk.Frame(player_frame, bg=THEME["bg"])
controls.pack(pady=5)

add_btn = tk.Button(controls, text="➕ Add Songs", command=add_songs, font=FONT_OPTION)
play_btn = tk.Button(controls, text="▶ Play", command=play_selected, font=FONT_OPTION)
stop_btn = tk.Button(controls, text="⏹ Stop All", command=stop_all, font=FONT_OPTION)
upload_btn = tk.Button(controls, text="🖼 Upload GIF/Image", command=upload_image, font=FONT_OPTION)
resolutions = ["900x600","1024x768","1280x720","1920x1080"]
res_menu = ttk.Combobox(controls, values=resolutions, font=("Comic Sans MS",11), state="readonly")
res_menu.set("900x600")
res_menu.bind("<<ComboboxSelected>>", lambda e: root.geometry(res_menu.get()))

add_btn.grid(row=0,column=0,padx=5,pady=5)
play_btn.grid(row=0,column=1,padx=5,pady=5)
stop_btn.grid(row=0,column=2,padx=5,pady=5)
upload_btn.grid(row=0,column=3,padx=5,pady=5)
res_menu.grid(row=0,column=4,padx=5,pady=5)

preset_frame = tk.Frame(player_frame, bg=THEME["bg"])
preset_frame.pack(pady=5)
save_btn = tk.Button(preset_frame, text="💾 Save Preset", command=lambda: save_preset(), font=FONT_OPTION)
load_btn = tk.Button(preset_frame, text="📂 Load Preset", command=lambda: load_preset(), font=FONT_OPTION)
save_btn.pack(side="left", padx=5)
load_btn.pack(side="left", padx=5)

# ----------------------------- Vertical Volume -----------------------------
volume_frame = tk.Frame(root, bg=THEME["bg"])
volume_frame.place(relx=0.97, rely=0.5, anchor="center")
volume_label = tk.Label(volume_frame, text="Volume", bg=THEME["bg"], fg=THEME["fg"], font=FONT_OPTION)
volume_label.pack()
volume_slider = tk.Scale(volume_frame, from_=1, to=0, resolution=0.01, orient="vertical",
                         bg=THEME["bg"], fg=THEME["fg"], length=200, font=FONT_OPTION,
                         command=lambda v: [ch.set_volume(float(v)) for ch in channels if ch.get_busy()])
volume_slider.set(DEFAULT_VOLUME)
volume_slider.pack()

# ----------------------------- Preset Functions -----------------------------
def save_preset():
    preset = {"tracks": tracks, "images":[]}
    for img in images:
        preset["images"].append({
            "path": img["path"],
            "x": img["label"].winfo_x(),
            "y": img["label"].winfo_y(),
            "scale": img["scale"]
        })
    file = filedialog.asksaveasfilename(defaultextension=".json",
                                        filetypes=[("JSON Files","*.json")])
    if file:
        with open(file,"w") as f: json.dump(preset,f)
        messagebox.showinfo("Saved","Preset saved successfully!")

def load_preset():
    global tracks, track_names, images
    file = filedialog.askopenfilename(filetypes=[("JSON Files","*.json")])
    if not file: return
    with open(file,"r") as f: preset=json.load(f)

    playlist_box.delete(0,"end")
    tracks.clear(); track_names.clear()
    for img in images: img["label"].destroy()
    images.clear()

    for t in preset["tracks"]:
        tracks.append(t)
        name=os.path.splitext(os.path.basename(t))[0]
        track_names.append(name)
        playlist_box.insert("end",name)

    for info in preset["images"]:
        img = Image.open(info["path"])
        w,h=int(150*info["scale"]),int(150*info["scale"])
        frames=[]
        if info["path"].lower().endswith(".gif"):
            try:
                while True:
                    frame=img.copy().resize((w,h),Image.LANCZOS)
                    frames.append(ImageTk.PhotoImage(frame))
                    img.seek(len(frames))
            except EOFError: pass
        else: frames=[ImageTk.PhotoImage(img.resize((w,h),Image.LANCZOS))]

        label=tk.Label(root,bg=THEME["bg"])
        label.place(x=info["x"],y=info["y"])
        label.configure(image=frames[0])
        img_data={"frames":frames,"label":label,"scale":info["scale"],"path":info["path"]}
        images.append(img_data)

        label.bind("<Button-1>", lambda e,d=img_data: start_drag(e,d))
        label.bind("<B1-Motion>", lambda e,d=img_data: do_drag(e,d))
        label.bind("<Button-3>", lambda e,d=img_data: delete_image(d))
        if len(frames)>1: animate_gif(img_data,0)

# ----------------------------- Init -----------------------------
decorations = make_decorations()
animate_decorations()
rotate_disk()

root.mainloop()
