import ctypes
import keyboard

# estrutura de cor do windows
class RAMP(ctypes.Structure):
    _fields_ = [("Red", ctypes.c_ushort * 256),
                ("Green", ctypes.c_ushort * 256),
                ("Blue", ctypes.c_ushort * 256)]

# função para setar gamma
def set_gamma(gamma_value):
    hdc = ctypes.windll.user32.GetDC(0)
    ramp = RAMP()
    for i in range(256):
        val = min(int((i / 255.0) ** gamma_value * 65535 + 0.5), 65535)
        ramp.Red[i] = ramp.Green[i] = ramp.Blue[i] = val
    ctypes.windll.gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(ramp))

# valores de gamma
gamma_total = 1.8  # gamma escuro
gamma_medio = 2.2  # gamma normal

estado = False  # estado atual do gamma

# função para alternar
def alternar_gamma():
    global estado
    if estado:
        set_gamma(gamma_medio)
    else:
        set_gamma(gamma_total)
    estado = not estado

# atalho
keyboard.add_hotkey('F10', alternar_gamma)

print("Pressione F10 para alternar gamma. Feche a janela para sair.")
keyboard.wait()
