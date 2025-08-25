
import tkinter as tk
from tkinter import messagebox

class ProductSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Ürün Seçme Yazılımı")
        self.root.geometry("600x400")

        self.questions = [
            ("Su Şartlandırmanın hangi dalında bir çözüm arıyorsunuz?",
             ["Soğutma Kapalı Devre", "Soğutma Kulesi", "Diğer Proses Soğutma"]),
            ("Sisteminizde hangi işletme sorunlarını çözmek istersiniz?",
             ["Korozyon", "Birikinti", "Bakteriyel Kirlilik", "Hepsi"]),
            ("Sisteminizde bakır, alüminyum gibi yumuşak metal var mı?",
             ["Evet", "Hayır"]),
            ("Sisteminizde bakteriyel su analizi yaptınız mı?",
             ["Evet", "Hayır"]),
            ("4. soruya cevabınız evet ise bakteri miktarı nedir?",
             [">100", ">1000", ">10000"])
        ]

        self.answers = []
        self.current_question = 0

        self.label = tk.Label(root, text=self.questions[0][0], font=("Arial", 14))
        self.label.pack(pady=20)

        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack()

        self.show_options()

    def show_options(self):
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        for option in self.questions[self.current_question][1]:
            btn = tk.Button(self.buttons_frame, text=option, width=30, height=2,
                            command=lambda opt=option: self.next_question(opt))
            btn.pack(pady=5)

    def next_question(self, answer):
        self.answers.append(answer)
        self.current_question += 1

        if self.current_question < len(self.questions):
            self.label.config(text=self.questions[self.current_question][0])
            self.show_options()
        else:
            self.show_result()

    def show_result(self):
        result = self.determine_product()
        messagebox.showinfo("Önerilen Ürün", f"Sizin için uygun ürün: {result}")
        self.root.destroy()

    def determine_product(self):
        if (self.answers[0] == "Soğutma Kulesi" and
            self.answers[1] == "Hepsi" and
            self.answers[2] == "Evet" and
            self.answers[3] == "Evet" and
            self.answers[4] == ">10000"):
            return "Gelişmiş Bakteri Kontrol Paketi"
        elif (self.answers[0] == "Soğutma Kapalı Devre" and
              self.answers[1] == "Korozyon" and
              self.answers[2] == "Hayır"):
            return "Kapalı Devre Korozyon İnhibitörü"
        elif (self.answers[0] == "Diğer Proses Soğutma" and
              self.answers[1] == "Birikinti" and
              self.answers[2] == "Evet"):
            return "Özel Formülasyonlu Antiskalant"
        else:
            return "Standart Su Şartlandırma Çözümü"

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductSelector(root)
    root.mainloop()
