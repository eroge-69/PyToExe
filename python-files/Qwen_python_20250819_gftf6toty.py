from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import random

def generate_worksheet(operation='addition', min_num=1, max_num=10, num_problems=48):
    # Create PDF document
    doc = SimpleDocTemplate("math_worksheet.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Header
    elements = []
    elements.append(Image('timer.png', 0.5*inch, 0.5*inch, hAlign='LEFT'))  # Add timer image
    elements.append(Paragraph("<para align=center><b>1 Minute Math: {}</b></para>".format(operation.capitalize()), styles['Title']))
    elements.append(Paragraph("Solve as many of the {} problems as you can in 1 minute".format(operation), styles['Normal']))
    
    # Problem grid
    problems = []
    for _ in range(num_problems):
        a = random.randint(min_num, max_num)
        b = random.randint(min_num, max_num)
        
        if operation == 'addition':
            prob = f"{a} + {b}"
        elif operation == 'subtraction':
            # Ensure result is positive
            while a < b:
                a = random.randint(min_num, max_num)
                b = random.randint(min_num, max_num)
            prob = f"{a} - {b}"
        elif operation == 'multiplication':
            prob = f"{a} × {b}"
        elif operation == 'division':
            # Ensure exact division
            while b == 0 or a % b != 0:
                a = random.randint(min_num, max_num)
                b = random.randint(min_num, max_num)
            prob = f"{a} ÷ {b}"
        
        problems.append(prob)
    
    # Format problems into a table
    data = [['Name:', 'Date:'], []]
    data += [[prob] for prob in problems]
    data += [['Score: ____ / {}'.format(num_problems)]]
    
    table = Table(data, colWidths=[4.5*inch])
    table.setStyle([
        ('BACKGROUND', (0,0), (-1,0), (0.9,0.9,0.9)),
        ('TEXTCOLOR', (0,0), (-1,0), (0,0,0)),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,2), (-1,-2), (1,1,1)),
    ])
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)

# Generate an addition worksheet
generate_worksheet(operation='addition', min_num=1, max_num=10, num_problems=48)