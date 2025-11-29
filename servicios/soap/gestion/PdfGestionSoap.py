import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class PdfGestionSoap:

    def __init__(self):
        # 👉 LINK DEL WSDL SOAP
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "PdfWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ---------------------------------------------------------
    # Normalización SOAP → dict
    # ---------------------------------------------------------
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "idPdf": d.get("IdPdf"),
            "idFactura": d.get("IdFactura"),
            "urlPdf": d.get("UrlPdf"),
            "estadoPdf": d.get("EstadoPdf"),
            "fechaModificacionPdf": fmt(d.get("FechaModificacionPdf")),
        }

    # ---------------------------------------------------------
    # LISTAR PDF
    # ---------------------------------------------------------
    def listar(self):
        try:
            r = self.client.service.ObtenerPdf()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar PDFs: {e}")

    # ---------------------------------------------------------
    # OBTENER POR ID
    # ---------------------------------------------------------
    def obtener_por_id(self, id_pdf):
        try:
            r = self.client.service.ObtenerPdfPorId(id_pdf)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener PDF por ID: {e}")

    # ---------------------------------------------------------
    # CREAR PDF
    # ---------------------------------------------------------
    def crear(self, dto):
        try:
            r = self.client.service.CrearPdf(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear PDF: {e}")

    # ---------------------------------------------------------
    # ACTUALIZAR PDF
    # ---------------------------------------------------------
    def actualizar(self, id_pdf, dto):
        try:
            r = self.client.service.ActualizarPdf(id_pdf, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar PDF: {e}")

    # ---------------------------------------------------------
    # ELIMINAR PDF (LÓGICO)
    # ---------------------------------------------------------
    def eliminar(self, id_pdf):
        try:
            return self.client.service.EliminarPdf(id_pdf)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar PDF: {e}")
