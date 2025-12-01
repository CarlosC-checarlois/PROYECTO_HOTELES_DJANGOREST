import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from datetime import datetime


class AmexHabGestionSoap:

    def __init__(self):
        # Cambia el puerto si tu SOAP usa otro
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/AmexHabWS.asmx?wsdl"

        # Desactivar verificación SSL porque es localhost
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

        self.DtoAmexHab = self.client.get_type("ns0:AmexHabDto")


    # -----------------------------------------
    # NORMALIZADOR — Igual que REST
    # -----------------------------------------
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "IdHabitacion": d.get("IdHabitacion"),
            "IdAmenidad": d.get("IdAmenidad"),
            "EstadoAmexHab": d.get("EstadoAmexHab"),
            "FechaModificacionAmexHab": (
                d.get("FechaModificacionAmexHab").isoformat()
                if d.get("FechaModificacionAmexHab") else None
            )
        }

    # ---------------------------------------------------------
    # CREAR DTO compatible REST
    # ---------------------------------------------------------
    def _dto(self, id_habitacion, id_amenidad, estado=True):
        return self.DtoAmexHab(
            IdHabitacion=id_habitacion,
            IdAmenidad=id_amenidad,
            EstadoAmexHab=estado,
            FechaModificacionAmexHab=datetime.now()
        )

    # ---------------------------------------------------------
    # GET LISTAR  → ObtenerAmexHab()
    # ---------------------------------------------------------
    def obtener_amexhab(self):
        try:
            data = self.client.service.ObtenerAmexHab()
            data = serialize_object(data)
            return [self._normalize(item) for item in data]
        except Fault as e:
            raise Exception(f"Error SOAP al listar AMEXHAB: {e}")

    # ---------------------------------------------------------
    # GET POR ID (ID compuesto)
    # ---------------------------------------------------------
    def obtener_amexhab_por_id(self, id_habitacion, id_amenidad):
        try:
            result = self.client.service.ObtenerAmexHabPorId(id_habitacion, id_amenidad)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener AMEXHAB: {e}")

    # ---------------------------------------------------------
    # POST → CrearAmexHab
    # ---------------------------------------------------------
    def crear_amexhab(self, id_habitacion, id_amenidad, estado=True):

        dto = self._dto(id_habitacion, id_amenidad, estado)

        try:
            result = self.client.service.CrearAmexHab(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear AMEXHAB: {e}")

    # ---------------------------------------------------------
    # PUT → ActualizarAmexHab
    # ---------------------------------------------------------
    def actualizar_amexhab(self, id_habitacion, id_amenidad, estado=True):

        dto = self._dto(id_habitacion, id_amenidad, estado)

        try:
            result = self.client.service.ActualizarAmexHab(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar AMEXHAB: {e}")

    # ---------------------------------------------------------
    # DELETE → EliminarAmexHab
    # ---------------------------------------------------------
    def eliminar_amexhab(self, id_habitacion, id_amenidad):
        try:
            return self.client.service.EliminarAmexHab(id_habitacion, id_amenidad)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar AMEXHAB: {e}")
        
        