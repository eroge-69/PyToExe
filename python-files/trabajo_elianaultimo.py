from tkinter import *
from tkinter import ttk
from math import *
from PIL import Image, ImageTk
import re

class Miproyecto():

    def __init__(self):
        self.completacion = False
        self.facilidades = False
        self.fondo_imagen = False
        self.ventana_madre()
        
    def ventana_madre(self):
        self.ventana = Tk()
        self.ventana.state('zoomed')
        self.ventana.title("Programa Sexto Semestre")
        self.modificacion_ventana()
        self.ventana.mainloop()

    def modificacion_ventana(self):
        primer_fondo= Frame(self.ventana,
                            bg = "white")
        primer_fondo.pack(expand= True,
                          fill= "both")

        self.primer_cuadro= Frame(primer_fondo,
                            bg = "#1d1529")
        self.primer_cuadro.pack( fill= "x",ipady=50)

        Titulo = Label(self.primer_cuadro,
                       bg="#1d1529",
                       fg="white",
                       text="Proyecto de ",
                       font=("Helvetica", 30, "bold")) 
        Titulo.place(x=250, y=20)

        boton_completacion = Button(self.primer_cuadro,
                                    text="Completacion de Pozos",
                                    font=("Arial" , 16 , "bold"),
                                    bg="white",
                                    width=20,
                                    fg="black",
                                    border= 5,
                                    command=  lambda: self.completacion_pozos())
        boton_completacion.place(x = 550 , y = 25)

        boton_facilidades = Button(self.primer_cuadro,
                                   text="Facilidades de Superficie",
                                   font=("Arial" , 16 , "bold"),
                                   bg="white",
                                   width=20,
                                   fg="black",
                                   border= 5,
                                   command= lambda: self.facilidades_superficie())
        boton_facilidades.place(x = 900 , y = 25)

        boton_regresar = Button(self.primer_cuadro,
                                   text="←",
                                   font=("Arial" , 15 , "bold"),
                                   bg="white",
                                   fg="black",
                                   border= 5,
                                   
                                   command= lambda: self.imagen_fondo())
        boton_regresar.place(x = 20 , y = 30,height = 40 )


        self.segundo_cuadro= Frame(primer_fondo,bg = "red")
        self.segundo_cuadro.pack(side="bottom",
                                 expand= True ,
                                 fill= "both")

        self.imagen_fondo()

    def imagen_fondo(self):

        if self.fondo_imagen ==True:
            self.imagen_cuadro.destroy()

        if self.facilidades ==True:
            self.cuadro_facilidades.destroy()

        if self.completacion ==True:
            self.cuadro_completacion.destroy()

        self.imagen_cuadro= Frame(self.segundo_cuadro)
        self.imagen_cuadro.pack(side="bottom",
                                 expand= True ,
                                 fill= "both")

        ancho_pantalla = self.ventana.winfo_screenwidth()
        alto_pantalla = self.ventana.winfo_screenheight()

        # Cargar y redimensionar la imagen
        imagen = Image.open("levantamientos.png")
        imagen = imagen.resize((int(ancho_pantalla), int(alto_pantalla)-160), Image.Resampling.LANCZOS)  # Redimensionar si es necesario
        # Convertir para Tkinter
        imagen_tk = ImageTk.PhotoImage(imagen)
        # Mostrar en Label
        etiqueta_imagen = Label(self.imagen_cuadro, image=imagen_tk)
        etiqueta_imagen.image = imagen_tk  # ¡Importante! Mantener referencia
        etiqueta_imagen.pack(expand= 1 , fill = "both")

        self.fondo_imagen = True

    def completacion_pozos(self):

        if self.fondo_imagen ==True:
            self.imagen_cuadro.destroy()

        if self.facilidades ==True:
            self.cuadro_facilidades.destroy()

        if self.completacion ==True:
            self.cuadro_completacion.destroy()

        self.cuadro_completacion= Frame(self.segundo_cuadro, 
                                        bg = "#2c1f40")
        self.cuadro_completacion.pack(side="bottom",expand= True , fill= "both")

        Titulo = Label(self.cuadro_completacion,
                       bg="#2c1f40",
                       fg="white",
                       text="Sistemas de Levantamiento Artificial",
                       font=("Helvetica", 26, "bold"))
        Titulo.place(x=500, y=10)

        # Entradas de datos
        self.profundidad = Entry(self.cuadro_completacion,
                                   width=8,
                                   font=("Arial", 15),
                                   fg="black",
                                   bg="white")
        self.profundidad.place(x=350, y=100)

        profundidad_maxima = Label(self.cuadro_completacion,
                         bg="#2c1f40",
                         fg="white",
                         text="Profundidad Maxima",
                         font=("Helvetica", 20, "bold"))
        profundidad_maxima.place(x=50, y=100)

        self.tasa = Entry(self.cuadro_completacion,
                                   width=8,
                                   font=("Arial", 15),
                                   fg="black",
                                   bg="white")
        self.tasa.place(x=350, y=150)

        tasa_operativa = Label(self.cuadro_completacion,
                         bg="#2c1f40",
                         fg="white",
                         text="Tasa Maxima",
                         font=("Helvetica", 20, "bold"))
        tasa_operativa.place(x=50, y=150)

        self.temperatura = Entry(self.cuadro_completacion,
                            width=8,
                            font=("Arial", 15),
                            fg="black",
                            bg="white")
        self.temperatura.place(x=350, y=200)

        temperatura_maxima = Label(self.cuadro_completacion,
                  bg="#2c1f40",
                  fg="white",
                  text="Temperatura Maxima",
                  font=("Helvetica", 20, "bold"))
        temperatura_maxima.place(x=50, y=200)

        self.manejo_gas = StringVar()
        manejo_de_gas =  ttk.Combobox(self.cuadro_completacion,
                                  textvariable= self.manejo_gas,
                                    values=["","Regular","Bueno","Exelente"],  # Lista de opciones
                                    state="readonly",  # Evita que el usuario escriba
                                    font=("Arial", 12),
                                    width=8)
        manejo_de_gas.place(x=350, y=250)

        ManejoGas = Label(self.cuadro_completacion,
                  bg="#2c1f40",
                  fg="white",
                  text="Manejo de Gas",
                  font=("Helvetica", 20, "bold"))
        ManejoGas.place(x=50, y=250)

        self.manejo_corrosion = StringVar()
        manejo_de_corrosion= ttk.Combobox(self.cuadro_completacion,
                                  textvariable= self.manejo_corrosion,
                                    values=["","Regular","Bueno","Excelente"],  # Lista de opciones
                                    state="readonly",  # Evita que el usuario escriba
                                    font=("Arial", 12),
                                    width=8)
        manejo_de_corrosion.place(x=350, y=300)

        ManejoCorrosion = Label(self.cuadro_completacion,
                  bg="#2c1f40",
                  fg="white",
                  text="Manejo de Corrosion",
                  font=("Helvetica", 20, "bold"))
        ManejoCorrosion.place(x=50, y=300)

        self.manejo_solidos = StringVar()
        manejo_de_solidos = ttk.Combobox(self.cuadro_completacion,
                                  textvariable= self.manejo_solidos,
                                    values=["","Regular","Bueno","Excelente"],  # Lista de opciones
                                    state="readonly",  # Evita que el usuario escriba
                                    font=("Arial", 12),
                                    width=8)
        manejo_de_solidos.place(x=350, y=350)

        ManejoSolidos = Label(self.cuadro_completacion,
                   bg="#2c1f40",
                   fg="white",
                   text="Manejo de Solidos",
                   font=("Helvetica", 20, "bold"))
        ManejoSolidos.place(x=50, y=350)

        self.api = Entry(self.cuadro_completacion,
                                   width=8,
                                   font=("Arial", 15),
                                   fg="black",
                                   bg="white")
        self.api.place(x=350, y=400)

        API = Label(self.cuadro_completacion,
                         bg="#2c1f40",
                         fg="white",
                         text="Gravedad API",
                         font=("Helvetica", 20, "bold"))
        API.place(x=50, y=400)

        self.aplicacion= StringVar()
        aplicacion_lista = ttk.Combobox(self.cuadro_completacion,
                                  textvariable= self.aplicacion,
                                    values=["","Limitado","Bueno","Excelente"],  # Lista de opciones
                                    state="readonly",  # Evita que el usuario escriba
                                    font=("Arial", 12),
                                    width=8)
        aplicacion_lista.place(x=350, y=450)

        aplicacion_offshore = Label(self.cuadro_completacion,
                          bg="#2c1f40",
                          fg="white",
                          text="Aplicacion Offshore",
                          font=("Helvetica", 20, "bold"))
        aplicacion_offshore.place(x=50, y=450)

        # Botón para calcular
        boton_calcular = Button(self.cuadro_completacion,
                                 text="Realizar Analisis", 
                                 font=("Arial", 15),
                                   width=20, 
                                   command= self.levantamientos_artificiales)# crea un boton dentro de la ventana  y ejecuta funciones establecidas (donde va, su texto, tu tipo de texto, su largo, el commands es donde se ejecutara las funciones establecidas )
        boton_calcular.place(x=210, y=510)

        RESULTADO = Label(self.cuadro_completacion,
                          bg="#2c1f40",
                          fg="white",
                          text="El mejor Levantamiento Artificial para este caso es: ",
                          font=("Helvetica", 20, "bold"))
        RESULTADO.place(x=500, y=510)

        self.resultado = Label(self.cuadro_completacion,
                          bg="#2c1f40",
                          fg="white",
                          text="----------------------",
                          font=("Helvetica", 20, "bold"))
        self.resultado.place(x=500, y=560)

        #diseño de la tabla

        self.tabla = Frame(self.cuadro_completacion, bg = "white")
        self.tabla.place(x=500, y=100 , width= 1000 , height=400)

        self.completacion = True

    def levantamientos_artificiales(self):


        profundidad = self.profundidad.get()

        tasa = self.tasa.get() 

        temperatura = self.temperatura.get()

        manejo_gas = self.manejo_gas.get()

        manejo_corrosion = self.manejo_corrosion.get()

        manejo_solidos = self.manejo_solidos.get()

        api = self.api.get() 

        aplicacion = self.aplicacion.get()

        try:
            listado_resultados = []

            # Convert inputs to appropriate types or None
            profundidad = float(profundidad) if profundidad != "" else None
            tasa = float(tasa) if tasa != "" else None
            temperatura = float(temperatura) if temperatura != "" else None
            manejo_gas = str(manejo_gas) if manejo_gas != "" else None
            manejo_corrosion = str(manejo_corrosion) if manejo_corrosion != "" else None
            manejo_solidos = str(manejo_solidos) if manejo_solidos != "" else None
            api = float(api) if api != "" else None
            aplicacion = str(aplicacion) if aplicacion != "" else None

            # Count for BV
            c_bv = 0
            if profundidad is not None and profundidad <= 16000:
                c_bv += 1
            if temperatura is not None and temperatura <= 550:
                c_bv += 1
            if tasa is not None and tasa <= 6000:
                c_bv += 1
            if manejo_solidos is not None and (manejo_solidos == "Regular" or manejo_solidos == "Bueno"):
                c_bv += 1
            if manejo_gas is not None and (manejo_gas == "Bueno" or manejo_gas == "Regular"):
                c_bv += 1
            if manejo_corrosion is not None and (manejo_corrosion == "Bueno" or manejo_corrosion == "Excelente"):
                c_bv += 1
            if api is not None and 8 < api:
                c_bv += 1
            if aplicacion is not None and aplicacion == "Limitado":
                c_bv += 1
            listado_resultados.append(("BV", c_bv))

            # Count for GL
            c_gl = 0  
            if profundidad is not None and profundidad <= 18000:
                c_gl += 1
            if temperatura is not None and temperatura <= 450:
                c_gl += 1
            if tasa is not None and tasa <= 50000:
                c_gl += 1
            if manejo_solidos is not None and manejo_solidos == "Bueno":
                c_gl += 1
            if manejo_gas is not None and manejo_gas == "Excelente":
                c_gl += 1
            if manejo_corrosion is not None and (manejo_corrosion == "Bueno" or manejo_corrosion == "Excelente"):
                c_gl += 1
            if api is not None and 15 < api:
                c_gl += 1
            if aplicacion is not None and aplicacion == "Excelente":
                c_gl += 1
            listado_resultados.append(("GL", c_gl))

            # Count for ESP
            c_esp = 0          
            if profundidad is not None and profundidad <= 15000:
                c_esp += 1
            if temperatura is not None and temperatura <= 400:
                c_esp += 1
            if tasa is not None and tasa <= 60000:
                c_esp += 1
            if manejo_solidos is not None and manejo_solidos == "Regular":
                c_esp += 1
            if manejo_gas is not None and manejo_gas == "Regular":
                c_esp += 1
            if manejo_corrosion is not None and manejo_corrosion == "Bueno":
                c_esp += 1
            if api is not None and 10 < api:
                c_esp += 1
            if aplicacion is not None and aplicacion == "Excelente":
                c_esp += 1
            listado_resultados.append(("ESP", c_esp))

            # Count for PCP
            c_pcp = 0          
            if profundidad is not None and profundidad <= 12000:
                c_pcp += 1
            if temperatura is not None and temperatura <= 250:
                c_pcp += 1
            if tasa is not None and tasa <= 6000:
                c_pcp += 1
            if manejo_solidos is not None and manejo_solidos == "Excelente":
                c_pcp += 1
            if manejo_gas is not None and manejo_gas == "Bueno":
                c_pcp += 1
            if manejo_corrosion is not None and manejo_corrosion == "Regular":
                c_pcp += 1
            if api is not None and api < 40:
                c_pcp += 1
            if aplicacion is not None and aplicacion == "Limitado":
                c_pcp += 1
            listado_resultados.append(("PCP", c_pcp))

            # Count for BH
            c_bh = 0              
            if profundidad is not None and profundidad <= 17000:
                c_bh += 1
            if temperatura is not None and temperatura <= 550:
                c_bh += 1
            if tasa is not None and tasa <= 8000:
                c_bh += 1
            if manejo_solidos is not None and manejo_solidos == "Regular":
                c_bh += 1
            if manejo_gas is not None and manejo_gas == "Regular":
                c_bh += 1
            if manejo_corrosion is not None and manejo_corrosion == "Bueno":
                c_bh += 1
            if api is not None:
                c_bh += 1  # No condition for api_bh in original code
            if aplicacion is not None and aplicacion == "Bueno":
                c_bh += 1
            listado_resultados.append(("BH", c_bh))

            # Count for BJ
            c_bj = 0           
            if profundidad  is not None and profundidad <= 15000:
                c_bj += 1
            if temperatura is not None and temperatura <= 550:
                c_bj += 1
            if tasa is not None and tasa <= 20000:
                c_bj += 1
            if manejo_solidos is not None and manejo_solidos == "Bueno":
                c_bj += 1
            if manejo_gas is not None and manejo_gas == "Bueno":
                c_bj += 1
            if manejo_corrosion is not None and manejo_corrosion == "Excelente":
                c_bj += 1
            if api is not None and 8 < api:
                c_bj += 1
            if aplicacion is not None and aplicacion == "Excelente":
                c_bj += 1
            listado_resultados.append(("BJ", c_bj))

            # Find maximum count and generate final text
            mayor = max(listado_resultados, key=lambda x: x[1])[1]
            mayores = [item for item in listado_resultados if item[1] == mayor]
            texto_final = ""
            for levantamiento, valor in mayores:
                if valor !=0:
                    texto_final += f"({levantamiento} : {valor})    "
            self.resultado.config(text=f"{texto_final}")

            # Extract lifting methods from texto_final
            best_methods = re.findall(r'\((.*?)\s*:\s*\d+\)', texto_final)

            # Clear previous images in the frame
            for widget in self.tabla.winfo_children():
                widget.destroy()

            # Image mapping
            image_map = {
                'BV': 'Bombeo por Varilla.png',
                'GL': 'Gas_Lift.png',
                'ESP': 'Bombeo_Electrosumergible.png',
                'PCP': 'PCP.png',
                'BH': 'Bombeo_Hidráulico.png',
                'BJ': 'Bombeo_Jet.png'
            }

            # Display images for best lifting methods
            for i, method in enumerate(best_methods):
                if method in image_map:
                    try:
                        # Load and resize image (assuming 100x100 for example)
                        image = Image.open(image_map[method])
                        image = image.resize((int(1000/len(best_methods)), 400), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                        # Create label for image
                        label = Label(self.tabla, image=photo)
                        label.image = photo  # Keep a reference to avoid garbage collection
                        label.grid(row=0, column=i, padx=0, pady=0)
                    except FileNotFoundError:
                        # Fallback if image is not found
                        label = Label(self.tabla, text=f"No image for {method}")
                        label.grid(row=0, column=i, padx=0, pady=0)

        except:
            self.resultado.config(text="----------------------")
            # Clear previous images in the frame
            for widget in self.tabla.winfo_children():
                widget.destroy()

    def facilidades_superficie(self):

        if self.fondo_imagen ==True:
            self.imagen_cuadro.destroy()

        if self.completacion ==True:
            self.cuadro_completacion.destroy() 

        if self.facilidades ==True:
            self.cuadro_facilidades.destroy() 
            
        self.cuadro_facilidades= Frame(self.segundo_cuadro, bg = "#2c1f40")
        self.cuadro_facilidades.pack(side="bottom",expand= True , fill= "both")
        self.facilidades = True

        Titulo = Label(self.cuadro_facilidades,
                    bg="#2c1f40",
                    fg="white",
                    text="Calculo de Tuberias Simples",
                    font=("Helvetica", 26, "bold"))
        Titulo.place(x=500, y=10)

        # Entradas de datos
        self.dato_gravedad = Entry(self.cuadro_facilidades,
                                width=8,
                                font=("Arial", 15),
                                fg="black",
                                bg="white")
        self.dato_gravedad.place(x=500, y=75)

        gravedad = Label(self.cuadro_facilidades,
                        bg="#2c1f40",
                        fg="white",
                        text="Gravedad",
                        font=("Helvetica", 20, "bold"))
        gravedad.place(x=300, y=75)

        self.dato_diametro = Entry(self.cuadro_facilidades,
                                width=8,
                                font=("Arial", 15),
                                fg="black",
                                bg="white")
        self.dato_diametro.place(x=500, y=125)

        diametro = Label(self.cuadro_facilidades,
                        bg="#2c1f40",
                        fg="white",
                        text="Diametro",
                        font=("Helvetica", 20, "bold"))
        diametro.place(x=300, y=125)

        self.dato_L = Entry(self.cuadro_facilidades,
                            width=8,
                            font=("Arial", 15),
                            fg="black",
                            bg="white")
        self.dato_L.place(x=500, y=175)

        L = Label(self.cuadro_facilidades,
                bg="#2c1f40",
                fg="white",
                text="Longitud",
                font=("Helvetica", 20, "bold"))
        L.place(x=300, y=175)

        self.dato_e = Entry(self.cuadro_facilidades,
                            width=8,
                            font=("Arial", 15),
                            fg="black",
                            bg="white")
        self.dato_e.place(x=500, y=225)

        e = Label(self.cuadro_facilidades,
                bg="#2c1f40",
                fg="white",
                text="Rugosidad",
                font=("Helvetica", 20, "bold"))
        e.place(x=300, y=225)

        self.dato_H = Entry(self.cuadro_facilidades,
                            width=8,
                            font=("Arial", 15),
                            fg="black",
                            bg="white")
        self.dato_H.place(x=500, y=275)

        H = Label(self.cuadro_facilidades,
                bg="#2c1f40",
                fg="white",
                text="Altura",
                font=("Helvetica", 20, "bold"))
        H.place(x=300, y=275)

        self.dato_km = Entry(self.cuadro_facilidades,
                            width=8,
                            font=("Arial", 15),
                            fg="black",
                            bg="white")
        self.dato_km.place(x=500, y=325)

        km = Label(self.cuadro_facilidades,
                bg="#2c1f40",
                fg="white",
                text="Km",
                font=("Helvetica", 20, "bold"))
        km.place(x=300, y=325)

        self.dato_densidad = Entry(self.cuadro_facilidades,
                                width=8,
                                font=("Arial", 15),
                                fg="black",
                                bg="white")
        self.dato_densidad.place(x=500, y=375)

        densidad = Label(self.cuadro_facilidades,
                        bg="#2c1f40",
                        fg="white",
                        text="Densidad",
                        font=("Helvetica", 20, "bold"))
        densidad.place(x=300, y=375)

        self.dato_altura_z2 = Entry(self.cuadro_facilidades,
                                    width=8,
                                    font=("Arial", 15),
                                    fg="black",
                                    bg="white")
        self.dato_altura_z2.place(x=500, y=425)

        altura_z2 = Label(self.cuadro_facilidades,
                        bg="#2c1f40",
                        fg="white",
                        text="Altura 2",
                        font=("Helvetica", 20, "bold"))
        altura_z2.place(x=300, y=425)

        self.dato_viscosidad_dinamica = Entry(self.cuadro_facilidades,
                                            width=8,
                                            font=("Arial", 15),
                                            fg="black",
                                            bg="white")
        self.dato_viscosidad_dinamica.place(x=500, y=475)

        viscosidad_dinamica = Label(self.cuadro_facilidades,
                                    bg="#2c1f40",
                                    fg="white",
                                    text="Dinamica",
                                    font=("Helvetica", 20, "bold"))
        viscosidad_dinamica.place(x=300, y=475)

        self.dato_viscosidad_cinematica= Entry(self.cuadro_facilidades,
                                            width=8,
                                            font=("Arial", 15),
                                            fg="black",
                                            bg="white")
        self.dato_viscosidad_cinematica.place(x=500, y=525)

        viscosidad_cinematica = Label(self.cuadro_facilidades,
                                    bg="#2c1f40",
                                    fg="white",
                                    text="Cinematica",
                                    font=("Helvetica", 20, "bold"))
        viscosidad_cinematica.place(x=300, y=525)


        self.dato_precision = Entry(self.cuadro_facilidades,
                                    width=8,
                                    font=("Arial", 15),
                                    fg="black",
                                    bg="white")
        self.dato_precision.place(x=500, y=575)

        precision = Label(self.cuadro_facilidades,
                        bg="#2c1f40",
                        fg="white",
                        text="Comprobar",
                        font=("Helvetica", 20, "bold"))
        precision.place(x=300, y=575)

        tipo_tuberia = Label(self.cuadro_facilidades,
                            bg="#2c1f40",
                            fg="white",
                            text="Tuberia",
                            font=("Helvetica", 20, "bold"))
        tipo_tuberia.place(x=300, y=625)

        self.tuberia = ttk.Combobox(self.cuadro_facilidades,
                                    values=["","Lisa" , "Rugosa"],  # Lista de opciones
                                    state="readonly",  # Evita que el usuario escriba
                                    font=("Arial", 12),
                                    width=8)
        self.tuberia.place(x=500, y=625)

        #Imprimir los resultados en el cuadro de la derecha----------------------------------------------------------


        tabla_resultados =  Frame(self.cuadro_facilidades, bg = "white")
        tabla_resultados.place(x=800, y=65 , width= 426 , height= 610)


        dato_velocidad = Label(tabla_resultados, 
        text= "Velocidad", 
        bg="white", 
        fg="black", 
        borderwidth=3, 
        relief="solid", 
        font=("Arial", 15), width=20)
        dato_velocidad.grid(row= 0 , column= 0  ,ipadx= 20,ipady= 10)
        self.Velocidad_Calculada = Label(
            tabla_resultados, 
            text= "", 
            bg="white", 
            fg="black", 
            borderwidth=3, 
            relief="solid", 
            font=("Arial", 15), 
            width=10)
        self.Velocidad_Calculada.grid(row= 0 , column= 1  ,ipadx= 20,ipady= 10)



        dato_area = Label(
            tabla_resultados,
                        text= "Area", 
                        bg="white",
                        fg="black", 
                        borderwidth=3,
                        relief="solid",
                        font=("Arial", 15),
                        width=20)
        dato_area.grid(row= 1 , column= 0  ,ipadx= 20,ipady= 10)

        self.Area_Calculada = Label(
            tabla_resultados, 
        text= "", 
        bg="white", 
        fg="black",
        borderwidth=3, 
        relief="solid", 
        font=("Arial", 15), 
        width=10)
        self.Area_Calculada.grid(row= 1 , column= 1  ,ipadx= 20,ipady= 10)


        dato_caudal = Label(
            tabla_resultados, 
        text= "Caudal",
        bg="white",
        fg="black",
        borderwidth=3,
        relief="solid",
        font=("Arial", 15),
        width=20)
        dato_caudal.grid(row= 2 , column= 0  ,ipadx= 20,ipady= 10)

        self.Caudal_Calculada = Label(
            tabla_resultados,
        text= "", 
        bg="white",
        fg="black", borderwidth=3, 
        relief="solid", 
        font=("Arial", 15),
        width=10)
        self.Caudal_Calculada.grid(row= 2 , column= 1  ,ipadx= 20,ipady= 10)


        dato_reynolds = Label(
            tabla_resultados,
        text= "Numero Reynolds",
        bg="white", 
        fg="black", 
        borderwidth=3, 
        relief="solid", 
        font=("Arial", 15),
        width=20)
        dato_reynolds.grid(row= 3 , column= 0  ,ipadx= 20,ipady= 10)

        self.Reynolds_Calculada = Label(
            tabla_resultados, 
        text= "", 
        bg="white",
        fg="black",
        borderwidth=3, 
        relief="solid", font=("Arial", 15),
        width=10)
        self.Reynolds_Calculada.grid(row= 3 , column= 1  ,ipadx= 20,ipady= 10)

        
        dato_condicion = Label(
            tabla_resultados,
        text= "Tipo Flujo",
        bg="white", 
        fg="black",
        borderwidth=3,
        relief="solid",
        font=("Arial", 15),
        width=20)
        dato_condicion.grid(row= 4 , column= 0  ,ipadx= 20,ipady= 10)

        self.condicion_de_flujo = Label(
            tabla_resultados,
        text= "", 
        bg="white",
        fg="black",
        borderwidth=3,
        relief="solid",
        font=("Arial", 15),
        width=10)
        self.condicion_de_flujo.grid(row= 4 , column= 1  ,ipadx= 20,ipady= 10)

        dato_tuberia = Label(
            tabla_resultados,
        text= "Tipo Tuberia",
        bg="white", 
        fg="black", 
        borderwidth=3,
        relief="solid",
        font=("Arial", 15),
        width=20)
        dato_tuberia.grid(row= 5 , column= 0  ,ipadx= 20,ipady= 10)

        self.tuberia_eleccion = Label(
            tabla_resultados,
        text= "",
        bg="white",
        fg="black",
        borderwidth=3,
        relief="solid",
        font=("Arial", 15),
        width=10)
        self.tuberia_eleccion.grid(row= 5 , column= 1  ,ipadx= 20,ipady= 10)

        friccion_laminar= Label(
            tabla_resultados,
        text= "Friccion Lisa",
        bg="white", 
        fg="black", 
        borderwidth=3, 
        relief="solid", 
        font=("Arial", 15), 
        width=20)
        friccion_laminar.grid(row= 6 , column= 0  ,ipadx= 20,ipady= 10)

        self.calculo_laminar = Label(
            tabla_resultados, 
        text= "", 
        bg="white",
        fg="black",
        borderwidth=3,
        relief="solid", 
        font=("Arial", 15),
        width=10)
        self.calculo_laminar.grid(row= 6 , column= 1  ,ipadx= 20,ipady= 10)


        friccion_turbulento= Label(
            tabla_resultados, 
        text= "Friccion Rugosa", 
        bg="white", 
        fg="black",
        borderwidth=3, 
        relief="solid", 
        font=("Arial", 15),
        width=20)
        friccion_turbulento.grid(row= 7 , column= 0  ,ipadx= 20,ipady= 10)
        self.calculo_turbulento= Label(
            tabla_resultados, 
        text= "", 
        bg="white",
        fg="black",
        borderwidth=3, 
        relief="solid",
        font=("Arial", 15),
        width=10)
        self.calculo_turbulento.grid(row= 7 , column= 1  ,ipadx= 20,ipady= 10)

        friccion_turbulento= Label(
            tabla_resultados,
        text= "Iteraciones",
        bg="white", 
        fg="black",
        borderwidth=3, 
        relief="solid",
        font=("Arial", 15),
        width=20)
        friccion_turbulento.grid(row= 8 , column= 0  ,ipadx= 20,ipady= 10)

        self.calculo_iteraciones= Label(
            tabla_resultados,
        text= "",
        bg="white", 
        fg="black", 
        borderwidth=3,
        relief="solid",
        font=("Arial", 15), 
        width=10)
        self.calculo_iteraciones.grid(row= 8 , column= 1  ,ipadx= 20,ipady= 10)

        friccion_turbulento= Label(
            tabla_resultados, 
        text= "Newton Rapshon",
        bg="white", 
        fg="black", 
        borderwidth=3, 
        relief="solid",
        font=("Arial", 15),
        width=20)
        friccion_turbulento.grid(row= 9 , column= 0  ,ipadx= 20,ipady= 10)

        self.calculo_newton= Label(
            tabla_resultados, 
        text= "",
        bg="white",
        fg="black", 
        borderwidth=3,
        relief="solid",
        font=("Arial", 15),
        width=10)
        self.calculo_newton.grid(row= 9 , column= 1  ,ipadx= 20,ipady= 10)


        potencia= Label(
            tabla_resultados, 
        text= "Potencia",
        bg="white", 
        fg="black", 
        borderwidth=3, 
        relief="solid",
        font=("Arial", 15),
        width=20)
        potencia.grid(row= 10 , column= 0  ,ipadx= 20,ipady= 10)

        self.calculo_potencia= Label(
            tabla_resultados,
        text= "",
        bg="white",
        fg="black",
        borderwidth=3,
        relief="solid", 
        font=("Arial", 15),
        width=10)
        self.calculo_potencia.grid(row= 10 , column= 1  ,ipadx= 20,ipady= 10)

        diametro_requerido= Label(
            tabla_resultados,
        text= "Diametro Requerido", 
        bg="white", 
        fg="black", 
        borderwidth=3, 
        relief="solid", 
        font=("Arial", 15),
        width=20)
        diametro_requerido.grid(row= 11 , column= 0  ,ipadx= 20,ipady= 10)
        
        self.diametro_calculado_requerido= Label(
            tabla_resultados,
        text= "",
        bg="white", 
        fg="black",
        borderwidth=3,
        relief="solid", 
        font=("Arial", 15),
        width=10)
        self.diametro_calculado_requerido.grid(row= 11 , column= 1  ,ipadx= 20,ipady= 10)


        # Entradas de datos
        gravedad =  self.dato_gravedad.get()
        diametro = self.dato_diametro.get()
        Longitud = self.dato_L.get()
        rugosidad = self.dato_e.get()
        Datum = self.dato_H.get()
        Km = self.dato_km.get()
        densidad = self.dato_densidad.get()
        altura_final = self.dato_altura_z2.get()
        viscosidad_dinamica =  self.dato_viscosidad_dinamica.get()
        cinematica = self.dato_viscosidad_cinematica.get()
        precision =  self.dato_precision.get()
        tuberia = self.tuberia.get()
        
        self.tuberia.bind("<<ComboboxSelected>>",  self.calculo_facilidades)

    def calculo_facilidades(self, event):
        
        try:

            # Entradas de datos
            gravedad =  self.dato_gravedad.get()
            diametro = self.dato_diametro.get()
            Longitud = self.dato_L.get()
            rugosidad = self.dato_e.get()
            Datum = self.dato_H.get()
            Km = self.dato_km.get()
            densidad = self.dato_densidad.get()
            altura_final = self.dato_altura_z2.get()
            viscosidad_dinamica =  self.dato_viscosidad_dinamica.get()
            cinematica = self.dato_viscosidad_cinematica.get()
            precision =  self.dato_precision.get()
            tuberia = self.tuberia.get()

            if densidad !=""  and viscosidad_dinamica !="":
                densidad = float(densidad)
                viscosidad_dinamica = float(viscosidad_dinamica)
                cinematica = viscosidad_dinamica / densidad

            elif cinematica != "" and densidad !="":
                cinematica = float(cinematica)
                densidad = float(densidad)
                viscosidad_dinamica = cinematica * densidad

            elif cinematica != "" and viscosidad_dinamica !="":
                cinematica = float(cinematica)
                viscosidad_dinamica = float(viscosidad_dinamica)
                densidad = viscosidad_dinamica / cinematica

            if gravedad !="" and  diametro !="" and  Longitud !="" and rugosidad !="" and Datum !="" and Km  !=""  and altura_final !=""   and precision!=""  and  tuberia!="" and cinematica != "" and viscosidad_dinamica != "" and densidad != "": 

                gravedad =   float(gravedad)
                diametro =  float(diametro)
                Longitud =  float(Longitud)
                rugosidad = float(rugosidad)
                Datum = float(Datum)
                KM =  float(Km)
                densidad =  float(densidad)
                altura_final =  float(altura_final)
                viscosidad_dinamica =  float(viscosidad_dinamica)
                precision = float(precision)
                tuberia =  str(tuberia)
                vc = cinematica

                def primer_bucle():
                    Hl = abs(Datum - altura_final)
                    Hl_i = 0
                    iteraciones= 0
                    prueba = 1000000000000000000000000000

                    while iteraciones < prueba:
                        #ECUACION 3
                        VELOCIDAD = (-2*((2*gravedad*diametro*Hl/Longitud)**0.5)) * log10( (rugosidad/(3.7*diametro))  + ((2.51*vc*(Longitud**0.5))/(diametro*((2*gravedad*diametro*Hl)**0.5)))  )
                        #ECUACION 10
                        Hl_calculado = Datum - altura_final - (KM*VELOCIDAD*VELOCIDAD/(2*gravedad))

                        if abs(Hl_calculado - Hl_i) <= precision:
                            AREA_TUBERIA = pi *((diametro/2)**2)
                            CAUDAL = VELOCIDAD * ( AREA_TUBERIA)
                            prueba = -1 * prueba
                            self.Area_Calculada.config(text=f"{round(AREA_TUBERIA,5)} m2") 
                            self.Caudal_Calculada.config(text=f"{round(CAUDAL,5)} m3/s") 
                            self.Velocidad_Calculada.config(text=f"{round(VELOCIDAD,5)} m/s")
                            resultados = (VELOCIDAD, CAUDAL)
                            return resultados
                        else:
                            Hl = Hl_calculado
                            Hl_i = Hl_calculado
                            iteraciones = iteraciones+1

                def calculo_reynolds():
                    respuestas = primer_bucle()
                    VELOCIDAD = respuestas[0]
                    CAUDAL = respuestas[1]
                    #primero nesesitamos el numero de reynolds para saber en que tipo de flujo estamos - laminar y turbulento
                    NUMERO_REYNOLDS = (VELOCIDAD*diametro)/(cinematica)
                    self.Reynolds_Calculada.config(text=f"{round(NUMERO_REYNOLDS,2)}")

                    def metodo_iteraciones(friccion_tuberia_lisa):
                        fr_bucle = friccion_tuberia_lisa
                        fr_inicio = 0
                        while True:
                            friccion_calculada = (1/(1.74-2*log10( ((2*rugosidad/diametro) + (18.7 / (NUMERO_REYNOLDS * ((fr_bucle) ** 0.5)))))))**2
                            friccion_calculada = float(round(friccion_calculada,6))

                            if friccion_calculada == fr_inicio:
                                return friccion_calculada
                            else:
                                fr_bucle = friccion_calculada
                                fr_inicio = friccion_calculada

                    def metodo_newton_rapshon(friccion_tuberia_lisa):
                        factor_inicio = 0
                        factor_lisa = friccion_tuberia_lisa
                        factor_lisa = float(round(factor_lisa, 7))
                        while True: 
                            
                            funcion_original = -2 * log10( (rugosidad/ (diametro*3.7))   +  ((2.51 * factor_lisa) / (NUMERO_REYNOLDS * (float(factor_lisa)**0.5)))  )
                            derivada_funcion =  (-2/log(10)) * ( (2.51/NUMERO_REYNOLDS) / ( (rugosidad/ (diametro*3.7))   +  ((2.51 * factor_lisa) / (NUMERO_REYNOLDS)))       )
                            Xi_1 = factor_lisa - ((funcion_original-factor_lisa)/(derivada_funcion-1))
                            Xi_1 = round(Xi_1, 7)
                            if Xi_1 == factor_inicio:
                                newton_calculado = 1/ (Xi_1 *Xi_1)
                                newton_calculado = round(newton_calculado,3)
                                return newton_calculado
                            else:
                                factor_lisa = Xi_1
                                factor_inicio = Xi_1

                    def calculo_diametro():

                        boleano = True
                        diametro_comercial = diametro/10
                        HL = abs(Datum - altura_final)
                        PERDIDA_INICIAL = 0

                        while boleano == True:
                            
                            VELOCIDAD_2 = (-2 * ((2 * gravedad * diametro_comercial * HL / Longitud) ** 0.5)) * log10((rugosidad / (3.7 * diametro_comercial)) + ((2.51 * cinematica * (Longitud ** 0.5)) / (diametro_comercial * ((2 * gravedad * diametro_comercial * HL) ** 0.5))))
                            AREA_2 = pi * ((diametro_comercial / 2) ** 2)
                            CAUDAL_2 = VELOCIDAD_2 * AREA_2
                            
                            CAUDALxDIAMETRO = CAUDAL * diametro
                            CAUDALxDIAMETRO=  round(CAUDALxDIAMETRO, 3)
                            CAUDAL_2 = round(CAUDAL_2, 3)

                            if CAUDAL_2 >= CAUDALxDIAMETRO:
                                
                                HL_calculada_2 = Datum - altura_final - ((KM * VELOCIDAD_2 ** 2) / (2 * gravedad))
                                E = HL_calculada_2 - PERDIDA_INICIAL
                                
                                if E <= precision:

                                    CAUDAL_2 = round(CAUDAL_2, 3)
                                    if CAUDAL_2 >= CAUDALxDIAMETRO:
                                        boleano = False
                                        diametro_comercial = round(diametro_comercial,5)
                                        return diametro_comercial

                                    else:
                                        HL = abs(Datum - altura_final)  # Actualizar HL2
                                        diametro_comercial = diametro + (diametro-diametro_comercial)
                                    
                                else:
                                    PERDIDA_INICIAL = HL_calculada_2
                                    HL = HL_calculada_2
                            
                            
                            else:
                                diametro_comercial = diametro + (diametro-diametro_comercial)
                                HL = abs(Datum - altura_final)  # Actualizar HL2

                    #flujo laminar
                    if NUMERO_REYNOLDS <= 2000:
                        NUMERO_REYNOLDS = round(NUMERO_REYNOLDS, 2)
                        fr = 64/NUMERO_REYNOLDS #factor de friccion
                        fr = round(fr, 2)

                        #SUMA DE Z2 + Hl + Hm
                        H_calculada = altura_final + (fr * (Longitud/diametro) * ((VELOCIDAD * VELOCIDAD)/ (2 * gravedad))) + (KM*((VELOCIDAD * VELOCIDAD)/ (2 * gravedad)))
                        Potencia = densidad * gravedad * CAUDAL * H_calculada
                        Potencia = round(Potencia,6)
                        self.Reynolds_Calculada.config(text=f"{NUMERO_REYNOLDS}")
                        
                        self.condicion_de_flujo.config(text="Flujo Laminar")
                        self.tuberia_eleccion.config(text=f"{str(tuberia)}")
                        self.calculo_laminar.config(text=f"{fr}")
                        self.calculo_turbulento.config(text=f"{fr}")
                        self.calculo_iteraciones.config(text=f"")
                        self.calculo_newton.config(text=f"")
                        self.calculo_potencia.config(text=f"{Potencia}")
                        diametro_requerido = calculo_diametro()
                        self.diametro_calculado_requerido.config(text=f"{diametro_requerido}")
                    #no cumple para laminar o turbulento
                    if 2000 < NUMERO_REYNOLDS < 4000:
                        self.condicion_de_flujo.config(text="No cumple")
                        self.tuberia_eleccion.config(text=f"{tuberia}")
                        self.tuberia_eleccion.config(text=f"{tuberia}")
                        self.calculo_potencia.config(text=f"")
                    #flujo turbulento
                    
                    if  4000<=   NUMERO_REYNOLDS:
                        
                        self.condicion_de_flujo.config(text="Flujo Turbulento")
                        if str(tuberia) == "Lisa":
                            friccion_tuberia_lisa = 0.25/(((log10( (rugosidad/(3.7*diametro)) + (5.74/(NUMERO_REYNOLDS**0.9)))))**2) #factor de friccion liso
                            fr = friccion_tuberia_lisa
                            H_calculada = altura_final + (fr * (Longitud/diametro) * ((VELOCIDAD * VELOCIDAD)/ (2 * gravedad))) + (KM*((VELOCIDAD * VELOCIDAD)/ (2 * gravedad)))
                            Potencia = densidad * gravedad * CAUDAL * H_calculada
                            Potencia = round(Potencia,6)
                            self.calculo_potencia.config(text=f"{Potencia}")
                            self.calculo_laminar.config(text=f"{round(friccion_tuberia_lisa,3)}")
                            self.calculo_turbulento.config(text=f"")
                            self.calculo_iteraciones.config(text="")
                            self.calculo_newton.config(text="")
                            diametro_requerido = calculo_diametro()
                            self.diametro_calculado_requerido.config(text=f"{diametro_requerido}")

                        if str(tuberia) == "Rugosa":
                            friccion_tuberia_lisa = 0.25/(((log10( (rugosidad/(3.7*diametro)) + (5.74/(NUMERO_REYNOLDS**0.9)))))**2) #factor de friccion liso
                            self.calculo_laminar.config(text=f"")
                            self.calculo_turbulento.config(text="")
                            fr_iterciones = metodo_iteraciones(friccion_tuberia_lisa)
                            fr_newton_rapshon = metodo_newton_rapshon(friccion_tuberia_lisa)
                            fr = fr_newton_rapshon
                            H_calculada = altura_final + (fr * (Longitud/diametro) * ((VELOCIDAD * VELOCIDAD)/ (2 * gravedad))) + (KM*((VELOCIDAD * VELOCIDAD)/ (2 * gravedad)))
                            Potencia = densidad * gravedad * CAUDAL * H_calculada
                            Potencia = round(Potencia,6)
                            self.calculo_potencia.config(text=f"{Potencia}")
                            self.calculo_iteraciones.config(text=f"{fr_iterciones}")
                            self.calculo_newton.config(text=f"{fr_newton_rapshon}")
                            diametro_requerido = calculo_diametro()
                            self.diametro_calculado_requerido.config(text=f"{diametro_requerido}")


                        self.tuberia_eleccion.config(text=f"{str(tuberia)}")
                
                calculo_reynolds()       

        except ValueError:

            self.Velocidad_Calculada.config(text="")
            self.Area_Calculada.config(text="")
            self.Caudal_Calculada.config(text="")
            self.Reynolds_Calculada.config(text="")
            self.condicion_de_flujo.config(text="")
            self.tuberia_eleccion.config(text="")
            self.calculo_laminar.config(text="")
            self.calculo_turbulento.config(text="")
            self.calculo_iteraciones.config(text="")
            self.calculo_newton.config(text="")
            self.calculo_potencia.config(text="")
            self.diametro_calculado_requerido.config(text="")


proyecto = Miproyecto()




   

