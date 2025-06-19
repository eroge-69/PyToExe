import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import math
import matplotlib.pyplot as plt
import os 
import vlc
import webbrowser

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Estudio de Caracterización de Residuos Sólidos Municipales (ECRS)")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        width = int(screen_width * 1)
        height = int(screen_height * 0.85)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")
        root.configure(background="#F2DA5E", bd=10, relief="groove")
        self.fuente = ('Segoe UI', 11)
        
        # Inicialización de las listas de resultados y contadores
        self.densidad_resultados = []  # Lista para almacenar los resultados de la densidad
        self.humedad_resultados = []  # Lista para almacenar los resultados de humedad
        self.eia_resultados = []  # Lista para almacenar los resultados de EIA
        self.contador_densidad = 0  # Contador para los resultados de densidad
        self.contador_humedad = 0  # Contador para los resultados de humedad
        self.contador_eia = 0  # Contador para los resultados de EIA

        self.crear_interfaz()

    def crear_interfaz(self):
        frame_titulo = tk.Frame(self.root, bg="#8C2029")
        frame_titulo.pack(fill="x", pady=20)
        ttk.Label(frame_titulo, text="Estudio de Caracterización de Residuos Sólidos Municipales (ECRS)",
                  font=('Segoe UI', 20, 'bold'), foreground="white", background="#8C2029").pack(pady=5)

        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, expand=True, fill="both")
        
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Estimación de Densidad", padding=10)
        self.crear_interfaz_tab2(tab2)
        
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Estimación de la Humedad", padding=10)
        self.crear_interfaz_tab3(tab3)

        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="EIA Metologia CONESA", padding=10)
        self.crear_interfaz_tab4(tab4)

        tab5 = tk.Frame(notebook)
        notebook.add(tab5, text="Archivos de trabajo", padding=10)
        self.crear_interfaz_tab5(tab5)

    def crear_interfaz_tab2(self, tab):
        ttk.Label(tab, text="Estimación de la Densidad de Residuos Sólidos", font=('Segoe UI', 13, 'bold')).pack(pady=10)
        ttk.Label(tab, text="Fórmula:\nVolumen (Vr) = pi * D * D * (Hf - H0) / 4\nDensidad (S) = W / Vr",
                  font=self.fuente, anchor='center', background="#F2DA5E").pack(pady=10, padx=20, anchor='center')

        frame_formulario = ttk.Frame(tab)
        frame_formulario.pack(fill="both", expand=True)
        
        self.peso_residuos = self.crear_entrada(frame_formulario, "Peso de los residuos sólidos (W) [kg]", 0)
        self.diametro = self.crear_entrada(frame_formulario, "Diámetro del cilindro (D) [m]", 1)
        self.altura_total = self.crear_entrada(frame_formulario, "Altura total del cilindro (Hf) [m]", 2)
        self.altura_libre = self.crear_entrada(frame_formulario, "Altura libre del cilindro (H0) [m]", 3)

        frame_resultado = ttk.Frame(tab)
        frame_resultado.pack(pady=20)
        
        ttk.Button(frame_resultado, text="Calcular Densidad", command=self.calcular_densidad, style="TButton").pack(pady=5)
        
        self.resultado_label2 = ttk.Label(frame_resultado, text="Resultado: ", font=('Segoe UI', 13, 'bold'))
        self.resultado_label2.pack(pady=10)
        
        ttk.Button(frame_resultado, text="Limpiar campos", command=self.limpiar_campos_tab2, style="TButton").pack(pady=5)
        ttk.Button(frame_resultado, text="Generar gráfico", command=self.generar_grafico_densidad, style="TButton").pack(pady=5)

        # Agregar tabla para mostrar los resultados
        self.tabla_resultados = ttk.Treeview(tab, columns=("Resultado", "Peso", "Diámetro", "Altura Total", "Altura Libre"), show="headings")
        self.tabla_resultados.pack(pady=20, fill="both", expand=True)
        
        self.tabla_resultados.heading("Resultado", text="Densidad (kg/m³)")
        self.tabla_resultados.heading("Peso", text="Peso (kg)")
        self.tabla_resultados.heading("Diámetro", text="Diámetro (m)")
        self.tabla_resultados.heading("Altura Total", text="Altura Total (m)")
        self.tabla_resultados.heading("Altura Libre", text="Altura Libre (m)")
        
        self.contador_label = ttk.Label(tab, text=f"Resultados guardados: {self.contador_densidad}", font=self.fuente)
        self.contador_label.pack()

    def crear_entrada(self, frame, texto, fila):
        ttk.Label(frame, text=texto, font=self.fuente).grid(row=fila, column=0, padx=10, pady=5, sticky="e")
        entry = ttk.Entry(frame, width=20, font=self.fuente, background="#D9D9D9")
        entry.grid(row=fila, column=1, padx=10, pady=5, sticky="w")
        entry.insert(0, '0.0')
        entry.bind("<FocusOut>", lambda e: self.validar_entrada(entry))
        return entry

    def validar_entrada(self, entry):
        try:
            float(entry.get())
        except ValueError:
            messagebox.showerror("Error de entrada", "Por favor, ingrese un valor numérico válido.")
            entry.delete(0, tk.END)
            entry.insert(0, '0.0')

    def calcular_densidad(self):
        try:
            W = float(self.peso_residuos.get())
            D = float(self.diametro.get())
            Hf = float(self.altura_total.get())
            H0 = float(self.altura_libre.get())
            Vr = math.pi * D * D * (Hf - H0) * 0.25
            densidad = W / Vr
            
            # Guardar el resultado
            self.densidad_resultados.append((densidad, W, D, Hf, H0))
            self.contador_densidad += 1
            
            # Actualizar el contador
            self.contador_label.config(text=f"Resultados guardados: {self.contador_densidad}")
            
            # Mostrar el resultado en la tabla
            self.tabla_resultados.insert("", "end", values=(f"{densidad:.2f}", W, D, Hf, H0))
            
            # Solo mostrar el resultado
            self.resultado_label2.config(text=f"Resultado: {densidad:.2f} kg/m³")
            
        except Exception as e:
            messagebox.showerror("Error", "Hubo un problema con los cálculos. Por favor revise las entradas.")

    def limpiar_campos_tab2(self):
        self.peso_residuos.delete(0, tk.END)
        self.diametro.delete(0, tk.END)
        self.altura_total.delete(0, tk.END)
        self.altura_libre.delete(0, tk.END)
        self.peso_residuos.insert(0, '0.0')
        self.diametro.insert(0, '0.0')
        self.altura_total.insert(0, '0.0')
        self.altura_libre.insert(0, '0.0')
        self.resultado_label2.config(text="Resultado: ")

    # Similar logic for Humedad Tab
    def crear_interfaz_tab3(self, tab):
        ttk.Label(tab, text="Estimación de la Humedad de Residuos Sólidos", font=('Segoe UI', 13, 'bold')).pack(pady=10)
        ttk.Label(tab, text="Fórmula:\nFracción de residuos orgánicos (r) = A / (A + B)\nHumedad total (Ht) = (r * 100) * (H / 100)",
                  font=self.fuente, anchor='center', background="#F2DA5E").pack(pady=10, padx=20, anchor='center')
        
        frame_formulario = ttk.Frame(tab)
        frame_formulario.pack(fill="both", expand=True)
        
        self.peso_organico = self.crear_entrada(frame_formulario, "Peso de residuos orgánicos (A) [kg]", 0)
        self.peso_inorganico = self.crear_entrada(frame_formulario, "Peso de residuos inorgánicos (B) [kg]", 1)
        self.humedad_organico = self.crear_entrada(frame_formulario, "Humedad orgánica (H) [%]", 2)
        
        frame_resultado = ttk.Frame(tab)
        frame_resultado.pack(pady=20)
        
        ttk.Button(frame_resultado, text="Calcular Humedad", command=self.calcular_humedad, style="TButton").pack(pady=5)
        
        self.resultado_label3 = ttk.Label(frame_resultado, text="Resultado: ", font=('Segoe UI', 13, 'bold'))
        self.resultado_label3.pack(pady=10)
        
        ttk.Button(frame_resultado, text="Limpiar campos", command=self.limpiar_campos_tab3, style="TButton").pack(pady=5)
        ttk.Button(frame_resultado, text="Generar gráfico", command=self.generar_grafico_humedad, style="TButton").pack(pady=5)

        # Agregar tabla para mostrar los resultados
        self.tabla_resultados_humedad = ttk.Treeview(tab, columns=("Resultado", "Peso Orgánico", "Peso Inorgánico", "Humedad Orgánica"), show="headings")
        self.tabla_resultados_humedad.pack(pady=20, fill="both", expand=True)
        
        self.tabla_resultados_humedad.heading("Resultado", text="Humedad (%)")
        self.tabla_resultados_humedad.heading("Peso Orgánico", text="Peso Orgánico (kg)")
        self.tabla_resultados_humedad.heading("Peso Inorgánico", text="Peso Inorgánico (kg)")
        self.tabla_resultados_humedad.heading("Humedad Orgánica", text="Humedad Orgánica (%)")
        
        self.contador_label_humedad = ttk.Label(tab, text=f"Resultados guardados: {self.contador_humedad}", font=self.fuente)
        self.contador_label_humedad.pack()

    def calcular_humedad(self):
        try:
            A = float(self.peso_organico.get())
            B = float(self.peso_inorganico.get())
            H = float(self.humedad_organico.get())
            r = A / (A + B)
            Ht = (r * 100) * (H / 100)
            
            # Guardar el resultado
            self.humedad_resultados.append((Ht, A, B, H))
            self.contador_humedad += 1
            
            # Actualizar el contador
            self.contador_label_humedad.config(text=f"Resultados guardados: {self.contador_humedad}")
            
            # Mostrar el resultado en la tabla
            self.tabla_resultados_humedad.insert("", "end", values=(f"{Ht:.2f}", A, B, H))
            
            # Solo mostrar el resultado
            self.resultado_label3.config(text=f"Resultado: {Ht:.2f} %")
            
        except Exception as e:
            messagebox.showerror("Error", "Hubo un problema con los cálculos. Por favor revise las entradas.")

    def limpiar_campos_tab3(self):
        self.peso_organico.delete(0, tk.END)
        self.peso_inorganico.delete(0, tk.END)
        self.humedad_organico.delete(0, tk.END)
        self.peso_organico.insert(0, '0.0')
        self.peso_inorganico.insert(0, '0.0')
        self.humedad_organico.insert(0, '0.0')
        self.resultado_label3.config(text="Resultado: ")

    # Similar logic for EIA Tab
    def crear_interfaz_tab4(self, tab):
        # Crear frame contenedor para canvas y scrollbar
        frame_contenedor = ttk.Frame(tab)
        frame_contenedor.pack(fill="both", expand=True)

        # Canvas y scrollbar vertical
        canvas = tk.Canvas(frame_contenedor, background="#F2DA5E")
        scrollbar = ttk.Scrollbar(frame_contenedor, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Frame interno dentro del canvas para el contenido
        scrollable_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Actualizar scrollregion cuando cambia tamaño del contenido
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", on_frame_configure)

        # Ajustar ancho del frame interno al ancho del canvas
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        # Contenido dentro del scrollable_frame (igual que antes)
        ttk.Label(scrollable_frame, text="EIA Metologia CONESA", font=('Segoe UI', 13, 'bold')).pack(pady=10)
        ttk.Label(scrollable_frame, text="Fórmula:\nEIA Metologia CONESA (EIA) = v1 × ( ( 3 × v2 ) + ( 2 × v3 ) + v4 + v5 + v6 + v7 + v8 + v9 + v10 + v11 )",
                  font=self.fuente, anchor='center', background="#F2DA5E").pack(pady=10, padx=20, anchor='center')

        frame_formulario = ttk.Frame(scrollable_frame)
        frame_formulario.pack(fill="both", expand=True)
        
        self.uno = self.crear_entrada(frame_formulario, "1. Naturaleza", 0)
        self.dos = self.crear_entrada(frame_formulario, "2. Entensidad", 1)
        self.tres = self.crear_entrada(frame_formulario, "3. Extensión", 2)
        self.cuatro = self.crear_entrada(frame_formulario, "4. Momento", 3)
        self.cinco = self.crear_entrada(frame_formulario, "5. Persistencia", 4)
        self.seis = self.crear_entrada(frame_formulario, "6. Reversibilidad", 5)
        self.siete = self.crear_entrada(frame_formulario, "7. Sinergia", 6)
        self.ocho = self.crear_entrada(frame_formulario, "8. Acumulación", 7)
        self.nueve = self.crear_entrada(frame_formulario, "9. Extensión", 8)
        self.diez = self.crear_entrada(frame_formulario, "10. Extensión", 9)
        self.once = self.crear_entrada(frame_formulario, "11. Extensión", 10)

        frame_resultado = ttk.Frame(scrollable_frame)
        frame_resultado.pack(pady=20)
        
        ttk.Button(frame_resultado, text="Calcular EIA", command=self.calcular_EIA, style="TButton").pack(pady=5)
        
        self.resultado_label4 = ttk.Label(frame_resultado, text="Resultado: ", font=('Segoe UI', 13, 'bold'))
        self.resultado_label4.pack(pady=10)
        
        ttk.Button(frame_resultado, text="Limpiar campos", command=self.limpiar_campos_tab4, style="TButton").pack(pady=5)
        ttk.Button(frame_resultado, text="Generar gráfico", command=self.generar_grafico_eia, style="TButton").pack(pady=5)

        self.tabla_resultados_eia = ttk.Treeview(scrollable_frame, columns=("Resultado", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10", "V11"), show="headings")
        self.tabla_resultados_eia.pack(pady=20, fill="both", expand=True)

        # Configurar columnas y encabezados
        self.tabla_resultados_eia.column("Resultado", width=120, anchor="center", stretch=tk.YES)
        self.tabla_resultados_eia.column("V1", width=100, anchor="center", stretch=tk.YES)
        self.tabla_resultados_eia.column("V2", width=100, anchor="center", stretch=tk.YES)
        self.tabla_resultados_eia.column("V3", width=100, anchor="center", stretch=tk.YES)
        self.tabla_resultados_eia.column("V4", width=100, anchor="center", stretch=tk.YES)
        self.tabla_resultados_eia.column("V5", width=100, anchor="center", stretch=tk.YES)
        self.tabla_resultados_eia.column("V6", width=100, anchor="center", stretch=tk.YES)
        self.tabla_resultados_eia.column("V7", width=100, anchor="center", stretch=tk.YES)
        self.tabla_resultados_eia.column("V8", width=100, anchor="center", stretch=tk.YES)
        self.tabla_resultados_eia.column("V9", width=100, anchor="center", stretch=tk.YES)
        self.tabla_resultados_eia.column("V10", width=100, anchor="center", stretch=tk.YES)
        self.tabla_resultados_eia.column("V11", width=100, anchor="center", stretch=tk.YES)

        self.tabla_resultados_eia.heading("Resultado", text="EIA")
        self.tabla_resultados_eia.heading("V1", text="Naturaleza")
        self.tabla_resultados_eia.heading("V2", text="Entensidad")
        self.tabla_resultados_eia.heading("V3", text="Extensión")
        self.tabla_resultados_eia.heading("V4", text="Momento")
        self.tabla_resultados_eia.heading("V5", text="Persistencia")
        self.tabla_resultados_eia.heading("V6", text="Reversibilidad")
        self.tabla_resultados_eia.heading("V7", text="Sinergia")
        self.tabla_resultados_eia.heading("V8", text="Acumulación")
        self.tabla_resultados_eia.heading("V9", text="Extensión")
        self.tabla_resultados_eia.heading("V10", text="Extensión")
        self.tabla_resultados_eia.heading("V11", text="Extensión")

        self.contador_label_eia = ttk.Label(scrollable_frame, text=f"Resultados guardados: {self.contador_eia}", font=self.fuente)
        self.contador_label_eia.pack()


    def crear_entrada(self, frame, texto, fila):
        ttk.Label(frame, text=texto, font=self.fuente).grid(row=fila, column=0, padx=10, pady=5, sticky="e")
        entry = ttk.Entry(frame, width=20, font=self.fuente, background="#D9D9D9")
        entry.grid(row=fila, column=1, padx=10, pady=5, sticky="w")
        entry.insert(0, '0.0')
        entry.bind("<FocusOut>", lambda e: self.validar_entrada(entry))
        return entry

    def validar_entrada(self, entry):
        try:
            float(entry.get())
        except ValueError:
            messagebox.showerror("Error de entrada", "Por favor, ingrese un valor numérico válido.")
            entry.delete(0, tk.END)
            entry.insert(0, '0.0')
    def calcular_EIA(self):
        try:
            V1 = float(self.uno.get())
            V2 = float(self.dos.get())
            V3 = float(self.tres.get())
            V4 = float(self.cuatro.get())
            V5 = float(self.cinco.get())
            V6 = float(self.seis.get())
            V7 = float(self.siete.get())
            V8 = float(self.ocho.get())
            V9 = float(self.nueve.get())
            V10 = float(self.diez.get())
            V11 = float(self.once.get())
            
            EIA = V1 * ( ( 3 * V2 ) + ( 2 * V3 ) + V4 + V5 + V6 + V7 + V8 + V9 + V10 + V11 )
            
            # Guardar el resultado
            self.eia_resultados.append((EIA, V1, V2, V3, V4, V5, V6, V7, V8, V9, V10, V11))
            self.contador_eia += 1
            
            # Actualizar el contador
            self.contador_label_eia.config(text=f"Resultados guardados: {self.contador_eia}")
            
            # Mostrar el resultado en la tabla
            self.tabla_resultados_eia.insert("", "end", values=(f"{EIA:.2f}", V1, V2, V3, V4, V5, V6, V7, V8, V9, V10, V11))
            
            # Solo mostrar el resultado
            self.resultado_label4.config(text=f"Resultado: {EIA:.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", "Hubo un problema con los cálculos. Por favor revise las entradas.")

    def limpiar_campos_tab4(self):
        self.uno.delete(0, tk.END)
        self.dos.delete(0, tk.END)
        self.tres.delete(0, tk.END)
        self.cuatro.delete(0, tk.END)
        self.cinco.delete(0, tk.END)
        self.seis.delete(0, tk.END)
        self.siete.delete(0, tk.END)
        self.ocho.delete(0, tk.END)
        self.nueve.delete(0, tk.END)
        self.diez.delete(0, tk.END)
        self.once.delete(0, tk.END)
        self.uno.insert(0, '0.0')
        self.dos.insert(0, '0.0')
        self.tres.insert(0, '0.0')
        self.cuatro.insert(0, '0.0')
        self.cinco.insert(0, '0.0')
        self.seis.insert(0, '0.0')
        self.siete.insert(0, '0.0')
        self.ocho.insert(0, '0.0')
        self.nueve.insert(0, '0.0')
        self.diez.insert(0, '0.0')
        self.once.insert(0, '0.0')
        self.resultado_label4.config(text="Resultado: ")

    def crear_interfaz_tab5(self, tab):
        
        ttk.Label(tab, text="Archivos de Trabajo", font=('Segoe UI', 13, 'bold')).pack(pady=15)
        ttk.Label(tab, text="Seleccione el archivo Excel que desea abrir:",
                  font=self.fuente, background="#F2DA5E").pack(pady=10)

        frame_botones = ttk.Frame(tab)
        frame_botones.pack(pady=20)

        ruta_excel_1 = r"C:\Users\Johan\Downloads\Excel Phyton\Matriz-de-Leopold (2).xlsx"
        ruta_excel_2 = r"C:\Users\Johan\Downloads\Excel Phyton\ITR - INGENIERÍA AMBIENTAL.xlsx"
        ruta_excel_3 = r"C:\Users\Johan\Downloads\Excel Phyton\MSDS.xlsx"
        ruta_video = r"C:\Users\Johan\Downloads\Excel Phyton\video.mp4"
        self.ruta_video = r"C:\Users\Johan\Downloads\Excel Phyton\video.mp4"
        
        def abrir_archivo(ruta):
            try:
                os.startfile(ruta)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")

        ttk.Button(frame_botones, text="Abrir Excel Leopold", command=lambda: abrir_archivo(ruta_excel_1),
                   style="TButton").pack(pady=10, fill='x')
        ttk.Button(frame_botones, text="Abrir Excel ITR", command=lambda: abrir_archivo(ruta_excel_2),
                   style="TButton").pack(pady=10, fill='x')
        ttk.Button(frame_botones, text="Abrir Excel MSDS", command=lambda: abrir_archivo(ruta_excel_3),
                   style="TButton").pack(pady=10, fill='x')
        
        def abrir_pagina_web():
            url = "https://sites.google.com/unmsm.edu.pe/ing-ambiental/inicio"
            webbrowser.open(url)
            
        ttk.Button(frame_botones, text="Ir a Ingeniería Ambiental UNMSM", command=abrir_pagina_web).pack(pady=10, fill='x')
        
        ttk.Label(tab, text="Visualizar video demostrativo:", font=self.fuente).pack(pady=5)
        ttk.Button(frame_botones, text="Abrir video", command=lambda: abrir_archivo(ruta_video)).pack(pady=10, fill='x')

        # Frame para botones de video
        frame_video = ttk.Frame(tab)
        frame_video.pack(pady=10, fill='both', expand=True)

        # Frame para contener el video
        video_panel = tk.Frame(frame_video, bg='black')
        video_panel.pack(fill='both', expand=True)

        # Instanciar VLC
        instancia = vlc.Instance()
        player = instancia.media_player_new()

        def reproducir_video():
            media = instancia.media_new(ruta_video)
            player.set_media(media)

            # Asignar el handle del widget para que VLC renderice ahí (Windows)
            player.set_hwnd(video_panel.winfo_id())

            player.play()

        ttk.Button(frame_video, text="Reproducir video", command=reproducir_video).pack(pady=5)

        # Guardar referencias para que no se recolecten (si es clase, usa self)
        self.vlc_instance = instancia
        self.vlc_player = player
        self.video_panel = video_panel
        
    def generar_grafico_densidad(self):
        if not self.densidad_resultados:
            messagebox.showwarning("Sin datos", "No hay resultados para graficar.")
            return
        
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker

        # Extraer valores de densidad (primer elemento de cada tupla en la lista de resultados)
        resultados = [res[0] for res in self.densidad_resultados]
        indices = list(range(1, len(resultados) + 1))

        plt.figure(figsize=(8, 5))
        plt.plot(indices, resultados, marker='o', linestyle='-', color='r')
        plt.title("Gráfico de Densidad (kg/m³)")
        plt.xlabel("Número de resultado")
        plt.ylabel("Densidad (kg/m³)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    
    def generar_grafico_humedad(self):
        if not self.humedad_resultados:
            messagebox.showwarning("Sin datos", "No hay resultados para graficar.")
            return

        # Extraer valores de humedad total (Ht) de los resultados guardados
        resultados = [res[0] for res in self.humedad_resultados]
        indices = list(range(1, len(resultados) + 1))

        plt.figure(figsize=(8, 5))
        plt.plot(indices, resultados, marker='o', linestyle='-', color='g')
        plt.title("Gráfico de Humedad Total (%)")
        plt.xlabel("Número de resultado")
        plt.ylabel("Humedad Total (%)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def generar_grafico_eia(self):
        if not self.eia_resultados:
            messagebox.showwarning("Sin datos", "No hay resultados para graficar.")
            return
    
        # Extraer los valores EIA de los resultados guardados
        resultados = [res[0] for res in self.eia_resultados]
        indices = list(range(1, len(resultados) + 1))
        
        plt.figure(figsize=(8, 5))
        plt.plot(indices, resultados, marker='o', linestyle='-', color='b')
        plt.title("Gráfico de resultados EIA")
        plt.xlabel("Número de resultado")
        plt.ylabel("Valor EIA")
        plt.grid(True)
        ax = plt.gca()
        plt.tight_layout()
        plt.show()
    
# Iniciar la aplicación
root = tk.Tk()
app = App(root)
root.mainloop()
