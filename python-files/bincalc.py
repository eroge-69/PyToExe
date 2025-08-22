import customtkinter as ctk
from PIL import Image
import requests
from io import BytesIO
from tkinter import messagebox

class ProBinaryConverter(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIG JANELA ---
        self.title("Conversor Decimal ⇄ Binário | IFCE Umirim")
        self.geometry("450x600")
        self.resizable(False, False)

        # --- APARÊNCIA ---
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("green")

        self.primary_color = "#2FA572"
        self.font_title = ("Arial", 22, "bold")
        self.font_entry = ("Arial", 18)
        self.font_button = ("Arial", 16, "bold")
        self.font_footer = ("Arial", 11)

        # --- LAYOUT ---
        self.create_widgets()

    def create_widgets(self):
        # --- LOGO ---
        try:
            logo_url = "https://ifce.edu.br/umirim/campus_umirim/documentos-do-campus/relatorios/comunicacao/logomarcas-umirim/umirim-02.png/@@images/image.png"
            response = requests.get(logo_url)
            img = Image.open(BytesIO(response.content))

            # Redimensiona mantendo proporção
            new_width = 230
            aspect_ratio = img.height / img.width
            new_height = int(new_width * aspect_ratio)

            self.logo_image = ctk.CTkImage(light_image=img, dark_image=img, size=(new_width, new_height))
            logo_label = ctk.CTkLabel(self, image=self.logo_image, text="")
            logo_label.pack(pady=(20, 10))
        except Exception:
            logo_label = ctk.CTkLabel(self, text="IFCE Umirim", font=self.font_title, text_color=self.primary_color)
            logo_label.pack(pady=(20, 10))

        # --- FRAME PRINCIPAL ---
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # --- TÍTULO ---
        title_label = ctk.CTkLabel(main_frame, text="Conversor Decimal ⇄ Binário", font=self.font_title, text_color=self.primary_color)
        title_label.pack(pady=(20, 15))

        # --- ENTRADA DECIMAL ---
        self.decimal_entry = ctk.CTkEntry(main_frame, placeholder_text="Valor Decimal",
                                          font=self.font_entry, height=50, corner_radius=10)
        self.decimal_entry.pack(pady=10, padx=20, fill="x")

        # --- BOTÃO CONVERTER ---
        self.convert_button = ctk.CTkButton(main_frame, text="Converter", font=self.font_button,
                                            height=45, fg_color=self.primary_color, hover_color="#24885C",
                                            command=self.convert)
        self.convert_button.pack(pady=15, padx=20, fill="x")

        # --- ENTRADA BINÁRIA ---
        self.binary_entry = ctk.CTkEntry(main_frame, placeholder_text="Valor Binário",
                                         font=self.font_entry, height=50, corner_radius=10)
        self.binary_entry.pack(pady=10, padx=20, fill="x")

        # --- BOTÃO LIMPAR ---
        self.clear_button = ctk.CTkButton(main_frame, text="Limpar", font=self.font_button, height=40,
                                          fg_color="#555555", hover_color="#777777", corner_radius=8,
                                          command=self.clear)
        self.clear_button.pack(pady=(15, 20), padx=20, fill="x")

        # --- RODAPÉ ---
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", pady=10)

        footer_label = ctk.CTkLabel(footer_frame, text="Desenvolvido por Victor Manuel | IFCE Umirim",
                                    font=self.font_footer, text_color="#444444")
        footer_label.pack()

    # --- FUNÇÕES ---
    def convert(self):
        dec_val = self.decimal_entry.get()
        bin_val = self.binary_entry.get()

        if dec_val and not bin_val:
            self.to_binary()
        elif bin_val and not dec_val:
            self.to_decimal()
        else:
            messagebox.showwarning("Aviso", "Preencha apenas um dos campos para converter!")

    def to_binary(self):
        try:
            decimal_value = int(self.decimal_entry.get())
            binary_value = bin(decimal_value)[2:]
            self.binary_entry.delete(0, "end")
            self.binary_entry.insert(0, binary_value)
        except ValueError:
            messagebox.showerror("Erro", "Valor decimal inválido!")

    def to_decimal(self):
        try:
            binary_value = self.binary_entry.get()
            if not all(c in '01' for c in binary_value):
                raise ValueError
            decimal_value = int(binary_value, 2)
            self.decimal_entry.delete(0, "end")
            self.decimal_entry.insert(0, str(decimal_value))
        except ValueError:
            messagebox.showerror("Erro", "Valor binário inválido!")

    def clear(self):
        self.decimal_entry.delete(0, "end")
        self.binary_entry.delete(0, "end")


if __name__ == "__main__":
    app = ProBinaryConverter()
    app.mainloop()
