import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class ReservaGestionSoap:

    def __init__(self):
        # 👉 LINK DEL WSDL SOAP
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "ReservaWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ============================================================
    # Normalización SOAP → dict
    # ============================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "idReserva": d.get("IdReserva"),
            "idUnicoUsuario": d.get("IdUnicoUsuario"),
            "idUnicoUsuarioExterno": d.get("IdUnicoUsuarioExterno"),
            "costoTotalReserva": d.get("CostoTotalReserva"),
            "fechaRegistroReserva": fmt(d.get("FechaRegistroReserva")),
            "fechaInicioReserva": fmt(d.get("FechaInicioReserva")),
            "fechaFinalReserva": fmt(d.get("FechaFinalReserva")),
            "estadoGeneralReserva": d.get("EstadoGeneralReserva"),
            "estadoReserva": d.get("EstadoReserva"),
            "fechaModificacionReserva": fmt(d.get("FechaModificacionReserva")),
        }

    # ============================================================
    # LISTAR RESERVAS
    # ============================================================
    def listar(self):
        try:
            r = self.client.service.ObtenerReservas()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar reservas: {e}")

    # ============================================================
    # OBTENER POR ID
    # ============================================================
    def obtener_por_id(self, id_reserva):
        try:
            r = self.client.service.ObtenerReservaPorId(id_reserva)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener reserva por ID: {e}")

    # ============================================================
    # CREAR RESERVA
    # ============================================================
    def crear(self, dto):
        try:
            r = self.client.service.CrearReserva(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear reserva: {e}")

    # ============================================================
    # ACTUALIZAR RESERVA
    # ============================================================
    def actualizar(self, id_reserva, dto):
        try:
            r = self.client.service.ActualizarReserva(id_reserva, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar reserva: {e}")

    # ============================================================
    # ELIMINAR (CANCELAR) RESERVA
    # ============================================================
    def eliminar(self, id_reserva):
        try:
            return self.client.service.EliminarReserva(id_reserva)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar reserva: {e}")
