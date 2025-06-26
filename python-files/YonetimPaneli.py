import sys
import os
import json
import glob
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTableView,
                             QHBoxLayout, QPushButton, QFileDialog, QDateEdit, QComboBox, QSplitter,
                             QSizePolicy, QTextEdit, QCheckBox,QHeaderView, QLineEdit, QFormLayout, QDesktopWidget,QMessageBox)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QDate, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Giriş")
        self.setFixedSize(300, 100)

        layout = QFormLayout()

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        layout.addRow("Kullanıcı Adı:", self.username_edit)
        layout.addRow("Şifre:", self.password_edit)

        self.btn_login = QPushButton("Giriş")
        self.btn_login.clicked.connect(self.check_credentials)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.btn_login)
        self.setLayout(main_layout)

        self.login_successful = False

    def check_credentials(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        if username == "admin" and password == "medicana":
            self.login_successful = True
            self.close()
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış!")

class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Raporlama Paneli")

        # Tam ekran aç
        self.setGeometry(QDesktopWidget().availableGeometry())
        self.showMaximized()

        self.model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(-1)  # Tüm sütunlarda filtreleme yapabilsin

        self.splitter = QSplitter(Qt.Horizontal)

        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view.horizontalHeader().setStretchLastSection(False)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.clicked.connect(self.show_details)

        self.splitter.addWidget(self.table_view)

        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(5,5,5,5)

        self.graph_combo = QComboBox()
        self.graph_combo.addItems([
            "Günlük Hasta Sayısı",
            "Birim Bazlı Çağrı",
            "Banko Bazlı Çağrı"
        ])
        self.graph_combo.currentIndexChanged.connect(lambda: self.update_graph())
        right_layout.addWidget(QLabel("Grafikte Gösterilecek Veri:"))
        right_layout.addWidget(self.graph_combo)

        self.fig, self.ax = plt.subplots(figsize=(6,5))
        self.canvas = FigureCanvas(self.fig)
        right_layout.addWidget(self.canvas)

        self.label_avg_wait = QLabel("Ortalama Bekleme Süresi: -")
        font_bekleme = QFont()
        font_bekleme.setPointSize(20)  # Puntoyu burada ayarlarsın
        font_bekleme.setBold(True)     # (İsteğe bağlı kalın)
        self.label_avg_wait.setFont(font_bekleme)
        self.label_avg_wait.setMinimumHeight(30)
        right_layout.addWidget(self.label_avg_wait)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFixedHeight(400)
        right_layout.addWidget(QLabel("Seçilen Satır Detayları:"))
        right_layout.addWidget(self.details_text)

        right_widget.setLayout(right_layout)
        self.splitter.addWidget(right_widget)

        # Splitter genişlik ayarı:
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.setStretchFactor(0, 3)  # Tablonun alanı 3 birim
        self.splitter.setStretchFactor(1, 1) 

        self.label_status = QLabel("Toplam Hasta: 0")
        self.label_status.setMinimumHeight(20)
        self.label_status.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.date_start = QDateEdit(calendarPopup=True)
        self.date_start.setDate(QDate.currentDate())
        self.date_end = QDateEdit(calendarPopup=True)
        self.date_end.setDate(QDate.currentDate())

        self.combo_banko = QComboBox()
        self.combo_banko.setEditable(False)
        self.combo_banko.addItem("Tümü")

        self.combo_birim = QComboBox()
        self.combo_birim.setEditable(False)
        self.combo_birim.addItem("Tümü")

        self.checkbox_only_iceri = QCheckBox("Sadece İçeriye Çağrılanlar")

        self.btn_filter = QPushButton("Sorgula")
        self.btn_filter.clicked.connect(self.filter_data)

        self.btn_export = QPushButton("Excel'e Aktar")
        self.btn_export.clicked.connect(self.export_excel)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Başlangıç Tarihi:"))
        top_layout.addWidget(self.date_start)
        top_layout.addWidget(QLabel("Bitiş Tarihi:"))
        top_layout.addWidget(self.date_end)
        top_layout.addWidget(QLabel("Banko:"))
        top_layout.addWidget(self.combo_banko)
        top_layout.addWidget(QLabel("Birim:"))
        top_layout.addWidget(self.combo_birim)
        top_layout.addWidget(self.checkbox_only_iceri)
        top_layout.addWidget(self.btn_filter)
        top_layout.addWidget(self.btn_export)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.splitter)
        main_layout.addWidget(self.label_status)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.load_data()

        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(300000)

    def load_data(self):
        try:
            log_files = glob.glob("logs/*.json")
            logs = []
            for file in log_files:
                with open(file, encoding="utf-8") as f:
                    logs.extend(json.load(f))
            df_logs = pd.DataFrame(logs)
            df_logs["tarih"] = pd.to_datetime(df_logs["tarih"], errors='coerce')

            with open("cagrilan_hastalar.json", encoding="utf-8") as f:
                ch = json.load(f)
            df_ch = pd.DataFrame(ch)
            df_ch["zaman"] = pd.to_datetime(df_ch["zaman"], errors='coerce')

            with open("iceriden_cagrilan.json", encoding="utf-8") as f:
                ic = json.load(f)
            df_ic = pd.DataFrame(ic)
            df_ic["zaman"] = pd.to_datetime(df_ic["zaman"], errors='coerce')

            df_logs["gun"] = df_logs["tarih"].dt.date
            df_ch["gun"] = df_ch["zaman"].dt.date
            df_ic["gun"] = df_ic["zaman"].dt.date

            merged = pd.merge(df_logs, df_ch, how="left", on=["sira", "gun"], suffixes=("", "_ch"))
            merged = pd.merge(merged, df_ic, how="left", on=["sira", "gun"], suffixes=("", "_ic"))

            merged.rename(columns={
                "tarih": "Sıra Alınan Zaman",
                "zaman": "Bankoya Çağrılma",
                "zaman_ic": "İçeri Çağrılma",
                "sira": "Sıra No",
                "ad_soyad": "Ad Soyad",
                "birim": "Birim",
                "banko": "Banko"
            }, inplace=True)

            def calculate_wait_time(row):
                start = row["Sıra Alınan Zaman"]
                end = row["İçeri Çağrılma"]
                if pd.isna(start) or pd.isna(end):
                    return "-"
                delta = end - start
                if delta.total_seconds() < 0:
                    return "-"
                seconds = int(delta.total_seconds())
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                secs = seconds % 60
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"

            merged["Bekleme Süresi"] = merged.apply(calculate_wait_time, axis=1)

            datetime_cols = ["Sıra Alınan Zaman", "Bankoya Çağrılma", "İçeri Çağrılma"]
            for col in datetime_cols:
                merged[col] = merged[col].apply(lambda x: "-" if pd.isna(x) else x.strftime("%Y-%m-%d %H:%M:%S"))

            for col in merged.select_dtypes(include=['object']).columns:
                merged[col] = merged[col].fillna("-")

            self.df = merged[[
                "Sıra No", "Ad Soyad", "Birim", "Banko",
                "Sıra Alınan Zaman", "Bankoya Çağrılma", "İçeri Çağrılma",
                "Bekleme Süresi"
            ]]

            self.model.clear()
            self.model.setHorizontalHeaderLabels(self.df.columns.tolist())
            for _, row in self.df.iterrows():
                items = [QStandardItem(str(x)) for x in row.values]
                self.model.appendRow(items)

            self.combo_banko.clear()
            self.combo_banko.addItem("Tümü")
            self.combo_banko.addItems(sorted(set(self.df["Banko"].unique()) - {"-"}))

            self.combo_birim.clear()
            self.combo_birim.addItem("Tümü")
            self.combo_birim.addItems(sorted(set(self.df["Birim"].unique()) - {"-"}))

            self.label_status.setText(f"Toplam Hasta: {len(self.df)}")

            # Sütun genişliklerini otomatik ayarla
            self.table_view.resizeColumnsToContents()

            # Özellikle "Bekleme Süresi" sütununu biraz geniş tutalım
            bekleme_index = self.df.columns.get_loc("Bekleme Süresi")
            self.table_view.setColumnWidth(bekleme_index, 120)

            self.update_graph()
            self.update_avg_wait()

        except Exception as e:
            self.label_status.setText(f"Veriler yüklenirken hata oluştu: {e}")

    def filter_data(self):
        start = self.date_start.date().toPyDate()
        end = self.date_end.date().toPyDate()

        df_filtered = self.df.copy()
        df_filtered["Sıra Alınan Zaman"] = pd.to_datetime(df_filtered["Sıra Alınan Zaman"], errors='coerce')

        mask = (df_filtered["Sıra Alınan Zaman"].dt.date >= start) & (df_filtered["Sıra Alınan Zaman"].dt.date <= end)
        df_filtered = df_filtered[mask]

        selected_banko = self.combo_banko.currentText()
        if selected_banko != "Tümü":
            df_filtered = df_filtered[df_filtered["Banko"] == selected_banko]

        selected_birim = self.combo_birim.currentText()
        if selected_birim != "Tümü":
            df_filtered = df_filtered[df_filtered["Birim"] == selected_birim]

        if self.checkbox_only_iceri.isChecked():
            df_filtered = df_filtered[df_filtered["İçeri Çağrılma"] != "-"]

        self.model.clear()
        self.model.setHorizontalHeaderLabels(df_filtered.columns.tolist())
        for _, row in df_filtered.iterrows():
            items = [QStandardItem(str(x)) for x in row.values]
            self.model.appendRow(items)

        self.label_status.setText(f"Filtrelenmiş Hasta sayısı: {len(df_filtered)}")

        self.table_view.resizeColumnsToContents()
        bekleme_index = df_filtered.columns.get_loc("Bekleme Süresi")
        self.table_view.setColumnWidth(bekleme_index, 120)

        self.update_graph(df_filtered)
        self.update_avg_wait(df_filtered)

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Excel'e Aktar", "rapor.xlsx", "Excel Files (*.xlsx)")
        if path:
            try:
                data = []
                for row in range(self.model.rowCount()):
                    row_data = []
                    for col in range(self.model.columnCount()):
                        row_data.append(self.model.item(row, col).text())
                    data.append(row_data)
                df_export = pd.DataFrame(data, columns=self.df.columns.tolist())
                df_export.to_excel(path, index=False)
                self.label_status.setText("Excel çıktısı başarıyla oluşturuldu.")
            except Exception as e:
                self.label_status.setText(f"Excel'e aktarılırken hata: {e}")

    def update_graph(self, df=None):
        if df is None:
            df = self.df.copy()

        self.ax.clear()
        selected_index = self.graph_combo.currentIndex()

        if selected_index == 0:
            # Günlük Hasta Sayısı
            df['gun'] = pd.to_datetime(df["Sıra Alınan Zaman"], errors='coerce').dt.date
            daily_counts = df.groupby('gun').size()
            bars = self.ax.bar(daily_counts.index.astype(str), daily_counts.values, color='skyblue')
            self.ax.set_title("Günlük Hasta Sayısı")
            self.ax.set_xlabel("Tarih")
            self.ax.set_ylabel("Hasta Sayısı")
            self.ax.bar_label(bars, padding=3)

        elif selected_index == 1:
            # Birim Bazlı Çağrı
            filtered = df[~df["Birim"].isin(["-", "", None, " -"]) & df["Birim"].notna()]
            counts = filtered["Birim"].value_counts()
            bars = self.ax.bar(counts.index, counts.values, color='orange')
            self.ax.set_title("Birim Bazlı Çağrı")
            self.ax.set_xlabel("Birim")
            self.ax.set_ylabel("Çağrı Sayısı")
            self.ax.bar_label(bars, padding=3)

        elif selected_index == 2:
            # Banko Bazlı Çağrı
            filtered = df[~df["Banko"].isin(["-", "", None, " -"]) & df["Banko"].notna()]
            counts = filtered["Banko"].value_counts()
            bars = self.ax.bar(counts.index, counts.values, color='green')
            self.ax.set_title("Banko Bazlı Çağrı")
            self.ax.set_xlabel("Banko")
            self.ax.set_ylabel("Çağrı Sayısı")
            self.ax.bar_label(bars, padding=3)

        self.ax.grid(axis='y')
        self.canvas.draw()



    def update_avg_wait(self, df=None):
        if df is None:
            df = self.df.copy()

        def to_seconds(t):
            if t == "-":
                return None
            parts = t.split(":")
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

        waits = df["Bekleme Süresi"].apply(to_seconds).dropna()
        if len(waits) == 0:
            self.label_avg_wait.setText("Ortalama Bekleme Süresi: -")
            return
        avg_seconds = int(waits.mean())
        h = avg_seconds // 3600
        m = (avg_seconds % 3600) // 60
        s = avg_seconds % 60
        self.label_avg_wait.setText(f"Ortalama Bekleme Süresi: {h:02d}:{m:02d}:{s:02d}")

    def show_details(self, index):
        source_index = self.proxy_model.mapToSource(index)
        row = source_index.row()
        details = []
        for col in range(self.model.columnCount()):
            header = self.model.headerData(col, Qt.Horizontal)
            value = self.model.item(row, col).text()
            details.append(f"<b>{header}:</b> {value}")
        self.details_text.setHtml("<br>".join(details))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    app.exec_()

    if login.login_successful:
        window = AdminPanel()
        window.show()
        sys.exit(app.exec_())
