import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class HoldGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/HoldWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ======================================================
    # NORMALIZAR (igual formato que REST)
    # ======================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(x):
            return x.isoformat() if x else None

        return {
            "IdHold": d.get("IdHold"),
            "IdHabitacion": d.get("IdHabitacion"),
            "IdReserva": d.get("IdReserva"),
            "TiempoHold": d.get("TiempoHold"),
            "FechaInicioHold": fmt(d.get("FechaInicioHold")),
            "FechaFinalHold": fmt(d.get("FechaFinalHold")),
            "EstadoHold": d.get("EstadoHold"),
        }

    # ======================================================
    # DESNORMALIZAR 
    # ======================================================
    def _denormalize(
        self,
        id_hold,
        id_habitacion,
        id_reserva,
        tiempo_hold,
        fecha_inicio,
        fecha_final,
        estado
    ):
        return {
            "IdHold": id_hold,
            "IdHabitacion": id_habitacion,
            "IdReserva": id_reserva,
            "TiempoHold": tiempo_hold,
            "FechaInicioHold": fecha_inicio,
            "FechaFinalHold": fecha_final,
            "EstadoHold": estado
        }

    # ======================================================
    # GET → Obtener todos 
    # ======================================================
    def obtener_hold(self):
        try:
            result = self.client.service.ObtenerHold()
            result = serialize_object(result)
            return [self._normalize(x) for x in result]
        except Fault as e:
            raise Exception(f"Error SOAP al obtener HOLD: {e}")

    # ======================================================
    # GET → Obtener por ID 
    # ======================================================
    def obtener_hold_por_id(self, id_hold):
        try:
            r = self.client.service.ObtenerHoldPorId(id_hold)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener HOLD por ID {id_hold}: {e}")

    # ======================================================
    # POST → Crear HOLD 
    # ======================================================
    def crear_hold(
        self,
        id_hold,
        id_habitacion,
        id_reserva,
        tiempo_hold=None,
        fecha_inicio=None,
        fecha_final=None,
        estado=True
    ):
        dto = self._denormalize(
            id_hold,
            id_habitacion,
            id_reserva,
            tiempo_hold,
            fecha_inicio,
            fecha_final,
            estado
        )

        try:
            r = self.client.service.CrearHold(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al crear HOLD: {e}")

    # ======================================================
    # PUT → Actualizar 
    # ======================================================
    def actualizar_hold(
        self,
        id_hold,
        id_habitacion,
        id_reserva,
        tiempo_hold=None,
        fecha_inicio=None,
        fecha_final=None,
        estado=None
    ):
        dto = self._denormalize(
            id_hold,
            id_habitacion,
            id_reserva,
            tiempo_hold,
            fecha_inicio,
            fecha_final,
            estado
        )

        try:
            r = self.client.service.ActualizarHold(id_hold, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar HOLD {id_hold}: {e}")

    # ======================================================
    # DELETE → Eliminar 
    # ======================================================
    def eliminar_hold(self, id_hold):
        try:
            return self.client.service.EliminarHold(id_hold)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar HOLD {id_hold}: {e}")

