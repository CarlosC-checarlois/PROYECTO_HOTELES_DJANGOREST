import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class HoldGestionSoap:

    def __init__(self):
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "HoldWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ================= NORMALIZAR DATOS =====================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(x):
            return x.isoformat() if x else None

        return {
            "idHold": d.get("IdHold"),
            "idHabitacion": d.get("IdHabitacion"),
            "idReserva": d.get("IdReserva"),
            "tiempoHold": d.get("TiempoHold"),
            "fechaInicioHold": fmt(d.get("FechaInicioHold")),
            "fechaFinalHold": fmt(d.get("FechaFinalHold")),
            "estadoHold": d.get("EstadoHold"),
        }

    # ================= LISTAR =====================
    def listar(self):
        try:
            r = self.client.service.ObtenerHold()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"Error SOAP al listar Hold: {e}")

    # ================= OBTENER POR ID =====================
    def obtener_por_id(self, id_hold):
        try:
            r = self.client.service.ObtenerHoldPorId(id_hold)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener Hold {id_hold}: {e}")

    # ================= CREAR =====================
    def crear(self, dto):
        try:
            r = self.client.service.CrearHold(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al crear Hold: {e}")

    # ================= ACTUALIZAR =====================
    def actualizar(self, id_hold, dto):
        try:
            r = self.client.service.ActualizarHold(id_hold, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar Hold {id_hold}: {e}")

    # ================= ELIMINAR =====================
    def eliminar(self, id_hold):
        try:
            return self.client.service.EliminarHold(id_hold)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar Hold {id_hold}: {e}")
