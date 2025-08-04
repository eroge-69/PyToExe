# CONFIGURACIÓ DEL SCRIPT
# Aquí pots ajustar les opcions de forma senzilla. Només canvia els valors segons les teves necessitats.

ACTIVA_SCRIPT = True       # Posa True per activar el script, False per desactivar-lo (no farà res).
PORT_SERIE = 'COM4'        # Port sèrie a utilitzar (per exemple, 'COM4', 'COM5', etc.).
DURADA_SEGONS = 600        # Temps en segons que el port estarà ocupat (600 segons = 10 minuts).
EXECUTA_CADA_HORES = 3     # Cada quantes hores es repetirà el procés (3 hores).

# NO MODIFIQUIS NADA MÉS AVALL A MENYS QUE SAPIGUES QUÈ FAS

import subprocess
import re
import serial
import time
import sys
import logging

# Configura el logging per guardar missatges en un fitxer
logging.basicConfig(
    filename='caigudes_sobtades.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def close_program(process_name='Multigraph.exe'):
    """Tanca tots els processos amb el nom especificat usant tasklist i taskkill."""
    try:
        # Busca processos amb tasklist
        result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {process_name}'], capture_output=True, text=True)
        output = result.stdout
        pids = []
        for line in output.splitlines():
            if process_name.lower() in line.lower():
                match = re.search(r'(\d+)\s+Console', line)
                if match:
                    pids.append(int(match.group(1)))
        if not pids:
            logging.info(f"No s'han trobat processos per {process_name}")
            return False
        
        # Tanca els processos trobats
        for pid in pids:
            try:
                subprocess.run(['taskkill', '/PID', str(pid), '/F'], capture_output=True, text=True)
                logging.info(f"Procés {process_name} amb PID {pid} tancat")
            except subprocess.CalledProcessError as e:
                logging.error(f"Error al tancar el procés {pid}: {e}")
                if "Access is denied" in e.stderr:
                    logging.error("Executa el programa com a administrador.")
                return False
        return True
    except Exception as e:
        logging.error(f"Error al tancar {process_name}: {e}")
        return False

def occupy_serial_port(com_port, baudrate=19200, duration_seconds=60):
    """Ocupa el port sèrie durant el temps especificat després d'esperar 5 segons."""
    try:
        # Espera 5 segons perquè el port es pugui alliberar
        logging.info("Esperant 5 segons perquè el port es pugui alliberar...")
        time.sleep(5)
        
        # Obre el port sèrie
        ser = serial.Serial(port=com_port, baudrate=baudrate, timeout=1)
        logging.info(f"Port {com_port} obert amb baudrate {baudrate}")
        
        # Manté el port ocupat durant el temps especificat
        logging.info(f"Ocupant {com_port} durant {duration_seconds} segons...")
        time.sleep(duration_seconds)
        
        # Tanca el port
        ser.close()
        logging.info(f"Port {com_port} alliberat")
    except serial.SerialException as e:
        logging.error(f"Error al obrir el port {com_port}: {e}")
        logging.error("Assegura't que el port està disponible i no en ús.")
    except Exception as e:
        logging.error(f"Error inesperat: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            logging.info(f"Port {com_port} alliberat")

def main(com_port, duration_seconds, execute_every_hours):
    """Tanca Multigraph.exe (si existeix) i ocupa el port sèrie cada cert temps."""
    if not ACTIVA_SCRIPT:
        logging.info("Script desactivat (ACTIVA_SCRIPT = False). No s'executarà cap acció.")
        return
    
    # Converteix hores a segons
    execute_interval_seconds = execute_every_hours * 3600
    
    while True:
        logging.info("Iniciant procés: tancant Multigraph.exe i ocupant el port...")
        # Intenta tancar Multigraph.exe
        close_program('Multigraph.exe')
        
        # Ocupa el port fins i tot si Multigraph.exe no estava executant-se
        occupy_serial_port(com_port=com_port, baudrate=19200, duration_seconds=duration_seconds)
        
        # Espera fins al proper cicle
        logging.info(f"Esperant {execute_every_hours} hores fins al proper cicle...")
        time.sleep(execute_interval_seconds)

if __name__ == "__main__":
    try:
        main(com_port=PORT_SERIE, duration_seconds=DURADA_SEGONS, execute_every_hours=EXECUTA_CADA_HORES)
    except KeyboardInterrupt:
        logging.info("Script aturat manualment")
    except Exception as e:
        logging.error(f"Error general en l'execució: {e}")