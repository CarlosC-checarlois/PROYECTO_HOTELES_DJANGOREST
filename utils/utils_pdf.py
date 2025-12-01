# webapp/utils_pdf.py
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime


def generar_pdf_factura_html(id_factura: int, datos: dict) -> bytes:
    """
    Genera una factura en PDF con diseño.
    Compatible 100% con xhtml2pdf.
    """

    fecha = datetime.now().strftime('%d/%m/%Y %H:%M')

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 12px;
                color: #333;
            }}

            .container {{
                width: 100%;
                padding: 20px;
            }}

            .header {{
                border-bottom: 2px solid #1d4ed8;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}

            .header h1 {{
                color: #1d4ed8;
                margin: 0;
            }}

            .header .info {{
                font-size: 11px;
                color: #555;
            }}

            .section {{
                margin-bottom: 20px;
            }}

            .section-title {{
                font-weight: bold;
                background: #f3f4f6;
                padding: 5px 10px;
            }}

            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}

            .data-table th {{
                background: #1d4ed8;
                color: white;
                padding: 8px;
                border: 1px solid #ccc;
            }}

            .data-table td {{
                padding: 8px;
                border: 1px solid #ccc;
                text-align: center;
            }}

            .total-box {{
                margin-top: 20px;
                text-align: right;
                font-size: 14px;
                font-weight: bold;
            }}

            .footer {{
                margin-top: 40px;
                border-top: 1px dashed #ccc;
                padding-top: 10px;
                text-align: center;
                font-size: 10px;
                color: #555;
            }}

        </style>
    </head>
    <body>

        <div class="container">

            <div class="header">
                <h1>HOTEL LO PROPIO GUAYAS - GUAYAQUIL - ECUADOR</h1>
                <div class="info">
                    FACTURA ELECTRÓNICA<br>
                    Fecha de emisión: {fecha}
                </div>
            </div>

            <div class="section">
                <div class="section-title">Datos del Cliente</div>
                <table class="data-table">
                    <tr>
                        <th>Factura</th>
                        <th>Reserva</th>
                        <th>Cliente</th>
                    </tr>
                    <tr>
                        <td>#{id_factura}</td>
                        <td>{datos.get("id_reserva")}</td>
                        <td>{datos.get("cliente")}</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <div class="section-title">Detalle de Cobro</div>
                <table class="data-table">
                    <tr>
                        <th>Concepto</th>
                        <th>Total</th>
                    </tr>
                    <tr>
                        <td>Servicio de Hospedaje</td>
                        <td>${datos.get("total")}</td>
                    </tr>
                </table>
            </div>

            <div class="total-box">
                TOTAL A PAGAR: ${datos.get("total")}
            </div>

            <div class="footer">
                Este documento fue generado automáticamente.<br>
                Gracias por confiar en HOTEL GENÉRICO.
            </div>

        </div>

    </body>
    </html>
    """

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        raise Exception("Error al generar PDF vía HTML")

    return result.getvalue()
