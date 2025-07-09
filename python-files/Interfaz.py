#  Copyright (c) 2020-2023 Tabares, Inc Todos los derechos reservados.


"""

      Titulo: CSE
      Autor: César Alejandro Tabares Espinosa
      Fecha: 22.10.2022

"""

from tkinter import messagebox
import requests
import json
import bs4
import dbm
import os
import re
import time
from tkinter import *
import psutil
import threading
import dbm.dumb


# Creacion de archivos
ruta_ejecutable = os.getcwd()
CONFIG_DIR = os.path.expanduser(ruta_ejecutable)

try:
    os.makedirs(CONFIG_DIR)
except FileExistsError:
    pass

CARDS_DB = os.path.join(CONFIG_DIR, "cards")
ATTR_UUID_FILE = os.path.join(CONFIG_DIR, "attribute_uuid")
LOGOUT_URL_FILE = os.path.join(CONFIG_DIR, "logout_url")
logfile = open(os.path.join(CONFIG_DIR, "connections.log"), "a")
ruta_usuarios = f"{ruta_ejecutable}/usuarios.txt"
ruta_usuario_conectado = f"{ruta_ejecutable}/usuario_actual.txt"
ruta_temporizador = f"{ruta_ejecutable}/temporizador.txt"
icono = f'{ruta_ejecutable}/Moon.ico'

UB = "Ubuntu 30 normal"
TNR = "Times New Roman"
C = "Courier"
A = "Arial"


def efecto_boton(nombre_boton_ef):
    def enter(*args):
        nombre_boton_ef.config(relief="solid",
                               border="1",
                               background="#222",
                               foreground="#ffffff",
                               activebackground="#111",
                               activeforeground="#fff",
                               highlightbackground="#333",
                               highlightcolor="#333",
                               fg="#ffffff",
                               justify="center")

    def leave(*args):
        ccs_boton(nombre_boton_ef)

    nombre_boton_ef.bind("<Enter>", enter)
    nombre_boton_ef.bind("<Leave>", leave)


def efecto_pantalla(nombre_pantalla_ef):
    def enter(*args):
        nombre_pantalla_ef.config(relief="solid",
                                  border="0",
                                  background="#444",
                                  foreground="#ffffff",
                                  highlightbackground="#555",
                                  highlightcolor="#0cb7f2",
                                  highlightthickness="1",
                                  fg="#ffffff",
                                  justify="left")

    def leave(*args):
        ccs_pantalla(nombre_pantalla_ef)

    nombre_pantalla_ef.bind("<Enter>", enter)
    nombre_pantalla_ef.bind("<Leave>", leave)


def ccs_boton(nombre_boton):
    nombre_boton.config(relief="solid",
                        border="1",
                        background="#444",
                        foreground="#ffffff",
                        activebackground="#333",
                        activeforeground="#fff",
                        highlightbackground="#555",
                        highlightcolor="#444",
                        fg="#ffffff",
                        justify="center")


def ccs_pantalla(nombre_pantalla):
    nombre_pantalla.config(relief="solid",
                           border="0",
                           background="#444",
                           foreground="#ffffff",
                           highlightbackground="#444",
                           highlightcolor="#0cb7f2",
                           highlightthickness="1",
                           fg="#ffffff",
                           justify="left")


def leer_ruta_usuarios():
    if os.path.isfile(ruta_usuarios):
        y = 0
        f = open(ruta_usuarios, "r")
        while True:
            linea = list(f.readline())
            for elemento in linea:
                if elemento == '\n':
                    linea.remove('\n')
            linea = ''.join(linea)
            listbox_cuentas.insert(END, linea)

            y += 1
            if not linea:
                break

        listbox_cuentas.delete(y - 1)
        f.close()


def valor_temporizador(var1):
    if os.path.isfile(ruta_temporizador):
        with open(ruta_temporizador, "r") as input:
            te = input.readline()
        return te[var1]
    else:
        return '0'


def get_size(bytes):  # Transforma los datos de bytes a valores legibles
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}B"
        bytes /= 1024


def ico_err_pass(ico_pass):  # Evitar el error de no tener icono
    try:
        ico_pass.iconbitmap(icono)
    except:
        pass


def log(*args, **kwargs):  # Manejo del log
    import datetime
    date = datetime.datetime.now()
    date = datetime.datetime.strftime(date, '%Y-%m-%d %H:%M:%S')

    kwargs.update(dict(file=logfile))
    print("{}".format(date, ), *args, **kwargs, )
    logfile.flush()


def get_inputs(form_soup):
    form = {}
    for i in form_soup.find_all("input"):
        try:
            form[i["name"]] = i["value"]
        except KeyError:
            continue
    return form


def parse_time(t):  # Transformar a tiempo legible
    try:
        h, m, s = [int(x.strip()) for x in t.split(":")]
        return h * 3600 + m * 60 + s
    except:
        return 0


def get_password(username):
    with dbm.open(CARDS_DB) as cards_db:
        if not username in cards_db:
            return None
        info = json.loads(cards_db[username].decode())
        return info['password']


def select_card():
    cards = []
    with dbm.open(CARDS_DB) as cards_db:
        for card in cards_db.keys():
            info = json.loads(cards_db[card].decode())
            tl = parse_time(info.get('time_left', '00:00:00'))
            if tl <= 0:
                continue
            info['username'] = card
            cards.append(info)
    cards.sort(key=lambda c: c['time_left'])
    if len(cards) == 0:
        return None, None
    return cards[0]['username'], cards[0]['password']


def err_temporiz(pantalla_h, pantalla_m, pantalla_s):  # Comprobar ejecución correcta en el apartado de temporizador
    try:
        int(pantalla_h.get())
        int(pantalla_m.get())
        int(pantalla_s.get())
    except:
        messagebox.showerror('Error de tiempo', 'Establezca una hora correcta')
        pantalla_h.set('00')
        pantalla_m.set('00')
        pantalla_s.set('00')
        raise ZeroDivisionError

    if len(pantalla_h.get()) != 2:
        messagebox.showerror('Error de tiempo', 'Establezca una hora correcta')
        pantalla_h.set('00')
        raise ZeroDivisionError
    if len(pantalla_m.get()) != 2:
        messagebox.showerror('Error de tiempo', 'Establezca una hora correcta')
        pantalla_m.set('00')
        raise ZeroDivisionError
    if len(pantalla_s.get()) != 2:
        messagebox.showerror('Error de tiempo', 'Establezca una hora correcta')
        pantalla_s.set('00')
        raise ZeroDivisionError
    for x in range(60, 100):
        if int(pantalla_m.get()) == int(x) or int(pantalla_s.get()) == int(x):
            messagebox.showerror('Error de tiempo', 'Establezca una hora correcta')
            pantalla_h.set('00')
            pantalla_m.set('00')
            pantalla_s.set('00')
            raise ZeroDivisionError


def up(username):
    try:
        err_temporiz(pantalla_hora, pantalla_minutos, pantalla_segundos)
    except ZeroDivisionError:
        return


    # Comprobar si un usuario está conectado

    session = requests.Session()
    try:
        resp = session.head("https://www.google.es/", timeout=1, allow_redirects=False)
        if resp.ok:
            messagebox.showinfo('Información', 'Ya hay un usuario conectado')
            log('Información', 'Ya hay un usuario conectado')
            return
    except:
        pass
    else:
        pass


    # Comprobar si un usuario está conectado a una red nacional
    try:
        resp = session.head("https://www.sld.cu/", timeout=1, allow_redirects=False)
        if resp.ok:
            messagebox.showinfo('Información', 'Ya hay un usuario conectado a la red nacional')
            log('Información', 'Ya hay un usuario conectado a la red nacional')
            return
    except:
        pass
    else:
        pass

    # Comprobar si un usuario no dispone de tiempo en su cuenta
    if time_left(username) == '00:00:00':
        messagebox.showinfo('Información', 'Su cuenta no dispone de saldo')
        return

    # empezar a conectar
    try:
        r = session.get("https://secure.etecsa.net:8443/", timeout=(2, 1))
    except:
        messagebox.showerror('Error de conexión', 'No se pudo establecer una conexión al portal de usuario')
        log('Error de conexión, No se pudo establecer una conexión al portal de usuario')
        return

    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    action = 'https://secure.etecsa.net:8443'

    if username:
        username = username
        password = get_password(username)
        if password is None:
            messagebox.showerror("Error", "Datos incorrectos: {}".format(username))
            return

    else:
        username, password = select_card()
        if username is None:
            messagebox.showerror("Error", "Datos incorrectos\nElimine la cuenta y vuelva a agregarla")
            return
        username = username.decode()

    tl = time_left(username)
    log("Conectado con la cuenta {}. Tiempo restante de la cuenta: {}".format(username, tl))

    form = get_inputs(soup)
    r = session.post(action, form)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    form_soup = soup.find("form", id="formulario")
    action = form_soup["action"]
    form = get_inputs(form_soup)
    form['username'] = username
    form['password'] = password
    csrfhw = form['CSRFHW']
    wlanuserip = form['wlanuserip']
    last_attribute_uuid = ""

    try:
        last_attribute_uuid = open(ATTR_UUID_FILE, "r").read().strip()
    except FileNotFoundError:
        pass
    guessed_logout_url = (
            "https://secure.etecsa.net:8443/LogoutServlet?" +
            "CSRFHW={}&" +
            "username={}&" +
            "ATTRIBUTE_UUID={}&" +
            "wlanuserip={}"
    ).format(
        csrfhw,
        username,
        last_attribute_uuid,
        wlanuserip
    )
    with open(LOGOUT_URL_FILE, "w") as f:
        f.write(guessed_logout_url + "\n")

    log("Intentando conexión. URL de desconexión esperado:", guessed_logout_url)

    try:
        r = session.post(action, form)
        m = re.search(r'ATTRIBUTE_UUID=(\w+)&CSRFHW=', r.text)
        attribute_uuid = None
        if m:
            attribute_uuid = m.group(1)
    except:
        messagebox.showerror('Error de conexión', 'No se pudo establecer una conexión al servidor de ETECSA')
        log('Error de conexión, No se pudo establecer una conexión al servidor de ETECSA')
        attribute_uuid = None

    if attribute_uuid is None:
        messagebox.showerror('Error de conexión', 'La conexión falló por un error inesperado')

    else:
        try:
            open(ruta_usuario_conectado, 'w').write(obtener_usuario_selec())
        except:
            pass

        with open(ATTR_UUID_FILE, "w") as f:
            f.write(attribute_uuid + "\n")
        login_time = int(time.time())
        logout_url = (
                "https://secure.etecsa.net:8443/LogoutServlet?" +
                "CSRFHW={}&" +
                "username={}&" +
                "ATTRIBUTE_UUID={}&" +
                "wlanuserip={}"
        ).format(
            csrfhw,
            username,
            attribute_uuid,
            wlanuserip
        )
        with open(LOGOUT_URL_FILE, "w") as f:
            f.write(logout_url + "\n")
        log("Conectado, URL de desconexión actual: '{}'".format(logout_url))
        if logout_url == guessed_logout_url:
            log("URL de desconexión activo")
        else:
            log("URL de desconexión no activo")

        net_before = psutil.net_io_counters()  # Contador de bytes
        pantalla_p_hora.config(state='disabled')
        pantalla_p_minutos.config(state='disabled')
        pantalla_p_segundos.config(state='disabled')

        toplevel_conectado = Toplevel(raiz)
        toplevel_conectado.title("Bienvenido")
        toplevel_conectado.resizable(False, False)
        toplevel_conectado.config(background="#333")
        toplevel_conectado.transient(raiz)

        ico_err_pass(toplevel_conectado)

        frame_conectado_izquierdo = Frame(toplevel_conectado)
        frame_conectado_izquierdo.grid(row=0, column=0)
        frame_conectado_izquierdo.config(bd="4", background="#333", relief='ridge')

        frame_conectado = Frame(frame_conectado_izquierdo)
        frame_conectado.grid(row=0, column=0)
        frame_conectado.config(bd="2", background="#333")

        label_info_conect = Label(frame_conectado, font=(UB, 18), text='Estado: conectado')
        label_info_conect.grid(row=0, column=0, padx='1', pady='15')
        label_info_conect.config(background="#333", fg="#fff", justify="center")

        label_info_usuario = Label(frame_conectado, font=(UB, 16), text=f'Usuario: {username}')
        label_info_usuario.grid(row=1, column=0, padx='1', pady='2')
        label_info_usuario.config(background="#333", fg="#fff", justify="center")

        label_info_tiempo_disp = Label(frame_conectado, font=(UB, 16))
        label_info_tiempo_disp.grid(row=2, column=0, padx='1', pady='2')
        label_info_tiempo_disp.config(background="#333", fg="#fff", justify="center")

        # Método para obtener el tiempo de los temporizadores

        def obtener_tiempo():
            horas = pantalla_hora.get()
            if horas == '':
                horas = '00'
            minutos = pantalla_minutos.get()
            if minutos == '':
                minutos = '00'
            segundos = pantalla_segundos.get()
            if minutos == '':
                minutos = '00'
            total_tiempo = f'{horas}:{minutos}:{segundos}'
            return total_tiempo

        def obtener_tiempo_2():
            horas = pantalla_hora_2.get()
            if horas == '':
                horas = '00'
            minutos = pantalla_minutos_2.get()
            if minutos == '':
                minutos = '00'
            segundos = pantalla_segundos_2.get()
            if minutos == '':
                minutos = '00'
            total_tiempo_2 = f'{horas}:{minutos}:{segundos}'
            return total_tiempo_2

        def tiempo_mostrado():  # Método para detener el tiempo por temporizador

            tiempo = ("\rTiempo consumido: {} ".format(human_secs(int(time.time()) - login_time)))
            tiempo_detener = human_secs(int(time.time()) - login_time)
            label_info_tiempo_disp.config(text=tiempo)
            label_info_tiempo_disp.after(1000, tiempo_mostrado)
            if obtener_tiempo_2() != '00:00:00':
                if tiempo_detener == obtener_tiempo_2():
                    desconectar()
            else:
                if obtener_tiempo() != '00:00:00':
                    if tiempo_detener == obtener_tiempo():
                        desconectar()

        label_info_tiempo_disponible = Label(frame_conectado, font=(UB, 16), text=f'Tiempo disponible: {tl}')
        label_info_tiempo_disponible.grid(row=3, column=0, padx='1', pady='10')
        label_info_tiempo_disponible.config(background="#333", fg="#fff", justify="center")

        frame_conectado_botones = Frame(frame_conectado_izquierdo)
        frame_conectado_botones.grid(row=1, column=0)
        frame_conectado_botones.config(bd='2', background="#333")

        boton_actualizar_frame_conectado = Button(frame_conectado_botones, text='Actualizar', width='12',
                                                  height='1',
                                                  font=(UB, 14),
                                                  command=lambda: actualizar_tiempo())
        boton_actualizar_frame_conectado.grid(row=0, column=0, padx='6', pady='5')
        ccs_boton(boton_actualizar_frame_conectado)
        efecto_boton(boton_actualizar_frame_conectado)

        boton_desconectar_frame_conectado = Button(frame_conectado_botones, text='Desconectar', width='12', height='1',
                                                   font=(UB, 14),
                                                   command=lambda: desconectar())
        boton_desconectar_frame_conectado.grid(row=0, column=1, padx='6', pady='5')
        ccs_boton(boton_desconectar_frame_conectado)
        efecto_boton(boton_desconectar_frame_conectado)

        frame_conectado_derecha = Frame(toplevel_conectado)
        frame_conectado_derecha.grid(row=0, column=1)
        frame_conectado_derecha.config(bd="4", background="#333", relief="ridge")

        frame_conectado_info_temporizador = Frame(frame_conectado_derecha)
        frame_conectado_info_temporizador.grid(row=0, column=0)
        frame_conectado_info_temporizador.config(background="#333")

        label_info_temporizador = Label(frame_conectado_info_temporizador, font=(UB, 18), text="Temporizador")
        label_info_temporizador.grid(row=0, column=1, padx='1', pady='23')
        label_info_temporizador.config(background="#333", fg="#fff", justify="center")

        label_info_nuevo_temporizador = Label(frame_conectado_info_temporizador, font=(UB, 16))
        label_info_nuevo_temporizador.grid(row=1, column=1, padx='1', pady='10')
        label_info_nuevo_temporizador.config(background="#333", fg="#fff", justify="center")
        if obtener_tiempo() == '00:00:00':
            label_info_nuevo_temporizador.config(text="No se ha establecido ningún\ntiempo de detención")
        else:
            label_info_nuevo_temporizador.config(text=f"El temporizador se ha\nestablecido en: {obtener_tiempo()}")

        frame_conectado_temporizador = Frame(frame_conectado_derecha)
        frame_conectado_temporizador.grid(row=1, column=0)
        frame_conectado_temporizador.config(background="#333")

        pantalla_hora_2 = StringVar(value='00')
        pantalla_h_2 = Entry(frame_conectado_temporizador, textvariable=pantalla_hora_2, width=4, font=(A, 14))
        pantalla_h_2.grid(row=0, column=1, padx="5", pady="2")
        ccs_pantalla(pantalla_h_2)
        efecto_pantalla(pantalla_h_2)

        label_temp_2 = Label(frame_conectado_temporizador, text=':', font=(A, 14))
        label_temp_2.grid(row=0, column=2)
        label_temp_2.config(background="#333", fg="#fff", justify="center")

        pantalla_minutos_2 = StringVar(value='00')
        pantalla_m_2 = Entry(frame_conectado_temporizador, textvariable=pantalla_minutos_2, width=4, font=(UB, 14))
        pantalla_m_2.grid(row=0, column=3, padx="5", pady="2")
        ccs_pantalla(pantalla_m_2)
        efecto_pantalla(pantalla_m_2)

        label_temp_3 = Label(frame_conectado_temporizador, text=':', font=(UB, 14))
        label_temp_3.grid(row=0, column=4)
        label_temp_3.config(background="#333", fg="#fff", justify="center")

        pantalla_segundos_2 = StringVar(value='00')
        pantalla_s_2 = Entry(frame_conectado_temporizador, textvariable=pantalla_segundos_2, width=4,
                             font=(UB, 14))
        pantalla_s_2.grid(row=0, column=5, padx="5", pady="2")
        ccs_pantalla(pantalla_s_2)
        efecto_pantalla(pantalla_s_2)

        boton_actualiz_temp_frame_conect = Button(frame_conectado_derecha, text='Actualizar', width='12', height='1',
                                                  font=(UB, 14),
                                                  command=lambda: actualizar_temporizador())
        boton_actualiz_temp_frame_conect.grid(row=2, column=0, padx='1', pady='20')
        ccs_boton(boton_actualiz_temp_frame_conect)
        efecto_boton(boton_actualiz_temp_frame_conect)

        def actualizar_tiempo():
            tl = time_left(username)
            label_info_tiempo_disponible.config(text=f'Tiempo disponible: {tl}')

        def actualizar_temporizador():
            try:
                err_temporiz(pantalla_hora_2, pantalla_minutos_2, pantalla_segundos_2)
            except ZeroDivisionError:
                return False
            if obtener_tiempo_2() == "00:00:00":
                pass
            else:
                label_info_nuevo_temporizador.config(
                    text=f"El temporizador se ha\nestablecido en: {obtener_tiempo_2()}")

        tiempo_mostrado()

        def desconectar():

            try:
                down([])
            except:
                messagebox.showerror('Error de desconexión', 'Hubo un error durante la desconexión')
                return

            frame_conectado.destroy()
            frame_conectado_derecha.destroy()
            frame_conectado_izquierdo.destroy()
            frame_conectado_info_temporizador.destroy()
            frame_conectado_temporizador.destroy()
            frame_conectado_botones.destroy()

            pantalla_p_hora.config(state='normal')
            pantalla_p_minutos.config(state='normal')
            pantalla_p_segundos.config(state='normal')

            now = int(time.time())
            log("Tiempo de conexión:", human_secs(now - login_time))

            frame_desconectar = Frame(toplevel_conectado)
            frame_desconectar.grid()
            frame_desconectar.config(background="#333", relief='ridge', bd='5')

            label_cerrar_sesion = Label(frame_desconectar, font=(UB, 18),
                                        text='Usted ha cerrado con éxito su sesión.')
            label_cerrar_sesion.grid(row=0, column=0, padx='1', pady='15')
            label_cerrar_sesion.config(background="#333", fg="#fff", justify="center")

            label_tiempo_conexion = Label(frame_desconectar, font=(UB, 16),
                                          text=f"Tiempo de conexión: {human_secs(now - login_time)}")
            label_tiempo_conexion.grid(row=1, column=0, padx='1', pady='10')
            label_tiempo_conexion.config(background="#333", fg="#fff", justify="center")

            tl = time_left(username)

            label_tiempo_restante = Label(frame_desconectar, font=(UB, 16), text=f"Tiempo restante: {tl}")
            label_tiempo_restante.grid(row=2, column=0, padx='1', pady='10')
            label_tiempo_restante.config(background="#333", fg="#fff", justify="center")
            log("Tiempo restante:", tl)

            boton_salir = Button(frame_desconectar, text='Salir', width='10', height='1', font=(UB, 14),
                                 command=lambda: salir_3())
            boton_salir.grid(row=4, column=0, padx='1', pady='20')
            ccs_boton(boton_salir)
            efecto_boton(boton_salir)

            pantalla_hora.set('00')
            pantalla_minutos.set('00')
            pantalla_segundos.set('00')

            net_after = psutil.net_io_counters()

            bytes_sent = net_after.bytes_sent - net_before.bytes_sent
            bytes_recv = net_after.bytes_recv - net_before.bytes_recv

            label_info_datos = Label(frame_desconectar, font=(UB, 16),
                                     text=f"Total de datos enviados:"
                                          f" {get_size(bytes_sent)}\nTotal de datos recibidos: {get_size(bytes_recv)}")
            label_info_datos.grid(row=3, column=0, padx='1', pady='10')
            label_info_datos.config(background="#333", fg="#fff", justify="center")
            log(f"Total de datos enviados: {get_size(bytes_sent)}  Total de datos recibidos: {get_size(bytes_recv)}")
            log("Se ha desconectado correctamente\n")

            def salir_3():
                toplevel_conectado.destroy()


def human_secs(secs):
    return "{:02.0f}:{:02.0f}:{:02.0f}".format(
        secs // 3600,
        (secs % 3600) // 60,
        secs % 60,
    )


def down(args):
    global r
    try:
        logout_url = open(LOGOUT_URL_FILE).read().strip()
    except FileNotFoundError:
        messagebox.showinfo('Información', 'La conexión ya se cerró')
        return
    session = requests.Session()
    for error_count in range(10):
        try:
            r = session.get(logout_url)
            break
        except requests.RequestException:
            continue
    if 'SUCCESS' in r.text:
        os.remove(LOGOUT_URL_FILE)
    else:
        messagebox.showerror('Error de desconexión', 'Hubo un error durante la desconexión')
        log('Hubo un error durante la desconexión')
        return
    if os.path.isfile(ruta_usuario_conectado):
        os.remove(ruta_usuario_conectado)


def fetch_expire_date(username, password):
    session = requests.Session()
    try:
        r = session.get("https://secure.etecsa.net:8443/")
    except:
        messagebox.showerror('Error de conexión', 'No se pudo establecer una conexión al portal')
        log('Error de conexión, No se pudo establecer una conexión al portal')
        return
    soup = bs4.BeautifulSoup(r.text, 'html.parser')

    form = get_inputs(soup)
    action = "https://secure.etecsa.net:8443/EtecsaQueryServlet"
    form['username'] = username
    form['password'] = password
    r = session.post(action, form)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    exp_node = soup.find(string=re.compile("expiración"))
    if not exp_node:
        return "**invalid credentials**"
    exp_text = exp_node.parent.find_next_sibling('td').text.strip()
    exp_text = exp_text.replace('\\', '')
    return exp_text


def fetch_usertime(username):
    session = requests.Session()
    try:
        r = session.get("https://secure.etecsa.net:8443/EtecsaQueryServlet?op=getLeftTime&op1={}".format(username))
    except:
        pass
    try:
        attribute_uuid = open(ATTR_UUID_FILE).read().strip()
    except FileNotFoundError:
        pass
    try:
        r = session.get("https://secure.etecsa.net:8443/EtecsaQueryServlet?op=getLeftTime&username={}&ATTRIBUTE_UUID={}"
                        .format(username, attribute_uuid))
    except:
        pass

    return r.text


def time_left(username, fresh=False, cached=False):
    try:
        now = time.time()
        with dbm.open(CARDS_DB, "c") as cards_db:
            card_info = json.loads(cards_db[username].decode())
            last_update = card_info.get('last_update', 0)
            password = card_info['password']
            if not cached:
                if (now - last_update > 60) or fresh:
                    time_left = fetch_usertime(username)
                    last_update = time.time()
                    if re.match(r"[0-9:]+", str(time_left)):
                        card_info['time_left'] = time_left
                        card_info['last_update'] = last_update
                        cards_db[username] = json.dumps(card_info)
            time_left = card_info.get('time_left', 'Requiere actualizar')
        return time_left
    except:
        messagebox.showinfo("Información", "No se puedo acceder al tiempo restante de la cuenta")
        log("Error, No se puedo acceder al tiempo restante de la cuenta")


def expire_date(username, fresh=False, cached=False):
    with dbm.open(CARDS_DB, "c") as cards_db:
        card_info = json.loads(cards_db[username].decode())
        if not cached:
            if (not 'expire_date' in card_info) or fresh:
                password = card_info['password']
                exp_date = fetch_expire_date(username, password)
                card_info['expire_date'] = exp_date
                cards_db[username] = json.dumps(card_info)
        exp_date = card_info['expire_date']
        return exp_date


def delete_cards(cards):
    import sys
    with dbm.open(CARDS_DB, "c") as cards_db:
        if len(cards) > 0:
            sys.stdout.flush()
            while True:
                reply = messagebox.askyesno('Eliminar cartas', 'Eliminar todas las cartas ?')
                if reply:
                    for card in cards:
                        del cards_db[card]
                    break
                else:
                    break


def cards(args):
    with dbm.open(CARDS_DB, "c") as cards_db:
        for card in cards_db.keys():
            card = card.decode()
            card_info = json.loads(cards_db[card].decode())
            password = card_info['password']
            if not args.v:
                password = "*" * (len(password) - 4) + password[-4:]
            print("{}\t{}\t{}\t(expira {})".format(
                card,
                password,
                time_left(card, args.fresh, args.cached),
                expire_date(card, args.fresh, args.cached)
            ))


def verify(username, password):
    session = requests.Session()
    try:
        r = session.get("https://secure.etecsa.net:8443/")
    except:
        messagebox.showerror('Error de conexión', 'No se pudo establecer una conexión al portal')
        return
    soup = bs4.BeautifulSoup(r.text, 'html.parser')

    form = get_inputs(soup)
    action = "https://secure.etecsa.net:8443/EtecsaQueryServlet"
    form['username'] = username
    form['password'] = password
    r = session.post(action, form)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    exp_node = soup.find(string=re.compile("expiración"))
    if not exp_node:
        return False
    return True


def cards_add(username, password):
    username = username
    password = password
    if not verify(username, password):
        return
    with dbm.open(CARDS_DB, "c") as cards_db:
        cards_db[username] = json.dumps({
            'password': password,
        })


def cards_clean(args):
    cards_to_purge = []
    with dbm.open(CARDS_DB, "c") as cards_db:
        for card in cards_db.keys():
            info = json.loads(cards_db[card].decode())
            tl = parse_time(info.get('time_left'))
            if tl == 0:
                cards_to_purge.append(card)
    delete_cards(cards_to_purge)


def cards_rm(usernames):
    delete_cards(usernames)


def cards_info(username):
    global key, r
    username = username
    with dbm.open(CARDS_DB, "c") as cards_db:
        card_info = json.loads(cards_db[username].decode())
        password = card_info['password']

    session = requests.Session()
    try:
        r = session.get("https://secure.etecsa.net:8443/")
    except:
        messagebox.showerror('Error de conexión', 'No se puede acceder al portal')
        return
    soup = bs4.BeautifulSoup(r.text, 'html.parser')

    form = get_inputs(soup)
    action = "https://secure.etecsa.net:8443/EtecsaQueryServlet"
    form['username'] = username
    form['password'] = password
    r = session.post(action, form)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')

    toplevel_info = Toplevel()
    toplevel_info.title("Información de Usuario")
    toplevel_info.resizable(False, False)
    toplevel_info.config(bd='2', background="#333", relief='ridge')
    toplevel_info.transient(raiz)

    ico_err_pass(toplevel_info)

    frame_informacion = Frame(toplevel_info)
    frame_informacion.grid()
    frame_informacion.config(background="#333", relief='ridge', bd='2')

    label_informacion_text = Label(frame_informacion, text="Información"
                                                           "\n_____________________________________________________________________\n\n", font=(TNR, 12))
    label_informacion_text.config(background="#333", fg="grey", justify="left")
    label_informacion_text.grid()

    table = soup.find('table', id='sessioninfo')
    for tr in table.find_all('tr'):
        key, val = tr.find_all('td')
        key = key.text.strip()
        val = val.text.strip().replace('\\', '')
        label_informacion_contenido = Label(frame_informacion, text=key + ' ' + val, font=(A, 16))
        label_informacion_contenido.config(background="#333", fg="#fff", justify="center")
        label_informacion_contenido.grid()

    label_informacion_sesiones = Label(frame_informacion, text="\nSesiones"
                                                               "\n____________________________________________________________________\n\n", font=(TNR, 12))
    label_informacion_sesiones.config(background="#333", fg="grey", justify="left")
    label_informacion_sesiones.grid()
    table = soup.find('table', id='sesiontraza')
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) > 0:
            for cell in tds:
                label_informacion_contenido = Label(frame_informacion, text=cell.text.strip(), font=(A, 16))
                label_informacion_contenido.config(background="#333", fg="#fff", justify="center")
                label_informacion_contenido.grid()

    boton_info = Button(frame_informacion, text='Salir', width='15', height='1', font=(A, 16),
                        command=lambda: salir_top_level_informacion(), borderwidth='1')
    boton_info.grid(padx='3', pady='15')
    ccs_boton(boton_info)
    efecto_boton(boton_info)

    def salir_top_level_informacion():
        toplevel_info.destroy()


################################   Interfaz Principal    #############################################


raiz = Tk()
raiz.title("Control de Sesión de Etecsa")
raiz.resizable(False, False)
ico_err_pass(raiz)
raiz.config(bd="5", background="#333", relief='ridge')

frame_principal = Frame(raiz)
frame_principal.grid()
frame_principal.config(bd='6', background="#333")

label_cuentas_disp = Label(frame_principal, text='Cuentas Disponibles', font=(TNR, 17))
label_cuentas_disp.grid(row=1, column=0, pady=4)
label_cuentas_disp.config(background="#333", foreground="#ffffff", fg="#ffffff", justify="center")

listbox_cuentas = Listbox(frame_principal, width=26, height=8, font=(A, 14), selectmode=SINGLE)
listbox_cuentas.grid(row=2, column=0, padx="5", pady="2")
listbox_cuentas.config(activestyle="none")
ccs_pantalla(listbox_cuentas)
efecto_pantalla(listbox_cuentas)

leer_ruta_usuarios()

mi_frame_temporiz = Frame(raiz)
mi_frame_temporiz.grid()
mi_frame_temporiz.config(bd='5', background="#333")

label_tiempo_de_detencion = Label(mi_frame_temporiz, text='Cronómetro', font=(TNR, 17))
label_tiempo_de_detencion.grid(row=0, column=0, pady=1)
label_tiempo_de_detencion.config(background="#333", fg="#ffffff", justify="center", width="20")

frame_temporizador_principal = Frame(raiz)
frame_temporizador_principal.grid()
frame_temporizador_principal.config(bd='3', background="#333")

pantalla_hora = StringVar(value=f'{valor_temporizador(0)}{valor_temporizador(1)}')
pantalla_p_hora = Entry(frame_temporizador_principal, textvariable=pantalla_hora, width=4, font=(A, 14))
pantalla_p_hora.grid(row=0, column=1, padx="5", pady="2")
ccs_pantalla(pantalla_p_hora)
efecto_pantalla(pantalla_p_hora)

label_espaciador_2 = Label(frame_temporizador_principal, text=':', font=(A, 14))
label_espaciador_2.grid(row=0, column=2)
label_espaciador_2.config(background="#333", fg="#ffffff", justify="center")

pantalla_minutos = StringVar(value=f'{valor_temporizador(2)}{valor_temporizador(3)}')
pantalla_p_minutos = Entry(frame_temporizador_principal, textvariable=pantalla_minutos, width=4, font=(A, 14))
pantalla_p_minutos.grid(row=0, column=3, padx="5", pady="2")
ccs_pantalla(pantalla_p_minutos)
efecto_pantalla(pantalla_p_minutos)

label_espaciador_3 = Label(frame_temporizador_principal, text=':', font=(A, 14))
label_espaciador_3.grid(row=0, column=4)
label_espaciador_3.config(background="#333", fg="#ffffff", justify="center")

pantalla_segundos = StringVar(value=f'{valor_temporizador(4)}{valor_temporizador(5)}')
pantalla_p_segundos = Entry(frame_temporizador_principal, textvariable=pantalla_segundos, width=4, font=(A, 14))
pantalla_p_segundos.grid(row=0, column=5, padx="5", pady="2")
ccs_pantalla(pantalla_p_segundos)
efecto_pantalla(pantalla_p_segundos)

frame_botones = Frame(raiz)
frame_botones.grid()
frame_botones.config(bd='5', background="#333")

boton_agregar_cuenta = Button(frame_botones, text='Agregar\nCuenta', width='10', height='1', font=(UB, 14),
                              command=lambda: agregar_cuenta(), borderwidth='1')
boton_agregar_cuenta.grid(row=0, column=1, padx='10', pady='10', ipadx='5', ipady='4')
ccs_boton(boton_agregar_cuenta)
efecto_boton(boton_agregar_cuenta)

boton_salir = Button(frame_botones, text='Salir', width='10', height='1', font=(UB, 14),
                     command=lambda: salir(), borderwidth='1')
boton_salir.grid(row=2, column=1, padx='10', pady='10', ipadx='5', ipady='4')
ccs_boton(boton_salir)
efecto_boton(boton_salir)

boton_conectar = Button(frame_botones, text='Conectar', width='10', height='1', font=(UB, 14),
                        command=lambda: conectar(), borderwidth='1')
boton_conectar.grid(row=0, column=0, padx='10', pady='10', ipadx='5', ipady='4')
ccs_boton(boton_conectar)
efecto_boton(boton_conectar)

boton_eliminar_cuenta = Button(frame_botones, text='Eliminar\nCuenta', width='10', height='1', font=(UB, 14),
                               command=lambda: eliminar_cuenta(), borderwidth='1')
boton_eliminar_cuenta.grid(row=1, column=1, padx='1', pady='10', ipadx='5', ipady='4')
ccs_boton(boton_eliminar_cuenta)
efecto_boton(boton_eliminar_cuenta)

boton_informacion = Button(frame_botones, text='Información\nUsuario', width='10', height='1', font=(UB, 14),
                           command=lambda: informacion(), borderwidth='1')
boton_informacion.grid(row=1, column=0, padx='10', pady='10', ipadx='5', ipady='4')
ccs_boton(boton_informacion)
efecto_boton(boton_informacion)

boton_opciones = Button(frame_botones, text='Opciones', width='10', height='1', font=(UB, 14),
                        command=lambda: opciones(), borderwidth='1')
boton_opciones.grid(row=2, column=0, padx='10', pady='10', ipadx='5', ipady='4')
ccs_boton(boton_opciones)
efecto_boton(boton_opciones)


def conexion_activa(username):
    if os.path.exists(LOGOUT_URL_FILE):
        minfo = messagebox.askyesnocancel('Información', 'Ya existe una conexión activa:\n\nDesea retomar la conexión ('
                                                         'Sí)\nCerrar la conexión (No) '
                                                         '\nIgnorar la advertencia (Cancelar) ?')
        if minfo == True:

            login_time = int(time.time())

            tl = time_left(username)

            top_level_sesion_rec = Toplevel()
            top_level_sesion_rec.resizable(False, False)
            top_level_sesion_rec.title('Bienvenido (Sesión recuperada)')
            top_level_sesion_rec.config(bd="5", background="#333", relief='ridge')
            top_level_sesion_rec.transient(raiz)

            frame_conectado_rec = Frame(top_level_sesion_rec)
            frame_conectado_rec.grid(row=0, column=0)
            frame_conectado_rec.config(bd='5', background="#333")

            label_info_rec = Label(frame_conectado_rec, font=(UB, 18),
                                   text='Estado: Conectado\n(Sesión recuperada)')
            label_info_rec.grid(row=0, column=0, padx='1', pady='15')
            label_info_rec.config(background="#333", fg="#fff", justify="center")

            label_info_usuario_rec = Label(frame_conectado_rec, font=(UB, 16), text=f'Usuario: {username}')
            label_info_usuario_rec.grid(row=1, column=0, padx='1', pady='2')
            label_info_usuario_rec.config(background="#333", fg="#fff", justify="center")

            label_info_tiempo_disp_rec = Label(frame_conectado_rec, font=(UB, 16))
            label_info_tiempo_disp_rec.grid(row=2, column=0, padx='1', pady='2')
            label_info_tiempo_disp_rec.config(background="#333", fg="#fff", justify="center")

            def tiempo_mostrado():

                tiempo = ("\rTiempo consumido: {} ".format(human_secs(int(time.time()) - login_time)))
                label_info_tiempo_disp_rec.config(text=tiempo)
                label_info_tiempo_disp_rec.after(1000, tiempo_mostrado)

            tiempo_mostrado()

            label_info_tiempo_disponible_rec = Label(frame_conectado_rec, font=(UB, 16),
                                                     text=f'Tiempo disponible: {tl}')
            label_info_tiempo_disponible_rec.grid(row=3, column=0, padx='1', pady='10')
            label_info_tiempo_disponible_rec.config(background="#333", fg="#fff", justify="center")

            frame_conectado_botones_rec = Frame(top_level_sesion_rec)
            frame_conectado_botones_rec.grid(row=1, column=0)
            frame_conectado_botones_rec.config(bd='10', background="#333")

            boton_actualizar_frame_conectado_rec = Button(frame_conectado_botones_rec, text='Actualizar', width='12',
                                                          height='1',
                                                          font=(UB, 14),
                                                          command=lambda: actualizar_tiempo_rec())
            boton_actualizar_frame_conectado_rec.grid(row=0, column=0, padx='6', pady='5')
            ccs_boton(boton_actualizar_frame_conectado_rec)
            efecto_boton(boton_actualizar_frame_conectado_rec)

            boton_desconectar_frame_conectado_rec = Button(frame_conectado_botones_rec, text='Desconectar', width='12',
                                                           height='1',
                                                           font=(UB, 14),
                                                           command=lambda: desconectar_rec())
            boton_desconectar_frame_conectado_rec.grid(row=0, column=1, padx='6', pady='5')
            ccs_boton(boton_desconectar_frame_conectado_rec)
            efecto_boton(boton_desconectar_frame_conectado_rec)

            def actualizar_tiempo_rec():
                tl = time_left(username)
                label_info_tiempo_disponible_rec.config(text=f'Tiempo disponible: {tl}')

            def desconectar_rec():

                try:
                    down([])
                except:
                    messagebox.showerror('Error de desconexión', 'Hubo un error durante la desconexión')
                    return

                frame_conectado_rec.destroy()
                frame_conectado_botones_rec.destroy()

                now = int(time.time())

                frame_desconectar_rec = Frame(top_level_sesion_rec)
                frame_desconectar_rec.grid()
                frame_desconectar_rec.config(bd='5', background="#333")

                label_cerrar_sesion_rec = Label(frame_desconectar_rec, font=(UB, 18),
                                                text='Usted ha cerrado con éxito su sesión.')
                label_cerrar_sesion_rec.grid(row=0, column=0, padx='1', pady='15')
                label_cerrar_sesion_rec.config(background="#333", fg="#fff", justify="center")

                label_tiempo_conexion_rec = Label(frame_desconectar_rec, font=(UB, 16),
                                                  text=f"Tiempo de conexión: {human_secs(now - login_time)}")
                label_tiempo_conexion_rec.grid(row=1, column=0, padx='1', pady='10')
                label_tiempo_conexion_rec.config(background="#333", fg="#fff", justify="center")

                tl = time_left(username)

                label_tiempo_restante = Label(frame_desconectar_rec, font=(UB, 16), text=f"Tiempo restante: {tl}")
                label_tiempo_restante.grid(row=2, column=0, padx='1', pady='10')
                label_tiempo_restante.config(background="#333", fg="#fff", justify="center")

                boton_salir = Button(frame_desconectar_rec, text='Salir', width='10', height='1', font=(UB, 14),
                                     command=lambda: salir_3())
                boton_salir.grid(row=3, column=0, padx='1', pady='20')
                ccs_boton(boton_salir)
                efecto_boton(boton_salir)

                log(f"Tiempo de conexion: {human_secs(now - login_time)}")
                log(f"Tiempo restante: {tl}")
                log("Se ha desconectado correctamente con una sesión recuperada\n")

                def salir_3():
                    top_level_sesion_rec.destroy()

        elif minfo == False:
            down([])

        elif minfo == None:
            pass

        else:
            pass


if os.path.isfile(ruta_usuario_conectado):
    with open(ruta_usuario_conectado, "r") as input:
        user = input.readline()
    conexion_activa(user)


def obtener_usuario_selec():
    for item in listbox_cuentas.curselection():
        a3 = listbox_cuentas.get(item)
        usuario_2 = [a3]
        usuario_final = usuario_2[0]
        return usuario_final


def opciones():
    toplevel_opciones = Toplevel()
    toplevel_opciones.title("Opciones")
    toplevel_opciones.resizable(False, False)
    toplevel_opciones.config(bd="5", background="#333", relief='ridge')
    toplevel_opciones.transient(raiz)

    ico_err_pass(toplevel_opciones)

    frame_opciones = Frame(toplevel_opciones)
    frame_opciones.grid()
    frame_opciones.config(bd="5", background="#333")

    boton_eliminar_datos = Button(frame_opciones, text='Eliminar\nDatos', width='11', height='1', font=(TNR, 14),
                                  command=lambda: eliminar_datos(), borderwidth='1')
    boton_eliminar_datos.grid(row=0, column=0, padx='10', pady='10', ipadx='5', ipady='4')
    ccs_boton(boton_eliminar_datos)
    efecto_boton(boton_eliminar_datos)

    boton_activar_status = Button(frame_opciones, text='Estadísticas\nde Red', width='11', height='1',
                                  font=(TNR, 14),
                                  command=lambda: threading.Thread(target=activar_status).start(), borderwidth='1')
    boton_activar_status.grid(row=0, column=1, padx='10', pady='10', ipadx='5', ipady='4')
    ccs_boton(boton_activar_status)
    efecto_boton(boton_activar_status)

    boton_establecer_temporizado = Button(frame_opciones, text='Establecer\nTemporizador', width='11', height='1',
                                          font=(TNR, 14),
                                          command=lambda: temporizado_por_defecto(), borderwidth='1')
    boton_establecer_temporizado.grid(row=1, column=0, padx='10', pady='10', ipadx='5', ipady='4')
    ccs_boton(boton_establecer_temporizado)
    efecto_boton(boton_establecer_temporizado)

    boton_salir_opciones = Button(frame_opciones, text="Salir", width='11', height='1', font=(TNR, 14),
                                  command=lambda: salir_opciones(), borderwidth='1')
    boton_salir_opciones.grid(row=2, column=1, padx='10', pady='10', ipadx='5', ipady='4')
    ccs_boton(boton_salir_opciones)
    efecto_boton(boton_salir_opciones)

    boton_acerca_desarollador = Button(frame_opciones, text="Acerca de", width='11', height='1', font=(TNR, 14),
                                       relief='solid',
                                       command=lambda: mostrar_info_des(), borderwidth='1')
    boton_acerca_desarollador.grid(row=1, column=1, padx='10', pady='10', ipadx='5', ipady='4')
    ccs_boton(boton_acerca_desarollador)
    efecto_boton(boton_acerca_desarollador)

    boton_calculadora_descarga = Button(frame_opciones, text="Calculadora", width='11', height='1', font=(TNR, 14),
                                       relief='solid',
                                       command=lambda: calculadora_descarga(), borderwidth='1')
    boton_calculadora_descarga.grid(row=2, column=0, padx='10', pady='10', ipadx='5', ipady='4')
    ccs_boton(boton_calculadora_descarga)
    efecto_boton(boton_calculadora_descarga)


    def calculadora_descarga():
        def convertir_a_bits(segundos, tamaño, velocidad):
            unidades_tiempo = {'Seg': 1, 'Min': 60, 'Hor': 3600}
            unidades_datos = {'KB': 8 * 10**3, 'MB': 8 * 10**6, 'GB': 8 * 10**9}
            u_t = unidades_tiempo[tiempo_unit.get()]
            u_d = unidades_datos[tamano_unit.get()]
            u_v = unidades_datos[velocidad_unit.get()]
            return segundos * u_t, tamaño * u_d, velocidad * u_v

        def calcular():
            t = tiempo_var.get().strip()
            s = tamano_var.get().strip()
            v = velocidad_var.get().strip()
            if [bool(t), bool(s), bool(v)].count(True) != 2:
                messagebox.showerror("Error", "Introduce exactamente dos valores para calcular el tercero.")
                return
            try:
                t_val = float(t) if t else None
                s_val = float(s) if s else None
                v_val = float(v) if v else None
            except ValueError:
                messagebox.showerror("Error", "Valores numéricos inválidos.")
                return

            tb, sb, vb = convertir_a_bits(
                t_val or 0,
                s_val or 0,
                v_val or 0
            )

            if t_val is None:
                resultado_s = sb / vb
                factor = {'Seg':1,'Min':60,'Hor':3600}[tiempo_unit.get()]
                tiempo_var.set(f"{(resultado_s/factor):.2f}")
            elif s_val is None:
                resultado_bits = vb * tb
                factor = {'KB':8*10**3,'MB':8*10**6,'GB':8*10**9}[tamano_unit.get()]
                tamano_var.set(f"{(resultado_bits/factor):.2f}")
            else:
                resultado_bits_s = sb / tb
                factor = {'KB':8*10**3,'MB':8*10**6,'GB':8*10**9}[velocidad_unit.get()]
                velocidad_var.set(f"{(resultado_bits_s/factor):.2f}")

        toplevel = Toplevel()
        toplevel.title("Cálculo Tiempo↔Tamaño↔Velocidad")
        toplevel.resizable(False, False)
        toplevel.config(bd=5, background="#333", relief='ridge')
        toplevel.transient(raiz)
        ico_err_pass(toplevel)

        frame = Frame(toplevel, bd=5, background="#333")
        frame.grid(row=0, column=0, padx=10, pady=10)

        tiempo_var = StringVar(value="")
        tamano_var = StringVar(value="")
        velocidad_var = StringVar(value="")
        tiempo_unit = StringVar(value="Seg")
        tamano_unit = StringVar(value="MB")
        velocidad_unit = StringVar(value="MB")

        def fila(label_txt, var, unit_var, unidades, row):
            lbl = Label(frame, text=label_txt, font=(TNR, 14), background="#333", fg="#fff")
            lbl.grid(row=row, column=0, sticky="e", padx=5, pady=5)
            entry = Entry(frame, textvariable=var, width=8, font=(A, 14))
            entry.grid(row=row, column=1, padx=5, pady=5)
            ccs_pantalla(entry)
            efecto_pantalla(entry)
            om = OptionMenu(frame, unit_var, *unidades)
            om.config(width=5, font=(A,12), bg="#333", fg="#fff", activebackground="#444", highlightthickness=0)
            om["menu"].config(bg="#333", fg="#fff", activebackground="#444")
            om.grid(row=row, column=2, padx=5, pady=5)
            return entry

        fila("Tiempo",    tiempo_var,    tiempo_unit,    ['Seg','Min','Hor'],  0)
        fila("Tamaño",    tamano_var,    tamano_unit,    ['KB','MB','GB'],      1)
        fila("Velocidad", velocidad_var, velocidad_unit, ['KB','MB','GB'],      2)

        fb = Frame(toplevel, bd=5, background="#333")
        fb.grid(row=1, column=0, pady=(0,10))

        btn_calc = Button(fb, text='Calcular', width=12, height=1, font=(TNR,14), command=calcular)
        btn_calc.grid(row=0, column=0, padx=10)
        ccs_boton(btn_calc)
        efecto_boton(btn_calc)

        btn_salir = Button(fb, text='Salir', width=12, height=1, font=(TNR,14), command=toplevel.destroy)
        btn_salir.grid(row=0, column=1, padx=10)
        ccs_boton(btn_salir)
        efecto_boton(btn_salir)


    def mostrar_info_des():
        toplevel_info_des = Toplevel()
        toplevel_info_des.title("Acerca de")
        toplevel_info_des.resizable(False, False)
        toplevel_info_des.config(bd="5", background="#333", relief='ridge')
        # toplevel_info_des.transient(raiz)
        ico_err_pass(toplevel_info_des)

        frame_acerca_de = Frame(toplevel_info_des)
        frame_acerca_de.grid()
        frame_acerca_de.config(bd="5", background="#333")

        label_info_acerca_de = Label(frame_acerca_de, text="Control de Sesión de Etecsa\nCSE", font=(A, 12))
        label_info_acerca_de.config(background="#333", fg="#0cb7f2", justify="left")
        label_info_acerca_de.grid(row=0, column=0, padx='1', pady='10')

        label_version = Label(frame_acerca_de, text="Version\n________________________________________", font=(TNR, 11))
        label_version.config(background="#333", fg="grey", justify="left")
        label_version.grid(row=1, column=0, padx='1', pady='1')

        label_espacio = Label(frame_acerca_de, text="v0.9.0\n[32-64 bit]", font=(A, 12))
        label_espacio.config(background="#333", fg="#fff", justify="center")
        label_espacio.grid(row=2, column=0, padx='1', pady='10')

        label_copyright = Label(frame_acerca_de, text="Copyright\n________________________________________",
                                font=(TNR, 11))
        label_copyright.config(background="#333", fg="grey", justify="left")
        label_copyright.grid(row=3, column=0, padx='1', pady='1')

        label_copyr = Label(frame_acerca_de, text="Copyright(c) 2020 Tabares, Inc.\n\nTodos los derechos"
                                                  " reservados.", font=(A, 11))
        label_copyr.config(background="#333", fg="#fff", justify="left")
        label_copyr.grid(row=4, column=0, padx='1', pady='10')

        boton_acerca_desarollador.config(state=DISABLED)
        toplevel_info_des.wait_window()
        boton_acerca_desarollador.config(state=NORMAL)

    def salir_opciones():
        toplevel_opciones.destroy()

    def temporizado_por_defecto():
        toplevel_temporizador = Toplevel()
        toplevel_temporizador.title("Temporizador")
        toplevel_temporizador.resizable(False, False)
        toplevel_temporizador.config(bd="5", background="#333", relief='ridge')
        toplevel_temporizador.transient(raiz)

        ico_err_pass(toplevel_temporizador)

        frame_temporizador = Frame(toplevel_temporizador)
        frame_temporizador.grid(row=0, column=0)
        frame_temporizador.config(bd="5", background="#333")

        label_info_temporizador = Label(frame_temporizador, text='Seleccione el temporizador que se usará por defecto',
                                        font=(TNR, 17))
        label_info_temporizador.grid(row=0, column=0, padx='1', pady='7')
        label_info_temporizador.config(background="#333", fg="#fff", justify="center")

        frame_temporizador_pantalla = Frame(toplevel_temporizador)
        frame_temporizador_pantalla.grid(row=1, column=0)
        frame_temporizador_pantalla.config(background="#333")

        pantalla_hora_3 = StringVar(value='00')
        pantalla_h_3 = Entry(frame_temporizador_pantalla, textvariable=pantalla_hora_3, width=4, font=(A, 14))
        pantalla_h_3.grid(row=0, column=1, padx="5", pady="2")
        ccs_pantalla(pantalla_h_3)
        efecto_pantalla(pantalla_h_3)

        label_temp_3 = Label(frame_temporizador_pantalla, text=':', font=(A, 14))
        label_temp_3.grid(row=0, column=2)
        label_temp_3.config(background="#333", fg="#fff", justify="center")

        pantalla_minutos_3 = StringVar(value='00')
        pantalla_m_3 = Entry(frame_temporizador_pantalla, textvariable=pantalla_minutos_3, width=4, font=(A, 14))
        pantalla_m_3.grid(row=0, column=3, padx="5", pady="2")
        ccs_pantalla(pantalla_m_3)
        efecto_pantalla(pantalla_m_3)

        label_temp_3 = Label(frame_temporizador_pantalla, text=':', font=(A, 14))
        label_temp_3.grid(row=0, column=4)
        label_temp_3.config(background="#333", fg="#fff", justify="center")

        pantalla_segundos_3 = StringVar(value='00')
        pantalla_s_3 = Entry(frame_temporizador_pantalla, textvariable=pantalla_segundos_3, width=4, font=(A, 14))
        pantalla_s_3.grid(row=0, column=5, padx="5", pady="2")
        ccs_pantalla(pantalla_s_3)
        efecto_pantalla(pantalla_s_3)

        frame_temporizador_boton = Frame(toplevel_temporizador)
        frame_temporizador_boton.grid(row=2, column=0)
        frame_temporizador_boton.config(bd="5", background="#333")

        boton_temporizador = Button(frame_temporizador_boton, text='Aplicar', width='12', height='1',
                                    font=(TNR, 14),
                                    command=lambda: aplicar_temporizador())
        boton_temporizador.grid(row=2, column=0, padx='1', pady='10')
        ccs_boton(boton_temporizador)
        efecto_boton(boton_temporizador)

        def aplicar_temporizador():

            try:
                err_temporiz(pantalla_hora_3, pantalla_minutos_3, pantalla_segundos_3)
            except ZeroDivisionError:
                return

            horas = pantalla_hora_3.get()
            if horas == '':
                horas = '00'
            minutos = pantalla_minutos_3.get()
            if minutos == '':
                minutos = '00'
            segundos = pantalla_segundos_3.get()
            if minutos == '':
                minutos = '00'
            total_tiempo = f'{horas}{minutos}{segundos}'
            with open(ruta_temporizador, "w") as output:
                output.write(total_tiempo)
            messagebox.showinfo('Información', 'Se ha establecido un nuevo temporizador por defecto')

            pantalla_hora.set(horas)
            pantalla_minutos.set(minutos)
            pantalla_segundos.set(segundos)

            toplevel_temporizador.destroy()

        boton_establecer_temporizado.config(state=DISABLED)
        toplevel_temporizador.wait_window()
        boton_establecer_temporizado.config(state=NORMAL)

    def activar_status():

        frame_activar_status = Frame(raiz)
        frame_activar_status.grid(row=5, column=0)
        frame_activar_status.config(bd='2', background="#333")

        boton_activar_status.config(state=DISABLED)

        status_label = Label(frame_activar_status, font=(A, 13), foreground="#fff", background="#333")
        status_label.grid(row=0, column=0)

        estado_label = Label(frame_activar_status, font=(A, 13), foreground='#fff', background="#333")
        estado_label.grid(row=1, column=0)

        estado_label_2 = Label(frame_activar_status, font=(A, 13), foreground='#fff', background="#333")
        estado_label_2.grid(row=2, column=0)
        
        estado_label_3 = Label(frame_activar_status, font=(A, 13), foreground='#fff', background="#333")
        estado_label_3.grid(row=3, column=0)

        ping_label = Label(frame_activar_status, font=(A, 13), foreground='#fff', background="#333")
        ping_label.grid(row=4, column=0)

        def comprobar_velocidad():

            io = psutil.net_io_counters()
            bytes_sent, bytes_recv = io.bytes_sent, io.bytes_recv
            time.sleep(1)
            io_2 = psutil.net_io_counters()
            us, ds = io_2.bytes_sent - bytes_sent, io_2.bytes_recv - bytes_recv
            vel_subida = get_size(us)
            vel_bajada = get_size(ds)
            status_label.config(text=f'Bajada: {vel_bajada}     Subida: {vel_subida}', fg='#965ccb')

            def mult_hilo_2():
                mult_hilo_2 = threading.Thread(target=comprobar_velocidad)
                mult_hilo_2.start()

            status_label.after(1000, mult_hilo_2)

        def comprobar_conexion():

            session = requests.Session()

            try:
                session.head("https://www.google.com/", timeout=8)
            except:
                estado = "Sin conexión a internet"
                estado_label.config(text=estado, fg='#FF5A5F')
            else:
                estado = "Con conexión a internet"
                estado_label.config(text=estado, fg='#5ccb5f')

            try:
                session.head("https://www.sld.cu/", timeout=8)
            except:
                estado = "Sin conexión a red nacional"
                estado_label_2.config(text=estado, fg='#FF5A5F')
            else:
                estado = "Con conexión a red nacional"
                estado_label_2.config(text=estado, fg='#5ccb5f')

            try:
                session.head("https://secure.etecsa.net:8443/", timeout=8)
            except:
                estado = "Sin conexión al portal"
                estado_label_3.config(text=estado, fg='#FF5A5F')
            else:
                estado = "Con conexión al portal"
                estado_label_3.config(text=estado, fg='#5ccb5f')

            session.close()

            def mult_hilo_1():
                mult_hilo_1 = threading.Thread(target=comprobar_conexion)
                mult_hilo_1.start()

            estado_label.after(10000, mult_hilo_1)

        def comprobar_ping_pkts():
            import ping3
            global end_time
            global start_time
            host = 'www.google.com'
            num_pings = 5
            ttl = 64  # Time To Live (TTL) para el paquete ICMP
            seq_num = 0
            num_received = 0
            total_time = 0

            for i in range(num_pings):
                seq_num += 1
                start_time = time.time()
                response_time = ping3.ping(host, ttl=ttl, seq=seq_num)
                end_time = time.time()
                if response_time is not None:
                    num_received += 1
                    total_time += response_time

            packet_loss = (num_pings - num_received) / num_pings * 100

            packts = f'Pkts: Env = {num_pings} Rec = {num_received} Perd = {num_pings - num_received} ({packet_loss}%)'
            ping_real = int((end_time - start_time) * 1000)
            ping = f"Ping = {ping_real} ms"

            if int(ping_real) > 200 or packet_loss > 20.0:
                ping_label.config(text=f"{packts} \n {ping}", fg='#FF5A5F')
            else:
                ping_label.config(text=f"{packts} \n {ping}", fg='#5ccb5f')

            def mult_hilo_3():
                mult_hilo_3 = threading.Thread(target=comprobar_ping_pkts)
                mult_hilo_3.start()

            status_label.after(1000, mult_hilo_3)

        comprobar_velocidad()
        comprobar_conexion()
        comprobar_ping_pkts()

    def eliminar_datos():
        minfo_2 = messagebox.askyesno('Información', 'Está seguro que desea eliminar los datos guardados')

        if minfo_2 == True:
            try:
                try:
                    os.remove(f"{ruta_ejecutable}/cards.bak")
                except FileNotFoundError:
                    pass
                try:
                    os.remove(f"{ruta_ejecutable}/cards.dat")
                except FileNotFoundError:
                    pass
                try:
                    os.remove(f"{ruta_ejecutable}/cards.dir")
                except FileNotFoundError:
                    pass
                try:
                    logfile.close()
                    os.remove(f"{ruta_ejecutable}/connections.log")
                except FileNotFoundError:
                    pass
                try:
                    os.remove(f"{ruta_ejecutable}/usuarios.txt")
                except FileNotFoundError:
                    pass
                try:
                    os.remove(f"{ruta_ejecutable}/usuario_actual.txt")
                except FileNotFoundError:
                    pass
                try:
                    os.remove(f"{ruta_ejecutable}/logout_url")
                except FileNotFoundError:
                    pass
                try:
                    os.remove(f"{ruta_ejecutable}/temporizador.txt")
                except FileNotFoundError:
                    pass
                try:
                    os.remove(f"{ruta_ejecutable}/attribute_uuid")
                except FileNotFoundError:
                    pass
                messagebox.showinfo('Información', 'Se eliminaron todos los datos')
            except Exception as e:
                messagebox.showerror("Error", str(e))
                pass
            raiz.destroy()
        else:
            pass

    boton_opciones.config(state=DISABLED)
    toplevel_opciones.wait_window()
    boton_opciones.config(state=NORMAL)


def informacion():
    if obtener_usuario_selec() == None:
        messagebox.showerror("Error", "Debe seleccionar una cuenta")
        return
    cards_info(obtener_usuario_selec())


def conectar():
    if obtener_usuario_selec() == None:
        messagebox.showerror("Error", "Debe seleccionar una cuenta")
        return
    up(obtener_usuario_selec())


def salir():
    raiz.destroy()


def eliminar_cuenta():
    if obtener_usuario_selec() == None:
        messagebox.showerror("Error", "Debe seleccionar una cuenta")
    fmes = messagebox.askyesno('Eliminar cuenta', '¿ Está seguro que desea eliminar esta cuenta ?')
    if fmes == True:
        for item in listbox_cuentas.curselection():
            a2 = listbox_cuentas.get(item)
            p = [a2]
            listbox_cuentas.delete(item)
            with open(ruta_usuarios, "r") as input:
                with open("bb.txt", "w") as output:
                    for line in input:
                        if p[0] not in line.strip(""):
                            output.write(line)
            os.replace('bb.txt', 'usuarios.txt')
    else:
        return


def agregar_cuenta():
    toplevel_agregar_cuenta = Toplevel()
    toplevel_agregar_cuenta.title("Agregar Usuario")
    toplevel_agregar_cuenta.resizable(False, False)
    toplevel_agregar_cuenta.config(bd="5", background="#333", relief='ridge')
    toplevel_agregar_cuenta.transient(raiz)

    ico_err_pass(toplevel_agregar_cuenta)

    label_usuario = Label(toplevel_agregar_cuenta, text='Usuario', font=(TNR, 17))
    label_usuario.grid(row=0, column=0)
    label_usuario.config(background="#333", fg="#fff", justify="center")

    pantallita_usuario = StringVar()
    pantalla_usuario = Entry(toplevel_agregar_cuenta, textvariable=pantallita_usuario, width=26, font=(A, 14))
    pantalla_usuario.grid(row=1, column=0, padx="5", pady="2")
    ccs_pantalla(pantalla_usuario)
    efecto_pantalla(pantalla_usuario)
    pantalla_usuario.focus()

    label_contras = Label(toplevel_agregar_cuenta, text='Contraseña', font=(A, 17))
    label_contras.grid(row=2, column=0)
    label_contras.config(background="#333", fg="#fff", justify="center")

    pantallita_contra = StringVar()
    pantalla_contra = Entry(toplevel_agregar_cuenta, textvariable=pantallita_contra, width=26, font=(A, 14))
    pantalla_contra.grid(row=3, column=0, padx="5", pady="2")
    pantalla_contra.config(show='*')
    ccs_pantalla(pantalla_contra)
    efecto_pantalla(pantalla_contra)

    boton_guardar = Button(toplevel_agregar_cuenta, text='Guardar', width='10', height='1', font=(TNR, 14),
                           command=lambda: guardar(), borderwidth='1')
    boton_guardar.grid(row=5, column=0, padx='1', pady='10')
    ccs_boton(boton_guardar)
    efecto_boton(boton_guardar)

    boton_salir_cuentas = Button(toplevel_agregar_cuenta, text='Salir', width='10', height='1', font=(TNR, 14),
                                 command=lambda: salir_cuentas(), borderwidth='1')
    boton_salir_cuentas.grid(row=6, column=0, padx='1', pady='10')
    ccs_boton(boton_salir_cuentas)
    efecto_boton(boton_salir_cuentas)

    boton_mostrar_pass = Button(toplevel_agregar_cuenta, width='0', height='0', font=(C, 12),
                                command=lambda: mostrar_contra(), text='Mostrar Contraseña', justify='left',
                                background="#FFFFFF")
    boton_mostrar_pass.grid(row=4, column=0, padx='1', pady='10')
    ccs_boton(boton_mostrar_pass)
    efecto_boton(boton_mostrar_pass)

    def mostrar_contra():
        pantalla_contra.config(show='')
        boton_ocultar_pass = Button(toplevel_agregar_cuenta, width='0', height='0', font=(C, 12),
                                    command=lambda: ocultar_contra(), text='Ocultar Contraseña', justify='left')
        boton_ocultar_pass.grid(row=4, column=0, padx='1', pady='10')
        ccs_boton(boton_ocultar_pass)
        efecto_boton(boton_ocultar_pass)

    def ocultar_contra():
        pantalla_contra.config(show='*')

        boton_mostrar_pass = Button(toplevel_agregar_cuenta, width='0', height='0', font=(C, 12),
                                    command=lambda: mostrar_contra(), text='Mostrar Contraseña', justify='left')
        boton_mostrar_pass.grid(row=4, column=0, padx='1', pady='10')
        ccs_boton(boton_mostrar_pass)
        efecto_boton(boton_mostrar_pass)

    def guardar():
        usuario = pantallita_usuario.get()
        password = pantallita_contra.get()
        cards_add(usuario, password)

        if os.path.isfile(ruta_usuarios) == False:
            usuario_txt = open(ruta_usuarios, 'w')
        if verify(usuario, password):
            comp = True
            with open(ruta_usuarios, "r") as input:

                for line in input:
                    if usuario in line.strip(""):
                        messagebox.showerror('Error de cuenta', 'Esa cuenta ya existe')
                        comp = False

            if comp:
                listbox_cuentas.insert(0, usuario)
                usuario_txt = open(ruta_usuarios, 'a')
                usuario_txt.write(usuario + '\n')

                messagebox.showinfo('Información', 'Se agregó la cuenta exitosamente')

                pantallita_usuario.set('')
                pantallita_contra.set('')

        if not verify(usuario, password):
            messagebox.showerror('Error de credenciales', 'El usuario o la contraseña son incorrectos')

    def salir_cuentas():
        toplevel_agregar_cuenta.destroy()

    boton_agregar_cuenta.config(state=DISABLED)
    toplevel_agregar_cuenta.wait_window()
    boton_agregar_cuenta.config(state=NORMAL)


raiz.mainloop()
