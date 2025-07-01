import customtkinter as ctk
from tkinter import messagebox

# === COLOR CONFIGURATION ===
ACCENT_COLOR = "#FFD700"   # Rockstar-style gold
BG_COLOR = "#0A0A0A"        # Deep black
CARD_COLOR = "#1A1A1A"      # Slightly lighter card background

# === SETUP ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark")

app = ctk.CTk()
app.title("🎮 GameVerse Launcher")
app.state("zoomed")

# === FRAMES ===
login_frame = ctk.CTkFrame(app, fg_color=BG_COLOR)
dashboard_frame = ctk.CTkScrollableFrame(app, fg_color=BG_COLOR, width=1500, height=800)

# === VALID CODES ===
valid_codes = ["FN-1122-3344", "MC-3344-XXYY", "VP-XYZ1-7890"]

# === STARTUP LOGIN SCREEN ===
def show_login():
    dashboard_frame.pack_forget()
    login_frame.pack(pady=80)

    ctk.CTkLabel(login_frame, text="🎮 GameVerse Activation",
                 font=ctk.CTkFont(size=36, weight="bold"),
                 text_color=ACCENT_COLOR).pack(pady=30)

    ctk.CTkLabel(login_frame, text="Enter your activation code",
                 font=ctk.CTkFont(size=18),
                 text_color="white").pack(pady=10)

    code_entry = ctk.CTkEntry(login_frame, width=400, height=45,
                              font=ctk.CTkFont(size=20),
                              placeholder_text="e.g. FN-1234-ABCD",
                              text_color="white")
    code_entry.pack(pady=20)

    def validate_code():
        code = code_entry.get().strip()
        if code in valid_codes:
            show_dashboard()
        else:
            messagebox.showerror("❌ Invalid", "The activation code is incorrect.")

    ctk.CTkButton(login_frame, text="Activate",
                  font=ctk.CTkFont(size=16, weight="bold"),
                  fg_color=ACCENT_COLOR, hover_color="#FFC700", text_color="black",
                  command=validate_code).pack(pady=20)

    ctk.CTkLabel(login_frame, text="© 2025 GameVerse | Secure Launcher",
                 font=ctk.CTkFont(size=12), text_color="gray").pack(pady=30)

# === DASHBOARD ===
def show_dashboard():
    login_frame.pack_forget()
    dashboard_frame.pack(pady=20)

    ctk.CTkLabel(dashboard_frame, text="🛒 Game Store",
                 font=ctk.CTkFont(size=32, weight="bold"),
                 text_color=ACCENT_COLOR).pack(pady=20)

    products = {
        "Fortnite V-Bucks": {"price": "9.99", "keys": ["FN-5566-7788"]},
        "Minecraft Java": {"price": "26.99", "keys": ["MC-7788-WWQQ"]},
        "Valorant Points": {"price": "13.99", "keys": ["VP-ABC2-1234"]},
        "GTA V Premium": {"price": "19.49", "keys": ["GT-REAL-KEY2"]}
    }

    for name, info in products.items():
        card = ctk.CTkFrame(dashboard_frame, width=1100, height=120,
                            fg_color=CARD_COLOR, corner_radius=10)
        card.pack(pady=12)

        ctk.CTkLabel(card, text=name,
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=ACCENT_COLOR).place(x=30, y=25)

        ctk.CTkLabel(card, text=f"Price: ${info['price']}",
                     font=ctk.CTkFont(size=18),
                     text_color="white").place(x=500, y=28)

        def purchase(product=name):
            if products[product]["keys"]:
                key = products[product]["keys"].pop(0)
                messagebox.showinfo("✅ Purchase Successful",
                                    f"{product}\n💵 ${products[product]['price']}\n🔑 Code: {key}")
            else:
                messagebox.showerror("❌ Out of Stock", f"No keys available for {product}.")

        ctk.CTkButton(card, text="Buy Now", width=140, height=40,
                      font=ctk.CTkFont(size=16, weight="bold"),
                      fg_color=ACCENT_COLOR, hover_color="#FFC700", text_color="black",
                      command=purchase).place(x=800, y=35)

# === SAFETY WRAP FOR DEBUGGING ===
try:
    show_login()
    app.mainloop()
except Exception as e:
    print("Error:", e)
    input("Press Enter to close...")