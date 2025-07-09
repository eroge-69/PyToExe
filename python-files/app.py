from flask import Flask, request, jsonify
import win32print
import win32ui
import win32con
import tempfile
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://pos-master-frontend-web.vercel.app"])

def format_bill(data):
    # Optional: Fetch shop name from request or set default
    shop_name = "POS Master Shop"

    # Format date and time
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%I:%M:%S %p")

    # Header
    lines = []
    lines.append(shop_name.center(40))
    lines.append("-" * 40)
    lines.append(f"Date: {date_str}".center(40))
    lines.append(f"Time: {time_str}".center(40))
    lines.append("-" * 40)
    lines.append("{:<15}{:<5}{:>7}{:>10}".format("Product", "Qty", "Price", "Total"))

    # Items
    lines.append("-" * 40)
    for item in data.get('itemsSelled', []):
        name = item.get('product', {}).get('name', 'Unknown')
        qty = item.get('qty', 0)
        price = item.get('qntPrice', 0)
        total = qty * price
        # Truncate name to fit within 15 characters to maintain alignment
        name = (name[:12] + '...') if len(name) > 15 else name
        lines.append("{:<15}{:<5}{:>7.2f}{:>10.2f}".format(name, qty, price, total))

    # Totals
    lines.append("-" * 40)
    lines.append(f"{'Total:':>30} {data.get('total', 0):.2f}")
    lines.append(f"{'Discount:':>30} {data.get('discount', 0):.2f}")
    lines.append(f"{'Pending Amount:':>30} {data.get('pendingdAmount', 0):.2f}")
    lines.append(f"{'Net Total:':>30} {data.get('netTotal', 0):.2f}")
    
    lines.append("-" * 40)
    lines.append("** GOOD DAY COME BACK **".center(40))
    lines.append("\n")

    return '\n'.join(lines)

@app.route('/invoice/bill', methods=['POST'])
def print_bill():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON'}), 400

        bill_text = format_bill(data)

        # Get the default printer
        printer_name = win32print.GetDefaultPrinter()
        
        # Create a device context for the printer
        hprinter = win32print.OpenPrinter(printer_name)
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(printer_name)

        # Start the print job
        hdc.StartDoc('Bill')
        hdc.StartPage()

        # Set margins to zero (in device units, typically 1000ths of an inch)
        hdc.SetMapMode(win32con.MM_TEXT)
        hdc.SetWindowOrg((0, 0))
        hdc.SetViewportOrg((0, 0))

        # Set font (optional, adjust as needed for your thermal printer)
        font = win32ui.CreateFont({
            "name": "Courier New",
            "height": 100,  # Adjust font size as needed
            "weight": win32con.FW_NORMAL
        })
        hdc.SelectObject(font)

        # Print the bill text line by line
        y = 0
        for line in bill_text.split('\n'):
            hdc.TextOut(0, y, line)
            y += 80  # Adjust line spacing as needed

        # End the print job
        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()
        win32print.ClosePrinter(hprinter)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)