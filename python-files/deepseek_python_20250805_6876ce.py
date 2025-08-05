# WhatsApp Integration (add this to your code)
import webbrowser

def send_whatsapp_invoice():
    phone = self.customer_phone.get()
    message = f"Dear {self.customer_name.get()}, your invoice {self.current_invoice_no} is ready!"
    webbrowser.open(f"https://wa.me/{phone}?text={message}")