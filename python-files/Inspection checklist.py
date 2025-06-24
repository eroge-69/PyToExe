from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Register a more compact font
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))

def create_editable_checklist():
    c = canvas.Canvas("Truck-Inspection-Checklist.pdf", pagesize=letter)
    width, height = letter
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading2_style = styles['Heading2']
    normal_style = styles['BodyText']
    normal_style.fontName = 'DejaVuSans'
    normal_style.fontSize = 9
    
    # Page 1
    c.setFont("DejaVuSans-Bold", 16)
    c.drawCentredString(width/2, height-50, "Truck Inspection Checklist")
    
    # Truck Information Table
    truck_data = [
        ["Truck Make/Model", "________________________", "License Plate Number", "________________________"],
        ["Inspection Date", "________________________", "Inspector", "________________________"]
    ]
    truck_table = Table(truck_data, colWidths=[100, 150, 100, 150])
    truck_table.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'DejaVuSans', 9),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('SPAN', (0,0), (0,1)),
        ('SPAN', (2,0), (2,1))
    ]))
    truck_table.wrapOn(c, width, height)
    truck_table.drawOn(c, 50, height-120)
    
    # Instructions
    c.setFont("DejaVuSans-Bold", 10)
    c.drawString(50, height-170, "INSTRUCTIONS")
    c.setFont("DejaVuSans", 9)
    instruction_text = "This checklist is designed to ensure a thorough inspection of the truck. Carefully review each item and mark the corresponding checkbox for compliance or note any issues identified. Use the 'Notes/Issues' section to provide additional details and actions required."
    c.drawString(50, height-190, instruction_text[:90])
    c.drawString(50, height-205, instruction_text[90:])
    
    # Inspection Sections
    sections = [
        {
            "title": "1. EXTERIOR INSPECTION",
            "items": [
                "Check for any visible damage or dents on the body and frame.",
                "Ensure all lights (headlights, taillights, indicators) are functional.",
                "Check the condition of mirrors and ensure they are correctly adjusted.",
                "Verify the integrity of windshield and windows for cracks or chips.",
                "Inspect tires for wear, proper inflation, and secure lug nuts."
            ]
        },
        {
            "title": "2. ENGINE COMPARTMENT",
            "items": [
                "Check the engine oil level and condition.",
                "Inspect the coolant level and look for any leaks.",
                "Check power steering fluid and brake fluid levels.",
                "Verify the condition of belts and hoses.",
                "Ensure the battery is secure and connections are clean."
            ]
        },
        {
            "title": "3. BRAKE SYSTEM",
            "items": [
                "Test the functionality of parking brake and emergency brake.",
                "Check brake pedal for responsiveness and abnormal noises.",
                "Inspect brake pads, rotors, and drums for wear.",
                "Verify brake fluid level and condition.",
                "Check for any signs of brake fluid leaks."
            ]
        }
    ]
    
    y_position = height-250
    for section in sections:
        c.setFont("DejaVuSans-Bold", 12)
        c.drawString(50, y_position, section["title"])
        y_position -= 20
        
        c.setFont("DejaVuSans", 9)
        for item in section["items"]:
            c.drawString(60, y_position, item)
            # Create checkboxes
            c.rect(450, y_position-3, 12, 12)  # Yes
            c.drawString(465, y_position, "Yes")
            c.rect(500, y_position-3, 12, 12)  # No
            c.drawString(515, y_position, "No")
            c.rect(540, y_position-3, 12, 12)  # NA
            c.drawString(555, y_position, "NA")
            y_position -= 20
        
        # Action required
        c.drawString(60, y_position, "Action required, if any")
        c.line(180, y_position+3, 550, y_position+3)
        y_position -= 30
    
    c.showPage()
    
    # Page 2
    sections = [
        {
            "title": "4. STEERING AND SUSPENSION",
            "items": [
                "Check steering wheel for excessive play or tightness.",
                "Inspect suspension components for damage or wear.",
                "Ensure shock absorbers and struts are in good condition.",
                "Test the alignment and steering responsiveness.",
                "Check for any unusual noises when turning."
            ]
        },
        {
            "title": "5. TRANSMISSION AND DRIVETRAIN",
            "items": [
                "Test the functionality of the transmission in all gears.",
                "Check for any signs of transmission fluid leaks.",
                "Verify the condition of the driveshaft and universal joints.",
                "Test the engagement and release of the clutch (if applicable).",
                "Inspect the condition of the differential and axle seals."
            ]
        },
        {
            "title": "6. ELECTRICAL SYSTEM",
            "items": [
                "Check all dashboard gauges and warning lights.",
                "Test the functionality of turn signals and hazard lights.",
                "Ensure all interior lights (dome light, cabin lights) are operational.",
                "Verify the condition of the battery and charging system.",
                "Test the functionality of the horn."
            ]
        },
        {
            "title": "7. INTERIOR INSPECTION",
            "items": [
                "Check the condition of the seats, seatbelts, and adjusters.",
                "Inspect the condition of the floor mats and carpeting.",
                "Ensure all controls (air conditioning, radio, etc.) are working.",
                "Verify the functionality of windshield wipers and washers.",
                "Check for any signs of leaks inside the cabin."
            ]
        }
    ]
    
    y_position = height-50
    for section in sections:
        c.setFont("DejaVuSans-Bold", 12)
        c.drawString(50, y_position, section["title"])
        y_position -= 20
        
        c.setFont("DejaVuSans", 9)
        for item in section["items"]:
            c.drawString(60, y_position, item)
            # Create checkboxes
            c.rect(450, y_position-3, 12, 12)  # Yes
            c.drawString(465, y_position, "Yes")
            c.rect(500, y_position-3, 12, 12)  # No
            c.drawString(515, y_position, "No")
            c.rect(540, y_position-3, 12, 12)  # NA
            c.drawString(555, y_position, "NA")
            y_position -= 20
        
        # Action required
        c.drawString(60, y_position, "Action required, if any")
        c.line(180, y_position+3, 550, y_position+3)
        y_position -= 30
    
    c.showPage()
    
    # Page 3
    # Safety Equipment
    c.setFont("DejaVuSans-Bold", 12)
    c.drawString(50, height-50, "8. SAFETY EQUIPMENT")
    
    safety_items = [
        "Ensure the truck is equipped with a proper first aid kit.",
        "Check for the presence of reflective triangles or warning flares.",
        "Verify the condition and accessibility of a fire extinguisher.",
        "Ensure the truck has a spare tire, jack, and lug wrench.",
        "Check for the presence of an emergency escape tool."
    ]
    
    y_position = height-80
    c.setFont("DejaVuSans", 9)
    for item in safety_items:
        c.drawString(60, y_position, item)
        # Create checkboxes
        c.rect(450, y_position-3, 12, 12)  # Yes
        c.drawString(465, y_position, "Yes")
        c.rect(500, y_position-3, 12, 12)  # No
        c.drawString(515, y_position, "No")
        c.rect(540, y_position-3, 12, 12)  # NA
        c.drawString(555, y_position, "NA")
        y_position -= 25
    
    # Action required
    c.drawString(60, y_position, "Action required, if any")
    c.line(180, y_position+3, 550, y_position+3)
    y_position -= 40
    
    # Notes/Issues
    c.setFont("DejaVuSans-Bold", 12)
    c.drawString(50, y_position, "NOTES/ISSUES:")
    c.setFont("DejaVuSans", 9)
    c.rect(50, y_position-150, 510, 130, fill=0)
    
    # Approval Section
    y_position -= 180
    c.setFont("DejaVuSans-Bold", 12)
    c.drawCentredString(width/2, y_position, "STATEMENT OF APPROVAL")
    c.setFont("DejaVuSans", 10)
    c.drawCentredString(width/2, y_position-20, "I hereby certify that I have conducted the above inspection and that the information provided is accurate to the best of my knowledge.")
    
    # Inspector signature
    c.drawString(50, y_position-60, "Inspector's Name:")
    c.line(130, y_position-60, 300, y_position-60)
    c.drawString(320, y_position-60, "Signature:")
    c.line(380, y_position-60, 550, y_position-60)
    c.drawString(50, y_position-80, "Date:")
    c.line(80, y_position-80, 200, y_position-80)
    
    # Approved by
    c.drawString(50, y_position-120, "Approved By:")
    c.drawString(50, y_position-140, "Name:")
    c.line(90, y_position-140, 260, y_position-140)
    c.drawString(280, y_position-140, "Signature:")
    c.line(340, y_position-140, 510, y_position-140)
    c.drawString(50, y_position-160, "Date:")
    c.line(80, y_position-160, 200, y_position-160)
    
    # Footer
    c.setFont("DejaVuSans", 8)
    c.drawString(50, 50, "Inspection template by:")
    c.drawString(50, 40, "Digitize your Audits & Inspections through Safetymint")
    c.drawString(50, 30, "Get started with a free trial at www.safetymint.com")
    
    c.save()

if __name__ == "__main__":
    create_editable_checklist()
    print("Editable PDF checklist created: Truck-Inspection-Checklist.pdf")