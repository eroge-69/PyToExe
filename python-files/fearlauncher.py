import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageSequence
import os
import subprocess
import requests
import zipfile
import shutil
import psutil
import pygame
import time
import gc
import sys

class FEARManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FEAR Steam Multiplayer Fix")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        # Set window icon
        self.root.iconbitmap(self.resource_path("app_icon.ico"))  # Use resource_path for the icon

        self.game_path = ""
        self.music_playing = True

        # Initialize pygame mixer
        pygame.mixer.init()
        try:
            pygame.mixer.music.load(self.resource_path("music.mp3"))  # Use resource_path for music
            pygame.mixer.music.set_volume(0.6)  # Set volume to 60% (reduce by 40%)
            pygame.mixer.music.play(-1)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load music: {e}")

        try:
            self.button_sound = pygame.mixer.Sound(self.resource_path("button.mp3"))  # Use resource_path for button sound
            self.button_sound.set_volume(0.08)  # Set volume to 8%
        except Exception as e:
            self.button_sound = None
            messagebox.showwarning("Warning", f"Failed to load button sound: {e}")

        # Animated GIF background
        self.canvas = tk.Canvas(root, width=400, height=200, bd=0, highlightthickness=0)
        self.canvas.pack()
        self.gif_frames = self.load_gif(self.resource_path("background.gif"))  # Use resource_path for GIF
        self.current_frame = 0
        self.update_gif()  # Start updating the GIF using after()

        # Directory path entry
        self.path_entry = tk.Entry(root, width=30)
        self.path_entry.place(x=100, y=13)

        # Buttons
        button_style = {"bg": "#1E3C5A", "fg": "white", "activebackground": "#294A64", "activeforeground": "white"}
        tk.Button(root, text="Select Path", command=self.with_sound(self.select_path), **button_style).place(x=10, y=10)
        self.music_button = tk.Button(root, text="Music", command=self.with_sound(self.toggle_music), **button_style)
        self.music_button.place(x=330, y=10)
        tk.Button(root, text="Install", command=self.with_sound(self.install_files), **button_style).place(x=10, y=50)
        tk.Button(root, text="Run FEAR", command=self.with_sound(self.run_fear), **button_style).place(x=10, y=80)
        tk.Button(root, text="Run Extraction Point", command=self.with_sound(self.run_extraction_point), **button_style).place(x=10, y=110)
        tk.Button(root, text="Run Perseus Mandate", command=self.with_sound(self.run_perseus_mandate), **button_style).place(x=10, y=140)

        # Handling window close and focus properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle window close
        self.root.protocol("WM_TAKE_FOCUS", self.on_focus)

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS  # For packaged version
        except Exception:
            base_path = os.path.abspath(".")  # For development version
        return os.path.join(base_path, relative_path)

    def load_gif(self, gif_path):
        try:
            gif = Image.open(gif_path)
            # Resize GIF frames to lower resolution (400x200)
            resized_frames = [
                ImageTk.PhotoImage(frame.copy().resize((400, 200))) for frame in ImageSequence.Iterator(gif)
            ]
            return resized_frames
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GIF: {e}")
            self.root.quit()

    def update_gif(self):
        # Update the GIF every 50ms for smoother animation
        if self.gif_frames:
            frame = self.gif_frames[self.current_frame]
            self.canvas.create_image(0, 0, anchor=tk.NW, image=frame)
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)

            # Free up memory by removing frames that are no longer needed
            if self.current_frame == 0:
                # Trigger garbage collection after clearing previous frames
                self.gif_frames.clear()  # Clear previous frames
                gc.collect()  # Manually trigger garbage collection
                self.gif_frames = self.load_gif(self.resource_path("background.gif"))  # Reload the GIF frames
            
            self.root.after(50, self.update_gif)  # Call update_gif every 50ms

    def select_path(self):
        path = filedialog.askdirectory()
        if path:
            self.game_path = path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            messagebox.showinfo("Path Selected", f"Game path set to: {path}")

    def toggle_music(self):
        if pygame.mixer.music.get_busy() or not self.music_playing:
            if self.music_playing:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
            self.music_playing = not self.music_playing

    def _is_process_running(self, process_name):
        """Helper function to check if a process with a given name is running."""
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                return True
        return False

    def download_and_extract(self, url, extract_to, rename_files=None):
        try:
            filename = url.split("/")[-1]
            filepath = os.path.join(self.game_path, filename)
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(filepath, "wb") as f:
                    shutil.copyfileobj(r.raw, f)

            # Check if it's a zip file before extracting
            if zipfile.is_zipfile(filepath):
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            else:
                # If it's not a zip, move the file to the destination
                destination = os.path.join(extract_to, filename)
                if os.path.exists(destination):
                    os.remove(destination)  # Remove the existing file if it exists
                shutil.move(filepath, extract_to)

            # Rename files if necessary
            if rename_files:
                for old_name, new_name in rename_files.items():
                    old_path = os.path.join(extract_to, old_name)
                    new_path = os.path.join(extract_to, new_name)
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)

            # Clean up downloaded zip file
            os.remove(filepath)

        except zipfile.BadZipFile:
            messagebox.showerror("Error", "Downloaded file is not a valid zip file.")
        except shutil.Error as e:
            messagebox.showerror("Error", f"Failed to move the file: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download or extract: {e}")

    def download_dll(self, url, target_dirs):
        try:
            filename = url.split("/")[-1]
            for target_dir in target_dirs:
                target_path = os.path.join(target_dir, filename)
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    with open(target_path, "wb") as f:
                        shutil.copyfileobj(r.raw, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download .dll: {e}")

    def delete_existing_files(self):
        """Delete existing files or folders from the game path before installation."""
        if not self.game_path:
            return

        paths_to_delete = [
            #os.path.join(self.game_path, "FEAR108.zip"),
            #os.path.join(self.game_path, "FEAR.v1.08.NoCD.zip"),
            os.path.join(self.game_path, "EchoPatch.zip"),
            os.path.join(self.game_path, "STEAMLESS_310.zip"),
            os.path.join(self.game_path, "openspy.zip"),
            os.path.join(self.game_path, "version.dll"),
            os.path.join(self.game_path, "winmm.dll"),
            #os.path.join(self.game_path, "FEAR.exe"),
            #os.path.join(self.game_path, "FEARMP.exe"),
            #os.path.join(self.game_path, "FEARXP", "FEARXP.exe"),
            os.path.join(self.game_path, "FEARXP", "version.dll"),
            os.path.join(self.game_path, "FEARXP", "winmm.dll"),
            #os.path.join(self.game_path, "FEARXP2", "FEARXP2.exe"),
            os.path.join(self.game_path, "FEARXP2", "version.dll"),
            os.path.join(self.game_path, "FEARXP2", "winmm.dll"),
        ]

        for path in paths_to_delete:
            if os.path.exists(path):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)  # Delete directories
                    else:
                        os.remove(path)  # Delete files
                    print(f"Deleted: {path}")
                except Exception as e:
                    print(f"Failed to delete {path}: {e}")

    def install_files(self):
        if not self.game_path:
            messagebox.showerror("Error", "Please select a game path first.")
            return

        # Delete existing files before installation
        self.delete_existing_files()

        messagebox.showinfo("Please Wait", "The application may freeze, please wait until fully installed.\n\nPress OK to continue.")
        
        steps = [
            #("https://github.com/2cwldys/FEAR-Launcher/releases/download/PREREQUISITES/FEAR108.zip", self.game_path, None),
            #("https://github.com/2cwldys/FEAR-Launcher/releases/download/PREREQUISITES/FEAR.v1.08.NoCD.zip", self.game_path, None),
            ("https://github.com/2cwldys/FEAR-Launcher/releases/download/PREREQUISITES/STEAMLESS_310.zip", self.game_path, None),
            ("https://github.com/2cwldys/FEAR-Launcher/releases/download/PREREQUISITES/EchoPatch.zip", self.game_path, None),
            ("https://github.com/2cwldys/FEAR-Launcher/releases/download/PREREQUISITES/openspy.zip", self.game_path, {"openspy.x86.dll": "version.dll"}),  # Base game path
            ("https://github.com/2cwldys/FEAR-Launcher/releases/download/PREREQUISITES/openspy.zip", os.path.join(self.game_path, "FEARXP"), {"openspy.x86.dll": "version.dll"}),
            ("https://github.com/2cwldys/FEAR-Launcher/releases/download/PREREQUISITES/openspy.zip", os.path.join(self.game_path, "FEARXP2"), {"openspy.x86.dll": "version.dll"}),
        ]

        # Process all download and extraction steps
        for url, extract_to, rename_files in steps:
            self.download_and_extract(url, extract_to, rename_files)

        # Separate download for winmm.dll and place in base game path, FEARXP, and FEARXP2
        dll_url = "https://github.com/2cwldys/FEAR-Launcher/releases/download/PREREQUISITES/winmm.dll"
        self.download_dll(dll_url, [self.game_path, os.path.join(self.game_path, "FEARXP"), os.path.join(self.game_path, "FEARXP2")])

        # Deleting any remaining zip files after installation
        for url, _, _ in steps:
            zip_filename = url.split("/")[-1]
            zip_filepath = os.path.join(self.game_path, zip_filename)
            if os.path.exists(zip_filepath) and not zip_filepath.endswith(".dll"):  # Ensure DLLs are not deleted
                os.remove(zip_filepath)

        # Handle Steamless DRM removal & deletion thereafter
        self.handle_steamless()
        self.remove_steamless()

        # Delete openspy.x64.dll if it exists in base path, FEARXP, and FEARXP2
        self.delete_openspy_dll()

        messagebox.showinfo("Installation Completed", "Installation completed successfully.")
        
        messagebox.showinfo("Important Info", 
                    "Multiplayer functionality is now compatible with Openspy!\n\n"
                    "You must run FEAR.exe.unpacked in your Steamapps/Common/FEAR directory in order to play.\n\n"
                    "Launching through steam by default will not work!")

    def delete_openspy_dll(self):
        # Delete openspy.x64.dll if it exists in base path, FEARXP, and FEARXP2
        for folder in ["", "FEARXP", "FEARXP2"]:
            dll_path = os.path.join(self.game_path, folder, "openspy.x64.dll")
            if os.path.exists(dll_path):
                try:
                    os.remove(dll_path)
                    print(f"Deleted: {dll_path}")
                except Exception as e:
                    print(f"Failed to delete {dll_path}: {e}")

    def handle_steamless(self):
        """
        Runs Steamless.CLI.exe on the specified game executables.
        """
        # 1. Define the path to the Steamless tool.
        #    It's assumed to be in the root of the game directory.
        steamless_cli_path = os.path.join(self.game_path, "Steamless.CLI.exe")

        # 2. Check if Steamless.CLI.exe exists before proceeding.
        if not os.path.exists(steamless_cli_path):
            print("Error: Steamless.CLI.exe not found. Cannot perform the requested operation.")
            return

        # 3. Define the target executables and their corresponding sub-folders.
        #    The key is the executable name, and the value is its directory.
        targets = {
            "FEAR.exe": ""
        }

        print("Starting Steamless processing...")

        # 4. Iterate through the targets and run the command for each one.
        for exe_name, sub_folder in targets.items():
            print(f"\nProcessing: {exe_name}")
            
            # Construct the full path to the target executable.
            exe_path = os.path.join(self.game_path, sub_folder, exe_name)

            # 5. Check if the target executable exists before trying to process it.
            if not os.path.exists(exe_path):
                print(f"Warning: {exe_name} not found at '{exe_path}'. Skipping.")
                continue

            # 6. Run the subprocess command.
            try:
                # subprocess.run is the modern way to run external commands.
                # It takes a list of strings for the command and its arguments.
                # 'check=True' will raise an exception if the command returns a non-zero exit code.
                # 'capture_output=True' will save stdout and stderr.
                # 'text=True' decodes the output as text.
                result = subprocess.run(
                    [steamless_cli_path, exe_path],
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                # Print success message and the output from Steamless.CLI.exe
                print(f"Successfully processed {exe_name}.")
                if result.stdout:
                    print("--- Steamless Output ---")
                    print(result.stdout.strip())
                
            except FileNotFoundError:
                print(f"Error: The command failed because '{steamless_cli_path}' or '{exe_path}' was not found.")
            except subprocess.CalledProcessError as e:
                # This block handles non-zero exit codes from the command.
                print(f"Error: Steamless failed for {exe_name} with exit code {e.returncode}.")
                print("--- Error Output ---")
                print(e.stderr.strip())
            except Exception as e:
                # Catch any other unexpected errors.
                print(f"An unexpected error occurred while processing {exe_name}: {e}")

        print("\nSteamless processing complete.")

    def remove_steamless(self):
        # Delete steamless contents

        # Wait until the process has finished
        process_name = "Steamless.CLI.exe"
        if self._is_process_running(process_name):
            print(f"Waiting for '{process_name}' to close before deleting files...")
            while self._is_process_running(process_name):
                time.sleep(1) # Wait for 1 second before checking again
            print(f"'{process_name}' has closed. Proceeding with file deletion.")

        content_to_remove = ["ExamplePlugin.zip", "Steamless.CLI.exe", "Steamless.CLI.exe.config", "Steamless.exe", "Steamless.exe.config"]
        plugins_folder = "Plugins"
        
        for folder in [""]:
            for file_name in content_to_remove:
                file_path = os.path.join(self.game_path, folder, file_name)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")

        plugins_path = os.path.join(self.game_path, plugins_folder)
        if os.path.exists(plugins_path) and os.path.isdir(plugins_path):
            try:
                # Use shutil.rmtree to remove the folder and all its contents
                shutil.rmtree(plugins_path)
                print(f"Deleted entire folder: {plugins_path}")
            except Exception as e:
                print(f"Failed to delete folder {plugins_path}: {e}")

    def run_fear(self):
        if not self.game_path:
            messagebox.showerror("Error", "Please select a game path first.")
            return

        os.startfile("steam://run/21090") # Run FEAR via Steam URL

    def run_extraction_point(self):
        if not self.game_path:
            messagebox.showerror("Error", "Please select a game path first.")
            return

        os.startfile("steam://run/21110")  # Run Extraction Point via Steam URL

    def run_perseus_mandate(self):
        if not self.game_path:
            messagebox.showerror("Error", "Please select a game path first.")
            return

        os.startfile("steam://run/21120")  # Run Perseus Mandate via Steam URL

    def with_sound(self, func):
        def wrapper(*args, **kwargs):
            if self.button_sound:
                self.button_sound.play()  # Play button sound
            return func(*args, **kwargs)
        return wrapper

    def on_focus(self):
        self.root.lift()

    def on_close(self):
        # Exit gracefully
        pygame.mixer.music.stop()
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = FEARManagerApp(root)
    root.mainloop()