from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO


def generar_pdf_factura(id_factura: int, datos: dict) -> bytes:
    """
    Genera un PDF sencillo para la factura usando reportlab.
    Retorna los bytes del PDF.
    """

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"FACTURA #{id_factura}")
    c.drawString(50, 730, f"Reserva: {datos.get('id_reserva')}")
    c.drawString(50, 710, f"Cliente: {datos.get('cliente')}")
    c.drawString(50, 690, f"Total: ${datos.get('total')}")

    c.drawString(50, 650, "Gracias por su reserva en HOTEL GENÉRICO.")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()
