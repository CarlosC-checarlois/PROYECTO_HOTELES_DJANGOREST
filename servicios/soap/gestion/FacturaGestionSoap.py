import requests
from datetime import datetime
from decimal import Decimal

from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class FacturaGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/FacturaWS.asmx?wsdl"

        # SSL bypass (Azure)
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ==========================================================
    # NORMALIZAR → Igual que REST, pero convirtiendo Decimal
    # ==========================================================
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        def fix(v):
            return float(v) if isinstance(v, Decimal) else v

        return {
            "IdFactura": d.get("IdFactura"),
            "IdReserva": d.get("IdReserva"),
            "Subtotal": fix(d.get("Subtotal")),
            "Descuento": fix(d.get("Descuento")),
            "Impuesto": fix(d.get("Impuesto")),
            "Total": fix(d.get("Total")),
            "UrlPdf": d.get("UrlPdf"),
            "FechaEmision": (
                d.get("FechaEmision").isoformat()
                if d.get("FechaEmision") else None
            )
        }

    # ==========================================================
    # DESNORMALIZAR → Construir DTO idéntico a REST
    # ==========================================================
    def _denormalize(self, id_factura, id_reserva, subtotal, descuento, impuesto, total, url_pdf):
        return {
            "IdFactura": id_factura,
            "IdReserva": id_reserva,
            "Subtotal": subtotal,
            "Descuento": descuento,
            "Impuesto": impuesto,
            "Total": total,
            "UrlPdf": url_pdf,
            "FechaEmision": datetime.now()
        }

    # ==========================================================
    # GET → obtener_facturas
    # ==========================================================
    def obtener_facturas(self):
        try:
            result = self.client.service.ObtenerFacturas()
            data = serialize_object(result)

            if isinstance(data, list):
                return [self._normalize(x) for x in data]

            if isinstance(data, dict):
                for k in data:
                    if isinstance(data[k], list):
                        return [self._normalize(x) for x in data[k]]

            return []
        except Fault as e:
            raise Exception(f"Error SOAP al listar facturas: {e}")

    # ==========================================================
    # GET → obtener_por_id
    # ==========================================================
    def obtener_por_id(self, id_factura):
        try:
            result = self.client.service.ObtenerFacturaPorId(id_factura)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener factura {id_factura}: {e}")

    # ==========================================================
    # POST → crear_factura
    # ==========================================================
    def crear_factura(self, id_factura, id_reserva, subtotal=None, descuento=None,
                      impuesto=None, total=None, url_pdf=None):

        dto = self._denormalize(id_factura, id_reserva, subtotal, descuento, impuesto, total, url_pdf)

        try:
            result = self.client.service.CrearFactura(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear factura: {e}")

    # ==========================================================
    # PUT → actualizar_factura
    # ==========================================================
    def actualizar_factura(self, id_factura, id_reserva, subtotal=None, descuento=None,
                           impuesto=None, total=None, url_pdf=None):

        dto = self._denormalize(id_factura, id_reserva, subtotal, descuento, impuesto, total, url_pdf)

        try:
            result = self.client.service.ActualizarFactura(id_factura, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar factura {id_factura}: {e}")

    # ==========================================================
    # DELETE → eliminar_factura
    # ==========================================================
    def eliminar_factura(self, id_factura):
        try:
            return self.client.service.EliminarFactura(id_factura)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar factura {id_factura}: {e}")

