import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault

class DescuentoGestionSoap:

    def __init__(self):
        # Cambia el puerto si tu SOAP usa otro
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/DescuentoWS.asmx?wsdl"

        # Desactivar SSL (IIS Express usa certificado auto-firmado)
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ---------------------------------------------------------
    # NORMALIZACIÓN (SOAP → JSON REST)
    # ---------------------------------------------------------
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "idDescuento": d.get("IdDescuento"),
            "nombreDescuento": d.get("NombreDescuento"),
            "valorDescuento": float(d.get("ValorDescuento")) if d.get("ValorDescuento") is not None else None,
            "fechaInicioDescuento": (
                d.get("FechaInicioDescuento").isoformat()
                if d.get("FechaInicioDescuento") else None
            ),
            "fechaFinDescuento": (
                d.get("FechaFinDescuento").isoformat()
                if d.get("FechaFinDescuento") else None
            ),
            "estadoDescuento": d.get("EstadoDescuento"),
            "fechaModificacionDescuento": (
                d.get("FechaModificacionDescuento").isoformat()
                if d.get("FechaModificacionDescuento") else None
            )
        }

    # ---------------------------------------------------------
    # LISTAR DESCUENTOS
    # ---------------------------------------------------------
    def listar(self):
        try:
            data = self.client.service.ObtenerDescuentos()
            data = serialize_object(data)
            return [self._normalize(item) for item in data]

        except Fault as e:
            raise Exception(f"Error SOAP al listar descuentos: {e}")

    # ---------------------------------------------------------
    # OBTENER POR ID
    # ---------------------------------------------------------
    def obtener_por_id(self, id_descuento):
        try:
            res = self.client.service.ObtenerDescuentoPorId(id_descuento)
            return self._normalize(res)

        except Fault as e:
            raise Exception(f"Error SOAP al obtener descuento {id_descuento}: {e}")

    # ---------------------------------------------------------
    # CREAR DESCUENTO
    # ---------------------------------------------------------
    def crear(self, dto):
        try:
            result = self.client.service.CrearDescuento(dto)
            return self._normalize(result)

        except Fault as e:
            raise Exception(f"Error SOAP al crear descuento: {e}")

    # ---------------------------------------------------------
    # ACTUALIZAR DESCUENTO
    # ---------------------------------------------------------
    def actualizar(self, id_descuento, dto):
        try:
            result = self.client.service.ActualizarDescuento(id_descuento, dto)
            return self._normalize(result)

        except Fault as e:
            raise Exception(f"Error SOAP al actualizar descuento {id_descuento}: {e}")

    # ---------------------------------------------------------
    # ELIMINAR DESCUENTO
    # ---------------------------------------------------------
    def eliminar(self, id_descuento):
        try:
            return self.client.service.EliminarDescuento(id_descuento)

        except Fault as e:
            raise Exception(f"Error SOAP al eliminar descuento {id_descuento}: {e}")
