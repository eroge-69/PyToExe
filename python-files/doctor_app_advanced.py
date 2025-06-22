# Patient Manager GUI with Light/Dark Mode, Charts, Side Navigation, and Background Images
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PIL import Image, ImageTk
from datetime import datetime

# Font settings
FONT = ("Segoe UI", 11)
BIG_FONT = ("Segoe UI", 14, "bold")
DATA_FILE = "patients.json"
BACKGROUND_IMAGE = "background.png"  # For statistics tab
PATIENTS_BACKGROUND = "background2.png"  # For patients tab

# Days of the week in French
JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

# Global variables
patients = []
filtered_patients = []
theme = "light"
current_listbox = None
bg_image = None
bg_photo = None
patients_bg_image = None
patients_bg_photo = None

# Load background images
def load_backgrounds():
    global bg_image, bg_photo, patients_bg_image, patients_bg_photo
    try:
        # Load statistics background
        if os.path.exists(BACKGROUND_IMAGE):
            print(f"Loading background image from: {BACKGROUND_IMAGE}")
            bg_image = Image.open(BACKGROUND_IMAGE)
            bg_photo = ImageTk.PhotoImage(bg_image)
            print("Statistics background loaded successfully")
        else:
            print(f"Warning: {BACKGROUND_IMAGE} not found")
        
        # Load patients background
        if os.path.exists(PATIENTS_BACKGROUND):
            print(f"Loading patients background from: {PATIENTS_BACKGROUND}")
            patients_bg_image = Image.open(PATIENTS_BACKGROUND)
            patients_bg_photo = ImageTk.PhotoImage(patients_bg_image)
            print("Patients background loaded successfully")
            return True
        else:
            print(f"Warning: {PATIENTS_BACKGROUND} not found")
            return False
    except Exception as e:
        print(f"Error loading background images: {e}")
        return False

# Load data at startup
def load_data():
    global patients
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                patients = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data: {e}")
            # Try to load from backup
            backup_file = DATA_FILE + ".backup"
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, "r", encoding="utf-8") as f:
                        patients = json.load(f)
                    messagebox.showinfo("Récupération", "Données restaurées depuis la sauvegarde de sécurité")
                except:
                    patients = []
            else:
                patients = []
    else:
        patients = []

def save_data():
    try:
        # First try without changing permissions
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(patients, f, ensure_ascii=False, indent=2)
            
    except PermissionError:
        try:
            # If permission denied, try making file writable first
            import os
            os.chmod(DATA_FILE, 0o644)  # Make file writable
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(patients, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder: {e}")
            # Try saving to alternate location
            try:
                alt_path = os.path.expanduser("~/patients_backup.json")
                with open(alt_path, "w", encoding="utf-8") as f:
                    json.dump(patients, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Sauvegarde", f"Données sauvegardées à: {alt_path}")
            except:
                messagebox.showerror("Erreur", "Échec de la sauvegarde dans tous les emplacements")

def export_data():
    """Export data to a timestamped backup file"""
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = f"patients_export_{timestamp}.json"
        
        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(patients, f, ensure_ascii=False, indent=2)
        
        messagebox.showinfo("Export", f"Données exportées vers: {export_file}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")

def delete_patient():
    """Delete selected patient with confirmation"""
    if not current_listbox:
        messagebox.showwarning("Attention", "Aucune liste de patients affichée")
        return
        
    selection = current_listbox.curselection()
    if not selection:
        messagebox.showwarning("Attention", "Veuillez sélectionner un patient à supprimer")
        return
    
    idx = selection[0]
    if idx >= len(filtered_patients):
        return
        
    patient, original_idx = filtered_patients[idx]
    patient_name = f"{patient.get('nom', 'N/A')} {patient.get('prenom', 'N/A')}"
    
    # Confirmation dialog
    result = messagebox.askyesno(
        "Confirmer la suppression", 
        f"Êtes-vous sûr de vouloir supprimer le patient:\n{patient_name}?\n\nCette action est irréversible!",
        icon="warning"
    )
    
    if result:
        try:
            # Remove patient from the main list
            patients.pop(original_idx)
            save_data()
            refresh_list(search_var.get() if not search_is_placeholder else "")
            messagebox.showinfo("Succès", f"Patient {patient_name} supprimé avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")
    

def toggle_theme():
    global theme
    theme = "dark" if theme == "light" else "light"
    apply_theme()

def apply_theme():
    bg = "#2b2b2b" if theme == "dark" else "#f5f5f5"
    fg = "#ffffff" if theme == "dark" else "#333333"
    
    # Apply theme to main components
    root.configure(bg=bg)
    nav_frame.configure(bg=bg)
    main_frame.configure(bg=bg)
    
    # Apply theme to search entry
    search_entry.configure(
        bg="#404040" if theme == "dark" else "white", 
        fg=fg, 
        insertbackground=fg,
        relief="flat",
        borderwidth=1
    )
    
    # Apply theme to navigation buttons
    for widget in nav_frame.winfo_children():
        if isinstance(widget, tk.Button):
            if widget.cget("text") == "🗑 Supprimer":
                # Special styling for delete button
                widget.configure(
                    bg="#d9534f" if theme == "dark" else "#d9534f",
                    fg="white",
                    activebackground="#c9302c" if theme == "dark" else "#c9302c",
                    relief="flat",
                    borderwidth=0,
                    padx=10,
                    pady=5
                )
            else:
                widget.configure(
                    bg="#3a3a3a" if theme == "dark" else "#e0e0e0",
                    fg=fg,
                    activebackground="#505050" if theme == "dark" else "#d0d0d0",
                    relief="flat",
                    borderwidth=0,
                    padx=10,
                    pady=5
                )
    
    # Apply theme to current listbox if it exists
    if current_listbox:
        current_listbox.configure(
            bg="#404040" if theme == "dark" else "white",
            fg=fg,
            selectbackground="#606060" if theme == "dark" else "#5bc0de",
            selectforeground="white" if theme == "dark" else "black",
            relief="flat",
            borderwidth=1
        )

def open_add_window(patient=None, index=None):
    add_win = tk.Toplevel(root)
    add_win.title("Modifier le Patient" if patient else "Ajouter un Patient")
    add_win.geometry("500x700")
    add_win.configure(bg="#2b2b2b" if theme == "dark" else "#f5f5f5")
    add_win.resizable(False, False)

    def submit_patient():
        data = {
            "nom": nom_var.get().strip(),
            "prenom": prenom_var.get().strip(),
            "date_naissance": naissance_var.get().strip(),
            "date_consultation": consultation_var.get().strip(),
            "willaya": willaya_var.get().strip(),
            "raison": raison_var.get().strip(),
            "medecin": medecin_var.get().strip(),
            "sexe": sexe_var.get().strip(),
            "tel": tel_var.get().strip(),
            "payment": payment_var.get().strip(),  # Added payment field
            "jour": jour_var.get().strip(),  # Added day of week field
            "consultations": patient.get("consultations", []) if patient else []  # Preserve existing consultations
        }
        
        if not data["nom"] or not data["prenom"]:
            messagebox.showerror("Erreur", "Nom et prénom requis")
            return
            
        try:
            if patient and index is not None:
                patients[index] = data
            else:
                patients.append(data)
            save_data()
            refresh_list(search_var.get())
            add_win.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}")

    def make_labeled_entry(row, label_text, var, default_val=""):
        label = tk.Label(add_win, text=label_text, font=FONT)
        label.grid(row=row, column=0, sticky="e", padx=10, pady=5)
        label.configure(
            bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
            fg="#ffffff" if theme == "dark" else "#333333"
        )
        
        entry = tk.Entry(add_win, textvariable=var, font=FONT, width=30)
        entry.grid(row=row, column=1, pady=5, padx=10)
        entry.configure(
            bg="#404040" if theme == "dark" else "white",
            fg="#ffffff" if theme == "dark" else "#333333",
            insertbackground="#ffffff" if theme == "dark" else "#000000",
            relief="flat",
            borderwidth=1
        )
        if default_val:
            entry.insert(0, default_val)
        return entry

    # Create variables
    nom_var = tk.StringVar()
    prenom_var = tk.StringVar()
    naissance_var = tk.StringVar()
    consultation_var = tk.StringVar()
    raison_var = tk.StringVar()
    medecin_var = tk.StringVar()
    sexe_var = tk.StringVar()
    tel_var = tk.StringVar()
    willaya_var = tk.StringVar()
    payment_var = tk.StringVar()  # Added payment variable
    jour_var = tk.StringVar()  # Added day of week variable

    # Create form fields
    make_labeled_entry(0, "Nom", nom_var, patient["nom"] if patient else "")
    make_labeled_entry(1, "Prénom", prenom_var, patient["prenom"] if patient else "")
    make_labeled_entry(2, "Date de Naissance", naissance_var, patient["date_naissance"] if patient else "")
    make_labeled_entry(3, "Date de Consultation", consultation_var, patient["date_consultation"] if patient else "")

    # Willaya dropdown
    willaya_label = tk.Label(add_win, text="Willaya", font=FONT)
    willaya_label.grid(row=4, column=0, sticky="e", padx=10, pady=5)
    willaya_label.configure(
        bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
        fg="#ffffff" if theme == "dark" else "#333333"
    )
    
    willaya_menu = ttk.Combobox(add_win, textvariable=willaya_var, font=FONT, width=28, values=[
        "Adrar", "Chlef", "Laghouat", "Oum El Bouaghi", "Batna", "Béjaïa", "Biskra", "Béchar", "Blida", "Bouira",
        "Tamanrasset", "Tébessa", "Tlemcen", "Tiaret", "Tizi Ouzou", "Alger", "Djelfa", "Jijel", "Sétif", "Saïda",
        "Skikda", "Sidi Bel Abbès", "Annaba", "Guelma", "Constantine", "Médéa", "Mostaganem", "M'Sila", "Mascara",
        "Ouargla", "Oran", "El Bayadh", "Illizi", "Bordj Bou Arréridj", "Boumerdès", "El Tarf", "Tindouf", "Tissemsilt",
        "El Oued", "Khenchela", "Souk Ahras", "Tipaza", "Mila", "Aïn Defla", "Naâma", "Aïn Témouchent", "Ghardaïa", "Relizane"
    ])
    willaya_menu.grid(row=4, column=1, pady=5, padx=10)
    if patient:
        willaya_var.set(patient["willaya"])

    # Jour de la semaine dropdown
    jour_label = tk.Label(add_win, text="Jour", font=FONT)
    jour_label.grid(row=5, column=0, sticky="e", padx=10, pady=5)
    jour_label.configure(
        bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
        fg="#ffffff" if theme == "dark" else "#333333"
    )
    
    jour_menu = ttk.Combobox(add_win, textvariable=jour_var, font=FONT, width=28, values=JOURS_SEMAINE)
    jour_menu.grid(row=5, column=1, pady=5, padx=10)
    if patient:
        jour_var.set(patient.get("jour", ""))

    make_labeled_entry(6, "Raison", raison_var, patient["raison"] if patient else "")
    make_labeled_entry(7, "Médecin", medecin_var, patient["medecin"] if patient else "")
    
    # Gender checkboxes
    sexe_label = tk.Label(add_win, text="Sexe", font=FONT)
    sexe_label.grid(row=8, column=0, sticky="e", padx=10, pady=5)
    sexe_label.configure(
        bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
        fg="#ffffff" if theme == "dark" else "#333333"
    )
    
    sexe_frame = tk.Frame(add_win)
    sexe_frame.grid(row=8, column=1, pady=5, sticky="w")
    sexe_frame.configure(bg="#2b2b2b" if theme == "dark" else "#f5f5f5")
    
    homme_var = tk.BooleanVar()
    femme_var = tk.BooleanVar()
    
    def on_homme_select():
        if homme_var.get():
            femme_var.set(False)
            sexe_var.set("Homme")
        else:
            sexe_var.set("")
    
    def on_femme_select():
        if femme_var.get():
            homme_var.set(False)
            sexe_var.set("Femme")
        else:
            sexe_var.set("")
    
    homme_cb = tk.Checkbutton(sexe_frame, text="Homme", variable=homme_var, command=on_homme_select, font=FONT)
    homme_cb.pack(side="left", padx=(0, 20))
    homme_cb.configure(
        bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
        fg="#ffffff" if theme == "dark" else "#333333",
        selectcolor="#404040" if theme == "dark" else "white",
        activebackground="#2b2b2b" if theme == "dark" else "#f5f5f5",
        activeforeground="#ffffff" if theme == "dark" else "#333333"
    )
    
    femme_cb = tk.Checkbutton(sexe_frame, text="Femme", variable=femme_var, command=on_femme_select, font=FONT)
    femme_cb.pack(side="left")
    femme_cb.configure(
        bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
        fg="#ffffff" if theme == "dark" else "#333333",
        selectcolor="#404040" if theme == "dark" else "white",
        activebackground="#2b2b2b" if theme == "dark" else "#f5f5f5",
        activeforeground="#ffffff" if theme == "dark" else "#333333"
    )
    
    # Set initial values if editing
    if patient and patient.get("sexe"):
        if patient["sexe"].lower() in ["homme", "h", "male", "m"]:
            homme_var.set(True)
            sexe_var.set("Homme")
        elif patient["sexe"].lower() in ["femme", "f", "female"]:
            femme_var.set(True)
            sexe_var.set("Femme")
    make_labeled_entry(9, "Tél", tel_var, patient.get("tel", "") if patient else "")
    make_labeled_entry(10, "Payment", payment_var, patient.get("payment", "") if patient else "")  # Added payment field

    # Submit button
    submit_btn = tk.Button(add_win, text="Enregistrer", font=BIG_FONT, command=submit_patient)
    submit_btn.grid(row=11, columnspan=2, pady=15)
    submit_btn.configure(
        bg="#5cb85c" if theme == "dark" else "#5cb85c",
        fg="white",
        activebackground="#4cae4c" if theme == "dark" else "#4cae4c",
        relief="flat",
        borderwidth=0,
        padx=20,
        pady=5
    )

def show_charts():
    global current_listbox
    current_listbox = None
    
    # Clear main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Create a canvas for the background
    canvas = tk.Canvas(main_frame, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    # Add background image if available
    if bg_photo:
        def resize_background(event):
            # Resize background image to fit canvas
            canvas_width = event.width
            canvas_height = event.height
            
            if canvas_width > 1 and canvas_height > 1:
                # Resize the background image
                resized_image = bg_image.resize((canvas_width, canvas_height), Image.LANCZOS)
                resized_photo = ImageTk.PhotoImage(resized_image)
                
                # Clear canvas and add background
                canvas.delete("all")
                canvas.create_image(0, 0, anchor="nw", image=resized_photo)
                canvas.image = resized_photo  # Keep a reference
                
                # Create charts on top of background
                create_charts(canvas, canvas_width, canvas_height)
        
        canvas.bind("<Configure>", resize_background)
    else:
        # Create charts directly if no background
        create_charts(main_frame)

def create_charts(parent, width=None, height=None):
    """Create charts on the given parent widget"""
    if not patients:
        # Add text overlay if no data
        if isinstance(parent, tk.Canvas):
            parent.create_text(
                width//2 if width else 400, 
                height//2 if height else 300,
                text="Aucune donnée disponible pour les graphiques",
                font=BIG_FONT,
                fill="white" if theme == "dark" else "black",
                anchor="center"
            )
        else:
            no_data_label = tk.Label(parent, text="Aucune donnée disponible pour les graphiques", font=BIG_FONT)
            no_data_label.pack(pady=50)
            no_data_label.configure(
                bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
                fg="#ffffff" if theme == "dark" else "#333333"
            )
        return

    # Count data for charts
    wilaya_counts = {}
    sexe_counts = {"Homme": 0, "Femme": 0}
    jour_counts = {jour: 0 for jour in JOURS_SEMAINE}
    consultation_counts = {}  # Count consultations per patient
    
    for p in patients:
        # Count by willaya
        willaya = p.get("willaya", "Non spécifié")
        wilaya_counts[willaya] = wilaya_counts.get(willaya, 0) + 1
        
        # Count by sex
        sexe = p.get("sexe", "").strip()
        if sexe == "Homme":
            sexe_counts["Homme"] += 1
        elif sexe == "Femme":
            sexe_counts["Femme"] += 1
            
        # Count by day of week
        jour = p.get("jour", "")
        if jour in JOURS_SEMAINE:
            jour_counts[jour] += 1
            
        # Count consultations
        consultation_count = len(p.get("consultations", []))
        if consultation_count > 0:
            consultation_counts[p["nom"] + " " + p["prenom"]] = consultation_count

    try:
        # Create charts frame
        if isinstance(parent, tk.Canvas):
            # If parent is a canvas, create a frame to hold the charts
            charts_frame = tk.Frame(parent, bg="#2b2b2b" if theme == "dark" else "#f5f5f5")
            parent.create_window(
                (width//2 if width else 400, height//2 if height else 300),
                window=charts_frame, 
                anchor="center"
            )
        else:
            # Otherwise just use the parent frame
            charts_frame = parent
        
        # Willaya chart
        if wilaya_counts:
            fig1 = Figure(figsize=(8, 4), facecolor='#2b2b2b' if theme == "dark" else 'white')
            ax1 = fig1.add_subplot(111)
            ax1.set_facecolor('#2b2b2b' if theme == "dark" else 'white')
            
            bars = ax1.bar(list(wilaya_counts.keys()), list(wilaya_counts.values()), color="#5bc0de")
            ax1.set_title("Patients par Willaya", color='white' if theme == "dark" else 'black', fontweight="bold")
            ax1.tick_params(axis='x', rotation=45, colors='white' if theme == "dark" else 'black')
            ax1.tick_params(axis='y', colors='white' if theme == "dark" else 'black')
            
            fig1.tight_layout()
            canvas1 = FigureCanvasTkAgg(fig1, master=charts_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(pady=10, fill="x")

        # Sex distribution chart
        active_sexe_counts = {k: v for k, v in sexe_counts.items() if v > 0}
        if active_sexe_counts:
            fig2 = Figure(figsize=(6, 4), facecolor='#2b2b2b' if theme == "dark" else 'white')
            ax2 = fig2.add_subplot(111)
            ax2.set_facecolor('#2b2b2b' if theme == "dark" else 'white')
            
            wedges, texts, autotexts = ax2.pie(
                list(active_sexe_counts.values()), 
                labels=list(active_sexe_counts.keys()), 
                autopct='%1.1f%%', 
                startangle=140,
                textprops={'color': 'white' if theme == "dark" else 'black'},
                colors=["#5cb85c", "#5bc0de"]
            )
            ax2.set_title("Répartition par Sexe", color='white' if theme == "dark" else 'black', fontweight="bold")
            
            fig2.tight_layout()
            canvas2 = FigureCanvasTkAgg(fig2, master=charts_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(pady=10, fill="x")

        # Day of week distribution chart
        active_jour_counts = {k: v for k, v in jour_counts.items() if v > 0}
        if active_jour_counts:
            fig3 = Figure(figsize=(8, 4), facecolor='#2b2b2b' if theme == "dark" else 'white')
            ax3 = fig3.add_subplot(111)
            ax3.set_facecolor('#2b2b2b' if theme == "dark" else 'white')
            
            bars = ax3.bar(list(active_jour_counts.keys()), list(active_jour_counts.values()), color="#f0ad4e")
            ax3.set_title("Patients par Jour de la Semaine", color='white' if theme == "dark" else 'black', fontweight="bold")
            ax3.tick_params(axis='x', colors='white' if theme == "dark" else 'black')
            ax3.tick_params(axis='y', colors='white' if theme == "dark" else 'black')
            
            fig3.tight_layout()
            canvas3 = FigureCanvasTkAgg(fig3, master=charts_frame)
            canvas3.draw()
            canvas3.get_tk_widget().pack(pady=10, fill="x")
            
        # Consultations per patient chart (if any patients have consultations)
        if consultation_counts:
            fig4 = Figure(figsize=(8, 4), facecolor='#2b2b2b' if theme == "dark" else 'white')
            ax4 = fig4.add_subplot(111)
            ax4.set_facecolor('#2b2b2b' if theme == "dark" else 'white')
            
            # Sort by number of consultations (descending)
            sorted_consultations = sorted(consultation_counts.items(), key=lambda x: x[1], reverse=True)
            names = [x[0] for x in sorted_consultations]
            counts = [x[1] for x in sorted_consultations]
            
            bars = ax4.bar(names, counts, color="#d9534f")
            ax4.set_title("Nombre de Consultations par Patient", color='white' if theme == "dark" else 'black', fontweight="bold")
            ax4.tick_params(axis='x', rotation=45, colors='white' if theme == "dark" else 'black')
            ax4.tick_params(axis='y', colors='white' if theme == "dark" else 'black')
            
            fig4.tight_layout()
            canvas4 = FigureCanvasTkAgg(fig4, master=charts_frame)
            canvas4.draw()
            canvas4.get_tk_widget().pack(pady=10, fill="x")

    except Exception as e:
        error_label = tk.Label(parent, text=f"Erreur lors de la création des graphiques: {e}", font=FONT)
        error_label.pack(pady=20)
        error_label.configure(
            bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
            fg="#ffffff" if theme == "dark" else "#333333"
        )

def refresh_list(query=""):
    global filtered_patients, current_listbox, patients_bg_photo
    
    # Clear main frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    filtered_patients = []
    
    # Create a container frame that will hold both background and list
    container = tk.Frame(main_frame)
    container.pack(fill="both", expand=True)
    
    # Create canvas for background (lower layer)
    bg_canvas = tk.Canvas(container, highlightthickness=0)
    bg_canvas.pack(fill="both", expand=True)
    
    # Create frame for list (upper layer) - now top-left
    list_frame = tk.Frame(container, bg='#f5f5f5' if theme == "light" else '#2b2b2b')
    list_frame.place(relx=0, rely=0, anchor="nw", x=20, y=20)  # 20px from top-left
    
    # Add background image if available
    if patients_bg_photo:
        def resize_background(event):
            # Resize background image to fit canvas
            resized_image = patients_bg_image.resize((event.width, event.height), Image.LANCZOS)
            resized_photo = ImageTk.PhotoImage(resized_image)
            
            # Update background
            bg_canvas.delete("all")
            bg_canvas.create_image(0, 0, anchor="nw", image=resized_photo)
            bg_canvas.image = resized_photo  # Keep reference
        
        bg_canvas.bind("<Configure>", resize_background)
    
    # Create the list content and pass the query
    create_list_content(list_frame, query)

def create_list_content(parent, query=""):
    """Create the list content on the given parent widget"""
    # Create canvas with scrollbar
    canvas = tk.Canvas(parent, highlightthickness=0, bg='#f5f5f5' if theme == "light" else '#2b2b2b')
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='#f5f5f5' if theme == "light" else '#2b2b2b')

    # Configure the scrollable frame
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Create listbox with theme colors
    current_listbox = tk.Listbox(
        scrollable_frame, 
        font=FONT, 
        width=80, 
        height=20,
        bg='#ffffff' if theme == "light" else '#383838',
        fg="#333333" if theme == "light" else "#ffffff",
        selectbackground="#5bc0de" if theme == "light" else "#606060",
        selectforeground="white",
        highlightthickness=0,
        borderwidth=1,
        relief='flat'
    )
    current_listbox.pack(padx=10, pady=10, fill='both', expand=True)
    current_listbox.bind("<Double-Button-1>", show_details)

    # Filter and display patients using the passed query
    query = query.strip().lower()
    for i, patient in enumerate(patients):
        fullname = f"{patient.get('nom', '')} {patient.get('prenom', '')}".lower()
        if not query or query in fullname:
            display = f"{patient.get('nom', 'N/A')} {patient.get('prenom', 'N/A')} - {patient.get('date_naissance', 'N/A')} - {patient.get('willaya', 'N/A')} - {patient.get('jour', 'N/A')}"
            current_listbox.insert(tk.END, display)
            filtered_patients.append((patient, i))

    # Show message if no patients
    if not filtered_patients:
        no_patients_label = tk.Label(
            scrollable_frame, 
            text="Aucun patient enregistré" if not query else f"Aucun patient trouvé pour '{query}'",
            font=BIG_FONT,
            bg='#f8f8f8' if theme == "light" else '#383838',
            fg="#333333" if theme == "light" else "white"
        )
        no_patients_label.pack(pady=50)

def show_details(event):
    try:
        selection = event.widget.curselection()
        if not selection:
            return
        
        idx = selection[0]
        if idx >= len(filtered_patients):
            return
            
        patient, original_idx = filtered_patients[idx]
        
        detail = tk.Toplevel(root)
        detail.title("Détails du Patient")
        detail.geometry("450x550")  # Original size
        detail.configure(bg="#2b2b2b" if theme == "dark" else "#f5f5f5")
        detail.resizable(False, False)

        # Main container with fixed bottom section
        main_container = tk.Frame(detail, bg="#2b2b2b" if theme == "dark" else "#f5f5f5")
        main_container.pack(fill="both", expand=True)

        # Create main canvas and scrollbar
        canvas = tk.Canvas(main_container, bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
                         highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg="#2b2b2b" if theme == "dark" else "#f5f5f5")

        # Configure scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw", width=430)  # Adjusted width
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack scrollable area
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add patient details
        row = 0
        for key, value in patient.items():
            if key == "consultations":
                continue
                
            tk.Label(content_frame, text=f"{key.capitalize()} :", font=FONT,
                    bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
                    fg="#ffffff" if theme == "dark" else "#333333"
                    ).grid(row=row, column=0, sticky="w", padx=10, pady=2)
            
            tk.Label(content_frame, text=str(value), font=FONT,
                    bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
                    fg="#ffffff" if theme == "dark" else "#333333"
                    ).grid(row=row, column=1, sticky="w", padx=10, pady=2)
            row += 1

        # Consultations section
        consultations = patient.get("consultations", [])
        tk.Label(content_frame, text="Consultations:", font=BIG_FONT,
                bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
                fg="#ffffff" if theme == "dark" else "#333333"
                ).grid(row=row, column=0, sticky="w", padx=10, pady=(10,2))
        row += 1

        # Create a frame for consultations (no fixed height)
        consult_frame = tk.Frame(content_frame, 
                               bg="#2b2b2b" if theme == "dark" else "#f5f5f5")
        consult_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        # Add all consultations
        for i, consult in enumerate(consultations):
            tk.Label(consult_frame,
                   text=f"#{i+1} {consult.get('date','N/A')}: {consult.get('notes','')}",
                   font=FONT, wraplength=400, justify="left",
                   bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
                   fg="#ffffff" if theme == "dark" else "#333333"
                   ).pack(anchor="w", padx=5, pady=2)

        # Add consultation button
        tk.Button(content_frame,
                text="+ Ajouter Consultation",
                font=FONT,
                command=lambda: add_consultation(patient, original_idx, detail),
                bg="#5bc0de", fg="white",
                activebackground="#46b8da",
                relief="flat"
                ).grid(row=row+1, column=0, columnspan=2, pady=(10,20), sticky="ew", padx=10)

        # Fixed bottom frame for Modifier button
        bottom_frame = tk.Frame(main_container, 
                              bg="#2b2b2b" if theme == "dark" else "#f5f5f5")
        bottom_frame.pack(side="bottom", fill="x", pady=(10,0))

        # Modifier button
        tk.Button(bottom_frame,
                text="Modifier", 
                font=BIG_FONT, 
                command=lambda: [detail.destroy(), open_add_window(patient, original_idx)],
                bg="#5bc0de", fg="white",
                activebackground="#46b8da",
                relief="flat",
                padx=20
                ).pack(pady=10, fill="x")

        # Force update of scroll region
        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'affichage des détails: {e}")
def add_consultation(patient, patient_index, parent_window):
    """Open a window to add a new consultation for the patient"""
    consult_win = tk.Toplevel(parent_window)
    consult_win.title("Ajouter Consultation")
    consult_win.geometry("400x250")  # Adjusted height
    consult_win.configure(bg="#2b2b2b" if theme == "dark" else "#f5f5f5")
    consult_win.resizable(False, False)

    # Date variable (auto-filled with today's date)
    date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    notes_var = tk.StringVar()

    # Form elements
    date_label = tk.Label(consult_win, text="Date:", font=FONT)
    date_label.pack(pady=(20, 5))
    date_label.configure(
        bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
        fg="#ffffff" if theme == "dark" else "#333333"
    )

    date_entry = tk.Entry(consult_win, textvariable=date_var, font=FONT)
    date_entry.pack(pady=5, padx=20, fill="x")
    date_entry.configure(
        bg="#404040" if theme == "dark" else "white",
        fg="#ffffff" if theme == "dark" else "#333333",
        insertbackground="#ffffff" if theme == "dark" else "#000000",
        relief="flat",
        borderwidth=1
    )

    notes_label = tk.Label(consult_win, text="Notes:", font=FONT)
    notes_label.pack(pady=(10, 5))
    notes_label.configure(
        bg="#2b2b2b" if theme == "dark" else "#f5f5f5",
        fg="#ffffff" if theme == "dark" else "#333333"
    )

    # Use Entry for single-line notes (or Text for multi-line)
    notes_entry = tk.Entry(consult_win, textvariable=notes_var, font=FONT)
    notes_entry.pack(pady=5, padx=20, fill="x")
    notes_entry.configure(
        bg="#404040" if theme == "dark" else "white",
        fg="#ffffff" if theme == "dark" else "#333333",
        insertbackground="#ffffff" if theme == "dark" else "#000000",
        relief="flat",
        borderwidth=1
    )

    def save_consultation():
        """Save the consultation data to the patient's record"""
        consultation = {
            "date": date_var.get(),
            "notes": notes_var.get()
        }

        # Initialize consultations list if it doesn't exist
        if "consultations" not in patient:
            patient["consultations"] = []

        patient["consultations"].append(consultation)
        patients[patient_index] = patient
        save_data()

        # Refresh the parent window to show the new consultation
        parent_window.destroy()
        show_details_by_index(patient_index)
        consult_win.destroy()

    # Save button (now clearly visible)
    save_btn = tk.Button(
        consult_win,
        text="Enregistrer",
        font=BIG_FONT,
        command=save_consultation
    )
    save_btn.pack(pady=20, padx=20, fill="x")  # Added padding
    save_btn.configure(
        bg="#5cb85c",
        fg="white",
        activebackground="#4cae4c",
        relief="flat",
        borderwidth=0
    )

def show_details_by_index(patient_index):
    """Show details for a patient by their index in the patients list"""
    global filtered_patients
    
    # Find the patient in filtered_patients
    for i, (patient, original_idx) in enumerate(filtered_patients):
        if original_idx == patient_index:
            # Simulate a double-click on this item
            current_listbox.selection_clear(0, tk.END)
            current_listbox.selection_set(i)
            current_listbox.activate(i)
            current_listbox.event_generate("<Double-Button-1>")
            break

def on_search_focus_in(event):
    global search_is_placeholder
    if search_is_placeholder:
        search_var.set("")
        search_entry.configure(fg="#ffffff" if theme == "dark" else "#333333")
        search_is_placeholder = False

def on_search_focus_out(event):
    global search_is_placeholder
    if not search_var.get().strip():
        search_var.set(search_placeholder)
        search_entry.configure(fg="#888888")
        search_is_placeholder = True

# Initialize the application
try:
    root = tk.Tk()
    root.title("Gestion des Patients")
    root.geometry("1000x700")
    root.minsize(800, 600)
    
    # Style configuration
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure ttk combobox style
    style.configure('TCombobox', 
                   fieldbackground='white', 
                   background='white',
                   foreground='black',
                   selectbackground='#5bc0de',
                   selectforeground='white')
    
    # Load background images
    try:
        has_backgrounds = load_backgrounds()
        if not has_backgrounds:
            print("Warning: background images not found or could not be loaded")
    except Exception as bg_error:
        print(f"Error loading backgrounds: {bg_error}")
        has_backgrounds = False
    
    # Load data
    try:
        load_data()
    except Exception as data_error:
        print(f"Error loading data: {data_error}")
        patients = []
        messagebox.showerror("Error", f"Failed to load data: {data_error}")

    # Create main layout
    try:
        nav_frame = tk.Frame(root, width=200, bg="#2b2b2b" if theme == "dark" else "#f5f5f5")
        nav_frame.pack(side="left", fill="y")
        nav_frame.pack_propagate(False)

        main_frame = tk.Frame(root, bg="#2b2b2b" if theme == "dark" else "#f5f5f5")
        main_frame.pack(side="right", fill="both", expand=True)

        # Navigation buttons
        patients_btn = tk.Button(nav_frame, text="👤 Patients", font=BIG_FONT, command=lambda: refresh_list(search_var.get()))
        patients_btn.pack(pady=10, padx=10, fill="x")

        add_btn = tk.Button(nav_frame, text="➕ Ajouter", font=BIG_FONT, command=open_add_window)
        add_btn.pack(pady=10, padx=10, fill="x")

        delete_btn = tk.Button(nav_frame, text="🗑 Supprimer", font=BIG_FONT, command=delete_patient)
        delete_btn.pack(pady=10, padx=10, fill="x")
        delete_btn.configure(
            bg="#d9534f",
            fg="white",
            activebackground="#c9302c",
            relief="flat",
            borderwidth=0
        )

        stats_btn = tk.Button(nav_frame, text="📊 Statistiques", font=BIG_FONT, command=show_charts)
        stats_btn.pack(pady=10, padx=10, fill="x")

        # Export button
        export_btn = tk.Button(nav_frame, text="📤 Exporter", font=BIG_FONT, command=export_data)
        export_btn.pack(pady=10, padx=10, fill="x")

        # Search functionality
        search_var = tk.StringVar()
        search_placeholder = "Rechercher..."
        search_is_placeholder = True
        
        def on_search_change(*args):
            if not search_is_placeholder:
                refresh_list(search_var.get())
        
        search_var.trace("w", on_search_change)
        search_var.set(search_placeholder)

        search_entry = tk.Entry(nav_frame, textvariable=search_var, font=FONT)
        search_entry.pack(padx=10, pady=20, fill="x")
        search_entry.bind("<FocusIn>", on_search_focus_in)
        search_entry.bind("<FocusOut>", on_search_focus_out)
        search_entry.configure(fg="#888888", relief="flat", borderwidth=1)

        # Theme toggle button
        theme_btn = tk.Button(root, text="☼ Mode", font=BIG_FONT, command=toggle_theme)
        theme_btn.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")
        theme_btn.configure(
            bg="#3a3a3a" if theme == "dark" else "#e0e0e0",
            fg="#ffffff" if theme == "dark" else "#333333",
            relief="flat",
            borderwidth=0
        )

        # Initialize display
        refresh_list()
        apply_theme()
        
        root.mainloop()
        
    except Exception as ui_error:
        messagebox.showerror("UI Error", f"Failed to create UI: {ui_error}")
        raise
    
except Exception as e:
    print(f"Critical error: {e}")
    messagebox.showerror("Erreur Critique", f"Erreur lors du lancement de l'application: {e}")
    raise