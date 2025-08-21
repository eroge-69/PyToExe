import os
from tkinter import ttk,filedialog,messagebox
from tkinter.ttk import Button
from datetime import datetime

import mysql.connector as connector
from tkinter import *
import os
from pathlib import Path
import pandas
import openpyxl

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,A3
from reportlab.lib.colors import lightblue
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle
from reportlab.lib.units import cm
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer

class purchase:

    def __init__(self,root):
        self.con = connector.connect(host='127.0.0.1',port='3306',user='root',password='Dearmart@1233',database='mso_inven')
        self.root = root
        self.root.title("purchase")
        self.root.resizable(1,1)
        width = 1360
        height = 768
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        x = (self.width / 2) - (width / 2)
        y = (self.height / 2) - (height / 2)
        self.root.geometry('%dx%d+%d+%d' % (width,height,x,y))
        self.root.focus_force()
        self.root.grab_set()
        self.root.bind("<Return>",self.assine_style_for_purchase_ev)

        # =====Menu========
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)
        # =====Billing==========
        sales_window_menu = Menu(self.menu,tearoff=0)
        self.menu.add_cascade(label="Menu",menu=sales_window_menu)
        sales_window_menu.add_command(label="Print Purchase List",command=self.print_pdf)

        self.Pro_ID_var = StringVar()
        self.Type_var = StringVar()
        self.SKU_CODE_var = StringVar()
        self.Product_Name_inventory_var = StringVar()
        self.Product_Name_Display_var = StringVar()
        self.Supplier_var = StringVar()
        self.Group_var= StringVar()
        self.Order_qty_var=StringVar()

        #======================

        self.Po_ID_var = StringVar()
        self.Po_Number_var = StringVar()
        self.Supplier_var = StringVar()
        self.Status_var = StringVar()
        self.Product_Price_var = StringVar()
        self.Total_var = StringVar()
        self.Total_qty_var = StringVar()
        self.Trn1_var = StringVar()
        self.Trn2_var = StringVar()
        self.Avg_price_var = StringVar()

        #================
        self.Pur_ID_var = StringVar()
        #=================

        self.view_option_var=StringVar()
        self.filter_group_var=StringVar()
        self.filter_group_var.set("")
        #===============================

        self.Product_Detail = ttk.LabelFrame(self.root,text='Product Detail')
        self.Product_Data = ttk.LabelFrame(self.root,text='Product Data')
        self.Order_Detail = ttk.LabelFrame(self.root,text='Order Data')
        self.Select_Detail = ttk.LabelFrame(self.root,text='Select_Detail')
        self.Purchase_Data = ttk.LabelFrame(self.root,text='Purchase Data')

        self.Product_Detail.place(x=0,y=0,width=670,height=50)
        self.Product_Data.place(x=0,y=50,width=670,height=715)
        self.Order_Detail.place(x=760,y=0,width=599,height=50)
        self.Select_Detail.place(x=670,y=0,width=90,height=275)
        self.Purchase_Data.place(x=760,y=50,width=599,height=715)

        self.view_op_txt = ttk.Combobox(self.Product_Detail,textvariable=self.view_option_var,values=('View_Sales As','View_Sales DeAs','View_Normal'),state='readonly')
        self.view_op_txt.bind("<<ComboboxSelected>>",self.show_ev)
        self.view_op_txt.current(0)
        self.view_op_txt.place(x=0,y=5,width=120)
        self.clear_btn = ttk.Button(self.Product_Detail,text="Clr_grp",command=self.clear_group)
        self.clear_btn.place(x=120,y=4,width=60)
        self.Product_Name_inventory_txt = ttk.Entry(self.Product_Detail,textvariable=self.Product_Name_inventory_var,state='readonly')
        self.Product_Name_inventory_txt.place(x=185,y=5,width=475)

        self.Qty_text = ttk.Entry(self.root,textvariable=self.Order_qty_var)
        self.Qty_text.place(x=670,y=280,width=90,height=30)
        self.add_btn = ttk.Button(self.root,text="Add/Update",command=self.assine_style_for_purchase)
        self.add_btn.place(x=670,y=310,width=90,height=50)

        self.add_po_btn = ttk.Button(self.root,text="add po",command=self.add_po_number)
        self.add_po_btn.place(x=670,y=370,width=90,height=40)
        self.de_po_btn = ttk.Button(self.root,text="delete po",command=self.delete_po_number)
        self.de_po_btn.place(x=670,y=410,width=90,height=40)

        self.Product_Price_txt = ttk.Entry(self.root,textvariable=self.Product_Price_var)
        self.Product_Price_txt.place(x=670,y=460,width=90,height=30)
        self.Trn1_txt = ttk.Entry(self.root,textvariable=self.Trn1_var)
        self.Trn1_txt.place(x=670,y=490,width=90,height=30)
        self.Trn2_txt = ttk.Entry(self.root,textvariable=self.Trn2_var)
        self.Trn2_txt.place(x=670,y=520,width=90,height=30)
        self.Status_txt = ttk.Combobox(self.root,textvariable=self.Status_var,values=('Approve','Pending'),state='readonly')
        self.Status_txt.current(0)
        self.Status_txt.place(x=670,y=550,width=90,height=30)


        self.up_po_btn = ttk.Button(self.root,text="update po",command=self.update_po)
        self.up_po_btn.place(x=670,y=580,width=90,height=40)

        self.re_btn = ttk.Button(self.root,text="reset",command=self.eql_qty)
        # self.re_btn.place(x=780,y=580,width=90,height=40)


        #===Po Details===
        self.Supplier_lbl = ttk.Entry(self.Order_Detail,textvariable=self.Supplier_var,state='readonly',)
        self.Supplier_txt = ttk.Entry(self.Order_Detail,textvariable=self.Supplier_var,state='readonly',)
        self.Supplier_txt.place(x=0,y=5,width=100)

        self.Total_qty_txt = ttk.Entry(self.Order_Detail,textvariable=self.Total_qty_var,state='readonly')
        self.Total_qty_txt.place(x=100,y=5,width=100)

        self.Total_txt = ttk.Entry(self.Order_Detail,textvariable=self.Total_var,state='readonly')
        self.Total_txt.place(x=200,y=5,width=100)

        self.Avg_price_txt = ttk.Entry(self.Order_Detail,textvariable=self.Avg_price_var,state='readonly')
        self.Avg_price_txt.place(x=300,y=5,width=100)

        #===Product data=====
        scrolly = Scrollbar(self.Product_Data,orient=VERTICAL)
        scrollx = Scrollbar(self.Product_Data,orient=HORIZONTAL)
        self.Product_Data_Tabel = ttk.Treeview(self.Product_Data,columns=('S_No','Product_Name_inventory','Supplier','Buy_Qty','Sell_Qty','Balance_Qty','Order_Qty',
        ),yscrollcommand=scrolly.set,xscrollcommand=scrollx.set)
        scrollx.pack(side=BOTTOM,fill=X)
        scrolly.pack(side=RIGHT,fill=Y)
        scrollx.config(command=self.Product_Data_Tabel.xview)
        scrolly.config(command=self.Product_Data_Tabel.yview)

        self.Product_Data_Tabel.heading('S_No',text='S.No',)
        self.Product_Data_Tabel.heading('Product_Name_inventory',text='Product Name',)
        self.Product_Data_Tabel.heading('Supplier',text='Sup',)
        self.Product_Data_Tabel.heading('Buy_Qty',text='BQ',)
        self.Product_Data_Tabel.heading('Sell_Qty',text='SQ',)
        self.Product_Data_Tabel.heading('Balance_Qty',text='LQ',)
        self.Product_Data_Tabel.heading('Order_Qty',text='OQ',)

        self.Product_Data_Tabel.column('S_No',width=12,anchor=CENTER,)
        self.Product_Data_Tabel.column('Product_Name_inventory',width=425,anchor=W,)
        self.Product_Data_Tabel.column('Supplier',width=20,anchor=W,)
        self.Product_Data_Tabel.column('Buy_Qty',width=12,anchor=CENTER,)
        self.Product_Data_Tabel.column('Sell_Qty',width=12,anchor=CENTER,)
        self.Product_Data_Tabel.column('Balance_Qty',width=12,anchor=CENTER,)
        self.Product_Data_Tabel.column('Order_Qty',width=12,anchor=CENTER,)

        self.Product_Data_Tabel['show'] = 'headings'
        self.Product_Data_Tabel.pack(fill=BOTH,expand=1)
        self.Product_Data_Tabel.tag_configure('odd',background="#FfFfFf")
        self.Product_Data_Tabel.tag_configure('even',background="#f8f4f4")
        self.Product_Data_Tabel.bind("<ButtonRelease-1>",self.get_product)
        self.Product_Data_Tabel.bind("<Double-Button-1>",self.filter_by_group)
        self.show_products()

        #====Purchase data=====
        scrolly = Scrollbar(self.Purchase_Data,orient=VERTICAL)
        scrollx = Scrollbar(self.Purchase_Data,orient=HORIZONTAL)
        self.Purchase_Data_Tabel = ttk.Treeview(self.Purchase_Data,columns=('S_No','Product_Name_inventory','Order_Qty',
        ),yscrollcommand=scrolly.set,xscrollcommand=scrollx.set)
        scrollx.pack(side=BOTTOM,fill=X)
        scrolly.pack(side=RIGHT,fill=Y)
        scrollx.config(command=self.Purchase_Data_Tabel.xview)
        scrolly.config(command=self.Purchase_Data_Tabel.yview)
        self.Purchase_Data_Tabel.heading('S_No',text='S.No',)
        self.Purchase_Data_Tabel.heading('Product_Name_inventory',text='Product Name',)
        self.Purchase_Data_Tabel.heading('Order_Qty',text='OQ',)

        self.Purchase_Data_Tabel.column('S_No',width=12,anchor=CENTER,)
        self.Purchase_Data_Tabel.column('Product_Name_inventory',width=475,anchor=W,)
        self.Purchase_Data_Tabel.column('Order_Qty',width=12,anchor=CENTER,)
        self.Purchase_Data_Tabel['show'] = 'headings'

        self.Purchase_Data_Tabel.pack(fill=BOTH,expand=1)
        self.Purchase_Data_Tabel.tag_configure('odd',background="#FfFfFf")
        self.Purchase_Data_Tabel.tag_configure('even',background="#f8f4f4")
        self.Purchase_Data_Tabel.bind("<ButtonRelease-1>",self.get_purchase)
        # self.Purchase_Data_Tabel.bind("<Double-Button-1>",self.filter_by_group)


        #====Order Data====

        scrolly = Scrollbar(self.Select_Detail ,orient=VERTICAL)
        scrollx = Scrollbar(self.Select_Detail ,orient=HORIZONTAL)
        self.Order_Data_Tabel = ttk.Treeview(self.Select_Detail,columns=('PO',
        ),yscrollcommand=scrolly.set,xscrollcommand=scrollx.set)
        scrollx.pack(side=BOTTOM,fill=X)
        scrolly.pack(side=RIGHT,fill=Y)
        scrollx.config(command=self.Order_Data_Tabel.xview)
        scrolly.config(command=self.Order_Data_Tabel.yview)

        self.Order_Data_Tabel.heading('PO',text='PO',)
        self.Order_Data_Tabel.column('PO',width=50,anchor=W,)

        self.Order_Data_Tabel['show'] = 'headings'

        self.Order_Data_Tabel.pack(fill=BOTH,expand=1)
        self.Order_Data_Tabel.tag_configure('odd',background="#FfFfFf")
        self.Order_Data_Tabel.tag_configure('even',background="#f8f4f4")
        self.Order_Data_Tabel.bind("<ButtonRelease-1>",self.get_po_number)
        self.show_po_number()


    def po_number_generate(self):
        cur = self.con.cursor()
        cur.execute("SELECT PoNumber FROM po")
        results = cur.fetchall()

        max_number = 0

        for row in results:
            po = row[0]
            if po and po.startswith("P") and po[1:5].isdigit():
                num = int(po[1:5])
                if num > max_number:
                    max_number = num

        new_number = max_number + 1
        po_number = f"P{str(new_number).zfill(4)}"

        return po_number


    def add_po_number(self):
        po_number=self.po_number_generate()
        cur = self.con.cursor(buffered=True)
        cur.execute("INSERT INTO po(PoNumber,Supplier,Status,ProductPrice,Total,Transport1,Transport2,AvgPrice)values(%s,%s,%s,%s,%s,%s,%s,%s)",
                    (po_number,"","Pending","0","0","0","0","0",))
        self.con.commit()
        self.Order_qty_var.set("")
        self.show_po_number()

    def delete_po_number(self):
            try:
                po_number = self.Po_Number_var.get()

                if po_number == "":
                    messagebox.showerror("Error","Please select one PO",parent=self.root)
                    return

                cur = self.con.cursor(buffered=True)

                # Check if PO is already used in the purchase table
                cur.execute("SELECT * FROM purchase WHERE PoNumber = %s",(po_number,))
                existing_linked = cur.fetchall()

                if existing_linked:
                    messagebox.showerror("Error", f"{po_number} is already used in some Purchase Order,\nso you can't delete the PO!",parent=self.root)
                    return

                # Ask for confirmation before deletion
                confirm = messagebox.askyesno( "Confirm",f"Do you really want to delete selected PO ({po_number})?",parent=self.root)

                if confirm:
                    cur.execute("DELETE FROM po WHERE PoNumber = %s",(po_number,))
                    self.con.commit()
                    self.show_products()
                    messagebox.showinfo("Deleted",f"PO ({po_number}) deleted successfully",parent=self.root)

                # Reset UI fields
                self.Supplier_var.set("")
                self.Order_qty_var.set("")
                self.show_po_number()
                self.clear_po_dta()

            except Exception as ex:
                messagebox.showerror("Error",f"Error due to: {str(ex)}",parent=self.root)

    def clear_po_dta(self):
        self.Product_Price_var.set("")
        self.Total_var.set("")
        self.Total_qty_var.set("")
        self.Trn1_var.set("")
        self.Trn2_var.set("")
        self.Avg_price_var.set("")
        self.Order_qty_var.set("")

    def update_po(self):
            try:
                po_number = self.Po_Number_var.get()
                product_price = self.Product_Price_var.get()
                trn1 = self.Trn1_var.get()
                trn2 = self.Trn2_var.get()
                status = self.Status_var.get()
                if not po_number:
                    messagebox.showerror("Error","Please select one PO",parent=self.root)
                    return
                if product_price in ("","0"):
                    messagebox.showerror("Error","Please add Product Price",parent=self.root)
                    return
                if status == "Approve":
                    if trn1 in ("","0"):
                        messagebox.showerror("Error","Please add Transport - 1",parent=self.root)
                        return
                    if trn2 in ("","0"):
                        messagebox.showerror("Error","Please add Transport - 2",parent=self.root)
                        self.Trn2_txt.focus()
                        return
                # === Perform PO Calculations ===
                self.po_calculations(po_number)
                # === Fetch Existing Status ===
                cur = self.con.cursor(buffered=True)
                cur.execute("SELECT Status FROM po WHERE PoNumber = %s",(po_number,))
                result = cur.fetchone()
                ex_sts = result[0] if result else ""

                # === Update PO ===
                cur.execute("UPDATE po SET Status=%s,ProductPrice=%s,Total=%s,Transport1=%s,Transport2=%s,AvgPrice=%s WHERE PoNumber=%s",
                            ( status,product_price,self.Total_var.get(),trn1,trn2,self.Avg_price_var.get(),po_number))
                self.con.commit()

                # === Post-Update Actions ===
                self.approve_po(po_number,ex_sts,status)
                self.show_purchase()
                self.view_rows_in_purchase_list(po_number,self.Product_Name_inventory_var.get())
                messagebox.showinfo("Updated",f"PO updated successfully",parent=self.root)
            except Exception as ex:
                messagebox.showerror("Error",f"Error due to: {str(ex)}",parent=self.root)

    def po_calculations(self,po):
        try:
            # Parse numeric inputs safely
            price = float(self.Product_Price_var.get() or 0)
            transport_1 = float(self.Trn1_var.get() or 0)
            transport_2 = float(self.Trn2_var.get() or 0)

            # Get total quantity from the database
            cur = self.con.cursor(buffered=True)
            cur.execute("SELECT SUM(BuyQty) FROM purchase WHERE PoNumber = %s",(po,))
            total_qty_result = cur.fetchone()
            total_quantity = int(total_qty_result[0]) if total_qty_result and total_qty_result[0] else 0

            # Calculate total and average prices
            if price > 0 and total_quantity > 0:
                total_price = (price * total_quantity) + transport_1 + transport_2
                avg_price = total_price / total_quantity

                # Set values in UI
                self.Total_qty_var.set(total_quantity)
                self.Total_var.set(round(total_price))
                self.Avg_price_var.set(round(avg_price))
            else:
                # Reset if data is incomplete
                self.Total_qty_var.set("")
                self.Total_var.set("")
                self.Avg_price_var.set("")

            # Update product display
            self.show_products()

        except Exception as ex:
            messagebox.showerror("Error",f"Calculation error: {str(ex)}",parent=self.root)

    def approve_po(self,po,ex_sts,new_sts):
        if ex_sts==new_sts:
            pass
        else:
            cur = self.con.cursor(buffered=True)
            cur.execute("SELECT PurId,SkuCode,BuyQty FROM purchase where PoNumber=%s",(self.Po_Number_var.get(),))
            pur_ids = cur.fetchall()
            if len(pur_ids) == 0:
                pass
            else:
                for x in pur_ids:
                    cur.execute("UPDATE purchase SET AvgPrice=%s,Status=%s WHERE PurId=%s",
                                (self.Avg_price_var.get(),new_sts,x[0],))
                self.con.commit()
                for y in pur_ids:
                        self.assine_update_quantity_in_Products(po,y[1],y[2],new_sts)
            self.show_purchase()
            if self.Status_var.get()=="Approve":
                self.add_btn["state"] = "disabled"
                self.Qty_text["state"] = "disabled"
            else:
                self.add_btn["state"] = "enable"
                self.Qty_text["state"] = "enable"

    def assine_update_quantity_in_Products(self,po,sku,add_qty,new_sts):

        Po_Number=po
        Need_Change_Quantity=int(0)
        Sku_Code = sku
        Status_Type = new_sts
        #---------------------
        if Status_Type=="Approve":
            Need_Change_Quantity=int(add_qty)
        elif Status_Type=="Pending":
            Need_Change_Quantity = -int(add_qty)
        self.update_quantity_in_Products(Sku_Code,Need_Change_Quantity)
        self.show_products()

    def update_quantity_in_Products(self,sku,qty):
        Sku_Code=sku
        Change_Qty=int(qty)
        Existing_Buy_Qty=int(0)
        Existing_Sell_Qty=int(0)
        Final_Buying_Qty=int(0)
        Balance_Qty=int(0)
        cur = self.con.cursor(buffered=True)
        cur.execute("SELECT BuyQty,SellQty FROM product where  SkuCode=%s",(Sku_Code,))
        exqty = cur.fetchone()
        if exqty is None:
            pass
        else:
            Existing_Buy_Qty=int(exqty[0])
            Existing_Sell_Qty=int(exqty[1])
            Final_Buying_Qty=int(Existing_Buy_Qty+Change_Qty)
            Balance_Qty=int(Final_Buying_Qty-Existing_Sell_Qty)
            cur = self.con.cursor(buffered=True)
            cur.execute("UPDATE product SET BuyQty=%s,BalanceQty=%s WHERE SkuCode=%s ",(Final_Buying_Qty,Balance_Qty,Sku_Code,))
            self.con.commit()


    def assine_style_for_purchase_ev(self,ev):
        self.assine_style_for_purchase()

    def assine_style_for_purchase(self):
        #---------------------
        po_number = self.Po_Number_var.get().strip()
        product_name = self.Product_Name_inventory_var.get().strip()
        order_qty = self.Order_qty_var.get().strip()
        supplier = self.Supplier_var.get().strip()
        supplier_status=""
        #---------------------
        if not product_name:
            return messagebox.showerror("Info","Please select one style",parent=self.root)
        if not po_number:
            return messagebox.showerror("Info","Please select one PO",parent=self.root)
        if not order_qty:
            self.Qty_text.focus()
            return messagebox.showerror("Info","Please add order quantity",parent=self.root)
        if not order_qty.isdecimal():
            self.Order_qty_var.set("")
            self.Qty_text.focus()
            return messagebox.showerror("Info","Order quantity must be numeric",parent=self.root)
        order_qty_int = int(order_qty)
        style_exists = self.check_style_in_existing(po_number,product_name)
        if style_exists == "YES":
            if order_qty_int == 0:
                self.delete_product_in_po(po_number,product_name)
            else:
                self.update_product_in_po(po_number,product_name,order_qty_int)
        elif style_exists == "NO":
            supplier_check = self.match_supplier(po_number,supplier)
            if supplier_check == "NOT MATCH":
                return messagebox.showinfo("Info","Supplier differs from PO. Create a new PO.",parent=self.root)
            elif supplier_check == "NOT PRESENT":
                self.add_supplier(po_number,supplier)
                self.inset_style()
                return messagebox.showinfo("Info","Supplier differs from PO. Create a new PO.",parent=self.root)
            elif supplier_check == "MATCH":
                self.inset_style()
            self.po_calculations(po_number)
            self.show_purchase()
            self.show_products()
            self.view_rows_in_purchase_list(po_number,product_name)


    def check_style_in_existing(self,Po_number,ProductNameInventory):
        existing = ""
        cur = self.con.cursor(buffered=True)
        cur.execute("SELECT 1 from purchase WHERE ProductNameInventory=%s and PoNumber=%s LIMIT 1 ",
                    (ProductNameInventory,Po_number,))
        return "YES" if cur.fetchone() else "NO"

    def delete_product_in_po(self,Po_number,ProductNameInventory):
        cur = self.con.cursor(buffered=True)
        cur.execute("DELETE FROM  purchase  WHERE ProductNameInventory=%s and PoNumber=%s",(ProductNameInventory,Po_number,))
        self.con.commit()
        self.show_purchase()
        self.show_products()
        self.Order_qty_var.set("")
        self.po_calculations(Po_number)

    def update_product_in_po(self,Po_number,ProductNameInventory,Order_Qty):
        cur = self.con.cursor(buffered=True)
        cur.execute("UPDATE purchase SET BuyQty=%s WHERE ProductNameInventory=%s and PoNumber=%s",(Order_Qty,ProductNameInventory,Po_number,))
        self.con.commit()
        self.show_purchase()
        self.show_products()
        self.Order_qty_var.set("")
        self.po_calculations(Po_number)

    def match_supplier(self,po_number,new_supplier):
        cur = self.con.cursor(buffered=True)
        cur.execute("SELECT Supplier FROM po WHERE PoNumber = %s",(po_number,))
        result = cur.fetchone()
        if not result or result[0] is None or result[0].strip() == "":
            return "NOT PRESENT"
        elif result[0].strip() != new_supplier.strip():
            return "NOT MATCH"
        else:
            return "MATCH"



    def inset_style(self):
        cur = self.con.cursor(buffered=True)
        cur.execute("SELECT Status FROM po where  PoNumber=%s",(self.Po_Number_var.get(),))
        ex_sts = cur.fetchone()[0]
        cur = self.con.cursor(buffered=True)
        cur.execute("INSERT INTO purchase (PoNumber,SkuCode,ProductNameInventory,ProductNameDisplay,Supplier,BuyQty,SellQty,BalanceQty,AvgPrice,Status)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
               (self.Po_Number_var.get(), self.SKU_CODE_var.get() , self.Product_Name_inventory_var.get() , self.Product_Name_Display_var.get(),self.Supplier_var.get(),self.Order_qty_var.get(),"0","0","0","Pending"))
        self.con.commit()
        self.show_purchase()
        self.show_products()
        self.Order_qty_var.set("")

    def add_supplier(self,po,supp):
        cur = self.con.cursor(buffered=True)
        cur.execute("UPDATE po SET Supplier=%s  WHERE PoNumber=%s",(supp,po))
        self.con.commit()
        self.show_po_number()

    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    def clear_group(self):
        self.filter_group_var.set("")
        self.show_products()

    def show_ev(self,ev):
        self.show_products()

    def filter_by_group(self,ev):
        self.filter_group_var.set(self.Group_var.get())
        self.show_products()

    def show_products(self):
            group=self.filter_group_var.get()
            view_option=self.view_option_var.get()
            cur = self.con.cursor(buffered=True)
            # --- Build SQL query dynamically ---
            base_query = "SELECT ProductNameInventory, Supplier, BuyQty, SellQty, BalanceQty FROM product"
            where_clauses = []
            params = []
            if group:
                where_clauses.append("Grop = %s")
                params.append(group)
            where_clauses.append("(Status = 'live')")
            where_clause = " WHERE " + " AND ".join(where_clauses)
            order_by_clause = ""
            if view_option == "View_Sales As":
                order_by_clause = " ORDER BY SellQty"
            elif view_option == "View_Sales DeAs":
                order_by_clause = " ORDER BY SellQty DESC"
            query = base_query + where_clause + order_by_clause
            # --- Execute query ---
            cur.execute(query,tuple(params))
            rows = cur.fetchall()
            self.Product_Data_Tabel.delete(*self.Product_Data_Tabel.get_children())
            for count,row in enumerate(rows,start=1):
                ordered_qty = self.get_quantity(row[0])
                tag = 'even' if count % 2 == 0 else 'odd'
                self.Product_Data_Tabel.insert('','end',values=(count,row[0],row[1],row[2],row[3],row[4],ordered_qty), tags=tag)

    def get_quantity(self,ProductNameInventory):
        name=ProductNameInventory
        OrderedQuantity=int(0)
        cur = self.con.cursor(buffered=True)
        cur.execute("select sum(BuyQty) FROM purchase Where ProductNameInventory=%s and Status=%s ",(name,"Pending"))
        Ord_Quantity=cur.fetchone()
        if Ord_Quantity[0] is None:
            OrderedQuantity = int(0)
        else:
            OrderedQuantity = int(Ord_Quantity[0])
        return OrderedQuantity

    def eql_qty(self):
        cur = self.con.cursor(buffered=True)
        cur.execute("SELECT BuyQty,BalanceQty,SkuCode,PoNumber FROM purchase" )
        row = cur.fetchall()
        for x in row:
            cur = self.con.cursor(buffered=True)
            cur.execute("UPDATE purchase SET BuyQty=%s,SellQty=%s,BalanceQty=%s WHERE SkuCode=%s and PoNumber=%s ",(x[0],"0",x[0],x[2],x[3]))
            self.con.commit()
        cur = self.con.cursor(buffered=True)
        cur.execute("SELECT BuyQty,SkuCode FROM product" )
        row = cur.fetchall()
        for y in row:
            cur = self.con.cursor(buffered=True)
            cur.execute("UPDATE product SET BuyQty=%s ,SellQty=%s,BalanceQty=%s WHERE SkuCode=%s ",(y[0],"0",y[0],y[1]))
            self.con.commit()


    def show_purchase(self):
        # try:
            cur = self.con.cursor(buffered=True)
            cur.execute("SELECT ProductNameInventory,BuyQty FROM purchase where PoNumber=%s", (self.Po_Number_var.get(),))
            rows = cur.fetchall()
            self.Purchase_Data_Tabel.delete(*self.Purchase_Data_Tabel.get_children())
            for count ,row in enumerate (rows,start=1):
                my_tag = 'even' if count % 2 == 0 else 'odd'
                self.Purchase_Data_Tabel.insert('','end',values=(count,row[0],row[1]),tags=my_tag)
        # except Exception as ex:
        #     pass

    def print_pdf(self,):
        if self.Po_Number_var.get()=="":
            messagebox.showinfo("info",f"Please Select One Po  ",parent=self.root)
        else:
            cur = self.con.cursor(buffered=True)
            po_number=self.Po_Number_var.get()
            cur.execute("SELECT SkuCode,ProductNameInventory,BuyQty FROM purchase where PoNumber=%s",(po_number,))
            rows = cur.fetchall()
            if not rows:
                messagebox.showinfo("info",f"Dont Have Qty in po{po_number} ",parent=self.root)
            else:
                cur.execute("SELECT sum(BuyQty) FROM purchase where PoNumber=%s",(po_number,))
                q = cur.fetchone()[0] or 0
                pagesize = (260 * mm,297 * mm)
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"PO_{po_number}_Purchase_List_{timestamp}.pdf"

                styles = getSampleStyleSheet()
                elements = []
                doc = SimpleDocTemplate(filename,pagesize=pagesize,leftMargin=10,rightMargin=10,topMargin=10,bottomMargin=10)

                # header = Paragraph("<b>Company Name</b><br/>Purchase Order Summary",styles["Title"])
                metadata = Paragraph( f"<b>PO Number:</b> {po_number}<br/><b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}",styles["Normal"])
                # elements.extend([header,Spacer(1,12),metadata,Spacer(1,20)])
                elements.extend([metadata,Spacer(1,20)])
                data = [['S.No','SKU Code','Description','Order Qty','Received','Balance']]
                for idx,(sku,name,qty) in enumerate(rows,start=1):
                    data.append([idx,sku,name,qty,"",""])
                data.append(["","","Total",q,"",""])
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#2766A8")),
                    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                    ('ALIGN',(0,0),(-1,0),'CENTER'),
                    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                    ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor("#f8f4f4")]),
                    ('GRID',(0,0),(-1,-1),0.25,colors.grey),]))
                elements.append(table)
                doc.build(elements)
                pdf_path = os.path.abspath(filename)
                try:
                    os.startfile(pdf_path)
                except AttributeError:
                    import subprocess
                    subprocess.Popen(["open" if os.name == "posix" else "xdg-open",pdf_path])

    def show_po_number(self):
        # try:
            cur = self.con.cursor(buffered=True)
            cur.execute("SELECT PoNumber FROM po ")
            rows = cur.fetchall()
            self.Order_Data_Tabel.delete(*self.Order_Data_Tabel.get_children())
            for count,row in enumerate(rows):
                my_tag = 'even' if count % 2 == 0 else 'odd'
                self.Order_Data_Tabel.insert('','end',values=(row[0],),tags=(my_tag,))
        # except Exception as ex:
        #     pass

    def get_product(self,ev):
        try:
            f = self.Product_Data_Tabel.focus()
            content = (self.Product_Data_Tabel.item(f))
            row = content['values']
            self.Product_Name_inventory_var.set(row[1]),
            cur=self.con.cursor()
            cur.execute("select ProId,Grop,SkuCode,ProductNameDisplay,Supplier FROM product Where ProductNameInventory=%s ",(self.Product_Name_inventory_var.get(),))
            ids=cur.fetchone()
            self.Pro_ID_var.set(ids[0])
            self.Group_var.set(ids[1])
            self.SKU_CODE_var.set(ids[2])
            self.Product_Name_Display_var.set(ids[3])
            self.Supplier_var.set(ids[4])
            self.Qty_text.focus()
            self.Order_qty_var.set(""),
            self.view_rows_in_purchase_list(self.Po_Number_var.get(),self.Product_Name_inventory_var.get())
        except Exception as ex:
            pass

    def view_rows_in_purchase_list(self,po,pro):
            try:
                cur = self.con.cursor(buffered=True)
                cur.execute("SELECT ProductNameInventory FROM purchase WHERE PoNumber = %s",(po,))
                purchase_detail = cur.fetchall()

                # Find the index of the matching product
                product_location_index = None
                for idx,pur in enumerate(purchase_detail):
                    if pro == pur[0]:
                        product_location_index = idx
                        break
                # Focus on the corresponding row in the Treeview
                children = self.Purchase_Data_Tabel.get_children()
                if children and product_location_index < len(children):
                    target_item = children[product_location_index]
                    self.Purchase_Data_Tabel.focus(target_item)
                    self.Purchase_Data_Tabel.selection_set(target_item)
                    content = self.Purchase_Data_Tabel.item(target_item)
                    row = content['values']
                    # Assuming proper indexes for data in row
                    self.Product_Name_inventory_var.set(row[1])  # Product name
                    self.Order_qty_var.set(row[2])  # Ordered qty
                    self.Qty_text.focus()
                    self.Order_qty_var.set("")  # Reset entry field (possibly accidental?)
                else:
                    pass
            except Exception as ex:
                pass

    def get_po_number(self,ev):
        # try:
            self.Total_qty_var.set("0")
            f = self.Order_Data_Tabel.focus()
            content = (self.Order_Data_Tabel.item(f))
            row = content['values']
            self.Po_Number_var.set(row[0]),
            cur=self.con.cursor()
            cur.execute("select Supplier,Status,ProductPrice,Total,Transport1,Transport2,AvgPrice FROM po Where PoNumber=%s ",(self.Po_Number_var.get(),))
            ids=cur.fetchone()
            self.Supplier_var.set(ids[0])
            self.Status_var.set(ids[1])
            self.Product_Price_var .set(ids[2])
            self.Total_var.set(ids[3])
            self.Trn1_var.set(ids[4])
            self.Trn2_var.set(ids[5])
            self.Avg_price_var.set(ids[6])
            self.show_purchase()
            self.Qty_text.focus()
            self.Order_qty_var.set(""),
            self.po_calculations(self.Po_Number_var.get())
            if self.Status_var.get()=="Approve":
                self.add_btn["state"] = "disabled"
                self.Qty_text["state"] = "disabled"
                self.Trn1_txt["state"] = "disabled"
                self.Trn2_txt["state"] = "disabled"
                self.Product_Price_txt["state"] = "disabled"
            else:
                self.add_btn["state"] = "enable"
                self.Qty_text["state"] = "enable"
                self.Trn1_txt["state"] = "enable"
                self.Trn2_txt["state"] = "enable"
                self.Product_Price_txt["state"] = "enable"
    # except Exception as ex:
        #     pass

    def get_purchase(self,ev):
        try:
            f = self.Purchase_Data_Tabel.focus()
            content = (self.Purchase_Data_Tabel.item(f))
            row = content['values']
            self.Product_Name_inventory_var.set(row[1]),
            self.Order_qty_var.set(row[2]),
            self.Qty_text.focus()
            self.Order_qty_var.set(""),
        except Exception as ex:
            pass







if __name__ == '__main__':
    root = Tk()
    obj = purchase(root)
    root.mainloop()
