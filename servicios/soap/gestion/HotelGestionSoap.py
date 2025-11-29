import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class HotelGestionSoap:

    def __init__(self):
        # WSDL publicado en Azure
        self.wsdl = (
            "https://gesoca-exd5cdh5fmc3hdf9.canadacentral-01.azurewebsites.net/"
            "HotelWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ================= NORMALIZAR =====================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(x):
            return x.isoformat() if x else None

        return {
            "idHotel": d.get("IdHotel"),
            "nombreHotel": d.get("NombreHotel"),
            "estadoHotel": d.get("EstadoHotel"),
            "fechaModificacionHotel": fmt(d.get("FechaModificacionHotel")),
        }

    # ================= LISTAR =====================
    def listar(self):
        try:
            r = self.client.service.ObtenerHotel()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar hoteles: {e}")

    # ================= OBTENER POR ID =====================
    def obtener_por_id(self, id):
        try:
            r = self.client.service.ObtenerHotelPorId(id)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener hotel {id}: {e}")

    # ================= CREAR =====================
    def crear(self, dto):
        try:
            r = self.client.service.CrearHotel(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear hotel: {e}")

    # ================= ACTUALIZAR =====================
    def actualizar(self, id, dto):
        try:
            r = self.client.service.ActualizarHotel(id, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar hotel: {e}")

    # ================= ELIMINAR =====================
    def eliminar(self, id):
        try:
            return self.client.service.EliminarHotel(id)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar hotel {id}: {e}")
