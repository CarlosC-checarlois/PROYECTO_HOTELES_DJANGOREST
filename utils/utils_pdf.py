# webapp/utils_pdf.py
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime



def generar_pdf_factura_html(id_factura: int, datos: dict) -> bytes:
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M')

    habitaciones = datos.get("habitaciones") or []
    reserva = datos.get("id_reserva") or "—"
    cliente = datos.get("cliente") or "—"
    fecha_inicio = datos.get("fecha_inicio") or "—"
    fecha_fin = datos.get("fecha_fin") or "—"
    total_general = round(float(datos.get("total") or 0), 2)

    filas_items = ""
    total_subtotal = 0.0
    total_impuestos = 0.0
    total_descuentos = 0.0

    for h in habitaciones:
        habitacion = h.get("habitacion") or ""
        capacidad = h.get("capacidad") or 1
        subtotal = round(float(h.get("subtotal") or 0), 2)
        impuestos = round(float(h.get("impuestos") or 0), 2)

        total_subtotal += subtotal
        total_impuestos += impuestos

        # ÍTEM HABITACIÓN
        filas_items += f"""
        <tr>
            <td>Habitación {habitacion}</td>
            <td align="center">{capacidad}</td>
            <td align="right">${subtotal:.2f}</td>
            <td align="right">${subtotal:.2f}</td>
        </tr>
        """

        # ÍTEMS DESCUENTOS
        descuento_hab = 0.0
        descuentos = h.get("descuentos") or []

        for d in descuentos:
            nombre = d.get("nombre") or "Descuento"
            monto = round(float(d.get("monto") or 0), 2)
            descuento_hab += monto
            filas_items += f"""
            <tr>
                <td style="padding-left:15px;">Descuento - {nombre}</td>
                <td align="center">1</td>
                <td align="right">-${monto:.2f}</td>
                <td align="right">-${monto:.2f}</td>
            </tr>
            """

        total_descuentos += descuento_hab

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>

body {{
    font-family: Arial, sans-serif;
    font-size: 11px;
    max-width: 950px;
    margin: 10px auto;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th {{
    background: #1f4ed8;
    color: white;
    padding: 6px;
    border: 1px solid #000;
}}

td {{
    border: 1px solid #000;
    padding: 4px 6px;
}}

.header {{
    margin-bottom: 6px;
}}

.header td {{
    border: none;
}}

.title {{
    font-size: 22px;
    font-weight: bold;
    color: #1f4ed8;
}}

.company {{
    font-size: 10px;
    color: #666;
}}

.invoice {{
    text-align: right;
}}

.invoice-box {{
    border: 2px solid #1f4ed8;
    display: inline-block;
    padding: 6px 10px;
    font-weight: bold;
    font-size: 13px;
}}

.block {{
    margin-top: 6px;
}}

.summary {{
    width: 35%;
    float: right;
    margin-top: 6px;
}}

.summary td {{
    border: 1px solid #000;
}}

.summary tr:last-child td {{
    font-weight: bold;
    border-top: 2px solid #000;
}}

.total-box {{
    margin-top: 8px;
    border: 3px solid #000;
    text-align: right;
    font-size: 16px;
    font-weight: bold;
    padding: 8px;
}}

.footer {{
    margin-top: 10px;
    text-align: center;
    font-size: 10px;
    color: #777;
}}

</style>
</head>

<body>

<table class="header">
<tr>
<td width="60%">
    <div class="title">HOTEL LO PROPIO</div>
    <div class="company">
        Guayaquil - Ecuador<br>
        contacto@hotellopropio.ec | +593 0999999999
    </div>
</td>
<td width="40%" class="invoice">
    <div class="invoice-box">FACTURA Nº {id_factura}</div>
    <div>Fecha: {fecha}</div>
</td>
</tr>
</table>

<table class="block">
<tr>
<td width="60%">
<b>FACTURAR A:</b><br>
Cliente: {cliente}<br>
Reserva: {reserva}
</td>
<td width="40%">
<b>ESTADÍA</b><br>
Ingreso: {fecha_inicio}<br>
Salida: {fecha_fin}
</td>
</tr>
</table>

<br>

<table>
<tr>
<th>Descripción</th>
<th>Cantidad</th>
<th>Precio unitario</th>
<th>Monto</th>
</tr>

{filas_items}

</table>

<table class="summary">
<tr><td>Subtotal</td><td align="right">${total_subtotal:.2f}</td></tr>
<tr><td>Impuestos</td><td align="right">${total_impuestos:.2f}</td></tr>
<tr><td>Descuentos</td><td align="right">-${total_descuentos:.2f}</td></tr>
<tr><td>Total</td><td align="right">${total_general:.2f}</td></tr>
</table>

<div style="clear:both;"></div>

<div class="total-box">
TOTAL PAGADO: ${total_general:.2f}
</div>

<div class="footer">
Documento generado automáticamente.<br>
Gracias por confiar en HOTEL LO PROPIO.
</div>

</body>
</html>
"""

    result = BytesIO()
    pdf = pisa.CreatePDF(html, dest=result)

    if pdf.err:
        raise Exception("Error generando PDF")

    return result.getvalue()


