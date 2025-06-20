import tkinter as tk
import win32com.client
import tkinter.filedialog as filedialog
from tkinter import messagebox as mb
from PIL import Image, ImageTk
import os


#########################################
#          Define functions             #
#########################################

def obtener_nombre_desde_email(email):
    nombre_raw = email.split('@')[0]       
    nombre = nombre_raw.split('.')[0]        
    return nombre.capitalize()  
    
def update_ids_entry(*args):
    selected_project = project_selection.get()
    if selected_project in ["SE336/0EU_PS", "SE316_3EU_P1", "SE380/0EU_P1"]:
        IDS_entry.delete(0, tk.END)
        IDS_entry.insert(0, 'PV')
    else:
        IDS_entry.delete(0, tk.END)
        IDS_entry.insert(0, 'IDS')

def attach_files():
    global attached_files
    files = filedialog.askopenfilenames()
    attached_files.extend(files)
    update_file_listbox()

def delete_selected_file():
    global attached_files
    selected_index = file_listbox.curselection()
    if selected_index:
        selected_file = file_listbox.get(selected_index)
        attached_files.remove(selected_file)
        update_file_listbox()

def delete_all_files():
    global attached_files
    response = mb.askyesno(title="Warning!", message="Are you sure you want to delete all attached files?")
    if response:
        attached_files = []
        update_file_listbox()

def update_file_listbox():
    file_listbox.delete(0, tk.END)
    for file in attached_files:
        file_listbox.insert(tk.END, file)

def generate_template():
    status = status_selection.get()
    VR = VR_entry.get()
    year = year_entry.get()
    project = project_selection.get()
    IDS = IDS_entry.get() 
    NE = NE_entry.get()
    
    if project == "Select" or status == "Select" or VR == "" or IDS == "Select":
        mb.showwarning(title="Empty field", message="There is an empty field")
        return
    if not attached_files:
        mb.showwarning(title="Error!", message="Please attach a file!")
        return

    selected_project = project_selection.get()
    if selected_project == "Select":
        mb.showwarning(title="No Project Selected", message="Please select a project!")
        return
    
    To_recipient = project_data_To_list[selected_project]
    cc_recipients = project_data_cc_list[selected_project]
    nombre_destinatario = obtener_nombre_desde_email(To_recipient[0])

    template = f"Hola {nombre_destinatario}:\n\nLos resultados de las pruebas de HV-Safety son: {status}\n\n"
    template += f"El vehículo testeado corresponde a un {project} {IDS} actualizado a VR {VR}/{year}.\n\n"

    if status in ["i.O, con restricciones.", "n.I.O, con restricciones."]:
        template += "Adjunto el Excel con las restricciones.\n\n"

    template += "Un saludo,\n\n"

    result_text.config(state=tk.NORMAL)
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, template)
    result_text.config(state=tk.DISABLED)

    template_text = result_text.get("1.0", "end-1c")
    
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.Subject = f"HVSi ExtIBN {selected_project} -VR {VR}/{year}- {IDS} - {NE}" 
    mail.Body = template_text  
    mail.To = "".join(To_recipient)
    mail.CC = ";".join(cc_recipients)

    for file in attached_files:
        mail.Attachments.Add(Source=file)

    mail.Display()

#########################################
#          Window Settings              #
#########################################

# Window configuration
window = tk.Tk()
window.geometry("850x600")
window.title("HVSafety Email Generator")
attached_files = []
image_path = "im2.png"
original_image = Image.open(image_path)
resized_image = original_image.resize((250, 200)) 
image = ImageTk.PhotoImage(resized_image)
selector_1_var = tk.BooleanVar()
selector_2_var = tk.BooleanVar()

# Labels
tk.Label(window, image=image).grid(row=3, column=0,columnspan=6, rowspan=9, pady=5,padx=30, sticky='w')
tk.Label(window, text="Status:").grid(row=1, column=1, sticky='w', padx=(10, 5), pady=5)
tk.Label(window, text="Project:").grid(row=2, column=1, sticky='w', padx=(10, 5), pady=5)
tk.Label(window, text="IDS/PV:").grid(row=3, column=1, sticky='w', padx=(10, 5), pady=5)
tk.Label(window, text="VR:").grid(row=4, column=1, sticky='w', padx=(10, 5), pady=5)
tk.Label(window, text="Year:").grid(row=5, column=1, sticky='w', padx=(10, 5), pady=5)
tk.Label(window, text="NE:").grid(row=6, column=1, sticky='w', padx=(10, 5), pady=5)

# Selection labels
status_selection = tk.StringVar(window)
status_selection.set("Select")
status_options = ["i.O, sin restricciones.", "i.O, con restricciones." ,  "n.I.O, con restricciones."]
status_menu = tk.OptionMenu(window, status_selection, *status_options)
status_menu.grid(row=1, column=1, padx=(0, 30), pady=5)

project_selection = tk.StringVar(window)
project_selection.set("Select")
project_options = ["SE316_3EU_P1", "SE380/0EU_P1", "SE310_6EU_BS1", "SE336/0EU_PS", "SE316_8CM_BS", "SE210_EU_BS"]
project_menu = tk.OptionMenu(window, project_selection, *project_options)
project_menu.grid(row=2, column=1, padx=(0, 30), pady=5)

checkbox_1 = tk.Checkbutton(window, text="Restricción lámpara amarilla/roja", variable=selector_1_var)
checkbox_1.grid(row=7, column=1, sticky='w', padx=(10, 5), pady=5)
checkbox_2 = tk.Checkbutton(window, text="Restricción circular vía pública", variable=selector_2_var)
checkbox_2.grid(row=8, column=1, sticky='w', padx=(10, 5), pady=5)


# Entry labels
IDS_entry = tk.Entry(window)
IDS_entry.grid(row=3, column=1, padx=(0, 30), pady=5)
project_selection.trace_add('write', update_ids_entry)

VR_entry = tk.Entry(window)
VR_entry.grid(row=4, column=1, padx=(0, 30), pady=5)

year_entry = tk.Entry(window)
year_entry.insert(0, '25')
year_entry.grid(row=5, column=1, padx=(0, 30), pady=5)

NE_entry = tk.Entry(window)
NE_entry.insert(0, 'NE_2025_')
NE_entry.grid(row=6, column=1, padx=(0, 30), pady=5)

window.columnconfigure(0, weight=3)
window.columnconfigure(1, weight=2)

#########################################
#           Define buttons              #
#########################################

# Button to attach files
attach_button = tk.Button(window, text="Attach Files", command=attach_files)
attach_button.grid(row=12, column=1, sticky="w", padx=10, pady=10)

# Listbox to display attached files
file_listbox = tk.Listbox(window)
file_listbox.grid(row=11, column=1, padx=(10,30), pady=5, sticky="we")

# Button to delete selected file
delete_file_button = tk.Button(window, text="Delete Selected File", command=delete_selected_file)
delete_file_button.grid(row=12, column=1, padx=(0,30), pady=5)

# Button to delete all files
delete_all_button = tk.Button(window, text="Delete All Files", command=delete_all_files)
delete_all_button.grid(row=12, column=1, sticky="e", padx=30, pady=5)

# Button to Generate template
delete_all_button = tk.Button(window, text="Generate Email", command=generate_template)
delete_all_button.grid(row=13, column=1, padx=(0,30), pady=5)

#########################################
#            Project lists              #
#########################################

project_data_cc_list = {
    "SE316_3EU_P1": (["oscar1.garcia@seat.es ", "david.cejudo@seat.es", "andres.penalver@seat.es" , "marta.robledo@seat.es" , "eduardo1.lopez@seat.es" , "cesar.mendez@seat.es" , "hv_safety@seat.es" , "ruth.moreno@seat.es"]),
    "SE380/0EU_P1": (["oscar1.garcia@seat.es ", "david.cejudo@seat.es", "andres.penalver@seat.es" , "marta.robledo@seat.es" , "eduardo1.lopez@seat.es" , "cesar.mendez@seat.es" , "hv_safety@seat.es", "ruth.moreno@seat.es"]),
    "SE310_6EU_BS1": (["oscar1.garcia@seat.es", "andres.penalver@seat.es", "david.cejudo@seat.es" , "lluis.franch@seat.es" ,  "cesar.mendez@seat.es" , "marta.robledo@seat.es" , "hv_safety@seat.es"]),
    "SE210_EU_BS": (["oscar1.garcia@seat.es", "andres.penalver@seat.es", "david.cejudo@seat.es" , "lluis.franch@seat.es" ,  "cesar.mendez@seat.es" , "marta.robledo@seat.es" , "hv_safety@seat.es"]),
    "SE336/0EU_PS": (["oscar1.garcia@seat.es" , "david.cejudo@seat.es" , "andres.penalver@seat.es" , "marta.robledo@seat.es" , "eduardo1.lopez@seat.es" , "cesar.mendez@seat.es" , "hv_safety@seat.es" , "ruth.moreno@seat.es"]),
    "SE316_8CM_BS": (["andres.penalver@seat.es" , "david.cejudo@seat.es", "lluis.franch@seat.es" , "cesar.mendez@seat.es" , "oscar1.garcia@seat.es", "marta.robledo@seat.es" , "hv_safety@seat.es"])
}

project_data_To_list = {
   "SE316_3EU_P1": ["rafael.blazquez@seat.es"],
    "SE380/0EU_P1": ["rafael.blazquez@seat.es"],
    "SE310_6EU_BS1": ["eva.garcia@seat.es"],
    "SE210_EU_BS": ["eva.garcia@seat.es"],
    "SE336/0EU_PS": ["nils.boerner@seat.es"],
    "SE316_8CM_BS": ["fernando.zafra@seat.es"]
}

#########################################
#                RESULT                 #
#########################################

result_text = tk.Text()
result_text.config(state=tk.DISABLED)
project_selection.trace_add('write', update_ids_entry)
window.mainloop()
