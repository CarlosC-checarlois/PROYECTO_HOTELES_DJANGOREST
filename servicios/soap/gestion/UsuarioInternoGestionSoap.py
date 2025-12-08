import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from decimal import Decimal


class UsuarioInternoGestionSoap:

    def __init__(self):

        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/UsuarioInternoWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # =====================================================================
    # Normalizar (SOAP → REST)
    # =====================================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fix(v):
            if isinstance(v, Decimal):
                return float(v)
            return v

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "Id": d.get("Id"),
            "IdRol": d.get("IdRol"),
            "Nombre": d.get("Nombre"),
            "Apellido": d.get("Apellido"),
            "Correo": d.get("Correo"),
            "Clave": d.get("Clave"),
            "Estado": d.get("Estado"),
            "FechaNacimiento": fmt(d.get("FechaNacimiento")),
            "FechaModificacion": fmt(d.get("FechaModificacion")),
            "TipoDocumento": d.get("TipoDocumento"),
            "Documento": d.get("Documento"),
        }

    # =====================================================================
    # Des-normalizar (REST → SOAP)
    # =====================================================================
    def _denormalize(self, dto):
        return {
            "Id": dto.get("Id"),
            "IdRol": dto.get("IdRol"),
            "Nombre": dto.get("Nombre"),
            "Apellido": dto.get("Apellido"),
            "Correo": dto.get("Correo"),
            "Clave": dto.get("Clave"),
            "Estado": dto.get("Estado"),
            "FechaNacimiento": dto.get("FechaNacimiento"),
            "TipoDocumento": dto.get("TipoDocumento"),
            "Documento": dto.get("Documento"),
            "FechaModificacion": datetime.now()
        }

    # =====================================================================
    # GET: listar
    # =====================================================================
    def listar(self):
        try:
            r = self.client.service.Listar()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar usuarios: {e}")

    # =====================================================================
    # GET: obtener por ID
    # =====================================================================
    def obtener_por_id(self, id_usuario):
        try:
            r = self.client.service.ObtenerPorId(id_usuario)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener usuario: {e}")

    # =====================================================================
    # POST: crear
    # =====================================================================
    def crear(self, dto):
        try:
            dto_soap = self._denormalize(dto)
            r = self.client.service.Crear(dto_soap)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear usuario: {e}")

    # =====================================================================
    # PUT: actualizar
    # =====================================================================
    def actualizar(self, dto):
        try:
            dto_soap = self._denormalize(dto)
            r = self.client.service.Actualizar(dto_soap)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar usuario: {e}")

    # =====================================================================
    # DELETE: eliminar
    # =====================================================================
    def eliminar(self, id_usuario):
        try:
            return self.client.service.Eliminar(id_usuario)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar usuario: {e}")

    # =====================================================================
    # POST: login
    # =====================================================================
    def login(self, correo, clave):
        try:
            r = self.client.service.IniciarSesion(correo, clave)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error en login: {e}")
