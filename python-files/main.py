import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QComboBox

class AutoCMM(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoCMM v0.1")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.label_pdf = QLabel("Teknik Resim (PDF) Yüklenmedi")
        self.btn_pdf = QPushButton("📂 Teknik Resim Yükle (PDF)")
        self.btn_pdf.clicked.connect(self.load_pdf)

        self.label_step = QLabel("Katı Model (STEP) Yüklenmedi")
        self.btn_step = QPushButton("📂 Katı Model Yükle (STEP)")
        self.btn_step.clicked.connect(self.load_step)

        self.combo_prob = QComboBox()
        self.combo_prob.addItems(["Prob Seçiniz", "Ø2 mm", "Ø5 mm", "Yıldız Prob"])

        self.btn_measure = QPushButton("▶️ ÖLÇ")
        self.btn_measure.clicked.connect(self.measure)

        layout.addWidget(self.label_pdf)
        layout.addWidget(self.btn_pdf)
        layout.addWidget(self.label_step)
        layout.addWidget(self.btn_step)
        layout.addWidget(self.combo_prob)
        layout.addWidget(self.btn_measure)

        self.setLayout(layout)

    def load_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "PDF Seç", "", "PDF Files (*.pdf)")
        if file_name:
            self.label_pdf.setText(f"PDF Yüklendi: {file_name}")

    def load_step(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "STEP Seç", "", "STEP Files (*.step *.stp)")
        if file_name:
            self.label_step.setText(f"STEP Yüklendi: {file_name}")

    def measure(self):
        with open("örnek_cikti.RTF", "w") as f:
            f.write("********** 1 **********\n")
            f.write("DIM LOC1= POSITION OF CIRCLE CIR1  UNITS=MM\n")
            f.write("AX       MEAS    NOMINAL       +TOL       -TOL      BONUS        DEV     OUTTOL\n")
            f.write("X     -28.623    -28.600                                       0.023\n")
            f.write("Y       9.125      9.100                                       0.025\n")
            f.write("DF      4.254      4.200      0.200      0.000      0.054      0.054      0.000\n")
            f.write("TP      0.068        MMC      0.200                 0.054      0.068      0.000\n")
        self.label_pdf.setText("✔ Ölçüm Tamamlandı: örnek_cikti.RTF oluşturuldu")

app = QApplication(sys.argv)
window = AutoCMM()
window.show()
sys.exit(app.exec_())
