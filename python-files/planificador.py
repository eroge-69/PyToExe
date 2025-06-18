
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# Ruta al escritorio del usuario
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
file_name = os.path.join(desktop_path, "planificador_viola_tesina.pdf")

c = canvas.Canvas(file_name, pagesize=letter)
width, height = letter

# Título
c.setFont("Helvetica-Bold", 16)
c.setFillColor(colors.darkgreen)
c.drawCentredString(width / 2, height - 50, "📅 Planificador Semanal - Viola + Tesina")

# Fecha
c.setFont("Helvetica", 10)
c.setFillColor(colors.black)
c.drawRightString(width - 40, height - 40, "Semana de: ____________________")

# Horario
c.setFont("Helvetica-Bold", 12)
c.drawString(50, height - 80, "🗓 Horario Semanal")

days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
blocks = [
    "08:30 - 09:30 Desayuno y estiramiento",
    "09:30 - 10:30 Tesina - Escritura/Corrección",
    "10:45 - 12:00 Práctica de Viola - Técnica y Obra 1",
    "13:00 - 14:30 Práctica de Viola - Obra 2 / Repaso",
    "16:00 - 17:00 Tesina - Lectura o revisión",
    "19:00 - 21:00 Tiempo libre / autocuidado"
]

x_start = 50
y_start = height - 110
cell_width = 70
cell_height = 30

c.setFont("Helvetica-Bold", 9)
for i, day in enumerate(days):
    c.drawString(x_start + cell_width * (i + 1) + 5, y_start, day)

c.setFont("Helvetica", 8)
for j, block in enumerate(blocks):
    y = y_start - cell_height * (j + 1)
    c.drawString(x_start, y + 10, block)
    for i in range(len(days)):
        c.rect(x_start + cell_width * (i + 1), y, cell_width, cell_height)

# Metas
y -= 40
c.setFont("Helvetica-Bold", 12)
c.drawString(50, y, "🎯 Metas de la Semana")
c.setFont("Helvetica", 10)
c.drawString(60, y - 20, "- Tesina: ___________________________________________")
c.drawString(60, y - 40, "- Viola: ____________________________________________")
c.drawString(60, y - 60, "- Autocuidado: ______________________________________")

# Seguimiento emocional
y -= 100
c.setFont("Helvetica-Bold", 12)
c.drawString(50, y, "💚 Seguimiento Diario")
c.setFont("Helvetica", 9)
for i, day in enumerate(days):
    c.drawString(60, y - 20 - i*20, f"{day}: ¿Dormí bien? ____  ¿Toqué? ____  ¿Tesina? ____  ¿Me cuidé? ____")

# Frase final
c.setFont("Helvetica-Oblique", 10)
c.setFillColor(colors.darkgreen)
c.drawCentredString(width / 2, 40, "“Avanzar poco a poco también es avanzar. Sé paciente contigo.”")

c.save()
print("✅ PDF creado en tu escritorio como 'planificador_viola_tesina.pdf'")
