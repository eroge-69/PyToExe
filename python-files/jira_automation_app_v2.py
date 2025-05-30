import tkinter as tk
from tkinter import ttk, messagebox
import json
import datetime
import uuid
import os

class JiraAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatización de Incidencias Jira - Estellantis")
        self.root.geometry("800x600")
        self.root.configure(bg="#f5f5f5")
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('TLabel', background='#f5f5f5', font=('Segoe UI', 11))
        self.style.configure('TButton', font=('Segoe UI', 11, 'bold'))
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))
        self.style.configure('Subheader.TLabel', font=('Segoe UI', 12, 'bold'))
        
        # Variables
        self.issue_types = ["Error", "Mejora", "Tarea", "Incidencia", "Consulta"]
        self.priorities = ["Baja", "Media", "Alta", "Crítica"]
        self.systems = ["GP", "CIDE", "TRACON", "EKIP", "TICKET", "TELMA", "EQUIFAX"]
        
        # Crear widgets
        self.create_widgets()
        
        # Historial de tickets
        self.tickets_history = []
        self.load_tickets_history()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        header_label = ttk.Label(main_frame, text="Creación Automática de Incidencias en Jira", style='Header.TLabel')
        header_label.pack(pady=(0, 20))
        
        # Frame para formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Columna izquierda
        left_frame = ttk.Frame(form_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Tipo de incidencia
        ttk.Label(left_frame, text="Tipo de Incidencia:").pack(anchor=tk.W, pady=(0, 5))
        self.issue_type_var = tk.StringVar()
        issue_type_combo = ttk.Combobox(left_frame, textvariable=self.issue_type_var, values=self.issue_types, state="readonly")
        issue_type_combo.pack(fill=tk.X, pady=(0, 15))
        issue_type_combo.current(0)
        
        # Sistema afectado
        ttk.Label(left_frame, text="Sistema Afectado:").pack(anchor=tk.W, pady=(0, 5))
        self.system_var = tk.StringVar()
        system_combo = ttk.Combobox(left_frame, textvariable=self.system_var, values=self.systems, state="readonly")
        system_combo.pack(fill=tk.X, pady=(0, 15))
        system_combo.current(0)
        
        # Prioridad
        ttk.Label(left_frame, text="Prioridad:").pack(anchor=tk.W, pady=(0, 5))
        self.priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(left_frame, textvariable=self.priority_var, values=self.priorities, state="readonly")
        priority_combo.pack(fill=tk.X, pady=(0, 15))
        priority_combo.current(1)  # Media por defecto
        
        # Asignado a
        ttk.Label(left_frame, text="Asignado a (Email):").pack(anchor=tk.W, pady=(0, 5))
        self.assignee_var = tk.StringVar()
        assignee_entry = ttk.Entry(left_frame, textvariable=self.assignee_var)
        assignee_entry.pack(fill=tk.X, pady=(0, 15))
        self.assignee_var.set("soporte@estellantis.com")
        
        # Columna derecha
        right_frame = ttk.Frame(form_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Título de la incidencia
        ttk.Label(right_frame, text="Título de la Incidencia:").pack(anchor=tk.W, pady=(0, 5))
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(right_frame, textvariable=self.title_var)
        title_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Descripción
        ttk.Label(right_frame, text="Descripción:").pack(anchor=tk.W, pady=(0, 5))
        self.description_text = tk.Text(right_frame, height=10)
        self.description_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Notificar a
        ttk.Label(right_frame, text="Notificar a (Email):").pack(anchor=tk.W, pady=(0, 5))
        self.notify_var = tk.StringVar()
        notify_entry = ttk.Entry(right_frame, textvariable=self.notify_var)
        notify_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botón crear incidencia
        create_button = ttk.Button(button_frame, text="Crear Incidencia", command=self.create_issue)
        create_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Botón limpiar
        clear_button = ttk.Button(button_frame, text="Limpiar Formulario", command=self.clear_form)
        clear_button.pack(side=tk.RIGHT)
        
        # Frame para historial
        history_frame = ttk.Frame(main_frame)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Título historial
        history_label = ttk.Label(history_frame, text="Historial de Incidencias", style='Subheader.TLabel')
        history_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Tabla de historial
        columns = ("id", "tipo", "titulo", "sistema", "prioridad", "fecha")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=5)
        
        # Configurar columnas
        self.history_tree.heading("id", text="ID")
        self.history_tree.heading("tipo", text="Tipo")
        self.history_tree.heading("titulo", text="Título")
        self.history_tree.heading("sistema", text="Sistema")
        self.history_tree.heading("prioridad", text="Prioridad")
        self.history_tree.heading("fecha", text="Fecha")
        
        self.history_tree.column("id", width=80)
        self.history_tree.column("tipo", width=100)
        self.history_tree.column("titulo", width=200)
        self.history_tree.column("sistema", width=100)
        self.history_tree.column("prioridad", width=100)
        self.history_tree.column("fecha", width=150)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Evento de selección
        self.history_tree.bind("<Double-1>", self.on_ticket_select)
        
    def create_issue(self):
        # Validar campos
        if not self.title_var.get().strip():
            messagebox.showerror("Error", "El título de la incidencia es obligatorio")
            return
            
        if not self.description_text.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "La descripción de la incidencia es obligatoria")
            return
            
        # Generar ID de incidencia
        issue_id = f"EST-{uuid.uuid4().hex[:6].upper()}"
        
        # Obtener fecha actual
        current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Crear objeto de incidencia
        issue = {
            "id": issue_id,
            "type": self.issue_type_var.get(),
            "title": self.title_var.get(),
            "description": self.description_text.get("1.0", tk.END).strip(),
            "system": self.system_var.get(),
            "priority": self.priority_var.get(),
            "assignee": self.assignee_var.get(),
            "notify": self.notify_var.get(),
            "date": current_date
        }
        
        # Simular creación en Jira
        self.simulate_jira_creation(issue)
        
        # Enviar notificación por email
        if self.notify_var.get():
            self.send_notification_email(issue)
            
        # Añadir al historial
        self.tickets_history.append(issue)
        self.save_tickets_history()
        
        # Actualizar tabla de historial
        self.update_history_table()
        
        # Mostrar mensaje de éxito
        messagebox.showinfo("Éxito", f"Incidencia {issue_id} creada correctamente en Jira")
        
        # Limpiar formulario
        self.clear_form()
        
    def simulate_jira_creation(self, issue):
        # Simulación de creación en Jira
        # En una implementación real, aquí iría la integración con la API de Jira
        print(f"Simulando creación en Jira: {issue['id']}")
        
        # Crear un log de la operación
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "jira_operations.log")
        with open(log_file, "a") as f:
            f.write(f"{datetime.datetime.now()} - Creada incidencia {issue['id']}: {issue['title']}\n")
            
    def send_notification_email(self, issue):
        # Simulación de envío de email
        # En una implementación real, aquí iría la configuración SMTP
        print(f"Simulando envío de email a {issue['notify']}")
        
        # Crear un log de la operación
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "email_notifications.log")
        with open(log_file, "a") as f:
            f.write(f"{datetime.datetime.now()} - Enviada notificación para {issue['id']} a {issue['notify']}\n")
            
        # Mostrar la simulación del email
        email_preview = f"""
        Asunto: [Estellantis] Nueva incidencia creada: {issue['id']} - {issue['title']}
        
        Estimado usuario,
        
        Se ha creado una nueva incidencia en el sistema de Jira de Estellantis con los siguientes detalles:
        
        ID: {issue['id']}
        Tipo: {issue['type']}
        Título: {issue['title']}
        Sistema: {issue['system']}
        Prioridad: {issue['priority']}
        Fecha de creación: {issue['date']}
        Asignado a: {issue['assignee']}
        
        Descripción:
        {issue['description']}
        
        Puede acceder a la incidencia a través del siguiente enlace:
        https://jira.estellantis.com/browse/{issue['id']}
        
        Este es un mensaje automático, por favor no responda a este correo.
        
        Saludos,
        Equipo de Soporte de Estellantis
        """
        
        # Guardar preview del email
        email_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emails")
        os.makedirs(email_dir, exist_ok=True)
        
        email_file = os.path.join(email_dir, f"email_{issue['id']}.txt")
        with open(email_file, "w") as f:
            f.write(email_preview)
            
        # Mostrar preview en una ventana
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Vista previa del email - {issue['id']}")
        preview_window.geometry("700x500")
        
        email_text = tk.Text(preview_window, wrap=tk.WORD)
        email_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        email_text.insert(tk.END, email_preview)
        email_text.config(state=tk.DISABLED)
        
        close_button = ttk.Button(preview_window, text="Cerrar", command=preview_window.destroy)
        close_button.pack(pady=(0, 20))
        
    def clear_form(self):
        self.title_var.set("")
        self.description_text.delete("1.0", tk.END)
        self.issue_type_var.set(self.issue_types[0])
        self.system_var.set(self.systems[0])
        self.priority_var.set(self.priorities[1])
        self.notify_var.set("")
        
    def update_history_table(self):
        # Limpiar tabla
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Añadir tickets al historial
        for ticket in self.tickets_history:
            self.history_tree.insert("", tk.END, values=(
                ticket["id"],
                ticket["type"],
                ticket["title"],
                ticket["system"],
                ticket["priority"],
                ticket["date"]
            ))
            
    def on_ticket_select(self, event):
        # Obtener item seleccionado
        selected_item = self.history_tree.selection()[0]
        ticket_id = self.history_tree.item(selected_item, "values")[0]
        
        # Buscar ticket en el historial
        selected_ticket = None
        for ticket in self.tickets_history:
            if ticket["id"] == ticket_id:
                selected_ticket = ticket
                break
                
        if selected_ticket:
            # Mostrar detalles del ticket
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Detalles de la Incidencia {ticket_id}")
            details_window.geometry("600x500")
            
            # Frame principal
            main_frame = ttk.Frame(details_window, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            ttk.Label(main_frame, text=f"Incidencia: {ticket_id}", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 20))
            
            # Detalles
            details_frame = ttk.Frame(main_frame)
            details_frame.pack(fill=tk.BOTH, expand=True)
            
            # Columna izquierda
            left_frame = ttk.Frame(details_frame)
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            
            ttk.Label(left_frame, text="Tipo:").pack(anchor=tk.W, pady=(0, 5))
            ttk.Label(left_frame, text=selected_ticket["type"]).pack(anchor=tk.W, pady=(0, 15))
            
            ttk.Label(left_frame, text="Sistema:").pack(anchor=tk.W, pady=(0, 5))
            ttk.Label(left_frame, text=selected_ticket["system"]).pack(anchor=tk.W, pady=(0, 15))
            
            ttk.Label(left_frame, text="Prioridad:").pack(anchor=tk.W, pady=(0, 5))
            ttk.Label(left_frame, text=selected_ticket["priority"]).pack(anchor=tk.W, pady=(0, 15))
            
            ttk.Label(left_frame, text="Fecha:").pack(anchor=tk.W, pady=(0, 5))
            ttk.Label(left_frame, text=selected_ticket["date"]).pack(anchor=tk.W, pady=(0, 15))
            
            # Columna derecha
            right_frame = ttk.Frame(details_frame)
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
            
            ttk.Label(right_frame, text="Título:").pack(anchor=tk.W, pady=(0, 5))
            ttk.Label(right_frame, text=selected_ticket["title"]).pack(anchor=tk.W, pady=(0, 15))
            
            ttk.Label(right_frame, text="Asignado a:").pack(anchor=tk.W, pady=(0, 5))
            ttk.Label(right_frame, text=selected_ticket["assignee"]).pack(anchor=tk.W, pady=(0, 15))
            
            ttk.Label(right_frame, text="Notificado a:").pack(anchor=tk.W, pady=(0, 5))
            ttk.Label(right_frame, text=selected_ticket["notify"] if selected_ticket["notify"] else "N/A").pack(anchor=tk.W, pady=(0, 15))
            
            # Descripción
            ttk.Label(main_frame, text="Descripción:").pack(anchor=tk.W, pady=(20, 5))
            description_text = tk.Text(main_frame, height=10, wrap=tk.WORD)
            description_text.pack(fill=tk.BOTH, expand=True)
            description_text.insert(tk.END, selected_ticket["description"])
            description_text.config(state=tk.DISABLED)
            
            # Botón cerrar
            ttk.Button(main_frame, text="Cerrar", command=details_window.destroy).pack(pady=(20, 0))
            
    def save_tickets_history(self):
        # Guardar historial en archivo JSON
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        history_file = os.path.join(data_dir, "tickets_history.json")
        with open(history_file, "w") as f:
            json.dump(self.tickets_history, f)
            
    def load_tickets_history(self):
        # Cargar historial desde archivo JSON
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        history_file = os.path.join(data_dir, "tickets_history.json")
        try:
            with open(history_file, "r") as f:
                self.tickets_history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tickets_history = []
            
        # Actualizar tabla de historial
        self.update_history_table()

def main():
    root = tk.Tk()
    app = JiraAutomationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
