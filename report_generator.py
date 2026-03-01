from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table

def generate_report(filename, savings, carbon):
    doc = SimpleDocTemplate(filename)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>AI Energy Optimization Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.5*inch))

    data = [
        ["Savings %", f"{savings}%"],
        ["CO₂ Reduction (kg)", f"{carbon}"]
    ]

    table = Table(data)
    elements.append(table)

    doc.build(elements)