import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit

class SymptomToTreatment(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symptom to Treatment")
        self.setGeometry(100, 100, 600, 400)
        self.layout = QVBoxLayout()

        self.label = QLabel("Enter Symptoms (comma-separated):")
        self.layout.addWidget(self.label)

        self.input = QLineEdit()
        self.layout.addWidget(self.input)

        self.button = QPushButton("Diagnose")
        self.button.clicked.connect(self.diagnose)
        self.layout.addWidget(self.button)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.layout.addWidget(self.result)

        self.setLayout(self.layout)

        self.df = pd.read_csv("diseases.csv")
        self.show()

    def diagnose(self):
        entered_symptoms = [s.strip().lower() for s in self.input.text().split(",") if s.strip()]
        results = []
        for _, row in self.df.iterrows():
            disease = row['Disease']
            symptoms = [s.strip().lower() for s in str(row['Symptoms']).split(",")]
            investigations = row['Investigations']
            treatment = row['Treatment']
            matches = sum(1 for s in entered_symptoms if s in symptoms)
            probability = round((matches / len(symptoms)) * 100) if symptoms else 0
            if probability > 0:
                results.append((probability, disease, investigations, treatment))

        results.sort(reverse=True)
        display_text = ""
        for prob, disease, inv, treat in results:
            display_text += f"🩺 {disease} – {prob}% match\n"
            display_text += f"🔬 Investigations:\n"
            for i in str(inv).split(","):
                display_text += f"   • {i.strip()}\n"
            display_text += f"💊 Treatment:\n"
            for t in str(treat).split(","):
                display_text += f"   • {t.strip()}\n"
            display_text += "\n"

        self.result.setText(display_text or "No matching diseases found.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SymptomToTreatment()
    sys.exit(app.exec_())
