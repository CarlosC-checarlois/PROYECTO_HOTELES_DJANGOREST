import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class MetodoPagoGestionSoap:

    def __init__(self):
        # 👉 Asegúrate de reemplazar por el WSDL verdadero una vez publicado:
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "MetodoPagoWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ========================================================
    # Normalización de respuesta SOAP → dict Python
    # ========================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(x):
            return x.isoformat() if x else None

        return {
            "idMetodoPago": d.get("IdMetodoPago"),
            "nombreMetodoPago": d.get("NombreMetodoPago"),
            "estadoMetodoPago": d.get("EstadoMetodoPago"),
            "fechaModificacionMetodoPago": fmt(d.get("FechaModificacionMetodoPago")),
        }

    # ========================================================
    # LISTAR MÉTODOS DE PAGO
    # ========================================================
    def listar(self):
        try:
            r = self.client.service.ObtenerMetodoPago()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar métodos de pago: {e}")

    # ========================================================
    # OBTENER POR ID
    # ========================================================
    def obtener_por_id(self, id_metodo):
        try:
            r = self.client.service.ObtenerMetodoPagoPorId(id_metodo)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener método por ID: {e}")

    # ========================================================
    # CREAR MÉTODO DE PAGO
    # ========================================================
    def crear(self, dto):
        try:
            r = self.client.service.CrearMetodoPago(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear método de pago: {e}")

    # ========================================================
    # ACTUALIZAR MÉTODO DE PAGO
    # ========================================================
    def actualizar(self, id_metodo, dto):
        try:
            r = self.client.service.ActualizarMetodoPago(id_metodo, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar método de pago: {e}")

    # ========================================================
    # ELIMINAR MÉTODO DE PAGO (LÓGICO)
    # ========================================================
    def eliminar(self, id_metodo):
        try:
            return self.client.service.EliminarMetodoPago(id_metodo)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar método de pago: {e}")
