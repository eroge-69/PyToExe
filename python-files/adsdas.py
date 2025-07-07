# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd
import json
from datetime import datetime
import locale

# --- Importações do PySide6 ---
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QTabWidget, QTableView,
    QMessageBox, QFileDialog, QGroupBox, QHeaderView, QDialog, QDialogButtonBox,
    QScrollArea, QAbstractItemView, QComboBox, QSizePolicy, QStackedWidget
)
from PySide6.QtCore import (
    QAbstractTableModel, Qt, QModelIndex, QEvent
)
from PySide6.QtGui import QIcon, QDoubleValidator

# --- Lógica de Geração de PDF (ReportLab) ---
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ──────────────────────────────────────────────────────────────────────────────
# 1. ESTILIZAÇÃO E CONSTANTES
# ──────────────────────────────────────────────────────────────────────────────
COLOR_THISTLE = "#CDB4DB"
COLOR_FAIRY_TALE = "#FFC8DD"
COLOR_CARNATION_PINK = "#FFAFCC"
COLOR_URANIAN_BLUE = "#BDE0FE"
COLOR_LIGHT_SKY_BLUE = "#A2D2FF"
COLOR_BASE_WHITE = "#FCFCFC"
COLOR_DARK_TEXT = "#494949"

QSS_STYLE = f"""
    QWidget {{
        background-color: {COLOR_BASE_WHITE}; color: {COLOR_DARK_TEXT};
        font-family: Segoe UI, Arial, sans-serif; font-size: 10pt;
    }}
    QTabWidget::pane {{ border-top: 1px solid {COLOR_LIGHT_SKY_BLUE}; }}
    QTabBar::tab {{
        background: {COLOR_BASE_WHITE}; border: 1px solid {COLOR_LIGHT_SKY_BLUE};
        padding: 8px 20px; border-bottom: none;
    }}
    QTabBar::tab:selected {{
        background: {COLOR_BASE_WHITE}; border-bottom: 2px solid {COLOR_CARNATION_PINK};
    }}
    QTabBar::tab:!selected:hover {{ background: {COLOR_URANIAN_BLUE}; }}
    QPushButton {{
        background-color: {COLOR_THISTLE}; color: {COLOR_DARK_TEXT};
        border: none; padding: 8px 16px;
        border-radius: 4px; font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {COLOR_LIGHT_SKY_BLUE}; }}
    QPushButton:pressed {{ background-color: {COLOR_CARNATION_PINK}; }}
    QPushButton#importantButton, QPushButton#managePartsButton {{ background-color: {COLOR_CARNATION_PINK}; }}
    QPushButton#importantButton:hover, QPushButton#managePartsButton:hover {{ background-color: {COLOR_FAIRY_TALE}; }}
    QPushButton#deleteItemButton, QPushButton#dialogDeleteButton, QPushButton#deleteCategoryButton {{
        background-color: #ff6b6b; color: white;
    }}
    QPushButton#deleteItemButton:hover, QPushButton#dialogDeleteButton:hover, QPushButton#deleteCategoryButton:hover {{
        background-color: #ee5253;
    }}
    QPushButton#deleteItemButton {{ max-width: 30px; font-size: 12pt; }}
    QPushButton#deleteCategoryButton {{ padding: 2px 8px; font-size: 9pt; }}

    QPushButton#squareRegisterButton {{
        background-color: {COLOR_CARNATION_PINK};
        color: {COLOR_DARK_TEXT};
        font-size: 11pt; font-weight: bold;
        padding: 20px; border-radius: 10px;
    }}
    QPushButton#squareRegisterButton:hover {{ background-color: {COLOR_FAIRY_TALE}; }}
    QLineEdit, QTextEdit, QComboBox {{
        background-color: {COLOR_BASE_WHITE}; border: 1px solid {COLOR_LIGHT_SKY_BLUE};
        padding: 5px; border-radius: 4px;
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{ border: 1px solid {COLOR_THISTLE}; }}
    QLineEdit:read-only, QTextEdit:read-only {{
        background-color: #eeeeee;
        border: 1px solid #dddddd;
    }}
    QTableView {{
        background-color: {COLOR_BASE_WHITE}; border: 1px solid {COLOR_LIGHT_SKY_BLUE};
        gridline-color: {COLOR_URANIAN_BLUE};
    }}
    QTableView::item:selected {{
        background-color: {COLOR_URANIAN_BLUE}; color: {COLOR_DARK_TEXT};
    }}
    QHeaderView::section {{
        background-color: {COLOR_THISTLE}; color: {COLOR_DARK_TEXT};
        padding: 5px; border: none;
        border-bottom: 1px solid {COLOR_LIGHT_SKY_BLUE}; font-weight: bold;
    }}
    QGroupBox {{
        border: 1px solid {COLOR_LIGHT_SKY_BLUE}; border-radius: 5px;
        margin-top: 10px; font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin; subcontrol-position: top left;
        padding: 0 5px; left: 10px;
    }}
    QScrollBar:vertical {{
        border: none; background: {COLOR_BASE_WHITE};
        width: 12px; margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {COLOR_LIGHT_SKY_BLUE}; min-height: 20px; border-radius: 6px;
    }}
"""

FIELD_NAMES = ['os_number', 'data', 'nome', 'contato', 'veiculo', 'modelo', 'ano', 'placa',
               'quilometragem', 'observacoes', 'pecas', 'total_pecas', 'orcamento_aprovado', 'desconto']
DISPLAY_LABELS = {
    'os_number': 'Nº OS', 'data': 'Data', 'nome': 'Nome do Cliente', 'contato': 'Contato',
    'veiculo': 'Veículo', 'modelo': 'Modelo', 'ano': 'Ano', 'placa': 'Placa',
    'quilometragem': 'Quilometragem (km)', 'observacoes': 'Observações', 'pecas': 'Peças (JSON)',
    'total_pecas': 'Total Peças (R$)', 'orcamento_aprovado': 'Orçamento Aprovado?',
    'desconto': 'Desconto (R$)'
}

# ──────────────────────────────────────────────────────────────────────────────
# 2. LÓGICA DE NEGÓCIO (BACKEND)
# ──────────────────────────────────────────────────────────────────────────────
def validate_price(price_str):
    try: return float(str(price_str).replace(',', '.')) >= 0
    except: return False
def get_next_os_number(df):
    if df.empty or 'os_number' not in df.columns or df['os_number'].isnull().all(): return 1
    numeric_os = pd.to_numeric(df['os_number'], errors='coerce')
    return 1 if numeric_os.isnull().all() else int(numeric_os.max()) + 1
def compute_parts_total(pecas_data):
    total = 0.0
    if not isinstance(pecas_data, str) or not pecas_data: return 0.0
    try:
        categories = json.loads(pecas_data)
        for items in categories.values():
            for item in items:
                preco = float(item.get('preco', 0))
                quantidade = int(item.get('quantidade', 1))
                total += preco * quantidade
        return total
    except (json.JSONDecodeError, AttributeError): return 0.0
def load_and_prepare_csv(csv_path):
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        return pd.DataFrame(columns=FIELD_NAMES)
    try:
        df = pd.read_csv(csv_path, header=None, encoding='utf-8-sig', dtype=str).fillna('')
        num_cols_to_add = len(FIELD_NAMES) - len(df.columns)
        if num_cols_to_add > 0:
            for i in range(num_cols_to_add):
                df[len(df.columns)] = ''
        df.columns = FIELD_NAMES
        df.fillna({
            'pecas': '', 'total_pecas': '0', 'orcamento_aprovado': 'Não',
            'desconto': '0', 'quilometragem': ''
        }, inplace=True)
        df['total_pecas'] = df['pecas'].apply(compute_parts_total)
        return df
    except Exception as e:
        QMessageBox.critical(None, "Erro", f"Erro ao carregar ou processar o arquivo CSV:\n{e}")
        return pd.DataFrame(columns=FIELD_NAMES)
def save_csv(df, csv_path):
    try:
        df_to_save = df.reindex(columns=FIELD_NAMES, fill_value='')
        df_to_save.to_csv(csv_path, index=False, header=False, encoding='utf-8-sig')
        return True
    except Exception as e:
        QMessageBox.critical(None, "Erro", f"Erro ao salvar o arquivo CSV:\n{e}")
        return False

# Em seu arquivo, SUBSTITUA a função generate_invoice inteira por esta:

def generate_invoice(filename, customer, vehicle, invoice_number, notes, pecas_data):
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        except locale.Error:
            print("Aviso: Locale 'pt_BR.UTF-8' não encontrado.")
    
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=15*mm, bottomMargin=30*mm, leftMargin=20*mm, rightMargin=20*mm)
    color_header_table = colors.HexColor("#CDB4DB")
    color_dark_text = colors.HexColor("#494949")
    color_subtotal_bg = colors.HexColor("#F1E8FF")
    styles = getSampleStyleSheet()
    style_body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=color_dark_text, leading=12)
    style_body_right = ParagraphStyle('BodyRight', parent=style_body, alignment=2)
    style_h1 = ParagraphStyle('H1', parent=styles['h1'], fontName='Helvetica-Bold', fontSize=28, textColor=color_dark_text, spaceAfter=2, alignment=1)
    style_grand_total = ParagraphStyle('GrandTotal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=color_dark_text, alignment=2)
    story = []
    
    header_data = [[Paragraph("ORDEM DE SERVIÇO", style_h1)], [Paragraph(f"Data: {datetime.now():%d/%m/%Y} | OS Nº: {str(invoice_number).zfill(4)}", style_body)]]
    header_table = Table(header_data, colWidths=[170*mm])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (0,0), (0,0), 'CENTER'), ('ALIGN', (0,1), (0,1), 'LEFT'), ('BOTTOMPADDING', (0,0), (0,0), 10)]))
    story.append(header_table)
    story.append(Spacer(1, 10*mm))
    company_info = [Paragraph("<b>Auto Mecânica Anderson</b>", style_body), Paragraph("Rua Andréa Paulinetti, 383", style_body), Paragraph("Brooklin – São Paulo – SP", style_body)]
    client_vehicle_info = f"""
        <b>Cliente:</b> {customer.get('nome', 'N/A')}<br/>
        <b>Veículo:</b> {vehicle.get('veiculo', '')} {vehicle.get('modelo', '')} {vehicle.get('ano', '')}<br/>
        <b>Placa:</b> {vehicle.get('placa', '')} | <b>KM:</b> {customer.get('quilometragem', 'N/A')} | <b>Tel:</b> {customer.get('contato', '')}
    """
    client_info = [Paragraph(client_vehicle_info, style_body)]
    info_table = Table([[company_info, client_info]], colWidths=[85*mm, 85*mm])
    info_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(info_table)
    story.append(Spacer(1, 5*mm))

    # --- NOVO BLOCO PARA ADICIONAR AS OBSERVAÇÕES ---
    # Verifica se o campo 'notes' (observacoes) não está vazio
    if notes and notes.strip():
        # Substitui quebras de linha por <br/> para o ReportLab
        formatted_notes = notes.strip().replace('\n', '<br/>')
        notes_paragraph = Paragraph(f"<b>Observações:</b><br/>{formatted_notes}", style_body)
        
        # Cria uma tabela para desenhar uma borda ao redor das observações
        notes_table = Table([[notes_paragraph]], colWidths=[170*mm])
        notes_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(notes_table)
    # --- FIM DO NOVO BLOCO ---

    story.append(Spacer(1, 10*mm))

    subtotal = compute_parts_total(pecas_data)
    try:
        discount_str = str(customer.get('desconto', '0')).replace(',', '.')
        discount = float(discount_str) if discount_str else 0
    except (ValueError, TypeError):
        discount = 0.0

    try:
        categories = json.loads(pecas_data)
        for category_name, items in categories.items():
            if not items: continue
            story.append(Paragraph(f"<b>Categoria: {category_name}</b>", style_body))
            story.append(Spacer(1, 2*mm))
            
            table_header = [Paragraph("<b>Descrição</b>", style_body), Paragraph("<b>Quant.</b>", style_body), Paragraph("<b>Vlr. Unit.</b>", style_body), Paragraph("<b>Vlr. Total</b>", style_body)]
            category_data = [table_header]
            
            category_subtotal = 0.0
            for item in items:
                price = float(item.get('preco', 0))
                quantity = int(item.get('quantidade', 1))
                total_item = price * quantity
                category_subtotal += total_item
                category_data.append([
                    Paragraph(item.get('descricao', ''), style_body), Paragraph(str(quantity), style_body),
                    Paragraph(locale.currency(price, grouping=True), style_body_right), Paragraph(locale.currency(total_item, grouping=True), style_body_right)
                ])

            category_data.append([
                Paragraph("<b>Subtotal da Categoria</b>", style_body_right), '', '',
                Paragraph(f"<b>{locale.currency(category_subtotal, grouping=True)}</b>", style_body_right)
            ])

            items_table = Table(category_data, colWidths=[90*mm, 20*mm, 30*mm, 30*mm])
            
            table_style = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), color_header_table),
                ('TEXTCOLOR', (0,0), (-1,0), color_dark_text),
                ('ALIGN', (1,0), (-1,-1), 'CENTER'),
                ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                ('BOTTOMPADDING', (0,0), (-1,0), 5),
                ('TOPPADDING', (0,0), (-1,0), 5),
                ('SPAN', (0, -1), (2, -1)),
                ('BACKGROUND', (0, -1), (-1, -1), color_subtotal_bg),
                ('ALIGN', (0, -1), (0,-1), 'RIGHT'),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 4),
                ('TOPPADDING', (0, -1), (-1, -1), 4)
            ])
            items_table.setStyle(table_style)
            story.append(items_table)
            story.append(Spacer(1, 8*mm))
    except (json.JSONDecodeError, TypeError): pass
    
    grand_total = subtotal - discount
    totals_data = [['Subtotal:', locale.currency(subtotal, grouping=True)],]
    if discount > 0:
        totals_data.append(['Desconto:', f"- {locale.currency(discount, grouping=True)}"])
    totals_data.append(['', '']) 
    totals_data.append([
        Paragraph("<b>Valor total:</b>", style_body_right),
        Paragraph(f"<b>{locale.currency(grand_total, grouping=True)}</b>", style_grand_total)
    ])
    summary_table = Table(totals_data, colWidths=[140*mm, 30*mm])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEABOVE', (0, -2), (-1, -2), 1, colors.grey), ('TOPPADDING', (0,-1), (-1,-1), 5)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 25*mm))
    style_signature = ParagraphStyle('Signature', parent=style_body, alignment=1)
    signature_line = "________________________________________"
    client_signature_content = [Paragraph(signature_line, style_signature), Paragraph(customer.get('nome', 'N/A'), style_signature), Paragraph("(Cliente)", style_signature)]
    mechanic_signature_content = [Paragraph(signature_line, style_signature), Paragraph("Anderson", style_signature), Paragraph("(Responsável Técnico)", style_signature)]
    signatures_table = Table([[client_signature_content, mechanic_signature_content]], colWidths=[85*mm, 85*mm])
    signatures_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(signatures_table)
    def footer(canvas, doc):
        canvas.saveState()
        terms_text = "<b>Termos e Condições:</b><br/>Garantia de 90 dias para peças e serviços. Este orçamento é válido por 7 dias.<br/><br/><b>Dúvidas?</b><br/>Email: contato.andersonmecanica@gmail.com"
        account_manager_text = "<b>Responsável Técnico:</b><br/>Anderson"
        p_terms = Paragraph(terms_text, style_body)
        p_manager = Paragraph(account_manager_text, style_body)
        terms_table = Table([[p_terms, p_manager]], colWidths=[100*mm, 70*mm])
        terms_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
        terms_table.wrapOn(canvas, doc.width, doc.bottomMargin)
        terms_table.drawOn(canvas, doc.leftMargin, 10*mm)
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)

# ──────────────────────────────────────────────────────────────────────────────
# 3. WIDGETS E MODELOS DE DADOS CUSTOMIZADOS
# ──────────────────────────────────────────────────────────────────────────────
class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event): event.ignore()

class EnterKeyFilter(QWidget):
    def __init__(self, *widgets_to_connect):
        super().__init__()
        self.widgets = widgets_to_connect
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if watched in self.widgets:
                try:
                    current_index = self.widgets.index(watched)
                    if current_index == len(self.widgets) - 1:
                        self.widgets[current_index].click()
                    else:
                        self.widgets[current_index + 1].setFocus()
                except (ValueError, IndexError): pass
                return True
        return super().eventFilter(watched, event)

class EditableItemWidget(QWidget):
    def __init__(self, cat_name, item_data, parent_handler):
        super().__init__()
        self.cat_name = cat_name
        self.item_data = item_data
        self.parent_handler = parent_handler

        self.stack = QStackedWidget()
        self._create_display_widget()
        self._create_edit_widget()
        self.stack.addWidget(self.display_widget)
        self.stack.addWidget(self.edit_widget)

        layout = QHBoxLayout()
        layout.addWidget(self.stack)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def _create_display_widget(self):
        self.display_widget = QWidget()
        layout = QHBoxLayout(self.display_widget)
        self.item_label = QLabel()
        self.item_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.item_label.installEventFilter(self)
        self.update_label_text()
        
        delete_button = QPushButton("X")
        delete_button.setObjectName("deleteItemButton")
        delete_button.clicked.connect(self._delete_item)

        layout.addWidget(self.item_label)
        layout.addWidget(delete_button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.display_widget.setLayout(layout)

    def _create_edit_widget(self):
        self.edit_widget = QWidget()
        layout = QHBoxLayout(self.edit_widget)
        
        self.desc_edit = QLineEdit(self.item_data['descricao'])
        self.price_edit = QLineEdit(f"{self.item_data['preco']:.2f}")
        self.price_edit.setValidator(QDoubleValidator(0, 999999, 2))
        self.qty_edit = NoScrollComboBox()
        self.qty_edit.addItems([str(i) for i in range(1, 51)])
        self.qty_edit.setCurrentText(str(self.item_data['quantidade']))
        
        save_button = QPushButton("Salvar")
        cancel_button = QPushButton("Cancelar")
        
        save_button.clicked.connect(self._save_edit)
        cancel_button.clicked.connect(self._cancel_edit)
        
        layout.addWidget(self.desc_edit)
        layout.addWidget(QLabel("Preço:"))
        layout.addWidget(self.price_edit)
        layout.addWidget(QLabel("Quant.:"))
        layout.addWidget(self.qty_edit)
        layout.addWidget(save_button)
        layout.addWidget(cancel_button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.edit_widget.setLayout(layout)

    def eventFilter(self, watched, event):
        if watched == self.item_label and event.type() == QEvent.Type.MouseButtonDblClick:
            self._show_edit_view()
            return True
        return super().eventFilter(watched, event)
    
    def _show_edit_view(self):
        self.desc_edit.setText(self.item_data['descricao'])
        self.price_edit.setText(f"{self.item_data['preco']:.2f}")
        self.qty_edit.setCurrentText(str(self.item_data['quantidade']))
        self.stack.setCurrentWidget(self.edit_widget)

    def _show_display_view(self):
        self.stack.setCurrentWidget(self.display_widget)

    def _save_edit(self):
        new_desc = self.desc_edit.text().strip()
        new_price_str = self.price_edit.text().replace(',', '.')
        
        if not new_desc or not validate_price(new_price_str):
            QMessageBox.warning(self, "Erro de Validação", "A descrição não pode ser vazia e o preço deve ser um número válido.")
            return

        self.item_data['descricao'] = new_desc
        self.item_data['preco'] = float(new_price_str)
        self.item_data['quantidade'] = int(self.qty_edit.currentText())

        self.update_label_text()
        self._show_display_view()
        
        if hasattr(self.parent_handler, '_update_category_subtotal'):
            self.parent_handler._update_category_subtotal(self.cat_name)
        
    def _cancel_edit(self):
        self._show_display_view()

    def _delete_item(self):
        self.parent_handler.delete_item(self.cat_name, self.item_data, self)

    def update_label_text(self):
        qty = self.item_data['quantidade']
        desc = self.item_data['descricao']
        price = self.item_data['preco']
        self.item_label.setText(f"  - {qty}x {desc} (R$ {price:.2f})")

class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
    def rowCount(self, parent=QModelIndex()): return self._data.shape[0]
    def columnCount(self, parent=QModelIndex()): return self._data.shape[1]
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                col_name = self._data.columns[section]
                return DISPLAY_LABELS.get(col_name, col_name.title())
            if orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        return None
    def refresh_data(self, new_data):
        self.beginResetModel(); self._data = new_data; self.endResetModel()

# ──────────────────────────────────────────────────────────────────────────────
# 4. JANELAS DE DIÁLOGO
# ──────────────────────────────────────────────────────────────────────────────

class PartsAndServicesDialog(QDialog):
    def __init__(self, current_items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciar Peças e Serviços")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        self.session_items = json.loads(json.dumps(current_items))
        self.category_widgets = {}

        main_layout = QVBoxLayout(self)
        
        category_add_layout = QHBoxLayout()
        self.new_category_input = QLineEdit()
        self.new_category_input.setPlaceholderText("Nome da Nova Categoria")
        self.add_category_button = QPushButton("Adicionar Nova Categoria")
        self.new_category_input.returnPressed.connect(self.add_category_button.click)
        self.add_category_button.clicked.connect(self.add_new_category)
        category_add_layout.addWidget(self.new_category_input)
        category_add_layout.addWidget(self.add_category_button)
        main_layout.addLayout(category_add_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.categories_layout = QVBoxLayout(scroll_content)
        self.categories_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)
        
        self._populate_categories()

    def _populate_categories(self):
        for cat_name, items in self.session_items.items():
            self.add_category_widget(cat_name)
            for item_data in items:
                self.add_item_widget(cat_name, item_data)
            self._update_category_subtotal(cat_name)

    def _update_category_subtotal(self, cat_name):
        if cat_name in self.session_items and cat_name in self.category_widgets:
            subtotal = sum(item['preco'] * item['quantidade'] for item in self.session_items[cat_name])
            subtotal_label = self.category_widgets[cat_name].get('subtotal_label')
            if subtotal_label:
                subtotal_label.setText(f"<b>Subtotal: R$ {subtotal:.2f}</b>")

    def add_new_category(self):
        cat_name = self.new_category_input.text().strip()
        if not cat_name: return
        if cat_name in self.session_items:
            QMessageBox.warning(self, "Atenção", "Nome da categoria já existe.")
            return
        self.session_items[cat_name] = []
        self.add_category_widget(cat_name)
        self.new_category_input.clear()

    def add_category_widget(self, cat_name):
        group_box = QGroupBox(cat_name)
        group_layout = QVBoxLayout()
        items_layout = QVBoxLayout()
        items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        subtotal_label = QLabel("<b>Subtotal: R$ 0.00</b>")
        subtotal_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        add_item_form = QFormLayout()
        desc_input = QLineEdit()
        price_input = QLineEdit()
        qty_input = NoScrollComboBox()
        qty_input.addItems([str(i) for i in range(1, 51)])
        add_item_button = QPushButton("+ Adicionar Item")
        
        event_filter = EnterKeyFilter(desc_input, price_input, qty_input, add_item_button)
        desc_input.installEventFilter(event_filter)
        price_input.installEventFilter(event_filter)
        qty_input.installEventFilter(event_filter)

        add_item_button.clicked.connect(lambda: self.add_item(cat_name, desc_input, price_input, qty_input, items_layout))
        add_item_form.addRow("Descrição:", desc_input)
        add_item_form.addRow("Preço:", price_input)
        add_item_form.addRow("Quant.:", qty_input)
        add_item_form.addRow(add_item_button)
        
        group_layout.addLayout(items_layout)
        group_layout.addWidget(subtotal_label)
        group_layout.addLayout(add_item_form)
        group_box.setLayout(group_layout)
        
        self.categories_layout.addWidget(group_box)
        self.category_widgets[cat_name] = {
            'group_box': group_box, 
            'items_layout': items_layout,
            'subtotal_label': subtotal_label
        }

    def add_item(self, cat_name, desc_input, price_input, qty_input, items_layout):
        desc = desc_input.text().strip()
        price_str = price_input.text().strip().replace(',', '.')
        if not (desc and validate_price(price_str)):
            QMessageBox.warning(self, "Erro", "Descrição ou preço do item inválido.")
            return
        qty = int(qty_input.currentText())
        price = float(price_str)
        item_data = {'descricao': desc, 'preco': price, 'quantidade': qty}
        self.session_items[cat_name].append(item_data)
        self.add_item_widget(cat_name, item_data)
        
        self._update_category_subtotal(cat_name)

        desc_input.clear(); price_input.clear(); qty_input.setCurrentIndex(0)
        desc_input.setFocus()

    def add_item_widget(self, cat_name, item_data):
        item_widget = EditableItemWidget(cat_name, item_data, self)
        self.category_widgets[cat_name]['items_layout'].addWidget(item_widget)

    def delete_item(self, cat_name, item_to_delete, item_widget):
        try:
            self.session_items[cat_name].remove(item_to_delete)
            item_widget.deleteLater()
            self._update_category_subtotal(cat_name)
        except (ValueError, KeyError):
             QMessageBox.warning(self, "Erro", "Não foi possível remover o item.")
    
    def get_data(self):
        return self.session_items

class FullEditDialog(QDialog):
    DeleteRole = 1001

    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Editando OS Nº {record.get('os_number', '')} - {record.get('nome', '')}")
        self.setMinimumWidth(600)
        
        self.session_items = {}
        main_layout = QVBoxLayout(self)
        
        main_data_group = QGroupBox("Dados do Cliente e Veículo")
        form_layout = QFormLayout()
        self.fields = {}
        fields_to_create = [('os_number', 'Nº OS'), ('data', 'Data'), ('nome', 'Nome'), ('contato', 'Contato'), 
                            ('veiculo', 'Veículo'), ('modelo', 'Modelo'), ('ano', 'Ano'), ('placa', 'Placa'),
                            ('quilometragem', 'Quilometragem (km)')]
        for key, label in fields_to_create:
            widget = QLineEdit(); self.fields[key] = widget; form_layout.addRow(label, widget)
        main_data_group.setLayout(form_layout)
        main_layout.addWidget(main_data_group)
        
        other_data_group = QGroupBox("Observações e Financeiro")
        extra_fields_layout = QHBoxLayout()
        obs_form = QFormLayout()
        self.fields['observacoes'] = QTextEdit(); self.fields['observacoes'].setFixedHeight(80)
        obs_form.addRow('Observações:', self.fields['observacoes'])
        status_form = QFormLayout()
        self.fields['orcamento_aprovado'] = QComboBox(); self.fields['orcamento_aprovado'].addItems(['Não', 'Sim'])
        self.fields['desconto'] = QLineEdit(); self.fields['desconto'].setValidator(QDoubleValidator(0, 99999, 2))
        status_form.addRow('Orçamento Aprovado?:', self.fields['orcamento_aprovado'])
        status_form.addRow('Desconto (R$):', self.fields['desconto'])
        extra_fields_layout.addLayout(obs_form); extra_fields_layout.addLayout(status_form)
        other_data_group.setLayout(extra_fields_layout)
        main_layout.addWidget(other_data_group)
        
        self.manage_parts_button = QPushButton("Gerenciar Peças e Serviços")
        self.manage_parts_button.setObjectName("managePartsButton")
        self.manage_parts_button.clicked.connect(self.open_parts_editor)
        main_layout.addWidget(self.manage_parts_button)

        self.button_box = QDialogButtonBox()
        ok_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        cancel_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        delete_button = self.button_box.addButton("Excluir Cadastro", QDialogButtonBox.ButtonRole.DestructiveRole)
        delete_button.setObjectName("dialogDeleteButton")
        ok_button.clicked.connect(self.accept); cancel_button.clicked.connect(self.reject)
        delete_button.clicked.connect(self.handle_delete)
        main_layout.addWidget(self.button_box)
        
        self.populate_data(record)

    def populate_data(self, record):
        for key, widget in self.fields.items():
            value = str(record.get(key, ''))
            if isinstance(widget, QLineEdit): widget.setText(value)
            elif isinstance(widget, QTextEdit): widget.setPlainText(value)
            elif isinstance(widget, QComboBox):
                index = widget.findText(value, Qt.MatchFlag.MatchFixedString)
                if index >= 0: widget.setCurrentIndex(index)
        try:
            self.session_items = json.loads(record.get('pecas', '{}'))
        except json.JSONDecodeError: 
            self.session_items = {}

    def open_parts_editor(self):
        dialog = PartsAndServicesDialog(self.session_items, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.session_items = dialog.get_data()
            QMessageBox.information(self, "Sucesso", "A lista de peças e serviços foi atualizada.")

    def handle_delete(self):
        reply = QMessageBox.question(self, "Confirmar Exclusão", "Você tem certeza que deseja excluir este cadastro?\nEsta ação não pode ser desfeita.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes: self.done(FullEditDialog.DeleteRole)
    
    def get_data(self):
        data = {field: widget.text() if isinstance(widget, QLineEdit) else (widget.toPlainText() if isinstance(widget, QTextEdit) else widget.currentText()) for field, widget in self.fields.items()}
        data['pecas'] = json.dumps(self.session_items, ensure_ascii=False, indent=2)
        return data

# ──────────────────────────────────────────────────────────────────────────────
# 5. JANELA PRINCIPAL DA APLICAÇÃO (PySide6)
# ──────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self, csv_path):
        super().__init__()
        self.csv_path = csv_path
        self.df = load_and_prepare_csv(csv_path)
        self.sort_dataframe()
        self.shared_pandas_model = PandasModel(self.df)
        self.session_items = {}; self.category_widgets = {}
        self.setWindowTitle("Sistema de Gestão de Clientes v6.5 - Subtotais")
        self.setGeometry(100, 100, 1000, 800)
        self.tabs = QTabWidget(); self.setCentralWidget(self.tabs)
        self._create_register_tab(); self._create_editor_tab(); self._create_invoice_tab()

    def sort_dataframe(self):
        if 'os_number' in self.df.columns and not self.df.empty:
            numeric_os = pd.to_numeric(self.df['os_number'], errors='coerce')
            self.df['sort_key'] = numeric_os
            self.df.sort_values(by='sort_key', ascending=False, inplace=True, na_position='last')
            self.df.drop(columns='sort_key', inplace=True)
            self.df.reset_index(drop=True, inplace=True)

    def _create_register_tab(self):
        tab = QWidget(); main_h_layout = QHBoxLayout(tab)
        left_column_widget = QWidget(); left_v_layout = QVBoxLayout(left_column_widget)
        form_layout = QFormLayout()
        self.register_fields = {}
        fields_to_create = [('os_number', 'Nº OS (auto se vazio)'), ('data', 'Data (DD/MM/YYYY)'), 
                            ('nome', 'Nome do Cliente'), ('contato', 'Contato'), ('veiculo', 'Veículo'), 
                            ('modelo', 'Modelo'), ('ano', 'Ano'), ('placa', 'Placa'),
                            ('quilometragem', 'Quilometragem (km)')]
        for key, label in fields_to_create:
            widget = QLineEdit()
            if key == 'data': widget.setText(datetime.now().strftime('%d/%m/%Y'))
            self.register_fields[key] = widget; form_layout.addRow(label, widget)
        extra_fields_layout = QHBoxLayout(); obs_form = QFormLayout()
        self.register_fields['observacoes'] = QTextEdit()
        obs_form.addRow('Observações:', self.register_fields['observacoes'])
        status_form = QFormLayout()
        self.register_fields['orcamento_aprovado'] = QComboBox(); self.register_fields['orcamento_aprovado'].addItems(['Não', 'Sim'])
        self.register_fields['desconto'] = QLineEdit(); self.register_fields['desconto'].setPlaceholderText("Ex: 50,00")
        self.register_fields['desconto'].setValidator(QDoubleValidator(0, 99999, 2))
        status_form.addRow('Orçamento Aprovado?:', self.register_fields['orcamento_aprovado'])
        status_form.addRow('Desconto (R$):', self.register_fields['desconto'])
        extra_fields_layout.addLayout(obs_form); extra_fields_layout.addLayout(status_form)
        left_v_layout.addLayout(form_layout); left_v_layout.addLayout(extra_fields_layout)
        left_v_layout.addStretch()
        right_column_widget = QGroupBox("Peças, Serviços e Finalização"); right_v_layout = QVBoxLayout(right_column_widget)
        category_layout = QHBoxLayout()
        self.new_category_input = QLineEdit()
        self.add_category_button = QPushButton("Adicionar Categoria")
        self.new_category_input.returnPressed.connect(self.add_category_button.click)
        self.add_category_button.clicked.connect(self.add_category)
        category_layout.addWidget(self.new_category_input); category_layout.addWidget(self.add_category_button)
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.categories_layout = QVBoxLayout(scroll_content)
        self.categories_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(scroll_content)
        self.register_button = QPushButton("Registrar Cliente"); self.register_button.setObjectName("squareRegisterButton")
        self.register_button.clicked.connect(self.register_client)
        right_v_layout.addLayout(category_layout); right_v_layout.addWidget(scroll_area)
        right_v_layout.addWidget(self.register_button)
        main_h_layout.addWidget(left_column_widget, 1); main_h_layout.addWidget(right_column_widget, 2)
        self.tabs.addTab(tab, "Cadastrar")
        
    def _create_shared_table_view(self):
        table_view = QTableView()
        table_view.setModel(self.shared_pandas_model)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        return table_view

    def _create_editor_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Visualizar e Editar Registros"))
        self.editor_table_view = self._create_shared_table_view()
        layout.addWidget(self.editor_table_view)
        button_layout = QHBoxLayout(); edit_button = QPushButton("Editar Registro Selecionado")
        save_button = QPushButton("Salvar Alterações no CSV")
        edit_button.clicked.connect(self.edit_record); save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(edit_button); button_layout.addWidget(save_button)
        layout.addLayout(button_layout); self.tabs.addTab(tab, "Editar Registros")
        
    def _create_invoice_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Gerar Orçamento em PDF"))
        self.invoice_table_view = self._create_shared_table_view()
        layout.addWidget(self.invoice_table_view)
        generate_button = QPushButton("Gerar PDF para Selecionado"); generate_button.setObjectName("importantButton")
        generate_button.clicked.connect(self.generate_selected_invoice)
        layout.addWidget(generate_button); self.tabs.addTab(tab, "Gerar PDF")
    
    def _update_category_subtotal(self, cat_name):
        if cat_name in self.session_items and cat_name in self.category_widgets:
            subtotal = sum(item['preco'] * item['quantidade'] for item in self.session_items[cat_name])
            subtotal_label = self.category_widgets[cat_name].findChild(QLabel, "subtotalLabel")
            if subtotal_label:
                subtotal_label.setText(f"<b>Subtotal: R$ {subtotal:.2f}</b>")

    def add_category(self):
        cat_name = self.new_category_input.text().strip()
        if not cat_name or cat_name in self.session_items:
            QMessageBox.warning(self, "Atenção", "Nome da categoria está vazio ou já existe.")
            return
        self.session_items[cat_name] = []
        group_box = QGroupBox(cat_name)
        group_layout = QVBoxLayout(); items_layout = QVBoxLayout(); items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        subtotal_label = QLabel("<b>Subtotal: R$ 0.00</b>")
        subtotal_label.setObjectName("subtotalLabel")
        subtotal_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        add_item_form = QFormLayout()
        desc_input = QLineEdit(); price_input = QLineEdit()
        qty_input = NoScrollComboBox(); qty_input.addItems([str(i) for i in range(1, 51)])
        add_item_button = QPushButton("+ Adicionar Item")
        
        event_filter = EnterKeyFilter(desc_input, price_input, qty_input, add_item_button)
        desc_input.installEventFilter(event_filter)
        price_input.installEventFilter(event_filter)
        qty_input.installEventFilter(event_filter)

        add_item_button.clicked.connect(lambda: self.add_item(cat_name, desc_input, price_input, qty_input, items_layout))
        add_item_form.addRow("Descrição:", desc_input); add_item_form.addRow("Preço:", price_input)
        add_item_form.addRow("Quant.:", qty_input); add_item_form.addRow(add_item_button)
        
        group_layout.addLayout(items_layout)
        group_layout.addWidget(subtotal_label)
        group_layout.addLayout(add_item_form)
        group_box.setLayout(group_layout)
        
        self.categories_layout.addWidget(group_box)
        self.category_widgets[cat_name] = group_box
        self.new_category_input.clear()

    def add_item(self, cat_name, desc_widget, price_widget, qty_widget, layout_to_add):
        desc = desc_widget.text().strip()
        price_str = price_widget.text().strip().replace(',', '.')
        if desc:
            try: price = float(price_str) if price_str else 0.0
            except ValueError: price = 0.0
            qty = int(qty_widget.currentText())
            item_data = {'descricao': desc, 'preco': price, 'quantidade': qty}
            self.session_items[cat_name].append(item_data)
            
            item_widget = EditableItemWidget(cat_name, item_data, self)
            layout_to_add.addWidget(item_widget)

            self._update_category_subtotal(cat_name)

            desc_widget.clear(); price_widget.clear(); qty_widget.setCurrentIndex(0)
            desc_widget.setFocus()
        else:
            QMessageBox.warning(self, "Erro", "Descrição do item não pode estar vazia.")

    def delete_item(self, cat_name, item_to_delete, item_widget):
        try:
            self.session_items[cat_name].remove(item_to_delete)
            item_widget.deleteLater()
            self._update_category_subtotal(cat_name)
        except (ValueError, KeyError):
             QMessageBox.warning(self, "Erro", "Não foi possível remover o item.")
            
    def register_client(self):
        values = {key: widget.currentText() if isinstance(widget, QComboBox) else (widget.toPlainText() if isinstance(widget, QTextEdit) else widget.text())
                  for key, widget in self.register_fields.items()}
        if not values['nome'].strip():
            QMessageBox.critical(self, "Erro de Validação", "O campo Nome é obrigatório.")
            return
            
        os_number = values['os_number'].strip() or get_next_os_number(self.df)
        pecas_json = json.dumps(self.session_items, ensure_ascii=False, indent=2)

        new_record = {
            'os_number': os_number, 'data': values['data'], 'nome': values['nome'], 'contato': values['contato'],
            'veiculo': values['veiculo'], 'modelo': values['modelo'], 'ano': values['ano'], 'placa': values['placa'],
            'quilometragem': values['quilometragem'], 'observacoes': values['observacoes'],
            'pecas': pecas_json, 'total_pecas': compute_parts_total(pecas_json),
            'orcamento_aprovado': values['orcamento_aprovado'], 'desconto': values['desconto']
        }

        new_record_df = pd.DataFrame([new_record])
        self.df = pd.concat([self.df, new_record_df], ignore_index=True)
        if save_csv(self.df, self.csv_path):
            QMessageBox.information(self, "Sucesso", f"Cliente registrado com a OS Nº: {os_number}")
            self.sort_dataframe()
            self.shared_pandas_model.refresh_data(self.df)
            self.clear_registration_form()

    def clear_registration_form(self):
        for key, widget in self.register_fields.items():
            if key == 'data': widget.setText(datetime.now().strftime('%d/%m/%Y'))
            elif isinstance(widget, QComboBox): widget.setCurrentIndex(0)
            else: widget.clear()
        
        for cat_name, widget in self.category_widgets.items(): widget.deleteLater()
        
        self.category_widgets.clear(); self.session_items.clear()
        
    def edit_record(self):
        selected_indexes = self.editor_table_view.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "Atenção", "Selecione uma linha para editar.")
            return
        row_index = selected_indexes[0].row()
        original_index = self.df.index[row_index]
        record = self.df.loc[original_index].copy()
        dialog = FullEditDialog(record, self)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            edited_data = dialog.get_data()
            for field, value in edited_data.items():
                self.df.loc[original_index, field] = value
            self.df.loc[original_index, 'total_pecas'] = compute_parts_total(edited_data.get('pecas', ''))
            self.sort_dataframe(); self.shared_pandas_model.refresh_data(self.df)
            QMessageBox.information(self, "Sucesso", "Registro atualizado. Clique em 'Salvar Alterações' para gravar no CSV.")
        elif result == FullEditDialog.DeleteRole:
            self.df.drop(original_index, inplace=True)
            self.sort_dataframe(); self.shared_pandas_model.refresh_data(self.df)
            QMessageBox.information(self, "Sucesso", "O registro foi excluído. Clique em 'Salvar Alterações' para gravar no CSV.")

    def save_changes(self):
        if save_csv(self.df, self.csv_path):
            QMessageBox.information(self, "Sucesso", "Todas as alterações foram salvas no arquivo CSV.")
            
    def generate_selected_invoice(self):
        selected_indexes = self.invoice_table_view.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "Atenção", "Selecione uma linha para gerar o PDF.")
            return
        row_index = selected_indexes[0].row()
        rec = self.df.iloc[row_index]
        os_num = str(rec.get('os_number', '0')).zfill(4)
        client_name = str(rec.get('nome', 'Cliente')).replace(' ', '_')
        vehicle = f"{rec.get('veiculo', '')} {rec.get('modelo', '')}".strip().replace(' ', '_')
        default_path = f"OS_{os_num}_{client_name}_{vehicle}.pdf" if vehicle else f"OS_{os_num}_{client_name}.pdf"
        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar PDF como...", default_path, "PDF Files (*.pdf)")
        if save_path:
            try:
                generate_invoice(save_path, rec, rec, rec['os_number'], rec['observacoes'], rec['pecas'])
                QMessageBox.information(self, "Sucesso", f"PDF gerado com sucesso em:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao gerar o PDF:\n{e}")

# ──────────────────────────────────────────────────────────────────────────────
# 6. PONTO DE ENTRADA DA APLICAÇÃO
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    def resource_path(relative_path):
        try: base_path = sys._MEIPASS
        except Exception: base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    if getattr(sys, 'frozen', False): base_dir = os.path.dirname(sys.executable)
    else: base_dir = os.path.dirname(os.path.abspath(__file__))
    
    data_dir = os.path.join(base_dir, "Base de Dados")
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    csv_path = os.path.join(data_dir, "Banco de dados clientes.csv")

    icon_path = resource_path('2logonovo.ico')
    if os.path.exists(icon_path): app.setWindowIcon(QIcon(icon_path))
    else:
        icon_path_png = resource_path('2logonovo.png')
        if os.path.exists(icon_path_png): app.setWindowIcon(QIcon(icon_path_png))

    app.setStyleSheet(QSS_STYLE)
    main_window = MainWindow(csv_path)
    main_window.show()
    sys.exit(app.exec())