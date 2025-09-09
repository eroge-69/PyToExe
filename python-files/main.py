# receipt_app.py
import os
import tempfile
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm as mm_unit
from reportlab.lib.pagesizes import landscape

# ---------- Helper functions ----------
def mm_to_points(mm_val):
    return mm_val * mm_unit

# ---------- PDF generator ----------
def generate_receipt_pdf(filename, store_info, customer_info, items, vat_percent=0):
    # Receipt width: 80 mm (common thermal width). Height is dynamic based on number of lines.
    width_mm = 80
    lines = max(10, len(items) + 10)  # baseline lines
    line_height_mm = 6  # each line height approx
    header_height_mm = 30
    footer_height_mm = 30
    height_mm = header_height_mm + footer_height_mm + len(items) * line_height_mm
    width_pts = mm_to_points(width_mm)
    height_pts = mm_to_points(height_mm)

    c = canvas.Canvas(filename, pagesize=(width_pts, height_pts))

    x_margin = mm_to_points(4)
    y = height_pts - mm_to_points(6)

    # Header (store info)
    c.setFont("Helvetica-Bold", 9)
    if store_info.get("name"):
        c.drawCentredString(width_pts/2, y, store_info.get("name"))
        y -= mm_to_points(4)
    c.setFont("Helvetica", 7)
    if store_info.get("warehouse"):
        c.drawString(x_margin, y, f"Warehouse/Store: {store_info.get('warehouse')}")
        y -= mm_to_points(3)
    if store_info.get("sales_person"):
        c.drawString(x_margin, y, f"Sales person: {store_info.get('sales_person')}")
        y -= mm_to_points(3)
    # date and phone on same line
    nowstr = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    c.drawString(x_margin, y, f"Phone: {store_info.get('phone','')}")
    c.drawRightString(width_pts - x_margin, y, f"Date: {nowstr}")
    y -= mm_to_points(4)

    # Order code / items count
    items_count = sum([it['qty'] for it in items])
    c.drawString(x_margin, y, f"Items count: {items_count}")
    c.drawRightString(width_pts - x_margin, y, f"Order code: {store_info.get('order_code','')}")
    y -= mm_to_points(5)

    # Customer info
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_margin, y, f"Customer: {customer_info.get('name','')}")
    y -= mm_to_points(3)
    c.setFont("Helvetica", 7)
    if customer_info.get('address'):
        c.drawString(x_margin, y, f"Address: {customer_info.get('address')}")
        y -= mm_to_points(3)
    if customer_info.get('phone'):
        c.drawString(x_margin, y, f"Phone: {customer_info.get('phone')}")
        y -= mm_to_points(4)

    # Table header
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x_margin, y, "Description")
    c.drawRightString(width_pts - x_margin - mm_to_points(2+10), y, "Code")
    c.drawRightString(width_pts - x_margin - mm_to_points(2), y, "Qty")
    c.drawRightString(width_pts - x_margin - mm_to_points(20), y, "Price")
    c.drawRightString(width_pts - x_margin, y, "Total")
    y -= mm_to_points(4)

    c.setFont("Helvetica", 7)
    line_pad = mm_to_points(4)
    total_sum = 0
    for it in items:
        desc = it['desc']
        code = it['code']
        qty = it['qty']
        price = it['price']
        line_total = qty * price
        total_sum += line_total

        # Description (wrap if too long)
        c.drawString(x_margin, y, desc[:30])
        c.drawRightString(width_pts - x_margin - mm_to_points(2+10), y, str(code))
        c.drawRightString(width_pts - x_margin - mm_to_points(2), y, f"{qty}")
        c.drawRightString(width_pts - x_margin - mm_to_points(20), y, f"{price:,.0f}")
        c.drawRightString(width_pts - x_margin, y, f"{line_total:,.0f}")
        y -= mm_to_points(4)

    # Totals
    y -= mm_to_points(2)
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(width_pts - x_margin, y, f"Subtotal: {total_sum:,.0f}")
    y -= mm_to_points(4)
    vat_amount = total_sum * (vat_percent/100.0)
    c.setFont("Helvetica", 8)
    c.drawRightString(width_pts - x_margin, y, f"VAT ({vat_percent}%): {vat_amount:,.0f}")
    y -= mm_to_points(4)
    net = total_sum + vat_amount
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(width_pts - x_margin, y, f"Amount due: {net:,.0f}")
    y -= mm_to_points(6)

    # Footer
    c.setFont("Helvetica", 7)
    c.drawCentredString(width_pts/2, y, store_info.get('footer_note','Thank you'))
    # finish
    c.showPage()
    c.save()

# ---------- GUI ----------
class ReceiptApp:
    def __init__(self, master):
        self.master = master
        master.title("Simple Receipt Printer")
        master.geometry("800x600")

        # store info (editable)
        self.store_info = {
            "name": "Sales order",
            "warehouse": "المؤسسة العامة",
            "sales_person": "اسم البائع",
            "phone": "23961143",
            "order_code": "SO-#83",
            "footer_note": ""
        }

        self.items = []

        # Top frame: store and customer
        top = tk.Frame(master)
        top.pack(fill="x", padx=8, pady=6)

        # Store editable fields
        store_frame = tk.LabelFrame(top, text="Store info (editable)")
        store_frame.pack(side="left", padx=6)
        tk.Label(store_frame, text="Name").grid(row=0,column=0)
        self.ent_store_name = tk.Entry(store_frame, width=30)
        self.ent_store_name.insert(0, self.store_info["name"])
        self.ent_store_name.grid(row=0,column=1)
        tk.Label(store_frame, text="Phone").grid(row=1,column=0)
        self.ent_store_phone = tk.Entry(store_frame, width=30)
        self.ent_store_phone.insert(0, self.store_info["phone"])
        self.ent_store_phone.grid(row=1,column=1)
        tk.Label(store_frame, text="Order code").grid(row=2,column=0)
        self.ent_order_code = tk.Entry(store_frame, width=30)
        self.ent_order_code.insert(0, self.store_info["order_code"])
        self.ent_order_code.grid(row=2,column=1)

        # Customer frame
        cust_frame = tk.LabelFrame(top, text="Customer")
        cust_frame.pack(side="left", padx=6)
        tk.Label(cust_frame, text="Name").grid(row=0,column=0)
        self.ent_cust_name = tk.Entry(cust_frame, width=30)
        self.ent_cust_name.grid(row=0,column=1)
        tk.Label(cust_frame, text="Phone").grid(row=1,column=0)
        self.ent_cust_phone = tk.Entry(cust_frame, width=30)
        self.ent_cust_phone.grid(row=1,column=1)
        tk.Label(cust_frame, text="Address").grid(row=2,column=0)
        self.ent_cust_addr = tk.Entry(cust_frame, width=30)
        self.ent_cust_addr.grid(row=2,column=1)

        # Items table
        tbl_frame = tk.LabelFrame(master, text="Items")
        tbl_frame.pack(fill="both", expand=True, padx=8, pady=6)
        cols = ("desc","code","qty","price","total")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings")
        self.tree.heading("desc", text="Description")
        self.tree.heading("code", text="Code")
        self.tree.heading("qty", text="Qty")
        self.tree.heading("price", text="Price")
        self.tree.heading("total", text="Line total")
        self.tree.pack(fill="both", expand=True, side="left")
        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side="left", fill="y")

        # Buttons for items
        btns = tk.Frame(master)
        btns.pack(fill="x", padx=8, pady=6)
        tk.Button(btns, text="Add item", command=self.add_item_dialog).pack(side="left", padx=4)
        tk.Button(btns, text="Remove selected", command=self.remove_selected).pack(side="left", padx=4)
        tk.Button(btns, text="Clear all", command=self.clear_all).pack(side="left", padx=4)

        # Bottom: totals and print
        bottom = tk.Frame(master)
        bottom.pack(fill="x", padx=8, pady=6)
        tk.Label(bottom, text="VAT %").pack(side="left")
        self.vat_var = tk.DoubleVar(value=0.0)
        tk.Entry(bottom, textvariable=self.vat_var, width=6).pack(side="left", padx=4)
        tk.Button(bottom, text="Generate PDF", command=self.generate_pdf).pack(side="right", padx=4)
        tk.Button(bottom, text="Generate and Print", command=self.generate_and_print).pack(side="right", padx=4)

    def add_item_dialog(self):
        d = simpledialog.Dialog(self.master, title="Add item")
        # We'll make a tiny custom dialog instead
        dialog = tk.Toplevel(self.master)
        dialog.title("Add item")
        tk.Label(dialog, text="Description").grid(row=0,column=0)
        e_desc = tk.Entry(dialog, width=30); e_desc.grid(row=0,column=1)
        tk.Label(dialog, text="Code").grid(row=1,column=0)
        e_code = tk.Entry(dialog, width=20); e_code.grid(row=1,column=1)
        tk.Label(dialog, text="Qty").grid(row=2,column=0)
        e_qty = tk.Entry(dialog, width=10); e_qty.insert(0,"1"); e_qty.grid(row=2,column=1)
        tk.Label(dialog, text="Price").grid(row=3,column=0)
        e_price = tk.Entry(dialog, width=15); e_price.insert(0,"0"); e_price.grid(row=3,column=1)

        def on_ok():
            try:
                desc = e_desc.get()
                code = e_code.get()
                qty = float(e_qty.get())
                price = float(e_price.get())
            except Exception as ex:
                messagebox.showerror("Error", "Invalid quantity or price")
                return
            line_total = qty * price
            item = {'desc': desc, 'code': code, 'qty': qty, 'price': price}
            self.items.append(item)
            self.tree.insert("", "end", values=(desc, code, qty, f"{price:,.0f}", f"{line_total:,.0f}"))
            dialog.destroy()

        tk.Button(dialog, text="OK", command=on_ok).grid(row=4,column=0)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=4,column=1)
        dialog.transient(self.master)
        dialog.grab_set()
        self.master.wait_window(dialog)

    def remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        idxs = [self.tree.index(s) for s in sel]
        for s in sel:
            self.tree.delete(s)
        # remove from items list by indices (reverse order)
        for i in sorted(idxs, reverse=True):
            if i < len(self.items):
                del self.items[i]

    def clear_all(self):
        self.tree.delete(*self.tree.get_children())
        self.items = []

    def generate_pdf(self):
        # collect store info
        self.store_info['name'] = self.ent_store_name.get()
        self.store_info['phone'] = self.ent_store_phone.get()
        self.store_info['order_code'] = self.ent_order_code.get()
        customer_info = {
            'name': self.ent_cust_name.get(),
            'phone': self.ent_cust_phone.get(),
            'address': self.ent_cust_addr.get()
        }
        if not self.items:
            messagebox.showwarning("No items", "Add items before generating receipt.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")], title="Save receipt as")
        if not path:
            return
        try:
            generate_receipt_pdf(path, self.store_info, customer_info, self.items, vat_percent=self.vat_var.get())
            messagebox.showinfo("Done", f"PDF generated: {path}")
            return path
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None

    def generate_and_print(self):
        # generate in temp then print
        self.store_info['name'] = self.ent_store_name.get()
        self.store_info['phone'] = self.ent_store_phone.get()
        self.store_info['order_code'] = self.ent_order_code.get()
        customer_info = {
            'name': self.ent_cust_name.get(),
            'phone': self.ent_cust_phone.get(),
            'address': self.ent_cust_addr.get()
        }
        if not self.items:
            messagebox.showwarning("No items", "Add items before generating receipt.")
            return
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.close()
        try:
            generate_receipt_pdf(tmp.name, self.store_info, customer_info, self.items, vat_percent=self.vat_var.get())
        except Exception as e:
            messagebox.showerror("Error generating PDF", str(e))
            return
        # Try to print using default program on Windows
        try:
            if os.name == 'nt':
                # This sends the file to default printer (uses registered application for .pdf)
                os.startfile(tmp.name, "print")
                messagebox.showinfo("Printed", "تم إرسال الفاتورة للطابعة (الافتراضية).")
            else:
                messagebox.showinfo("PDF Created", f"PDF created at: {tmp.name}")
        except Exception as e:
            messagebox.showerror("Print error", f"Could not print automatically. PDF saved at: {tmp.name}\n\nError: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReceiptApp(root)
    root.mainloop()
