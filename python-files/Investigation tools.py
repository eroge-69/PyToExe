from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import pandas as pd
import os

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), colorize=False, parent=None):
        super().__init__(parent)
        self._df = df
        self.colorize = colorize

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        cell_value = self._df.iloc[index.row(), index.column()]
        value = "" if pd.isna(cell_value) else str(cell_value)

        if role == QtCore.Qt.DisplayRole:
            return value

        if role == QtCore.Qt.BackgroundRole and self.colorize:
            try:
                status = str(self._df.iloc[index.row(), 8]).strip().lower()
                ticket_id = str(self._df.iloc[index.row(), 0]).strip()
                id_counts = self._df[self._df.columns[0]].astype(str).str.strip().value_counts()

                if status == "open":
                    if id_counts[ticket_id] == 1:
                        return QtGui.QColor("#2BE265")  # Vert
                    else:
                        return QtGui.QColor("#55EDEB")  # Bleu
                elif status == "closed":
                    if id_counts[ticket_id] == 1:
                        return QtGui.QColor("#F5DD7F")  # Jaune
                    else:
                        return QtGui.QColor("#E57B7B")  # Rouge
            except Exception as e:
                print(f"Erreur coloration: {e}")
                return None

        if role == QtCore.Qt.FontRole and self.colorize:
            return QtGui.QFont("Times New Roman", 9, QtGui.QFont.Bold)

        if role == QtCore.Qt.ForegroundRole and self.colorize:
            return QtGui.QBrush(QtGui.QColor("black"))

        return None

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._df.columns[section]
            else:
                return section + 1
        elif role == QtCore.Qt.BackgroundRole and orientation == QtCore.Qt.Horizontal:
            return QtGui.QColor("#8A2BE2")
        elif role == QtCore.Qt.ForegroundRole and orientation == QtCore.Qt.Horizontal:
            return QtGui.QBrush(QtGui.QColor("white"))
        elif role == QtCore.Qt.FontRole and orientation == QtCore.Qt.Horizontal:
            font = QtGui.QFont("Times New Roman", 9)
            font.setBold(True)
            return font
        return None

    def set_dataframe(self, df):
        self.beginResetModel()
        self._df = df
        self.endResetModel()

class AnalysisModel(PandasModel):
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        cell_value = self._df.iloc[index.row(), index.column()]
        value = "" if pd.isna(cell_value) else str(cell_value)

        if role == QtCore.Qt.DisplayRole:
            return value

        if role == QtCore.Qt.BackgroundRole:
            try:
                row = self._df.iloc[index.row()]
                if not pd.isna(row[4]) and str(row[4]).strip():
                    return QtGui.QColor("#87CEFA")  # Bleu ciel
                if not pd.isna(row[7]) and str(row[7]).strip():
                    return QtGui.QColor("#90EE90")  # Vert clair
                if not pd.isna(row[9]) and str(row[9]).strip():
                    return QtGui.QColor("#FFFF99")  # Jaune (col 10)
                if not pd.isna(row[10]) and str(row[10]).strip():
                    return QtGui.QColor("#DA70D6")  # Magenta (col 11)
            except Exception as e:
                print(f"Erreur coloration analysis: {e}")

        if role == QtCore.Qt.FontRole:
            return QtGui.QFont("Times New Roman", 9, QtGui.QFont.Bold)

        if role == QtCore.Qt.ForegroundRole:
            return QtGui.QBrush(QtGui.QColor("black"))

        return None

class FilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.column_filters = {}

    def setFilterForColumn(self, column, pattern):
        if pattern:
            self.column_filters[column] = pattern.lower()
        elif column in self.column_filters:
            del self.column_filters[column]
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        for column, pattern in self.column_filters.items():
            index = model.index(source_row, column, source_parent)
            data = str(model.data(index, QtCore.Qt.DisplayRole)).lower()
            if pattern not in data:
                return False
        return True

class ExcelViewer(QtWidgets.QWidget):
    def __init__(self, cm_path, analysis_path):
        super().__init__()
        self.setWindowTitle("Customer Complaint Investigation Tools")
        self.setGeometry(0, 0, 1900, 1080)

        # Fond noir + scroll bar style
        base_style = "background-color: black;"
        scroll_style = """
        QScrollBar:vertical, QScrollBar:horizontal {
            background-color: white;
            width: 14px;
        }
        QScrollBar::handle {
            background-color: #8A2BE2;
            border-radius: 6px;
        }
        QScrollBar::handle:hover {
            background-color: #A060F0;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            background: none;
        }
        """
        self.setStyleSheet(base_style + scroll_style)

        layout = QtWidgets.QVBoxLayout(self)

        # Recherche layout
        search_layout = QtWidgets.QHBoxLayout()
        self.search_fields = [QtWidgets.QLineEdit() for _ in range(3)]
        for field in self.search_fields:
            field.setPlaceholderText("Recherche...")
            field.setStyleSheet("background-color: white; color: black;")
            search_layout.addWidget(field)

        button_style = """
            QPushButton {
                background-color: #8A2BE2;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #A060F0;
            }
        """

        self.search_cm_btn = QtWidgets.QPushButton("Search CM")
        self.search_cm_btn.setStyleSheet(button_style)

        self.search_analysis_btn = QtWidgets.QPushButton("Search Analysis")
        self.search_analysis_btn.setStyleSheet(button_style)

        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_btn.setStyleSheet(button_style)

        self.filter_green_btn = QtWidgets.QPushButton("Filtrer Vert (Open & Unique)")
        self.filter_green_btn.setStyleSheet(button_style)

        self.export_btn = QtWidgets.QPushButton("Exporter Excel (vue actuelle)")
        self.export_btn.setStyleSheet(button_style)

        for btn in [self.search_cm_btn, self.search_analysis_btn, self.refresh_btn, self.filter_green_btn, self.export_btn]:
            search_layout.addWidget(btn)

        layout.addLayout(search_layout)

        # Charger les fichiers Excel
        self.cm_path = cm_path
        self.analysis_path = analysis_path

        self.df_cm = pd.read_excel(cm_path)
        self.df_analysis = pd.read_excel(analysis_path)

        # Modèles et vues
        self.model_cm = PandasModel(self.df_cm, colorize=True)
        self.proxy_cm = FilterProxyModel()
        self.proxy_cm.setSourceModel(self.model_cm)

        self.view_cm = QtWidgets.QTableView()
        self.view_cm.setModel(self.proxy_cm)
        self.view_cm.setMinimumHeight(300)
        self.view_cm.setStyleSheet("background-color: white;")
        self.view_cm.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.view_cm.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.view_cm.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #8A2BE2;
                color: white;
                font: bold 9pt 'Times New Roman';
                padding: 4px;
            }
            QHeaderView::section:hover {
                background-color: #A060F0;
            }
        """)

        header_cm = self.view_cm.horizontalHeader()
        header_cm.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        header_cm.customContextMenuRequested.connect(self.header_context_menu_cm)

        self.model_analysis = AnalysisModel(self.df_analysis)
        self.proxy_analysis = FilterProxyModel()
        self.proxy_analysis.setSourceModel(self.model_analysis)

        self.view_analysis = QtWidgets.QTableView()
        self.view_analysis.setModel(self.proxy_analysis)
        self.view_analysis.setMinimumHeight(300)
        self.view_analysis.setStyleSheet("background-color: white;")
        self.view_analysis.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.view_analysis.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.view_analysis.horizontalHeader().setStyleSheet(self.view_cm.horizontalHeader().styleSheet())

        header_analysis = self.view_analysis.horizontalHeader()
        header_analysis.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        header_analysis.customContextMenuRequested.connect(self.header_context_menu_analysis)

        layout.addWidget(self.view_cm)
        layout.addWidget(self.view_analysis)

        # Connexions boutons
        self.search_cm_btn.clicked.connect(self.search_cm)
        self.search_analysis_btn.clicked.connect(self.search_analysis)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.filter_green_btn.clicked.connect(self.filter_open_unique)
        self.export_btn.clicked.connect(self.export_to_excel)

        # Légende des couleurs
        legend_layout = QtWidgets.QHBoxLayout()
        legend_texts = [
            ("#2BE265", "🟢 Open & unique"),
            ("#55EDEB", "🔵 Open & doublé"),
            ("#F5DD7F", "🟡 Closed unique"),
            ("#E57B7B", "🔴 Closed doublé"),
            ("#87CEFA", "🔷 Col 5 rempli (Analysis)"),
            ("#90EE90", "🟩 Col 8 rempli"),
            ("#FFFF99", "🟨 Col 11 rempli"),
            ("#DA70D6", "🟣 Col 12 rempli"),
        ]
        for color, label in legend_texts:
            box = QtWidgets.QLabel()
            box.setFixedSize(15, 15)
            box.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            text = QtWidgets.QLabel(label)
            text.setStyleSheet("color: white; font-weight: bold;")
            legend_layout.addWidget(box)
            legend_layout.addWidget(text)
        layout.addLayout(legend_layout)

    def header_context_menu_cm(self, pos):
        header = self.view_cm.horizontalHeader()
        col = header.logicalIndexAt(pos)
        menu = QtWidgets.QMenu()
        action_filter = menu.addAction("Filtrer par cette colonne")
        action_clear = menu.addAction("Effacer tous les filtres")
        action = menu.exec_(self.view_cm.mapToGlobal(pos))
        if action == action_filter:
            text, ok = QtWidgets.QInputDialog.getText(self, "Filtrer", f"Texte à filtrer (col {col}):")
            if ok:
                self.proxy_cm.setFilterForColumn(col, text)
        elif action == action_clear:
            self.proxy_cm.column_filters.clear()
            self.proxy_cm.invalidateFilter()

    def header_context_menu_analysis(self, pos):
        header = self.view_analysis.horizontalHeader()
        col = header.logicalIndexAt(pos)
        menu = QtWidgets.QMenu()
        action_filter = menu.addAction("Filtrer par cette colonne")
        action_clear = menu.addAction("Effacer tous les filtres")
        action = menu.exec_(self.view_analysis.mapToGlobal(pos))
        if action == action_filter:
            text, ok = QtWidgets.QInputDialog.getText(self, "Filtrer", f"Texte à filtrer (col {col}):")
            if ok:
                self.proxy_analysis.setFilterForColumn(col, text)
        elif action == action_clear:
            self.proxy_analysis.column_filters.clear()
            self.proxy_analysis.invalidateFilter()

    def search_cm(self):
        for i, field in enumerate(self.search_fields):
            self.proxy_cm.setFilterForColumn(i, field.text())

    def search_analysis(self):
        for i, field in enumerate(self.search_fields):
            self.proxy_analysis.setFilterForColumn(i, field.text())

    def refresh_data(self):
        try:
            self.df_cm = pd.read_excel(self.cm_path)
            self.df_analysis = pd.read_excel(self.analysis_path)
            self.model_cm.set_dataframe(self.df_cm)
            self.model_analysis.set_dataframe(self.df_analysis)
            self.proxy_cm.column_filters.clear()
            self.proxy_cm.invalidateFilter()
            self.proxy_analysis.column_filters.clear()
            self.proxy_analysis.invalidateFilter()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur", f"Impossible de recharger les fichiers : {e}")

    def filter_open_unique(self):
        # Filtrer les lignes "Open" et uniques dans la colonne 0 sur CM
        id_counts = self.df_cm[self.df_cm.columns[0]].astype(str).str.strip().value_counts()
        mask = (self.df_cm.iloc[:, 8].str.lower() == "open") & (self.df_cm[self.df_cm.columns[0]].astype(str).str.strip().map(id_counts) == 1)
        filtered_df = self.df_cm[mask]
        self.model_cm.set_dataframe(filtered_df)
        self.proxy_cm.column_filters.clear()
        self.proxy_cm.invalidateFilter()

    def export_to_excel(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Exporter les données visibles", "", "Fichiers Excel (*.xlsx)")
        if filename:
            if not filename.endswith(".xlsx"):
                filename += ".xlsx"
            # Export CM
            df_export_cm = self.get_filtered_df(self.proxy_cm)
            # Export Analysis
            df_export_analysis = self.get_filtered_df(self.proxy_analysis)
            try:
                with pd.ExcelWriter(filename) as writer:
                    df_export_cm.to_excel(writer, sheet_name="CM", index=False)
                    df_export_analysis.to_excel(writer, sheet_name="Analysis", index=False)
                QtWidgets.QMessageBox.information(self, "Export", f"Export réussi vers {filename}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export : {e}")

    def get_filtered_df(self, proxy_model):
        source_model = proxy_model.sourceModel()
        rows = proxy_model.rowCount()
        cols = proxy_model.columnCount()
        data = []
        for row in range(rows):
            row_data = []
            for col in range(cols):
                index = proxy_model.index(row, col)
                row_data.append(proxy_model.data(index, QtCore.Qt.DisplayRole))
            data.append(row_data)
        return pd.DataFrame(data, columns=[source_model._df.columns[i] for i in range(cols)])

class FileSelectionDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sélection des fichiers Excel")
        self.setFixedSize(550, 170)

        layout = QtWidgets.QVBoxLayout(self)

        self.cm_path_edit = QtWidgets.QLineEdit()
        self.analysis_path_edit = QtWidgets.QLineEdit()

        btn_select_cm = QtWidgets.QPushButton("Sélectionner CM.xlsx")
        btn_select_analysis = QtWidgets.QPushButton("Sélectionner analysis.xlsx")

        btn_ok = QtWidgets.QPushButton("Valider")
        btn_cancel = QtWidgets.QPushButton("Annuler")

        layout_cm = QtWidgets.QHBoxLayout()
        layout_cm.addWidget(self.cm_path_edit)
        layout_cm.addWidget(btn_select_cm)

        layout_analysis = QtWidgets.QHBoxLayout()
        layout_analysis.addWidget(self.analysis_path_edit)
        layout_analysis.addWidget(btn_select_analysis)

        layout_btns = QtWidgets.QHBoxLayout()
        layout_btns.addWidget(btn_ok)
        layout_btns.addWidget(btn_cancel)

        layout.addLayout(layout_cm)
        layout.addLayout(layout_analysis)
        layout.addLayout(layout_btns)

        btn_select_cm.clicked.connect(self.select_cm)
        btn_select_analysis.clicked.connect(self.select_analysis)
        btn_ok.clicked.connect(self.validate)
        btn_cancel.clicked.connect(self.reject)

    def select_cm(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Sélectionner CM.xlsx", "", "Fichiers Excel (*.xlsx)")
        if path:
            self.cm_path_edit.setText(path)

    def select_analysis(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Sélectionner analysis.xlsx", "", "Fichiers Excel (*.xlsx)")
        if path:
            self.analysis_path_edit.setText(path)

    def validate(self):
        if not self.cm_path_edit.text() or not self.analysis_path_edit.text():
            QtWidgets.QMessageBox.warning(self, "Erreur", "Veuillez sélectionner les deux fichiers.")
            return
        if not os.path.isfile(self.cm_path_edit.text()) or not os.path.isfile(self.analysis_path_edit.text()):
            QtWidgets.QMessageBox.warning(self, "Erreur", "Un des fichiers sélectionnés est invalide.")
            return
        self.accept()

def main():
    app = QtWidgets.QApplication(sys.argv)

    dialog = FileSelectionDialog()
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        cm_path = dialog.cm_path_edit.text()
        analysis_path = dialog.analysis_path_edit.text()
        window = ExcelViewer(cm_path, analysis_path)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
