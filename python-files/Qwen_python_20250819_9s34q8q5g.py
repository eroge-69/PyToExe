import sys
import os
import random
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import argparse

def resource_path(relative_path):
    """Get absolute path to resource for PyInstaller compatibility"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def generate_worksheet(operation, min_num, max_num, num_problems, output_file):
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create embedded timer graphic (base64 encoded)
    timer_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 6v6l4 2"/>
        <circle cx="12" cy="12" r="1" fill="black"/>
    </svg>"""
    
    # Convert SVG to PNG in-memory
    from io import BytesIO
    from reportlab.graphics import renderPM
    from svglib.svglib import svg2rlg
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
        tmp.write(timer_svg.encode())
        tmp_path = tmp.name
    
    drawing = svg2rlg(tmp_path)
    os.unlink(tmp_path)
    
    img_buffer = BytesIO()
    renderPM.drawToFile(drawing, img_buffer, fmt="PNG")
    img_buffer.seek(0)
    
    # Header
    elements = []
    elements.append(Paragraph(f'<img src="{img_buffer}" width="30" height="30" valign="middle"/>', styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>1 Minute Math: {operation.capitalize()}</b>", styles['Title']))
    elements.append(Paragraph(f"Solve as many of the {num_problems} problems as you can in 1 minute", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Problem grid
    problems = []
    for _ in range(num_problems):
        a = random.randint(min_num, max_num)
        b = random.randint(min_num, max_num)
        
        if operation == 'addition':
            prob = f"{a} + {b}"
        elif operation == 'subtraction':
            while a < b:
                a = random.randint(min_num, max_num)
                b = random.randint(min_num, max_num)
            prob = f"{a} - {b}"
        elif operation == 'multiplication':
            prob = f"{a} × {b}"
        elif operation == 'division':
            while b == 0 or a % b != 0:
                a = random.randint(min_num, max_num)
                b = random.randint(min_num, max_num)
            prob = f"{a} ÷ {b}"
        
        problems.append([prob])
    
    # Format problems into a table
    data = [
        ['Name:', 'Date:'],
        [''] * 2,
        *problems,
        [f'Score: ____ / {num_problems}']
    ]
    
    table = Table(data, colWidths=[2.25*inch, 2.25*inch])
    table.setStyle([
        ('GRID', (0,0), (-1,-1), 0.5, 'black'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('SPAN', (0,1), (1,1)),  # Merge header row
        ('BACKGROUND', (0,0), (1,0), (0.9, 0.9, 0.9)),
        ('BACKGROUND', (0,-1), (1,-1), (0.9, 0.9, 0.9))
    ])
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)

def main():
    parser = argparse.ArgumentParser(description='Generate math worksheets')
    parser.add_argument('--operation', choices=['addition', 'subtraction', 'multiplication', 'division'], 
                        default='addition', help='Type of math operation')
    parser.add_argument('--min', type=int, default=1, help='Minimum number')
    parser.add_argument('--max', type=int, default=10, help='Maximum number')
    parser.add_argument('--problems', type=int, default=48, help='Number of problems')
    parser.add_argument('--output', default='math_worksheet.pdf', help='Output PDF filename')
    
    args = parser.parse_args()
    
    generate_worksheet(
        args.operation,
        args.min,
        args.max,
        args.problems,
        args.output
    )
    
    print(f"✅ Worksheet generated: {os.path.abspath(args.output)}")
    if getattr(sys, 'frozen', False):
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()