import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import sys
from datetime import datetime
import threading
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any

# ===========================================
# CLASES BASE Y CONFIGURACIÓN
# ===========================================

class ConfiguracionApp:
    """Clase para manejar la configuración de la aplicación"""
   
    def __init__(self):
        self._base_path = self._obtener_ruta_base()
        self._configurar_rutas()
        self._configurar_ui()
   
    def _obtener_ruta_base(self) -> str:
        """Obtiene la ruta base del programa"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))
   
    def _configurar_rutas(self):
        """Configura las rutas de archivos y carpetas"""
        self.archivo_maestro = os.path.join(self._base_path, "maestro.xlsx")
        self.logo_path = os.path.join(self._base_path, "logo.png")
        self.carpeta_resultados = os.path.join(self._base_path, "Resultados")
       
        # Crear carpeta de resultados
        Path(self.carpeta_resultados).mkdir(exist_ok=True)
   
    def _configurar_ui(self):
        """Configura los parámetros de la interfaz"""
        self.ventana_config = {
            'width': 650,
            'height': 550,
            'bg': 'white',
            'resizable': False
        }
       
        self.colores = {
            'primary': '#002060',
            'secondary': '#4472C4',
            'success': '#70AD47',
            'warning': '#FFC000',
            'text': '#666666',
            'background': 'white'
        }
       
        self.fuentes = {
            'titulo': ('Arial', 20, 'bold'),
            'subtitulo': ('Arial', 11),
            'boton': ('Arial', 12, 'bold'),
            'info': ('Arial', 10, 'bold'),
            'detalle': ('Arial', 9)
        }

# ===========================================
# CLASES DE PROCESAMIENTO DE DATOS
# ===========================================

class ValidadorDatos:
    """Clase para validar datos y archivos"""
   
    @staticmethod
    def validar_archivo_existe(ruta: str) -> bool:
        """Valida si un archivo existe"""
        return os.path.exists(ruta) and os.path.isfile(ruta)
   
    @staticmethod
    def validar_columnas_dataframe(df: pd.DataFrame, columnas_requeridas: list) -> Tuple[bool, str]:
        """Valida que un DataFrame tenga las columnas requeridas"""
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
       
        if columnas_faltantes:
            return False, f"Faltan las siguientes columnas: {', '.join(columnas_faltantes)}"
        return True, ""
   
    @staticmethod
    def validar_extension_archivo(ruta: str, extensiones_validas: list) -> bool:
        """Valida la extensión de un archivo"""
        extension = os.path.splitext(ruta)[1].lower()
        return extension in extensiones_validas

class ProcesadorDatos:
    """Clase para procesar los datos de homologación"""
   
    def __init__(self, validador: ValidadorDatos):
        self._validador = validador
   
    def leer_archivo_excel(self, ruta: str) -> pd.DataFrame:
        """Lee un archivo Excel y retorna un DataFrame"""
        try:
            df = pd.read_excel(ruta, dtype=str)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            raise Exception(f"Error al leer el archivo {os.path.basename(ruta)}: {str(e)}")
   
    def preparar_datos_sap(self, df_sap: pd.DataFrame) -> pd.DataFrame:
        """Prepara los datos del archivo SAP"""
        # Validar columnas requeridas
        es_valido, mensaje = self._validador.validar_columnas_dataframe(df_sap, ["Cuentas"])
        if not es_valido:
            raise ValueError(f"Archivo SAP: {mensaje}")
       
        # Limpiar y preparar datos
        df_preparado = df_sap.copy()
        df_preparado["Cuentas"] = df_preparado["Cuentas"].astype(str).str.strip()
       
        # Convertir Balance si existe
        if "Balance" in df_preparado.columns:
            df_preparado["Balance"] = pd.to_numeric(df_preparado["Balance"], errors="coerce").fillna(0)
       
        return df_preparado
   
    def preparar_datos_maestro(self, df_maestro: pd.DataFrame) -> pd.DataFrame:
        """Prepara los datos del archivo maestro"""
        # Validar columnas requeridas
        es_valido, mensaje = self._validador.validar_columnas_dataframe(df_maestro, ["COSI", "CMF"])
        if not es_valido:
            raise ValueError(f"Archivo maestro: {mensaje}")
       
        # Limpiar y preparar datos
        df_preparado = df_maestro.copy()
        df_preparado["COSI"] = df_preparado["COSI"].astype(str).str.strip()
       
        return df_preparado
   
    def realizar_homologacion(self, df_sap: pd.DataFrame, df_maestro: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Realiza la homologación y retorna el resultado y las cuentas no homologadas"""
        # Realizar merge
        df_resultado = df_sap.merge(
            df_maestro[["COSI", "CMF"]],
            left_on="Cuentas",
            right_on="COSI",
            how="left"
        )
       
        # Renombrar columna
        df_resultado.rename(columns={"CMF": "Homologación CMF"}, inplace=True)
       
        # Identificar cuentas no homologadas
        if "Balance" in df_resultado.columns:
            df_no_homologadas = df_resultado[
                df_resultado["Homologación CMF"].isna() & (df_resultado["Balance"] != 0)
            ]
        else:
            df_no_homologadas = df_resultado[df_resultado["Homologación CMF"].isna()]
       
        return df_resultado, df_no_homologadas

class GestorArchivos:
    """Clase para gestionar la creación y guardado de archivos"""
   
    def __init__(self, carpeta_resultados: str):
        self._carpeta_resultados = carpeta_resultados
   
    def generar_nombre_archivo(self, nombre_base: str, sufijo: str) -> str:
        """Genera un nombre de archivo con timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{nombre_base}_{sufijo}_{timestamp}.xlsx"
   
    def guardar_dataframe(self, df: pd.DataFrame, nombre_archivo: str) -> str:
        """Guarda un DataFrame en un archivo Excel"""
        ruta_completa = os.path.join(self._carpeta_resultados, nombre_archivo)
        df.to_excel(ruta_completa, index=False)
        return ruta_completa

# ===========================================
# CLASES DE INTERFAZ GRÁFICA
# ===========================================

class ComponenteUI(ABC):
    """Clase base abstracta para componentes de la interfaz"""
   
    def __init__(self, parent, config: ConfiguracionApp):
        self._parent = parent
        self._config = config
   
    @abstractmethod
    def crear_componente(self):
        """Método abstracto para crear el componente"""
        pass

class EncabezadoUI(ComponenteUI):
    """Componente para el encabezado de la aplicación"""
   
    def crear_componente(self):
        """Crea el encabezado con logo y títulos"""
        frame = tk.Frame(self._parent, bg=self._config.colores['background'])
        frame.pack(fill="x", padx=20, pady=10)
       
        self._mostrar_logo(frame)
        self._crear_titulos(frame)
       
        return frame
   
    def _mostrar_logo(self, parent):
        """Muestra el logo o texto alternativo"""
        try:
            if os.path.exists(self._config.logo_path):
                logo_img = Image.open(self._config.logo_path)
                logo_img = logo_img.resize((100, 100), Image.Resampling.LANCZOS)
                logo = ImageTk.PhotoImage(logo_img)
                lbl_logo = tk.Label(parent, image=logo, bg=self._config.colores['background'])
                lbl_logo.image = logo
                lbl_logo.pack(pady=10)
            else:
                self._crear_logo_texto(parent)
        except Exception:
            self._crear_logo_texto(parent)
   
    def _crear_logo_texto(self, parent):
        """Crea un logo de texto cuando no hay imagen"""
        tk.Label(
            parent,
            text="BTG PACTUAL",
            font=('Arial', 16, 'bold'),
            fg=self._config.colores['primary'],
            bg=self._config.colores['background']
        ).pack(pady=10)
   
    def _crear_titulos(self, parent):
        """Crea los títulos principales"""
        tk.Label(
            parent,
            text="Homologador de Cuentas SAP",
            font=self._config.fuentes['titulo'],
            fg=self._config.colores['primary'],
            bg=self._config.colores['background']
        ).pack(pady=5)
       
        tk.Label(
            parent,
            text="Herramienta para homologar cuentas SAP con archivo maestro",
            font=self._config.fuentes['subtitulo'],
            fg=self._config.colores['text'],
            bg=self._config.colores['background']
        ).pack(pady=5)

class ControlesUI(ComponenteUI):
    """Componente para los controles principales"""
   
    def __init__(self, parent, config: ConfiguracionApp, callback_seleccionar, callback_procesar):
        super().__init__(parent, config)
        self._callback_seleccionar = callback_seleccionar
        self._callback_procesar = callback_procesar
        self._archivo_seleccionado = None
       
    def crear_componente(self):
        """Crea los controles de la aplicación"""
        frame = tk.Frame(self._parent, bg=self._config.colores['background'])
        frame.pack(fill="x", padx=20, pady=20)
       
        self._crear_separador(frame)
        self._crear_botones(frame)
        self._crear_barra_progreso(frame)
       
        return frame
   
    def _crear_separador(self, parent):
        """Crea un separador visual"""
        separator = tk.Frame(parent, height=2, bg="#E0E0E0")
        separator.pack(fill="x", pady=10)
   
    def _crear_botones(self, parent):
        """Crea los botones de control"""
        # Botón seleccionar archivo
        self._btn_seleccionar = tk.Button(
            parent,
            text="📁 Seleccionar Archivo SAP",
            font=self._config.fuentes['boton'],
            bg=self._config.colores['secondary'],
            fg="white",
            relief="flat",
            padx=30,
            pady=12,
            cursor="hand2",
            command=self._callback_seleccionar
        )
        self._btn_seleccionar.pack(pady=10)
       
        # Label para archivo seleccionado
        self._lbl_archivo = tk.Label(
            parent,
            text="Ningún archivo seleccionado",
            font=self._config.fuentes['subtitulo'],
            fg=self._config.colores['text'],
            bg=self._config.colores['background'],
            wraplength=500
        )
        self._lbl_archivo.pack(pady=5)
       
        # Botón procesar
        self._btn_procesar = tk.Button(
            parent,
            text="⚡ Procesar Homologación",
            font=self._config.fuentes['boton'],
            bg=self._config.colores['success'],
            fg="white",
            relief="flat",
            padx=30,
            pady=12,
            cursor="hand2",
            command=self._callback_procesar,
            state="disabled"
        )
        self._btn_procesar.pack(pady=10)
   
    def _crear_barra_progreso(self, parent):
        """Crea la barra de progreso"""
        self._progress = ttk.Progressbar(parent, mode='indeterminate', length=400)
        self._progress.pack(pady=10)
        self._progress.pack_forget()
   
    def actualizar_archivo_seleccionado(self, archivo: str):
        """Actualiza la información del archivo seleccionado"""
        if archivo:
            self._archivo_seleccionado = archivo
            nombre_archivo = os.path.basename(archivo)
            self._lbl_archivo.config(
                text=f"📄 Archivo seleccionado: {nombre_archivo}",
                fg=self._config.colores['success']
            )
            self._btn_procesar.config(state="normal")
        else:
            self._archivo_seleccionado = None
            self._lbl_archivo.config(
                text="Ningún archivo seleccionado",
                fg=self._config.colores['text']
            )
            self._btn_procesar.config(state="disabled")
   
    def iniciar_procesamiento(self):
        """Inicia el estado de procesamiento"""
        self._btn_seleccionar.config(state="disabled")
        self._btn_procesar.config(state="disabled")
        self._progress.pack(pady=10)
        self._progress.start()
   
    def finalizar_procesamiento(self):
        """Finaliza el estado de procesamiento"""
        self._progress.stop()
        self._progress.pack_forget()
        self._btn_seleccionar.config(state="normal")
        self._btn_procesar.config(state="normal")
   
    @property
    def archivo_seleccionado(self) -> Optional[str]:
        """Getter para el archivo seleccionado"""
        return self._archivo_seleccionado

class InformacionUI(ComponenteUI):
    """Componente para mostrar información del sistema"""
   
    def crear_componente(self):
        """Crea el panel de información"""
        frame = tk.Frame(self._parent, bg=self._config.colores['background'])
        frame.pack(fill="x", padx=20, pady=10)
       
        self._crear_titulo_info(frame)
        self._crear_detalles_sistema(frame)
       
        return frame
   
    def _crear_titulo_info(self, parent):
        """Crea el título de la sección de información"""
        tk.Label(
            parent,
            text="ℹ️ Información del Sistema:",
            font=self._config.fuentes['info'],
            fg=self._config.colores['primary'],
            bg=self._config.colores['background']
        ).pack(anchor="w")
   
    def _crear_detalles_sistema(self, parent):
        """Crea los detalles del sistema"""
        info_text = self._generar_texto_info()
       
        tk.Label(
            parent,
            text=info_text,
            font=self._config.fuentes['detalle'],
            fg=self._config.colores['text'],
            bg=self._config.colores['background'],
            justify="left"
        ).pack(anchor="w", padx=20)
   
    def _generar_texto_info(self) -> str:
        """Genera el texto de información del sistema"""
        maestro_existe = "✅ Encontrado" if os.path.exists(self._config.archivo_maestro) else "❌ No encontrado"
       
        return (
            f"• Ruta base: {self._config._base_path}\n"
            f"• Archivo maestro: {maestro_existe}\n"
            f"• Carpeta resultados: {self._config.carpeta_resultados}"
        )

# ===========================================
# CLASE PRINCIPAL DE LA APLICACIÓN
# ===========================================

class HomologadorSAP:
    """Clase principal que orquesta toda la aplicación"""
   
    def __init__(self):
        self._config = ConfiguracionApp()
        self._validador = ValidadorDatos()
        self._procesador = ProcesadorDatos(self._validador)
        self._gestor_archivos = GestorArchivos(self._config.carpeta_resultados)
       
        self._inicializar_interfaz()
        self._validar_configuracion_inicial()
   
    def _inicializar_interfaz(self):
        """Inicializa la interfaz gráfica"""
        self._root = tk.Tk()
        self._configurar_ventana()
        self._crear_componentes()
   
    def _configurar_ventana(self):
        """Configura la ventana principal"""
        self._root.title("Homologador SAP - BTG Pactual")
        self._root.geometry(f"{self._config.ventana_config['width']}x{self._config.ventana_config['height']}")
        self._root.configure(bg=self._config.ventana_config['bg'])
        self._root.resizable(self._config.ventana_config['resizable'], self._config.ventana_config['resizable'])
        self._centrar_ventana()
   
    def _centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self._root.update_idletasks()
        width = self._root.winfo_width()
        height = self._root.winfo_height()
        x = (self._root.winfo_screenwidth() // 2) - (width // 2)
        y = (self._root.winfo_screenheight() // 2) - (height // 2)
        self._root.geometry(f"{width}x{height}+{x}+{y}")
   
    def _crear_componentes(self):
        """Crea todos los componentes de la interfaz"""
        # Frame principal
        main_frame = tk.Frame(self._root, bg=self._config.colores['background'])
        main_frame.pack(fill="both", expand=True)
       
        # Crear componentes
        self._encabezado = EncabezadoUI(main_frame, self._config)
        self._encabezado.crear_componente()
       
        self._controles = ControlesUI(
            main_frame,
            self._config,
            self._seleccionar_archivo,
            self._iniciar_procesamiento
        )
        self._controles.crear_componente()
       
        self._informacion = InformacionUI(main_frame, self._config)
        self._informacion.crear_componente()
   
    def _validar_configuracion_inicial(self):
        """Valida la configuración inicial de la aplicación"""
        if not self._validador.validar_archivo_existe(self._config.archivo_maestro):
            messagebox.showwarning(
                "Archivo Maestro No Encontrado",
                f"No se encontró el archivo maestro en:\n{self._config.archivo_maestro}\n\n"
                "Por favor, asegúrate de que el archivo 'maestro.xlsx' esté en la misma carpeta que el programa."
            )
   
    def _seleccionar_archivo(self):
        """Maneja la selección de archivo SAP"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo SAP",
            filetypes=[
                ("Archivos Excel", "*.xlsx"),
                ("Archivos Excel Legacy", "*.xls"),
                ("Todos los archivos", "*.*")
            ],
            initialdir=os.path.expanduser("~")
        )
       
        self._controles.actualizar_archivo_seleccionado(archivo)
   
    def _iniciar_procesamiento(self):
        """Inicia el procesamiento de homologación"""
        if not self._controles.archivo_seleccionado:
            messagebox.showwarning("Aviso", "Por favor, selecciona un archivo SAP primero.")
            return
       
        self._controles.iniciar_procesamiento()
       
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self._procesar_homologacion)
        thread.daemon = True
        thread.start()
   
    def _procesar_homologacion(self):
        """Procesa la homologación en un hilo separado"""
        try:
            # Leer archivos
            df_sap = self._procesador.leer_archivo_excel(self._controles.archivo_seleccionado)
            df_maestro = self._procesador.leer_archivo_excel(self._config.archivo_maestro)
           
            # Preparar datos
            df_sap_preparado = self._procesador.preparar_datos_sap(df_sap)
            df_maestro_preparado = self._procesador.preparar_datos_maestro(df_maestro)
           
            # Realizar homologación
            df_resultado, df_no_homologadas = self._procesador.realizar_homologacion(
                df_sap_preparado, df_maestro_preparado
            )
           
            # Guardar resultados
            mensaje_resultado = self._guardar_resultados(df_resultado, df_no_homologadas)
           
            # Mostrar resultado en el hilo principal
            self._root.after(0, lambda: self._mostrar_resultado(mensaje_resultado))
           
        except Exception as e:
            error_msg = f"❌ Error durante el procesamiento:\n\n{str(e)}"
            self._root.after(0, lambda: self._mostrar_error(error_msg))
   
    def _guardar_resultados(self, df_resultado: pd.DataFrame, df_no_homologadas: pd.DataFrame) -> str:
        """Guarda los resultados y genera el mensaje de resultado"""
        nombre_base = os.path.splitext(os.path.basename(self._controles.archivo_seleccionado))[0]
       
        # Guardar archivo homologado
        nombre_homologado = self._gestor_archivos.generar_nombre_archivo(nombre_base, "homologado")
        archivo_homologado = self._gestor_archivos.guardar_dataframe(df_resultado, nombre_homologado)
       
        mensaje = f"✅ Archivo homologado guardado:\n{archivo_homologado}\n\n"
       
        # Guardar cuentas no homologadas si existen
        if not df_no_homologadas.empty:
            nombre_no_homologadas = self._gestor_archivos.generar_nombre_archivo("cuentas", "no_homologadas")
            archivo_no_homologadas = self._gestor_archivos.guardar_dataframe(df_no_homologadas, nombre_no_homologadas)
            mensaje += f"⚠️ Cuentas no homologadas ({len(df_no_homologadas)}):\n{archivo_no_homologadas}"
        else:
            mensaje += "🎉 ¡Todas las cuentas fueron homologadas exitosamente!"
       
        return mensaje
   
    def _mostrar_resultado(self, mensaje: str):
        """Muestra el resultado del procesamiento"""
        self._controles.finalizar_procesamiento()
        messagebox.showinfo("✅ Proceso Completado", mensaje)
   
    def _mostrar_error(self, mensaje: str):
        """Muestra un error del procesamiento"""
        self._controles.finalizar_procesamiento()
        messagebox.showerror("❌ Error", mensaje)
   
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self._root.mainloop()

# ===========================================
# FUNCIÓN PRINCIPAL
# ===========================================

def main():
    """Función principal para ejecutar la aplicación"""
    try:
        app = HomologadorSAP()
        app.ejecutar()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error Crítico",
            f"Error al iniciar la aplicación:\n\n{str(e)}\n\n"
            "Contacte al administrador del sistema."
        )
        root.destroy()

if __name__ == "__main__":
    main()