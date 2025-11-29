import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class PagoGestionSoap:

    def __init__(self):
        # 👉 WSDL publicado de PagoWS (ajústalo si tu URL cambia)
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "PagoWS.asmx?wsdl"
        )

        # Azure → requiere desactivar verificación SSL
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ===============================================================
    # NORMALIZADOR → que coincida con REST EXACTAMENTE
    # ===============================================================
    def _normalize(self, p):
        if p is None:
            return None

        d = serialize_object(p)

        return {
            "idPago": d.get("IdPago"),
            "idMetodoPago": d.get("IdMetodoPago"),
            "idUnicoUsuarioExterno": d.get("IdUnicoUsuarioExterno"),
            "idUnicoUsuario": d.get("IdUnicoUsuario"),
            "idFactura": d.get("IdFactura"),
            "cuentaOrigenPago": d.get("CuentaOrigenPago"),
            "cuentaDestinoPago": d.get("CuentaDestinoPago"),
            "montoTotalPago": d.get("MontoTotalPago"),

            "fechaEmisionPago": (
                d.get("FechaEmisionPago").isoformat()
                if d.get("FechaEmisionPago") else None
            ),

            "estadoPago": d.get("EstadoPago"),

            "fechaModificacionPago": (
                d.get("FechaModificacionPago").isoformat()
                if d.get("FechaModificacionPago") else None
            )
        }

    # ===============================================================
    # LISTAR
    # ===============================================================
    def listar(self):
        try:
            result = self.client.service.ObtenerPago()
            result = serialize_object(result)
            return [self._normalize(p) for p in result]
        except Fault as e:
            raise Exception(f"Error SOAP al listar pagos: {e}")

    # ===============================================================
    # OBTENER POR ID
    # ===============================================================
    def obtener_por_id(self, id_pago):
        try:
            result = self.client.service.ObtenerPagoPorId(id_pago)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener pago {id_pago}: {e}")

    # ===============================================================
    # CREAR
    # ===============================================================
    def crear(self, dto):
        try:
            result = self.client.service.CrearPago(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear pago: {e}")

    # ===============================================================
    # ACTUALIZAR
    # ===============================================================
    def actualizar(self, id_pago, dto):
        try:
            result = self.client.service.ActualizarPago(id_pago, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar pago {id_pago}: {e}")

    # ===============================================================
    # ELIMINAR (lógico)
    # ===============================================================
    def eliminar(self, id_pago):
        try:
            return self.client.service.EliminarPago(id_pago)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar pago {id_pago}: {e}")
