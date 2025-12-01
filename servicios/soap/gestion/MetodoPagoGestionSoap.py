import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from decimal import Decimal


class MetodoPagoGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/MetodoPagoWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        self.client = Client(wsdl=self.wsdl, transport=Transport(session=session))

    # ========================================================
    # Normalización EXACTA a formato REST
    # ========================================================
    def _normalize(self, data):
        if data is None:
            return None

        d = serialize_object(data)

        # convertir decimales a float
        def fix(x):
            if isinstance(x, Decimal):
                return float(x)
            return x

        fecha = d.get("FechaModificacionMetodoPago")
        if hasattr(fecha, "isoformat"):
            fecha = fecha.isoformat()

        return {
            "IdMetodoPago": fix(d.get("IdMetodoPago")),
            "NombreMetodoPago": d.get("NombreMetodoPago"),
            "EstadoMetodoPago": d.get("EstadoMetodoPago"),
            "FechaModificacionMetodoPago": fecha,
        }

    # ========================================================
    # Construir DTO SOAP
    # ========================================================
    def _denormalize(self, id_metodo, nombre, estado):
        return {
            "IdMetodoPago": id_metodo,
            "NombreMetodoPago": nombre,
            "EstadoMetodoPago": estado,
            "FechaModificacionMetodoPago": datetime.now()
        }

    # ========================================================
    # GET → Obtener todos
    # ========================================================
    def obtener_metodos_pago(self):
        try:
            result = self.client.service.ObtenerMetodoPago()
            result = serialize_object(result)
            return [self._normalize(x) for x in result]
        except Fault as e:
            raise Exception(f"SOAP Error al obtener métodos de pago: {e}")

    # ========================================================
    # GET → Obtener por ID
    # ========================================================
    def obtener_metodo_pago_por_id(self, id_metodo):
        try:
            r = self.client.service.ObtenerMetodoPagoPorId(id_metodo)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener método por ID: {e}")

    # ========================================================
    # POST → Crear 
    # ========================================================
    def crear_metodo_pago(self, id_metodo, nombre_metodo, estado_metodo=True):
        dto = self._denormalize(id_metodo, nombre_metodo, estado_metodo)

        try:
            r = self.client.service.CrearMetodoPago(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear método de pago: {e}")

    # ========================================================
    # PUT → Actualizar 
    # ========================================================
    def actualizar_metodo_pago(self, id_metodo, nombre_metodo, estado_metodo):
        dto = self._denormalize(id_metodo, nombre_metodo, estado_metodo)

        try:
            r = self.client.service.ActualizarMetodoPago(id_metodo, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar método de pago: {e}")

    # ========================================================
    # DELETE → Lógico 
    # ========================================================
    def eliminar_metodo_pago(self, id_metodo):
        try:
            return self.client.service.EliminarMetodoPago(id_metodo)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar método de pago: {e}")
        
