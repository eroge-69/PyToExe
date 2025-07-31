import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import pandas as pd  # برای اکسل
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from datetime import datetime

# ——————————————————————— تنظیمات ——————————————————————— #
DATA_FILE = "data.json"
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# رنگ‌ها
BG_COLOR = "#f0f2f5"
HEADER_COLOR = "#2c3e50"
BTN_COLOR = "#3498db"
BTN_HOVER = "#2980b9"
DANGER = "#e74c3c"
SUCCESS = "#2ecc71"
TEXT_COLOR = "#2c3e50"
FONT_TITLE = ("Tahoma", 14, "bold")
FONT_NORMAL = ("Tahoma", 10)
FONT_SMALL = ("Tahoma", 9)

# ——————————————————————— کلاس اصلی ——————————————————————— #
class FoodCostPro:
    def __init__(self, root):
        self.root = root
        self.root.title("🍽️ FoodCost Pro - آنالیز هزینه غذا")
        self.root.geometry("950x850")
        self.root.resizable(False, False)
        self.root.config(bg=BG_COLOR)

        # داده‌ها
        self.ingredients = {}
        self.recipes = {}
        self.categories = ["سنتی", "سوخاری", "نوشیدنی", "سالاد", "دسر", "پیتزا", "کباب"]

        self.load_data()

        # متغیرها
        self.ingredient_name = tk.StringVar()
        self.ingredient_price = tk.StringVar()
        self.recipe_name_var = tk.StringVar()
        self.extra_cost_percent = tk.StringVar(value="30")
        self.selected_category = tk.StringVar(value=self.categories[0])
        self.current_image_path = None
        self.current_photo = None

        self.setup_ui()

    def setup_ui(self):
        # ——— سربرگ ———
        header = tk.Frame(self.root, bg=HEADER_COLOR, height=60)
        header.pack(fill="x")
        tk.Label(header, text="🍽️ FoodCost Pro", font=("Tahoma", 16, "bold"),
                 bg=HEADER_COLOR, fg="white").place(relx=0.5, rely=0.5, anchor="center")

        # ——— نوتبوک (تب‌ها) ———
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=BG_COLOR)
        style.configure("TNotebook.Tab", font=FONT_NORMAL, padding=(10, 5))
        style.map("TNotebook.Tab", background=[("selected", BTN_COLOR)], foreground=[("selected", "white")])

        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=15, padx=20, fill="both", expand=True)

        # ——— تب مواد اولیه ———
        tab_ing = self.create_tab(notebook)
        tk.Label(notebook, text="مواد اولیه", compound="center").place()
        self.setup_ingredients_tab(tab_ing)

        # ——— تب آنالیز ———
        tab_analysis = self.create_tab(notebook)
        tk.Label(notebook, text="آنالیز", compound="center").place()
        self.setup_analysis_tab(tab_analysis)

    def create_tab(self, parent):
        frame = tk.Frame(parent, bg=BG_COLOR, padx=15, pady=15)
        parent.add(frame)
        return frame

    def setup_ingredients_tab(self, tab):
        tk.Label(tab, text="➕ مواد اولیه", font=FONT_TITLE, bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        tk.Label(tab, text="نام ماده:", font=FONT_NORMAL, bg=BG_COLOR).grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(tab, textvariable=self.ingredient_name, width=25, font=FONT_NORMAL, relief="solid", bd=1).grid(row=1, column=1)

        tk.Label(tab, text="قیمت به ازای کیلو (تومان):", font=FONT_NORMAL, bg=BG_COLOR).grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(tab, textvariable=self.ingredient_price, width=25, font=FONT_NORMAL, relief="solid", bd=1).grid(row=2, column=1)

        btn_frame = tk.Frame(tab, bg=BG_COLOR)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=15)

        self.create_button(btn_frame, "افزودن", self.add_ingredient, side="left", bg=BTN_COLOR)
        self.create_button(btn_frame, "ویرایش", self.edit_ingredient, side="left", bg="#f39c12", fg="white", ml=10)
        self.create_button(btn_frame, "حذف", self.remove_ingredient, side="left", bg=DANGER, fg="white", ml=10)

        tk.Label(tab, text="📋 لیست مواد اولیه", font=FONT_TITLE, bg=BG_COLOR, fg=TEXT_COLOR).grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 5))
        self.ing_listbox = tk.Listbox(tab, height=12, width=50, font=FONT_SMALL, bd=0, highlightthickness=0)
        self.ing_listbox.grid(row=5, column=0, columnspan=3, pady=5)
        self.update_ingredient_list()

    def setup_analysis_tab(self, tab):
        tk.Label(tab, text="📊 آنالیز غذاها", font=FONT_TITLE, bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        tk.Label(tab, text="دسته‌بندی:", font=FONT_NORMAL, bg=BG_COLOR).grid(row=1, column=0, sticky="w", pady=5)
        category_combo = ttk.Combobox(tab, textvariable=self.selected_category, values=self.categories, state="readonly", width=15, font=FONT_SMALL)
        category_combo.grid(row=1, column=1, padx=5)
        category_combo.bind("<<ComboboxSelected>>", lambda e: self.update_recipe_list())

        tk.Label(tab, text="نام غذا:", font=FONT_NORMAL, bg=BG_COLOR).grid(row=1, column=2, sticky="w", pady=5)
        tk.Entry(tab, textvariable=self.recipe_name_var, width=20, font=FONT_SMALL).grid(row=1, column=3)

        self.create_button(tab, "➕ غذا", self.define_recipe, row=2, col=0, col_span=4, bg=SUCCESS, fg="white", pady=10)

        tk.Label(tab, text="📋 لیست غذاها", font=FONT_TITLE, bg=BG_COLOR, fg=TEXT_COLOR).grid(row=3, column=0, columnspan=4, sticky="w", pady=(10, 5))
        self.recipe_listbox = tk.Listbox(tab, height=10, width=80, font=FONT_SMALL, bd=0, highlightthickness=0)
        self.recipe_listbox.grid(row=4, column=0, columnspan=4, pady=5)
        self.update_recipe_list()

        btn_frame = tk.Frame(tab, bg=BG_COLOR)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=15)

        self.create_button(btn_frame, "👁️ مشاهده", self.show_cost, side="left")
        self.create_button(btn_frame, "✏️ ویرایش", self.edit_recipe, side="left", ml=5)
        self.create_button(btn_frame, "🗑️ حذف", self.delete_recipe, side="left", bg=DANGER, fg="white", ml=5)
        self.create_button(btn_frame, "📄 PDF", self.export_pdf, side="left", bg="#9b59b6", fg="white", ml=5)
        self.create_button(btn_frame, "📊 اکسل", self.export_excel, side="left", bg="#27ae60", fg="white", ml=5)

        tk.Label(tab, text="📈 درصد افزایش (سود/هزینه):", font=FONT_NORMAL, bg=BG_COLOR).grid(row=6, column=0, sticky="w", pady=(10, 0))
        tk.Entry(tab, textvariable=self.extra_cost_percent, width=8, font=FONT_NORMAL).grid(row=6, column=1, sticky="w")
        tk.Label(tab, text="%", font=FONT_NORMAL, bg=BG_COLOR).grid(row=6, column=1, sticky="e", padx=60)

    def create_button(self, parent, text, command, row=None, col=None, col_span=1, side=None, bg=BTN_COLOR, fg="white", pady=5, ml=0):
        btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg, font=FONT_SMALL, relief="flat", padx=10, pady=5)
        btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOVER if bg == BTN_COLOR else bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        if row is not None:
            btn.grid(row=row, column=col, columnspan=col_span, pady=pady, padx=(ml, 0), sticky="w")
        else:
            btn.pack(side=side, padx=(ml, 5))
        return btn

    # ——— مواد اولیه ———
    def add_ingredient(self):
        name = self.ingredient_name.get().strip()
        price_str = self.ingredient_price.get().strip()
        if not name or not price_str:
            return messagebox.showwarning("⚠️", "نام و قیمت را وارد کنید.")
        try:
            price = float(price_str)
        except:
            return messagebox.showerror("❌", "قیمت باید عدد باشد.")
        if name in self.ingredients and not messagebox.askyesno("تکراری", f"'{name}' وجود دارد. جایگزین شود؟"):
            return
        self.ingredients[name] = price
        self.save_data()
        self.update_ingredient_list()
        self.ingredient_name.set("")
        self.ingredient_price.set("")

    def edit_ingredient(self):
        sel = self.ing_listbox.curselection()
        if not sel:
            return messagebox.showwarning("⚠️", "ماده‌ای را انتخاب کنید.")
        item = self.ing_listbox.get(sel[0])
        name = item.split(":")[0]
        old_price = self.ingredients[name]

        new_price_str = simpledialog.askstring("ویرایش قیمت", f"قیمت جدید برای '{name}' (تومان/کیلو):", initialvalue=str(old_price))
        if not new_price_str: return
        try:
            new_price = float(new_price_str)
        except:
            return messagebox.showerror("❌", "قیمت نامعتبر.")
        self.ingredients[name] = new_price
        self.save_data()
        self.update_ingredient_list()

    def remove_ingredient(self):
        sel = self.ing_listbox.curselection()
        if not sel: return messagebox.showwarning("⚠️", "ماده‌ای انتخاب نشده.")
        name = self.ing_listbox.get(sel[0]).split(":")[0]
        if messagebox.askyesno("حذف", f"'{name}' حذف شود؟"):
            del self.ingredients[name]
            self.save_data()
            self.update_ingredient_list()

    def update_ingredient_list(self):
        self.ing_listbox.delete(0, tk.END)
        for n, p in self.ingredients.items():
            self.ing_listbox.insert(tk.END, f"{n}: {p:,.0f} تومان/کیلو")

    # ——— آنالیز غذا ———
    def define_recipe(self):
        name = self.recipe_name_var.get().strip()
        if not name: return messagebox.showwarning("⚠️", "نام غذا؟")
        if name in self.recipes and not messagebox.askyesno("تکراری", "این نام وجود دارد. جایگزین شود؟"):
            return
        self.open_recipe_window(name, edit_mode=False)

    def edit_recipe(self):
        sel = self.recipe_listbox.curselection()
        if not sel: return messagebox.showwarning("⚠️", "غذا را انتخاب کنید.")
        name = self.recipe_listbox.get(sel[0]).split(" | ")[0]
        self.open_recipe_window(name, edit_mode=True)

    def delete_recipe(self):
        sel = self.recipe_listbox.curselection()
        if not sel: return messagebox.showwarning("⚠️", "غذا را انتخاب کنید.")
        name = self.recipe_listbox.get(sel[0]).split(" | ")[0]
        if messagebox.askyesno("حذف", f"'{name}' حذف شود؟"):
            del self.recipes[name]
            self.save_data()
            self.update_recipe_list()

    def open_recipe_window(self, name, edit_mode=False):
        data = self.recipes.get(name, {}) if edit_mode else {}
        items = data.get("items", [])
        category = data.get("category", self.categories[0])
        img_path = data.get("image", None)

        win = tk.Toplevel(self.root)
        win.title(f"✏️ {'ویرایش' if edit_mode else 'تعریف'} غذا: {name}")
        win.geometry("650x700")
        win.config(bg=BG_COLOR)

        tk.Label(win, text="📝 مواد این غذا", font=FONT_TITLE, bg=BG_COLOR).pack(pady=(10, 5))
        listbox = tk.Listbox(win, height=10, font=FONT_SMALL, width=60)
        listbox.pack(pady=5)
        for item in items:
            listbox.insert(tk.END, f"{item[0]} — {item[1]} گرم")

        frm = tk.Frame(win, bg=BG_COLOR)
        frm.pack(pady=10)
        sel_ing = tk.StringVar()
        ttk.Combobox(frm, textvariable=sel_ing, values=list(self.ingredients.keys()), state="readonly", width=20).pack(side="left", padx=5)
        amt_var = tk.StringVar()
        tk.Entry(frm, textvariable=amt_var, width=10).pack(side="left", padx=5)
        tk.Label(frm, text="گرم", bg=BG_COLOR).pack(side="left")
        self.create_button(frm, "➕ افزودن", lambda: self.add_to_listbox(listbox, sel_ing.get(), amt_var.get()), side="left", ml=5)

        btn_frm = tk.Frame(win, bg=BG_COLOR)
        btn_frm.pack(pady=5)
        self.create_button(btn_frm, "✏️ ویرایش", lambda: self.edit_list_item(listbox), side="left")
        self.create_button(btn_frm, "🗑️ حذف", lambda: listbox.delete(tk.ANCHOR), side="left", bg=DANGER, ml=5)

        tk.Label(win, text="🗂️ دسته‌بندی:", font=FONT_NORMAL, bg=BG_COLOR).pack(anchor="w", padx=20, pady=(10, 5))
        cat_var = tk.StringVar(value=category)
        ttk.Combobox(win, textvariable=cat_var, values=self.categories, state="readonly").pack(padx=20, fill="x")

        img_btn = self.create_button(win, "🖼️ انتخاب تصویر", lambda: self.select_image(win), pady=10)
        if img_path and os.path.exists(img_path):
            self.display_temp_image(win, img_path, img_btn)

        self.create_button(win, "✅ ذخیره", lambda: self.save_recipe(win, name, listbox, cat_var), bg=SUCCESS, fg="white", pady=20)

    def save_recipe(self, win, name, listbox, cat_var):
        try:
            items = []
            for item in listbox.get(0, tk.END):
                parts = item.split(" — ")
                ing = parts[0]
                amt = float(parts[1].replace(" گرم", ""))
                items.append((ing, amt))
            self.recipes[name] = {
                "items": items,
                "category": cat_var.get(),
                "image": self.current_image_path or ""
            }
            self.save_data()
            self.update_recipe_list()
            win.destroy()
        except Exception as e:
            messagebox.showerror("❌", f"خطا: {e}")

    def add_to_listbox(self, lb, name, amt):
        if not name or not amt: return messagebox.showwarning("!", "پر کن")
        try: float(amt)
        except: return messagebox.showerror("!", "عدد باشد")
        lb.insert(tk.END, f"{name} — {amt} گرم")

    def edit_list_item(self, lb):
        sel = lb.curselection()
        if not sel: return
        item = lb.get(sel[0])
        name, rest = item.split(" — ")
        old = rest.replace(" گرم", "")
        new = simpledialog.askstring("ویرایش", "مقدار جدید (گرم):", initialvalue=old)
        if new:
            try:
                float(new)
                lb.delete(sel[0])
                lb.insert(sel[0], f"{name} — {new} گرم")
            except: messagebox.showerror("!", "عدد")

    def select_image(self, parent):
        path = filedialog.askopenfilename(title="انتخاب تصویر", filetypes=[("Image", "*.jpg *.jpeg *.png *.bmp")])
        if path:
            self.current_image_path = self.copy_image_to_app(path)
            self.display_temp_image(parent, self.current_image_path)

    def copy_image_to_app(self, src):
        ext = os.path.splitext(src)[1]
        dest = os.path.join(IMAGES_DIR, f"img_{len(self.recipes) + 1}{ext}")
        import shutil
        shutil.copy(src, dest)
        return dest

    def display_temp_image(self, parent, path, button=None):
        try:
            img = Image.open(path)
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(parent, image=photo, bg=BG_COLOR)
            label.image = photo
            label.pack(pady=5)
            if button: button.config(text="🔄 تغییر تصویر")
        except: messagebox.showerror("!", "خطا در نمایش تصویر")

    def show_cost(self):
        sel = self.recipe_listbox.curselection()
        if not sel: return messagebox.showwarning("!", "انتخاب کن")
        name = self.recipe_listbox.get(sel[0]).split(" | ")[0]
        self.generate_cost_report(name)

    def generate_cost_report(self, name):
        data = self.recipes[name]
        base = sum((self.ingredients.get(ing, 0) / 1000) * amt for ing, amt in data["items"])
        try: extra_p = float(self.extra_cost_percent.get())
        except: extra_p = 30
        extra = (base * extra_p) / 100
        final = base + extra

        msg = f"🍽️ {name}\n🗂️ دسته: {data.get('category', '-')}\n\n📋 مواد:\n"
        for ing, amt in data["items"]:
            cost = (self.ingredients.get(ing, 0) / 1000) * amt
            msg += f"  • {ing}: {amt}گ → {cost:,.0f} تومان\n"
        msg += f"\n💰 پایه: {base:,.0f}\n📈 +{extra_p}%: {extra:,.0f}\n🎯 نهایی: {final:,.0f} تومان"
        messagebox.showinfo("هزینه", msg)

    def export_pdf(self):
        sel = self.recipe_listbox.curselection()
        if not sel:
            return messagebox.showwarning("⚠️", "ابتدا یک غذا را انتخاب کنید.")
        name = self.recipe_listbox.get(sel[0]).split(" | ")[0]
        pdf_path = f"{name}_گزارش.pdf"
        try:
            c = canvas.Canvas(pdf_path, pagesize=A4)
            w, h = A4
            c.setFont("Helvetica", 16)
            c.drawString(5*cm, h-3*cm, f"گزارش: {name}")
            c.setFont("Helvetica", 12)
            c.drawString(5*cm, h-4*cm, f"دسته: {self.recipes[name].get('category', '-')}")

            y = h - 5.5*cm
            for ing, amt in self.recipes[name]["items"]:
                cost = (self.ingredients.get(ing, 0) / 1000) * amt
                c.drawString(5.5*cm, y, f"• {ing} ({amt} گرم): {cost:,.0f} تومان")
                y -= 0.4*cm

            base = sum((self.ingredients.get(ing, 0) / 1000) * amt for ing, amt in self.recipes[name]["items"])
            extra_p = float(self.extra_cost_percent.get() or 30)
            extra = (base * extra_p) / 100
            final = base + extra

            c.setFillColor(colors.green)
            c.drawString(5*cm, y, f"هزینه پایه: {base:,.0f} تومان")
            y -= 0.4*cm
            c.drawString(5*cm, y, f"+ {extra_p}%: {extra:,.0f} تومان")
            y -= 0.4*cm
            c.setFillColor(colors.red)
            c.drawString(5*cm, y, f"جمع نهایی: {final:,.0f} تومان")
            c.save()
            messagebox.showinfo("✅", f"PDF با موفقیت ذخیره شد:\n{pdf_path}")
        except Exception as e:
            messagebox.showerror("❌", f"خطا در ساخت PDF:\n{e}")

    def export_excel(self):
        if not self.recipes:
            return messagebox.showwarning("⚠️", "هیچ غذایی تعریف نشده.")
        data = []
        for name, recipe in self.recipes.items():
            base = sum((self.ingredients.get(ing, 0) / 1000) * amt for ing, amt in recipe["items"])
            extra_p = float(self.extra_cost_percent.get() or 30)
            final = base + (base * extra_p) / 100
            data.append({
                "نام غذا": name,
                "دسته": recipe.get("category", "-"),
                "هزینه پایه (تومان)": f"{base:,.0f}",
                "درصد افزایش": f"{extra_p}%",
                "هزینه نهایی (تومان)": f"{final:,.0f}"
            })
        df = pd.DataFrame(data)
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            try:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("✅", f"فایل اکسل با موفقیت ذخیره شد:\n{file_path}")
            except Exception as e:
                messagebox.showerror("❌", f"خطا در ذخیره اکسل:\n{e}")

    def update_recipe_list(self):
        self.recipe_listbox.delete(0, tk.END)
        cat = self.selected_category.get()
        for name, data in self.recipes.items():
            if data.get("category") != cat: continue
            base = sum((self.ingredients.get(ing, 0) / 1000) * amt for ing, amt in data["items"])
            self.recipe_listbox.insert(tk.END, f"{name} | {base:,.0f} تومان | {data.get('category')}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.ingredients = data.get("ingredients", {})
                    self.recipes = data.get("recipes", {})
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در بارگذاری داده‌ها:\n{e}")

    def save_data(self):
        data = {"ingredients": self.ingredients, "recipes": self.recipes}
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("خطا", f"ذخیره داده با خطا مواجه شد:\n{e}")

if __name__ == "__main__":
    root = tk.Toplevel()
    app = FoodCostPro(root)
    root.mainloop()