import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault

class RolGestionSoap:

    def __init__(self):
        # URL DEL WSDL
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "RolWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        # Cliente SOAP
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ---------------------------------------------
    # Normalización de SOAP → dict
    # ---------------------------------------------
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "idRol": d.get("IdRol"),
            "nombreRol": d.get("NombreRol"),
            "estadoRol": d.get("EstadoRol"),
            "fechaModificacionRol": fmt(d.get("FechaModificacionRol")),
        }

    # ---------------------------------------------
    # LISTAR
    # ---------------------------------------------
    def listar(self):
        try:
            r = self.client.service.ObtenerRol()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar roles: {e}")

    # ---------------------------------------------
    # OBTENER POR ID
    # ---------------------------------------------
    def obtener_por_id(self, id_rol):
        try:
            r = self.client.service.ObtenerRolPorId(id_rol)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener rol por ID: {e}")

    # ---------------------------------------------
    # CREAR
    # ---------------------------------------------
    def crear(self, dto):
        try:
            r = self.client.service.CrearRol(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear rol: {e}")

    # ---------------------------------------------
    # ACTUALIZAR
    # ---------------------------------------------
    def actualizar(self, id_rol, dto):
        try:
            r = self.client.service.ActualizarRol(id_rol, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar rol: {e}")

    # ---------------------------------------------
    # ELIMINAR
    # ---------------------------------------------
    def eliminar(self, id_rol):
        try:
            return self.client.service.EliminarRol(id_rol)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar rol: {e}")
