from __future__ import annotations

import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class PdfGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/PdfWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ==========================================================
    # NORMALIZAR → SOAP → REST dict
    # ==========================================================
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        fecha = d.get("FechaModificacionPdf")
        if hasattr(fecha, "isoformat"):
            fecha = fecha.isoformat()

        return {
            "IdPdf": d.get("IdPdf"),
            "IdFactura": d.get("IdFactura"),
            "UrlPdf": d.get("UrlPdf"),
            "EstadoPdf": d.get("EstadoPdf"),
            "FechaModificacionPdf": fecha
        }

    # ==========================================================
    # DESNORMALIZAR → REST → DTO SOAP
    # ==========================================================
    def _denormalize(self, id_pdf, id_factura, url_pdf, estado_pdf):
        return {
            "IdPdf": id_pdf,
            "IdFactura": id_factura,
            "UrlPdf": url_pdf,
            "EstadoPdf": estado_pdf,
            "FechaModificacionPdf": datetime.now()
        }

    # ==========================================================
    # GET → Obtener lista completa  
    # ==========================================================
    def obtener_pdfs(self):
        try:
            result = self.client.service.ObtenerPdf()
            data = serialize_object(result)

            # si es lista
            if isinstance(data, list):
                return [self._normalize(x) for x in data]

            # si viene como dict con lista dentro
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list):
                        return [self._normalize(x) for x in v]

            return []

        except Fault as e:
            raise Exception(f"SOAP Error al obtener PDFs: {e}")

    # ==========================================================
    # GET → Obtener por ID  
    # ==========================================================
    def obtener_pdf_por_id(self, id_pdf: int):
        if not id_pdf:
            raise ValueError("ID_PDF es obligatorio.")

        try:
            result = self.client.service.ObtenerPdfPorId(id_pdf)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener PDF por ID: {e}")

    # ==========================================================
    # POST → Crear PDF  
    # ==========================================================
    def crear_pdf(self, id_pdf: int, id_factura: int | None, url_pdf: str, estado_pdf: bool = True):
        dto = self._denormalize(id_pdf, id_factura, url_pdf, estado_pdf)

        try:
            result = self.client.service.CrearPdf(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"SOAP Error al crear PDF: {e}")

    # ==========================================================
    # PUT → Actualizar PDF  
    # ==========================================================
    def actualizar_pdf(self, id_pdf: int, id_factura: int | None, url_pdf: str, estado_pdf: bool):
        dto = self._denormalize(id_pdf, id_factura, url_pdf, estado_pdf)

        try:
            result = self.client.service.ActualizarPdf(id_pdf, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar PDF: {e}")

    # ==========================================================
    # DELETE → Eliminación lógica  
    # ==========================================================
    def eliminar_pdf(self, id_pdf: int):
        if not id_pdf:
            raise ValueError("ID_PDF es obligatorio.")

        try:
            return self.client.service.EliminarPdf(id_pdf)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar PDF: {e}")
