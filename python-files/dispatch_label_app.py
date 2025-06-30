import os
import sys
import qrcode
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QSpinBox
)


class DispatchLabelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dispatch Label Generator")
        self.setGeometry(100, 100, 600, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.order_number = 12345  # Initial order number
        self.create_input_fields()
        self.create_buttons()

    def create_input_fields(self):
        # Product Type
        self.product_label = QLabel("Product Type:")
        self.product_dropdown = QComboBox()
        self.product_dropdown.addItems(["Power", "Booster"])

        # Dispatch Date
        self.date_label = QLabel("Dispatch Date (DD/MM/YYYY):")
        self.date_input = QLineEdit()

        # Customer Name
        self.name_label = QLabel("Customer Name:")
        self.name_input = QLineEdit()

        # Address
        self.address_label = QLabel("Address:")
        self.address_input = QLineEdit()

        # Contact
        self.contact_label = QLabel("Contact Number:")
        self.contact_input = QLineEdit()

        # Quantity
        self.quantity_label = QLabel("Quantity:")
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)

        # Batch Number
        self.batch_label = QLabel("Batch Number:")
        self.batch_input = QLineEdit()

        # Add fields to the layout
        fields = [
            (self.product_label, self.product_dropdown),
            (self.date_label, self.date_input),
            (self.name_label, self.name_input),
            (self.address_label, self.address_input),
            (self.contact_label, self.contact_input),
            (self.quantity_label, self.quantity_input),
            (self.batch_label, self.batch_input),
        ]
        for label, widget in fields:
            self.layout.addWidget(label)
            self.layout.addWidget(widget)

    def create_buttons(self):
        # Generate and Exit Buttons
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Dispatch Label")
        self.generate_button.clicked.connect(self.generate_dispatch_label)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)

        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.exit_button)
        self.layout.addLayout(button_layout)

    def generate_dispatch_label(self):
        # Gather inputs
        product_type = self.product_dropdown.currentText()
        dispatch_date = self.date_input.text()
        customer_name = self.name_input.text()
        address = self.address_input.text()
        contact = self.contact_input.text()
        quantity = self.quantity_input.value()
        batch_number = self.batch_input.text()

        # Validate inputs
        if not (dispatch_date and customer_name and address and contact and batch_number):
            QMessageBox.warning(self, "Input Error", "All fields are mandatory!")
            return

        # Generate data for dispatch
        order_number = f"#{product_type[0].upper()}{self.order_number}"
        self.order_number += 1
        weight = f"{quantity * 10}ml"

        data = {
            "Order Number": order_number,
            "Dispatch Date": dispatch_date,
            "Customer Name": customer_name,
            "Address": address,
            "Contact": contact,
            "Product": product_type,
            "Quantity": quantity,
            "Weight": weight,
            "Batch Number": batch_number,
        }

        # Generate dispatch label and update Excel
        folder_path = r"C:\Users\Bhavesh Kayya\Downloads\dispatch code"
        os.makedirs(folder_path, exist_ok=True)
        label_path, log_path = self.create_dispatch_label(data, folder_path)

        QMessageBox.information(
            self, "Success",
            f"Dispatch label saved at:\n{label_path}\n\nLog updated at:\n{log_path}"
        )

    def create_dispatch_label(self, data, save_directory):
        # Generate QR code
        qr_path = os.path.join(save_directory, "dispatch_qr.png")
        self.generate_qr(data, qr_path)

        # Generate JPEG
        jpeg_path = os.path.join(save_directory, f"dispatch_label_{data['Order Number']}.jpeg")
        self.generate_jpeg(data, qr_path, jpeg_path)

        # Update Excel log
        excel_path = os.path.join(save_directory, "dispatch_log.xlsx")
        self.update_excel(data, excel_path)

        return jpeg_path, excel_path

    @staticmethod
    def generate_qr(data, output_path):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)

    @staticmethod
    def generate_jpeg(data, qr_path, output_path):
        # Create blank image
        image = Image.new("RGB", (1000, 700), "white")
        draw = ImageDraw.Draw(image)

        # Load fonts
        try:
            font_title = ImageFont.truetype("arial.ttf", 26)
            font_content = ImageFont.truetype("arial.ttf", 18)
            font_bold = ImageFont.truetype("arialbd.ttf", 18)
        except IOError:
            font_title = ImageFont.load_default()
            font_content = ImageFont.load_default()
            font_bold = ImageFont.load_default()

        # Draw header box
        draw.rectangle([(20, 20), (980, 120)], outline="black", width=3)
        draw.text((30, 40), "Naavinya Power Lubricants India Private Limited", fill="black", font=font_title)
        draw.text((30, 80), "Contact: 9326201351 | Email: support@naavinyapowerlubricants.com", fill="black", font=font_content)

        # Draw dispatch details
        draw.rectangle([(20, 140), (980, 600)], outline="black", width=3)
        draw.text((30, 150), "Dispatch Details", fill="black", font=font_bold)

        details = [
            ("Order Number", data["Order Number"]),
            ("Dispatch Date", data["Dispatch Date"]),
            ("Customer Name", data["Customer Name"]),
            ("Address", data["Address"]),
            ("Contact", data["Contact"]),
            ("Product", data["Product"]),
            ("Quantity", str(data["Quantity"])),
            ("Weight", data["Weight"]),
            ("Batch Number", data["Batch Number"]),
        ]

        y_offset = 190
        for label, value in details:
            draw.text((40, y_offset), f"{label}:", fill="black", font=font_bold)
            draw.text((300, y_offset), value, fill="black", font=font_content)
            y_offset += 40

        qr_image = Image.open(qr_path).resize((150, 150))
        image.paste(qr_image, (800, 200))

        image.save(output_path)

    def update_excel(self, data, excel_path):
        row_data = pd.DataFrame([data])

        if os.path.exists(excel_path):
            try:
                with open(excel_path, "rb"):
                    pass
            except IOError:
                QMessageBox.warning(self, "File Error", "Close the Excel file to update!")
                return

            existing_data = pd.read_excel(excel_path, engine='openpyxl')
            updated_data = pd.concat([existing_data, row_data], ignore_index=True)
        else:
            updated_data = row_data

        updated_data.to_excel(excel_path, index=False, engine='openpyxl')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = DispatchLabelApp()
    main_window.show()
    sys.exit(app.exec_())
