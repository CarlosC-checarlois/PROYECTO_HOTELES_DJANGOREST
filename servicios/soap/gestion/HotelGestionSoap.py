import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class HotelGestionSoap:

    def __init__(self):
        self.wsdl = "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/HotelWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ========================================================
    # NORMALIZAR (formato idéntico a REST)
    # ========================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        fecha = d.get("FechaModificacionHotel")
        if hasattr(fecha, "isoformat"):
            fecha = fecha.isoformat()

        return {
            "IdHotel": d.get("IdHotel"),
            "NombreHotel": d.get("NombreHotel"),
            "EstadoHotel": d.get("EstadoHotel"),
            "FechaModificacionHotel": fecha
        }

    # ========================================================
    # DESNORMALIZAR 
    # ========================================================
    def _denormalize(self, id_hotel, nombre, estado):
        return {
            "IdHotel": id_hotel,
            "NombreHotel": nombre,
            "EstadoHotel": estado,
            "FechaModificacionHotel": datetime.now()
        }

    # ========================================================
    # GET → Obtener lista de hoteles 
    # ========================================================
    def obtener_hoteles(self):
        try:
            r = self.client.service.ObtenerHotel()
            data = serialize_object(r)

            if isinstance(data, list):
                return [self._normalize(x) for x in data]

            if isinstance(data, dict):
                for k in data:
                    if isinstance(data[k], list):
                        return [self._normalize(x) for x in data[k]]

            return []

        except Fault as e:
            raise Exception(f"SOAP Error al listar hoteles: {e}")

    # ========================================================
    # GET → Obtener hotel por ID 
    # ========================================================
    def obtener_hotel_por_id(self, id_hotel):
        try:
            r = self.client.service.ObtenerHotelPorId(id_hotel)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener hotel {id_hotel}: {e}")

    # ========================================================
    # POST → Crear hotel 
    # ========================================================
    def crear_hotel(self, id_hotel, nombre_hotel, estado_hotel=True):
        dto = self._denormalize(id_hotel, nombre_hotel, estado_hotel)

        try:
            r = self.client.service.CrearHotel(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear hotel: {e}")

    # ========================================================
    # PUT → Actualizar hotel 
    # ========================================================
    def actualizar_hotel(self, id_hotel, nombre_hotel, estado_hotel):
        dto = self._denormalize(id_hotel, nombre_hotel, estado_hotel)

        try:
            r = self.client.service.ActualizarHotel(id_hotel, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(
                f"SOAP Error al actualizar hotel {id_hotel}: {e}"
            )

    # ========================================================
    # DELETE → Eliminación lógica 
    # ========================================================
    def eliminar_hotel(self, id_hotel):
        try:
            return self.client.service.EliminarHotel(id_hotel)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar hotel {id_hotel}: {e}")

