
import pyodbc
import time
import datetime
import os

# Configuración
SERVIDORES = ['localhost\\SQLEXPRESS', 'localhost', '(local)']
PALABRAS_CLAVE = ['descripcion', 'detalle', 'observacion', 'comentario']
REEMPLAZOS = {
    'Ã±': 'ñ', 'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
    'Ã': 'Ñ', 'Ã“': 'Ó', 'Ã‰': 'É', 'Ãš': 'Ú', 'Ã': 'í'
}
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

def reparar_texto(texto):
    for k, v in REEMPLAZOS.items():
        texto = texto.replace(k, v)
    return texto

def log(msg):
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(os.path.join(LOG_DIR, f"log_{fecha}.txt"), "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} - {msg}\n")

def conectar_sql():
    for server in SERVIDORES:
        try:
            conn = pyodbc.connect(
                f"DRIVER={{SQL Server}};SERVER={server};Trusted_Connection=yes;", timeout=3)
            log(f"Conectado a SQL Server: {server}")
            return conn
        except:
            continue
    log("❌ No se pudo conectar a SQL Server.")
    return None

def monitorear():
    log("🛡️ Iniciando Guardian OPUS")
    conn = conectar_sql()
    if not conn:
        print("No se pudo conectar a SQL Server.")
        return

    cursor = conn.cursor()
    while True:
        try:
            cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
            bases = [row[0] for row in cursor.fetchall()]
            for base in bases:
                try:
                    cursor.execute(f"USE [{base}]")
                    cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE DATA_TYPE LIKE '%char%'")
                    columnas = cursor.fetchall()
                    for tabla, columna in columnas:
                        if any(pal in columna.lower() for pal in PALABRAS_CLAVE):
                            try:
                                cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{tabla}' AND COLUMN_NAME='id'")
                                tiene_id = cursor.fetchone()
                                if not tiene_id:
                                    continue
                                cursor.execute(f"SELECT id, [{columna}] FROM [{tabla}]")
                                filas = cursor.fetchall()
                                for fila in filas:
                                    texto = fila[1]
                                    if texto and any(c in texto for c in REEMPLAZOS.keys()):
                                        nuevo = reparar_texto(texto)
                                        cursor.execute(f"UPDATE [{tabla}] SET [{columna}] = ? WHERE id = ?", (nuevo, fila[0]))
                                        conn.commit()
                                        log(f"✅ Reparado en {base}.{tabla}.{columna} (ID: {fila[0]})")
                            except Exception as e:
                                log(f"Error en tabla {tabla}: {e}")
                except:
                    continue
        except:
            log("Error general en monitoreo.")
        time.sleep(60)  # Espera 1 minuto entre escaneos

if __name__ == "__main__":
    monitorear()
