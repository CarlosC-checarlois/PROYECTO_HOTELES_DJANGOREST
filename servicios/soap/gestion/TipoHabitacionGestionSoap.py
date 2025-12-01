import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class TipoHabitacionGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/TipoHabitacionWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

        # Tipo real SOAP (DTO fuerte)
        self.dto_type = self.client.get_type('ns0:TipoHabitacionDto')  # si falla, cambia ns0 por tns o ns1

    # ========================================================
    # SOAP DTO -> dict tipo REST
    # ========================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        fecha = d.get("FechaModificacionTipoHabitacion")
        if hasattr(fecha, "isoformat"):
            fecha = fecha.isoformat()

        return {
            "IdTipoHabitacion": d.get("IdTipoHabitacion"),
            "NombreHabitacion": d.get("NombreHabitacion"),
            "EstadoTipoHabitacion": d.get("EstadoTipoHabitacion"),
            "FechaModificacionTipoHabitacion": fecha,
        }

    # ========================================================
    # dict REST -> SOAP DTO real
    # ========================================================
    def _denormalize(self, tipo_dto: dict, id_tipo: int = 0):

        return self.dto_type(
            IdTipoHabitacion=id_tipo,
            NombreHabitacion=tipo_dto.get("NombreHabitacion"),
            EstadoTipoHabitacion=tipo_dto.get("EstadoTipoHabitacion"),
            FechaModificacionTipoHabitacion=datetime.now()
        )

    # ================================================================
    # GET: obtener todos los tipos de habitación
    # ================================================================
    def obtener_tipos(self):
        try:
            r = self.client.service.ObtenerTiposHabitacion()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise ConnectionError(f"SOAP Error al obtener lista de tipos de habitación: {e}")

    # ================================================================
    # GET: obtener tipo por ID
    # ================================================================
    def obtener_tipo_por_id(self, id_tipo: int):
        try:
            r = self.client.service.ObtenerTipoHabitacionPorId(id_tipo)
            return self._normalize(r)
        except Fault as e:
            raise ConnectionError(f"SOAP Error al obtener tipo de habitación {id_tipo}: {e}")

    # ================================================================
    # POST: crear tipo de habitación
    # ================================================================
    def crear_tipo(self, tipo_dto: dict):
        try:
            dto = self._denormalize(tipo_dto, 0)   # ID = 0 en creación
            r = self.client.service.CrearTipoHabitacion(dto)
            return self._normalize(r)
        except Fault as e:
            raise ConnectionError(f"SOAP Error al crear tipo de habitación: {e}")

    # ================================================================
    # PUT: actualizar tipo de habitación
    # ================================================================
    def actualizar_tipo(self, id_tipo: int, tipo_dto: dict):
        try:
            dto = self._denormalize(tipo_dto, id_tipo)
            r = self.client.service.ActualizarTipoHabitacion(id_tipo, dto)
            return self._normalize(r)
        except Fault as e:
            raise ConnectionError(f"SOAP Error al actualizar tipo de habitación {id_tipo}: {e}")

    # ================================================================
    # DELETE: eliminar tipo de habitación
    # ================================================================
    def eliminar_tipo(self, id_tipo: int):
        try:
            ok = self.client.service.EliminarTipoHabitacion(id_tipo)
            return bool(ok)
        except Fault as e:
            raise ConnectionError(f"SOAP Error al eliminar tipo de habitación {id_tipo}: {e}")

