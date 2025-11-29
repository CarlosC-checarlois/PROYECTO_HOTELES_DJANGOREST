import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class HabitacionGestionSoap:

    def __init__(self):
        # 🔥 WSDL de Habitaciones publicado en Azure
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "HabitacionWS.asmx?wsdl"
        )

        # Azure → SSL intermedio → permitir verify=False
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # =============================================================
    # NORMALIZAR → MISMO FORMATO QUE REST
    # =============================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(dt):
            return dt.isoformat() if dt else None

        return {
            "idHabitacion": d.get("IdHabitacion"),
            "idTipoHabitacion": d.get("IdTipoHabitacion"),
            "idCiudad": d.get("IdCiudad"),
            "idHotel": d.get("IdHotel"),
            "nombreHabitacion": d.get("NombreHabitacion"),
            "precioNormalHabitacion": d.get("PrecioNormalHabitacion"),
            "precioActualHabitacion": d.get("PrecioActualHabitacion"),
            "capacidadHabitacion": d.get("CapacidadHabitacion"),
            "estadoHabitacion": d.get("EstadoHabitacion"),
            "fechaRegistroHabitacion": fmt(d.get("FechaRegistroHabitacion")),
            "estadoActivoHabitacion": d.get("EstadoActivoHabitacion"),
            "fechaModificacionHabitacion": fmt(d.get("FechaModificacionHabitacion")),
        }

    # =============================================================
    # LISTAR
    # =============================================================
    def listar(self):
        try:
            result = self.client.service.ObtenerHabitaciones()
            result = serialize_object(result)
            return [self._normalize(x) for x in result]
        except Fault as e:
            raise Exception(f"Error SOAP al listar habitaciones: {e}")

    # =============================================================
    # OBTENER POR ID
    # =============================================================
    def obtener_por_id(self, id_hab):
        try:
            result = self.client.service.ObtenerHabitacionPorId(id_hab)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener habitación ({id_hab}): {e}")

    # =============================================================
    # CREAR
    # =============================================================
    def crear(self, dto):
        try:
            result = self.client.service.CrearHabitacion(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear habitación: {e}")

    # =============================================================
    # ACTUALIZAR
    # =============================================================
    def actualizar(self, id_hab, dto):
        try:
            result = self.client.service.ActualizarHabitacion(id_hab, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar habitación ({id_hab}): {e}")

    # =============================================================
    # ELIMINAR (lógica)
    # =============================================================
    def eliminar(self, id_hab):
        try:
            return self.client.service.EliminarHabitacion(id_hab)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar habitación ({id_hab}): {e}")
