import tkinter as tk
from tkinter import messagebox
import serial
import serial.tools.list_ports

class USBRelayApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Connexion à la carte relais USB")

        tk.Label(master, text="Port COM :").grid(row=0, column=0, padx=5, pady=5)

        # Liste déroulante des ports disponibles
        self.ports = self.get_serial_ports()
        self.port_var = tk.StringVar()
        if self.ports:
            self.port_var.set(self.ports[0])
        else:
            self.port_var.set("Aucun port détecté")

        self.port_menu = tk.OptionMenu(master, self.port_var, *self.ports)
        self.port_menu.grid(row=0, column=1, padx=5, pady=5)

        self.refresh_button = tk.Button(master, text="🔄 Rafraîchir", command=self.refresh_ports)
        self.refresh_button.grid(row=0, column=2, padx=5, pady=5)

        self.connect_button = tk.Button(master, text="Se connecter", command=self.connect)
        self.connect_button.grid(row=1, column=0, columnspan=3, pady=5)

        self.ser = None
        self.relaynumber = 0
        self.current_state = 0  # état actif actuel

        # Libellés des 16 états
        self.state_labels = [
            "Mode REPOS",     # 0000
            "",               # 0001
            "",               # 0010
            "Demmarage extracteurs",  # 0011
            "ALN+NAV",        # 0100
            "ALCM+NAV",       # 0101
            "",               # 0110
            "ALIM 21V",       # 0111
            "ALIM 24V",       # 1000
            "ALIM 28V",       # 1001
            "ALIM 30V",       # 1010
            "Mise hors tension", # 1011
            "Arret extracteurs",  # 1100
            "Lecture DCI",    # 1101
            "",               # 1110
            "Fin d'essai"     # 1111
        ]

    def get_serial_ports(self):
        """Retourne une liste des ports COM disponibles"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def refresh_ports(self):
        """Met à jour la liste des ports COM"""
        self.ports = self.get_serial_ports()
        menu = self.port_menu["menu"]
        menu.delete(0, "end")
        for p in self.ports:
            menu.add_command(label=p, command=lambda value=p: self.port_var.set(value))
        if self.ports:
            self.port_var.set(self.ports[0])
        else:
            self.port_var.set("Aucun port détecté")

    def connect(self):
        port = self.port_var.get()
        if port == "Aucun port détecté":
            messagebox.showerror("Erreur", "Aucun port COM disponible")
            return
        try:
            self.ser = serial.Serial(port, 9600, timeout=1)
            if self.init_board():
                messagebox.showinfo("Succès", f"Connecté à {port} ({self.relaynumber} relais)")
                self.show_relay_window()
            else:
                messagebox.showerror("Erreur", "Initialisation de la carte échouée")
                self.ser.close()
                self.ser = None
        except serial.SerialException:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir {port}")

    def send(self, byte, delay_ms=0.05):
        self.ser.write(bytes([byte]))
        self.ser.flush()
        if delay_ms > 0:
            import time
            time.sleep(delay_ms)

    def recv(self, n):
        return self.ser.read(n)

    def init_board(self):
        self.send(0x50, 0.2)
        resp = self.recv(1)
        if len(resp) != 1:
            return False
        val = resp[0]
        if val == 0xad:
            self.relaynumber = 2
        elif val == 0xab:
            self.relaynumber = 4
        elif val == 0xac:
            self.relaynumber = 8
        else:
            return False
        self.send(0x51, 0.01)
        self.send(0xff, 0.01)
        return True

    def send_state(self, state):
        """state = entier (0 à 15) représentant la combinaison des 4 relais"""
        self.current_state = state
        to_send = state
        if self.relaynumber > 2:
            to_send = (~state) & 0xFF
        self.send(to_send, 0.05)
        self.update_button_colors()

    def update_button_colors(self):
        """Met à jour les couleurs en fonction de l'état actif"""
        for i, btn in enumerate(self.relay_buttons):
            if i == self.current_state:
                btn.config(bg="green")
            else:
                btn.config(bg="red")

    def show_relay_window(self):
        relay_win = tk.Toplevel(self.master)
        relay_win.title("Contrôle des relais (4 bits)")

        self.relay_buttons = []
        for i in range(16):
            label = self.state_labels[i] if self.state_labels[i] else format(i, '04b')
            btn = tk.Button(relay_win, text=label, width=20, height=2, bg="red",
                            command=lambda val=i: self.send_state(val))
            btn.grid(row=i // 4, column=i % 4, padx=5, pady=5)
            self.relay_buttons.append(btn)

        # Bouton de déconnexion
        disconnect_btn = tk.Button(relay_win, text="Déconnecter", bg="orange",
                                   command=lambda: self.disconnect(relay_win))
        disconnect_btn.grid(row=4, column=0, columnspan=4, pady=10)

        self.update_button_colors()

    def disconnect(self, window):
        if self.ser and self.ser.is_open:
            self.ser.close()
        window.destroy()
        messagebox.showinfo("Info", "Déconnecté de la carte relais")

if __name__ == "__main__":
    root = tk.Tk()
    app = USBRelayApp(root)
    root.mainloop()
