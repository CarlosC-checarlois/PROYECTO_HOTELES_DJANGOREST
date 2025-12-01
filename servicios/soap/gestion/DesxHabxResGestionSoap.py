import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from decimal import Decimal


class DesxHabxResGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/DesxHabxResWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # =====================================================
    # NORMALIZAR →
    # =====================================================
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        # --- Convertir Decimal a float ---
        def fix_numeric(v):
            if isinstance(v, Decimal):
                return float(v)
            return v

        monto = fix_numeric(d.get("MontoDesxHabxRes"))

        fecha = d.get("FechaModificacionDesxHabxRes")
        if hasattr(fecha, "isoformat"):
            fecha = fecha.isoformat()

        return {
            "IdDescuento": d.get("IdDescuento"),
            "IdHabxRes": d.get("IdHabxRes"),
            "MontoDesxHabxRes": monto,
            "EstadoDesxHabxRes": d.get("EstadoDesxHabxRes"),
            "FechaModificacionDesxHabxRes": fecha
        }

    # =====================================================
    # DESNORMALIZAR 
    # =====================================================
    def _denormalize(self, id_descuento, id_habxres, monto, estado):
        return {
            "IdDescuento": id_descuento,
            "IdHabxRes": id_habxres,
            "MontoDesxHabxRes": monto,
            "EstadoDesxHabxRes": estado,
            "FechaModificacionDesxHabxRes": datetime.now()
        }

    # =====================================================
    # GET → Obtener lista completa
    # =====================================================
    def obtener_desxhabxres(self):
        try:
            result = self.client.service.ObtenerDesxHabxRes()
            data = serialize_object(result)

            # Si viene como lista
            if isinstance(data, list):
                return [self._normalize(x) for x in data]

            # Si viene como dict con lista dentro
            if isinstance(data, dict):
                for k in data:
                    if isinstance(data[k], list):
                        return [self._normalize(x) for x in data[k]]

            return []

        except Fault as e:
            raise Exception(f"Error SOAP al obtener lista: {e}")

    # =====================================================
    # GET → Obtener por ID compuesto 
    # =====================================================
    def obtener_por_id(self, id_descuento, id_habxres):
        try:
            result = self.client.service.ObtenerDesxHabxResPorId(id_descuento, id_habxres)
            return self._normalize(result)
        except Fault as e:
            raise Exception(
                f"Error SOAP al obtener ({id_descuento}, {id_habxres}): {e}"
            )

    # =====================================================
    # POST → Crear 
    # =====================================================
    def crear_desxhabxres(self, id_descuento, id_habxres, monto=None, estado=True):
        dto = self._denormalize(id_descuento, id_habxres, monto, estado)

        try:
            result = self.client.service.CrearDesxHabxRes(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear DesxHabxRes: {e}")

    # =====================================================
    # PUT → Actualizar 
    # =====================================================
    def actualizar_desxhabxres(self, id_descuento, id_habxres, monto, estado):
        dto = self._denormalize(id_descuento, id_habxres, monto, estado)

        try:
            result = self.client.service.ActualizarDesxHabxRes(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(
                f"Error SOAP al actualizar ({id_descuento}, {id_habxres}): {e}"
            )

    # =====================================================
    # DELETE → Eliminación lógica 
    # =====================================================
    def eliminar_desxhabxres(self, id_descuento, id_habxres):
        try:
            return self.client.service.EliminarDesxHabxRes(id_descuento, id_habxres)
        except Fault as e:
            raise Exception(
                f"Error SOAP al eliminar ({id_descuento}, {id_habxres}): {e}"
            )

