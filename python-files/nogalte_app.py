import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import os
import tempfile
import io
import sqlite3
import random
import string
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode.code128 import Code128
from reportlab.lib.units import mm
from datetime import datetime
import math

T = {
    "title": "Fix & Send Nogalte",
    "logo": "🛠️ Fix & Send Nogalte",
    "id": "ID",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "phone": "Teléfono",
    "email": "Correo",
    "device": "Dispositivo",
    "imei": "IMEI",
    "issues": "Problemas y Costo",
    "cost": "Costo",
    "add_issue": "➕ Agregar Problema",
    "remove_selected": "❌ Eliminar Seleccionado",
    "total": "Total:",
    "discount": "Descuento:",
    "paid": "Pagado:",
    "rest": "Restante:",
    "update_total": "🔄 ACTUALIZAR TOTAL",
    "previous": "⬅ Anterior",
    "next": "Siguiente ➡",
    "last": "Último ⏭",
    "save": "💾 Guardar",
    "delete": "🗑 Eliminar",
    "new": "✨ Nuevo",
    "save_invoice": "📄 Guardar Factura (A4)",
    "print_thermal": "🖨 Imprimir Térmica",
    "search": "🔍 Buscar",
    "open_webcam": "📷 Abrir Cámara",
    "take_picture": "📸 Tomar Foto",
    "delete_photos": "🗑 Borrar Fotos",
    "view_photos": "👁 Ver Fotos",
    "photo": "📸 FOTO",
    "input_needed": "Se requieren problema y costo.",
    "cost_number": "El costo debe ser un número.",
    "id_required": "Se requiere ID.",
    "saved": "Registro guardado.",
    "deleted": "Registro eliminado exitosamente.",
    "no_record_selected": "Ningún registro seleccionado para eliminar.",
    "photo_taken": "Foto {n} tomada.",
    "failed_capture": "No se pudo capturar la foto.",
    "webcam_open": "Por favor, abre la cámara y verifica los espacios de fotos (máx 4).",
    "webcam_error": "No se pudo abrir la cámara.",
    "no_record_selected_print": "Ningún registro seleccionado.",
    "failed_print": "No se pudo imprimir: {err}",
    "printed": "Registro enviado a impresora térmica.",
    "save_invoice_error": "No se pudo guardar la factura: {err}",
    "invoice_saved": "Factura guardada como {path}",
    "error": "Error",
    "saved_": "Guardado",
    "deleted_": "Eliminado",
    "printed_": "Impreso",
    "clear_db": "🧹 Limpiar Base de Datos",
    "db_cleared": "Base de datos limpiada exitosamente.",
    "db_clear_error": "Error al limpiar la base de datos: {err}",
    "invoice_title": "FIX & SEND",
    "invoice_subtitle": "NOGALTE",
    "date": "Fecha",
    "customer_info": "Información del cliente",
    "name": "Nombre",
    "invoice_issues": "Problemas y Costos",
    "payment_summary": "Resumen de pago",
    "barcode_failed": "Código de barras: Error al mostrar"
}

DB_PATH = "nogalte_records.db"

def image_to_bytes(img):
    if img is None:
        return None
    with io.BytesIO() as output:
        img.save(output, format="PNG")
        return output.getvalue()

def bytes_to_image(data):
    if data is None:
        return None
    return Image.open(io.BytesIO(data))

def ensure_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records (
        id TEXT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        email TEXT,
        device TEXT,
        imei TEXT,
        total TEXT,
        discount TEXT,
        paid TEXT,
        rest TEXT,
        issues TEXT,
        photo1 BLOB,
        photo2 BLOB,
        photo3 BLOB,
        photo4 BLOB
    )''')
    conn.commit()
    conn.close()

class FixSendApp:
    def __init__(self, root):
        self.root = root
        self.t = T
        self.root.title(self.t["title"])
        self.root.configure(bg="#ECF0F1")
        ensure_table()
        self.records = self.load_all_records()
        self.photos = [None, None, None, None]
        self.current_index = None

        # Color scheme
        self.primary_color = "#2C3E50"
        self.accent_color = "#E74C3C"
        self.bg_color = "#ECF0F1"
        self.text_color = "#34495E"
        self.button_bg = "#3498DB"
        self.button_fg = "#FFFFFF"
        self.button_hover_bg = "#2980B9"

        # Izquierda: logo y formulario
        left = tk.Frame(root, bg=self.bg_color)
        left.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        self.logo = tk.Label(left, text=self.t["logo"], font=("Arial", 18, "bold"), fg=self.primary_color, bg=self.bg_color, justify="left")
        self.logo.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        fields = [
            (self.t["id"], "id"),
            (self.t["first_name"], "first_name"),
            (self.t["last_name"], "last_name"),
            (self.t["phone"], "phone"),
            (self.t["email"], "email"),
            (self.t["device"], "device"),
            (self.t["imei"], "imei"),
        ]
        self.entries = {}
        self.field_labels = []
        for i, (label, key) in enumerate(fields):
            l = tk.Label(left, text=label, fg=self.text_color, bg=self.bg_color)
            l.grid(row=i+1, column=0, sticky='e')
            self.field_labels.append(l)
            entry = tk.Entry(left, width=25, fg=self.text_color, bg="#FFFFFF", relief=tk.FLAT, bd=1)
            entry.grid(row=i+1, column=1, pady=2, sticky='w')
            self.entries[key] = entry

        # Problemas
        self.issues_label = tk.Label(left, text=self.t["issues"], fg=self.text_color, bg=self.bg_color)
        self.issues_label.grid(row=len(fields)+1, column=0, sticky='ne', pady=(10,0))
        issues_frame = tk.Frame(left, bg=self.bg_color)
        issues_frame.grid(row=len(fields)+1, column=1, sticky='w', pady=(10,0))

        self.issues_listbox = tk.Listbox(issues_frame, selectmode=tk.SINGLE, width=30, height=4, fg=self.text_color, bg="#FFFFFF", relief=tk.FLAT, bd=1)
        self.issues_listbox.grid(row=0, column=0, columnspan=3, sticky='w')
        self.issues_entry = tk.Entry(issues_frame, width=14, fg=self.text_color, bg="#FFFFFF", relief=tk.FLAT, bd=1)
        self.issues_entry.grid(row=1, column=0, sticky='w', pady=2)
        self.cost_entry = tk.Entry(issues_frame, width=8, fg=self.text_color, bg="#FFFFFF", relief=tk.FLAT, bd=1)
        self.cost_entry.grid(row=1, column=1, sticky='w', padx=2, pady=2)
        self.cost_label = tk.Label(issues_frame, text=self.t["cost"], fg=self.text_color, bg=self.bg_color)
        self.cost_label.grid(row=1, column=2, sticky='w')
        
        def on_button_enter(e, btn, hover_color):
            btn.config(bg=hover_color)
        
        def on_button_leave(e, btn, default_color):
            btn.config(bg=default_color)

        self.add_issue_btn = tk.Button(issues_frame, text=self.t["add_issue"], command=self.add_issue, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.add_issue_btn.grid(row=2, column=0, sticky='w', padx=2)
        self.add_issue_btn.bind("<Enter>", lambda e: on_button_enter(e, self.add_issue_btn, self.button_hover_bg))
        self.add_issue_btn.bind("<Leave>", lambda e: on_button_leave(e, self.add_issue_btn, self.button_bg))
        
        self.remove_issue_btn = tk.Button(issues_frame, text=self.t["remove_selected"], command=self.remove_issue, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.remove_issue_btn.grid(row=2, column=1, columnspan=2, pady=2, sticky='w')
        self.remove_issue_btn.bind("<Enter>", lambda e: on_button_enter(e, self.remove_issue_btn, self.button_hover_bg))
        self.remove_issue_btn.bind("<Leave>", lambda e: on_button_leave(e, self.remove_issue_btn, self.button_bg))

        # Pagos/descuento
        pay_frame = tk.Frame(left, bg=self.bg_color)
        pay_frame.grid(row=len(fields)+2, column=0, columnspan=2, sticky='w', pady=(10,0))
        self.total_label = tk.Label(pay_frame, text=self.t["total"], fg=self.text_color, bg=self.bg_color)
        self.total_label.grid(row=0, column=0, sticky="e")
        self.total_var = tk.StringVar(value="0.00")
        self.total_show = tk.Label(pay_frame, textvariable=self.total_var, width=10, relief=tk.SUNKEN, font=("Arial", 18, "bold"), fg="#2ECC71", bg="#FFFFFF")
        self.total_show.grid(row=0, column=1, sticky="w", padx=(0,10))

        self.discount_label = tk.Label(pay_frame, text=self.t["discount"], fg=self.text_color, bg=self.bg_color)
        self.discount_label.grid(row=1, column=0, sticky="e")
        self.discount_entry = tk.Entry(pay_frame, width=10, font=("Arial", 16), fg=self.text_color, bg="#FFFFFF", relief=tk.FLAT, bd=1)
        self.discount_entry.grid(row=1, column=1, sticky="w", pady=1)
        self.paid_label = tk.Label(pay_frame, text=self.t["paid"], fg=self.text_color, bg=self.bg_color)
        self.paid_label.grid(row=2, column=0, sticky="e")
        self.paid_entry = tk.Entry(pay_frame, width=10, font=("Arial", 16), fg=self.text_color, bg="#FFFFFF", relief=tk.FLAT, bd=1)
        self.paid_entry.grid(row=2, column=1, sticky="w", pady=1)
        self.rest_label = tk.Label(pay_frame, text=self.t["rest"], fg=self.text_color, bg=self.bg_color)
        self.rest_label.grid(row=3, column=0, sticky="e")
        self.rest_var = tk.StringVar(value="0.00")
        self.rest_show = tk.Label(pay_frame, textvariable=self.rest_var, width=10, relief=tk.SUNKEN, font=("Arial", 18, "bold"), fg=self.accent_color, bg="#FFFFFF")
        self.rest_show.grid(row=3, column=1, sticky="w", padx=(0,10))

        self.update_total_btn = tk.Button(pay_frame, text=self.t["update_total"], command=self.update_total_and_rest, font=("Arial", 18, "bold"), bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT)
        self.update_total_btn.grid(row=4, column=0, columnspan=2, pady=(10,0), sticky="we")
        self.update_total_btn.bind("<Enter>", lambda e: on_button_enter(e, self.update_total_btn, self.button_hover_bg))
        self.update_total_btn.bind("<Leave>", lambda e: on_button_leave(e, self.update_total_btn, self.button_bg))

        # Centro: navegación y botones
        center = tk.Frame(root, bg=self.bg_color)
        center.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(center, bg=self.bg_color)
        btn_frame.pack(pady=2)
        self.prev_btn = tk.Button(btn_frame, text=self.t["previous"], width=8, command=self.prev_record, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.prev_btn.pack(side=tk.LEFT, padx=2)
        self.prev_btn.bind("<Enter>", lambda e: on_button_enter(e, self.prev_btn, self.button_hover_bg))
        self.prev_btn.bind("<Leave>", lambda e: on_button_leave(e, self.prev_btn, self.button_bg))

        self.next_btn = tk.Button(btn_frame, text=self.t["next"], width=8, command=self.next_record, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.next_btn.pack(side=tk.LEFT, padx=2)
        self.next_btn.bind("<Enter>", lambda e: on_button_enter(e, self.next_btn, self.button_hover_bg))
        self.next_btn.bind("<Leave>", lambda e: on_button_leave(e, self.next_btn, self.button_bg))

        self.last_btn = tk.Button(btn_frame, text=self.t["last"], width=8, command=self.last_record, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.last_btn.pack(side=tk.LEFT, padx=2)
        self.last_btn.bind("<Enter>", lambda e: on_button_enter(e, self.last_btn, self.button_hover_bg))
        self.last_btn.bind("<Leave>", lambda e: on_button_leave(e, self.last_btn, self.button_bg))

        self.save_btn = tk.Button(btn_frame, text=self.t["save"], width=8, command=self.save_record, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.save_btn.pack(side=tk.LEFT, padx=2)
        self.save_btn.bind("<Enter>", lambda e: on_button_enter(e, self.save_btn, self.button_hover_bg))
        self.save_btn.bind("<Leave>", lambda e: on_button_leave(e, self.save_btn, self.button_bg))

        self.delete_btn = tk.Button(btn_frame, text=self.t["delete"], width=8, command=self.delete_record, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.delete_btn.pack(side=tk.LEFT, padx=2)
        self.delete_btn.bind("<Enter>", lambda e: on_button_enter(e, self.delete_btn, self.button_hover_bg))
        self.delete_btn.bind("<Leave>", lambda e: on_button_leave(e, self.delete_btn, self.button_bg))

        self.new_btn = tk.Button(btn_frame, text=self.t["new"], width=8, command=self.new_record, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.new_btn.pack(side=tk.LEFT, padx=2)
        self.new_btn.bind("<Enter>", lambda e: on_button_enter(e, self.new_btn, self.button_hover_bg))
        self.new_btn.bind("<Leave>", lambda e: on_button_leave(e, self.new_btn, self.button_bg))

        self.save_invoice_btn = tk.Button(btn_frame, text=self.t["save_invoice"], width=15, command=self.save_record_a4, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.save_invoice_btn.pack(side=tk.LEFT, padx=2)
        self.save_invoice_btn.bind("<Enter>", lambda e: on_button_enter(e, self.save_invoice_btn, self.button_hover_bg))
        self.save_invoice_btn.bind("<Leave>", lambda e: on_button_leave(e, self.save_invoice_btn, self.button_bg))

        self.print_thermal_btn = tk.Button(btn_frame, text=self.t["print_thermal"], width=12, command=self.print_record_thermal, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.print_thermal_btn.pack(side=tk.LEFT, padx=2)
        self.print_thermal_btn.bind("<Enter>", lambda e: on_button_enter(e, self.print_thermal_btn, self.button_hover_bg))
        self.print_thermal_btn.bind("<Leave>", lambda e: on_button_leave(e, self.print_thermal_btn, self.button_bg))

        self.clear_db_btn = tk.Button(btn_frame, text=self.t["clear_db"], width=15, command=self.clear_database, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.clear_db_btn.pack(side=tk.LEFT, padx=2)
        self.clear_db_btn.bind("<Enter>", lambda e: on_button_enter(e, self.clear_db_btn, self.button_hover_bg))
        self.clear_db_btn.bind("<Leave>", lambda e: on_button_leave(e, self.clear_db_btn, self.button_bg))

        self.search_label = tk.Label(center, text=self.t["search"], fg=self.text_color, bg=self.bg_color)
        self.search_label.pack(anchor='w', pady=(8, 0))
        self.search_entry = tk.Entry(center, width=40, fg=self.text_color, bg="#FFFFFF", relief=tk.FLAT, bd=1)
        self.search_entry.pack(anchor='w')
        self.search_btn = tk.Button(center, text=self.t["search"], command=self.search_record, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.search_btn.pack(anchor='w', pady=4)
        self.search_btn.bind("<Enter>", lambda e: on_button_enter(e, self.search_btn, self.button_hover_bg))
        self.search_btn.bind("<Leave>", lambda e: on_button_leave(e, self.search_btn, self.button_bg))

        # Tabla de registros
        table_frame = tk.Frame(center, bg=self.bg_color)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        columns = ("ID", self.t["first_name"], self.t["last_name"], self.t["phone"], self.t["device"], self.t["issues"], self.t["total"], self.t["discount"], self.t["paid"], self.t["rest"])
        style = ttk.Style()
        style.configure("Treeview", background="#FFFFFF", foreground=self.text_color, fieldbackground="#FFFFFF")
        style.configure("Treeview.Heading", background=self.primary_color, foreground="#FFFFFF", font=("Arial", 10, "bold"))
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90 if col not in (self.t["issues"],) else 170)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_table_select)

        # Derecha: fotos y cámara
        right = tk.Frame(root, bg=self.bg_color)
        right.pack(side=tk.RIGHT, padx=10, pady=10)

        self.photo_labels = []
        for i in range(2):
            for j in range(2):
                lbl = tk.Label(right, text=f"{self.t['photo']} {i*2+j+1}", relief=tk.RIDGE, width=20, height=8, bd=2, bg="#FFFFFF", fg=self.text_color, highlightbackground=self.primary_color, highlightthickness=1)
                lbl.grid(row=i, column=j, padx=6, pady=6)
                self.photo_labels.append(lbl)

        cam_btns = tk.Frame(right, bg=self.bg_color)
        cam_btns.grid(row=2, column=0, columnspan=2, pady=(6, 0))
        self.open_webcam_btn = tk.Button(cam_btns, text=self.t["open_webcam"], command=self.open_webcam, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.open_webcam_btn.pack(side=tk.LEFT, padx=3)
        self.open_webcam_btn.bind("<Enter>", lambda e: on_button_enter(e, self.open_webcam_btn, self.button_hover_bg))
        self.open_webcam_btn.bind("<Leave>", lambda e: on_button_leave(e, self.open_webcam_btn, self.button_bg))

        self.take_picture_btn = tk.Button(cam_btns, text=self.t["take_picture"], command=self.take_picture, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.take_picture_btn.pack(side=tk.LEFT, padx=3)
        self.take_picture_btn.bind("<Enter>", lambda e: on_button_enter(e, self.take_picture_btn, self.button_hover_bg))
        self.take_picture_btn.bind("<Leave>", lambda e: on_button_leave(e, self.take_picture_btn, self.button_bg))

        self.delete_photos_btn = tk.Button(cam_btns, text=self.t["delete_photos"], command=self.delete_photos, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.delete_photos_btn.pack(side=tk.LEFT, padx=3)
        self.delete_photos_btn.bind("<Enter>", lambda e: on_button_enter(e, self.delete_photos_btn, self.button_hover_bg))
        self.delete_photos_btn.bind("<Leave>", lambda e: on_button_leave(e, self.delete_photos_btn, self.button_bg))

        self.view_photos_btn = tk.Button(cam_btns, text=self.t["view_photos"], command=self.view_photos, bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, font=("Arial", 10))
        self.view_photos_btn.pack(side=tk.LEFT, padx=3)
        self.view_photos_btn.bind("<Enter>", lambda e: on_button_enter(e, self.view_photos_btn, self.button_hover_bg))
        self.view_photos_btn.bind("<Leave>", lambda e: on_button_leave(e, self.view_photos_btn, self.button_bg))

        self.cam_preview = tk.Label(right, bg=self.bg_color)
        self.cam_preview.grid(row=3, column=0, columnspan=2, pady=10)

        self.cap = None
        self.previewing = False
        self.current_photo_index = 0

        self.new_record()
        self.update_ui_language()

    def update_ui_language(self):
        self.root.title(self.t["title"])
        self.logo.config(text=self.t["logo"])
        fields = [
            self.t["id"], self.t["first_name"], self.t["last_name"], self.t["phone"], self.t["email"], self.t["device"], self.t["imei"]
        ]
        for i, l in enumerate(self.field_labels):
            l.config(text=fields[i])
        self.issues_label.config(text=self.t["issues"])
        self.cost_label.config(text=self.t["cost"])
        self.add_issue_btn.config(text=self.t["add_issue"])
        self.remove_issue_btn.config(text=self.t["remove_selected"])
        self.total_label.config(text=self.t["total"])
        self.discount_label.config(text=self.t["discount"])
        self.paid_label.config(text=self.t["paid"])
        self.rest_label.config(text=self.t["rest"])
        self.update_total_btn.config(text=self.t["update_total"])
        self.prev_btn.config(text=self.t["previous"])
        self.next_btn.config(text=self.t["next"])
        self.last_btn.config(text=self.t["last"])
        self.save_btn.config(text=self.t["save"])
        self.delete_btn.config(text=self.t["delete"])
        self.new_btn.config(text=self.t["new"])
        self.save_invoice_btn.config(text=self.t["save_invoice"])
        self.print_thermal_btn.config(text=self.t["print_thermal"])
        self.clear_db_btn.config(text=self.t["clear_db"])
        self.search_label.config(text=self.t["search"])
        self.search_btn.config(text=self.t["search"])
        self.open_webcam_btn.config(text=self.t["open_webcam"])
        self.take_picture_btn.config(text=self.t["take_picture"])
        self.delete_photos_btn.config(text=self.t["delete_photos"])
        self.view_photos_btn.config(text=self.t["view_photos"])
        for i, lbl in enumerate(self.photo_labels):
            lbl.config(text=f"{self.t['photo']} {i+1}")
        columns = ("ID", self.t["first_name"], self.t["last_name"], self.t["phone"], self.t["device"], self.t["issues"], self.t["total"], self.t["discount"], self.t["paid"], self.t["rest"])
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90 if col not in (self.t["issues"],) else 170)
        self.update_table()
        if self.previewing and self.cap is not None:
            self.show_webcam_frame()

    def __del__(self):
        if self.cap is not None:
            self.cap.release()

    def get_next_auto_id(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM records ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row and row[0].isdigit():
            return f"{int(row[0])+1:07d}"
        return "0000001"

    def clear_database(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("DELETE FROM records")
            conn.commit()
            conn.close()
            self.records = []
            self.current_index = None
            self.update_table()
            self.new_record()
            messagebox.showinfo(self.t["deleted_"], self.t["db_cleared"])
        except Exception as e:
            messagebox.showerror(self.t["error"], self.t["db_clear_error"].format(err=str(e)))

    def open_webcam(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror(self.t["error"], self.t["webcam_error"])
            self.cap = None
            return
        self.previewing = True
        self.show_webcam_frame()

    def show_webcam_frame(self):
        if self.cap is not None and self.previewing:
            ret, frame = self.cap.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                img = img.resize((260, 180))
                imgtk = ImageTk.PhotoImage(image=img)
                self.cam_preview.imgtk = imgtk
                self.cam_preview.configure(image=imgtk)
            self.root.after(20, self.show_webcam_frame)

    def take_picture(self):
        if self.cap is not None and self.previewing and self.current_photo_index < 4:
            ret, frame = self.cap.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
                img.thumbnail((150, 100))
                self.photos[self.current_photo_index] = img
                self.update_photo_labels()
                self.current_photo_index += 1
                messagebox.showinfo(self.t["saved_"], self.t["photo_taken"].format(n=self.current_photo_index))
            else:
                messagebox.showerror(self.t["error"], self.t["failed_capture"])
        else:
            messagebox.showinfo(self.t["error"], self.t["webcam_open"])

    def delete_photos(self):
        self.photos = [None, None, None, None]
        self.current_photo_index = 0
        self.update_photo_labels()

    def view_photos(self):
        view = tk.Toplevel(self.root)
        view.title(self.t["view_photos"])
        view.configure(bg=self.bg_color)
        for i, img in enumerate(self.photos):
            lbl = tk.Label(view, text=f"{self.t['photo']} {i+1}", relief=tk.RIDGE, fg=self.text_color, bg="#FFFFFF")
            lbl.grid(row=0, column=i, padx=6, pady=6)
            if img:
                img_resized = img.copy().resize((200, 130))
                tkimg = ImageTk.PhotoImage(img_resized)
                lbl2 = tk.Label(view, image=tkimg, bg=self.bg_color)
                lbl2.image = tkimg
                lbl2.grid(row=1, column=i, padx=6, pady=6)
            else:
                lbl2 = tk.Label(view, text="No Photo", width=25, height=8, relief=tk.RIDGE, fg=self.text_color, bg="#FFFFFF")
                lbl2.grid(row=1, column=i, padx=6, pady=6)

    def update_photo_labels(self):
        for i in range(4):
            img = self.photos[i]
            if img:
                tkimg = ImageTk.PhotoImage(img)
                self.photo_labels[i].configure(image=tkimg, text="")
                self.photo_labels[i].image = tkimg
            else:
                self.photo_labels[i].configure(image="", text=f"{self.t['photo']} {i+1}")

    def add_issue(self):
        issue = self.issues_entry.get().strip()
        cost = self.cost_entry.get().strip()
        if issue and cost:
            try:
                cost_val = float(cost)
                display = f"{issue} | {cost_val:.2f}"
                self.issues_listbox.insert(tk.END, display)
                self.issues_entry.delete(0, tk.END)
                self.cost_entry.delete(0, tk.END)
                self.update_total_and_rest()
            except ValueError:
                messagebox.showerror(self.t["error"], self.t["cost_number"])
        else:
            messagebox.showinfo(self.t["error"], self.t["input_needed"])

    def remove_issue(self):
        selected = list(self.issues_listbox.curselection())
        for idx in reversed(selected):
            self.issues_listbox.delete(idx)
        self.update_total_and_rest()

    def get_issues(self):
        issues = []
        for i in range(self.issues_listbox.size()):
            item = self.issues_listbox.get(i)
            if " | " in item:
                name, cost = item.rsplit(" | ", 1)
                try:
                    cost_val = float(cost)
                except ValueError:
                    cost_val = 0.0
                issues.append((name, cost_val))
        return issues

    def set_issues(self, issues):
        self.issues_listbox.delete(0, tk.END)
        for issue, cost in issues:
            self.issues_listbox.insert(tk.END, f"{issue} | {float(cost):.2f}")
        self.update_total_and_rest()

    def update_total_and_rest(self):
        issues = self.get_issues()
        total = sum(cost for _, cost in issues)
        try:
            discount_val = float(self.discount_entry.get().strip()) if self.discount_entry.get().strip() else 0.0
        except ValueError:
            discount_val = 0.0
        total_after_discount = max(total - discount_val, 0.0)
        self.total_var.set(f"{total_after_discount:.2f}")
        paid = self.paid_entry.get()
        try:
            paid_val = float(paid) if paid else 0.0
        except ValueError:
            paid_val = 0.0
        rest = total_after_discount - paid_val
        self.rest_var.set(f"{rest:.2f}")

    def save_record(self):
        data = {key: entry.get() for key, entry in self.entries.items()}
        if not data["id"]:
            messagebox.showerror(self.t["error"], self.t["id_required"])
            return
        data["issues"] = self.get_issues()
        data["photos"] = self.photos.copy()
        data["total"] = self.total_var.get()
        data["discount"] = self.discount_entry.get()
        data["paid"] = self.paid_entry.get()
        data["rest"] = self.rest_var.get()
        self.save_record_to_db(data)
        self.records = self.load_all_records()
        self.update_table()
        self.current_index = self.find_record_index(data["id"])
        messagebox.showinfo(self.t["saved_"], self.t["saved"])

    def save_record_to_db(self, data):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        issues_str = "|".join(f"{i[0]}~{i[1]}" for i in data["issues"])
        photo_blobs = [image_to_bytes(img) for img in data["photos"]]
        c.execute('''INSERT OR REPLACE INTO records
        (id, first_name, last_name, phone, email, device, imei, total, discount, paid, rest, issues, photo1, photo2, photo3, photo4)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (data["id"], data["first_name"], data["last_name"], data["phone"], data["email"], data["device"], data["imei"], data["total"], data["discount"], data["paid"], data["rest"], issues_str, *photo_blobs))
        conn.commit()
        conn.close()

    def load_all_records(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, first_name, last_name, phone, email, device, imei, total, discount, paid, rest, issues FROM records ORDER BY id")
        rows = c.fetchall()
        conn.close()
        records = []
        for row in rows:
            rec = {
                "id": row[0], "first_name": row[1], "last_name": row[2], "phone": row[3],
                "email": row[4], "device": row[5], "imei": row[6], "total": row[7],
                "discount": row[8], "paid": row[9], "rest": row[10], "issues": self.issues_str_to_list(row[11])
            }
            records.append(rec)
        return records

    def issues_str_to_list(self, s):
        if not s:
            return []
        return [tuple(i.split("~")) if "~" in i else (i, "0.00") for i in s.split("|")]

    def find_record_index(self, record_id):
        for idx, rec in enumerate(self.records):
            if rec["id"] == record_id:
                return idx
        return None

    def load_photos_for_id(self, record_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT photo1, photo2, photo3, photo4 FROM records WHERE id=?", (record_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            return [None, None, None, None]
        return [bytes_to_image(row[i]) if row[i] else None for i in range(4)]

    def delete_record(self):
        if self.current_index is not None and 0 <= self.current_index < len(self.records):
            rec_id = self.records[self.current_index]["id"]
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("DELETE FROM records WHERE id=?", (rec_id,))
            conn.commit()
            conn.close()
            self.records = self.load_all_records()
            self.update_table()
            if self.records:
                self.current_index = min(self.current_index, len(self.records) - 1)
                self.load_record(self.current_index)
            else:
                self.current_index = None
                self.new_record()
            messagebox.showinfo(self.t["deleted_"], self.t["deleted"])
        else:
            messagebox.showerror(self.t["error"], self.t["no_record_selected"])

    def prev_record(self):
        if self.current_index is not None and self.current_index > 0:
            self.current_index -= 1
            self.load_record(self.current_index)

    def next_record(self):
        if self.current_index is not None and self.current_index < len(self.records) - 1:
            self.current_index += 1
            self.load_record(self.current_index)

    def last_record(self):
        if self.records:
            self.current_index = len(self.records) - 1
            self.load_record(self.current_index)
        else:
            self.current_index = None
            self.new_record()

    def new_record(self):
        self.current_index = None
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
        self.entries["id"].insert(0, self.get_next_auto_id())
        self.issues_listbox.delete(0, tk.END)
        self.discount_entry.delete(0, tk.END)
        self.paid_entry.delete(0, tk.END)
        self.total_var.set("0.00")
        self.rest_var.set("0.00")
        self.delete_photos()

    def load_record(self, index):
        if 0 <= index < len(self.records):
            rec = self.records[index]
            for key, entry in self.entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, rec.get(key, ""))
            self.set_issues(rec["issues"])
            self.discount_entry.delete(0, tk.END)
            self.discount_entry.insert(0, rec.get("discount", ""))
            self.paid_entry.delete(0, tk.END)
            self.paid_entry.insert(0, rec.get("paid", ""))
            self.total_var.set(rec.get("total", "0.00"))
            self.rest_var.set(rec.get("rest", "0.00"))
            self.photos = self.load_photos_for_id(rec["id"])
            self.current_photo_index = sum(1 for p in self.photos if p is not None)
            self.update_photo_labels()

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        columns = ("ID", self.t["first_name"], self.t["last_name"], self.t["phone"], self.t["device"], self.t["issues"], self.t["total"], self.t["discount"], self.t["paid"], self.t["rest"])
        for rec in self.records:
            issues_str = ", ".join(f"{i[0]} ({float(i[1]):.2f})" for i in rec["issues"])
            self.tree.insert("", tk.END, values=(
                rec["id"], rec["first_name"], rec["last_name"], rec["phone"],
                rec["device"], issues_str, rec["total"], rec["discount"], rec["paid"], rec["rest"]
            ))

    def on_table_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            record_id = item["values"][0]
            self.current_index = self.find_record_index(record_id)
            self.load_record(self.current_index)

    def search_record(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.update_table()
            return
        filtered_records = [
            rec for rec in self.records
            if any(query in str(rec[field]).lower() for field in ["id", "first_name", "last_name", "phone", "device"])
        ]
        for item in self.tree.get_children():
            self.tree.delete(item)
        for rec in filtered_records:
            issues_str = ", ".join(f"{i[0]} ({float(i[1]):.2f})" for i in rec["issues"])
            self.tree.insert("", tk.END, values=(
                rec["id"], rec["first_name"], rec["last_name"], rec["phone"],
                rec["device"], issues_str, rec["total"], rec["discount"], rec["paid"], rec["rest"]
            ))

    def save_record_a4(self):
        if self.current_index is None:
            messagebox.showerror(self.t["error"], self.t["no_record_selected_print"])
            return
        rec = self.records[self.current_index]
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        default_name = f"factura_{rec['id']}_{random_part}.pdf"
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=default_name, filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        try:
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4

            c.setFillColorRGB(0.17, 0.24, 0.31)
            c.setFont("Helvetica-Bold", 36)
            c.drawCentredString(width / 2, height - 40 * mm, f"{self.t['invoice_title']} {self.t['invoice_subtitle']}")
            c.setStrokeColorRGB(0.17, 0.24, 0.31)
            c.line(30 * mm, height - 55 * mm, 180 * mm, height - 55 * mm)

            c.setFillColorRGB(0.20, 0.29, 0.37)
            c.setFont("Helvetica", 10)
            personal_info = [
                "Fix & Send Nogalte",
                "Teléfono: +34631856586",
                "Email: fixandsendnogalte@gmail.com",
                "Dirección: Calle Nogalte 18 Bajo, Lorca, Murcia 30800"
            ]
            y_personal = height - 70 * mm
            for line in personal_info:
                c.drawCentredString(width / 2, y_personal, line)
                y_personal -= 5 * mm
            c.line(30 * mm, height - 88 * mm, 180 * mm, height - 88 * mm)

            try:
                barcode = Code128(rec["id"], barWidth=0.5 * mm, barHeight=10 * mm)
                barcode.drawOn(c, 30 * mm, height - 100 * mm)
            except Exception as e:
                c.drawString(30 * mm, height - 100 * mm, self.t["barcode_failed"])

            c.setFillColorRGB(0.20, 0.29, 0.37)
            c.setFont("Helvetica", 12)
            c.drawString(30 * mm, height - 115 * mm, f"{self.t['id']}: {rec['id']}")
            c.drawString(30 * mm, height - 125 * mm, f"{self.t['date']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            c.setFont("Helvetica-Bold", 12)
            c.drawString(30 * mm, height - 145 * mm, self.t["customer_info"])
            c.setFont("Helvetica", 10)
            y = height - 155 * mm
            c.drawString(30 * mm, y, f"{self.t['name']}: {rec['first_name'] or 'N/A'} {rec['last_name'] or ''}")
            y -= 10 * mm
            c.drawString(30 * mm, y, f"{self.t['phone']}: {rec['phone'] or 'N/A'}")
            y -= 10 * mm
            email = rec['email'] if rec['email'] and isinstance(rec['email'], str) else "N/A"
            try:
                email = email.encode('ascii', 'ignore').decode('ascii')
                c.drawString(30 * mm, y, f"{self.t['email']}: {email[:100]}")
            except Exception as e:
                c.drawString(30 * mm, y, f"{self.t['email']}: Caracteres inválidos")
            y -= 10 * mm
            c.drawString(30 * mm, y, f"{self.t['device']}: {rec['device'] or 'N/A'}")
            y -= 10 * mm
            c.drawString(30 * mm, y, f"{self.t['imei']}: {rec['imei'] or 'N/A'}")
            y -= 15 * mm

            c.setFont("Helvetica-Bold", 12)
            c.drawString(30 * mm, y, self.t["invoice_issues"])
            y -= 10 * mm
            c.setFont("Helvetica", 10)
            for issue, cost in rec["issues"]:
                try:
                    c.drawString(30 * mm, y, f"{issue}: {float(cost):.2f}")
                except ValueError:
                    c.drawString(30 * mm, y, f"{issue}: Costo inválido")
                y -= 10 * mm
            y -= 10 * mm

            c.setFont("Helvetica-Bold", 12)
            c.drawString(30 * mm, y, self.t["payment_summary"])
            y -= 10 * mm
            c.setFont("Helvetica", 10)
            c.drawString(30 * mm, y, f"{self.t['total']} {rec['total'] or '0.00'}")
            y -= 10 * mm
            c.drawString(30 * mm, y, f"{self.t['discount']} {rec['discount'] or '0.00'}")
            y -= 10 * mm
            c.drawString(30 * mm, y, f"{self.t['paid']} {rec['paid'] or '0.00'}")
            y -= 10 * mm
            c.drawString(30 * mm, y, f"{self.t['rest']} {rec['rest'] or '0.00'}")
            y -= 20 * mm

            photos = self.load_photos_for_id(rec["id"])
            photo_size = 50 * mm
            x_start = 120 * mm
            y_start = height - 95 * mm
            temp_files = []
            for i, img in enumerate(photos):
                if img:
                    try:
                        temp_file = tempfile.mktemp(suffix=".png")
                        img.save(temp_file)
                        temp_files.append(temp_file)
                        x = x_start
                        y_img = y_start - i * (photo_size * 0.75 + 4 * mm)
                        c.drawImage(temp_file, x, y_img - photo_size * 0.75, width=photo_size, height=photo_size * 0.75)
                    except Exception as e:
                        print(f"Photo {i+1} rendering error: {str(e)}")
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except OSError:
                    pass

            c.setFillColorRGB(0.20, 0.29, 0.37)
            c.setFont("Helvetica-Bold", 13)
            info = u"+34631856586 · EMAIL: FIXANDSENDNOGALTE@GMAIL.COM · DIRECCIÓN: CALLE NOGALTE 18 BAJO LORCA MURCIA 30800"
            center_x = width / 2
            last_photo_y = y_start - (len([p for p in photos if p]) - 1) * (photo_size * 0.75 + 4 * mm) - photo_size * 0.75
            center_y = max(28 * mm, last_photo_y - 20 * mm)
            radius = 80 * mm
            start_angle = -120
            end_angle = -60
            angle_step = (end_angle - start_angle) / max(1, len(info)-1)
            for i, char in enumerate(info):
                angle_deg = start_angle + i * angle_step
                angle_rad = math.radians(angle_deg)
                char_x = center_x + radius * math.cos(angle_rad)
                char_y = center_y + radius * math.sin(angle_rad)
                c.saveState()
                c.translate(char_x, char_y)
                c.rotate(angle_deg + 90)
                c.drawString(0, 0, char)
                c.restoreState()

            c.showPage()
            c.save()
            messagebox.showinfo(self.t["saved_"], self.t["invoice_saved"].format(path=file_path))
        except Exception as e:
            messagebox.showerror(self.t["error"], self.t["save_invoice_error"].format(err=str(e)))

    def print_record_thermal(self):
        if self.current_index is None:
            messagebox.showerror(self.t["error"], self.t["no_record_selected_print"])
            return
        rec = self.records[self.current_index]
        try:
            from escpos.printer import Usb
            p = Usb(0x1234, 0x5678)
            p.text("Fix & Send Nogalte\n")
            p.text("--------------------\n")
            p.text(f"ID: {rec['id']}\n")
            p.text(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            p.text(f"Nombre: {rec['first_name']} {rec['last_name']}\n")
            p.text(f"Teléfono: {rec['phone'] or 'N/A'}\n")
            p.text(f"Dispositivo: {rec['device'] or 'N/A'}\n")
            p.text(f"IMEI: {rec['imei'] or 'N/A'}\n")
            p.text("Problemas:\n")
            for issue, cost in rec["issues"]:
                p.text(f"  {issue}: {float(cost):.2f}\n")
            p.text("--------------------\n")
            p.text(f"Total: {rec['total'] or '0.00'}\n")
            p.text(f"Descuento: {rec['discount'] or '0.00'}\n")
            p.text(f"Pagado: {rec['paid'] or '0.00'}\n")
            p.text(f"Restante: {rec['rest'] or '0.00'}\n")
            p.barcode(rec["id"], "CODE128", height=50, width=2)
            p.cut()
            p.close()
            messagebox.showinfo(self.t["printed_"], self.t["printed"])
        except Exception as e:
            messagebox.showerror(self.t["error"], self.t["failed_print"].format(err=str(e)))

if __name__ == "__main__":
    root = tk.Tk()
    app = FixSendApp(root)
    root.mainloop()