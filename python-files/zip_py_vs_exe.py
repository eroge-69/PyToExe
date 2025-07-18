import streamlit as st
import zipfile, os, tempfile, shutil, subprocess, datetime, io
from pathlib import Path

# --- PDF Utilities (Ensure reportlab is installed: pip install reportlab) ---
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf_report(log_text:str, timestamp:str, project_name:str, output_path:io.BytesIO):
    """
    Generates a simple PDF report of the compilation logs.
    """
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)
    c.drawString(72, height - 72, "ErnestMind.ai - Compilation Report")
    c.drawString(72, height - 92, f"Project: {project_name}")
    c.drawString(72, height - 112, f"Date/Time: {timestamp}")
    
    text_object = c.beginText(72, height - 140)
    text_object.setFont("Helvetica", 10) 
    y_position = height - 140
    line_height = 12 # Approximate height of each line

    lines = log_text.splitlines()
    for line in lines:
        # Check if there's enough space for the next line
        if y_position < 72 + line_height: # 72 is bottom margin, add line_height to ensure space for next line
            c.drawText(text_object)
            c.showPage()
            text_object = c.beginText(72, height - 72) # Start new page from top margin
            text_object.setFont("Helvetica", 10)
            y_position = height - 72
        
        text_object.textLine(line)
        y_position -= line_height # Move down for the next line
        
    c.drawText(text_object)
    c.save()

# -------- LANGUAGE SYSTEM ----------
LANGS = {
    "fr": {
        "title": "Convertisseur Python vers EXE (ErnestMind Pro)",
        "upload_file": "Téléverser votre fichier .py ou ZIP de projet Python ici",
        "compile_button": "Compiler en .exe",
        "download_ready": "Téléchargement prêt !",
        "download_exe": "Télécharger le fichier .exe",
        "download_zip": "Télécharger le package complet (.zip)",
        "help": "Aide",
        "help_content": """
### Comment utiliser ?
1.  **Téléversez votre fichier/projet Python :**
    * Un fichier `.py` unique.
    * Un fichier `.zip` contenant un projet Python (avec un `main.py` à la racine ou dans un sous-dossier).
    * Un fichier `.zip` batch (plusieurs dossiers Python, chacun avec un `main.py`).
    **Pour les projets avec dépendances :** Si votre projet Python utilise des bibliothèques externes (ex: `pandas`, `requests`, `streamlit`), assurez-vous d'inclure un fichier `requirements.txt` à la racine de votre ZIP. Le système l'installera automatiquement avant la compilation.
2.  Cliquez sur "Compiler en .exe". Le système détectera automatiquement le type de projet.
3.  Une fois compilé, téléchargez le `.exe` ou le package complet `.zip` contenant votre exécutable et d'autres fichiers utiles (README, rapport de compilation).

**Astuce pour compiler cette application en EXE :**
Cette application Streamlit elle-même est un projet Python. Pour la compiler en EXE, vous devriez :
1.  Créer un fichier `main.py` qui contient le code de cette application.
2.  Créer un fichier `requirements.txt` avec les dépendances nécessaires : `streamlit`, `nuitka`, `reportlab`, etc.
3.  Zipper ces deux fichiers (`main.py` et `requirements.txt`) dans un fichier `mon_app_convertisseur.zip`.
4.  Téléverser ce `mon_app_convertisseur.zip` dans cette même application et compiler !
        """,
        "about": "À propos",
        "about_content": """
**ErnestMind.ai – Moteur de conversion Python professionnel**

Cette application transforme localement vos projets Python en `.exe` autonomes, sans connexion externe.

🛡️ 100% local – Aucun Cloud  
🛠️ Développé par ErnestMind.ai  
📍 Version 3.0 – 2025
        """,
        "error_file": "Veuillez téléverser un fichier Python (.py) ou un fichier ZIP valide.",
        "error_zip_single_py": "Le fichier ZIP pour un projet Python unique doit contenir un `main.py` ou un seul fichier `.py`.",
        "error_zip_batch_py": "Aucun projet Python valide (dossier avec main.py) détecté dans le fichier ZIP batch.",
        "error_compile": "Erreur lors de la compilation. Veuillez vérifier les logs détaillés.",
        "success_compile_single": "Compilation terminée avec succès pour le projet unique.",
        "success_compile_batch": "Compilation batch Python terminée avec succès.",
        "building_single": "🔧 Préparation et compilation du projet unique en cours...",
        "building_batch": "🔧 Préparation et compilation des projets batch Python en cours...",
        "log_preview": "Afficher les logs détaillés de compilation",
        "timestamp": "Horodatage",
        "pdf_report": "Rapport PDF",
        "branding_notice": "Le package final contient le logo ErnestMind.ai et un README",
        "compiling_project": "Compilation de : ",
        "build_report_for": "Rapport de build pour : ",
        "error_no_main_in_project": "Le projet {project_name} ne contient pas de `main.py` valide.",
        "installing_deps": "Installation des dépendances (requirements.txt)...",
        "deps_installed": "Dépendances installées avec succès.",
        "deps_error": "Erreur lors de l'installation des dépendances : ",
        "no_deps_file": "Aucun fichier requirements.txt trouvé. Poursuite sans installation de dépendances.",
        "cleaning_up": "Nettoyage des fichiers temporaires...",
        "cleaning_done": "Nettoyage terminé.",
        "extracting_zip": "Extraction du fichier ZIP...",
        "detecting_project_type": "Détection du type de projet...",
        "preparing_project": "Préparation du projet...",
        "building_exe": "Construction de l'exécutable...",
        "exe_not_found": "Exécutable non trouvé après la compilation.",
        "preparing_assets": "Préparation des assets et de l'icône...",
        "error_icon_assets": "Erreur lors de la gestion de l'icône ou des assets : ",
        "finalizing_package": "Finalisation du package...",
        "package_ready": "Package prêt au téléchargement."
    },
    "en": {
        "title": "Python to EXE Converter (ErnestMind Pro)",
        "upload_file": "Upload your .py file or Python project ZIP here",
        "compile_button": "Compile to .exe",
        "download_ready": "Download ready!",
        "download_exe": "Download .exe file",
        "download_zip": "Download full package (.zip)",
        "help": "Help",
        "help_content": """
### How to use?
1.  **Upload your Python file/project:**
    * A single `.py` file.
    * A `.zip` file containing a Python project (with a `main.py` at the root or in a subfolder).
    * A batch `.zip` file (multiple Python folders, each with a `main.py`).
    **For projects with dependencies:** If your Python project uses external libraries (e.g., `pandas`, `requests`, `streamlit`), make sure to include a `requirements.txt` file at the root of your ZIP. The system will automatically install it before compilation.
2.  Click "Compile to .exe". The system will automatically detect the project type.
3.  Once compiled, download the `.exe` or the full `.zip` package containing your executable and other useful files (README, build report).

**Tip for compiling this app to EXE:**
This Streamlit app itself is a Python project. To compile it to EXE, you would:
1.  Create a `main.py` file containing the code of this application.
2.  Create a `requirements.txt` file with the necessary dependencies: `streamlit`, `nuitka`, `reportlab`, etc.
3.  Zip these two files (`main.py` and `requirements.txt`) into a `my_converter_app.zip`.
4.  Upload this `my_converter_app.zip` into this very application and compile!
        """,
        "about": "About",
        "about_content": """
**ErnestMind.ai – Professional Python Compiler**

This app converts your Python projects into standalone `.exe`s, fully offline.

🛡️ 100% local – No Cloud  
🛠️ Powered by ErnestMind.ai  
📍 Version 3.0 – 2025
        """,
        "error_file": "Please upload a valid Python (.py) file or ZIP file.",
        "error_zip_single_py": "The ZIP for a single Python project must contain a `main.py` or a single `.py` file.",
        "error_zip_batch_py": "No valid Python project (folder with main.py) detected in the batch ZIP.",
        "error_compile": "Error during compilation. Please check detailed logs.",
        "success_compile_single": "Single project compilation completed successfully.",
        "success_compile_batch": "Python batch compilation completed successfully.",
        "building_single": "🔧 Preparing and compiling single project...",
        "building_batch": "🔧 Preparing and compiling Python batch projects...",
        "log_preview": "Show detailed compilation logs",
        "timestamp": "Timestamp",
        "pdf_report": "PDF Report",
        "branding_notice": "Final package includes ErnestMind.ai logo and README",
        "compiling_project": "Compiling: ",
        "build_report_for": "Build report for: ",
        "error_no_main_in_project": "Project {project_name} does not contain a valid `main.py`.",
        "installing_deps": "Installing dependencies (requirements.txt)...",
        "deps_installed": "Dependencies installed successfully.",
        "deps_error": "Error installing dependencies: ",
        "no_deps_file": "No requirements.txt file found. Proceeding without dependency installation.",
        "cleaning_up": "Cleaning up temporary files...",
        "cleaning_done": "Cleaning done.",
        "extracting_zip": "Extracting ZIP file...",
        "detecting_project_type": "Detecting project type...",
        "preparing_project": "Preparing project...",
        "building_exe": "Building executable...",
        "exe_not_found": "Executable non trouvé après la compilation.",
        "preparing_assets": "Preparing assets and icon...",
        "error_icon_assets": "Error handling icon or assets: ",
        "finalizing_package": "Finalizing package...",
        "package_ready": "Package ready for download."
    }
}

# -------- APP ----------
def main():
    if 'lang' not in st.session_state:
        st.session_state.lang = "fr"
    
    st.sidebar.title("🌐 Langue / Language")
    st.session_state.lang = st.sidebar.selectbox("", ["fr", "en"], index=["fr", "en"].index(st.session_state.lang))
    T = LANGS[st.session_state.lang]

    # Streamlit page configuration
    st.set_page_config(page_title=T["title"], layout="centered")
    
    # CSS style for a more stylish and fast interface
    st.markdown("""
        <style>
        /* Centering the main content */
        .stApp {
            text-align: center;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 800px; /* Limit width for better readability */
            margin-left: auto;
            margin-right: auto;
        }
        /* Title style */
        h1 {
            color: #4CAF50; /* Green for main title */
            font-size: 2.5em;
            margin-bottom: 0.5em;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        /* Subtitle and info style */
        .st-emotion-cache-10qj07v p { /* Target st.info text */
            font-size: 1.1em;
            color: #333;
        }
        /* Button style */
        .stButton>button {
            background-color: #007BFF; /* Bright blue */
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            font-weight: bold;
            font-size: 1.1em;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
            width: 100%;
            margin-top: 15px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        }
        .stButton>button:hover {
            background-color: #0056b3; /* Darker blue on hover */
            transform: translateY(-2px);
        }
        /* File uploader style */
        .st-emotion-cache-1iy8w7v { /* Target st.file_uploader */
            border: 2px dashed #007BFF;
            border-radius: 10px;
            padding: 20px;
            background-color: #f0f8ff; /* Very light blue */
        }
        /* Info message style */
        .st-emotion-cache-10qj07v { /* Target st.info */
            background-color: #e6f7ff; /* Very light blue */
            border-left: 5px solid #2196F3; /* Blue border */
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        /* Success message style */
        .st-emotion-cache-10qj07v.stAlert.stSuccess { /* Target st.success */
            background-color: #e8f5e9; /* Very light green */
            border-left: 5px solid #4CAF50; /* Green border */
        }
        /* Error message style */
        .st-emotion-cache-10qj07v.stAlert.stError { /* Target st.error */
            background-color: #ffebee; /* Very light red */
            border-left: 5px solid #F44336; /* Red border */
        }
        /* Progress bar style */
        .stProgress > div > div > div > div {
            background-color: #4CAF50; /* Green for progress */
        }
        </style>
    """, unsafe_allow_html=True)

    logo_url = "https://i.postimg.cc/FRjs6pNz/logo-ernestmind-png.png"
    st.image(logo_url, width=200)
    st.title("🛠️ " + T["title"])

    source_language = "Python" # Hardcoded to Python as requested
    
    uploaded_file = st.file_uploader(T["upload_file"], type=["py", "zip"])

    # Default options (simplified)
    exe_name_default = "converted_app"
    console_mode_default = True # By default, show console for debugging
    add_readme_default = True
    readme_content_default = "Package generated by ErnestMind.ai - 2025"
    pdf_report_opt_default = True
    
    # Placeholder for logs
    logs_placeholder = st.empty()
    full_session_log = ""

    @st.cache_data(show_spinner=False)
    def install_dependencies(project_path, _logs_area):
        """
        Installs dependencies listed in requirements.txt if the file exists.
        """
        req_path = os.path.join(project_path, "requirements.txt")
        if os.path.exists(req_path):
            _logs_area.info(T["installing_deps"])
            try:
                pip_command = [os.sys.executable, "-m", "pip", "install", "-r", req_path]
                process = subprocess.Popen(pip_command, cwd=project_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='ignore')
                
                log_output = ""
                for line in process.stdout:
                    log_output += line
                    _logs_area.write(line) # Real-time display in logs
                process.wait()

                if process.returncode == 0:
                    _logs_area.success(T["deps_installed"])
                    return True, log_output
                else:
                    _logs_area.error(f"{T['deps_error']} {log_output}")
                    return False, log_output
            except Exception as e:
                _logs_area.error(f"{T['deps_error']} {e}")
                return False, str(e)
        else:
            _logs_area.info(T["no_deps_file"])
            return True, T["no_deps_file"]

    def prepare_project_py(base_path, input_path, _logs_area):
        """
        Prepares the Python project in a temporary folder.
        Handles copying the script/folder, and installing dependencies.
        Returns the staging folder path, if it's a valid project, and the main script path.
        """
        _logs_area.info(T["preparing_project"])
        project_name = Path(input_path).name.replace(".py", "") if str(input_path).endswith(".py") else Path(input_path).name
        project_path = os.path.join(base_path, "py_project_staging", project_name)
        os.makedirs(project_path, exist_ok=True)

        main_script = ""

        if Path(input_path).is_file() and str(input_path).endswith(".py"):
            shutil.copy(input_path, os.path.join(project_path, "main.py"))
            main_script = os.path.join(project_path, "main.py")
        elif Path(input_path).is_dir():
            shutil.copytree(input_path, project_path, dirs_exist_ok=True)
            # Search for main.py at the root or in a subfolder
            found_main = False
            for root, _, files in os.walk(project_path):
                if "main.py" in files:
                    main_script = os.path.join(root, "main.py")
                    # If main.py is not at the root of the staging folder, adjust project_path
                    if Path(root) != Path(project_path):
                        # Copy the content of the subfolder containing main.py to the root of staging
                        # to simplify Nuitka compilation
                        temp_sub_dir = os.path.join(base_path, "temp_sub_dir")
                        shutil.copytree(root, temp_sub_dir)
                        shutil.rmtree(project_path)
                        shutil.move(temp_sub_dir, project_path)
                        main_script = os.path.join(project_path, "main.py")
                    found_main = True
                    break
            if not found_main:
                # If only one .py is in the zip and no main.py, rename it to main.py
                py_files = [f for f in os.listdir(project_path) if f.endswith(".py")]
                if len(py_files) == 1:
                    original_py_path = os.path.join(project_path, py_files[0])
                    new_main_path = os.path.join(project_path, "main.py")
                    os.rename(original_py_path, new_main_path)
                    main_script = new_main_path
                else:
                    _logs_area.error(T["error_no_main_in_project"].format(project_name=project_name))
                    return None, False, "", ""
        
        if not main_script or not os.path.exists(main_script):
            _logs_area.error(T["error_no_main_in_project"].format(project_name=project_name))
            return None, False, "", ""

        deps_success, deps_log = install_dependencies(project_path, _logs_area)
        if not deps_success:
            return None, False, "", deps_log

        return project_path, True, main_script, deps_log

    @st.cache_data(show_spinner=False)
    def build_exe(language, project_path, main_script, exe_output_name, icon_path=None, console=True, _logs_area=None):
        """
        Executes the compilation command (Nuitka) and captures logs.
        """
        _logs_area.info(T["building_exe"])
        build_log = ""
        success = False
        try:
            # Nuitka places its output in the current working directory, not a 'dist' folder like PyInstaller.
            # We will look for the .exe directly in project_path.
            
            # Clean up previous Nuitka build artifacts
            nuitka_cache_dir = os.path.join(Path.home(), ".cache", "nuitka")
            if os.path.exists(nuitka_cache_dir):
                shutil.rmtree(nuitka_cache_dir, ignore_errors=True)

            # Nuitka creates a .build folder and the executable directly in cwd.
            # We remove them if they exist from a previous run to ensure clean build.
            # Executable name will be `exe_output_name.exe`
            existing_exe = os.path.join(project_path, f"{exe_output_name}.exe")
            existing_build_dir = os.path.join(project_path, f"{exe_output_name}.build")
            
            if os.path.exists(existing_exe): shutil.remove(existing_exe)
            if os.path.exists(existing_build_dir): shutil.rmtree(existing_build_dir)
            
            cmd = [
                os.sys.executable, # Use the current Python executable to run Nuitka module
                "-m",
                "nuitka",
                "--standalone", # Create a standalone executable
                "--onefile",    # Package into a single file
                f"--output-filename={exe_output_name}.exe" # Set the output executable name
            ]
            if not console:
                cmd.append("--windows-disable-console") # Do not show console window on Windows
            if icon_path and os.path.exists(icon_path):
                cmd.append(f"--windows-icon-file={icon_path}") # Set the icon for Windows

            # Nuitka automatically includes data files that are referred to by your script
            # or by packages it imports. For arbitrary data files, --include-package-data
            # or --include-file can be used, but for simplicity, we rely on automatic detection.
            
            cmd.append(main_script)
            cwd = project_path # Nuitka should be run from the project root

            process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='ignore')
            
            for line in process.stdout:
                build_log += line
                if _logs_area: 
                    _logs_area.write(line)

            process.wait() 
            success = (process.returncode == 0) 
            
        except FileNotFoundError as fnfe:
            build_log += f"\nError: Nuitka compiler not found. Please ensure Nuitka is installed (pip install nuitka) and in your PATH. ({fnfe})"
            if _logs_area: _logs_area.error(f"\nError: Nuitka compiler not found.") 
            success = False
        except Exception as e:
            build_log += f"\nException during compilation: {e}"
            if _logs_area: _logs_area.error(f"\nException during compilation: {e}") 
            success = False

        return success, build_log

    if st.button(T["compile_button"], disabled=not uploaded_file):
        st.session_state.exe_data = None
        st.session_state.final_zip_data = None
        st.session_state.download_ready = False
        st.session_state.build_log = ""
        st.session_state.build_in_progress = True

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                uploaded_file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(uploaded_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                is_batch_zip_py = False
                extracted_single_project_path = None # Path to the extracted single project folder

                if uploaded_file.name.endswith(".zip"):
                    logs_placeholder.info(T["extracting_zip"])
                    with zipfile.ZipFile(uploaded_file_path, 'r') as zip_ref:
                        namelist = zip_ref.namelist()
                        
                        py_projects_in_zip = []
                        # Detect if it's a batch zip (multiple folders with main.py)
                        for name in namelist:
                            if name.endswith("main.py"):
                                parts = Path(name).parts
                                if len(parts) > 1: # main.py is in a subfolder
                                    project_folder = parts[0]
                                    project_full_path = os.path.join(temp_dir, project_folder)
                                    if (project_folder, project_full_path) not in py_projects_in_zip:
                                        py_projects_in_zip.append((project_folder, project_full_path))
                                elif len(parts) == 1: # main.py is at the root of the zip
                                    # It's a single project at the root
                                    extracted_single_project_path = temp_dir 
                                    
                        if len(py_projects_in_zip) > 1:
                            is_batch_zip_py = True
                            zip_ref.extractall(temp_dir) 
                            st.session_state.py_batch_projects = py_projects_in_zip
                            logs_placeholder.info(T["detecting_project_type"] + " " + "Batch Mode.")
                        elif extracted_single_project_path: # It's a single project zip with main.py at the root
                            zip_ref.extractall(temp_dir)
                            logs_placeholder.info(T["detecting_project_type"] + " " + "Single Project (ZIP).")
                        else: # It's a zip that doesn't contain main.py at the root, nor a clear batch structure
                            zip_ref.extractall(temp_dir)
                            # Check if it's a zip containing a single .py that is not main.py
                            py_files_at_root = [f for f in os.listdir(temp_dir) if f.endswith(".py")]
                            if len(py_files_at_root) == 1:
                                extracted_single_project_path = temp_dir # Treat as a single project
                                logs_placeholder.info(T["detecting_project_type"] + " " + "Single Project (ZIP with a single .py).")
                            else:
                                logs_placeholder.error(T["error_zip_single_py"])
                                st.session_state.build_in_progress = False
                                return
                else: # Single .py file
                    logs_placeholder.info(T["detecting_project_type"] + " " + "Single .py File.")
                    extracted_single_project_path = temp_dir # The file is already in temp_dir

                current_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

                # No icon/assets options uploaded by the user for simplification
                # We can add a default icon if desired
                icon_final_path = None # No default icon for now
                assets_temp_buffer = None # No uploaded assets for now

                if is_batch_zip_py:
                    logs_placeholder.info(T["building_batch"])
                    compiled_exes = {} 
                    compiled_reports = {} 

                    for project_name, project_full_path in st.session_state.py_batch_projects:
                        logs_placeholder.write(f"\n--- **{T['compiling_project']} {project_name}** ---")
                        full_session_log += f"\n--- Compiling project: {project_name} ---\n"
                        
                        project_stage_path, is_valid_proj, main_script, deps_log = prepare_project_py(
                            temp_dir, project_full_path, logs_placeholder
                        )
                        full_session_log += deps_log

                        if is_valid_proj:
                            success, log = build_exe(source_language, project_stage_path, main_script, project_name, icon_final_path, console_mode_default, logs_placeholder)
                            full_session_log += log
                            
                            if success:
                                logs_placeholder.success(f"Compilation successful for {project_name}.")
                                # Nuitka output is directly in project_stage_path
                                exe_source_path = os.path.join(project_stage_path, f"{project_name}.exe") 
                                if os.path.exists(exe_source_path):
                                    with open(exe_source_path, "rb") as f_exe:
                                        compiled_exes[project_name] = f_exe.read()
                                    
                                    if pdf_report_opt_default:
                                        pdf_report_buffer = io.BytesIO()
                                        generate_pdf_report(log, current_timestamp, project_name, pdf_report_buffer)
                                        pdf_report_buffer.seek(0)
                                        compiled_reports[project_name] = pdf_report_buffer.getvalue()
                                else:
                                    logs_placeholder.error(f"{T['error_compile']} ({T['exe_not_found']}) for {project_name}.")
                            else:
                                logs_placeholder.error(f"{T['error_compile']} for {project_name}.")
                        else:
                            logs_placeholder.error(f"{T['error_no_main_in_project'].format(project_name=project_name)}")
                    
                    if compiled_exes: 
                        logs_placeholder.info(T["finalizing_package"])
                        st.success(T["success_compile_batch"])
                        final_zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(final_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            for proj_name, exe_data in compiled_exes.items():
                                zipf.writestr(f"{proj_name}/{proj_name}.exe", exe_data)
                            for proj_name, pdf_data in compiled_reports.items():
                                zipf.writestr(f"{proj_name}/rapport_compilation_{current_timestamp}.pdf", pdf_data)
                            
                            if add_readme_default:
                                zipf.writestr("README.txt", readme_content_default)
                            
                            try: 
                                import requests
                                response = requests.get("https://i.postimg.cc/FRjs6pNz/logo-ernestmind-png.png") 
                                if response.status_code == 200:
                                    zipf.writestr("ErnestMind_logo.png", response.content)
                            except Exception as e:
                                logs_placeholder.warning(f"{T['error_icon_assets']} {e}")

                        final_zip_buffer.seek(0)
                        st.session_state.final_zip_data = final_zip_buffer.getvalue()
                        st.session_state.download_ready = True
                    else:
                        st.error(T["error_compile"])
                
                else: # Single project compilation
                    logs_placeholder.info(T["building_single"])
                    project_name_for_single_output = exe_name_default 
                    
                    # The input path for prepare_project_py is the extracted folder
                    project_stage_path, is_valid, main_script, deps_log = prepare_project_py(
                        temp_dir, extracted_single_project_path, logs_placeholder
                    )
                    full_session_log = deps_log 
                    
                    if is_valid:
                        success, log = build_exe(source_language, project_stage_path, main_script, project_name_for_single_output, icon_final_path, console_mode_default, logs_placeholder)
                        full_session_log += log
                        
                        if success:
                            logs_placeholder.info(T["finalizing_package"])
                            st.success(T["success_compile_single"])
                            # Nuitka output is directly in project_stage_path
                            exe_source_path = os.path.join(project_stage_path, f"{project_name_for_single_output}.exe")

                            if os.path.exists(exe_source_path):
                                with open(exe_source_path, "rb") as f_exe:
                                    st.session_state.exe_data = f_exe.read()

                                final_zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(final_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                    zipf.writestr(f"{project_name_for_single_output}.exe", st.session_state.exe_data)
                                    
                                    if add_readme_default:
                                        zipf.writestr("README.txt", readme_content_default)
                                    
                                    try: 
                                        import requests
                                        response = requests.get("https://i.postimg.cc/FRjs6pNz/logo-ernestmind-png.png")
                                        if response.status_code == 200:
                                            zipf.writestr("ErnestMind_logo.png", response.content)
                                    except Exception as e:
                                        logs_placeholder.warning(f"{T['error_icon_assets']} {e}")
                                    
                                    if pdf_report_opt_default:
                                        pdf_report_buffer = io.BytesIO()
                                        generate_pdf_report(log, current_timestamp, project_name_for_single_output, pdf_report_buffer)
                                        pdf_report_buffer.seek(0)
                                        zipf.writestr(f"rapport_compilation_{current_timestamp}.pdf", pdf_report_buffer.getvalue())

                                final_zip_buffer.seek(0)
                                st.session_state.final_zip_data = final_zip_buffer.getvalue()
                                st.session_state.download_ready = True
                            else:
                                logs_placeholder.error(T["error_compile"] + f" ({T['exe_not_found']})")
                        else:
                            logs_placeholder.error(T["error_compile"])
                    else:
                        logs_placeholder.error(T["error_file"])
                
                # Clean up Nuitka temporary files (.build folder)
                logs_placeholder.info(T["cleaning_up"])
                if 'py_project_staging' in os.listdir(temp_dir):
                    # For Nuitka, the .build directory will be alongside the executable.
                    # We also need to clean the Nuitka global cache.
                    for root, dirs, files in os.walk(os.path.join(temp_dir, 'py_project_staging')):
                        for d in dirs:
                            if d.endswith(".build"):
                                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                        for f in files:
                            if f.endswith(".spec"): # PyInstaller specific, but good to clean if any residual
                                os.remove(os.path.join(root, f))
                
                # Clean global Nuitka cache
                nuitka_cache_dir = os.path.join(Path.home(), ".cache", "nuitka")
                if os.path.exists(nuitka_cache_dir):
                    shutil.rmtree(nuitka_cache_dir, ignore_errors=True)
                
                logs_placeholder.success(T["cleaning_done"])

        except Exception as e:
            logs_placeholder.error(f"An unexpected error occurred: {e}")
            full_session_log += f"\nUnexpected error: {e}"
        finally:
            st.session_state.build_in_progress = False
            st.session_state.build_log = full_session_log
            
    # Display detailed logs (optional)
    if 'build_log' in st.session_state and st.session_state.build_log:
        with st.expander(T["log_preview"]):
            st.text_area("Logs", st.session_state.build_log, height=300)

    # Download buttons
    if 'download_ready' in st.session_state and st.session_state.download_ready:
        st.subheader(T["download_ready"])
        col_dl1, col_dl2 = st.columns(2)
        
        # Determine if it was a batch or single build for button display
        is_batch_build = False
        if 'py_batch_projects' in st.session_state and st.session_state.py_batch_projects:
            is_batch_build = True

        if not is_batch_build and st.session_state.exe_data: 
            with col_dl1:
                st.download_button(
                    label=T["download_exe"],
                    data=st.session_state.exe_data,
                    file_name=f"{exe_name_default}.exe",
                    mime="application/octet-stream",
                    key="download_exe_button"
                )
        
        with (col_dl2 if not is_batch_build and st.session_state.exe_data else st): 
            zip_file_name_prefix = 'batch_compilation' if is_batch_build else exe_name_default
            st.download_button(
                label=T["download_zip"],
                data=st.session_state.final_zip_data,
                file_name=f"{zip_file_name_prefix}_package.zip",
                mime="application/zip",
                key="download_zip_button"
            )
        st.markdown(f"**{T['branding_notice']}**")
    
    st.sidebar.markdown("---")
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "main"

    if st.sidebar.button(T["help"]):
        st.session_state.current_page = "help"
    if st.sidebar.button(T["about"]):
        st.session_state.current_page = "about"
    if st.sidebar.button("Retour à l'outil" if st.session_state.lang == "fr" else "Back to tool"):
        st.session_state.current_page = "main"

    if st.session_state.current_page == "help":
        st.header(T["help"])
        st.markdown(T["help_content"])
    elif st.session_state.current_page == "about":
        st.header(T["about"])
        st.markdown(T["about_content"])

if __name__ == "__main__":
    main()

