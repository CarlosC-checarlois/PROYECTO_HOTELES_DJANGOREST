from pprint import pprint

import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from datetime import datetime

class AmenidadGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/AmenidadWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()
        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # -----------------------------
    # NORMALIZADOR
    # -----------------------------
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "idAmenidad": d.get("IdAmenidad"),
            "nombreAmenidad": d.get("NombreAmenidad"),
            "estadoAmenidad": d.get("EstadoAmenidad"),
            "fechaModificacionAmenidad": (
                d.get("FechaModificacionAmenidad").isoformat()
                if d.get("FechaModificacionAmenidad") else None
            )
        }

    # -----------------------------
    # LISTAR
    # -----------------------------
    def obtener_amenidades(self):
        try:
            data = self.client.service.ObtenerAmenidades()
            data = serialize_object(data)
            return [self._normalize(item) for item in data]
        except Fault as e:
            raise Exception(f"Error SOAP al listar amenidades: {e}")

    # -----------------------------
    # OBTENER
    # -----------------------------
    def obtener_por_id(self, id_amenidad):
        try:
            result = self.client.service.ObtenerAmenidadPorId(id_amenidad)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener amenidad {id_amenidad}: {e}")

    # -----------------------------
    # CREAR
    # -----------------------------
    def crear(self, dto):
        try:
            result = self.client.service.CrearAmenidad(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear amenidad: {e}")

    # -----------------------------
    # ACTUALIZAR
    # -----------------------------
    def actualizar(self, id_amenidad, dto):
        try:
            result = self.client.service.ActualizarAmenidad(id_amenidad, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar amenidad {id_amenidad}: {e}")

    # -----------------------------
    # ELIMINAR
    # -----------------------------
    def eliminar(self, id_amenidad):
        try:
            return self.client.service.EliminarAmenidad(id_amenidad)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar amenidad {id_amenidad}: {e}")
