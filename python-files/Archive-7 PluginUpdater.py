import os
import sys
import shutil
import json
import glob
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# -------------------------
# Plugin Migration + UBT GUI
# -------------------------
class PluginMigrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plugin Migration Tool")

        # Theme
        self.bg_color = "#121212"
        self.text_bg = "#000000"
        self.text_fg = "#39FF14"

        # paths/state
        self.uplugin_path = None
        self.destination_folder = None
        self.engine_folder_path = None
        self.target_engine_version = None

        self.root.configure(bg=self.bg_color)
        self.setup_ui()

    def setup_ui(self):
        button_style = {"bg": "#222222", "fg": self.text_fg,
                        "activebackground": "#333333", "activeforeground": self.text_fg,
                        "relief": "flat", "bd": 0}

        # Buttons
        self.uplugin_btn = tk.Button(self.root, text="Select .uplugin File",
                                     command=self.select_uplugin_file, **button_style)
        self.uplugin_btn.pack(pady=5, ipadx=10, ipady=5)

        self.destination_btn = tk.Button(self.root, text="Select Destination Folder",
                                         command=self.select_destination_folder, **button_style)
        self.destination_btn.pack(pady=5, ipadx=10, ipady=5)

        self.engine_btn = tk.Button(self.root, text="Select UE Engine Folder",
                                    command=self.select_engine_folder, **button_style)
        self.engine_btn.pack(pady=5, ipadx=10, ipady=5)

        # Log area
        self.log_area = scrolledtext.ScrolledText(self.root, width=100, height=20,
                                                  bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                                                  font=("Consolas", 11), relief="flat", bd=2)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Buttons for actions
        self.start_btn = tk.Button(self.root, text="Begin Migration (Copy & Update .uplugin)",
                                   command=self.begin_migration, **button_style)
        self.start_btn.pack(pady=6, ipadx=10, ipady=6)

        # UBT button
        self.ubt_btn = tk.Button(self.root, text="Rebuild with Unreal Build Tool (UBT)",
                                 command=self.run_unreal_build_tool, **button_style)
        self.ubt_btn.pack(pady=6, ipadx=10, ipady=6)

        # Optional: build solution button (runs msbuild/dotnet build)
        self.build_btn = tk.Button(self.root, text="Build Generated Solution (msbuild/dotnet)",
                                   command=self.build_solution, **button_style)
        self.build_btn.pack(pady=6, ipadx=10, ipady=6)

        # Keep list of buttons for convenient enabling/disabling
        self._action_buttons = [self.start_btn, self.ubt_btn, self.build_btn]

    # -------------------------
    # Utility / UI helpers
    # -------------------------
    def log(self, message):
        try:
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
        except Exception:
            # never let logging crash the app
            print("LOG ERR:", message, file=sys.stderr)

    def _set_buttons_state(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        for b in self._action_buttons:
            try:
                b.config(state=state)
            except Exception:
                pass

    # -------------------------
    # Path selection handlers
    # -------------------------
    def select_uplugin_file(self):
        path = filedialog.askopenfilename(title="Select .uplugin file", filetypes=[("UPlugin files", "*.uplugin")])
        if path:
            if not path.lower().endswith(".uplugin"):
                messagebox.showerror("Invalid file", "Please choose a .uplugin file.")
                return
            self.uplugin_path = os.path.abspath(path)
            self.log(f"Selected .uplugin file: {self.uplugin_path}")

    def select_destination_folder(self):
        folder = filedialog.askdirectory(title="Select plugin destination folder")
        if folder:
            self.destination_folder = os.path.abspath(folder)
            self.log(f"Selected destination folder: {self.destination_folder}")

    def select_engine_folder(self):
        folder = filedialog.askdirectory(title="Select UE Engine folder (e.g., .../UE_5.3)")
        if folder:
            base = os.path.basename(folder)
            # Accept also folder names that might not start with UE_ but contain version
            if base.startswith("UE_") or any(ch.isdigit() for ch in base):
                self.engine_folder_path = os.path.abspath(folder)
                # Try parse version from folder name if it starts with "UE_"
                if base.startswith("UE_"):
                    self.target_engine_version = base[3:]
                else:
                    # best-effort: take trailing numbers/dots from name
                    self.target_engine_version = base
                self.log(f"Selected engine folder: {self.engine_folder_path}")
                self.log(f"Detected target engine version (best-effort): {self.target_engine_version}")
            else:
                messagebox.showerror("Invalid Folder", "Please select a UE engine folder (folder name typically starts with 'UE_').")

    # -------------------------
    # Migration: copy plugin & update .uplugin
    # -------------------------
    def begin_migration(self):
        if not self.uplugin_path:
            messagebox.showerror("Missing", "Please select a .uplugin file.")
            return
        if not self.destination_folder:
            messagebox.showerror("Missing", "Please select a destination folder.")
            return
        if not self.engine_folder_path or not self.target_engine_version:
            messagebox.showerror("Missing", "Please select a valid UE engine folder.")
            return

        self._set_buttons_state(False)
        self.log("\n=== Starting Migration ===")
        try:
            updated = self.migrate_plugin()
            if updated:
                self.log("Migration finished: .uplugin updated to target engine version and plugin copied.")
                messagebox.showinfo("Migration", "Migration completed successfully.")
            else:
                self.log("Migration finished: plugin copied but target engine version already matched.")
                messagebox.showinfo("Migration", "Plugin copied; no version change required.")
        except Exception as exc:
            self.log(f"Migration failed: {exc}")
            messagebox.showerror("Migration Error", f"Migration failed:\n{exc}")
        finally:
            self._set_buttons_state(True)

    def migrate_plugin(self) -> bool:
        """
        Copies the plugin folder to destination and updates the .uplugin JSON.
        Returns True if plugin .uplugin required update (version changed), False otherwise.
        """
        plugin_dir = os.path.dirname(self.uplugin_path)
        plugin_filename = os.path.basename(self.uplugin_path)
        plugin_name = os.path.splitext(plugin_filename)[0]
        dest_plugin_dir = os.path.join(self.destination_folder, plugin_name)

        # Read source .uplugin JSON safely
        try:
            with open(self.uplugin_path, "r", encoding="utf-8") as f:
                ujson = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Could not read source .uplugin: {e}")

        # determine existing version (best-effort)
        existing_version = None
        if isinstance(ujson, dict):
            existing_version = ujson.get("TargetEngineVersion")
            if not existing_version:
                # fallback to EngineVersion dict
                ev = ujson.get("EngineVersion")
                if isinstance(ev, dict):
                    existing_version = f"{ev.get('Major',0)}.{ev.get('Minor',0)}"
                    if ev.get("Patch") is not None:
                        existing_version = f"{existing_version}.{ev.get('Patch')}"

        target = self.target_engine_version

        # ensure destination parent exists
        os.makedirs(self.destination_folder, exist_ok=True)

        # copy (overwrite) plugin folder to destination
        if os.path.exists(dest_plugin_dir):
            self.log(f"Destination plugin folder exists, removing: {dest_plugin_dir}")
            try:
                shutil.rmtree(dest_plugin_dir)
            except Exception as e:
                raise RuntimeError(f"Failed to remove existing destination folder: {e}")
        try:
            shutil.copytree(plugin_dir, dest_plugin_dir)
        except Exception as e:
            raise RuntimeError(f"Failed to copy plugin folder: {e}")
        self.log(f"Copied plugin to: {dest_plugin_dir}")

        # update the copied .uplugin
        dest_uplugin = os.path.join(dest_plugin_dir, plugin_filename)
        if not os.path.exists(dest_uplugin):
            raise RuntimeError(f"Copied .uplugin not found at destination: {dest_uplugin}")

        try:
            with open(dest_uplugin, "r", encoding="utf-8") as f:
                dest_json = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read destination .uplugin JSON: {e}")

        # determine whether update needed
        if existing_version and str(existing_version) == str(target):
            self.log(f"Plugin already targets engine {existing_version}. No .uplugin version change necessary.")
            return False

        # set TargetEngineVersion and EngineVersion dict (best-effort)
        dest_json["TargetEngineVersion"] = target
        parts = target.split(".")
        try:
            major = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
        except:
            major = 0
        try:
            minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        except:
            minor = 0
        try:
            patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        except:
            patch = 0
        dest_json["EngineVersion"] = {"Major": major, "Minor": minor, "Patch": patch}

        # Save file
        try:
            with open(dest_uplugin, "w", encoding="utf-8") as f:
                json.dump(dest_json, f, indent=4)
        except Exception as e:
            raise RuntimeError(f"Failed to write updated .uplugin JSON: {e}")

        self.log(f"Updated {os.path.basename(dest_uplugin)} with TargetEngineVersion = {target}")
        return True

    # -------------------------
    # UBT / Project regeneration
    # -------------------------
    def run_unreal_build_tool(self):
        """
        Attempts to run UnrealBuildTool to compile plugin target, regenerate project files,
        and optionally build the solution later with build_solution button.
        This step requires a .uproject in the tree above the plugin (project root).
        """
        if not self.uplugin_path or not self.engine_folder_path:
            messagebox.showerror("Missing", "Please select both a .uplugin file and an engine folder before running UBT.")
            return

        project_root = self.find_project_root(self.uplugin_path)
        if not project_root:
            messagebox.showerror("Project not found", "No .uproject found above the selected plugin. UBT needs a project context.")
            return

        uproject_files = glob.glob(os.path.join(project_root, "*.uproject"))
        if not uproject_files:
            messagebox.showerror("Project not found", "No .uproject found in the project root.")
            return

        uproject = os.path.abspath(uproject_files[0])
        self.log(f"\n=== UBT Step: project detected: {uproject} ===")

        self._set_buttons_state(False)
        try:
            ubt_exe = self._locate_unrealbuildtool()
            if not ubt_exe:
                self.log("UnrealBuildTool not found in engine installation. UBT step cannot run.")
                messagebox.showwarning("UBT not found", "UnrealBuildTool executable not found in the selected engine folder.")
                return

            self.log(f"Using UnrealBuildTool: {ubt_exe}")

            # Determine target name: usually the project's name or plugin-specific target.
            # We'll try project target first (project base name)
            project_name = os.path.splitext(os.path.basename(uproject))[0]

            # Build arguments for UBT. This is best-effort; UBT arguments vary by engine version.
            # We will attempt: UnrealBuildTool.exe <TargetName> <Platform> <Config> -project="<uproject>" -plugin="<path>" -progress
            platform = "Win64" if os.name == "nt" else "Linux"
            config = "Development"

            cmd = [ubt_exe, project_name, platform, config, f"-project={uproject}", f"-plugin={self.uplugin_path}", "-progress"]
            # On Windows UnrealBuildTool is a .exe and can be called directly; on Mono/DotNet you might need "dotnet" invocation.
            self.log("Running UBT (this may take a while)...")
            proc = self._run_subprocess(cmd)
            self.log(proc.stdout or "")
            if proc.returncode != 0:
                self.log(f"UBT returned exit code {proc.returncode}. stderr:\n{proc.stderr or 'none'}")
                messagebox.showwarning("UBT failed", "UnrealBuildTool returned a non-zero exit code. Check logs for details.")
            else:
                self.log("UBT completed successfully (exit code 0).")

            # After UBT, regenerate project files
            self.log("Now attempting to regenerate project files (GenerateProjectFiles).")
            self._generate_project_files(uproject)
            self.log("Project generation step complete (see logs).")

            messagebox.showinfo("UBT Step Finished", "UBT step completed (or attempted). Check logs for details.")
        except Exception as e:
            self.log(f"Error during UBT step: {e}")
            messagebox.showerror("UBT Error", f"Error during UBT step:\n{e}")
        finally:
            self._set_buttons_state(True)

    def _locate_unrealbuildtool(self):
        """
        Return a path to UnrealBuildTool executable/script if found, or None.
        Check common engine locations and fallback to engine's Binaries/Win64 or DotNET locations.
        """
        engine = self.engine_folder_path
        candidates = []

        # common windows paths
        candidates.append(os.path.join(engine, "Engine", "Binaries", "Win64", "UnrealBuildTool.exe"))
        candidates.append(os.path.join(engine, "Engine", "Binaries", "DotNET", "UnrealBuildTool.exe"))
        # older engine builds sometimes have UBT in Engine/Binaries/<platform>
        candidates.append(os.path.join(engine, "Engine", "Binaries", "Linux", "UnrealBuildTool"))
        candidates.append(os.path.join(engine, "Engine", "Binaries", "Mac", "UnrealBuildTool"))

        # also check Engine/Build/BatchFiles for RunUAT scripts and UBT wrappers
        # not exhaustive but gives decent coverage
        for c in candidates:
            if os.path.exists(c):
                return c

        # try searching a little deeper (best-effort)
        pattern = os.path.join(engine, "Engine", "Binaries", "**", "UnrealBuildTool*")
        found = glob.glob(pattern, recursive=True)
        for f in found:
            if os.path.exists(f):
                return f

        return None

    def _run_subprocess(self, cmd, shell=False, cwd=None):
        """
        Run subprocess with capture and return CompletedProcess. Use shell only when requested.
        """
        try:
            # On Windows, if cmd is a list and contains an exe path, subprocess.run works fine.
            proc = subprocess.run(cmd, capture_output=True, text=True, shell=shell, cwd=cwd)
            return proc
        except Exception as e:
            # try running via shell fallback (string)
            try:
                cmdstr = " ".join(f'"{c}"' if " " in c else c for c in cmd)
                proc = subprocess.run(cmdstr, capture_output=True, text=True, shell=True, cwd=cwd)
                return proc
            except Exception as e2:
                raise RuntimeError(f"Failed to run command: {e2}")

    def _generate_project_files(self, uproject):
        """
        Attempts to run the engine's GenerateProjectFiles script (bat/sh).
        """
        batch_dir = os.path.join(self.engine_folder_path, "Engine", "Build", "BatchFiles")
        gen_bat = os.path.join(batch_dir, "GenerateProjectFiles.bat")
        gen_sh = os.path.join(batch_dir, "GenerateProjectFiles.sh")

        if os.path.exists(gen_bat) and os.name == "nt":
            cmd = [gen_bat, f"-project={uproject}", "-game", "-engine"]
            self.log(f"Running: {gen_bat}")
            proc = self._run_subprocess(cmd, shell=True)
            self.log(proc.stdout or "")
            if proc.returncode != 0:
                self.log(f"GenerateProjectFiles.bat returned code {proc.returncode}. stderr:\n{proc.stderr}")
                return False
            return True
        elif os.path.exists(gen_sh) and os.name != "nt":
            cmd = [gen_sh, f"-project={uproject}", "-game", "-engine"]
            self.log(f"Running: {gen_sh}")
            proc = self._run_subprocess(cmd, shell=False)
            self.log(proc.stdout or "")
            if proc.returncode != 0:
                self.log(f"GenerateProjectFiles.sh returned code {proc.returncode}. stderr:\n{proc.stderr}")
                return False
            return True
        else:
            self.log("GenerateProjectFiles script not found in engine. You may need to regenerate project files from the editor or verify engine installation.")
            return False

    # -------------------------
    # Build solution (msbuild/dotnet)
    # -------------------------
    def build_solution(self):
        """
        Find a .sln in the project root and attempt to build it using msbuild or dotnet build.
        """
        if not self.uplugin_path:
            messagebox.showerror("Missing", "Please select a .uplugin file (so we can find the project).")
            return
        project_root = self.find_project_root(self.uplugin_path)
        if not project_root:
            messagebox.showerror("Project not found", "No .uproject found above the plugin.")
            return

        slns = glob.glob(os.path.join(project_root, "*.sln"))
        if not slns:
            messagebox.showwarning("No solution", "No .sln found in project root. Generate project files first.")
            return

        sln = slns[0]
        self.log(f"Found solution: {sln}")
        self._set_buttons_state(False)
        try:
            # try msbuild first
            msbuild_exe = shutil.which("msbuild") or shutil.which("MSBuild.exe")
            if msbuild_exe:
                cmd = [msbuild_exe, sln, "/m", "/p:Configuration=Development"]
                self.log(f"Running msbuild: {msbuild_exe}")
                proc = self._run_subprocess(cmd)
                self.log(proc.stdout or "")
                if proc.returncode == 0:
                    self.log("msbuild completed successfully.")
                    messagebox.showinfo("Build", "msbuild completed successfully.")
                    return
                else:
                    self.log(f"msbuild returned {proc.returncode}. stderr:\n{proc.stderr}")
                    # fall through to dotnet try
            # try dotnet build (for environments that use SDK-style projects)
            dotnet = shutil.which("dotnet")
            if dotnet:
                cmd = [dotnet, "build", sln, "--configuration", "Development"]
                self.log(f"Running dotnet build: {dotnet}")
                proc = self._run_subprocess(cmd)
                self.log(proc.stdout or "")
                if proc.returncode == 0:
                    self.log("dotnet build completed successfully.")
                    messagebox.showinfo("Build", "dotnet build completed successfully.")
                    return
                else:
                    self.log(f"dotnet build returned {proc.returncode}. stderr:\n{proc.stderr}")
            # if neither succeeded
            messagebox.showwarning("Build", "Build attempted but failed or no suitable build tool found. Check logs.")
        except Exception as e:
            self.log(f"Error building solution: {e}")
            messagebox.showerror("Build Error", f"Error building solution:\n{e}")
        finally:
            self._set_buttons_state(True)

    # -------------------------
    # Helpers
    # -------------------------
    def find_project_root(self, any_plugin_file_path):
        """
        Walk up directories from the plugin path to find a folder containing a .uproject.
        Returns path to project root or None.
        """
        current = os.path.abspath(os.path.dirname(any_plugin_file_path))
        for _ in range(12):
            candidates = glob.glob(os.path.join(current, "*.uproject"))
            if candidates:
                return current
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
        return None

# -------------------------
# Run the app
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(800, 650)
    app = PluginMigrationApp(root)
    root.mainloop()