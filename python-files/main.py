import tkinter as tk
from ui.inbound import InboundFrame
from ui.outbound import OutboundFrame
from ui.item_master import ItemMasterFrame
from ui.stock_report import StockReportFrame
from ui.location_report import LocationReportFrame
from ui.date_report import DateReportFrame
from ui.settings import SettingsFrame
from database import init_db

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management System")
        self.geometry("1024x600")
        self.resizable(False, False)
        self.create_menu()
        self.main_frame = None
        self.show_frame(InboundFrame)

    def create_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)

        menu.add_command(label="Inbound Entry", command=lambda: self.show_frame(InboundFrame))
        menu.add_command(label="Outbound Entry", command=lambda: self.show_frame(OutboundFrame))
        menu.add_command(label="Item Master", command=lambda: self.show_frame(ItemMasterFrame))
        menu.add_command(label="Stock Report", command=lambda: self.show_frame(StockReportFrame))
        menu.add_command(label="Location Report", command=lambda: self.show_frame(LocationReportFrame))
        menu.add_command(label="Date-wise Report", command=lambda: self.show_frame(DateReportFrame))
        menu.add_command(label="Company Settings", command=lambda: self.show_frame(SettingsFrame))

    def show_frame(self, frame_class):
        if self.main_frame:
            self.main_frame.destroy()
        self.main_frame = frame_class(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

if __name__ == '__main__':
    init_db()
    app = InventoryApp()
    app.mainloop()
