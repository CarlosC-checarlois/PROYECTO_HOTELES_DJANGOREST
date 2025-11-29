import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class PaisGestionSoap:

    def __init__(self):
        # 👉 Asegúrate de que el link sea exactamente este:
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "PaisWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ========================================================
    # Normalizador de respuesta SOAP → dict
    # ========================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(x):
            return x.isoformat() if x else None

        return {
            "idPais": d.get("IdPais"),
            "nombrePais": d.get("NombrePais"),
            "estadoPais": d.get("EstadoPais"),
            "fechaModificacionPais": fmt(d.get("FechaModificacionPais")),
        }

    # ========================================================
    # LISTAR PAISES
    # ========================================================
    def listar(self):
        try:
            r = self.client.service.ObtenerPais()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar países: {e}")

    # ========================================================
    # OBTENER POR ID
    # ========================================================
    def obtener_por_id(self, id_pais):
        try:
            r = self.client.service.ObtenerPaisPorId(id_pais)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener país por ID: {e}")

    # ========================================================
    # CREAR PAÍS
    # ========================================================
    def crear(self, dto):
        try:
            r = self.client.service.CrearPais(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear país: {e}")

    # ========================================================
    # ACTUALIZAR PAÍS
    # ========================================================
    def actualizar(self, id_pais, dto):
        try:
            r = self.client.service.ActualizarPais(id_pais, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar país: {e}")

    # ========================================================
    # ELIMINAR PAÍS (LÓGICO)
    # ========================================================
    def eliminar(self, id_pais):
        try:
            return self.client.service.EliminarPais(id_pais)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar país: {e}")
