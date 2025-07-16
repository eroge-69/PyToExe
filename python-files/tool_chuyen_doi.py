
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)

class ChuyenDoiApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🗂️Tool tìm Tờ-thửa sau sát nhập ĐVHC trên địa bàn tỉnh Đắk Lắk")
        self.resize(600, 500)

        # Đọc file Excel
        try:
            self.df = pd.read_excel("du_lieu_chuyen_doi.xlsx")
            self.df[["Tờ cũ", "Thửa cũ", "Tờ mới", "Thửa mới"]] = self.df[["Tờ cũ", "Thửa cũ", "Tờ mới", "Thửa mới"]].astype(int)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không đọc được file Excel:\n{e}")
            exit()

        # Giao diện
        layout = QVBoxLayout()

        self.label_dv = QLabel("CHỌN ĐƠN VỊ HÀNH CHÍNH CŨ:")
        self.combo_dv = QComboBox()
        self.combo_dv.addItems(sorted(self.df["Đơn vị cũ"].dropna().unique()))

        self.input_to = QLineEdit()
        self.input_to.setPlaceholderText("Nhập số tờ cũ")

        self.input_thua = QLineEdit()
        self.input_thua.setPlaceholderText("Nhập số thửa cũ")

        self.btn = QPushButton("🔍 Chuyển đổi")
        self.btn.clicked.connect(self.chuyen_doi)

        self.ket_qua = QLabel("Kết quả sẽ hiển thị ở đây...")
        self.ket_qua.setWordWrap(True)

        self.footer = QLabel("Được tạo bởi Trần Tiến Giáp – Phòng Dữ liệu Thông tin lưu trữ")
        self.footer.setWordWrap(True)

        # Thêm vào layout
        layout.addWidget(self.label_dv)
        layout.addWidget(self.combo_dv)
        layout.addWidget(self.input_to)
        layout.addWidget(self.input_thua)
        layout.addWidget(self.btn)
        layout.addWidget(self.ket_qua)
        layout.addWidget(self.footer)
        self.setLayout(layout)

    def chuyen_doi(self):
        dv = self.combo_dv.currentText()
        to_cu = self.input_to.text().strip()
        thua_cu = self.input_thua.text().strip()

        if not (to_cu.isdigit() and thua_cu.isdigit()):
            QMessageBox.warning(self, "⚠️ Lỗi", "Số tờ và thửa phải là số.")
            return

        to_cu = int(to_cu)
        thua_cu = int(thua_cu)

        # Tìm khớp hoàn toàn
        match = self.df[
            (self.df["Đơn vị cũ"] == dv) &
            (self.df["Tờ cũ"] == to_cu) &
            (self.df["Thửa cũ"] == thua_cu)
        ]

        if not match.empty:
            row = match.iloc[0]
            result = (
                f"✅ Đơn vị mới: {row['Đơn vị mới']}\n"
                f"Tờ mới: {int(row['Tờ mới'])}\n"
                f"Thửa mới: {int(row['Thửa mới'])}"
            )
            self.ket_qua.setText(result)
            return

        # Không tìm thấy cả thửa – tìm theo đơn vị + tờ để lấy TỜ MỚI
        match_to = self.df[
            (self.df["Đơn vị cũ"] == dv) &
            (self.df["Tờ cũ"] == to_cu)
        ]

        if not match_to.empty:
            row = match_to.iloc[0]
            self.ket_qua.setText(
                f"⚠️ Không tìm thấy đúng thửa.\n"
                f"✅ Đơn vị mới: {row['Đơn vị mới']}\n"
                f"Tờ mới: {int(row['Tờ mới'])} – Thửa mới: {thua_cu} (giữ nguyên)"
            )
        else:
            # Không có dữ liệu về tờ – báo lỗi rõ ràng
            self.ket_qua.setText(
                f"❌ Không tìm thấy dữ liệu chuyển đổi cho Tờ {to_cu} trong {dv}."
            )

if __name__ == "__main__":
    app = QApplication([])
    win = ChuyenDoiApp()
    win.show()
    app.exec()
