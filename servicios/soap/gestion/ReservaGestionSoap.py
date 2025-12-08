
import requests
from datetime import datetime
from decimal import Decimal
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class ReservaGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/ReservaWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ============================================================
    # UTIL: Convertir Decimal → float
    # ============================================================
    def _fix(self, v):
        if isinstance(v, Decimal):
            return float(v)
        return v

    # ============================================================
    # UTIL: Convertir fechas SOAP → ISO8601
    # ============================================================
    def _fmt(self, date):
        return date.isoformat() if date else None

    # ============================================================
    # NORMALIZAR: SOAP → Formato REST
    # ============================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        return {
            "IdReserva": d.get("IdReserva"),
            "IdUnicoUsuario": d.get("IdUnicoUsuario"),
            "IdUnicoUsuarioExterno": d.get("IdUnicoUsuarioExterno"),
            "CostoTotalReserva": self._fix(d.get("CostoTotalReserva")),
            "FechaRegistroReserva": self._fmt(d.get("FechaRegistroReserva")),
            "FechaInicioReserva": self._fmt(d.get("FechaInicioReserva")),
            "FechaFinalReserva": self._fmt(d.get("FechaFinalReserva")),
            "EstadoGeneralReserva": d.get("EstadoGeneralReserva"),
            "EstadoReserva": d.get("EstadoReserva"),
            "FechaModificacionReserva": self._fmt(d.get("FechaModificacionReserva")),
        }

    # ============================================================
    # DENORMALIZAR: REST → SOAP DTO
    # ============================================================
    def _denormalize(self, dto: dict):
        return {
            "IdReserva": dto.get("idReserva"),
            "IdUnicoUsuario": dto.get("idUnicoUsuario"),
            "IdUnicoUsuarioExterno": dto.get("idUnicoUsuarioExterno"),
            "CostoTotalReserva": dto.get("costoTotalReserva"),
            "FechaRegistroReserva": dto.get("fechaRegistroReserva"),
            "FechaInicioReserva": dto.get("fechaInicioReserva"),
            "FechaFinalReserva": dto.get("fechaFinalReserva"),
            "EstadoGeneralReserva": dto.get("estadoGeneralReserva"),
            "EstadoReserva": dto.get("estadoReserva"),
            "FechaModificacionReserva": datetime.now(),
        }

    # ============================================================
    # GET → Obtener lista completa
    # ============================================================
    def obtener_reservas(self):
        try:
            r = self.client.service.ObtenerReservas()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]

        except Fault as e:
            raise Exception(f"SOAP Error al listar reservas: {e}")

    # ============================================================
    # GET → Obtener reserva por ID
    # ============================================================
    def obtener_reserva_por_id(self, id_reserva):
        try:
            r = self.client.service.ObtenerReservaPorId(id_reserva)
            return self._normalize(r)

        except Fault as e:
            raise Exception(f"SOAP Error al obtener reserva por ID: {e}")

    # ============================================================
    # POST → Crear reserva
    # ============================================================
    def crear_reserva(self, dto):
        dto_soap = self._denormalize(dto)

        try:
            r = self.client.service.CrearReserva(dto_soap)
            return self._normalize(r)

        except Fault as e:
            raise Exception(f"SOAP Error al crear reserva: {e}")

    # ============================================================
    # PUT → Actualizar reserva
    # ============================================================
    def actualizar_reserva(self, id_reserva, dto):
        dto_soap = self._denormalize(dto)

        try:
            r = self.client.service.ActualizarReserva(id_reserva, dto_soap)
            return self._normalize(r)

        except Fault as e:
            raise Exception(f"SOAP Error al actualizar reserva: {e}")

    # ============================================================
    # DELETE → Eliminar reserva (lógico)
    # ============================================================
    def eliminar_reserva(self, id_reserva):
        try:
            return self.client.service.EliminarReserva(id_reserva)

        except Fault as e:
            raise Exception(f"SOAP Error al eliminar reserva: {e}")

    # ============================================================
    # INTEGRACIÓN → Crear PRE-RESERVA
    # ============================================================
    def crear_prereserva(
        self, id_habitacion, fecha_inicio, fecha_fin, numero_huespedes,
        nombre=None, apellido=None, correo=None, tipo_doc=None, documento=None,
        duracion_seg=None, precio_actual=None
    ):
        try:
            r = self.client.service.CrearPreReserva(
                id_habitacion, fecha_inicio, fecha_fin, numero_huespedes,
                nombre, apellido, correo, tipo_doc, documento,
                duracion_seg, precio_actual
            )
            return serialize_object(r)

        except Fault as e:
            raise Exception(f"SOAP Error al crear pre-reserva: {e}")

    # ============================================================
    # INTEGRACIÓN → Confirmar reserva
    # ============================================================
    def confirmar_reserva(
        self, id_habitacion, id_hold, nombre, apellido, correo, tipo_doc,
        fecha_inicio, fecha_fin, numero_huespedes
    ):
        try:
            r = self.client.service.ConfirmarReserva(
                id_habitacion, id_hold, nombre, apellido, correo, tipo_doc,
                fecha_inicio, fecha_fin, numero_huespedes
            )
            return serialize_object(r)

        except Fault as e:
            raise Exception(f"SOAP Error al confirmar reserva: {e}")

    # ============================================================
    # INTEGRACIÓN → Buscar datos reserva
    # ============================================================
    def buscar_datos_reserva(self, id_reserva=None):
        try:
            r = self.client.service.BuscarDatosReserva(id_reserva)
            return serialize_object(r)

        except Fault as e:
            raise Exception(f"SOAP Error al buscar datos reserva: {e}")

