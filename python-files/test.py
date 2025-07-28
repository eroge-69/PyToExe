import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton, QFileDialog,
    QSizePolicy, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import textwrap

structure = {
    "Informations générales": {
        "Ingénieur Technique": "text",
        "Entreprise utilisatrice": "text",
        "Numéro de série Biochrom": "text",
        "Date révision (JJ/MM/AAAA)": "text",
    },
    "Autosampler": {
        "Aiguille échantillon": ["remplacée", "vérifiée", "nettoyée et vérifiée", "N/A"],
        "Aiguille air 62mm": ["remplacée", "vérifiée", "nettoyée et vérifiée", "N/A"],
        "seringue 500µL": ["remplacée", "vérifiée", "nettoyée et vérifiée", "N/A"],
        "Rotor Seal": ["remplacée", "vérifiée", "nettoyée et vérifiée", "N/A"],
        "Port de rinçage": ["Démonté et nettoyé", "N/A"],
        "Etat général de l'appareil": "text",
        "Commentaire": "textarea"
    },
    "Biochrom - Pompe Ninhydrine": {
        "céramiques": ["démontées et nettoyées", "remplacées", "coincées et nettoyées", "N/A"],
        "Joints de pompe": ["Remplacés", "N/A"],
        "pistons": ["Remplacés", "nettoyés", "N/A"],
        "Clapets": ["Remplacés", "nettoyés", "N/A"],
        "Commentaires": "textarea"
    },
    "Biochrom - Pompe tampon": {
        "céramiques": ["démontées et nettoyées", "remplacées", "coincées et nettoyées", "N/A"],
        "Joints de pompe": ["Remplacés", "N/A"],
        "pistons": ["Remplacés", "nettoyés", "N/A"],
        "Clapets": ["Remplacés", "nettoyés", "N/A"],
        "Commentaires": "textarea"
    },
    "Biochrom - Divers": {
        "Lampe hallogène": ["remplacée et alignée", "vérifiée et alignée", "N/A"],
        "Filtre ligne tampon et Ninhydrine": ["Remplacés", "vérifiés", "N/A"],
        "Niveau d'huile coil": ["vérifié", "complété", "N/A"],
        "Contrepressions 53 Psi": ["Nettoyées", "vérifiées", "N/A"],
        "Diaphragme coil flush": ["vérifiés", "remplacés", "N/A"],
        "Cellule de détection": ["nettoyée", "remplacée", "fenêtres remplacées", "N/A"],
        "Commentaires": "textarea"
    },
    "Validation": {
        "Bruit de fond": ["OK", "Mauvais", "N/A"],
        "Pression pompes": ["OK", "Faible", "Forte", "N/A"],
        "Séquence": ["Complète", "Incomplète", "N/A"],
        "Commentaires": "textarea"
    },
}

couleurs = [
    colors.HexColor("#1f497d"),
    colors.HexColor("#4bacc6"),
    colors.HexColor("#c0504d"),
    colors.HexColor("#9bbb59"),
    colors.HexColor("#8064a2"),
    colors.HexColor("#f79646"),
]

from PyQt5.QtWidgets import QLineEdit, QTextEdit, QComboBox

class QuestionnaireApp(QTabWidget):
    def __init__(self, entete_path=None):
        super().__init__()
        self.entete_path = entete_path or "entete.png"  # fichier par défaut
        self.answer_widgets = []
        self.initUI()
        self.setMinimumSize(700, 600)

    def initUI(self):
        for partie, questions in structure.items():
            w = QWidget()
            main_layout = QVBoxLayout()
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll_content = QWidget()
            v_layout = QVBoxLayout()
            self.answer_widgets.append({})
            for q_name, q_type in questions.items():
                h = QHBoxLayout()
                label = QLabel(q_name)
                label.setMinimumWidth(200)
                label.setWordWrap(True)
                h.addWidget(label)
                if isinstance(q_type, list):
                    cb = QComboBox()
                    cb.addItems(q_type)
                    cb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    h.addWidget(cb)
                    self.answer_widgets[-1][q_name] = cb
                elif q_type == "text":
                    le = QLineEdit()
                    le.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    h.addWidget(le)
                    self.answer_widgets[-1][q_name] = le
                elif q_type == "textarea":
                    te = QTextEdit()
                    te.setMinimumHeight(60)
                    te.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    h.addWidget(te)
                    self.answer_widgets[-1][q_name] = te
                else:
                    le = QLineEdit()
                    h.addWidget(le)
                    self.answer_widgets[-1][q_name] = le
                v_layout.addLayout(h)
            v_layout.addStretch()
            scroll_content.setLayout(v_layout)
            scroll.setWidget(scroll_content)
            main_layout.addWidget(scroll)
            w.setLayout(main_layout)
            self.addTab(w, partie)

        btn_pdf = QPushButton("Imprimer en PDF")
        btn_pdf.clicked.connect(self.generate_pdf)
        self.setCornerWidget(btn_pdf, Qt.TopRightCorner)

        btn_clear = QPushButton("Effacer tout")
        btn_clear.clicked.connect(self.clear_all_fields)
        self.setCornerWidget(btn_clear, Qt.TopLeftCorner)

    def clear_all_fields(self):
        for page_widgets in self.answer_widgets:
            for w in page_widgets.values():
                if isinstance(w, QLineEdit) or isinstance(w, QTextEdit):
                    w.clear()
                elif isinstance(w, QComboBox):
                    w.setCurrentIndex(0)

    def generate_pdf(self):
        from reportlab.lib.utils import ImageReader

        fname, _ = QFileDialog.getSaveFileName(self, "Enregistrer PDF", "", "Fichiers PDF (*.pdf)")
        if not fname:
            return

        entete_exists = False
        if self.entete_path and os.path.isfile(self.entete_path):
            try:
                img = ImageReader(self.entete_path)
                entete_exists = True
            except Exception:
                QMessageBox.warning(self, "Attention", "Erreur lors du chargement de l’entête. Elle sera omise du PDF.")
        else:
            QMessageBox.information(self, "Information", "Fichier entête non trouvé, il sera omis du PDF.")

        c = canvas.Canvas(fname, pagesize=A4)
        width, height = A4
        margin = 30
        rect_w = width - 2 * margin

        page_number = 1
        font_name = "Helvetica"
        font_size = 11
        line_height = 13
        v_padding = 12
        h_padding = 18
        blank_vspace = 18
        question_resp_space = 7
        title_height = 28
        entete_offset = 0

        img_width = 210
        img_height = 48

        def draw_entete():
            if entete_exists:
                c.drawImage(img, (width - img_width) / 2, height - img_height - 10, img_width, img_height, mask='auto')

        def page_footer():
            c.setFillColor(colors.black)
            c.setFont(font_name + "-Oblique", 9)
            c.drawRightString(width - margin, margin / 2, f"Page {page_number}")

        y_top_initial = height - margin * 2.5
        y = y_top_initial
        if entete_exists:
            draw_entete()
            entete_offset = img_height + 18
            y -= entete_offset

        for i, (partie, questions) in enumerate(structure.items()):
            couleur_section = couleurs[i % len(couleurs)]

            min_space_needed = title_height + 2 * (line_height + v_padding)
            if y - min_space_needed < margin:
                page_footer()
                c.showPage()
                page_number += 1
                y = y_top_initial

            c.setFont(font_name + "-Bold", 18)
            c.setFillColor(couleur_section)
            c.drawCentredString(width / 2, y, partie)
            c.setLineWidth(1)
            c.line(margin, y - 4, width - margin, y - 4)
            y -= title_height + 4

            question_names = list(questions.keys())
            n = len(question_names)
            left_count = (n + 1) // 2
            right_count = n - left_count

            columns = [
                question_names[:left_count],
                question_names[left_count:]
            ]

            largecase_wtot = rect_w * 0.8
            col_sep = 16
            box_width = (largecase_wtot - col_sep) / 2
            col_x = [margin + (rect_w - largecase_wtot) / 2,
                     margin + (rect_w - largecase_wtot) / 2 + box_width + col_sep]
            col_y = [y, y]

            max_rows = max(len(columns[0]), len(columns[1]))

            for row in range(max_rows):
                blocks = []
                for col in (0, 1):
                    if row < len(columns[col]):
                        q_name = columns[col][row]
                        try:
                            w = self.answer_widgets[i][q_name]
                        except KeyError as e:
                            print(f"Erreur d'accès au widget {q_name} (clé manquante) : {e}")
                            blocks.append(None)
                            continue
                        try:
                            if isinstance(w, QLineEdit):
                                rep = w.text()
                            elif isinstance(w, QTextEdit):
                                rep = w.toPlainText()
                            elif isinstance(w, QComboBox):
                                rep = w.currentText()
                            else:
                                rep = ""
                        except Exception as e:
                            print(f"Erreur d'accès au widget {q_name} : {e}")
                            rep = ""
                        rep_lines_full = rep.splitlines() if rep else [""]
                        q_lines = textwrap.wrap(q_name, 32) or [""]
                        r_lines = []
                        for l in rep_lines_full:
                            r_lines.extend(textwrap.wrap(l, 32) or [""])
                        contenu_height = (len(q_lines) + len(r_lines)) * line_height + question_resp_space
                        cadre_height = contenu_height + v_padding

                        blocks.append({
                            "x": col_x[col],
                            "y": col_y[col],
                            "cadre_height": cadre_height,
                            "q_lines": q_lines,
                            "r_lines": r_lines,
                            "couleur_section": couleur_section,
                        })
                    else:
                        blocks.append(None)

                row_height = max(block["cadre_height"] if block else 0 for block in blocks)
                need_break = any(col_y[col] - row_height - blank_vspace < margin for col in (0, 1))
                if need_break:
                    page_footer()
                    c.showPage()
                    page_number += 1
                    y = y_top_initial
                    if entete_exists and page_number == 1:
                        draw_entete()
                        y -= entete_offset
                    col_y = [y, y]
                    c.setFont(font_name + "-Bold", 18)
                    c.setFillColor(couleur_section)
                    c.drawCentredString(width / 2, y, partie)
                    c.setLineWidth(1)
                    c.line(margin, y - 4, width - margin, y - 4)
                    y -= title_height + 4

                for col in (0, 1):
                    block = blocks[col]
                    if block:
                        x = block["x"]
                        y_block = col_y[col]

                        c.setFillColor(colors.HexColor("#f5f5f5"))
                        c.rect(x, y_block - row_height, box_width, row_height, stroke=0, fill=1)

                        c.setStrokeColor(block["couleur_section"])
                        c.setLineWidth(1)
                        c.rect(x, y_block - row_height, box_width, row_height, stroke=1, fill=0)

                        contenu_height = (len(block["q_lines"]) + len(block["r_lines"])) * line_height + question_resp_space

                        top_text_y = y_block - (v_padding / 2) - (row_height - contenu_height) / 2

                        c.setFont(font_name + "-Bold", font_size)
                        c.setFillColor(colors.blue)
                        for idx, line in enumerate(block["q_lines"]):
                            c.drawString(x + h_padding, top_text_y - idx * line_height, line)

                        y_resp = top_text_y - len(block["q_lines"]) * line_height - question_resp_space
                        c.setFont(font_name, font_size)
                        c.setFillColor(colors.green)
                        for idx, line in enumerate(block["r_lines"]):
                            c.drawString(x + h_padding, y_resp - idx * line_height, line)

                        col_y[col] -= row_height + blank_vspace

                y = min(col_y)

            y = min(col_y)

        page_footer()
        c.save()
        QMessageBox.information(self, "PDF créé", f"Le fichier PDF a été enregistré :\n{fname}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    entete_path = "entete.png"  # Modifiez ici si besoin
    wnd = QuestionnaireApp(entete_path=entete_path)
    wnd.setWindowTitle("Questionnaire Maintenance Biochrom")
    wnd.show()
    sys.exit(app.exec_())
