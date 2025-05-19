from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

def txt_to_pdf(input_txt_path: str, output_pdf_path: str):
    print(f"✅ Text file PAth: {input_txt_path}")
    if not os.path.exists(input_txt_path):
        raise FileNotFoundError(f"Text file not found: {input_txt_path}")
    
    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin  # start near the top

    with open(input_txt_path, 'r', encoding='utf-8') as file:
        for line in file:
            if y <= margin:  # new page if not enough space
                c.showPage()
                y = height - margin
            c.drawString(margin, y, line.strip())
            y -= 14  # line spacing

    c.save()
    print(f"✅ Text file converted to PDF: {output_pdf_path}")
    return output_pdf_path
    
    

