import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

class PDFEmailSender:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Email Sender with Watermark")
        self.root.geometry("800x900")
        
        # Variables
        self.pdf_path = ""
        self.output_dir = os.getcwd()
        
        # Setup UI
        self.create_widgets()
    
    def create_widgets(self):
        # Email Entry Frame
        email_frame = tk.LabelFrame(self.root, text="Recipient Emails", padx=10, pady=10)
        email_frame.pack(pady=10, padx=10, fill="x")
        
        self.email_entry = scrolledtext.ScrolledText(email_frame, width=70, height=8)
        self.email_entry.pack()
        tk.Label(email_frame, text="Enter one email per line").pack()
        
        # PDF Selection Frame
        pdf_frame = tk.LabelFrame(self.root, text="PDF File", padx=10, pady=10)
        pdf_frame.pack(pady=10, padx=10, fill="x")
        
        self.pdf_label = tk.Label(pdf_frame, text="No PDF selected", wraplength=600)
        self.pdf_label.pack()
        tk.Button(pdf_frame, text="Browse PDF", command=self.select_pdf).pack(pady=5)
        
        # Output Directory Frame
        dir_frame = tk.LabelFrame(self.root, text="Output Folder", padx=10, pady=10)
        dir_frame.pack(pady=10, padx=10, fill="x")
        
        self.dir_label = tk.Label(dir_frame, text=self.output_dir, wraplength=600)
        self.dir_label.pack()
        tk.Button(dir_frame, text="Select Output Folder", command=self.select_output_dir).pack(pady=5)
        
        # Email Message Frame
        msg_frame = tk.LabelFrame(self.root, text="Email Message", padx=10, pady=10)
        msg_frame.pack(pady=10, padx=10, fill="x")
        
        tk.Label(msg_frame, text="Subject:").pack()
        self.msg_subject = tk.Entry(msg_frame, width=70)
        self.msg_subject.insert(0, "Your Document")
        self.msg_subject.pack()
        
        tk.Label(msg_frame, text="Body:").pack()
        self.msg_body = scrolledtext.ScrolledText(msg_frame, width=70, height=6)
        self.msg_body.insert("1.0", "Hello,\n\nPlease find attached your document.")
        self.msg_body.pack()
        
        # Email Config Frame
        config_frame = tk.LabelFrame(self.root, text="Gmail Configuration", padx=10, pady=10)
        config_frame.pack(pady=10, padx=10, fill="x")
        
        tk.Label(config_frame, text="Your Gmail:").grid(row=0, column=0, sticky="w")
        self.sender_entry = tk.Entry(config_frame, width=40)
        self.sender_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(config_frame, text="App Password:").grid(row=1, column=0, sticky="w")
        self.password_entry = tk.Entry(config_frame, width=40, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        # Send Button
        tk.Button(self.root, text="PROCESS & SEND EMAILS", 
                 command=self.process_and_send_emails,
                 bg="green", fg="white", font=("Arial", 12)).pack(pady=20)
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        tk.Label(self.root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w").pack(fill="x")
    
    def select_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        self.pdf_label.config(text=os.path.basename(self.pdf_path) if self.pdf_path else "No PDF selected")
    
    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        if self.output_dir:
            self.dir_label.config(text=self.output_dir)

    def add_watermark(self, pdf_path, email, output_path):
        """Adds a single centered watermark behind text"""
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Create watermark
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        c.setFont("Helvetica", 40)
        c.setFillColorRGB(0.7, 0.7, 0.7, alpha=0.4)  # Light gray, 40% opacity
        
        # Calculate center position
        page_width, page_height = letter
        text = email
        text_width = c.stringWidth(text, "Helvetica", 40)
        
        # Draw single watermark at 30° angle
        c.saveState()
        c.translate(page_width/2, page_height/2)
        c.rotate(30)
        c.drawString(-text_width/2, 0, text)  # Perfectly centered
        c.restoreState()
        c.save()
        
        # Merge watermark
        packet.seek(0)
        watermark = PdfReader(packet)
        
        for page in reader.pages:
            page.merge_page(watermark.pages[0])
            writer.add_page(page)
        
        with open(output_path, "wb") as f:
            writer.write(f)
    
    def process_and_send_emails(self):
        try:
            # Get inputs
            sender = self.sender_entry.get().strip()
            password = self.password_entry.get().strip()
            emails = [line.strip() for line in self.email_entry.get("1.0", "end").splitlines() if line.strip()]
            subject = self.msg_subject.get().strip()
            body = self.msg_body.get("1.0", "end").strip()
            
            # Validate
            if not all([sender, password, emails, self.pdf_path]):
                messagebox.showerror("Error", "All fields are required!")
                return
            
            # Process each email
            for email in emails:
                self.status_var.set(f"Processing {email}...")
                self.root.update()
                
                # Create watermarked PDF (named with just the email)
                output_pdf = os.path.join(self.output_dir, f"{email}.pdf")  # Removed "watermarked_" prefix
                self.add_watermark(self.pdf_path, email, output_pdf)
                
                # Prepare email
                msg = MIMEMultipart()
                msg['From'] = sender
                msg['To'] = email
                msg['Subject'] = subject
                
                # Personalize body
                personalized_body = body.replace("{email}", email)
                msg.attach(MIMEText(personalized_body, 'plain'))
                
                # Attach PDF
                with open(output_pdf, "rb") as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 
                                  f'attachment; filename="{os.path.basename(output_pdf)}"')
                    msg.attach(part)
                
                # Send email
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(sender, password)
                    server.sendmail(sender, email, msg.as_string())
                
                # Removed the os.remove(output_pdf) line to keep the file
                self.status_var.set(f"Sent to {email}")
                self.root.update()
            
            messagebox.showinfo("Success", "All emails sent successfully! PDFs saved in output folder.")
            self.status_var.set("Process completed - PDFs saved")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process:\n{str(e)}")
            self.status_var.set(f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFEmailSender(root)
    root.mainloop()