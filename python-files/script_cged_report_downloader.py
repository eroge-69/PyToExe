"""
script_cged_report_downloader.py
Requiere: pip install selenium webdriver-manager
"""

import os, time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

# === CONFIGURACIÓN GENERAL ===================================================
# --- CARGA DE PARÁMETROS DESDE data.txt --------------------------------------
try:
    BASE_DIR = Path(__file__).parent          # ejecución normal / .exe
except NameError:                             # Jupyter o intérprete interactivo
    BASE_DIR = Path.cwd()

DATA_FILE = BASE_DIR / "data.txt"

try:
    with DATA_FILE.open(encoding="utf-8") as fh:
        _lines = [ln.strip() for ln in fh.readlines()]
        if len(_lines) < 4:
            raise ValueError("data.txt debe tener al menos 4 líneas.")
        FECHA_DESDE_DEF, PLANCONT_DEF, USER, PWD = _lines[:4]
except FileNotFoundError:
    raise FileNotFoundError(
        f"No se encontró {DATA_FILE}. Colócalo en {BASE_DIR}."
    ) from None
# ----------------------------------------------------------------------------


TIMEOUT      = 15
DOWNLOAD_DIR = Path.cwd() / "descargas_cged"; DOWNLOAD_DIR.mkdir(exist_ok=True)
STEP_DELAY   = 0
# FECHA_DESDE_DEF = "30/07/2025"
# PLANCONT_DEF = "CONT20250730ZRancagua"
# ============================================================================

# === LISTA DE REPORTES =======================================================
REPORTS = [
    {   # Bloques de restauración (id 123)
        "url": "https://cged.grupocge.cl:8082/backend/cge/reports.php?id=123",
        "fecha_desde": FECHA_DESDE_DEF,
        "dest_name": "1. Bloques_de_restauracion_por_Comuna_(CGE)-cge.csv",
        "container_id": "cmp_4",
        "to_container_id": None,
        "set_times": False,
        "solo_confirmados_id": "cmp_6",        # ← desmarcar
    },
    {   # Detalle Doctos (id 268)
        "url": "https://cged.grupocge.cl:8082/backend/cge/reports.php?id=268",
        "fecha_desde": FECHA_DESDE_DEF,
        "dest_name": "2. Detalle_Doctos-cge.csv",
        "container_id": "cmp_1",
        "to_container_id": "cmp_2",
        "set_times": True,
    },
    {   # Seguimiento de fallas en contingencia (id 415)
        "url": "https://cged.grupocge.cl:8082/backend/cge/reports.php?id=415",
        "fecha_desde": FECHA_DESDE_DEF,
        "dest_name": "3. Reporte_de_seguimiento_de_fallas_en_contingencia-cge.csv",
        "container_id": "cmp_1",
        "to_container_id": "cmp_2",
        "set_times": True,
        "coz_field_id": "cmp_3",
        "coz_value_id": 581,
        "coz_value_txt": "O'Higgins",
    },
    {   # Levantamiento temprano de daños (id 396)
        "url": "https://cged.grupocge.cl:8082/backend/cge/reports.php?id=396",
        "fecha_desde": "",
        "dest_name": "4. informe_general_de_levantamiento_temprano_de_danos-cge.csv",
        "container_id": None,
        "to_container_id": None,
        "set_times": False,
        "plan_field_id": "cmp_1",
        "plan_value_id": 527674088,
        "plan_value_txt": PLANCONT_DEF,
    },
    {   # Informe general de reconstrucción (id 397)
        "url": "https://cged.grupocge.cl:8082/backend/cge/reports.php?id=397",
        "fecha_desde": "",
        "dest_name": "5. Informe_general_de_reconstruccion-cge.csv",
        "container_id": None,
        "to_container_id": None,
        "set_times": False,
        "plan_field_id": "cmp_1",
        "plan_value_id": 527674088,
        "plan_value_txt": PLANCONT_DEF,
    },
]
# ============================================================================

def pause(msg=""):
    if msg:
        print(f"⏸  {msg} ({STEP_DELAY}s)")
    time.sleep(STEP_DELAY)

# ---------- driver -----------------------------------------------------------
def iniciar_driver():
    chromepath = ChromeDriverManager(driver_version="137.0.7151.120").install()
    driver_exe = Path(chromepath) if chromepath.endswith(".exe") else Path(chromepath).with_name("chromedriver.exe")

    prefs = {"download.default_directory": str(DOWNLOAD_DIR),
             "download.prompt_for_download": False}
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option("prefs", prefs)
    opts.add_argument("--start-maximized")
    opts.add_experimental_option("detach", True)

    print(f"🟢  Chrome listo – descargas → {DOWNLOAD_DIR}")
    return webdriver.Chrome(service=ChromeService(driver_exe), options=opts)

# ---------- login ------------------------------------------------------------
def login_si_es_necesario(d):
    if "login" not in d.current_url.lower():
        return
    print("🔑  Login…")
    d.find_element(By.ID, "usrname").send_keys(USER)
    d.find_element(By.ID, "usrpwd").send_keys(PWD)
    d.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    WebDriverWait(d, TIMEOUT).until_not(EC.url_contains("login"))
    print("✅  Login OK"); pause("post-login")

# ---------- helpers ----------------------------------------------------------
def _set_datetime_by_container(d, container_id, date_val, time_val=None):
    dt_str = f"{date_val} {time_val or ''}".strip()
    fmt = "d/m/Y H:i:s" if time_val else "d/m/Y"
    ext_ok = d.execute_script(
        """
        const id=arguments[0],text=arguments[1],fmt=arguments[2];
        if(window.Ext&&Ext.ComponentMgr&&Ext.ComponentMgr.get(id)){
            const cmp=Ext.ComponentMgr.get(id),
                  parse=Date.parseDate||(Ext.Date&&Ext.Date.parse);
            const parsed=parse?parse(text,fmt):null;
            if(parsed){cmp.setValue(parsed);cmp.fireEvent('select',cmp,parsed);return true;}
        }return false;
        """, container_id, dt_str, fmt)
    if ext_ok:
        return
    cont = WebDriverWait(d, TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"div#x-form-el-{container_id}")))
    inputs = cont.find_elements(By.CSS_SELECTOR, "input[type='text']")
    if not inputs:
        return
    def fill(inp, val):
        d.execute_script("arguments[0].removeAttribute('readonly');", inp)
        inp.clear(); inp.send_keys(val); inp.send_keys(Keys.TAB)
    fill(inputs[0], date_val)
    if time_val and len(inputs) > 1:
        fill(inputs[1], time_val)

# ---------- parámetros -------------------------------------------------------
def configurar_parametros(d, rep):
    print("⚙️  Configurando parámetros…")

    # --- Fechas ---------------------------------------------------------
    if rep["container_id"]:
        if rep["set_times"]:
            _set_datetime_by_container(d, rep["container_id"],
                                       rep["fecha_desde"], "00:00:01")
        else:
            _set_datetime_by_container(d, rep["container_id"],
                                       rep["fecha_desde"])
        pause("fecha-desde establecida")

    if rep["set_times"] and rep["to_container_id"]:
        now = datetime.now()
        _set_datetime_by_container(d, rep["to_container_id"],
                                   now.strftime("%d/%m/%Y"),
                                   now.strftime("%H:%M:%S"))
        pause("fecha-hasta establecida")

    # --- COZ ------------------------------------------------------------
    if rep.get("coz_field_id"):
        d.execute_script(
            "const c=Ext.ComponentMgr.get(arguments[0]); if(c){c.setValue(arguments[1]);}",
            rep["coz_field_id"], rep["coz_value_id"]
        )
        pause("COZ seleccionado")

    # --- Plan -----------------------------------------------------------
    if rep.get("plan_field_id"):
        d.execute_script(
            "const c=Ext.ComponentMgr.get(arguments[0]); if(c){c.setValue(arguments[1]);}",
            rep["plan_field_id"], rep["plan_value_id"]
        )
        pause("Plan seleccionado")

    # --- Solo confirmados ----------------------------------------------
    if rep.get("solo_confirmados_id"):
        try:
            chk = d.find_element(
                By.CSS_SELECTOR,
                f"input#{rep['solo_confirmados_id']}[type='checkbox']"
            )
            if chk.is_selected():
                chk.click()
            pause("Solo confirmados desmarcado")
        except:
            pass

    # --- Formato CSV plano ---------------------------------------------
    try:
        csv_radio = d.find_element(By.CSS_SELECTOR, "input[name='format'][value='plaincsv']")
        if not csv_radio.is_selected():
            csv_radio.click()
    except:
        pass
    pause("formato CSV seleccionado")

# ---------- ejecutar ---------------------------------------------------------
def ejecutar_reporte(d):
    d.find_element(By.XPATH, "//button[text()='Generar']").click()
    pause("botón generar")

def esperar_descarga(prev_files, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        current = {f for f in DOWNLOAD_DIR.glob("*.csv") if not f.name.endswith(".crdownload")}
        new = current - prev_files
        if new:
            return max(new, key=lambda p: p.stat().st_mtime)
        time.sleep(1)
    return None

# ---------- main -------------------------------------------------------------
def main():
    with iniciar_driver() as d:
        logged = False
        for rep in REPORTS:
            prev = {f for f in DOWNLOAD_DIR.glob("*.csv")}
            d.get(rep["url"])

            if not logged:
                login_si_es_necesario(d)
                logged = True

            WebDriverWait(d, TIMEOUT).until(EC.title_contains("Reportes"))

            if rep.get("container_id"):
                WebDriverWait(d, TIMEOUT).until(
                    lambda drv: drv.execute_script(
                        "return window.Ext && Ext.ComponentMgr && Ext.ComponentMgr.get(arguments[0]) && Ext.ComponentMgr.get(arguments[0]).rendered;",
                        rep["container_id"])
                )

            pause("antes de configurar parámetros")
            configurar_parametros(d, rep)
            ejecutar_reporte(d)

            csv = esperar_descarga(prev)
            if csv:
                dest = DOWNLOAD_DIR / rep["dest_name"]
                dest.unlink(missing_ok=True)
                csv.rename(dest)
                print(f"📂  {dest.name}")

            pause("siguiente reporte")

        print("🏁  Todos los reportes descargados")

if __name__ == "__main__":
    main()
