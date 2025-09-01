import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time

# ASCII Art Animation
def computer_animation()
    frames = [
        
  ____________________________
   ________________________  
                           
      DARKBOSS1BD          
      Email Sender         
  ________________________ 
 ____________________________
        
        ,
        
  ____________________________
   ________________________  
                           
      DARKBOSS1BD          
      Sending Emails...    
  ________________________ 
 ____________________________
        
        ,
        
  ____________________________
   ________________________  
                           
      DARKBOSS1BD          
      Sent Successfully!   
  ________________________ 
 ____________________________
        
        
    ]
    for frame in frames
        banner_label.config(text=frame)
        time.sleep(1)

# Send Emails
def send_emails()
    smtp_server = smtp_entry.get()
    smtp_port = int(port_entry.get())
    sender_email = email_entry.get()
    sender_password = password_entry.get()
    subject = subject_entry.get()
    body = body_text.get(1.0, tk.END)
    recipients = recipient_text.get(1.0, tk.END).strip().split(n)

    if not all([smtp_server, sender_email, sender_password, subject, body]) or not recipients
        messagebox.showerror(Error, Please fill in all fields and at least one recipient.)
        return

    def send()
        try
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)

            for recipient in recipients
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                server.sendmail(sender_email, recipient, msg.as_string())

            server.quit()
            messagebox.showinfo(Success, Emails sent successfully!)
        except Exception as e
            messagebox.showerror(Error, str(e))

    # Start animation and send in background
    threading.Thread(target=computer_animation).start()
    threading.Thread(target=send).start()

# GUI Setup
root = tk.Tk()
root.title(📧 DARKBOSS1BD - Email Sender Tool)
root.geometry(700x600)
root.configure(bg=#1e1e1e)

# Banner
banner_label = tk.Label(root, text=, font=(Courier, 10), bg=#1e1e1e, fg=cyan)
banner_label.pack(pady=10)

# SMTP Settings
frame_smtp = tk.LabelFrame(root, text=⚙️ SMTP Settings, bg=#2e2e2e, fg=white)
frame_smtp.pack(fill=x, padx=10, pady=5)

tk.Label(frame_smtp, text=SMTP Server, bg=#2e2e2e, fg=white).grid(row=0, column=0, sticky=w, padx=5, pady=5)
smtp_entry = tk.Entry(frame_smtp, width=30)
smtp_entry.grid(row=0, column=1, padx=5, pady=5)
smtp_entry.insert(0, smtp.gmail.com)

tk.Label(frame_smtp, text=Port, bg=#2e2e2e, fg=white).grid(row=0, column=2, sticky=w, padx=5, pady=5)
port_entry = tk.Entry(frame_smtp, width=10)
port_entry.grid(row=0, column=3, padx=5, pady=5)
port_entry.insert(0, 587)

tk.Label(frame_smtp, text=Email, bg=#2e2e2e, fg=white).grid(row=1, column=0, sticky=w, padx=5, pady=5)
email_entry = tk.Entry(frame_smtp, width=30)
email_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_smtp, text=Password, bg=#2e2e2e, fg=white).grid(row=1, column=2, sticky=w, padx=5, pady=5)
password_entry = tk.Entry(frame_smtp, show=, width=20)
password_entry.grid(row=1, column=3, padx=5, pady=5)

# Email Content
frame_content = tk.LabelFrame(root, text=✉️ Email Content, bg=#2e2e2e, fg=white)
frame_content.pack(fill=both, expand=True, padx=10, pady=5)

tk.Label(frame_content, text=Subject, bg=#2e2e2e, fg=white).grid(row=0, column=0, sticky=w, padx=5, pady=5)
subject_entry = tk.Entry(frame_content, width=60)
subject_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_content, text=Body, bg=#2e2e2e, fg=white).grid(row=1, column=0, sticky=nw, padx=5, pady=5)
body_text = scrolledtext.ScrolledText(frame_content, width=60, height=6, bg=#1e1e1e, fg=white)
body_text.grid(row=1, column=1, padx=5, pady=5)

# Recipients
frame_recipients = tk.LabelFrame(root, text=👥 Recipients (One per line), bg=#2e2e2e, fg=white)
frame_recipients.pack(fill=both, expand=True, padx=10, pady=5)

recipient_text = scrolledtext.ScrolledText(frame_recipients, width=60, height=6, bg=#1e1e1e, fg=white)
recipient_text.pack(padx=5, pady=5)

# Send Button
send_button = tk.Button(root, text=🚀 Send Emails, command=send_emails, bg=#0066cc, fg=white, font=(Arial, 12))
send_button.pack(pady=10)

# Footer
footer = tk.Label(root, text=🛠️ Developed by DARKBOSS1BD, bg=#1e1e1e, fg=gray)
footer.pack(side=bottom, pady=5)

# Run Animation on Start
threading.Thread(target=computer_animation).start()

root.mainloop()