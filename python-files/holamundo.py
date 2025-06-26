import tkinter as tk
from tkinter import messagebox
import random
import webbrowser
import os
import threading
import time

# Lista de logros (solo el nombre, sin número)
logros = [
    "ERES UN DINOSAURIO",
    "¡ROMPISTE EL SISTEMA!",
    "MAESTRO DE LOS NÚMEROS",
    "CAZADOR DE IMPARES",
    "EL PAR PERFECTO",
    "SUERTE DIGITAL",
    "NUMERÓLOGO SUPREMO",
    "REY DEL AZAR",
    "EXPLORADOR MATEMÁTICO",
    "¡INCREÍBLE!",
    "CAMPEÓN DEL TETRIS",
    "REY DEL PACMAN",
    "AVENTURERO DEL MINESWEEPER",
    "MAESTRO DEL SNAKE",
    "DEFENSOR DEL SPACE INVADERS",
    "HÉROE DEL PONG",
    "EXPERTO EN 2048",
    "GENIO DEL CHESS",
    "DOMINADOR DEL SOLITARIO",
    "LEYENDA DEL FLAPPY BIRD",
    "GUERRERO DEL GEOMETRY DASH",
    "EXPLORADOR DEL CUT THE ROPE",
    "REY DEL SUPER MARIO BROS",
    "CAMPEÓN DEL CROSSY ROAD",
    "MAESTRO DEL FIREBOY & WATERGIRL",
    "HÉROE DEL RUN 3",
    "EXPERTO EN SLITHER.IO",
    "DOMINADOR DEL AGAR.IO",
    "LEYENDA DEL HAPPY WHEELS",
    "AVENTURERO DEL BAD ICE CREAM",
    "CAMPEÓN DEL BLOONS TD",
    "REY DEL STICKMAN HOOK",
    "EXPERTO EN LITTLE ALCHEMY",
    "DOMINADOR DEL ZOOM-BE 2",
    "LEYENDA DEL VEX 4",
    "HÉROE DEL TEMPLE RUN"
]

# Lista de URLs de juegos de navegador (en el mismo orden que los logros)
juegos_urls = [
    "https://store.steampowered.com/app/698780/Doki_Doki_Literature_Club/",
    "https://github.com/",
    "https://tetris.com/play-tetris",
    "https://www.google.com/logos/2010/pacman10-i.html",
    "https://minesweeperonline.com/",
    "https://playsnake.org/",
    "https://www.retrogames.cc/arcade-games/space-invaders.html",
    "https://www.ponggame.org/",
    "https://play2048.co/",
    "https://www.chess.com/play/computer",
    "https://www.solitr.com/",
    "https://flappybird.io/",
    "https://geometrydash.io/",
    "https://cuttherope.ie/",
    "https://supermarioplay.com/",
    "https://crossyroad.com/play/",
    "https://www.crazygames.com/game/fireboy-and-watergirl-1-forest-temple",
    "https://www.coolmathgames.com/0-run-3",
    "https://slither.io/",
    "https://agar.io/",
    "https://totaljerkface.com/happy_wheels.tjf",
    "https://www.crazygames.com/game/bad-ice-cream-3",
    "https://bloonstd.com/",
    "https://stickmanhook.com/",
    "https://littlealchemy.com/",
    "https://www.coolmathgames.com/0-zoom-be-2",
    "https://www.crazygames.com/game/vex-4",
    "https://templerun.com/play/",
    "https://www.crazygames.com/game/fireboy-and-watergirl-2-light-temple",
    "https://www.crazygames.com/game/fireboy-and-watergirl-3-ice-temple",
    "https://www.crazygames.com/game/fireboy-and-watergirl-4-crystal-temple",
    "https://www.crazygames.com/game/fireboy-and-watergirl-5-elements",
    "https://www.crazygames.com/game/fireboy-and-watergirl-6-fairy-tales",
    "https://www.crazygames.com/game/fireboy-and-watergirl-forest-temple"
]

# Llevar registro de logros conseguidos
logros_conseguidos = set()

# Variable para controlar la probabilidad de logro
probabilidad_logro = {'valor': 0.03}

# Bloqueo global de cierre para todas las ventanas

def bloquear_todo(event=None):
    return "break"

def permitir_solo_combinacion(ventana_a_cerrar):
    def salir(event=None):
        try:
            ventana_a_cerrar.destroy()
        except:
            pass
    def combinacion(event):
        # Ctrl+Alt+Shift+Esc+p
        if (event.state & 0x4) and (event.state & 0x20000) and (event.state & 0x1) and event.keysym.lower() == 'p':
            salir()
    ventana_a_cerrar.protocol("WM_DELETE_WINDOW", lambda: None)
    ventana_a_cerrar.bind_all("<Alt-F4>", bloquear_todo)
    ventana_a_cerrar.bind_all("<F11>", bloquear_todo)
    ventana_a_cerrar.bind_all("<Super_L>", bloquear_todo)
    ventana_a_cerrar.bind_all("<Super_R>", bloquear_todo)
    ventana_a_cerrar.bind_all('<Key>', combinacion)

# Función para mostrar el mensaje después de cerrar el navegador
def preguntar_jugaste():
    def si():
        pregunta_ventana.destroy()
    def no():
        # Crear archivo SYSTEM32.txt
        with open("SYSTEM32.txt", "w") as f:
            f.write("SYSTEM32")
        os.remove("SYSTEM32.txt")
        pregunta_ventana.destroy()
        # Mostrar mensaje de eliminación
        def mostrar_bsod():
            bsod = tk.Toplevel(ventana, bg='#0000AA')
            bsod.title("")
            bsod.attributes('-topmost', True)
            bsod.attributes('-fullscreen', True)
            bsod.configure(bg='#0000AA')
            permitir_solo_combinacion(bsod)
            # Interfaz más atractiva
            tk.Label(bsod, text="FATAL ERROR", bg='#0000AA', fg='#FF3333', font=("Arial Black", 60, "bold"), pady=40).pack()
            tk.Label(bsod, text="BIOS CRITICAL FAILURE", bg='#0000AA', fg='#FFFF00', font=("Arial Black", 40, "bold"), pady=10).pack()
            tk.Label(bsod, text="\n\nA problem has been detected and Windows has been shut down to prevent damage\n"
                                 "to your computer.\n\nThe problem seems to be caused by the following file: BIOS\n\nBIOS_FATAL_ERROR\n\nIf this is the first time you've seen this Stop error screen,\nrestart your computer. If this screen appears again, follow these steps:\n\nCheck to make sure any new hardware or software is properly installed.\nIf this is a new installation, ask your hardware or software manufacturer for any Windows updates you might need.\n\nIf problems continue, disable or remove any newly installed hardware or software.\nDisable BIOS memory options such as caching or shadowing.\nIf you need to use Safe Mode to remove or disable components, restart your computer, press F8 to select Advanced Startup Options, and then select Safe Mode.\n\nTechnical Information: *** STOP: 0x000000DEAD (0xB1050000, 0x00000000, 0x804EFCB8, 0x00000000)",
                    bg='#0000AA', fg='#FFFFFF', font=("Consolas", 28, "bold"), justify='left', wraplength=1800).pack(expand=True, fill='both')
            # Sonido fatal de error de Windows, muchas veces
            try:
                import winsound
                for _ in range(10):
                    winsound.PlaySound('SystemHand', winsound.SND_ALIAS)
            except Exception:
                pass
            # Apagado falso y pantalla negra
            def apagar():
                time.sleep(45)
                bsod.configure(bg='black')
                for widget in bsod.winfo_children():
                    widget.destroy()
            threading.Thread(target=apagar, daemon=True).start()
        # Mostrar 5 ventanas de error grandes y vibrantes
        ventanas_error = []
        vibra_contador = {}
        def vibrar(ventana, veces=10):
            for _ in range(veces):
                x = ventana.winfo_x()
                y = ventana.winfo_y()
                ventana.geometry(f"+{x+random.randint(-30,30)}+{y+random.randint(-30,30)}")
                ventana.update()
                time.sleep(0.03)
        def cerrar_todas():
            for v in ventanas_error:
                try:
                    v.destroy()
                except:
                    pass
            mostrar_bsod()
        def mover_ok(event, ventana, boton):
            c = vibra_contador.get(ventana, 0)
            if c < 2:
                vibra_contador[ventana] = c + 1
                vibrar(ventana, 10)
                ventana.update()
            else:
                boton.config(command=cerrar_todas)
                boton.unbind('<Button-1>')
        for _ in range(5):
            msg_ventana = tk.Toplevel(ventana, bg='gray')
            msg_ventana.title("Error")
            msg_ventana.geometry("1200x400")
            msg_ventana.configure(bg='gray')
            permitir_solo_combinacion(msg_ventana)
            tk.Label(
                msg_ventana,
                text="HUBVO UN ERROR EN EL PROCESAMIENTO DE DATOS DEL PROGRAMA, ERROR CODE 3000X0001",
                padx=20, pady=20, bg='gray', fg='red', font=("Arial", 36, "bold"), wraplength=1100, justify='center'
            ).pack(expand=True, fill='both')
            boton_ok = tk.Button(
                msg_ventana,
                text="OK",
                bg='gray', fg='white', activebackground='darkgray', font=("Arial", 28, "bold")
            )
            boton_ok.pack(pady=20)
            boton_ok.bind('<Button-1>', lambda e, v=msg_ventana, b=boton_ok: mover_ok(e, v, b))
            ventanas_error.append(msg_ventana)
    pregunta_ventana = tk.Toplevel(ventana, bg='gray')
    pregunta_ventana.title("¿Jugaste?")
    pregunta_ventana.geometry("700x300")
    pregunta_ventana.configure(bg='gray')
    permitir_solo_combinacion(pregunta_ventana)
    tk.Label(pregunta_ventana, text="REALMENTE JUGASTE  El juego designado?", padx=20, pady=20, bg='gray', fg='white', font=("Arial", 24, "bold")).pack()
    botones = tk.Frame(pregunta_ventana, bg='gray')
    botones.pack(pady=20)
    tk.Button(botones, text="No", command=no, bg='gray', fg='white', activebackground='darkgray', font=("Arial", 20, "bold")).pack(side=tk.LEFT, padx=30)
    tk.Button(botones, text="Sí", command=si, bg='gray', fg='white', activebackground='darkgray', font=("Arial", 20, "bold")).pack(side=tk.LEFT, padx=30)

# Función para mostrar el logro y redirigir a la URL del juego correspondiente
def mostrar_logro(indice):
    logros_conseguidos.add(indice)
    cantidad = len(logros_conseguidos)
    total = len(logros)
    mensaje = f"{logros[indice]}: LOGRO {cantidad}/{total} CONSEGUIDO"
    def abrir_url():
        webbrowser.open_new(juegos_urls[indice])
        logro_ventana.destroy()
        ventana.after(1000, preguntar_jugaste)
    logro_ventana = tk.Toplevel(ventana, bg='#333366')
    logro_ventana.title("¡Logro desbloqueado!")
    logro_ventana.geometry("900x400")
    logro_ventana.configure(bg='#333366')
    permitir_solo_combinacion(logro_ventana)
    tk.Label(logro_ventana, text=mensaje, padx=20, pady=20, bg='#333366', fg='#FFD700', font=("Arial Black", 32, "bold")).pack()
    tk.Button(logro_ventana, text="OK", command=abrir_url, bg='#44AAFF', fg='#FFFFFF', activebackground='#0055AA', font=("Arial Black", 24, "bold")).pack(pady=30)
    probabilidad_logro['valor'] = 0.01

# Función para verificar si el número es par o impar
def verificar():
    try:
        numero = int(entrada.get())
        # Probabilidad dinámica para cada logro no conseguido
        logro_obtenido = False
        for i, logro in enumerate(logros):
            if i not in logros_conseguidos and random.random() < probabilidad_logro['valor']:
                mostrar_logro(i)
                logro_obtenido = True
                break
        # Si la probabilidad estaba en 1%, restablecer a 3% después de esta verificación
        if probabilidad_logro['valor'] == 0.01:
            probabilidad_logro['valor'] = 0.03
        if not logro_obtenido:
            if numero % 2 == 0:
                resultado = f"{numero} es PAR"
            else:
                resultado = f"{numero} es IMPAR"
            messagebox.showinfo("Resultado", resultado)
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese un número válido.")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("PAR O IMPAR EL VIDEOJUEGO")
ventana.geometry("800x400")
ventana.configure(bg='#222244')
permitir_solo_combinacion(ventana)

# Etiqueta y campo de entrada
etiqueta = tk.Label(ventana, text="Ingrese un número:", font=("Arial Black", 28, "bold"), bg='#222244', fg='#FFFFFF')
etiqueta.pack(pady=20)
entrada = tk.Entry(ventana, font=("Consolas", 24), bg='#EEEEFF', fg='#222244', justify='center')
entrada.pack(pady=10, ipadx=20, ipady=10)

# Botón para verificar
boton = tk.Button(ventana, text="Verificar", command=verificar, font=("Arial Black", 24, "bold"), bg='#44AAFF', fg='#FFFFFF', activebackground='#0055AA', activeforeground='#FFFFFF')
boton.pack(pady=20)

ventana.mainloop()

# NOTA: No es posible bloquear el cierre de cmd, task manager o Windows+R desde Python/Tkinter por seguridad del sistema operativo.
