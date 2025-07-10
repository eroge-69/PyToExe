import tkinter as tk

SMALL_CAPS_MAP = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'ç': 'ᴄ̧', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ',
    'g': 'ɢ', 'ğ': 'ɢ̆', 'h': 'ʜ', 'ı': 'ɪ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ',
    'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'ö': 'ᴏ̈', 'p': 'ᴘ', 'q': 'ǫ',
    'r': 'ʀ', 's': 's', 'ş': 'ş', 't': 'ᴛ', 'u': 'ᴜ', 'ü': 'ᴜ̈', 'v': 'ᴠ',
    'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
}

def convert_to_small_caps(event=None):
    input_text = input_text_box.get("1.0", "end-1c")
    output_text = ""

    i = 0
    while i < len(input_text):
        if input_text[i:i+2] in ("&a", "&b", "&c", "&d", "&e", "&f", "&k", "&l", "&m", "&n", "&o", "&r"):
            output_text += input_text[i:i+2]
            i += 2
        else:
            char = input_text[i]
            lower_char = char.lower()
            output_text += SMALL_CAPS_MAP.get(lower_char, char)
            i += 1

    output_text_box.config(state="normal")
    output_text_box.delete("1.0", tk.END)
    output_text_box.insert("1.0", output_text)
    output_text_box.config(state="disabled")

window = tk.Tk()
window.title("Küçük Font Çevirici By KuroSBey")
window.configure(bg="#242424")

app_w, app_h = 600, 340
screen_w, screen_h = window.winfo_screenwidth(), window.winfo_screenheight()
x = (screen_w / 2) - (app_w / 2)
y = (screen_h / 2) - (app_h / 2)
window.geometry(f"{app_w}x{app_h}+{int(x)}+{int(y)}")

window.minsize(app_w, app_h)
window.maxsize(app_w, app_h)

input_label = tk.Label(window, text="Metin:", font=("Consolas"), fg="white", bg="#242424")
input_label.grid(row=0, column=0, padx=10, pady=10)
input_text_box = tk.Text(window, width=53, height=5, font=("Consolas", 12), bg="#424242", fg="white", bd=0)
input_text_box.grid(row=0, column=1, padx=10, pady=10)

output_label = tk.Label(window, text="Sonuç:", font=("Consolas"), fg="white", bg="#242424")
output_label.grid(row=1, column=0, padx=10, pady=10)
output_text_box = tk.Text(window, width=53, height=5, font=("Consolas", 12), bg="#424242", fg="white", bd=0)
output_text_box.grid(row=1, column=1, padx=10, pady=10)
output_text_box.config(state="disabled")

convert_button = tk.Button(window, text="Çevir", cursor="hand2", command=convert_to_small_caps,
                           font=("Consolas", 12), padx=10, pady=10,
                           bg="#007acc", activebackground="#00367D", activeforeground="white",
                           bd=0, fg="white")
convert_button.place(x=100, y=240)

info_label = tk.Label(window, text="Kullandığınız İçin Teşekkür Ederim ❤ By KuroSBey", font=("Consolas"),
                      fg="red", bg="#242424")
info_label.place(x=5, y=300)

window.bind('<Control-c>', convert_to_small_caps)

window.mainloop()
