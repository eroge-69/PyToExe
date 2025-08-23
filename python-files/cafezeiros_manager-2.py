import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from dataclasses import dataclass
import json
import os
from typing import List

@dataclass
class Semanal:
    cliente: str = ''
    contato: str = ''
    kits: int = 0

class CafezeirosManager:
    def __init__(self):
        self.lista_clientes: List[Semanal] = []
        self.arquivo_dados = "cafezeiros.json"
        self.carregar_dados()
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario moderna para Windows"""
        self.root = tk.Tk()
        self.root.title("☕ Gestor de Clientes Cafezeiros - Tony Edition")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(True, True)
        
        # Configurar icono si existe
        try:
            self.root.iconbitmap('coffee.ico')  # Opcional
        except:
            pass
        
        # Configurar estilo moderno
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilos personalizados
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 20, 'bold'), 
                       background='#1a1a2e', 
                       foreground='#eee')
        
        # Frame principal con diseño elegante
        main_container = tk.Frame(self.root, bg='#1a1a2e')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título con gradiente visual
        title_frame = tk.Frame(main_container, bg='#16213e', height=80, relief='flat')
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)
        
        title = tk.Label(title_frame, 
                        text="☕ GESTOR DE CLIENTES CAFEZEIROS", 
                        font=('Segoe UI', 18, 'bold'),
                        bg='#16213e', 
                        fg='#00d4ff')
        title.pack(expand=True)
        
        subtitle = tk.Label(title_frame,
                           text="🚀 Tony Edition - Sistema Profesional",
                           font=('Segoe UI', 10),
                           bg='#16213e',
                           fg='#a0a0a0')
        subtitle.pack()
        
        # Container para botones y información
        content_frame = tk.Frame(main_container, bg='#1a1a2e')
        content_frame.pack(fill='both', expand=True)
        
        # Panel izquierdo - Botones
        left_panel = tk.Frame(content_frame, bg='#0f3460', width=350, relief='raised', bd=1)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Título del panel
        panel_title = tk.Label(left_panel,
                              text="🎯 PANEL DE CONTROL",
                              font=('Segoe UI', 12, 'bold'),
                              bg='#0f3460',
                              fg='#00d4ff')
        panel_title.pack(pady=20)
        
        # Botones con diseño profesional
        buttons_data = [
            ("📋 Registrar Cliente", "#27ae60", self.registrar_cliente),
            ("🔍 Consultar Cliente", "#3498db", self.consultar_cliente), 
            ("❌ Excluir Cliente", "#e74c3c", self.excluir_cliente),
            ("📋 Listar Todos", "#f39c12", self.listar_todos),
            ("📊 Estadísticas", "#9b59b6", self.mostrar_estadisticas),
            ("💾 Guardar Datos", "#1abc9c", self.salvar_dados),
            ("🔄 Recargar", "#34495e", self.recargar_datos),
            ("🚪 Salir", "#95a5a6", self.salir)
        ]
        
        self.buttons = {}
        for text, color, command in buttons_data:
            btn = tk.Button(left_panel,
                           text=text,
                           font=('Segoe UI', 11, 'bold'),
                           bg=color,
                           fg='white',
                           relief='flat',
                           padx=15,
                           pady=12,
                           command=command,
                           cursor='hand2',
                           activebackground=self.darken_color(color),
                           activeforeground='white',
                           borderwidth=0)
            btn.pack(pady=8, padx=20, fill='x')
            
            # Efectos hover mejorados
            btn.bind("<Enter>", lambda e, b=btn, c=color: self.on_hover(b, c))
            btn.bind("<Leave>", lambda e, b=btn, c=color: self.on_leave(b, c))
            
            self.buttons[text] = btn
        
        # Panel derecho - Información
        right_panel = tk.Frame(content_frame, bg='#16213e', relief='raised', bd=1)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Título del panel de información
        info_title_frame = tk.Frame(right_panel, bg='#0f3460', height=50)
        info_title_frame.pack(fill='x')
        info_title_frame.pack_propagate(False)
        
        info_title = tk.Label(info_title_frame,
                             text="📋 INFORMACIÓN Y RESULTADOS",
                             font=('Segoe UI', 12, 'bold'),
                             bg='#0f3460',
                             fg='#00d4ff')
        info_title.pack(expand=True)
        
        # Frame para información con scroll
        self.info_frame = tk.Frame(right_panel, bg='#16213e')
        self.info_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Texto de información con scroll mejorado
        text_frame = tk.Frame(self.info_frame, bg='#16213e')
        text_frame.pack(fill='both', expand=True)
        
        self.info_text = tk.Text(text_frame,
                                font=('Consolas', 10),
                                bg='#1e1e1e',
                                fg='#e0e0e0',
                                relief='flat',
                                wrap=tk.WORD,
                                padx=15,
                                pady=15,
                                selectbackground='#3498db',
                                selectforeground='white',
                                insertbackground='#00d4ff',
                                borderwidth=0)
        
        # Scrollbar personalizado
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.info_text.yview,
                                bg='#16213e', troughcolor='#16213e', 
                                activebackground='#3498db')
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Barra de estado
        status_frame = tk.Frame(self.root, bg='#0f3460', height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame,
                                    text=f"✅ Sistema listo - {len(self.lista_clientes)} clientes cargados",
                                    font=('Segoe UI', 9),
                                    bg='#0f3460',
                                    fg='#a0a0a0',
                                    anchor='w')
        self.status_label.pack(side='left', padx=10, expand=True, fill='x')
        
        # Contador de clientes
        self.contador_label = tk.Label(status_frame,
                                      text=f"👥 {len(self.lista_clientes)}",
                                      font=('Segoe UI', 9, 'bold'),
                                      bg='#0f3460',
                                      fg='#00d4ff')
        self.contador_label.pack(side='right', padx=10)
        
        # Mensaje de bienvenida
        self.mostrar_mensaje_bienvenida()
    
    def on_hover(self, button, color):
        """Efecto hover mejorado"""
        button.config(bg=self.darken_color(color), relief='raised', bd=2)
    
    def on_leave(self, button, color):
        """Salir del hover"""
        button.config(bg=color, relief='flat', bd=0)
    
    def darken_color(self, color):
        """Oscurecer color para efectos hover"""
        color_map = {
            "#27ae60": "#229954", "#3498db": "#2980b9", "#e74c3c": "#c0392b",
            "#f39c12": "#d68910", "#9b59b6": "#8e44ad", "#1abc9c": "#17a085",
            "#34495e": "#2c3e50", "#95a5a6": "#7f8c8d"
        }
        return color_map.get(color, color)
    
    def actualizar_contador(self):
        """Actualizar contador de clientes"""
        self.contador_label.config(text=f"👥 {len(self.lista_clientes)}")
        self.status_label.config(text=f"✅ Sistema actualizado - {len(self.lista_clientes)} clientes")
    
    def mostrar_mensaje_bienvenida(self):
        """Mostrar mensaje de bienvenida estilizado"""
        mensaje = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🎉 ¡BIENVENIDO TONY! 🎉                   ║
║                  Sistema Gestor de Cafezeiros               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📊 ESTADO ACTUAL:                                           ║
║  • Clientes registrados: {len(self.lista_clientes):>3} cafezeiros                     ║
║  • Archivo de datos: {'✅ Encontrado' if os.path.exists(self.arquivo_dados) else '❌ No existe':>12}                         ║
║  • Sistema: ✅ Operativo                                      ║
║                                                              ║
║  🎯 INSTRUCCIONES:                                           ║
║  1. Selecciona una opción del panel izquierdo               ║
║  2. Los resultados aparecerán en esta área                  ║
║  3. Los datos se guardan automáticamente                    ║
║                                                              ║
║  💡 CONSEJO: Usa "Guardar Datos" regularmente para          ║
║     asegurar que tu información esté respaldada             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 ¡Todo listo para gestionar tus clientes cafezeiros!
Selecciona una opción del menú para empezar...
"""
        self.mostrar_mensaje(mensaje)
    
    def mostrar_mensaje(self, mensaje):
        """Mostrar mensaje en el área de información"""
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, mensaje)
        self.info_text.see(tk.END)
    
    def registrar_cliente(self):
        """Registrar nuevo cliente con ventana mejorada"""
        dialog = ClienteDialog(self.root, "Registrar Nuevo Cliente")
        if dialog.resultado:
            try:
                # Verificar si el cliente ya existe
                nombre_nuevo = dialog.resultado['cliente'].lower().strip()
                for cliente_existente in self.lista_clientes:
                    if cliente_existente.cliente.lower() == nombre_nuevo:
                        messagebox.showwarning("⚠️ Cliente Existente", 
                                             f"El cliente '{nombre_nuevo.title()}' ya está registrado.\n"
                                             f"Contacto: {cliente_existente.contato}\n"
                                             f"Kits: {cliente_existente.kits}")
                        return
                
                cliente = Semanal(
                    cliente=nombre_nuevo,
                    contato=dialog.resultado['contato'].strip(),
                    kits=int(dialog.resultado['kits'])
                )
                self.lista_clientes.append(cliente)
                self.actualizar_contador()
                
                mensaje = f"""
✅ CLIENTE REGISTRADO EXITOSAMENTE
═══════════════════════════════════════

👤 Nome: {cliente.cliente.title()}
📱 Contacto: {cliente.contato}  
📦 Kits: {cliente.kits}

🎉 ¡Pronto meu perro(a)! Cliente agregado correctamente.

📊 Total de clientes: {len(self.lista_clientes)}
"""
                self.mostrar_mensaje(mensaje)
                messagebox.showinfo("✅ Registro Exitoso", 
                                   f"Cliente '{cliente.cliente.title()}' registrado correctamente!")
                
            except ValueError:
                messagebox.showerror("❌ Error", "El número de kits debe ser un número válido")
    
    def consultar_cliente(self):
        """Consultar cliente por nombre"""
        if not self.lista_clientes:
            messagebox.showinfo("📋 Sin Datos", "No hay clientes registrados aún.")
            return
            
        nombre = simpledialog.askstring("🔍 Consultar Cliente", 
                                       "Ingrese el nombre del cafezeiro a buscar:")
        if not nombre:
            return
            
        nombre = nombre.lower().strip()
        encontrados = []
        
        # Búsqueda exacta y parcial
        for cliente in self.lista_clientes:
            if nombre in cliente.cliente.lower():
                encontrados.append(cliente)
        
        if encontrados:
            mensaje = f"🔍 RESULTADOS DE BÚSQUEDA PARA: '{nombre.title()}'\n"
            mensaje += "═" * 60 + "\n\n"
            
            for i, cliente in enumerate(encontrados, 1):
                mensaje += f"✅ RESULTADO #{i}\n"
                mensaje += f"👤 Nome: {cliente.cliente.title()}\n"
                mensaje += f"📱 Contacto: {cliente.contato}\n"
                mensaje += f"📦 Kits: {cliente.kits}\n"
                mensaje += "─" * 40 + "\n\n"
            
            mensaje += f"📊 Total encontrados: {len(encontrados)} cliente(s)"
            self.mostrar_mensaje(mensaje)
            
        else:
            mensaje = f"""
❌ BÚSQUEDA SIN RESULTADOS
═══════════════════════════════

🔍 Término buscado: "{nombre.title()}"
📊 Clientes totales: {len(self.lista_clientes)}

💡 SUGERENCIAS:
• Verifica la ortografía
• Intenta con parte del nombre
• Usa "Listar Todos" para ver todos los clientes

"""
            self.mostrar_mensaje(mensaje)
            messagebox.showwarning("⚠️ No Encontrado", 
                                 f"No se encontraron clientes con '{nombre}'")
    
    def excluir_cliente(self):
        """Excluir cliente por nombre"""
        if not self.lista_clientes:
            messagebox.showinfo("📋 Sin Datos", "No hay clientes para excluir.")
            return
            
        # Crear ventana de selección
        dialog = ExcluirDialog(self.root, self.lista_clientes)
        if dialog.cliente_seleccionado:
            cliente = dialog.cliente_seleccionado
            respuesta = messagebox.askyesno("⚠️ Confirmar Exclusión",
                                           f"¿Estás SEGURO que deseas excluir?\n\n"
                                           f"👤 Cliente: {cliente.cliente.title()}\n"
                                           f"📱 Contacto: {cliente.contato}\n"
                                           f"📦 Kits: {cliente.kits}\n\n"
                                           f"⚠️ Esta acción NO se puede deshacer.")
            if respuesta:
                nombre_excluido = cliente.cliente.title()
                self.lista_clientes.remove(cliente)
                self.actualizar_contador()
                
                mensaje = f"""
✅ CLIENTE EXCLUÍDO EXITOSAMENTE
═══════════════════════════════════

👤 Cliente excluído: {nombre_excluido}
📊 Clientes restantes: {len(self.lista_clientes)}

🗑️ El cliente ha sido eliminado permanentemente del sistema.
"""
                self.mostrar_mensaje(mensaje)
                messagebox.showinfo("✅ Exclusión Completada", 
                                   f"Cliente '{nombre_excluido}' excluído exitosamente")
    
    def listar_todos(self):
        """Listar todos los clientes"""
        if not self.lista_clientes:
            mensaje = """
📋 LISTA DE CLIENTES VACÍA
══════════════════════════════

😔 No hay clientes registrados aún.

💡 ¡Registra tu primer cliente!
Usa "📋 Registrar Cliente" para empezar.
"""
            self.mostrar_mensaje(mensaje)
            return
        
        # Ordenar clientes alfabéticamente
        clientes_ordenados = sorted(self.lista_clientes, key=lambda x: x.cliente.lower())
        
        mensaje = f"📋 LISTA COMPLETA DE CAFEZEIROS ({len(clientes_ordenados)} clientes)\n"
        mensaje += "═" * 70 + "\n\n"
        
        total_kits = 0
        for i, cliente in enumerate(clientes_ordenados, 1):
            mensaje += f"🔢 #{i:02d} ┃ {cliente.cliente.title():<25} ┃ {cliente.kits:>3} kits\n"
            mensaje += f"      📱 {cliente.contato}\n"
            mensaje += "─" * 60 + "\n"
            total_kits += cliente.kits
        
        mensaje += f"\n📊 RESUMEN ESTADÍSTICO:\n"
        mensaje += f"👥 Total clientes: {len(clientes_ordenados)}\n"
        mensaje += f"📦 Total kits: {total_kits}\n"
        mensaje += f"📈 Promedio kits/cliente: {total_kits/len(clientes_ordenados):.1f}\n"
        
        self.mostrar_mensaje(mensaje)
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas detalladas"""
        if not self.lista_clientes:
            messagebox.showinfo("📊 Sin Datos", "No hay datos para mostrar estadísticas.")
            return
            
        total_clientes = len(self.lista_clientes)
        lista_kits = [c.kits for c in self.lista_clientes]
        total_kits = sum(lista_kits)
        promedio_kits = total_kits / total_clientes
        max_kits = max(lista_kits)
        min_kits = min(lista_kits)
        
        # Cliente con más kits
        cliente_max = next(c for c in self.lista_clientes if c.kits == max_kits)
        cliente_min = next(c for c in self.lista_clientes if c.kits == min_kits)
        
        mensaje = f"""
📊 ESTADÍSTICAS DETALLADAS DEL SISTEMA
═══════════════════════════════════════════════

📈 DATOS GENERALES:
👥 Total de clientes: {total_clientes}
📦 Total de kits: {total_kits}
📊 Promedio kits/cliente: {promedio_kits:.1f}

🔺 MÁXIMOS Y MÍNIMOS:
⬆️ Mayor cantidad de kits: {max_kits}
   👤 Cliente: {cliente_max.cliente.title()}
   📱 Contacto: {cliente_max.contato}

⬇️ Menor cantidad de kits: {min_kits}
   👤 Cliente: {cliente_min.cliente.title()}  
   📱 Contacto: {cliente_min.contato}

📊 DISTRIBUCIÓN DE KITS:
"""
        
        # Distribución por rangos
        rangos = {"1-5": 0, "6-10": 0, "11-20": 0, "20+": 0}
        for kits in lista_kits:
            if kits <= 5:
                rangos["1-5"] += 1
            elif kits <= 10:
                rangos["6-10"] += 1
            elif kits <= 20:
                rangos["11-20"] += 1
            else:
                rangos["20+"] += 1
        
        for rango, cantidad in rangos.items():
            porcentaje = (cantidad/total_clientes)*100
            barra = "█" * int(porcentaje/5)  # Barra visual
            mensaje += f"📊 {rango:>5} kits: {cantidad:>3} clientes ({porcentaje:5.1f}%) {barra}\n"
        
        self.mostrar_mensaje(mensaje)
    
    def salvar_dados(self):
        """Guardar datos en archivo JSON"""
        try:
            dados = [{"cliente": c.cliente, "contato": c.contato, "kits": c.kits} 
                    for c in self.lista_clientes]
            with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            
            mensaje = f"""
💾 DATOS GUARDADOS EXITOSAMENTE
═══════════════════════════════════

📁 Archivo: {self.arquivo_dados}
📊 Clientes guardados: {len(self.lista_clientes)}
⏰ Guardado: {tk.datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

✅ Todos los datos están seguros y respaldados.
"""
            self.mostrar_mensaje(mensaje)
            messagebox.showinfo("💾 Guardado Exitoso", 
                               f"¡Datos guardados correctamente!\n"
                               f"📁 {self.arquivo_dados}\n"
                               f"📊 {len(self.lista_clientes)} clientes")
        except Exception as e:
            messagebox.showerror("❌ Error al Guardar", f"Error: {str(e)}")
    
    def recargar_datos(self):
        """Recargar datos del archivo"""
        respuesta = messagebox.askyesno("🔄 Recargar Datos", 
                                       "¿Deseas recargar los datos desde el archivo?\n"
                                       "⚠️ Los cambios no guardados se perderán.")
        if respuesta:
            clientes_antes = len(self.lista_clientes)
            self.carregar_dados()
            clientes_despues = len(self.lista_clientes)
            self.actualizar_contador()
            
            mensaje = f"""
🔄 DATOS RECARGADOS EXITOSAMENTE
═══════════════════════════════════

📊 Clientes antes: {clientes_antes}
📊 Clientes después: {clientes_despues}
📁 Archivo: {self.arquivo_dados}

✅ Sistema actualizado con los últimos datos guardados.
"""
            self.mostrar_mensaje(mensaje)
            messagebox.showinfo("🔄 Recarga Exitosa", "Datos recargados correctamente")
    
    def carregar_dados(self):
        """Cargar datos del archivo JSON"""
        if os.path.exists(self.arquivo_dados):
            try:
                with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self.lista_clientes = [Semanal(**item) for item in dados]
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error al cargar datos: {e}")
                self.lista_clientes = []
    
    def salir(self):
        """Salir de la aplicación"""
        respuesta = messagebox.askyesnocancel("🚪 Salir", 
                                             "¿Deseas guardar los datos antes de salir?\n\n"
                                             "Sí: Guardar y salir\n"
                                             "No: Salir sin guardar\n"
                                             "Cancelar: Continuar trabajando")
        if respuesta is True:  # Sí
            self.salvar_dados()
            messagebox.showinfo("👋 ¡Hasta Luego Tony!", 
                               "¡Gracias por usar el Gestor de Cafezeiros!\n\n"
                               "💾 Datos guardados correctamente\n"
                               "☕ ¡Hasta la próxima!")
            self.root.quit()
        elif respuesta is False:  # No
            messagebox.showinfo("👋 ¡Hasta Luego Tony!", 
                               "☕ ¡Gracias por usar el sistema!")
            self.root.quit()
        # Si es None (Cancelar), no hace nada
    
    def ejecutar(self):
        """Ejecutar la aplicación"""
        self.root.protocol("WM_DELETE_WINDOW", self.salir)
        self.root.mainloop()


class ClienteDialog:
    def __init__(self, parent, titulo):
        self.resultado = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(titulo)
        self.dialog.geometry("450x350")
        self.dialog.configure(bg='#1a1a2e')
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.transient(parent)
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 225
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 175
        self.dialog.geometry(f"+{x}+{y}")
        
        self.setup_dialog()
        self.dialog.wait_window()
    
    def setup_dialog(self):
        # Marco principal
        main_frame = tk.Frame(self.dialog, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        titulo = tk.Label(main_frame, text="📝 Registro de Nuevo Cliente", 
                         font=('Segoe UI', 16, 'bold'),
                         bg='#1a1a2e', fg='#00d4ff')
        titulo.pack(pady=(0, 20))
        
        # Campos
        fields_frame = tk.Frame(main_frame, bg='#1a1a2e')
        fields_frame.pack(fill='both', expand=True)
        
        # Campo nombre
        tk.Label(fields_frame, text="👤 Nome do Cafezeiro:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#1a1a2e', fg='#eee').pack(anchor='w', pady=(10,5))
        self.entry_cliente = tk.Entry(fields_frame, font=('Segoe UI', 11), 
                                     width=40, bg='#16213e', fg='#eee',
                                     insertbackground='#00d4ff',
                                     selectbackground='#3498db')
        self.entry_cliente.pack(pady=(0,15), ipady=8)
        
        # Campo contacto
        tk.Label(fields_frame, text="📱 Contacto (WhatsApp/Celular):", 
                font=('Segoe UI', 11, 'bold'),
                bg='#1a1a2e', fg='#eee').pack(anchor='w', pady=(0,5))
        self.entry_contato = tk.Entry(fields_frame, font=('Segoe UI', 11), 
                                     width=40, bg='#16213e', fg='#eee',
                                     insertbackground='#00d4ff',
                                     selectbackground='#3498db')
        self.entry_contato.pack(pady=(0,15), ipady=8)
        
        # Campo kits
        tk.Label(fields_frame, text="📦 Número de Kits:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#1a1a2e', fg='#eee').pack(anchor='w', pady=(0,5))
        self.entry_kits = tk.Entry(fields_frame, font=('Segoe UI', 11), 
                                  width=20, bg='#16213e', fg='#eee',
                                  insertbackground='#00d4ff',
                                  selectbackground='#3498db')
        self.entry_kits.pack(pady=(0,25), ipady=8)
        self.entry_kits.insert(0, "1")  # Valor por defecto
        
        # Botones
        btn_frame = tk.Frame(fields_frame, bg='#1a1a2e')
        btn_frame.pack(pady=20)
        
        btn_registrar = tk.Button(btn_frame, text="✅ Registrar Cliente", 
                                 font=('Segoe UI', 11, 'bold'),
                                 bg='#27ae60', fg='white', 
                                 padx=25, pady=8,
                                 command=self.registrar,
                                 cursor='hand2', relief='flat')
        btn_registrar.pack(side='left', padx=10)
        
        btn_cancelar = tk.Button(btn_frame, text="❌ Cancelar", 
                                font=('Segoe UI', 11, 'bold'),
                                bg='#e74c3c', fg='white', 
                                padx=25, pady=8,
                                command=self.cancelar,
                                cursor='hand2', relief='flat')
        btn_cancelar.pack(side='left', padx=10)
        
        # Focus en el primer campo
        self.entry_cliente.focus()
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.registrar())
        self.dialog.bind('<Escape>', lambda e: self.cancelar())
    
    def registrar(self):
        cliente = self.entry_cliente.get().strip()
        contato = self.entry_contato.get().strip()
        kits = self.entry_kits.get().strip()
        
        if not cliente or not contato or not kits:
            messagebox.showerror("❌ Error", "Todos los campos son obligatorios!")
            return
            
        try:
            kits_int = int(kits)
            if kits_int < 0:
                raise ValueError("Número negativo")
        except ValueError:
            messagebox.showerror("❌ Error", "El número de kits debe ser un número positivo!")
            return
        
        self.resultado = {
            'cliente': cliente,
            'contato': contato,
            'kits': kits
        }
        self.dialog.destroy()
    
    def cancelar(self):
        self.dialog.destroy()


class ExcluirDialog:
    def __init__(self, parent, lista_clientes):
        self.cliente_seleccionado = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("❌ Excluir Cliente")
        self.dialog.geometry("500x400")
        self.dialog.configure(bg='#1a1a2e')
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.transient(parent)
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 250
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 200
        self.dialog.geometry(f"+{x}+{y}")
        
        self.setup_dialog(lista_clientes)
        self.dialog.wait_window()
    
    def setup_dialog(self, lista_clientes):
        main_frame = tk.Frame(self.dialog, bg='#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        titulo = tk.Label(main_frame, text="⚠️ Seleccionar Cliente a Excluir", 
                         font=('Segoe UI', 16, 'bold'),
                         bg='#1a1a2e', fg='#e74c3c')
        titulo.pack(pady=(0, 20))
        
        # Advertencia
        warning = tk.Label(main_frame, 
                          text="⚠️ Esta acción NO se puede deshacer", 
                          font=('Segoe UI', 10, 'italic'),
                          bg='#1a1a2e', fg='#f39c12')
        warning.pack(pady=(0, 15))
        
        # Lista de clientes
        list_frame = tk.Frame(main_frame, bg='#1a1a2e')
        list_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Listbox con scrollbar
        listbox_frame = tk.Frame(list_frame, bg='#1a1a2e')
        listbox_frame.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame, bg='#16213e', troughcolor='#16213e')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(listbox_frame,
                                 font=('Consolas', 10),
                                 bg='#16213e',
                                 fg='#eee',
                                 selectbackground='#3498db',
                                 selectforeground='white',
                                 yscrollcommand=scrollbar.set,
                                 relief='flat',
                                 borderwidth=0)
        self.listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Llenar la lista
        for i, cliente in enumerate(lista_clientes):
            display_text = f"{cliente.cliente.title():<25} | {cliente.kits:>3} kits | {cliente.contato}"
            self.listbox.insert(tk.END, display_text)
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg='#1a1a2e')
        btn_frame.pack(pady=15)
        
        btn_excluir = tk.Button(btn_frame, text="❌ Excluir Seleccionado", 
                               font=('Segoe UI', 11, 'bold'),
                               bg='#e74c3c', fg='white', 
                               padx=20, pady=8,
                               command=lambda: self.seleccionar_cliente(lista_clientes),
                               cursor='hand2', relief='flat')
        btn_excluir.pack(side='left', padx=10)
        
        btn_cancelar = tk.Button(btn_frame, text="🚪 Cancelar", 
                                font=('Segoe UI', 11, 'bold'),
                                bg='#95a5a6', fg='white', 
                                padx=20, pady=8,
                                command=self.dialog.destroy,
                                cursor='hand2', relief='flat')
        btn_cancelar.pack(side='left', padx=10)
        
        # Doble click para seleccionar
        self.listbox.bind('<Double-1>', lambda e: self.seleccionar_cliente(lista_clientes))
        
        # Escape para cancelar
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def seleccionar_cliente(self, lista_clientes):
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showwarning("⚠️ Sin Selección", "Selecciona un cliente de la lista")
            return
        
        indice = seleccion[0]
        self.cliente_seleccionado = lista_clientes[indice]
        self.dialog.destroy()


# Importar datetime para timestamps
import datetime


if __name__ == "__main__":
    print("🚀 Iniciando Gestor de Cafezeiros - Tony Edition...")
    print("☕ Sistema profesional para gestión de clientes")
    print("━" * 50)
    
    try:
        app = CafezeirosManager()
        app.ejecutar()
    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        input("Presiona Enter para salir...")