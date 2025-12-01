import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from datetime import datetime


class CiudadGestionSoap:

    def __init__(self):
        # WSDL público
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/CiudadService.asmx?wsdl"

        # Permitir certificado Azure
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

        # Tipos reales del WSDL
        self.CiudadDto = self.client.get_type("ns0:CiudadDto")

    # =====================================================================
    # NORMALIZACIÓN → DEVUELVE EL MISMO FORMATO QUE EL REST
    # =====================================================================
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "IdCiudad": d.get("IdCiudad"),
            "IdPais": d.get("IdPais"),
            "NombreCiudad": d.get("NombreCiudad"),
            "EstadoCiudad": d.get("EstadoCiudad"),
            "FechaModificacionCiudad": (
                d.get("FechaModificacionCiudad").isoformat()
                if d.get("FechaModificacionCiudad") else None
            )
        }

    # =====================================================================
    # CONSTRUCTOR DE DTO 
    # =====================================================================
    def _build_dto(self, id_ciudad, id_pais, nombre, estado, fecha=None):
        if fecha is None:
            fecha = datetime.now()

        return self.CiudadDto(
            IdCiudad=id_ciudad,
            IdPais=id_pais,
            NombreCiudad=nombre,
            EstadoCiudad=estado,
            FechaModificacionCiudad=fecha
        )

    # =====================================================================
    # GET → ObtenerCiudad
    # =====================================================================
    def obtener_ciudades(self):
        try:
            response = self.client.service.ObtenerCiudad()
            data = serialize_object(response)

            # Puede venir como lista directa
            if isinstance(data, list):
                return [self._normalize(item) for item in data]

            # O a veces como dict con key 'CiudadDto'
            if isinstance(data, dict) and "CiudadDto" in data:
                return [self._normalize(item) for item in data["CiudadDto"]]

            # Si viene vacío
            return []

        except Fault as e:
            raise Exception(f"Error SOAP al obtener ciudades: {e}")


    # =====================================================================
    # GET → ObtenerCiudadPorId
    # =====================================================================
    def obtener_ciudad_por_id(self, id_ciudad):
        try:
            resp = self.client.service.ObtenerCiudadPorId(id=id_ciudad)
            return self._normalize(resp)

        except Fault as e:
            raise Exception(f"Error SOAP al obtener ciudad {id_ciudad}: {e}")

    # =====================================================================
    # POST → CrearCiudad
    # =====================================================================
    def crear_ciudad(self, id_ciudad, id_pais, nombre, estado=True):
        try:
            dto = self._build_dto(
                id_ciudad=id_ciudad,
                id_pais=id_pais,
                nombre=nombre,
                estado=estado
            )

            resp = self.client.service.CrearCiudad(dto=dto)
            return self._normalize(resp)

        except Fault as e:
            raise Exception(f"Error SOAP al crear ciudad: {e}")

    # =====================================================================
    # PUT → ActualizarCiudad
    # =====================================================================
    def actualizar_ciudad(self, id_ciudad, id_pais, nombre, estado=True):
        try:
            dto = self._build_dto(
                id_ciudad=id_ciudad,
                id_pais=id_pais,
                nombre=nombre,
                estado=estado
            )

            resp = self.client.service.ActualizarCiudad(id=id_ciudad, dto=dto)
            return self._normalize(resp)

        except Fault as e:
            raise Exception(f"Error SOAP al actualizar ciudad {id_ciudad}: {e}")

    # =====================================================================
    # DELETE → EliminarCiudad
    # =====================================================================
    def eliminar_ciudad(self, id_ciudad):
        try:
            result = self.client.service.EliminarCiudad(id=id_ciudad)
            return bool(result)

        except Fault as e:
            raise Exception(f"Error SOAP al eliminar ciudad {id_ciudad}: {e}")


