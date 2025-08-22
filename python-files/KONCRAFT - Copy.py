#!/usr/bin/env python3
"""
Python GUI wrapper for launching Minecraft 1.7.10 (Forge) mimicking the provided .bat.

Features
- Remembers usernames in a local JSON file with dropdown selection.
- Add & delete usernames.
- Auto-installs `requests` if missing.
- Tries to auto-download a compatible JRE 8 (Temurin) if the expected JAVA folder isn't present.
- Verifies required game libraries exist before launch and shows helpful errors.

Notes
- This script does NOT download Minecraft, Forge, or any Mojang assets. It only helps you use files you already have locally.
- For Java runtime auto-download, it calls the Adoptium endpoint for the latest GA JRE 8 for Windows x64 and unzips it into ./.jre .
- Windows-only (uses javaw.exe and semicolon classpath).
"""
import json
import os
import sys
import subprocess
import threading
import zipfile
import io
import shutil
from pathlib import Path
from tkinter import Tk, StringVar, messagebox
from tkinter import N, S, E, W
from tkinter import Text
from tkinter import filedialog
from tkinter.ttk import Frame, Button, Label, Combobox

# --------------- Config derived from the .bat ---------------
APP_TITLE = "KON Launcher v1.0 (Python)"
MAX_MEM = os.environ.get("KON_MAX_MEM", "8G")
LIBRARIES = Path("natives/windows")
MAIN_CLASS = "net.minecraft.launchwrapper.Launch"
# Keep exactly the same classpath entries (relative paths)
CLASSPATH_ENTRIES = [
    "libraries/com/mojang/netty/1.8.8/netty-1.8.8.jar",
    "libraries/com/mojang/realms/1.3.5/realms-1.3.5.jar",
    "libraries/org/apache/commons/commons-compress/1.8.1/commons-compress-1.8.1.jar",
    "libraries/org/apache/httpcomponents/httpclient/4.3.3/httpclient-4.3.3.jar",
    "libraries/commons-logging/commons-logging/1.1.3/commons-logging-1.1.3.jar",
    "libraries/org/apache/httpcomponents/httpcore/4.3.2/httpcore-4.3.2.jar",
    "libraries/java3d/vecmath/1.3.1/vecmath-1.3.1.jar",
    "libraries/net/sf/trove4j/trove4j/3.0.3/trove4j-3.0.3.jar",
    "libraries/com/ibm/icu/icu4j-core-mojang/51.2/icu4j-core-mojang-51.2.jar",
    "libraries/net/sf/jopt-simple/jopt-simple/4.5/jopt-simple-4.5.jar",
    "libraries/com/paulscode/codecjorbis/20101023/codecjorbis-20101023.jar",
    "libraries/com/paulscode/codecwav/20101023/codecwav-20101023.jar",
    "libraries/com/paulscode/libraryjavasound/20101123/libraryjavasound-20101123.jar",
    "libraries/com/paulscode/librarylwjglopenal/20100824/librarylwjglopenal-20100824.jar",
    "libraries/com/paulscode/soundsystem/20120107/soundsystem-20120107.jar",
    "libraries/io/netty/netty-all/4.0.10.Final/netty-all-4.0.10.Final.jar",
    "libraries/org/apache/commons/commons-lang3/3.1/commons-lang3-3.1.jar",
    "libraries/commons-io/commons-io/2.4/commons-io-2.4.jar",
    "libraries/commons-codec/commons-codec/1.9/commons-codec-1.9.jar",
    "libraries/net/java/jinput/jinput/2.0.5/jinput-2.0.5.jar",
    "libraries/net/java/jutils/jutils/1.0.0/jutils-1.0.0.jar",
    "libraries/com/google/code/gson/gson/2.2.4/gson-2.2.4.jar",
    "libraries/com/mojang/authlib/1.5.21/authlib-1.5.21.jar",
    "libraries/org/apache/logging/log4j/log4j-api/2.0-beta9/log4j-api-2.0-beta9.jar",
    "libraries/org/apache/logging/log4j/log4j-core/2.0-beta9/log4j-core-2.0-beta9.jar",
    "libraries/org/lwjgl/lwjgl/lwjgl/2.9.1/lwjgl-2.9.1.jar",
    "libraries/org/lwjgl/lwjgl/lwjgl_util/2.9.1/lwjgl_util-2.9.1.jar",
    "libraries/org/lwjgl/lwjgl/lwjgl-platform/2.9.1/lwjgl-platform-2.9.1-natives-windows.jar",
    "libraries/net/java/jinput/jinput-platform/2.0.5/jinput-platform-2.0.5-natives-windows.jar",
    "libraries/tv/twitch/twitch/5.16/twitch-5.16.jar",
    "libraries/tv/twitch/twitch-platform/5.16/twitch-platform-5.16-natives-windows-64.jar",
    "libraries/tv/twitch/twitch-external-platform/4.5/twitch-external-platform-4.5-natives-windows-64.jar",
    "libraries/tv/twitch/twitch-external-platform/4.5/twitch-external-platform-4.5-natives-windows-64.jar",
    "libraries/net/minecraftforge/forge/1.7.10-10.13.4.1614-1.7.10/forge-1.7.10-10.13.4.1614-1.7.10.jar",
    "libraries/net/minecraft/launchwrapper/1.12/launchwrapper-1.12.jar",
    "libraries/org/ow2/asm/asm-all/5.0.3/asm-all-5.0.3.jar",
    "libraries/com/typesafe/akka/akka-actor_2.11/2.3.3/akka-actor_2.11-2.3.3.jar",
    "libraries/com/typesafe/config/1.2.1/config-1.2.1.jar",
    "libraries/org/scala-lang/scala-actors-migration_2.11/1.1.0/scala-actors-migration_2.11-1.1.0.jar",
    "libraries/org/scala-lang/scala-compiler/2.11.1/scala-compiler-2.11.1.jar",
    "libraries/org/scala-lang/plugins/scala-continuations-library_2.11/1.0.2/scala-continuations-library_2.11-1.0.2.jar",
    "libraries/org/scala-lang/plugins/scala-continuations-plugin_2.11.1/1.0.2/scala-continuations-plugin_2.11.1-1.0.2.jar",
    "libraries/org/scala-lang/scala-library/2.11.1/scala-library-2.11.1.jar",
    "libraries/org/scala-lang/scala-parser-combinators_2.11/1.0.1/scala-parser-combinators_2.11-1.0.1.jar",
    "libraries/org/scala-lang/scala-reflect/2.11.1/scala-reflect-2.11.1.jar",
    "libraries/org/scala-lang/scala-swing_2.11/1.0.1/scala-swing_2.11-1.0.1.jar",
    "libraries/org/scala-lang/scala-xml_2.11/1.0.2/scala-xml_2.11-1.0.2.jar",
    "libraries/lzma/lzma/0.0.1/lzma-0.0.1.jar",
    "libraries/net/sf/jopt-simple/jopt-simple/4.5/jopt-simple-4.5.jar",
    "libraries/com/google/guava/guava/17.0/guava-17.0.jar",
    "libraries/org/apache/commons/commons-lang3/3.3.2/commons-lang3-3.3.2.jar",
    "versions/1.7.10/1.7.10.jar",
]

JAVA_HOME_DEFAULT = Path("runtime/jre-legacy/windows-x64/jre-legacy")
USERDATA_FILE = Path("usernames.json")
JRE_INSTALL_DIR = Path(".jre")  # where we put the downloaded JRE if needed
ADOPTIUM_JRE8_WINX64_URL = (
    "https://api.adoptium.net/v3/binary/latest/8/ga/windows/x64/jre/hotspot/normal/eclipse"
)

# --------------- Helpers ---------------

def ensure_requests():
    try:
        import requests  # noqa: F401
        return
    except Exception:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])


def download_jre_if_needed(logfn):
    """Ensure we have a JAVA_HOME with javaw.exe. Prefer the batch's folder; else download Temurin 8."""
    # 1) Prefer the existing structure from the .bat
    candidate = JAVA_HOME_DEFAULT
    javaw = candidate / "bin" / "javaw.exe"
    if javaw.exists():
        return candidate

    # 2) Check if we've already installed to ./.jre
    javaw2 = JRE_INSTALL_DIR / "bin" / "javaw.exe"
    if javaw2.exists():
        return JRE_INSTALL_DIR

    # 3) Offer to auto-download
    logfn("Java runtime not found. Downloading JRE 8 (Temurin)...")
    ensure_requests()
    import requests

    JRE_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    resp = requests.get(ADOPTIUM_JRE8_WINX64_URL, timeout=120, stream=True)
    resp.raise_for_status()

    # The endpoint typically redirects to a .zip
    zip_bytes = io.BytesIO()
    for chunk in resp.iter_content(chunk_size=1024 * 256):
        if chunk:
            zip_bytes.write(chunk)
    zip_bytes.seek(0)

    with zipfile.ZipFile(zip_bytes) as zf:
        # Some archives have a top-level folder; extract all
        zf.extractall(JRE_INSTALL_DIR)

    # If the archive unpacks to a subdir, flatten to JRE_INSTALL_DIR
    # Find javaw.exe somewhere inside and reposition if needed
    found_javaw = None
    for root, dirs, files in os.walk(JRE_INSTALL_DIR):
        if "javaw.exe" in files:
            found_javaw = Path(root) / "javaw.exe"
            break
    if not found_javaw:
        raise RuntimeError("Downloaded JRE doesn't contain javaw.exe (unexpected archive layout).")

    # If javaw is not directly in .jre/bin, normalize by moving content up
    if found_javaw.parent.parent != JRE_INSTALL_DIR:
        top = Path(found_javaw).parents[1]  # this should be .../bin
        base = top.parent  # JRE root
        # Move everything from base/* into JRE_INSTALL_DIR
        for item in base.iterdir():
            dest = JRE_INSTALL_DIR / item.name
            if dest.exists():
                continue
            shutil.move(str(item), str(dest))
        # Remove the leftover top-level dir if empty
        try:
            shutil.rmtree(base, ignore_errors=True)
        except Exception:
            pass

    return JRE_INSTALL_DIR


def load_usernames():
    if USERDATA_FILE.exists():
        try:
            data = json.loads(USERDATA_FILE.read_text(encoding="utf-8"))
            return data.get("usernames", []), data.get("last_used", "")
        except Exception:
            return [], ""
    return [], ""


def save_usernames(usernames, last_used=""):
    data = {"usernames": sorted(set(usernames)), "last_used": last_used}
    USERDATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def verify_files(entries):
    missing = []
    for rel in entries:
        if not Path(rel).exists():
            missing.append(rel)
    # natives directory is needed for -Djava.library.path
    if not LIBRARIES.exists():
        missing.append(str(LIBRARIES))
    return missing


def build_classpath(entries):
    # Windows uses semicolons
    return ";".join(str(Path(p)) for p in entries)


def build_java_options(max_mem):
    opts = [
        f"-Xmx{max_mem}",
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+UseG1GC",
        "-XX:G1NewSizePercent=20",
        "-XX:G1ReservePercent=20",
        "-XX:MaxGCPauseMillis=50",
        "-XX:G1HeapRegionSize=32M",
        "-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump",
        f"-Djava.library.path={LIBRARIES}",
        "-Dminecraft.launcher.brand=java-minecraft-launcher",
        "-Dminecraft.launcher.version=unknown",
        "-Dfml.ignoreInvalidMinecraftCertificates=true",
    ]
    return opts


def build_game_args(username):
    return [
        "--version", "1.7.10",
        "--gameDir", ".",
        "--assetsDir", "assets",
        "--assetIndex", "1.7",
        "--accessToken", "1337535510N",
        "--userType", "legacy",
        "--userProperties", "{}",
        "--versionType", "release",
        "--uuid", username,
        "--username", username,
        "--tweakClass", "cpw.mods.fml.common.launcher.FMLTweaker",
    ]

# --------------- GUI ---------------
class LauncherGUI(Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        self.grid(sticky=(N, S, E, W))
        master.title(APP_TITLE)

        for i in range(0, 6):
            self.columnconfigure(i, weight=1)
        for i in range(0, 4):
            self.rowconfigure(i, weight=0)
        self.rowconfigure(4, weight=1)

        Label(self, text="Username").grid(row=0, column=0, sticky=W)
        self.username_var = StringVar()
        self.combo = Combobox(self, textvariable=self.username_var, state="normal")
        self.combo.grid(row=0, column=1, columnspan=4, sticky=(E, W), padx=6)

        self.add_btn = Button(self, text="Save Username", command=self.on_save_username)
        self.add_btn.grid(row=0, column=5, sticky=E)

        self.del_btn = Button(self, text="Delete Selected", command=self.on_delete_username)
        self.del_btn.grid(row=1, column=5, sticky=E, pady=(6, 0))

        self.detect_java_btn = Button(self, text="Locate Java…", command=self.on_locate_java)
        self.detect_java_btn.grid(row=1, column=0, sticky=W, pady=(6, 0))

        self.launch_btn = Button(self, text="Launch", command=self.on_launch)
        self.launch_btn.grid(row=1, column=1, columnspan=2, sticky=(E, W), pady=(6, 0))

        self.check_btn = Button(self, text="Verify Files", command=self.on_verify)
        self.check_btn.grid(row=1, column=3, columnspan=2, sticky=(E, W), pady=(6, 0))

        Label(self, text="Logs").grid(row=2, column=0, sticky=W, pady=(10, 0))
        self.log = Text(self, height=16)
        self.log.grid(row=3, column=0, columnspan=6, sticky=(N, S, E, W))

        # Load usernames
        self.usernames, last = load_usernames()
        self.combo["values"] = self.usernames
        if last:
            self.username_var.set(last)

        self.java_home = None

    # ---------- UI helpers ----------
    def logln(self, msg):
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.update_idletasks()

    def on_save_username(self):
        name = self.username_var.get().strip()
        if not name:
            messagebox.showwarning(APP_TITLE, "Enter a username first.")
            return
        if name not in self.usernames:
            self.usernames.append(name)
            self.combo["values"] = sorted(self.usernames)
        save_usernames(self.usernames, last_used=name)
        self.logln(f"Saved username: {name}")

    def on_delete_username(self):
        name = self.username_var.get().strip()
        if not name:
            messagebox.showwarning(APP_TITLE, "Select a username to delete.")
            return
        if name in self.usernames:
            if messagebox.askyesno(APP_TITLE, f"Delete '{name}' from saved usernames?"):
                self.usernames.remove(name)
                self.combo["values"] = sorted(self.usernames)
                if self.usernames:
                    self.username_var.set(self.usernames[0])
                else:
                    self.username_var.set("")
                save_usernames(self.usernames, last_used=self.username_var.get())
                self.logln(f"Deleted username: {name}")
        else:
            self.logln(f"Username not found: {name}")

    def on_locate_java(self):
        chosen = filedialog.askdirectory(title="Select JAVA_HOME (folder containing bin/javaw.exe)")
        if not chosen:
            return
        candidate = Path(chosen)
        if not (candidate / "bin" / "javaw.exe").exists():
            messagebox.showerror(APP_TITLE, "That folder does not contain bin/javaw.exe")
            return
        self.java_home = candidate
        self.logln(f"Using JAVA_HOME: {self.java_home}")

    def on_verify(self):
        missing = verify_files(CLASSPATH_ENTRIES)
        if missing:
            self.logln("Missing files:")
            for m in missing:
                self.logln(f"  - {m}")
            messagebox.showerror(APP_TITLE, f"{len(missing)} required files are missing. See Logs.")
        else:
            self.logln("All required classpath entries found.")
            messagebox.showinfo(APP_TITLE, "All required files are present.")

    def on_launch(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showwarning(APP_TITLE, "Please enter/select a username.")
            return
        save_usernames(self.usernames if username in self.usernames else self.usernames + [username], last_used=username)

        def worker():
            try:
                # Determine JAVA_HOME
                if self.java_home is None:
                    try:
                        self.java_home = download_jre_if_needed(self.logln)
                    except Exception as e:
                        self.logln(f"Java auto-download failed: {e}")
                        # Give the user a chance to select manually
                        self.logln("Please locate a JRE 8 manually via 'Locate Java…'")
                        messagebox.showerror(APP_TITLE, f"Java not found: {e}")
                        return

                javaw = self.java_home / "bin" / "javaw.exe"
                if not javaw.exists():
                    messagebox.showerror(APP_TITLE, f"javaw.exe not found in {self.java_home}")
                    return
                self.logln(f"Using Java: {javaw}")

                # Verify required files
                missing = verify_files(CLASSPATH_ENTRIES)
                if missing:
                    self.logln("Cannot launch. Missing files:")
                    for m in missing:
                        self.logln(f"  - {m}")
                    messagebox.showerror(APP_TITLE, "Missing required game files. See Logs.")
                    return

                classpath = build_classpath(CLASSPATH_ENTRIES)
                java_opts = build_java_options(MAX_MEM)
                game_args = build_game_args(username)

                cmd = [str(javaw)] + java_opts + ["-cp", classpath, MAIN_CLASS] + game_args
                self.logln("Launching Minecraft…")
                self.logln("Command:")
                self.logln(" ".join(cmd))

                subprocess.Popen(cmd, cwd=os.getcwd())
                self.logln("Launch command executed.")
            except Exception as e:
                self.logln(f"Error: {e}")
                messagebox.showerror(APP_TITLE, f"Launch failed: {e}")

        threading.Thread(target=worker, daemon=True).start()


# --------------- Main ---------------

def main():
    # Windows DPI awareness for crisper UI (optional)
    try:
        import ctypes
        ctypes.OleDLL("shcore").SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = Tk()
    gui = LauncherGUI(root)

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    gui.mainloop()


if __name__ == "__main__":
    main()
