import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import subprocess, threading, time, os, json, re
import sys

# =========================
# CONFIGURACIÓN
# =========================
COLOR_FONDO = "#1e1e1e"
COLOR_TEXTO = "#ffffff"
COLOR_ACENTO = "#9b59b6"  # morado

CARPETA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
FLASHGBX = r"C:\Users\mrmur\AppData\Local\Programs\FlashGBX\FlashGBX-app.exe"
MGBA = r"C:\Program Files\mGBA\mGBA.exe"
CARPETA_PORTADAS = os.path.join(CARPETA_SCRIPT, "PORTADAS")
LOGO_PATH = os.path.join(CARPETA_SCRIPT, "logo.png")

ROM_PATH = os.path.join(CARPETA_SCRIPT, "cartucho.gb")
SAV_PATH = os.path.join(CARPETA_SCRIPT, "cartucho.sav")

# =========================
# FUNCIONES
# =========================
def centrar_ventana(ventana):
    """Centra cualquier ventana en la pantalla"""
    ventana.update_idletasks()
    ancho = ventana.winfo_width()
    alto = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
    y = (ventana.winfo_screenheight() // 2) - (alto // 2)
    ventana.geometry(f"+{x}+{y}")

def mostrar_manual_usuario():
    """Muestra ventana de selección de idioma para el manual"""
    def seleccionar_idioma(idioma):
        ventana_idioma.destroy()
        mostrar_instrucciones(idioma)
    
    ventana_idioma = tk.Toplevel()
    ventana_idioma.title("GB Player - Seleccionar Idioma")
    ventana_idioma.configure(bg=COLOR_FONDO)
    ventana_idioma.geometry("400x250")
    ventana_idioma.resizable(False, False)
    
    # Centrar ventana
    centrar_ventana(ventana_idioma)
    
    ventana_idioma.transient()
    ventana_idioma.grab_set()
    
    frame_principal = tk.Frame(ventana_idioma, bg=COLOR_FONDO)
    frame_principal.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    # Título
    lbl_titulo = tk.Label(frame_principal, text="SELECCIONA IDIOMA", 
                         font=("Arial", 16, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO)
    lbl_titulo.pack(pady=(0, 30))
    
    # Botón Español - MISMO COLOR QUE LOS DEMÁS
    btn_espanol = tk.Button(frame_principal, text="ESPAÑOL", 
                           command=lambda: seleccionar_idioma("es"),
                           bg=COLOR_ACENTO, fg="white", 
                           font=("Arial", 12, "bold"),
                           relief="flat", padx=20, pady=12,
                           width=15)
    btn_espanol.pack(pady=10)
    
    # Botón English - MISMO COLOR QUE LOS DEMÁS
    btn_english = tk.Button(frame_principal, text="ENGLISH", 
                           command=lambda: seleccionar_idioma("en"),
                           bg=COLOR_ACENTO, fg="white", 
                           font=("Arial", 12, "bold"),
                           relief="flat", padx=20, pady=12,
                           width=15)
    btn_english.pack(pady=10)
    
    # Centrar nuevamente después de crear los widgets
    ventana_idioma.after(100, lambda: centrar_ventana(ventana_idioma))

def mostrar_instrucciones(idioma):
    """Muestra las instrucciones según el idioma seleccionado"""
    # Textos en español
    textos_es = {
        "titulo": "MANUAL DE USUARIO - INSTRUCCIONES",
        "instrucciones": [
            "1. Asegúrate de que tu cartucho esté limpio y bien conectado",
            "2. Algunos cartuchos bootleg de Pokémon o sin batería pueden no funcionar correctamente",
            "3. NO desconectes el cartucho hasta que todas las ventanas se hayan cerrado",
            "4. Tu partida guardada se restaurará automáticamente al cerrar mGBA",
            "5. Algunos juegos homebrew pueden no mostrar portada pero funcionarán correctamente",
            "6. Mantén el cartucho insertado durante todo el proceso",
            "7. ¡Feliz gaming! 🎮"
        ]
    }
    
    # Textos en inglés
    textos_en = {
        "titulo": "USER MANUAL - INSTRUCTIONS", 
        "instrucciones": [
            "1. Ensure your cartridge is clean and properly connected",
            "2. Some Pokémon bootleg or battery-less cartridges may not work properly",
            "3. DO NOT disconnect the cartridge until all windows have closed",
            "4. Your saved game will be automatically restored when closing mGBA",
            "5. Some homebrew games may not show cover art but will work correctly",
            "6. Keep the cartridge inserted throughout the entire process",
            "7. Happy gaming! 🎮"
        ]
    }
    
    textos = textos_es if idioma == "es" else textos_en
    
    ventana_instrucciones = tk.Toplevel()
    ventana_instrucciones.title("GB Player - Manual")
    ventana_instrucciones.configure(bg=COLOR_FONDO)
    ventana_instrucciones.geometry("700x450")
    ventana_instrucciones.resizable(False, False)
    
    # Centrar ventana
    centrar_ventana(ventana_instrucciones)
    
    ventana_instrucciones.transient()
    ventana_instrucciones.grab_set()
    
    frame_principal = tk.Frame(ventana_instrucciones, bg=COLOR_FONDO)
    frame_principal.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
    
    # Título
    lbl_titulo = tk.Label(frame_principal, text=textos["titulo"],
                         font=("Arial", 16, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO)
    lbl_titulo.pack(pady=(0, 25))
    
    # Frame para instrucciones con scroll
    frame_scroll = tk.Frame(frame_principal, bg=COLOR_FONDO)
    frame_scroll.pack(fill=tk.BOTH, expand=True)
    
    canvas = tk.Canvas(frame_scroll, bg=COLOR_FONDO, highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=COLOR_FONDO)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Instrucciones
    for i, instruccion in enumerate(textos["instrucciones"]):
        frame_inst = tk.Frame(scrollable_frame, bg=COLOR_FONDO)
        frame_inst.pack(fill=tk.X, pady=8, padx=10)
        
        # Número
        lbl_num = tk.Label(frame_inst, text=str(i+1), font=("Arial", 12, "bold"),
                          bg=COLOR_ACENTO, fg="white", width=3, height=1)
        lbl_num.pack(side=tk.LEFT, padx=(0, 15))
        
        # Texto de la instrucción
        lbl_texto = tk.Label(frame_inst, text=instruccion, font=("Arial", 11),
                            bg=COLOR_FONDO, fg=COLOR_TEXTO, justify=tk.LEFT, anchor="w")
        lbl_texto.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Botón Cerrar
    btn_cerrar = tk.Button(frame_principal, text="CERRAR", 
                          command=ventana_instrucciones.destroy,
                          bg=COLOR_ACENTO, fg="white", 
                          font=("Arial", 12, "bold"),
                          relief="flat", padx=30, pady=10)
    btn_cerrar.pack(pady=20)
    
    # Centrar nuevamente después de crear los widgets
    ventana_instrucciones.after(100, lambda: centrar_ventana(ventana_instrucciones))

def mostrar_advertencia_inicial():
    """Muestra ventana de advertencia antes de iniciar el proceso"""
    root_advertencia = tk.Tk()
    root_advertencia.title("GB Player Launcher - Información")
    root_advertencia.configure(bg=COLOR_FONDO)
    root_advertencia.geometry("600x350")
    root_advertencia.resizable(False, False)
    
    # Centrar ventana
    centrar_ventana(root_advertencia)
    
    # Frame principal
    frame_principal = tk.Frame(root_advertencia, bg=COLOR_FONDO)
    frame_principal.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    # Icono de advertencia
    lbl_icono = tk.Label(frame_principal, text="⚠️", font=("Arial", 32), 
                         bg=COLOR_FONDO, fg="#f39c12")
    lbl_icono.pack(pady=(0, 20))
    
    # Mensaje principal
    lbl_mensaje = tk.Label(frame_principal, 
                          text="ALGUNOS TÍTULOS NO TENDRÁN PORTADA\nPERO SERÁN JUGABLES",
                          font=("Arial", 14, "bold"),
                          bg=COLOR_FONDO, fg=COLOR_TEXTO,
                          justify=tk.CENTER)
    lbl_mensaje.pack(pady=(0, 15))
    
    # Mensaje adicional
    lbl_info = tk.Label(frame_principal, 
                       text="El juego funcionará correctamente incluso si no se muestra portada.",
                       font=("Arial", 11),
                       bg=COLOR_FONDO, fg=COLOR_TEXTO,
                       justify=tk.CENTER)
    lbl_info.pack(pady=(0, 25))
    
    # Botón Manual de Usuario - MISMO COLOR QUE LOS DEMÁS
    btn_manual = tk.Button(frame_principal, text="MANUAL DE USUARIO", 
                          command=mostrar_manual_usuario,
                          bg=COLOR_ACENTO, fg="white", 
                          font=("Arial", 11, "bold"),
                          relief="flat", padx=20, pady=10)
    btn_manual.pack(pady=(0, 10))
    
    # Botón Aceptar
    btn_aceptar = tk.Button(frame_principal, text="ACEPTAR", 
                           command=root_advertencia.destroy,
                           bg=COLOR_ACENTO, fg="white", 
                           font=("Arial", 12, "bold"),
                           relief="flat", padx=30, pady=12)
    btn_aceptar.pack()
    
    # Hacer que la ventana sea modal
    root_advertencia.transient()
    root_advertencia.grab_set()
    
    # Centrar nuevamente después de crear los widgets
    root_advertencia.after(100, lambda: centrar_ventana(root_advertencia))
    
    root_advertencia.mainloop()

def limpiar_archivos():
    """Eliminar ROM y SAVE generados."""
    for archivo in [ROM_PATH, SAV_PATH]:
        if os.path.exists(archivo):
            os.remove(archivo)

def buscar_nombre_en_json(game_title):
    json_path = os.path.join(CARPETA_SCRIPT, "juegos.json")
    if not os.path.exists(json_path):
        print(f"❌ Archivo juegos.json no encontrado en: {json_path}")
        return game_title, game_title  # Retorna ambos: (nombre_bonito, nombre_para_portada)
    
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            juegos = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Error leyendo juegos.json: {e}")
            return game_title, game_title
    
    print(f"🔍 Buscando título: '{game_title}' en juegos.json")
    
    # DIAGNÓSTICO: Mostrar qué estamos buscando exactamente
    print(f"🎯 Búsqueda exacta para: '{game_title.strip()}'")
    
    # Buscar coincidencia exacta primero (case sensitive)
    for juego in juegos:
        titulo_json = juego.get("title", "").strip()
        if titulo_json == game_title.strip():
            nombre_encontrado = juego.get("name", game_title)
            print(f"✅ Coincidencia exacta encontrada:")
            print(f"   Título FlashGBX: '{game_title}'")
            print(f"   Título JSON: '{titulo_json}'") 
            print(f"   Nombre bonito: '{nombre_encontrado}'")
            return nombre_encontrado, nombre_encontrado
    
    # Si no encuentra coincidencia exacta, buscar case insensitive
    for juego in juegos:
        titulo_json = juego.get("title", "").strip().lower()
        if titulo_json == game_title.strip().lower():
            nombre_encontrado = juego.get("name", game_title)
            print(f"✅ Coincidencia (case-insensitive) encontrada: {nombre_encontrado}")
            return nombre_encontrado, nombre_encontrado
    
    print("❌ No se encontró coincidencia en juegos.json")
    print(f"📝 Usando título original: '{game_title}'")
    return game_title, game_title

def buscar_portada(nombre_mostrado):
    """Busca la portada del juego. Si no se encuentra, usa NO GAME IN DATABASE.png"""
    
    # Primero buscar imagen exacta
    ruta_exacta = os.path.join(CARPETA_PORTADAS, f"{nombre_mostrado}.png")
    if os.path.exists(ruta_exacta):
        print(f"🖼️  Portada encontrada (exacta): {ruta_exacta}")
        return ruta_exacta
    
    # Buscar coincidencia parcial (solo si no hay coincidencia exacta)
    base_name = re.sub(r"\(.*?\)", "", nombre_mostrado).strip().lower()
    for archivo in os.listdir(CARPETA_PORTADAS):
        if archivo.lower().endswith(".png"):
            nombre_archivo_sin_extension = os.path.splitext(archivo)[0]
            nombre_archivo_limpio = re.sub(r"\(.*?\)", "", nombre_archivo_sin_extension.lower()).strip()
            
            # Coincidencia más estricta - el nombre base debe ser igual
            if base_name == nombre_archivo_limpio:
                ruta_encontrada = os.path.join(CARPETA_PORTADAS, archivo)
                print(f"🖼️  Portada encontrada (parcial estricta): {ruta_encontrada}")
                return ruta_encontrada
    
    # Si no se encuentra ninguna portada, usar "NO GAME IN DATABASE.png"
    ruta_no_game = os.path.join(CARPETA_PORTADAS, "NO GAME IN DATABASE.png")
    if os.path.exists(ruta_no_game):
        print(f"🔍 No se encontró portada para '{nombre_mostrado}'. Usando: NO GAME IN DATABASE.png")
        return ruta_no_game
    else:
        print(f"⚠️  No se encontró portada y NO GAME IN DATABASE.png no existe. Usando portada por defecto.")
        return os.path.join(CARPETA_SCRIPT, "portada.png")

def actualizar_progreso(porcentaje, estado, detalle=""):
    barra_progreso['value'] = porcentaje
    lbl_estado.config(text=estado)
    lbl_detalle.config(text=detalle)
    barra_inferior['value'] = porcentaje
    lbl_estado_inferior.config(text=estado)
    ventana.update_idletasks()

def verificar_cartucho():
    """Verifica si hay cartucho - retorna False o el título del juego"""
    try:
        MODE = "dmg"
        
        print("=== 🔍 INICIANDO VERIFICACIÓN DE CARTUCHO ===")
        print(f"📁 Carpeta de trabajo: {CARPETA_SCRIPT}")
        print(f"🛠️  Ejecutando: {FLASHGBX}")
        
        # Ejecutar con CREATE_NO_WINDOW para ocultar la ventana de comandos
        resultado = subprocess.run(
            [FLASHGBX, "--cli", "--mode", MODE, "--action", "info"],
            capture_output=True, text=True, timeout=30,
            cwd=CARPETA_SCRIPT,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        print(f"📊 Return code: {resultado.returncode}")
        print("=== 📋 SALIDA COMPLETA DE FLASHGBX ===")
        print(resultado.stdout)
        print("=======================================")
        
        if resultado.stderr:
            print("=== ⚠️  ERRORES ===")
            print(resultado.stderr)
            print("===================")

        if resultado.returncode != 0:
            print("❌ FlashGBX retornó código de error")
            return False, "❌ No se detectó cartucho o está mal conectado."

        # Buscar el título del juego de múltiples formas
        game_title_detectado = "Juego Desconocido"
        not_in_database = False
        
        for linea in resultado.stdout.splitlines():
            linea = linea.strip()
            print(f"📝 Analizando línea: {linea}")
            
            # Verificar si FlashGBX reporta "Not in database"
            if "(Not in database)" in linea:
                print("🔍 FlashGBX reporta: (Not in database)")
                not_in_database = True
            
            if "Game Title:" in linea:
                game_title_detectado = linea.split("Game Title:")[1].strip()
                break
            elif "Title:" in linea:
                game_title_detectado = linea.split("Title:")[1].strip()
                break
            elif "Name:" in linea:
                game_title_detectado = linea.split("Name:")[1].strip()
                break

        if not game_title_detectado or game_title_detectado == "Juego Desconocido":
            print("❌ No se pudo encontrar el título en la salida")
            # Mostrar más líneas para debug
            print("=== 🔍 PRIMERAS 15 LÍNEAS PARA DEBUG ===")
            for i, linea in enumerate(resultado.stdout.splitlines()[:15]):
                print(f"Línea {i}: {linea}")
            return False, "❌ No se pudo leer el título del juego."

        print(f"✅ Título detectado: '{game_title_detectado}'")
        print(f"📊 Estado de base de datos: {'NO EN BASE DE DATOS' if not_in_database else 'EN BASE DE DATOS'}")

        # Si FlashGBX reporta "Not in database", forzar el uso de NO GAME IN DATABASE.png
        if not_in_database:
            return True, (game_title_detectado, True)  # True = not in database
        else:
            return True, (game_title_detectado, False)  # False = está en database

    except subprocess.TimeoutExpired:
        print("❌ Timeout: FlashGBX tardó demasiado en responder")
        return False, "❌ Timeout: El cartucho no respondió a tiempo."
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {e}")
        return False, f"❌ Ocurrió un error verificando el cartucho:\n{e}"

def proceso_juego(datos_cartucho):
    """Proceso principal que se ejecuta solo si hay cartucho válido"""
    try:
        MODE = "dmg"
        
        game_title_detectado, not_in_database = datos_cartucho
        
        print(f"🎮 Iniciando proceso para: {game_title_detectado}")
        print(f"📊 Estado base datos FlashGBX: {'NO EN DB' if not_in_database else 'EN DB'}")
        
        # Actualizar interfaz con información del juego
        nombre_mostrado, nombre_para_portada = buscar_nombre_en_json(game_title_detectado)
        
        print(f"🏷️  Nombre a mostrar: '{nombre_mostrado}'")
        print(f"🖼️  Nombre para portada: '{nombre_para_portada}'")
        
        # MOSTRAR EL NOMBRE BONITO EN LA INTERFAZ
        lbl_nombre_juego.config(text=nombre_mostrado)

        # Si FlashGBX reporta "Not in database", usar directamente NO GAME IN DATABASE.png
        if not_in_database:
            ruta_no_game = os.path.join(CARPETA_PORTADAS, "NO GAME IN DATABASE.png")
            if os.path.exists(ruta_no_game):
                print(f"🔍 Juego reportado como 'Not in database'. Usando: NO GAME IN DATABASE.png")
                ruta_portada = ruta_no_game
            else:
                print(f"⚠️  NO GAME IN DATABASE.png no existe. Usando portada por defecto.")
                ruta_portada = os.path.join(CARPETA_SCRIPT, "portada.png")
        else:
            # Buscar portada usando el NOMBRE PARA PORTADA (que es el mismo que el nombre mostrado)
            ruta_portada = buscar_portada(nombre_para_portada)

        try:
            img = Image.open(ruta_portada).resize((200, 200))
            print(f"🖼️  Portada cargada: {ruta_portada}")
        except Exception as e:
            print(f"❌ Error cargando portada: {e}")
            img = Image.new("RGB", (200, 200), color="#555555")
            print("⚠️  No se pudo cargar la portada, usando imagen por defecto")
        portada_img = ImageTk.PhotoImage(img)
        lbl_portada.config(image=portada_img)
        lbl_portada.image = portada_img

        # Actualizar logo GameBoy Color - 50% MÁS PEQUEÑO
        if os.path.exists(LOGO_PATH):
            logo_img = Image.open(LOGO_PATH)
            largo_barra = barra_progreso.winfo_width() or 300
            proporcion = logo_img.height / logo_img.width
            
            # Reducir el tamaño en un 50%
            nuevo_ancho = int(largo_barra * 0.5)  # 50% del tamaño original
            nuevo_alto = int(nuevo_ancho * proporcion)
            
            logo_img = logo_img.resize((nuevo_ancho, nuevo_alto))
            logo_tk = ImageTk.PhotoImage(logo_img)
            lbl_logo.config(image=logo_tk)
            lbl_logo.image = logo_tk
            print("📱 Logo redimensionado al 50%")

        # -------- Extracción ROM --------
        actualizar_progreso(10, "Leyendo Cartucho...")
        print("💾 Leyendo Cartucho...")
        resultado = subprocess.run(
            [FLASHGBX, "--cli", "--mode", MODE, "--action", "backup-rom",
             "--overwrite", ROM_PATH],
            timeout=60, cwd=CARPETA_SCRIPT,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if resultado.returncode != 0:
            print("❌ Error extrayendo ROM")
            messagebox.showerror("ERROR", "❌ Error extrayendo ROM")
            limpiar_archivos()
            return
        else:
            print("✅ ROM extraída correctamente")

        # -------- Extracción SAVE --------
        actualizar_progreso(30, "Leyendo SAVE...")
        print("💾 Leyendo SAVE...")
        resultado = subprocess.run(
            [FLASHGBX, "--cli", "--mode", MODE, "--action", "backup-save",
             "--overwrite", SAV_PATH],
            timeout=60, cwd=CARPETA_SCRIPT,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if resultado.returncode != 0:
            actualizar_progreso(35, "SAVE no encontrado")
            print("⚠️  SAVE no encontrado")
        else:
            actualizar_progreso(60, "SAVE extraído")
            print("✅ SAVE extraído correctamente")

        # -------- Preparar Launch (botón) ----------
        btn_launch.pack(side=tk.BOTTOM, pady=10)
        actualizar_progreso(70, "Cartucho listo", "Presiona Launch para jugar")
        print("🎯 Cartucho listo, mostrando botón Launch")

    except Exception as e:
        print(f"❌ Error en proceso_juego: {e}")
        messagebox.showerror("ERROR", f"Ocurrió un error:\n{e}")
        limpiar_archivos()

def abrir_mgba():
    if not os.path.exists(ROM_PATH):
        messagebox.showerror("ERROR", "❌ No hay ROM para ejecutar.")
        return

    actualizar_progreso(75, "Iniciando mGBA...")

    # Ejecutar mGBA sin bloquear la interfaz
    proceso_mgba = subprocess.Popen([MGBA, ROM_PATH])

    # Esperar a que cierre mGBA
    def esperar_cierre():
        proceso_mgba.wait()

        # -------- Restaurar SAVE con barra animada --------
        porcentaje_actual = 80
        actualizar_progreso(porcentaje_actual, "Restaurando SAVE al cartucho...")

        resultado = subprocess.Popen(
            [FLASHGBX, "--cli", "--mode", "dmg", "--action", "restore-save",
             "--overwrite", SAV_PATH],
            cwd=CARPETA_SCRIPT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        while resultado.poll() is None:
            porcentaje_actual += 2
            if porcentaje_actual > 99:
                porcentaje_actual = 99
            actualizar_progreso(porcentaje_actual, "Restaurando SAVE al cartucho...")
            time.sleep(0.05)

        salida, error = resultado.communicate()
        if resultado.returncode == 0:
            actualizar_progreso(100, "Proceso completado", "SAVE restaurado correctamente")
        else:
            actualizar_progreso(100, "Error", "❌ No se pudo restaurar SAVE")

        limpiar_archivos()
        time.sleep(2)
        ventana.quit()

    hilo_espera = threading.Thread(target=esperar_cierre)
    hilo_espera.start()

# =========================
# INTERFAZ PRINCIPAL
# =========================
def crear_interfaz():
    """Crea la interfaz gráfica completa"""
    global ventana, frame_principal, lbl_nombre_juego, lbl_portada, lbl_logo
    global lbl_estado, lbl_detalle, barra_progreso, btn_launch
    global frame_inferior, lbl_estado_inferior, barra_inferior, style
    
    ventana = tk.Tk()
    ventana.title("GB Player Launcher")
    ventana.configure(bg=COLOR_FONDO)
    ventana.geometry("800x520")

    # Centrar ventana principal
    centrar_ventana(ventana)

    frame_principal = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Nombre del juego
    lbl_nombre_juego = tk.Label(frame_principal, text="", fg=COLOR_TEXTO,
                                bg=COLOR_FONDO, font=("Arial", 16, "bold"))
    lbl_nombre_juego.pack(pady=5)

    # Portada
    lbl_portada = tk.Label(frame_principal, bg=COLOR_FONDO)
    lbl_portada.pack(pady=5)

    # Logo GameBoy Color
    lbl_logo = tk.Label(frame_principal, bg=COLOR_FONDO)
    lbl_logo.pack(pady=5)

    # Estado y barra
    lbl_estado = tk.Label(frame_principal, text="Iniciando...", fg=COLOR_TEXTO, bg=COLOR_FONDO,
                          font=("Arial", 12))
    lbl_estado.pack()
    lbl_detalle = tk.Label(frame_principal, text="", fg=COLOR_TEXTO, bg=COLOR_FONDO,
                           font=("Arial", 10))
    lbl_detalle.pack()

    barra_progreso = ttk.Progressbar(frame_principal, orient="horizontal", length=400,
                                     mode="determinate", style="GameBoy.Horizontal.TProgressbar")
    barra_progreso.pack(pady=10)

    # Botón Launch oculto al inicio
    btn_launch = tk.Button(frame_principal, text="Launch", command=abrir_mgba,
                           bg=COLOR_ACENTO, fg="white", font=("Arial", 12, "bold"),
                           relief="flat", padx=20, pady=10)
    btn_launch.pack_forget()

    # Barra inferior fija
    frame_inferior = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_inferior.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    lbl_estado_inferior = tk.Label(frame_inferior, text="Iniciando...",
                                   font=("Courier New", 9, "bold"),
                                   fg=COLOR_TEXTO, bg=COLOR_FONDO, anchor="w")
    lbl_estado_inferior.pack(side=tk.LEFT, padx=5)
    barra_inferior = ttk.Progressbar(frame_inferior, orient=tk.HORIZONTAL,
                                     length=300, mode='determinate',
                                     maximum=100, style="GameBoy.Horizontal.TProgressbar")
    barra_inferior.pack(side=tk.RIGHT, padx=5, pady=5)

    # Estilo barra
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("GameBoy.Horizontal.TProgressbar",
                    troughcolor="#2c2c2c", background=COLOR_ACENTO,
                    thickness=12)

    # Centrar nuevamente después de crear todos los widgets
    ventana.after(100, lambda: centrar_ventana(ventana))

    return ventana

# =========================
# EJECUCIÓN PRINCIPAL
# =========================
if __name__ == "__main__":
    print("🚀 INICIANDO GB PLAYER LAUNCHER")
    print(f"📁 Directorio actual: {os.getcwd()}")
    print(f"📁 Script en: {CARPETA_SCRIPT}")
    
    # MOSTRAR ADVERTENCIA INICIAL ANTES DE TODO
    print("📢 Mostrando advertencia inicial...")
    mostrar_advertencia_inicial()
    print("✅ Advertencia aceptada, continuando...")
    
    # Primero verificamos el cartucho SIN interfaz gráfica
    print("🔄 Verificando cartucho...")
    cartucho_ok, resultado = verificar_cartucho()
    
    if not cartucho_ok:
        print("❌ No hay cartucho válido")
        # Si no hay cartucho, mostramos error con una mini ventana temporal
        root_temp = tk.Tk()
        root_temp.withdraw()  # Ocultar ventana principal
        messagebox.showerror("ERROR", resultado)
        # Centrar también la ventana de error
        root_temp.update_idletasks()
        centrar_ventana(root_temp)
        root_temp.deiconify()  # Mostrar ventana centrada
        root_temp.mainloop()
        sys.exit(1)  # Salir del programa
    
    # Si hay cartucho válido, creamos la interfaz completa
    print("✅ Cartucho detectado. Iniciando interfaz...")
    ventana = crear_interfaz()
    
    # Iniciar proceso del juego en un hilo
    hilo = threading.Thread(target=proceso_juego, args=(resultado,))
    hilo.start()
    
    # Iniciar el loop principal de tkinter
    print("🎮 Iniciando interfaz gráfica...")
    ventana.mainloop()