import tkinter as tk
from tkinter import messagebox, filedialog
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

def detect_retail_signals(data):
    signals = []

    buyer_share = data['buyer_share']
    seller_share = data['seller_share']
    buyers_in_profit = data['buyers_in_profit']
    sellers_in_profit = data['sellers_in_profit']
    buyers_in_loss = data['buyers_in_loss']
    sellers_in_loss = data['sellers_in_loss']
    buy_stops = data['buy_stops']
    sell_stops = data['sell_stops']
    buy_limits = data['buy_limits']
    sell_limits = data['sell_limits']
    profit_ratio_buyers = data['profit_ratio_buyers']
    profit_ratio_sellers = data['profit_ratio_sellers']

    if seller_share > 65 and sellers_in_loss > 10 and buy_stops > sell_stops:
        signals.append("🔥 Bullish Reversal: Short squeeze setup.")
    if buyer_share > 65 and buyers_in_loss > 10 and sell_stops > buy_stops:
        signals.append("🧊 Bearish Reversal: Long squeeze setup.")
    if buy_limits > sell_limits * 1.5:
        signals.append("📉 Buy Limit Support: Strong dip buying.")
    if sell_limits > buy_limits * 1.5:
        signals.append("📈 Sell Limit Resistance: Strong supply zone.")
    if buyers_in_profit < 7 and sellers_in_profit < 7:
        signals.append("💤 Market Indecision: Very few in profit.")
    if profit_ratio_buyers > 55 and buyer_share < 40:
        signals.append("🔍 Hidden Bullish Divergence: Fewer buyers, better performance.")

    if not signals:
        signals.append("✅ No strong signals. Market might be neutral or consolidating.")

    return signals

def run_analysis():
    try:
        data = {
            'buyer_share': float(entries['Buyer Share'].get()),
            'seller_share': float(entries['Seller Share'].get()),
            'buyers_in_profit': float(entries['Buyers in Profit'].get()),
            'sellers_in_profit': float(entries['Sellers in Profit'].get()),
            'buyers_in_loss': float(entries['Buyers in Loss'].get()),
            'sellers_in_loss': float(entries['Sellers in Loss'].get()),
            'buy_stops': float(entries['Buy Stops'].get()),
            'sell_stops': float(entries['Sell Stops'].get()),
            'buy_limits': float(entries['Buy Limits'].get()),
            'sell_limits': float(entries['Sell Limits'].get()),
            'profit_ratio_buyers': float(entries['Profit Ratio - Buyers'].get()),
            'profit_ratio_sellers': float(entries['Profit Ratio - Sellers'].get())
        }

        global last_signals
        last_signals = detect_retail_signals(data)

        output_text.delete(1.0, tk.END)
        for s in last_signals:
            output_text.insert(tk.END, f"• {s}\n")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers.")

def save_pdf():
    if not last_signals:
        messagebox.showwarning("No Data", "Run the analysis before saving.")
        return

    filepath = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")],
        title="Save analysis report as PDF"
    )

    if not filepath:
        return

    try:
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter

        # Title and timestamp
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 50, "Retail Order Book Signal Analysis")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, f"Generated on: {timestamp}")

        # Prepare raw data table
        data = [["Field", "Value (%)"]]
        for field in entries:
            val = entries[field].get()
            data.append([field, val])

        # Table styling
        table = Table(data, colWidths=[200, 100])
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ])
        table.setStyle(style)

        # Calculate table position and wrap
        table_width, table_height = table.wrap(0, 0)
        x = 50
        y = height - 110 - table_height
        if y < 50:  # page break if not enough space
            c.showPage()
            y = height - 50 - table_height

        table.drawOn(c, x, y)

        # Move below table to write signals
        y -= 30

        # Draw signals header
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "📊 Signals:")
        y -= 20

        c.setFont("Helvetica", 11)
        for signal in last_signals:
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(60, y, f"• {signal}")
            y -= 15

        c.save()
        messagebox.showinfo("Saved", f"PDF report saved to:\n{filepath}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save PDF: {e}")

# GUI Setup
root = tk.Tk()
root.title("Retail Order Book Signal Detector")

fields = [
    'Buyer Share', 'Seller Share',
    'Buyers in Profit', 'Sellers in Profit',
    'Buyers in Loss', 'Sellers in Loss',
    'Buy Stops', 'Sell Stops',
    'Buy Limits', 'Sell Limits',
    'Profit Ratio - Buyers', 'Profit Ratio - Sellers'
]

entries = {}
for idx, field in enumerate(fields):
    label = tk.Label(root, text=field)
    label.grid(row=idx, column=0, padx=10, pady=5, sticky='e')
    entry = tk.Entry(root, width=10)
    entry.grid(row=idx, column=1, padx=10, pady=5)
    entries[field] = entry

analyze_button = tk.Button(root, text="🔍 Analyze", command=run_analysis, bg="lightblue")
analyze_button.grid(row=len(fields), column=0, pady=10)

save_button = tk.Button(root, text="💾 Save as PDF", command=save_pdf, bg="lightgreen")
save_button.grid(row=len(fields), column=1, pady=10)

output_text = tk.Text(root, height=10, width=50, wrap=tk.WORD, bg="#f0f0f0")
output_text.grid(row=len(fields)+1, columnspan=2, padx=10, pady=10)

last_signals = []

root.mainloop()
