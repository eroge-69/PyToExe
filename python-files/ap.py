from flask import Flask, request, render_template, send_file, redirect, url_for
import os
import pandas as pd
import pdfplumber
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)

# ಫೈಲ್‌ಗಳನ್ನು ತಾತ್ಕಾಲಿಕವಾಗಿ ಉಳಿಸಲು ಫೋಲ್ಡರ್‌ಗಳು
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ಡೌನ್‌ಲೋಡ್ ಮಾಡಲು ಕೊನೆಯದಾಗಿ ರಚಿಸಿದ ಫೈಲ್‌ನ ಪಾತ್
last_output_path = ""

def clean_amount(amount_str):
    """ಮೊತ್ತದಲ್ಲಿರುವ ಕಾಮ (,) ಮತ್ತು ಕರೆನ್ಸಿ (Cr/Dr) ತೆಗೆದುಹಾಕುವ ಫಂಕ್ಷನ್"""
    if amount_str is None or amount_str.strip() == "":
        return 0.0
    cleaned_str = str(amount_str).replace(',', '')
    cleaned_str = re.sub(r'[^\d.]', '', cleaned_str)
    try:
        return float(cleaned_str)
    except (ValueError, TypeError):
        return 0.0

def parse_canara_statement(filepath):
    """ಕೆನರಾ ಬ್ಯಾಂಕ್ ಸ್ಟೇಟ್‌ಮೆಂಟ್‌ಗಳನ್ನು ಪಾರ್ಸ್ ಮಾಡುವ ಫಂಕ್ಷನ್"""
    all_transactions = []
    full_text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text(x_tolerance=2) + "\n"
    
    # ಪ್ರತಿ ದಿನಾಂಕದೊಂದಿಗೆ ಪ್ರಾರಂಭವಾಗುವ ಸಾಲುಗಳನ್ನು ಹುಡುಕಿ.
    # ಮಾದರಿ: 01-04-2024	01-04-2024	110901004117	By Clearing	31835.00	148107.41
    lines = full_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not re.match(r'^\d{2}-\d{2}-\d{4}', line):
            continue

        try:
            parts = line.split('\t')  # ಟ್ಯಾಬ್‌ಗಳನ್ನು ಬಳಸಿ ಡೇಟಾವನ್ನು ವಿಭಜಿಸಿ
            if len(parts) < 6:
                continue

            gl_date = parts[0].strip()
            value_date = parts[1].strip()
            
            # ನರೇಟಿವ್ ಮತ್ತು ಮೊತ್ತವನ್ನು ಗುರುತಿಸಿ
            particulars = parts[3].strip()
            tran_id = parts[2].strip()
            
            # ಡೆಬಿಟ್/ಕ್ರೆಡಿಟ್ ಮತ್ತು ಬ್ಯಾಲೆನ್ಸ್ ಮೊತ್ತಗಳನ್ನು ಕಂಡುಹಿಡಿಯಿರಿ.
            # ಕೆನರಾ ಬ್ಯಾಂಕ್ ಸ್ಟೇಟ್‌ಮೆಂಟ್‌ಗಳಲ್ಲಿ ಡೆಬಿಟ್ ಮತ್ತು ಕ್ರೆಡಿಟ್ ಮೊತ್ತಗಳು ಬೇರೆ ಬೇರೆ ಕಾಲಂಗಳಲ್ಲಿರುತ್ತವೆ.
            # ಆದರೆ ಕೆಲವು ಸ್ಟೇಟ್‌ಮೆಂಟ್‌ಗಳಲ್ಲಿ ಕ್ರೆಡಿಟ್ ಮೊತ್ತಗಳು ಕೊನೆಯಲ್ಲಿ ಇರುತ್ತವೆ.
            
            # ಇಲ್ಲಿ ಡೆಬಿಟ್ ಅಥವಾ ಕ್ರೆಡಿಟ್ ಯಾವುದು ಎಂಬುದು ಮೊತ್ತದ ನಂತರ ಬರುವ 'Cr' ಅಥವಾ 'Dr' ನಿಂದ ನಿರ್ಧರಿಸಲಾಗುತ್ತದೆ.
            # ಕೆನರಾ ಬ್ಯಾಂಕ್ ಸ್ಟೇಟ್‌ಮೆಂಟ್‌ಗಳಲ್ಲಿ ಈ ಸೂಚಕಗಳು ಸಾಮಾನ್ಯವಾಗಿರುತ್ತವೆ.
            
            transaction_amount = 0.0
            balance = 0.0
            debit = 0.0
            credit = 0.0

            # ಸಾಲಿನಲ್ಲಿ ಕೊನೆಯ ಎರಡು ಸಂಖ್ಯಾ ಮೌಲ್ಯಗಳು ಸಾಮಾನ್ಯವಾಗಿ ಟ್ರಾನ್ಸಾಕ್ಷನ್ ಮೊತ್ತ ಮತ್ತು ಬ್ಯಾಲೆನ್ಸ್ ಆಗಿರುತ್ತವೆ
            amounts = re.findall(r'[\d,]+\.\d{2}', line)
            if len(amounts) >= 2:
                balance = clean_amount(amounts[-1])
                transaction_amount = clean_amount(amounts[-2])
            
            # ಇಲ್ಲಿ ಕ್ರೆಡಿಟ್ ಮತ್ತು ಡೆಬಿಟ್ ಅನ್ನು ಸರಿಯಾಗಿ ಬೇರ್ಪಡಿಸಲು ಪ್ರಯತ್ನಿಸುತ್ತೇವೆ
            if "Cr" in line:
                credit = transaction_amount
            else:
                debit = transaction_amount

            all_transactions.append({
                "GL Date": gl_date,
                "Value Date": value_date,
                "Tran Id": tran_id,
                "Particulars": particulars,
                "Debit Amount": debit,
                "Credit Amount": credit,
                "Balance": balance
            })

        except Exception as e:
            print(f"Error parsing line: '{line}' -> {e}")
            continue
    
    return all_transactions

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    global last_output_path
    if 'pdf_file' not in request.files:
        return redirect(request.url)
    file = request.files['pdf_file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # ಕೆನರಾ ಬ್ಯಾಂಕ್ ಸ್ಟೇಟ್‌ಮೆಂಟ್‌ಗಳನ್ನು ನಿರ್ದಿಷ್ಟವಾಗಿ ನಿರ್ವಹಿಸಲು
        # ಇಲ್ಲಿ ನಾವು ಬ್ಯಾಕಪ್ ವಿಧಾನವನ್ನು ಬಳಸುತ್ತೇವೆ, ಏಕೆಂದರೆ `extract_tables` ಯಾವಾಗಲೂ ಕೆಲಸ ಮಾಡುವುದಿಲ್ಲ.
        data = parse_canara_statement(filepath)
        
        if data:
            df = pd.DataFrame(data)
            output_excel = os.path.join(OUTPUT_FOLDER, "Canara_Bank_Statement_Converted.xlsx")
            df.to_excel(output_excel, index=False)
            last_output_path = output_excel
            table_html = df.to_html(classes='table table-striped', index=False)
            return render_template("index.html", table=table_html, show_download=True)
        else:
            message = "❌ ಈ PDF ಫೈಲ್‌ನಲ್ಲಿ ಯಾವುದೇ ಟ್ರಾನ್ಸಾಕ್ಷನ್ ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ಫೈಲ್ ಪರಿಶೀಲಿಸಿ."
            return render_template("index.html", message=message)
            
    return redirect(url_for('index'))

@app.route('/download')
def download_file():
    if last_output_path and os.path.exists(last_output_path):
        return send_file(last_output_path, as_attachment=True)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)