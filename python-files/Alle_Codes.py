import os
import re
import sys
import uuid
import shutil
import tempfile
import subprocess
from pathlib import Path
from collections import defaultdict
import tkinter as tk
import tkinter as tk
from tkinter import filedialog, messagebox, messagebox
from PIL import Image, ImageTk, ImageSequence
import cv2
import imagehash
import numpy as np


#Code 1:
def code1():
    print("✅ Vorschaubild(Video) läuft")
    root = tk.Tk()
    root.withdraw()
    video_path = filedialog.askopenfilename(title="Wähle ein MP4-Video", filetypes=[("MP4-Dateien", "*.mp4")])
    if not video_path:
        print("❌ Abgebrochen.")
        return
    temp_thumb = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    thumb_path = temp_thumb.name
    temp_thumb.close()
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path, "-ss", "00:00:01.000",
        "-frames:v", "1", "-q:v", "2", thumb_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(thumb_path):
        print("❌ Konnte kein Vorschaubild extrahieren.")
        return
    atomic_path = r"C:\AtomicParsleyWindows\AtomicParsley.exe"
    output_video = os.path.splitext(video_path)[0] + "_mit_cover.mp4"
    try:
        subprocess.run([
            atomic_path, video_path,
            "--artwork", thumb_path,
            "--overWrite", "--output", output_video
        ], check=True)
        os.remove(video_path)
        print(f"🗑️ Originaldatei gelöscht: {video_path}")
        print(f"✅ Fertige Datei: {output_video}")
    except subprocess.CalledProcessError as e:
        print("❌ Fehler bei AtomicParsley:", e)
    if os.path.exists(thumb_path):
        os.remove(thumb_path)
    print("🧹 Temporäre Dateien entfernt.")


#Code 2:
def code2():
    print("✅ Zufälliger Name läuft")
    VALID_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.heic',
        '.gif',
        '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm'
        }
    def is_valid_file(filename):
        return os.path.splitext(filename)[1].lower() in VALID_EXTENSIONS
    def get_all_valid_files(root_folder):
        valid_files = []
        for dirpath, _, filenames in os.walk(root_folder):
            for filename in filenames:
                if is_valid_file(filename):
                    valid_files.append(os.path.join(dirpath, filename))
        return valid_files
    def rename_files(file_paths):
        used_names = set()
        for path in file_paths:
            ext = os.path.splitext(path)[1].lower()
            new_name = None
            while not new_name or new_name in used_names:
                new_name = str(uuid.uuid4()) + ext
            used_names.add(new_name)
            new_path = os.path.join(os.path.dirname(path), new_name)
            print(f"📛 Umbenennen:\n  {path}\n-> {new_path}\n")
            shutil.move(path, new_path)
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Wähle einen Ordner")
    if not folder_selected:
        print("❌ Kein Ordner ausgewählt.")
        return
    valid_files = get_all_valid_files(folder_selected)
    if not valid_files:
        print("ℹ️ Keine passenden Dateien gefunden.")
        return
    rename_files(valid_files)
    print(f"✅ {len(valid_files)} Datei(en) wurden erfolgreich umbenannt.")


#Code 3:
def code3():
    print("✅ Doppelt(Bilder-Video) läuft")
    def choose_folder():
        root = tk.Tk()
        root.withdraw()
        return filedialog.askdirectory(title="Ordner mit Bildern und Videos wählen")
    def collect_images_and_videos(folder):
        image_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.webp')
        video_exts = ('.mp4', '.avi', '.mov', '.mkv')
        images, videos = [], []
        for root_dir, _, files in os.walk(folder):
            for file in files:
                path = os.path.join(root_dir, file)
                if file.lower().endswith(image_exts):
                    images.append(path)
                elif file.lower().endswith(video_exts):
                    videos.append(path)
        return images, videos
    def calculate_image_hash(image_path):
        try:
            img = Image.open(image_path).convert("RGB")
            return imagehash.phash(img.resize((256, 256)))
        except Exception as e:
            print(f"❌ Fehler bei Bild {image_path}: {e}")
            return None
    def extract_video_frame_hashes(video_path, max_frames=60):
        try:
            cap = cv2.VideoCapture(video_path)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            step = max(1, total // max_frames)
            hashes = []
            frames = []
            idx = 0
            while cap.isOpened() and len(hashes) < max_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if not ret:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb).resize((256, 256))
                frame_hash = imagehash.phash(pil_img)
                hashes.append(frame_hash)
                frames.append(pil_img)
                idx += step
            cap.release()
            return hashes, frames
        except Exception as e:
            print(f"❌ Fehler bei Video {video_path}: {e}")
            return [], []
    def compare_image_to_video(image_hash, video_hashes, threshold=5):
        for vh in video_hashes:
            if (image_hash - vh) <= threshold:
                return True
        return False
    def resize_keep_aspect(img, height):
        ratio = height / img.shape[0]
        width = int(img.shape[1] * ratio)
        return cv2.resize(img, (width, height))
    def open_in_explorer(path):
        try:
            if sys.platform == 'win32':
                subprocess.Popen(['explorer', '/select,', os.path.normpath(path)])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', '-R', path])
            else:
                folder = os.path.dirname(path)
                subprocess.Popen(['xdg-open', folder])
        except Exception as e:
            print(f"⚠️ Fehler beim Öffnen von {path}: {e}")
    def show_match(image_path, video_path, matching_frame):
        img1 = cv2.imread(image_path)
        img2 = cv2.cvtColor(np.array(matching_frame), cv2.COLOR_RGB2BGR)
        img1 = resize_keep_aspect(img1, 400)
        img2 = resize_keep_aspect(img2, 400)
        combined = np.hstack((img1, img2))
        win = tk.Toplevel()
        win.title("Bild-Vergleich mit Video-Frame")
        canvas = tk.Canvas(win, width=combined.shape[1], height=combined.shape[0])
        canvas.pack()
        img = Image.fromarray(cv2.cvtColor(combined, cv2.COLOR_BGR2RGB))
        photo = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        frame_info = tk.Frame(win)
        frame_info.pack(pady=10)
        left = tk.Frame(frame_info)
        left.pack(side="left", padx=20)
        tk.Label(left, text=f"🖼️ Bild:\n{image_path}", justify="left").pack(side="left")
        tk.Button(left, text="Öffnen", command=lambda: open_in_explorer(image_path)).pack(side="left", padx=5)
        right = tk.Frame(frame_info)
        right.pack(side="left", padx=20)
        tk.Label(right, text=f"🎞️ Video:\n{video_path}", justify="left").pack(side="left")
        tk.Button(right, text="Öffnen", command=lambda: open_in_explorer(video_path)).pack(side="left", padx=5)
        tk.Button(win, text="➡️ Weiter", command=win.destroy).pack(pady=10)
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"+{x}+{y}")
        win.mainloop()
    def main():
        folder = choose_folder()
        if not folder:
            print("🚫 Kein Ordner gewählt.")
            return
        images, videos = collect_images_and_videos(folder)
        print(f"🖼️ {len(images)} Bilder gefunden.")
        print(f"🎞️ {len(videos)} Videos gefunden.")
        print("\n🔑 Verarbeite Videos...")
        video_hash_map = {}
        video_frame_map = {}
        for video in videos:
            print(f"📹 {os.path.basename(video)} wird analysiert...")
            hashes, frames = extract_video_frame_hashes(video, max_frames=60)
            video_hash_map[video] = hashes
            video_frame_map[video] = frames
        print("\n🔍 Vergleiche Bilder mit Video-Frames...")
        matches = []
        for img_path in images:
            img_hash = calculate_image_hash(img_path)
            if not img_hash:
                continue
            for video_path, frame_hashes in video_hash_map.items():
                if compare_image_to_video(img_hash, frame_hashes):
                    best_dist = float('inf')
                    best_frame = None
                    for i, vh in enumerate(frame_hashes):
                        dist = img_hash - vh
                        if dist < best_dist:
                            best_dist = dist
                            best_frame = video_frame_map[video_path][i]
                    matches.append((img_path, video_path))
                    show_match(img_path, video_path, best_frame)
                    break
        if not matches:
            print("✅ Keine Übereinstimmungen zwischen Bildern und Videos gefunden.")
        else:
            print(f"\n✅ {len(matches)} Übereinstimmungen erkannt.")
    main()


#Code 4:
def code4():
    print("✅ Doppelt(Bilder) läuft")
    def choose_folder():
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory(title="Ordner auswählen")
        return folder_path
    def is_relevant_folder(folder_name):
        folder_name = folder_name.lower()
        return any(folder_name.startswith(prefix) and any(char.isdigit() for char in folder_name)
                   for prefix in ['bilder', 'story'])
    def collect_images(base_path):
        image_map = {}
        for root_dir, _, files in os.walk(base_path):
            folder = os.path.basename(root_dir)
            if is_relevant_folder(folder):
                for file in sorted(files):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                        img_path = os.path.join(root_dir, file)
                        if root_dir not in image_map:
                            image_map[root_dir] = img_path
                            break
            else:
                for file in sorted(files):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                        img_path = os.path.join(root_dir, file)
                        image_map[img_path] = img_path
                        return list(image_map.values())
    def calculate_hash(image_path):
        try:
            image = Image.open(image_path)
            if image.mode == 'P':
                image = image.convert('RGBA')
            else:
                image = image.convert('RGB')
            return imagehash.phash(image)
        except Exception as e:
            print(f"Fehler bei {image_path}: {e}")
            return None
    def compare_images(image_list, threshold=5):
        hash_map = {}
        for img in image_list:
            h = calculate_hash(img)
            if h:
                hash_map[img] = h
        checked = set()
        similar_pairs = []
        keys = list(hash_map.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                if (keys[i], keys[j]) not in checked:
                    dist = hash_map[keys[i]] - hash_map[keys[j]]
                    if dist <= threshold:
                        similar_pairs.append((keys[i], keys[j]))
                    checked.add((keys[i], keys[j]))
        return similar_pairs
    def delete_file(path):
        try:
            os.remove(path)
            print(f"🗑️ Gelöscht: {path}")
        except Exception as e:
            print(f"⚠️ Fehler beim Löschen von {path}: {e}")
    def open_in_explorer(path):
        try:
            if sys.platform == 'win32':
                subprocess.run(['explorer', '/select,', os.path.normpath(path)])
            elif sys.platform == 'darwin':
                subprocess.run(['open', '-R', path])
            else:
                folder = os.path.dirname(path)
                subprocess.run(['xdg-open', folder])
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Pfad nicht öffnen:\n{e}")

    def show_image_pair_gui(img1_path, img2_path, callback):
        win = tk.Toplevel()
        win.title("Bildvergleich")
        def load_image(path, max_height=400):
            img = Image.open(path)
            ratio = max_height / img.height
            new_size = (int(img.width * ratio), max_height)
            img = img.resize(new_size, Image.ANTIALIAS)
            return ImageTk.PhotoImage(img)
        img1 = load_image(img1_path)
        img2 = load_image(img2_path)
        frame = tk.Frame(win)
        frame.pack()
        label1 = tk.Label(frame, image=img1)
        label1.image = img1
        label1.pack(side="left", padx=10)
        label2 = tk.Label(frame, image=img2)
        label2.image = img2
        label2.pack(side="right", padx=10)
        info_frame = tk.Frame(win)
        info_frame.pack(pady=10)
        left_frame = tk.Frame(info_frame)
        left_frame.pack(side="left", padx=20)
        left_label = tk.Label(left_frame, text=f"Links:\n{img1_path}", justify="left", anchor="w")
        left_label.pack(side="left")
        left_btn = tk.Button(left_frame, text="Öffnen", command=lambda: open_in_explorer(img1_path))
        left_btn.pack(side="left", padx=5)
        right_frame = tk.Frame(info_frame)
        right_frame.pack(side="left", padx=20)
        right_label = tk.Label(right_frame, text=f"Rechts:\n{img2_path}", justify="left", anchor="w")
        right_label.pack(side="left")
        right_btn = tk.Button(right_frame, text="Öffnen", command=lambda: open_in_explorer(img2_path))
        right_btn.pack(side="left", padx=5)
        def on_action(action):
            win.destroy()
            callback(action)
        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🔴 Links löschen", command=lambda: on_action('l')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🔵 Rechts löschen", command=lambda: on_action('r')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⚫ Beide löschen", command=lambda: on_action('lr')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⏭️ Überspringen", command=lambda: on_action('')).pack(side="left", padx=5)
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"+{x}+{y}")
        win.mainloop()
    def main():
        folder = choose_folder()
        if not folder:
            print("❌ Kein Ordner gewählt.")
            return
        print("🔍 Suche nach Bildern...")
        image_list = collect_images(folder)
        print(f"📸 {len(image_list)} Bilder gefunden. Vergleiche...")
        similar = compare_images(image_list)
        if not similar:
            print("✅ Keine ähnlichen oder doppelten Bilder gefunden.")
            return
        print(f"🔁 {len(similar)} ähnliche/duplizierte Paare gefunden.")
        index = 0
        def next_pair(action=None):
            nonlocal index
            if action == 'l':
                delete_file(similar[index][0])
            elif action == 'r':
                delete_file(similar[index][1])
            elif action == 'lr':
                delete_file(similar[index][0])
                delete_file(similar[index][1])
            elif action == '':
                print("⏭️ Übersprungen.")
            index += 1
            if index < len(similar):
                show_image_pair_gui(similar[index][0], similar[index][1], next_pair)
            else:
                messagebox.showinfo("Fertig", "✅ Alle Bildpaare durchlaufen.")
                print("✅ Fertig.")
        show_image_pair_gui(similar[0][0], similar[0][1], next_pair)
    main()


#Code 5:
def code5():
    def choose_folder():
        root = tk.Tk()
        root.withdraw()
        return filedialog.askdirectory(title="Ordner mit GIFs wählen")
    def collect_gif_files(folder):
        return sorted([
            os.path.join(root, f)
            for root, _, files in os.walk(folder)
            for f in files
            if f.lower().endswith('.gif')
        ])
    def extract_gif_hashes(path, max_frames=50):
        try:
            img = Image.open(path)
            frames = [frame.copy().convert("RGB") for frame in ImageSequence.Iterator(img)]
            if len(frames) == 0:
                return []
            step = max(1, len(frames) // max_frames)
            sampled_frames = frames[::step][:max_frames]
            hashes = [imagehash.phash(f.resize((256, 256))) for f in sampled_frames]
            return hashes
        except Exception as e:
            print(f"⚠️ Fehler bei {path}: {e}")
            return []
    def sliding_hash_distance(hashes1, hashes2, max_shift=10):
        if not hashes1 or not hashes2:
            return float('inf')
        min_len = min(len(hashes1), len(hashes2))
        min_distance = float('inf')
        for shift in range(-max_shift, max_shift + 1):
            dists = []
            for i in range(min_len):
                idx1 = i
                idx2 = i + shift
                if 0 <= idx2 < len(hashes2):
                    dists.append(hashes1[idx1] - hashes2[idx2])
            if dists:
                avg_dist = np.mean(dists)
                min_distance = min(min_distance, avg_dist)
        return min_distance
    def delete_file(path):
        try:
            os.remove(path)
            print(f"🗑️ Gelöscht: {path}")
        except Exception as e:
            print(f"⚠️ Fehler beim Löschen von {path}: {e}")
    def open_in_explorer(path):
        try:
            if sys.platform == 'win32':
                subprocess.Popen(['explorer', '/select,', os.path.normpath(path)])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', '-R', path])
            else:
                folder = os.path.dirname(path)
                subprocess.Popen(['xdg-open', folder])
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Pfad nicht öffnen:\n{e}")
    def show_gif_pair_gui(path1, path2, callback):
        win = tk.Toplevel()
        win.title("GIF-Vergleich")
        def load_gif_preview(path, max_size=(300, 300)):
            try:
                img = Image.open(path)
                frame = next(ImageSequence.Iterator(img)).convert("RGBA")
                frame.thumbnail(max_size, Image.ANTIALIAS)
                return ImageTk.PhotoImage(frame)
            except Exception as e:
                print(f"⚠️ Fehler beim Laden von {path}: {e}")
                return None
        img1 = load_gif_preview(path1)
        img2 = load_gif_preview(path2)
        frame = tk.Frame(win)
        frame.pack()
        label1 = tk.Label(frame, image=img1)
        label1.image = img1
        label1.pack(side="left", padx=10)
        label2 = tk.Label(frame, image=img2)
        label2.image = img2
        label2.pack(side="right", padx=10)
        info_frame = tk.Frame(win)
        info_frame.pack(pady=10)
        left_frame = tk.Frame(info_frame)
        left_frame.pack(side="left", padx=20)
        left_label = tk.Label(left_frame, text=f"Links:\n{path1}", justify="left", anchor="w")
        left_label.pack(side="left")
        left_btn = tk.Button(left_frame, text="Öffnen", command=lambda: open_in_explorer(path1))
        left_btn.pack(side="left", padx=5)
        right_frame = tk.Frame(info_frame)
        right_frame.pack(side="left", padx=20)
        right_label = tk.Label(right_frame, text=f"Rechts:\n{path2}", justify="left", anchor="w")
        right_label.pack(side="left")
        right_btn = tk.Button(right_frame, text="Öffnen", command=lambda: open_in_explorer(path2))
        right_btn.pack(side="left", padx=5)
        def on_action(action):
            win.destroy()
            callback(action)
        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🔴 Links löschen", command=lambda: on_action('l')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🔵 Rechts löschen", command=lambda: on_action('r')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⚫ Beide löschen", command=lambda: on_action('lr')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⏭️ Überspringen", command=lambda: on_action('')).pack(side="left", padx=5)
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"+{x}+{y}")
        win.mainloop()
    def main():
        folder = choose_folder()
        if not folder:
            print("🚫 Kein Ordner gewählt.")
            return
        print("📁 Suche nach GIF-Dateien...")
        gifs = collect_gif_files(folder)
        print(f"🔍 {len(gifs)} GIFs gefunden.")
        print("🔑 Erzeuge Frame-Hashes...")
        gif_hashes = {}
        for path in gifs:
            print(f"⏳ {os.path.basename(path)} verarbeiten...")
            gif_hashes[path] = extract_gif_hashes(path, max_frames=50)
        print("🔁 Vergleiche GIFs...")
        similar_pairs = []
        paths = list(gif_hashes.keys())
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                dist = sliding_hash_distance(gif_hashes[paths[i]], gif_hashes[paths[j]], max_shift=10)
                if dist <= 5:
                    similar_pairs.append((paths[i], paths[j], dist))
        if not similar_pairs:
            print("✅ Keine ähnlichen GIFs gefunden.")
            return
        print(f"\n🔎 {len(similar_pairs)} ähnliche GIF-Paare gefunden.")
        index = 0
        def next_pair(action=None):
            nonlocal index
            if action == 'l':
                delete_file(similar_pairs[index][0])
            elif action == 'r':
                delete_file(similar_pairs[index][1])
            elif action == 'lr':
                delete_file(similar_pairs[index][0])
                delete_file(similar_pairs[index][1])
            elif action == '':
                print("⏭️ Übersprungen.")
            index += 1
            if index < len(similar_pairs):
                show_gif_pair_gui(similar_pairs[index][0], similar_pairs[index][1], next_pair)
            else:
                messagebox.showinfo("Fertig", "✅ Alle GIF-Paare durchlaufen.")
                print("✅ Fertig.")
        show_gif_pair_gui(similar_pairs[0][0], similar_pairs[0][1], next_pair)
    main()


#Code 6:
def code6():
    print("✅ Doppelt(GIF-Bilder) läuft")
    def choose_folder():
        root = tk.Tk()
        root.withdraw()
        return filedialog.askdirectory(title="Ordner mit GIFs und Bildern wählen")
    def collect_gifs_and_images(folder):
        gifs, images = [], []
        for root_dir, _, files in os.walk(folder):
            for file in files:
                path = os.path.join(root_dir, file)
                if file.lower().endswith('.gif'):
                    gifs.append(path)
                elif file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                    images.append(path)
        return gifs, images
    def extract_gif_frame_hashes(gif_path, max_frames=30):
        try:
            img = Image.open(gif_path)
            frames = [frame.copy().convert("RGB") for frame in ImageSequence.Iterator(img)]
            if not frames:
                return []
            step = max(1, len(frames) // max_frames)
            sampled = frames[::step][:max_frames]
            return [imagehash.phash(f.resize((256, 256))) for f in sampled]
        except Exception as e:
            print(f"⚠️ Fehler bei {gif_path}: {e}")
            return []
    def calculate_image_hash(image_path):
        try:
            img = Image.open(image_path).convert("RGB")
            return imagehash.phash(img)
        except Exception as e:
            print(f"⚠️ Fehler bei {image_path}: {e}")
            return None
    def compare_image_to_gif(image_hash, gif_hashes, threshold=5):
        return any((frame_hash - image_hash) <= threshold for frame_hash in gif_hashes)
    def resize_keep_aspect_cv(img, height):
        ratio = height / img.shape[0]
        width = int(img.shape[1] * ratio)
        return cv2.resize(img, (width, height))
    def pil_to_ImageTk(pil_img, max_height=400):
        ratio = max_height / pil_img.height
        new_size = (int(pil_img.width * ratio), max_height)
        resized = pil_img.resize(new_size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(resized)
    def delete_file(path):
        try:
            os.remove(path)
            print(f"🗑️ Datei gelöscht: {path}")
        except Exception as e:
            print(f"⚠️ Fehler beim Löschen von {path}: {e}")
    def open_in_explorer(path):
        try:
            if sys.platform == 'win32':
                os.startfile(os.path.normpath(path))
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', '-R', path])
            else:
                subprocess.Popen(['xdg-open', os.path.dirname(path)])
        except Exception as e:
            print(f"⚠️ Fehler beim Öffnen von {path}: {e}")
    def show_match_gui(image_path, gif_path, best_frame, callback):
        win = tk.Toplevel()
        win.title("🖼️ Bild vs GIF-Frame")
        # Lade Bild (OpenCV)
        img1 = cv2.imread(image_path)
        if img1 is None:
            messagebox.showerror("Fehler", f"Bild {image_path} konnte nicht geladen werden.")
            win.destroy()
            callback('skip')
            return
        img1 = resize_keep_aspect_cv(img1, 400)
        img1_pil = Image.fromarray(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))
        img1_tk = ImageTk.PhotoImage(img1_pil)
        # Lade besten GIF-Frame als ImageTk
        img2_tk = pil_to_ImageTk(best_frame, max_height=400)
        frame = tk.Frame(win)
        frame.pack()
        label1 = tk.Label(frame, image=img1_tk)
        label1.image = img1_tk
        label1.pack(side="left", padx=10)
        label2 = tk.Label(frame, image=img2_tk)
        label2.image = img2_tk
        label2.pack(side="right", padx=10)
        # Pfadangabe + Button
        path_frame = tk.Frame(win)
        path_frame.pack(pady=10)
        left = tk.Frame(path_frame)
        left.pack(side="left", padx=10)
        tk.Label(left, text=f"Bild:\n{image_path}", justify="left").pack(side="left")
        tk.Button(left, text="Öffnen", command=lambda: open_in_explorer(image_path)).pack(side="left", padx=5)
        right = tk.Frame(path_frame)
        right.pack(side="left", padx=10)
        tk.Label(right, text=f"GIF:\n{gif_path}", justify="left").pack(side="left")
        tk.Button(right, text="Öffnen", command=lambda: open_in_explorer(gif_path)).pack(side="left", padx=5)
        # Steuerbuttons
        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🔴 Bild löschen", command=lambda: on_action('image')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🔵 GIF löschen", command=lambda: on_action('gif')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⚫ Beide löschen", command=lambda: on_action('both')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⏭️ Überspringen", command=lambda: on_action('skip')).pack(side="left", padx=5)
        def on_action(action):
            win.destroy()
            callback(action)
        # Fenster zentrieren
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"+{x}+{y}")
        win.mainloop()
    def main():
        folder = choose_folder()
        if not folder:
            print("🚫 Kein Ordner gewählt.")
            return
        gifs, images = collect_gifs_and_images(folder)
        print(f"🎞️ {len(gifs)} GIFs gefunden.")
        print(f"🖼️ {len(images)} Bilder gefunden.")
        gif_hash_map = {}
        for gif in gifs:
            print(f"🔑 Verarbeite GIF: {os.path.basename(gif)}")
            gif_hash_map[gif] = extract_gif_frame_hashes(gif)
        print("\n🔍 Vergleiche Bilder mit GIF-Frames...")
        matches = []
        for img_path in images:
            img_hash = calculate_image_hash(img_path)
            if not img_hash:
                continue
            for gif_path, frame_hashes in gif_hash_map.items():
                if compare_image_to_gif(img_hash, frame_hashes):
                    best_frame = None
                    min_dist = float('inf')
                    gif_img = Image.open(gif_path)
                    for frame in ImageSequence.Iterator(gif_img):
                        frame_rgb = frame.convert("RGB")
                        frame_hash = imagehash.phash(frame_rgb.resize((256, 256)))
                        dist = frame_hash - img_hash
                        if dist < min_dist:
                            best_frame = frame_rgb
                            min_dist = dist
                    matches.append((img_path, gif_path, best_frame))
                    break
        if not matches:
            print("✅ Keine Übereinstimmungen zwischen GIFs und Bildern gefunden.")
        else:
            print(f"\n✅ {len(matches)} Übereinstimmungen erkannt.")
            idx = 0
            def next_match(action):
                nonlocal idx
                if idx > 0:
                    prev_img, prev_gif, _ = matches[idx - 1]
                    if action == 'image':
                        delete_file(prev_img)
                    elif action == 'gif':
                        delete_file(prev_gif)
                    elif action == 'both':
                        delete_file(prev_img)
                        delete_file(prev_gif)
                    elif action == 'skip':
                        print("⏭️ Übersprungen.")
                if idx >= len(matches):
                    messagebox.showinfo("Fertig", f"✅ Alle {len(matches)} Übereinstimmungen durchgesehen.")
                    print("✅ Fertig.")
                    return
                img_path, gif_path, best_frame = matches[idx]
                idx += 1
                show_match_gui(img_path, gif_path, best_frame, next_match)
            next_match('skip')
    main()


#Code 7:
def code7():
    def choose_folder():
        root = tk.Tk()
        root.withdraw()
        return filedialog.askdirectory(title="Ordner mit Videos wählen")
    def collect_video_files(folder):
        supported_ext = ('.mp4', '.mov', '.avi', '.mkv')
        video_files = []
        for root_dir, _, files in os.walk(folder):
            for f in files:
                if f.lower().endswith(supported_ext):
                    video_files.append(os.path.join(root_dir, f))
        return sorted(video_files)
    def get_sampled_hashes(video_path, max_frames=100):
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, total_frames // max_frames)
        hashes = []
        for i in range(0, total_frames, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                continue
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            hash_val = imagehash.phash(pil_img)
            hashes.append(hash_val)
        cap.release()
        return hashes
    def sliding_hash_distance(hashes1, hashes2, max_shift=20):
        if len(hashes1) == 0 or len(hashes2) == 0:
            return float('inf')
        min_len = min(len(hashes1), len(hashes2))
        min_distance = float('inf')
        for shift in range(-max_shift, max_shift + 1):
            dists = []
            for i in range(min_len):
                idx1 = i
                idx2 = i + shift
                if 0 <= idx2 < len(hashes2):
                    dists.append(hashes1[idx1] - hashes2[idx2])
            if dists:
                avg_dist = np.mean(dists)
                min_distance = min(min_distance, avg_dist)
        return min_distance
    def extract_first_frame(path):
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        cap.release()
        return frame if ret else None
    def resize_keep_aspect(img, height):
        ratio = height / img.shape[0]
        width = int(img.shape[1] * ratio)
        return cv2.resize(img, (width, height))
    def delete_file(path):
        try:
            os.remove(path)
            print(f"🗑️ Gelöscht: {path}")
        except Exception as e:
            print(f"⚠️ Fehler beim Löschen von {path}: {e}")
    def open_in_explorer(path):
        try:
            if sys.platform == 'win32':
                os.startfile(os.path.normpath(path))
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', '-R', path])
            else:
                subprocess.Popen(['xdg-open', os.path.dirname(path)])
        except Exception as e:
            print(f"⚠️ Fehler beim Öffnen von {path}: {e}")
    def show_video_pair_gui(path1, path2, callback):
        win = tk.Toplevel()
        win.title("🎞️ Ähnliche Videos (erster Frame)")
        def load_frame(path, max_height=400):
            frame = extract_first_frame(path)
            if frame is None:
                return None
            frame = resize_keep_aspect(frame, max_height)
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            return ImageTk.PhotoImage(img)
        img1 = load_frame(path1)
        img2 = load_frame(path2)
        frame = tk.Frame(win)
        frame.pack()
        label1 = tk.Label(frame, image=img1)
        label1.image = img1
        label1.pack(side="left", padx=10)
        label2 = tk.Label(frame, image=img2)
        label2.image = img2
        label2.pack(side="right", padx=10)
        # Pfade + Buttons
        path_frame = tk.Frame(win)
        path_frame.pack(pady=10)
        left = tk.Frame(path_frame)
        left.pack(side="left", padx=10)
        tk.Label(left, text=f"Links:\n{path1}", justify="left").pack(side="left")
        tk.Button(left, text="Öffnen", command=lambda: open_in_explorer(path1)).pack(side="left", padx=5)
        right = tk.Frame(path_frame)
        right.pack(side="left", padx=10)
        tk.Label(right, text=f"Rechts:\n{path2}", justify="left").pack(side="left")
        tk.Button(right, text="Öffnen", command=lambda: open_in_explorer(path2)).pack(side="left", padx=5)
        def on_action(action):
            win.destroy()
            callback(action)
        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🔴 Links löschen", command=lambda: on_action('l')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🔵 Rechts löschen", command=lambda: on_action('r')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⚫ Beide löschen", command=lambda: on_action('lr')).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⏭️ Überspringen", command=lambda: on_action('')).pack(side="left", padx=5)
        # Fenster zentrieren
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"+{x}+{y}")
        win.mainloop()
    def main():
        folder = choose_folder()
        if not folder:
            print("🚫 Kein Ordner gewählt.")
            return
        print("📁 Suche nach Videos...")
        videos = collect_video_files(folder)
        print(f"🔍 {len(videos)} Videos gefunden.")
        print("🔑 Erzeuge Frame-Hashes...")
        video_hashes = {}
        for path in videos:
            try:
                print(f"⏳ {os.path.basename(path)} verarbeiten...")
                video_hashes[path] = get_sampled_hashes(path, max_frames=10)
            except Exception as e:
                print(f"⚠️ Fehler bei {path}: {e}")
        print("🔁 Vergleiche Videos mit Sliding-Window...")
        similar_pairs = []
        paths = list(video_hashes.keys())
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                dist = sliding_hash_distance(video_hashes[paths[i]], video_hashes[paths[j]], max_shift=20)
                if dist <= 5:
                    similar_pairs.append((paths[i], paths[j], dist))
        if not similar_pairs:
            print("✅ Keine ähnlichen Videos gefunden.")
            return
        print(f"\n🔎 {len(similar_pairs)} ähnliche/duplizierte Paare gefunden:")
        index = 0
        def next_pair(action=None):
            nonlocal index
            if action == 'l':
                delete_file(similar_pairs[index][0])
            elif action == 'r':
                delete_file(similar_pairs[index][1])
            elif action == 'lr':
                delete_file(similar_pairs[index][0])
                delete_file(similar_pairs[index][1])
            elif action == '':
                print("⏭️ Übersprungen.")
            index += 1
            if index < len(similar_pairs):
                show_video_pair_gui(similar_pairs[index][0], similar_pairs[index][1], next_pair)
            else:
                messagebox.showinfo("Fertig", "✅ Alle Video-Paare durchlaufen.")
                print("✅ Fertig.")
        show_video_pair_gui(similar_pairs[0][0], similar_pairs[0][1], next_pair)
    main()


#Code 8:
def code8():
    print("✅ Endung Ändern(Alle) läuft")
    extension_map = {
        # Bilder
        'jpg': 'jpg',
        'jpeg': 'jpg',
        'png': 'jpg',
        'bmp': 'jpg',
        'tif': 'jpg',
        'webp': 'jpg',
        'tiff': 'jpg',
        # Videos
        'mp4': 'mp4',
        'mov': 'mp4',
        'avi': 'mp4',
        'mkv': 'mp4',
        'webm': 'mp4',
        'wmv': 'mp4',
        # GIFs
        'gif': 'gif',
    }
    def rename_extensions_in_folder(folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                name, ext = os.path.splitext(file)
                ext = ext.lower().lstrip('.')  # Dateiendung ohne Punkt und klein
                if ext in extension_map:
                    new_ext = extension_map[ext]
                    old_file_path = os.path.join(root, file)
                    new_file_path = os.path.join(root, f"{name}.{new_ext}")
                    if old_file_path != new_file_path:
                        print(f"Renaming: {old_file_path} -> {new_file_path}")
                        os.rename(old_file_path, new_file_path)
    root = tk.Tk()
    root.withdraw()  # Hauptfenster verstecken
    folder_selected = filedialog.askdirectory(title="Ordner auswählen")
    if folder_selected:
        rename_extensions_in_folder(folder_selected)
        print("Fertig!")


#Code 9:
def code9():
    def is_real_gif(filepath):
        try:
            with open(filepath, 'rb') as f:
                header = f.read(6)
                return header in [b'GIF87a', b'GIF89a']
        except Exception:
            return False
    def rename_gif_files(folder):
        renamed = 0
        for root, _, files in os.walk(folder):
            for filename in files:
                full_path = os.path.join(root, filename)
                if is_real_gif(full_path):
                    base, ext = os.path.splitext(filename)
                    if ext.lower() != '.gif':
                        new_name = base + '.gif'
                        new_path = os.path.join(root, new_name)
                        os.rename(full_path, new_path)
                        print(f"🔁 Umbenannt: {filename} ➜ {new_name}")
                        print(f"📂 Pfad:      {root}\n")
                        renamed += 1
        print(f"\n✅ Fertig. {renamed} Datei(en) umbenannt.")
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Ordner mit GIFs wählen")
    if folder:
        rename_gif_files(folder)
    else:
        print("🚫 Kein Ordner gewählt.")


#Code 10:
def code10():
    print("✅ Bestimmen läuft")
    image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp")
    last_geometry = None  # Position und Größe merken

    def is_already_named(filename):
        name, _ = os.path.splitext(filename)
        return re.match(r"^\d+(10|20|30)$", name) is not None
    def choose_folder():
        root = tk.Tk()
        root.withdraw()
        return filedialog.askdirectory(title="Wähle einen Ordner")
    def open_in_explorer(path):
        try:
            if sys.platform == 'win32':
                subprocess.run(['explorer', '/select,', os.path.normpath(path)])
            elif sys.platform == 'darwin':
                subprocess.run(['open', '-R', path])
            else:
                folder = os.path.dirname(path)
                subprocess.run(['xdg-open', folder])
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Pfad nicht öffnen:\n{e}")
    def restore_window_geometry(win):
        nonlocal last_geometry
        win.update_idletasks()
        if last_geometry:
            win.geometry(last_geometry)
        else:
            width = win.winfo_width()
            height = win.winfo_height()
            x = (win.winfo_screenwidth() // 2) - (width // 2)
            y = (win.winfo_screenheight() // 2) - (height // 2)
            win.geometry(f"{width}x{height}+{x}+{y}")
    def on_move_or_resize(event=None):
            nonlocal last_geometry
            last_geometry = win.geometry()
            win.bind("<Configure>", on_move_or_resize)
    def show_image_gui(image_path, callback):
        win = tk.Toplevel()
        win.title("Bild-Bewertung")
        try:
            img = Image.open(image_path)
            img.thumbnail((600, 600))
            tk_img = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"⚠️ Fehler beim Öffnen von {image_path}: {e}")
            callback(None, image_path)
            win.destroy()
            return
        img_label = tk.Label(win, image=tk_img)
        img_label.image = tk_img
        img_label.pack(pady=10)
        path_frame = tk.Frame(win)
        path_frame.pack(pady=5)
        path_label = tk.Label(path_frame, text=image_path, anchor="w", justify="left", wraplength=500)
        path_label.pack(side="left")
        def open_folder():
            open_in_explorer(image_path)
        open_btn = tk.Button(path_frame, text="📂 Öffnen", command=open_folder)
        open_btn.pack(side="left", padx=10)
        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=15)
        def on_choice(suffix):
            win.destroy()
            callback(suffix, image_path)
        tk.Button(btn_frame, text="10", width=10, command=lambda: on_choice("10")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="20", width=10, command=lambda: on_choice("20")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="30", width=10, command=lambda: on_choice("30")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⏭️ Überspringen", width=12, command=lambda: on_choice(None)).pack(side="left", padx=5)
        restore_window_geometry(win)
    def generate_unique_name(dirpath, suffix, ext, folder_counter):
        while True:
            candidate_number = folder_counter * 100 + int(suffix)
            new_name = f"{candidate_number}{ext}"
            new_path = os.path.join(dirpath, new_name)
            if not os.path.exists(new_path):
                return new_path
            folder_counter += 1
    def process_images(root_folder):
        image_list = []
        for dirpath, _, filenames in os.walk(root_folder):
            for file in sorted(filenames):
                if not file.lower().endswith(image_extensions):
                    continue
                if is_already_named(file):
                    continue
                full_path = os.path.join(dirpath, file)
                image_list.append(full_path)
        root = tk.Tk()
        root.withdraw()
        index = 0
        current_dir = None
        folder_counters = {}
        def process_next(choice=None, previous_path=None):
            nonlocal index, current_dir
            if choice and previous_path:
                dirpath = os.path.dirname(previous_path)
                if dirpath != current_dir:
                    current_dir = dirpath
                    folder_counters[dirpath] = 1
                ext = os.path.splitext(previous_path)[1]
                folder_counter = folder_counters.get(dirpath, 1)
                new_path = generate_unique_name(dirpath, choice, ext, folder_counter)
                try:
                    os.rename(previous_path, new_path)
                    print(f"✅ Umbenannt: {os.path.basename(previous_path)} → {os.path.basename(new_path)}")
                    folder_counters[dirpath] += 1
                except Exception as e:
                    print(f"⚠️ Fehler beim Umbenennen: {e}")
            while index < len(image_list):
                current_path = image_list[index]
                index += 1
                if os.path.exists(current_path):
                    show_image_gui(current_path, process_next)
                    return
            messagebox.showinfo("Fertig", "✅ Alle Bilder wurden durchlaufen.")
            root.quit()
        process_next()
        root.mainloop()
    folder = choose_folder()
    if folder:
        process_images(folder)
    else:
        print("❌ Kein Ordner ausgewählt.")


#Code 11:
def code11():
    print("✅ Komplett läuft")
    ALLOWED_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp',
        '.mp4', '.mov', '.avi', '.mkv'
    }
    AUTO_MODE = True  # Automatische Auswahl aktiviert
    def extract_bewertungen(filename):
        return sorted([b for b in [10, 20, 30] if str(b) in filename])
    def get_bewertung_choice(bewertungen, dateiname):
        if len(bewertungen) == 1:
            return bewertungen[0]
        if AUTO_MODE:
            return bewertungen[-1] if len(bewertungen) >= 2 else max(bewertungen)
        print(f"\nMehrere Bewertungen im Dateinamen '{dateiname}' gefunden:")
        print("Verfügbare Bewertungen:", ", ".join(map(str, bewertungen)))
        while True:
            choice = input("Welche Bewertung soll verwendet werden? (10, 20, 30): ").strip()
            if choice.isdigit() and int(choice) in bewertungen:
                return int(choice)
            print("Ungültige Eingabe, bitte erneut.")
    def extract_story_bilder_suffix(ordnername):
        m = re.match(r'^(Bilder|Story|Video) (\d+)$', ordnername, re.IGNORECASE)
        if m:
            return m.group(2)
        return ''
    def get_buchstaben_for_ordner(ordnername, ordnerpfad, cache):
        if extract_story_bilder_suffix(ordnername):
            buchstaben = ordnername[0]
            cache[ordnerpfad] = buchstaben
            return buchstaben
        if ordnerpfad in cache:
            return cache[ordnerpfad]
        parent = os.path.dirname(ordnerpfad)
        if not parent:
            buchstaben = ordnername[0]
            cache[ordnerpfad] = buchstaben
            return buchstaben
        try:
            alle_ordner = [
                d for d in os.listdir(parent)
                if os.path.isdir(os.path.join(parent, d))
            ]
        except FileNotFoundError:
            alle_ordner = []
        erster_buchstabe = ordnername[0].upper()
        ordner_mit_anfang = [d for d in alle_ordner if d.upper().startswith(erster_buchstabe)]
        if len(ordner_mit_anfang) > 1:
            ordner_mit_anfang.sort()
            print(f"Im Ordner '{parent}' gibt es mehrere Ordner, die mit '{erster_buchstabe}' beginnen:")
            print(", ".join(ordner_mit_anfang))
            buchstaben = input(f"Gib die Buchstaben für den Ordner '{ordnername}' an: ").strip()
        else:
            buchstaben = ordnername[0]
        cache[ordnerpfad] = buchstaben
        return buchstaben
    root = tk.Tk()
    root.withdraw()
    startordner = filedialog.askdirectory(title="Wähle den Startordner aus")
    if not startordner:
        print("🚫 Kein Ordner ausgewählt. Abbruch.")
        return
    startordner = os.path.abspath(startordner)
    buchstaben_cache = {}
    bewertung_counts = defaultdict(lambda: defaultdict(int))
    for rootdir, dirs, files in os.walk(startordner):
        dateien = [f for f in files if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS]
        dateien.sort()
        if not dateien:
            continue
        ordnername = os.path.basename(rootdir)
        relative_path = os.path.relpath(rootdir, os.path.dirname(startordner))
        ordnerteile = relative_path.split(os.sep)
        buchstaben_teile = []
        aktueller_pfad = os.path.dirname(startordner)
        for teil in ordnerteile:
            aktueller_pfad = os.path.join(aktueller_pfad, teil)
            buchstaben_teil = get_buchstaben_for_ordner(teil, aktueller_pfad, buchstaben_cache)
            buchstaben_teile.append(buchstaben_teil)
        buchstaben = ''.join(buchstaben_teile)
        story_suffix = extract_story_bilder_suffix(ordnername)
        bewertete_dateien = []
        for datei in dateien:
            bewertungen = extract_bewertungen(datei)
            if not bewertungen:
                print(f"Keine Bewertung in Dateiname gefunden: {datei}, überspringe Datei.")
                continue
            bewertung = get_bewertung_choice(bewertungen, datei)
            bewertete_dateien.append((bewertung, datei))
        bewertete_dateien.sort(key=lambda x: -x[0])
        for idx, (bewertung, datei) in enumerate(bewertete_dateien, start=1):
            dateipfad_alt = os.path.join(rootdir, datei)
            bewertung_counts[rootdir][bewertung] += 1
            bewertung_anzahl_str = f"{bewertung_counts[rootdir][bewertung]:02d}"
            neuer_name = f"{idx}{buchstaben}{story_suffix}{bewertung}{bewertung_anzahl_str}{os.path.splitext(datei)[1].lower()}"
            dateipfad_neu = os.path.join(rootdir, neuer_name)
            if os.path.exists(dateipfad_neu):
                print(f"⚠️ Datei existiert bereits: {dateipfad_neu}, überspringe.")
                continue
            print(f"'{datei}' → '{neuer_name}'")
            os.rename(dateipfad_alt, dateipfad_neu)
    print("✅ Fertig!")


#Code 12:
def code12():
    print("✅ Vorbereitung läuft")

    import os
    import uuid
    from pathlib import Path
    import tkinter as tk
    from tkinter import filedialog

    VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi'}
    SHORTHAND_MAP = {'3': '30', '2': '20', '1': '10'}

    def detect_categories(filename: str):
        name = filename.lower()
        found = []
        if "30" in name:
            found.append("30")
        if "20" in name:
            found.append("20")
        if "10" in name:
            found.append("10")
        return found

    def ask_user_choice(filepath: Path, options: list[str]) -> str:
        print(f"\n📂 Datei: {filepath}")
        print(f"   ➤ Enthält mehrere Kategorien: {', '.join(options)}")
        while True:
            choice = input("   ➤ Welche verwenden? (3 = 30, 2 = 20, 1 = 10): ").strip()
            if choice in SHORTHAND_MAP and SHORTHAND_MAP[choice] in options:
                return SHORTHAND_MAP[choice]
            print("   ⚠️ Ungültige Eingabe.")

    def categorize_files(folder_path: Path):
        files = sorted([f for f in folder_path.iterdir() if f.suffix.lower() in VALID_EXTENSIONS and f.is_file()])
        categorized = []

        for file in files:
            found = detect_categories(file.name)
            if len(found) == 1:
                category = found[0]
            elif len(found) > 1:
                category = ask_user_choice(file, found)
            else:
                print(f"⚠️ Keine Kategorie erkannt: {file.name}")
                continue

            categorized.append((category, file))

        return categorized

    def rename_sorted_files_two_step(categorized_files: list[tuple[str, Path]]):
        # Sortiere: 30 zuerst, dann 20, dann 10
        category_order = {"30": 0, "20": 1, "10": 2}
        categorized_files.sort(key=lambda x: category_order[x[0]])

        # 1. Schritt: Alle Dateien temporär umbenennen
        temp_names = []
        for _, file in categorized_files:
            temp_name = file.with_name(f"tmp_{uuid.uuid4().hex}{file.suffix.lower()}")
            file.rename(temp_name)
            temp_names.append(temp_name)

        # 2. Schritt: In endgültige Namen umbenennen
        counter = 1
        for (category, _), temp_file in zip(categorized_files, temp_names):
            new_name = f"{counter}{category}{temp_file.suffix.lower()}"
            new_path = temp_file.with_name(new_name)

            if new_path.exists():
                print(f"⚠️ Datei existiert bereits: {new_name} — wird übersprungen.")
            else:
                print(f"📛 Umbenennen: {temp_file.name} → {new_name}")
                temp_file.rename(new_path)

            counter += 1

    def process_directory_recursively(base_path: Path):
        for root, dirs, files in os.walk(base_path):
            folder = Path(root)
            print(f"\n📁 Bearbeite Ordner: {folder}")
            categorized = categorize_files(folder)
            if categorized:
                rename_sorted_files_two_step(categorized)

    # --- Start der Logik ---
    tk.Tk().withdraw()
    selected_folder = filedialog.askdirectory(title="Ordner auswählen")

    if not selected_folder:
        print("🚫 Kein Ordner ausgewählt.")
        return

    base_path = Path(selected_folder)
    if not base_path.exists():
        print("🚫 Pfad existiert nicht.")
        return

    process_directory_recursively(base_path)
    print("\n✅ Fertig.")



#Codes dictionary:
codes = {
    "Vorschaubild(Video)": code1,
    "Zufälliger Name": code2,
    "Doppelt(Bilder-Video)": code3,
    "Doppelte(Bilder)": code4,
    "Doppelt(GIF)": code5,
    "Doppelt(GIF-Bilder)": code6,
    "Doppelt(Video)": code7,
    "Endung Ändern(Alle)": code8,
    "Endung Ändern(GIF)": code9,
    "Bestimmen": code10,
    "Komplett": code11,
    "Vorbereitung": code12,
}

def start_code():
    auswahl = listbox.curselection()
    if not auswahl:
        messagebox.showwarning("Fehler", "Bitte einen Code auswählen!")
        return
    name = listbox.get(auswahl)
    func = codes[name]
    try:
        root.destroy()
        func()
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

root = tk.Tk()
root.title("Code Starter")
root.geometry("300x400")
label = tk.Label(root, text="Wähle einen Code:")
label.pack(pady=10)
listbox = tk.Listbox(root, height=15)
for name in codes.keys():
    listbox.insert(tk.END, name)
listbox.pack(pady=10, fill=tk.BOTH, expand=True)
start_button = tk.Button(root, text="Starten", command=start_code)
start_button.pack(pady=10)
root.mainloop()