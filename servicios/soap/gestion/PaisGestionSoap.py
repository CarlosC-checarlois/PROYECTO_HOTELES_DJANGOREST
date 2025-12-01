import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class PaisGestionSoap:

    def __init__(self):

        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/PaisWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()
        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ========================================================
    # NORMALIZAR SOAP → REST-like dict
    # ========================================================
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        fecha = d.get("FechaModificacionPais")
        if hasattr(fecha, "isoformat"):
            fecha = fecha.isoformat()

        return {
            "IdPais": d.get("IdPais"),
            "NombrePais": d.get("NombrePais"),
            "EstadoPais": d.get("EstadoPais"),
            "FechaModificacionPais": fecha,
        }

    # ========================================================
    # DESNORMALIZAR REST-like → SOAP DTO
    # ========================================================
    def _denormalize(self, id_pais, nombre_pais, estado_pais):
        return {
            "IdPais": id_pais,
            "NombrePais": nombre_pais,
            "EstadoPais": estado_pais,
            "FechaModificacionPais": datetime.now(),
        }

    # ========================================================
    # GET → Lista de países
    # ========================================================
    def obtener_paises(self):
        try:
            result = self.client.service.ObtenerPais()
            result = serialize_object(result)

            if isinstance(result, list):
                return [self._normalize(x) for x in result]

            return []
        except Fault as e:
            raise Exception(f"Error SOAP al obtener países: {e}")

    # ========================================================
    # GET → País por ID
    # ========================================================
    def obtener_pais_por_id(self, id_pais):
        try:
            result = self.client.service.ObtenerPaisPorId(id_pais)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener país por ID: {e}")

    # ========================================================
    # POST → Crear país 
    # ========================================================
    def crear_pais(self, id_pais, nombre_pais, estado_pais=True):
        dto = self._denormalize(id_pais, nombre_pais, estado_pais)

        try:
            result = self.client.service.CrearPais(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear país: {e}")

    # ========================================================
    # PUT → Actualizar país 
    # ========================================================
    def actualizar_pais(self, id_pais, nombre_pais, estado_pais):
        dto = self._denormalize(id_pais, nombre_pais, estado_pais)

        try:
            result = self.client.service.ActualizarPais(id_pais, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar país: {e}")

    # ========================================================
    # DELETE → Eliminación lógica
    # ========================================================
    def eliminar_pais(self, id_pais):
        try:
            return self.client.service.EliminarPais(id_pais)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar país: {e}")

