from flask import Flask, render_template, request, redirect, flash
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)
app.secret_key = "secret-key"

# Configure sender details
SENDER_EMAIL = "test.server.0789@gmail.com"
SENDER_PASSWORD = "iodjruuqholxupnm"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send():
    print("IN FUNC")
    emails = request.form["emails"].split(",")
    subject = request.form["subject"]
    body = request.form["body"]
    attachment = request.files["attachment"]

    for email in emails:
        email = email.strip()
        if not email:
            continue
        print(f"Sending to {email}")
        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = email
        msg["Subject"] = subject
        msg.set_content(body)

        if attachment and attachment.filename != "":
            file_data = attachment.read()
            msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=attachment.filename)

        try:
            print("In try")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.set_debuglevel(1)
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
                print("logged in")
                smtp.send_message(msg)
                print("hello")
        except Exception as e:
            flash(f"Failed to send to {email}: {e}", "danger")
            continue

    flash("Emails sent successfully!", "success")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
