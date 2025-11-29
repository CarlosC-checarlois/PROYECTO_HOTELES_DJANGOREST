import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class CiudadGestionSoap:

    def __init__(self):
        # WSDL PUBLICADO EN AZURE 🚀
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "CiudadService_asmx.asmx?wsdl"
        )

        # Desactivar SSL (Azure usa certificado intermedio)
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # =====================================================
    #     NORMALIZACIÓN → Igual a REST
    # =====================================================
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "idCiudad": d.get("IdCiudad"),
            "idPais": d.get("IdPais"),
            "nombreCiudad": d.get("NombreCiudad"),
            "estadoCiudad": d.get("EstadoCiudad"),
            "fechaModificacionCiudad": (
                d.get("FechaModificacionCiudad").isoformat()
                if d.get("FechaModificacionCiudad") else None
            )
        }

    # =====================================================
    #     LISTAR
    # =====================================================
    def listar(self):
        try:
            result = self.client.service.ObtenerCiudad()
            result = serialize_object(result)
            return [self._normalize(item) for item in result]
        except Fault as e:
            raise Exception(f"Error SOAP al listar ciudades: {e}")

    # =====================================================
    #     OBTENER POR ID
    # =====================================================
    def obtener_por_id(self, id_ciudad):
        try:
            result = self.client.service.ObtenerCiudadPorId(id_ciudad)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener ciudad {id_ciudad}: {e}")

    # =====================================================
    #     CREAR
    # =====================================================
    def crear(self, dto):
        try:
            result = self.client.service.CrearCiudad(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear ciudad: {e}")

    # =====================================================
    #     ACTUALIZAR
    # =====================================================
    def actualizar(self, id_ciudad, dto):
        try:
            result = self.client.service.ActualizarCiudad(id_ciudad, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar ciudad {id_ciudad}: {e}")

    # =====================================================
    #     ELIMINAR
    # =====================================================
    def eliminar(self, id_ciudad):
        try:
            return self.client.service.EliminarCiudad(id_ciudad)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar ciudad {id_ciudad}: {e}")
