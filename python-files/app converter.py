Python 3.13.1 (tags/v3.13.1:0671451, Dec  3 2024, 19:06:28) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import pygame
... import tkinter as tk
... from tkinter import filedialog
... import zipfile
... import os
... import shutil
... import tempfile
... import subprocess
... 
... # Initialize Pygame
... pygame.init()
... screen = pygame.display.set_mode((500, 300))
... pygame.display.set_caption("Game App Builder")
... font = pygame.font.SysFont(None, 28)
... 
... # Colors
... WHITE = (255, 255, 255)
... BLUE = (70, 130, 180)
... GRAY = (220, 220, 220)
... 
... def draw_button(text, rect, color):
...     pygame.draw.rect(screen, color, rect)
...     txt = font.render(text, True, WHITE)
...     screen.blit(txt, (rect.x + 20, rect.y + 10))
... 
... def show_message(msg):
...     screen.fill(GRAY)
...     txt = font.render(msg, True, BLUE)
...     screen.blit(txt, (20, 250))
...     pygame.display.flip()
... 
... def build_app(zip_path):
...     temp_dir = tempfile.mkdtemp()
...     try:
...         # Extract ZIP contents
...         with zipfile.ZipFile(zip_path, 'r') as zip_ref:
...             zip_ref.extractall(temp_dir)

        # Find the first .py file
        py_files = []
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))

        if not py_files:
            show_message("No .py file found.")
            return

        main_path = py_files[0]
        main_script_name = os.path.basename(main_path)

        # Preserve original folder structure for assets
        zip_root = os.path.dirname(main_path)
        add_data = []
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(".png"):
                    full_path = os.path.join(root, file)
                    filename = os.path.basename(full_path)

    # If it's the sprite sheet, place it at the root
                    if filename in ["Player_Sprite_Sheet.png", "Player_Sprite_Sheet_Custom.png"]:
                        rel_path = filename
                    else:
                        rel_path = os.path.relpath(full_path, zip_root)

                    add_data += ["--add-data", f"{full_path}{os.pathsep}{rel_path}"]


        # Check for icon.ico
        icon_path = None
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.lower() == "icon.ico":
                    icon_path = os.path.join(root, file)
                    break

        # Build PyInstaller command
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            *add_data,
        ]

        if icon_path:
            cmd += ["--icon", icon_path]

        cmd.append(main_path)

        result = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True)
        if result.returncode != 0:
            print("PyInstaller error:", result.stderr)
            show_message("PyInstaller failed.")
            return

        # Locate the executable
        exe_name = os.path.splitext(main_script_name)[0]
        dist_path = os.path.join(temp_dir, "dist", exe_name + (".exe" if os.name == "nt" else ""))
        if os.path.exists(dist_path):
            shutil.move(dist_path, os.path.join(os.getcwd(), os.path.basename(dist_path)))
            show_message("✓ App built successfully!")
        else:
            show_message("Build failed.")
    finally:
        shutil.rmtree(temp_dir)

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])

# Main loop
running = True
button_rect = pygame.Rect(150, 100, 200, 50)
while running:
    screen.fill(GRAY)
    draw_button("Upload ZIP", button_rect, BLUE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                zip_file = open_file_dialog()
                if zip_file:
                    show_message("Building app...")
                    pygame.display.flip()
                    build_app(zip_file)
    pygame.display.flip()

pygame.quit()
