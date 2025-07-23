import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from datetime import datetime, timedelta
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import calendar
from tkcalendar import Calendar
from collections import defaultdict
import requests
from urllib.parse import quote

class UserManager:
    """Clase para manejar el registro y autenticación de usuarios"""
    def __init__(self):
        self.users_file = "user_credentials.json"
        self.users = self.load_users()
    
    def load_users(self):
        """Cargar usuarios desde el archivo"""
        if os.path.exists(self.users_file):
            with open(self.users_file, "r") as f:
                return json.load(f)
        else:
            # Usuarios por defecto
            default_users = {
                "eugenio": {
                    "password": "Sanit3rd$hift",
                    "email": "eugenio.morales@casameats.com",
                    "email_config": {
                        "smtp_server": "smtp.office365.com",
                        "smtp_port": 587,
                        "sender_email": "eugenio.morales@casameats.com",
                        "sender_password": "Morales#2024",
                        "receiver_email": "elias.arroyo@casameats.com;reynaldo.montalvo-morales@casameats.com;daniel.moreno@casameats.com;francis.patterson@casameats.com;edgardo-rodriguez@casameats.com;joseph.zogby@casameats.com;juan.martinez-rivera@casameats.com;ramon.hernandez@casameats.com;christian.gonzales-vega@casameats.com;michael.whitehouse@casameats.com;markeith.atkins@casameats.com;keenan.atkins@casameats.com;paola.lopez-cordero@casameats.com;keyla.perez-perez@casameats.com;terry.everwine@casameats.com;miriam.velez@casameats.com;mario.gonzalez-igartua@casameats.com;joshuarivera@casameats.com;ltia.veney@casameats.com;lourdes-lugo@casameats.com;fiana.baker@casameats.com;phil.wagner@casameats.com"
                    }
                },
                "christian": {
                    "password": "VegaClean#24",
                    "email": "christian.gonzales-vega@casameats.com",
                    "email_config": {
                        "smtp_server": "smtp.office365.com",
                        "smtp_port": 587,
                        "sender_email": "christian.gonzales-vega@casameats.com",
                        "sender_password": "GonzalesVega$3",
                        "receiver_email": "elias.arroyo@casameats.com;reynaldo.montalvo-morales@casameats.com;daniel.moreno@casameats.com;francis.patterson@casameats.com;edgardo-rodriguez@casameats.com;joseph.zogby@casameats.com;juan.martinez-rivera@casameats.com;ramon.hernandez@casameats.com;eugenio.morales@casameats.com;michael.whitehouse@casameats.com;markeith.atkins@casameats.com;keenan.atkins@casameats.com;paola.lopez-cordero@casameats.com;keyla.perez-perez@casameats.com;terry.everwine@casameats.com;miriam.velez@casameats.com;mario.gonzalez-igartua@casameats.com;joshuarivera@casameats.com;ltia.veney@casameats.com;lourdes-lugo@casameats.com;fiana.baker@casameats.com;phil.wagner@casameats.com"
                    }
                }
            }
            self.save_users(default_users)
            return default_users
    
    def save_users(self, users=None):
        """Guardar usuarios en el archivo"""
        with open(self.users_file, "w") as f:
            json.dump(users or self.users, f, indent=4)
    
    def authenticate(self, username, password):
        """Autenticar un usuario"""
        return username in self.users and self.users[username]["password"] == password
    
    def register_user(self, username, password, email):
        """Registrar un nuevo usuario"""
        if username in self.users:
            return False, "Username already exists"
        
        self.users[username] = {
            "password": password,
            "email": email,
            "email_config": {
                "smtp_server": "",
                "smtp_port": 587,
                "sender_email": email,
                "sender_password": "",
                "receiver_email": ""
            }
        }
        self.save_users()
        return True, "User registered successfully"
    
    def update_email(self, username, new_email):
        """Actualizar el email de un usuario"""
        if username in self.users:
            self.users[username]["email"] = new_email
            self.users[username]["email_config"]["sender_email"] = new_email
            self.save_users()
            return True
        return False

class VacationCalendar:
    def __init__(self, parent, employees, main_app):
        self.parent = parent
        self.employees = employees
        self.main_app = main_app
        self.vacation_data = defaultdict(list)
        self.load_vacation_data()
        
        self.window = tk.Toplevel(parent)
        self.window.title("Vacation & Personal Days Calendar")
        self.window.geometry("1200x800")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de controles
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Selector de año (2024-2040 como solicitado)
        tk.Label(control_frame, text="Year:").pack(side=tk.LEFT, padx=5)
        self.year_var = tk.IntVar(value=datetime.now().year)
        year_menu = ttk.Combobox(control_frame, textvariable=self.year_var, 
                                values=list(range(2024, 2041)), width=5)  # 2024-2040
        year_menu.pack(side=tk.LEFT, padx=5)
        year_menu.bind("<<ComboboxSelected>>", self.update_calendar)
        
        # Selector de mes
        tk.Label(control_frame, text="Month:").pack(side=tk.LEFT, padx=5)
        self.month_var = tk.IntVar(value=datetime.now().month)
        month_menu = ttk.Combobox(control_frame, textvariable=self.month_var, 
                                 values=[(i, calendar.month_name[i]) for i in range(1, 13)], 
                                 width=10)
        month_menu.pack(side=tk.LEFT, padx=5)
        month_menu.bind("<<ComboboxSelected>>", self.update_calendar)
        
        # Botón para ir al mes actual
        tk.Button(control_frame, text="Current Month", 
                 command=self.go_to_current_month).pack(side=tk.LEFT, padx=10)
        
        # Botón para imprimir
        tk.Button(control_frame, text="Print Receipt", 
                 command=self.print_vacation_receipt).pack(side=tk.RIGHT, padx=5)
        
        # Frame del calendario
        calendar_frame = tk.Frame(main_frame)
        calendar_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Crear widget de calendario con más espacio para los nombres
        self.cal = Calendar(calendar_frame, selectmode='day', 
                          year=self.year_var.get(), 
                          month=self.month_var.get(),
                          showweeknumbers=False,
                          firstweekday='sunday',
                          font="Arial 10", 
                          headersbackground="#D2B48C",
                          normalbackground="#F5F5DC",
                          weekendbackground="#F5F5DC",
                          othermonthbackground="#E8E8E8",
                          selectbackground="#8B4513",
                          selectforeground="white",
                          cursor="hand1")
        self.cal.pack(fill=tk.BOTH, expand=True)
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)
        
        # Frame de información
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        # Información de la fecha seleccionada
        self.selected_date_label = tk.Label(info_frame, text="Selected Date: ", font=("Arial", 10, "bold"))
        self.selected_date_label.pack(side=tk.LEFT, padx=5)
        
        # Frame de edición
        edit_frame = tk.Frame(main_frame)
        edit_frame.pack(fill=tk.X, pady=5)
        
        # Selector de empleado
        tk.Label(edit_frame, text="Employee:").grid(row=0, column=0, padx=5, sticky="e")
        self.employee_var = tk.StringVar()
        self.employee_menu = ttk.Combobox(edit_frame, textvariable=self.employee_var, 
                                         values=sorted(self.employees), width=25)
        self.employee_menu.grid(row=0, column=1, padx=5, sticky="w")
        
        # Tipo de día
        tk.Label(edit_frame, text="Type:").grid(row=0, column=2, padx=5, sticky="e")
        self.type_var = tk.StringVar()
        type_menu = ttk.Combobox(edit_frame, textvariable=self.type_var, 
                                values=["Vacation", "Personal", "Sick"], width=10)
        type_menu.grid(row=0, column=3, padx=5, sticky="w")
        
        # Rango de fechas
        tk.Label(edit_frame, text="Start Date:").grid(row=1, column=0, padx=5, sticky="e")
        self.start_date_entry = ttk.Entry(edit_frame, width=10)
        self.start_date_entry.grid(row=1, column=1, padx=5, sticky="w")
        
        tk.Label(edit_frame, text="End Date:").grid(row=1, column=2, padx=5, sticky="e")
        self.end_date_entry = ttk.Entry(edit_frame, width=10)
        self.end_date_entry.grid(row=1, column=3, padx=5, sticky="w")
        
        # Botón para establecer rango desde selección
        tk.Button(edit_frame, text="Set Range", 
                 command=self.set_date_range).grid(row=1, column=4, padx=5)
        
        # Botones de acción
        button_frame = tk.Frame(edit_frame)
        button_frame.grid(row=2, column=0, columnspan=5, pady=10)
        
        tk.Button(button_frame, text="Add/Update", 
                 command=self.save_vacation_day, bg="#D2B48C").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", 
                 command=self.delete_vacation_day, bg="#D2B48C").pack(side=tk.LEFT, padx=5)
        
        # Notas
        tk.Label(edit_frame, text="Notes:").grid(row=3, column=0, padx=5, sticky="ne")
        self.notes_entry = tk.Text(edit_frame, height=4, width=50)
        self.notes_entry.grid(row=3, column=1, columnspan=4, padx=5, sticky="w")
        
        # Lista de vacaciones para la fecha seleccionada
        self.vacation_list_frame = tk.LabelFrame(main_frame, text="Scheduled Vacations/Personal Days")
        self.vacation_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.vacation_list = tk.Listbox(self.vacation_list_frame, height=5)
        self.vacation_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Actualizar el calendario con los datos existentes
        self.update_calendar_display()
    
    def set_date_range(self):
        selected_date = self.cal.selection_get()
        if not hasattr(self, 'start_date') or self.start_date is None:
            self.start_date = selected_date
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, selected_date.strftime("%m/%d/%Y"))
        else:
            self.end_date = selected_date
            self.end_date_entry.delete(0, tk.END)
            self.end_date_entry.insert(0, selected_date.strftime("%m/%d/%Y"))
    
    def load_vacation_data(self):
        try:
            if os.path.exists("vacation_data.json"):
                with open("vacation_data.json", "r") as f:
                    data = json.load(f)
                    # Convertir de formato antiguo a nuevo si es necesario
                    if isinstance(data, dict):
                        for date_str, entries in data.items():
                            if isinstance(entries, dict):  # Formato antiguo (solo un empleado por día)
                                self.vacation_data[date_str].append(entries)
                            elif isinstance(entries, list):  # Formato nuevo (múltiples empleados)
                                self.vacation_data[date_str].extend(entries)
                    elif isinstance(data, list):  # Formato muy antiguo (lista plana)
                        for entry in data:
                            date_str = entry.get("date")
                            if date_str:
                                self.vacation_data[date_str].append(entry)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load vacation data: {str(e)}")
    
    def save_vacation_data(self):
        try:
            with open("vacation_data.json", "w") as f:
                # Convertir defaultdict a dict normal para serialización
                json.dump(dict(self.vacation_data), f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save vacation data: {str(e)}")
    
    def update_calendar(self, event=None):
        """Actualizar el calendario cuando cambia el mes o año"""
        self.cal.config(year=self.year_var.get(), month=self.month_var.get())
        self.update_calendar_display()
    
    def go_to_current_month(self):
        """Ir al mes actual"""
        now = datetime.now()
        self.year_var.set(now.year)
        self.month_var.set(now.month)
        self.update_calendar()
    
    def update_calendar_display(self):
        """Actualizar la visualización del calendario con los datos de vacaciones"""
        # Limpiar todos los tags del calendario
        for tag in self.cal.calevent_tags():
            self.cal.tag_remove(tag, "date")
        
        # Añadir eventos al calendario
        for date_str, entries in self.vacation_data.items():
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                if date_obj.year == self.year_var.get() and date_obj.month == self.month_var.get():
                    # Crear texto para mostrar en el día
                    day_text = "\n".join([f"{e['employee']} ({e['type'][0]})" for e in entries])
                    
                    # Determinar color basado en el tipo
                    if any(e['type'] == "Vacation" for e in entries):
                        bg_color = "#8FBC8F"  # Verde claro
                    elif any(e['type'] == "Personal" for e in entries):
                        bg_color = "#ADD8E6"  # Azul claro
                    elif any(e['type'] == "Sick" for e in entries):
                        bg_color = "#FFA07A"  # Salmón claro
                    else:
                        bg_color = "#E8E8E8"  # Gris claro
                    
                    # Configurar tag y añadir al día
                    self.cal.tag_config(f"{date_str}_tag", background=bg_color, foreground="black")
                    self.cal.tag_add(f"{date_str}_tag", date_str)
                    
                    # Añadir texto al día
                    self.cal.calevent_create(date_obj, day_text, tags=[f"{date_str}_tag"])
            except ValueError:
                continue
    
    def on_date_select(self, event=None):
        """Manejador para cuando se selecciona una fecha en el calendario"""
        selected_date = self.cal.selection_get()
        date_str = selected_date.strftime("%Y-%m-%d")
        self.selected_date_label.config(text=f"Selected Date: {selected_date.strftime('%m/%d/%Y')}")
        
        # Limpiar campos
        self.employee_var.set("")
        self.type_var.set("")
        self.notes_entry.delete("1.0", tk.END)
        self.start_date = None
        self.end_date = None
        self.start_date_entry.delete(0, tk.END)
        self.end_date_entry.delete(0, tk.END)
        
        # Actualizar lista de vacaciones para esta fecha
        self.update_vacation_list(date_str)
    
    def update_vacation_list(self, date_str):
        """Actualizar la lista de vacaciones para la fecha seleccionada"""
        self.vacation_list.delete(0, tk.END)
        
        if date_str in self.vacation_data:
            for entry in self.vacation_data[date_str]:
                self.vacation_list.insert(tk.END, 
                                         f"{entry['employee']} - {entry['type']} - {entry.get('notes', '')}")
    
    def save_vacation_day(self):
        """Guardar un día de vacaciones/personal"""
        employee = self.employee_var.get()
        day_type = self.type_var.get()
        notes = self.notes_entry.get("1.0", tk.END).strip()
        
        if not employee or not day_type:
            messagebox.showwarning("Warning", "Please select an employee and type")
            return
        
        # Obtener rango de fechas
        start_date = self.start_date if hasattr(self, 'start_date') and self.start_date else self.cal.selection_get()
        end_date = self.end_date if hasattr(self, 'end_date') and self.end_date else start_date
        
        if start_date > end_date:
            messagebox.showwarning("Warning", "End date cannot be before start date")
            return
        
        # Crear entradas para cada día en el rango
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Crear nueva entrada
            new_entry = {
                "employee": employee,
                "type": day_type,
                "notes": notes,
                "recorded_by": self.main_app.username,
                "recorded_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
            
            # Añadir a los datos
            self.vacation_data[date_str].append(new_entry)
            
            # Siguiente día
            current_date += timedelta(days=1)
        
        self.save_vacation_data()
        self.update_calendar_display()
        self.update_vacation_list(self.cal.selection_get().strftime("%Y-%m-%d"))
        messagebox.showinfo("Success", f"{day_type} days saved for {employee}")
    
    def delete_vacation_day(self):
        """Eliminar una entrada de vacaciones/personal"""
        selection = self.vacation_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an entry to delete")
            return
            
        selected_date = self.cal.selection_get()
        date_str = selected_date.strftime("%Y-%m-%d")
        
        if date_str in self.vacation_data and self.vacation_data[date_str]:
            # Obtener el índice seleccionado
            idx = selection[0]
            
            # Obtener la entrada completa para mostrar en el mensaje de confirmación
            entry = self.vacation_data[date_str][idx]
            
            confirm = messagebox.askyesno("Confirm", 
                                        f"Delete {entry['type']} day for {entry['employee']} on {selected_date.strftime('%m/%d/%Y')}?")
            if confirm:
                # Eliminar solo esta entrada específica
                del self.vacation_data[date_str][idx]
                
                # Si no quedan más entradas para esta fecha, eliminar la fecha
                if not self.vacation_data[date_str]:
                    del self.vacation_data[date_str]
                
                self.save_vacation_data()
                self.update_calendar_display()
                self.update_vacation_list(date_str)
                
                messagebox.showinfo("Success", "Entry deleted successfully")
        else:
            messagebox.showwarning("Warning", "No entry to delete for selected date")
    
    def print_vacation_receipt(self):
        """Generar e imprimir un recibo de vacaciones/personal"""
        selection = self.vacation_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an entry to print")
            return
            
        selected_date = self.cal.selection_get()
        date_str = selected_date.strftime("%Y-%m-%d")
        entry = self.vacation_data[date_str][selection[0]]
        
        # Obtener todas las entradas para este rango de fechas
        start_date = datetime.strptime(entry['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(entry['end_date'], "%Y-%m-%d").date()
        
        # Crear ventana de impresión
        print_window = tk.Toplevel(self.window)
        print_window.title("Vacation Receipt")
        print_window.geometry("800x600")
        
        # Contenido del recibo
        receipt_text = tk.Text(print_window, wrap=tk.WORD, font=("Arial", 12))
        receipt_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Encabezado
        receipt_text.insert(tk.END, "CASA MEATS\n", "header")
        receipt_text.insert(tk.END, "Third Shift Sanitation\n\n", "header")
        receipt_text.insert(tk.END, f"{entry['type'].upper()} REQUEST RECEIPT\n\n", "title")
        
        # Información del empleado
        receipt_text.insert(tk.END, f"Employee: {entry['employee']}\n")
        receipt_text.insert(tk.END, f"Type: {entry['type']}\n")
        receipt_text.insert(tk.END, f"Recorded by: {entry['recorded_by']}\n")
        receipt_text.insert(tk.END, f"Recorded on: {entry['recorded_date']}\n\n")
        
        # Rango de fechas
        receipt_text.insert(tk.END, f"From: {start_date.strftime('%m/%d/%Y')}\n")
        receipt_text.insert(tk.END, f"To: {end_date.strftime('%m/%d/%Y')}\n")
        receipt_text.insert(tk.END, f"Total Days: {(end_date - start_date).days + 1}\n\n")
        
        # Mini calendario con los días marcados
        receipt_text.insert(tk.END, "Calendar:\n", "subheader")
        
        # Crear mini calendario para el mes
        cal = calendar.TextCalendar(calendar.SUNDAY)
        cal_str = cal.formatmonth(start_date.year, start_date.month)
        
        # Resaltar los días solicitados
        cal_lines = cal_str.split('\n')
        for i in range(len(cal_lines)):
            if i >= 2:  # Saltar las líneas de encabezado
                days = cal_lines[i].split()
                for j in range(len(days)):
                    try:
                        day = int(days[j])
                        current_date = datetime(start_date.year, start_date.month, day).date()
                        if start_date <= current_date <= end_date:
                            days[j] = f"[{day}]"
                    except ValueError:
                        pass
                cal_lines[i] = ' '.join(days)
        
        # Insertar el calendario modificado
        receipt_text.insert(tk.END, '\n'.join(cal_lines) + '\n\n')
        receipt_text.insert(tk.END, f"* Marked days: {entry['employee']}\n\n")
        
        # Notas
        if entry.get("notes"):
            receipt_text.insert(tk.END, "Notes:\n", "subheader")
            receipt_text.insert(tk.END, f"{entry['notes']}\n\n")
        
        # Firma
        receipt_text.insert(tk.END, "\n\n___________________________\n")
        receipt_text.insert(tk.END, "Employee Signature\n\n")
        receipt_text.insert(tk.END, "___________________________\n")
        receipt_text.insert(tk.END, "Supervisor Signature\n")
        
        # Configurar estilos
        receipt_text.tag_configure("header", font=("Arial", 14, "bold"), justify="center")
        receipt_text.tag_configure("title", font=("Arial", 16, "bold"), justify="center", foreground="blue")
        receipt_text.tag_configure("subheader", font=("Arial", 12, "bold"))
        
        # Botón de impresión
        print_button = tk.Button(print_window, text="Print Receipt", 
                               command=lambda: self.send_to_printer(receipt_text, "vacation_receipt"),
                               bg="#D2B48C")
        print_button.pack(side=tk.BOTTOM, pady=10)
        
        # Hacer el widget de texto de solo lectura
        receipt_text.config(state=tk.DISABLED)
    
    def send_to_printer(self, text_widget, filename_prefix):
        """Enviar el contenido a la impresora"""
        try:
            # Obtener todo el texto del widget
            text_widget.config(state=tk.NORMAL)
            content = text_widget.get("1.0", tk.END)
            text_widget.config(state=tk.DISABLED)
            
            # Crear archivo temporal
            filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w") as f:
                f.write(content)
            
            # Imprimir usando la impresora predeterminada del sistema (Windows)
            if os.name == 'nt':
                os.startfile(filename, "print")
                messagebox.showinfo("Print", "Document sent to printer")
            else:
                messagebox.showinfo("Print", f"Content saved to {filename}\nPrint from your system")
        except Exception as e:
            messagebox.showerror("Print Error", f"Could not print: {str(e)}")

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Casa Meats - Login")
        self.root.geometry("400x400")  # Aumentado para incluir registro
        self.root.configure(bg="#F5F5DC")
        
        self.user_manager = UserManager()
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#F5F5DC", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, 
                text="Casa Meats Sanitation System", 
                bg="#F5F5DC", 
                font=("Arial", 14, "bold")).pack(pady=(10, 20))
        
        # Frame de login
        login_frame = tk.LabelFrame(main_frame, text="Login", bg="#F5F5DC")
        login_frame.pack(fill=tk.X, pady=10)
        
        # Formulario de login
        form_frame = tk.Frame(login_frame, bg="#F5F5DC")
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="Username:", bg="#F5F5DC").grid(row=0, column=0, pady=5, sticky="e")
        self.username_entry = tk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(form_frame, text="Password:", bg="#F5F5DC").grid(row=1, column=0, pady=5, sticky="e")
        self.password_entry = tk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Botón de login
        tk.Button(login_frame, 
                 text="Login", 
                 command=self.attempt_login, 
                 bg="#D2B48C", 
                 width=15).pack(pady=10)
        
        # Frame de registro
        register_frame = tk.LabelFrame(main_frame, text="Register New User", bg="#F5F5DC")
        register_frame.pack(fill=tk.X, pady=10)
        
        # Formulario de registro
        reg_form_frame = tk.Frame(register_frame, bg="#F5F5DC")
        reg_form_frame.pack(pady=10)
        
        tk.Label(reg_form_frame, text="Username:", bg="#F5F5DC").grid(row=0, column=0, pady=5, sticky="e")
        self.reg_username_entry = tk.Entry(reg_form_frame)
        self.reg_username_entry.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(reg_form_frame, text="Password:", bg="#F5F5DC").grid(row=1, column=0, pady=5, sticky="e")
        self.reg_password_entry = tk.Entry(reg_form_frame, show="*")
        self.reg_password_entry.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(reg_form_frame, text="Email:", bg="#F5F5DC").grid(row=2, column=0, pady=5, sticky="e")
        self.reg_email_entry = tk.Entry(reg_form_frame)
        self.reg_email_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Botón de registro
        tk.Button(register_frame, 
                 text="Register", 
                 command=self.register_user, 
                 bg="#D2B48C", 
                 width=15).pack(pady=10)
        
        # Información de versión
        version_frame = tk.Frame(main_frame, bg="#F5F5DC")
        version_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        tk.Label(version_frame, 
                text="Version 2.0", 
                bg="#F5F5DC", 
                font=("Arial", 8)).pack(side=tk.LEFT)
        
        tk.Label(version_frame, 
                text="Created by Eugenio Morales - Sanitation Team Lead", 
                bg="#F5F5DC", 
                font=("Arial", 8)).pack(side=tk.RIGHT)
    
    def attempt_login(self):
        username = self.username_entry.get().lower()
        password = self.password_entry.get()
        
        if self.user_manager.authenticate(username, password):
            email_config = self.user_manager.users[username]["email_config"]
            self.root.destroy()
            root = tk.Tk()
            app = AttendanceApp(root, username, email_config)
            root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    def register_user(self):
        username = self.reg_username_entry.get().lower()
        password = self.reg_password_entry.get()
        email = self.reg_email_entry.get()
        
        if not username or not password or not email:
            messagebox.showwarning("Warning", "All fields are required")
            return
        
        success, message = self.user_manager.register_user(username, password, email)
        if success:
            messagebox.showinfo("Success", message)
            self.reg_username_entry.delete(0, tk.END)
            self.reg_password_entry.delete(0, tk.END)
            self.reg_email_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", message)

class AttendanceApp:
    def __init__(self, root, username, email_config):
        self.root = root
        self.username = username
        self.email_config = email_config
        
        self.root.title(f"Attendance System - Casa Meats (User: {username})")
        self.root.geometry("1200x800")
        self.root.configure(bg="#F5F5DC")
        
        # Configuración de colores
        self.main_color = "#FFFFE0"
        self.secondary_color = "#D2B48C"
        self.button_color = "#E6D5B8"
        self.entry_color = "#FFFFFF"
        self.summary_color = "#E8F4F8"
        
        # Lista de empleados
        self.employees = [
            'Christian Gonzalez', 'Heriberta Nicolas', 'Felix Sanchez', 'Brian Garcia',
            'Miguel Rios', 'Juan Morales', 'Chris Money', 'David Rivera', 
            'Landron Cristopher', 'Ruben Rodriguez', 'Rafael Rivera', 'Edgar Cortes', 
            'Donta Thompson', 'Eric Cardona', 'Wilmaris Cevilla', 'Laplante Edmond', 
            'Saint Zidor', 'Johncy Joseph', 'Israel Rivera', 'Wiliston', 'Eduard', 
            'Joel Delva', 'Jeanot Verger', 'Perlino Choc'
        ]
        
        # Almacenamiento de datos
        self.attendance = {}
        self.counters = {}
        self.daily_data = {}
        self.employee_comments = {}
        self.load_data()
        
        # Variables de control
        self.current_date = datetime.now().date()
        self.selected_employee = tk.StringVar()
        self.point_type = tk.IntVar(value=0)
        self.attendance_status = tk.StringVar(value="present")
        self.ppm_yellow = tk.StringVar()
        self.ppm_clear = tk.StringVar()
        self.daily_notes = tk.StringVar()
        self.inedible_weight = tk.StringVar()
        self.rte_start = tk.StringVar()
        self.rte_end = tk.StringVar()
        self.qa_raw_start = tk.StringVar()
        self.qa_raw_end = tk.StringVar()
        self.daily_comment = tk.StringVar()
        self.cook_room_time = tk.StringVar()

        # Inicializar interfaz
        self.create_interface()
        self.configure_copy_paste()
        self.add_version_info()
        self.load_daily_data()
    
    def add_version_info(self):
        version_frame = tk.Frame(self.root, bg=self.secondary_color)
        version_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Label(version_frame, 
                text=f"Version 2.0 | User: {self.username} | Created by Eugenio Morales - Sanitation Team Lead", 
                bg=self.secondary_color, 
                font=("Arial", 8)).pack(pady=5)
    
    def configure_copy_paste(self):
        # Atajos de teclado
        self.root.bind_all("<Control-c>", lambda e: self.root.focus_get().event_generate("<<Copy>>"))
        self.root.bind_all("<Control-v>", lambda e: self.root.focus_get().event_generate("<<Paste>>"))
        self.root.bind_all("<Control-x>", lambda e: self.root.focus_get().event_generate("<<Cut>>"))
        
        # Menú contextual
        def show_context_menu(event):
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Cut", command=lambda: self.root.focus_get().event_generate("<<Cut>>"))
            menu.add_command(label="Copy", command=lambda: self.root.focus_get().event_generate("<<Copy>>"))
            menu.add_command(label="Paste", command=lambda: self.root.focus_get().event_generate("<<Paste>>"))
            menu.tk.call("tk_popup", menu, event.x_root, event.y_root)
        
        # Aplicar a widgets de entrada
        widgets = ['ppm_yellow_entry', 'ppm_clear_entry', 'inedible_entry',
                  'rte_start_entry', 'rte_end_entry', 
                  'qa_raw_start_entry', 'qa_raw_end_entry', 'notes_text',
                  'comment_entry', 'cook_room_entry']
        
        for widget in widgets:
            if hasattr(self, widget):
                getattr(self, widget).bind("<Button-3>", show_context_menu)
    
    def create_interface(self):
        # Contenedor principal
        main_container = tk.Frame(self.root, bg=self.main_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de título
        title_frame = tk.Frame(main_container, bg=self.secondary_color)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(title_frame, 
                text="Casa Meats - Third Shift Sanitation", 
                bg=self.secondary_color, 
                font=("Arial", 14, "bold")).pack(pady=5)
        
        # Frame de navegación
        nav_frame = tk.Frame(main_container, bg=self.secondary_color, padx=5, pady=5)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Navegación por fechas
        tk.Button(nav_frame, 
                 text="Today", 
                 command=self.go_to_today, 
                 bg=self.button_color).pack(side=tk.LEFT, padx=5)
        
        tk.Button(nav_frame, 
                 text="<", 
                 command=self.previous_day, 
                 bg=self.button_color).pack(side=tk.LEFT, padx=5)
        
        tk.Button(nav_frame, 
                 text=">", 
                 command=self.next_day, 
                 bg=self.button_color).pack(side=tk.LEFT, padx=5)
        
        # Date selection with month and year dropdowns
        date_sel_frame = tk.Frame(nav_frame, bg=self.secondary_color)
        date_sel_frame.pack(side=tk.LEFT, padx=10)
        
        # Month dropdown
        self.month_var = tk.StringVar()
        self.month_var.set(self.current_date.strftime("%m"))
        month_menu = ttk.Combobox(date_sel_frame, textvariable=self.month_var, 
                                 values=[f"{i:02d}" for i in range(1, 13)], width=3)
        month_menu.pack(side=tk.LEFT)
        month_menu.bind("<<ComboboxSelected>>", self.update_date_from_dropdowns)
        
        tk.Label(date_sel_frame, text="/", bg=self.secondary_color).pack(side=tk.LEFT)
        
        # Year dropdown (2024-2040 como solicitado)
        self.year_var = tk.StringVar()
        self.year_var.set(self.current_date.strftime("%Y"))
        year_menu = ttk.Combobox(date_sel_frame, textvariable=self.year_var, 
                                values=[str(i) for i in range(2024, 2041)], width=5)  # 2024-2040
        year_menu.pack(side=tk.LEFT)
        year_menu.bind("<<ComboboxSelected>>", self.update_date_from_dropdowns)
        
        # Day dropdown
        self.day_var = tk.StringVar()
        self.day_var.set(self.current_date.strftime("%d"))
        self.day_menu = ttk.Combobox(date_sel_frame, textvariable=self.day_var, 
                                    values=[f"{i:02d}" for i in range(1, 32)], width=3)
        self.day_menu.pack(side=tk.LEFT)
        self.day_menu.bind("<<ComboboxSelected>>", self.update_date_from_dropdowns)
        
        # Fecha actual
        self.date_label = tk.Label(nav_frame, 
                                 text=self.current_date.strftime("%m/%d/%Y"), 
                                 bg=self.secondary_color, 
                                 font=("Arial", 12, "bold"))
        self.date_label.pack(side=tk.LEFT, padx=20)
        
        # Botón de actualización
        tk.Button(nav_frame,
                 text="Refresh",
                 command=self.refresh_data,
                 bg=self.button_color).pack(side=tk.RIGHT, padx=5)
        
        # Botón para editar email
        tk.Button(nav_frame,
                 text="Edit Email",
                 command=self.edit_user_email,
                 bg=self.button_color).pack(side=tk.RIGHT, padx=5)
        
        # Panel izquierdo (empleados y registro)
        left_panel = tk.Frame(main_container, bg=self.main_color)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Frame de empleados
        employees_frame = tk.LabelFrame(left_panel, text="Employees", bg=self.main_color)
        employees_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(employees_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.employees_listbox = tk.Listbox(employees_frame, 
                                          height=15, 
                                          selectmode=tk.SINGLE,
                                          yscrollcommand=scrollbar.set, 
                                          bg=self.entry_color)
        self.employees_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.employees_listbox.yview)
        
        self.update_employees_list()
        
        # Botones de empleados
        btn_frame = tk.Frame(employees_frame, bg=self.main_color)
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(btn_frame, 
                 text="Add Employee", 
                 command=self.add_employee, 
                 bg=self.button_color).pack(side=tk.LEFT, padx=5, expand=True)
        
        tk.Button(btn_frame, 
                 text="Remove Employee", 
                 command=self.remove_employee, 
                 bg=self.button_color).pack(side=tk.LEFT, padx=5, expand=True)
        
        # Frame de registro
        register_frame = tk.LabelFrame(left_panel, text="Attendance Registration", bg=self.main_color)
        register_frame.pack(fill=tk.X, pady=5)
        
        # Estado de asistencia
        attendance_frame = tk.LabelFrame(register_frame, text="Attendance Status", bg=self.main_color)
        attendance_frame.pack(fill=tk.X, pady=5)
        
        statuses = [("Present", "present"), ("Absent", "absent"), 
                  ("Late", "late"), ("Vacation", "vacation"), 
                  ("Personal", "personal")]
        
        for text, value in statuses:
            tk.Radiobutton(attendance_frame, 
                         text=text, 
                         variable=self.attendance_status, 
                         value=value, 
                         bg=self.main_color).pack(anchor="w")
        
        # Acción disciplinaria
        points_frame = tk.LabelFrame(register_frame, text="Disciplinary Action (0-6)", bg=self.main_color)
        points_frame.pack(fill=tk.X, pady=5)
        
        for i in range(0, 7):
            text = f"{i}"
            if i == 0: text += " (No action)"
            elif i == 4: text += " (Verbal)"
            elif i == 5: text += " (Written)"
            elif i == 6: text += " (Final)"
                
            tk.Radiobutton(points_frame, 
                         text=text, 
                         variable=self.point_type, 
                         value=i, 
                         bg=self.main_color).pack(anchor="w")
        
        # Botón de registro
        tk.Button(register_frame, 
                 text="Record Attendance", 
                 command=self.record_attendance,
                 bg=self.button_color, 
                 font=("Arial", 10, "bold")).pack(fill=tk.X, pady=10)
        
        # Contadores
        counters_frame = tk.LabelFrame(register_frame, text="Counters", bg=self.main_color)
        counters_frame.pack(fill=tk.X, pady=5)
        
        self.counters_label = tk.Label(counters_frame, 
                                     text="Select an employee", 
                                     bg=self.main_color, 
                                     justify=tk.LEFT)
        self.counters_label.pack(anchor="w")
        
        # Panel central (datos de producción)
        middle_panel = tk.Frame(main_container, bg=self.main_color)
        middle_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame de producción
        production_frame = tk.LabelFrame(middle_panel, text="Daily Sanitation Data", bg=self.main_color)
        production_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Fila superior
        top_row = tk.Frame(production_frame, bg=self.main_color)
        top_row.pack(fill=tk.X, pady=5)
        
        # Horas totales
        hours_frame = tk.Frame(top_row, bg=self.main_color)
        hours_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(hours_frame, text="Total Hours:", bg=self.main_color).pack(anchor="w")
        self.total_hours_label = tk.Label(hours_frame, 
                                        text="0", 
                                        bg=self.entry_color,
                                        relief=tk.SUNKEN, 
                                        width=10)
        self.total_hours_label.pack(side=tk.LEFT, padx=5)
        
        # PPM Amarillo
        ppm_yellow_frame = tk.Frame(top_row, bg=self.main_color)
        ppm_yellow_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(ppm_yellow_frame, text="PPM Yellow LP:", bg=self.main_color).pack(anchor="w")
        self.ppm_yellow_entry = tk.Entry(ppm_yellow_frame, 
                                       textvariable=self.ppm_yellow,
                                       bg=self.entry_color, 
                                       width=10)
        self.ppm_yellow_entry.pack(side=tk.LEFT, padx=5)
        
        # PPM Claro
        ppm_clear_frame = tk.Frame(top_row, bg=self.main_color)
        ppm_clear_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(ppm_clear_frame, text="PPM Clear V:", bg=self.main_color).pack(anchor="w")
        self.ppm_clear_entry = tk.Entry(ppm_clear_frame, 
                                      textvariable=self.ppm_clear,
                                      bg=self.entry_color, 
                                      width=10)
        self.ppm_clear_entry.pack(side=tk.LEFT, padx=5)
        
        # Peso no comestible
        inedible_frame = tk.Frame(top_row, bg=self.main_color)
        inedible_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(inedible_frame, text="Inedible Weight:", bg=self.main_color).pack(anchor="w")
        self.inedible_entry = tk.Entry(inedible_frame, 
                                     textvariable=self.inedible_weight,
                                     bg=self.entry_color, 
                                     width=10)
        self.inedible_entry.pack(side=tk.LEFT, padx=5)
        
        # Cook Room Time
        cook_room_frame = tk.Frame(top_row, bg=self.main_color)
        cook_room_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(cook_room_frame, text="Cook Room Time:", bg=self.main_color).pack(anchor="w")
        self.cook_room_entry = tk.Entry(cook_room_frame, 
                                      textvariable=self.cook_room_time,
                                      bg=self.entry_color, 
                                      width=10)
        self.cook_room_entry.pack(side=tk.LEFT, padx=5)
        
        # Fila media
        middle_row = tk.Frame(production_frame, bg=self.main_color)
        middle_row.pack(fill=tk.X, pady=5)
        
        # Inspección RTE
        rte_frame = tk.Frame(middle_row, bg=self.main_color)
        rte_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(rte_frame, text="RTE Inspection:", bg=self.main_color).pack(anchor="w")
        
        rte_subframe = tk.Frame(rte_frame, bg=self.main_color)
        rte_subframe.pack()
        
        tk.Label(rte_subframe, text="Start:", bg=self.main_color).grid(row=0, column=0, sticky="e")
        self.rte_start_entry = tk.Entry(rte_subframe, 
                                      textvariable=self.rte_start,
                                      bg=self.entry_color, 
                                      width=8)
        self.rte_start_entry.grid(row=0, column=1, padx=2)
        
        tk.Label(rte_subframe, text="End:", bg=self.main_color).grid(row=0, column=2, padx=(5,2))
        self.rte_end_entry = tk.Entry(rte_subframe, 
                                    textvariable=self.rte_end,
                                    bg=self.entry_color, 
                                    width=8)
        self.rte_end_entry.grid(row=0, column=3)
        
        # Inspección QA RAW
        qa_raw_frame = tk.Frame(middle_row, bg=self.main_color)
        qa_raw_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(qa_raw_frame, text="QA RAW Inspection:", bg=self.main_color).pack(anchor="w")
        
        qa_raw_subframe = tk.Frame(qa_raw_frame, bg=self.main_color)
        qa_raw_subframe.pack()
        
        tk.Label(qa_raw_subframe, text="Start:", bg=self.main_color).grid(row=0, column=0, sticky="e")
        self.qa_raw_start_entry = tk.Entry(qa_raw_subframe, 
                                         textvariable=self.qa_raw_start,
                                         bg=self.entry_color, 
                                         width=8)
        self.qa_raw_start_entry.grid(row=0, column=1, padx=2)
        
        tk.Label(qa_raw_subframe, text="End:", bg=self.main_color).grid(row=0, column=2, padx=(5,2))
        self.qa_raw_end_entry = tk.Entry(qa_raw_subframe, 
                                      textvariable=self.qa_raw_end,
                                      bg=self.entry_color, 
                                      width=8)
        self.qa_raw_end_entry.grid(row=0, column=3)
        
        # Fila inferior (notas y botones)
        bottom_row = tk.Frame(production_frame, bg=self.main_color)
        bottom_row.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame de notas
        notes_frame = tk.Frame(bottom_row, bg=self.main_color)
        notes_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(notes_frame, text="Important notes:", bg=self.main_color).pack(anchor="w")
        
        self.notes_text = tk.Text(notes_frame, 
                                height=8, 
                                width=40, 
                                bg=self.entry_color)
        self.notes_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame de botones de producción
        btn_prod_frame = tk.Frame(bottom_row, bg=self.main_color, width=150)
        btn_prod_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        tk.Button(btn_prod_frame, 
                 text="Save Data", 
                 command=self.save_production, 
                 bg=self.button_color).pack(fill=tk.X, pady=5)
        
        tk.Button(btn_prod_frame, 
                 text="Vacation Calendar", 
                 command=self.open_vacation_calendar, 
                 bg=self.button_color).pack(fill=tk.X, pady=5)
        
        tk.Button(btn_prod_frame, 
                 text="Email Settings", 
                 command=self.configure_email, 
                 bg=self.button_color).pack(fill=tk.X, pady=5)
        
        tk.Button(btn_prod_frame, 
                 text="Send Report", 
                 command=self.send_email_report, 
                 bg=self.button_color).pack(fill=tk.X, pady=5)
        
        # Panel derecho (resumen e historial)
        right_panel = tk.Frame(main_container, bg=self.main_color)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame de resumen del empleado
        summary_frame = tk.LabelFrame(right_panel, text="Employee Summary", bg=self.summary_color)
        summary_frame.pack(fill=tk.X, pady=5)
        
        # Contenido del resumen
        self.summary_text = scrolledtext.ScrolledText(summary_frame, 
                                                    height=10, 
                                                    wrap=tk.WORD,
                                                    bg=self.summary_color,
                                                    font=("Arial", 10))
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.summary_text.insert(tk.END, "Select an employee to view summary")
        self.summary_text.config(state=tk.DISABLED)
        
        # Botón para imprimir resumen
        tk.Button(summary_frame, 
                 text="Print Summary", 
                 command=self.print_employee_summary,
                 bg=self.button_color).pack(fill=tk.X, pady=5)
        
        # Frame de comentarios diarios
        comments_frame = tk.LabelFrame(right_panel, text="Daily Comments", bg=self.main_color)
        comments_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Entrada de comentario
        tk.Label(comments_frame, text="Today's Comment:", bg=self.main_color).pack(anchor="w")
        self.comment_entry = tk.Entry(comments_frame, 
                                    textvariable=self.daily_comment,
                                    bg=self.entry_color)
        self.comment_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame para botones de comentarios
        comment_btn_frame = tk.Frame(comments_frame, bg=self.main_color)
        comment_btn_frame.pack(fill=tk.X, pady=5)
        
        # Botón para guardar comentario
        tk.Button(comment_btn_frame, 
                 text="Save Comment", 
                 command=self.save_daily_comment,
                 bg=self.button_color).pack(side=tk.LEFT, padx=5, expand=True)
        
        # Botón para borrar comentario
        tk.Button(comment_btn_frame, 
                 text="Delete Comment", 
                 command=self.delete_daily_comment,
                 bg=self.button_color).pack(side=tk.LEFT, padx=5, expand=True)
        
        # Comentarios anteriores
        tk.Label(comments_frame, text="Previous Comments:", bg=self.main_color).pack(anchor="w")
        self.comments_text = scrolledtext.ScrolledText(comments_frame, 
                                                     height=6, 
                                                     wrap=tk.WORD,
                                                     bg=self.entry_color)
        self.comments_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.comments_text.insert(tk.END, "No comments available")
        self.comments_text.config(state=tk.DISABLED)
        
        # Frame de historial
        history_frame = tk.LabelFrame(right_panel, text="Employee History", bg=self.main_color)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview para historial
        tree_scroll_y = tk.Scrollbar(history_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = tk.Scrollbar(history_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.history_tree = ttk.Treeview(history_frame, 
                                       columns=("date", "status", "points", "type"), 
                                       show="headings", 
                                       yscrollcommand=tree_scroll_y.set,
                                       xscrollcommand=tree_scroll_x.set)
        
        self.history_tree.heading("date", text="Date")
        self.history_tree.heading("status", text="Status")
        self.history_tree.heading("points", text="Points")
        self.history_tree.heading("type", text="Disciplinary Action")
        
        self.history_tree.column("date", width=100, anchor=tk.CENTER)
        self.history_tree.column("status", width=80, anchor=tk.CENTER)
        self.history_tree.column("points", width=60, anchor=tk.CENTER)
        self.history_tree.column("type", width=120, anchor=tk.CENTER)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y.config(command=self.history_tree.yview)
        tree_scroll_x.config(command=self.history_tree.xview)
        
        # Botón para imprimir historial
        print_button = tk.Button(history_frame, 
                               text="Print History", 
                               command=self.print_history,
                               bg=self.button_color)
        print_button.pack(side=tk.BOTTOM, pady=5)
        
        # Eventos
        self.employees_listbox.bind("<<ListboxSelect>>", self.show_employee_data)
    
    def edit_user_email(self):
        """Permitir al usuario editar su email"""
        user_manager = UserManager()
        current_email = user_manager.users[self.username]["email"]
        
        new_email = simpledialog.askstring("Edit Email", 
                                          "Enter your new email address:",
                                          initialvalue=current_email)
        
        if new_email and new_email != current_email:
            if user_manager.update_email(self.username, new_email):
                messagebox.showinfo("Success", "Email updated successfully")
            else:
                messagebox.showerror("Error", "Could not update email")
    
    def open_vacation_calendar(self):
        """Abrir la ventana del calendario de vacaciones mejorado"""
        VacationCalendar(self.root, self.employees, self)
    
    def delete_daily_comment(self):
        """Borrar el comentario diario del empleado seleccionado"""
        selection = self.employees_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select an employee first")
            return
            
        employee = self.employees_listbox.get(selection)
        date_str = self.current_date.strftime("%Y-%m-%d")
        
        if employee in self.employee_comments and date_str in self.employee_comments[employee]:
            del self.employee_comments[employee][date_str]
            self.save_data()
            self.show_employee_comments()
            messagebox.showinfo("Success", "Comment deleted successfully")
        else:
            messagebox.showwarning("Warning", "No comment to delete")
    
    def update_date_from_dropdowns(self, event=None):
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            day = int(self.day_var.get())
            
            # Validar día para el mes seleccionado
            last_day = 31
            if month in [4, 6, 9, 11]:
                last_day = 30
            elif month == 2:
                last_day = 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
            
            day = min(day, last_day)
            self.day_var.set(f"{day:02d}")
            
            # Actualizar días disponibles en el dropdown
            self.day_menu['values'] = [f"{i:02d}" for i in range(1, last_day + 1)]
            
            self.current_date = datetime(year, month, day).date()
            self.update_date()
            self.load_daily_data()
        except ValueError:
            pass
    
    def show_employee_data(self, event=None):
        """Mostrar todos los datos del empleado seleccionado"""
        self.show_history()
        self.show_employee_summary()
        self.show_employee_comments()
    
    def show_employee_summary(self):
        """Mostrar resumen del empleado seleccionado"""
        selection = self.employees_listbox.curselection()
        if not selection:
            return
            
        employee = self.employees_listbox.get(selection)
        
        # Calcular totales
        total_points = 0
        vacation_dates = []
        personal_dates = []
        absent_dates = []
        late_dates = []
        
        if employee in self.attendance:
            for date_str, record in self.attendance[employee].items():
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                formatted_date = date.strftime("%m/%d/%Y")
                
                total_points += record["points"]
                
                if record["status"] == "vacation":
                    vacation_dates.append(formatted_date)
                elif record["status"] == "personal":
                    personal_dates.append(formatted_date)
                elif record["status"] == "absent":
                    absent_dates.append(formatted_date)
                elif record["status"] == "late":
                    late_dates.append(formatted_date)
        
        # Preparar texto del resumen
        summary = f"Summary for: {employee}\n\n"
        summary += f"Total Points: {total_points}\n\n"
        
        summary += f"Vacation Days: {len(vacation_dates)}\n"
        if vacation_dates:
            summary += "Dates: " + ", ".join(vacation_dates) + "\n"
        
        summary += f"\nPersonal Days: {len(personal_dates)}\n"
        if personal_dates:
            summary += "Dates: " + ", ".join(personal_dates) + "\n"
        
        summary += f"\nAbsences: {len(absent_dates)}\n"
        if absent_dates:
            summary += "Dates: " + ", ".join(absent_dates) + "\n"
        
        summary += f"\nLate Arrivals: {len(late_dates)}\n"
        if late_dates:
            summary += "Dates: " + ", ".join(late_dates) + "\n"
        
        # Actualizar visualización
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state=tk.DISABLED)
    
    def show_employee_comments(self):
        """Mostrar comentarios del empleado seleccionado"""
        selection = self.employees_listbox.curselection()
        if not selection:
            return
            
        employee = self.employees_listbox.get(selection)
        
        # Actualizar entrada de comentario con el de hoy si existe
        date_str = self.current_date.strftime("%Y-%m-%d")
        if employee in self.employee_comments and date_str in self.employee_comments[employee]:
            self.daily_comment.set(self.employee_comments[employee][date_str])
        else:
            self.daily_comment.set("")
        
        # Preparar historial de comentarios
        comments_text = ""
        if employee in self.employee_comments:
            dates = sorted(self.employee_comments[employee].keys(), reverse=True)
            for date_str in dates:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                formatted_date = date.strftime("%m/%d/%Y")
                comment = self.employee_comments[employee][date_str]
                comments_text += f"{formatted_date}: {comment}\n\n"
        
        # Actualizar visualización
        self.comments_text.config(state=tk.NORMAL)
        self.comments_text.delete(1.0, tk.END)
        if comments_text:
            self.comments_text.insert(tk.END, comments_text)
        else:
            self.comments_text.insert(tk.END, "No comments available for this employee")
        self.comments_text.config(state=tk.DISABLED)
    
    def save_daily_comment(self):
        """Guardar un comentario diario para el empleado seleccionado"""
        selection = self.employees_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select an employee first")
            return
            
        employee = self.employees_listbox.get(selection)
        comment = self.daily_comment.get().strip()
        date_str = self.current_date.strftime("%Y-%m-%d")
        
        if not comment:
            messagebox.showwarning("Warning", "Comment cannot be empty")
            return
        
        if employee not in self.employee_comments:
            self.employee_comments[employee] = {}
        
        self.employee_comments[employee][date_str] = comment
        self.save_data()
        self.show_employee_comments()
        messagebox.showinfo("Success", "Comment saved successfully")
    
    def print_employee_summary(self):
        """Imprimir el resumen del empleado"""
        selection = self.employees_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an employee first")
            return
            
        employee = self.employees_listbox.get(selection)
        
        # Obtener el texto del resumen
        self.summary_text.config(state=tk.NORMAL)
        summary = self.summary_text.get(1.0, tk.END)
        self.summary_text.config(state=tk.DISABLED)
        
        # Crear ventana temporal para imprimir
        print_window = tk.Toplevel(self.root)
        print_window.title(f"Print Summary - {employee}")
        print_window.geometry("800x600")
        
        # Crear widget de texto para mostrar contenido imprimible
        text_widget = tk.Text(print_window, wrap=tk.WORD, font=("Arial", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Añadir encabezado
        text_widget.insert(tk.END, f"Employee Summary Report\n", "header")
        text_widget.insert(tk.END, f"Employee: {employee}\n", "header")
        text_widget.insert(tk.END, f"Generated on: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}\n\n", "header")
        text_widget.tag_configure("header", font=("Arial", 12, "bold"), justify="center")
        
        # Añadir contenido del resumen
        text_widget.insert(tk.END, summary)
        
        # Botón de impresión
        print_button = tk.Button(print_window, 
                               text="Print", 
                               command=lambda: self.send_to_printer(text_widget, f"{employee}_summary"),
                               bg=self.button_color)
        print_button.pack(side=tk.BOTTOM, pady=10)
        
        # Hacer el widget de texto de solo lectura
        text_widget.config(state=tk.DISABLED)
    
    def print_history(self):
        """Imprimir el historial del empleado"""
        selection = self.employees_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an employee first")
            return
            
        employee = self.employees_listbox.get(selection)
        
        # Crear ventana temporal para imprimir
        print_window = tk.Toplevel(self.root)
        print_window.title(f"Print History - {employee}")
        print_window.geometry("800x600")
        
        # Crear widget de texto para mostrar contenido imprimible
        text_widget = tk.Text(print_window, wrap=tk.WORD, font=("Arial", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Añadir encabezado
        text_widget.insert(tk.END, f"Employee History Report\n", "header")
        text_widget.insert(tk.END, f"Employee: {employee}\n", "header")
        text_widget.insert(tk.END, f"Generated on: {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}\n\n", "header")
        text_widget.tag_configure("header", font=("Arial", 12, "bold"), justify="center")
        
        # Añadir encabezados de tabla
        text_widget.insert(tk.END, f"{'Date':<15}{'Status':<15}{'Points':<10}{'Disciplinary Action':<20}\n", "table_header")
        text_widget.insert(tk.END, "-"*60 + "\n", "table_header")
        text_widget.tag_configure("table_header", font=("Arial", 10, "bold"))
        
        # Añadir datos del historial
        if employee in self.attendance:
            dates = sorted(self.attendance[employee].keys(), reverse=True)
            one_year_ago = self.current_date - timedelta(days=365)
            
            for date_str in dates:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if date >= one_year_ago and date <= self.current_date:
                    record = self.attendance[employee][date_str]
                    text_widget.insert(tk.END, 
                                     f"{date.strftime('%m/%d/%Y'):<15}"
                                     f"{record['status'].capitalize():<15}"
                                     f"{record['points']:<10}"
                                     f"{record['type'].capitalize():<20}\n")
        
        # Añadir contadores si están disponibles
        if employee in self.counters:
            counters = self.counters[employee]
            text_widget.insert(tk.END, "\nCounters:\n", "subheader")
            text_widget.insert(tk.END, f"Vacation: {counters['vacation']}\n")
            text_widget.insert(tk.END, f"Personal: {counters['personal']}\n")
            text_widget.insert(tk.END, f"Late: {counters['late']}\n")
            text_widget.tag_configure("subheader", font=("Arial", 10, "bold"))
        
        # Botón de impresión
        print_button = tk.Button(print_window, 
                               text="Print", 
                               command=lambda: self.send_to_printer(text_widget, f"{employee}_history"),
                               bg=self.button_color)
        print_button.pack(side=tk.BOTTOM, pady=10)
        
        # Hacer el widget de texto de solo lectura
        text_widget.config(state=tk.DISABLED)
    
    def send_to_printer(self, text_widget, filename_prefix):
        """Enviar el contenido a la impresora"""
        try:
            # Obtener todo el texto del widget
            text_widget.config(state=tk.NORMAL)
            content = text_widget.get("1.0", tk.END)
            text_widget.config(state=tk.DISABLED)
            
            # Crear archivo temporal
            filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w") as f:
                f.write(content)
            
            # Imprimir usando la impresora predeterminada del sistema (Windows)
            if os.name == 'nt':
                os.startfile(filename, "print")
                messagebox.showinfo("Print", "Document sent to printer")
            else:
                messagebox.showinfo("Print", f"Content saved to {filename}\nPrint from your system")
        except Exception as e:
            messagebox.showerror("Print Error", f"Could not print: {str(e)}")
    
    def refresh_data(self):
        """Refrescar todos los datos sin cambiar la fecha"""
        self.load_data()
        self.load_daily_data()
        self.show_employee_data()
        messagebox.showinfo("Refresh", "Data has been refreshed")
    
    def update_employees_list(self):
        self.employees_listbox.delete(0, tk.END)
        for employee in sorted(self.employees):
            self.employees_listbox.insert(tk.END, employee)
    
    def add_employee(self):
        name = simpledialog.askstring("Add Employee", "Employee name:")
        if name and name not in self.employees:
            self.employees.append(name)
            self.update_employees_list()
            self.save_data()
    
    def remove_employee(self):
        selection = self.employees_listbox.curselection()
        if selection:
            employee = self.employees_listbox.get(selection)
            confirm = messagebox.askyesno("Confirm", f"Remove {employee} from system?")
            if confirm:
                self.employees.remove(employee)
                if employee in self.attendance:
                    del self.attendance[employee]
                if employee in self.counters:
                    del self.counters[employee]
                if employee in self.employee_comments:
                    del self.employee_comments[employee]
                self.update_employees_list()
                self.save_data()
    
    def calculate_present_today(self):
        date_str = self.current_date.strftime("%Y-%m-%d")
        present = 0
        
        for employee in self.employees:
            if employee in self.attendance and date_str in self.attendance[employee]:
                if self.attendance[employee][date_str]["status"] == "present":
                    present += 1
        
        return present
    
    def update_total_hours(self):
        present = self.calculate_present_today()
        total_hours = present * 8
        self.total_hours_label.config(text=str(total_hours))
    
    def record_attendance(self):
        selection = self.employees_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select an employee first")
            return
            
        employee = self.employees_listbox.get(selection)
        date_str = self.current_date.strftime("%Y-%m-%d")
        status = self.attendance_status.get()
        point_type = self.point_type.get()
        
        # Asignar puntos disciplinarios (0-6) independientemente del estado
        points = point_type
        
        if employee not in self.counters:
            self.counters[employee] = {"vacation": 0, "personal": 0, "late": 0}
        
        if status == "vacation":
            self.counters[employee]["vacation"] += 1
        elif status == "personal":
            self.counters[employee]["personal"] += 1
        elif status == "late":
            self.counters[employee]["late"] += 1
        
        if employee not in self.attendance:
            self.attendance[employee] = {}
        
        # Determinar el tipo de acción disciplinaria basado en los puntos
        disciplinary_action = ""
        if points > 0:
            if points == 4:
                disciplinary_action = "verbal"
            elif points == 5:
                disciplinary_action = "written"
            elif points == 6:
                disciplinary_action = "final"
            else:
                disciplinary_action = f"action {points}"
        else:
            disciplinary_action = "no action"
        
        # Guardar el registro con puntos, incluso para "absent" y "late"
        self.attendance[employee][date_str] = {
            "status": status,
            "points": points,
            "type": disciplinary_action
        }
        
        self.save_data()
        self.show_employee_data()
        self.update_total_hours()
        messagebox.showinfo("Success", f"Attendance recorded for {employee}")
    
    def save_production(self):
        date_str = self.current_date.strftime("%Y-%m-%d")
        
        self.daily_data[date_str] = {
            "total_hours": self.total_hours_label.cget("text"),
            "ppm_yellow": self.ppm_yellow.get(),
            "ppm_clear": self.ppm_clear.get(),
            "inedible_weight": self.inedible_weight.get(),
            "rte_start": self.rte_start.get(),
            "rte_end": self.rte_end.get(),
            "qa_raw_start": self.qa_raw_start.get(),
            "qa_raw_end": self.qa_raw_end.get(),
            "cook_room_time": self.cook_room_time.get(),
            "notes": self.notes_text.get("1.0", tk.END).strip()
        }
        
        with open("casa_meats_production.json", "w") as f:
            json.dump(self.daily_data, f)
        
        messagebox.showinfo("Success", "Production data saved successfully")
    
    def load_daily_data(self):
        date_str = self.current_date.strftime("%Y-%m-%d")
        
        if date_str in self.daily_data:
            data = self.daily_data[date_str]
            self.total_hours_label.config(text=data["total_hours"])
            self.ppm_yellow.set(data.get("ppm_yellow", ""))
            self.ppm_clear.set(data.get("ppm_clear", ""))
            self.inedible_weight.set(data.get("inedible_weight", ""))
            self.rte_start.set(data.get("rte_start", ""))
            self.rte_end.set(data.get("rte_end", ""))
            self.qa_raw_start.set(data.get("qa_raw_start", ""))
            self.qa_raw_end.set(data.get("qa_raw_end", ""))
            self.cook_room_time.set(data.get("cook_room_time", ""))
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", data.get("notes", ""))
        
        self.update_total_hours()
    
    def configure_email(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("Email Configuration")
        config_window.geometry("400x300")
        
        tk.Label(config_window, text="SMTP Server:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        smtp_server_entry = tk.Entry(config_window)
        smtp_server_entry.grid(row=0, column=1, padx=5, pady=5)
        smtp_server_entry.insert(0, self.email_config["smtp_server"])
        
        tk.Label(config_window, text="SMTP Port:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        smtp_port_entry = tk.Entry(config_window)
        smtp_port_entry.grid(row=1, column=1, padx=5, pady=5)
        smtp_port_entry.insert(0, str(self.email_config["smtp_port"]))
        
        tk.Label(config_window, text="Sender Email:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        sender_email_entry = tk.Entry(config_window)
        sender_email_entry.grid(row=2, column=1, padx=5, pady=5)
        sender_email_entry.insert(0, self.email_config["sender_email"])
        
        tk.Label(config_window, text="Password:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        sender_password_entry = tk.Entry(config_window, show="*")
        sender_password_entry.grid(row=3, column=1, padx=5, pady=5)
        sender_password_entry.insert(0, self.email_config["sender_password"])
        
        tk.Label(config_window, text="Recipient Email:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        receiver_email_entry = tk.Entry(config_window)
        receiver_email_entry.grid(row=4, column=1, padx=5, pady=5)
        receiver_email_entry.insert(0, self.email_config["receiver_email"])
        
        def save_config():
            self.email_config = {
                "smtp_server": smtp_server_entry.get(),
                "smtp_port": int(smtp_port_entry.get()),
                "sender_email": sender_email_entry.get(),
                "sender_password": sender_password_entry.get(),
                "receiver_email": receiver_email_entry.get()
            }
            
            # Guardar configuración
            try:
                with open("email_config.json", "r") as f:
                    config_data = json.load(f)
            except:
                config_data = {}
            
            config_data[self.username] = {
                "password": self.user_manager.users[self.username]["password"],
                "email": self.user_manager.users[self.username]["email"],
                "email_config": self.email_config
            }
            
            with open("email_config.json", "w") as f:
                json.dump(config_data, f)
            
            messagebox.showinfo("Success", "Email configuration saved")
            config_window.destroy()
        
        tk.Button(config_window, text="Save", command=save_config).grid(row=5, column=1, pady=10)
    
    def load_data(self):
        try:
            if os.path.exists("casa_meats_employees.json"):
                with open("casa_meats_employees.json", "r") as f:
                    data = json.load(f)
                    self.employees = data.get("employees", self.employees)
            
            if os.path.exists("casa_meats_attendance.json"):
                with open("casa_meats_attendance.json", "r") as f:
                    self.attendance = json.load(f)
            
            if os.path.exists("casa_meats_counters.json"):
                with open("casa_meats_counters.json", "r") as f:
                    self.counters = json.load(f)
                    
            if os.path.exists("casa_meats_production.json"):
                with open("casa_meats_production.json", "r") as f:
                    self.daily_data = json.load(f)
            
            if os.path.exists("employee_comments.json"):
                with open("employee_comments.json", "r") as f:
                    self.employee_comments = json.load(f)
            
            if os.path.exists("email_config.json"):
                with open("email_config.json", "r") as f:
                    user_creds = json.load(f)
                    if self.username in user_creds:
                        self.email_config = user_creds[self.username]["email_config"]
        except Exception as e:
            messagebox.showerror("Error", f"Could not load data: {str(e)}")
    
    def save_data(self):
        try:
            with open("casa_meats_employees.json", "w") as f:
                json.dump({"employees": self.employees}, f)
            
            with open("casa_meats_attendance.json", "w") as f:
                json.dump(self.attendance, f)
                
            with open("casa_meats_counters.json", "w") as f:
                json.dump(self.counters, f)
                
            with open("casa_meats_production.json", "w") as f:
                json.dump(self.daily_data, f)
                
            with open("employee_comments.json", "w") as f:
                json.dump(self.employee_comments, f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save data: {str(e)}")

    def send_email_report(self):
        date_str = self.current_date.strftime("%Y-%m-%d")
        formatted_date = self.current_date.strftime("%m/%d/%Y")
        
        if not self.email_config["sender_email"] or not self.email_config["receiver_email"]:
            messagebox.showerror("Error", "Please configure email first")
            self.configure_email()
            return
        
        if date_str in self.daily_data:
            data = self.daily_data[date_str]
        else:
            data = {
                "total_hours": self.total_hours_label.cget("text"),
                "ppm_yellow": self.ppm_yellow.get(),
                "ppm_clear": self.ppm_clear.get(),
                "inedible_weight": self.inedible_weight.get(),
                "rte_start": self.rte_start.get(),
                "rte_end": self.rte_end.get(),
                "qa_raw_start": self.qa_raw_start.get(),
                "qa_raw_end": self.qa_raw_end.get(),
                "cook_room_time": self.cook_room_time.get(),
                "notes": self.notes_text.get("1.0", tk.END).strip()
            }
        
        present = []
        for employee in self.employees:
            if employee in self.attendance and date_str in self.attendance[employee]:
                if self.attendance[employee][date_str]["status"] == "present":
                    present.append(employee)
        
        subject = f"Sanitation Report - Casa Meats - {formatted_date} (Sent by {self.username})"
        
        html = f"""
        <html>
            <body>
                <h2>Sanitation Report - Casa Meats - {formatted_date}</h2>
                <h3>Third Shift Sanitation - Sent by {self.username}</h3>
                
                <h4>Production Data:</h4>
                <table border="1" cellpadding="5">
                    <tr>
                        <th>Total Hours</th>
                        <td>{data['total_hours']}</td>
                    </tr>
                    <tr>
                        <th>PPM Yellow LP</th>
                        <td>{data['ppm_yellow']}</td>
                    </tr>
                    <tr>
                        <th>PPM Clear V</th>
                        <td>{data['ppm_clear']}</td>
                    </tr>
                    <tr>
                        <th>Inedible Room Weight</th>
                        <td>{data.get('inedible_weight', 'N/A')}</td>
                    </tr>
                    <tr>
                        <th>Cook Room Time</th>
                        <td>{data.get('cook_room_time', 'N/A')}</td>
                    </tr>
                    <tr>
                        <th>RTE Inspection</th>
                        <td>{data.get('rte_start', 'N/A')} - {data.get('rte_end', 'N/A')}</td>
                    </tr>
                    <tr>
                        <th>QA RAW Inspection</th>
                        <td>{data.get('qa_raw_start', 'N/A')} - {data.get('qa_raw_end', 'N/A')}</td>
                    </tr>
                </table>
                
                <h4>Present Staff ({len(present)}):</h4>
                <ul>
                    {''.join(f'<li>{emp}</li>' for emp in sorted(present))}
                </ul>
                
                <h4>Notes:</h4>
                <p>{data['notes']}</p>
                
                <p>--</p>
                <p>This is an automated message from Casa Meats Attendance System</p>
                """
        
        # Custom footer based on sender
        if self.username == "eugenio":
            html += """
                <p>Eugenio Morales<br>
                Sanitation Team Leader<br>
                Phone: 856-592-2612<br>
                Email: eugenio.morales@casameats.com</p>
            """
        elif self.username == "christian":
            html += """
                <p>Christian Gonzalez Vega<br>
                Sanitation Group Leader<br>
                Phone: 856-238-4053</p>
            """
        
        html += """
            </body>
        </html>
        """
        
        msg = MIMEMultipart()
        msg['From'] = self.email_config["sender_email"]
        msg['To'] = self.email_config["receiver_email"]
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html, 'html'))
        
        try:
            server = smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"])
            server.starttls()
            server.login(self.email_config["sender_email"], self.email_config["sender_password"])
            
            server.sendmail(
                self.email_config["sender_email"], 
                self.email_config["receiver_email"].split(";"), 
                msg.as_string()
            )
            server.quit()
            
            messagebox.showinfo("Success", f"Report sent by {self.username} successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Could not send email: {str(e)}")

    def show_counters(self, employee):
        if employee in self.counters:
            counters = self.counters[employee]
            text = (f"Vacation: {counters['vacation']}\n"
                    f"Personal: {counters['personal']}\n"
                    f"Late: {counters['late']}")
        else:
            text = "Vacation: 0\nPersonal: 0\nLate: 0"
        
        self.counters_label.config(text=text)
    
    def show_history(self, event=None):
        selection = self.employees_listbox.curselection()
        if not selection:
            return
            
        employee = self.employees_listbox.get(selection)
        self.show_counters(employee)
        
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        one_year_ago = self.current_date - timedelta(days=365)
        
        if employee in self.attendance:
            dates = sorted(self.attendance[employee].keys(), reverse=True)
            
            for date_str in dates:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if date >= one_year_ago and date <= self.current_date:
                    record = self.attendance[employee][date_str]
                    self.history_tree.insert("", tk.END, values=(
                        date.strftime("%m/%d/%Y"),
                        record["status"].capitalize(),
                        record["points"],
                        record["type"].capitalize()
                    ))
    
    def go_to_today(self):
        self.current_date = datetime.now().date()
        self.update_date()
        self.load_daily_data()
    
    def previous_day(self):
        self.save_production()
        self.current_date -= timedelta(days=1)
        self.update_date()
        self.load_daily_data()
    
    def next_day(self):
        self.save_production()
        self.current_date += timedelta(days=1)
        self.update_date()
        self.load_daily_data()
    
    def update_date(self):
        self.date_label.config(text=self.current_date.strftime("%m/%d/%Y"))
        self.month_var.set(self.current_date.strftime("%m"))
        self.year_var.set(self.current_date.strftime("%Y"))
        self.day_var.set(self.current_date.strftime("%d"))
        self.show_employee_data()

def main():
    root = tk.Tk()
    login = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()