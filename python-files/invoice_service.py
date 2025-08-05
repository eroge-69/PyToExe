#!/usr/bin/env python3
import os
import json
import zipfile
from io import BytesIO
from decimal import Decimal
from datetime import datetime

from num2words import num2words
from flask import Flask, request, send_file, abort, jsonify
from flask_cors import CORS
import mysql.connector

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ――― APP SETUP ―――
app = Flask(__name__)
CORS(app)
BASE_DIR = os.path.dirname(__file__)

# ―― Load header/footer config from invoice.json ――
cfg_path   = os.path.join(BASE_DIR, 'config', 'invoice.json')
with open(cfg_path, encoding='utf8') as f:
    invoice_cfg = json.load(f)
header_cfg  = invoice_cfg.get('header', {})
FOOTER_TEXT = invoice_cfg.get('footer', '')

# ―― DATABASE CONFIG ――
DB_CONFIG = {
    'host':     '127.0.0.1',
    'user':     'root',
    'password': 'Faress12',
    'database': 'invoice'
}

# ―― Helpers ――
def to_french_words(n):
    return num2words(n, lang='fr').capitalize()

def fetch_invoice(inv_id):
    cnx = mysql.connector.connect(**DB_CONFIG)
    cur = cnx.cursor(dictionary=True)
    cur.execute("""
        SELECT f.*, c.nom AS client_name,
               n.libelle AS navire_name,
               m.libelle AS mode_label
          FROM factures f
     LEFT JOIN clients         c ON c.id = f.client_id
     LEFT JOIN navires         n ON n.id = f.navire_id
     LEFT JOIN mode_reglements m ON m.id = f.mode_reglement_id
         WHERE f.id = %s
    """, (inv_id,))
    inv = cur.fetchone()
    if not inv:
        cur.close(); cnx.close()
        return None, None

    cur.execute("""
        SELECT * FROM facture_lignes
         WHERE facture_id = %s
      ORDER BY position, id
    """, (inv_id,))
    lines = cur.fetchall()
    cur.close(); cnx.close()
    return inv, lines

def draw_footer(canvas, doc):
    canvas.saveState()
    footer_y = doc.bottomMargin / 2
    canvas.setFont("Helvetica", 8)
    for i, line in enumerate(FOOTER_TEXT.strip().split('\n')):
        canvas.drawCentredString(
            doc.leftMargin + doc.width/2,
            footer_y + (len(FOOTER_TEXT.split('\n'))-1 - i)*10,
            line
        )
    canvas.restoreState()

def build_invoice_flow(inv, lines, hide_tax, hide_mode, doc):
    """
    Returns a list of flowables for one invoice,
    respecting hide_tax & hide_mode.
    """
    styles    = getSampleStyleSheet()
    box_style = ParagraphStyle(
        'InfoBox', parent=styles['Normal'],
        borderColor=colors.black, borderWidth=1,
        borderPadding=6, leading=14, spaceAfter=6
    )
    small_dt = ParagraphStyle('SmallDT', parent=styles['Normal'], fontSize=8, leading=10)

    flow = []

    # 1) Logo
    logo_file = header_cfg.get('logo','').strip()
    if logo_file:
        logo_path = os.path.join(BASE_DIR, logo_file)
        if os.path.isfile(logo_path):
            img = Image(logo_path, width=300, height=100)
            img.hAlign = 'CENTER'
            flow += [img, Spacer(1,30)]

    # 2) Facture / Client boxes
    fact_par = Paragraph(
        f"<b>Facture</b><br/>Numéro : {inv['numero']}<br/>Date : {inv['date_facture']}",
        box_style
    )
    cli_html = f"<b>Client</b><br/>{inv.get('client_name','')}"
    if inv.get('navire_name'):
        cli_html += f"<br/>Navire : {inv['navire_name']}"
    client_par = Paragraph(cli_html, box_style)

    w = doc.width
    info_tbl = Table([[fact_par, client_par]],
                     colWidths=[w*0.45, w*0.45], hAlign='CENTER')
    info_tbl.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),6),
        ('RIGHTPADDING',(0,0),(-1,-1),6),
        ('RIGHTPADDING',(0,0),(0,0),12),
        ('LEFTPADDING',(1,0),(1,0),12),
    ]))
    flow += [info_tbl, Spacer(1,30)]

    # 3) Lines table
    headers = ['Réf.','Désignation','Check-in','Check-out','Qté','PU','Montant HT']
    col_w   = [60,180,70,70,30,60,60]
    tbl_data = [headers]

    for L in lines:
        # Check-in formatting
        ci = L.get('check_in')
        if isinstance(ci, datetime):
            d1,t1 = ci.strftime('%Y-%m-%d'), ci.strftime('%H:%M')
        elif isinstance(ci, str) and ' ' in ci:
            d1,t1 = ci.split(' ',1)
        else:
            d1,t1 = '',''
        ci_para = Paragraph(f"{d1}<br/>{t1}", small_dt)

        # Check-out formatting
        co = L.get('check_out')
        if isinstance(co, datetime):
            d2,t2 = co.strftime('%Y-%m-%d'), co.strftime('%H:%M')
        elif isinstance(co, str) and ' ' in co:
            d2,t2 = co.split(' ',1)
        else:
            d2,t2 = '',''
        co_para = Paragraph(f"{d2}<br/>{t2}", small_dt)

        qty = Decimal(str(L.get('quantite',0)))
        pu  = Decimal(str(L.get('prix_unitaire',0)))
        mt  = (qty * pu).quantize(Decimal('0.00'))

        tbl_data.append([
            Paragraph(L.get('reference','') or '', small_dt),
            L.get('designation','') or '',
            ci_para,
            co_para,
            str(int(qty)),
            f"{pu:.2f}",
            f"{mt:.2f}"
        ])

    # pad to at least 12 rows
    while len(tbl_data)-1 < 12:
        tbl_data.append(['']*7)

    tbl = Table(tbl_data, colWidths=col_w, repeatRows=1)
    style = [
        ('BOX',(0,0),(-1,-1),1,colors.grey),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
    ]
    for col in range(len(col_w)-1):
        style.append(('LINEAFTER',(col,0),(col,-1),0.5,colors.grey))
    tbl.setStyle(TableStyle(style))
    flow += [tbl, Spacer(1,16)]

    # 4) Summary
    total_ht  = sum(Decimal(str(l['quantite'])) * Decimal(str(l['prix_unitaire'])) for l in lines)
    total_tva = (total_ht * Decimal('0.20')).quantize(Decimal('0.01'))
    total_ttc = (total_ht + total_tva).quantize(Decimal('0.01'))

    words = to_french_words(total_ttc)
    left_txt = (
        "<i>Arrêté la présente facture en DIRHAMS NET A PAYER à la somme de :</i><br/>"
        f"<b>{words}</b>"
    )
    if not hide_mode and inv.get('mode_label') and inv.get('transaction_number'):
        left_txt += f"<br/>Mode : {inv['mode_label']}  N° Tx : {inv['transaction_number']}"

    left_par = Paragraph(left_txt, styles['Normal'])

    rows = [[Paragraph("Total HT :",styles['Normal']), f"{total_ht:.2f} Dh"]]
    if not hide_tax:
        rows.append([Paragraph("Total TVA :",styles['Normal']), f"{total_tva:.2f} Dh"])
        rows.append([Paragraph("<b>Total TTC :</b>",styles['Normal']), f"{total_ttc:.2f} Dh"])
    else:
        rows.append([Paragraph("<b>Total TTC :</b>",styles['Normal']), f"{total_ttc:.2f} Dh"])

    tot_tbl = Table(rows, colWidths=[80,100])
    tot_tbl.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),1,colors.black),
        ('ALIGN',(1,0),(-1,-1),'RIGHT'),
        ('FONTNAME',(0,0),(0,0),'Helvetica-Bold'),
        ('BOTTOMPADDING',(0,0),(-1,0),6),
    ]))

    summary = Table([[left_par, tot_tbl]],
                    colWidths=[w*0.45, w*0.45], hAlign='RIGHT')
    summary.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
    flow += [summary, Spacer(1,24)]

    # 5) Footer text
    #if FOOTER_TEXT:
       # flow.append(Paragraph(FOOTER_TEXT.replace('\n','<br/>'), styles['Normal']))

    return flow

# ――― SINGLE‐INVOICE PDF ROUTE ―――
@app.route('/api/invoice/pdf', methods=['POST'])
def invoice_pdf():
    data      = request.get_json(silent=True)
    if not data or 'id' not in data:
        return jsonify(error="Missing invoice id"), 400

    inv_id    = int(data['id'])
    hide_tax  = bool(data.get('hideTax', False))
    hide_mode = bool(data.get('hideMode', False))
    inv, lines= fetch_invoice(inv_id)
    if not inv:
        return abort(404, "Invoice not found")

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=20, rightMargin=20,
        topMargin=40, bottomMargin=80
    )

    flow = build_invoice_flow(inv, lines, hide_tax, hide_mode, doc)
    doc.build(flow, onFirstPage=draw_footer, onLaterPages=draw_footer)

    buf.seek(0)
    return send_file(
        buf,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=f"Facture_{inv['numero']}.pdf"
    )

# ――― BATCH‐EXPORT PDF ROUTE ―――
@app.route('/api/invoice/pdf/batch', methods=['POST'])
def invoice_pdf_batch():
    data      = request.get_json(force=True)
    ids       = data.get('ids') or []
    hide_tax  = bool(data.get('hideTax', False))
    hide_mode = bool(data.get('hideMode', False))

    if not isinstance(ids, list) or not ids:
        return jsonify(error="Aucun ID de facture fourni"), 400

    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for inv_id in ids:
            inv, lines = fetch_invoice(inv_id)
            if not inv: continue

            pdf_buf = BytesIO()
            doc = SimpleDocTemplate(
                pdf_buf, pagesize=A4,
                leftMargin=20, rightMargin=20,
                topMargin=40, bottomMargin=80
            )
            flow = build_invoice_flow(inv, lines, hide_tax, hide_mode, doc)
            doc.build(flow, onFirstPage=draw_footer, onLaterPages=draw_footer)

            pdf_buf.seek(0)
            fname = f"Facture_{inv['numero']}.pdf"
            zf.writestr(fname, pdf_buf.read())

    zip_buf.seek(0)
    return send_file(
        zip_buf,
        mimetype='application/zip',
        as_attachment=True,
        download_name='Factures.zip'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
