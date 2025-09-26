#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app_presupuesto_integral.py
Aplicación de presupuesto de obra integral (CLI + Web)
Guarda como app_presupuesto_integral.py y ejecútalo:
  python app_presupuesto_integral.py
Dependencias:
  pip install pandas matplotlib openpyxl reportlab flask waitress
"""
import os
import re
import io
import json
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from flask import Flask, render_template_string, request, redirect, url_for, send_file, flash

# Servir con waitress en producción simple
from waitress import serve

# ---------------- rutas ----------------
BASE = Path.cwd()
DATA_DIR = BASE / "data"
OUTPUT_DIR = BASE / "output"
CHARTS_DIR = OUTPUT_DIR / "charts"
for d in (DATA_DIR, OUTPUT_DIR, CHARTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

PROYECTO_FILE = DATA_DIR / "proyecto.json"
CATALOGO_FILE = DATA_DIR / "catalogo_materiales.csv"
MO_FILE = DATA_DIR / "mano_obra.csv"
NORMAS_FILE = DATA_DIR / "normas.csv"
PARTIDAS_FILE = DATA_DIR / "partidas.csv"
DET_MAT_FILE = DATA_DIR / "detalle_materiales.csv"
DET_MO_FILE = DATA_DIR / "detalle_manoobra.csv"
OUTPUT_XLSX = OUTPUT_DIR / "resumen_presupuesto.xlsx"
OUTPUT_PDF = OUTPUT_DIR / "resumen_presupuesto.pdf"

# ---------------- datos de ejemplo ----------------
def crear_datos_ejemplo():
    if not PROYECTO_FILE.exists():
        proyecto = {
            "NombreProyecto": "Edificio Demo",
            "Cliente": "Cliente Demo",
            "Ubicacion": "Ciudad Demo",
            "FechaInicio": "2025-01-01",
            "FechaFinEstim": "2025-12-31",
            "AreaTotal_m2": 2000,
            "UnidadMedida": "m",
            "FactorSeguridadGlobal": 1.02,
            "IVA_pct": 0.19,
            "Margen_pct": 0.10,
            "Observaciones": "Ajustar parámetros según normativa local."
        }
        PROYECTO_FILE.write_text(json.dumps(proyecto, indent=2, ensure_ascii=False), encoding="utf-8")

    if not CATALOGO_FILE.exists():
        df = pd.DataFrame([
            ["M001","Cemento Portland Tipo I","Cemento","saco 50kg",150.0, "proveedor A"],
            ["M002","Arena Silícea","Agregado","m3",400.0, "proveedor B"],
            ["M003","Varilla Acero Ø12","Acero","ml",250.0, "proveedor C"],
            ["M004","Ladrillo Hueco","Ladrillo","un",0.35, "proveedor D"],
            ["M005","Pintura Plástica Blanco","Acabado","L",5.5, "proveedor E"],
            ["M006","Mortero Premezclado","Mortero","bolsa 25kg",90.0, "proveedor F"],
            ["M007","Tornillo 1/4\"","Ferretería","pack 100",180.0, "proveedor G"]
        ], columns=["Codigo","NombreMaterial","Categoria","Unidad","PrecioUnitario","Proveedor"])
        df.to_csv(CATALOGO_FILE, index=False)

    if not MO_FILE.exists():
        df = pd.DataFrame([
            ["MO01","Albañil",12.0,0.30],
            ["MO02","Peón",8.0,0.30],
            ["MO03","Pintor",10.0,0.30],
            ["MO04","Ingeniero Residente",30.0,0.25]
        ], columns=["Codigo","Puesto","SalarioHora","PorcCargas"])
        df.to_csv(MO_FILE, index=False)

    if not NORMAS_FILE.exists():
        df = pd.DataFrame([
            ["NSR-01","Norma seguridad estructuras hormigón",1.05,"Estructura"],
            ["NORM-AC","Norma acabados",1.03,"Acabados"]
        ], columns=["CodigoNorma","Descripcion","FactorSeguridad","Aplicacion"])
        df.to_csv(NORMAS_FILE, index=False)

    if not PARTIDAS_FILE.exists():
        df = pd.DataFrame([
            ["P001","Estructura","CIM-001","Cimentación corrida hormigón armado","m3",100.0,"NSR-01","",0.0,"",""],
            ["P002","Estructura","LOS-001","Losas aligeradas de entrepiso","m2",850.0,"NSR-01","",0.0,"",""],
            ["P003","Acabados","REV-001","Revoque exterior y pintado","m2",2500.0,"NORM-AC","",0.0,"",""],
            ["P004","Instalaciones","INS-001","Instalación sanitaria principal","un",10.0,"","",0.0,"",""]
        ], columns=["ID","Capitulo","CodigoPartida","DescripcionPartida","UnidadPartida","CantidadProyecto","CodigoNorma","FactorNorma","CantidadAjustada","Notas","Reserved"])
        df.to_csv(PARTIDAS_FILE, index=False)

    if not DET_MAT_FILE.exists():
        df = pd.DataFrame([
            ["P001","M001",0.13,"saco 50kg"],   # sacos por m3 (ejemplo)
            ["P001","M002",0.8,"m3"],
            ["P001","M003",10.0,"ml"],
            ["P001","M006",0.5,"bolsa 25kg"],
            ["P002","M003",6.5,"ml"],
            ["P003","M004",5.0,"un"],
            ["P003","M005",0.12,"L"],
            ["P004","M007",0.01,"pack 100"],
        ], columns=["IDPartida","MaterialCodigo","CantidadPorUnidadPartida","UnidadMaterial"])
        df.to_csv(DET_MAT_FILE, index=False)

    if not DET_MO_FILE.exists():
        df = pd.DataFrame([
            ["P001","MO01",0.5],
            ["P001","MO02",0.8],
            ["P002","MO01",0.12],
            ["P003","MO03",0.08],
            ["P004","MO02",0.5]
        ], columns=["IDPartida","MO_Codigo","HorasPorUnidadPartida"])
        df.to_csv(DET_MO_FILE, index=False)

# ---------------- utilidades ----------------
def leer_csv_num(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for c in df.columns:
        try:
            df[c] = pd.to_numeric(df[c], errors="ignore")
        except Exception:
            pass
    return df

def cargar_proyecto() -> Dict:
    if PROYECTO_FILE.exists():
        return json.loads(PROYECTO_FILE.read_text(encoding="utf-8"))
    return {}

# ---------- normalización de embalajes ----------
EMBALAJE_RE = re.compile(r"(saco|bolsa|pack|caja)\s*[:\-]?\s*(\d+\.?\d*)\s*(kg|g|un|u|pcs|pc)?", flags=re.IGNORECASE)

def parse_embalaje(unidad_text: str):
    if not isinstance(unidad_text, str):
        return None
    m = EMBALAJE_RE.search(unidad_text)
    if not m:
        return None
    tipo = m.group(1).lower()
    cantidad = float(m.group(2))
    unidad = (m.group(3) or "").lower()
    if unidad == "g":
        cantidad = cantidad / 1000.0
        unidad = "kg"
    return tipo, cantidad, unidad

def normalizar_catalogo(df_cat: pd.DataFrame) -> pd.DataFrame:
    df = df_cat.copy()
    df["PrecioUnitarioNormalizado"] = pd.to_numeric(df["PrecioUnitario"], errors="coerce").fillna(0.0)
    df["UnidadNormalizada"] = df["Unidad"]
    for i, r in df.iterrows():
        parsed = parse_embalaje(str(r["Unidad"]))
        if parsed:
            tipo, contenido, um = parsed
            if contenido > 0:
                df.at[i, "PrecioUnitarioNormalizado"] = float(r["PrecioUnitario"]) / float(contenido)
                if um in ("kg",):
                    df.at[i, "UnidadNormalizada"] = "kg"
                else:
                    df.at[i, "UnidadNormalizada"] = "un"
    return df

# ---------------- cálculo principal ----------------
def calcular_presupuesto(save_outputs: bool = True):
    proyecto = cargar_proyecto()
    if not proyecto:
        proyecto = {"FactorSeguridadGlobal": 1.02, "IVA_pct": 0.19, "Margen_pct": 0.10}

    factor_global = float(proyecto.get("FactorSeguridadGlobal", 1.0))
    iva = float(proyecto.get("IVA_pct", 0.0))
    margen_pct = float(proyecto.get("Margen_pct", 0.0))

    cat = leer_csv_num(CATALOGO_FILE)
    mo = leer_csv_num(MO_FILE)
    normas = leer_csv_num(NORMAS_FILE)
    partidas = leer_csv_num(PARTIDAS_FILE)
    det_mat = leer_csv_num(DET_MAT_FILE)
    det_mo = leer_csv_num(DET_MO_FILE)

    # normalizar catálogo
    cat_norm = normalizar_catalogo(cat)

    partidas_idx = partidas.set_index("ID")
    normas_idx = normas.set_index("CodigoNorma") if "CodigoNorma" in normas.columns else pd.DataFrame()

    # Cantidad ajustada por partida: priorizar Norma (si existe), luego FactorNorma de partida
    def cantidad_ajustada_row(row):
        q = float(row.get("CantidadProyecto", 0.0))
        f_partida = row.get("FactorNorma", 0.0)
        codigo_norma = row.get("CodigoNorma", "")
        f_norma = None
        if pd.notna(codigo_norma) and str(codigo_norma).strip() != "":
            if codigo_norma in normas_idx.index:
                f_norma = float(normas_idx.loc[codigo_norma, "FactorSeguridad"])
        f_elegido = f_norma if (f_norma is not None and f_norma > 0) else (float(f_partida) if (pd.notna(f_partida) and float(f_partida)>0) else 1.0)
        return q * f_elegido * factor_global

    partidas["CantidadAjustada"] = partidas.apply(cantidad_ajustada_row, axis=1)

    # Detalle materiales: unir con catálogo normalizado
    det_mat = det_mat.merge(cat_norm[["Codigo","PrecioUnitarioNormalizado","UnidadNormalizada","Unidad"]].rename(columns={"Codigo":"MaterialCodigo"}), on="MaterialCodigo", how="left")
    det_mat["CantidadPorUnidadPartida"] = pd.to_numeric(det_mat["CantidadPorUnidadPartida"], errors="coerce").fillna(0.0)
    det_mat["CantidadTotalMaterial"] = det_mat.apply(lambda r: r["CantidadPorUnidadPartida"] * float(partidas_idx.loc[r["IDPartida"], "CantidadAjustada"]) if r["IDPartida"] in partidas_idx.index else 0.0, axis=1)
    # Elegir precio: normalizado si existe (PrecioUnitarioNormalizado) sino PrecioUnitario original
    def precio_usado(r):
        pnorm = r.get("PrecioUnitarioNormalizado", None)
        if pd.notna(pnorm) and float(pnorm) > 0:
            return float(pnorm)
        # si no hay normalizado, intentar buscar en catálogo original (columna PrecioUnitario)
        # La columna original no fue traída; asumimos pnorm existirá o el usuario debe corregir catálogo
        return float(r.get("PrecioUnitarioNormalizado", 0.0))
    det_mat["PrecioUnitarioUsado"] = det_mat["PrecioUnitarioNormalizado"].fillna(0.0)
    det_mat["CostoMaterial"] = det_mat["CantidadTotalMaterial"] * det_mat["PrecioUnitarioUsado"]

    # Mano de obra
    det_mo = det_mo.merge(mo[["Codigo","SalarioHora","PorcCargas"]].rename(columns={"Codigo":"MO_Codigo"}), on="MO_Codigo", how="left")
    det_mo["HorasPorUnidadPartida"] = pd.to_numeric(det_mo["HorasPorUnidadPartida"], errors="coerce").fillna(0.0)
    det_mo["HorasTotales"] = det_mo.apply(lambda r: r["HorasPorUnidadPartida"] * float(partidas_idx.loc[r["IDPartida"], "CantidadAjustada"]) if r["IDPartida"] in partidas_idx.index else 0.0, axis=1)
    det_mo["SalarioHora"] = pd.to_numeric(det_mo["SalarioHora"], errors="coerce").fillna(0.0)
    det_mo["PorcCargas"] = pd.to_numeric(det_mo["PorcCargas"], errors="coerce").fillna(0.0)
    det_mo["CostoHoraTotal"] = det_mo["SalarioHora"] * (1.0 + det_mo["PorcCargas"])
    det_mo["CostoMO"] = det_mo["HorasTotales"] * det_mo["CostoHoraTotal"]

    # Consolidación por partida
    mat_sum = det_mat.groupby("IDPartida", as_index=True)["CostoMaterial"].sum().rename("MaterialesCosto")
    mo_sum_h = det_mo.groupby("IDPartida", as_index=True)["HorasTotales"].sum().rename("ManoObraHoras")
    mo_sum_cost = det_mo.groupby("IDPartida", as_index=True)["CostoMO"].sum().rename("ManoObraCosto")

    partidas = partidas.set_index("ID")
    partidas = partidas.join(mat_sum).join(mo_sum_h).join(mo_sum_cost)
    partidas["MaterialesCosto"] = partidas["MaterialesCosto"].fillna(0.0)
    partidas["ManoObraHoras"] = partidas["ManoObraHoras"].fillna(0.0)
    partidas["ManoObraCosto"] = partidas["ManoObraCosto"].fillna(0.0)
    partidas["EquipoCosto"] = partidas.get("EquipoCosto", 0.0).fillna(0.0) if "EquipoCosto" in partidas.columns else 0.0

    partidas["SubtotalParcial"] = partidas["MaterialesCosto"] + partidas["ManoObraCosto"] + partidas["EquipoCosto"]
    partidas["Impuestos"] = partidas["SubtotalParcial"] * iva
    partidas["Margen"] = partidas["SubtotalParcial"] * margen_pct
    partidas["TotalPartida"] = partidas["SubtotalParcial"] + partidas["Impuestos"] + partidas["Margen"]

    resumen = partidas.reset_index().groupby("Capitulo").agg(
        CostoMaterial=pd.NamedAgg(column="MaterialesCosto", aggfunc="sum"),
        CostoManoObra=pd.NamedAgg(column="ManoObraCosto", aggfunc="sum"),
        CostoEquipo=pd.NamedAgg(column="EquipoCosto", aggfunc="sum"),
        Subtotal=pd.NamedAgg(column="SubtotalParcial", aggfunc="sum")
    ).reset_index()

    totales = {
        "TotalMaterial": float(partidas["MaterialesCosto"].sum()),
        "TotalMO": float(partidas["ManoObraCosto"].sum()),
        "SubtotalGlobal": float(partidas["SubtotalParcial"].sum()),
        "TotalImpuestos": float(partidas["Impuestos"].sum()),
        "TotalMargen": float(partidas["Margen"].sum()),
        "TotalFinal": float(partidas["TotalPartida"].sum())
    }

    charts = []
    if save_outputs:
        partidas_out = partidas.reset_index()
        partidas_out.to_csv(OUTPUT_DIR / "05_Partidas_calculado.csv", index=False)
        det_mat.to_csv(OUTPUT_DIR / "05A_DetallePartidas_calculado.csv", index=False)
        det_mo.to_csv(OUTPUT_DIR / "05B_DetalleMO_calculado.csv", index=False)
        resumen.to_csv(OUTPUT_DIR / "06_ResumenPresupuesto_calculado.csv", index=False)

        # gráficos por partida
        for _, row in partidas_out.iterrows():
            pid = row["ID"]
            desc = row.get("DescripcionPartida", pid)
            mat = float(row.get("MaterialesCosto", 0.0))
            moc = float(row.get("ManoObraCosto", 0.0))
            eq = float(row.get("EquipoCosto", 0.0))
            total = mat + moc + eq
            if total <= 0:
                continue
            # barra apilada
            fig, ax = plt.subplots(figsize=(6,3))
            ax.bar([0], [mat], label="Materiales", color="#4C72B0")
            ax.bar([0], [moc], bottom=[mat], label="Mano de Obra", color="#55A868")
            ax.bar([0], [eq], bottom=[mat+moc], label="Equipo", color="#C44E52")
            ax.set_xticks([])
            ax.set_title(f"{pid} - {desc}")
            ax.legend()
            plt.tight_layout()
            f1 = CHARTS_DIR / f"{pid}_barra.png"
            fig.savefig(f1)
            plt.close(fig)
            charts.append(str(f1))
            # pastel
            fig2, ax2 = plt.subplots(figsize=(4,4))
            ax2.pie([mat, moc, eq], labels=["Materiales","ManoObra","Equipo"], autopct='%1.1f%%', startangle=90)
            ax2.set_title(f"{pid} - porcentaje")
            plt.tight_layout()
            f2 = CHARTS_DIR / f"{pid}_pastel.png"
            fig2.savefig(f2)
            plt.close(fig2)
            charts.append(str(f2))

        # Guardar Excel
        with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
            pd.DataFrame([proyecto]).to_excel(writer, sheet_name="01_Proyecto", index=False)
            cat_norm.to_excel(writer, sheet_name="02_CatalogoMateriales", index=False)
            mo.to_excel(writer, sheet_name="03_ManoObra", index=False)
            normas.to_excel(writer, sheet_name="04_Normas", index=False)
            partidas_out.to_excel(writer, sheet_name="05_Partidas", index=False)
            det_mat.to_excel(writer, sheet_name="05A_DetallePartidas", index=False)
            det_mo.to_excel(writer, sheet_name="05B_DetalleMO", index=False)
            resumen.to_excel(writer, sheet_name="06_ResumenPresupuesto", index=False)
            pd.DataFrame([totales]).to_excel(writer, sheet_name="07_Totales", index=False)

        # generar PDF resumen
        generar_pdf_resumen(partidas.reset_index(), resumen, totales, charts, proyecto)

    return {
        "partidas": partidas.reset_index(),
        "det_mat": det_mat,
        "det_mo": det_mo,
        "resumen": resumen,
        "totales": totales,
        "charts": charts
    }

# ---------------- PDF resumen ----------------
def generar_pdf_resumen(partidas_df: pd.DataFrame, resumen_df: pd.DataFrame, totales: Dict, charts: list, proyecto: Dict):
    doc = SimpleDocTemplate(str(OUTPUT_PDF), pagesize=A4, rightMargin=20,leftMargin=20, topMargin=20,bottomMargin=20)
    styles = getSampleStyleSheet()
    flow = []

    flow.append(Paragraph(f"Resumen Presupuesto - {proyecto.get('NombreProyecto','Proyecto')}", styles['Title']))
    flow.append(Spacer(1,6))
    info = f"Cliente: {proyecto.get('Cliente','-')} - Ubicación: {proyecto.get('Ubicacion','-')} - Periodo: {proyecto.get('FechaInicio','-')} → {proyecto.get('FechaFinEstim','-')}"
    flow.append(Paragraph(info, styles['Normal']))
    flow.append(Spacer(1,12))

    # tabla resumen por capitulo
    data = [["Capitulo","CostoMaterial","CostoManoObra","CostoEquipo","Subtotal"]]
    for _, r in resumen_df.iterrows():
        data.append([r['Capitulo'], f"{r['CostoMaterial']:,.2f}", f"{r['CostoManoObra']:,.2f}", f"{r['CostoEquipo']:,.2f}", f"{r['Subtotal']:,.2f}"])
    t = Table(data, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#4C72B0")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),0.25,colors.grey),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')
    ]))
    flow.append(t)
    flow.append(Spacer(1,12))

    tot_text = f"Total Material: {totales['TotalMaterial']:,.2f}   Total Mano Obra: {totales['TotalMO']:,.2f}   Subtotal: {totales['SubtotalGlobal']:,.2f}"
    flow.append(Paragraph(tot_text, styles['Normal']))
    flow.append(Spacer(1,12))

    # incluir hasta 6 gráficos
    for ch in charts[:6]:
        try:
            img = Image(ch, width=170*mm, height=90*mm)
            flow.append(img)
            flow.append(Spacer(1,6))
        except Exception:
            continue

    doc.build(flow)

# ---------------- Flask web UI ----------------
app = Flask(__name__)
app.secret_key = "cambia_esta_clave_localmente"

TEMPLATE_INDEX = """
<!doctype html>
<title>Presupuesto Integral</title>
<h1>Presupuesto Integral - Panel</h1>
<ul>
  <li><a href="{{ url_for('ver_tabla','catalogo') }}">Catálogo de Materiales</a></li>
  <li><a href="{{ url_for('ver_tabla','mano_obra') }}">Mano de Obra</a></li>
  <li><a href="{{ url_for('ver_tabla','normas') }}">Normas</a></li>
  <li><a href="{{ url_for('ver_tabla','partidas') }}">Partidas</a></li>
  <li><a href="{{ url_for('ver_tabla','detalles_material') }}">Detalle Materiales</a></li>
  <li><a href="{{ url_for('ver_tabla','detalles_manoobra') }}">Detalle Mano Obra</a></li>
  <li><a href="{{ url_for('calcular') }}">Calcular presupuesto</a></li>
  <li><a href="{{ url_for('descargar','excel') }}">Descargar Excel</a></li>
  <li><a href="{{ url_for('descargar','pdf') }}">Descargar PDF</a></li>
</ul>
<p>{{ mensaje }}</p>
"""

TEMPLATE_TABLE = """
<!doctype html>
<title>Tabla {{ nombre }}</title>
<h1>{{ nombre }}</h1>
<p><a href="{{ url_for('index') }}">Volver</a></p>
<form method="post">
<textarea name="contenido" rows="25" cols="120">{{ csv }}</textarea><br/>
<button type="submit">Guardar CSV</button>
</form>
"""

@app.route("/")
def index():
    mensaje = ""
    return render_template_string(TEMPLATE_INDEX, mensaje=mensaje)

@app.route("/tabla/<tabla>", methods=["GET","POST"])
def ver_tabla(tabla):
    mapping = {
        "catalogo": CATALOGO_FILE,
        "mano_obra": MO_FILE,
        "normas": NORMAS_FILE,
        "partidas": PARTIDAS_FILE,
        "detalles_material": DET_MAT_FILE,
        "detalles_manoobra": DET_MO_FILE
    }
    if tabla not in mapping:
        flash("Tabla no encontrada")
        return redirect(url_for("index"))
    path = mapping[tabla]
    if request.method == "POST":
        contenido = request.form.get("contenido","")
        path.write_text(contenido, encoding="utf-8")
        flash("Guardado")
        return redirect(url_for("ver_tabla", tabla=tabla))
    csv = path.read_text(encoding="utf-8")
    nombre = tabla.replace("_"," ").title()
    return render_template_string(TEMPLATE_TABLE, csv=csv, nombre=nombre)

@app.route("/calcular")
def calcular():
    res = calcular_presupuesto(save_outputs=True)
    flash("Cálculo realizado y archivos generados en carpeta output/")
    return redirect(url_for("index"))

@app.route("/descargar/<tipo>")
def descargar(tipo):
    if tipo == "excel":
        if OUTPUT_XLSX.exists():
            return send_file(str(OUTPUT_XLSX), as_attachment=True)
        flash("Excel no encontrado. Genera el cálculo primero.")
        return redirect(url_for("index"))
    elif tipo == "pdf":
        if OUTPUT_PDF.exists():
            return send_file(str(OUTPUT_PDF), as_attachment=True)
        flash("PDF no encontrado. Genera el cálculo primero.")
        return redirect(url_for("index"))
    else:
        flash("Tipo no soportado.")
        return redirect(url_for("index"))

# ---------------- CLI ----------------
def cli():
    crear_datos_ejemplo()
    print("Datos de ejemplo creados en ./data/")
    print("Iniciando servidor web en http://127.0.0.1:5000")
    serve(app, listen="127.0.0.1:5000")

if __name__ == "__main__":
    cli()