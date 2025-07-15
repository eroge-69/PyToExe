import sys
import pandas as pd
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTableView, QVBoxLayout, QWidget, QAction, QInputDialog
)
from PyQt5.QtCore import QAbstractTableModel, Qt, QFileSystemWatcher


class DataFrameModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df

    def rowCount(self, parent=None): return self._df.shape[0]
    def columnCount(self, parent=None): return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            val = self._df.iat[index.row(), index.column()]
            if role == Qt.DisplayRole:
                return str(val)
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            value = value.strip()
            if value.startswith('='):
                try:
                    expr = value[1:].upper()
                    for r in range(self._df.shape[0]):
                        for c in range(self._df.shape[1]):
                            expr = expr.replace(f"{chr(65+c)}{r+1}", str(self._df.iat[r, c]))
                    result = eval(expr)
                    self._df.iat[index.row(), index.column()] = result
                except Exception:
                    self._df.iat[index.row(), index.column()] = "ERR"
            else:
                self._df.iat[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return chr(65 + section)
            else:
                return str(section + 1)
        return None

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setDataFrame(self, df):
        self.beginResetModel()
        self._df = df
        self.endResetModel()

    def getDataFrame(self):
        return self._df


class ExcelClone(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Clone")
        self.resize(800, 600)

        self.current_csv_path = None
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.reload_csv)

        self.table = QTableView()
        self.model = DataFrameModel(pd.DataFrame([[""] * 10 for _ in range(20)]))
        self.table.setModel(self.model)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        open_action = QAction("Open CSV", self)
        open_action.triggered.connect(self.open_csv)
        save_action = QAction("Save CSV", self)
        save_action.triggered.connect(self.save_csv)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        db_menu = menubar.addMenu("Database")
        load_db_action = QAction("Load from DB", self)
        load_db_action.triggered.connect(self.load_from_db)
        db_menu.addAction(load_db_action)
        save_db_action = QAction("Save to DB", self)
        save_db_action.triggered.connect(self.save_to_db)
        db_menu.addAction(save_db_action)

    def open_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if path:
            df = pd.read_csv(path)
            self.model.setDataFrame(df)
            # Watch for external changes
            if self.current_csv_path:
                self.watcher.removePath(self.current_csv_path)
            self.current_csv_path = path
            self.watcher.addPath(path)

    def save_csv(self):
        if self.current_csv_path:
            # overwrite existing file
            self.model.getDataFrame().to_csv(self.current_csv_path, index=False)
        else:
            path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
            if not path:
                return
            self.current_csv_path = path
            self.watcher.addPath(path)
            self.model.getDataFrame().to_csv(path, index=False)

    def reload_csv(self, path):
        # Called when the watched CSV file changes externally
        if path == self.current_csv_path:
            try:
                df = pd.read_csv(path)
                self.model.setDataFrame(df)
            except Exception as e:
                print(f"Error reloading CSV: {e}")

    def load_from_db(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Database", "", "SQLite DB (*.db *.sqlite)")
        if path:
            conn = sqlite3.connect(path)
            table_name, ok = QInputDialog.getText(self, "Table Name", "Enter table name to load:")
            if ok and table_name:
                try:
                    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                    self.model.setDataFrame(df)
                except Exception as e:
                    print(f"Error loading from DB: {e}")
            conn.close()

    def save_to_db(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save to Database", "", "SQLite DB (*.db *.sqlite)")
        if path:
            conn = sqlite3.connect(path)
            table_name, ok = QInputDialog.getText(self, "Table Name", "Enter table name to save:")
            if ok and table_name:
                try:
                    self.model.getDataFrame().to_sql(table_name, conn, if_exists='replace', index=False)
                except Exception as e:
                    print(f"Error saving to DB: {e}")
            conn.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExcelClone()
    window.show()
    sys.exit(app.exec_())
