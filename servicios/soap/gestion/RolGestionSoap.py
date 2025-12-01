import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from decimal import Decimal


class RolGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/RolWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ============================================================
    # Normalizar SOAP → REST-friendly JSON
    # ============================================================
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        # Convertir Decimal → float
        def num(v):
            if isinstance(v, Decimal):
                return float(v)
            return v

        fecha = d.get("FechaModificacionRol")
        if hasattr(fecha, "isoformat"):
            fecha = fecha.isoformat()

        return {
            "IdRol": num(d.get("IdRol")),
            "NombreRol": d.get("NombreRol"),
            "EstadoRol": d.get("EstadoRol"),
            "FechaModificacionRol": fecha,
        }

    # ============================================================
    # Desnormalizar → construir DTO idéntico al REST
    # ============================================================
    def _denormalize(self, rol_dto):
        """
        rol_dto REST:
        {
            "idRol": 3,
            "nombreRol": "Admin",
            "estadoRol": true,
            "fechaModificacionRol": "2025-01-01T12:00:00"
        }
        """
        return {
            "IdRol": rol_dto.get("idRol"),
            "NombreRol": rol_dto.get("nombreRol"),
            "EstadoRol": rol_dto.get("estadoRol"),
            "FechaModificacionRol": datetime.now(),
        }

    # ============================================================
    # GET ALL 
    # ============================================================
    def obtener_roles(self):
        try:
            result = self.client.service.ObtenerRol()
            result = serialize_object(result)
            return [self._normalize(r) for r in result]
        except Fault as e:
            raise Exception(f"SOAP Error al obtener roles: {e}")

    # ============================================================
    # GET BY ID 
    # ============================================================
    def obtener_rol_por_id(self, id_rol: int):
        try:
            result = self.client.service.ObtenerRolPorId(id_rol)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener rol {id_rol}: {e}")

    # ============================================================
    # CREATE 
    # ============================================================
    def crear_rol(self, rol_dto: dict):
        dto = self._denormalize(rol_dto)
        try:
            result = self.client.service.CrearRol(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"SOAP Error al crear rol: {e}")

    # ============================================================
    # UPDATE 
    # ============================================================
    def actualizar_rol(self, id_rol: int, rol_dto: dict):
        dto = self._denormalize(rol_dto)
        try:
            result = self.client.service.ActualizarRol(id_rol, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar rol {id_rol}: {e}")

    # ============================================================
    # DELETE 
    # ============================================================
    def eliminar_rol(self, id_rol: int):
        try:
            return self.client.service.EliminarRol(id_rol)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar rol {id_rol}: {e}")

