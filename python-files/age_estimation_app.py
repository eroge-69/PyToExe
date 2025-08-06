# age_estimation_app.py
# Gereksinimler: deepface, opencv-python
# (Tkinter standart kütüphane olarak gelir)
# Kurulum: pip install deepface opencv-python
# .exe oluşturmak için: pip install pyinstaller
#                pyinstaller --onefile age_estimation_app.py

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from deepface import DeepFace

# Geçici dizin (isteğe bağlı)
IMAGE_DIR = 'downloads'
os.makedirs(IMAGE_DIR, exist_ok=True)

class AgeEstimatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yaş Tahmin Botu")
        self.root.geometry("300x150")

        self.btn = tk.Button(root, text="Resim Seç ve Tahmin Et", command=self.load_and_predict)
        self.btn.pack(pady=20)

        self.result_label = tk.Label(root, text="Tahmin edilen yaş burada görünecek.")
        self.result_label.pack(pady=10)

    def load_and_predict(self):
        # Dosya seçme penceresi
        file_path = filedialog.askopenfilename(
            title="Resim Seç",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if not file_path:
            return
        try:
            self.result_label.config(text="Tahmin ediliyor...")
            # DeepFace ile yaş analizi
            result = DeepFace.analyze(img_path=file_path, actions=['age'])
            age = result.get('age', None)
            if age is not None:
                self.result_label.config(text=f"Tahmin edilen yaş: {age} yaş")
            else:
                self.result_label.config(text="Yaş tahmini alınamadı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Yaş tahmini sırasında hata:\n{e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = AgeEstimatorApp(root)
    root.mainloop()
