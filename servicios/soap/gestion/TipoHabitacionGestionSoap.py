import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class TipoHabitacionGestionSoap:

    def __init__(self):
        # URL WSDL del servicio SOAP publicado en Azure
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "TipoHabitacionWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ========================================================
    # NORMALIZADOR
    # ========================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "idTipoHabitacion": d.get("IdTipoHabitacion"),
            "nombreHabitacion": d.get("NombreHabitacion"),
            "estadoTipoHabitacion": d.get("EstadoTipoHabitacion"),
            "fechaModificacionTipoHabitacion": fmt(d.get("FechaModificacionTipoHabitacion")),
        }

    # ========================================================
    # LISTAR
    # ========================================================
    def listar(self):
        try:
            r = self.client.service.ObtenerTiposHabitacion()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar tipos: {e}")

    # ========================================================
    # OBTENER POR ID
    # ========================================================
    def obtener_por_id(self, id_tipo):
        try:
            r = self.client.service.ObtenerTipoHabitacionPorId(id_tipo)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener tipo por ID: {e}")

    # ========================================================
    # CREAR
    # ========================================================
    def crear(self, dto):
        try:
            r = self.client.service.CrearTipoHabitacion(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear tipo habitación: {e}")

    # ========================================================
    # ACTUALIZAR
    # ========================================================
    def actualizar(self, id_tipo, dto):
        try:
            r = self.client.service.ActualizarTipoHabitacion(id_tipo, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar tipo habitación: {e}")

    # ========================================================
    # ELIMINAR
    # ========================================================
    def eliminar(self, id_tipo):
        try:
            return self.client.service.EliminarTipoHabitacion(id_tipo)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar tipo habitación: {e}")
