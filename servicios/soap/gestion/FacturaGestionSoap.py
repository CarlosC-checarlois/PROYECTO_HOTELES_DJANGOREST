import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault

class FacturaGestionSoap:

    def __init__(self):
        # WSDL PUBLICADO EN AZURE
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "FacturaWS.asmx?wsdl"
        )

        # Desactivar validación SSL (Azure)
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ==========================================================
    # NORMALIZAR → Parámetros idénticos a REST
    # ==========================================================
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "idFactura": d.get("IdFactura"),
            "idReserva": d.get("IdReserva"),
            "subtotal": d.get("Subtotal"),
            "descuento": d.get("Descuento"),
            "impuesto": d.get("Impuesto"),
            "total": d.get("Total"),
            "urlPdf": d.get("UrlPdf"),
        }

    # ==========================================================
    # LISTAR FACTURAS
    # ==========================================================
    def listar(self):
        try:
            result = self.client.service.ObtenerFacturas()
            result = serialize_object(result)
            return [self._normalize(item) for item in result]
        except Fault as e:
            raise Exception(f"Error SOAP al listar facturas: {e}")

    # ==========================================================
    # OBTENER POR ID
    # ==========================================================
    def obtener_por_id(self, id_factura):
        try:
            result = self.client.service.ObtenerFacturaPorId(id_factura)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener factura {id_factura}: {e}")

    # ==========================================================
    # CREAR FACTURA
    # ==========================================================
    def crear(self, dto):
        try:
            result = self.client.service.CrearFactura(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear factura: {e}")

    # ==========================================================
    # ACTUALIZAR FACTURA
    # ==========================================================
    def actualizar(self, id_factura, dto):
        try:
            result = self.client.service.ActualizarFactura(id_factura, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar factura {id_factura}: {e}")

    # ==========================================================
    # ELIMINAR FACTURA
    # ==========================================================
    def eliminar(self, id_factura):
        try:
            return self.client.service.EliminarFactura(id_factura)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar factura {id_factura}: {e}")
