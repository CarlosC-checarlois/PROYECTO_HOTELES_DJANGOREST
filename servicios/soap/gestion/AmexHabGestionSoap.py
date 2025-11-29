import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class AmexHabGestionSoap:

    def __init__(self):
        # Cambia el puerto si tu SOAP usa otro
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/CiudadService_asmx.asmx?wsdl"

        # Desactivar verificación SSL porque es localhost
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # -----------------------------------------
    # NORMALIZADOR — Igual que REST
    # -----------------------------------------
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "idHabitacion": d.get("IdHabitacion"),
            "idAmenidad": d.get("IdAmenidad"),
            "estadoAmexHab": d.get("EstadoAmexHab"),
            "fechaModificacionAmexHab": (
                d.get("FechaModificacionAmexHab").isoformat()
                if d.get("FechaModificacionAmexHab") else None
            )
        }

    # -----------------------------------------
    # LISTAR
    # -----------------------------------------
    def listar(self):
        try:
            data = self.client.service.ObtenerAmexHab()
            data = serialize_object(data)
            return [self._normalize(item) for item in data]
        except Fault as e:
            raise Exception(f"Error SOAP al listar AMEXHAB: {e}")

    # -----------------------------------------
    # OBTENER POR ID COMPUESTO
    # -----------------------------------------
    def obtener_por_id(self, id_habitacion, id_amenidad):
        try:
            result = self.client.service.ObtenerAmexHabPorId(id_habitacion, id_amenidad)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener AmexHab: {e}")

    # -----------------------------------------
    # CREAR
    # -----------------------------------------
    def crear(self, dto):
        try:
            result = self.client.service.CrearAmexHab(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear AmexHab: {e}")

    # -----------------------------------------
    # ACTUALIZAR
    # -----------------------------------------
    def actualizar(self, dto):
        try:
            result = self.client.service.ActualizarAmexHab(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar AmexHab: {e}")

    # -----------------------------------------
    # ELIMINAR
    # -----------------------------------------
    def eliminar(self, id_habitacion, id_amenidad):
        try:
            return self.client.service.EliminarAmexHab(id_habitacion, id_amenidad)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar AmexHab: {e}")
